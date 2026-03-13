from __future__ import annotations

import structlog
import redis.asyncio as aioredis

from apps.backend.core.config import settings

logger = structlog.get_logger(__name__)

_redis_client: aioredis.Redis | None = None


async def connect_redis() -> None:
    global _redis_client
    try:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
        await _redis_client.ping()
        logger.info("redis_connected", url=settings.REDIS_URL)
    except Exception as exc:
        logger.warning("redis_connect_failed", error=str(exc))
        _redis_client = None


async def disconnect_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
    logger.info("redis_disconnected")


async def get_redis() -> aioredis.Redis | None:
    return _redis_client
