#!/usr/bin/env python3
"""PBJ how-to pass: sync narration, wire better screens, rebuild shot-map."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "pbj" / "user-guide"
META = Path(r"C:\Users\jossp\Documents\MobileApps\PBJ\Meta\adgraphics")
ASSETS = ROOT / "assets" / "screenshots" / "pbj"

shutil.copy2(META / "pbj-real-budget-subs.png", ASSETS / "16-budget-envelopes.png")
shutil.copy2(META / "pbj-real-coach-august.png", ASSETS / "17-coach-today.png")

html_path = OUT / "index.html"
html = html_path.read_text(encoding="utf-8")
narr = json.loads((OUT / "narration-en.json").read_text(encoding="utf-8"))
if len(narr) != 120:
    raise SystemExit(f"expected 120 narration lines, got {len(narr)}")

replacements = [
    (
        'data-index="28" data-tap-x="12" data-tap-y="94" data-tap-label="Activity"',
        'data-index="28" data-tap-x="50" data-tap-y="58" data-tap-label="Add my first transaction"',
    ),
    (
        '<div class="slide" data-index="33" data-tap-x="38" data-tap-y="94" data-tap-label="Budget" data-tap-show-at="0.2" data-tap-duration="2.7">\n <img src="/assets/screenshots/pbj/01-home-dashboard.png" alt="01 Home Dashboard"',
        '<div class="slide" data-index="33" data-tap-x="50" data-tap-y="94" data-tap-label="Budget" data-tap-show-at="0.2" data-tap-duration="2.7">\n <img src="/assets/screenshots/pbj/import/14-home-hero.png" alt="Tap Budget"',
    ),
    (
        '<img src="/assets/screenshots/pbj/03-budget-envelopes.png" alt="03 Budget Envelopes"',
        '<img src="/assets/screenshots/pbj/16-budget-envelopes.png" alt="Budget envelopes"',
    ),
    (
        '<div class="slide" data-index="39" data-tap-x="62" data-tap-y="94" data-tap-label="Goals" data-tap-show-at="0.2" data-tap-duration="2.8">\n <img src="/assets/screenshots/pbj/01-home-dashboard.png" alt="01 Home Dashboard"',
        '<div class="slide" data-index="39" data-tap-x="70" data-tap-y="94" data-tap-label="Goals" data-tap-show-at="0.2" data-tap-duration="2.8">\n <img src="/assets/screenshots/pbj/import/14-home-hero.png" alt="Tap Goals"',
    ),
    (
        '<div class="slide" data-index="40" data-tap-none>\n <img src="/assets/screenshots/pbj/06-goals-languages.png" alt="06 Goals Languages"',
        '<div class="slide" data-index="40" data-tap-x="82" data-tap-y="42" data-tap-label="Add one" data-tap-show-at="0.4" data-tap-duration="2.8">\n <img src="/assets/screenshots/pbj/06-goals-languages.png" alt="Goals empty"',
    ),
    (
        '<div class="slide" data-index="44" data-tap-x="88" data-tap-y="94" data-tap-label="Coach" data-tap-show-at="0.2" data-tap-duration="3">\n <img src="/assets/screenshots/pbj/01-home-dashboard.png" alt="01 Home Dashboard"',
        '<div class="slide" data-index="44" data-tap-x="90" data-tap-y="94" data-tap-label="Coach" data-tap-show-at="0.2" data-tap-duration="3">\n <img src="/assets/screenshots/pbj/import/14-home-hero.png" alt="Tap Coach"',
    ),
    (
        '<img src="/assets/screenshots/pbj/05-ai-coach.png" alt="05 AI Coach"',
        '<img src="/assets/screenshots/pbj/17-coach-today.png" alt="Coach Today"',
    ),
    (
        '<div class="slide" data-index="46" data-tap-x="85" data-tap-y="24" data-tap-label="Ask"',
        '<div class="slide" data-index="46" data-tap-x="28" data-tap-y="54" data-tap-label="Ask PBJ"',
    ),
    (
        '<div class="slide" data-index="48" data-tap-x="50" data-tap-y="88" data-tap-label="Gold +" data-tap-show-at="1.4" data-tap-duration="2.2">\n <img src="/assets/screenshots/pbj/01-home-dashboard.png" alt="01 Home Dashboard"',
        '<div class="slide" data-index="48" data-tap-x="88" data-tap-y="88" data-tap-label="Gold +" data-tap-show-at="1.4" data-tap-duration="2.2">\n <img src="/assets/screenshots/pbj/import/14-home-hero.png" alt="Home plus"',
    ),
]
for old, new in replacements:
    if old not in html:
        raise SystemExit(f"missing HTML chunk:\n{old[:160]}")
    html = html.replace(old, new)

new_arr = json.dumps(narr, ensure_ascii=False)
html2, n = re.subn(r"const NARRATION = \[.*?\];", "const NARRATION = " + new_arr + ";", html, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f"NARRATION replace count={n}")
html_path.write_text(html2, encoding="utf-8")

rows = []
for m in re.finditer(r'<div class="slide(?:\s+active)?"([^>]*)>', html2):
    attrs = m.group(1)
    idx = int(re.search(r'data-index="(\d+)"', attrs).group(1))
    chunk = html2[m.start() : m.start() + 1400]
    src_m = re.search(r'<img[^>]+src="([^"]+)', chunk)
    alt_m = re.search(r'alt="([^"]*)"', chunk)
    src = src_m.group(1).split("?")[0] if src_m else None
    rows.append(
        {
            "i": idx,
            "n": narr[idx] if idx < len(narr) else "",
            "src": src,
            "alt": alt_m.group(1) if alt_m else "",
            "exists": bool(src and (ROOT / src.lstrip("/")).exists()),
        }
    )
rows.sort(key=lambda r: r["i"])
(OUT / "_shot-map.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("slides", len(rows), "missing", sum(1 for r in rows if not r["exists"]))
for i in (9, 27, 28, 33, 34, 39, 40, 44, 45, 46, 54, 56, 60):
    r = rows[i]
    print(f"{i:3} {Path(r['src']).name:28} {r['n'][:72]}")
