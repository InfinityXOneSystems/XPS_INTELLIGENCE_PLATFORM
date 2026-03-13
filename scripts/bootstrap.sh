#!/usr/bin/env bash
# XPS Intelligence Platform — Bootstrap Script
# Installs all workspace dependencies for local development
# Usage: ./scripts/bootstrap.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "🚀 XPS Intelligence Platform Bootstrap"
echo "======================================="

# ── Check prerequisites ────────────────────────────────────────────────────
check_cmd() {
  if ! command -v "$1" &>/dev/null; then
    echo "❌ Required tool not found: $1"
    echo "   Please install $1 and re-run this script."
    exit 1
  fi
  echo "✅ $1 found: $(command -v "$1")"
}

echo ""
echo "Checking prerequisites..."
check_cmd git
check_cmd python3
check_cmd pip
check_cmd node
check_cmd npm

# ── Python backend ─────────────────────────────────────────────────────────
if [[ -f "apps/backend/pyproject.toml" ]]; then
  echo ""
  echo "📦 Installing backend Python dependencies..."
  cd apps/backend
  pip install --upgrade pip
  pip install -e ".[dev]"
  cd "$REPO_ROOT"
  echo "✅ Backend dependencies installed"
else
  echo "⚠️  No apps/backend/pyproject.toml yet — skipping backend install"
fi

# ── Frontend ───────────────────────────────────────────────────────────────
if [[ -f "apps/frontend/package.json" ]]; then
  echo ""
  echo "📦 Installing frontend npm dependencies..."
  cd apps/frontend
  npm ci
  cd "$REPO_ROOT"
  echo "✅ Frontend dependencies installed"
else
  echo "⚠️  No apps/frontend/package.json yet — skipping frontend install"
fi

# ── Root / shared ──────────────────────────────────────────────────────────
if [[ -f "package.json" ]]; then
  echo ""
  echo "📦 Installing root npm dependencies..."
  npm ci
  echo "✅ Root dependencies installed"
fi

if [[ -f "packages/shared/package.json" ]]; then
  echo ""
  echo "📦 Installing shared package dependencies..."
  cd packages/shared
  npm ci
  cd "$REPO_ROOT"
  echo "✅ Shared dependencies installed"
fi

# ── Playwright ────────────────────────────────────────────────────────────
echo ""
echo "🎭 Installing Playwright browsers..."
if command -v npx &>/dev/null; then
          npx playwright install --with-deps chromium 2>/dev/null || echo "⚠️  Playwright browser installation skipped (Playwright may not be fully configured yet)"
fi

# ── Pre-commit hooks ──────────────────────────────────────────────────────
if command -v pre-commit &>/dev/null && [[ -f ".pre-commit-config.yaml" ]]; then
  echo ""
  echo "🪝 Installing pre-commit hooks..."
  pre-commit install
  echo "✅ Pre-commit hooks installed"
fi

echo ""
echo "✅ Bootstrap complete!"
echo ""
echo "Next steps:"
echo "  ./scripts/dev.sh        — Start local development environment"
echo "  ./scripts/db-migrate.sh — Run database migrations"
