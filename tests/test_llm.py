"""
Tests for LLM service layer.

These tests verify:
- LLM configuration
- Response handling
- Error handling
- Retry logic
- Cost tracking
- Response validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
import anthropic

from app.llm import (
    LLMConfig,
    LLMResponse,
    LLMService,
    LLMError,
    get_llm_service
)


class TestLLMConfig:
    """Tests for LLM configuration."""
    
    def test_default_config(self):
        """Default config should have sensible values."""
        config = LLMConfig()
        
        assert config.model == "claude-3-5-sonnet-20241022"
        assert config.max_tokens == 1024
        assert config.temperature == 0.3
        assert config.timeout == 30.0
        assert config.max_retries == 2
    
    def test_custom_config(self):
        """Custom config values should be respected."""
        config = LLMConfig(
            model="claude-3-opus-20240229",
            max_tokens=2048,
            temperature=0.5,
            timeout=60.0,
            max_retries=3
        )
        
        assert config.model == "claude-3-opus-20240229"
        assert config.max_tokens == 2048
        assert config.temperature == 0.5
        assert config.timeout == 60.0
        assert config.max_retries == 3


class TestLLMResponse:
    """Tests for LLM response model."""
    
    def test_response_creation(self):
        """Response should be created with all fields."""
        response = LLMResponse(
            content="Test summary",
            model="claude-3-5-sonnet-20241022",
            tokens_used=500,
            latency_ms=1234.56,
            cost_usd=0.00675,
            stop_reason="end_turn"
        )
        
        assert response.content == "Test summary"
        assert response.model == "claude-3-5-sonnet-20241022"
        assert response.tokens_used == 500
        assert response.latency_ms == 1234.56
        assert response.cost_usd == 0.00675
        assert response.stop_reason == "end_turn"
    
    def test_response_to_dict(self):
        """Response should convert to dict for logging."""
        response = LLMResponse(
            content="Test summary",
            model="claude-3-5-sonnet-20241022",
            tokens_used=500,
            latency_ms=1234.56,
            cost_usd=0.00675,
            stop_reason="end_turn"
        )
        
        data = response.to_dict()
        
        assert data["model"] == "claude-3-5-sonnet-20241022"
        assert data["tokens_used"] == 500
        assert data["latency_ms"] == 1234.56
        assert data["cost_usd"] == 0.00675
        assert data["stop_reason"] == "end_turn"
        assert data["content_length"] == len("Test summary")


class TestLLMService:
    """Tests for LLM service."""
    
    def test_service_initialization_with_api_key(self):
        """Service should initialize with API key."""
        service = LLMService(api_key="test-key")
        assert service.api_key == "test-key"
        assert service.config is not None
    
    def test_service_initialization_without_api_key(self):
        """Service should raise error without API key."""
        with patch('app.llm.settings') as mock_settings:
            mock_settings.anthropic_api_key = None
            
            with pytest.raises(ValueError, match="Anthropic API key required"):
                LLMService()
    
    def test_service_initialization_with_custom_config(self):
        """Service should accept custom config."""
        config = LLMConfig(max_tokens=2048)
        service = LLMService(api_key="test-key", config=config)
        
        assert service.config.max_tokens == 2048
    
    @patch('app.llm.anthropic.Anthropic')
    def test_summarize_clinical_note_success(self, mock_anthropic_class):
        """Successful summarization should return response."""
        # Mock the Anthropic client
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        # Mock the API response
        mock_response = Mock()
        mock_response.content = [Mock(text="Clinical summary here")]
        mock_response.model = "claude-3-5-sonnet-20241022"
        mock_response.usage = Mock(input_tokens=200, output_tokens=100)
        mock_response.stop_reason = "end_turn"
        
        mock_client.messages.create.return_value = mock_response
        
        # Create service and call
        service = LLMService(api_key="test-key")
        audit_id = uuid4()
        
        response, error = service.summarize_clinical_note(
            "Patient presents with headache.",
            audit_id
        )
        
        # Verify success
        assert error is None
        assert response is not None
        assert response.content == "Clinical summary here"
        assert response.tokens_used == 300  # 200 + 100
        assert response.cost_usd > 0
    
    @patch('app.llm.anthropic.Anthropic')
    def test_summarize_timeout_error(self, mock_anthropic_class):
        """Timeout should return error message."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        # Mock timeout error
        mock_client.messages.create.side_effect = anthropic.APITimeoutError("Timeout")
        
        service = LLMService(api_key="test-key")
        audit_id = uuid4()
        
        response, error = service.summarize_clinical_note(
            "Patient presents with headache.",
            audit_id
        )
        
        assert response is None
        assert error is not None
        assert "timeout" in error.lower()
    
    @patch('app.llm.anthropic.Anthropic')
    def test_summarize_rate_limit_error(self, mock_anthropic_class):
        """Rate limit should return error message."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        # Mock rate limit error with proper initialization
        mock_response = Mock()
        mock_response.status_code = 429
        rate_limit_error = anthropic.RateLimitError(
            "Rate limit exceeded",
            response=mock_response,
            body={"error": {"message": "Rate limit exceeded"}}
        )
        mock_client.messages.create.side_effect = rate_limit_error
        
        service = LLMService(api_key="test-key")
        audit_id = uuid4()
        
        response, error = service.summarize_clinical_note(
            "Patient presents with headache.",
            audit_id
        )
        
        assert response is None
        assert error is not None
        assert "rate limit" in error.lower()
    
    @patch('app.llm.anthropic.Anthropic')
    def test_summarize_authentication_error(self, mock_anthropic_class):
        """Authentication error should raise ValueError."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        # Mock auth error with proper initialization
        mock_response = Mock()
        mock_response.status_code = 401
        auth_error = anthropic.AuthenticationError(
            "Invalid API key",
            response=mock_response,
            body={"error": {"message": "Invalid API key"}}
        )
        mock_client.messages.create.side_effect = auth_error
        
        service = LLMService(api_key="test-key")
        audit_id = uuid4()
        
        with pytest.raises(ValueError, match="authentication failed"):
            service.summarize_clinical_note(
                "Patient presents with headache.",
                audit_id
            )
    
    @patch('app.llm.anthropic.Anthropic')
    def test_summarize_api_error(self, mock_anthropic_class):
        """API error should return error message."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        # Mock API error with proper initialization
        mock_request = Mock()
        api_error = anthropic.APIError(
            "API error",
            request=mock_request,
            body={"error": {"message": "API error"}}
        )
        mock_client.messages.create.side_effect = api_error
        
        service = LLMService(api_key="test-key")
        audit_id = uuid4()
        
        response, error = service.summarize_clinical_note(
            "Patient presents with headache.",
            audit_id
        )
        
        assert response is None
        assert error is not None
        assert "API error" in error
    
    @patch('app.llm.anthropic.Anthropic')
    def test_summarize_unexpected_error(self, mock_anthropic_class):
        """Unexpected error should return error message."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        # Mock unexpected error
        mock_client.messages.create.side_effect = Exception("Unexpected")
        
        service = LLMService(api_key="test-key")
        audit_id = uuid4()
        
        response, error = service.summarize_clinical_note(
            "Patient presents with headache.",
            audit_id
        )
        
        assert response is None
        assert error is not None
        assert "Unexpected" in error
    
    def test_validate_response_success(self):
        """Valid response should pass validation."""
        service = LLMService(api_key="test-key")
        
        response = LLMResponse(
            content="This is a valid clinical summary.",
            model="claude-3-5-sonnet-20241022",
            tokens_used=100,
            latency_ms=1000.0,
            cost_usd=0.001,
            stop_reason="end_turn"
        )
        
        is_valid, error = service.validate_response(response)
        
        assert is_valid is True
        assert error is None
    
    def test_validate_response_empty_content(self):
        """Empty content should fail validation."""
        service = LLMService(api_key="test-key")
        
        response = LLMResponse(
            content="",
            model="claude-3-5-sonnet-20241022",
            tokens_used=100,
            latency_ms=1000.0,
            cost_usd=0.001,
            stop_reason="end_turn"
        )
        
        is_valid, error = service.validate_response(response)
        
        assert is_valid is False
        assert error is not None
        assert "empty" in error.lower()
    
    def test_validate_response_too_short(self):
        """Too short content should fail validation."""
        service = LLMService(api_key="test-key")
        
        response = LLMResponse(
            content="Short",
            model="claude-3-5-sonnet-20241022",
            tokens_used=100,
            latency_ms=1000.0,
            cost_usd=0.001,
            stop_reason="end_turn"
        )
        
        is_valid, error = service.validate_response(response)
        
        assert is_valid is False
        assert error is not None
        assert "too short" in error.lower()
    
    def test_validate_response_incomplete(self):
        """Incomplete response should fail validation."""
        service = LLMService(api_key="test-key")
        
        response = LLMResponse(
            content="This is a valid summary",
            model="claude-3-5-sonnet-20241022",
            tokens_used=100,
            latency_ms=1000.0,
            cost_usd=0.001,
            stop_reason="max_tokens"  # Incomplete
        )
        
        is_valid, error = service.validate_response(response)
        
        assert is_valid is False
        assert error is not None
        assert "incomplete" in error.lower()


class TestCostCalculation:
    """Tests for cost tracking."""
    
    @patch('app.llm.anthropic.Anthropic')
    def test_cost_calculation_accuracy(self, mock_anthropic_class):
        """Cost should be calculated accurately."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        # Mock response with known token counts
        mock_response = Mock()
        mock_response.content = [Mock(text="Summary")]
        mock_response.model = "claude-3-5-sonnet-20241022"
        mock_response.usage = Mock(
            input_tokens=1_000_000,  # 1M tokens
            output_tokens=1_000_000   # 1M tokens
        )
        mock_response.stop_reason = "end_turn"
        
        mock_client.messages.create.return_value = mock_response
        
        service = LLMService(api_key="test-key")
        audit_id = uuid4()
        
        response, error = service.summarize_clinical_note(
            "Test note",
            audit_id
        )
        
        # Expected cost:
        # Input: 1M * $3/M = $3.00
        # Output: 1M * $15/M = $15.00
        # Total: $18.00
        assert response.cost_usd == 18.0


class TestGetLLMService:
    """Tests for service singleton."""
    
    @patch('app.llm.LLMService')
    def test_get_llm_service_singleton(self, mock_service_class):
        """get_llm_service should return singleton."""
        # Reset the singleton
        import app.llm
        app.llm._llm_service = None
        
        mock_instance = Mock()
        mock_service_class.return_value = mock_instance
        
        # First call should create instance
        service1 = get_llm_service()
        assert mock_service_class.call_count == 1
        
        # Second call should return same instance
        service2 = get_llm_service()
        assert mock_service_class.call_count == 1  # Not called again
        
        assert service1 is service2


class TestLLMError:
    """Tests for LLMError exception."""
    
    def test_llm_error_with_message(self):
        """LLMError should be created with message."""
        error = LLMError("Test error message")
        assert str(error) == "Test error message"
        assert error.message == "Test error message"
        assert error.original_error is None
    
    def test_llm_error_with_original_error(self):
        """LLMError should capture original error."""
        original = ValueError("Original error")
        error = LLMError("Wrapped error", original_error=original)
        assert str(error) == "Wrapped error"
        assert error.message == "Wrapped error"
        assert error.original_error is original


class TestRetryEdgeCases:
    """Tests for retry logic edge cases."""
    
    @patch('app.llm.anthropic.Anthropic')
    def test_retry_fallthrough_raises_last_error(self, mock_anthropic_class):
        """If all retries fail, should raise the last error."""
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        
        # Mock timeout on all attempts
        mock_client.messages.create.side_effect = anthropic.APITimeoutError("Timeout")
        
        service = LLMService(api_key="test-key", config=LLMConfig(max_retries=1))
        audit_id = uuid4()
        
        # This should exhaust retries and return error
        response, error = service.summarize_clinical_note(
            "Test note",
            audit_id
        )
        
        assert response is None
        assert error is not None
        assert "timeout" in error.lower()
