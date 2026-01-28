"""
Structured logging with audit trail support.

This module provides healthcare-grade logging with:
- Unique audit IDs for every request
- Structured JSON output for log aggregation
- Privacy-aware payload handling
- Deterministic, traceable operations
"""

import logging
import uuid
import json
from datetime import datetime
from typing import Any, Dict, Optional
from app.config import settings


class StructuredLogger:
    """
    Structured logger for healthcare audit trails.
    
    Ensures every operation is traceable and compliant with
    healthcare logging requirements.
    """
    
    def __init__(self, name: str = "clinical_service"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(settings.get_log_level())
        
        # Remove existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Configure handler based on settings
        handler = logging.StreamHandler()
        
        if settings.log_format == "json":
            handler.setFormatter(JSONFormatter())
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        
        # Add file handler if specified
        if settings.log_file:
            file_handler = logging.FileHandler(settings.log_file)
            file_handler.setFormatter(JSONFormatter())
            self.logger.addHandler(file_handler)
    
    def log_request(
        self,
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> uuid.UUID:
        """
        Log an incoming request with audit ID.
        
        Args:
            payload: Request payload (should contain note_text)
            metadata: Additional metadata to log
            
        Returns:
            Unique audit ID for this request
        """
        audit_id = uuid.uuid4()
        
        # Privacy-aware logging: only log preview of note text
        note_text = payload.get("note_text", "")
        preview_length = settings.log_payload_preview_length
        payload_preview = note_text[:preview_length]
        if len(note_text) > preview_length:
            payload_preview += "..."
        
        log_data = {
            "audit_id": str(audit_id),
            "event": "request_received",
            "patient_id": payload.get("patient_id"),
            "payload_preview": payload_preview,
            "payload_length": len(note_text),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if metadata:
            log_data["metadata"] = metadata
        
        self.logger.info(self._format_message(log_data))
        return audit_id
    
    def log_response(
        self,
        audit_id: uuid.UUID,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a response being sent.
        
        Args:
            audit_id: Audit ID from the request
            status: Response status
            metadata: Additional metadata to log
        """
        log_data = {
            "audit_id": str(audit_id),
            "event": "response_sent",
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if metadata:
            log_data["metadata"] = metadata
        
        self.logger.info(self._format_message(log_data))
    
    def log_error(
        self,
        audit_id: Optional[uuid.UUID],
        error_type: str,
        error_message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an error with audit trail.
        
        Args:
            audit_id: Audit ID if available
            error_type: Type/category of error
            error_message: Error description
            metadata: Additional error context
        """
        log_data = {
            "event": "error",
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        if audit_id:
            log_data["audit_id"] = str(audit_id)
        
        if metadata:
            log_data["metadata"] = metadata
        
        self.logger.error(self._format_message(log_data))
    
    def _format_message(self, data: Dict[str, Any]) -> str:
        """Format log message based on configuration."""
        if settings.log_format == "json":
            return json.dumps(data)
        else:
            return str(data)


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logs.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


# Global logger instance
logger = StructuredLogger()


# Convenience functions for direct use
def log_request(payload: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> uuid.UUID:
    """Log an incoming request. Returns audit ID."""
    return logger.log_request(payload, metadata)


def log_response(audit_id: uuid.UUID, status: str, metadata: Optional[Dict[str, Any]] = None) -> None:
    """Log an outgoing response."""
    logger.log_response(audit_id, status, metadata)


def log_error(
    audit_id: Optional[uuid.UUID],
    error_type: str,
    error_message: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """Log an error."""
    logger.log_error(audit_id, error_type, error_message, metadata)
