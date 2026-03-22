/** @type {import('next').NextConfig} */
const nextConfig = {
  // Standalone output enables the minimal Docker deployment used by Railway.
  // The multi-stage Dockerfile copies .next/standalone + .next/static.
  output: 'standalone',

  /**
   * Proxy /api/v1/* to the FastAPI backend.
   *
   * Two deployment modes are supported:
   *
   *   ALL-IN-ONE (single Railway service):
   *     Set BACKEND_INTERNAL_URL=http://127.0.0.1:8000 in the container.
   *     The Next.js server-side rewrite forwards to the co-located FastAPI
   *     process. The browser never directly reaches port 8000.
   *
   *   SEPARATE SERVICES (two Railway services):
   *     Set NEXT_PUBLIC_BACKEND_URL=https://<your-backend>.up.railway.app.
   *     The Next.js server-side rewrite forwards to the external Railway URL.
   *
   * BACKEND_INTERNAL_URL takes precedence when set (all-in-one mode).
   */
  async rewrites() {
    const backendUrl =
      process.env.BACKEND_INTERNAL_URL ||
      process.env.NEXT_PUBLIC_BACKEND_URL;
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
   */
  async headers() {
    const legacyDashboardUrl =
      process.env.NEXT_PUBLIC_LEGACY_DASHBOARD_URL ||
      'https://infinityxonesystems.github.io';

    // In all-in-one mode, the API is served by the same origin (self).
    // In separate-services mode, the public backend URL is needed for CSP.
    const connectSrc = process.env.NEXT_PUBLIC_BACKEND_URL
      ? `'self' ${process.env.NEXT_PUBLIC_BACKEND_URL}`
      : "'self'";

    return [
      {
        source: '/(.*)',
        headers: [
          { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline'",
              "style-src 'self' 'unsafe-inline'",
              `frame-src 'self' ${legacyDashboardUrl}`,
              "img-src 'self' data: blob:",
              `connect-src ${connectSrc}`,
              "font-src 'self'",
            ].join('; '),
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
