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
