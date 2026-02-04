"""
Tests for API endpoints.

These tests verify:
- Request/response contracts
- Validation behavior
- Error handling
- Audit trail generation
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from uuid import UUID

from app.main import app
from app.models import ClinicalNoteRequest, ClinicalNoteResponse


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def valid_request():
    """Sample valid clinical note request."""
    return {
        "patient_id": "PT-12345",
        "note_text": "Patient presents with acute onset headache. Vital signs stable. Blood pressure 120/80, pulse 72."
    }


class TestHealthEndpoint:
    """Tests for health check endpoint."""
    
    def test_health_check_success(self, client):
        """Health endpoint should return healthy status."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_health_check_schema(self, client):
        """Health endpoint response should match schema."""
        response = client.get("/health")
        data = response.json()
        
        # Verify all required fields are present
        assert "status" in data
        assert "timestamp" in data
        
        # Verify timestamp is valid ISO format
        datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))


class TestRootEndpoint:
    """Tests for root endpoint."""
    
    def test_root_endpoint(self, client):
        """Root endpoint should return service info."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "service" in data
        assert "version" in data
        assert "status" in data


class TestIngestEndpoint:
    """Tests for clinical note ingestion endpoint."""
    
    def test_ingest_valid_request(self, client, valid_request):
        """Valid request should return success with audit ID."""
        response = client.post("/ingest", json=valid_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "audit_id" in data
        assert "received_at" in data
        assert "status" in data
        assert "patient_id" in data
        
        # Verify audit_id is valid UUID
        UUID(data["audit_id"])
        
        # Verify timestamp is valid
        datetime.fromisoformat(data["received_at"].replace("Z", "+00:00"))
        
        # Verify status
        assert data["status"] == "received"
        
        # Verify patient_id matches request
        assert data["patient_id"] == valid_request["patient_id"]
    
    def test_ingest_empty_patient_id(self, client):
        """Empty patient_id should return validation error."""
        request = {
            "patient_id": "",
            "note_text": "Some clinical text"
        }
        
        response = client.post("/ingest", json=request)
        assert response.status_code == 422  # Validation error
    
    def test_ingest_empty_note_text(self, client):
        """Empty note_text should return validation error."""
        request = {
            "patient_id": "PT-12345",
            "note_text": ""
        }
        
        response = client.post("/ingest", json=request)
        assert response.status_code == 422  # Validation error
    
    def test_ingest_whitespace_patient_id(self, client):
        """Whitespace-only patient_id should return validation error."""
        request = {
            "patient_id": "   ",
            "note_text": "Some clinical text"
        }
        
        response = client.post("/ingest", json=request)
        assert response.status_code == 422  # Validation error
    
    def test_ingest_whitespace_note_text(self, client):
        """Whitespace-only note_text should return validation error."""
        request = {
            "patient_id": "PT-12345",
            "note_text": "   "
        }
        
        response = client.post("/ingest", json=request)
        assert response.status_code == 422  # Validation error
    
    def test_ingest_missing_patient_id(self, client):
        """Missing patient_id should return validation error."""
        request = {
            "note_text": "Some clinical text"
        }
        
        response = client.post("/ingest", json=request)
        assert response.status_code == 422
    
    def test_ingest_missing_note_text(self, client):
        """Missing note_text should return validation error."""
        request = {
            "patient_id": "PT-12345"
        }
        
        response = client.post("/ingest", json=request)
        assert response.status_code == 422
    
    def test_ingest_long_note_text(self, client):
        """Very long note_text should be handled correctly."""
        request = {
            "patient_id": "PT-12345",
            "note_text": "A" * 5000  # 5000 character note
        }
        
        response = client.post("/ingest", json=request)
        assert response.status_code == 200
    
    def test_ingest_max_length_note_text(self, client):
        """Note at max length should be accepted."""
        request = {
            "patient_id": "PT-12345",
            "note_text": "A" * 10000  # Max length from model
        }
        
        response = client.post("/ingest", json=request)
        assert response.status_code == 200
    
    def test_ingest_over_max_length_note_text(self, client):
        """Note over max length should be rejected."""
        request = {
            "patient_id": "PT-12345",
            "note_text": "A" * 10001  # Over max length
        }
        
        response = client.post("/ingest", json=request)
        assert response.status_code == 422
    
    def test_ingest_special_characters(self, client):
        """Note with special characters should be handled."""
        request = {
            "patient_id": "PT-12345",
            "note_text": "Patient's BP: 120/80 mmHg. Temp: 98.6°F. Notes: \"stable\""
        }
        
        response = client.post("/ingest", json=request)
        assert response.status_code == 200
    
    def test_ingest_unicode_characters(self, client):
        """Note with unicode should be handled."""
        request = {
            "patient_id": "PT-12345",
            "note_text": "Patient name: José García. Diagnosis: café au lait spots"
        }
        
        response = client.post("/ingest", json=request)
        assert response.status_code == 200
    
    def test_ingest_multiple_requests_unique_audit_ids(self, client, valid_request):
        """Multiple requests should get unique audit IDs."""
        response1 = client.post("/ingest", json=valid_request)
        response2 = client.post("/ingest", json=valid_request)
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        audit_id1 = response1.json()["audit_id"]
        audit_id2 = response2.json()["audit_id"]
        
        assert audit_id1 != audit_id2


class TestProcessTimeHeader:
    """Tests for process time middleware."""
    
    def test_process_time_header_present(self, client):
        """Response should include X-Process-Time header."""
        response = client.get("/health")
        
        assert "X-Process-Time" in response.headers
        
        # Verify it's a valid float
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0


class TestCORS:
    """Tests for CORS configuration."""
    
    def test_cors_headers_present(self, client):
        """CORS headers should be present in response."""
        response = client.options(
            "/ingest",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST"
            }
        )
        
        # CORS preflight should succeed
        assert response.status_code in [200, 204]


class TestSummarizeEndpoint:
    """Tests for /summarize endpoint (Post 2: LLM Integration)."""
    
    def test_summarize_llm_disabled(self, client, valid_request):
        """Summarize should return 503 when LLM is disabled."""
        from unittest.mock import patch
        
        with patch('app.main.settings') as mock_settings:
            mock_settings.llm_enabled = False
            
            response = client.post("/summarize", json=valid_request)
            
            assert response.status_code == 503
            # Response could be either error format
            data = response.json()
            response_text = str(data).lower()
            assert "not enabled" in response_text or "llm" in response_text
    
    def test_summarize_success(self, client, valid_request):
        """Successful summarization should return summary with metrics."""
        from unittest.mock import patch, Mock
        from app.llm import LLMResponse
        from uuid import UUID
        
        # Mock LLM service to return success
        mock_response = LLMResponse(
            content="Patient presents with headache. Vital signs stable.",
            model="claude-3-5-sonnet-20241022",
            tokens_used=350,
            latency_ms=1250.0,
            cost_usd=0.00525,
            stop_reason="end_turn"
        )
        
        with patch('app.main.settings') as mock_settings:
            mock_settings.llm_enabled = True
            
            with patch('app.main.get_llm_service') as mock_get_service:
                mock_service = Mock()
                mock_service.summarize_clinical_note.return_value = (mock_response, None)
                mock_service.validate_response.return_value = (True, None)
                mock_get_service.return_value = mock_service
                
                response = client.post("/summarize", json=valid_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "audit_id" in data
        assert "received_at" in data
        assert "status" in data
        assert "patient_id" in data
        assert "summary" in data
        assert "llm_metrics" in data
        assert "error" in data
        
        # Verify audit_id is valid UUID
        UUID(data["audit_id"])
        
        # Verify status
        assert data["status"] == "completed"
        
        # Verify summary
        assert data["summary"] is not None
        assert len(data["summary"]) > 0
        
        # Verify metrics
        metrics = data["llm_metrics"]
        assert metrics["model"] == "claude-3-5-sonnet-20241022"
        assert metrics["tokens_used"] == 350
        assert metrics["latency_ms"] == 1250.0
        assert metrics["cost_usd"] == 0.00525
        
        # Verify no error
        assert data["error"] is None
    
    def test_summarize_llm_failure(self, client, valid_request):
        """LLM failure should return error response."""
        from unittest.mock import patch, Mock
        
        with patch('app.main.settings') as mock_settings:
            mock_settings.llm_enabled = True
            
            with patch('app.main.get_llm_service') as mock_get_service:
                mock_service = Mock()
                mock_service.summarize_clinical_note.return_value = (None, "LLM API timeout")
                mock_get_service.return_value = mock_service
                
                response = client.post("/summarize", json=valid_request)
        
        assert response.status_code == 200  # Graceful degradation
        data = response.json()
        
        assert data["status"] == "failed"
        assert data["summary"] is None
        assert data["llm_metrics"] is None
        assert data["error"] is not None
        assert "timeout" in data["error"].lower()
    
    def test_summarize_validation_failure(self, client, valid_request):
        """Validation failure should return error response."""
        from unittest.mock import patch, Mock
        from app.llm import LLMResponse
        
        mock_response = LLMResponse(
            content="Short",
            model="claude-3-5-sonnet-20241022",
            tokens_used=50,
            latency_ms=500.0,
            cost_usd=0.001,
            stop_reason="end_turn"
        )
        
        with patch('app.main.settings') as mock_settings:
            mock_settings.llm_enabled = True
            
            with patch('app.main.get_llm_service') as mock_get_service:
                mock_service = Mock()
                mock_service.summarize_clinical_note.return_value = (mock_response, None)
                mock_service.validate_response.return_value = (False, "Response too short")
                mock_get_service.return_value = mock_service
                
                response = client.post("/summarize", json=valid_request)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "failed"
        assert data["summary"] is None
        assert data["error"] is not None
        assert "validation failed" in data["error"].lower()
    
    def test_summarize_empty_patient_id(self, client):
        """Empty patient_id should return validation error."""
        request = {
            "patient_id": "",
            "note_text": "Some clinical text"
        }
        
        response = client.post("/summarize", json=request)
        assert response.status_code == 422
    
    def test_summarize_empty_note_text(self, client):
        """Empty note_text should return validation error."""
        request = {
            "patient_id": "PT-12345",
            "note_text": ""
        }
        
        response = client.post("/summarize", json=request)
        assert response.status_code == 422
    
    def test_summarize_missing_api_key(self, client, valid_request):
        """Missing API key should return 503."""
        from unittest.mock import patch
        
        with patch('app.main.settings') as mock_settings:
            mock_settings.llm_enabled = True
            
            with patch('app.main.get_llm_service') as mock_get_service:
                mock_get_service.side_effect = ValueError("Anthropic API key required")
                
                response = client.post("/summarize", json=valid_request)
        
        assert response.status_code == 503
    
    def test_summarize_unexpected_error(self, client, valid_request):
        """Unexpected errors should be handled gracefully."""
        from unittest.mock import patch, Mock
        
        with patch('app.main.settings') as mock_settings:
            mock_settings.llm_enabled = True
            
            with patch('app.main.get_llm_service') as mock_get_service:
                mock_service = Mock()
                mock_service.summarize_clinical_note.side_effect = Exception("Unexpected error")
                mock_get_service.return_value = mock_service
                
                response = client.post("/summarize", json=valid_request)
        
        assert response.status_code == 200  # Graceful degradation
        data = response.json()
        
        assert data["status"] == "failed"
        assert data["error"] is not None
    
    def test_summarize_audit_trail_maintained(self, client, valid_request):
        """Audit trail should be maintained even on failure."""
        from unittest.mock import patch, Mock
        
        with patch('app.main.settings') as mock_settings:
            mock_settings.llm_enabled = True
            
            with patch('app.main.get_llm_service') as mock_get_service:
                mock_service = Mock()
                mock_service.summarize_clinical_note.return_value = (None, "Error")
                mock_get_service.return_value = mock_service
                
                response = client.post("/summarize", json=valid_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify audit_id is present even on failure
        assert "audit_id" in data
        from uuid import UUID
        UUID(data["audit_id"])
    
    def test_summarize_long_note(self, client):
        """Long clinical notes should be handled."""
        from unittest.mock import patch, Mock
        from app.llm import LLMResponse
        
        long_note = "Patient history. " * 500  # ~8500 chars
        
        request = {
            "patient_id": "PT-12345",
            "note_text": long_note
        }
        
        mock_response = LLMResponse(
            content="Summarized clinical note",
            model="claude-3-5-sonnet-20241022",
            tokens_used=2000,
            latency_ms=3000.0,
            cost_usd=0.030,
            stop_reason="end_turn"
        )
        
        with patch('app.main.settings') as mock_settings:
            mock_settings.llm_enabled = True
            
            with patch('app.main.get_llm_service') as mock_get_service:
                mock_service = Mock()
                mock_service.summarize_clinical_note.return_value = (mock_response, None)
                mock_service.validate_response.return_value = (True, None)
                mock_get_service.return_value = mock_service
                
                response = client.post("/summarize", json=request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
