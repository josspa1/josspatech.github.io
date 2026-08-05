# Local shows / flea markets — automated trust (deferred)

**Status:** Deferred idea — not scheduled. Captured 2026-08-04.  
**Apps:** Primarily **HHH** and **CVC** (collectors hunting local shows). Optional later surface on josspatech.com.  
**Related:** Existing in-app ZIP flea tips/alerts (`fleaMarketAlerts` in CVC; HHH first-use flea tips). This doc is about **scaling supply + spam control**, not the basic ZIP UI.

**Pointer from future backlog:** [FUTURE_WEBSITE_IDEAS.md](./FUTURE_WEBSITE_IDEAS.md) → “Local shows / flea markets (automated trust)”.

---

## Problem

Collectors want **flea markets, antique shows, swap meets** with **dates and times** near them.

Constraints Joe locked in conversation:

- Prefer **search by ZIP** (cheap) — avoid per-search Maps/Places API costs.
- Must **not** become free advertising for random shops or spammy “always open” storefronts.
- Vetting must be **automated trust**, not Joe approving every listing.

---

## Product shape (when built)

1. **Event rows** in PocketBase (or similar): name, `starts_at`, `ends_at`, ZIP (and optional city), source URL, `trust_score`, `status` (`live` / `rejected` / `quarantine`), source id.
2. **App search:** filter by ZIP (or ZIP3) + date window. Optional offline ZIP→lat table for radius — **no live geocoding per search**.
3. **Ingest workers** (cron): pull allowlisted calendars / ICS / RSS / HTML; upsert candidates; score; auto-publish or drop.
4. **Recurring series:** once a show is trusted (“3rd Sunday, ZIP 06457”), auto-generate the next N months.

Open “list your business” without proof is explicitly **out of scope** for v1.

---

## Automated trust (core idea)

Every candidate gets a **trust score** from machine checks. Then:

| Score band | Action |
|---|---|
| High | `status=live` — shown in ZIP search |
| Low | `status=rejected` — never shown |
| Middle | `status=quarantine` — rare human peek |

**Trust is not “this person is nice.”** It is **signals that correlate with real dated public shows.**

Joe’s ongoing role: maintain **allowlists** and thresholds; clear quarantine occasionally. **Not** open every URL by hand.

---

## Who runs each check?

| Check | Runner | How |
|---|---|---|
| URL loads | **Worker** | HTTP GET/HEAD; 200 → boost; fail → penalize/drop |
| Looks like an event page | **Worker** heuristics; optional **AI** | Worker: `/event`, schema.org Event, dates in HTML, ICS link. Borderline → optional Gemini classify |
| Same show last year + same ZIP | **Worker** | DB fuzzy name + ZIP + ~1 year ago → boost |
| “Visit our mall, always open” | **Worker** keywords/rules; optional **AI** | No single end date + retail phrasing → penalize |
| Same submitter posted 20 events this week | **Worker** | Count by account / IP / feed id → hard reject |
| Source on allowlist / `.gov` | **Worker** | Config list Joe maintains rarely |
| Dedupe same weekend + ZIP + name | **Worker** | Merge instead of multiply |

**AI is optional and for fuzzy text/pages only.** Scoring math, HTTP, and DB history are workers.

---

## Example score walkthrough

**Good:** “Maple Street Antique Show — Sat Apr 12, 2026, 8am–3pm — ZIP 06457 — https://anytown.gov/events/…”  
Allowlist/gov + real datetime + ZIP + URL OK + seen last year → **auto-live**.

**Bad:** “Best Antiques LLC — open 7 days — buy now — ZIP 10001”  
No dated event shape + shop language + no trusted source → **auto-reject**.

---

## Ingest (automated supply)

Preferred order:

1. Allowlisted ICS/RSS/HTML calendars (cities, fairgrounds, known promoters, collector orgs).
2. Series expansion from approved templates.
3. Change detection on known URLs (date moved → update).
4. Later: email-in from organizer domain; flyer OCR as draft only (still scored).

Do **not** start with open-web scrape of every Craigslist-style ad.

---

## Cost posture

- ZIP search: DB only (cheap).
- Workers: Cloudflare/ cron free tiers until volume grows.
- Optional AI classify: pay-per-use on borderline rows only.
- Avoid Google Places / geocode-per-search.

---

## Anti-goals

- Free perpetual storefront ads.
- Manual approve queue for every US flea meet.
- AI as the only gate (use as score adjuster).
- Building before HHH/CVC core store + support load justifies local-events investment.

---

## Suggested v1 (when un-deferred)

1. Schema + ZIP search against curated/imported `live` rows.  
2. One nightly worker + small allowlist (even 5–10 sources).  
3. Trust score with publish/reject thresholds; quarantine empty most weeks.  
4. Recurring series generator for the best sources.

---

## Open decisions (leave for later)

- Exact numeric weights and thresholds.
- Shared HHH+CVC event DB vs per-app.
- Whether organizers ever get a claim portal (post–automated-trust maturity).
