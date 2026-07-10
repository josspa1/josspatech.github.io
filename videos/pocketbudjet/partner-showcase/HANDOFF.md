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
| `home-concierge.jpg` | Home hero (ALL · AT A GLANCE) — Joe 2026-07-09, buttons surfaced | 7 HOME carousel |
| `home-sankey.jpg` | Where Your Money Went · ALL | 7 HOME carousel |
| `home-donut.jpg` | Spending donut | 7 HOME carousel |
| `home-merchants.jpg` | Top merchants | unused (dropped from slide 7 — layout bleed) |
| `screens/_spare/home-transactions-card.jpg` | Recent transactions on Home | unused |

**Still mock HTML:** GOALS (`debt.html`), MATCH (`scanner.html`), CLOSE (`paywall.html`)

**Preview:** `file://` breaks Start in Chrome (fetch blocked). Use a local server:

```bash
cd C:\Users\jossp\Documents\MobileApps\WebSite\HostedFiles\videos\pocketbudjet\partner-showcase
python -m http.server 8765
```

Open **http://localhost:8765/** (not file://).

---

## Replicate for other apps (HHH, CVC, …)

Use this checklist when building a partner showcase like PBJ’s. **PBJ is the reference implementation.**

### 1. Content & assets

| Requirement | PBJ example |
|-------------|-------------|
| **Slide deck** | ~11 slides: welcome → feature highlights → close. Narration-driven timing (`audio.onended`). |
| **Screenshots** | Real device JPGs at **1440×3120** (Galaxy S25 Ultra). Match app locale in UI; narration can be localized separately. |
| **Hero video** | Optional MP4 for slide 0 (e.g. `video/home-hero.mp4`). Privacy/intro layer crossfades in before video. |
| **HTML mocks** | `screens/*.html` for flows hard to capture (iframe scaled inside phone frame). |
| **Logo / wordmark** | `logo/*-ad-logo.svg` for Start overlay. |
| **locales.json** | Per-locale: `narrations[]`, `captions[]`, `eyeLabels`, `themeLabels`, UI strings (`start`, `pause`, …). |
| **Narration MP3s** | `audio/{locale}/slide-0.mp3` … `slide-N.mp3` via `gen-partner-showcase-audio.py` (edge-tts, neural voices). |
| **Demo data on device** | CSV / sample vault so Home and key tabs show real numbers before capture. |

### 2. Phone mockup (critical for “looks right”)

| Requirement | Value |
|-------------|--------|
| **Capture device** | Samsung Galaxy **S25 Ultra** (`R5CXC2K4Z8F` in PBJ notes) |
| **Screenshot size** | **1440 × 3120** (QHD+ 19.5:9) |
| **CSS aspect ratio** | `--phone-ar: 1440 / 3120` on `.phone` |
| **Sizing** | Width scales to viewport; **height from aspect-ratio only** — never cap `max-height` independently (squashes frame). |
| **Embed JS** | `syncEmbedPhoneSize()` — fit phone inside stage: `w = min(maxW, maxH * PHONE_AR)`. |
| **Iframe HTML mocks** | Scale iframes with `--frame-scale` from `phone.clientWidth / 1242`. |

### 3. `index.html` behavior

- **`?embed=1`** — iframe mode on homepage / how-to:
  - Start overlay (logo + tagline + gold **Start**); no autoplay until click.
  - Stage uses **container queries** + full width (`width: 100%` on stage-wrap — flex collapse bug if missing).
  - Compact progress / caption / controls when `.playing`.
- **Full page** — language picker, taller stage, all chrome visible.
- **`?lang=xx`** — 8 locales (or subset); fallback to `en` in `locales.json`.
- **Valid HTML** — closing `</style>` before `</head>` (broken tag = empty navy box).

### 4. Site integration (josspatech.github.io)

| Location | What |
|----------|------|
| `HostedFiles/videos/{app}/partner-showcase/` | **Canonical source** |
| GitHub mirror | `videos/{app}/partner-showcase/` — push for Pages |
| NAS archive | `\\10.0.0.252\MobileApps\WebSite\VideoArchive\pbj\videos\` (per-app subfolder) |
| Homepage embed | `#intro-tour` iframe: `src="/videos/.../partner-showcase/?embed=1"`, height **`min(960px, 92vh)`** |
| Hash routing | `#intro-tour` must call `showPage('{app-page}')` + scroll — anchor lives inside hidden `.page` otherwise iframe is **0×0** |
| Boot script | Inline `<head>` script: `boot-pbj` (etc.) so refresh doesn’t flash company homepage |
| how-to | Same iframe block + “Open full screen” + locale links |

### 5. Deploy & verify

1. Sync HostedFiles → GitHub → `git push origin main`
2. Hard-refresh after Pages CDN (~1–2 min)
3. Test: standalone `?embed=1`, homepage `#intro-tour`, click **Start** → sound + visible phone + no horizontal scrollbar
4. Optional: screen-record deck with narration for partner MP4 deliverable

### 6. Per-app paths (when ready)

| App | Suggested folder | Homepage page id |
|-----|------------------|------------------|
| PocketBudJet | `videos/pocketbudjet/partner-showcase/` | `#intro-tour` on `page-pbj` |
| HHH | `videos/hhh/partner-showcase/` (TBD) | `page-hhh` + anchor |
| CVC | `videos/cvc/partner-showcase/` (TBD) | `page-cvc` + anchor |

Copy PBJ `index.html` + `locales.json` structure; replace slides, screenshots, voices, and generator script. Reuse embed CSS/JS patterns verbatim.

---
