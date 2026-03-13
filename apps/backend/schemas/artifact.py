from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

ArtifactTypeStr = Literal[
    "image",
    "video",
    "music",
    "template",
    "chart",
    "lead",
    "web_browse",
    "system",
    "text",
]


class ArtifactCreate(BaseModel):
    artifact_type: ArtifactTypeStr
    title: str = Field(..., max_length=512)
    content: dict[str, Any] = Field(default_factory=dict)
    storage_url: Optional[str] = Field(None, max_length=2048)
    job_id: Optional[str] = Field(None, max_length=255)


class ArtifactRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    artifact_type: str
    title: str
    content: dict[str, Any]
    storage_url: Optional[str]
    job_id: Optional[str]
    created_at: datetime
