"""Service for managing application caching."""
import logging
from datetime import datetime, timedelta, time
from typing import Any, Callable, Dict, Optional, Tuple, Union
import redis
import pickle
import hashlib
import inspect
import asyncio
from functools import wraps

from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """
    Service for managing caching functionality.

    This service provides methods for caching and retrieving data,
    as well as utility methods for cache management.
    """

    _instance = None
    _redis_client = None

    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super(CacheService, cls).__new__(cls)
            cls._initialize_redis()
        return cls._instance

    @classmethod
    def _initialize_redis(cls):
        """Initialize the Redis client."""
        try:
            cls._redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=False  # We want binary data for pickle
            )
            # Test connection
            cls._redis_client.ping()
            logger.info("Successfully connected to Redis")
        except redis.ConnectionError as e:
            logger.warning(f"Could not connect to Redis: {str(e)}. Caching will be disabled.")
            cls._redis_client = None

    @classmethod
    def is_available(cls) -> bool:
        """
        Check if caching is available.

        Returns:
            bool: True if caching is available, False otherwise
        """
        if cls._redis_client is None:
            return False

        try:
            return cls._redis_client.ping()
        except Exception:
            return False

    @classmethod
    def generate_key(cls, prefix: str, *args, **kwargs) -> str:
        """
        Generate a cache key from the given arguments.

        Args:
            prefix: Prefix for the key
            *args: Positional arguments to include in the key
            **kwargs: Keyword arguments to include in the key

        Returns:
            str: The generated cache key
        """
        # Convert args and kwargs to a string representation
        key_parts = [prefix]

        if args:
            key_parts.append(str(args))

        if kwargs:
            # Sort kwargs by key to ensure consistent order
            sorted_kwargs = sorted(kwargs.items())
            key_parts.append(str(sorted_kwargs))

        # Join parts and hash to create a deterministic key
        key_str = ":".join(key_parts)
        hashed = hashlib.md5(key_str.encode()).hexdigest()

        return f"{settings.CACHE_PREFIX}:{prefix}:{hashed}"

    @classmethod
    def set(
            cls,
            key: str,
            value: Any,
            expire: Optional[int] = None,
            nx: bool = False
    ) -> bool:
        """
        Set a value in the cache.

        Args:
            key: The cache key
            value: The value to store
            expire: Expiration time in seconds, or None for no expiration
            nx: If True, only set if key doesn't exist

        Returns:
            bool: True if successful, False otherwise
        """
        if not cls.is_available():
            return False

        try:
            # Serialize the value
            serialized = pickle.dumps(value)

            # Set the value
            if nx:
                return bool(cls._redis_client.setnx(key, serialized))

            cls._redis_client.set(key, serialized)

            # Set expiration if specified
            if expire is not None:
                cls._redis_client.expire(key, expire)

            return True

        except Exception as e:
            logger.error(f"Error setting cache key {key}: {str(e)}")
            return False

    @classmethod
    def get(cls, key: str) -> Tuple[bool, Any]:
        """
        Get a value from the cache.

        Args:
            key: The cache key

        Returns:
            Tuple[bool, Any]: A tuple containing a success flag and the value
                              (True, value) if successful, (False, None) otherwise
        """
        if not cls.is_available():
            return False, None

        try:
            # Get the value
            value = cls._redis_client.get(key)

            if value is None:
                return False, None

            # Deserialize the value
            deserialized = pickle.loads(value)
            return True, deserialized

        except Exception as e:
            logger.error(f"Error getting cache key {key}: {str(e)}")
            return False, None

    @classmethod
    def delete(cls, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: The cache key

        Returns:
            bool: True if successful, False otherwise
        """
        if not cls.is_available():
            return False

        try:
            return bool(cls._redis_client.delete(key))
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {str(e)}")
            return False

    @classmethod
    def clear_namespace(cls, namespace: str) -> int:
        """
        Clear all keys in a namespace.

        Args:
            namespace: The namespace to clear

        Returns:
            int: The number of keys deleted
        """
        if not cls.is_available():
            return 0

        try:
            # Get all keys in the namespace
            pattern = f"{settings.CACHE_PREFIX}:{namespace}:*"
            keys = cls._redis_client.keys(pattern)

            if not keys:
                return 0

            # Delete all keys
            return cls._redis_client.delete(*keys)

        except Exception as e:
            logger.error(f"Error clearing namespace {namespace}: {str(e)}")
            return 0

    @classmethod
    def cache_decorator(
            cls,
            expire: int,
            prefix: Optional[str] = None,
            invalidate_at_midnight: bool = False
    ) -> Callable:
        """
        Create a decorator for caching function results.

        Args:
            expire: Expiration time in seconds
            prefix: Prefix for the cache key, defaults to function name
            invalidate_at_midnight: If True, invalidate at midnight UTC

        Returns:
            Callable: A decorator function
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not cls.is_available():
                    # If caching is not available, just call the function
                    return await func(*args, **kwargs)

                # Generate cache key
                key_prefix = prefix or func.__qualname__
                cache_key = cls.generate_key(key_prefix, *args, **kwargs)

                # Try to get from cache
                cached, value = cls.get(cache_key)
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
                    now = datetime.utcnow()
                    midnight = datetime.combine(now.date() + timedelta(days=1), time(0, 0))
                    seconds_to_midnight = (midnight - now).total_seconds()
                    expiration = min(expire, int(seconds_to_midnight))

                # Store in cache
                cls.set(cache_key, result, expire=expiration)

                return result

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not cls.is_available():
                    # If caching is not available, just call the function
                    return func(*args, **kwargs)

                # Generate cache key
                key_prefix = prefix or func.__qualname__
                cache_key = cls.generate_key(key_prefix, *args, **kwargs)

                # Try to get from cache
                cached, value = cls.get(cache_key)
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
                    now = datetime.utcnow()
                    midnight = datetime.combine(now.date() + timedelta(days=1), time(0, 0))
                    seconds_to_midnight = (midnight - now).total_seconds()
                    expiration = min(expire, int(seconds_to_midnight))

                # Store in cache
                cls.set(cache_key, result, expire=expiration)

                return result

            # Return the appropriate wrapper based on whether the function is async
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator