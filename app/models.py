"""
Pydantic models for request and response validation.

These models define the contract between the API and its clients.
In healthcare systems, these contracts should be stable and versioned,
as they outlive any individual model or algorithm.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional


class ClinicalNoteRequest(BaseModel):
    """
    Request model for ingesting clinical notes.
    
    Attributes:
        patient_id: Unique identifier for the patient (not PHI in real systems)
        note_text: The clinical note content to be processed
    """
    patient_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique patient identifier",
        examples=["PT-12345"]
    )
    note_text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Clinical note content",
        examples=["Patient presents with acute onset headache. Vital signs stable."]
    )
    
    @field_validator('patient_id')
    @classmethod
    def validate_patient_id(cls, v: str) -> str:
        """Ensure patient_id follows expected format."""
        if not v.strip():
            raise ValueError("patient_id cannot be empty or whitespace")
        return v.strip()
    
    @field_validator('note_text')
    @classmethod
    def validate_note_text(cls, v: str) -> str:
        """Ensure note_text is not empty."""
        if not v.strip():
            raise ValueError("note_text cannot be empty or whitespace")
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "PT-12345",
                "note_text": "Patient presents with acute onset headache. Vital signs stable. Blood pressure 120/80, pulse 72, temperature 98.6F."
            }
        }


class ClinicalNoteResponse(BaseModel):
    """
    Response model for clinical note ingestion.
    
    Attributes:
        audit_id: Unique identifier for this request (for traceability)
        received_at: Timestamp when the request was received
        status: Current status of the request
        patient_id: Echo back the patient_id for verification
    """
    audit_id: UUID = Field(
        ...,
        description="Unique audit identifier for request tracing"
    )
    received_at: datetime = Field(
        ...,
        description="UTC timestamp when request was received"
    )
    status: str = Field(
        ...,
        description="Current status of the request",
        examples=["received", "processing", "completed"]
    )
    patient_id: Optional[str] = Field(
        None,
        description="Patient identifier (echoed back for verification)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "audit_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "received_at": "2026-01-27T10:30:45.123456Z",
                "status": "received",
                "patient_id": "PT-12345"
            }
        }


class HealthResponse(BaseModel):
    """
    Health check response model.
    
    Used for monitoring and readiness probes in production.
    """
    status: str = Field(
        ...,
        description="Service health status",
        examples=["healthy", "degraded", "unhealthy"]
    )
    timestamp: datetime = Field(
        ...,
        description="UTC timestamp of health check"
    )
    version: Optional[str] = Field(
        None,
        description="Service version"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-01-27T10:30:45.123456Z",
                "version": "0.1.0"
            }
        }


class ErrorResponse(BaseModel):
    """
    Standard error response model.
    
    Provides consistent error reporting across the API.
    """
    error: str = Field(
        ...,
        description="Error type or code"
    )
    message: str = Field(
        ...,
        description="Human-readable error message"
    )
    audit_id: Optional[UUID] = Field(
        None,
        description="Audit ID if request was logged before failing"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp of error"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "note_text cannot be empty or whitespace",
                "audit_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "timestamp": "2026-01-27T10:30:45.123456Z"
            }
        }


class LLMMetrics(BaseModel):
    """
    Metadata about LLM processing.
    
    Tracks cost, latency, and token usage for observability.
    """
    model: str = Field(
        ...,
        description="LLM model used"
    )
    tokens_used: int = Field(
        ...,
        description="Total tokens consumed (input + output)"
    )
    latency_ms: float = Field(
        ...,
        description="Time taken for LLM call in milliseconds"
    )
    cost_usd: float = Field(
        ...,
        description="Estimated cost in USD"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "model": "claude-3-5-sonnet-20241022",
                "tokens_used": 450,
                "latency_ms": 1234.56,
                "cost_usd": 0.006750
            }
        }


class SummarizeNoteResponse(BaseModel):
    """
    Response model for clinical note summarization.
    
    Extends the base response with LLM-generated summary and metrics.
    """
    audit_id: UUID = Field(
        ...,
        description="Unique audit identifier for request tracing"
    )
    received_at: datetime = Field(
        ...,
        description="UTC timestamp when request was received"
    )
    status: str = Field(
        ...,
        description="Current status of the request",
        examples=["completed", "failed", "fallback"]
    )
    patient_id: Optional[str] = Field(
        None,
        description="Patient identifier (echoed back for verification)"
    )
    summary: Optional[str] = Field(
        None,
        description="Generated clinical summary (if successful)"
    )
    llm_metrics: Optional[LLMMetrics] = Field(
        None,
        description="LLM processing metrics (if LLM was used)"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if processing failed"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "audit_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "received_at": "2026-01-29T10:30:45.123456Z",
                "status": "completed",
                "patient_id": "PT-12345",
                "summary": "Chief Complaint: Acute onset headache. Examination: Vital signs stable (BP 120/80, HR 72, Temp 98.6F). Assessment: Tension headache. Plan: Acetaminophen 500mg PO PRN, follow up if symptoms worsen.",
                "llm_metrics": {
                    "model": "claude-3-5-sonnet-20241022",
                    "tokens_used": 450,
                    "latency_ms": 1234.56,
                    "cost_usd": 0.006750
                },
                "error": None
            }
        }
