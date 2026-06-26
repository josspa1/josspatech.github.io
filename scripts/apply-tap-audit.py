#!/usr/bin/env python3
"""Apply user-guide tap pointer audit: tap-none for misleading pointers, fix coords/PNGs."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "videos" / "user-guide" / "index.html"
BANK = "/assets/screenshots/connect-bank/bank-sync.png"
STEP9 = "/assets/screenshots/import/step-9-settings-export.png"

HOME = "/assets/screenshots/import/step-10-home-dashboard.png"

# index -> (action, ...)
# action: 'none' | ('coords', x, y, label) | ('png', src) | ('both', src, x, y, label)
FIXES: dict[int, tuple] = {
    # Home slides — real captures, not stale marketing mockup
    26: ("png", HOME),
    # Wayfinding 10-14 wired manually in index.html (distinct PNGs + RECORD_NOW gaps)
    # Terms disclaimer tab
    6: ("coords", 75, 35, "Disclaimer"),
    # Home / Activity / Budget tab taps on real app chrome
    27: ("both", BANK, 12, 94, "Activity"),
    30: ("both", BANK, 38, 94, "Budget"),
    34: ("coords", 80, 96, "Goals"),
    38: ("coords", 90, 96, "Coach"),
    # transactions.png is Settings — disable misleading taps
    29: ("none",),
    42: ("none",),
    74: ("none",),
    75: ("none",),
    76: ("none",),
    # Manual entry on scan screen
    43: ("coords", 50, 72, "Amount"),
    44: ("coords", 82, 72, "Category"),
    45: ("none",),
    46: ("none",),
    # Import chapter
    48: ("coords", 50, 32, "Share"),
    49: ("none",),
    # receipt-scan.png / scanner.png are splash screens
    54: ("none",),
    55: ("none",),
    56: ("none",),
    # bills-calendar.png is Settings screen
    58: ("none",),
    59: ("none",),
    # step-9 is import home, not export settings
    66: ("none",),
    67: ("none",),
    # privacy.png is Settings YOUR SETUP list
    69: ("none",),
    70: ("none",),
    86: ("none",),
    87: ("none",),
    # Settings gear / search on screens that show them
    68: ("both", STEP9, 91, 8, "Settings"),
    84: ("both", BANK, 50, 12, "Search"),
    85: ("none",),
    78: ("none",),
    # Connect bank row on home/import screen
    72: ("coords", 50, 68, "Connect Bank"),
    73: ("none",),
    # Reports segment tabs
    62: ("coords", 35, 23, "Reports"),
    63: ("coords", 50, 55, "Trends"),
    64: ("coords", 50, 72, "Categories"),
    # Marketing mockups / wrong PNGs — no reliable tap target
    15: ("none",),
    47: ("none",),
    50: ("none",),
    52: ("none",),
    53: ("none",),
    77: ("none",),
    79: ("none",),
    80: ("none",),
    81: ("none",),
    83: ("none",),
}


def patch_slide(block: str, idx: int, fix: tuple) -> str:
    action = fix[0]
    open_tag = re.search(
        rf'(<div class="slide" data-index="{idx}")([^>]*)(>)',
        block,
    )
    if not open_tag:
        raise SystemExit(f"slide {idx} not found")

    if action == "none":
        new_attrs = " data-tap-none"
    elif action == "coords":
        _, x, y, label = fix
        new_attrs = f' data-tap-x="{x}" data-tap-y="{y}" data-tap-label="{label}"'
    elif action == "png":
        _, src = fix
        block = re.sub(r'(<img src=")[^"]+(")', rf"\1{src}\2", block, count=1)
        new_attrs = open_tag.group(2)
        if "data-tap-none" in new_attrs:
            new_attrs = re.sub(r'\s*data-tap-none', "", new_attrs)
    elif action == "both":
        _, src, x, y, label = fix
        block = re.sub(r'(<img src=")[^"]+(")', rf"\1{src}\2", block, count=1)
        new_attrs = f' data-tap-x="{x}" data-tap-y="{y}" data-tap-label="{label}"'
    else:
        raise SystemExit(f"unknown action {action}")

    # Strip existing tap attrs from opening tag
    attrs = open_tag.group(2)
    attrs = re.sub(r'\s*data-tap-none', "", attrs)
    attrs = re.sub(r'\s*data-tap-x="[^"]*"', "", attrs)
    attrs = re.sub(r'\s*data-tap-y="[^"]*"', "", attrs)
    attrs = re.sub(r'\s*data-tap-label="[^"]*"', "", attrs)

    new_open = open_tag.group(1) + attrs + new_attrs + open_tag.group(3)
    return block[: open_tag.start()] + new_open + block[open_tag.end() :]


def main() -> None:
    html = HTML.read_text(encoding="utf-8")
    chunk_start = html.index('<div class="slideshow"')
    chunk_end = html.index('<div class="progress-dots"')
    chunk = html[chunk_start:chunk_end]

    slide_re = re.compile(
        r'(<div class="slide" data-index="(\d+)"[^>]*>[\s\S]*?)(?=\n <div class="slide"|\n </div>\n </div>\n </div>\n <div class="progress-dots")'
    )
    blocks = {int(m.group(2)): m.group(1) for m in slide_re.finditer(chunk)}

    tap_none_before = len(re.findall(r"data-tap-none", html))
    tap_active_before = len(re.findall(r'data-tap-x="', html))

    for idx, fix in sorted(FIXES.items()):
        if idx not in blocks:
            raise SystemExit(f"missing slide block {idx}")
        old = blocks[idx]
        new = patch_slide(old, idx, fix)
        chunk = chunk.replace(old, new, 1)
        blocks[idx] = new

    html = html[:chunk_start] + chunk + html[chunk_end:]

    tap_none_after = len(re.findall(r"data-tap-none", html))
    tap_active_after = len(re.findall(r'data-tap-x="', html))

  # Count fix types
    none_added = sum(1 for f in FIXES.values() if f[0] == "none")
    coords_fixed = sum(1 for f in FIXES.values() if f[0] == "coords")
    png_fixed = sum(1 for f in FIXES.values() if f[0] in ("png", "both"))
    both = sum(1 for f in FIXES.values() if f[0] == "both")

    HTML.write_text(html, encoding="utf-8")
    print(f"tap-none: {tap_none_before} -> {tap_none_after} (+{tap_none_after - tap_none_before})")
    print(f"tap-x slides: {tap_active_before} -> {tap_active_after}")
    print(f"slides patched: {len(FIXES)} (tap-none={none_added}, coords={coords_fixed}, png/both={png_fixed}, both={both})")


if __name__ == "__main__":
    main()
