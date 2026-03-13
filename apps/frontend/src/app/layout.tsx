import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'XPS Intelligence Platform',
  description: 'XPS Intelligence Platform — Autonomous Lead Intelligence System',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
