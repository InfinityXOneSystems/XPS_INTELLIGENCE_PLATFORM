'use client';

import React from 'react';

export type SectionId =
  | 'dashboard'
  | 'leads'
  | 'analytics'
  | 'crm'
  | 'workspace'
  | 'studio'
  | 'intelligence'
  | 'connectors'
  | 'trends'
  | 'guardian'
  | 'invention-lab'
  | 'settings'
  | 'admin';

interface NavItem {
  id: SectionId;
  label: string;
  icon: React.ReactNode;
  group?: string;
}

const NAV_ITEMS: NavItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    group: 'OVERVIEW',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <rect x="3" y="3" width="7" height="7" rx="1" stroke="currentColor" strokeWidth="1.8" />
        <rect x="14" y="3" width="7" height="7" rx="1" stroke="currentColor" strokeWidth="1.8" />
        <rect x="3" y="14" width="7" height="7" rx="1" stroke="currentColor" strokeWidth="1.8" />
        <rect x="14" y="14" width="7" height="7" rx="1" stroke="currentColor" strokeWidth="1.8" />
      </svg>
    ),
  },
  {
    id: 'leads',
    label: 'Leads',
    group: 'INTELLIGENCE',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <circle cx="9" cy="7" r="4" stroke="currentColor" strokeWidth="1.8" />
        <path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    id: 'analytics',
    label: 'Analytics',
    group: 'INTELLIGENCE',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    id: 'crm',
    label: 'CRM',
    group: 'INTELLIGENCE',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <rect x="2" y="7" width="20" height="14" rx="2" stroke="currentColor" strokeWidth="1.8" />
        <path d="M16 3H8a2 2 0 00-2 2v2h12V5a2 2 0 00-2-2z" stroke="currentColor" strokeWidth="1.8" />
      </svg>
    ),
  },
  {
    id: 'workspace',
    label: 'Workspace',
    group: 'CREATE',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <polygon points="12 2 2 7 12 12 22 7 12 2" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
        <polyline points="2 17 12 22 22 17" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <polyline points="2 12 12 17 22 12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    id: 'studio',
    label: 'Studio',
    group: 'CREATE',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.8" />
        <path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    id: 'intelligence',
    label: 'Intelligence',
    group: 'CREATE',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <path d="M9.5 2A2.5 2.5 0 017 4.5v1A2.5 2.5 0 009.5 8h5A2.5 2.5 0 0017 5.5v-1A2.5 2.5 0 0014.5 2h-5z" stroke="currentColor" strokeWidth="1.8" />
        <path d="M6 10a6 6 0 100 12 6 6 0 000-12zM18 10a6 6 0 100 12 6 6 0 000-12z" stroke="currentColor" strokeWidth="1.8" />
        <path d="M6 16l2-2 2 2M18 16l-2-2-2 2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    id: 'connectors',
    label: 'Connectors',
    group: 'INTEGRATIONS',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
        <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    id: 'trends',
    label: 'Trends',
    group: 'INTEGRATIONS',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        <polyline points="17 6 23 6 23 12" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    id: 'guardian',
    label: 'Guardian',
    group: 'SYSTEM',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    id: 'invention-lab',
    label: 'Invention Lab',
    group: 'SYSTEM',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <path d="M9 3h6M9 3v10l-4 5h14l-4-5V3M9 3H7M15 3h2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M9 17h6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    id: 'settings',
    label: 'Settings',
    group: 'SYSTEM',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.8" />
        <path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z" stroke="currentColor" strokeWidth="1.8" />
      </svg>
    ),
  },
  {
    id: 'admin',
    label: 'Admin',
    group: 'SYSTEM',
    icon: (
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
        <rect x="3" y="11" width="18" height="11" rx="2" stroke="currentColor" strokeWidth="1.8" />
        <path d="M7 11V7a5 5 0 0110 0v4" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      </svg>
    ),
  },
];

interface LeftSidebarProps {
  activeSection: SectionId;
  onSectionChange: (id: SectionId) => void;
}

export default function LeftSidebar({ activeSection, onSectionChange }: LeftSidebarProps) {
  // Group items by group label
  const groups = NAV_ITEMS.reduce<Record<string, NavItem[]>>((acc, item) => {
    const g = item.group ?? 'OTHER';
    if (!acc[g]) acc[g] = [];
    acc[g].push(item);
    return acc;
  }, {});

  const groupOrder = ['OVERVIEW', 'INTELLIGENCE', 'CREATE', 'INTEGRATIONS', 'SYSTEM'];

  return (
    <nav
      style={{
        width: 220,
        minWidth: 220,
        background: '#0d1117',
        borderRight: '1px solid rgba(99,102,241,0.12)',
        display: 'flex',
        flexDirection: 'column',
        overflowY: 'auto',
        overflowX: 'hidden',
        padding: '12px 0',
        flexShrink: 0,
      }}
    >
      {groupOrder.map((groupName) => {
        const items = groups[groupName];
        if (!items) return null;
        return (
          <div key={groupName} style={{ marginBottom: 4 }}>
            <div
              style={{
                fontSize: 10,
                fontWeight: 600,
                color: 'rgba(148,163,184,0.5)',
                letterSpacing: '0.08em',
                padding: '10px 16px 4px',
                userSelect: 'none',
              }}
            >
              {groupName}
            </div>
            {items.map((item) => {
              const isActive = activeSection === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onSectionChange(item.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    width: '100%',
                    padding: '8px 14px',
                    margin: '1px 6px',
                    width: 'calc(100% - 12px)',
                    background: isActive
                      ? 'linear-gradient(90deg, rgba(99,102,241,0.2), rgba(99,102,241,0.08))'
                      : 'transparent',
                    border: isActive ? '1px solid rgba(99,102,241,0.25)' : '1px solid transparent',
                    borderRadius: 6,
                    color: isActive ? '#a5b4fc' : '#94a3b8',
                    cursor: 'pointer',
                    fontSize: 13,
                    fontWeight: isActive ? 600 : 400,
                    textAlign: 'left',
                    transition: 'all 0.15s',
                    position: 'relative',
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      (e.currentTarget as HTMLButtonElement).style.background =
                        'rgba(99,102,241,0.07)';
                      (e.currentTarget as HTMLButtonElement).style.color = '#cbd5e1';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
                      (e.currentTarget as HTMLButtonElement).style.color = '#94a3b8';
                    }
                  }}
                >
                  {/* Active indicator bar */}
                  {isActive && (
                    <span
                      style={{
                        position: 'absolute',
                        left: 0,
                        top: '20%',
                        height: '60%',
                        width: 3,
                        borderRadius: '0 2px 2px 0',
                        background: '#6366f1',
                      }}
                    />
                  )}
                  <span
                    style={{
                      color: isActive ? '#818cf8' : 'inherit',
                      display: 'flex',
                      alignItems: 'center',
                      flexShrink: 0,
                    }}
                  >
                    {item.icon}
                  </span>
                  <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {item.label}
                  </span>
                </button>
              );
            })}
          </div>
        );
      })}

      {/* Bottom spacer with version */}
      <div style={{ flex: 1 }} />
      <div
        style={{
          padding: '12px 16px',
          borderTop: '1px solid rgba(99,102,241,0.1)',
          marginTop: 8,
        }}
      >
        <div style={{ fontSize: 10, color: 'rgba(148,163,184,0.4)', letterSpacing: '0.05em' }}>
          XPS INTELLIGENCE v0.1
        </div>
      </div>
    </nav>
  );
}
