#!/usr/bin/env python3
"""Apply full post-audit tap fixes to HHH user guide."""
from __future__ import annotations

import re
from pathlib import Path

HTML = Path(__file__).resolve().parents[1] / "videos" / "user-guide-hhh" / "index.html"
BUST = "taps-full-audit-2026-07-24"

# idx -> (x, y, label) or None for data-tap-none
FIXES: dict[int, tuple[int, int, str] | None] = {
    # Keep known-good early slides
    0: (50, 90, "Continue"),
    1: (50, 90, "Get Started"),
    2: (50, 74, "Sample collection"),
    3: (50, 61, "Own piece"),
    4: (50, 72, "Get Started"),
    6: (82, 16, "Clear samples"),
    8: (14, 43, "Hunt"),
    9: None,  # path cards not on stocked home screenshot
    10: (10, 92, "Home"),
    11: (30, 92, "My Museum"),
    12: (20, 44, "Owned"),
    14: (50, 56, "Search"),
    15: (50, 68, "Piece row"),
    16: (50, 32, "Photos"),
    17: (92, 8, "More"),  # overflow → Passport/Provenance
    18: None,  # Service log not visible on piece detail keeper
    19: (50, 44, "Wish"),
    20: (80, 44, "For Sale"),
    21: (88, 60, "More"),
    22: (50, 83, "Add"),
    23: None,  # Manual entry not on Identify camera shot
    24: (25, 84, "Brand"),
    26: (20, 83, "Identify"),
    27: (27, 50, "Photo 1: Dial"),
    28: (73, 50, "Choose Photo"),
    29: None,  # Skip appears after capture — not on this shot
    30: (25, 84, "Brand guess"),
    31: None,  # Item-type chips not on this shot
    33: (50, 40, "Top match"),
    34: (50, 35, "This is correct"),
    35: (50, 62, "Detail photos"),
    36: (50, 72, "What I know"),
    37: (50, 82, "Save"),
    38: (25, 68, "Find parts"),
    40: (50, 18, "Symptom"),
    41: (25, 68, "Find Clock Parts"),
    42: (50, 12, "Symptom"),
    45: None,  # Shop control not on parts list keeper
    47: (50, 44, "Wish"),
    48: (50, 52, "Add wishes"),
    49: (50, 28, "Wish row"),  # grail hero card on radar shot
    50: (82, 36, "Edit rules"),
    51: (16, 54, "Check now"),
    52: None,  # no listing row when feed empty
    53: (50, 9, "Notification"),
    54: (50, 32, "eBay Listings"),
    56: (28, 15, "Finances"),
    58: (40, 59, "Purchase price"),
    59: None,  # Add service entry not on piece detail keeper
    60: None,  # Insurance not on museum filter shot
    61: (72, 15, "Budget"),
    63: (50, 48, "Web Companion"),
    64: (50, 72, "Pairing code"),
    66: (50, 57, "Backup"),
    67: (50, 57, "Save a Copy"),
    68: (50, 70, "Bring a Copy Back"),
    69: (50, 55, "Device Sync"),
    70: (90, 92, "Settings"),
    71: (50, 47, "Theme"),
    72: (50, 42, "Language"),
    73: (88, 18, "App lock"),
    75: (50, 9, "Notification"),
    77: (50, 73, "Subscribe"),
    78: None,  # Manage not on trial/paywall keeper
    79: (50, 92, "Tools"),
    80: (25, 30, "Worth"),
    81: (32, 55, "Compare"),
    82: (25, 48, "Condition"),
    83: (50, 40, "Value trend"),
    85: (45, 82, "Ask Expert"),
    86: (50, 48, "Photo Coach"),
    87: (50, 32, "ID Card"),
    94: (50, 40, "Exact Time"),
    95: (50, 40, "Moon Phase"),
    96: (50, 80, "Print"),  # Columns chips (print CTA off-screen on this crop)
    97: (25, 28, "Share Nearby"),
    98: (85, 80, "Offline pack"),
    99: (50, 25, "Big Screen"),
    100: (50, 48, "Movement to Parts"),
    103: (50, 18, "Send"),
    104: (50, 25, "Name"),
    105: (87, 56, "Share all"),
    106: (50, 67, "Send nearby"),
    107: (50, 48, "Scan nearby"),
    108: (72, 74, "Accept card"),
    109: (88, 32, "Board group"),
    110: None,  # rating UI only after expand — not on board list
}

# Optional image swaps so the tap target exists on-screen
IMG: dict[int, str] = {
    38: f"/assets/screenshots/hhh/manual/08-tools-hub.png?v={BUST}",
}


def main() -> None:
    html = HTML.read_text(encoding="utf-8")
    html = re.sub(r"\?v=[^\"]+", f"?v={BUST}", html)
    changed = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal changed
        full = m.group(0)
        idx = int(m.group(1))
        if idx not in FIXES:
            return full
        fix = FIXES[idx]
        show = re.search(r'data-tap-show-at="([^"]+)"', full)
        dur = re.search(r'data-tap-duration="([^"]+)"', full)
        class_m = re.search(r'class="([^"]*)"', full)
        cls = class_m.group(1) if class_m else "slide"
        show_at = show.group(1) if show else "0.2"
        duration = dur.group(1) if dur else "3.0"
        if fix is None:
            new = f'<div class="{cls}" data-index="{idx}" data-tap-none>'
        else:
            x, y, label = fix
            new = (
                f'<div class="{cls}" data-index="{idx}" '
                f'data-tap-x="{x}" data-tap-y="{y}" data-tap-label="{label}" '
                f'data-tap-show-at="{show_at}" data-tap-duration="{duration}">'
            )
        if new != full:
            changed += 1
            print(f"  slide {idx} updated")
        return new

    html = re.sub(
        r'<div class="slide[^"]*"[^>]*data-index="(\d+)"[^>]*>',
        repl,
        html,
    )

    for idx, src in IMG.items():
        pat = rf'(data-index="{idx}"[^>]*>\s*<img[^>]+src=")[^"]+(")'
        html, n = re.subn(pat, rf"\g<1>{src}\g<2>", html, count=1)
        print(f"  slide {idx} image swap n={n}")

    HTML.write_text(html, encoding="utf-8", newline="\n")
    print(f"done changed={changed} bust={BUST}")


if __name__ == "__main__":
    main()
