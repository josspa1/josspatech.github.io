#!/usr/bin/env python3
"""Export HHH user manual PDF from videos/user-guide-hhh/index.html via Playwright."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "videos" / "user-guide-hhh" / "index.html"
OUT = ROOT / "docs" / "handyhorology" / "HandyHorology_UserGuide.pdf"


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install playwright: pip install playwright && playwright install chromium", file=sys.stderr)
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    file_url = HTML.resolve().as_uri() + "?record=1"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1200, "height": 1600})
        page.goto(file_url, wait_until="networkidle", timeout=120000)
        page.emulate_media(media="print")
        page.pdf(
            path=str(OUT),
            format="Letter",
            print_background=True,
            margin={"top": "0.5in", "bottom": "0.5in", "left": "0.5in", "right": "0.5in"},
        )
        browser.close()

    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
