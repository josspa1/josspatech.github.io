# HHH videos — build status (site)

**Updated:** 2026-07-13  
**Naming:** Walkthrough (short overview) · User Manual (detailed how-to). Not “guide” in UI.

## Live URLs

| Piece | Path | Status |
|-------|------|--------|
| Hub | `/videos/hhh/` | Live |
| Walkthrough | `/videos/hhh/walkthrough/` | Live EN — 10 intro keepers |
| User Manual (canonical) | `/videos/hhh/user-manual/` | Redirect → player |
| Interactive player | `/videos/user-guide-hhh/` | Live EN — 105 slides, EN audio |
| PDF | `/docs/handyhorology/HandyHorology_UserGuide.pdf` | Live |

## Screenshot keepers

- `assets/screenshots/hhh/intro/` — **10/10** KEEP (audit)
- `assets/screenshots/hhh/manual/` — **21** KEEP; still missing honest **TestFlight**, **Identify results**, **offline queue** (interim reuse in player)

## Done this pass

- Canonical `/videos/hhh/*` stubs + Walkthrough player
- HHH product page + How To hub links (PBJ layout untouched)
- Side-by-side anti-cage CSS on HHH User Manual player
- Broken missing-PNG refs pointed at interim keepers

## Remaining

1. Capture/replace interim PNGs when Identify API + iPhone available (do not block on Identify USB verify for video publish)
2. Commit EN `audio/` for User Manual if not already on remote
3. Multilingual Walkthrough + User Manual (ES/ZH/… after EN polish)
4. Optional MP4 export for offline / store listing
5. Walkthrough TTS / partner-showcase motion polish (themes optional — HHH can stay stills)
