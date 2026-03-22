from __future__ import annotations

import uuid
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.backend.core.database import get_db
from apps.backend.models.lead import Lead
from apps.backend.pipeline.normalize import normalize_lead
from apps.backend.pipeline.score import score_lead
from apps.backend.schemas.lead import LeadCreate, LeadRead

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/leads", tags=["leads"])


@router.get("", response_model=list[LeadRead])
async def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Lead).order_by(Lead.created_at.desc()).offset(skip).limit(limit)
    if status:
        stmt = stmt.where(Lead.status == status)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=LeadRead, status_code=201)
async def create_lead(payload: LeadCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(Lead).where(Lead.idempotency_key == payload.idempotency_key)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail="Lead with this idempotency_key already exists"
        )

    lead = Lead(
        source_url=payload.source_url,
        raw_data=payload.raw_data,
        idempotency_key=payload.idempotency_key,
        status="raw",
    )
    db.add(lead)
    await db.flush()
    await db.refresh(lead)
    logger.info("lead_created", lead_id=str(lead.id))
    return lead


@router.get("/{lead_id}", response_model=LeadRead)
async def get_lead(lead_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}/normalize", response_model=LeadRead)
async def normalize_lead_route(lead_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    updated = await normalize_lead(db, lead_id)
    return updated


@router.patch("/{lead_id}/score", response_model=LeadRead)
async def score_lead_route(lead_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if lead.status not in ("normalized", "scored"):
        raise HTTPException(
            status_code=400,
            detail="Lead must be normalized before scoring. Call /normalize first.",
        )
    updated = await score_lead(db, lead_id)
    return updated
