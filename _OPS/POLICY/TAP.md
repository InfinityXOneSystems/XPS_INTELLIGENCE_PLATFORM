# TAP Protocol — Policy > Authority > Truth

This document is the **canonical policy enforcement contract** for the
XPS Intelligence Platform mono-repo. All automation, agents, and contributors
must comply.

## Policy (What Must Always Be True)

These are invariants. Violating them is a blocking issue requiring immediate
remediation.

1. **GitHub is the system of record.** No changes take effect outside of a
   reviewed and merged pull request.
2. **No production deploy without green CI and signed artifacts.** The `main`
   branch deploy gate requires all required status checks to pass.
3. **All automation is idempotent and safe to re-run.** Workflows must produce
   the same result whether run once or ten times.
4. **No secret exposure to client bundles.** Secrets may never carry a `VITE_`
   prefix. Frontend environment variables are public by definition.
5. **No change to frontend aesthetic (visual identity).** Changes to UI are
   additive only; existing component styles, tokens, and layout are immutable
   without an explicit design change PR approved by the platform team.
6. **Sandbox boundary is enforced.** All code execution, shell commands, and
   web scraping run inside the designated sandbox worker service.

## Authority (What Is Allowed to Act)

These define who and what can take action within the system.

| Actor | Allowed Actions | Restrictions |
|---|---|---|
| GitHub Actions (CI) | Read repo, run tests, lint, build | No write to main without policy gates |
| GitHub Actions (deploy) | Deploy to Railway on main | Only after all gates pass |
| GitHub Actions (audit) | Read repo settings, generate reports | Read-only; no mutations |
| Autonomous agent workflows | Open PRs, update branches | Cannot self-merge; cannot touch secrets |
| Human operators | Approve PRs, configure environments | All high-risk actions require operator approval |
| Railway | Deploy services from artifacts | Only from signed, gate-passing builds |

### Auto-Merge Policy

Autonomous PRs may auto-merge **only when**:

- Change scope is `documentation`, `dependency-patch`, or `audit-report`
- All required status checks pass
- No human review is required by CODEOWNERS for the changed paths
- The PR carries the `auto-merge` label and the `safe-auto-merge` label

## Truth (How We Prove It)

Every claimed capability must have **all three**:

1. Automated tests (unit and/or integration and/or e2e) that execute in CI
2. A reproducible runbook step documented in `_OPS/RUNBOOK/OPERATOR_RUNBOOK.md`
3. An artifact stored under `FORENSIC_AUDIT/` or `TEST_EVIDENCE/` that proves
   the capability worked in CI on a specific commit SHA

### Evidence Hierarchy

| Evidence Type | Minimum Requirement |
|---|---|
| Feature claim | Unit test + integration test + CI artifact |
| Security claim | CodeQL scan + dependency audit + secret scan |
| Performance claim | Benchmark test with baseline + CI artifact |
| Deployment claim | Successful Railway deploy log + health check result |

## Shadow Scraper Compliance Policy

These rules govern all use of the Shadow Scraper within the platform.

### Operator Directive (2026-03-13)

| Parameter | Default | Override |
|---|---|---|
| `SCRAPER_RESPECT_ROBOTS_TXT` | `false` — ignore robots.txt | Set `true` to honour robots.txt |
| `SCRAPER_MAX_CONCURRENCY` | `20` | Global concurrent-request cap |
| `SCRAPER_DOMAIN_CONCURRENCY` | `5` | Per-domain concurrent-request cap |
| `SCRAPER_MAX_REQUESTS` | `10000` | Max HTTP requests per job |
| `SCRAPER_MAX_PAGES` | `5000` | Max pages crawled per job |
| `SCRAPER_MAX_RUNTIME_SECONDS` | `3600` | Hard job deadline (1 hour) |
| `SCRAPER_BACKOFF_BASE_MS` | `250` | Adaptive back-off base delay |
| `SCRAPER_BACKOFF_MAX_MS` | `30000` | Adaptive back-off ceiling |
| `SCRAPER_REQUEST_TIMEOUT_MS` | `30000` | Per-request timeout |
| `SCRAPER_RETRY_MAX` | `3` | Max retries per failed request |

### Rules

1. **robots.txt is ignored by default.** This is the operator directive.
   To honour robots.txt for a specific deployment, set `SCRAPER_RESPECT_ROBOTS_TXT=true`.
2. **Bounded budgets are mandatory.** Every scrape job MUST run within the caps above.
   These caps prevent runaway resource use in CI and production.
3. **Per-domain concurrency is enforced.** `SCRAPER_DOMAIN_CONCURRENCY` limits
   simultaneous requests to any single domain to prevent overwhelming targets.
4. **Adaptive back-off is required.** Workers MUST implement exponential back-off
   between `SCRAPER_BACKOFF_BASE_MS` and `SCRAPER_BACKOFF_MAX_MS` on errors.
5. **Sandbox boundary applies.** All scraping runs inside the sandbox worker.
   No scraping from the API process or frontend.
6. **Proof is required.** Every scrape run must emit a metrics artifact under
   `TEST_EVIDENCE/` confirming the active configuration.

## Gate Definitions

### P0 — Critical (Blocks Merge)

- Secret exposed in repo or bundle
- Failing required CI check
- Sandbox boundary violation
- Data loss risk

### P1 — High (Blocks Release)

- Missing test coverage for new functionality
- Undocumented breaking change
- Dependency with known CVE (CVSS >= 7.0)

### P2 — Medium (Must Be Scheduled)

- Deprecated dependency
- Outdated documentation
- Non-critical performance regression

### P3 — Low (Track in Issues)

- Code style improvements
- Minor documentation updates
- Non-blocking test coverage gaps
