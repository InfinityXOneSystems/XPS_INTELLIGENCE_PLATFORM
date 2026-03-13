from __future__ import annotations

import uuid
from typing import Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.backend.models.lead import Lead

logger = structlog.get_logger(__name__)


async def ingest_raw_lead(
    db: AsyncSession,
    raw_data: dict[str, Any],
    source_url: str,
    idempotency_key: str,
) -> Lead:
    existing_result = await db.execute(
        select(Lead).where(Lead.idempotency_key == idempotency_key)
    )
    existing = existing_result.scalar_one_or_none()
    if existing:
        logger.info("ingest_idempotent_hit", idempotency_key=idempotency_key)
        return existing

    lead = Lead(
        source_url=source_url,
        raw_data=raw_data,
        idempotency_key=idempotency_key,
        status="raw",
    )
    db.add(lead)
    await db.flush()
    await db.refresh(lead)
    logger.info("lead_ingested", lead_id=str(lead.id), source_url=source_url)
    return lead
