#!/usr/bin/env python3
"""Fix Clear samples / quick-command multi-taps / 5-tab narration on HHH guide."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "user-guide-hhh"
HTML = OUT / "index.html"
NARR = OUT / "narration-en.json"
BUST = "taps-home-fix-2026-07-24"

narr = json.loads(NARR.read_text(encoding="utf-8"))
html = HTML.read_text(encoding="utf-8")

narr_js = json.dumps(narr, ensure_ascii=False)
html2, n = re.subn(
    r"const NARRATION = \[.*?\];",
    "const NARRATION = " + narr_js + ";",
    html,
    count=1,
    flags=re.S,
)
if n != 1:
    raise SystemExit(f"NARRATION replace failed ({n})")

html2 = html2.replace(
    'data-index="6" data-tap-x="82" data-tap-y="16" data-tap-label="Clear samples" data-tap-show-at="0.2" data-tap-duration="2.1"',
    'data-index="6" data-tap-x="77" data-tap-y="17" data-tap-label="Clear samples" data-tap-show-at="0.2" data-tap-duration="2.8"',
)

old8 = (
    ' <div class="slide" data-index="8" data-tap-x="14" data-tap-y="43" '
    'data-tap-label="Hunt" data-tap-show-at="0.2" data-tap-duration="3.2">\n'
    ' <img src="/assets/screenshots/hhh/manual/01-home-command-center.png?v=taps-full-audit-2026-07-24" '
    'alt="Quick commands row" loading="lazy">\n'
    " </div>"
)
new8 = (
    ' <div class="slide" data-index="8" data-taps=\''
    '[{"x":15,"y":44,"at":0.2,"dur":2.2,"label":"Hunt"},'
    '{"x":37,"y":44,"at":2.6,"dur":2.2,"label":"Fix clock"},'
    '{"x":61,"y":44,"at":5.0,"dur":2.2,"label":"Add Watch"},'
    '{"x":84,"y":44,"at":7.4,"dur":2.6,"label":"Tools"}]\'>\n'
    f' <img src="/assets/screenshots/hhh/manual/01-home-command-center.png?v={BUST}" '
    'alt="Quick commands row" loading="lazy">\n'
    " </div>"
)
if old8 not in html2:
    raise SystemExit("slide 8 block not found")
html2 = html2.replace(old8, new8)

old10 = (
    ' <div class="slide" data-index="10" data-tap-x="10" data-tap-y="92" '
    'data-tap-label="Home" data-tap-show-at="6.1" data-tap-duration="1.4">\n'
    ' <img src="/assets/screenshots/hhh/manual/01-home-command-center.png?v=taps-full-audit-2026-07-24" '
    'alt="Bottom tab bar" loading="lazy">\n'
    " </div>"
)
new10 = (
    ' <div class="slide" data-index="10" data-taps=\''
    '[{"x":10,"y":92,"at":1.6,"dur":1.3,"label":"Home"},'
    '{"x":30,"y":92,"at":3.1,"dur":1.3,"label":"My Museum"},'
    '{"x":50,"y":92,"at":4.6,"dur":1.3,"label":"Tools"},'
    '{"x":70,"y":92,"at":6.1,"dur":1.3,"label":"Collectors"},'
    '{"x":90,"y":92,"at":7.6,"dur":1.6,"label":"Settings"}]\'>\n'
    f' <img src="/assets/screenshots/hhh/manual/01-home-command-center.png?v={BUST}" '
    'alt="Bottom tab bar" loading="lazy">\n'
    " </div>"
)
if old10 not in html2:
    raise SystemExit("slide 10 block not found")
html2 = html2.replace(old10, new10)

html2 = html2.replace("taps-full-audit-2026-07-24", BUST)
html2 = html2.replace(
    '/videos/shared/walkthrough.js"',
    f'/videos/shared/walkthrough.js?v={BUST}"',
)

HTML.write_text(html2, encoding="utf-8")
print("updated", HTML)
print("clear samples 77,17:", 'data-tap-x="77"' in html2)
print("data-taps slides:", html2.count("data-taps="))
print("five tabs narrated:", "five tabs" in html2)
print("Fix clock narrated:", "Fix clock opens" in html2)
