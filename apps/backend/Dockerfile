# syntax=docker/dockerfile:1

# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY apps/backend/requirements.txt ./requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    # playwright system deps
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libdbus-1-3 libxkbcommon0 libx11-6 libxcomposite1 \
    libxdamage1 libxext6 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 \
    libcairo2 libasound2 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

# Copy entire repo so monorepo imports work
COPY . .

# Install playwright browsers only when INSTALL_PLAYWRIGHT=true
# The backend itself does not run browsers; the playwright worker does.
# Set INSTALL_PLAYWRIGHT=true in the playwright worker image, not here.
RUN if [ "${INSTALL_PLAYWRIGHT:-false}" = "true" ]; then \
        python -m playwright install chromium --with-deps; \
    fi

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PORT=8000

EXPOSE 8000

# Shell form so Railway's $PORT env var is interpolated at runtime
CMD uvicorn apps.backend.main:app --host 0.0.0.0 --port "${PORT:-8000}"
