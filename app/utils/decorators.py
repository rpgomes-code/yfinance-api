"""Custom decorators for the YFinance API.

This module provides decorators for endpoint functions, including
caching, validation, error handling, and performance tracking.
"""
import functools
import inspect
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Union

from fastapi import Depends, Request, Response

from app.core.config import settings
from app.core.exceptions import YFinanceError, TickerNotFoundError
from app.services.metrics_service import MetricsService
from app.services.cache_service import CacheService
from app.utils.formatters import format_response

logger = logging.getLogger(__name__)


def response_formatter(
        format_type: str = 'default',
        add_metadata: bool = False
) -> Callable:
    """
    Decorator for formatting endpoint responses.

    Args:
        format_type: Response format type (default, compact, extended)
        add_metadata: Whether to add metadata to response

    Returns:
        Callable: Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get format from query parameters if provided
            format_param = kwargs.get('format')
            current_format = format_param if format_param else format_type

            # Call the function
            result = await func(*args, **kwargs)

            # Format the response
            metadata = None

            if add_metadata:
                # Add basic metadata
                metadata = {
                    "endpoint": func.__name__,
                }

                # Add parameter info
                params = {}
                for key, value in kwargs.items():
                    if key not in ('request', 'response', 'format'):
                        params[key] = value

                if params:
                    metadata["parameters"] = params

            return format_response(result, current_format, metadata)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get format from query parameters if provided
            format_param = kwargs.get('format')
            current_format = format_param if format_param else format_type

            # Call the function
            result = func(*args, **kwargs)

            # Format the response
            metadata = None

            if add_metadata:
                # Add basic metadata
                metadata = {
                    "endpoint": func.__name__,
                }

                # Add parameter info
                params = {}
                for key, value in kwargs.items():
                    if key not in ('request', 'response', 'format'):
                        params[key] = value

                if params:
                    metadata["parameters"] = params

            return format_response(result, current_format, metadata)

        # Return the appropriate wrapper based on whether the function is async
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def error_handler() -> Callable:
    """
    Decorator for handling errors in endpoint functions.

    Returns:
        Callable: Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except TickerNotFoundError:
                # Re-raise ticker not found errors
                raise
            except YFinanceError:
                # Re-raise YFinance errors
                raise
            except Exception as e:
                # Log the error
                logger.exception(f"Error in {func.__name__}: {str(e)}")

                # Convert to YFinance error
                raise YFinanceError(f"Error processing request: {str(e)}")

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except TickerNotFoundError:
                # Re-raise ticker not found errors
                raise
            except YFinanceError:
                # Re-raise YFinance errors
                raise
            except Exception as e:
                # Log the error
                logger.exception(f"Error in {func.__name__}: {str(e)}")

                # Convert to YFinance error
                raise YFinanceError(f"Error processing request: {str(e)}")

        # Return the appropriate wrapper based on whether the function is async
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def performance_tracker() -> Callable:
    """
    Decorator for tracking function performance.

    Returns:
        Callable: Decorator function
    """
    metrics_service = MetricsService()

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get endpoint name and path
            endpoint_name = func.__name__
            path = f"/v1/{endpoint_name.replace('get_', '').replace('_', '/')}"

            # Start timer
            start_time = time.time()
            error = False

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception:
                error = True
                raise
            finally:
                # Calculate response time
                response_time = time.time() - start_time

                # Record metrics
                metrics_service.record_endpoint_call(
                    endpoint_name=endpoint_name,
                    path=path,
                    response_time=response_time,
                    error=error
                )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get endpoint name and path
            endpoint_name = func.__name__
            path = f"/v1/{endpoint_name.replace('get_', '').replace('_', '/')}"

            # Start timer
            start_time = time.time()
            error = False

            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                error = True
                raise
            finally:
                # Calculate response time
                response_time = time.time() - start_time

                # Record metrics
                metrics_service.record_endpoint_call(
                    endpoint_name=endpoint_name,
                    path=path,
                    response_time=response_time,
                    error=error
                )

        # Return the appropriate wrapper based on whether the function is async
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def custom_cache(
        expire: int,
        namespace: Optional[str] = None,
        key_prefix: Optional[str] = None,
        invalidate_at_midnight: bool = False
) -> Callable:
    """
    Decorator for caching function results.

    Args:
        expire: Expiration time in seconds
        namespace: Cache namespace
        key_prefix: Prefix for cache key
        invalidate_at_midnight: Whether to invalidate at midnight UTC

    Returns:
        Callable: Decorator function
    """
    cache_service = CacheService()

    def decorator(func: Callable) -> Callable:
        # Get function name for key prefix
        func_name = key_prefix or func.__name__

        # Build cache namespace
        cache_ns = namespace or f"yfinance:{func_name}"

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Skip caching if disabled
            if not settings.CACHE_ENABLED:
                return await func(*args, **kwargs)

            # Generate cache key
            cache_key = cache_service.generate_key(
                cache_ns,
                *args,
                **{k: v for k, v in kwargs.items() if k != 'request' and k != 'response'}
            )

            # Try to get from cache
            cached, value = cache_service.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for {cache_key}")
                return value

            # Call the function
            logger.debug(f"Cache miss for {cache_key}")
            result = await func(*args, **kwargs)

            # Calculate expiration time
            expiration = expire
            if invalidate_at_midnight:
                # Calculate seconds until midnight UTC
                from app.core.cache import calculate_seconds_until_midnight
                seconds_to_midnight = calculate_seconds_until_midnight()
                expiration = min(expire, seconds_to_midnight)

                logger.debug(f"Setting expiration to {expiration}s (midnight invalidation)")

            # Store in cache
            cache_service.set(cache_key, result, expire=expiration)

            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Skip caching if disabled
            if not settings.CACHE_ENABLED:
                return func(*args, **kwargs)

            # Generate cache key
            cache_key = cache_service.generate_key(
                cache_ns,
                *args,
                **{k: v for k, v in kwargs.items() if k != 'request' and k != 'response'}
            )

            # Try to get from cache
            cached, value = cache_service.get(cache_key)
            if cached:
                logger.debug(f"Cache hit for {cache_key}")
                return value

            # Call the function
            logger.debug(f"Cache miss for {cache_key}")
            result = func(*args, **kwargs)

            # Calculate expiration time
            expiration = expire
            if invalidate_at_midnight:
                # Calculate seconds until midnight UTC
                from app.core.cache import calculate_seconds_until_midnight
                seconds_to_midnight = calculate_seconds_until_midnight()
                expiration = min(expire, seconds_to_midnight)

                logger.debug(f"Setting expiration to {expiration}s (midnight invalidation)")

            # Store in cache
            cache_service.set(cache_key, result, expire=expiration)

            return result

        # Return the appropriate wrapper based on whether the function is async
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def endpoint_decorator(
        cache_duration: Optional[str] = None,
        invalidate_at_midnight: bool = False,
        track_performance: bool = True,
        handle_errors: bool = True,
        format_response: bool = True,
        format_type: str = 'default',
        add_metadata: bool = False
) -> Callable:
    """
    Combined decorator for endpoint functions.

    This decorator combines caching, performance tracking,
    error handling, and response formatting.

    Args:
        cache_duration: Cache duration (30_minutes, 1_day, 1_week, 1_month, 3_months)
        invalidate_at_midnight: Whether to invalidate at midnight UTC
        track_performance: Whether to track performance
        handle_errors: Whether to handle errors
        format_response: Whether to format response
        format_type: Response format type (default, compact, extended)
        add_metadata: Whether to add metadata to response

    Returns:
        Callable: Decorator function
    """

    def decorator(func: Callable) -> Callable:
        # Apply decorators in reverse order (last applied = first executed)
        decorated = func

        if format_response:
            decorated = response_formatter(format_type, add_metadata)(decorated)

        if handle_errors:
            decorated = error_handler()(decorated)

        if cache_duration:
            # Get cache time in seconds
            from app.core.constants import (
                THIRTY_MINUTES, ONE_DAY, ONE_WEEK, ONE_MONTH, THREE_MONTHS
            )

            cache_times = {
                "30_minutes": THIRTY_MINUTES,
                "1_day": ONE_DAY,
                "1_week": ONE_WEEK,
                "1_month": ONE_MONTH,
                "3_months": THREE_MONTHS
            }

            expire = cache_times.get(cache_duration, ONE_DAY)
            decorated = custom_cache(expire, invalidate_at_midnight=invalidate_at_midnight)(decorated)

        if track_performance:
            decorated = performance_tracker()(decorated)

        return decorated

    return decorator