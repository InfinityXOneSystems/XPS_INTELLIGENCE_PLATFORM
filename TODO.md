# XPS Intelligence Platform — Living TODO

> **Living Document** — Updated by the `docs-sync` workflow and Infinity Orchestrator.  
> Items are automatically created from GitHub Issues with the `todo` label.

---

## 🔴 Critical / Blockers

- [ ] Configure GitHub branch protection rules on `main` and `develop` (manual — requires repo admin)
- [ ] Add `RAILWAY_TOKEN` to GitHub Actions Secrets (manual — requires Railway access)
- [ ] Install **Infinity Orchestrator** GitHub App on this repository (manual — requires org admin)
- [ ] Configure **GitGuardian** integration on this repository (manual — requires org admin)
- [ ] Add `GITGUARDIAN_API_KEY` to GitHub Actions Secrets

---

## 🟠 High Priority (Foundation Phase)

- [ ] Create `develop` branch from `main`
- [ ] Configure Dependabot (`dependabot.yml`) for all package ecosystems
- [ ] Set up GitHub Projects board for Phase tracking
- [ ] Configure GitHub Pages for docs hosting
- [ ] Add repository topics and description in GitHub settings
- [ ] Review and activate all GitHub Actions workflows
- [ ] Verify Playwright test workflow runs cleanly on a stub test

---

## 🟡 Medium Priority (Phase 1 Prep)

- [ ] Audit `XPS_INTELLIGENCE_SYSTEM` backend for consolidation readiness
- [ ] Audit `XPS-INTELLIGENCE-FRONTEND` for consolidation readiness
- [ ] Map all environment variables across source repos
- [ ] Create Railway project for staging and production environments
- [ ] Design Postgres schema for memory system
- [ ] Define Shadow Scraper integration interface
- [ ] Document all agent contracts in `docs/agents/`

---

## 🟢 Low Priority / Enhancements

- [ ] GitHub Copilot Extensions configuration
- [ ] Groq API fallback configuration
- [ ] GPT Actions schema definition
- [ ] Copilot Mobile setup instructions
- [ ] Advanced Playwright visual regression baseline snapshots
- [ ] Semantic release configuration
- [ ] SBOM (Software Bill of Materials) generation workflow

---

## ✅ Completed

- [x] Repository created and initialized
- [x] Living README implemented
- [x] BLUEPRINT.md created
- [x] ROADMAP.md created
- [x] TODO.md created (this file)
- [x] CHANGELOG.md created
- [x] `.github/copilot-instructions.md` created
- [x] `.github/ARCHITECTURE.md` created
- [x] `.github/CODEOWNERS` created
- [x] `.github/PULL_REQUEST_TEMPLATE.md` created
- [x] Issue templates created
- [x] All foundation GitHub Actions workflows created
- [x] Monorepo directory skeleton created
- [x] Bootstrap and dev scripts created

---

*TODO auto-maintained by `docs-sync` workflow. Create a GitHub Issue with label `todo` to add items automatically.*
