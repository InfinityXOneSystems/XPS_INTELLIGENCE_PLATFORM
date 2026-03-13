# System Topology — XPS Intelligence Platform

> **Status:** Active  
> **Last Updated:** 2026-03-13  
> **Owner:** `@InfinityXOneSystems`

---

## 1. High-Level Topology

```
┌─────────────────────────────────────────────────────────────────────┐
│                      CONTROL PLANE (GitHub)                         │
│  Workflows · Branch Protection · Environments · Secrets · Labels   │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ CI/CD triggers
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                     EXECUTION PLANE (Railway)                     │
│                                                                   │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │  api service │  │ worker-default│  │ worker-playwright      │  │
│  │  (FastAPI)   │  │ (queue tasks) │  │ (browser automation)   │  │
│  └──────┬───────┘  └──────┬───────┘  └────────────────────────┘  │
│         │                 │                                        │
│  ┌──────▼─────────────────▼──────────────────────────────────┐   │
│  │                  Infrastructure Layer                      │   │
│  │  PostgreSQL (Railway) · Redis (Railway) · Supabase (opt.) │   │
│  └────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────────┐
│                  PRESENTATION PLANE (Frontend)                    │
│                                                                   │
│  apps/frontend/  (Next.js 15.5.x — Railway or Vercel)            │
│  ├── / (root → redirects to /legacy-dashboard)                   │
│  ├── /legacy-dashboard  ◄── LEGACY BRIDGE (see §4)               │
│  └── [future native routes]                                       │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │  LEGACY BRIDGE (iframe, default)                         │    │
│  │  GitHub Pages: infinityxonesystems.github.io/            │    │
│  │               XPS_INTELLIGENCE_SYSTEM/                   │    │
│  │  Source: XPS_INTELLIGENCE_SYSTEM/dashboard/ (Next.js)   │    │
│  └──────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────┘
```

---

## 2. Service Inventory

| Service | Type | Repository | Deployment | Status |
|---------|------|------------|------------|--------|
| `api` | FastAPI (Python) | `apps/backend/` | Railway | Planned |
| `worker-default` | Node.js queue consumer | `apps/workers/` | Railway | Planned |
| `worker-playwright` | Playwright automation | `apps/workers/playwright` | Railway | Planned |
| `sandbox-runner` | Isolated execution sandbox | `apps/workers/sandbox` | Railway | Planned |
| `frontend` | Next.js 15.5.x | `apps/frontend/` | Railway | Active (bridge) |
| `legacy-pages` | Static GitHub Pages | `XPS_INTELLIGENCE_SYSTEM/dashboard/` | GitHub Pages | Active (source) |
| `postgres` | PostgreSQL 16 | Railway managed | Railway | Planned |
| `redis` | Redis 7 | Railway managed | Railway | Planned |

---

## 3. Monorepo Module Map

```
XPS_INTELLIGENCE_PLATFORM/
├── apps/
│   ├── backend/              FastAPI backend + runtime controller
│   └── frontend/             Next.js frontend (additive-only UI)
│       └── src/app/
│           ├── layout.tsx    Root layout
│           ├── page.tsx      Root → redirects to /legacy-dashboard
│           └── legacy-dashboard/
│               └── page.tsx  Legacy dashboard bridge (iframe/native)
├── packages/
│   ├── agents/               Autonomous AI agents (BaseAgent interface)
│   └── shared/               Shared utilities, types, constants
├── scripts/                  Automation scripts (bash/python)
├── docs/                     Architecture, API, deployment docs
├── tests/
│   └── e2e/                  Playwright E2E tests
│       ├── foundation.spec.ts
│       └── legacy-dashboard.spec.ts  ◄── ADDED: bridge proof tests
├── FORENSIC_AUDIT/           Auto-generated evidence + audit reports
│   ├── legacy_dashboard_discovery.md
│   └── legacy_dashboard_feature_matrix.json
├── LEGACY_DASHBOARD_MIGRATION.md   ◄── ADDED: migration ledger
└── _OPS/
    ├── ARCHITECTURE/
    │   └── SYSTEM_TOPOLOGY.md   (this file)
    └── RUNBOOK/
        └── REPO_SETTINGS_BASELINE.md
```

---

## 4. Legacy Dashboard Integration

### Overview
The XPS Intelligence System (`InfinityXOneSystems/XPS_INTELLIGENCE_SYSTEM`) has a fully operational dashboard published to GitHub Pages at:

```
https://infinityxonesystems.github.io/XPS_INTELLIGENCE_SYSTEM/
```

This dashboard is built from `XPS_INTELLIGENCE_SYSTEM/dashboard/` (a Next.js 15 application) via the `.github/workflows/nextjs.yml` workflow.

### Integration Architecture

```
User → apps/frontend/legacy-dashboard → <iframe>
                                           └→ GitHub Pages
                                                └→ Railway API
                                                     └→ PostgreSQL
```

### Feature Flag

| Variable | Default | Values | Effect |
|----------|---------|--------|--------|
| `NEXT_PUBLIC_LEGACY_DASHBOARD_MODE` | `iframe` | `iframe`, `native` | Controls render strategy |
| `NEXT_PUBLIC_LEGACY_DASHBOARD_URL` | See below | URL string | Override iframe src |

Default iframe URL: `https://infinityxonesystems.github.io/XPS_INTELLIGENCE_SYSTEM/`

### Migration Status
See `LEGACY_DASHBOARD_MIGRATION.md` for the full per-feature migration ledger.

**Current phase:** Bridge (iframe)  
**Gate to native:** All 34 features must be marked `ported` with test coverage.

---

## 5. Data Flow

### Lead Intelligence Pipeline
```
Shadow Scraper (Railway worker-playwright)
  └─► Redis/BullMQ queue
        └─► worker-default
              ├─► Validation agent
              ├─► Enrichment agent
              ├─► Scoring agent
              └─► PostgreSQL (leads table)
                    └─► Railway REST API (/api/leads)
                          └─► frontend (/legacy-dashboard iframe)
                                └─► User browser
```

### Agent Dispatch Pattern
```
Frontend (trigger) → POST /api/v1/runtime/command
  └─► Backend runtime controller
        └─► BullMQ queue (Redis)
              └─► Worker consumer
                    └─► Agent execution (sandboxed)
                          └─► Artifact stored (PostgreSQL)
                                └─► GET /api/v1/artifacts (frontend poll)
```

---

## 6. CI/CD Pipeline

```
Push / PR
  ├─► CI workflow (ci.yml)
  │     ├─► backend: ruff · mypy · pytest
  │     ├─► frontend: eslint · tsc · next build
  │     └─► agents: py_compile
  ├─► Playwright E2E (playwright-tests.yml)
  │     ├─► foundation.spec.ts
  │     └─► legacy-dashboard.spec.ts
  ├─► Security scan (security-scan.yml)
  ├─► Self-audit (repo-self-audit.yml)
  └─► Deploy (deploy-railway.yml)
        ├─► staging (push to main, auto)
        └─► production (tagged release, manual approval)
```

---

## 7. Environment Variables Schema

### Frontend (`apps/frontend/`)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `NEXT_PUBLIC_LEGACY_DASHBOARD_MODE` | `iframe\|native` | `iframe` | Legacy dashboard render mode |
| `NEXT_PUBLIC_LEGACY_DASHBOARD_URL` | URL | `https://infinityxonesystems.github.io/XPS_INTELLIGENCE_SYSTEM/` | Legacy iframe src |

### Backend (`apps/backend/`)

| Variable | Type | Required | Description |
|----------|------|----------|-------------|
| `DATABASE_URL` | `postgresql://...` | ✅ | Primary database |
| `REDIS_URL` | `redis://...` | ✅ | Queue + cache |
| `GROQ_API_KEY` | string | ✅ | Groq LLM provider |
| `ENVIRONMENT` | `development\|staging\|production` | ✅ | Runtime environment |
| `AUTONOMY_ENABLED` | `true\|false` | — | Enable autonomous operations |
| `SCRAPER_AUTORUN_ENABLED` | `true\|false` | — | Enable scheduled scraping |

---

## 8. Legacy System Inventory (XPS_INTELLIGENCE_SYSTEM)

The following components from `InfinityXOneSystems/XPS_INTELLIGENCE_SYSTEM` are being migrated into this monorepo. See `FORENSIC_AUDIT/legacy_dashboard_discovery.md` for the detailed inventory.

| Component | Source Path | Target Path | Status |
|-----------|-------------|-------------|--------|
| Dashboard (Next.js) | `dashboard/` | `apps/frontend/` (native, TBD) | bridged via iframe |
| Backend API | `api/`, `backend/` | `apps/backend/` | Planned |
| Agents | `agents/` | `packages/agents/` | Planned |
| Scrapers | `scrapers/` | `apps/workers/playwright` | Planned |
| Queue system | `queue/`, `task_queue/` | `apps/workers/default` | Planned |
| Runtime controller | `runtime_controller/` | `apps/backend/` | Planned |
| Contracts | `contracts/` | `packages/contracts/` | Planned |
| Shared library | `infinity_library/` | `packages/shared/` | Planned |

---

*This document is the authoritative system topology. All architectural changes must update this file via PR.*
