# Backend — XPS Intelligence Platform

> **Status:** ⬜ Pending Phase 1 consolidation  
> **Source:** `XPS_INTELLIGENCE_SYSTEM`  
> **Runtime:** FastAPI (Python 3.12) → Railway

## Overview

The backend service provides the core intelligence API, agent orchestration, Shadow Scraper integration, and memory system.

## Directory Structure (Target)

```
apps/backend/
├── src/
│   ├── api/          ← Route handlers (FastAPI routers)
│   ├── core/         ← Config, database, security, logging
│   ├── models/       ← SQLAlchemy ORM models
│   ├── schemas/      ← Pydantic request/response schemas
│   └── services/     ← Business logic services
├── tests/
│   └── test_*.py
├── alembic/          ← Database migrations
├── Dockerfile
├── pyproject.toml
└── railway.json
```

## Phase 1 Consolidation Checklist

- [ ] Pull and refactor source from `XPS_INTELLIGENCE_SYSTEM`
- [ ] Create `pyproject.toml` with all dependencies
- [ ] Set up FastAPI application with health endpoint
- [ ] Configure SQLAlchemy + Alembic for Postgres
- [ ] Configure Redis client
- [ ] Implement JWT authentication
- [ ] Add rate limiting middleware
- [ ] Add structured JSON logging
- [ ] Create Railway deployment config
- [ ] Write pytest unit tests (100% coverage gate)
- [ ] Document all API endpoints in OpenAPI

## Environment Variables Required

See root `.env.example` for the complete list.

Key variables:
- `DATABASE_URL` — Railway Postgres connection string
- `REDIS_URL` — Railway Redis connection string
- `SECRET_KEY` — JWT signing secret
- `ENVIRONMENT` — `development` | `staging` | `production`

## Human Gate

This directory will be populated during **Phase 1** after explicit human command to begin consolidation.
