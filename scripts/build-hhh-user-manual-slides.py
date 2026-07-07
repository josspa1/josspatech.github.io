#!/usr/bin/env python3
"""Build HHH user manual from docs/users-manual/*.md (PBJ parity).

Parses User asks / What to do numbered steps into imperative tap-step slides.
Image + tap metadata in STEP_META keyed by topic id and step index.
"""
from __future__ import annotations

import json
import re
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "videos" / "user-guide-hhh" / "index.html"
NARRATION_JSON = ROOT / "videos" / "user-guide-hhh" / "narration-en.json"
COVERAGE_MD = ROOT / "docs" / "HHH_USER_MANUAL_COVERAGE.md"
HHH_MANUAL = Path(r"C:\Users\jossp\Documents\MobileApps\HHH\SourceCode\docs\users-manual")

M = "/assets/screenshots/hhh/manual/"
HOME = f"{M}01-home-command-center.png"
MUSEUM = f"{M}02-museum-collection.png"
DETAIL = f"{M}03-piece-detail.png"
WISH = f"{M}04-wishlist-grails.png"
GRAIL = f"{M}05-ebay-grail-radar.png"
CLOCK_SYM = f"{M}06a-clock-repair-symptoms.png"
CLOCK_PARTS = f"{M}06-clockworks-parts.png"
ID_CAM = f"{M}07a-identify-camera.png"
ID_RES = f"{M}07-identify-results.png"
TOOLS = f"{M}08-tools-hub.png"
WEB = f"{M}09-web-companion.png"
SETTINGS = f"{M}10-settings.png"
BACKUP = f"{M}11-backup-restore.png"
TRIAL = f"{M}12-trial-subscription.png"
WELCOME = f"{M}13-onboarding-welcome.png"
PATH = f"{M}14-onboarding-path.png"
FIN = f"{M}15-finances-pl.png"
COMPARE = f"{M}16-compare.png"
ATOMIC = f"{M}17-atomic-clock.png"
MOON = f"{M}18-moon-phase.png"


def S(chapter, feature, narration, img=None, png_status="missing", alt="", tap=None):
    return {
        "chapter": chapter,
        "feature": feature,
        "narration": narration,
        "img": img,
        "png_status": png_status if img else "missing",
        "alt": alt or feature,
        "tap": tap,
        "topic": "",
    }


def _meta(img, status="OK", alt="", tap=None):
    return {"img": img, "png_status": status, "alt": alt, "tap": tap}


# Per-topic step metadata (index aligns with parsed What to do steps)
STEP_META: dict[str, list[dict]] = {
    "UM-H01": [
        _meta(None, "missing", "Google Play internal testing install"),
        _meta(None, "missing", "TestFlight install"),
    ],
    "UM-H02": [
        _meta(WELCOME, "OK", "Welcome carousel", (50, 92, "Continue")),
        _meta(WELCOME, "interim", "Welcome — Get Started", (50, 92, "Get Started")),
        _meta(PATH, "OK", "Sample vs own piece choice", (50, 55, "Sample collection")),
        _meta(PATH, "OK", "Start with my own piece", (50, 70, "Own piece")),
    ],
    "UM-H03": [
        _meta(HOME, "interim", "Sample collection loading", (50, 92, "Get Started")),
        _meta(HOME, "interim", "Sample mode banner"),
        _meta(SETTINGS, "interim", "Clear sample data", (50, 75, "Clear sample")),
    ],
    "UM-H04": [
        _meta(HOME, "OK", "Command Center home screen"),
        _meta(HOME, "OK", "Quick commands row", (50, 28, "Quick commands")),
        _meta(HOME, "interim", "Getting started path cards", (50, 45, "Path card")),
        _meta(HOME, "interim", "Bottom tab bar", (50, 97, "Tab bar")),
    ],
    "UM-H05": [
        _meta(MUSEUM, "OK", "Tap My Pieces tab", (30, 97, "My Pieces")),
        _meta(MUSEUM, "OK", "Owned Wish For Sale tabs", (25, 18, "Owned")),
        _meta(MUSEUM, "OK", "Portfolio value hero card"),
        _meta(MUSEUM, "interim", "Search collection", (50, 14, "Search")),
        _meta(MUSEUM, "OK", "Tap piece in list", (50, 35, "Piece row")),
        _meta(DETAIL, "OK", "Piece detail overview"),
        _meta(DETAIL, "interim", "Provenance section", (50, 55, "Provenance")),
        _meta(DETAIL, "interim", "Service history", (50, 65, "Service")),
        _meta(WISH, "OK", "Wish list segment", (66, 18, "Wish")),
        _meta(WISH, "interim", "For Sale segment", (88, 18, "For Sale")),
        _meta(MUSEUM, "interim", "My Museum More menu", (88, 12, "More")),
    ],
    "UM-H06": [
        _meta(MUSEUM, "OK", "Tap Add on action bar", (50, 92, "Add")),
        _meta(ID_CAM, "OK", "Tap Manual entry", (50, 22, "Manual")),
        _meta(ID_CAM, "interim", "Fill manual fields", (50, 50, "Brand")),
        _meta(ID_CAM, "OK", "Tap Save", (50, 88, "Save")),
    ],
    "UM-H07": [
        _meta(MUSEUM, "interim", "Tap Identify", (50, 92, "Identify")),
        _meta(ID_CAM, "OK", "Take Photo", (50, 35, "Take Photo")),
        _meta(ID_CAM, "OK", "Choose Photo", (50, 48, "Choose Photo")),
        _meta(ID_CAM, "interim", "Optional movement photo", (50, 72, "Skip")),
        _meta(ID_CAM, "interim", "Manual clue fields", (50, 58, "Brand guess")),
        _meta(ID_CAM, "interim", "Item type toggle", (50, 22, "Item type")),
        _meta(ID_CAM, "OK", "Identify this timepiece", (50, 88, "Identify")),
    ],
    "UM-H08": [
        _meta(ID_RES, "OK", "Top match confidence", (50, 40, "Top match")),
        _meta(ID_RES, "OK", "This is correct", (50, 55, "This is correct")),
        _meta(ID_RES, "interim", "Add detail photos", (50, 70, "Detail photos")),
        _meta(ID_RES, "interim", "Edit clues", (50, 62, "What I know")),
        _meta(ID_RES, "OK", "Save to Collection", (50, 82, "Save")),
        _meta(ID_RES, "interim", "Find parts on Clockworks", (50, 90, "Find parts")),
        _meta(None, "missing", "Offline identify queue"),
    ],
    "UM-H09": [
        _meta(CLOCK_SYM, "interim", "Home Fix clock", (38, 28, "Fix clock")),
        _meta(TOOLS, "interim", "Tools Clock Repair Help", (50, 45, "Clock Repair")),
        _meta(CLOCK_SYM, "OK", "Symptom list", (50, 42, "Symptom")),
        _meta(CLOCK_PARTS, "interim", "Repair guidance steps"),
        _meta(CLOCK_PARTS, "OK", "Suggested parts list"),
    ],
    "UM-H10": [
        _meta(CLOCK_PARTS, "OK", "Shop on Clockworks", (50, 75, "Shop")),
        _meta(CLOCK_PARTS, "interim", "Clockworks checkout in browser"),
    ],
    "UM-H11": [
        _meta(WISH, "interim", "Hunt quick command", (13, 28, "Hunt")),
        _meta(WISH, "interim", "Add wish list item", (88, 12, "Add")),
        _meta(GRAIL, "OK", "Grail Radar screen"),
        _meta(GRAIL, "interim", "Hunt rules editor", (50, 55, "Save rules")),
        _meta(GRAIL, "OK", "Check now", (50, 75, "Check now")),
        _meta(GRAIL, "interim", "Open eBay listing", (50, 65, "Listing")),
        _meta(None, "missing", "eBay match notification"),
    ],
    "UM-H12": [
        _meta(TOOLS, "interim", "eBay Listings tool", (50, 40, "eBay Listings")),
        _meta(GRAIL, "interim", "eBay search results"),
    ],
    "UM-H13": [
        _meta(FIN, "OK", "Finances menu", (50, 50, "Finances")),
        _meta(FIN, "OK", "P/L portfolio dashboard"),
        _meta(DETAIL, "interim", "Enter purchase price", (50, 48, "Purchase price")),
        _meta(DETAIL, "interim", "Add service expense", (50, 68, "Add entry")),
        _meta(MUSEUM, "interim", "Insurance Report", (50, 55, "Insurance")),
    ],
    "UM-H14": [
        _meta(FIN, "interim", "Budget Tracker", (50, 60, "Budget")),
        _meta(FIN, "interim", "Budget progress"),
    ],
    "UM-H15": [
        _meta(WEB, "OK", "Web Companion screen", (50, 55, "Web Companion")),
        _meta(WEB, "OK", "QR code pairing", (50, 45, "QR code")),
        _meta(WEB, "interim", "PC companion dashboard"),
    ],
    "UM-H16": [
        _meta(BACKUP, "OK", "Backup and Restore", (50, 55, "Backup")),
        _meta(BACKUP, "OK", "Export backup", (50, 65, "Export")),
        _meta(BACKUP, "interim", "Restore backup", (50, 75, "Restore")),
        _meta(BACKUP, "interim", "Cloud sync toggle", (50, 85, "Cloud sync")),
    ],
    "UM-H17": [
        _meta(SETTINGS, "OK", "Settings tab", (90, 97, "Settings")),
        _meta(SETTINGS, "interim", "Theme toggle", (50, 35, "Theme")),
        _meta(SETTINGS, "interim", "Language picker", (50, 45, "Language")),
        _meta(SETTINGS, "interim", "App lock", (50, 55, "App lock")),
        _meta(SETTINGS, "interim", "Notification preferences", (50, 65, "Notifications")),
    ],
    "UM-H18": [
        _meta(TRIAL, "OK", "Trial intro"),
        _meta(TRIAL, "OK", "Subscribe to Pro", (50, 70, "Subscribe")),
        _meta(TRIAL, "interim", "Manage subscription", (50, 80, "Manage")),
    ],
    "UM-H19": [
        _meta(TOOLS, "OK", "Tools tab", (50, 97, "Tools")),
        _meta(TOOLS, "interim", "What's It Worth Pro", (50, 30, "Worth")),
        _meta(COMPARE, "OK", "Compare two pieces", (50, 35, "Compare")),
        _meta(TOOLS, "interim", "Condition Assessment", (50, 40, "Condition")),
        _meta(FIN, "interim", "Collection Value trend", (50, 45, "Value trend")),
        _meta(TOOLS, "interim", "Trade Analyzer Pro", (50, 50, "Trade")),
        _meta(TOOLS, "interim", "Ask the Expert Pro", (50, 55, "Ask Expert")),
        _meta(TOOLS, "interim", "Photo Studio Pro", (50, 58, "Photo Studio")),
        _meta(TOOLS, "interim", "Digital ID Card Pro", (50, 60, "ID Card")),
        _meta(TOOLS, "interim", "Scan Barcode", (50, 62, "Barcode")),
        _meta(TOOLS, "interim", "Scan Papers", (50, 64, "Scan Papers")),
        _meta(TOOLS, "interim", "Complication calculator", (50, 66, "Complexity")),
        _meta(TOOLS, "interim", "Accuracy tracker", (50, 68, "Accuracy")),
        _meta(TOOLS, "interim", "Rotation planner", (50, 70, "Rotation")),
        _meta(TOOLS, "interim", "Warranty tracker", (50, 72, "Warranty")),
        _meta(TOOLS, "interim", "Event calendar", (50, 74, "Events")),
        _meta(ATOMIC, "OK", "Exact Time atomic clock", (50, 40, "Exact Time")),
        _meta(MOON, "OK", "Moon Phase tool", (50, 45, "Moon Phase")),
        _meta(TOOLS, "interim", "Print and Export List", (50, 78, "Print")),
        _meta(TOOLS, "interim", "Nearby Finds Pro", (50, 80, "Flea market")),
        _meta(TOOLS, "interim", "BLE Share Pro", (50, 82, "Share Nearby")),
        _meta(TOOLS, "interim", "LAN Report big screen", (50, 84, "Big Screen")),
        _meta(TOOLS, "interim", "Movement to Parts tool", (50, 50, "Movement → Parts")),
    ],
    "UM-H20": [
        _meta(HOME, "interim", "Help and support"),
        _meta(HOME, "interim", "User manual link"),
    ],
}

TOPIC_CHAPTER: dict[str, str] = {
    "UM-H01": "Install",
    "UM-H02": "Onboarding",
    "UM-H03": "Onboarding",
    "UM-H04": "Home",
    "UM-H05": "My Museum",
    "UM-H06": "Add Watch",
    "UM-H07": "Identify",
    "UM-H08": "Identify",
    "UM-H09": "Clock Repair",
    "UM-H10": "Clock Repair",
    "UM-H11": "Grail Radar",
    "UM-H12": "Grail Radar",
    "UM-H13": "Finances",
    "UM-H14": "Finances",
    "UM-H15": "Web Companion",
    "UM-H16": "Backup",
    "UM-H17": "Settings",
    "UM-H18": "Trial",
    "UM-H19": "Tools",
    "UM-H20": "Help",
}


def strip_md(s: str) -> str:
    s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
    s = re.sub(r"`([^`]+)`", r"\1", s)
    return s.strip()


def parse_steps(section: str) -> list[str]:
    m = re.search(r"\*\*What to do:\*\*\s*\n((?:[\s\S]*?)(?=\n\*\*|\n---|\Z))", section)
    if not m:
        return []
    block = m.group(1)
    steps: list[str] = []
    for line in block.splitlines():
        line = line.strip()
        if re.match(r"^\d+\.\s+", line):
            steps.append(strip_md(re.sub(r"^\d+\.\s+", "", line)))
        elif line.startswith("- "):
            steps.append(strip_md(line[2:]))
    return steps


def parse_see(section: str) -> str | None:
    m = re.search(r"\*\*What you'll see:\*\*\s*(.+)", section)
    return strip_md(m.group(1)) if m else None


def parse_title(section: str) -> tuple[str, str]:
    m = re.search(r"^## (UM-H\d+) — (.+)$", section, re.M)
    if not m:
        return "", ""
    return m.group(1), strip_md(m.group(2))


def parse_topics(manual_dir: Path) -> list[dict]:
    topics: list[dict] = []
    files = sorted(
        p for p in manual_dir.glob("*.md") if p.name not in ("README.md", "OUTLINE.md")
    )
    for path in files:
        text = path.read_text(encoding="utf-8")
        for section in re.split(r"(?=^## UM-H\d+)", text, flags=re.M):
            if not section.strip().startswith("## UM-H"):
                continue
            tid, title = parse_title(section)
            if not tid:
                continue
            see = parse_see(section)
            steps = parse_steps(section)
            topics.append({"id": tid, "title": title, "see": see, "steps": steps, "file": path.name})
    topics.sort(key=lambda t: t["id"])
    return topics


def step_to_narration(step: str) -> str:
    """Imperative tap-step voiceover — coffee-maker rule, not component lists."""
    step = strip_md(step)
    if step.startswith("**Android:**") or step.startswith("**iOS:**"):
        return step.replace("**Android:**", "On Android,").replace("**iOS:**", "On iPhone,")
    if step and step[0].islower():
        step = step[0].upper() + step[1:]
    return step


def step_feature_label(step: str, topic_title: str, step_idx: int) -> str:
    """Short slide label from the first tap target in the step."""
    m = re.search(r"(?:Tap|Open|Swipe to|Choose|Pick|Fill|Enter|Scroll to|Wait for)\s+([^—.\n]+)", step, re.I)
    if m:
        label = strip_md(m.group(1)).strip()
        if len(label) > 36:
            label = label[:33] + "…"
        return label
    if step_idx == 0:
        return topic_title[:40]
    return f"{topic_title[:28]} — step {step_idx + 1}"


def build_slides_from_markdown() -> list[dict]:
    """One slide per numbered What-to-do step — no What-you'll-see overview slides."""
    topics = parse_topics(HHH_MANUAL)
    slides: list[dict] = []
    for topic in topics:
        tid = topic["id"]
        chapter = TOPIC_CHAPTER.get(tid, topic["title"].split("—")[0].strip())
        meta_list = STEP_META.get(tid, [])
        for i, step in enumerate(topic["steps"]):
            meta = meta_list[i] if i < len(meta_list) else (
                meta_list[-1] if meta_list else _meta(None, "missing", topic["title"])
            )
            feature = meta.get("alt") or step_feature_label(step, topic["title"], i)
            slide = S(
                chapter,
                feature,
                step_to_narration(step),
                meta.get("img"),
                meta.get("png_status", "missing"),
                meta.get("alt") or feature,
                meta.get("tap"),
            )
            slide["topic"] = tid
            slides.append(slide)
    return slides


SLIDES: list[dict] = build_slides_from_markdown()

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
        return " data-tap-none"
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
         .progress-dots {{ display: flex; justify-content: center; gap: 8px; margin-top: 1rem; flex-wrap: wrap; max-height: 48px; overflow-y: auto; }}
         .dot {{ width: 8px; height: 8px; border-radius: 50%; background: rgba(91,35,51,0.2); cursor: pointer; flex-shrink: 0; }}
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
         .chapter-btn {{ background: var(--navy); border-color: var(--navy); color: var(--white); border: 1px solid var(--navy); }}
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
           <p class="subheader">Detailed user manual — install through every shipped v1 feature in app order. Imperative tap steps, real PNGs where captured, gold pulse guides.</p>
          </div>
         </div>
         <section class="user-manual walkthrough">
          <div class="container">
           <h2>Interactive User Manual</h2>
           <p class="section-sub">{n} slides with synced narration and gold tap guides — generated from users-manual markdown. Use the {len(CHAPTER_PILLS)} chapter pills to jump, or read the scrolling transcript beside the phone. <a href="/docs/handyhorology/HandyHorology_UserGuide.pdf" style="color:var(--navy-medium);font-weight:700;">Download PDF</a></p>
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
                timer = setTimeout(function () {
                  if (playing) goTo(current + 1 > LAST_SLIDE ? 0 : current + 1);
                  if (playing) playSlide();
                }, SLIDE_MS);
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
        "# HHH User Manual — Coverage Inventory",
        "",
        f"**Generated:** build-hhh-user-manual-slides.py  ",
        "**Live URL:** https://josspatech.com/videos/user-guide-hhh/  ",
        "**PDF:** https://josspatech.com/docs/handyhorology/HandyHorology_UserGuide.pdf  ",
        f"**Slide count:** {len(SLIDES)} (indices 0–{len(SLIDES) - 1})  ",
        f"**Chapter pills:** {len(CHAPTER_PILLS)}  ",
        f"**Source:** `{HHH_MANUAL}`  ",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|--------|------:|",
        f"| Slides with voice + narration | {len(SLIDES)} |",
        f"| PNG OK | {ok} |",
        f"| PNG interim (reuse / mockup) | {interim} |",
        f"| PNG missing (placeholder) | {missing} |",
        "",
        "## Slide inventory",
        "",
        "| Slide | Topic | Chapter | Feature | PNG |",
        "|------:|-------|---------|---------|:---:|",
    ]
    for i, s in enumerate(SLIDES):
        png = s["png_status"] if s["img"] else "missing"
        lines.append(f"| {i} | {s.get('topic', '')} | {s['chapter']} | {s['feature']} | {png} |")

    lines += [
        "",
        "## Regenerate",
        "",
        "```powershell",
        "cd josspatech.github.io",
        "python scripts/capture-hhh-manual-screenshots.py",
        "python scripts/build-hhh-user-manual-slides.py",
        "python scripts/build-hhh-user-guide-pdf.py",
        "```",
        "",
    ]
    COVERAGE_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def resolve_png_statuses() -> None:
    manual = ROOT / "assets" / "screenshots" / "hhh" / "manual"
    for slide in SLIDES:
        if not slide["img"]:
            continue
        name = slide["img"].split("/")[-1]
        if (manual / name).exists() and (manual / name).stat().st_size > 10000:
            slide["png_status"] = "OK"


def main():
    resolve_png_statuses()
    global SLIDES, CHAPTER_PILLS
    SLIDES = build_slides_from_markdown()
    CHAPTER_PILLS = []
    seen: set[str] = set()
    for i, slide in enumerate(SLIDES):
        ch = slide["chapter"]
        if ch not in seen:
            seen.add(ch)
            CHAPTER_PILLS.append((ch, i))

    INDEX.parent.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(build_html(), encoding="utf-8")
    NARRATION_JSON.write_text(
        json.dumps([s["narration"] for s in SLIDES], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_deck_js()
    write_coverage()
    print(f"Built {len(SLIDES)} slides, {len(CHAPTER_PILLS)} chapters -> {INDEX}")
    print(f"  OK={sum(1 for s in SLIDES if s['png_status']=='OK')} "
          f"interim={sum(1 for s in SLIDES if s['png_status']=='interim')} "
          f"missing={sum(1 for s in SLIDES if not s['img'])}")


if __name__ == "__main__":
    main()
