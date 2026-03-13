from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

ScrapeJobStatusStr = Literal["pending", "running", "done", "failed"]


class ScrapeJobCreate(BaseModel):
    target_url: str = Field(..., max_length=2048)
    idempotency_key: Optional[str] = Field(None, max_length=255)
    scheduled: bool = False


class ScrapeJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    target_url: str
    status: str
    idempotency_key: str
    result_count: int
    error: Optional[str]
    scheduled: bool
    created_at: datetime
    updated_at: datetime


class ScrapeJobStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    result_count: int
    error: Optional[str]
