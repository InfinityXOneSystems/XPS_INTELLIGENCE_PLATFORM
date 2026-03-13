# Repository Settings Baseline

> **Purpose:** Authoritative reference for the exact settings that MUST be enabled on
> `InfinityXOneSystems/XPS_INTELLIGENCE_PLATFORM`. Operators apply these settings manually
> (or via the `repo-self-audit` workflow) and verify them with the self-audit report.

---

## 1. Repository General Settings

| Setting | Required Value | Rationale |
| ------- | -------------- | --------- |
| Visibility | Private (or Public — owner decision) | Protect IP until deliberately released |
| Default branch | `main` | Single source of production truth |
| Delete branch on merge | ✅ Enabled | Keep branch list clean; reduces confusion |
| Allow squash merge | ✅ Enabled | Clean linear history |
| Allow merge commit | ❌ Disabled | Prevent cluttered history |
| Allow rebase merge | ✅ Enabled | Optional for contributor preference |
| Allow auto-merge | ✅ Enabled | Required for autonomous bot PRs |
| Automatically delete head branches | ✅ Enabled | Frictionless GitOps |
| Issues | ✅ Enabled | Bug tracking + feature requests |
| Projects | ✅ Enabled | Kanban visibility |
| Wiki | ❌ Disabled | Docs live in `_OPS/` — no scattered wikis |

---

## 2. Branch Protection Rules (default branch: `main`)

Navigate to: **Settings → Branches → Add rule**  
Branch name pattern: `main`

| Rule | Value |
| ---- | ----- |
| Require a pull request before merging | ✅ Enabled |
| Required approving reviews | **1** (minimum) |
| Dismiss stale pull request approvals | ✅ Enabled |
| Require review from Code Owners | ✅ Enabled (add `CODEOWNERS` file) |
| Require status checks to pass before merging | ✅ Enabled |
| Require branches to be up to date before merging | ✅ Enabled |
| Required status checks | See §5 below |
| Require conversation resolution before merging | ✅ Enabled |
| Require signed commits | ✅ Enabled (enforce on automation accounts) |
| Include administrators | ✅ Enabled |
| Restrict who can push | Owner + CI bot only |
| Allow force pushes | ❌ Disabled |
| Allow deletions | ❌ Disabled |

---

## 3. Environments

### `production`

| Setting | Value |
| ------- | ----- |
| Required reviewers | 1 human reviewer (repo owner) |
| Wait timer | 0 min (adjust if desired) |
| Deployment branches | `main` only |
| Secrets | `RAILWAY_TOKEN_PROD` |

### `staging`

| Setting | Value |
| ------- | ----- |
| Required reviewers | None (autonomous deploy allowed) |
| Deployment branches | `develop` |
| Secrets | `RAILWAY_TOKEN_STAGING` |

---

## 4. Labels to Create

Run the bootstrap script or create manually via **Issues → Labels**.

| Label | Color | Description |
| ----- | ----- | ----------- |
| `auto-merge` | `#0075ca` | Bot PRs eligible for autonomous merge |
| `governance` | `#e4e669` | Settings / compliance / policy changes |
| `forensic-audit` | `#d93f0b` | Audit and evidence collection PRs |
| `security` | `#b60205` | Security patches and hardening |
| `backend` | `#0e8a16` | Changes in `apps/backend/` |
| `frontend` | `#1d76db` | Changes in `apps/frontend/` |
| `ops` | `#5319e7` | `_OPS/` infrastructure changes |
| `documentation` | `#0075ca` | Docs-only changes |
| `dependencies` | `#cccccc` | Dependency bumps |
| `wontfix` | `#ffffff` | Deliberately not fixed |

---

## 5. Required Status Checks

The following checks MUST pass before merging to `main`:

| Check Name | Workflow / Source |
| ---------- | ----------------- |
| `lint-and-typecheck` | `.github/workflows/ci.yml` |
| `backend-tests` | `.github/workflows/ci.yml` |
| `frontend-build` | `.github/workflows/ci.yml` |
| `security-scan` | `.github/workflows/security.yml` |
| `repo-self-audit` | `.github/workflows/repo-self-audit.yml` |

> Add these incrementally as workflows are added. A check not yet in place cannot be required.

---

## 6. GitHub Actions Secrets Required

> ⚠️ **Never commit secret values.** All secrets are managed via GitHub Repository Secrets
> (Settings → Secrets and variables → Actions).

| Secret Name | Purpose |
| ----------- | ------- |
| `RAILWAY_TOKEN` | Railway deploy token (staging/prod) |
| `GROQ_API_KEY` | Groq LLM API key |
| `OPENAI_API_KEY` | OpenAI API key (optional fallback) |
| `AUDIT_PAT` | Fine-grained PAT for audit workflow (repo read + metadata) |

---

## 7. GitHub Actions Variables (Non-Secret Config)

| Variable Name | Purpose | Example Value |
| ------------- | ------- | ------------- |
| `RAILWAY_ENVIRONMENT` | Target Railway environment | `production` |
| `AUTONOMY_ENABLED` | Toggle autonomous agent actions | `true` |
| `SCRAPER_SCHEDULE_ENABLED` | Toggle 2-hour scraper cron | `true` |
| `AUDIT_OUTPUT_DIR` | Override audit output directory | `FORENSIC_AUDIT` |

---

## 8. CODEOWNERS

Create `.github/CODEOWNERS`:

```
# Global owner — must review all PRs
*                    @InfinityXOneSystems

# Governance and ops
/_OPS/               @InfinityXOneSystems
/.github/            @InfinityXOneSystems
/FORENSIC_AUDIT/     @InfinityXOneSystems
```

---

## 9. Verification

After applying all settings above, trigger a manual run of the self-audit workflow:

```
Actions → repo-self-audit → Run workflow
```

Review `FORENSIC_AUDIT/repo_settings_report.md` and confirm:
- Default branch is `main`
- Branch protection shows required checks active
- No unexpected open PRs
- Secrets list matches §6 above

---

*This document is the canonical settings baseline. Any deviation must be justified in a PR targeting `_OPS/RUNBOOK/`.*
