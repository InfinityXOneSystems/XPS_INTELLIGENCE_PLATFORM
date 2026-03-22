# Railway Environment Variable Contract

XPS Intelligence Platform — Railway Project ID: `139ef8de-840d-4110-aa21-fe3eeed7c469`

This document is the authoritative reference for all environment variables
required per service. It is maintained alongside `apps/backend/.env.example`.

> **Security Note:** Never commit `.env` files or real secret values. Use
> Railway's environment variable UI or the Railway CLI to set secrets.
> `DATABASE_URL` and `REDIS_URL` are injected automatically by Railway when
> the Postgres and Redis services are linked.
>
> **URL format handled automatically:** The backend auto-converts
> `postgres://` and `postgresql://` to `postgresql+asyncpg://` so you can
> use the URL exactly as Railway provides it — no manual editing required.

---

## Service: `xps-backend`

| Variable | Description | Default | Required | Notes |
|---|---|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | — | **Required** | Injected by Railway when Postgres service is linked. Any of `postgres://`, `postgresql://`, or `postgresql+asyncpg://` formats accepted. |
| `REDIS_URL` | Redis connection string | — | **Required** | Injected by Railway when Redis service is linked. Format: `redis://host:port` |
| `SECRET_KEY` | HMAC signing key for sessions/JWTs | — | **Required** | Generate with `openssl rand -hex 32`. Rotate on breach. |
| `CORS_ORIGINS` | JSON array of allowed CORS origins | `["http://localhost:3000"]` | **Required (prod)** | Must include the Railway frontend domain in production, e.g. `["https://xps-frontend.up.railway.app"]` |
| `LLM_PROVIDER` | Primary LLM backend | `groq` | Optional | Values: `groq`, `echo` (echo = no-op for testing) |
| `LLM_SECONDARY_PROVIDER` | Fallback LLM backend | `echo` | Optional | Used when primary provider is unavailable |
| `GROQ_API_KEY` | Groq API key | — | Optional | Required when `LLM_PROVIDER=groq`. Server-side only — never expose to frontend. |
| `AUTONOMY_ENABLED` | Enable 2-hour autonomy cycle | `false` | Optional | Set `true` in production after validating pipeline. |
| `SCRAPER_AUTORUN_ENABLED` | Enable scheduled scrape in autonomy cycle | `false` | Optional | Controlled at runtime via `/api/v1/scraper/settings`. |
| `SANDBOX_NETWORK_MODE` | Network isolation for code execution sandbox | `restricted` | Optional | Values: `restricted`, `open`. Keep `restricted` in production. |
| `OBJECT_STORAGE_ENDPOINT` | S3-compatible storage endpoint | `https://t3.storageapi.dev` | Optional | Required for image/file artifact storage. |
| `OBJECT_STORAGE_BUCKET` | Storage bucket name | `stocked-organizer-khf6nyu` | Optional | Pre-provisioned bucket. |
| `OBJECT_STORAGE_ACCESS_KEY` | Storage access key | — | Optional | Keep secret. |
| `OBJECT_STORAGE_SECRET_KEY` | Storage secret key | — | Optional | Keep secret. |
| `LOG_LEVEL` | Python log level | `INFO` | Optional | Values: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `PORT` | HTTP port | `8000` | Automatic | Set automatically by Railway. The app reads `$PORT` at runtime. |

---

## Service: `xps-frontend`

| Variable | Description | Default | Required | Notes |
|---|---|---|---|---|
| `NEXT_PUBLIC_BACKEND_URL` | Public URL of the `xps-backend` service | — | **Required** | Set to the Railway-generated domain for `xps-backend`, e.g. `https://xps-backend.up.railway.app`. Used by Next.js rewrites to proxy `/api/v1/*` to the backend AND in the CSP `connect-src` header. |
| `NEXT_PUBLIC_LEGACY_DASHBOARD_URL` | URL of the legacy GitHub Pages dashboard | `https://infinityxonesystems.github.io/XPS_INTELLIGENCE_SYSTEM/` | Optional | Override to use a custom deployment. |
| `NEXT_PUBLIC_LEGACY_DASHBOARD_MODE` | Dashboard mode | `iframe` | Optional | Values: `iframe` (safe default), `native` (when parity achieved). |
| `PORT` | HTTP port | `3000` | Automatic | Set automatically by Railway. |

> **Rule:** No `VITE_*KEY*`, `VITE_*SECRET*`, `VITE_*TOKEN*` variables are
> permitted. All secrets must remain server-side only. The CI `check-no-vite-secrets`
> job enforces this automatically.

---

## Service: `xps-worker-default`

| Variable | Description | Default | Required | Notes |
|---|---|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | — | **Required** | Same as backend — link the same Postgres service. Any URL format accepted. |
| `REDIS_URL` | Redis connection string | — | **Required** | Same as backend — link the same Redis service. |
| `LOG_LEVEL` | Log level | `INFO` | Optional | |

---

## Provisioned Infrastructure (Railway)

| Resource | Host | Port | TCP Proxy | Notes |
|---|---|---|---|---|
| **Postgres** | `postgres-production-5596.up.railway.app` | `5432` | `junction.proxy.rlwy.net:42332` | Link to all services that need DB |
| **Redis** | `redis-production-200b.up.railway.app` | `6379` | `tramway.proxy.rlwy.net:22806` | Link to backend and workers |
| **Object Storage** | `https://t3.storageapi.dev` | — | — | Bucket: `stocked-organizer-khf6nyu` |

---

## GitHub Actions Secrets Required

Set these in GitHub → Settings → Environments → `production` (and `staging`):

| Secret | Used By | Description |
|---|---|---|
| `RAILWAY_TOKEN` | `deploy-railway.yml` | Railway deploy token. Scoped to project `139ef8de-840d-4110-aa21-fe3eeed7c469`. |
| `DATABASE_URL` | `deploy-railway.yml` (migrate-db job) | Railway Postgres URL (any format). Used to run Alembic migrations before deploy. |
| `BACKEND_URL` | `deploy-railway.yml`, `autonomy-scheduler.yml` | Public HTTPS URL of deployed backend (e.g. `https://xps-backend.up.railway.app`). |
| `FRONTEND_URL` | `deploy-railway.yml` | Public HTTPS URL of deployed frontend. |
| `AUTONOMY_TOKEN` | `autonomy-scheduler.yml` | Bearer token for `/api/v1/autonomy/cycle`. |

---

## Quick-Start Checklist (first Railway deploy)

1. In Railway dashboard, link Postgres service to `xps-backend` and `xps-worker-default`
2. In Railway dashboard, link Redis service to `xps-backend` and `xps-worker-default`
3. Set `SECRET_KEY` on `xps-backend`: `openssl rand -hex 32`
4. Set `CORS_ORIGINS` on `xps-backend`: `["https://<your-frontend>.up.railway.app"]`
5. Set `NEXT_PUBLIC_BACKEND_URL` on `xps-frontend`: `https://<your-backend>.up.railway.app`
6. Add `RAILWAY_TOKEN` and `DATABASE_URL` to GitHub environment secrets
7. Push to `main` — the workflow runs migrations then deploys all services
