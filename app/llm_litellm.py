"""
LiteLLM-based implementation (Production Alternative).

This module shows how production systems typically integrate LLMs
using LiteLLM instead of building from scratch.

LiteLLM provides:
- Unified interface across providers (OpenAI, Anthropic, Azure, etc.)
- Built-in retry logic with exponential backoff
- Automatic cost tracking
- Fallback mechanisms
- Load balancing

Use this in production. Use llm.py for learning the patterns.
"""

import time
from typing import Optional, Dict, Any, Tuple
from uuid import UUID
import logging

try:
    from litellm import completion, completion_cost
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    completion = None
    completion_cost = None

from app.config import settings
from app.logging import log_error


class LiteLLMResponse:
    """
    Structured response from LiteLLM with metadata.
    
    Same interface as our custom LLMResponse for drop-in replacement.
    """
    def __init__(
        self,
        content: str,
        model: str,
        tokens_used: int,
        latency_ms: float,
        cost_usd: float,
        stop_reason: str,
    ):
        self.content = content
        self.model = model
        self.tokens_used = tokens_used
        self.latency_ms = latency_ms
        self.cost_usd = cost_usd
        self.stop_reason = stop_reason
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "model": self.model,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "cost_usd": self.cost_usd,
            "stop_reason": self.stop_reason,
            "content_length": len(self.content),
        }


class LiteLLMService:
    """
    Production LLM service using LiteLLM.
    
    This shows the production approach: use battle-tested libraries
    instead of building retry logic, cost tracking, etc. from scratch.
    
    Benefits over custom implementation:
    - Provider-agnostic (works with OpenAI, Anthropic, Azure, etc.)
    - Built-in retry logic and error handling
    - Automatic cost calculation
    - Fallback to alternative models
    - Load balancing across deployments
    - Caching support
    """
    
    def __init__(self):
        """Initialize LiteLLM service."""
        if not LITELLM_AVAILABLE:
            raise ImportError(
                "LiteLLM not installed. Install with: pip install litellm"
            )
        
        if not settings.anthropic_api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable."
            )
        
        self.logger = logging.getLogger(__name__)
    
    def summarize_clinical_note(
        self,
        note_text: str,
        audit_id: UUID,
    ) -> Tuple[Optional[LiteLLMResponse], Optional[str]]:
        """
        Summarize a clinical note using LiteLLM.
        
        LiteLLM handles:
        - Retry logic automatically
        - Cost calculation automatically
        - Provider-specific API differences
        - Fallbacks if configured
        
        Args:
            note_text: The clinical note to summarize
            audit_id: Audit ID for traceability
            
        Returns:
            Tuple of (LiteLLMResponse, error_message)
        """
        start_time = time.time()
        
        # Build messages (OpenAI-style format, works across providers)
        messages = [
            {
                "role": "system",
                "content": """You are a clinical documentation assistant. 
Your task is to create a concise summary of clinical notes while preserving all medically relevant information.

Guidelines:
- Include chief complaint, key findings, and plan
- Preserve all medications, dosages, and vital signs
- Use clinical terminology appropriately
- Keep summary under 200 words
- Never add information not in the original note"""
            },
            {
                "role": "user",
                "content": f"""Summarize the following clinical note:

{note_text}

Provide a concise clinical summary."""
            }
        ]
        
        try:
            # LiteLLM handles retry, cost calculation, provider differences
            response = completion(
                model="claude-3-5-sonnet-20241022",  # LiteLLM knows this is Anthropic
                messages=messages,
                max_tokens=1024,
                temperature=0.3,
                timeout=30.0,
                num_retries=2,  # Built-in retry logic
                api_key=settings.anthropic_api_key,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response content
            content = response.choices[0].message.content
            
            # LiteLLM calculates cost automatically
            try:
                cost = completion_cost(completion_response=response)
            except Exception:
                # Fallback if cost calculation fails
                cost = 0.0
            
            llm_response = LiteLLMResponse(
                content=content,
                model=response.model,
                tokens_used=response.usage.total_tokens,
                latency_ms=latency_ms,
                cost_usd=cost,
                stop_reason=response.choices[0].finish_reason,
            )
            
            # Log success
            self.logger.info(
                f"LiteLLM call successful | audit_id={audit_id} | "
                f"latency={latency_ms:.2f}ms | tokens={llm_response.tokens_used} | "
                f"cost=${cost:.6f}"
            )
            
            return llm_response, None
            
        except Exception as e:
            error_msg = f"LiteLLM error: {str(e)}"
            log_error(audit_id, "LiteLLMError", error_msg)
            
            # Check for authentication errors
            if "authentication" in str(e).lower() or "api_key" in str(e).lower():
                raise ValueError(f"Authentication failed: {str(e)}")
            
            return None, error_msg
    
    def validate_response(self, response: LiteLLMResponse) -> Tuple[bool, Optional[str]]:
        """
        Validate LiteLLM response.
        
        Same validation as custom implementation.
        """
        if not response.content or len(response.content.strip()) == 0:
            return False, "Empty response from LLM"
        
        if len(response.content.strip()) < 10:
            return False, "Response too short to be meaningful"
        
        if response.stop_reason not in ["stop", "end_turn"]:
            return False, f"Response incomplete: {response.stop_reason}"
        
        return True, None


# Global service instance
_litellm_service: Optional[LiteLLMService] = None


def get_litellm_service() -> LiteLLMService:
    """
    Get or create global LiteLLM service instance.
    
    Drop-in replacement for get_llm_service().
    """
    global _litellm_service
    if _litellm_service is None:
        _litellm_service = LiteLLMService()
    return _litellm_service