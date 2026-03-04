"""
Custom middleware for SatyaSetu
Rate limiting, request logging, and security
"""

import time
import json
import logging
from typing import Dict, Optional
from collections import defaultdict, deque
from datetime import datetime, timedelta

from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings
from core.exceptions import RateLimitError

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using sliding window"""
    
    def __init__(self, app, requests_per_minute: int = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_PER_MINUTE
        self.client_requests: Dict[str, deque] = defaultdict(deque)
        self.cleanup_interval = 300  # Clean up old entries every 5 minutes
        self.last_cleanup = time.time()
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Skip rate limit checks for health checks and docs, but still add timing header
        if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
            response = await call_next(request)
            response.headers["X-Process-Time"] = str(time.time() - start_time)
            return response
        
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        
        # Cleanup old entries periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_old_entries(current_time)
            self.last_cleanup = current_time
        
        # Check rate limit
        if self._is_rate_limited(client_ip, current_time):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute allowed",
                    "retry_after": 60
                }
            )
        
        # Record the request
        self.client_requests[client_ip].append(current_time)
        
        # Process the request
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded headers (for reverse proxy setups)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """Check if client has exceeded rate limit"""
        requests = self.client_requests[client_ip]
        
        # Remove requests older than 1 minute
        cutoff_time = current_time - 60
        while requests and requests[0] < cutoff_time:
            requests.popleft()
        
        return len(requests) >= self.requests_per_minute
    
    def _cleanup_old_entries(self, current_time: float):
        """Remove old entries to prevent memory leaks"""
        cutoff_time = current_time - 3600  # Remove entries older than 1 hour
        
        for client_ip in list(self.client_requests.keys()):
            requests = self.client_requests[client_ip]
            
            # Remove old requests
            while requests and requests[0] < cutoff_time:
                requests.popleft()
            
            # Remove empty entries
            if not requests:
                del self.client_requests[client_ip]

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for monitoring and debugging"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} - "
                f"{request.method} {request.url.path} - "
                f"{process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {str(e)} - "
                f"{request.method} {request.url.path} - "
                f"{process_time:.3f}s"
            )
            raise

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Add CSP for API endpoints
        if request.url.path.startswith("/api/"):
            response.headers["Content-Security-Policy"] = "default-src 'none'"
        
        return response
