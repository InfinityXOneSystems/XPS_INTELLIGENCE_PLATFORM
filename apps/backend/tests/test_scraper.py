from __future__ import annotations

from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from apps.backend.core.database import Base, get_db
from apps.backend.main import app

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_scrape_job(client: AsyncClient):
    payload = {
        "target_url": "https://example.com",
        "idempotency_key": "test:job:001",
    }
    resp = await client.post("/api/v1/scraper/jobs", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "pending"
    assert data["target_url"] == "https://example.com"
    assert data["idempotency_key"] == "test:job:001"


@pytest.mark.asyncio
async def test_create_scrape_job_idempotency(client: AsyncClient):
    payload = {
        "target_url": "https://example.com",
        "idempotency_key": "test:job:idempotent",
    }
    resp1 = await client.post("/api/v1/scraper/jobs", json=payload)
    assert resp1.status_code == 201
    resp2 = await client.post("/api/v1/scraper/jobs", json=payload)
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_create_scrape_job_invalid_url(client: AsyncClient):
    payload = {
        "target_url": "not-a-url",
        "idempotency_key": "test:job:bad-url",
    }
    resp = await client.post("/api/v1/scraper/jobs", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_scrape_jobs(client: AsyncClient):
    resp = await client.get("/api/v1/scraper/jobs")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_get_scrape_job_not_found(client: AsyncClient):
    import uuid

    resp = await client.get(f"/api/v1/scraper/jobs/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_run_scrape_job_mocked(client: AsyncClient):
    """Test job execution with mocked httpx to avoid real network calls."""
    payload = {
        "target_url": "https://example.com",
        "idempotency_key": "test:job:run:001",
    }
    create_resp = await client.post("/api/v1/scraper/jobs", json=payload)
    assert create_resp.status_code == 201
    job_id = create_resp.json()["id"]

    mock_html = """<html><body>
        <p>Contact: test@example.com</p>
        <p>Another: sales@example.org</p>
    </body></html>"""

    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.text = mock_html
    mock_response.raise_for_status = lambda: None

    with patch("apps.backend.api.routes.scraper.httpx.AsyncClient") as mock_client_cls:
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client_cls.return_value = mock_client_instance

        resp = await client.post(f"/api/v1/scraper/jobs/{job_id}/run")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] in ("running", "done", "pending")


@pytest.mark.asyncio
async def test_scraper_settings(client: AsyncClient):
    resp = await client.get("/api/v1/scraper/settings")
    assert resp.status_code == 200
    assert "autorun_enabled" in resp.json()


@pytest.mark.asyncio
async def test_update_scraper_settings(client: AsyncClient):
    resp = await client.patch(
        "/api/v1/scraper/settings", json={"autorun_enabled": True}
    )
    assert resp.status_code == 200
    assert resp.json()["autorun_enabled"] is True

    resp2 = await client.patch(
        "/api/v1/scraper/settings", json={"autorun_enabled": False}
    )
    assert resp2.status_code == 200
    assert resp2.json()["autorun_enabled"] is False
