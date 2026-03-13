# XPS Intelligence Platform — Detailed Architecture

> **Living Document** — Maintained by `docs-sync` workflow.  
> See `BLUEPRINT.md` for the executive overview.

---

## 1. Repository Structure

```
XPS_INTELLIGENCE_PLATFORM/
├── .github/
│   ├── ARCHITECTURE.md           ← This file
│   ├── BLUEPRINT.md              ← Executive blueprint
│   ├── CODEOWNERS                ← Code ownership
│   ├── copilot-instructions.md   ← Meta Copilot rules
│   ├── dependabot.yml            ← Automated dependency updates
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── feature_request.yml
│   │   └── phase5_task.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── auto-label.yml
│       ├── auto-merge.yml
│       ├── ci.yml
│       ├── deploy-railway.yml
│       ├── docs-sync.yml
│       ├── issue-manager.yml
│       ├── playwright-tests.yml
│       └── security-scan.yml
│
├── apps/
│   ├── backend/                  ← FastAPI backend (Railway)
│   │   ├── src/
│   │   │   ├── api/              ← Route handlers
│   │   │   ├── core/             ← Config, db, security
│   │   │   ├── models/           ← SQLAlchemy models
│   │   │   ├── schemas/          ← Pydantic schemas
│   │   │   └── services/         ← Business logic
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   └── railway.json
│   │
│   └── frontend/                 ← Next.js frontend (Railway)
│       ├── src/
│       │   ├── app/              ← Next.js app router
│       │   ├── components/       ← React components
│       │   ├── hooks/            ← Custom React hooks
│       │   ├── lib/              ← Utilities
│       │   └── styles/           ← Global styles
│       ├── public/
│       ├── tests/
│       ├── Dockerfile
│       ├── package.json
│       └── railway.json
│
├── packages/
│   ├── agents/                   ← All autonomous agents
│   │   ├── shadow-scraper/       ← Lead scraping (no API required)
│   │   ├── intelligence/         ← Core AI decision agent
│   │   ├── memory/               ← Persistent memory agent
│   │   ├── build/                ← Build automation agent
│   │   ├── admin/                ← Admin control agent
│   │   ├── conflict-resolver/    ← Git conflict resolution agent
│   │   └── bot-updater/          ← Autonomous bot self-update agent
│   │
│   └── shared/                   ← Cross-package utilities
│       ├── src/
│       │   ├── types/            ← Shared TypeScript types
│       │   ├── utils/            ← Shared utilities
│       │   └── constants/        ← Shared constants
│       └── package.json
│
├── scripts/
│   ├── bootstrap.sh              ← Full workspace bootstrap
│   ├── dev.sh                    ← Local dev launcher
│   ├── db-migrate.sh             ← Database migration runner
│   └── seed.sh                   ← DB seed (non-lead data only)
│
├── docs/
│   ├── architecture/             ← Deep-dive architecture docs
│   ├── api/                      ← API reference docs
│   ├── deployment/               ← Deployment guides
│   └── agents/                   ← Agent interface contracts
│
├── tests/
│   └── e2e/
│       ├── snapshots/            ← Playwright visual snapshots
│       └── *.spec.ts             ← E2E test specs
│
├── BLUEPRINT.md
├── CHANGELOG.md
├── README.md
├── ROADMAP.md
└── TODO.md
```

---

## 2. Backend Architecture (FastAPI)

### Request Flow
```
Client Request
    │
    ▼
Railway Load Balancer
    │
    ▼
FastAPI Application
    ├── Authentication Middleware (JWT)
    ├── Rate Limiting Middleware
    ├── Logging Middleware
    │
    ▼
Route Handler (apps/backend/src/api/)
    │
    ▼
Service Layer (apps/backend/src/services/)
    ├── Database (SQLAlchemy + Postgres)
    ├── Cache (Redis)
    ├── Agent Interface (packages/agents/)
    └── Memory Agent (Postgres)
```

### Database Schema (Core Tables)
- `agent_memory` — Persistent agent state
- `scraper_results` — Shadow Scraper output
- `agent_runs` — Agent execution history
- `system_config` — Runtime configuration
- `audit_log` — All system actions

### Configuration
All configuration is injected via environment variables:
```
DATABASE_URL        → Railway Postgres connection string
REDIS_URL           → Railway Redis connection string
SUPABASE_URL        → Supabase project URL (optional)
SUPABASE_KEY        → Supabase anon key (optional)
COPILOT_TOKEN       → GitHub Copilot API token
GROQ_API_KEY        → Groq API key (secondary LLM)
SECRET_KEY          → JWT signing secret
RAILWAY_ENVIRONMENT → "production" | "staging"
```

---

## 3. Frontend Architecture (Next.js)

### Component Architecture
```
apps/frontend/src/
├── app/
│   ├── layout.tsx            ← Root layout
│   ├── page.tsx              ← Dashboard home
│   ├── agents/               ← Agent management UI
│   ├── intelligence/         ← Intelligence views
│   ├── admin/                ← Admin control plane
│   └── api/                  ← Next.js API routes (BFF)
│
├── components/
│   ├── ui/                   ← Primitive UI components
│   ├── charts/               ← Data visualization
│   ├── agents/               ← Agent-specific components
│   └── layout/               ← Layout components
│
├── hooks/
│   ├── useAgent.ts           ← Agent state management
│   ├── useMemory.ts          ← Memory system hooks
│   └── useRealtime.ts        ← Railway/Supabase realtime
│
└── lib/
    ├── api.ts                ← Backend API client
    ├── auth.ts               ← Authentication utilities
    └── constants.ts          ← App constants
```

### Frontend Rules
- Frontend changes must be **additive only** — no breaking changes to existing UI
- All new components must have Playwright snapshot tests
- Use the existing design system — no new CSS frameworks
- API calls go through the BFF (`app/api/`) — never directly to backend from client

---

## 4. Agent Architecture

### Base Agent Contract
```python
# packages/agents/src/base.py
from abc import ABC, abstractmethod
from typing import Any

class BaseAgent(ABC):
    """All agents must implement this interface."""

    @abstractmethod
    async def run(self) -> dict[str, Any]:
        """Execute the agent's primary task."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if the agent is healthy."""

    async def save_memory(self, key: str, value: dict) -> None:
        """Persist agent memory to Postgres."""

    async def load_memory(self, key: str) -> dict | None:
        """Load agent memory from Postgres."""
```

### Agent Communication
Agents communicate via:
1. **Direct function calls** — within the same process
2. **Redis pub/sub** — for async cross-agent messaging
3. **Postgres** — for persistent shared state
4. **GitHub Issues/PRs** — for human-visible actions (via Infinity Orchestrator)

---

## 5. CI/CD Pipeline

```
Push to branch
    │
    ▼
GitHub Actions: ci.yml
    ├── Lint (ruff, eslint)
    ├── Type check (mypy, tsc)
    ├── Unit tests (pytest, vitest)
    ├── Security scan (CodeQL, GitGuardian)
    └── Build check
         │
         ▼ (if PR to develop/main)
GitHub Actions: playwright-tests.yml
    ├── E2E tests
    └── Visual snapshots
         │
         ▼ (if all pass + auto-merge label)
GitHub Actions: auto-merge.yml
    └── Merge to target branch
         │
         ▼ (if merge to main/develop)
GitHub Actions: deploy-railway.yml
    ├── Deploy backend to Railway
    ├── Deploy frontend to Railway
    └── Health check gate
         │
         ▼ (if deploy succeeds)
GitHub Actions: docs-sync.yml
    └── Update living docs (README, CHANGELOG, TODO)
```

---

## 6. Security Architecture

### Layers of Defense
1. **GitGuardian** — Secret scanning on every push
2. **CodeQL** — Static analysis on every PR
3. **Dependabot** — Automated dependency vulnerability patches
4. **Branch Protection** — Required CI + code review on `main`
5. **JWT Authentication** — All API endpoints require valid JWT
6. **Input Validation** — Pydantic (backend) + Zod (frontend) on all inputs
7. **SQL Injection Prevention** — SQLAlchemy ORM + parameterized queries
8. **Rate Limiting** — Redis-backed rate limiting on all public endpoints
9. **CORS** — Strict origin whitelist
10. **Environment Isolation** — Separate Railway environments for staging/production

### Secret Storage
| Secret | Storage Location | Access |
|--------|-----------------|--------|
| Database passwords | Railway Variables | Runtime only |
| API keys | GitHub Secrets | Workflows only |
| JWT secret | Railway Variables | Runtime only |
| Railway tokens | GitHub Secrets | Deploy workflows only |

---

## 7. Memory System

### Architecture
```
Agent Decision
    │
    ▼
MemoryAgent.save_memory(agent_id, key, value)
    │
    ├── Short-term: Redis (TTL = session duration)
    └── Long-term: Postgres (agent_memory table, no TTL)
         │
         ▼
MemoryAgent.load_memory(agent_id, key)
    │
    ├── Check Redis first (fast path)
    └── Fallback to Postgres (slow path, cache in Redis)
```

### Memory Schema
```sql
CREATE TABLE agent_memory (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id    TEXT NOT NULL,
    key         TEXT NOT NULL,
    value       JSONB NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(agent_id, key)
);
```

---

## 8. Infinity Orchestrator Integration

The Infinity Orchestrator GitHub App is granted:
- **Read** — All repository content, issues, PRs, actions
- **Write** — Issues, PRs, comments, labels, workflow dispatches
- **Command** — Trigger workflows, merge PRs, create branches

Integration points:
1. Workflow dispatch via Orchestrator → `workflow_dispatch` events
2. Issue creation/management → GitHub Issues API
3. PR automation → GitHub Pull Requests API
4. Memory persistence → via Backend API (Postgres)

---

*Architecture auto-maintained by `docs-sync` workflow.*
