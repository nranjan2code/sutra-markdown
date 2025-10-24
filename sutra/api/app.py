"""
Production-Grade FastAPI Application

Clean, modern API with proper dependency injection, error handling,
security, and observability.

This is the main production API for Sutra-Markdown V2.2.
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator
import uuid
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException

from ..config import Settings, get_settings
from ..exceptions import SutraException, FileTooLargeError, UnsupportedFormatError
from ..logging_config import setup_logging, get_logger, PerformanceLogger
from ..parsers import get_parser
from ..converters import convert_document
from ..models.enums import ConversionTier, OutputFormat

from .dependencies import (
    SettingsDep,
    EmbeddingServiceDep,
    CacheManagerDep,
    CurrentUserDep,
    RateLimitDep,
)
from .security import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    RequestIDMiddleware,
    FileSizeValidationMiddleware,
    validate_file_extension,
    sanitize_filename,
    ALLOWED_DOCUMENT_EXTENSIONS,
)
from .models import (
    ConvertResponse,
    HealthResponse,
    JobResponse,
    JobStatus,
    ComplexityAnalysis,
)

logger = get_logger(__name__)


# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifecycle management
    
    Handles startup and shutdown tasks.
    """
    # Startup
    settings: Settings = app.state.settings
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version}",
        extra={"extra": {"environment": settings.environment}}
    )
    
    # Setup logging
    setup_logging(
        log_level=settings.monitoring.log_level,
        log_format=settings.monitoring.log_format,
        log_dir=settings.log_dir,
        app_name="sutra"
    )
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Application shutting down")


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    
    Returns configured FastAPI app instance.
    """
    # Load settings
    settings = get_settings()
    
    # Create app
    app = FastAPI(
        title="Sutra-Markdown API",
        description="Production-grade AI-powered document conversion",
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production() else None,  # Disable in prod
        redoc_url="/redoc" if not settings.is_production() else None,
        debug=settings.debug,
    )
    
    # Store settings in app state
    app.state.settings = settings
    
    # Add middleware (order matters!)
    
    # 1. Request ID (first, for tracking)
    app.add_middleware(RequestIDMiddleware)
    
    # 2. Security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # 3. Rate limiting (if enabled)
    if settings.security.rate_limit_per_minute > 0:
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=settings.security.rate_limit_per_minute,
            requests_per_hour=settings.security.rate_limit_per_minute * 60,
        )
    
    # 4. File size validation
    app.add_middleware(
        FileSizeValidationMiddleware,
        max_size_mb=settings.api.max_file_size_mb
    )
    
    # 5. CORS (last, most permissive)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Exception handlers
    
    @app.exception_handler(SutraException)
    async def sutra_exception_handler(request, exc: SutraException):
        """Handle custom Sutra exceptions"""
        logger.error(
            f"Sutra exception: {exc.message}",
            exc_info=True,
            extra={"extra": {"error_code": exc.error_code.value, **exc.context}}
        )
        return JSONResponse(
            status_code=exc.http_status,
            content=exc.to_dict()
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request, exc):
        """Handle HTTP exceptions with structured response"""
        logger.warning(
            f"HTTP exception: {exc.status_code} - {exc.detail}",
            extra={"extra": {"status_code": exc.status_code, "path": request.url.path}}
        )
        return await http_exception_handler(request, exc)
    
    # Routes
    
    @app.get("/", response_model=HealthResponse, tags=["Health"])
    async def root(settings: SettingsDep) -> HealthResponse:
        """Root endpoint with health status"""
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            environment=settings.environment,
        )
    
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    async def health(
        settings: SettingsDep,
        embeddings: EmbeddingServiceDep,
        cache: CacheManagerDep,
    ) -> HealthResponse:
        """
        Detailed health check endpoint
        
        Checks status of all critical services.
        """
        # Check embedding service
        embeddings_status = {
            "available": True,
            "mode": embeddings.mode,
            "device": str(embeddings.embedder.device) if hasattr(embeddings, 'embedder') else "unknown"
        }
        
        # Check cache
        cache_stats = cache.get_stats()
        cache_status = {
            "enabled": settings.cache.enabled,
            "stats": cache_stats
        }
        
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            environment=settings.environment,
            details={
                "embeddings": embeddings_status,
                "cache": cache_status,
                "config": {
                    "intelligence_enabled": settings.api.enable_intelligence,
                    "quality": settings.api.default_quality,
                }
            }
        )
    
    @app.get("/config", tags=["Admin"])
    async def get_configuration(
        settings: SettingsDep,
        user: CurrentUserDep,  # Requires authentication
    ) -> dict:
        """Get current configuration (admin only)"""
        if settings.security.enable_auth and not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        return {
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "complexity": {
                "tier1_threshold": settings.complexity.tier1_threshold,
                "tier2_threshold": settings.complexity.tier2_threshold,
            },
            "api": {
                "max_file_size_mb": settings.api.max_file_size_mb,
                "timeout_seconds": settings.api.timeout_seconds,
            }
        }
    
    @app.post("/convert", response_model=ConvertResponse, tags=["Conversion"])
    async def convert(
        file: UploadFile = File(..., description="Document to convert"),
        tier: str | None = Form(None, description="Force specific tier (tier1, tier2, tier3)"),
        enable_intelligence: bool = Form(True, description="Enable AI analysis"),
        output_formats: str = Form("markdown", description="Comma-separated output formats"),
        # Dependencies
        settings: SettingsDep = None,
        embeddings: EmbeddingServiceDep = None,
        cache: CacheManagerDep = None,
        rate_limit: RateLimitDep = None,
    ) -> ConvertResponse:
        """
        Convert document to markdown and other formats
        
        Supports multiple output formats including JSON, XML, CSV, YAML, HTML.
        """
        with PerformanceLogger(logger, "document_conversion"):
            
            # Validate filename
            if not file.filename:
                raise UnsupportedFormatError("Filename is required")
            
            # Sanitize filename
            safe_filename = sanitize_filename(file.filename)
            
            # Validate file extension
            if not validate_file_extension(safe_filename, ALLOWED_DOCUMENT_EXTENSIONS):
                raise UnsupportedFormatError(
                    f"Unsupported file type: {safe_filename}",
                    context={"filename": safe_filename}
                )
            
            # Parse output formats
            requested_formats = [
                OutputFormat(fmt.strip().lower())
                for fmt in output_formats.split(',')
                if fmt.strip()
            ]
            
            # Save uploaded file temporarily
            temp_dir = settings.upload_dir / str(uuid.uuid4())
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_file = temp_dir / safe_filename
            
            try:
                # Write uploaded file
                content = await file.read()
                temp_file.write_bytes(content)
                
                logger.info(
                    f"Processing file: {safe_filename}",
                    extra={"extra": {
                        "filename": safe_filename,
                        "size_bytes": len(content),
                        "output_formats": [f.value for f in requested_formats]
                    }}
                )
                
                # Parse document
                with PerformanceLogger(logger, "document_parsing"):
                    parser = get_parser(str(temp_file))
                    parse_result = await parser.parse()
                
                if not parse_result.success or not parse_result.document:
                    raise HTTPException(
                        status_code=422,
                        detail=f"Failed to parse document: {parse_result.error or 'Unknown error'}"
                    )
                
                document = parse_result.document
                
                # AI-guided enhancement (if enabled)
                if enable_intelligence and settings.api.enable_intelligence:
                    with PerformanceLogger(logger, "ai_enhancement"):
                        try:
                            from ..intelligence.universal_extraction import enhance_document_extraction
                            
                            document, enhancement_metadata = await enhance_document_extraction(
                                document, embeddings
                            )
                            
                            logger.info(
                                f"AI enhancement applied: {enhancement_metadata['enhancement_strategy']}",
                                extra={"extra": enhancement_metadata}
                            )
                        except Exception as e:
                            logger.warning(f"AI enhancement failed: {e}", exc_info=True)
                
                # Complexity analysis and tier selection
                tier_enum = None
                if tier:
                    tier_map = {
                        "tier1": ConversionTier.RULE_BASED,
                        "tier2": ConversionTier.SPATIAL_AWARE,
                        "tier3": ConversionTier.LLM_ENHANCED,
                    }
                    tier_enum = tier_map.get(tier.lower())
                
                if not tier_enum and enable_intelligence:
                    with PerformanceLogger(logger, "complexity_analysis"):
                        try:
                            from ..router.analyzer import ComplexityAnalyzer
                            
                            analyzer = ComplexityAnalyzer(embeddings)
                            complexity_result = await analyzer.analyze(document)
                            
                            tier_enum = complexity_result.tier
                            
                            logger.info(
                                f"Complexity analysis: score={complexity_result.score:.3f}, tier={tier_enum.value}",
                                extra={"extra": {
                                    "score": complexity_result.score,
                                    "tier": tier_enum.value,
                                    "reasoning": complexity_result.reasoning
                                }}
                            )
                        except Exception as e:
                            logger.warning(f"Complexity analysis failed: {e}", exc_info=True)
                
                # Convert document
                with PerformanceLogger(logger, "document_to_markdown"):
                    result = await convert_document(
                        document,
                        tier=tier_enum,
                        output_formats=requested_formats
                    )
                
                # Build response
                response = ConvertResponse(
                    markdown=result.markdown,
                    outputs=result.outputs,
                    tier=result.tier.value,
                    quality_score=result.quality_score,
                    processing_time=result.processing_time,
                    word_count=result.word_count,
                    line_count=result.line_count,
                    cached=False,
                    warnings=result.warnings,
                )
                
                logger.info(
                    f"Conversion complete: {safe_filename}",
                    extra={"extra": {
                        "tier": result.tier.value,
                        "quality": result.quality_score,
                        "time": result.processing_time,
                    }}
                )
                
                return response
                
            except SutraException:
                raise
            except Exception as e:
                logger.error(f"Conversion failed: {e}", exc_info=True)
                raise HTTPException(
                    status_code=500,
                    detail=f"Conversion failed: {str(e)}"
                )
            finally:
                # Cleanup temporary files
                try:
                    temp_file.unlink(missing_ok=True)
                    temp_dir.rmdir()
                except Exception as e:
                    logger.warning(f"Cleanup failed: {e}")
    
    @app.get("/stats", tags=["Monitoring"])
    async def get_stats(cache: CacheManagerDep) -> dict:
        """Get system statistics"""
        return cache.get_stats()
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    from ..config import get_settings
    
    settings = get_settings()
    
    uvicorn.run(
        "sutra.api.app:app",
        host=settings.api.host,
        port=settings.api.port,
        workers=settings.api.workers if settings.is_production() else 1,
        reload=settings.is_development(),
        log_config=None,  # We handle logging ourselves
    )
