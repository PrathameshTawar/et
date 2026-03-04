"""
Custom exceptions for SatyaSetu
Centralized error handling and logging
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SatyaSetuException(Exception):
    """Base exception for SatyaSetu application"""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "GENERAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
        
        # Log the exception
        logger.error(f"SatyaSetuException: {error_code} - {message}", extra={"details": details})

class VoiceProcessingError(SatyaSetuException):
    """Raised when voice processing fails"""
    
    def __init__(self, message: str, stage: str = "unknown", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Voice processing failed at {stage}: {message}",
            error_code="VOICE_PROCESSING_ERROR",
            details={**(details or {}), "stage": stage}
        )

class AIOrchestrationError(SatyaSetuException):
    """Raised when AI orchestration pipeline fails"""
    
    def __init__(self, message: str, node: str = "unknown", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"AI orchestration failed at {node}: {message}",
            error_code="AI_ORCHESTRATION_ERROR",
            details={**(details or {}), "node": node}
        )

class ExternalServiceError(SatyaSetuException):
    """Raised when external service calls fail"""
    
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"External service '{service}' error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details={**(details or {}), "service": service}
        )

class ValidationError(SatyaSetuException):
    """Raised when input validation fails"""
    
    def __init__(self, field: str, message: str, value: Any = None):
        super().__init__(
            message=f"Validation error for '{field}': {message}",
            error_code="VALIDATION_ERROR",
            details={"field": field, "value": str(value) if value is not None else None}
        )

class RateLimitError(SatyaSetuException):
    """Raised when rate limits are exceeded"""
    
    def __init__(self, limit: int, window: str = "minute"):
        super().__init__(
            message=f"Rate limit exceeded: {limit} requests per {window}",
            error_code="RATE_LIMIT_ERROR",
            details={"limit": limit, "window": window}
        )