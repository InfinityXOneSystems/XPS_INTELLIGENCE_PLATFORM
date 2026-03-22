from __future__ import annotations

import json
import uuid
from typing import Any

import structlog
from fastapi import APIRouter, BackgroundTasks, HTTPException
from sqlalchemy import select

from apps.backend.core.config import settings
from apps.backend.core.redis_client import get_redis

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/autonomy", tags=["autonomy"])

_CYCLE_KEY_PREFIX = "xps:autonomy:cycle:"
_CYCLE_TTL_SECONDS = 86400  # keep cycle state for 24 hours


async def _get_cycle(cycle_id: str) -> dict[str, Any] | None:
    """Retrieve cycle state from Redis."""
    try:
        redis = await get_redis()
        val = await redis.get(f"{_CYCLE_KEY_PREFIX}{cycle_id}")
        return json.loads(val) if val is not None else None
    except Exception:
        return None


async def _set_cycle(cycle_id: str, state: dict[str, Any]) -> None:
    """Persist cycle state to Redis."""
    try:
        redis = await get_redis()
        await redis.set(
            f"{_CYCLE_KEY_PREFIX}{cycle_id}",
            json.dumps(state),
            ex=_CYCLE_TTL_SECONDS,
        )
    except Exception as exc:
        logger.warning("redis_cycle_persist_failed", cycle_id=cycle_id, error=str(exc))


@router.get("/status")
async def autonomy_status():
    return {
        "autonomy_enabled": settings.AUTONOMY_ENABLED,
        "scraper_autorun_enabled": settings.SCRAPER_AUTORUN_ENABLED,
    }


@router.post("/cycle")
async def trigger_cycle(background_tasks: BackgroundTasks):
    if not settings.AUTONOMY_ENABLED:
        return {"status": "disabled", "reason": "AUTONOMY_ENABLED is false"}

    cycle_id = str(uuid.uuid4())
    initial_state: dict[str, Any] = {
        "status": "started",
        "cycle_id": cycle_id,
        "steps": [],
    }
    await _set_cycle(cycle_id, initial_state)
    background_tasks.add_task(_run_autonomy_cycle, cycle_id=cycle_id)
    logger.info("autonomy_cycle_started", cycle_id=cycle_id)
    return {"status": "started", "cycle_id": cycle_id}


@router.get("/cycle/{cycle_id}/status")
async def cycle_status(cycle_id: str):
    state = await _get_cycle(cycle_id)
    if state is None:
        raise HTTPException(status_code=404, detail="Cycle not found")
    return state


async def _run_autonomy_cycle(cycle_id: str) -> None:
    from apps.backend.core.database import AsyncSessionLocal
    from apps.backend.models.lead import Lead
    from apps.backend.models.scrape_job import ScrapeJob
    from apps.backend.pipeline.normalize import normalize_lead
    from apps.backend.pipeline.score import score_lead

    state: dict[str, Any] = {"status": "running", "cycle_id": cycle_id, "steps": []}
    await _set_cycle(cycle_id, state)

    async with AsyncSessionLocal() as db:
        try:
            # Step 1: find pending scrape jobs and execute them
            state["steps"].append("scrape")
            pending_jobs_result = await db.execute(
                select(ScrapeJob).where(ScrapeJob.status == "pending").limit(10)
            )
            pending_jobs = pending_jobs_result.scalars().all()
            for job in pending_jobs:
                from apps.backend.api.routes.scraper import _execute_scrape_job

                await _execute_scrape_job(str(job.id), job.target_url)

            # Step 2: normalize raw leads
            state["steps"].append("normalize")
            raw_leads_result = await db.execute(
                select(Lead).where(Lead.status == "raw").limit(100)
            )
            raw_leads = raw_leads_result.scalars().all()
            for lead in raw_leads:
                try:
                    await normalize_lead(db, lead.id)
                except Exception as exc:
                    logger.warning(
                        "normalize_failed", lead_id=str(lead.id), error=str(exc)
                    )

            # Step 3: score normalized leads
            state["steps"].append("score")
            norm_leads_result = await db.execute(
                select(Lead).where(Lead.status == "normalized").limit(100)
            )
            norm_leads = norm_leads_result.scalars().all()
            for lead in norm_leads:
                try:
                    await score_lead(db, lead.id)
                except Exception as exc:
                    logger.warning("score_failed", lead_id=str(lead.id), error=str(exc))

            await db.commit()
            state["status"] = "done"
            await _set_cycle(cycle_id, state)
            logger.info("autonomy_cycle_done", cycle_id=cycle_id)

        except Exception as exc:
            state["status"] = "failed"
            state["error"] = str(exc)
            await _set_cycle(cycle_id, state)
            logger.error("autonomy_cycle_failed", cycle_id=cycle_id, error=str(exc))
