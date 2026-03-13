from __future__ import annotations

import re
import uuid
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from apps.backend.models.lead import Lead

logger = structlog.get_logger(__name__)

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}")
URL_RE = re.compile(r"https?://[^\s\"'>]+")


def _extract_field(data: dict[str, Any], *keys: str) -> str:
    for key in keys:
        val = data.get(key)
        if val and isinstance(val, str):
            return val.strip()
    return ""


def _extract_email(data: dict[str, Any]) -> str | None:
    direct = _extract_field(data, "email", "Email", "EMAIL")
    if direct:
        m = EMAIL_RE.fullmatch(direct.strip())
        if m:
            return direct.strip().lower()
    raw_str = str(data)
    found = EMAIL_RE.search(raw_str)
    return found.group(0).lower() if found else None


def _extract_phone(data: dict[str, Any]) -> str | None:
    direct = _extract_field(data, "phone", "Phone", "PHONE", "tel", "telephone")
    if direct:
        return direct
    raw_str = str(data)
    found = PHONE_RE.search(raw_str)
    return found.group(0) if found else None


def _extract_website(data: dict[str, Any]) -> str | None:
    direct = _extract_field(data, "website", "Website", "url", "URL", "href")
    if direct:
        return direct
    raw_str = str(data)
    found = URL_RE.search(raw_str)
    return found.group(0) if found else None


async def normalize_lead(db: AsyncSession, lead_id: uuid.UUID) -> Lead:
    lead = await db.get(Lead, lead_id)
    if not lead:
        raise ValueError(f"Lead {lead_id} not found")

    raw = lead.raw_data or {}

    normalized: dict[str, Any] = {
        "name": _extract_field(raw, "name", "Name", "full_name", "fullName") or None,
        "email": _extract_email(raw),
        "phone": _extract_phone(raw),
        "company": _extract_field(raw, "company", "Company", "organization", "org") or None,
        "website": _extract_website(raw),
    }

    lead.normalized_data = normalized
    lead.status = "normalized"
    await db.flush()
    await db.refresh(lead)
    logger.info("lead_normalized", lead_id=str(lead_id))
    return lead
