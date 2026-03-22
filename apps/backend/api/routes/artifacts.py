from __future__ import annotations

import uuid
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.backend.core.database import get_db
from apps.backend.models.artifact import Artifact
from apps.backend.schemas.artifact import ArtifactCreate, ArtifactRead

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/artifacts", tags=["artifacts"])


@router.get("", response_model=list[ArtifactRead])
async def list_artifacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    artifact_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Artifact).order_by(Artifact.created_at.desc()).offset(skip).limit(limit)
    )
    if artifact_type:
        stmt = stmt.where(Artifact.artifact_type == artifact_type)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=ArtifactRead, status_code=201)
async def create_artifact(payload: ArtifactCreate, db: AsyncSession = Depends(get_db)):
    artifact = Artifact(
        artifact_type=payload.artifact_type,
        title=payload.title,
        content=payload.content,
        storage_url=payload.storage_url,
        job_id=payload.job_id,
    )
    db.add(artifact)
    await db.flush()
    await db.refresh(artifact)
    logger.info(
        "artifact_created", artifact_id=str(artifact.id), type=artifact.artifact_type
    )
    return artifact


@router.get("/{artifact_id}", response_model=ArtifactRead)
async def get_artifact(artifact_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    artifact = await db.get(Artifact, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact


@router.delete("/{artifact_id}", status_code=204)
async def delete_artifact(artifact_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    artifact = await db.get(Artifact, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    await db.delete(artifact)
    logger.info("artifact_deleted", artifact_id=str(artifact_id))
