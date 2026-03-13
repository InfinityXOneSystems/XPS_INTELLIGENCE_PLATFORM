import { test, expect } from '@playwright/test';
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';

/**
 * Shadow Scraper E2E Tests — XPS Intelligence Platform
 *
 * These tests validate the Shadow Scraper infrastructure:
 *   1. scraper_config.json is present and well-formed.
 *   2. The denylist contains the mandatory private-network entries.
 *   3. The proof_targets list is non-empty.
 *   4. No flaky network calls — config validation only in this file.
 *
 * Actual live-scrape proof runs are performed by the
 * `.github/workflows/shadow-scraper-proof.yml` workflow which uploads
 * artifacts to TEST_EVIDENCE/ on every push and on the 2-hour schedule.
 *
 * Playwright retries are configured in playwright.config.ts
 * (retries: 2 in CI) to handle any transient test-runner issues.
 */

const REPO_ROOT = join(__dirname, '..', '..');
const CONFIG_PATH = join(REPO_ROOT, 'packages', 'agents', 'scraper_config.json');

// ---------------------------------------------------------------------------
// Scraper Config Validation
// ---------------------------------------------------------------------------

test.describe('Shadow Scraper: Config Validation', () => {
  test('scraper_config.json exists', () => {
    expect(existsSync(CONFIG_PATH)).toBe(true);
  });

  test('scraper_config.json is valid JSON', () => {
    const raw = readFileSync(CONFIG_PATH, 'utf-8');
    expect(() => JSON.parse(raw)).not.toThrow();
  });

  test('scraper_config.json has required fields', () => {
    const cfg = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'));

    expect(cfg).toHaveProperty('denylist');
    expect(Array.isArray(cfg.denylist)).toBe(true);

    expect(cfg).toHaveProperty('proof_targets');
    expect(Array.isArray(cfg.proof_targets)).toBe(true);
    expect(cfg.proof_targets.length).toBeGreaterThan(0);

    expect(cfg).toHaveProperty('defaults');
  });

  test('denylist includes mandatory private-network entries', () => {
    const cfg = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'));
    const denylist: string[] = cfg.denylist;

    const required = ['localhost', '127.0.0.1', '169.254.169.254'];
    for (const entry of required) {
      expect(denylist).toContain(entry);
    }
  });

  test('proof_targets are valid HTTPS URLs', () => {
    const cfg = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'));
    for (const url of cfg.proof_targets as string[]) {
      expect(url).toMatch(/^https:\/\//);
    }
  });

  test('defaults.compliance_mode is true', () => {
    const cfg = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'));
    expect(cfg.defaults?.compliance_mode).toBe(true);
  });

  test('defaults.respect_robots_txt is true', () => {
    const cfg = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'));
    expect(cfg.defaults?.respect_robots_txt).toBe(true);
  });

  test('defaults.max_requests_per_run is within safe bounds', () => {
    const cfg = JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'));
    const budget: number = cfg.defaults?.max_requests_per_run ?? 0;
    // Budget must be positive and not exceed 1000 (governance cap).
    expect(budget).toBeGreaterThan(0);
    expect(budget).toBeLessThanOrEqual(1000);
  });
});

// ---------------------------------------------------------------------------
// Shadow Scraper Python Module Validation
// ---------------------------------------------------------------------------

test.describe('Shadow Scraper: Module Validation', () => {
  const SCRAPER_PATH = join(
    REPO_ROOT,
    'packages',
    'agents',
    'shadow_scraper.py'
  );

  test('shadow_scraper.py exists', () => {
    expect(existsSync(SCRAPER_PATH)).toBe(true);
  });

  test('shadow_scraper.py contains ShadowScraper class', () => {
    const source = readFileSync(SCRAPER_PATH, 'utf-8');
    expect(source).toContain('class ShadowScraper');
  });

  test('shadow_scraper.py contains BudgetExhausted exception', () => {
    const source = readFileSync(SCRAPER_PATH, 'utf-8');
    expect(source).toContain('class BudgetExhausted');
  });

  test('shadow_scraper.py contains RobotsTxtCache', () => {
    const source = readFileSync(SCRAPER_PATH, 'utf-8');
    expect(source).toContain('class RobotsTxtCache');
  });

  test('shadow_scraper.py contains denylist check', () => {
    const source = readFileSync(SCRAPER_PATH, 'utf-8');
    expect(source).toContain('_is_denylisted');
  });

  test('shadow_scraper.py does NOT contain allowlist gating code', () => {
    const source = readFileSync(SCRAPER_PATH, 'utf-8');
    // Allowlist gating is explicitly removed per operator decision.
    // Comments may mention "allowlist" for documentation purposes, but no
    // functional allowlist check code (variable names / function calls) should exist.
    expect(source).not.toContain('SCRAPER_ALLOWLIST');
    expect(source).not.toContain('_is_allowlisted');
    expect(source).not.toContain('is_allowlisted(');
  });
});
