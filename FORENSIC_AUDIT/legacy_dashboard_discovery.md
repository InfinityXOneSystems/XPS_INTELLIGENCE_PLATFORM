# Legacy Dashboard Discovery Report

**Source Repo:** `InfinityXOneSystems/XPS_INTELLIGENCE_SYSTEM`  
**GitHub Pages URL:** https://infinityxonesystems.github.io/XPS_INTELLIGENCE_SYSTEM/  
**Discovery Date:** 2026-03-13  
**Auditor:** GitHub Copilot (Infinity Orchestrator)  
**Commit SHA Pinned:** `c706181899cc7f73af0f00a5f2d50ce0d9f43dc9`

---

## 1. GitHub Pages Source Discovery

### Serving Mechanism
The GitHub Pages site is produced by the **`dashboard/` Next.js application** in the `XPS_INTELLIGENCE_SYSTEM` repository. It is built and deployed by the workflow:

- **Workflow file:** `.github/workflows/nextjs.yml` ("Deploy Next.js site to Pages")
- **Trigger:** Push to `main` branch (paths: `dashboard/**`, `data/**`, `leads/**`) + `workflow_dispatch`
- **Build tool:** `next build` with `output: 'export'` (static export)
- **Artifact path:** `dashboard/out/` (uploaded via `actions/upload-pages-artifact@v3`)
- **Deploy action:** `actions/deploy-pages@v4`
- **Environment name:** `github-pages`

### Additional Static Assets
- `pages/index.html` — a standalone static Lead Dashboard HTML page (fetches data from Railway API or local JSON fallback)
- `pages/port_st_lucie_proof.html` — a proof-of-concept HTML page for Port St. Lucie lead results
- `pages/data/scored_leads.json` — scored leads JSON (data file)

---

## 2. Dashboard Application Stack

| Property | Value |
|----------|-------|
| Framework | Next.js 15.5.10 (App Router + Pages Router) |
| Language | JavaScript (React) |
| Rendering | Static Export (`next export`) |
| Deployment | GitHub Pages (`/XPS_INTELLIGENCE_SYSTEM/` base path) |
| API URL | `https://xps-intelligence.up.railway.app` |
| Gateway URL | `https://xps-intelligence.up.railway.app` |
| Node version | 20 |

---

## 3. Route Inventory

All routes discovered in `dashboard/pages/`:

| Route | File | Description |
|-------|------|-------------|
| `/` | `pages/index.js` | Dashboard home — redirect to main dashboard |
| `/analytics` | `pages/analytics.js` | Analytics & reporting view |
| `/chat` | `pages/chat.js` | AI chat interface |
| `/connectors` | `pages/connectors.js` | Data source connectors management |
| `/crm` | `pages/crm.js` | Customer Relationship Management (lead lifecycle) |
| `/guardian` | `pages/guardian.js` | System Guardian / health monitor |
| `/intelligence` | `pages/intelligence.js` | Intelligence engine dashboard |
| `/invention-lab` | `pages/invention-lab.js` | Invention Lab / R&D workspace |
| `/leads` | `pages/leads.js` | Lead list, search, filter, score |
| `/settings` | `pages/settings.js` | Settings center |
| `/studio` | `pages/studio.js` | Studio / content creation workspace |
| `/trends` | `pages/trends.js` | Market trends viewer |
| `/workspace` | `pages/workspace.js` | Workspace / execution canvas |
| `/admin/*` | `pages/admin/` | Admin panel sub-routes |
| `/404` | `pages/404.js` | Custom 404 page |

---

## 4. UI Widgets / Components

Discovered in `dashboard/components/`:

| Component Area | Description |
|----------------|-------------|
| Lead table | Sortable/filterable lead grid with score bars and tier badges |
| Stats bar | Summary cards: Total, Hot (≥75), Warm (50–74), Cold (<50) |
| Score bar | Visual score progress bar with tier-based color coding |
| Tier badge | Color-coded tier pill (HOT/WARM/COLD) |
| Filter controls | Search input + dropdowns: Tier, Industry, State, Per-page |
| Pagination | Smart page navigator with ellipsis |
| Nav sidebar/header | Global navigation across dashboard sections |
| Analytics charts | Lead trend charts (analytics.js) |
| CRM pipeline | Lead lifecycle kanban/pipeline (crm.js) |
| Chat interface | AI-powered chat UI (chat.js) |
| Connector cards | Integration/connector management cards (connectors.js) |
| Guardian monitor | System health status panel (guardian.js) |
| Intelligence feed | Intelligence engine results (intelligence.js) |
| Invention Lab | R&D workspace panels (invention-lab.js) |
| Settings forms | Configuration panels (settings.js) |
| Studio canvas | Content creation workspace (studio.js) |
| Trend charts | Market trend visualizations (trends.js) |
| Workspace canvas | Execution workspace (workspace.js) |

---

## 5. Data Dependencies

| Data Source | Type | URL / Path |
|-------------|------|-----------|
| Railway REST API | Live | `https://xps-intelligence.up.railway.app/api/leads?limit=2000` |
| Scored leads JSON | Static fallback | `./data/scored_leads.json` (relative to page) |
| Scoring report JSON | Static | `./data/scoring_report.json` |
| Railway API Gateway | Live | `https://xps-intelligence.up.railway.app` |

Data fetch strategy: Railway API with 8-second timeout, fallback to local JSON.

---

## 6. Build Pipeline

```
Push to main (dashboard/** or data/** or leads/**)
  └─► nextjs.yml workflow
        ├─► npm ci (dashboard/)
        ├─► Copy leads/scored_leads.json → dashboard/public/data/
        ├─► Copy leads/scoring_report.json → dashboard/public/data/
        ├─► next build (with NEXT_PUBLIC_BASE_PATH, NEXT_PUBLIC_API_URL)
        ├─► touch out/.nojekyll
        └─► upload-pages-artifact → deploy-pages → GitHub Pages
```

---

## 7. Integration Decision

| Factor | Value |
|--------|-------|
| Integration mode | `iframe` (default, pending native parity) |
| Feature flag | `NEXT_PUBLIC_LEGACY_DASHBOARD_MODE=iframe\|native` |
| iframe URL | `https://infinityxonesystems.github.io/XPS_INTELLIGENCE_SYSTEM/` |
| Target route | `/legacy-dashboard` in `apps/frontend/` |
| Native re-implementation | Deferred — tracked in `LEGACY_DASHBOARD_MIGRATION.md` |

The legacy dashboard is a fully functional GitHub Pages site. The iframe integration provides immediate access with zero feature loss. Native porting is tracked as a migration effort in the ledger.

---

## 8. Related Files

| File | Purpose |
|------|---------|
| `FORENSIC_AUDIT/legacy_dashboard_feature_matrix.json` | Machine-readable feature inventory |
| `LEGACY_DASHBOARD_MIGRATION.md` | Migration ledger (bridged/ported status per feature) |
| `apps/frontend/src/app/legacy-dashboard/page.tsx` | Integration route |
| `tests/e2e/legacy-dashboard.spec.ts` | Playwright E2E proof tests |
| `_OPS/ARCHITECTURE/SYSTEM_TOPOLOGY.md` | Updated system topology |
