from __future__ import annotations

import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

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
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_lead(client: AsyncClient):
    payload = {
        "source_url": "https://example.com",
        "raw_data": {"email": "alice@example.com", "name": "Alice"},
        "idempotency_key": "test:lead:001",
    }
    resp = await client.post("/api/v1/leads", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "raw"
    assert data["source_url"] == "https://example.com"
    assert data["idempotency_key"] == "test:lead:001"


@pytest.mark.asyncio
async def test_create_lead_idempotency(client: AsyncClient):
    payload = {
        "source_url": "https://example.com",
        "raw_data": {},
        "idempotency_key": "test:lead:idempotent",
    }
    resp1 = await client.post("/api/v1/leads", json=payload)
    assert resp1.status_code == 201
    resp2 = await client.post("/api/v1/leads", json=payload)
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_list_leads(client: AsyncClient):
    resp = await client.get("/api/v1/leads")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_get_lead_not_found(client: AsyncClient):
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/api/v1/leads/{fake_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_normalize_lead(client: AsyncClient, db_session: AsyncSession):
    from apps.backend.pipeline.ingest import ingest_raw_lead

    lead = await ingest_raw_lead(
        db=db_session,
        raw_data={"email": "bob@example.com", "name": "Bob", "company": "Acme"},
        source_url="https://example.com",
        idempotency_key="test:lead:normalize:001",
    )
    await db_session.commit()

    resp = await client.patch(f"/api/v1/leads/{lead.id}/normalize")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "normalized"
    assert data["normalized_data"]["email"] == "bob@example.com"
    assert data["normalized_data"]["company"] == "Acme"


@pytest.mark.asyncio
async def test_score_lead(client: AsyncClient, db_session: AsyncSession):
    from apps.backend.pipeline.ingest import ingest_raw_lead
    from apps.backend.pipeline.normalize import normalize_lead

    lead = await ingest_raw_lead(
        db=db_session,
        raw_data={"email": "carol@example.com", "name": "Carol", "phone": "555-555-5555"},
        source_url="https://example.com",
        idempotency_key="test:lead:score:001",
    )
    await db_session.flush()
    await normalize_lead(db_session, lead.id)
    await db_session.commit()

    resp = await client.patch(f"/api/v1/leads/{lead.id}/score")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "scored"
    assert data["score"] is not None
    assert 0.0 <= data["score"] <= 1.0


@pytest.mark.asyncio
async def test_full_pipeline(db_session: AsyncSession):
    from apps.backend.pipeline.ingest import ingest_raw_lead
    from apps.backend.pipeline.normalize import normalize_lead
    from apps.backend.pipeline.score import score_lead

    lead = await ingest_raw_lead(
        db=db_session,
        raw_data={
            "email": "dave@example.com",
            "name": "Dave",
            "phone": "+15555555555",
            "company": "TechCo",
            "website": "https://techco.example.com",
        },
        source_url="https://example.com",
        idempotency_key="test:pipeline:full:001",
    )
    assert lead.status == "raw"

    lead = await normalize_lead(db_session, lead.id)
    assert lead.status == "normalized"
    assert lead.normalized_data["email"] == "dave@example.com"

    lead = await score_lead(db_session, lead.id)
    assert lead.status == "scored"
    # All 5 fields present → score == 1.0
    assert lead.score == 1.0
