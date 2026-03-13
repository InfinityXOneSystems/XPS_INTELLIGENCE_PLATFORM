import { test, expect } from '@playwright/test';

/**
 * Legacy Dashboard E2E Tests — XPS Intelligence Platform
 *
 * Validates the /legacy-dashboard route added as part of the legacy
 * dashboard integration (see LEGACY_DASHBOARD_MIGRATION.md).
 *
 * These tests run against a live frontend when FRONTEND_URL is set,
 * and are skipped in the foundation phase (no deployed frontend yet).
 *
 * Feature flag coverage:
 *   NEXT_PUBLIC_LEGACY_DASHBOARD_MODE=iframe (default)
 *   → iframe is rendered with the GitHub Pages URL
 */

// Match the fallback URL used in apps/frontend/src/app/legacy-dashboard/page.tsx
const LEGACY_PAGES_URL =
  process.env.NEXT_PUBLIC_LEGACY_DASHBOARD_URL ||
  'https://infinityxonesystems.github.io/XPS_INTELLIGENCE_SYSTEM/';

test.describe('Legacy Dashboard: Route Existence', () => {
  test.skip(
    !process.env.FRONTEND_URL,
    'FRONTEND_URL not set — skipping legacy dashboard E2E tests (bridge phase)'
  );

  test('navigates to /legacy-dashboard without error', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (err) => errors.push(err.message));

    await page.goto('/legacy-dashboard');
    await expect(page).toHaveURL(/\/legacy-dashboard/);

    // No uncaught JS errors on the page
    expect(errors).toHaveLength(0);
  });

  test('/legacy-dashboard page title contains XPS Intelligence', async ({ page }) => {
    await page.goto('/legacy-dashboard');
    await expect(page).toHaveTitle(/XPS Intelligence/i);
  });

  test('/legacy-dashboard renders the container element', async ({ page }) => {
    await page.goto('/legacy-dashboard');
    const container = page.locator('[data-testid="legacy-dashboard-container"]');
    await expect(container).toBeVisible();
  });
});

test.describe('Legacy Dashboard: iframe Bridge Mode', () => {
  test.skip(
    !process.env.FRONTEND_URL,
    'FRONTEND_URL not set — skipping legacy dashboard iframe tests (bridge phase)'
  );

  test('iframe element is present and visible', async ({ page }) => {
    await page.goto('/legacy-dashboard');

    const iframe = page.locator('[data-testid="legacy-dashboard-iframe"]');
    await expect(iframe).toBeVisible();
  });

  test('iframe src points to the correct legacy URL', async ({ page }) => {
    await page.goto('/legacy-dashboard');

    const iframe = page.locator('[data-testid="legacy-dashboard-iframe"]');
    const src = await iframe.getAttribute('src');
    expect(src).toBe(LEGACY_PAGES_URL);
  });

  test('iframe has appropriate sandbox attributes', async ({ page }) => {
    await page.goto('/legacy-dashboard');

    const iframe = page.locator('[data-testid="legacy-dashboard-iframe"]');
    const sandbox = await iframe.getAttribute('sandbox');

    // Must allow scripts (for the legacy dashboard JS to run)
    expect(sandbox).toContain('allow-scripts');
    // Must allow same-origin (for data fetch within the page)
    expect(sandbox).toContain('allow-same-origin');
  });

  test('iframe has accessible title attribute', async ({ page }) => {
    await page.goto('/legacy-dashboard');

    const iframe = page.locator('[data-testid="legacy-dashboard-iframe"]');
    const title = await iframe.getAttribute('title');
    expect(title).toBeTruthy();
    expect(title).toContain('Legacy Dashboard');
  });
});

test.describe('Legacy Dashboard: Visual Snapshot', () => {
  test.skip(
    !process.env.FRONTEND_URL,
    'FRONTEND_URL not set — skipping legacy dashboard snapshots (bridge phase)'
  );

  test('/legacy-dashboard page snapshot', async ({ page }) => {
    await page.goto('/legacy-dashboard');
    await page.waitForLoadState('networkidle');

    // Full-page screenshot stored as snapshot artifact
    await expect(page).toHaveScreenshot('legacy-dashboard.png', {
      fullPage: true,
      threshold: 0.2,
    });
  });
});
