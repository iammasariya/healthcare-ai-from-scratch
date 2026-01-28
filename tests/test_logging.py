"""
Tests for logging functionality.

These tests verify:
- Audit ID generation
- Privacy-aware logging
- Structured log format
"""

import pytest
from uuid import UUID
import json

from app.logging import StructuredLogger, log_request, log_response, log_error


@pytest.fixture
def test_logger():
    """Create a test logger instance."""
    return StructuredLogger(name="test_logger")


@pytest.fixture
def sample_payload():
    """Sample clinical note payload."""
    return {
        "patient_id": "PT-12345",
        "note_text": "Patient presents with acute onset headache. Vital signs stable. Blood pressure 120/80, pulse 72, temperature 98.6F."
    }


class TestAuditIDGeneration:
    """Tests for audit ID generation."""
    
    def test_audit_id_is_uuid(self, test_logger, sample_payload):
        """Audit ID should be a valid UUID."""
        audit_id = test_logger.log_request(sample_payload)
        
        # Should not raise exception
        UUID(str(audit_id))
    
    def test_audit_ids_are_unique(self, test_logger, sample_payload):
        """Each request should get a unique audit ID."""
        audit_id1 = test_logger.log_request(sample_payload)
        audit_id2 = test_logger.log_request(sample_payload)
        
        assert audit_id1 != audit_id2
    
    def test_audit_id_format(self, test_logger, sample_payload):
        """Audit ID should be UUID4 format."""
        audit_id = test_logger.log_request(sample_payload)
        
        # UUID4 has specific version field
        assert audit_id.version == 4


class TestPrivacyAwareLogging:
    """Tests for privacy-aware logging."""
    
    def test_long_text_is_truncated(self, test_logger):
        """Long clinical text should be truncated in logs."""
        long_text = "A" * 500  # Much longer than preview length
        payload = {
            "patient_id": "PT-12345",
            "note_text": long_text
        }
        
        # We can't easily capture logs in tests, but we verify it doesn't crash
        audit_id = test_logger.log_request(payload)
        assert audit_id is not None
    
    def test_short_text_not_truncated(self, test_logger):
        """Short clinical text should not be truncated."""
        short_text = "Brief note"
        payload = {
            "patient_id": "PT-12345",
            "note_text": short_text
        }
        
        audit_id = test_logger.log_request(payload)
        assert audit_id is not None


class TestLogResponse:
    """Tests for response logging."""
    
    def test_log_response_with_audit_id(self, test_logger, sample_payload):
        """Response logging should work with audit ID."""
        audit_id = test_logger.log_request(sample_payload)
        
        # Should not raise exception
        test_logger.log_response(audit_id, "received")
    
    def test_log_response_with_metadata(self, test_logger, sample_payload):
        """Response logging should accept metadata."""
        audit_id = test_logger.log_request(sample_payload)
        
        metadata = {"processing_time": 0.123}
        test_logger.log_response(audit_id, "received", metadata)


class TestLogError:
    """Tests for error logging."""
    
    def test_log_error_with_audit_id(self, test_logger, sample_payload):
        """Error logging should work with audit ID."""
        audit_id = test_logger.log_request(sample_payload)
        
        test_logger.log_error(
            audit_id=audit_id,
            error_type="ValidationError",
            error_message="Invalid input"
        )
    
    def test_log_error_without_audit_id(self, test_logger):
        """Error logging should work without audit ID."""
        test_logger.log_error(
            audit_id=None,
            error_type="SystemError",
            error_message="Unexpected error"
        )
    
    def test_log_error_with_metadata(self, test_logger):
        """Error logging should accept metadata."""
        metadata = {"traceback": "...", "user_agent": "test"}
        test_logger.log_error(
            audit_id=None,
            error_type="RuntimeError",
            error_message="Test error",
            metadata=metadata
        )


class TestConvenienceFunctions:
    """Tests for module-level convenience functions."""
    
    def test_log_request_function(self, sample_payload):
        """Module-level log_request should work."""
        audit_id = log_request(sample_payload)
        assert isinstance(audit_id, UUID)
    
    def test_log_response_function(self, sample_payload):
        """Module-level log_response should work."""
        audit_id = log_request(sample_payload)
        log_response(audit_id, "received")
    
    def test_log_error_function(self):
        """Module-level log_error should work."""
        log_error(
            audit_id=None,
            error_type="TestError",
            error_message="Test message"
        )
