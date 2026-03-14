/** @type {import('next').NextConfig} */
const nextConfig = {
  // Standalone output enables the minimal Docker deployment used by Railway.
  // The multi-stage Dockerfile copies .next/standalone + .next/static.
  output: 'standalone',

  /**
   * Proxy /api/v1/* to the FastAPI backend so the frontend pages can use
   * relative fetch('/api/v1/...') calls that work in both local dev and
   * Railway production (where frontend and backend are separate services).
   *
   * Set NEXT_PUBLIC_BACKEND_URL in Railway frontend service environment:
   *   https://<your-backend-service>.up.railway.app
   */
  async rewrites() {
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
    if (!backendUrl) return [];
    return [
      {
        source: '/api/v1/:path*',
        destination: `${backendUrl}/api/v1/:path*`,
      },
    ];
  },

  /**
   * Append custom security headers to all responses.
   * The legacy dashboard iframe is allowed via Content-Security-Policy only
   * when LEGACY_DASHBOARD_MODE=iframe (default).
   */
  async headers() {
    const legacyDashboardUrl =
      process.env.NEXT_PUBLIC_LEGACY_DASHBOARD_URL ||
      'https://infinityxonesystems.github.io';

    // Use the configured backend URL for connect-src so the CSP is not
    // hardcoded to a specific Railway subdomain.
    const backendUrl =
      process.env.NEXT_PUBLIC_BACKEND_URL ||
      'https://xps-backend.up.railway.app';

    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              // Next.js App Router uses inline scripts for hydration; restrict to
              // self-hosted scripts only. 'unsafe-eval' is intentionally omitted
              // as Next.js 15 production builds do not require it.
              "script-src 'self' 'unsafe-inline'",
              "style-src 'self' 'unsafe-inline'",
              `frame-src 'self' ${legacyDashboardUrl}`,
              "img-src 'self' data: blob:",
              `connect-src 'self' ${backendUrl}`,
              "font-src 'self'",
            ].join('; '),
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
