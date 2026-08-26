import json
from typing import Any

from redis.asyncio import Redis

from app.core.config import get_settings

CACHE_PREFIX = "datajud:v4:proc:"
LOCK_PREFIX = "datajud:v4:lock:"
RATE_KEY = "datajud:rl:global"


def cache_key(digitos: str) -> str:
    return f"{CACHE_PREFIX}{digitos}"


def lock_key(digitos: str) -> str:
    return f"{LOCK_PREFIX}{digitos}"


async def get_cached(redis: Redis, digitos: str) -> dict[str, Any] | None:
    raw = await redis.get(cache_key(digitos))
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


async def set_cached(redis: Redis, digitos: str, payload: dict[str, Any], *, empty: bool) -> None:
    settings = get_settings()
    ttl = settings.datajud_empty_ttl_seconds if empty else settings.datajud_cache_ttl_seconds
    await redis.set(cache_key(digitos), json.dumps(payload, ensure_ascii=False), ex=ttl)


async def acquire_lock(redis: Redis, digitos: str) -> bool:
    settings = get_settings()
    acquired = await redis.set(
        lock_key(digitos),
        "1",
        nx=True,
        ex=settings.datajud_lock_ttl_seconds,
    )
    return bool(acquired)


async def release_lock(redis: Redis, digitos: str) -> None:
    await redis.delete(lock_key(digitos))


async def allow_request(redis: Redis) -> bool:
    settings = get_settings()
    current = await redis.incr(RATE_KEY)
    if current == 1:
        await redis.expire(RATE_KEY, 60)
    return current <= settings.datajud_rate_limit_per_minute
