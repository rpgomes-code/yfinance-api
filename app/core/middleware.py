"""FastAPI middleware for the YFinance API.

This module contains middleware for request processing, including
- Request ID generation
- Logging
- Rate limiting
- Performance tracking
- Error handling
"""
import logging
import time
import uuid
from typing import Callable, Dict, Optional, Tuple

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.config import settings
from app.core.exceptions import RateLimitExceededError
from app.services.metrics_service import MetricsService
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds a unique request ID to each request.

    This ID can be used to track requests through the system.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request to add a unique request ID.

        Args:
            request: The HTTP request
            call_next: The next middleware or endpoint

        Returns:
            Response: The HTTP response
        """
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Add the request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging requests and responses.

    This middleware logs information about each request and response,
    including timing information.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request to log information.

        Args:
            request: The HTTP request
            call_next: The next middleware or endpoint

        Returns:
            Response: The HTTP response
        """
        # Get request information
        start_time = time.time()
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "data": {
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.query_params),
                    "client_host": request.client.host if request.client else "unknown",
                    "user_agent": request.headers.get("user-agent", "unknown"),
                }
            }
        )

        # Process request
        try:
            response = await call_next(request)

            # Calculate response time
            process_time = time.time() - start_time

            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path} {response.status_code}",
                extra={
                    "data": {
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "processing_time": process_time,
                    }
                }
            )

            # Add timing header
            response.headers["X-Process-Time"] = str(process_time)

            return response

        except Exception as e:
            # Calculate response time
            process_time = time.time() - start_time

            # Log exception
            logger.exception(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "data": {
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "error": str(e),
                        "processing_time": process_time,
                    }
                }
            )

            # Re-raise the exception
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests.

    This middleware limits the number of requests that can be made
    in a specified time period.
    """

    def __init__(
            self,
            app: ASGIApp,
            requests: int = settings.RATE_LIMIT_REQUESTS,
            period: int = settings.RATE_LIMIT_PERIOD,
    ):
        """
        Initialize rate limit middleware.

        Args:
            app: The ASGI application
            requests: Maximum number of requests allowed
            period: Time period in seconds
        """
        super().__init__(app)
        self.requests = requests
        self.period = period
        self.cache_service = CacheService()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request to apply rate limiting.

        Args:
            request: The HTTP request
            call_next: The next middleware or endpoint

        Returns:
            Response: The HTTP response

        Raises:
            RateLimitExceededError: If the rate limit is exceeded
        """
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        # Skip rate limiting for excluded paths
        if self._should_skip_rate_limit(request):
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Generate cache key
        rate_limit_key = f"rate_limit:{client_ip}"

        # Check if rate limit exists
        counter = await self._get_rate_limit_counter(rate_limit_key)

        if counter >= self.requests:
            # Rate limit exceeded
            logger.warning(
                f"Rate limit exceeded for {client_ip}: {counter} requests in {self.period}s",
                extra={"data": {"client_ip": client_ip}}
            )

            # Calculate time until reset
            reset_time = await self._get_rate_limit_reset_time(rate_limit_key)

            # Add rate limit headers
            headers = {
                "X-RateLimit-Limit": str(self.requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset_time),
            }

            # Raise rate limit error
            raise RateLimitExceededError(
                detail=f"Rate limit exceeded: {self.requests} requests per {self.period} seconds",
                headers=headers
            )

        # Increment rate limit counter
        new_counter = await self._increment_rate_limit_counter(rate_limit_key)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.requests - new_counter))
        response.headers["X-RateLimit-Reset"] = str(await self._get_rate_limit_reset_time(rate_limit_key))

        return response

    def _should_skip_rate_limit(self, request: Request) -> bool:
        """
        Check if rate limiting should be skipped for this request.

        Args:
            request: The HTTP request

        Returns:
            bool: True if rate limiting should be skipped
        """
        # Skip rate limiting for documentation endpoints
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return True

        # Skip rate limiting for static files
        if request.url.path.startswith("/static/"):
            return True

        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/ping"]:
            return True

        return False

    async def _get_rate_limit_counter(self, key: str) -> int:
        """
        Get the current rate limit counter.

        Args:
            key: The rate limit key

        Returns:
            int: The current counter value
        """
        if not self.cache_service.is_available():
            # If Redis is not available, don't apply rate limiting
            return 0

        success, value = self.cache_service.get(key)

        if not success:
            return 0

        return value or 0

    async def _increment_rate_limit_counter(self, key: str) -> int:
        """
        Increment the rate limit counter.

        Args:
            key: The rate limit key

        Returns:
            int: The new counter value
        """
        if not self.cache_service.is_available():
            # If Redis is not available, don't apply rate limiting
            return 0

        # Check if key exists
        success, value = self.cache_service.get(key)

        if not success or value is None:
            # Create new counter
            self.cache_service.set(key, 1, expire=self.period)
            return 1

        # Increment counter
        new_value = value + 1
        self.cache_service.set(key, new_value, expire=self.period)

        return new_value

    async def _get_rate_limit_reset_time(self, key: str) -> int:
        """
        Get the time until the rate limit resets.

        Args:
            key: The rate limit key

        Returns:
            int: Seconds until reset
        """
        if not self.cache_service.is_available():
            # If Redis is not available, use default period
            return self.period

        client = self.cache_service._redis_client

        # Get TTL of the key
        ttl = client.ttl(key)

        # If key doesn't exist or has no expiration, use default period
        if ttl < 0:
            return self.period

        return ttl


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking request performance.

    This middleware records performance metrics for each request.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request to track performance.

        Args:
            request: The HTTP request
            call_next: The next middleware or endpoint

        Returns:
            Response: The HTTP response
        """
        if not settings.METRICS_ENABLED:
            return await call_next(request)

        # Get metrics service
        metrics_service = MetricsService()

        # Start timer
        start_time = time.time()

        # Parse endpoint name
        endpoint_name = self._parse_endpoint_name(request)

        # Set endpoint as active
        metrics_service.set_endpoint_active(endpoint_name)

        # Process request
        error = False
        try:
            response = await call_next(request)
        except Exception:
            error = True
            raise
        finally:
            # Calculate response time
            response_time = time.time() - start_time

            # Record metrics
            metrics_service.record_endpoint_call(
                endpoint_name=endpoint_name,
                path=request.url.path,
                response_time=response_time,
                error=error
            )

            # Set endpoint as inactive
            metrics_service.set_endpoint_inactive(endpoint_name)

        return response

    def _parse_endpoint_name(self, request: Request) -> str:
        """
        Parse the endpoint name from the request.

        Args:
            request: The HTTP request

        Returns:
            str: The endpoint name
        """
        # Get route path if available
        if hasattr(request, "scope") and "route" in request.scope and hasattr(request.scope["route"], "path"):
            return request.scope["route"].path

        # Otherwise use URL path
        return request.url.path


def add_middleware(app: FastAPI) -> None:
    """
    Add middleware to FastAPI application.

    Args:
        app: FastAPI application
    """
    # Add middleware in reverse order (last added = first executed)
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(LoggingMiddleware)

    if settings.RATE_LIMIT_ENABLED:
        app.add_middleware(
            RateLimitMiddleware,
            requests=settings.RATE_LIMIT_REQUESTS,
            period=settings.RATE_LIMIT_PERIOD
        )

    if settings.METRICS_ENABLED:
        app.add_middleware(PerformanceMiddleware)