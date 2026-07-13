#!/usr/bin/env python3
"""DEPRECATED (Jul 2026 terminology): do not run.

Canonical product term is User Manual (not User Guide). Walkthrough =
partner-showcase overview only. This one-shot script would reverse live
branding back to "User Guide". Kept for history only.
"""
import sys
print("DEPRECATED: refuse to run — would reverse User Manual branding.", file=sys.stderr)
raise SystemExit(2)

# --- original script below (unreachable) ---
#!/usr/bin/env python3
"""Restore 89-slide user guide, apply branding, verify MP3s."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "videos" / "user-guide" / "index.html"
AUDIO = ROOT / "videos" / "user-guide" / "audio"

# 1. Restore HTML from 4b289c9
content = subprocess.check_output(
    ["git", "show", "4b289c9:videos/user-guide/index.html"],
    text=True,
    encoding="utf-8",
    cwd=ROOT,
)

replacements = [
    ("PocketBudJet User Manual | JosspaTech", "PocketBudJet User Guide | JosspaTech"),
    ('<span class="current">User Manual</span>', '<span class="current">User Guide</span>'),
    (
        "<h1>PocketBudJet User Manual</h1>\n"
        " <p class=\"subheader\">Master walkthrough — cold launch through every major feature in app order. "
        "Imperative tap steps, real PNGs where captured, gold pulse guides. All other how-to videos are slices of this manual.</p>",
        "<h1>PocketBudJet User Guide</h1>\n"
        " <p class=\"subheader\">Detailed user guide — 89 slides from cold launch through every major feature. "
        "Real app screenshots, gold tap pointers, and synced narration across 28 chapters.</p>",
    ),
    ("<h2>Master Manual</h2>", "<h2>Interactive User Guide</h2>"),
    (
        "Prefer passive viewing? Play the recorded walkthrough below, or scroll down for the interactive manual with chapter pills.",
        "Prefer passive viewing? Play the recorded user guide below, or scroll down for the interactive guide with chapter pills.",
    ),
    ('aria-label="Pause walkthrough"', 'aria-label="Pause user guide"'),
    (
        "Download PocketBudJet and follow this manual from slide one — cold launch through every major screen.",
        "Download PocketBudJet and follow this user guide from slide one — cold launch through every major screen.",
    ),
    (
        "This manual at josspatech.com/videos/user-guide/ covers every feature.",
        "This user guide at josspatech.com/videos/user-guide/ covers every feature.",
    ),
]
for old, new in replacements:
    if old not in content:
        print(f"WARN missing: {old[:50]}", file=sys.stderr)
    else:
        content = content.replace(old, new)

INDEX.write_text(content, encoding="utf-8")

# 2. Restore MP3s from ebb02de for slides 28-88 + any missing
for i in range(89):
    out = AUDIO / f"slide-{i}.mp3"
    if out.exists() and out.stat().st_size > 10000:
        continue
    blob = subprocess.check_output(
        ["git", "show", f"ebb02de:videos/user-guide/audio/slide-{i}.mp3"],
        cwd=ROOT,
    )
    out.write_bytes(blob)
    print(f"restored slide-{i}.mp3 ({len(blob)} bytes)")

# 3. Verify
h = INDEX.read_text(encoding="utf-8")
narr = re.search(r"const NARRATION = \[(.*?)\];", h, re.S)
items = re.findall(r'"((?:[^"\\]|\\.)*)"', narr.group(1)) if narr else []
indices = re.findall(r'data-index="(\d+)"', h)
mp3s = sorted(AUDIO.glob("slide-*.mp3"))
bad = [p.name for p in mp3s if p.stat().st_size < 10000]
print(f"VERIFY: narr={len(items)} slides={len(indices)} mp3s={len(mp3s)} bad={bad}")
if len(items) != 89 or len(indices) != 89 or len(mp3s) != 89:
    sys.exit(1)
