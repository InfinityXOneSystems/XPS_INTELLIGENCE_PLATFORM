# XPS Intelligence Platform — Active Memory

This file is the persistent memory context for Copilot and autonomous agents
operating on this repository. It must be read at the start of every session.
Update this file whenever a phase is completed or the system state changes.

## Current Phase

**Phase: Bootstrap (Governance Layer Complete)**

The repo bootstrap PR has established the governance scaffolding. No
application code has been added yet. Subsequent phases follow the prompts
in `prompts/`.

## Completed Milestones

- [x] Repo bootstrap: governance docs, CI workflows, meta-files committed to
  `main` via PR from `copilot/bootstrap-repo-infinityxonesystems`

## Next Phase

**Phase 1: Forensic Audit** — Use `prompts/01_forensic_audit.prompt` to
create a PR that audits the 6 source repositories and generates
`FORENSIC_AUDIT/FORENSIC_ANALYSIS_REPORT.md` and
`FORENSIC_AUDIT/consolidation_plan.json`.

Source repos to audit:

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
| Railway for backend/workers | Specified by operator; no deviation |
| Shadow Scraper ignores robots.txt by default | Operator directive (2026-03-13) |
| Shadow Scraper max parallelism with budget caps | Operator directive (2026-03-13) |

## Operator Preferences

- Approve-only mode: operator approves PRs; all other work is automated.
- No aesthetic changes to existing frontend. Additive UI only.
- 2-hour scraper cycle when `SCRAPER_ENABLED=true`.
- `AUTONOMY_ENABLED=false` is the emergency stop for all agents.
- **Shadow Scraper compliance (2026-03-13):** robots.txt IGNORED by default.
  Set `SCRAPER_RESPECT_ROBOTS_TXT=true` to honour robots.txt when needed.
- **Shadow Scraper parallelism (2026-03-13):** maximum safe inhalation.
  Default caps: MAX_CONCURRENCY=20, DOMAIN_CONCURRENCY=5,
  MAX_REQUESTS=10000, MAX_PAGES=5000, MAX_RUNTIME_SECONDS=3600.

## TAP Status

- **Policy:** `_OPS/POLICY/TAP.md` — committed, enforced via CI
- **Authority:** Branch protections — to be configured by operator per
  `_OPS/RUNBOOK/OPERATOR_RUNBOOK.md`
- **Truth:** `FORENSIC_AUDIT/` — populated after Phase 1 audit

## Known Gaps (to resolve in Phase 1)

- Source repo forensic reports not yet generated
- `FORENSIC_AUDIT/FORENSIC_ANALYSIS_REPORT.md` — pending Phase 1
- `FORENSIC_AUDIT/REMEDIATION_CHECKLIST.md` — pending Phase 1
- Branch protections not yet configured (requires operator action)
