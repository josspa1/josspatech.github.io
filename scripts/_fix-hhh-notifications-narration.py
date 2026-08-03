#!/usr/bin/env python3
"""Apply Notifications narration fix to shot-map + sync HTML from narration-en.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "user-guide-hhh"
texts = json.loads((OUT / "narration-en.json").read_text(encoding="utf-8"))

slides = json.loads((OUT / "_shot-map.json").read_text(encoding="utf-8"))
for s in slides:
    if s["i"] == 75:
        s["n"] = texts[75]
        s["alt"] = "eBay Grail Radar match notification"
(OUT / "_shot-map.json").write_text(
    json.dumps(slides, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)

# Sync NARRATION via existing helper
import subprocess
import sys

subprocess.check_call([sys.executable, str(ROOT / "scripts" / "_sync-hhh-guide-html-from-narration.py")])

html = (OUT / "index.html").read_text(encoding="utf-8")
html2 = html.replace(
    'data-index="75" data-tap-x="50" data-tap-y="65" data-tap-label="Notifications"',
    'data-index="75" data-tap-x="50" data-tap-y="40" data-tap-label="Notification"',
)
(OUT / "index.html").write_text(html2, encoding="utf-8")
print("slide 75:", texts[75][:90], "...")
