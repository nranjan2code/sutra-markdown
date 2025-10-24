"""
FastAPI Dependencies for Dependency Injection

Provides clean dependency injection for services, ensuring testability
and proper lifecycle management.
"""

from typing import Annotated
from fastapi import Depends, Header, HTTPException, status
from functools import lru_cache

from ..config import Settings, get_settings
from ..intelligence.embeddings import EmbeddingService
from ..cache.manager import CacheManager
from ..exceptions import InvalidTokenError
from ..logging_config import get_logger

logger = get_logger(__name__)


# Settings dependency (singleton)
@lru_cache
def get_settings_cached() -> Settings:
    """Get cached settings instance"""
    return get_settings()


SettingsDep = Annotated[Settings, Depends(get_settings_cached)]


# Embedding service dependency (singleton)
_embedding_service: EmbeddingService | None = None


def get_embedding_service(settings: SettingsDep) -> EmbeddingService:
    """
    Get or create embedding service singleton
    
    This ensures only one embedding service is created and shared
    across all requests for efficiency.
    """
    global _embedding_service
    
    if _embedding_service is None:
        logger.info("Initializing embedding service")
        try:
            _embedding_service = EmbeddingService(
                config={
                    "model_path": str(settings.embeddings.model_path),
                    "vision_model_path": str(settings.embeddings.vision_model_path),
                    "device": settings.embeddings.device,
                    "batch_size": settings.embeddings.batch_size,
                    "max_workers": settings.embeddings.max_workers,
                }
            )
            logger.info(f"Embedding service initialized: {_embedding_service}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}", exc_info=True)
            raise
    
    return _embedding_service


EmbeddingServiceDep = Annotated[EmbeddingService, Depends(get_embedding_service)]


# Cache manager dependency (singleton)
_cache_manager: CacheManager | None = None


def get_cache_manager(settings: SettingsDep) -> CacheManager:
    """
    Get or create cache manager singleton
    """
    global _cache_manager
    
    if _cache_manager is None:
        logger.info("Initializing cache manager")
        _cache_manager = CacheManager(
            enable_document_cache=settings.cache.enabled,
            enable_embedding_cache=settings.cache.enabled,
            enable_result_cache=settings.cache.enabled,
            redis_url=settings.cache.redis_url if settings.cache.redis_enabled else None,
            max_memory_entries=settings.cache.max_memory_entries,
            ttl_seconds=settings.cache.ttl_seconds,
        )
        logger.info("Cache manager initialized")
    
    return _cache_manager


CacheManagerDep = Annotated[CacheManager, Depends(get_cache_manager)]


# Authentication dependency (optional, for future use)
async def get_current_user(
    settings: SettingsDep,
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header()] = None,
) -> dict[str, str] | None:
    """
    Extract and validate user from request headers
    
    Supports both JWT tokens and API keys.
    Returns None if authentication is disabled.
    """
    if not settings.security.enable_auth:
        return None
    
    # Check API key first
    if x_api_key:
        # TODO: Validate API key against database
        # For now, just check it exists
        if len(x_api_key) >= 32:
            return {"user_id": "api_key_user", "auth_method": "api_key"}
        raise InvalidTokenError("Invalid API key")
    
    # Check JWT token
    if authorization:
        if not authorization.startswith("Bearer "):
            raise InvalidTokenError("Invalid authorization header format")
        
        token = authorization[7:]  # Remove "Bearer " prefix
        
        # TODO: Validate JWT token
        # For now, just check it exists
        if len(token) >= 10:
            return {"user_id": "jwt_user", "auth_method": "jwt"}
        raise InvalidTokenError("Invalid JWT token")
    
    # No authentication provided but required
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )


CurrentUserDep = Annotated[dict[str, str] | None, Depends(get_current_user)]


# Rate limiting dependency (placeholder)
async def check_rate_limit(
    settings: SettingsDep,
    x_forwarded_for: Annotated[str | None, Header()] = None,
) -> None:
    """
    Check rate limits for the request
    
    Uses X-Forwarded-For header for IP-based rate limiting.
    """
    if not settings.security.rate_limit_per_minute:
        return
    
    # TODO: Implement actual rate limiting with Redis
    # For now, just a placeholder
    pass


RateLimitDep = Annotated[None, Depends(check_rate_limit)]


def reset_singletons() -> None:
    """
    Reset all singleton instances
    
    Useful for testing to ensure clean state.
    """
    global _embedding_service, _cache_manager
    _embedding_service = None
    _cache_manager = None
    logger.info("All singletons reset")
