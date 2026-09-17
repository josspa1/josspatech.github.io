#!/usr/bin/env python3
"""Build CVC user-guide deck (HHH/PAL parity) from narration-en.json + stills."""
from __future__ import annotations

import html
import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "cvc" / "user-guide"
INDEX = OUT / "index.html"
NARRATION_JSON = OUT / "narration-en.json"
SHOT_MAP = OUT / "_shot-map.json"
ASSET_MANUAL = ROOT / "assets" / "screenshots" / "cvc" / "manual"
ASSET_STORE = ROOT / "assets" / "screenshots" / "cvc" / "store"
CVC_SHOTS = Path(r"C:\Users\jossp\Documents\MobileApps\CVC\screenshots")

CHAPTERS = [
    (0, "Open"),
    (9, "Home"),
    (14, "Identify"),
    (26, "Vault"),
    (32, "Worth & hunt"),
    (43, "Tools"),
    (53, "Floor & PC"),
    (56, "Keep"),
    (63, "Help"),
]

# Local labeled stills → dest basename under assets/screenshots/cvc/manual
COPY_MANUAL = {
    "listing/listing-01-home-command-center.png": "01-home-command-center.png",
    "guide/guide-01-home-command-center.png": "01-home-command-center.png",
    "listing/listing-02-collection-gallery.png": "02-collection-gallery.png",
    "guide/guide-02-collection-gallery.png": "02-collection-gallery.png",
    "guide/guide-02b-collection-filled.png": "02-collection-gallery.png",
    "guide/guide-03-item-detail.png": "03-item-detail.png",
    "guide/guide-04-compare.png": "04-compare.png",
    "listing/listing-03-identify-chips.png": "05-identify.png",
    "guide/guide-05-identify-chips.png": "05-identify.png",
    "listing/listing-04-portfolio-pl.png": "06-portfolio-pl.png",
    "guide/guide-06-portfolio-pl.png": "06-portfolio-pl.png",
    "guide/guide-07-grail-radar.png": "07-grail-radar.png",
    "guide/guide-08-grading-guide.png": "08-grading-guide.png",
    "listing/listing-06-web-companion.png": "09-web-companion.png",
    "guide/guide-09-web-companion.png": "09-web-companion.png",
    "listing/listing-07-languages.png": "10-language.png",
    "guide/guide-10-language.png": "10-language.png",
    "guide/guide-11-privacy.png": "11-privacy.png",
    "guide/guide-12-file-backup.png": "12-backup-sync.png",
    "listing/listing-05-wish-grails.png": "26-wish-list.png",
    "guide/guide-26-wish-list.png": "26-wish-list.png",
    "guide/guide-30-cert-tracker.png": "30-cert-tracker.png",
    "guide/guide-32-photo-studio.png": "32-photo-studio.png",
    "guide/guide-37-settings.png": "37-settings.png",
    "guide/guide-40-zippo-decoder.png": "40-zippo-decoder.png",
}

COPY_STORE = {
    "listing/listing-01-home-command-center.png": "01-search-home.png",
    "listing/listing-02-collection-gallery.png": "02-collection.png",
    "listing/listing-03-identify-chips.png": "03-identify.png",
    "listing/listing-04-portfolio-pl.png": "04-analytics.png",
    "listing/listing-05-wish-grails.png": "05-hunt-alerts.png",
    "listing/listing-06-web-companion.png": "06-web-companion.png",
    "listing/listing-07-languages.png": "07-languages.png",
}

FALLBACK = {
    "00-terms-privacy.png": "01-home-command-center.png",
    "13-onboarding-welcome.png": "01-home-command-center.png",
    "14-onboarding-name.png": "01-home-command-center.png",
    "15-onboarding-categories.png": "05-identify.png",
    "16-onboarding-path.png": "01-home-command-center.png",
    "19-sample-home-banner.png": "01-home-command-center.png",
    "20-identify-result.png": "05-identify.png",
    "21-scan-individually.png": "05-identify.png",
    "22-identify-history.png": "05-identify.png",
    "23-add-item.png": "02-collection-gallery.png",
    "24-buying-budget.png": "06-portfolio-pl.png",
    "25-insurance-report.png": "06-portfolio-pl.png",
    "26-wish-list.png": "26-wish-list.png",
    "27-ebay-listings.png": "07-grail-radar.png",
    "28-tools-worth.png": "09-web-companion.png",
    "29-estate-intake.png": "02-collection-gallery.png",
    "30-cert-tracker.png": "30-cert-tracker.png",
    "31-set-completion.png": "02-collection-gallery.png",
    "32-photo-studio.png": "32-photo-studio.png",
    "33-passport.png": "02-collection-gallery.png",
    "34-event-calendar.png": "01-home-command-center.png",
    "35-offline-viewing.png": "01-home-command-center.png",
    "36-share-connect.png": "09-web-companion.png",
    "37-settings.png": "37-settings.png",
    "40-zippo-decoder.png": "40-zippo-decoder.png",
    "38-app-lock.png": "11-privacy.png",
    "39-upgrade.png": "10-language.png",
    "03-item-detail.png": "02-collection-gallery.png",
}


def copy_png(src: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.exists():
        shutil.copy2(src, dest)


def prepare_stills() -> None:
    ASSET_MANUAL.mkdir(parents=True, exist_ok=True)
    ASSET_STORE.mkdir(parents=True, exist_ok=True)
    for rel, dest_name in COPY_MANUAL.items():
        src = CVC_SHOTS.joinpath(*rel.split("/"))
        if src.exists():
            copy_png(src, ASSET_MANUAL / dest_name)
    for rel, dest_name in COPY_STORE.items():
        src = CVC_SHOTS.joinpath(*rel.split("/"))
        if src.exists():
            copy_png(src, ASSET_STORE / dest_name)
    home = ASSET_MANUAL / "01-home-command-center.png"
    for missing, fb in FALLBACK.items():
        dest = ASSET_MANUAL / missing
        if dest.exists() and dest.stat().st_size > 8000:
            continue
        src = ASSET_MANUAL / fb
        if src.exists():
            copy_png(src, dest)
        elif home.exists():
            copy_png(home, dest)


def export_play_1080(dest_dir: Path) -> None:
    dest_dir.mkdir(parents=True, exist_ok=True)
    for name in COPY_STORE.values():
        src = ASSET_STORE / name
        if not src.exists():
            continue
        im = Image.open(src).convert("RGB")
        w, h = im.size
        scale = 1080 / w
        nw, nh = 1080, int(h * scale)
        im = im.resize((nw, nh), Image.Resampling.LANCZOS)
        if nh >= 1920:
            im = im.crop((0, 0, 1080, 1920))
        else:
            canvas = Image.new("RGB", (1080, 1920), (247, 245, 240))
            canvas.paste(im, (0, (1920 - nh) // 2))
            im = canvas
        im.save(dest_dir / name, "PNG", optimize=True)


def slide_html(i: int, src: str, alt: str) -> str:
    loading = "eager" if i < 3 else "lazy"
    active = " active" if i == 0 else ""
    return (
        f'                  <div class="slide{active}" data-index="{i}" data-tap-none>\n'
        f'                    <img src="{src}" alt="{html.escape(alt)}" loading="{loading}">\n'
        f'                  </div>\n'
    )


def chapter_buttons() -> str:
    lines = []
    for idx, (start, label) in enumerate(CHAPTERS):
        active = " active" if idx == 0 else ""
        lines.append(
            f'        <button type="button" class="chapter-btn{active}" data-slide="{start}">{html.escape(label)}</button>'
        )
    return "\n".join(lines)


def build_index(slides: list[dict], narration: list[str]) -> str:
    n = len(slides) - 1
    chapter_starts = [str(c[0]) for c in CHAPTERS]
    slides_html = "".join(slide_html(i, s["src"], s.get("alt") or f"Step {i + 1}") for i, s in enumerate(slides))
    narr_js = ",\n    ".join(json.dumps(t, ensure_ascii=False) for t in narration)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Curator's Vault: Classics — User Guide | JosspaTech</title>
  <meta name="description" content="How to use Curator's Vault: Classics — Identify, vault, hunt, and Web Companion. Narrated walkthrough.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://josspatech.com/videos/cvc/user-guide/">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Curator's Vault: Classics — User Guide | JosspaTech">
  <meta property="og:description" content="Identify a piece, keep a private vault, and hunt grails. Step-by-step with narration.">
  <meta property="og:url" content="https://josspatech.com/videos/cvc/user-guide/">
  <meta property="og:site_name" content="JosspaTech">
  <meta property="og:image" content="https://josspatech.com/assets/brand/og-cvc.jpg">
  <script>if(new URLSearchParams(location.search).get('embed')==='1')document.documentElement.classList.add('embed-mode');</script>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Sans+3:wght@300;400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/videos/shared/walkthrough.css">
  <link rel="stylesheet" href="walkthrough.css?v=cvc-ug-2026-09-16">
  <link rel="stylesheet" href="/videos/shared/site-chrome.css?v=chrome-2026-07-28">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{ font-family: 'Source Sans 3', sans-serif; line-height: 1.6; background: var(--white); color: var(--navy); }}
    :root {{
      --navy: #1B4D3E; --navy-dark: #0F2E25; --navy-medium: #2A6B56;
      --gold: #C8AA6E; --gold-dark: #A8884A;
      --slate: #5A7068; --slate-light: #8A9E96;
      --background: #F5EDE4; --white: #FFFFFF;
    }}
    nav {{ position: sticky; top: 0; z-index: 1000; padding: 1rem 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); background-color: var(--navy-dark); }}
    nav .container {{ max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }}
    nav .logo {{ font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 700; color: var(--white); text-decoration: none; }}
    nav .nav-links {{ display: flex; gap: 1.5rem; align-items: center; list-style: none; flex-wrap: wrap; }}
    nav .nav-links a {{ color: var(--white); text-decoration: none; font-weight: 500; font-size: 0.95rem; }}
    nav .nav-links a:hover {{ color: var(--gold); }}
    .breadcrumbs {{ max-width: 1200px; margin: 0 auto; padding: 1rem 2rem 0; font-size: 0.95rem; color: var(--slate); }}
    .breadcrumbs a {{ color: var(--navy-medium); text-decoration: underline; text-decoration-color: var(--gold); text-underline-offset: 4px; font-weight: 700; }}
    .breadcrumbs span.sep {{ margin: 0 0.45rem; color: var(--slate-light); }}
    .breadcrumbs span.current {{ color: var(--navy); font-weight: 700; }}
    .hero {{ color: var(--white); padding: 2rem; text-align: center; background: linear-gradient(135deg, #0F2E25 0%, #1B4D3E 100%); }}
    .hero h1 {{ font-family: 'Playfair Display', serif; font-size: clamp(1.8rem, 4vw, 2.5rem); font-weight: 900; margin-bottom: 0.75rem; }}
    .hero .subheader {{ font-size: 1.05rem; max-width: 760px; margin: 0 auto; opacity: 0.95; line-height: 1.55; }}
    .walkthrough {{ padding: 3rem 2rem; background: var(--background); }}
    .walkthrough .container {{ max-width: 1200px; margin: 0 auto; }}
    .walkthrough h2 {{ font-family: 'Playfair Display', serif; font-size: 2rem; text-align: center; margin-bottom: 0.5rem; color: var(--navy); }}
    .walkthrough .section-sub {{ text-align: center; color: var(--slate); margin-bottom: 1.5rem; max-width: 820px; margin-left: auto; margin-right: auto; }}
    .phone-frame {{ width: 300px; border: 3px solid var(--navy-dark); border-radius: 24px; overflow: hidden; background: #000; aspect-ratio: 9/19.5; position: relative; box-shadow: 0 16px 48px rgba(15,46,37,0.22); }}
    .slideshow {{ width: 100%; height: 100%; position: relative; }}
    .slide {{ position: absolute; inset: 0; opacity: 0; transition: opacity 0.6s; }}
    .slide.active {{ opacity: 1; }}
    .slide img {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
    .cta-section {{ padding: 3rem 2rem; text-align: center; color: white; background: linear-gradient(135deg, #0F2E25 0%, #1B4D3E 100%); }}
    .cta-section h2 {{ font-family: 'Playfair Display', serif; font-size: 2rem; margin-bottom: 0.75rem; }}
    .cta-section p {{ max-width: 640px; margin: 0 auto 1.25rem; opacity: 0.9; line-height: 1.6; }}
    .download-button {{ display: inline-block; padding: 0.9rem 2rem; border-radius: 6px; font-weight: 700; text-decoration: none; margin: 0.35rem; background: var(--gold); color: var(--navy-dark); border: 2px solid var(--gold); }}
    .download-button:hover {{ background: var(--gold-dark); }}
    .download-button.ghost {{ background: transparent; color: var(--gold); }}
    footer {{ padding: 2rem; text-align: center; color: white; font-size: 0.9rem; background: var(--navy-dark); }}
    footer a {{ color: var(--gold); }}
    @media (max-width: 768px) {{
      nav .nav-links {{ gap: 0.75rem; font-size: 0.85rem; }}
      .walkthrough {{ padding: 2rem 1rem; }}
    }}
  </style>
</head>
<body data-jt-product="cvc">
  <nav>
    <div class="container">
      <a href="/" class="logo">JosspaTech</a>
      <ul class="nav-links">
        <li><a href="/">Home</a></li>
        <li><a href="/#cvc">Curator's Vault</a></li>
        <li><a href="/how-to/">How To</a></li>
      </ul>
    </div>
  </nav>
  <div class="breadcrumbs" aria-label="Breadcrumb">
    <a href="/">Home</a><span class="sep">/</span>
    <a href="/#cvc">Curator's Vault: Classics</a><span class="sep">/</span>
    <span class="current">User Guide</span>
  </div>
  <div class="hero">
    <div class="container">
      <h1>Curator's Vault: Classics — User Guide</h1>
      <p class="subheader">{len(slides)} steps with synced narration. Identify a piece, keep a private vault, and hunt grails — then open the same guide from Settings in the app.</p>
    </div>
  </div>
  <section class="user-manual walkthrough">
    <div class="container">
      <h2>Interactive User Guide</h2>
      <p class="section-sub">Tap a chapter to jump ahead, or press play. Previous and Next move one step. Tap any sentence in the transcript to jump there.</p>
      <div class="chapter-nav" id="chapterNav">
{chapter_buttons()}
      </div>
      <div class="user-manual-stage walkthrough-stage">
        <div class="video-wrapper">
          <div class="phone-column">
            <div class="phone-viewport">
              <div class="phone-frame">
                <div class="slideshow" id="slideshow">
                  <div class="tap-to-start" id="tapToStart">
                    <div class="tap-to-start-icon">&#9654;</div>
                    <div class="tap-to-start-label">Tap to play</div>
                  </div>
{slides_html}
                </div>
              </div>
            </div>
            <div class="progress-dots" id="dots"></div>
            <div class="playback-controls">
              <button type="button" class="nav-step-btn" id="prevBtn" title="Previous step" aria-label="Previous step">&#9664;</button>
              <button type="button" class="voice-btn" id="voiceBtn" title="Toggle narration" aria-label="Toggle narration">&#128266;</button>
              <button type="button" class="play-pause-btn" id="playPauseBtn" title="Play/Pause">&#9654;</button>
              <button type="button" class="nav-step-btn" id="nextBtn" title="Next step" aria-label="Next step">&#9654;&#9654;</button>
              <span class="speed-label" id="speedLabel">Tap play to start</span>
            </div>
          </div>
          <div class="narration-panel" id="narrationPanel">
            <div class="narration-panel-heading">Transcript</div>
            <div class="transcript-body" id="transcriptBody"></div>
          </div>
        </div>
      </div>
    </div>
  </section>
  <section class="cta-section">
    <div class="container">
      <h2>Ready to identify a piece?</h2>
      <p>Start free on Google Play Internal. Questions: support@josspatech.com.</p>
      <a href="https://play.google.com/apps/internaltest/4700723698680674529" class="download-button">Start on Google Play</a>
      <a href="/#cvc" class="download-button ghost">Product page</a>
    </div>
  </section>
  <footer class="jt-site-footer">
    <ul class="jt-products" aria-label="JosspaTech products">
      <li><a href="/">Home</a></li>
      <li><a href="/#pbj">PocketBudJet</a></li>
      <li><a href="/#hhh">Handy Horology Helper</a></li>
      <li><a href="/#pal">Pocket Allowance Ledger</a></li>
      <li><a href="/#cvc">Curator's Vault: Classics</a></li>
    </ul>
    <p class="jt-copy">&copy; 2026 JosspaTech. All Rights Reserved.</p>
    <p class="jt-legal"><a href="mailto:support@josspatech.com">support@josspatech.com</a></p>
  </footer>
  <script>
  const NARRATION = [
    {narr_js}
  ];
  const CHAPTER_STARTS = [{", ".join(chapter_starts)}];
  const LAST_SLIDE = {n};
  const AUDIO_BASE = 'audio/';
  </script>
  <script src="/videos/shared/walkthrough.js?v=cvc-ug-2026-09-16" defer></script>
  <script src="deck.js?v=cvc-ug-2026-09-16" defer></script>
  <script src="/scripts/site-analytics-saas.js" defer></script>
</body>
</html>
"""


def main() -> None:
    prepare_stills()
    play_dir = CVC_SHOTS / "play-phone-1080x1920"
    export_play_1080(play_dir)
    export_play_1080(ASSET_STORE / "play-1080")
    slides = json.loads(SHOT_MAP.read_text(encoding="utf-8"))
    narration = json.loads(NARRATION_JSON.read_text(encoding="utf-8"))
    if len(slides) != len(narration):
        raise SystemExit(f"shot-map {len(slides)} vs narration {len(narration)}")
    for row in slides:
        dest = ROOT.joinpath(*row["src"].lstrip("/").split("/"))
        row["exists"] = dest.exists() and dest.stat().st_size > 4000
    SHOT_MAP.write_text(json.dumps(slides, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    INDEX.write_text(build_index(slides, narration), encoding="utf-8")
    missing = [s["src"] for s in slides if not s["exists"]]
    print("Built %s - %s slides, %s chapters" % (INDEX, len(slides), len(CHAPTERS)))
    print("Play 1080x1920 at %s" % play_dir)
    if missing:
        print("Missing stills:", len(missing))
        for m in missing[:12]:
            print(" ", m)


if __name__ == "__main__":
    main()
