import logging

from redis.asyncio import Redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_redis: Redis | None = None


async def get_redis() -> Redis | None:
    global _redis
    if _redis is not None:
        return _redis

    settings = get_settings()
    client = Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )
    try:
        await client.ping()
    except Exception:
        logger.warning("Redis indisponível em %s", settings.redis_url)
        await client.aclose()
        return None

    _redis = client
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is None:
        return
    await _redis.aclose()
    _redis = None
