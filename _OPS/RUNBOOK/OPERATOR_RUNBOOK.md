# Operator Runbook

> **Audience:** Repository owners and platform operators.  
> **Mode:** Approve-only. All automation is hands-off; humans approve PRs and monitor.

---

## Table of Contents

1. [Normal Operation](#1-normal-operation)
2. [Apply Settings Checklist](#2-apply-settings-checklist)
3. [Verify Settings](#3-verify-settings)
4. [Emergency Stop](#4-emergency-stop)
5. [Runbook Scenarios](#5-runbook-scenarios)
6. [Escalation](#6-escalation)

---

## 1. Normal Operation

| Interval | Automated Action |
| -------- | ---------------- |
| Every push / PR | CI runs lint, typecheck, tests, security scan |
| Every merge to `main` | Railway deploys backend + workers |
| Every 2 hours (when `SCRAPER_SCHEDULE_ENABLED=true`) | Shadow scraper ingests + normalises + scores leads |
| Weekly (Sundays 02:00 UTC) | Repository self-audit runs; report committed + artifact uploaded |
| On demand | Trigger any workflow from Actions tab |

**Your only required actions:**
- Review and approve (or reject) PRs raised by the autonomous bot.
- Monitor the FORENSIC_AUDIT reports for compliance drift.
- Rotate secrets when prompted by the security workflow.

---

## 2. Apply Settings Checklist

Use this checklist when bootstrapping a fresh repo or recovering from a settings reset.

### 2.1 Repository General Settings

Navigate to: **Settings → General**

- [ ] Default branch set to `main`
- [ ] Delete branch on merge → **Enabled**
- [ ] Allow squash merge → **Enabled**
- [ ] Allow merge commit → **Disabled**
- [ ] Allow rebase merge → **Enabled**
- [ ] Allow auto-merge → **Enabled**
- [ ] Automatically delete head branches → **Enabled**
- [ ] Issues → **Enabled**
- [ ] Projects → **Enabled**
- [ ] Wiki → **Disabled**

### 2.2 Branch Protection for `main`

Navigate to: **Settings → Branches → Add rule** (pattern: `main`)

- [ ] Require a pull request before merging → **Enabled**
- [ ] Required approving review count → **1**
- [ ] Dismiss stale reviews → **Enabled**
- [ ] Require review from Code Owners → **Enabled** (requires `.github/CODEOWNERS`)
- [ ] Require status checks to pass before merging → **Enabled**
  - [ ] Add check: `lint-and-typecheck`
  - [ ] Add check: `backend-tests`
  - [ ] Add check: `frontend-build`
  - [ ] Add check: `security-scan`
  - [ ] Add check: `repo-self-audit`
- [ ] Require branches to be up to date → **Enabled**
- [ ] Require conversation resolution before merging → **Enabled**
- [ ] Require signed commits → **Enabled**
- [ ] Include administrators → **Enabled**
- [ ] Allow force pushes → **Disabled**
- [ ] Allow deletions → **Disabled**

### 2.3 Environments

Navigate to: **Settings → Environments**

- [ ] Create environment: `production`
  - [ ] Required reviewers: repo owner
  - [ ] Deployment branches: `main` only
  - [ ] Add secret: `RAILWAY_TOKEN_PROD`
- [ ] Create environment: `staging`
  - [ ] Deployment branches: `develop`
  - [ ] Add secret: `RAILWAY_TOKEN_STAGING`

### 2.4 Secrets and Variables

Navigate to: **Settings → Secrets and variables → Actions**

**Repository secrets:**
- [ ] `RAILWAY_TOKEN`
- [ ] `GROQ_API_KEY`
- [ ] `OPENAI_API_KEY` (optional)
- [ ] `AUDIT_PAT` (fine-grained PAT: repo read + metadata)

**Repository variables:**
- [ ] `RAILWAY_ENVIRONMENT` = `production`
- [ ] `AUTONOMY_ENABLED` = `true`
- [ ] `SCRAPER_SCHEDULE_ENABLED` = `true`
- [ ] `AUDIT_OUTPUT_DIR` = `FORENSIC_AUDIT`

### 2.5 Labels

Navigate to: **Issues → Labels → New label** (or use GitHub CLI):

```bash
gh label create "auto-merge"      --color "#0075ca" --description "Bot PRs eligible for autonomous merge"
gh label create "governance"      --color "#e4e669" --description "Settings / compliance / policy changes"
gh label create "forensic-audit"  --color "#d93f0b" --description "Audit and evidence collection PRs"
gh label create "security"        --color "#b60205" --description "Security patches and hardening"
gh label create "backend"         --color "#0e8a16" --description "Changes in apps/backend/"
gh label create "frontend"        --color "#1d76db" --description "Changes in apps/frontend/"
gh label create "ops"             --color "#5319e7" --description "_OPS/ infrastructure changes"
gh label create "documentation"   --color "#0075ca" --description "Docs-only changes"
gh label create "dependencies"    --color "#cccccc" --description "Dependency bumps"
```

### 2.6 CODEOWNERS

Ensure `.github/CODEOWNERS` exists:

```
*                    @InfinityXOneSystems
/_OPS/               @InfinityXOneSystems
/.github/            @InfinityXOneSystems
/FORENSIC_AUDIT/     @InfinityXOneSystems
```

---

## 3. Verify Settings

### 3.1 Trigger the Self-Audit Workflow

```
Actions → repo-self-audit → Run workflow (branch: main)
```

Wait for the workflow to complete, then review:

- [ ] Workflow status: **green**
- [ ] Artifact `repo-settings-report` uploaded
- [ ] `FORENSIC_AUDIT/repo_settings_report.md` committed with current timestamp

### 3.2 Review the Report

Open `FORENSIC_AUDIT/repo_settings_report.md` and verify:

- [ ] `Default branch` = `main`
- [ ] Branch protection for `main` is active (no ⚠️ on protection section)
- [ ] Required status checks list matches §2.2 above
- [ ] Environments `production` and `staging` listed
- [ ] Secrets section lists all required secrets (names only — values never shown)
- [ ] No unexpected open PRs

### 3.3 Confirm Branch Protection via CLI

```bash
gh api repos/InfinityXOneSystems/XPS_INTELLIGENCE_PLATFORM/branches/main/protection \
  --jq '{enforce_admins: .enforce_admins.enabled, required_reviews: .required_pull_request_reviews.required_approving_review_count}'
```

Expected output:
```json
{
  "enforce_admins": true,
  "required_reviews": 1
}
```

---

## 4. Emergency Stop

### 4.1 Disable Autonomous Scheduling

1. Go to **Settings → Secrets and variables → Actions → Variables**
2. Set `AUTONOMY_ENABLED` = `false`
3. Set `SCRAPER_SCHEDULE_ENABLED` = `false`

All scheduled workflows check these variables before running.

### 4.2 Disable a Workflow Entirely

```bash
gh workflow disable <workflow-name>
```

Or via: **Actions → \<workflow\> → ... → Disable workflow**

### 4.3 Rotate a Compromised Secret

1. **Immediately** revoke the compromised credential at the source (Railway, Groq, etc.)
2. Issue new credential
3. Update via: **Settings → Secrets and variables → Actions → \<SECRET_NAME\> → Update**
4. Trigger a new deployment to confirm the new secret is effective

---

## 5. Runbook Scenarios

### A. Self-audit report shows ⚠️ unavailable for branch protection

**Cause:** The `AUDIT_PAT` token lacks `admin:repo_hook` or `repo` scope, or branch protection
is not yet configured.  
**Resolution:**
1. Apply branch protection per §2.2.
2. Re-generate `AUDIT_PAT` with `repo` scope (read-only sufficient for audit).
3. Re-run the self-audit workflow.

### B. Workflow fails with `GITHUB_TOKEN` permission error

**Cause:** The workflow's `contents: write` permission is blocked by repo settings.  
**Resolution:** Verify **Settings → Actions → General → Workflow permissions** is set to
"Read and write permissions".

### C. No artifacts uploaded from self-audit run

**Cause:** The `upload-artifact` step failed, or the report files were not generated.  
**Check:** Expand the "Upload reports as artifacts" step in the Actions log.  
**Resolution:** Ensure `FORENSIC_AUDIT/` directory exists in repo and `AUDIT_PAT` is valid.

### D. Railway deploy fails after merge to `main`

**Cause:** `RAILWAY_TOKEN` is expired or the Railway service config changed.  
**Resolution:**
1. Check Railway dashboard for the service status.
2. Rotate `RAILWAY_TOKEN` per §4.3.
3. Re-run the deploy workflow manually from Actions.

---

## 6. Escalation

| Severity | Who | Channel |
| -------- | --- | ------- |
| P0 — production down | Repo owner | Direct |
| P1 — security incident | Repo owner + GitHub Security Advisories | Private advisory |
| P2 — audit drift | Repo owner | PR comment / issue |
| P3 — non-critical CI flake | Bot auto-retry + owner review | GitHub issue |

---

*This runbook is auto-linked from `.github/copilot-instructions.md` and REPO_SETTINGS_BASELINE.md.*
