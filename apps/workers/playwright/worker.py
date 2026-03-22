from __future__ import annotations

import base64
import re
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")


async def scrape_with_browser(url: str, selectors: dict[str, str] | None = None) -> dict[str, Any]:
    from playwright.async_api import async_playwright

    selectors = selectors or {}
    result: dict[str, Any] = {
        "url": url,
        "title": "",
        "leads": [],
        "screenshot_b64": "",
    }

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
            ],
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (compatible; XPS-Scraper/1.0)",
            java_script_enabled=True,
        )
        page = await context.new_page()

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            result["title"] = await page.title()

            # Screenshot
            screenshot_bytes = await page.screenshot(full_page=False)
            result["screenshot_b64"] = base64.b64encode(screenshot_bytes).decode("utf-8")

            # Extract text content and find emails
            body_text = await page.inner_text("body")
            emails = list(set(EMAIL_RE.findall(body_text)))
            for email in emails:
                result["leads"].append({"email": email, "source": "playwright_email_extraction"})

            # Run any custom selectors
            for field_name, selector in selectors.items():
                try:
                    elements = await page.query_selector_all(selector)
                    values = []
                    for el in elements:
                        text = await el.inner_text()
                        if text.strip():
                            values.append(text.strip())
                    if values:
                        result[f"selector_{field_name}"] = values
                except Exception as exc:
                    logger.warning("selector_failed", field=field_name, error=str(exc))

        finally:
            await context.close()
            await browser.close()

    logger.info("playwright_scrape_done", url=url, leads=len(result["leads"]))
    return result


if __name__ == "__main__":
    import asyncio
    import sys

    url = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    data = asyncio.run(scrape_with_browser(url))
    print(f"Title: {data['title']}")
    print(f"Leads found: {len(data['leads'])}")
    for lead in data["leads"]:
        print(f"  {lead}")
