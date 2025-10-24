"""
Production-Grade Structured Logging

Provides structured JSON logging with context injection, performance tracking,
and integration with distributed tracing systems.
"""

import logging
import sys
import time
from contextvars import ContextVar
from typing import Any, Dict, Optional
from pathlib import Path
import json
from datetime import datetime

# Context variables for request tracking
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_ctx: ContextVar[Optional[str]] = ContextVar("user_id", default=None)


class StructuredFormatter(logging.Formatter):
    """
    JSON structured log formatter
    
    Produces structured JSON logs suitable for parsing by log aggregation systems
    like ELK, Splunk, or DataDog.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON"""
        
        # Base log structure
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add request context if available
        request_id = request_id_ctx.get()
        if request_id:
            log_data["request_id"] = request_id
        
        user_id = user_id_ctx.get()
        if user_id:
            log_data["user_id"] = user_id
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None,
            }
        
        # Add custom attributes from extra
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra
        
        # Add performance metrics if available
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        return json.dumps(log_data, default=str)


class TextFormatter(logging.Formatter):
    """
    Human-readable text formatter for development
    """
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Build message
        message_parts = [
            f"{color}[{timestamp}]{reset}",
            f"{color}[{record.levelname}]{reset}",
            f"[{record.name}]",
            record.getMessage()
        ]
        
        # Add request ID if available
        request_id = request_id_ctx.get()
        if request_id:
            message_parts.insert(3, f"[req:{request_id[:8]}]")
        
        message = " ".join(message_parts)
        
        # Add exception info
        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)
        
        return message


class PerformanceLogger:
    """
    Context manager for performance logging
    
    Usage:
        with PerformanceLogger(logger, "operation_name"):
            # Your code here
            pass
    """
    
    def __init__(
        self, 
        logger: logging.Logger, 
        operation: str,
        level: int = logging.INFO,
        **extra: Any
    ):
        self.logger = logger
        self.operation = operation
        self.level = level
        self.extra = extra
        self.start_time: float = 0.0
    
    def __enter__(self) -> "PerformanceLogger":
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        duration_ms = (time.perf_counter() - self.start_time) * 1000
        
        log_extra = {
            "operation": self.operation,
            "duration_ms": round(duration_ms, 2),
            **self.extra
        }
        
        if exc_type is None:
            self.logger.log(
                self.level,
                f"{self.operation} completed in {duration_ms:.2f}ms",
                extra={"extra": log_extra}
            )
        else:
            self.logger.error(
                f"{self.operation} failed after {duration_ms:.2f}ms",
                exc_info=(exc_type, exc_val, exc_tb),
                extra={"extra": log_extra}
            )


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_dir: Optional[Path] = None,
    app_name: str = "sutra"
) -> None:
    """
    Configure application logging
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format ("json" or "text")
        log_dir: Directory for log files (None for console only)
        app_name: Application name for log identification
    """
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Choose formatter
    if log_format == "json":
        formatter = StructuredFormatter()
    else:
        formatter = TextFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler if log directory specified
    if log_dir:
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Main log file
        file_handler = logging.FileHandler(
            log_dir / f"{app_name}.log",
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(StructuredFormatter())  # Always JSON for files
        root_logger.addHandler(file_handler)
        
        # Error log file
        error_handler = logging.FileHandler(
            log_dir / f"{app_name}.error.log",
            encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredFormatter())
        root_logger.addHandler(error_handler)
    
    # Suppress noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    root_logger.info(
        f"Logging configured: level={log_level}, format={log_format}",
        extra={"extra": {"log_dir": str(log_dir) if log_dir else None}}
    )


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Context management functions for request tracking
def set_request_context(request_id: str, user_id: Optional[str] = None) -> None:
    """Set request context for logging"""
    request_id_ctx.set(request_id)
    if user_id:
        user_id_ctx.set(user_id)


def clear_request_context() -> None:
    """Clear request context"""
    request_id_ctx.set(None)
    user_id_ctx.set(None)


def get_request_id() -> Optional[str]:
    """Get current request ID"""
    return request_id_ctx.get()
