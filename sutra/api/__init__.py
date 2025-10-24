"""
REST API - FastAPI application for document conversion

Provides HTTP endpoints for:
- Document upload and conversion
- Async job processing
- Status tracking
- Result retrieval

Features:
- FastAPI async endpoints
- File upload support
- Job queue with status tracking
- Caching integration
- Rate limiting
- Authentication ready
"""

from .app import create_app, app
from .models import (
    ConvertRequest,
    ConvertResponse,
    JobStatus,
    JobResponse,
    HealthResponse,
)

__all__ = [
    'create_app',
    'app',
    'ConvertRequest',
    'ConvertResponse',
    'JobStatus',
    'JobResponse',
    'HealthResponse',
]
