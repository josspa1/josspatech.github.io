# HHH screenshot visual audit

**When:** 2026-07-12 (evening retake pass)  
**Device:** R5CXC2K4Z8F · Museum verified Owned(19) / Wish(5) / For Sale(2) before shoot  
**Method:** Navigate → screencap (adb pull) → `Read` vision on each keeper · no file-size guesses  
**Paths:** `josspatech.github.io/assets/screenshots/hhh/{intro,manual}/` (Documents + GitHub copies synced)  
**Rule:** Only **POPULATED** correct HHH screens count. No fake keepers.

---

## HARD BAN — never use as marketing / site hero

**Android launcher, home screen, and app-drawer dumps are forbidden** on josspatech.com (and Play listing art).

Symptoms that mean REJECT immediately (2026-07-13 live-site failure):
- Suggested-row + grid duplicates (Calendar / Contacts / Gmail / Play Store)
- Truncated launcher label `Handy Horol…`
- Any shot that is not an in-app HHH screen (Command Center, Museum, Piece Detail, Identify, Clockworks, etc.)

**Site hero (`#hhh`) must load only from** `assets/screenshots/hhh/intro/` **keepers** after a `Read`-tool visual check. Root filenames `01-home-museum.png` / `02-ai-identify.png` / `03-clockworks-wizard.png` previously held launcher junk — do not trust those names without re-verifying pixels.

**2026-07-13 fix:** `#hhh` hero → `intro/01-command-center.png`, `intro/02-my-museum.png`, `intro/03-piece-detail.png`. Version banners → Internal testing **v1.0.29 (build 52)**. Each PNG re-verified with Read after place.

---

## Verdict

| Bucket | Count | Usable? |
|--------|------:|---------|
| **intro/** KEEP | **10 / 10** | Yes — full intro deck on disk |
| **manual/** KEEP (this pass + prior 3) | **16** | Yes for critical + most story assets |
| **manual/** still MISSING / weak | **8** | See §C |

**Critical set (done):** intro 01–10 + manual home / museum / detail / tools / settings / backup.

---

## A) KEEP — `intro/`

| File | Verdict | What’s on screen |
|------|---------|------------------|
| `01-command-center.png` | **KEEP** | Home Command Center · sample banner · 22 pieces · $175,720 |
| `02-my-museum.png` | **KEEP** | My Museum Owned(19) · Omega + TAG visible · $175,720 |
| `03-piece-detail.png` | **KEEP** | Omega Speedmaster detail · value / 85% confident |
| `04-ai-identify.png` | **KEEP** | Identify camera / clues UI (not results — see note) |
| `05-clockworks-repair.png` | **KEEP** | Find clock parts · Hermle/Urgos/Kieninger movement picker |
| `06-grail-radar.png` | **KEEP** | Grail Radar · Daytona hunt rules · Check now · alert feed |
| `07-finances-pl.png` | **KEEP** | Finances P&L · $176.1K · unrealized +$16,546 |
| `08-pro-tools.png` | **KEEP** | Tools hub · Worth / Compare / eBay / Clock Parts |
| `09-web-companion.png` | **KEEP** | Web Companion live · QR “Scan on your PC” |
| `10-trial-pro.png` | **KEEP** | Unlock Pro sheet · Annual $74.99 / Monthly $9.99 |

**Note on `04`:** Quiltt ideal is identify **results** with top match %. Kept Identify entry UI (correct HHH screen with content). `07-identify-results.png` still missing.

---

## B) KEEP — `manual/`

| File | Verdict | Notes |
|------|---------|-------|
| `01-home-command-center.png` | **KEEP** | Same family as intro 01 |
| `02-museum-collection.png` | **KEEP** | Populated museum |
| `03-piece-detail.png` | **KEEP** | Omega detail |
| `04-wishlist-grails.png` | **KEEP** | Wish(5) · Patek / Rolex |
| `05-ebay-grail-radar.png` | **KEEP** | Same as intro 06 |
| `05b-ebay-match-notification.png` | **KEEP** | Prior keeper (unchanged) |
| `06-clockworks-parts.png` | **KEEP** | Movement picker (Clockworks path) |
| `06a-clock-repair-symptoms.png` | **KEEP** | Prior keeper (unchanged) |
| `07a-identify-camera.png` | **KEEP** | Identify dial/clues UI |
| `08-tools-hub.png` | **KEEP** | Tools hub |
| `09-web-companion.png` | **KEEP** | QR live companion |
| `10-settings.png` | **KEEP** | Profile top · trial / Upgrade to Pro |
| `11-backup-restore.png` | **KEEP** | Backup Your Data · 22 watches · Export .hhh |
| `12-trial-subscription.png` | **KEEP** | Unlock Pro sheet |
| `14-onboarding-path.png` | **KEEP** | Prior keeper (unchanged) |
| `15-finances-pl.png` | **KEEP** | P&L dashboard |

---

## C) Still missing / not KEEP

| File | Status |
|------|--------|
| `07-identify-results.png` | **MISSING** — need successful Identify run with confidence |
| `07b-offline-identify-queue.png` | **MISSING** / prior was empty vault |
| `13-onboarding-welcome.png` | **MISSING** / prior WRONG (drawer) |
| `00-play-internal-install.png` | **WRONG** marketing card — need real Play Internal UI |
| `00-testflight-install.png` | **WRONG** marketing card — need real TestFlight |
| `16-compare.png` | **MISSING** / prior WRONG |
| `17-atomic-clock.png` | **MISSING** / prior WRONG |
| `18-moon-phase.png` | **MISSING** / prior WRONG |

---

## D) Session notes

- Museum hierarchy confirmed before shoot (Owned 19 / Wish 5 / For Sale 2 · Omega + TAG).
- Mid-content / bottom-nav taps only · no Dialer · companion stopped after QR capture.
- Screen timeout restored to **120000** ms · app left on **Home / Command Center**.
- No Play ship · no git commit.
