# XPS Intelligence Platform — Workers

This directory contains the three worker types that power background processing.

## Worker Types

### 1. `default/` — Celery Worker
General-purpose task queue powered by [Celery](https://docs.celeryq.dev/) and Redis as the broker.

**Tasks:**
| Task | Description |
|------|-------------|
| `run_scrape_job` | Fetches a URL, extracts leads with BeautifulSoup, persists Lead records |
| `run_ingest_pipeline` | Ingests raw records for a given scrape job |
| `run_normalize_batch` | Normalizes a batch of leads (extracts email, phone, company, etc.) |
| `run_score_batch` | Scores a batch of normalized leads (0.0–1.0 completeness) |

**Start:**
```bash
celery -A apps.workers.default.worker worker --loglevel=info
```

---

### 2. `playwright/` — Browser Scraping Worker
Headless Chromium scraping via [Playwright](https://playwright.dev/python/).

**Capabilities:**
- JavaScript-rendered page scraping
- Screenshot capture (base64)
- Structured lead extraction using CSS selectors

**Start:**
```bash
python -m apps.workers.playwright.worker
```

---

### 3. `sandbox/` — Sandbox Runner
Isolated code execution for untrusted payloads. Capability-gated.

**Supported code types:**
| Type | Description |
|------|-------------|
| `scrape` | Execute a restricted HTTP fetch |
| `transform` | Apply a data transformation to a JSON payload |
| `analyze` | Run a simple analysis over structured data |

**Capability model:**  
Every execution validates a `capabilities` set against a registry. Unknown or disallowed capabilities are rejected before execution.

**Start:**
```bash
python -m apps.workers.sandbox.runner
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REDIS_URL` | Celery broker & result backend | `redis://localhost:6379/0` |
| `DATABASE_URL` | PostgreSQL async connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/xps_intelligence` |
| `SANDBOX_NETWORK_MODE` | `restricted` or `open` | `restricted` |
| `LOG_LEVEL` | Logging level | `INFO` |
