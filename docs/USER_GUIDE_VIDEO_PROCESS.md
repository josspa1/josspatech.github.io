# User-manual how-to video process (HHH, PBJ, future apps)

**Audience:** agents + Joe. Follow this for every JosspaTech how-to video after HHH.

**Terminology:** **User Manual** = detailed how-to deck + synced MP3s + optional MP4.  
**Walkthrough / partner showcase** = short marketing overview (not this process).

---

## Goals (non-negotiable)

1. **Picture ↔ dialogue match** — every slide’s screenshot matches what the narration describes.
2. **Audio ↔ slide advance** — next slide only after that slide’s MP3 ends (tiny buffer OK).
3. **Transcript UX (PBJ parity)** — right panel scrolls; sentence highlight tracks audio; chapter pills jump the deck **and** restart audio at that slide; pause/play works; `#chapter=N` deep links optional.
4. **No OS chrome in screenshots** — reject launcher / Contacts / Photos pickers; review before promote.
5. **MP4 is a render of the live deck** — after HTML/audio stabilize, re-render; never ship a stale MP4 as “done.”

---

## Canonical layout (per app)

| Asset | Example (HHH) | Example (PBJ) |
|-------|---------------|---------------|
| Player HTML | `videos/user-guide-hhh/index.html` | `videos/user-guide/index.html` |
| Narration JSON | `videos/user-guide-hhh/narration-en.json` | `videos/user-guide/narration-en.json` |
| Per-slide MP3 | `videos/user-guide-hhh/audio/slide-{i}.mp3` | `videos/user-guide/audio/slide-{i}.mp3` |
| Deck / player JS | `videos/user-guide-hhh/deck.js` | inline in PBJ `index.html` |
| Shared helpers | `videos/shared/walkthrough.js` + `.css` | same |
| Screenshots | `assets/screenshots/{app}/manual/` | `assets/screenshots/pbj/` (or site copy) |
| MP4 | `videos/user-guide-hhh/*.mp4` | `videos/user-guide/pocketbudjet-user-guide.mp4` |
| NAS catalogue | `\\Cerberus\MobileApps\{APP}\screenshots\` | same pattern |

---

## End-to-end pipeline

### A. Capture / keepers (phone when needed)

1. Write an ordered shot list (`docs/{APP}_PHONE_SHOT_LIST_*.md` + NAS `_catalog/`).
2. Capture **in-app only**. Abort/delete if Contacts, launcher, or gallery chrome appears.
3. **Review every PNG** before labeling (`HHH_manual_<name>_YYYYMMDD.png`) and promoting to `manual/` + NAS.
4. Prefer multiple aspects of long screens (e.g. Identify results top / review / confidence / insights).

### B. Wire slides to narration

1. Keep `narration-en.json` as source of truth for spoken lines.
2. Sync into HTML (`NARRATION`, `LAST_SLIDE`, chapter starts from pills):
   - HHH: `python scripts/_sync-hhh-guide-html-from-narration.py`
3. Remap images to keepers / new shots:
   - HHH: `python scripts/_remap-hhh-guide-keepers.py`
4. Audit: shot map + sync audit scripts under `scripts/_audit-*-guide-*.js`.

### C. Audio (edge-tts)

- Voice: `en-US-AndrewNeural` (demo character names like **Ludwig** are copy, not the TTS engine).
- HHH: `python scripts/gen-user-guide-hhh-en-audio.py`  
  Changed lines only: `--only-changed` with `_audio_regen_slides.json`.
- PBJ: `npm run gen:user-guide-audio` (or `python scripts/gen-user-guide-en-audio.py`).
- After any narration edit: regenerate affected MP3s **before** claiming sync is done.

### D. Interactive player UX checklist

- [ ] Right transcript panel scrolls with current paragraph
- [ ] Sentence spans highlight while audio plays (`timeupdate`)
- [ ] Chapter pills update **during** autoplay, not only on click
- [ ] Jumping chapter/dot/arrow while playing **restarts that slide’s audio**
- [ ] Pause freezes audio + highlight; play resumes from current slide
- [ ] Tap pulse / gold ring still works (HHH `scheduleTapPulse`)

### E. MP4 render

- HHH: `node scripts/render-user-guide-hhh-video.js` (optional `--fast` for draft)
- PBJ: `npm run render:user-guide`
- Confirm MP4 mtime ≥ HTML/narration/audio mtimes before calling the video “shipped.”

---

## HHH-specific notes (2026-07-23)

- Live deck: **111 slides** (0–110), **15 chapters**, install/TestFlight slides removed.
- Tabs copy: **four** tabs (Home / My Museum / Tools / Settings). Collector Network is under Settings.
- Identify results: multi-aspect PNGs `07`, `07b`, `07c`, `07d`.
- Player: `videos/user-guide-hhh/deck.js` (PBJ-parity transcript).

## PBJ follow-up

- Same process; phone not required for transcript UX.  
- PBJ how-to video re-sync + any missing screenshots when PBJ is installed on device.

---

## Do not

- Promote unreviewed screenshots.
- Leave MP4 older than the interactive deck.
- Call the user manual a “walkthrough” in user-facing copy.
- Skip Production Play promote via agent unless Joe explicitly says Production = yes (see Android ship policy).
