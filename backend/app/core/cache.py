import logging
import json
import hashlib
import time
from typing import Dict, Any, Optional, TypeVar, Callable, Union, Awaitable
from functools import wraps
import inspect

logger = logging.getLogger(__name__)

# Type for cache values
T = TypeVar('T')


# In-memory cache (in a production app, use Redis or similar)
class SimpleCache:
    """Simple in-memory cache for application data."""

    def __init__(self, ttl: int = 300):
        self.ttl = ttl  # Default TTL in seconds
        self.cache: Dict[str, Dict[str, Any]] = {}

    def _get_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from function arguments."""
        # Convert all arguments to JSON and hash them
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key_str = json.dumps(key_parts, sort_keys=True)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"

    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        if key not in self.cache:
            return None

        cache_item = self.cache[key]
        # Check if item has expired
        if cache_item["expiry"] < time.time():
            del self.cache[key]
            return None

        return cache_item["value"]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in the cache with expiry time."""
        expiry = time.time() + (ttl if ttl is not None else self.ttl)
        self.cache[key] = {
            "value": value,
            "expiry": expiry
        }

    def delete(self, key: str) -> None:
        """Delete a value from the cache."""
        if key in self.cache:
            del self.cache[key]

    def clear(self) -> None:
        """Clear all values from the cache."""
        self.cache.clear()

    def clean_expired(self) -> int:
        """Remove expired items from the cache and return count."""
        current_time = time.time()
        expired_keys = [
            key for key, item in self.cache.items()
            if item["expiry"] < current_time
        ]

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)


# Create global cache instance
cache = SimpleCache()


def cache_decorator(ttl: Optional[int] = None,
                    prefix: Optional[str] = None,
                    enabled: bool = True):
    """
    Decorator for caching function results.

    Args:
        ttl: Time to live in seconds
        prefix: Prefix for cache keys
        enabled: Whether caching is enabled
    """

    def decorator(func):
        if not enabled:
            return func

        # Get function name for cache key prefix
        func_prefix = prefix or func.__name__

        # Check if the function is async
        is_async = inspect.iscoroutinefunction(func)

        if is_async:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = cache._get_key(func_prefix, *args, **kwargs)

                # Try to get from cache
                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit for {cache_key}")
                    return cached_value

                # Call the function
                logger.debug(f"Cache miss for {cache_key}")
                result = await func(*args, **kwargs)

                # Store in cache
                cache.set(cache_key, result, ttl)

                return result

            return async_wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = cache._get_key(func_prefix, *args, **kwargs)

                # Try to get from cache
                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit for {cache_key}")
                    return cached_value

                # Call the function
                logger.debug(f"Cache miss for {cache_key}")
                result = func(*args, **kwargs)

                # Store in cache
                cache.set(cache_key, result, ttl)

                return result

            return wrapper

    return decorator