from __future__ import annotations

from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)

DEFAULT_CAPS: dict[str, bool] = {
    "network_restricted": True,
    "filesystem_read": False,
    "filesystem_write": False,
    "db_read": False,
    "db_write": False,
}

ALLOWED_SCHEMES = {"http", "https"}


def validate_capabilities(required_caps: set[str], granted_caps: set[str]) -> bool:
    return required_caps.issubset(granted_caps)


class SandboxExecutor:
    def __init__(self, capabilities: dict[str, bool] | None = None):
        self.capabilities: dict[str, bool] = {**DEFAULT_CAPS, **(capabilities or {})}

    def _is_cap_granted(self, cap: str) -> bool:
        return bool(self.capabilities.get(cap, False))

    async def execute_scrape(self, url: str, capabilities: dict[str, bool] | None = None) -> dict[str, Any]:
        effective_caps = {**self.capabilities, **(capabilities or {})}
        granted = {k for k, v in effective_caps.items() if v}

        required = {"network_restricted"}
        if not validate_capabilities(required, granted):
            logger.warning("sandbox_capability_denied", url=url, required=sorted(required))
            return {"allowed": False, "error": "Required capabilities not granted", "result": None}

        # Disallow filesystem access
        if effective_caps.get("filesystem_write"):
            return {"allowed": False, "error": "filesystem_write is not permitted in sandbox", "result": None}

        scheme = url.split("://")[0].lower() if "://" in url else ""
        if scheme not in ALLOWED_SCHEMES:
            return {"allowed": False, "error": f"URL scheme '{scheme}' not allowed", "result": None}

        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                return {
                    "allowed": True,
                    "error": None,
                    "result": {
                        "status_code": response.status_code,
                        "content_type": response.headers.get("content-type", ""),
                        "body_length": len(response.content),
                        "text_preview": response.text[:500],
                    },
                }
        except Exception as exc:
            logger.error("sandbox_scrape_error", url=url, error=str(exc))
            return {"allowed": True, "error": str(exc), "result": None}
