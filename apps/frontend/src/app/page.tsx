import { redirect } from 'next/navigation';

/**
 * Root page — redirects to the legacy dashboard while the native
 * implementation is in progress.
 *
 * Navigation links to new routes (e.g. /workspace, /scraper) are surfaced
 * via the floating nav bar rendered by the legacy dashboard layout. To add
 * more top-level links, see apps/frontend/src/app/legacy-dashboard/page.tsx.
 */
export default function HomePage() {
  redirect('/legacy-dashboard');
}
