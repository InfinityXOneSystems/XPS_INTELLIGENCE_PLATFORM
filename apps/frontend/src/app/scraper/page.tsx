'use client';
import Link from 'next/link';
import { useEffect, useState } from 'react';

interface ScraperSettings {
  autorun_enabled: boolean;
}

interface ScrapeJob {
  id: string;
  url: string;
  status: 'pending' | 'running' | 'done' | 'error';
  created_at: string;
  result_count?: number;
  error?: string;
}

export default function ScraperPage() {
  const [settings, setSettings] = useState<ScraperSettings | null>(null);
  const [jobs, setJobs] = useState<ScrapeJob[]>([]);
  const [manualUrl, setManualUrl] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [submitMsg, setSubmitMsg] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/v1/scraper/settings')
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(d => setSettings(d))
      .catch(() => setLoadError('Backend not reachable — showing defaults'));

    fetch('/api/v1/scraper/jobs')
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(d => setJobs(Array.isArray(d) ? d : d.jobs || []))
      .catch(() => {/* jobs stay empty */});
  }, []);

  const toggleAutorun = async () => {
    if (!settings) return;
    const next = !settings.autorun_enabled;
    setSettings({ ...settings, autorun_enabled: next });
    try {
      await fetch('/api/v1/scraper/settings', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ autorun_enabled: next }),
      });
    } catch {
      setSettings({ ...settings, autorun_enabled: !next });
    }
  };

  const submitManualJob = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!manualUrl.trim()) return;
    setSubmitting(true);
    setSubmitMsg(null);
    try {
      const res = await fetch('/api/v1/scraper/jobs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: manualUrl }),
      });
      if (res.ok) {
        const job: ScrapeJob = await res.json();
        setJobs(prev => [job, ...prev]);
        setManualUrl('');
        setSubmitMsg('✅ Job queued');
      } else {
        setSubmitMsg(`❌ Error ${res.status}`);
      }
    } catch {
      setSubmitMsg('⚠️ Backend not reachable');
    }
    setSubmitting(false);
  };

  const statusColor = (s: ScrapeJob['status']) => {
    const map: Record<ScrapeJob['status'], string> = {
      pending: '#94a3b8',
      running: '#fbbf24',
      done: '#34d399',
      error: '#f87171',
    };
    return map[s] || '#94a3b8';
  };

  return (
    <main style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%)',
      color: '#e2e8f0',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      padding: '24px',
    }}>
      <div style={{ maxWidth: 900, margin: '0 auto' }}>

        {/* Header */}
        <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h1 style={{ fontSize: 24, fontWeight: 700, color: '#e2e8f0', margin: 0 }}>
              🕷️ Scraper Settings
            </h1>
            <p style={{ fontSize: 13, color: '#94a3b8', margin: '4px 0 0 0' }}>
              Configure and trigger web scraping jobs
            </p>
          </div>
          <Link href="/" style={{ fontSize: 12, color: '#6366f1', textDecoration: 'none' }}>← Dashboard</Link>
        </div>

        {loadError && (
          <div style={{
            marginBottom: 16,
            padding: '10px 14px',
            background: 'rgba(251,191,36,0.1)',
            border: '1px solid rgba(251,191,36,0.3)',
            borderRadius: 8,
            fontSize: 13,
            color: '#fbbf24',
          }}>
            {loadError}
          </div>
        )}

        {/* Autorun Toggle */}
        <div style={{
          marginBottom: 24,
          padding: 20,
          background: 'rgba(15,23,42,0.8)',
          border: '1px solid rgba(99,102,241,0.3)',
          borderRadius: 8,
          backdropFilter: 'blur(8px)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 4 }}>Scheduled Autorun</div>
              <div style={{ fontSize: 13, color: '#94a3b8' }}>
                SCRAPER_AUTORUN_ENABLED — runs the scrape pipeline on the 2-hour autonomy cycle
              </div>
            </div>
            <button
              onClick={toggleAutorun}
              disabled={!settings}
              style={{
                width: 52,
                height: 28,
                borderRadius: 14,
                border: 'none',
                background: settings?.autorun_enabled ? '#6366f1' : 'rgba(99,102,241,0.2)',
                cursor: settings ? 'pointer' : 'not-allowed',
                position: 'relative',
                transition: 'background 0.2s',
                flexShrink: 0,
              }}
              aria-label={`Toggle autorun ${settings?.autorun_enabled ? 'off' : 'on'}`}
            >
              <span style={{
                position: 'absolute',
                top: 4,
                left: settings?.autorun_enabled ? 28 : 4,
                width: 20,
                height: 20,
                borderRadius: '50%',
                background: '#fff',
                transition: 'left 0.2s',
              }} />
            </button>
          </div>
          <div style={{ marginTop: 8, fontSize: 12, color: settings?.autorun_enabled ? '#34d399' : '#94a3b8' }}>
            {settings === null ? 'Loading...' : settings.autorun_enabled ? '● Autorun enabled' : '○ Autorun disabled'}
          </div>
        </div>

        {/* Manual Scrape Job */}
        <div style={{
          marginBottom: 24,
          padding: 20,
          background: 'rgba(15,23,42,0.8)',
          border: '1px solid rgba(99,102,241,0.3)',
          borderRadius: 8,
          backdropFilter: 'blur(8px)',
        }}>
          <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 12 }}>Manual Scrape Job</div>
          <form onSubmit={submitManualJob} style={{ display: 'flex', gap: 8 }}>
            <input
              type="url"
              value={manualUrl}
              onChange={e => setManualUrl(e.target.value)}
              placeholder="https://example.com/contacts"
              required
              style={{
                flex: 1,
                background: 'rgba(30,27,75,0.8)',
                border: '1px solid rgba(99,102,241,0.4)',
                borderRadius: 8,
                padding: '10px 14px',
                color: '#e2e8f0',
                fontSize: 14,
                outline: 'none',
                fontFamily: 'inherit',
              }}
            />
            <button
              type="submit"
              disabled={submitting || !manualUrl.trim()}
              style={{
                background: submitting ? 'rgba(99,102,241,0.3)' : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                color: '#fff',
                border: 'none',
                borderRadius: 8,
                padding: '10px 20px',
                cursor: submitting ? 'not-allowed' : 'pointer',
                fontSize: 14,
                fontWeight: 600,
                whiteSpace: 'nowrap',
              }}
            >
              {submitting ? 'Queueing...' : 'Scrape Now'}
            </button>
          </form>
          {submitMsg && (
            <div style={{ marginTop: 8, fontSize: 13, color: '#94a3b8' }}>{submitMsg}</div>
          )}
        </div>

        {/* Recent Jobs */}
        <div style={{
          padding: 20,
          background: 'rgba(15,23,42,0.8)',
          border: '1px solid rgba(99,102,241,0.3)',
          borderRadius: 8,
          backdropFilter: 'blur(8px)',
        }}>
          <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 12 }}>Recent Jobs</div>
          {jobs.length === 0 ? (
            <div style={{ color: '#4b5563', fontSize: 13, padding: '16px 0' }}>
              No jobs yet. Use the form above to start a manual scrape.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {jobs.map(job => (
                <div
                  key={job.id}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '1fr auto auto',
                    gap: 12,
                    alignItems: 'center',
                    padding: '10px 12px',
                    background: 'rgba(30,27,75,0.5)',
                    borderRadius: 6,
                    fontSize: 13,
                  }}
                >
                  <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    <div style={{ color: '#6366f1', marginBottom: 2 }}>{job.url}</div>
                    <div style={{ color: '#64748b', fontSize: 11 }}>{job.created_at}</div>
                  </div>
                  <div style={{ color: '#94a3b8', fontSize: 12 }}>
                    {job.result_count !== undefined ? `${job.result_count} results` : '—'}
                  </div>
                  <div style={{
                    padding: '2px 8px',
                    borderRadius: 12,
                    background: `${statusColor(job.status)}22`,
                    color: statusColor(job.status),
                    fontSize: 11,
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: 0.5,
                  }}>
                    {job.status}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
