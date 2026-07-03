# Admin Dashboard — Page Map & KV Quota Rules

Live: https://josspatech.com/admin/

## Pages

| URL | File | Contents |
|-----|------|----------|
| `/admin/` | `index.html` | Control Center hub — PB login, nav cards, **Refresh all Light**, backup + GitHub static panels, brief ops status |
| `/admin/app-pbj.html` | `app-pbj.html` | **PBJ all-in-one** — ship version strip, worker, OCR quota, thresholds, Teller, OpenCellID, capacity, cron |
| `/admin/app-hhh.html` | `app-hhh.html` | **HHH all-in-one** — ship version strip, worker, partner referrals, JJ report, thresholds, capacity |
| `/admin/app-cvc.html` | `app-cvc.html` | **CVC all-in-one** — ship version strip, worker, thresholds, capacity |
| `/admin/flywheel.html` | `flywheel.html` | PocketBase crowd-data grid, services, cron, capacity, founder economics, maintenance (+ backup/GitHub static panels) |
| `/admin/workers.html` | `workers.html` | Worker Monitoring PBJ/HHH/CVC + Thresholds & Baselines |
| `/admin/referrals.html` | `referrals.html` | HHH Partner Referrals — All stats (Joe) + JJ shareable tab + **JJ report (cache only)** |
| `/admin/ocr-quota.html` | `ocr-quota.html` | PBJ OCR quota, Teller status, OpenCellID quota |
| `/admin/josspatech-dashboard.html` | redirect | → `index.html` (backward compat) |

## Shared assets

- `shared/admin.css` — common styles (extracted from monolith)
- `shared/admin-common.js` — PB auth, session, **sessionStorage stats cache** (`wm`, `ocr`, `ref`, `fw`), stale-data banner (>24h), showDashboard, hub brief status
- `shared/admin-nav.js` — top nav + **footer link to this file** on every page
- `shared/admin-app.js` — all panel logic (preserved from monolith)
- `shared/ship-versions.json` — **static** shipped app + worker commit per app (update at ship time)
- `shared/backup-status.json` — **static** local HHH backup file mtime/size (no cloud cost)
- `shared/github-usage.json` — **static** repo pack sizes (no GitHub API from browser)

## Shared session cache

Worker stats (`wmCache`), PBJ OCR (`ocrQuotaCache`), and HHH referrals (`refLastData`) are written to `sessionStorage` on every manual refresh. Navigating between `workers.html`, `app-pbj.html`, `ocr-quota.html`, etc. **reuses cached data** — no KV re-fetch until you click Refresh. Refresh on any page updates the cache for all pages in the same browser tab.

Keys: `pbj_dash_cache_wm`, `pbj_dash_cache_ocr`, `pbj_dash_cache_ref`, `pbj_dash_cache_fw`

## Stale-data warning

If **any** cached slot (`wm`, `ocr`, `ref`, `fw`) has a `fetchedAt` older than **24 hours**, an amber banner appears: *"Some data may be stale — Refresh recommended"*. Pure JS — no fetch.

## Refresh tiers (manual by default)

| Label | Worker action | Approx KV reads |
|-------|---------------|-----------------|
| **Light** | `GET /` health only | 0 per worker |
| **Medium** | Today's quota counters (`/ops/stats` or `/ocr/quota/stats`) | ~6 per worker (~18 PBJ+HHH+CVC) |
| **Heavy · KV** | 12-month `cost_history` rollups | ~15–25 per worker (~60 total) |

**Do not** re-enable auto-polling of Worker KV or global `COST_GRAPH_ENABLED` — burned ~113k KV reads/day at 1m intervals.

## Hub: Refresh all Light

On `index.html`, **Refresh all Light** runs worker health ping for PBJ + HHH + CVC, updates shared `wmCache` in sessionStorage, and refreshes hub brief status via `updateOpsAlertBanner()`. Badge: **Light · ~0–18 KV reads per worker** (Light = 0; Medium would be ~6 each).

## JJ report (cache only)

On `referrals.html` and `app-hhh.html`: **JJ report** opens a printable window from `refLastData` / sessionStorage — **no extra Worker fetch**. Commerce + repair only; optional *Include resources* checkbox; eBay never included. Label: **Light · cache only**.

## Ship version strip (app pages)

`app-pbj.html`, `app-hhh.html`, `app-cvc.html` read `shared/ship-versions.json` and show:

**Shipped: app X · worker Y**

Update JSON at ship time (see below).

## Static JSON — update at ship / backup time

| File | When to update | How |
|------|----------------|-----|
| `shared/ship-versions.json` | Every app or worker deploy | Edit `apps.pbj` / `apps.hhh` / `apps.cvc` — `appVersion`, `appBuild`, `workerCommit`, `shippedAt` |
| `shared/backup-status.json` | After local HHH zip backup | `.\scripts\update-backup-status.ps1` or `-ZipPath "…\HHH-backup-YYYY-MM-DD.zip"` |
| `shared/github-usage.json` | After repo cleanup or monthly | `.\scripts\update-github-usage.ps1` (`git count-objects -vH` on site + PBJ repos) |

Commit all three JSON files to `josspatech.github.io` main with the dashboard HTML.

## GitHub usage panel

Hub + flywheel maintenance show pack sizes from `shared/github-usage.json`. Browser **cannot** call GitHub API without a token — manual/script refresh only. Seeded post-cleanup: PBJ ~144 MB, site ~125 MB, total ~270 MB.

## Backup status panel

Hub + flywheel show last local HHH backup from `shared/backup-status.json`. Label: **static JSON · no cloud cost**.

## Ops alert banner

Uses cached `wmCache` / `ocrQuotaCache` when available. On hub load: health ping + cron heartbeat only — no automatic `/ops/stats` or `/ocr/quota/stats` poll.

## PocketBase grid (flywheel page only)

Manual **Refresh grid** by default. Optional auto-refresh uses PocketHost `/api` only — not Worker KV.
