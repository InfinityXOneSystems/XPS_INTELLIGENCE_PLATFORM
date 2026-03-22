# Operator Runbook — XPS Intelligence Platform

This runbook documents all operator actions required to maintain and operate
the XPS Intelligence Platform in "approve-only" mode. Human operators approve
PRs and manage secrets; all other work is automated.

## Normal Operation

As an operator, your standard workflow is:

1. Review automated PRs opened by CI/CD agents.
2. Check that all required status checks pass.
3. Review the PR diff and TAP compliance checklist.
4. Approve and merge (or let auto-merge handle eligible PRs).
5. Monitor Railway deployment logs after merge to `main`.

You do **not** need to manually run scripts, deploy, or trigger tests for
normal operation.

## Required Branch Protections

Configure these settings on the `main` branch in
**Settings → Branches → Branch protection rules → main**:

| Setting | Required Value |
|---|---|
| Require a pull request before merging | Enabled |
| Required approving reviews | 1 minimum |
| Dismiss stale pull request approvals when new commits are pushed | Enabled |
| Require status checks to pass before merging | Enabled |
| Required status checks | `CI / Lint Markdown`, `CI / Lint YAML`, `CI / Check Repo Structure`, `CI / Check No VITE_ Secrets` |
| Require branches to be up to date before merging | Enabled |
| Require conversation resolution before merging | Enabled |
| Do not allow bypassing the above settings | Enabled |
| Allow auto-merge | Enabled (for automation) |
| Automatically delete head branches | Enabled |

## Required Repository Settings

Configure in **Settings → General**:

| Setting | Required Value |
|---|---|
| Default branch | `main` |
| Allow squash merging | Enabled |
| Allow merge commits | Disabled |
| Allow rebase merging | Disabled |
| Always suggest updating pull request branches | Enabled |
| Automatically delete head branches | Enabled |

## Required Environments

Configure in **Settings → Environments**:

### Environment: `production`

- **Deployment branches:** `main` only
- **Required reviewers:** 1 operator reviewer (your GitHub user)
- **Environment secrets:**
  - `RAILWAY_TOKEN` — Railway API token for production deploys
  - `GROQ_API_KEY` — Groq LLM API key
  - `DATABASE_URL` — PostgreSQL connection string (Railway-managed)
  - `REDIS_URL` — Redis connection string (Railway-managed)

### Environment: `staging`

- **Deployment branches:** `develop` only
- **Environment secrets:** (same as production, pointing to staging services)

## Railway Configuration

### Services

Deploy these Railway services from this repository:

| Service name | Railway service type | Start command |
|---|---|---|
| `api` | Web service | `cd apps/backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| `worker-default` | Worker | `cd apps/backend && python -m app.workers.worker_pool` |
| `worker-playwright` | Worker | `cd apps/backend && python -m app.workers.playwright_worker` |
| `sandbox-runner` | Worker | `cd apps/backend && python -m app.workers.sandbox_runner` |

### Required Railway Environment Variables

Set these in Railway project → Variables for each service:

```text
DATABASE_URL=<railway-postgres-connection-string>
REDIS_URL=<railway-redis-connection-string>
GROQ_API_KEY=<your-groq-api-key>
LLM_PROVIDER=groq
SCRAPER_ENABLED=true
SCRAPER_RESPECT_ROBOTS_TXT=true
SCRAPER_MAX_REQUESTS_PER_RUN=200
SCRAPER_MAX_CONCURRENCY=3
SCRAPER_MIN_DELAY_MS=1000
SCRAPER_COMPLIANCE_MODE=true
AUTONOMY_ENABLED=true
ENVIRONMENT=production
```

## Shadow Scraper Operation

### Overview

The Shadow Scraper is the primary ingestion method. It uses a headless Playwright
browser with anti-bot evasion, user-agent rotation, and configurable delays.
No domain allowlist is required; a denylist model is used instead.

### Safety Rail Configuration

All safety rail defaults live in `packages/agents/scraper_config.json`.
Override at runtime via Railway environment variables:

| Variable | Default | Description |
|---|---|---|
| `SCRAPER_RESPECT_ROBOTS_TXT` | `true` | Respect robots.txt directives |
| `SCRAPER_MAX_REQUESTS_PER_RUN` | `200` | Hard stop after N HTTP requests per run |
| `SCRAPER_MAX_CONCURRENCY` | `3` | Max parallel Playwright pages |
| `SCRAPER_MIN_DELAY_MS` | `1000` | Min ms between requests to the same domain |
| `SCRAPER_COMPLIANCE_MODE` | `true` | Doubles all delay floors; stricter rate limiting |

### Managing the Domain Denylist

To block a domain permanently:

1. Edit `packages/agents/scraper_config.json` → add to the `denylist` array.
2. Open a PR. The change takes effect after merge to `main`.

Denylist entries accept exact hostnames (e.g., `"example.com"`) or wildcard
subdomains prefixed with `*.` (e.g., `"*.private-corp.internal"`).

### Running a Manual Scrape

1. Navigate to **Actions → Shadow Scraper Proof** → **Run workflow**.
2. Optionally set `target_urls` input (newline-separated URLs).
3. Leave blank to use the default deterministic target set in the workflow.
4. Review the uploaded `shadow-scraper-proof-*` artifact for run results.

### 2-Hour Autonomy Cycle

The `audit.yml` schedule triggers the scrape cycle every 2 hours. The run is
idempotent: duplicate URLs are deduplicated by content hash at ingest time.
If `SCRAPER_MAX_REQUESTS_PER_RUN` is reached, the run stops cleanly and
commits partial results. No data is lost.

### Disabling the Scraper

- Immediate stop: set `SCRAPER_ENABLED=false` in Railway → all services.
- Full disable: also disable the 2-hour schedule in GitHub Actions.

## Emergency Procedures

### Stop All Automation

To halt all autonomous operations immediately:

1. In Railway: set `AUTONOMY_ENABLED=false` on all services.
2. In GitHub: go to **Actions → Workflows** and disable `audit.yml`.
3. In GitHub: disable the 2-hour scheduled workflow trigger.

Services will continue serving traffic but no background scraping or agent
tasks will execute.

### Rotate Secrets

1. Generate new credentials from the provider (Railway, Groq, etc.).
2. Update the GitHub Environment secret and the Railway variable in the same
   session.
3. Trigger a manual deployment to pick up the new credentials.
4. Verify the service health endpoint responds correctly.
5. Revoke the old credentials.

### Rollback a Deployment

1. In Railway: use the **Deployments** panel to revert to a previous build.
2. In GitHub: open a PR that reverts the offending commit on `main`.
3. CI will run, and Railway auto-deploys the reverted build after merge.

## Verification Procedure (Before Approving a Release PR)

Run through this checklist before approving any release candidate:

- [ ] All required CI status checks are green.
- [ ] `FORENSIC_AUDIT/repo_settings_report.json` shows `"status": "PASS"`.
- [ ] `TEST_EVIDENCE/` contains the latest Playwright snapshot artifacts.
- [ ] No open P0 or P1 issues in the repository.
- [ ] Railway staging deployment is healthy (`/health` endpoint returns 200).
- [ ] No new secrets exposed in the diff (CI secret scan passed).

## Audit Reports

The `audit.yml` workflow generates reports on every run and uploads them as
GitHub Actions artifacts. To review:

1. Go to **Actions → Audit → latest run**.
2. Download the `forensic-audit-report` artifact.
3. Review `repo_settings_report.json` for compliance gaps.

For historical reports, check the Actions artifact retention (default: 30 days).

## Troubleshooting

### CI fails on "Check Repo Structure"

A required governance file is missing. Check which file is reported missing
and ensure the branch contains it. All files listed in
`_OPS/ARCHITECTURE/SYSTEM_TOPOLOGY.md` under "Repository Layout" are required.

### CI fails on "Check No VITE_ Secrets"

A file in the repository contains a pattern matching `VITE_` followed by a
secret-like name and value. Locate the file from the CI output, remove the
hardcoded secret, and replace it with an environment variable reference.

### Audit workflow fails with API 403

The `GITHUB_TOKEN` in the audit workflow does not have sufficient permissions
to read branch protection settings. This is expected on repositories where
the token has only `contents: read`. The audit will still produce a report
noting that branch protection could not be verified — configure branch
protection manually per the settings above.

### Railway deploy fails

Check Railway build logs. Common causes:

- Missing environment variable (check the required variables list above).
- Application startup error (check `apps/backend` startup logs).
- Database migration pending (run `alembic upgrade head` as a one-off job).
