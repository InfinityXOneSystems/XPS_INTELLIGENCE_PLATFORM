# syntax=docker/dockerfile:1
# ============================================================================
# XPS Intelligence Platform — All-in-One Railway Deployment
# ============================================================================
#
# A single container that runs BOTH the FastAPI backend and the Next.js
# frontend, managed by supervisord.
#
# Port layout inside the container:
#   $PORT  (Railway-assigned) → Next.js  (public-facing, node server.js)
#   8000                       → FastAPI  (internal, localhost only)
#
# The Next.js server proxies every /api/v1/* request to FastAPI at
# http://127.0.0.1:8000 via the rewrites() config in next.config.js.
# The browser only ever talks to one origin — zero CORS complexity.
#
# External dependencies (Railway linked services):
#   DATABASE_URL → Railway Postgres  (auto-injected when service is linked)
#   REDIS_URL    → Railway Redis     (auto-injected when service is linked)
#
# ── Stage 1: Python dependencies ─────────────────────────────────────────────
FROM python:3.12-slim AS python-deps

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY apps/backend/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: Node dependencies ────────────────────────────────────────────────
FROM node:20-alpine AS node-deps

WORKDIR /app

COPY apps/frontend/package.json apps/frontend/package-lock.json ./
RUN npm ci

# ── Stage 3: Next.js build (standalone output) ────────────────────────────────
FROM node:20-alpine AS node-builder

WORKDIR /app

COPY --from=node-deps /app/node_modules ./node_modules
COPY apps/frontend/ .

# Ensure public/ directory exists for the multi-stage COPY
RUN mkdir -p public

# Build args for NEXT_PUBLIC_* vars baked into the browser bundle.
# In all-in-one mode: leave NEXT_PUBLIC_BACKEND_URL blank (the API is
# served from the same origin — the Next.js rewrite uses BACKEND_INTERNAL_URL
# which is set at RUNTIME by supervisord.conf, not at build time).
# In separate-services mode: set NEXT_PUBLIC_BACKEND_URL to the Railway
# backend URL so the CSP connect-src header includes it.
ARG NEXT_PUBLIC_BACKEND_URL=""
ARG NEXT_PUBLIC_LEGACY_DASHBOARD_URL=""
ARG NEXT_PUBLIC_LEGACY_DASHBOARD_MODE=iframe

ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}
ENV NEXT_PUBLIC_LEGACY_DASHBOARD_URL=${NEXT_PUBLIC_LEGACY_DASHBOARD_URL}
ENV NEXT_PUBLIC_LEGACY_DASHBOARD_MODE=${NEXT_PUBLIC_LEGACY_DASHBOARD_MODE}
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# ── Stage 4: All-in-one runtime ───────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    # PostgreSQL client library (required by asyncpg/psycopg2)
    libpq5 \
    # curl for Railway health checks
    curl \
    # Node.js for running the Next.js standalone server
    nodejs \
    # supervisord: manages multiple processes in one container
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Python packages from stage 1
COPY --from=python-deps /install /usr/local

# ── Copy application source ───────────────────────────────────────────────────
# Copy the full monorepo so that `from apps.backend.*` imports work.
COPY . .

# ── Copy the Next.js standalone output ───────────────────────────────────────
# The standalone server.js + traced node_modules live at
#   .next/standalone/  → we copy to apps/frontend/ so the path is:
#   /app/apps/frontend/server.js
# This matches the supervisord `command=node apps/frontend/server.js`.
COPY --from=node-builder /app/.next/standalone/ ./apps/frontend/

# Copy the compiled static chunks (CSS/JS bundles) and public/ assets.
# Next.js standalone server expects these alongside server.js.
COPY --from=node-builder /app/.next/static/ ./apps/frontend/.next/static/
COPY --from=node-builder /app/public/ ./apps/frontend/public/

# supervisord config
COPY supervisord.conf /etc/supervisor/conf.d/xps.conf

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    # Default internal ports; Railway overrides PORT at runtime
    PORT=3000 \
    LOG_LEVEL=info

EXPOSE 3000

# Health check — Railway polls this; it checks the Next.js server
# (which in turn means the backend is also reachable internally).
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -sf "http://localhost:${PORT:-3000}/" || exit 1

# supervisord starts both uvicorn (backend) and node (frontend).
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/xps.conf"]
