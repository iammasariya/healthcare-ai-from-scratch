"""
Pydantic models for request and response validation.

These models define the contract between the API and its clients.
In healthcare systems, these contracts should be stable and versioned,
as they outlive any individual model or algorithm.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime
from uuid import UUID
from typing import Optional, Any


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
    
    Tracks cost, latency, token usage, and prompt versioning for observability.
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
    prompt_version: Optional[str] = Field(
        None,
        description="Version of prompt used for this request (e.g., '1.0.0')"
    )
    prompt_hash: Optional[str] = Field(
        None,
        description="SHA256 hash of prompt content for verification"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "model": "claude-3-5-sonnet-20241022",
                "tokens_used": 450,
                "latency_ms": 1234.56,
                "cost_usd": 0.006750,
                "prompt_version": "1.0.0",
                "prompt_hash": "a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890"
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


class ShadowModeRequest(BaseModel):
    """
    Request model for Post 6 shadow-mode execution.

    Supports either direct clinical note input or HAPI FHIR-sourced input.
    """
    patient_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique patient identifier or FHIR patient ID",
        examples=["PT-12345", "patient-101"]
    )
    note_text: Optional[str] = Field(
        None,
        min_length=1,
        max_length=10000,
        description="Clinical note text to compare in shadow mode"
    )
    fhir_bundle: Optional[dict[str, Any]] = Field(
        None,
        description="Inline HAPI FHIR Bundle payload used to derive clinical context"
    )
    hapi_fhir_base_url: Optional[str] = Field(
        None,
        description="FHIR server base URL for fetching resources at runtime"
    )
    source_system: str = Field(
        default="internal",
        description="Source system label for audit and rollout analysis",
        examples=["internal", "hapi-fhir-r4"]
    )
    candidate_prompt_version: Optional[str] = Field(
        None,
        description="Optional prompt version override for the shadow candidate"
    )

    @field_validator("patient_id")
    @classmethod
    def validate_shadow_patient_id(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("patient_id cannot be empty or whitespace")
        return v.strip()

    @model_validator(mode="after")
    def validate_input_source(self) -> "ShadowModeRequest":
        has_note = bool(self.note_text and self.note_text.strip())
        has_bundle = self.fhir_bundle is not None
        has_hapi = bool(self.hapi_fhir_base_url and self.hapi_fhir_base_url.strip())

        if not any([has_note, has_bundle, has_hapi]):
            raise ValueError(
                "Provide note_text, fhir_bundle, or hapi_fhir_base_url for shadow execution"
            )

        return self

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "patient-101",
                "source_system": "hapi-fhir-r4",
                "hapi_fhir_base_url": "https://hapi.fhir.org/baseR4",
            }
        }


class ShadowModeAlert(BaseModel):
    """Alert metadata generated during shadow-mode comparison."""
    alert_triggered: bool = Field(..., description="Whether the run should trigger review")
    severity: str = Field(..., description="Alert severity", examples=["none", "warning", "critical"])
    message: str = Field(..., description="Human-readable alert message")


class RolloutDecision(BaseModel):
    """Promotion recommendation for gradual rollout."""
    total_runs_considered: int = Field(..., description="Number of shadow runs considered")
    divergent_runs: int = Field(..., description="Runs marked divergent")
    divergence_rate: float = Field(..., description="Divergence rate across recent runs")
    avg_similarity: float = Field(..., description="Average similarity across recent runs")
    recommended_traffic_percentage: int = Field(
        ...,
        description="Suggested percentage of traffic for the candidate model",
        examples=[0, 10, 25, 50, 100]
    )
    decision: str = Field(..., description="Promotion decision", examples=["hold", "advance", "promote"])
    reason: str = Field(..., description="Why this rollout decision was made")


class ShadowModeResponse(BaseModel):
    """Response model for shadow-mode execution."""
    audit_id: UUID = Field(..., description="Unique audit identifier for request tracing")
    received_at: datetime = Field(..., description="UTC timestamp when request was received")
    status: str = Field(..., description="Status of shadow execution", examples=["completed", "failed"])
    patient_id: str = Field(..., description="Patient identifier or FHIR patient ID")
    source_system: str = Field(..., description="Source system label")
    source_format: str = Field(..., description="How the clinical context was sourced")
    note_text: str = Field(..., description="Rendered clinical note used for both paths")
    production_summary: Optional[str] = Field(None, description="Production output")
    shadow_summary: Optional[str] = Field(None, description="Candidate output")
    production_metrics: Optional[LLMMetrics] = Field(None, description="Production path metrics")
    shadow_metrics: Optional[LLMMetrics] = Field(None, description="Shadow path metrics")
    similarity_score: Optional[float] = Field(None, description="Token-overlap similarity between outputs")
    divergent: bool = Field(..., description="Whether the candidate diverged beyond threshold")
    review_required: bool = Field(..., description="Whether manual review is required")
    recommendation: str = Field(..., description="Comparison recommendation")
    alert: ShadowModeAlert = Field(..., description="Alert outcome for this shadow run")
    rollout_decision: RolloutDecision = Field(..., description="Gradual rollout recommendation")
    error: Optional[str] = Field(None, description="Error message if shadow execution failed")
