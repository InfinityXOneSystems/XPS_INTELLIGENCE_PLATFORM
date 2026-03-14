# syntax=docker/dockerfile:1
# XPS Intelligence Frontend — Multi-stage Docker build for Railway.
#
# Build context: repo root (all `COPY` paths are relative to the repository
# root directory, which Railway sends as the Docker build context).
#
# Stages:
#   deps    — install Node deps
#   builder — run `next build` (standalone output)
#   runner  — minimal production image (no npm, no dev deps)

# ── Stage 1: Install dependencies ────────────────────────────────────────────
FROM node:20-alpine AS deps

WORKDIR /app

COPY apps/frontend/package.json apps/frontend/package-lock.json ./
RUN npm ci

# ── Stage 2: Build the Next.js app ───────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
# Copy the frontend source into /app (repo-root build context, paths prefixed)
COPY apps/frontend/ .

# Ensure public/ exists — Next.js requires this for the standalone COPY even
# when the app has no user-facing static assets.
RUN mkdir -p public

# Build-time environment variables (NEXT_PUBLIC_* are baked into the bundle).
# Railway re-exports env vars as Docker build args when using DOCKERFILE builder.
ARG NEXT_PUBLIC_BACKEND_URL
ARG NEXT_PUBLIC_LEGACY_DASHBOARD_URL
ARG NEXT_PUBLIC_LEGACY_DASHBOARD_MODE=iframe

ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}
ENV NEXT_PUBLIC_LEGACY_DASHBOARD_URL=${NEXT_PUBLIC_LEGACY_DASHBOARD_URL}
ENV NEXT_PUBLIC_LEGACY_DASHBOARD_MODE=${NEXT_PUBLIC_LEGACY_DASHBOARD_MODE}
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# ── Stage 3: Minimal production runner ───────────────────────────────────────
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create a non-root user for security
RUN addgroup --system --gid 1001 nodejs \
 && adduser  --system --uid 1001 nextjs

# public/ must be in place before the standalone server starts so Next.js can
# serve user-facing static assets from the correct path.
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

RUN mkdir -p .next && chown nextjs:nodejs .next

# Copy the standalone server (server.js + traced node_modules) and compiled
# static chunks produced by `output: 'standalone'`.
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# `output: 'standalone'` in next.config.js generates server.js at WORKDIR.
# Using exec form — no shell, no npm, no extra process overhead.
CMD ["node", "server.js"]
