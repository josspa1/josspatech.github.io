#!/usr/bin/env python3
"""Apply User Guide branding to 89-slide index.html."""
from pathlib import Path

p = Path("videos/user-guide/index.html")
text = p.read_text(encoding="utf-8")

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
    (
        "Prefer passive viewing? Play the recorded video below, or scroll down for the interactive manual with chapter pills.",
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
    if old not in text:
        print(f"SKIP (not found): {old[:60]}...")
    else:
        text = text.replace(old, new)
        print(f"OK: {old[:50]}...")

p.write_text(text, encoding="utf-8")
print("Done.")
