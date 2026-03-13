# GitHub Copilot Instructions — XPS Intelligence Platform

> **Meta Copilot Instructions**  
> These instructions govern all AI-assisted development on this repository.  
> Every Copilot suggestion, code generation, and review must conform to these rules.

---

## 🎯 Mission

You are the primary AI development assistant for the **XPS Intelligence Platform** — a fully autonomous, zero-human-intervention intelligence system. Your role is to:

1. Generate **100% production-ready, hardened code** — no stubs, no placeholders in active code paths
2. Enforce all architectural patterns defined in `.github/ARCHITECTURE.md`
3. Ensure every change maintains or improves test coverage
4. Never introduce secrets, hardcoded credentials, or insecure patterns
5. Always suggest the minimal, surgical change that solves the problem

---

## 📐 Architecture Constraints

### Monorepo Structure (MANDATORY)
```
apps/backend/    → FastAPI (Python) backend services
apps/frontend/   → Next.js / React frontend
packages/agents/ → All autonomous AI agents
packages/shared/ → Shared utilities, types, constants
scripts/         → Automation scripts (bash/python only)
docs/            → Architecture, API, deployment docs
tests/e2e/       → Playwright E2E tests
```

### Technology Stack (DO NOT DEVIATE)
- **Backend:** Python (FastAPI) + Node.js microservices where needed
- **Frontend:** React / Next.js — additions only, no breaking changes to existing UI
- **Database:** PostgreSQL (Railway) + Redis (Railway) + Supabase (optional)
- **Primary LLM:** GitHub Copilot
- **Secondary LLM:** Groq
- **Orchestration:** Infinity Orchestrator GitHub App
- **Scraping:** Shadow Scraper only — never use fake/sample leads or paid APIs for lead data
- **Testing:** Playwright (E2E + visual snapshots) + pytest (backend) + Jest/Vitest (frontend)
- **CI/CD:** GitHub Actions exclusively
- **Deployment:** Railway exclusively

---

## 🔐 Security Rules (NON-NEGOTIABLE)

1. **Never** commit secrets, API keys, tokens, or passwords
2. **Always** use environment variables via `os.environ` (Python) or `process.env` (Node)
3. **Always** validate and sanitize all external input
4. **Always** use parameterized queries — never string-format SQL
5. **Always** handle errors explicitly — never swallow exceptions silently
6. Use `httpx` or `aiohttp` for async HTTP (Python); `axios` or `fetch` (Node/React)
7. Secrets reference pattern: `os.environ["SECRET_NAME"]` — raise `KeyError` if missing, never default to empty string

---

## 🧪 Testing Requirements

Every PR must:
1. Include or update tests for all changed code paths
2. Pass Playwright E2E tests with no regressions
3. Maintain 100% coverage on new code (backend: pytest-cov; frontend: vitest --coverage)
4. Not break any existing tests

Test file conventions:
- Backend: `apps/backend/tests/test_*.py`
- Frontend: `apps/frontend/src/**/*.test.{ts,tsx}`
- E2E: `tests/e2e/*.spec.ts`

---

## 🌿 Branch & PR Rules

### Branch Names
- `feature/<ticket-id>-short-description` — new features
- `fix/<ticket-id>-short-description` — bug fixes
- `hotfix/<description>` — emergency production fixes
- `release/<version>` — release candidates
- `docs/<description>` — documentation only

### Commit Messages (Conventional Commits)
```
<type>(<scope>): <subject>

Types: feat | fix | docs | style | refactor | test | chore | ci | perf | security
```

Examples:
- `feat(backend): add shadow scraper lead ingestion endpoint`
- `fix(frontend): resolve memory leak in agent status polling`
- `ci(workflows): add playwright snapshot tests to CI`

### PR Requirements
- Fill all sections of `.github/PULL_REQUEST_TEMPLATE.md`
- Link to the GitHub Issue
- All CI checks must pass
- No merge conflicts

---

## 🤖 Agent Development Patterns

When building or modifying agents in `packages/agents/`:

1. **Memory:** All agent state must be persisted to Postgres via the `MemoryAgent` interface
2. **Retry logic:** Use exponential backoff for all external calls
3. **Logging:** Use structured JSON logging (`structlog` for Python, `pino` for Node)
4. **Health checks:** Every agent must implement a `/health` endpoint
5. **Config:** All configuration via environment variables — never hardcoded

Agent interface (Python):
```python
class BaseAgent:
    async def run(self) -> AgentResult: ...
    async def health_check(self) -> bool: ...
    async def save_memory(self, key: str, value: dict) -> None: ...
    async def load_memory(self, key: str) -> dict | None: ...
```

---

## 📝 Documentation Requirements

- Every public function/class must have a docstring
- Complex logic must have inline comments
- API endpoints must have OpenAPI docstrings
- Architecture changes must update `.github/ARCHITECTURE.md`
- New features must update `ROADMAP.md` and `TODO.md`

---

## 🚫 What to NEVER Do

- Never generate or use fake/sample lead data
- Never hardcode URLs, ports, or environment-specific values
- Never skip error handling
- Never use `eval()`, `exec()`, or dynamic code execution with user input
- Never disable security linting rules
- Never merge to `main` directly — always via PR
- Never use `print()` for logging in production code — use the structured logger
- Never introduce breaking changes to the frontend UI without explicit human approval

---

## ✅ What to ALWAYS Do

- Use the existing shared utilities in `packages/shared/` before writing new ones
- Check `docs/api/` before creating new API endpoints (avoid duplication)
- Run `./scripts/bootstrap.sh` after any dependency changes
- Update `CHANGELOG.md` in every PR
- Add Playwright snapshot tests for any new UI component
- Use Railway environment variables for all deployment config

---

*These instructions are enforced by GitHub Copilot and reviewed on every PR.*
