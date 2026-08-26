# Partner showcase — record highlights, trim glitches

## Workflow

1. **Record** one continuous take on the Samsung (adb gestures only — no Maestro during capture).
2. **Trim** stuck frames / glitches in post with `trim-partner-video.js`.
3. **Preview** the HTML deck with Andrew narration over `home-hero.mp4`.

## Record Home clip

```bat
set ANDROID_SERIAL=R5CXC2K4Z8F
cd C:\Users\jossp\Documents\MobileApps\PBJ\SourceCode
node scripts\record-partner-home-video.js
```

Optional sample data first (Maestro — can hang; skip if Home already populated):

```bat
node scripts\record-partner-home-video.js --prep-sample
```

**Outputs**

| File | Purpose |
|------|---------|
| `video/_source/raw-home.mp4` | Full capture — keep for re-editing |
| `video/home-hero.mp4` | Copy of raw until trimmed |
| `video/cuts.example.json` | Template for keep-segments |

## Highlights hit during recording

1. Sankey / header glance
2. Scroll to **hero carousel** (donut, pace, insights)
3. Carousel swipes (6 panels)
4. Scroll down widgets
5. Scroll back up
6. Hero carousel again — hold on the beautiful card

## Trim glitches

Open `video/_source/raw-home.mp4`, note timestamps of frozen/stuck frames, then copy `cuts.example.json` → `cuts.json` and tune segment `start`/`end` times (seconds).

```bat
node scripts\trim-partner-video.js
```

Writes trimmed `home-hero.mp4`. Regenerate deck if needed:

```bat
cd C:\PBJ\cvc-batch
node write-partner-showcase-v6.js
```

## Welcome slide (deck)

- **0–4.2s** — Feature Showcase “100% private” screen (HTML mock)
- **Then** — `home-hero.mp4` (real phone recording)

Andrew welcome line plays over both.

## Preview

```bat
cd C:\Users\jossp\Documents\MobileApps\WebSite\HostedFiles\videos\pocketbudjet\partner-showcase
python -m http.server 8765
```

Open `http://localhost:8765` (not `file://`).
