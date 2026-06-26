#!/usr/bin/env python3
"""Single interactive 89-slide user manual — remove duplicate MP4 embed."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "videos" / "user-guide" / "index-89.html"
OUT = ROOT / "videos" / "user-guide" / "index.html"

html = SRC.read_text(encoding="utf-8")

html = re.sub(
    r"\n \.mp4-player-block \{.*?\n body\.record-mode \.mp4-player-block \{ display: none !important; \}\n",
    "\n",
    html,
    count=1,
    flags=re.DOTALL,
)
html = re.sub(
    r'\n <div class="mp4-player-block".*?</div>\n',
    "\n",
    html,
    count=1,
    flags=re.DOTALL,
)
html = html.replace(
    "89 slides — cold launch through every major feature. 28 chapter pills jump to Home, Activity, Budget, Goals, Coach, Import, Scan, Bills, Debt, Reports, Export, Settings, and more.",
    "89 slides with synced narration and gold tap guides — cold launch through every major feature. Use the 28 chapter pills to jump to Home, Activity, Budget, Goals, Coach, Import, Scan, Bills, Debt, Reports, Export, Settings, and more.",
)

OUT.write_text(html, encoding="utf-8", newline="\n")

text = OUT.read_text(encoding="utf-8")
assert "mp4-player" not in text
assert text.count('id="slideshow"') == 1
assert text.count('id="chapterNav"') == 1
assert text.count('class="video-wrapper"') == 1
slides = text.count('class="slide"') + text.count('class="slide active"')
print(f"Wrote {OUT.name}: {slides} slides, one walkthrough block, no MP4 embed")
