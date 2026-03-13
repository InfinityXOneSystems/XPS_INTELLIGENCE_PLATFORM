from __future__ import annotations

import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from apps.backend.models.lead import Lead

logger = structlog.get_logger(__name__)

FIELD_WEIGHTS = {
    "email": 0.30,
    "phone": 0.20,
    "company": 0.20,
    "name": 0.15,
    "website": 0.15,
}


async def score_lead(db: AsyncSession, lead_id: uuid.UUID) -> Lead:
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise ValueError(f"Lead {lead_id} not found")

    if not lead.normalized_data:
        raise ValueError(f"Lead {lead_id} has no normalized_data; run normalize first")

    norm = lead.normalized_data
    score = sum(
        weight
        for field, weight in FIELD_WEIGHTS.items()
        if norm.get(field)
    )
    score = round(min(max(score, 0.0), 1.0), 4)

    lead.score = score
    lead.status = "scored"
    await db.flush()
    await db.refresh(lead)
    logger.info("lead_scored", lead_id=str(lead_id), score=score)
    return lead
