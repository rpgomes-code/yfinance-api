"""Application configuration module using Pydantic settings management."""
import os
from typing import Any, Dict, List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings model.

    This class uses Pydantic settings management to load configuration from
    environment variables with fallbacks to default values.
    """

    # API settings
    API_TITLE: str = "YFinance API"
    API_DESCRIPTION: str = "API for accessing Yahoo Finance data through yfinance"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = Field(False, env="DEBUG")
    ENVIRONMENT: str = Field("production", env="ENVIRONMENT")

    # Server settings
    API_PORT: int = Field(8000, env="API_PORT")
    WORKERS: int = Field(4, env="WORKERS")
    RELOAD: bool = Field(False, env="RELOAD")

    # CORS settings
    CORS_ORIGINS: List[str] = Field(["*"], env="CORS_ORIGINS")

    # Cache settings
    CACHE_ENABLED: bool = Field(True, env="CACHE_ENABLED")
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_DB: int = Field(0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(None, env="REDIS_PASSWORD")
    CACHE_PREFIX: str = Field("yfinance_api", env="CACHE_PREFIX")

    # Security settings
    API_KEY: Optional[str] = Field(None, env="API_KEY")
    SECRET_KEY: Optional[str] = Field(None, env="SECRET_KEY")

    # YFinance settings
    YFINANCE_REQUEST_TIMEOUT: int = Field(10, env="YFINANCE_REQUEST_TIMEOUT")
    YFINANCE_MAX_RETRIES: int = Field(3, env="YFINANCE_MAX_RETRIES")
    YFINANCE_PROXY: Optional[str] = Field(None, env="YFINANCE_PROXY")

    # Logging settings
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_PERIOD: int = Field(60, env="RATE_LIMIT_PERIOD")  # in seconds

    # Metrics and monitoring
    METRICS_ENABLED: bool = Field(True, env="METRICS_ENABLED")
    METRICS_ENDPOINT_ENABLED: bool = Field(False, env="METRICS_ENDPOINT_ENABLED")
    METRICS_ENDPOINT_TOKEN: Optional[str] = Field(None, env="METRICS_ENDPOINT_TOKEN")
    PROMETHEUS_PORT: int = Field(9090, env="PROMETHEUS_PORT")
    GRAFANA_PORT: int = Field(3000, env="GRAFANA_PORT")
    GRAFANA_USERNAME: str = Field("admin", env="GRAFANA_USERNAME")
    GRAFANA_PASSWORD: str = Field("admin", env="GRAFANA_PASSWORD")

    # Cache durations (in seconds)
    CACHE_30_MINUTES: int = 30 * 60
    CACHE_1_HOUR: int = 60 * 60
    CACHE_1_DAY: int = 24 * 60 * 60
    CACHE_1_WEEK: int = 7 * 24 * 60 * 60
    CACHE_1_MONTH: int = 30 * 24 * 60 * 60
    CACHE_3_MONTHS: int = 90 * 24 * 60 * 60

    # Documentation settings
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins from string to list if needed."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError("CORS_ORIGINS should be a comma-separated string or a list")

    @validator("ENVIRONMENT")
    def validate_environment(cls, v: str) -> str:
        """Validate environment string."""
        allowed = {"development", "testing", "staging", "production"}
        if v.lower() not in allowed:
            raise ValueError(f"ENVIRONMENT must be one of: {', '.join(allowed)}")
        return v.lower()

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level string."""
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v = v.upper()
        if v not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of: {', '.join(allowed)}")
        return v

    class Config:
        """Pydantic configuration."""
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached application settings.

    Uses functools.lru_cache to avoid reloading settings
    multiple times during application lifetime.

    Returns:
        Settings: Application settings
    """
    return Settings()


# Create a singleton instance of settings for use throughout the app
settings = get_settings()