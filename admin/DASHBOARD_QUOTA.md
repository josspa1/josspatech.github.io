# Admin Dashboard — Page Map & KV Quota Rules

Live: https://josspatech.com/admin/

## Pages

| URL | File | Contents |
|-----|------|----------|
| `/admin/` | `index.html` | Control Center hub — PB login, nav cards, brief ops status (health ping only, no KV on load) |
| `/admin/app-pbj.html` | `app-pbj.html` | **PBJ all-in-one** — worker, OCR quota, thresholds, Teller, OpenCellID, capacity, cron |
| `/admin/app-hhh.html` | `app-hhh.html` | **HHH all-in-one** — worker, partner referrals, thresholds, capacity |
| `/admin/app-cvc.html` | `app-cvc.html` | **CVC all-in-one** — worker, thresholds, capacity |
| `/admin/flywheel.html` | `flywheel.html` | PocketBase crowd-data grid, services, cron, capacity, founder economics, maintenance |
| `/admin/workers.html` | `workers.html` | Worker Monitoring PBJ/HHH/CVC + Thresholds & Baselines |
| `/admin/referrals.html` | `referrals.html` | HHH Partner Referrals — All stats (Joe) + JJ shareable tab |
| `/admin/ocr-quota.html` | `ocr-quota.html` | PBJ OCR quota, Teller status, OpenCellID quota |
| `/admin/josspatech-dashboard.html` | redirect | → `index.html` (backward compat) |

## Shared assets

- `shared/admin.css` — common styles (extracted from monolith)
- `shared/admin-common.js` — PB auth, session, **sessionStorage stats cache** (`wm`, `ocr`, `ref`), showDashboard, hub brief status
- `shared/admin-nav.js` — top nav: Control Center | Workers | Referrals | OCR | Flywheel · **Apps: PBJ | HHH | CVC**
- `shared/admin-app.js` — all panel logic (preserved from monolith)

## Shared session cache

Worker stats (`wmCache`), PBJ OCR (`ocrQuotaCache`), and HHH referrals (`refLastData`) are written to `sessionStorage` on every manual refresh. Navigating between `workers.html`, `app-pbj.html`, `ocr-quota.html`, etc. **reuses cached data** — no KV re-fetch until you click Refresh. Refresh on any page updates the cache for all pages in the same browser tab.

Keys: `pbj_dash_cache_wm`, `pbj_dash_cache_ocr`, `pbj_dash_cache_ref`

## Refresh tiers (manual by default)

| Label | Worker action | Approx KV reads |
|-------|---------------|-----------------|
| **Light** | `GET /` health only | 0 per worker |
| **Medium** | Today's quota counters (`/ops/stats` or `/ocr/quota/stats`) | ~6 per worker (~18 PBJ+HHH+CVC) |
| **Heavy · KV** | 12-month `cost_history` rollups | ~15–25 per worker (~60 total) |

**Do not** re-enable auto-polling of Worker KV or global `COST_GRAPH_ENABLED` — burned ~113k KV reads/day at 1m intervals.

## Ops alert banner

Uses cached `wmCache` / `ocrQuotaCache` when available. On hub load: health ping + cron heartbeat only — no automatic `/ops/stats` or `/ocr/quota/stats` poll.

## PocketBase grid (flywheel page only)

Manual **Refresh grid** by default. Optional auto-refresh uses PocketHost `/api` only — not Worker KV.
