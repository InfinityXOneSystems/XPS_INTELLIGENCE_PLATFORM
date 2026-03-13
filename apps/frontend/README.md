# Frontend — XPS Intelligence Platform

> **Status:** ⬜ Pending Phase 1 consolidation  
> **Source:** `XPS-INTELLIGENCE-FRONTEND`  
> **Runtime:** Next.js (React) → Railway  
> **Rule:** Additions only — NO breaking changes to existing UI

## Overview

The Intelligence Frontend provides the primary user interface for the XPS Intelligence Platform. It connects to the Railway-hosted backend API and displays real-time intelligence data, agent status, and system controls.

## Directory Structure (Target)

```
apps/frontend/
├── src/
│   ├── app/          ← Next.js App Router pages
│   ├── components/   ← React components
│   ├── hooks/        ← Custom React hooks
│   ├── lib/          ← API client, utilities
│   └── styles/       ← Global styles
├── public/           ← Static assets
├── tests/            ← Unit tests (Vitest)
├── Dockerfile
├── package.json
├── next.config.ts
└── railway.json
```

## Phase 1 Consolidation Checklist

- [ ] Pull source from `XPS-INTELLIGENCE-FRONTEND` (additions only)
- [ ] Configure Next.js App Router
- [ ] Connect to Railway backend API
- [ ] Set up authentication (JWT)
- [ ] Implement Playwright E2E tests + visual snapshots
- [ ] Configure Railway deployment
- [ ] Set up Vitest for unit tests

## Frontend Rule (MANDATORY)

> **Frontend changes are ADDITIVE ONLY.**  
> No existing component may be removed or have its behavior changed.  
> Only new components, pages, and features may be added.  
> This rule is enforced by CODEOWNERS review.

## Human Gate

This directory will be populated during **Phase 1** after explicit human command to begin consolidation.
