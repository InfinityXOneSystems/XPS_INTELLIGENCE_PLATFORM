/**
 * /legacy-dashboard route
 *
 * Integrates the XPS Intelligence System legacy dashboard
 * (https://infinityxonesystems.github.io/XPS_INTELLIGENCE_SYSTEM/) into the
 * monorepo frontend as an additive route with zero aesthetic drift.
 *
 * Feature flag: NEXT_PUBLIC_LEGACY_DASHBOARD_MODE
 *   "iframe"  (default) — embeds the deployed GitHub Pages site via <iframe>.
 *              Safe and immediately functional with zero porting risk.
 *   "native"  — renders the native re-implementation when parity is achieved.
 *              Gated until all items in LEGACY_DASHBOARD_MIGRATION.md are
 *              marked as "ported" with test coverage.
 */
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Legacy Dashboard — XPS Intelligence',
  description: 'XPS Intelligence legacy dashboard (bridge mode)',
};

const LEGACY_URL =
  process.env.NEXT_PUBLIC_LEGACY_DASHBOARD_URL ||
  'https://infinityxonesystems.github.io/XPS_INTELLIGENCE_SYSTEM/';

const MODE =
  (process.env.NEXT_PUBLIC_LEGACY_DASHBOARD_MODE as 'iframe' | 'native' | undefined) ||
  'iframe';

// The sandbox value deliberately includes `allow-same-origin` alongside `allow-scripts`.
// Security note: the parent app and the iframe are on DIFFERENT origins
// (railway.app/localhost vs infinityxonesystems.github.io), so this combination does NOT
// allow the iframe to escape the sandbox and access the parent document.
// `allow-same-origin` is required so the iframe can access its own GitHub Pages origin
// for storage/cookie reads and same-origin fetch calls to the Railway API.
const IFRAME_SANDBOX =
  'allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox';

export default function LegacyDashboardPage() {
  if (MODE === 'native') {
    // Native re-implementation stub — enabled only when full parity is
    // confirmed in LEGACY_DASHBOARD_MIGRATION.md.
    return (
      <main
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          background: '#0a0e1a',
          color: '#f9fafb',
          fontFamily: "'Segoe UI', system-ui, -apple-system, sans-serif",
          gap: '1rem',
          padding: '2rem',
        }}
      >
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700 }}>
          ⚡ XPS Intelligence — Native Dashboard
        </h1>
        <p style={{ color: '#9ca3af', textAlign: 'center', maxWidth: 480 }}>
          Native re-implementation is in progress. Track status in{' '}
          <code>LEGACY_DASHBOARD_MIGRATION.md</code>.
        </p>
      </main>
    );
  }

  // Default: iframe bridge mode
  return (
    <main
      data-testid="legacy-dashboard-container"
      style={{
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
        height: '100vh',
        overflow: 'hidden',
        background: '#0a0e1a',
      }}
    >
      <iframe
        data-testid="legacy-dashboard-iframe"
        src={LEGACY_URL}
        title="XPS Intelligence Legacy Dashboard"
        style={{
          flex: 1,
          width: '100%',
          height: '100%',
          border: 'none',
        }}
        sandbox={IFRAME_SANDBOX}
        loading="eager"
        referrerPolicy="strict-origin-when-cross-origin"
      />
    </main>
  );
}
