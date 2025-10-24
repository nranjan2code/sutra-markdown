"""
Production Security Middleware and Utilities

Implements rate limiting, input validation, and security headers.
"""

import time
from typing import Callable
from collections import defaultdict
import hashlib
from datetime import datetime, timedelta

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..logging_config import get_logger, set_request_context, clear_request_context
from ..exceptions import ResourceExhaustedError

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm
    
    Tracks requests per IP address and enforces rate limits.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # In-memory storage (use Redis in production for distributed systems)
        self.minute_requests: dict[str, list[float]] = defaultdict(list)
        self.hour_requests: dict[str, list[float]] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limits before processing request"""
        
        # Get client IP (respect X-Forwarded-For)
        client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.client.host if request.client else "unknown"
        
        current_time = time.time()
        
        # Clean old entries
        self._clean_old_entries(client_ip, current_time)
        
        # Check rate limits
        minute_count = len(self.minute_requests[client_ip])
        hour_count = len(self.hour_requests[client_ip])
        
        if minute_count >= self.requests_per_minute:
            logger.warning(
                f"Rate limit exceeded for {client_ip}: {minute_count} req/min",
                extra={"extra": {"client_ip": client_ip, "limit": "per_minute"}}
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        if hour_count >= self.requests_per_hour:
            logger.warning(
                f"Rate limit exceeded for {client_ip}: {hour_count} req/hour",
                extra={"extra": {"client_ip": client_ip, "limit": "per_hour"}}
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "RATE_LIMIT_EXCEEDED",
                    "message": "Hourly rate limit exceeded. Please try again later.",
                    "retry_after": 3600
                },
                headers={"Retry-After": "3600"}
            )
        
        # Record request
        self.minute_requests[client_ip].append(current_time)
        self.hour_requests[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            self.requests_per_minute - minute_count - 1
        )
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            self.requests_per_hour - hour_count - 1
        )
        
        return response
    
    def _clean_old_entries(self, client_ip: str, current_time: float) -> None:
        """Remove entries older than the time windows"""
        # Clean minute window (60 seconds)
        self.minute_requests[client_ip] = [
            t for t in self.minute_requests[client_ip]
            if current_time - t < 60
        ]
        
        # Clean hour window (3600 seconds)
        self.hour_requests[client_ip] = [
            t for t in self.hour_requests[client_ip]
            if current_time - t < 3600
        ]


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers"""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Add unique request ID to each request for tracking
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Generate and inject request ID"""
        
        # Check if request ID already exists
        request_id = request.headers.get("X-Request-ID")
        
        if not request_id:
            # Generate new request ID
            request_id = self._generate_request_id(request)
        
        # Set in logging context
        set_request_context(request_id)
        
        try:
            # Add to request state for access in route handlers
            request.state.request_id = request_id
            
            # Process request
            response = await call_next(request)
            
            # Add request ID to response
            response.headers["X-Request-ID"] = request_id
            
            return response
        finally:
            # Clean up context
            clear_request_context()
    
    def _generate_request_id(self, request: Request) -> str:
        """Generate unique request ID"""
        timestamp = datetime.utcnow().isoformat()
        client = request.client.host if request.client else "unknown"
        path = request.url.path
        
        unique_string = f"{timestamp}:{client}:{path}"
        hash_object = hashlib.sha256(unique_string.encode())
        return hash_object.hexdigest()[:16]


class FileSizeValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate file upload sizes before processing
    """
    
    def __init__(self, app: ASGIApp, max_size_mb: int = 500):
        super().__init__(app)
        self.max_size_bytes = max_size_mb * 1024 * 1024
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check content length"""
        
        # Only check for upload endpoints
        if request.url.path.startswith("/convert") or request.url.path.startswith("/upload"):
            content_length = request.headers.get("content-length")
            
            if content_length:
                content_length_int = int(content_length)
                
                if content_length_int > self.max_size_bytes:
                    max_size_mb = self.max_size_bytes / (1024 * 1024)
                    logger.warning(
                        f"File too large: {content_length_int} bytes (max: {self.max_size_bytes})",
                        extra={"extra": {
                            "content_length": content_length_int,
                            "max_size": self.max_size_bytes
                        }}
                    )
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "error": "FILE_TOO_LARGE",
                            "message": f"File size exceeds maximum allowed size of {max_size_mb}MB",
                            "max_size_mb": max_size_mb
                        }
                    )
        
        return await call_next(request)


# Input validation utilities
def validate_file_extension(filename: str, allowed_extensions: set[str]) -> bool:
    """
    Validate file extension against allowed list
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions (e.g., {'.pdf', '.docx'})
    
    Returns:
        True if extension is allowed
    """
    if not filename:
        return False
    
    # Get extension in lowercase
    extension = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    return extension in allowed_extensions


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal and other attacks
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove directory components
    filename = filename.rsplit('/', 1)[-1]
    filename = filename.rsplit('\\', 1)[-1]
    
    # Remove dangerous characters
    dangerous_chars = ['..', '~', '|', ';', '&', '$', '`']
    for char in dangerous_chars:
        filename = filename.replace(char, '')
    
    # Ensure not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename


# Allowed file extensions for document conversion
ALLOWED_DOCUMENT_EXTENSIONS = {
    '.pdf', '.docx', '.doc', '.pptx', '.ppt', 
    '.xlsx', '.xls', '.txt', '.md', '.html',
    '.png', '.jpg', '.jpeg', '.tiff', '.tif'
}
