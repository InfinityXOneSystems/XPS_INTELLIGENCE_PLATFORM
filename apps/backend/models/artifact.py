from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from apps.backend.core.database import Base


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    artifact_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    content: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    storage_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    job_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
