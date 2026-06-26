#!/usr/bin/env python3
"""Update how-to/index.html User Guide section for 89-slide product."""
from pathlib import Path

p = Path("how-to/index.html")
text = p.read_text(encoding="utf-8")

replacements = [
    (
        'content="PocketBudJet help center. Quick start guide, video walkthroughs, import help, and the complete user guide — find exactly what you need."',
        'content="PocketBudJet help center. Quick start guides, import help, and the full detailed user guide — 89 slides, 28 chapters with synced narration."',
    ),
    (
        "Quick start guides, step-by-step walkthroughs, and the full user manual. Pick exactly what you need.",
        "Quick start guides, import help, and the full detailed user guide. Pick exactly what you need.",
    ),
    (
        "Every screen, every feature, every setting — 28 chapters covering everything PocketBudJet can do.",
        "Every screen, every feature, every setting — 89 slides across 28 chapters, cold start through every feature.",
    ),
    (
        "<h3>Watch the Full User Guide Video</h3>\n                    <p>A visual walkthrough of every screen, feature, and setting across 28 chapters. ~18 min.</p>",
        "<h3>Open the Full Detailed User Guide</h3>\n                    <p>Interactive user guide with synced narration, gold tap pointers, and 28 chapter pills — every screen, feature, and setting. ~12 min.</p>",
    ),
]
for old, new in replacements:
    if old not in text:
        print(f"WARN: not found: {old[:60]}...")
    else:
        text = text.replace(old, new)
        print(f"OK: {old[:50]}...")

p.write_text(text, encoding="utf-8")
print("Done.")
