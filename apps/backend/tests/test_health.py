import pytest
from httpx import ASGITransport, AsyncClient

from apps.backend.main import app


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    # status is "ok" when DB+Redis are available, "degraded" otherwise.
    # The endpoint always returns HTTP 200 so Railway/load-balancers keep
    # the service alive even during transient connectivity issues.
    assert data["status"] in ("ok", "degraded")
    assert data["service"] == "xps-backend"
    assert data["version"] == "1.0.0"
    assert "checks" in data
    assert "database" in data["checks"]
    assert "redis" in data["checks"]


@pytest.mark.asyncio
async def test_api_health():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        resp = await ac.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("ok", "degraded")
    assert "checks" in data
