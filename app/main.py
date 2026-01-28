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
    HealthResponse,
    ErrorResponse
)
from app.logging import log_request, log_response, log_error
from app.config import settings


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
    
    **This is Post 1**: We build the foundation without any AI.
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
        content=error_response.model_dump()
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
        content=error_response.model_dump()
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


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
