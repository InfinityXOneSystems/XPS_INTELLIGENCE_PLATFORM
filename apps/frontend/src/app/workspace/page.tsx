'use client';
import { useState } from 'react';

type ArtifactType = 'image' | 'video' | 'music' | 'template' | 'chart' | 'lead' | 'web_browse' | 'system' | 'text';

interface ArtifactItem {
  id: string;
  type: ArtifactType;
  title: string;
  content: Record<string, unknown>;
  storageUrl?: string;
}

function ArtifactPanel({ artifact }: { artifact: ArtifactItem }) {
  const renderContent = () => {
    switch (artifact.type) {
      case 'image':
        return artifact.storageUrl ? (
          <img src={artifact.storageUrl} alt={artifact.title} style={{ maxWidth: '100%', borderRadius: 4 }} />
        ) : (
          <div style={{ padding: 16, color: '#666', fontSize: 13 }}>Image: {artifact.title}</div>
        );
      case 'lead': {
        const lead = artifact.content as Record<string, string>;
        return (
          <div style={{ fontSize: 12, lineHeight: 1.6 }}>
            {lead.name && <div><strong>Name:</strong> {lead.name}</div>}
            {lead.email && <div><strong>Email:</strong> {lead.email}</div>}
            {lead.phone && <div><strong>Phone:</strong> {lead.phone}</div>}
            {lead.company && <div><strong>Company:</strong> {lead.company}</div>}
            {lead.score !== undefined && <div><strong>Score:</strong> {(Number(lead.score) * 100).toFixed(0)}%</div>}
          </div>
        );
      }
      case 'chart': {
        const chartData = artifact.content as { labels?: string[]; values?: number[] };
        return (
          <div style={{ fontSize: 12 }}>
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 4, height: 80 }}>
              {(chartData.values || []).slice(0, 8).map((v, i) => (
                <div
                  key={i}
                  title={`${(chartData.labels || [])[i] || i}: ${v}`}
                  style={{
                    flex: 1,
                    background: 'rgba(99,102,241,0.7)',
                    height: `${Math.max(4, (v / Math.max(...(chartData.values || [1]))) * 70)}px`,
                    borderRadius: '2px 2px 0 0',
                  }}
                />
              ))}
            </div>
          </div>
        );
      }
      case 'text':
      case 'system':
      case 'template':
        return (
          <div style={{ fontSize: 12, lineHeight: 1.6, whiteSpace: 'pre-wrap', maxHeight: 120, overflowY: 'auto' }}>
            {String(artifact.content?.text || artifact.content?.content || JSON.stringify(artifact.content, null, 2))}
          </div>
        );
      case 'web_browse':
        return (
          <div style={{ fontSize: 12 }}>
            <div style={{ color: '#6366f1', marginBottom: 4 }}>{String(artifact.content?.url || '')}</div>
            <div style={{ color: '#888', lineHeight: 1.5 }}>{String(artifact.content?.summary || 'Web content')}</div>
          </div>
        );
      default:
        return (
          <pre style={{ fontSize: 11, maxHeight: 100, overflowY: 'auto', margin: 0 }}>
            {JSON.stringify(artifact.content, null, 2)}
          </pre>
        );
    }
  };

  return (
    <div style={{
      border: '1px solid rgba(99,102,241,0.3)',
      borderRadius: 8,
      padding: 12,
      background: 'rgba(15,23,42,0.8)',
      backdropFilter: 'blur(8px)',
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span style={{ fontSize: 11, fontWeight: 600, color: '#6366f1', textTransform: 'uppercase', letterSpacing: 1 }}>
          {artifact.type}
        </span>
        <span style={{ fontSize: 12, color: '#94a3b8' }}>{artifact.title}</span>
      </div>
      <div style={{ color: '#e2e8f0' }}>{renderContent()}</div>
    </div>
  );
}

const DEMO_ARTIFACTS: ArtifactItem[] = [
  {
    id: '1',
    type: 'lead',
    title: 'Sample Lead',
    content: { name: 'Jane Doe', email: 'jane@example.com', company: 'Acme Corp', score: 0.85 },
  },
  {
    id: '2',
    type: 'chart',
    title: 'Lead Scores',
    content: { labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], values: [42, 67, 55, 80, 91] },
  },
  {
    id: '3',
    type: 'text',
    title: 'System Output',
    content: { text: 'Pipeline completed: 12 leads ingested, 10 normalized, 10 scored.\nTop score: 0.95 (contact@bigcorp.com)' },
  },
  {
    id: '4',
    type: 'web_browse',
    title: 'Scraped Page',
    content: { url: 'https://example.com/contacts', summary: '5 contact records found on page.' },
  },
];

export default function WorkspacePage() {
  const [nlInput, setNlInput] = useState('');
  const [artifacts, setArtifacts] = useState<ArtifactItem[]>(DEMO_ARTIFACTS);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<ArtifactType | 'all'>('all');

  const ARTIFACT_TYPES: Array<ArtifactType | 'all'> = ['all', 'lead', 'chart', 'text', 'image', 'web_browse', 'template', 'system'];

  const filtered = filter === 'all' ? artifacts : artifacts.filter(a => a.type === filter);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nlInput.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('/api/v1/llm/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: [{ role: 'user', content: nlInput }] }),
      });
      if (res.ok) {
        const data = await res.json();
        const newArtifact: ArtifactItem = {
          id: Date.now().toString(),
          type: 'text',
          title: 'AI Response',
          content: { text: data.response || 'No response', provider: data.provider },
        };
        setArtifacts(prev => [newArtifact, ...prev]);
      }
    } catch {
      // Backend may not be running in dev
    }
    setLoading(false);
    setNlInput('');
  };

  return (
    <main style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%)',
      color: '#e2e8f0',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      padding: '24px',
    }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        <div style={{ marginBottom: 24, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <h1 style={{ fontSize: 24, fontWeight: 700, color: '#e2e8f0', margin: 0 }}>
              ⚡ XPS Workspace
            </h1>
            <p style={{ fontSize: 13, color: '#94a3b8', margin: '4px 0 0 0' }}>
              Natural language → Artifacts
            </p>
          </div>
          <a
            href="/"
            style={{ fontSize: 12, color: '#6366f1', textDecoration: 'none' }}
          >
            ← Dashboard
          </a>
        </div>

        <form onSubmit={handleSubmit} style={{ marginBottom: 24 }}>
          <div style={{ display: 'flex', gap: 8 }}>
            <textarea
              value={nlInput}
              onChange={e => setNlInput(e.target.value)}
              placeholder="Describe what you want to build, scrape, analyze, or generate..."
              rows={3}
              style={{
                flex: 1,
                background: 'rgba(30,27,75,0.8)',
                border: '1px solid rgba(99,102,241,0.4)',
                borderRadius: 8,
                padding: '12px 16px',
                color: '#e2e8f0',
                fontSize: 14,
                resize: 'vertical',
                outline: 'none',
                fontFamily: 'inherit',
              }}
              onKeyDown={e => { if (e.key === 'Enter' && e.metaKey) handleSubmit(e as unknown as React.FormEvent); }}
            />
            <button
              type="submit"
              disabled={loading || !nlInput.trim()}
              style={{
                background: loading ? 'rgba(99,102,241,0.3)' : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                color: '#fff',
                border: 'none',
                borderRadius: 8,
                padding: '12px 24px',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontSize: 14,
                fontWeight: 600,
                whiteSpace: 'nowrap',
                alignSelf: 'flex-start',
              }}
            >
              {loading ? 'Processing...' : 'Run ⌘↵'}
            </button>
          </div>
        </form>

        <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
          {ARTIFACT_TYPES.map(t => (
            <button
              key={t}
              onClick={() => setFilter(t)}
              style={{
                padding: '4px 12px',
                borderRadius: 20,
                border: '1px solid rgba(99,102,241,0.4)',
                background: filter === t ? 'rgba(99,102,241,0.3)' : 'transparent',
                color: filter === t ? '#e2e8f0' : '#94a3b8',
                cursor: 'pointer',
                fontSize: 12,
                fontWeight: filter === t ? 600 : 400,
              }}
            >
              {t}
            </button>
          ))}
        </div>

        {filtered.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#4b5563', padding: 48 }}>
            No artifacts yet. Enter a command above to get started.
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
            gap: 16,
          }}>
            {filtered.map(artifact => (
              <ArtifactPanel key={artifact.id} artifact={artifact} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
