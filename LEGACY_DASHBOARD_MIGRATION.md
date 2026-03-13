# Legacy Dashboard Migration Ledger

**Source:** `InfinityXOneSystems/XPS_INTELLIGENCE_SYSTEM` → GitHub Pages  
**Target:** `apps/frontend/` in `InfinityXOneSystems/XPS_INTELLIGENCE_PLATFORM`  
**Migration Start:** 2026-03-13  
**Current Mode:** `iframe` (default, see `NEXT_PUBLIC_LEGACY_DASHBOARD_MODE`)

---

## Integration Status Summary

| Metric | Value |
|--------|-------|
| Total features | 17 routes + 17 widgets |
| Bridged (iframe) | 34 |
| Ported (native) | 0 |
| In progress | 0 |
| Test coverage (E2E) | iframe-mode validated |

---

## Feature Migration Status

### Routes

| Route | Legacy File | Status | Test Coverage | Notes |
|-------|-------------|--------|---------------|-------|
| `/` | `dashboard/pages/index.js` | **bridged** | ✅ e2e-iframe | Redirect hub |
| `/leads` | `dashboard/pages/leads.js` | **bridged** | ✅ e2e-iframe | Priority: HIGH |
| `/analytics` | `dashboard/pages/analytics.js` | **bridged** | ✅ e2e-iframe | Priority: HIGH |
| `/crm` | `dashboard/pages/crm.js` | **bridged** | ✅ e2e-iframe | Priority: HIGH, 36KB |
| `/workspace` | `dashboard/pages/workspace.js` | **bridged** | ✅ e2e-iframe | Priority: MEDIUM, 30KB |
| `/studio` | `dashboard/pages/studio.js` | **bridged** | ✅ e2e-iframe | Priority: MEDIUM, 23KB |
| `/intelligence` | `dashboard/pages/intelligence.js` | **bridged** | ✅ e2e-iframe | Priority: MEDIUM |
| `/chat` | `dashboard/pages/chat.js` | **bridged** | ✅ e2e-iframe | Priority: MEDIUM |
| `/connectors` | `dashboard/pages/connectors.js` | **bridged** | ✅ e2e-iframe | Priority: MEDIUM |
| `/trends` | `dashboard/pages/trends.js` | **bridged** | ✅ e2e-iframe | Priority: LOW |
| `/guardian` | `dashboard/pages/guardian.js` | **bridged** | ✅ e2e-iframe | Priority: LOW |
| `/invention-lab` | `dashboard/pages/invention-lab.js` | **bridged** | ✅ e2e-iframe | Priority: LOW |
| `/settings` | `dashboard/pages/settings.js` | **bridged** | ✅ e2e-iframe | Priority: LOW |
| `/admin/*` | `dashboard/pages/admin/` | **bridged** | ✅ e2e-iframe | Priority: LOW |

### Widgets

| Widget | Used In | Status | Test Coverage | Notes |
|--------|---------|--------|---------------|-------|
| LeadTable | `/leads` | **bridged** | ✅ e2e-iframe | Core widget, high priority to port |
| StatsBar | `/leads`, `/analytics` | **bridged** | ✅ e2e-iframe | — |
| ScoreBar | `/leads`, `/crm` | **bridged** | ✅ e2e-iframe | — |
| TierBadge | `/leads`, `/crm` | **bridged** | ✅ e2e-iframe | HOT/WARM/COLD pill |
| FilterControls | `/leads` | **bridged** | ✅ e2e-iframe | Search + dropdowns |
| Pagination | `/leads` | **bridged** | ✅ e2e-iframe | Smart windowed pager |
| AnalyticsCharts | `/analytics` | **bridged** | ✅ e2e-iframe | — |
| CRMPipeline | `/crm` | **bridged** | ✅ e2e-iframe | Largest component |
| ChatInterface | `/chat` | **bridged** | ✅ e2e-iframe | — |
| ConnectorCards | `/connectors` | **bridged** | ✅ e2e-iframe | — |
| GuardianMonitor | `/guardian` | **bridged** | ✅ e2e-iframe | — |
| IntelligenceFeed | `/intelligence` | **bridged** | ✅ e2e-iframe | — |
| InventionLabWorkspace | `/invention-lab` | **bridged** | ✅ e2e-iframe | — |
| SettingsForms | `/settings` | **bridged** | ✅ e2e-iframe | — |
| StudioCanvas | `/studio` | **bridged** | ✅ e2e-iframe | — |
| TrendCharts | `/trends` | **bridged** | ✅ e2e-iframe | — |
| WorkspaceCanvas | `/workspace` | **bridged** | ✅ e2e-iframe | — |

---

## Migration Policy

### Current Phase: Bridge (iframe)
The legacy dashboard is accessible at `/legacy-dashboard` via an `<iframe>` that embeds the live GitHub Pages deployment at `https://infinityxonesystems.github.io/XPS_INTELLIGENCE_SYSTEM/`.

This approach:
- Delivers **zero feature loss** immediately
- **No aesthetic drift** — the legacy UI is preserved exactly as-is
- **No data pipeline duplication** — the iframe reads from the Railway API directly
- Allows native porting to be done incrementally and verified before switching

### Switching to Native Mode
To enable native mode, set the environment variable:
```
NEXT_PUBLIC_LEGACY_DASHBOARD_MODE=native
```

**Parity gate** — native mode MUST NOT be enabled until ALL items in the table above show status `ported` with unit + E2E test coverage. The parity gate is enforced by PR review policy.

### Port Prioritization Order
1. `/leads` + LeadTable + ScoreBar + TierBadge + FilterControls + Pagination + StatsBar (core loop)
2. `/analytics` + AnalyticsCharts
3. `/crm` + CRMPipeline
4. `/workspace` + WorkspaceCanvas
5. `/studio` + StudioCanvas
6. `/chat` + ChatInterface
7. `/intelligence` + IntelligenceFeed
8. `/connectors` + ConnectorCards
9. `/guardian` + GuardianMonitor
10. `/trends` + TrendCharts
11. `/invention-lab` + InventionLabWorkspace
12. `/settings` + SettingsForms
13. `/admin/*`
14. `/` redirect

---

## Acceptance Criteria for Marking a Feature as "ported"

A feature may be changed from `bridged` to `ported` only when:
1. ✅ Native React/Next.js component exists in `apps/frontend/src/`
2. ✅ Component renders identical output to the legacy version (visual snapshot diff ≤ 0.2 threshold)
3. ✅ Data dependencies connect to the same Railway API endpoints
4. ✅ Playwright E2E test covers the component with assertions
5. ✅ Unit/component test exists in `apps/frontend/src/**/*.test.{ts,tsx}`
6. ✅ PR review completed by `@InfinityXOneSystems`

---

## Related Documents

| File | Purpose |
|------|---------|
| `FORENSIC_AUDIT/legacy_dashboard_discovery.md` | Discovery report |
| `FORENSIC_AUDIT/legacy_dashboard_feature_matrix.json` | Machine-readable feature matrix |
| `apps/frontend/src/app/legacy-dashboard/page.tsx` | Integration route |
| `tests/e2e/legacy-dashboard.spec.ts` | Playwright E2E proof tests |
| `_OPS/ARCHITECTURE/SYSTEM_TOPOLOGY.md` | System topology |
