from __future__ import annotations

import asyncio
import os
import re
import uuid
from typing import Any

import httpx
import structlog
from bs4 import BeautifulSoup
from celery import Celery
from tenacity import retry, stop_after_attempt, wait_exponential

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/xps_intelligence",
)

logger = structlog.get_logger(__name__)

celery_app = Celery(
    "xps_worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


def _run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@celery_app.task(bind=True, max_retries=3, name="xps.run_scrape_job")
def run_scrape_job(self, job_id: str, url: str) -> dict[str, Any]:
    logger.info("task_run_scrape_job_start", job_id=job_id, url=url)
    try:
        result = _run_async(_async_scrape(job_id, url))
        logger.info("task_run_scrape_job_done", job_id=job_id, leads=result.get("leads_created"))
        return result
    except Exception as exc:
        logger.error("task_run_scrape_job_failed", job_id=job_id, error=str(exc))
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)


@celery_app.task(name="xps.run_ingest_pipeline")
def run_ingest_pipeline(job_id: str) -> dict[str, Any]:
    logger.info("task_run_ingest_pipeline", job_id=job_id)
    return {"job_id": job_id, "status": "ingested"}


@celery_app.task(name="xps.run_normalize_batch")
def run_normalize_batch(lead_ids: list[str]) -> dict[str, Any]:
    logger.info("task_run_normalize_batch", count=len(lead_ids))
    results = _run_async(_async_normalize_batch(lead_ids))
    return results


@celery_app.task(name="xps.run_score_batch")
def run_score_batch(lead_ids: list[str]) -> dict[str, Any]:
    logger.info("task_run_score_batch", count=len(lead_ids))
    results = _run_async(_async_score_batch(lead_ids))
    return results


async def _async_scrape(job_id: str, url: str) -> dict[str, Any]:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
    from sqlalchemy import select

    engine = create_async_engine(DATABASE_URL, echo=False)
    SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

    leads_created = 0
    async with SessionLocal() as db:
        try:
            from apps.backend.models.scrape_job import ScrapeJob
            from apps.backend.models.lead import Lead

            job = await db.get(ScrapeJob, uuid.UUID(job_id))
            if not job:
                return {"error": "job not found", "leads_created": 0}

            job.status = "running"
            await db.flush()

            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                html = resp.text

            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator=" ")
            emails = list(set(EMAIL_RE.findall(text)))

            for idx, email in enumerate(emails):
                idem_key = f"scrape:{job_id}:{url}:{idx}"
                existing = await db.execute(select(Lead).where(Lead.idempotency_key == idem_key))
                if existing.scalar_one_or_none():
                    continue
                lead = Lead(source_url=url, raw_data={"email": email}, idempotency_key=idem_key, status="raw")
                db.add(lead)
                leads_created += 1

            job.status = "done"
            job.result_count = leads_created
            await db.commit()
        except Exception as exc:
            job = await db.get(ScrapeJob, uuid.UUID(job_id))
            if job:
                job.status = "failed"
                job.error = str(exc)[:2048]
                await db.commit()
            raise
        finally:
            await engine.dispose()

    return {"job_id": job_id, "leads_created": leads_created}


async def _async_normalize_batch(lead_ids: list[str]) -> dict[str, Any]:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    engine = create_async_engine(DATABASE_URL, echo=False)
    SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

    normalized = 0
    errors = 0
    async with SessionLocal() as db:
        from apps.backend.pipeline.normalize import normalize_lead

        for lead_id_str in lead_ids:
            try:
                await normalize_lead(db, uuid.UUID(lead_id_str))
                normalized += 1
            except Exception as exc:
                logger.warning("normalize_failed", lead_id=lead_id_str, error=str(exc))
                errors += 1
        await db.commit()
    await engine.dispose()
    return {"normalized": normalized, "errors": errors}


async def _async_score_batch(lead_ids: list[str]) -> dict[str, Any]:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    engine = create_async_engine(DATABASE_URL, echo=False)
    SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

    scored = 0
    errors = 0
    async with SessionLocal() as db:
        from apps.backend.pipeline.score import score_lead

        for lead_id_str in lead_ids:
            try:
                await score_lead(db, uuid.UUID(lead_id_str))
                scored += 1
            except Exception as exc:
                logger.warning("score_failed", lead_id=lead_id_str, error=str(exc))
                errors += 1
        await db.commit()
    await engine.dispose()
    return {"scored": scored, "errors": errors}


def main():
    celery_app.worker_main(["-A", "apps.workers.default.worker", "worker", "--loglevel=info"])


if __name__ == "__main__":
    main()
