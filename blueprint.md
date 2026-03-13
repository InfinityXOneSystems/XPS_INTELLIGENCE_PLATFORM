# XPS Intelligence Platform — System Blueprint

> **Version:** 1.0.0-foundation  
> **Status:** 🔵 Foundation Phase (Pre-Phase 1)  
> **Last Updated:** auto (via `docs-sync` workflow)

---

## 1. Mission Statement

Build a **fully autonomous, zero-human-intervention intelligence platform** that:

- Consolidates all XPS/Infinity codebases into a single hardened monorepo
- Uses GitHub as the absolute source of truth for all state, code, and workflow
- Deploys to Railway (backend + frontend) with Postgres, Redis, and optional Supabase
- Operates autonomously 24/7 with humans only observing and issuing strategic commands
- Achieves 100% test coverage via Playwright E2E + unit tests on every commit
- Uses GitHub Copilot (primary LLM) and Groq (secondary LLM) for intelligence
- Routes all orchestration through the **Infinity Orchestrator** GitHub App

---

## 2. Core Principles

| Principle | Implementation |
|-----------|---------------|
| **GitHub-first** | All state, secrets, workflows live in GitHub |
| **Zero fake data** | Shadow Scraper only; no sample/mock leads |
| **Autonomous by default** | Every repeatable operation is automated |
| **Secure by design** | GitGuardian + CodeQL + branch protection on every merge |
| **Living documentation** | Docs auto-update via `docs-sync` workflow |
| **Observability** | Playwright snapshots + Railway metrics on every deploy |
| **Conflict-free** | Auto-conflict-resolve agent on every PR |
| **Memory-persistent** | Agent memory stored in Railway Postgres |

---

## 3. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GITHUB (Source of Truth)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Copilot  │  │ Projects │  │  Pages   │  │    Actions    │  │
│  │  (LLM)   │  │ (Tasks)  │  │  (Docs)  │  │  (Workflows)  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └───────┬───────┘  │
│       └─────────────┴─────────────┴────────────────┘           │
│                           │                                      │
│              ┌────────────▼───────────┐                         │
│              │  Infinity Orchestrator  │                         │
│              │  (Read/Write/Command)  │                         │
│              └────────────┬───────────┘                         │
└───────────────────────────┼─────────────────────────────────────┘
                            │
              ┌─────────────▼─────────────┐
              │        RAILWAY CLOUD        │
              │  ┌──────────┐ ┌─────────┐ │
              │  │ Backend  │ │Frontend │ │
              │  │(FastAPI) │ │(Next.js)│ │
              │  └────┬─────┘ └────┬────┘ │
              │  ┌────▼────────────▼────┐ │
              │  │  Postgres  │  Redis  │ │
              │  └────────────┬─────────┘ │
              └───────────────┼───────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Supabase (optional)│
                    │  (Extended Storage) │
                    └────────────────────┘
```

---

## 4. Technology Stack

### Runtime
| Layer | Technology | Hosting |
|-------|-----------|---------|
| Backend API | FastAPI (Python) + Node.js microservices | Railway |
| Frontend | React / Next.js | Railway |
| Database | PostgreSQL (Railway) + Supabase extension | Railway / Supabase |
| Cache/Queue | Redis (Railway) | Railway |
| File Storage | GitHub + Supabase Storage | Cloud |

### Intelligence & LLMs
| Role | Provider | Fallback |
|------|---------|---------|
| Primary LLM | GitHub Copilot | Groq |
| Code Review | GitHub Copilot | — |
| Agent Orchestration | Infinity Orchestrator | — |
| Scraping | Shadow Scraper (no API key required) | — |

### DevOps & Automation
| Tool | Purpose |
|------|---------|
| GitHub Actions | CI/CD, auto-merge, docs, security |
| GitHub Projects | Autonomous sprint/task management |
| GitHub Pages | Living docs hosting |
| GitGuardian | Secret scanning & security alerts |
| CodeQL | Static analysis on every PR |
| Dependabot | Automated dependency updates |
| Playwright | E2E tests + visual snapshots |

---

## 5. Data Flow

```
[Shadow Scraper] → [Railway Backend API] → [Postgres/Redis]
                                        ↓
                              [Agent Processing Layer]
                                        ↓
                           [Intelligence Frontend (Next.js)]
                                        ↓
                              [GitHub Projects / Reports]
```

### Memory System
- **Short-term:** Redis (session/request scoped)
- **Long-term:** Postgres (agent memory, decisions, history)
- **Structured docs:** GitHub (architecture, changelog, decisions)

---

## 6. Phase Gate Summary

| Phase | Name | Status |
|-------|------|--------|
| Foundation | Open-source foundation, docs, workflows | 🔵 In Progress |
| Phase 1 | Backend + Frontend consolidation | ⬜ Pending |
| Phase 2 | Build pipeline + Quantum-X integration | ⬜ Pending |
| Phase 3 | Admin control plane + Vizual-X | ⬜ Pending |
| Phase 4 | ConstructIQ-360 + full agent suite | ⬜ Pending |
| **Phase 5** | **Full Autonomous Operation** | ⬜ Pending |

See [`ROADMAP.md`](ROADMAP.md) for detailed phase breakdown.

---

## 7. Security Architecture

```
Every commit → GitGuardian scan (secret detection)
Every PR     → CodeQL static analysis
Every PR     → Playwright E2E tests
Every merge  → Railway deploy gates (health check required)
main branch  → Branch protection: required reviews + status checks + signed commits
```

### Secret Management
- **GitHub Secrets:** API keys, Railway tokens, Supabase credentials
- **Railway Variables:** Runtime environment config
- **Zero secrets in code:** Enforced by GitGuardian + pre-commit hooks

---

## 8. Agent Inventory (Consolidation Target)

| Agent | Source Repo | Purpose |
|-------|-------------|---------|
| Shadow Scraper | XPS_INTELLIGENCE_SYSTEM | Web scraping without API requirements |
| Intelligence Agent | XPS_INTELLIGENCE_SYSTEM | Core AI decision making |
| Build Agent | QUANTUM-X-BUILD | Automated build orchestration |
| Admin Agent | VIZUAL-X-ADMIN-CONTROL-PLANE | Admin automation |
| ConstructIQ Agent | CONSTRUCT-IQ-360 | Construction intelligence |
| Conflict Resolver | (new) | Auto-resolve git/code conflicts |
| Memory Agent | (new) | Persistent agent memory via Postgres |
| Bot Updater | (new) | Autonomous bot self-update |

---

## 9. Workflow Inventory

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci.yml` | Push / PR | Lint, test, build |
| `deploy-railway.yml` | Push to main/develop | Deploy to Railway |
| `playwright-tests.yml` | Push / PR | E2E tests + snapshots |
| `auto-label.yml` | PR/Issue open | Automatic labelling |
| `auto-merge.yml` | CI pass + label | Autonomous PR merge |
| `issue-manager.yml` | Schedule / event | Issue triage & assignment |
| `security-scan.yml` | Push / PR | GitGuardian + CodeQL |
| `docs-sync.yml` | Push to main | Update living docs |
| `dependabot-auto-merge.yml` | Dependabot PR | Auto-merge safe updates |

---

*Blueprint auto-maintained by `docs-sync` workflow.*
