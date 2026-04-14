'use client';

import React from 'react';

interface TopBarProps {
  onToggleChat?: () => void;
  chatOpen?: boolean;
}

export default function TopBar({ onToggleChat, chatOpen }: TopBarProps) {
  return (
    <header
      style={{
        height: 56,
        minHeight: 56,
        background: 'linear-gradient(90deg, #0d1117 0%, #0f1520 100%)',
        borderBottom: '1px solid rgba(99,102,241,0.18)',
        display: 'flex',
        alignItems: 'center',
        padding: '0 16px',
        gap: 12,
        zIndex: 100,
        flexShrink: 0,
      }}
    >
      {/* Logo / Brand */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0 }}>
        <div
          style={{
            width: 32,
            height: 32,
            borderRadius: 8,
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
            <path
              d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"
              stroke="#fff"
              strokeWidth="1.8"
              strokeLinejoin="round"
              fill="rgba(255,255,255,0.15)"
            />
          </svg>
        </div>
        <span
          style={{
            fontSize: 15,
            fontWeight: 700,
            color: '#f1f5f9',
            letterSpacing: '-0.01em',
            whiteSpace: 'nowrap',
          }}
        >
          XPS Intelligence
        </span>
        <span
          style={{
            fontSize: 11,
            fontWeight: 500,
            color: '#6366f1',
            background: 'rgba(99,102,241,0.12)',
            border: '1px solid rgba(99,102,241,0.25)',
            borderRadius: 4,
            padding: '1px 6px',
            whiteSpace: 'nowrap',
          }}
        >
          PLATFORM
        </span>
      </div>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* Status dot */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
        <span
          style={{
            width: 7,
            height: 7,
            borderRadius: '50%',
            background: '#22c55e',
            boxShadow: '0 0 6px #22c55e',
            display: 'inline-block',
          }}
        />
        <span style={{ fontSize: 12, color: '#94a3b8', whiteSpace: 'nowrap' }}>
          System Online
        </span>
      </div>

      {/* Toggle chat button */}
      {onToggleChat && (
        <button
          onClick={onToggleChat}
          title={chatOpen ? 'Hide Agent Panel' : 'Show Agent Panel'}
          style={{
            marginLeft: 8,
            background: chatOpen ? 'rgba(99,102,241,0.2)' : 'transparent',
            border: '1px solid rgba(99,102,241,0.3)',
            borderRadius: 6,
            padding: '5px 10px',
            color: chatOpen ? '#818cf8' : '#94a3b8',
            cursor: 'pointer',
            fontSize: 12,
            fontWeight: 500,
            display: 'flex',
            alignItems: 'center',
            gap: 5,
            transition: 'all 0.15s',
          }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
            <path
              d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2v10z"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinejoin="round"
            />
          </svg>
          Agent
        </button>
      )}
    </header>
  );
}
