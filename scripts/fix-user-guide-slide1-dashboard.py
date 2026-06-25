#!/usr/bin/env python3
"""Fix user-guide slide index 1 (Your Dashboard) to use home dashboard PNG."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASH_SRC = "/assets/screenshots/pbj/01-home-dashboard.png"

# Only the slide immediately after the active welcome slide.
SLIDE1_RE = re.compile(
    r'(<div class="slide active">\s*'
    r'<img src="[^"]+" alt="[^"]*">\s*'
    r'</div>\s*'
    r'<div class="slide">\s*'
    r'<img src=")/assets/screenshots/transactions\.png(" alt=")[^"]*(">\s*'
    r'</div>)',
    re.MULTILINE,
)


def main() -> None:
    for path in sorted((ROOT / "videos").glob("user-guide*/index.html")):
        html = path.read_text(encoding="utf-8")
        new_html, n = SLIDE1_RE.subn(
            rf'\1{DASH_SRC}\2Dashboard\3',
            html,
            count=1,
        )
        if n:
            path.write_text(new_html, encoding="utf-8", newline="\n")
            print(f"{path.parent.name}: fixed slide 1 dashboard PNG")
        else:
            print(f"{path.parent.name}: skip (already fixed or pattern missing)")


if __name__ == "__main__":
    main()
