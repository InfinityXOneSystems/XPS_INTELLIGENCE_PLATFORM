from __future__ import annotations

import re
import uuid
from typing import Any

import httpx
import structlog
from bs4 import BeautifulSoup
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.backend.core.config import settings
from apps.backend.core.database import get_db
from apps.backend.models.lead import Lead
from apps.backend.models.scrape_job import ScrapeJob
from apps.backend.schemas.scrape_job import ScrapeJobCreate, ScrapeJobRead, ScrapeJobStatus

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/scraper", tags=["scraper"])

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")

_scraper_settings: dict[str, Any] = {
    "autorun_enabled": settings.SCRAPER_AUTORUN_ENABLED,
}


# ── Settings ──────────────────────────────────────────────────────────────────

@router.get("/settings", tags=["scraper"])
async def get_scraper_settings():
    return {"autorun_enabled": _scraper_settings["autorun_enabled"]}


@router.patch("/settings", tags=["scraper"])
async def update_scraper_settings(payload: dict):
    if "autorun_enabled" in payload:
        value = payload["autorun_enabled"]
        if not isinstance(value, bool):
            raise HTTPException(status_code=422, detail="autorun_enabled must be a boolean")
        _scraper_settings["autorun_enabled"] = value
        logger.info("scraper_settings_updated", autorun_enabled=value)
    return {"autorun_enabled": _scraper_settings["autorun_enabled"]}


# ── Jobs ──────────────────────────────────────────────────────────────────────

@router.get("/jobs", response_model=list[ScrapeJobRead])
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ScrapeJob).order_by(ScrapeJob.created_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.post("/jobs", response_model=ScrapeJobRead, status_code=201)
async def create_job(payload: ScrapeJobCreate, db: AsyncSession = Depends(get_db)):
    if not payload.target_url.startswith(("http://", "https://")):
        raise HTTPException(status_code=422, detail="target_url must be a valid HTTP/HTTPS URL")

    idem_key = payload.idempotency_key or f"scrape_job:{payload.target_url}"
    existing = await db.execute(
        select(ScrapeJob).where(ScrapeJob.idempotency_key == idem_key)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Scrape job with this idempotency_key already exists")

    job = ScrapeJob(
        target_url=payload.target_url,
        idempotency_key=idem_key,
        scheduled=payload.scheduled,
        status="pending",
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    logger.info("scrape_job_created", job_id=str(job.id), url=job.target_url)
    return job


@router.get("/jobs/{job_id}", response_model=ScrapeJobRead)
async def get_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    job = await db.get(ScrapeJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Scrape job not found")
    return job


@router.post("/jobs/{job_id}/run", response_model=ScrapeJobStatus)
async def run_job(
    job_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    job = await db.get(ScrapeJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Scrape job not found")
    if job.status == "running":
        raise HTTPException(status_code=409, detail="Job is already running")

    job.status = "running"
    await db.flush()
    await db.refresh(job)

    background_tasks.add_task(_execute_scrape_job, job_id=str(job.id), url=job.target_url)
    logger.info("scrape_job_triggered", job_id=str(job.id))
    return job


# ── Background execution ──────────────────────────────────────────────────────

async def _execute_scrape_job(job_id: str, url: str) -> None:
    from apps.backend.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            job = await db.get(ScrapeJob, uuid.UUID(job_id))
            if not job:
                return

            leads_found: list[dict] = []
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                html = response.text

            soup = BeautifulSoup(html, "html.parser")
            text_content = soup.get_text(separator=" ")

            emails = list(set(EMAIL_RE.findall(text_content)))
            for idx, email in enumerate(emails):
                leads_found.append({"email": email, "source": "email_extraction"})

            # Also capture contact form fields as lead candidates
            forms = soup.find_all("form")
            for form_idx, form in enumerate(forms):
                inputs = form.find_all("input")
                form_data: dict[str, str] = {}
                for inp in inputs:
                    name = inp.get("name", "")
                    if name:
                        form_data[name] = inp.get("placeholder", inp.get("value", ""))
                if form_data:
                    leads_found.append({"form_fields": form_data, "source": "contact_form"})

            # Persist lead records with idempotency
            created_count = 0
            for idx, lead_data in enumerate(leads_found):
                idem_key = f"scrape:{job_id}:{url}:{idx}"
                existing = await db.execute(
                    select(Lead).where(Lead.idempotency_key == idem_key)
                )
                if existing.scalar_one_or_none():
                    continue
                lead = Lead(
                    source_url=url,
                    raw_data=lead_data,
                    idempotency_key=idem_key,
                    status="raw",
                )
                db.add(lead)
                created_count += 1

            job.status = "done"
            job.result_count = created_count
            await db.commit()
            logger.info("scrape_job_done", job_id=job_id, leads=created_count)

        except Exception as exc:
            logger.error("scrape_job_failed", job_id=job_id, error=str(exc))
            try:
                job = await db.get(ScrapeJob, uuid.UUID(job_id))
                if job:
                    job.status = "failed"
                    job.error = str(exc)[:2048]
                    await db.commit()
            except Exception:
                pass
