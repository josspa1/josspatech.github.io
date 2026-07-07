#!/usr/bin/env python3
"""Build Handy Horology Helper user manual at videos/user-guide-hhh/index.html."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "videos" / "user-guide-hhh" / "index.html"
NARRATION_JSON = ROOT / "videos" / "user-guide-hhh" / "narration-en.json"
COVERAGE_MD = ROOT / "docs" / "HHH_USER_MANUAL_COVERAGE.md"

M = "/assets/screenshots/hhh/manual/"
H = "/assets/screenshots/hhh/"


def S(chapter, feature, narration, img=None, png_status="missing", alt="", tap=None):
    return {
        "chapter": chapter,
        "feature": feature,
        "narration": narration,
        "img": img,
        "png_status": png_status if img else "missing",
        "alt": alt or feature,
        "tap": tap,
    }


SLIDES = [
    S("Welcome", "Install HHH",
      "Install Handy Horology Helper from Google Play internal testing or request a TestFlight invite from josspatech.com. Open the app to the welcome carousel.",
      f"{M}01-home-command-center.png", "OK", "HHH welcome and Command Center"),
    S("Welcome", "Choose your path",
      "After the welcome slides, pick Explore with sample collection to tour Harold's demo gallery, or Start with my own piece to add your first watch from the camera.",
      f"{M}01-home-command-center.png", "interim", "Onboarding path choice"),
    S("Home", "Command Center",
      "The Home tab is your Command Center. See how many pieces you own, what's on your wish list, and quick commands for Hunt, Fix clock, Add Watch, and Tools.",
      f"{M}01-home-command-center.png", "OK", "Command Center home screen"),
    S("My Museum", "Collection gallery",
      "Open My Pieces to enter My Museum. Portfolio value and profit tracking sit at the top. Switch between Owned, Wish, and For Sale tabs.",
      f"{M}02-museum-collection.png", "OK", "My Museum collection view"),
    S("My Museum", "Add a piece",
      "Tap Add to photograph a watch, pick from the catalog, or enter details manually. Each piece stores photos, provenance, service history, and estimated value.",
      f"{M}02-museum-collection.png", "interim", "Add piece from My Museum", (50, 88, "Add")),
    S("Identify", "Snap a photo",
      "From Tools or the Identify quick action, photograph a dial, caseback, or movement. HHH sends the image to AI and returns ranked brand and model matches.",
      None, "missing", "AI Identify camera screen", (50, 55, "Identify")),
    S("Identify", "Review matches",
      "Review confidence scores for each match. Save the top result straight to My Museum or compare alternatives before you buy, sell, or insure.",
      None, "missing", "Identify results with confidence scores"),
    S("Clock Repair", "Pick a symptom",
      "Clock not running right? Open Clock Repair Help from Home or Tools. Pick a symptom like won't chime, pendulum stops, or hands slip.",
      None, "missing", "Clock Repair Help symptom list", (50, 45, "Fix clock")),
    S("Clock Repair", "Find parts",
      "HHH walks you through likely causes and suggests parts from a major supplier catalog so you order the right item the first time.",
      None, "missing", "Suggested repair parts list"),
    S("Grail Radar", "Wish list targets",
      "Add grails to your Wish list with target prices. Keep hunting pieces separate from what you already own in My Museum.",
      f"{M}02-museum-collection.png", "interim", "Wish list tab", (66, 22, "Wish")),
    S("Grail Radar", "eBay Hunt Alerts",
      "Tap Hunt on Home or open eBay Hunt Alerts under Tools. Set keywords and a max price — HHH checks eBay when you open the app and notifies you of new matches.",
      f"{M}01-home-command-center.png", "interim", "Hunt quick command", (13, 24, "Hunt")),
    S("Financial", "Profit and loss",
      "Enter purchase price and expenses on each piece. My Museum shows estimated value, gain or loss per item, and portfolio totals across your collection.",
      f"{M}02-museum-collection.png", "interim", "Portfolio dashboard card"),
    S("Tools", "Horology toolkit",
      "Tools holds Identify, Clock Repair Help, eBay Hunt Alerts, Exact Time, Moon Phase, Reference Library, and more — your bench reference in one place.",
      f"{M}08-tools-hub.png", "OK", "Tools hub"),
    S("Web Companion", "Browse on your PC",
      "Open Web Companion under Tools. HHH starts a server on your phone — scan the QR code from a PC browser on the same Wi‑Fi to browse your collection on a big screen.",
      None, "missing", "Web Companion QR pairing", (50, 50, "Web Companion")),
    S("Backup", "Export and restore",
      "In Settings, open Backup and Restore. Share a full encrypted backup through Drive, iCloud, or your PC via the system share sheet. Restore replaces local data on a new phone.",
      None, "missing", "Backup and restore settings", (50, 55, "Backup")),
    S("Settings", "Theme and languages",
      "Settings controls light or dark theme, seven display languages, notification preferences, and app lock. Changes apply immediately.",
      None, "missing", "Settings screen", (90, 97, "Settings")),
    S("Trial", "Pro subscription",
      "HHH includes a 14-day Pro trial with full access. After the trial, subscribe for $9.99 per month or $74.99 per year. Pro unlocks Hunt Alerts, advanced tools, and cloud backup.",
      None, "missing", "Trial and subscription"),
    S("Help", "Support",
      "Questions? Email support@josspatech.com or use in-app feedback. This guide at josspatech.com/videos/user-guide-hhh/ covers every shipped v1 feature.",
      f"{M}01-home-command-center.png", "interim", "Help and support"),
]

CHAPTER_PILLS: list[tuple[str, int]] = []
_seen: set[str] = set()
for i, slide in enumerate(SLIDES):
    ch = slide["chapter"]
    if ch not in _seen:
        _seen.add(ch)
        CHAPTER_PILLS.append((ch, i))

PLACEHOLDER = (
    '<div style="width:100%;height:100%;display:flex;flex-direction:column;align-items:center;'
    'justify-content:center;background:#F5EDE4;color:#3D1522;padding:1.5rem;text-align:center;">'
    '<p style="font-family:\'Playfair Display\',serif;font-size:1rem;font-weight:700;margin-bottom:0.5rem;">{title}</p>'
    '<p style="font-size:0.82rem;line-height:1.5;color:#A89890;">Narration describes this screen — device capture pending.</p></div>'
)


def tap_attrs(tap):
    if tap is None:
        return ' data-tap-none'
    x, y, label = tap
    return f' data-tap-x="{x}" data-tap-y="{y}" data-tap-label="{label.replace(chr(34), "")}"'


def slide_inner(slide, idx):
    if slide["img"]:
        loading = "eager" if idx == 0 else "lazy"
        return f'<img src="{slide["img"]}" alt="{slide["alt"]}" loading="{loading}">'
    return PLACEHOLDER.format(title=slide["alt"])


def render_slides():
    lines = []
    for i, slide in enumerate(SLIDES):
        cls = "slide active" if i == 0 else "slide"
        lines.append(f' <div class="{cls}" data-index="{i}"{tap_attrs(slide["tap"])}>')
        lines.append(f" {slide_inner(slide, i)}")
        lines.append(" </div>")
    return "\n".join(lines)


def render_transcript():
    lines = ['<div class="transcript-body" id="transcriptBody">']
    for i, slide in enumerate(SLIDES):
        cls = "transcript-para current" if i == 0 else "transcript-para"
        lines.append(f' <p class="{cls}" data-slide="{i}">{slide["narration"]}</p>')
    lines.append("</div>")
    return "\n".join(lines)


def render_chapters():
    return "\n".join(
        f' <button class="chapter-btn{" active" if j == 0 else ""}" data-slide="{start}">{label}</button>'
        for j, (label, start) in enumerate(CHAPTER_PILLS)
    )


def render_dots():
    return "\n".join(
        f' <span class="dot{" active" if i == 0 else ""}" data-slide="{i}"></span>'
        for i in range(len(SLIDES))
    )


def build_html() -> str:
    n = len(SLIDES)
    last = n - 1
    starts = ", ".join(str(s) for _, s in CHAPTER_PILLS)
    narr_js = ",\n ".join(json.dumps(s["narration"], ensure_ascii=False) for s in SLIDES)
    return textwrap.dedent(
        f"""\
        <!DOCTYPE html>
        <html lang="en">
        <head>
         <meta charset="UTF-8">
         <meta name="viewport" content="width=device-width, initial-scale=1.0">
         <title>Handy Horology Helper User Manual | JosspaTech</title>
         <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Sans+3:wght@300;400;600;700&display=swap" rel="stylesheet">
         <link rel="stylesheet" href="walkthrough.css">
         <link rel="stylesheet" href="/videos/shared/walkthrough.css">
         <style>
         * {{ margin: 0; padding: 0; box-sizing: border-box; }}
         html {{ scroll-behavior: smooth; }}
         body {{ font-family: 'Source Sans 3', sans-serif; line-height: 1.6; background: var(--white); }}
         nav {{ position: sticky; top: 0; z-index: 1000; padding: 1rem 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
         nav .container {{ max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }}
         nav .logo {{ font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 700; color: var(--white); text-decoration: none; }}
         nav .nav-links {{ display: flex; gap: 1.5rem; align-items: center; list-style: none; }}
         nav .nav-links a {{ color: var(--white); text-decoration: none; font-weight: 500; }}
         .breadcrumbs {{ max-width: 1200px; margin: 0 auto; padding: 1rem 2rem 0; font-size: 0.9rem; color: var(--slate); }}
         .breadcrumbs a {{ color: var(--navy-medium); text-decoration: none; font-weight: 500; }}
         .hero {{ color: var(--white); padding: 2rem; text-align: center; }}
         .hero h1 {{ font-family: 'Playfair Display', serif; font-size: 2.5rem; font-weight: 900; margin-bottom: 0.75rem; }}
         .hero .subheader {{ font-size: 1.1rem; max-width: 760px; margin: 0 auto; opacity: 0.95; }}
         .walkthrough {{ padding: 3rem 2rem; }}
         .walkthrough .container {{ max-width: 1200px; margin: 0 auto; }}
         .walkthrough h2 {{ font-family: 'Playfair Display', serif; font-size: 2rem; text-align: center; margin-bottom: 0.5rem; }}
         .walkthrough .section-sub {{ text-align: center; color: var(--slate); margin-bottom: 1.5rem; }}
         .video-wrapper {{ display: flex; gap: 2rem; align-items: flex-start; }}
         .phone-column {{ flex-shrink: 0; width: 360px; }}
         .phone-frame {{ width: 340px; border: 3px solid var(--navy-dark); border-radius: 24px; overflow: hidden; background: #000; aspect-ratio: 9/19.5; max-height: 640px; position: relative; }}
         .slideshow {{ width: 100%; height: 100%; position: relative; }}
         .slide {{ position: absolute; inset: 0; opacity: 0; transition: opacity 0.6s; }}
         .slide.active {{ opacity: 1; }}
         .slide img {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
         .progress-dots {{ display: flex; justify-content: center; gap: 8px; margin-top: 1rem; flex-wrap: wrap; }}
         .dot {{ width: 10px; height: 10px; border-radius: 50%; background: rgba(91,35,51,0.2); cursor: pointer; }}
         .playback-controls {{ display: flex; justify-content: center; gap: 1rem; margin-top: 1rem; align-items: center; }}
         .play-pause-btn, .voice-btn {{ color: white; border: none; border-radius: 50%; width: 44px; height: 44px; cursor: pointer; }}
         .narration-panel {{ flex: 1; max-height: 580px; overflow-y: auto; padding: 0.5rem; }}
         .chapter-nav {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5rem; margin-top: 1.5rem; }}
         .chapter-btn {{ padding: 0.55rem 1rem; border-radius: 20px; cursor: pointer; font-size: 0.88rem; }}
         .cta-section {{ padding: 3rem 2rem; text-align: center; color: white; }}
         .cta-section h2 {{ font-family: 'Playfair Display', serif; font-size: 2rem; margin-bottom: 0.75rem; }}
         .download-button {{ display: inline-block; padding: 0.9rem 2rem; border-radius: 6px; font-weight: 700; text-decoration: none; margin-top: 1rem; }}
         footer {{ padding: 2rem; text-align: center; color: white; font-size: 0.9rem; }}
         body.record-mode nav, body.record-mode .breadcrumbs, body.record-mode .hero, body.record-mode .cta-section, body.record-mode footer {{ display: none !important; }}
         :root {{
           --navy: #5B2333; --navy-dark: #3D1522; --navy-medium: #7A3A4F;
           --gold: #C8AA6E; --gold-dark: #A8884A;
           --slate: #8A7070; --slate-light: #A89890;
           --background: #F5EDE4; --white: #FFFFFF;
         }}
         nav {{ background-color: var(--navy-dark); }}
         nav .cta-button {{ background-color: var(--gold); color: var(--navy-dark); }}
         .hero {{ background: linear-gradient(135deg, var(--navy) 0%, var(--navy-dark) 100%); }}
         .walkthrough h2, .narration-panel-heading, .transcript-sentence.active {{ color: var(--navy); }}
         .chapter-btn {{ background: var(--navy); border-color: var(--navy); }}
         .chapter-btn.active {{ background: var(--gold); color: var(--navy-dark); border-color: var(--gold); }}
         .dot.active {{ background: var(--gold); }}
         .play-pause-btn, .voice-btn {{ background: var(--navy); }}
         .phone-frame {{ border-color: var(--navy-dark); box-shadow: 0 16px 48px rgba(61,21,34,0.22); }}
         .tap-ring {{ border-color: var(--gold); box-shadow: 0 0 12px rgba(200,170,110,0.45); }}
         .transcript-para.current {{ border-left-color: var(--gold); background: rgba(200,170,110,0.1); }}
         .narration-panel-heading {{ border-bottom-color: var(--gold); }}
         .download-button {{ background: var(--gold); color: var(--navy-dark); border-color: var(--gold); }}
         footer {{ background: var(--navy-dark); }}
         footer a {{ color: var(--gold); }}
         body {{ color: var(--navy); }}
         .walkthrough {{ background: var(--background); }}
         .slide img {{ background: var(--background); }}
         </style>
        </head>
        <body>
         <nav>
          <div class="container">
           <a href="/" class="logo">JosspaTech</a>
           <ul class="nav-links">
            <li><a href="/">Home</a></li>
            <li><a href="/#hhh">Handy Horology Helper</a></li>
            <li><a href="/docs/handyhorology/HandyHorology_UserGuide.pdf">PDF</a></li>
            <li><a href="https://play.google.com/apps/internaltest/4701583732703251381" class="cta-button">Get the App</a></li>
           </ul>
          </div>
         </nav>
         <div class="breadcrumbs">
          <a href="/">Home</a><span class="sep">/</span>
          <a href="/#hhh">Handy Horology Helper</a><span class="sep">/</span>
          <span class="current">User Manual</span>
         </div>
         <div class="hero">
          <div class="container">
           <h1>Handy Horology Helper User Manual</h1>
           <p class="subheader">v1.0.22 — identify watches and clocks, track your collection, hunt grails on eBay, and find repair parts. Plain-English walkthrough of every shipped feature.</p>
          </div>
         </div>
         <section class="walkthrough">
          <div class="container">
           <h2>Interactive User Guide</h2>
           <p class="section-sub">{n} slides with synced narration — install through trial and support. Use the {len(CHAPTER_PILLS)} chapter pills to jump, or read the transcript beside the phone. <a href="/docs/handyhorology/HandyHorology_UserGuide.pdf" style="color:var(--navy-medium);font-weight:700;">Download PDF</a> · <a href="handy-horology-helper-user-guide.mp4" style="color:var(--navy-medium);font-weight:700;">Watch MP4</a></p>
           <div class="walkthrough-stage">
            <div class="video-wrapper">
             <div class="phone-column">
              <div class="phone-viewport">
               <div class="phone-frame">
                <div class="slideshow" id="slideshow">
                 <div class="tap-to-start" id="tapToStart">
                  <div class="tap-to-start-icon">&#9654;</div>
                  <div class="tap-to-start-label">Tap to play</div>
                 </div>
        {render_slides()}
                </div>
               </div>
              </div>
              <div class="progress-dots" id="progressDots">
        {render_dots()}
              </div>
              <div class="playback-controls">
               <button class="voice-btn" id="voiceBtn" title="Toggle narration" aria-label="Toggle narration">&#128266;</button>
               <button class="play-pause-btn" id="playPauseBtn" title="Play/Pause">&#9654;</button>
               <span class="speed-label" id="speedLabel">Tap play to start</span>
              </div>
             </div>
             <div class="narration-panel" id="narrationPanel">
              <div class="narration-panel-heading">Transcript</div>
        {render_transcript()}
             </div>
            </div>
           </div>
           <div class="chapter-nav" id="chapterNav">
        {render_chapters()}
           </div>
          </div>
         </section>
         <section class="cta-section">
          <div class="container">
           <h2>Ready to identify your first timepiece?</h2>
           <p>Try HHH free for 14 days on Google Play internal testing or request iOS TestFlight from josspatech.com.</p>
           <a href="https://play.google.com/apps/internaltest/4701583732703251381" class="download-button">Get HHH on Google Play</a>
          </div>
         </section>
         <footer>
          <p>&copy; 2026 JosspaTech · <a href="/docs/handyhorology/HandyHorology_PrivacyPolicy.html">Privacy</a> · <a href="/docs/handyhorology/HandyHorologyHelper_TermsOfService.html">Terms</a></p>
         </footer>
         <script>
         const NARRATION = [
          {narr_js}
         ];
         const CHAPTER_STARTS = [{starts}];
         const LAST_SLIDE = {last};
         const AUDIO_BASE = 'audio/';
         </script>
         <script src="/videos/shared/walkthrough.js" defer></script>
         <script src="deck.js" defer></script>
        </body>
        </html>
        """
    )


def write_deck_js():
    deck = ROOT / "videos" / "user-guide-hhh" / "deck.js"
    deck.write_text(
        textwrap.dedent(
            """\
            (function () {
              var current = 0;
              var playing = false;
              var voiceEnabled = true;
              var audioUnlocked = false;
              var slideAudio = null;
              var timer = null;
              var SLIDE_MS = 8000;
              var slides = document.querySelectorAll('.slide');
              var dots = document.querySelectorAll('.dot');
              var paras = document.querySelectorAll('.transcript-para');
              var playBtn = document.getElementById('playPauseBtn');
              var voiceBtn = document.getElementById('voiceBtn');
              var speedLabel = document.getElementById('speedLabel');
              var tapStart = document.getElementById('tapToStart');
              var recordMode = /[?&]record=1/.test(location.search);
              if (recordMode) document.body.classList.add('record-mode');

              function goTo(i) {
                current = Math.max(0, Math.min(i, LAST_SLIDE));
                slides.forEach(function (s, j) { s.classList.toggle('active', j === current); });
                dots.forEach(function (d, j) { d.classList.toggle('active', j === current); });
                paras.forEach(function (p, j) { p.classList.toggle('current', j === current); });
                if (window.syncTranscriptSlide) window.syncTranscriptSlide(current);
              }

              function resetTimer() {
                clearTimeout(timer);
                timer = setTimeout(function () { if (playing) goTo(current + 1 > LAST_SLIDE ? 0 : current + 1); if (playing) playSlide(); }, SLIDE_MS);
              }

              function playSlideAudio(i) {
                if (!voiceEnabled) { resetTimer(); return; }
                if (slideAudio) { slideAudio.pause(); slideAudio = null; }
                slideAudio = new Audio(AUDIO_BASE + 'slide-' + i + '.mp3');
                slideAudio.onended = resetTimer;
                slideAudio.onerror = resetTimer;
                slideAudio.play().catch(resetTimer);
              }

              function playSlide() {
                goTo(current);
                if (playing && voiceEnabled) playSlideAudio(current); else resetTimer();
              }

              function startPlayback() {
                audioUnlocked = true;
                playing = true;
                if (tapStart) tapStart.classList.add('hidden');
                playBtn.innerHTML = '&#10074;&#10074;';
                speedLabel.textContent = 'Playing';
                playSlide();
              }

              playBtn.addEventListener('click', function () {
                if (!playing) startPlayback();
                else { playing = false; playBtn.innerHTML = '&#9654;'; speedLabel.textContent = 'Paused'; clearTimeout(timer); if (slideAudio) slideAudio.pause(); }
              });
              if (tapStart) tapStart.addEventListener('click', startPlayback);
              voiceBtn.addEventListener('click', function () {
                voiceEnabled = !voiceEnabled;
                voiceBtn.classList.toggle('muted', !voiceEnabled);
              });
              dots.forEach(function (d) { d.addEventListener('click', function () { goTo(+d.dataset.slide); }); });
              document.querySelectorAll('.chapter-btn').forEach(function (b) {
                b.addEventListener('click', function () {
                  document.querySelectorAll('.chapter-btn').forEach(function (x) { x.classList.remove('active'); });
                  b.classList.add('active');
                  goTo(+b.dataset.slide);
                });
              });
              document.addEventListener('keydown', function (e) {
                if (e.key === 'ArrowRight') goTo(current + 1);
                if (e.key === 'ArrowLeft') goTo(current - 1);
              });
              goTo(0);
              if (window.initWalkthroughSlides) window.initWalkthroughSlides();
            })();
            """
        ),
        encoding="utf-8",
    )


def write_coverage():
    ok = sum(1 for s in SLIDES if s["png_status"] == "OK")
    interim = sum(1 for s in SLIDES if s["png_status"] == "interim")
    missing = sum(1 for s in SLIDES if s["png_status"] == "missing" or not s["img"])
    lines = [
        "# HHH User Manual Coverage",
        "",
        "**Live URL:** https://josspatech.com/videos/user-guide-hhh/  ",
        "**PDF:** https://josspatech.com/docs/handyhorology/HandyHorology_UserGuide.pdf  ",
        "**MP4:** https://josspatech.com/videos/user-guide-hhh/handy-horology-helper-user-guide.mp4  ",
        f"**Slide count:** {len(SLIDES)}  ",
        f"**Chapter pills:** {len(CHAPTER_PILLS)}  ",
        "",
        "## Summary",
        "",
        f"| PNG OK | {ok} |",
        f"| PNG interim (reuse) | {interim} |",
        f"| PNG missing (placeholder) | {missing} |",
        "",
        "## Locales",
        "",
        "English only for v1. HHH app supports 7 display languages in Settings; locale folders deferred (PBJ has 8).",
        "",
        "## Regenerate",
        "",
        "```powershell",
        "cd josspatech.github.io",
        "python scripts/capture-hhh-manual-screenshots.py",
        "python scripts/build-hhh-user-manual-slides.py",
        "python scripts/gen-user-guide-hhh-en-audio.py --force",
        "node scripts/render-user-guide-hhh-video.js",
        "python scripts/build-hhh-user-guide-pdf.py",
        "```",
        "",
    ]
    COVERAGE_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(build_html(), encoding="utf-8")
    NARRATION_JSON.write_text(
        json.dumps([s["narration"] for s in SLIDES], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_deck_js()
    write_coverage()
    print(f"Built {len(SLIDES)} slides, {len(CHAPTER_PILLS)} chapters -> {INDEX}")


if __name__ == "__main__":
    main()
