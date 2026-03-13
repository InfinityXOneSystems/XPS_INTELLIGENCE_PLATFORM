# System Topology — XPS Intelligence Platform

This document is the **single source of truth** for the runtime architecture
of the XPS Intelligence Platform mono-repo. All agents, workflows, and
contributors must conform to this topology.

## Repository Layout

```text
XPS_INTELLIGENCE_PLATFORM/
├── apps/
│   ├── backend/          # FastAPI runtime controller + REST + WebSocket API
│   └── frontend/         # Vite + React + TypeScript
├── packages/
│   ├── agents/           # Agent implementations (scraper, SEO, social, etc.)
│   └── shared/           # Shared types, schemas, and utilities
├── _OPS/
│   ├── POLICY/           # TAP governance policy
│   ├── ARCHITECTURE/     # System topology (this file)
│   ├── RUNBOOK/          # Operator runbook
│   └── scripts/          # Read-only validation scripts
├── prompts/              # Copilot operator prompts
├── FORENSIC_AUDIT/       # Auto-generated audit reports (CI artifacts)
├── TEST_EVIDENCE/        # Test result artifacts (CI artifacts)
└── .github/
    ├── workflows/        # GitHub Actions CI/CD pipelines
    └── copilot-instructions.md
```

## Services (Railway Deployment)

| Service | Type | Description |
|---|---|---|
| `api` | Web | FastAPI runtime controller — REST + WebSocket |
| `worker-default` | Worker | Async task queue consumer (general workloads) |
| `worker-playwright` | Worker | Playwright-sandboxed scraper worker |
| `sandbox-runner` | Worker | Isolated execution environment for code tasks |
| `redis` | Database | Task queue + state store |
| `postgres` | Database | Leads, artifacts, audit logs |

## Frontend Architecture

- **Stack:** Vite + React + TypeScript
- **LLM Layer:** `src/lib/llm.ts` — provider-routed (Groq secondary fallback)
- **Orchestrator:** `src/lib/orchestrator.ts` — UI-side planner/command client
- **API Client:** `src/lib/api.ts` — communicates with backend via
  `VITE_API_URL`
- **Center Editing Screen:** Monaco editor + unified artifact results panel
- **Agent Roster:** 13+ agents surfaced through the runtime command interface

### Frontend Invariants

- The center editing screen renders natural language and typed artifacts:
  images, video, music, business templates, charts, normalized leads, and
  system creation outputs.
- The visual identity (colors, typography, component library, layout) is
  **locked**. No changes without a design-approved PR.
- All environment variables are non-secret. Secrets are backend-only.

## Runtime Authority

All execution flows through exactly one path:

```text
User Command (UI)
  → Frontend Orchestrator (planner only)
    → POST /api/v1/runtime/command
      → RuntimeController
        → CommandValidator
          → CommandRouter
            → TaskDispatcher
              → Redis Queue
                → Worker (default | playwright | sandbox)
                  → Artifact Storage
                    → WebSocket push to UI
```

**No alternate execution paths are allowed.** The frontend orchestrator is a
client, not an execution authority.

## Scraper System

- **Universal Scraper:** supports both manual trigger and scheduled 2-hour cycle
- **Compliance:** allowlist-based domain targeting; rate limiting enforced
- **Pipeline:** scrape → ingest → normalize → score → store
- **Toggle:** `SCRAPER_ENABLED` environment variable (Railway + GitHub Actions)
- **Settings UI:** concurrency, rate limits, source selection, compliance flags

## Lead Pipeline

```text
Raw Scrape Output
  → Ingest Worker (dedup + validate)
    → Normalize Worker (standardize schema)
      → Score Worker (ML scoring model)
        → PostgreSQL (leads table)
          → Frontend Results Panel
```

## Security Boundary

| Layer | Constraint |
|---|---|
| Frontend bundle | No secrets; no server-side logic |
| API surface | CORS allowlist; JWT/token auth |
| Worker execution | Container-isolated; read-only mounts where possible |
| Sandbox runner | Constrained network (allowlist); per-task workspace |
| Database | Private Railway network; no public exposure |

## CI/CD Pipeline

```text
Push / PR
  → ci.yml (lint + structure + secrets scan)
    → backend tests (unit + integration)
      → frontend build (typecheck + lint + build)
        → e2e tests (Playwright)
          → audit.yml (repo settings + toolchain validation)
            → Deploy to Railway (main branch only, after all gates)
```

## Scheduled Automation (Every 2 Hours)

- Scraper cycle: fetch → ingest → normalize → score
- Audit report: regenerate `FORENSIC_AUDIT/` snapshot
- Dependency check: flag new CVEs in issues

## Environment Variables

| Variable | Location | Purpose |
|---|---|---|
| `DATABASE_URL` | Railway (backend) | PostgreSQL connection |
| `REDIS_URL` | Railway (backend) | Redis connection |
| `GROQ_API_KEY` | Railway (backend) | Groq LLM provider |
| `LLM_PROVIDER` | Railway (backend) | Primary LLM provider name |
| `SCRAPER_ENABLED` | Railway (backend) | Enable/disable scraper schedule |
| `AUTONOMY_ENABLED` | Railway + Actions | Master autonomy toggle |
| `VITE_API_URL` | Railway (frontend) | Backend API base URL |
| `GITHUB_TOKEN` | Actions (auto) | GitHub API access (read-only in audit) |
