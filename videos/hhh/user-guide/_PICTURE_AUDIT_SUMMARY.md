# HHH User Manual — EN picture audit (2026-07-24)

**Scope:** All **111** English slides in `videos/user-guide-hhh/`  
**Rule:** Picture must match the narration **and** current app UI.  
**Locales:** Frozen until this EN pass is acceptable (premature locale builds were a mistake).

---

## Answer to “is every QR wrong?”

**No.**

| Feature | QR OK? | Why |
|---------|--------|-----|
| **Web Companion** (phone → PC) | **No as primary UI** | Live app: LAN **URL + 4-digit pairing code**. QR is optional / phone-to-phone advanced. Old “Scan on your PC” shot was wrong. |
| **Share Nearby / Demand Rolodex send** (phone → phone/dealer) | **Yes** | QR + PIN between phones is intentional. Not the same screen as Web Companion. |

---

## What I changed tonight (EN only)

1. **Replaced** `09-web-companion.png` with a **mockup** of current connect UX: address + large **4-digit code** (old QR-to-PC backed up as `09-web-companion.png.bak-qr-to-pc`). Recapture from phone tomorrow.
2. **Already patched earlier:** `12-trial-subscription.png` / intro `10-trial-pro.png` — annual hero **$74.99/yr** (not $6.25 lead).
3. **Remapped** EN `index.html` + `_shot-map.json` to use keepers that already existed but weren’t wired:
   - Identify results → `07` / `07b`–`07d` (not camera for result slides)
   - Device Sync → `24-device-sync.png`
   - Offline Show Pack → `25-offline-show-pack.png`
   - Clear samples → `26-clear-ludwig-sample.png`
   - Demand Rolodex → `21` / `22` / `23` (not Tools hub stand-ins)

---

## Full-deck verdict (categories)

### REPLACE / MOCK (must not ship as-is)

| Asset / slides | Issue | Status |
|----------------|-------|--------|
| Web Companion (63–65, 99) | Old QR-to-PC UI | **Mock replaced** — phone recapture still required |
| Unlock Pro (trial slides) | $6.25 looked like ~$6/yr | **Mock patched** — phone recapture preferred |
| `19-sample-loading.png` | Misnamed: it’s an **old Home** (4 tabs), not a loading screen | **Still wrong for “loading” narration** — needs real loading shot or narration tweak |

### REMAP DONE (correct file existed)

| Need | Was wrongly using | Now |
|------|-------------------|-----|
| Identify results / confidence / insights | `07a` camera | `07` / `07b`–`07d` |
| Device Sync | Backup screen | `24-device-sync` |
| Offline Show Pack | Profile top | `25-offline-show-pack` |
| Clear Ludwig sample | Profile top | `26-clear-ludwig-sample` |
| Demand send / receive / board | Tools hub / wish list | `21` / `22` / `23` |

### KEEP (OK for narration, optional polish)

- Home `01`, Museum `02`, Detail `03`, Wishlist `04`, Grail Radar `05`, Clockworks `06`/`06a`
- Identify camera `07a` **only** for capture/clue slides
- Tools hub `08` **only** for Tools grid slides
- Backup `11` for backup slides
- Compare / Atomic / Moon / Collectors keepers where mapped
- Demand Rolodex send/receive/board feature UI (chrome may show older 4-tab bar — recapture when phone available)

### NEEDS PHONE RECAPTURE (Settings depth)

| Slide topic | Current shot | Problem |
|-------------|--------------|---------|
| Theme / Language / Security / Notifications / encryption | `10-settings.png` | File is **Profile top** only (trial / Upgrade). Does **not** show those rows. |

Until recapture: either scroll-capture Settings sections tomorrow, or temporarily mark those slides as Profile-only and adjust narration — **do not fake Settings rows tonight without a honest mock.**

---

## Share Nearby vs Web Companion (audit note)

- Slide ~97 “Share Nearby … QR + PIN” should use a **Share Nearby / piece QR** frame when we have one; Tools hub alone is a weak stand-in (entry point only).
- Demand Rolodex **send form** (`21`) is correct for contact/want-list steps; the **PIN+QR show-to-dealer** step may need a follow-up capture if not on `21`.

---

## Voice

EN narration MP3s were regenerated with Meta-ad polish (AndrewNeural + soft chain). That is independent of pictures.

---

## Locales (de/es/fr/it/pt/zh/hi)

Copies **exist** from the premature run. They must be **rebuilt from finished EN** after you accept this picture pass — not hand-patched.

---

## Suggested tomorrow (phone)

1. Web Companion live (URL + code) — replace mock  
2. Unlock Pro — replace pricing mock  
3. Settings scrolled: Theme, Language, Security, Notifications, encryption status  
4. Sample collection **loading** state (or change slide 4 narration)  
5. Share Nearby active QR+PIN (if distinct from Demand send)  
6. Optional: Demand post-send PIN+QR; 5-tab chrome on older Demand shots  

---

## Files for review

- This report: `videos/user-guide-hhh/_PICTURE_AUDIT_2026-07-24.md` (heuristic table) + this summary  
- WC mock: `assets/screenshots/hhh/manual/09-web-companion.png`  
- WC old backup: `09-web-companion.png.bak-qr-to-pc`
