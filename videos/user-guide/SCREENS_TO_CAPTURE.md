# PBJ User Manual — screens to capture (phone)

**Created:** 2026-07-27  
**Why:** Raise PBJ video toward HHH quality — pictures that match narration, then re-wire taps + audio sync + re-render.  
**App:** PocketBudJet on Joe’s phone (USB later).  
**Dest root:** `josspatech.github.io/assets/screenshots/` (new files under the folders below).  
**Deck:** `videos/user-guide/` (EN only; locales frozen until EN accepted).

**Full quality scope (not only pictures):**
1. These screenshots (this file)
2. Wire shots into `deck.js` / shot map
3. Gold **tap / touch points** synced to narration verbs
4. **Audio ↔ slide** advance on voice end (not a fixed timer)
5. Re-render `pocketbudjet-user-guide.mp4`

When phone is attached: work top → bottom; check off each row.

---

## Capture list (must-have)

Save as **PNG**, portrait, full phone UI (status bar OK). Prefer real data over empty states when the narration implies filled fields.

| # | New filename (suggested) | Open this in the app | Must show on screen | Used by slides | Status |
|--:|--------------------------|----------------------|---------------------|----------------|--------|
| 1 | `pbj/manual/add-transaction-amount.png` | Gold **+** → Add transaction (or Activity → add) | **Amount** field focused or clearly visible; ready to type | 50 | ☑ |
| 2 | `pbj/manual/add-transaction-merchant-category.png` | Same form, filled further | **Merchant** name typed, **Category** picked, **Account** selected | 51 | ☑ |
| 3 | `pbj/manual/add-transaction-split.png` | Same form | **Split** control visible (and ideally split UI open with portions) | 52 | ☑ |
| 4 | `pbj/manual/add-transaction-save.png` | Same form, ready to finish | **Save** button visible (merchant/amount filled) | 53 | ☑ |
| 5 | `pbj/settings/data-management-storage.png` | Settings → **Data Management** → **Storage** (or equivalent) | Storage / on-device history / receipt storage / archive controls — **not** Privacy overview | 96 | ☑ |
| 6 | `pbj/settings/mindful-features.png` | Settings → **Mindful Features** / Purchase Wishlist | Spending pause / wishlist cool-off | 108 | ☑ |
| 7 | `pbj/settings/app-lock.png` | Settings → Privacy → **App lock** (or App lock entry) | Biometric/passcode lock UI; recovery key mention OK if on screen | 117 | ☑ |
| 8 | `pbj/connect-bank/connect-bank-search.png` | Settings → **Connect Bank** | Bank **search** UI (US banks); no password fields with secrets | 87, 99 | ☑ |
| 9 | `pbj/connect-bank/connect-bank-pick-accounts.png` | Connect Bank flow after “signed in” / account picker (demo OK if Premium gated — use whatever live UI allows) | Checking / savings / credit **account pick** | 100 | ☑ mock |
| 10 | `pbj/connect-bank/bank-sync-premium-gate.png` | Connect Bank or Bank sync entry when Premium/trial messaging shows | Clear **US / Premium / not in free trial** messaging (covers 86, 98 if distinct from search) | 86, 98 | ☑ |
| 11 | `pbj/retirement/retirement-planning.png` | Retirement Planning screen (Toolbox / Goals / Coach path — whichever ships) | **Target age**, **desired income**, **current savings** (or current equivalent fields) — **not** Goals/languages | 106 | ☑ |
| 12 | `pbj/07-web-companion.png` *(replace if UX changed)* | Toolbox → **Web Companion** / Companion, session **started** | Current pairing UX: QR and/or code — must match narration (“scan the QR…”) or narration will be updated after capture | 110 | ☑ |

---

## Bank-statement import (slides 54–61) — share from bank app

Guide path is **Share → PocketBudJet** only (browse / email stay in-app, not in the video). Capture under `pbj/import/`. Bank-app download shots are **not** required.

| # | New filename | Open this in the app | Must show on screen | Used by slides | Status |
|--:|--------------|----------------------|---------------------|----------------|--------|
| I1 | `pbj/import/01-toolbox-import-center.png` | Toolbox | **Import Center** row visible | 54 | ☑ mock |
| I2 | `pbj/import/02-import-idle.png` | Import Center idle | **Share from your bank app** + **Show me how** | 55, 57, 59 | ☑ |
| I3 | `pbj/import/03-share-howto.png` | Idle → **Show me how** | Document Center + More/⋯ steps; **Got it** | 56 | ☑ mock |
| I5 | `pbj/import/07-review-import.png` | After share/sample → review | Draft list + **Import N new transactions** | 58 | ☑ |
| I7 | `pbj/import/10-import-history.png` | Import History | Prior imports list | 61 | ☑ mock |
| I8 | `pbj/import/08-import-done.png` | Post-import done | **Import complete** | 60 | ☑ mock |

Browse / email shots (`05-browse-files`, `09-email-forward`) are **not** needed for the guide.

Labeled working copies (NAS): `\\Cerberus\MobileApps\PBJ\screenshots\archive\2026-07-27-user-guide\2026-07-27\pbj\import\`. Local SSD path is a pointer only — see `PBJ/notes/user-guide-screenshots/README.md`.

---

## Receipt scanning (slides 62–66) — keep

Do **not** drop this chapter when simplifying bank import. Capture under `receipt-scanning/` (and scanner shots for 64–66).

| # | Filename | Open this in the app | Must show | Slides | Status |
|--:|----------|----------------------|-----------|--------|--------|
| R1 | `receipt-scanning/receipt-scan.png` *(upgrade)* | Toolbox → **Scan Receipt** → camera or review | OCR / merchant-amount-date or review+Save | 62–63 | ☑ existing (upgrade if stale) |
| R2 | `scanner.png` *(upgrade)* | Toolbox document / Universal Scan | Multi-page / crop / batch flow | 64–66 | ☑ existing (upgrade if stale) |

---

## Nice-to-have (CHECK slides — only if time)

Heuristic mismatches; capture only if wrong on visual review:

| Topic | Slides | Prefer showing |
|-------|--------|----------------|
| Feature showcase bills / debt | 1, 3 | Correct showcase card for bills or debt |
| Notification opt-in | 16 | System/app notification permission UI |
| Wizard bills | 22 | Bills step in setup wizard |
| Home / Budget / Coach when narrating bills or net worth | 27, 33, 105 | Screen that matches that beat |
| Spending plan | 38 | Spending Plan with envelopes after bills/goals |
| Widgets / Watch | 116 | Widget or watch complication UI |

---

## After capture (agent)

1. Copy PNGs into `assets/screenshots/…` paths above.  
2. Point slides in `videos/user-guide/deck.js` (and `_shot-map.json`) at new files.  
3. Fix gold taps for 50–53, 87, 96, 99–100, 106, 108, 110, 117.  
4. Regenerate audio only if narration changes (`npm run gen:user-guide-audio`).  
5. Confirm player/render advances on **audio ended**.  
6. `node scripts/_audit-pbj-guide-sync.js` → `tapIssues: 0`.  
7. `npm run render:user-guide` → publish `pocketbudjet-user-guide.mp4`.

---

## Do not

- Recapture Page/Meta ad art (different project).  
- Rebuild locale decks until EN video accepted.  
- Use HHH or CVC Web Companion shots for PBJ slide 110.
