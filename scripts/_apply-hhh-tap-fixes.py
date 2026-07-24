#!/usr/bin/env python3
"""Apply measured tap-target fixes to HHH EN user guide index.html."""
from __future__ import annotations

import re
from pathlib import Path

HTML = Path(__file__).resolve().parents[1] / "videos" / "user-guide-hhh" / "index.html"

# Measured on 1440x3120 keepers (app tab bar ~y92; system nav is ~y98).
# None = data-tap-none (tool not visible on the slide screenshot).
FIXES: dict[int, tuple[int, int, str] | None] = {
    6: (82, 16, "Clear samples"),
    8: (14, 43, "Hunt"),
    9: (50, 58, "Path card"),
    10: (10, 92, "Home"),
    11: (30, 92, "My Museum"),
    12: (20, 44, "Owned"),
    14: (50, 56, "Search"),
    15: (50, 68, "Piece row"),
    19: (50, 44, "Wish"),
    20: (80, 44, "For Sale"),
    21: (88, 60, "More"),
    22: (50, 83, "Add"),
    25: None,  # Save CTA not on identify-camera screenshot
    26: (20, 83, "Identify"),
    27: (27, 50, "Photo 1: Dial"),
    28: (73, 50, "Choose Photo"),
    32: None,  # Identify CTA not on results screenshot (y=95 was tab label)
    37: (50, 82, "Save"),
    40: (50, 18, "Symptom"),
    47: (50, 44, "Wish"),
    48: (50, 52, "Add wishes"),
    51: (16, 54, "Check now"),
    70: (90, 92, "Settings"),
    79: (50, 92, "Tools"),
    # Tools hub is 2-col; first viewport: Worth/Compare, Condition/eBay, Parts/Movement, Estate/Dealer.
    80: (25, 30, "Worth"),
    81: (32, 55, "Compare"),
    82: (25, 48, "Condition"),
    83: (50, 40, "Value trend"),
    84: None,  # Trade not on hub screenshot
    85: (88, 82, "Ask Expert"),
    86: (50, 48, "Photo Coach"),
    87: (50, 32, "ID Card"),
    88: None,  # Barcode not on hub screenshot
    89: None,  # Scan Papers not on hub screenshot
    90: None,  # Complexity not on hub screenshot
    91: None,  # Accuracy not on hub screenshot
    92: None,  # Rotation not on hub screenshot
    93: None,  # Warranty not on hub screenshot
    94: (50, 40, "Exact Time"),
    95: (50, 40, "Moon Phase"),
    96: (50, 45, "Print"),
    97: (50, 42, "Share Nearby"),
    98: (50, 40, "Offline pack"),
    99: (50, 40, "Big Screen"),
    100: (50, 50, "Movement to Parts"),
    103: (50, 18, "Send"),
    104: (50, 25, "Name"),
    105: (87, 56, "Share all"),
    106: (50, 67, "Send nearby"),
    107: (50, 48, "Scan nearby"),
    108: (72, 74, "Accept card"),
    109: (88, 32, "Board group"),
    110: (50, 55, "Rating"),
}

# Also keep early onboarding taps accurate when re-applying
FIXES.update({
    0: (50, 90, "Continue"),
    1: (50, 90, "Get Started"),
    4: (50, 72, "Get Started"),
})


def main() -> None:
    html = HTML.read_text(encoding="utf-8")
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
        show_at = show.group(1) if show else "0.2"
        duration = dur.group(1) if dur else "3.0"
        # Keep class + data-index only (and data-tap-none removal)
        class_m = re.search(r'class="([^"]*)"', full)
        cls = class_m.group(1) if class_m else "slide"
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

    html2 = re.sub(
        r'<div class="slide[^"]*"[^>]*data-index="(\d+)"[^>]*>',
        repl,
        html,
    )
    HTML.write_text(html2, encoding="utf-8", newline="\n")
    print(f"done changed={changed}")


if __name__ == "__main__":
    main()
