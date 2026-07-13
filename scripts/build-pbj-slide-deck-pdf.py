#!/usr/bin/env python3
"""Export PocketBudJet slide-deck PDF — one page per interactive user-manual slide.

IMPORTANT: Do NOT write to docs/pocketbudjet/PocketBudJet_UserManual.pdf
(or the legacy alias PocketBudJet_UserGuide.pdf). Those paths are the written
User Manual (16-page prose PDF). Overwriting them with slide screenshots
(commit 5309a1c, Jul 2026) broke the public download.

This script writes a separate slide-deck artifact only.
URL path videos/user-guide/ is a legacy folder name; product term is User Manual.
"""
from __future__ import annotations

import json
import sys
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Legacy path: videos/user-guide/ — displayed title is User Manual
HTML = ROOT / "videos" / "user-guide" / "index.html"
NARRATION = ROOT / "videos" / "user-guide" / "narration-en.json"
# Slide-deck print of the interactive user manual — NOT the written User Manual PDF.
OUT = ROOT / "docs" / "pocketbudjet" / "PocketBudJet_SlideDeck.pdf"
FORBIDDEN = [
    ROOT / "docs" / "pocketbudjet" / "PocketBudJet_UserManual.pdf",
    ROOT / "docs" / "pocketbudjet" / "PocketBudJet_UserGuide.pdf",  # legacy alias
]


def export_via_playwright(narrations: list[str]) -> int:
    from playwright.sync_api import sync_playwright

    if OUT.resolve() in {p.resolve() for p in FORBIDDEN}:
        print(f"Refusing to overwrite written user manual: {OUT}", file=sys.stderr)
        return 2

    OUT.parent.mkdir(parents=True, exist_ok=True)
    file_url = HTML.resolve().as_uri() + "?record=1"
    n = len(narrations)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": 900, "height": 1100}, device_scale_factor=2)
        page = ctx.new_page()
        page.goto(file_url, wait_until="networkidle", timeout=180000)
        page.wait_for_selector(".slide.active", timeout=60000)

        pdf_pages: list[bytes] = []
        for i in range(n):
            page.evaluate(
                """(idx) => {
                  document.querySelectorAll('.slide').forEach((s, j) => s.classList.toggle('active', j === idx));
                  const p = document.querySelector('.transcript-para[data-slide="' + idx + '"]');
                  document.querySelectorAll('.transcript-para').forEach(el => el.classList.remove('current'));
                  if (p) { p.classList.add('current'); p.scrollIntoView({ block: 'nearest' }); }
                }""",
                i,
            )
            page.wait_for_timeout(150)

            shot = page.locator(".walkthrough-stage").screenshot(type="png")
            narr = narrations[i].replace("&", "&amp;").replace("<", "&lt;")
            wrap = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
            <style>
             @page {{ margin: 0.4in; }}
             body {{ font-family: Segoe UI, sans-serif; color: #1A4F7A; margin: 0; text-align: center; }}
             .hdr {{ display:flex; justify-content:space-between; font-size:11px; color:#5A7A9A; margin-bottom:8px; }}
             img {{ max-width: 100%; height: auto; max-height: 7.5in; }}
             p {{ font-size: 13px; line-height: 1.45; margin-top: 12px; max-width: 7in; margin-left:auto; margin-right:auto; }}
            </style></head><body>
            <div class="hdr"><span>PocketBudJet Slide Deck</span><span>Slide {i + 1} / {n}</span></div>
            <img src="data:image/png;base64,{__import__('base64').b64encode(shot).decode()}" alt="">
            <p>{narr}</p></body></html>"""

            sub = ctx.new_page()
            sub.set_content(wrap, wait_until="load")
            pdf_pages.append(
                sub.pdf(
                    format="Letter",
                    print_background=True,
                    margin={"top": "0.35in", "bottom": "0.35in", "left": "0.5in", "right": "0.5in"},
                )
            )
            sub.close()

        if len(pdf_pages) == 1:
            OUT.write_bytes(pdf_pages[0])
        else:
            try:
                from pypdf import PdfWriter

                writer = PdfWriter()
                for blob in pdf_pages:
                    writer.append(BytesIO(blob))
                with OUT.open("wb") as f:
                    writer.write(f)
            except ImportError:
                OUT.write_bytes(pdf_pages[0])
                print("Warning: pip install pypdf for full multi-page merge", file=sys.stderr)

        browser.close()

    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes, {n} slides)")
    print("NOTE: Written User Manual remains at PocketBudJet_UserManual.pdf (not overwritten).")
    return 0


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        print("Install playwright: pip install playwright pypdf && playwright install chromium", file=sys.stderr)
        return 1

    narrations = json.loads(NARRATION.read_text(encoding="utf-8")) if NARRATION.exists() else []
    if not narrations:
        print("Run build-user-manual-slides.py first", file=sys.stderr)
        return 1
    return export_via_playwright(narrations)


if __name__ == "__main__":
    raise SystemExit(main())
