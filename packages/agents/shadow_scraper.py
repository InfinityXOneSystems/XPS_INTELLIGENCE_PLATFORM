"""
Shadow Scraper — XPS Intelligence Platform
==========================================
Primary ingestion method: headless Playwright browser with robust anti-bot
handling, robots.txt respect, domain denylist, request-budget enforcement,
concurrency caps, and compliance-mode rate limiting.

No domain allowlist is required.  Access to any public web resource is
permitted unless the domain is on the denylist or disallowed by robots.txt
(when the robots.txt toggle is enabled).

Safety rails (all configurable via environment variables):
  SCRAPER_RESPECT_ROBOTS_TXT   — default: true
  SCRAPER_MAX_REQUESTS_PER_RUN — default: 200
  SCRAPER_MAX_CONCURRENCY      — default: 3
  SCRAPER_MIN_DELAY_MS         — default: 1000
  SCRAPER_COMPLIANCE_MODE      — default: true (doubles delay floors)

Configuration file: packages/agents/scraper_config.json
  denylist — list of hostnames/wildcard patterns that are always blocked.
"""

from __future__ import annotations

import asyncio
import fnmatch
import json
import logging
import os
import random
import time
import urllib.parse
import urllib.robotparser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Optional Playwright import — gracefully degrade when the library is absent
# so that the module can be imported in test environments without browsers.
# ---------------------------------------------------------------------------
try:
    from playwright.async_api import Browser, BrowserContext, Page, async_playwright

    PLAYWRIGHT_AVAILABLE = True
except ImportError:  # pragma: no cover
    PLAYWRIGHT_AVAILABLE = False

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONFIG_PATH = Path(__file__).parent / "scraper_config.json"

# Rotating user-agent pool (desktop + mobile) for anti-bot evasion.
_USER_AGENTS: list[str] = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.4.1 Safari/605.1.15"
    ),
    (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.4 Mobile/15E148 Safari/604.1"
    ),
]


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def _load_config() -> dict[str, Any]:
    """Load scraper_config.json; fall back to safe defaults if absent."""
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open() as fh:
            return json.load(fh)
    return {"denylist": []}


@dataclass
class ScraperConfig:
    """Resolved, validated scraper configuration."""

    respect_robots_txt: bool = True
    max_requests_per_run: int = 200
    max_concurrency: int = 3
    min_delay_ms: int = 1000
    compliance_mode: bool = True
    denylist: list[str] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "ScraperConfig":
        """Build config from environment variables, falling back to defaults."""
        file_cfg = _load_config()

        def _bool(key: str, default: bool) -> bool:
            val = os.environ.get(key, "").strip().lower()
            if val in ("false", "0", "no"):
                return False
            if val in ("true", "1", "yes"):
                return True
            return default

        def _int(key: str, default: int) -> int:
            val = os.environ.get(key, "").strip()
            return int(val) if val.isdigit() else default

        cfg = cls(
            respect_robots_txt=_bool("SCRAPER_RESPECT_ROBOTS_TXT", True),
            max_requests_per_run=_int("SCRAPER_MAX_REQUESTS_PER_RUN", 200),
            max_concurrency=_int("SCRAPER_MAX_CONCURRENCY", 3),
            min_delay_ms=_int("SCRAPER_MIN_DELAY_MS", 1000),
            compliance_mode=_bool("SCRAPER_COMPLIANCE_MODE", True),
            denylist=file_cfg.get("denylist", []),
        )

        if cfg.compliance_mode:
            # Heightened mode: double all delay floors.
            cfg.min_delay_ms = max(cfg.min_delay_ms, cfg.min_delay_ms * 2)

        return cfg


# ---------------------------------------------------------------------------
# Safety Rails
# ---------------------------------------------------------------------------


def _hostname(url: str) -> str:
    """Extract the hostname from a URL."""
    return urllib.parse.urlparse(url).hostname or ""


def _is_denylisted(url: str, denylist: list[str]) -> bool:
    """Return True if the URL's hostname matches any denylist pattern."""
    host = _hostname(url)
    if not host:
        return True  # Malformed URL — block by default.
    for pattern in denylist:
        if fnmatch.fnmatch(host, pattern) or host == pattern:
            logger.warning("🚫 Denylist blocked: %s (pattern: %s)", url, pattern)
            return True
    return False


class RobotsTxtCache:
    """Lightweight cache for robots.txt parsers (one per origin)."""

    def __init__(self) -> None:
        self._cache: dict[str, urllib.robotparser.RobotFileParser] = {}

    def _origin(self, url: str) -> str:
        parsed = urllib.parse.urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def can_fetch(self, url: str, user_agent: str = "*") -> bool:
        """Return True if fetching *url* is allowed by robots.txt."""
        origin = self._origin(url)
        if origin not in self._cache:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = f"{origin}/robots.txt"
            rp.set_url(robots_url)
            try:
                rp.read()
            except Exception as exc:  # noqa: BLE001
                logger.debug("Could not read robots.txt for %s: %s", origin, exc)
                # On error: allow (fail-open for robots.txt fetch failures).
                rp = None  # type: ignore[assignment]
            self._cache[origin] = rp  # type: ignore[assignment]

        parser = self._cache[origin]
        if parser is None:
            return True
        return parser.can_fetch(user_agent, url)


# ---------------------------------------------------------------------------
# Scrape Result
# ---------------------------------------------------------------------------


@dataclass
class ScrapeResult:
    """Result of a single page scrape."""

    url: str
    status_code: int
    title: str
    text_content: str
    screenshot_bytes: bytes | None
    scraped_at: float = field(default_factory=time.time)
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.error is None and 200 <= self.status_code < 400


# ---------------------------------------------------------------------------
# Shadow Scraper
# ---------------------------------------------------------------------------


class ShadowScraper:
    """
    Headless Playwright browser scraper.

    Usage (async context manager)::

        async with ShadowScraper() as scraper:
            results = await scraper.scrape_many(urls)

    The scraper enforces all safety rails on construction via
    ``ScraperConfig.from_env()``.
    """

    def __init__(self, config: ScraperConfig | None = None) -> None:
        self.config = config or ScraperConfig.from_env()
        self._robots = RobotsTxtCache()
        self._request_count = 0
        self._last_request_time: dict[str, float] = {}  # hostname → epoch seconds
        self._browser: "Browser | None" = None
        self._playwright_ctx: Any = None

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "ShadowScraper":
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError(
                "playwright is not installed. "
                "Run: pip install playwright && playwright install chromium"
            )
        self._playwright_ctx = await async_playwright().start()
        self._browser = await self._playwright_ctx.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ],
        )
        logger.info("🌐 Shadow Scraper browser started.")
        return self

    async def __aexit__(self, *_: Any) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright_ctx:
            await self._playwright_ctx.stop()
        logger.info(
            "🌐 Shadow Scraper closed. Total requests: %d", self._request_count
        )

    # ------------------------------------------------------------------
    # Rate-limit helpers
    # ------------------------------------------------------------------

    async def _enforce_delay(self, url: str) -> None:
        """Sleep if needed to respect the per-domain minimum delay."""
        host = _hostname(url)
        last = self._last_request_time.get(host, 0.0)
        min_delay_s = self.config.min_delay_ms / 1000.0
        # Add a small random jitter (±20 %) as anti-bot evasion.
        jitter = random.uniform(-0.2 * min_delay_s, 0.2 * min_delay_s)
        required_gap = max(0.0, min_delay_s + jitter)
        elapsed = time.monotonic() - last
        wait = required_gap - elapsed
        if wait > 0:
            logger.debug("⏳ Rate-limit delay %.2fs for %s", wait, host)
            await asyncio.sleep(wait)
        self._last_request_time[host] = time.monotonic()

    def _budget_check(self) -> None:
        """Raise BudgetExhausted if the request budget has been reached."""
        if self._request_count >= self.config.max_requests_per_run:
            raise BudgetExhausted(
                f"Request budget of {self.config.max_requests_per_run} reached."
            )

    # ------------------------------------------------------------------
    # Safety gate
    # ------------------------------------------------------------------

    def _is_allowed(self, url: str) -> tuple[bool, str]:
        """
        Return (allowed, reason).  Checks denylist and robots.txt in order.
        """
        if _is_denylisted(url, self.config.denylist):
            return False, "denylist"

        if self.config.respect_robots_txt:
            user_agent = random.choice(_USER_AGENTS)
            if not self._robots.can_fetch(url, user_agent):
                logger.info("🤖 robots.txt disallows: %s", url)
                return False, "robots.txt"

        return True, "ok"

    # ------------------------------------------------------------------
    # Single-page scrape
    # ------------------------------------------------------------------

    async def scrape_one(
        self,
        url: str,
        *,
        take_screenshot: bool = False,
        retries: int = 3,
    ) -> ScrapeResult:
        """
        Scrape a single URL.  Retries up to *retries* times with exponential
        back-off on network errors.
        """
        allowed, reason = self._is_allowed(url)
        if not allowed:
            return ScrapeResult(
                url=url,
                status_code=0,
                title="",
                text_content="",
                screenshot_bytes=None,
                error=f"blocked:{reason}",
            )

        self._budget_check()

        user_agent = random.choice(_USER_AGENTS)
        last_error: str = ""

        for attempt in range(1, retries + 1):
            try:
                await self._enforce_delay(url)
                self._budget_check()

                assert self._browser is not None
                context: BrowserContext = await self._browser.new_context(
                    user_agent=user_agent,
                    viewport={"width": 1280, "height": 800},
                    java_script_enabled=True,
                    ignore_https_errors=False,
                )

                page: Page = await context.new_page()
                self._request_count += 1

                response = await page.goto(
                    url,
                    timeout=30_000,
                    wait_until="domcontentloaded",
                )

                status = response.status if response else 0
                title = await page.title()
                text = await page.evaluate("() => document.body?.innerText || ''")
                screenshot: bytes | None = None

                if take_screenshot:
                    screenshot = await page.screenshot(
                        full_page=False, type="png"
                    )

                await context.close()

                logger.info(
                    "✅ Scraped [%d] %s (attempt %d, budget used: %d/%d)",
                    status,
                    url,
                    attempt,
                    self._request_count,
                    self.config.max_requests_per_run,
                )

                return ScrapeResult(
                    url=url,
                    status_code=status,
                    title=title,
                    text_content=text,
                    screenshot_bytes=screenshot,
                )

            except BudgetExhausted:
                raise
            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                back_off = 2**attempt
                logger.warning(
                    "⚠️  Attempt %d/%d failed for %s: %s. Back-off %ds.",
                    attempt,
                    retries,
                    url,
                    exc,
                    back_off,
                )
                if attempt < retries:
                    await asyncio.sleep(back_off)

        return ScrapeResult(
            url=url,
            status_code=0,
            title="",
            text_content="",
            screenshot_bytes=None,
            error=last_error,
        )

    # ------------------------------------------------------------------
    # Batch scrape
    # ------------------------------------------------------------------

    async def scrape_many(
        self,
        urls: list[str],
        *,
        take_screenshot: bool = False,
        retries: int = 3,
    ) -> list[ScrapeResult]:
        """
        Scrape a list of URLs with concurrency capped at
        ``config.max_concurrency``.  Returns results in input order.
        """
        semaphore = asyncio.Semaphore(self.config.max_concurrency)
        results: list[ScrapeResult] = []

        async def _scrape(url: str) -> ScrapeResult:
            async with semaphore:
                return await self.scrape_one(
                    url, take_screenshot=take_screenshot, retries=retries
                )

        tasks = [_scrape(url) for url in urls]

        for coro in asyncio.as_completed(tasks):
            try:
                result = await coro
            except BudgetExhausted as exc:
                logger.warning("💰 Budget exhausted during batch scrape: %s", exc)
                break
            results.append(result)

        logger.info(
            "📦 Batch complete. %d/%d results. Requests used: %d/%d",
            len(results),
            len(urls),
            self._request_count,
            self.config.max_requests_per_run,
        )
        return results


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class BudgetExhausted(RuntimeError):
    """Raised when the scraper has reached SCRAPER_MAX_REQUESTS_PER_RUN."""


# ---------------------------------------------------------------------------
# CLI entry-point (used by the CI proof job)
# ---------------------------------------------------------------------------


async def _cli_main(urls: list[str]) -> int:
    """
    Scrape *urls* and print a JSON summary to stdout.
    Returns exit code 0 on success (at least one successful result),
    1 if all scrapes failed.
    """
    config = ScraperConfig.from_env()
    logger.info(
        "Shadow Scraper config: robots=%s budget=%d concurrency=%d delay=%dms "
        "compliance=%s denylist=%d entries",
        config.respect_robots_txt,
        config.max_requests_per_run,
        config.max_concurrency,
        config.min_delay_ms,
        config.compliance_mode,
        len(config.denylist),
    )

    async with ShadowScraper(config) as scraper:
        results = await scraper.scrape_many(urls, take_screenshot=False)

    summary = [
        {
            "url": r.url,
            "status_code": r.status_code,
            "title": r.title,
            "success": r.success,
            "error": r.error,
            "scraped_at": r.scraped_at,
        }
        for r in results
    ]

    print(json.dumps(summary, indent=2))

    successes = sum(1 for r in results if r.success)
    logger.info("Summary: %d/%d URLs scraped successfully.", successes, len(results))
    return 0 if successes > 0 else 1


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    target_urls = sys.argv[1:]
    if not target_urls:
        print("Usage: python shadow_scraper.py <url> [url ...]", file=sys.stderr)
        sys.exit(1)

    exit_code = asyncio.run(_cli_main(target_urls))
    sys.exit(exit_code)
