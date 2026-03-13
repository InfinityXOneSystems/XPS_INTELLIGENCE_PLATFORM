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
- **Compliance default:** robots.txt is **ignored** (operator directive, 2026-03-13)
  — set `SCRAPER_RESPECT_ROBOTS_TXT=true` to honour robots.txt
- **Pipeline:** scrape → ingest → normalize → score → store
- **Toggle:** `SCRAPER_ENABLED` environment variable (Railway + GitHub Actions)
- **Settings UI:** concurrency, rate limits, source selection, compliance flags

### Parallelism and Budget Caps

| Parameter | Default | Environment Variable |
|---|---|---|
| Global concurrency | 20 | `SCRAPER_MAX_CONCURRENCY` |
| Per-domain concurrency | 5 | `SCRAPER_DOMAIN_CONCURRENCY` |
| Max requests / job | 10 000 | `SCRAPER_MAX_REQUESTS` |
| Max pages / job | 5 000 | `SCRAPER_MAX_PAGES` |
| Max runtime / job | 3 600 s | `SCRAPER_MAX_RUNTIME_SECONDS` |
| Back-off base | 250 ms | `SCRAPER_BACKOFF_BASE_MS` |
| Back-off ceiling | 30 000 ms | `SCRAPER_BACKOFF_MAX_MS` |
| Request timeout | 30 000 ms | `SCRAPER_REQUEST_TIMEOUT_MS` |
| Retry max | 3 | `SCRAPER_RETRY_MAX` |

The scraper configuration module lives at
`packages/agents/shadow-scraper/config.py`. Tests at
`packages/agents/shadow-scraper/tests/test_config.py` (59 tests) verify
all defaults and override paths. The `shadow-scraper-proof` CI job
emits a `TEST_EVIDENCE/shadow-scraper-concurrency-metrics.json` artifact
on every run.

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
| `SCRAPER_RESPECT_ROBOTS_TXT` | Railway (backend) | `false` (default) / `true` to honour robots.txt |
| `SCRAPER_MAX_CONCURRENCY` | Railway (backend) | Global concurrent-request cap (default 20) |
| `SCRAPER_DOMAIN_CONCURRENCY` | Railway (backend) | Per-domain concurrent cap (default 5) |
| `SCRAPER_MAX_REQUESTS` | Railway (backend) | Max requests per scrape job (default 10000) |
| `SCRAPER_MAX_PAGES` | Railway (backend) | Max pages per scrape job (default 5000) |
| `SCRAPER_MAX_RUNTIME_SECONDS` | Railway (backend) | Hard job deadline in seconds (default 3600) |
| `SCRAPER_BACKOFF_BASE_MS` | Railway (backend) | Adaptive back-off base delay ms (default 250) |
| `SCRAPER_BACKOFF_MAX_MS` | Railway (backend) | Adaptive back-off ceiling ms (default 30000) |
| `SCRAPER_REQUEST_TIMEOUT_MS` | Railway (backend) | Per-request timeout ms (default 30000) |
| `SCRAPER_RETRY_MAX` | Railway (backend) | Max retries per failed request (default 3) |
| `AUTONOMY_ENABLED` | Railway + Actions | Master autonomy toggle |
| `VITE_API_URL` | Railway (frontend) | Backend API base URL |
| `GITHUB_TOKEN` | Actions (auto) | GitHub API access (read-only in audit) |
