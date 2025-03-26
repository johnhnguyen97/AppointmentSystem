"""
Redis cache implementation with in-memory fallback for the application.
"""
import pickle
from datetime import datetime, timedelta
from typing import Any, Optional
import redis.asyncio as redis
from functools import wraps
import logging

from src.main.config import settings

logger = logging.getLogger(__name__)

class RedisCache:
    """Cache implementation with Redis and in-memory fallback."""

    def __init__(self):
        self._local_cache = {}  # In-memory cache
        self.redis = None
        if settings.REDIS_ENABLED:
            try:
                self.redis = redis.from_url(
                    settings.REDIS_URL,
                    encoding="utf-8",
                    decode_responses=False
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Redis: {str(e)}")

    async def connect(self) -> None:
        """Ensure connection to Redis if enabled."""
        if not settings.REDIS_ENABLED:
            logger.info("Redis is disabled, using in-memory cache only")
            return

        if not self.redis:
            logger.warning("Redis client not initialized, using in-memory cache only")
            return

        try:
            await self.redis.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed: {str(e)}, using in-memory cache only")
            self.redis = None

    async def close(self) -> None:
        """Close Redis connection if active."""
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def get(self, key: str) -> Any:
        """Get value from cache."""
        # Check local cache first
        if key in self._local_cache:
            value, expire_at = self._local_cache[key]
            if expire_at > datetime.now():
                return value
            del self._local_cache[key]

        # Try Redis if available
        if self.redis:
            try:
                value = await self.redis.get(key)
                if value:
                    value = pickle.loads(value)
                    # Cache in local memory for faster subsequent access
                    self._local_cache[key] = (value, datetime.now() + timedelta(minutes=1))
                    return value
            except Exception as e:
                logger.error(f"Redis get error for {key}: {str(e)}")

        return None

    async def set(self, key: str, value: Any, expire_in: Optional[int] = None) -> bool:
        """Set value in cache with optional expiration in seconds."""
        success = True

        # Always set in local cache
        expire_at = datetime.max if expire_in is None else datetime.now() + timedelta(seconds=expire_in)
        self._local_cache[key] = (value, expire_at)

        # Try Redis if available
        if self.redis:
            try:
                serialized = pickle.dumps(value)
                if expire_in:
                    await self.redis.setex(key, expire_in, serialized)
                else:
                    await self.redis.set(key, serialized)
            except Exception as e:
                logger.error(f"Redis set error for {key}: {str(e)}")
                success = False

        return success

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        success = True

        # Remove from local cache
        self._local_cache.pop(key, None)

        # Try Redis if available
        if self.redis:
            try:
                await self.redis.delete(key)
            except Exception as e:
                logger.error(f"Redis delete error for {key}: {str(e)}")
                success = False

        return success

    async def incr(self, key: str) -> int:
        """Increment counter."""
        # Use local cache for counter if Redis is not available
        if not self.redis:
            value = self._local_cache.get(key, (0, datetime.max))[0]
            value += 1
            self._local_cache[key] = (value, datetime.max)
            return value

        try:
            return await self.redis.incr(key)
        except Exception as e:
            logger.error(f"Redis incr error for {key}: {str(e)}")
            # Fallback to local cache
            value = self._local_cache.get(key, (0, datetime.max))[0]
            value += 1
            self._local_cache[key] = (value, datetime.max)
            return value

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key."""
        success = True

        # Set expiration in local cache
        if key in self._local_cache:
            value = self._local_cache[key][0]
            self._local_cache[key] = (value, datetime.now() + timedelta(seconds=seconds))

        # Try Redis if available
        if self.redis:
            try:
                success = await self.redis.expire(key, seconds)
            except Exception as e:
                logger.error(f"Redis expire error for {key}: {str(e)}")
                success = False

        return success

# Global cache instance
cache = RedisCache()

def cache_decorator(expire_in: Optional[int] = None, prefix: str = ""):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            arg_str = ':'.join(str(a) for a in args[1:])  # Skip self
            kwarg_str = ':'.join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            cache_key = f"{prefix}:{func.__name__}:{arg_str}:{kwarg_str}"

            # Try to get from cache
            result = await cache.get(cache_key)
            if result is not None:
                return result

            # If not in cache, execute function
            result = await func(*args, **kwargs)

            # Cache the result if it's not None
            if result is not None:
                await cache.set(cache_key, result, expire_in)

            return result

        return wrapper
    return decorator

# Export cache instance and decorator
__all__ = ['cache', 'cache_decorator']
