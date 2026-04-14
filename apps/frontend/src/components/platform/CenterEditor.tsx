'use client';

import React from 'react';
import type { SectionId } from './LeftSidebar';

const LEGACY_BASE_URL =
  process.env.NEXT_PUBLIC_LEGACY_DASHBOARD_URL ||
  'https://infinityxonesystems.github.io/XPS_INTELLIGENCE_SYSTEM';

/** Map each section to the legacy dashboard path fragment */
const SECTION_PATH: Record<SectionId, string> = {
  dashboard: '/',
  leads: '/leads',
  analytics: '/analytics',
  crm: '/crm',
  workspace: '/workspace',
  studio: '/studio',
  intelligence: '/intelligence',
  connectors: '/connectors',
  trends: '/trends',
  guardian: '/guardian',
  'invention-lab': '/invention-lab',
  settings: '/settings',
  admin: '/admin',
};

const SECTION_LABELS: Record<SectionId, string> = {
  dashboard: 'Dashboard',
  leads: 'Leads',
  analytics: 'Analytics',
  crm: 'CRM Pipeline',
  workspace: 'Workspace',
  studio: 'Studio',
  intelligence: 'Intelligence',
  connectors: 'Connectors',
  trends: 'Trends',
  guardian: 'Guardian',
  'invention-lab': 'Invention Lab',
  settings: 'Settings',
  admin: 'Admin',
};

// sandbox mirrors the value in legacy-dashboard/page.tsx
const IFRAME_SANDBOX =
  'allow-scripts allow-same-origin allow-forms allow-popups allow-popups-to-escape-sandbox';

interface CenterEditorProps {
  section: SectionId;
}

export default function CenterEditor({ section }: CenterEditorProps) {
  const path = SECTION_PATH[section] ?? '/';
  // Trim trailing slash from base so we don't end up with double-slash
  const base = LEGACY_BASE_URL.replace(/\/$/, '');
  const iframeSrc = path === '/' ? `${base}/` : `${base}${path}`;

  return (
    <main
      data-testid="center-editor"
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        background: '#0a0e1a',
        position: 'relative',
      }}
    >
      {/* Breadcrumb strip */}
      <div
        style={{
          height: 36,
          minHeight: 36,
          background: '#0d1117',
          borderBottom: '1px solid rgba(99,102,241,0.1)',
          display: 'flex',
          alignItems: 'center',
          padding: '0 16px',
          gap: 6,
          flexShrink: 0,
        }}
      >
        <span style={{ fontSize: 11, color: 'rgba(148,163,184,0.5)' }}>XPS</span>
        <span style={{ fontSize: 11, color: 'rgba(148,163,184,0.3)' }}>›</span>
        <span style={{ fontSize: 11, color: '#94a3b8', fontWeight: 500 }}>
          {SECTION_LABELS[section]}
        </span>

        {/* Right: editor badge */}
        <div style={{ flex: 1 }} />
        <span
          style={{
            fontSize: 10,
            color: 'rgba(99,102,241,0.7)',
            background: 'rgba(99,102,241,0.08)',
            border: '1px solid rgba(99,102,241,0.15)',
            borderRadius: 4,
            padding: '1px 6px',
            letterSpacing: '0.05em',
          }}
        >
          EDITOR
        </span>
      </div>

      {/* Legacy iframe fills the rest */}
      <iframe
        key={iframeSrc}
        data-testid="center-editor-iframe"
        src={iframeSrc}
        title={`XPS Intelligence — ${SECTION_LABELS[section]}`}
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
