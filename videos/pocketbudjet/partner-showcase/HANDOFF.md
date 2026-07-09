# Partner Showcase — Handoff (2026-07-09 ~1:30 AM)

Joe unplugged phone (`R5CXC2K4Z8F`). Continue from here tomorrow.

---

## What shipped tonight

### Home hero video (DONE)
- **File:** `video/home-hero.mp4` (~12 MB, captured 1:29 AM)
- **Also:** `video/_source/raw-home.mp4` (same bytes; trim copy if glitches appear)
- **Method:** `node scripts/record-partner-home-video.js --from-current` (adb only, no Maestro during capture)
- **Device:** Samsung `R5CXC2K4Z8F`, 1440×3120, build **310**
- **Content:** ConciergeHeroCard at top (“THIS MONTH” aurora hero) — holds + light carousel peek
- **Wired in:** `index.html` slide 1 (welcome) — privacy intro → crossfade to `video/home-hero.mp4`

### Demo data on phone (DONE)
- CSV pushed to phone: `/sdcard/Download/pbj-demo-statement.csv`
- PC copy: `C:\Users\jossp\Downloads\pbj-demo-statement.csv`
- 18 rows (June + July 2026) — payroll, groceries, gas, Netflix, etc.
- **Simulate Premium:** ON (tester tools)
- Home showed **normal hero** with numbers before capture

### Recording script fixes (in SourceCode, not on build 310 yet)
- `PBJ/SourceCode/scripts/record-partner-home-video.js`
  - `--from-current`: no Home tab tap, no pre-scroll (avoids pull-to-refresh)
  - Scroll gestures start mid-screen (refresh-safe)
- **UI fix staged (needs reload/build):** mic/+ buttons above champagne splash
  - `src/components/PremiumHeroChrome.tsx` — zIndex stacking
  - `src/components/dashboard/ConciergeHeroCard.tsx` — darker icon pills

---

## Partner showcase deck

**Folder layout (canonical — HostedFiles is source, mirror to GitHub + NAS):**

```
partner-showcase/
  index.html          deck + ?lang=
  locales.json        all narration/UI strings (8 locales)
  audio/{locale}/     slide-0.mp3 … slide-10.mp3 only — no flat duplicates
  screens/            HTML mocks + *-live.jpg used in deck
  screens/_spare/     unused alternates (not linked from index.html)
  video/home-hero.mp4 shipped hero clip
  video/_source/      raw captures for re-trim
  logo/
```

| Item | Path |
|------|------|
| Deck HTML | `HostedFiles/videos/pocketbudjet/partner-showcase/index.html` |
| Generator | `C:\PBJ\cvc-batch\write-partner-showcase-v6.js` |
| Privacy mock (slide 1 intro) | `screens/feature-private.html` |
| Narration | `locales.json` + `audio/{locale}/slide-0.mp3` … `slide-10.mp3` (en, es, de, fr, pt, zh, it, hi) |
| Trim workflow | `VIDEO-PATH.md`, `video/cuts.example.json`, `scripts/trim-partner-video.js` |

### Slide structure (~10)
0. WELCOME — privacy layer + **home-hero.mp4**
1. BREAKDOWNS — transactions mock
2. BUDGET
3. GOALS — debt
4. COACH
5. MATCH — scanner
6. COLOR — theme cycle
7. TRUST — subscriptions (may still need subscription list PNG; was wired to mock)
8. AND MORE — feature chips
9. CLOSE — paywall

### Preview (local server — not `file://`)
```bat
cd C:\Users\jossp\Documents\MobileApps\WebSite\HostedFiles\videos\pocketbudjet\partner-showcase
python -m http.server 8765
```
Open `http://localhost:8765` → **Start**

### Joe’s final deliverable
- Screen-record the deck (Win+G / Loom) with narration playing
- Send MP4 to partners

---

## Still open (priority order)

1. **Quick preview** — Joe watches slide 1 hero; trim if needed (`trim-partner-video.js` + `video/cuts.json`)
2. **TRUST slide** — replace mock with real subscription list PNG if desired (`capture-partner-showcase.js` or manual)
3. **Re-record hero?** — only if tonight’s clip shows wrong framing or refresh glitch; script is fixed now
4. **Maestro sample import** — broken: missing subflows `dismiss-quick-tour.yaml`, `recover-stuck-ui.yaml` in `.maestro/subflows/`; capture_assisted tester unlock flaky on this device — **CSV manual import worked**
5. **Teller** — partial outage (~1:13 AM): homepage 503, connect/api timeout; use sandbox when back (`username`/`password`) if richer bank-sync demo needed
6. **Ship UI stacking fix** — next internal build so mic/+ sit above bloom on device

---

## Commands cheat sheet

```bat
set ANDROID_SERIAL=R5CXC2K4Z8F
cd C:\Users\jossp\Documents\MobileApps\PBJ\SourceCode

REM Re-capture hero (phone on Home, Concierge at top)
node scripts/record-partner-home-video.js --from-current

REM Push fresh CSV to phone
adb push C:\Users\jossp\Downloads\pbj-demo-statement.csv /sdcard/Download/pbj-demo-statement.csv

REM Full showcase PNG pipeline (wipe + Maestro — fragile)
node scripts/capture-partner-showcase.js

REM Regenerate index.html from generator
node C:\PBJ\cvc-batch\write-partner-showcase-v6.js
```

---

## Context for the agent

- **Goal:** Partner-facing sales deck — AndrewNeural narration, show don’t tell, privacy-first welcome
- **Hero must be:** ConciergeHeroCard at **top** of Home — NOT empty state, NOT carousel donut alone
- **Preferred device:** `R5CXC2K4Z8F`
- **Post-capture:** trim glitches in post (Maestro gets stuck; don’t rely on it for video capture)
- Joe was up until ~1:30 AM to get this done — hero video **is done**; don’t re-run capture unless Joe asks after reviewing

## Joe's device screenshots (2026-07-09 ~1:31 AM)

**Source:** `C:\Users\jossp\Downloads\Mobile Devices\PBJ-Screenshots` (23 JPGs)

**Copied into showcase** (`screens/`):

| File | Screen | Deck slide |
|------|--------|------------|
| `transactions-live.jpg` | Activity → Transactions (Jun 2026) | 2 BREAKDOWNS |
| `budget-live.jpg` | Budget tab | 3 BUDGET |
| `coach-ask.jpg` | Coach ask screen | 4 COACH |
| `screens/_spare/coach-live.jpg` | Coach → Reports (alt) | unused |
| `subscriptions-live.jpg` | Subscription Tracker (Netflix) | 8 TRUST |
| `home-concierge.jpg` | Home hero (ALL · AT A GLANCE) | 7 COLOR carousel |
| `home-sankey.jpg` | Where Your Money Went | 7 COLOR carousel |
| `home-donut.jpg` | Spending donut | 7 COLOR carousel |
| `home-merchants.jpg` | Top merchants | 7 HOME carousel |
| `screens/_spare/home-transactions-card.jpg` | Recent transactions on Home | unused |

**Still mock HTML:** GOALS (`debt.html`), MATCH (`scanner.html`), CLOSE (`paywall.html`)

**Preview:** `python -m http.server 8765` in partner-showcase folder

---
