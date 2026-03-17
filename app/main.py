"""
FastAPI application for healthcare clinical note ingestion.

This is the main entry point for the service. It provides:
- REST API for clinical note ingestion
- Health check endpoints
- Full request/response logging
- Production-ready error handling
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
from contextlib import asynccontextmanager
import time
from typing import Dict, Any

from app.models import (
    ClinicalNoteRequest,
    ClinicalNoteResponse,
    SummarizeNoteResponse,
    LLMMetrics,
    HealthResponse,
    ErrorResponse,
    ShadowModeRequest,
    ShadowModeResponse,
    ShadowModeAlert,
    RolloutDecision,
)
from app.logging import log_request, log_response, log_error
from app.config import settings
from app.llm import get_llm_service, LLMService
from app.shadow import ShadowModeRunner, build_llm_metrics


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    """
    # Startup
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Debug mode: {settings.debug}")
    print(f"Log level: {settings.log_level}")
    
    yield
    
    # Shutdown
    print(f"Shutting down {settings.app_name}")


# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    A production-grade foundation for healthcare AI systems.
    
    This service demonstrates the essential scaffolding every healthcare
    AI system needs before adding models:
    - Full audit trail with unique IDs
    - Structured logging
    - Type-safe request/response validation
    - Production-ready error handling
    
    **Post 6**: Shadow mode deployment with dual-path execution and HAPI FHIR support.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

shadow_runner = ShadowModeRunner()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware to track request processing time.
    Useful for performance monitoring in production.
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Global HTTP exception handler.
    Ensures consistent error response format.
    """
    error_response = ErrorResponse(
        error=exc.__class__.__name__,
        message=exc.detail,
        timestamp=datetime.utcnow()
    )
    
    log_error(
        audit_id=None,
        error_type=exc.__class__.__name__,
        error_message=exc.detail,
        metadata={"status_code": exc.status_code}
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump(mode='json')
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unexpected errors.
    Prevents leaking internal details to clients.
    """
    error_response = ErrorResponse(
        error="InternalServerError",
        message="An unexpected error occurred. Please contact support with your audit ID.",
        timestamp=datetime.utcnow()
    )
    
    log_error(
        audit_id=None,
        error_type=exc.__class__.__name__,
        error_message=str(exc),
        metadata={"traceback": True}
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(mode='json')
    )


@app.get("/", tags=["General"])
async def root() -> Dict[str, str]:
    """
    Root endpoint with service information.
    """
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check() -> HealthResponse:
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        Health status and timestamp
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.app_version
    )


@app.post(
    "/ingest",
    response_model=ClinicalNoteResponse,
    status_code=status.HTTP_200_OK,
    tags=["Clinical Notes"],
    summary="Ingest a clinical note",
    description="""
    Ingest a clinical note for processing.
    
    This endpoint:
    - Validates the input
    - Assigns a unique audit ID
    - Logs the request (with privacy controls)
    - Returns a traceable response
    
    **Note**: No AI processing yet. This is the foundation.
    """
)
async def ingest_note(request: ClinicalNoteRequest) -> ClinicalNoteResponse:
    """
    Main endpoint for ingesting clinical notes.
    
    This is where clinical text enters the system. Every request:
    1. Gets validated by Pydantic models
    2. Receives a unique audit ID
    3. Gets logged with privacy controls (only preview of text)
    4. Returns a traceable response
    
    Args:
        request: ClinicalNoteRequest containing patient_id and note_text
        
    Returns:
        ClinicalNoteResponse with audit_id, timestamp, and status
    """
    # Generate audit ID and log request
    audit_id = log_request(request.model_dump())
    
    # In a real system, this is where you would:
    # - Store the note in a database
    # - Queue it for processing
    # - Trigger downstream workflows
    # 
    # For Post 1, we just acknowledge receipt
    
    response = ClinicalNoteResponse(
        audit_id=audit_id,
        received_at=datetime.utcnow(),
        status="received",
        patient_id=request.patient_id
    )
    
    # Log the response
    log_response(audit_id, status="received")
    
    return response


@app.post(
    "/summarize",
    response_model=SummarizeNoteResponse,
    status_code=status.HTTP_200_OK,
    tags=["Clinical Notes"],
    summary="Summarize a clinical note using LLM",
    description="""
    Summarize a clinical note using Claude LLM.
    
    This endpoint demonstrates Post 2 concepts:
    - Safe LLM integration with timeouts and retries
    - Cost and latency tracking
    - Graceful failure handling
    - Audit trail preservation
    
    **Feature Flag**: LLM functionality must be enabled via LLM_ENABLED env var.
    **API Key**: Requires ANTHROPIC_API_KEY to be set.
    """
)
async def summarize_note(request: ClinicalNoteRequest) -> SummarizeNoteResponse:
    """
    Summarize a clinical note using LLM.
    
    This endpoint shows how to add AI safely:
    1. Check feature flag (fail fast if disabled)
    2. Generate audit ID for traceability
    3. Call LLM with timeouts and retries
    4. Validate response
    5. Track costs and latency
    6. Handle failures gracefully
    7. Return traceable response
    
    Args:
        request: ClinicalNoteRequest containing patient_id and note_text
        
    Returns:
        SummarizeNoteResponse with summary and metrics (or error)
    """
    # Check if LLM functionality is enabled
    if not settings.llm_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM functionality is not enabled. Set LLM_ENABLED=true to enable."
        )
    
    # Generate audit ID and log request
    audit_id = log_request(request.model_dump())
    received_at = datetime.utcnow()
    
    try:
        # Get LLM service instance
        llm_service = get_llm_service()
        
        # Call LLM to summarize the note
        llm_response, error = llm_service.summarize_clinical_note(
            note_text=request.note_text,
            audit_id=audit_id,
        )
        
        # Check if LLM call failed
        if error or llm_response is None:
            # Log failure
            log_response(audit_id, status="failed", metadata={"error": error})
            
            # Return error response
            return SummarizeNoteResponse(
                audit_id=audit_id,
                received_at=received_at,
                status="failed",
                patient_id=request.patient_id,
                summary=None,
                llm_metrics=None,
                error=error
            )
        
        # Validate LLM response
        is_valid, validation_error = llm_service.validate_response(llm_response)
        if not is_valid:
            # Log validation failure
            log_response(
                audit_id,
                status="validation_failed",
                metadata={"validation_error": validation_error}
            )
            
            # Return error response
            return SummarizeNoteResponse(
                audit_id=audit_id,
                received_at=received_at,
                status="failed",
                patient_id=request.patient_id,
                summary=None,
                llm_metrics=None,
                error=f"Response validation failed: {validation_error}"
            )
        
        # Build metrics object (including prompt versioning if available)
        metrics = LLMMetrics(
            model=llm_response.model,
            tokens_used=llm_response.tokens_used,
            latency_ms=llm_response.latency_ms,
            cost_usd=llm_response.cost_usd,
            prompt_version=llm_response.prompt_version,
            prompt_hash=llm_response.prompt_hash,
        )
        
        # Log successful response with metrics
        log_response(
            audit_id,
            status="completed",
            metadata={
                "llm_metrics": llm_response.to_dict(),
                "summary_length": len(llm_response.content)
            }
        )
        
        # Return successful response
        return SummarizeNoteResponse(
            audit_id=audit_id,
            received_at=received_at,
            status="completed",
            patient_id=request.patient_id,
            summary=llm_response.content,
            llm_metrics=metrics,
            error=None
        )
        
    except ValueError as e:
        # API key not configured
        error_msg = str(e)
        log_error(audit_id, "LLMConfigurationError", error_msg)
        
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=error_msg
        )
    
    except Exception as e:
        # Unexpected error
        error_msg = f"Unexpected error during summarization: {str(e)}"
        log_error(audit_id, "SummarizationError", error_msg)
        
        # Return error response instead of raising (graceful degradation)
        return SummarizeNoteResponse(
            audit_id=audit_id,
            received_at=received_at,
            status="failed",
            patient_id=request.patient_id,
            summary=None,
            llm_metrics=None,
            error=error_msg
        )


@app.get("/metrics", tags=["Monitoring"])
async def metrics() -> Dict[str, Any]:
    """
    Basic metrics endpoint for monitoring.
    
    In production, you'd integrate with Prometheus, DataDog, etc.
    """
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "See container metrics",
        "requests": "See middleware/logging"
    }


@app.post(
    "/shadow/summarize",
    response_model=ShadowModeResponse,
    status_code=status.HTTP_200_OK,
    tags=["Shadow Mode"],
    summary="Run production and candidate summaries in shadow mode",
    description="""
    Execute production and candidate summarization paths side by side.

    This endpoint demonstrates Post 6 concepts:
    - Safe dual-path execution
    - HAPI FHIR sourced clinical context
    - Divergence scoring and alerting
    - Gradual rollout recommendations
    """
)
async def summarize_note_shadow(request: ShadowModeRequest) -> ShadowModeResponse:
    """
    Run a shadow-mode comparison for a single request.

    The candidate output is never returned to an end user in production
    rollout patterns. Here it is returned because this codebase is intended
    to teach and verify the shadow-mode mechanics explicitly.
    """
    if not settings.llm_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM functionality is not enabled. Set LLM_ENABLED=true to enable."
        )

    if not settings.shadow_mode_enabled:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Shadow mode is not enabled. Set SHADOW_MODE_ENABLED=true to enable."
        )

    audit_id = log_request(
        request.model_dump(),
        metadata={"source_system": request.source_system, "shadow_mode": True},
    )
    received_at = datetime.utcnow()

    try:
        result = shadow_runner.run_llm_shadow(
            patient_id=request.patient_id,
            audit_id=str(audit_id),
            source_system=request.source_system,
            note_text=request.note_text,
            fhir_bundle=request.fhir_bundle,
            hapi_fhir_base_url=request.hapi_fhir_base_url,
            candidate_prompt_version=request.candidate_prompt_version,
        )

        log_response(
            audit_id,
            status="shadow_completed",
            metadata={
                "similarity_score": result.similarity_score,
                "divergent": result.divergent,
                "alert_triggered": result.alert_triggered,
                "recommended_traffic_percentage": (
                    result.rollout_recommendation.recommended_traffic_percentage
                ),
            },
        )

        return ShadowModeResponse(
            audit_id=audit_id,
            received_at=received_at,
            status="completed" if not (result.production_error or result.shadow_error) else "failed",
            patient_id=request.patient_id,
            source_system=result.source_system,
            source_format=result.source_format,
            note_text=result.note_text,
            production_summary=(
                result.production_response.content if result.production_response else None
            ),
            shadow_summary=result.shadow_response.content if result.shadow_response else None,
            production_metrics=(
                LLMMetrics(**build_llm_metrics(result.production_response))
                if result.production_response else None
            ),
            shadow_metrics=(
                LLMMetrics(**build_llm_metrics(result.shadow_response))
                if result.shadow_response else None
            ),
            similarity_score=result.similarity_score,
            divergent=result.divergent,
            review_required=result.review_required,
            recommendation=result.recommendation,
            alert=ShadowModeAlert(
                alert_triggered=result.alert_triggered,
                severity=result.alert_severity,
                message=result.alert_message,
            ),
            rollout_decision=RolloutDecision(
                total_runs_considered=result.rollout_recommendation.total_runs_considered,
                divergent_runs=result.rollout_recommendation.divergent_runs,
                divergence_rate=result.rollout_recommendation.divergence_rate,
                avg_similarity=result.rollout_recommendation.avg_similarity,
                recommended_traffic_percentage=(
                    result.rollout_recommendation.recommended_traffic_percentage
                ),
                decision=result.rollout_recommendation.decision,
                reason=result.rollout_recommendation.reason,
            ),
            error=result.production_error or result.shadow_error,
        )

    except ValueError as e:
        error_msg = str(e)
        log_error(audit_id, "ShadowModeConfigurationError", error_msg)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    except Exception as e:
        error_msg = f"Unexpected error during shadow execution: {str(e)}"
        log_error(audit_id, "ShadowModeExecutionError", error_msg)

        return ShadowModeResponse(
            audit_id=audit_id,
            received_at=received_at,
            status="failed",
            patient_id=request.patient_id,
            source_system=request.source_system,
            source_format="unknown",
            note_text=request.note_text or "",
            production_summary=None,
            shadow_summary=None,
            production_metrics=None,
            shadow_metrics=None,
            similarity_score=None,
            divergent=True,
            review_required=True,
            recommendation="Shadow execution failed before comparison",
            alert=ShadowModeAlert(
                alert_triggered=True,
                severity="critical",
                message=error_msg,
            ),
            rollout_decision=RolloutDecision(
                total_runs_considered=0,
                divergent_runs=0,
                divergence_rate=0.0,
                avg_similarity=0.0,
                recommended_traffic_percentage=0,
                decision="hold",
                reason="Shadow execution failed",
            ),
            error=error_msg,
        )


if __name__ == "__main__":  # pragma: no cover
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
