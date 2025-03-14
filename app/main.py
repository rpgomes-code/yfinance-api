"""Main application module for the YFinance API.

This module creates and configures the FastAPI application, setting up middleware,
exception handlers, and including API routes.
"""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import add_exception_handlers
from app.core.logging import setup_logging
from app.core.middleware import add_middleware
from app.core.cache import setup_cache
from app.api import api_router
from app.services.metrics_service import MetricsService
from app.services.scheduler_service import SchedulerService

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan():
    """
    Lifespan manager for FastAPI application.

    This handles startup and shutdown events for the application.

    """
    # Startup
    logger.info(f"Starting YFinance API v{settings.API_VERSION}")

    # Initialize cache
    setup_cache()
    logger.info("Cache initialized")

    # Start scheduler
    scheduler = SchedulerService()
    await scheduler.start()
    logger.info("Scheduler started")

    # Yield control back to FastAPI
    yield

    # Shutdown
    logger.info("Shutting down YFinance API")

    # Stop scheduler
    await scheduler.stop()
    logger.info("Scheduler stopped")

def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured application
    """
    # Create FastAPI application
    setup_app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOC_URL,
        openapi_url=settings.OPENAPI_URL,
        lifespan=lifespan
    )

    # Add middleware
    add_middleware(setup_app)

    # Add CORS middleware
    setup_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add exception handlers
    add_exception_handlers(setup_app)

    # Include API router
    setup_app.include_router(api_router)

    # Add root endpoint
    @setup_app.get("/", include_in_schema=False)
    async def root():
        """Root endpoint that returns basic API information."""
        return {
            "name": settings.API_TITLE,
            "version": settings.API_VERSION,
            "description": settings.API_DESCRIPTION,
            "docs_url": settings.DOCS_URL
        }

    # Add health check endpoint
    @setup_app.get("/health", include_in_schema=False)
    async def health():
        """Health check endpoint for monitoring."""
        return {
            "status": "healthy",
            "version": settings.API_VERSION,
            "timestamp": time.time()
        }

    # Add metrics endpoint
    @setup_app.get("/metrics", include_in_schema=False)
    async def metrics():
        """Metrics endpoint for monitoring."""
        if not settings.METRICS_ENDPOINT_ENABLED:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": "Metrics endpoint is disabled"}
            )

        metrics_service = MetricsService()
        return metrics_service.get_summary()

    return setup_app

# Create the application instance
app = create_application()

# Log application startup
logger.info(f"Application created: {settings.API_TITLE} v{settings.API_VERSION}")