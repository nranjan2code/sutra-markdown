"""
Production-Grade Configuration Management using Pydantic Settings

Provides type-safe configuration with validation, environment variable support,
and comprehensive settings management. All settings are validated at startup.
"""

from typing import Literal, Optional
from pathlib import Path
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class ComplexitySettings(BaseSettings):
    """Configuration for complexity analysis"""
    
    enabled: bool = Field(default=True, description="Enable complexity analysis")
    tier1_threshold: float = Field(default=0.3, ge=0.0, le=1.0, description="Threshold for Tier 1")
    tier2_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Threshold for Tier 2")
    timeout_seconds: float = Field(default=30.0, gt=0, description="Analysis timeout in seconds")
    max_pages_analysis: int = Field(default=50, gt=0, description="Max pages to analyze")
    cache_results: bool = Field(default=True, description="Cache analysis results")
    fallback_on_error: bool = Field(default=True, description="Fall back to simple analysis on error")
    
    @field_validator('tier2_threshold')
    @classmethod
    def validate_tier_thresholds(cls, v: float, info) -> float:
        """Ensure tier2 threshold is greater than tier1"""
        if 'tier1_threshold' in info.data and v <= info.data['tier1_threshold']:
            raise ValueError("tier2_threshold must be greater than tier1_threshold")
        return v
    
    model_config = SettingsConfigDict(
        env_prefix="SUTRA_COMPLEXITY_",
        case_sensitive=False
    )


class EmbeddingSettings(BaseSettings):
    """Configuration for embeddings service"""
    
    mode: Literal["local"] = Field(default="local", description="Always use local embeddings")
    model_path: Path = Field(default=Path("./models/nomic-embed-v2"), description="Text model path")
    vision_model_path: Path = Field(default=Path("./models/nomic-embed-vision-v1.5"), description="Vision model path")
    device: Literal["auto", "cuda", "cpu"] = Field(default="auto", description="Compute device")
    batch_size: int = Field(default=64, ge=1, le=256, description="Batch size for embeddings")
    max_workers: int = Field(default=4, ge=1, le=16, description="Number of worker processes")
    
    model_config = SettingsConfigDict(
        env_prefix="NOMIC_",
        case_sensitive=False
    )


class CacheSettings(BaseSettings):
    """Configuration for caching"""
    
    enabled: bool = Field(default=True, description="Enable caching")
    ttl_seconds: int = Field(default=86400, ge=0, description="Cache TTL in seconds")
    max_memory_entries: int = Field(default=1000, ge=0, description="Max in-memory cache entries")
    redis_enabled: bool = Field(default=True, description="Use Redis for distributed caching")
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    redis_max_connections: int = Field(default=50, ge=1, description="Redis connection pool size")
    
    model_config = SettingsConfigDict(
        env_prefix="CACHE_",
        case_sensitive=False
    )


class APISettings(BaseSettings):
    """Configuration for API behavior"""
    
    host: str = Field(default="0.0.0.0", description="API host")
    port: int = Field(default=8000, ge=1, le=65535, description="API port")
    enable_intelligence: bool = Field(default=True, description="Enable AI features")
    default_quality: Literal["low", "medium", "high", "ultra"] = Field(default="high", description="Default quality")
    max_file_size_mb: int = Field(default=500, gt=0, description="Max file size in MB")
    timeout_seconds: int = Field(default=300, gt=0, description="Request timeout in seconds")
    workers: int = Field(default=4, ge=1, description="Number of API workers")
    cors_origins: list[str] = Field(default=["*"], description="Allowed CORS origins")
    
    model_config = SettingsConfigDict(
        env_prefix="API_",
        case_sensitive=False
    )


class SecuritySettings(BaseSettings):
    """Security configuration"""
    
    secret_key: str = Field(
        default="INSECURE_DEV_KEY_CHANGE_IN_PRODUCTION_" + "x" * 16,
        min_length=32, 
        description="Secret key for JWT - MUST be changed in production"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_minutes: int = Field(default=60, gt=0, description="JWT expiration time")
    api_key_header: str = Field(default="X-API-Key", description="API key header name")
    rate_limit_per_minute: int = Field(default=60, ge=0, description="Rate limit per minute")
    enable_auth: bool = Field(default=False, description="Enable authentication")
    
    model_config = SettingsConfigDict(
        env_prefix="SECURITY_",
        case_sensitive=False
    )


class MonitoringSettings(BaseSettings):
    """Monitoring and observability configuration"""
    
    enable_metrics: bool = Field(default=True, description="Enable Prometheus metrics")
    enable_tracing: bool = Field(default=False, description="Enable distributed tracing")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", 
        description="Logging level"
    )
    log_format: Literal["json", "text"] = Field(default="json", description="Log format")
    metrics_port: int = Field(default=9090, ge=1, le=65535, description="Metrics endpoint port")
    
    model_config = SettingsConfigDict(
        env_prefix="MONITORING_",
        case_sensitive=False
    )


class Settings(BaseSettings):
    """
    Main application settings
    
    Loads configuration from environment variables and .env files.
    All settings are validated at startup for production safety.
    """
    
    # Application metadata
    app_name: str = Field(default="Sutra-Markdown", description="Application name")
    app_version: str = Field(default="2.1.0", description="Application version")
    environment: Literal["development", "staging", "production"] = Field(
        default="production", 
        description="Environment"
    )
    debug: bool = Field(default=False, description="Debug mode")
    
    # Sub-configurations
    complexity: ComplexitySettings = Field(default_factory=ComplexitySettings)
    embeddings: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    api: APISettings = Field(default_factory=APISettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    
    # Storage
    upload_dir: Path = Field(default=Path("./uploads"), description="Upload directory")
    output_dir: Path = Field(default=Path("./outputs"), description="Output directory")
    cache_dir: Path = Field(default=Path("./cache"), description="Cache directory")
    log_dir: Path = Field(default=Path("./logs"), description="Log directory")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore"
    )
    
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create required directories if they don't exist"""
        for directory in [self.upload_dir, self.output_dir, self.cache_dir, self.log_dir]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.environment == "development"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get global settings instance (singleton pattern)
    
    This function provides dependency injection support for FastAPI.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment (useful for testing)"""
    global _settings
    _settings = Settings()
    return _settings


# Backwards compatibility alias
get_config = get_settings
