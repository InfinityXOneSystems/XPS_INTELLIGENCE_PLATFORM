# XPS Intelligence Platform

> **The Autonomous Intelligence Monorepo — Phase 5 Foundation**
>
> GitHub is the single source of truth. All operations are autonomous, cloud-native, and zero-touch unless human command is required.

---

## 🚦 System Status

| Component | Status |
|-----------|--------|
| CI Pipeline | [![CI](../../actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml) |
| Deploy (Railway) | [![Deploy](../../actions/workflows/deploy-railway.yml/badge.svg)](../../actions/workflows/deploy-railway.yml) |
| Security Scan | [![Security](../../actions/workflows/security-scan.yml/badge.svg)](../../actions/workflows/security-scan.yml) |
| Playwright Tests | [![E2E](../../actions/workflows/playwright-tests.yml/badge.svg)](../../actions/workflows/playwright-tests.yml) |
| Docs Sync | [![Docs](../../actions/workflows/docs-sync.yml/badge.svg)](../../actions/workflows/docs-sync.yml) |

---

## 📐 Architecture Overview

```
XPS_INTELLIGENCE_PLATFORM (Monorepo)
├── apps/
│   ├── backend/          ← FastAPI / Node services (Railway)
│   └── frontend/         ← React / Next.js Intelligence UI (Railway)
├── packages/
│   ├── agents/           ← Autonomous AI agents consolidation
│   └── shared/           ← Shared utilities, types, constants
├── scripts/              ← Automation & bootstrap scripts
├── docs/                 ← Living architecture & API docs
├── .github/
│   ├── workflows/        ← All GitHub Actions (CI/CD, auto-merge, security…)
│   ├── ISSUE_TEMPLATE/   ← Structured issue forms
│   ├── copilot-instructions.md
│   ├── ARCHITECTURE.md
│   └── BLUEPRINT.md
├── ROADMAP.md
├── BLUEPRINT.md
├── TODO.md
└── CHANGELOG.md
```

Full architecture detail → [`.github/ARCHITECTURE.md`](.github/ARCHITECTURE.md)
System blueprint → [`BLUEPRINT.md`](BLUEPRINT.md)

---

## 🗂️ Source Repositories Being Consolidated

| Repo | Purpose | Phase |
|------|---------|-------|
| `XPS_INTELLIGENCE_SYSTEM` | Core backend intelligence engine | Phase 1 |
| `XPS-INTELLIGENCE-FRONTEND` | Intelligence dashboard UI | Phase 1 |
| `QUANTUM-X-BUILD` | Build pipeline & infra automation | Phase 2 |
| `VIZUAL-X-ADMIN-CONTROL-PLANE` | Admin control plane | Phase 3 |
| `CONSTRUCT-IQ-360` | AI construction intelligence | Phase 4 |

---

## 🤖 Automation System

This platform uses **GitHub-native tooling** as the backbone of full autonomy:

- **GitHub Actions** — CI/CD, auto-merge, auto-label, security gates, Playwright E2E
- **GitHub Projects** — Autonomous task and sprint tracking
- **GitHub Pages** — Living documentation hosting
- **GitHub Copilot** — Primary LLM; **Groq** as secondary
- **Infinity Orchestrator** — Read / Write / Command orchestration layer
- **Railway** — Backend + Frontend deployment; Postgres + Redis
- **Supabase** — Extended data layer if required
- **GitGuardian** — Secret scanning & security hardening
- **Playwright** — Automated frontend & backend E2E tests + snapshots

---

## 🌿 Branch Strategy

| Branch | Purpose | Auto-Deploy |
|--------|---------|-------------|
| `main` | Production (protected) | ✅ Railway Production |
| `develop` | Integration branch | ✅ Railway Staging |
| `feature/*` | Feature work | ❌ |
| `fix/*` | Bug fixes | ❌ |
| `release/*` | Release candidates | ✅ Railway Staging |
| `hotfix/*` | Emergency production fixes | ✅ Railway Production |

**Auto-merge** is enabled for PRs that:
1. Target `develop`
2. Pass all required CI checks
3. Are labelled `auto-merge`
4. Have at least one approving review (or are authored by a trusted bot)

---

## 🔐 Security Model

- All secrets are stored in **GitHub Actions Secrets** or **Railway Environment Variables** — never in code.
- **GitGuardian** scans every push and PR.
- **CodeQL** runs on every PR to `main` and `develop`.
- Dependency updates managed by **Dependabot**.
- Branch protection rules enforce signed commits and required status checks on `main`.

---

## 🚀 Quick Start (Local Development)

```bash
# 1. Clone
git clone https://github.com/InfinityXOneSystems/XPS_INTELLIGENCE_PLATFORM.git
cd XPS_INTELLIGENCE_PLATFORM

# 2. Bootstrap (installs all workspace dependencies)
./scripts/bootstrap.sh

# 3. Start local dev environment
./scripts/dev.sh
```

---

## 📋 Roadmap

See [`ROADMAP.md`](ROADMAP.md) for the full phased roadmap including **Phase 5: Full Autonomous Operation**.

## 📝 TODO

See [`TODO.md`](TODO.md) for the living task list.

## 📜 Changelog

See [`CHANGELOG.md`](CHANGELOG.md) for the complete history of changes.

---

## 🤝 Contributing

All contributions flow through the autonomous PR pipeline:
1. Branch from `develop` using the naming convention (`feature/`, `fix/`, etc.)
2. Open a PR using the provided templates
3. CI must pass; Copilot code review is automatic
4. Approved PRs targeting `develop` with `auto-merge` label are merged automatically

Human intervention is reserved for:
- Strategic direction changes
- Emergency hotfixes requiring manual approval
- Phase gate sign-offs

---

*This README is automatically maintained by the `docs-sync` workflow. Last updated: auto.*