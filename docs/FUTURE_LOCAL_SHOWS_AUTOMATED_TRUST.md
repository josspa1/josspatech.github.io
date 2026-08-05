# Local shows / flea markets — automated trust (deferred)

**Status:** Deferred idea — not scheduled. Captured 2026-08-04; expanded 2026-08-05.  
**Apps:** Primarily **HHH** and **CVC** (collectors hunting local shows). Optional later surface on josspatech.com.  
**Related:** Existing in-app ZIP flea tips/alerts (`fleaMarketAlerts` in CVC; HHH first-use flea tips / `@hhh_flea_market_events`). This doc covers **product phasing, seed catalog, live feed value, date freshness, and spam control**.

**Pointer from future backlog:** [FUTURE_WEBSITE_IDEAS.md](./FUTURE_WEBSITE_IDEAS.md) → “Local shows / flea markets (automated trust)”.

**Explicitly rejected:** Nightly nationwide search of the whole country for every flea meet (Joe removed an earlier in-app approach for that reason). Discovery scales later via **seed + sync + self-serve**, not open-web crawl-everything.

---

## Problem

Collectors want **flea markets, antique shows, swap meets** with **dates and times** near them — including when **traveling** (they may not know the local famous meet by name).

Constraints Joe locked:

- Prefer **search by ZIP** (cheap) — avoid per-search Maps/Places API costs.
- Must **not** become free advertising for random shops or spammy “always open” storefronts.
- Vetting for user-submitted / harvested long-tail must be **automated trust**, not Joe approving every listing.
- A paid **live feed** should be a real reason to buy/renew — not a thin mirror of sites Google already finds.

---

## Product value (why not “just Google?”)

**A list of Brimfield + link to brimfield.com is not enough to charge for.** Google already wins bare “famous show + dates.”

What we sell instead:

| Value | Why Google is weak here |
|---|---|
| **Personalized feed** | Shows near *my* ZIP / trip window in one place |
| **Traveler discovery** | “I’m in CT Sunday — what’s on?” without knowing Elephant’s Trunk by name |
| **Collector context** | Filter to horology / coins / cards / mixed — less junk tourism noise |
| **Alerts** | “Trunk this Sunday” / “Brimfield in 10 days” next to hunt / Offline Show Pack |
| **In-show tools** | Calendar is the *door*; Identify, offline pack, BLE want-list are the *booth* |
| **Long-tail later** | New/lesser meets that aren’t casually Googled by name |

**Rule of thumb:** Never sell “we have Brimfield’s dates.” Sell “we tell you which meets matter *for your hunt this month*, then help you work the aisle.”

Seed flagships are **credibility and coverage** so the feed isn’t empty — not the product themselves.

---

## Phased plan (locked direction)

### Phase 1 — Seed catalog + ZIP live feed
- Curate **well-known recurring** shows (national + strong regional) with verifiable official URLs.
- Optionally add **lesser-known but verified** meets (public calendar / organizer site) — not random malls.
- Ship as **live feed** in-app (Pro / purchase reason): near my ZIP, upcoming window, alerts.
- Storage: start as **JSON seed in repo** (~KB–low hundreds KB for dozens–hundreds of shows); move hot updates to **PocketBase** so dates can change without an App Store release.
- **No** nationwide nightly discovery crawl.

**Seed examples (illustrative):**
- **Elephant’s Trunk–style** — Sundays, season window, ZIP, official site  
- **Brimfield–style** — named weeks each year (published months ahead)  
- **Atlantique City–style** — fixed show weekends on organizer calendar  

### Phase 2 — Keep seed dates fresh (without hand-editing forever)

| Show type | How dates stay current |
|---|---|
| Simple weekly/monthly | **Recurrence rule** → expand next 6–12 months in app or worker |
| Big named events (Brimfield, Atlantique, etc.) | Rule **+ allowlisted sync** of *their* ICS/HTML page only |
| Changed / one-off season | Sync update or mark stale |

Also: **stale detection** — past dates with no future instance → hide / `needs_refresh`; optional periodic seed-health pass.

Allowlisted sync ≠ search America. It is refresh **N known URLs** (e.g. 20–50 flagships).

### Phase 3 — Open self-serve (when user volume exists)
- Unlisted shows/meets may **add themselves for free** → long-tail discovery (another reason to buy: find new meets).
- Still behind **automated trust** (score → auto-publish / reject / rare quarantine).
- Seed remains the trusted backbone; UGC fills gaps Google doesn’t surface well.

---

## Product shape (technical)

1. **Event rows** (PocketBase or similar): name, `starts_at` / `ends_at` or recurrence rule, ZIP, city/state, source URL, `trust_score`, `status` (`live` / `rejected` / `quarantine` / `needs_refresh`), source id, tier (`seed` / `synced` / `user`).
2. **App:** ZIP (or ZIP3) + date-window feed; optional static ZIP→lat table for radius — **no live geocode per search**.
3. **Workers:** expand recurrence; sync allowlisted flagship calendars; score self-serve candidates; stale cleanup.
4. **Pro positioning (suggested):** full feed + farther radius + alerts; free teaser optional.

Space: tens–hundreds of seed shows with a year of dates stays **well under 1 MB** — negligible vs Offline Show Pack / images.

---

## Automated trust (for harvest + Phase 3 self-serve)

Every non-seed (or newly submitted) candidate gets a **trust score**. Then:

| Score band | Action |
|---|---|
| High | `status=live` |
| Low | `status=rejected` |
| Middle | `status=quarantine` — rare human peek |

**Trust is not “this person is nice.”** It is **signals that correlate with real dated public shows.**

Joe: maintain allowlists + thresholds; clear quarantine. **Not** open every URL by hand.

### Who runs each check?

| Check | Runner | How |
|---|---|---|
| URL loads | **Worker** | HTTP GET/HEAD |
| Looks like an event page | **Worker**; optional **AI** | Heuristics first; Gemini only if borderline |
| Same show last year + same ZIP | **Worker** | DB history |
| “Visit our mall, always open” | **Worker**; optional **AI** | Keywords + no end date |
| Same submitter 20 events / week | **Worker** | Rate / velocity |
| Source on allowlist / `.gov` | **Worker** | Config |
| Dedupe weekend + ZIP + name | **Worker** | Merge |

### Example

**Good:** Dated county show on `*.gov` event page, ZIP set, seen last year → auto-live.  
**Bad:** “Our antique mall — open 7 days — buy now” → auto-reject.

---

## Ingest order (when automation is on)

1. Seed + recurrence expansion  
2. Allowlisted flagship calendar sync (known URLs only)  
3. Later: self-serve tips / organizer add (scored)  
4. Later still: email-in from organizer domain; flyer OCR as draft only  

Do **not** start with open-web scrape of every Craigslist-style ad or “search the entire country night after night.”

---

## Cost posture

- ZIP feed: DB / bundled JSON (cheap).  
- Recurrence expand: free compute.  
- Flagship sync: N HTTP fetches on a schedule (cheap).  
- Optional AI classify: pay-per-use on borderline rows only.  
- Avoid Google Places / geocode-per-search.

---

## Anti-goals

- Free perpetual storefront ads.  
- Manual approve queue for every US flea meet.  
- Nationwide discovery crawl as v1.  
- Selling only “we mirrored famous show websites.”  
- AI as the only gate.  
- Building before HHH/CVC core store + support load justify the investment.

---

## Suggested build slices (when un-deferred)

1. Seed JSON (Tier A flagships + verified regionals) + in-app ZIP feed.  
2. Recurrence expander + stale flags.  
3. Allowlisted sync for top flagship URLs.  
4. Pro alerts.  
5. Automated-trust self-serve when volume warrants.

---

## Open decisions (leave for later)

- Exact numeric trust weights and thresholds.  
- Shared HHH+CVC event DB vs per-app.  
- Free vs Pro feed boundaries.  
- Organizer claim portal timing (after automated trust is proven).  
- How many Tier A seed shows for first ship (e.g. 30–50 vs 200).
