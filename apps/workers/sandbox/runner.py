from __future__ import annotations

import asyncio
from typing import Any

import httpx
import structlog

logger = structlog.get_logger(__name__)

CAPABILITY_REGISTRY = {
    "network_restricted": "Access only allowlisted/public HTTP/HTTPS URLs",
    "network_external": "Access arbitrary external URLs",
    "filesystem_read": "Read from filesystem",
    "filesystem_write": "Write to filesystem",
    "db_read": "Read from database",
    "db_write": "Write to database",
    "scrape_execute": "Execute web scraping",
    "transform_execute": "Execute data transformation",
    "analyze_execute": "Execute data analysis",
}

SUPPORTED_CODE_TYPES = {"scrape", "transform", "analyze"}


class SandboxRunner:
    def __init__(self, default_capabilities: set[str] | None = None):
        self.default_capabilities: set[str] = default_capabilities or {
            "network_restricted",
            "scrape_execute",
            "transform_execute",
            "analyze_execute",
        }

    def _validate_caps(self, required: set[str], granted: set[str]) -> tuple[bool, str]:
        unknown = required - set(CAPABILITY_REGISTRY)
        if unknown:
            return False, f"Unknown capabilities requested: {sorted(unknown)}"
        missing = required - granted
        if missing:
            return False, f"Missing capabilities: {sorted(missing)}"
        return True, ""

    def run_in_sandbox(
        self,
        code_type: str,
        payload: dict[str, Any],
        capabilities: set[str] | None = None,
    ) -> dict[str, Any]:
        if code_type not in SUPPORTED_CODE_TYPES:
            return {
                "result": None,
                "error": f"Unsupported code_type '{code_type}'. Supported: {sorted(SUPPORTED_CODE_TYPES)}",
                "allowed": False,
            }

        granted = capabilities if capabilities is not None else self.default_capabilities

        if code_type == "scrape":
            required = {"network_restricted", "scrape_execute"}
            allowed, reason = self._validate_caps(required, granted)
            if not allowed:
                return {"result": None, "error": reason, "allowed": False}
            return asyncio.get_event_loop().run_until_complete(self._scrape(payload, granted))

        if code_type == "transform":
            required = {"transform_execute"}
            allowed, reason = self._validate_caps(required, granted)
            if not allowed:
                return {"result": None, "error": reason, "allowed": False}
            return self._transform(payload)

        if code_type == "analyze":
            required = {"analyze_execute"}
            allowed, reason = self._validate_caps(required, granted)
            if not allowed:
                return {"result": None, "error": reason, "allowed": False}
            return self._analyze(payload)

        return {"result": None, "error": "Unhandled code_type", "allowed": False}

    async def _scrape(self, payload: dict[str, Any], granted: set[str]) -> dict[str, Any]:
        url = payload.get("url", "")
        if not url.startswith(("http://", "https://")):
            return {"result": None, "error": "Invalid URL scheme", "allowed": True}

        try:
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                return {
                    "result": {
                        "status_code": resp.status_code,
                        "body_length": len(resp.content),
                        "text_preview": resp.text[:500],
                        "content_type": resp.headers.get("content-type", ""),
                    },
                    "error": None,
                    "allowed": True,
                }
        except Exception as exc:
            return {"result": None, "error": str(exc), "allowed": True}

    def _transform(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = payload.get("data")
        operation = payload.get("operation", "identity")

        if operation == "identity":
            return {"result": data, "error": None, "allowed": True}

        if operation == "flatten" and isinstance(data, dict):
            flat: dict[str, Any] = {}
            for k, v in data.items():
                if isinstance(v, dict):
                    for subk, subv in v.items():
                        flat[f"{k}.{subk}"] = subv
                else:
                    flat[k] = v
            return {"result": flat, "error": None, "allowed": True}

        if operation == "keys" and isinstance(data, dict):
            return {"result": list(data.keys()), "error": None, "allowed": True}

        return {"result": None, "error": f"Unknown transform operation: {operation}", "allowed": True}

    def _analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
        data = payload.get("data")
        if not isinstance(data, list):
            return {"result": None, "error": "data must be a list for analyze", "allowed": True}

        numeric_values = [v for v in data if isinstance(v, (int, float))]
        analysis: dict[str, Any] = {
            "count": len(data),
            "numeric_count": len(numeric_values),
        }
        if numeric_values:
            analysis["min"] = min(numeric_values)
            analysis["max"] = max(numeric_values)
            analysis["sum"] = sum(numeric_values)
            analysis["mean"] = sum(numeric_values) / len(numeric_values)

        return {"result": analysis, "error": None, "allowed": True}


if __name__ == "__main__":
    runner = SandboxRunner()
    print(runner.run_in_sandbox("analyze", {"data": [1, 2, 3, 4, 5]}))
    print(runner.run_in_sandbox("transform", {"data": {"a": 1, "b": {"c": 2}}, "operation": "flatten"}))
