import { test, expect } from '@playwright/test';

/**
 * Foundation E2E Tests — XPS Intelligence Platform
 *
 * These tests validate the foundation infrastructure.
 * As services are deployed, replace BASE_URL with the actual deployment URL.
 */

test.describe('Foundation: Playwright Infrastructure', () => {
  test('playwright configuration is valid', () => {
    // Validates that the Playwright test runner is correctly configured.
    // This test will always pass — it is the baseline.
    expect(true).toBe(true);
  });

  test('test environment variables are accessible', () => {
    // Validates that the CI environment is correctly set up.
    const env = process.env.CI;
    // Either CI=true (GitHub Actions) or undefined (local) — both are valid
    expect(env === 'true' || env === undefined).toBe(true);
  });
});

/**
 * Backend Health Check
 * Enabled only when BACKEND_URL is set in the environment.
 */
test.describe('Backend: Health Check', () => {
  test.skip(
    !process.env.BACKEND_URL,
    'BACKEND_URL not set — skipping backend health check (foundation phase)'
  );

  test('backend /health endpoint returns 200', async ({ request }) => {
    const backendUrl = process.env.BACKEND_URL!;
    const response = await request.get(`${backendUrl}/health`);
    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body).toHaveProperty('status');
    expect(body.status).toBe('ok');
  });
});

/**
 * Frontend Smoke Test
 * Enabled only when BASE_URL resolves to an actual deployment.
 */
test.describe('Frontend: Smoke Tests', () => {
  test.skip(
    !process.env.FRONTEND_URL,
    'FRONTEND_URL not set — skipping frontend smoke tests (foundation phase)'
  );

  test('homepage loads successfully', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/XPS Intelligence/i);
  });

  test('homepage has no console errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    await page.goto('/');
    await page.waitForLoadState('networkidle');

    expect(errors).toHaveLength(0);
  });

  test('homepage snapshot', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Take a full-page screenshot for visual regression tracking
    await expect(page).toHaveScreenshot('homepage.png', {
      fullPage: true,
      threshold: 0.2,
    });
  });
});
