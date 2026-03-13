/** @type {import('next').NextConfig} */
const nextConfig = {
  /**
   * Append custom security headers to all responses.
   * The legacy dashboard iframe is allowed via Content-Security-Policy only
   * when LEGACY_DASHBOARD_MODE=iframe (default).
   */
  async headers() {
    const legacyDashboardUrl =
      process.env.NEXT_PUBLIC_LEGACY_DASHBOARD_URL ||
      'https://infinityxonesystems.github.io';

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
              "connect-src 'self' https://xps-intelligence.up.railway.app",
              "font-src 'self'",
            ].join('; '),
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
