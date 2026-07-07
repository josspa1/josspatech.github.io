#!/usr/bin/env python3
"""Export HHH user manual PDF — one page per slide (screenshot + narration)."""
from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "videos" / "user-guide-hhh" / "index.html"
NARRATION = ROOT / "videos" / "user-guide-hhh" / "narration-en.json"
OUT = ROOT / "docs" / "handyhorology" / "HandyHorology_UserGuide.pdf"
TMP = ROOT / "videos" / "user-guide-hhh" / "_pdf_tmp"


def slide_count() -> int:
    if NARRATION.exists():
        return len(json.loads(NARRATION.read_text(encoding="utf-8")))
    text = HTML.read_text(encoding="utf-8")
    import re

    m = re.search(r"const LAST_SLIDE = (\d+);", text)
    return int(m.group(1)) + 1 if m else 0


def build_print_html(narrations: list[str]) -> Path:
    """Static print layout — all slides for reliable multi-page PDF."""
    pages: list[str] = []
    for i, narration in enumerate(narrations):
        pages.append(
            textwrap.dedent(
                f"""\
                <section class="page">
                 <header>
                  <span class="brand">Handy Horology Helper</span>
                  <span class="num">Slide {i + 1} / {len(narrations)}</span>
                 </header>
                 <div class="phone">
                  <div class="slide-slot" data-slide="{i}"></div>
                 </div>
                 <p class="narration">{narration}</p>
                </section>
                """
            )
        )
    doc = textwrap.dedent(
        f"""\
        <!DOCTYPE html>
        <html lang="en"><head>
        <meta charset="UTF-8">
        <title>HHH User Manual PDF</title>
        <style>
         @page {{ size: letter portrait; margin: 0.45in; }}
         * {{ box-sizing: border-box; }}
         body {{ font-family: 'Segoe UI', system-ui, sans-serif; color: #3D1522; margin: 0; }}
         .page {{
           page-break-after: always; min-height: 9.5in;
           display: flex; flex-direction: column; align-items: center;
           padding: 0.2in 0;
         }}
         .page:last-child {{ page-break-after: auto; }}
         header {{
           width: 100%; display: flex; justify-content: space-between;
           font-size: 11px; color: #7A3A4F; margin-bottom: 0.15in;
         }}
         .brand {{ font-weight: 700; letter-spacing: 0.02em; }}
         .phone {{
           width: 2.4in; height: 5.1in; border: 3px solid #3D1522;
           border-radius: 18px; overflow: hidden; background: #F5EDE4;
           flex-shrink: 0;
         }}
         .phone img {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
         .narration {{
           margin-top: 0.2in; max-width: 6.5in; font-size: 13px;
           line-height: 1.45; text-align: center; color: #3D1522;
         }}
        </style>
        </head><body>
        {''.join(pages)}
        <script>
         const LAST = {len(narrations) - 1};
         async function hydrate() {{
           const src = {json.dumps(HTML.resolve().as_uri())};
           const host = document.createElement('iframe');
           host.style.cssText = 'position:fixed;left:-9999px;width:400px;height:860px';
           host.src = src + '?record=1';
           document.body.appendChild(host);
           await new Promise(r => host.onload = r);
           const win = host.contentWindow;
           await new Promise(r => setTimeout(r, 1500));
           for (let i = 0; i <= LAST; i++) {{
             win.document.querySelectorAll('.slide').forEach((s, j) => s.classList.toggle('active', j === i));
             await new Promise(r => setTimeout(r, 120));
             const active = win.document.querySelector('.slide.active');
             const slot = document.querySelector('.slide-slot[data-slide="' + i + '"]');
             if (active && slot) {{
               const img = active.querySelector('img');
               if (img && img.src) {{
                 slot.innerHTML = '<img src="' + img.src + '" alt="">';
               }} else {{
                 slot.innerHTML = active.innerHTML;
               }}
             }}
           }}
           host.remove();
           document.body.classList.add('ready');
         }}
         hydrate();
        </script>
        </body></html>
        """
    )
    TMP.mkdir(parents=True, exist_ok=True)
    path = TMP / "print-all.html"
    path.write_text(doc, encoding="utf-8")
    return path


def export_via_playwright(narrations: list[str]) -> int:
    from playwright.sync_api import sync_playwright

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
             body {{ font-family: Segoe UI, sans-serif; color: #3D1522; margin: 0; text-align: center; }}
             .hdr {{ display:flex; justify-content:space-between; font-size:11px; color:#7A3A4F; margin-bottom:8px; }}
             img {{ max-width: 100%; height: auto; max-height: 7.5in; }}
             p {{ font-size: 13px; line-height: 1.45; margin-top: 12px; max-width: 7in; margin-left:auto; margin-right:auto; }}
            </style></head><body>
            <div class="hdr"><span>Handy Horology Helper User Manual</span><span>Slide {i + 1} / {n}</span></div>
            <img src="data:image/png;base64,{__import__('base64').b64encode(shot).decode()}" alt="">
            <p>{narr}</p></body></html>"""

            sub = ctx.new_page()
            sub.set_content(wrap, wait_until="load")
            pdf_pages.append(sub.pdf(format="Letter", print_background=True, margin={"top": "0.35in", "bottom": "0.35in", "left": "0.5in", "right": "0.5in"}))
            sub.close()

        if len(pdf_pages) == 1:
            OUT.write_bytes(pdf_pages[0])
        else:
            try:
                from pypdf import PdfWriter

                writer = PdfWriter()
                for blob in pdf_pages:
                    from io import BytesIO

                    writer.append(BytesIO(blob))
                with OUT.open("wb") as f:
                    writer.write(f)
            except ImportError:
                # Fallback: write first page only if pypdf missing
                OUT.write_bytes(pdf_pages[0])
                print("Warning: pip install pypdf for full multi-page merge", file=sys.stderr)

        browser.close()

    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes, {n} slides)")
    return 0


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        print("Install playwright: pip install playwright pypdf && playwright install chromium", file=sys.stderr)
        return 1

    narrations = json.loads(NARRATION.read_text(encoding="utf-8")) if NARRATION.exists() else []
    if not narrations:
        print("Run build-hhh-user-manual-slides.py first", file=sys.stderr)
        return 1
    return export_via_playwright(narrations)


if __name__ == "__main__":
    raise SystemExit(main())
