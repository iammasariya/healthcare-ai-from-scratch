"""
LLM integration layer with resilience and observability.

This module provides a production-grade interface to LLMs (Claude)
with the reliability guarantees healthcare systems require:
- Timeouts and retries
- Cost tracking
- Latency monitoring
- Response validation
- Graceful degradation
"""

import time
import anthropic
from typing import Optional, Dict, Any, Tuple
from uuid import UUID
import logging

from app.config import settings
from app.logging import log_error


class LLMConfig:
    """
    Configuration for LLM behavior.
    
    These settings control reliability, cost, and quality tradeoffs.
    """
    def __init__(
        self,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 1024,
        temperature: float = 0.3,
        timeout: float = 30.0,
        max_retries: int = 2,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.timeout = timeout
        self.max_retries = max_retries


class LLMResponse:
    """
    Structured response from LLM with metadata.
    
    Attributes:
        content: The actual LLM response text
        model: Model used for generation
        tokens_used: Total tokens consumed (input + output)
        latency_ms: Time taken for API call in milliseconds
        cost_usd: Estimated cost in USD
        stop_reason: Why the model stopped generating
        prompt_version: Version of prompt used (optional, for versioned prompts)
        prompt_hash: SHA256 hash of prompt (optional, for integrity verification)
    """
    def __init__(
        self,
        content: str,
        model: str,
        tokens_used: int,
        latency_ms: float,
        cost_usd: float,
        stop_reason: str,
        prompt_version: Optional[str] = None,
        prompt_hash: Optional[str] = None,
    ):
        self.content = content
        self.model = model
        self.tokens_used = tokens_used
        self.latency_ms = latency_ms
        self.cost_usd = cost_usd
        self.stop_reason = stop_reason
        self.prompt_version = prompt_version
        self.prompt_hash = prompt_hash
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        result = {
            "model": self.model,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms,
            "cost_usd": self.cost_usd,
            "stop_reason": self.stop_reason,
            "content_length": len(self.content),
        }
        if self.prompt_version:
            result["prompt_version"] = self.prompt_version
        if self.prompt_hash:
            result["prompt_hash"] = self.prompt_hash[:8] + "..."  # Log only prefix
        return result


class LLMError(Exception):
    """
    LLM-specific errors.
    
    Wraps underlying API errors with healthcare-appropriate context.
    """
    def __init__(self, message: str, original_error: Optional[Exception] = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class LLMService:
    """
    Production-grade LLM service with healthcare reliability requirements.
    
    This service wraps the Anthropic API with:
    - Automatic retries with exponential backoff
    - Timeout handling
    - Cost tracking
    - Latency monitoring
    - Structured logging
    
    Design decisions:
    - Synchronous by default (easier to reason about failures)
    - Explicit timeouts (never wait forever)
    - Cost tracking (healthcare budgets are real)
    - Detailed error context (debugging at 2am matters)
    """
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[LLMConfig] = None):
        """
        Initialize LLM service.
        
        Args:
            api_key: Anthropic API key (falls back to settings)
            config: LLM configuration (uses defaults if not provided)
        """
        self.api_key = api_key or settings.anthropic_api_key
        self.config = config or LLMConfig()
        
        if not self.api_key:
            raise ValueError(
                "Anthropic API key required. Set ANTHROPIC_API_KEY environment variable."
            )
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.logger = logging.getLogger(__name__)
    
    def summarize_clinical_note(
        self,
        note_text: str,
        audit_id: UUID,
        prompt_version: Optional[str] = None,
        use_versioned_prompts: bool = True,
    ) -> Tuple[Optional[LLMResponse], Optional[str]]:
        """
        Summarize a clinical note using Claude with versioned prompts.
        
        This demonstrates:
        - How to call the LLM safely
        - How to handle failures
        - How to track costs and latency
        - How to maintain audit trails
        - How to use versioned prompts for reproducibility
        
        Args:
            note_text: The clinical note to summarize
            audit_id: Audit ID for traceability
            prompt_version: Specific prompt version to use (uses latest if None)
            use_versioned_prompts: If True, load from prompt manager; if False, use legacy hardcoded prompts
            
        Returns:
            Tuple of (LLMResponse, error_message)
            If successful: (response, None)
            If failed: (None, error_description)
        """
        start_time = time.time()
        
        # Initialize prompt metadata
        prompt_v = None
        prompt_h = None
        
        # Load prompts (versioned or legacy)
        if use_versioned_prompts:
            try:
                from app.prompts import get_prompt_manager
                
                # Load versioned prompt
                prompt_manager = get_prompt_manager()
                prompt = prompt_manager.get_prompt(
                    task="clinical_summarization",
                    version=prompt_version
                )
                
                if not prompt:
                    error_msg = f"Prompt not found: clinical_summarization v{prompt_version or 'latest'}"
                    log_error(audit_id, "PromptNotFoundError", error_msg)
                    return None, error_msg
                
                # Verify prompt integrity
                if not prompt_manager.validate_prompt_integrity(prompt):
                    error_msg = f"Prompt integrity check failed for v{prompt.version}"
                    log_error(audit_id, "PromptIntegrityError", error_msg)
                    return None, error_msg
                
                # Render user prompt with actual note text
                system_prompt = prompt.system_prompt
                user_prompt = prompt_manager.render_user_prompt(
                    prompt,
                    note_text=note_text
                )
                
                # Store prompt metadata for logging
                prompt_v = prompt.version
                prompt_h = prompt.prompt_hash
                
                # Log which prompt version we're using
                self.logger.info(
                    f"Using prompt version {prompt.version} | "
                    f"hash={prompt.prompt_hash[:8]} | audit_id={audit_id}"
                )
                
            except Exception as e:
                error_msg = f"Error loading versioned prompt: {str(e)}"
                log_error(audit_id, "PromptLoadError", error_msg)
                return None, error_msg
        else:
            # Legacy: Use hardcoded prompts for backward compatibility
            system_prompt = """You are a clinical documentation assistant. 
Your task is to create a concise summary of clinical notes while preserving all medically relevant information.

Guidelines:
- Include chief complaint, key findings, and plan
- Preserve all medications, dosages, and vital signs
- Use clinical terminology appropriately
- Keep summary under 200 words
- Never add information not in the original note"""

            user_prompt = f"""Summarize the following clinical note:

{note_text}

Provide a concise clinical summary."""
            
            self.logger.info(f"Using legacy hardcoded prompts | audit_id={audit_id}")

        try:
            # Attempt API call with retries
            response = self._call_with_retry(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                audit_id=audit_id,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract response content
            content = response.content[0].text if response.content else ""
            
            # Calculate cost (approximate, based on Claude pricing)
            # Input: $3 per million tokens
            # Output: $15 per million tokens
            input_cost = (response.usage.input_tokens / 1_000_000) * 3.0
            output_cost = (response.usage.output_tokens / 1_000_000) * 15.0
            total_cost = input_cost + output_cost
            
            llm_response = LLMResponse(
                content=content,
                model=response.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens,
                latency_ms=latency_ms,
                cost_usd=total_cost,
                stop_reason=response.stop_reason,
                prompt_version=prompt_v,
                prompt_hash=prompt_h,
            )
            
            # Log success metrics (including prompt version if available)
            log_parts = [
                f"LLM call successful | audit_id={audit_id}",
                f"latency={latency_ms:.2f}ms",
                f"tokens={llm_response.tokens_used}",
                f"cost=${total_cost:.6f}",
            ]
            if prompt_v:
                log_parts.append(f"prompt_version={prompt_v}")
            
            self.logger.info(" | ".join(log_parts))
            
            return llm_response, None
            
        except anthropic.APITimeoutError as e:
            error_msg = f"LLM API timeout after {self.config.timeout}s"
            log_error(audit_id, "LLMTimeoutError", error_msg, {"retries": self.config.max_retries})
            return None, error_msg
            
        except anthropic.RateLimitError as e:
            error_msg = "LLM API rate limit exceeded"
            log_error(audit_id, "LLMRateLimitError", error_msg)
            return None, error_msg
            
        except anthropic.AuthenticationError as e:
            error_msg = f"LLM authentication failed: {str(e)}"
            log_error(audit_id, "LLMAuthenticationError", error_msg)
            # Authentication errors should not be retried
            raise ValueError(error_msg)
            
        except anthropic.APIError as e:
            error_msg = f"LLM API error: {str(e)}"
            log_error(audit_id, "LLMAPIError", error_msg)
            return None, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error calling LLM: {str(e)}"
            log_error(audit_id, "LLMUnexpectedError", error_msg)
            return None, error_msg
    
    def _call_with_retry(
        self,
        system_prompt: str,
        user_prompt: str,
        audit_id: UUID,
    ) -> anthropic.types.Message:
        """
        Call Claude API with exponential backoff retry.
        
        Retry strategy:
        - First attempt: immediate
        - Second attempt: wait 1 second
        - Third attempt: wait 2 seconds
        
        Only retries on transient failures (timeout, rate limit).
        Does not retry on validation errors or auth failures.
        """
        last_error = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                if attempt > 0:
                    # Exponential backoff: 1s, 2s, 4s, etc.
                    wait_time = 2 ** (attempt - 1)
                    self.logger.info(
                        f"Retrying LLM call (attempt {attempt + 1}/{self.config.max_retries + 1}) "
                        f"after {wait_time}s | audit_id={audit_id}"
                    )
                    time.sleep(wait_time)
                
                response = self.client.messages.create(
                    model=self.config.model,
                    max_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ],
                    timeout=self.config.timeout,
                )
                
                return response
                
            except (anthropic.APITimeoutError, anthropic.RateLimitError) as e:
                # These are retriable errors
                last_error = e
                if attempt == self.config.max_retries:
                    raise
                continue
                
            except anthropic.APIError as e:
                # Non-retriable API errors
                raise
        
        # Should not reach here, but if we do, raise the last error
        if last_error:
            raise last_error
        raise LLMError("Max retries exceeded without clear error")
    
    def validate_response(self, response: LLMResponse) -> Tuple[bool, Optional[str]]:
        """
        Validate LLM response meets basic quality criteria.
        
        In production, this would check:
        - Response length is reasonable
        - No hallucinated information
        - Proper medical terminology
        - Required sections present
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation: response should not be empty
        if not response.content or len(response.content.strip()) == 0:
            return False, "Empty response from LLM"
        
        # Check minimum length (should be a real summary, not just "N/A")
        if len(response.content.strip()) < 10:
            return False, "Response too short to be meaningful"
        
        # Check for complete generation (didn't hit max tokens)
        if response.stop_reason != "end_turn":
            return False, f"Response incomplete: {response.stop_reason}"
        
        # More validation would go here in production:
        # - Check for required sections
        # - Validate medical terminology
        # - Check for hallucinations
        # - Verify no PII leakage
        
        return True, None


# Global service instance (initialized on first use)
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """
    Get or create global LLM service instance.
    
    Uses singleton pattern to reuse HTTP connections.
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service