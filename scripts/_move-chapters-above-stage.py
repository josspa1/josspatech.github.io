#!/usr/bin/env python3
"""Move chapter pills above the phone stage so they are never viewport-clipped."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "videos"
BUST = "chapters-above-2026-07-28"


def move_chapters_above_stage(html: str) -> str:
    m = re.search(r'(\s*<div class="chapter-nav"[^>]*>[\s\S]*?</div>)', html)
    if not m:
        return html
    block = m.group(1).strip()
    # Already above stage?
    before = html[: m.start()]
    if re.search(r'walkthrough-stage">\s*$', before[-200:]) is None and "walkthrough-stage" in before:
        # If chapter-nav appears before first walkthrough-stage, keep
        stage_pos = html.find("walkthrough-stage")
        if stage_pos != -1 and m.start() < stage_pos:
            return html
    html2 = html[: m.start()] + html[m.end() :]
    html2, n = re.subn(
        r'(\s*)(<div class="(?:user-manual-stage )?walkthrough-stage">)',
        r"\1" + block + r"\n\1\2",
        html2,
        count=1,
    )
    if n != 1:
        raise RuntimeError("failed to insert chapter-nav before stage")
    return html2


def shrink_phone_css(css: str, width: int) -> str:
    css = re.sub(r"width:\s*340px\s*!important", f"width: {width}px !important", css)
    css = re.sub(r"width:\s*360px\b", f"width: {width + 20}px", css)
    css = re.sub(r"width:\s*440px\s*!important", f"width: {width}px !important", css)
    css = re.sub(r"width:\s*460px\b", f"width: {width + 20}px", css)
    return css


def bust(html: str) -> str:
    html = re.sub(r'walkthrough\.css\?v=[^"]+', f"walkthrough.css?v={BUST}", html)
    html = re.sub(r'deck\.js\?v=[^"]+', f"deck.js?v={BUST}", html)
    return html


def patch_inline(html: str, width: int) -> str:
    html = re.sub(
        r"\.phone-frame \{ width: \d+px;",
        f".phone-frame {{ width: {width}px;",
        html,
        count=1,
    )
    html = re.sub(
        r"\.phone-column \{ flex-shrink: 0; width: \d+px;",
        f".phone-column {{ flex-shrink: 0; width: {width + 20}px;",
        html,
        count=1,
    )
    html = html.replace(
        ".chapter-nav { display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5rem; margin-top: 1.5rem; }",
        ".chapter-nav { display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5rem; margin: 0 0 1.25rem; padding: 0.35rem 0 0.5rem; overflow: visible; }",
    )
    html = re.sub(
        r"\.chapter-nav \{\s*display: flex; flex-wrap: wrap; justify-content: center; gap: 0\.5rem;\s*margin-top: 1\.5rem;\s*\}",
        ".chapter-nav {\n display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5rem;\n margin: 0 0 1.25rem; padding: 0.35rem 0 0.5rem; overflow: visible;\n }",
        html,
        count=1,
    )
    return html


def main() -> None:
    for d in sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name.startswith("user-guide")):
        idx = d / "index.html"
        if not idx.exists():
            continue
        width = 300 if "hhh" in d.name else 320
        html = idx.read_text(encoding="utf-8")
        html = move_chapters_above_stage(html)
        html = bust(html)
        html = patch_inline(html, width)
        idx.write_text(html, encoding="utf-8")
        print("html", d.name)

        css_path = d / "walkthrough.css"
        if css_path.exists():
            css_path.write_text(
                shrink_phone_css(css_path.read_text(encoding="utf-8"), width),
                encoding="utf-8",
            )
            print(" css", d.name)

    shared = ROOT / "shared" / "walkthrough.css"
    s = shared.read_text(encoding="utf-8")
    s = re.sub(
        r"(\.walkthrough-stage \.phone-frame \{\s*\n\s*width:\s*)340px",
        r"\g<1>300px",
        s,
        count=1,
    )
    if "Chapter pills sit ABOVE" not in s:
        s += """

/* Chapter pills sit ABOVE the phone so they are never viewport-clipped under a tall frame */
.walkthrough .chapter-nav,
.user-manual .chapter-nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.5rem;
  margin: 0 0 1.25rem;
  padding: 0.35rem 0 0.65rem;
  overflow: visible;
  max-height: none;
}
"""
    shared.write_text(s, encoding="utf-8")
    print("shared ok")


if __name__ == "__main__":
    main()
