#!/usr/bin/env bash
# XPS Intelligence Platform — Railway Service Setup
# Run this ONCE to create services in your Railway project.
# Project ID: 139ef8de-840d-4110-aa21-fe3eeed7c469
# This is idempotent: existing services are not recreated.

set -euo pipefail

RAILWAY_PROJECT_ID="139ef8de-840d-4110-aa21-fe3eeed7c469"

echo "=== XPS Intelligence Platform — Railway Setup ==="
echo "Project ID: ${RAILWAY_PROJECT_ID}"
echo ""
echo "Prerequisites:"
echo "  1. Install Railway CLI: npm install -g @railway/cli"
echo "  2. Login: railway login"
echo "  3. Link project: railway link ${RAILWAY_PROJECT_ID}"
echo ""
echo "Services to create (run manually or via Railway dashboard):"
echo "  - xps-backend      (apps/backend/)"
echo "  - xps-frontend     (apps/frontend/)"
echo "  - xps-worker-default (apps/workers/default/)"
echo ""
echo "Required environment variables per service:"
echo "  xps-backend:       DATABASE_URL, REDIS_URL, SECRET_KEY, LLM_PROVIDER, GROQ_API_KEY,"
echo "                     AUTONOMY_ENABLED, SCRAPER_AUTORUN_ENABLED, SANDBOX_NETWORK_MODE,"
echo "                     OBJECT_STORAGE_ENDPOINT, OBJECT_STORAGE_BUCKET,"
echo "                     OBJECT_STORAGE_ACCESS_KEY, OBJECT_STORAGE_SECRET_KEY"
echo "  xps-worker-default: DATABASE_URL, REDIS_URL"
echo "  xps-frontend:      NEXT_PUBLIC_BACKEND_URL (= Railway xps-backend domain)"
echo ""
echo "Railway Postgres (already provisioned):"
echo "  Domain: postgres-production-5596.up.railway.app:5432"
echo "  TCP Proxy: junction.proxy.rlwy.net:42332"
echo ""
echo "Railway Redis (already provisioned):"
echo "  Proxy: tramway.proxy.rlwy.net:22806"
echo "  Domain: redis-production-200b.up.railway.app:6379"
echo ""
echo "Object Storage:"
echo "  Endpoint: https://t3.storageapi.dev"
echo "  Bucket: stocked-organizer-khf6nyu"
