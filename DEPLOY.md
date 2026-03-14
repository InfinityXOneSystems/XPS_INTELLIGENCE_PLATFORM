# XPS Intelligence Platform — Railway Deployment Guide

Deploy the entire XPS Intelligence Platform to Railway in minutes.
One service, one container, fully automated.

---

## Architecture

```text
Railway Project
├── xps-app          ← Single all-in-one service (this guide)
│   ├── Next.js frontend   (port $PORT — public)
│   └── FastAPI backend    (port 8000 — internal only)
├── Postgres         ← Railway managed (link to xps-app)
└── Redis            ← Railway managed (link to xps-app)
```

The Next.js server handles all browser traffic. Requests to `/api/v1/*`
are transparently proxied to the FastAPI process running on the same
container — no CORS, no separate backend URL needed.

---

## Prerequisites

- A [Railway](https://railway.app) account
- The Railway CLI: `npm install -g @railway/cli`
- This repo pushed to GitHub (it already is)

---

## One-Time Setup (do this once)

### 1 · Create a Railway project

```bash
railway login
railway init       # choose "Empty project", name it "XPS Intelligence"
```

### 2 · Provision Postgres

In the Railway dashboard → **New** → **Database** → **PostgreSQL**.
Name it `postgres`. Railway injects `DATABASE_URL` automatically.

### 3 · Provision Redis

In the Railway dashboard → **New** → **Database** → **Redis**.
Name it `redis`. Railway injects `REDIS_URL` automatically.

### 4 · Create the app service

```bash
railway service create xps-app
```

### 5 · Link Postgres and Redis to the app service

In Railway dashboard → **xps-app** → **Variables** → click
**"Reference another service's variable"**:

- Add `DATABASE_URL` from the `postgres` service
- Add `REDIS_URL` from the `redis` service

### 6 · Set required environment variables

In Railway dashboard → **xps-app** → **Variables**, add:

| Variable | Value | Notes |
|---|---|---|
| `SECRET_KEY` | output of `openssl rand -hex 32` | **Required** |
| `GROQ_API_KEY` | your Groq API key | Optional (enables AI chat) |
| `AUTONOMY_ENABLED` | `false` | Enable after testing |
| `SCRAPER_AUTORUN_ENABLED` | `false` | Enable after testing |
| `LOG_LEVEL` | `INFO` | Or `DEBUG` during testing |

You do **NOT** need to set `NEXT_PUBLIC_BACKEND_URL` — the frontend
and backend run in the same container and communicate internally.

### 7 · Add GitHub secrets

In GitHub → **Settings** → **Environments** → `production`:

| Secret | Value |
|---|---|
| `RAILWAY_TOKEN` | From Railway → Account Settings → Tokens |
| `DATABASE_URL` | Copy from Railway postgres service variables |
| `APP_URL` | Your Railway app URL (e.g. `https://xps-app.up.railway.app`) |

---

## Deploy

### Automatic (every push to `main`)

The GitHub Actions workflow (`.github/workflows/deploy-railway.yml`)
automatically:

1. Runs `alembic upgrade head` to apply any new DB migrations
2. Deploys the all-in-one container to Railway
3. Polls the health check until the service is up

Just push to `main`:

```bash
git push origin main
```

### Manual (from CLI)

```bash
# Run migrations first
DATABASE_URL="<your-railway-postgres-url>" \
  cd apps/backend && alembic upgrade head

# Deploy the app
railway up --service xps-app
```

---

## Verify it's working

Once deployed, open your Railway app URL (e.g.
`https://xps-app.up.railway.app`).

| URL | Expected |
|---|---|
| `/` | Redirects to `/legacy-dashboard` |
| `/legacy-dashboard` | Renders the XPS Intelligence dashboard |
| `/workspace` | AI workspace with artifact panels |
| `/scraper` | Scraper job settings + management |
| `/api/v1/health` | `{"status":"ok","checks":{"database":"ok","redis":"ok"}}` |
| `/api/v1/leads` | `{"leads":[],"total":0}` |

The `/api/v1/health` response is the authoritative status check. If
`database` or `redis` show `"unavailable"`, double-check that the
Postgres and Redis services are linked in the Railway dashboard.

---

## Local development

```bash
# 1. Copy env template
cp .env.example .env
# Fill in real DATABASE_URL, REDIS_URL, SECRET_KEY

# 2. Start everything
./scripts/dev.sh
# Backend:  http://localhost:8000
# Frontend: http://localhost:3000

# 3. Run backend tests
python -m pytest apps/backend/tests/ -v

# 4. Run frontend type-check + lint
cd apps/frontend && npm run type-check && npm run lint
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `{"status":"degraded","checks":{"database":"unavailable"}}` | Link Postgres to xps-app in Railway dashboard |
| `{"status":"degraded","checks":{"redis":"unavailable"}}` | Link Redis to xps-app in Railway dashboard |
| Container crash loop | Check Railway logs; run `railway logs --service xps-app` |
| `alembic: command not found` in CI | Ensure `DATABASE_URL` secret is set in the GitHub environment |
| API calls return 404 | Confirm `BACKEND_INTERNAL_URL` is set in `supervisord.conf` (it is) |

---

## Upgrade path

When you're ready to scale:

- **Scale the backend independently**: split into separate `xps-backend`
  and `xps-frontend` services using the per-service `railway.json` files
  in `apps/backend/` and `apps/frontend/`.
- **Add the Celery worker**: deploy `apps/workers/default/` as a
  separate `xps-worker-default` service.
- All three per-service configs are already committed and ready to use.
