#!/usr/bin/env python3
"""Fix transcript / LAST_SLIDE / chapters after postlaunch rebuild."""
import json
import re
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "videos" / "user-guide-hhh"
html_path = OUT / "index.html"
narr = json.loads((OUT / "narration-en.json").read_text(encoding="utf-8"))
html = html_path.read_text(encoding="utf-8")
n = len(narr)

# Replace entire transcript-body contents
paras = []
for i, line in enumerate(narr):
    esc = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    cls = "transcript-para current" if i == 0 else "transcript-para"
    paras.append(f' <p class="{cls}" data-slide="{i}">{esc}</p>')
body = "\n".join(paras)

html2, count = re.subn(
    r'(<div class="transcript-body"[^>]*>)[\s\S]*?(</div>)',
    lambda m: m.group(1) + "\n" + body + "\n" + m.group(2),
    html,
    count=1,
)
if count != 1:
    raise SystemExit(f"transcript-body replace failed: {count}")

# LAST_SLIDE
html2 = re.sub(r"const LAST_SLIDE = \d+;", f"const LAST_SLIDE = {n - 1};", html2)

# NARRATION embedded
html2 = re.sub(
    r"const NARRATION = \[[\s\S]*?\];",
    "const NARRATION = " + json.dumps(narr, ensure_ascii=False) + ";",
    html2,
    count=1,
)

# Slide count chrome
html2 = re.sub(r"\d+ slides with synced narration", f"{n} slides with synced narration", html2)
html2 = html2.replace(
    "Detailed user manual — install through every shipped v1 feature in app order.",
    "Detailed user manual — after install through every shipped v1 feature in app order.",
)
html2 = html2.replace(
    "install through every shipped v1 feature",
    "post-install through every shipped v1 feature",
)
html2 = re.sub(
    r"Try HHH free for 14 days on Google Play open testing or request iOS TestFlight from josspatech.com\.",
    "Try HHH free for 15 days on Google Play, or join iOS early access on TestFlight from josspatech.com.",
    html2,
)

# Chapter pills: drop Install, keep Onboarding at 0
chapters = [
    (0, "Onboarding", True),
    (7, "Home", False),
    (11, "My Museum", False),
    (22, "Add Watch", False),
    (26, "Identify", False),
    (40, "Clock Repair", False),
    (47, "Grail Radar", False),
    (56, "Finances", False),
    (63, "Web Companion", False),
    (66, "Backup", False),
    (70, "Settings", False),
    (76, "Trial", False),
    (79, "Tools", False),
    (101, "Help", False),
    (103, "Demand Rolodex", False),
]
ch_html = []
for idx, label, active in chapters:
    cls = "chapter-btn active" if active else "chapter-btn"
    ch_html.append(f'         <button class="{cls}" data-slide="{idx}">{label}</button>')
html2 = re.sub(
    r'(<div class="chapter-nav"[^>]*>)[\s\S]*?(</div>)',
    lambda m: m.group(1) + "\n" + "\n".join(ch_html) + "\n        " + m.group(2),
    html2,
    count=1,
)

html_path.write_text(html2, encoding="utf-8")
print(f"fixed transcript ({n}), LAST_SLIDE={n-1}, chapters={len(chapters)}")
# sanity
assert "Android: Open the Google Play internal" not in html2
assert "four tabs" not in html2
assert "Ludwig" in html2
assert f"LAST_SLIDE = {n - 1}" in html2
print("sanity OK")
