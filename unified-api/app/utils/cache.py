"""Caching utilities using Redis."""
import json
import redis.asyncio as redis
from typing import Optional, Any
from datetime import timedelta

from ..config import get_settings

settings = get_settings()

# Redis client
redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Get or create Redis client."""
    global redis_client
    
    if not redis_client:
        redis_client = redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
    
    return redis_client


async def cache_result(key: str, value: Any, ttl: int = None) -> None:
    """Cache a result in Redis."""
    if not settings.redis_url:
        return
    
    try:
        client = await get_redis_client()
        ttl = ttl or settings.cache_ttl
        
        # Serialize value to JSON
        json_value = json.dumps(value, default=str)
        
        await client.setex(key, ttl, json_value)
    except Exception as e:
        # Log error but don't fail the request
        print(f"Cache error: {e}")


async def get_cached_result(key: str) -> Optional[Any]:
    """Get a cached result from Redis."""
    if not settings.redis_url:
        return None
    
    try:
        client = await get_redis_client()
        value = await client.get(key)
        
        if value:
            return json.loads(value)
    except Exception as e:
        # Log error but don't fail the request
        print(f"Cache error: {e}")
    
    return None


async def invalidate_cache(pattern: str) -> int:
    """Invalidate cache entries matching a pattern."""
    if not settings.redis_url:
        return 0
    
    try:
        client = await get_redis_client()
        
        # Find all keys matching pattern
        keys = []
        async for key in client.scan_iter(match=pattern):
            keys.append(key)
        
        # Delete keys
        if keys:
            deleted = await client.delete(*keys)
            return deleted
    except Exception as e:
        print(f"Cache invalidation error: {e}")
    
    return 0


async def close_redis():
    """Close Redis connection."""
    global redis_client
    
    if redis_client:
        await redis_client.close()
        redis_client = None