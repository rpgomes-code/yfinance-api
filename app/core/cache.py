"""Caching functionality for the YFinance API.

This module provides decorators and utilities for caching API responses.
"""
import logging
from datetime import datetime, timedelta, time
from functools import wraps
from typing import Any, Callable, Optional

import redis
from app.core.config import settings
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None


def setup_cache() -> None:
    """
    Set up the Redis connection for caching.

    This function should be called during application startup.
    """
    global _redis_client

    try:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
            decode_responses=False,  # We want binary data for pickle
            socket_timeout=5,
            socket_connect_timeout=5
        )
        # Test connection
        _redis_client.ping()
        logger.info("Successfully connected to Redis for caching")
    except redis.ConnectionError as e:
        logger.warning(f"Could not connect to Redis: {str(e)}. Caching will be disabled.")
        _redis_client = None


def get_redis_client() -> Optional[redis.Redis]:
    """
    Get the Redis client.

    Returns:
        Optional[redis.Redis]: Redis client or None if not available
    """
    return _redis_client


def is_cache_available() -> bool:
    """
    Check if caching is available.

    Returns:
        bool: True if caching is available, False otherwise
    """
    try:
        client = get_redis_client()
        return client is not None and client.ping()
    except Exception:
        return False


def cache_30_minutes() -> Callable:
    """
    Decorator for caching response for 30 minutes.

    Returns:
        Callable: Decorator function
    """
    return CacheService.cache_decorator(expire=settings.CACHE_30_MINUTES)


def cache_1_hour() -> Callable:
    """
    Decorator for caching response for 1 hour.

    Returns:
        Callable: Decorator function
    """
    return CacheService.cache_decorator(expire=settings.CACHE_1_HOUR)


def cache_1_day(invalidate_at_midnight: bool = True) -> Callable:
    """
    Decorator for caching response for 1 day.

    Args:
        invalidate_at_midnight: If True, invalidate at midnight UTC

    Returns:
        Callable: Decorator function
    """
    return CacheService.cache_decorator(
        expire=settings.CACHE_1_DAY,
        invalidate_at_midnight=invalidate_at_midnight
    )


def cache_1_week() -> Callable:
    """
    Decorator for caching response for 1 week.

    Returns:
        Callable: Decorator function
    """
    return CacheService.cache_decorator(expire=settings.CACHE_1_WEEK)


def cache_1_month() -> Callable:
    """
    Decorator for caching response for 1 month.

    Returns:
        Callable: Decorator function
    """
    return CacheService.cache_decorator(expire=settings.CACHE_1_MONTH)


def cache_3_months() -> Callable:
    """
    Decorator for caching response for 3 months.

    Returns:
        Callable: Decorator function
    """
    return CacheService.cache_decorator(expire=settings.CACHE_3_MONTHS)


def calculate_seconds_until_midnight() -> int:
    """
    Calculate seconds until midnight UTC.

    Returns:
        int: Seconds until midnight UTC
    """
    now = datetime.utcnow()
    midnight = datetime.combine(now.date() + timedelta(days=1), time(0, 0))
    return int((midnight - now).total_seconds())


def clear_cache_namespace(namespace: str) -> int:
    """
    Clear all cache keys in a namespace.

    Args:
        namespace: The namespace to clear

    Returns:
        int: The number of keys cleared
    """
    return CacheService.clear_namespace(namespace)


def get_cache_stats() -> dict:
    """
    Get cache statistics.

    Returns:
        dict: Dictionary with cache statistics
    """
    if not is_cache_available():
        return {"available": False}

    client = get_redis_client()
    try:
        info = client.info()
        keys = client.keys(f"{settings.CACHE_PREFIX}:*")
        return {
            "available": True,
            "key_count": len(keys),
            "memory_used": info.get("used_memory_human", "unknown"),
            "hit_rate": info.get("keyspace_hits", 0) / (
                        info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1) or 1),
            "uptime_seconds": info.get("uptime_in_seconds", 0)
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {str(e)}")
        return {"available": False, "error": str(e)}