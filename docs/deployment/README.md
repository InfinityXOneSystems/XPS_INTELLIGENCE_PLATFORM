# Deployment Documentation

## Overview

All services deploy to **Railway** via the `deploy-railway.yml` GitHub Actions workflow.

## Environments

| Environment | Trigger | Branch |
|-------------|---------|--------|
| Production | Push to `main` | `main` |
| Staging | Push to `develop` | `develop` |
| Manual | `workflow_dispatch` | Any |

## Railway Services

| Service | Name in Railway | Port |
|---------|----------------|------|
| Backend | `xps-backend` | 8000 |
| Frontend | `xps-frontend` | 3000 |

## Required Secrets (GitHub Actions)

```
RAILWAY_TOKEN     — Railway API token for deployments
BACKEND_URL       — Deployed backend URL (health check)
FRONTEND_URL      — Deployed frontend URL (health check)
GITGUARDIAN_API_KEY — GitGuardian API key for secret scanning
```

## Required Variables (Railway)

```
DATABASE_URL      — Railway Postgres connection string
REDIS_URL         — Railway Redis connection string
SECRET_KEY        — JWT signing secret (32+ random chars)
ENVIRONMENT       — "production" or "staging"
COPILOT_TOKEN     — GitHub Copilot token
GROQ_API_KEY      — Groq API key (secondary LLM)
```

## Deployment Flow

1. Code merged to `main` or `develop`
2. CI workflow runs (lint, test, build)
3. Security scan runs (CodeQL + GitGuardian)
4. If all pass → `deploy-railway.yml` triggered
5. Railway CLI deploys backend service
6. Health check gate: polls `/health` every 10s for 120s
7. Railway CLI deploys frontend service
8. Health check gate: polls `/` for 120s
9. `docs-sync.yml` updates CHANGELOG and README

## Rollback

Manual rollback via Railway dashboard or:
```bash
railway deployments list
railway deployments rollback <deployment-id>
```

## Database Migrations

Migrations run automatically on backend deploy via Alembic.
Manual migration: `./scripts/db-migrate.sh up`
