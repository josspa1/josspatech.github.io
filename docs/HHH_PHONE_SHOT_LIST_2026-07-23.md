# HHH user-guide — phone shot list (do not connect yet)

**Status:** Copy/install cleanup in progress. Connect phone only when Joe is asked.  
**Demo name:** Ludwig (never Harold).  
**Guide rule:** How-to **after** install — no Play Internal / TestFlight install slides.

After capture: pull into `\\Cerberus\MobileApps\HHH\screenshots\manual\` (and `intro/` if marketing), then copy keepers to `josspatech.github.io/assets/screenshots/hhh/`.

## Priority new / retake shots

| # | Filename (canonical) | Screen to open | Why |
|---|----------------------|----------------|-----|
| 1 | `07-identify-results.png` | Identify → successful result with **confidence %** + alternatives | Guide talks results; we only have camera/clues UI |
| 2 | `19-sample-loading.png` | Path → Explore sample → Ludwig loading / confirmation | Guide uses Home as stand-in |
| 3 | `20-collectors-tab.png` | **Collectors** tab (bottom nav, 5th area) | Narration now names Collectors; need a clear tab focus shot |
| 4 | `21-demand-rolodex-send.png` | Tools → Demand Rolodex → Send / contact form | End-of-guide Rolodex steps share wrong screens |
| 5 | `22-demand-rolodex-receive.png` | Demand Rolodex → Receive / PIN | Same |
| 6 | `23-demand-rolodex-board.png` | Dealer board grouped by make/model | Same |
| 7 | `24-device-sync.png` | Settings/Tools → Device Sync | Spoken; no dedicated shot |
| 8 | `25-offline-show-pack.png` | Settings → Offline Show Pack | Spoken; no dedicated shot |
| 9 | `26-clear-ludwig-sample.png` | Settings → clear Ludwig’s collection | Clear-sample step uses generic Settings |
| 10 | Verify / retake if wrong: `17-atomic-clock.png`, `18-moon-phase.png` | Tools → Exact Time / Moon Phase | Prior audit marked wrong; confirm on device |
| 11 | Optional polish: `07b-offline-identify-queue.png` | Home banner when ID queued offline | Nice-to-have |

## Keep (no phone needed unless UI changed)

- `01-home-command-center.png` (shows sample banner + 5-tab bar)
- `02-museum-collection.png`, `03-piece-detail.png`, `04-wishlist-grails.png`
- `05-ebay-grail-radar.png`, `06-clockworks-parts.png`, `06a-clock-repair-symptoms.png`
- `07a-identify-camera.png`, `08-tools-hub.png`, `09-web-companion.png`
- `10-settings.png`, `11-backup-restore.png`, `12-trial-subscription.png`
- `13-onboarding-welcome.png`, `14-onboarding-path.png`, `15-finances-pl.png`
- `16-compare.png` (OK — Compare Watches with Collectors tab visible)

## Drop from guide (do not recapture for how-to)

- `00-play-internal-install.png` — Play Internal listing; removed from user-guide slides

## Capture order (when phone is connected)

1. Cold start / Ludwig sample path (shots 2, 9)  
2. Identify happy-path results (1, optional 11)  
3. Collectors + Demand Rolodex (3–6)  
4. Device Sync + Offline Show Pack (7–8)  
5. Atomic / Moon verify (10)

Label adb pulls: `HHH_manual_<filename>_YYYYMMDD.png` then rename to canonical after check.
