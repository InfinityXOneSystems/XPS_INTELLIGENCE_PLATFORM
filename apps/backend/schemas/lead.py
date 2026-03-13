from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class LeadCreate(BaseModel):
    source_url: str = Field(..., max_length=2048)
    raw_data: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = Field(..., max_length=255)


class LeadRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_url: str
    raw_data: dict[str, Any]
    normalized_data: Optional[dict[str, Any]]
    score: Optional[float]
    status: str
    idempotency_key: str
    created_at: datetime
    updated_at: datetime


class LeadNormalized(LeadRead):
    normalized_data: dict[str, Any]


class LeadScored(LeadNormalized):
    score: float
