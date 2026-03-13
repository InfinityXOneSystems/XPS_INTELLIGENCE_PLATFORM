"""Shadow Scraper — Compliance and Parallelism Configuration.

Operator directive (2026-03-13):
  robots.txt  : IGNORE BY DEFAULT
  parallelism : maximum safe, bounded by configurable budget caps

All defaults match the operator directive.  Operators may override any
value via the environment variables documented below without code changes.

Environment variables (all optional — hard-coded defaults are operator-approved):

  SCRAPER_RESPECT_ROBOTS_TXT   "true" to honour robots.txt; default "false"
  SCRAPER_MAX_CONCURRENCY      Global concurrent-request cap; default 20
  SCRAPER_DOMAIN_CONCURRENCY   Per-domain concurrent-request cap; default 5
  SCRAPER_MAX_REQUESTS         Max HTTP requests per scrape job; default 10000
  SCRAPER_MAX_PAGES            Max pages crawled per scrape job; default 5000
  SCRAPER_MAX_RUNTIME_SECONDS  Hard deadline per job in seconds; default 3600
  SCRAPER_BACKOFF_BASE_MS      Adaptive-backoff base delay (ms); default 250
  SCRAPER_BACKOFF_MAX_MS       Adaptive-backoff ceiling (ms); default 30000
  SCRAPER_REQUEST_TIMEOUT_MS   Per-request network timeout (ms); default 30000
  SCRAPER_RETRY_MAX            Max retries for a failed request; default 3
"""

from __future__ import annotations

import os
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _env_bool(name: str, default: bool) -> bool:
    """Read a boolean from an environment variable."""
    val = os.environ.get(name, "").strip().lower()
    if not val:
        return default
    return val in ("1", "true", "yes", "on")


def _env_int(name: str, default: int, *, min_val: int = 1) -> int:
    """Read a positive integer from an environment variable.

    Returns *default* when the variable is absent or non-numeric.
    Clamps the result to *min_val* if the supplied value is too small.
    """
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        parsed = int(raw)
    except ValueError:
        return default
    return max(min_val, parsed)


# ---------------------------------------------------------------------------
# Configuration dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ScraperConfig:
    """Immutable, validated snapshot of Shadow Scraper runtime parameters.

    Defaults reflect the operator directive: ignore robots.txt and maximise
    parallelism within bounded budgets.  Construct via :func:`load_config` to
    read from the environment, or instantiate directly for tests.
    """

    # ---- Compliance --------------------------------------------------------
    # Operator directive: IGNORE robots.txt by default.
    # Set SCRAPER_RESPECT_ROBOTS_TXT=true (or pass respect_robots_txt=True)
    # to honour robots.txt for a specific deployment.
    respect_robots_txt: bool = False

    # ---- Global parallelism budget caps ------------------------------------
    max_concurrency: int = 20        # global simultaneous requests
    domain_concurrency: int = 5      # simultaneous requests per domain
    max_requests: int = 10_000       # total HTTP requests per job
    max_pages: int = 5_000           # total pages crawled per job
    max_runtime_seconds: int = 3_600  # hard job deadline (1 hour)

    # ---- Retry / back-pressure / adaptive throttling -----------------------
    backoff_base_ms: int = 250       # initial back-off delay (ms)
    backoff_max_ms: int = 30_000     # back-off ceiling (ms)
    request_timeout_ms: int = 30_000  # per-request network timeout (ms)
    retry_max: int = 3               # max retries for a failed request

    # -----------------------------------------------------------------------
    # Validation
    # -----------------------------------------------------------------------

    def validate(self) -> None:
        """Raise AssertionError if any parameter is out of safe range."""
        assert 1 <= self.max_concurrency <= 200, (
            f"max_concurrency must be 1-200, got {self.max_concurrency}"
        )
        assert 1 <= self.domain_concurrency <= self.max_concurrency, (
            f"domain_concurrency must be 1-{self.max_concurrency}, "
            f"got {self.domain_concurrency}"
        )
        assert self.max_requests >= 1, (
            f"max_requests must be >= 1, got {self.max_requests}"
        )
        assert self.max_pages >= 1, (
            f"max_pages must be >= 1, got {self.max_pages}"
        )
        assert self.max_runtime_seconds >= 1, (
            f"max_runtime_seconds must be >= 1, got {self.max_runtime_seconds}"
        )
        assert self.backoff_base_ms >= 0, (
            f"backoff_base_ms must be >= 0, got {self.backoff_base_ms}"
        )
        assert self.backoff_max_ms >= self.backoff_base_ms, (
            f"backoff_max_ms ({self.backoff_max_ms}) must be >= "
            f"backoff_base_ms ({self.backoff_base_ms})"
        )
        assert self.request_timeout_ms >= 100, (
            f"request_timeout_ms must be >= 100 ms, got {self.request_timeout_ms}"
        )
        assert 0 <= self.retry_max <= 10, (
            f"retry_max must be 0-10, got {self.retry_max}"
        )

    # -----------------------------------------------------------------------
    # Metrics / observability
    # -----------------------------------------------------------------------

    def as_metrics(self) -> dict:
        """Return all config fields as a plain dict for logging and artifacts."""
        return {
            "respect_robots_txt": self.respect_robots_txt,
            "max_concurrency": self.max_concurrency,
            "domain_concurrency": self.domain_concurrency,
            "max_requests": self.max_requests,
            "max_pages": self.max_pages,
            "max_runtime_seconds": self.max_runtime_seconds,
            "backoff_base_ms": self.backoff_base_ms,
            "backoff_max_ms": self.backoff_max_ms,
            "request_timeout_ms": self.request_timeout_ms,
            "retry_max": self.retry_max,
        }


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def load_config() -> ScraperConfig:
    """Build a :class:`ScraperConfig` from environment variables.

    All parameters fall back to operator-approved defaults when the
    corresponding environment variable is absent or invalid.
    Calls :meth:`ScraperConfig.validate` before returning so that
    misconfigured deployments fail fast at startup.
    """
    cfg = ScraperConfig(
        respect_robots_txt=_env_bool("SCRAPER_RESPECT_ROBOTS_TXT", False),
        max_concurrency=_env_int("SCRAPER_MAX_CONCURRENCY", 20),
        domain_concurrency=_env_int("SCRAPER_DOMAIN_CONCURRENCY", 5),
        max_requests=_env_int("SCRAPER_MAX_REQUESTS", 10_000),
        max_pages=_env_int("SCRAPER_MAX_PAGES", 5_000),
        max_runtime_seconds=_env_int("SCRAPER_MAX_RUNTIME_SECONDS", 3_600),
        backoff_base_ms=_env_int("SCRAPER_BACKOFF_BASE_MS", 250, min_val=0),
        backoff_max_ms=_env_int("SCRAPER_BACKOFF_MAX_MS", 30_000),
        request_timeout_ms=_env_int("SCRAPER_REQUEST_TIMEOUT_MS", 30_000, min_val=100),
        retry_max=_env_int("SCRAPER_RETRY_MAX", 3, min_val=0),
    )
    cfg.validate()
    return cfg
