# XPS Intelligence Platform — Active Memory

This file is the persistent memory context for Copilot and autonomous agents
operating on this repository. It must be read at the start of every session.
Update this file whenever a phase is completed or the system state changes.

## Current Phase

**Phase: Foundation Complete → Phase 2 (Source Repo Consolidation)**

Phase 1 foundation has been delivered. The full backend, frontend features,
workers, packages, and Railway wiring are in place. The next phase imports
capabilities from the 6 source repositories into the monorepo.

## Completed Milestones

- [x] Repo bootstrap: governance docs, CI workflows, meta-files committed to
  `main`
- [x] Phase 1 Foundation:
  - [x] `apps/backend/` — FastAPI runtime controller (health, leads, artifacts,
    scraper, autonomy, LLM routing)
  - [x] `apps/workers/default/` — Celery task worker
  - [x] `apps/workers/playwright/` — Browser automation worker
  - [x] `apps/workers/sandbox/` — Capability-gated sandbox runner
  - [x] `packages/contracts/` — TypeScript artifact+command+lead schemas
  - [x] `packages/infinity-library/` — Python validators, logging, policy
  - [x] `apps/frontend/workspace` — Center editing screen + artifact panels
  - [x] `apps/frontend/scraper` — Scraper settings UI + job management
  - [x] `.github/workflows/autonomy-scheduler.yml` — 2-hour cron cycle
  - [x] `apps/backend/railway.json`, `apps/frontend/railway.json`,
    `apps/workers/default/railway.json`
  - [x] `apps/backend/.env.example` — full env variable template
  - [x] `docs/deployment/RAILWAY_ENV_CONTRACT.md` — per-service env contract
  - [x] `_OPS/scripts/setup_railway_services.sh` — Railway CLI setup guide
  - [x] `TEST_EVIDENCE/README.md` + `TEST_EVIDENCE/latest.md`
  - [x] 17 backend unit tests pass, 19 infinity-library tests pass
  - [x] Frontend build + lint + type-check pass
  - [x] Copilot instructions updated with full system context

## Next Phase

**Phase 2: Source Repo Consolidation** — Import unique capabilities from
source repos additively. For each of the 6 source repos:

1. Run `source-forensic-audit.yml` → inspect `FORENSIC_AUDIT/sources/<repo>/`
2. Identify unique capabilities not yet in the monorepo
3. Import code with tests
4. Do NOT change frontend aesthetic

Source repos to consolidate:

- `InfinityXOneSystems/XPS_INTELLIGENCE_SYSTEM`
- `InfinityXOneSystems/XPS-INTELLIGENCE-FRONTEND`
- `InfinityXOneSystems/quantum-x-builder`
- `InfinityXOneSystems/intelligence-system`
- `InfinityXOneSystems/manus-core-system`
- `InfinityXOneSystems/vizual-x-admin-control-plane`

## Architecture Decisions (Locked)

| Decision | Rationale |
|---|---|
| Single runtime controller (backend) | Prevents parallel execution authorities |
| Sandbox boundary enforced | All code execution and scraping in isolated workers |
| No VITE_ secrets | Frontend bundle is public; secrets are backend-only |
| Squash merge only | Clean linear history; clear attributions |
| Railway for backend/workers | Specified by operator; project 139ef8de-840d-4110-aa21-fe3eeed7c469 |
| Groq as LLM fallback | Server-side only via GROQ_API_KEY env var |
| Idempotency keys | All scrape/ingest operations use idempotency_key field |

## Infrastructure (read-only; do not hardcode)

| Resource | Read via env var |
|---|---|
| Postgres: postgres-production-5596.up.railway.app:5432 | `DATABASE_URL` |
| Redis: tramway.proxy.rlwy.net:22806 | `REDIS_URL` |
| Object storage: t3.storageapi.dev / stocked-organizer-khf6nyu | `OBJECT_STORAGE_*` |

## Operator Preferences

- Approve-only mode: operator approves PRs; all other work is automated.
- No aesthetic changes to existing frontend. Additive UI only.
- 2-hour scraper cycle controlled by `SCRAPER_AUTORUN_ENABLED` feature flag.
- `AUTONOMY_ENABLED=false` is the emergency stop for all agents.
- Railway token installed as `RAILWAY_TOKEN` GitHub Actions secret.

## TAP Status

- **Policy:** `_OPS/POLICY/TAP.md` — committed, enforced via CI
- **Authority:** Branch protections — configure per `_OPS/RUNBOOK/OPERATOR_RUNBOOK.md`
- **Truth:** `TEST_EVIDENCE/` — bootstrapped; populate via CI proof runs

## Known Gaps (resolve in Phase 2+)

- Source repo forensic reports not yet fully generated
  (run `source-forensic-audit.yml` manually)
- Alembic migrations not yet applied to Railway Postgres
  (run `scripts/db-migrate.sh` after Railway services deployed)
- Branch protections not yet configured (requires operator action via GitHub UI)
- `BACKEND_URL` secret not yet set in GitHub Actions (set after first Railway deploy)
