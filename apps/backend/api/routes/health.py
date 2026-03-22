from __future__ import annotations

import structlog
from fastapi import APIRouter
from sqlalchemy import text

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """Health check endpoint used by Railway and load balancers.

    Always returns HTTP 200 so Railway considers the service alive as long
    as the process is running.  The ``checks`` dict exposes DB / Redis
    connectivity so operators can detect degraded-but-alive states without
    triggering a container restart.
    """
    from apps.backend.core.database import engine
    from apps.backend.core.redis_client import get_redis

    db_status = "unavailable"
    redis_status = "unavailable"

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as exc:
        logger.warning("health_db_check_failed", error=str(exc))

    try:
        redis = await get_redis()
        if redis is not None:
            await redis.ping()
            redis_status = "ok"
    except Exception as exc:
        logger.warning("health_redis_check_failed", error=str(exc))

    overall = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"

    return {
        "status": overall,
        "service": "xps-backend",
        "version": "1.0.0",
        "checks": {
            "database": db_status,
            "redis": redis_status,
        },
    }
