import { redirect } from 'next/navigation';

/**
 * Root page — redirects to the legacy dashboard while the native
 * implementation is in progress.
 */
export default function HomePage() {
  redirect('/legacy-dashboard');
}
