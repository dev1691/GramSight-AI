import os
import json
from typing import Any, Optional
import redis
import redis.asyncio as aioredis

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

_redis_sync: Optional[redis.Redis] = None
_redis_async: Optional[aioredis.Redis] = None


def _get_sync() -> redis.Redis:
    global _redis_sync
    if _redis_sync is None:
        _redis_sync = redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_sync


async def _get_async() -> aioredis.Redis:
    global _redis_async
    if _redis_async is None:
        _redis_async = aioredis.from_url(REDIS_URL, decode_responses=True)
    return _redis_async


def get_cached_sync(key: str) -> Optional[Any]:
    r = _get_sync()
    val = r.get(key)
    if val is None:
        return None
    try:
        return json.loads(val)
    except Exception:
        return val


def set_cached_sync(key: str, value: Any, ttl: int = 3600) -> None:
    r = _get_sync()
    r.set(key, json.dumps(value), ex=ttl)


async def get_cached(key: str) -> Optional[Any]:
    r = await _get_async()
    val = await r.get(key)
    if val is None:
        return None
    try:
        return json.loads(val)
    except Exception:
        return val


async def set_cached(key: str, value: Any, ttl: int = 3600) -> None:
    r = await _get_async()
    await r.set(key, json.dumps(value), ex=ttl)
