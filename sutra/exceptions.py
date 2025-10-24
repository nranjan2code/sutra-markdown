"""
Production-grade exception hierarchy for Sutra-Markdown

All exceptions inherit from SutraException for easy catching and handling.
Includes proper error codes, context, and structured error information.
"""

from typing import Any, Dict, Optional
from enum import Enum


class ErrorCode(str, Enum):
    """Standard error codes for API responses"""
    
    # Parsing errors (1xxx)
    PARSE_ERROR = "PARSE_1000"
    CORRUPTED_FILE = "PARSE_1001"
    UNSUPPORTED_FORMAT = "PARSE_1002"
    FILE_TOO_LARGE = "PARSE_1003"
    
    # Conversion errors (2xxx)
    CONVERSION_ERROR = "CONV_2000"
    TIER_NOT_AVAILABLE = "CONV_2001"
    QUALITY_TOO_LOW = "CONV_2002"
    
    # Intelligence errors (3xxx)
    EMBEDDING_ERROR = "INTEL_3000"
    MODEL_NOT_FOUND = "INTEL_3001"
    ANALYSIS_TIMEOUT = "INTEL_3002"
    
    # Cache errors (4xxx)
    CACHE_ERROR = "CACHE_4000"
    CACHE_UNAVAILABLE = "CACHE_4001"
    
    # Configuration errors (5xxx)
    CONFIG_ERROR = "CONFIG_5000"
    INVALID_CONFIG = "CONFIG_5001"
    
    # Authentication errors (6xxx)
    AUTH_ERROR = "AUTH_6000"
    INVALID_TOKEN = "AUTH_6001"
    TOKEN_EXPIRED = "AUTH_6002"
    PERMISSION_DENIED = "AUTH_6003"
    
    # Validation errors (7xxx)
    VALIDATION_ERROR = "VALID_7000"
    INVALID_INPUT = "VALID_7001"
    
    # Resource errors (8xxx)
    RESOURCE_ERROR = "RESOURCE_8000"
    RESOURCE_NOT_FOUND = "RESOURCE_8001"
    RESOURCE_EXHAUSTED = "RESOURCE_8002"
    
    # System errors (9xxx)
    SYSTEM_ERROR = "SYSTEM_9000"
    SERVICE_UNAVAILABLE = "SYSTEM_9001"


class SutraException(Exception):
    """
    Base exception for all Sutra-Markdown errors
    
    Attributes:
        message: Human-readable error message
        error_code: Standardized error code
        context: Additional context information
        http_status: Suggested HTTP status code
    """
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.SYSTEM_ERROR,
        context: Optional[Dict[str, Any]] = None,
        http_status: int = 500
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.http_status = http_status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses"""
        return {
            "error": self.error_code.value,
            "message": self.message,
            "context": self.context
        }


# Parsing exceptions
class ParserError(SutraException):
    """Base class for parsing errors"""
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.PARSE_ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context, http_status=422)


class CorruptedFileError(ParserError):
    """Raised when file is corrupted or cannot be read"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.CORRUPTED_FILE, context)


class UnsupportedFormatError(ParserError):
    """Raised when file format is not supported"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.UNSUPPORTED_FORMAT, context)


class FileTooLargeError(ParserError):
    """Raised when file exceeds size limits"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.FILE_TOO_LARGE, context)


# Conversion exceptions
class ConversionError(SutraException):
    """Base class for conversion errors"""
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.CONVERSION_ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context, http_status=500)


class TierNotAvailableError(ConversionError):
    """Raised when requested conversion tier is not available"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.TIER_NOT_AVAILABLE, context)


class QualityTooLowError(ConversionError):
    """Raised when conversion quality is below acceptable threshold"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.QUALITY_TOO_LOW, context)


# Intelligence exceptions
class IntelligenceError(SutraException):
    """Base class for AI/intelligence errors"""
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.EMBEDDING_ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context, http_status=500)


class EmbeddingError(IntelligenceError):
    """Raised when embedding generation fails"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.EMBEDDING_ERROR, context)


class ModelNotFoundError(IntelligenceError):
    """Raised when required model is not available"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.MODEL_NOT_FOUND, context)


class AnalysisTimeoutError(IntelligenceError):
    """Raised when analysis takes too long"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.ANALYSIS_TIMEOUT, context)


# Cache exceptions
class CacheError(SutraException):
    """Base class for cache errors"""
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.CACHE_ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context, http_status=500)


# Configuration exceptions
class ConfigurationError(SutraException):
    """Base class for configuration errors"""
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.CONFIG_ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context, http_status=500)


# Authentication exceptions
class AuthenticationError(SutraException):
    """Base class for authentication errors"""
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.AUTH_ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context, http_status=401)


class InvalidTokenError(AuthenticationError):
    """Raised when authentication token is invalid"""
    def __init__(self, message: str = "Invalid authentication token", context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.INVALID_TOKEN, context)


class TokenExpiredError(AuthenticationError):
    """Raised when authentication token has expired"""
    def __init__(self, message: str = "Authentication token has expired", context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.TOKEN_EXPIRED, context)


class PermissionDeniedError(SutraException):
    """Raised when user lacks required permissions"""
    def __init__(self, message: str = "Permission denied", context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.PERMISSION_DENIED, context, http_status=403)


# Validation exceptions
class ValidationError(SutraException):
    """Base class for validation errors"""
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.VALIDATION_ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context, http_status=400)


# Resource exceptions
class ResourceError(SutraException):
    """Base class for resource errors"""
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.RESOURCE_ERROR,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context, http_status=404)


class ResourceNotFoundError(ResourceError):
    """Raised when requested resource is not found"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.RESOURCE_NOT_FOUND, context)


class ResourceExhaustedError(SutraException):
    """Raised when system resources are exhausted"""
    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, ErrorCode.RESOURCE_EXHAUSTED, context, http_status=503)
