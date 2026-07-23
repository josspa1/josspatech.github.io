#!/usr/bin/env python3
"""Sync HHH guide HTML constants from narration-en.json + chapter pills."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "user-guide-hhh"
HTML = OUT / "index.html"
NARR = OUT / "narration-en.json"


def main() -> None:
    narr = json.loads(NARR.read_text(encoding="utf-8"))
    html = HTML.read_text(encoding="utf-8")

    starts = [
        int(m.group(1))
        for m in re.finditer(
            r'<button class="chapter-btn[^"]*"[^>]*data-slide="(\d+)"',
            html,
        )
    ]
    if not starts:
        starts = [0, 7, 11, 22, 26, 40, 47, 56, 63, 66, 70, 76, 79, 101, 103]

    n = len(narr)
    narr_js = "const NARRATION = " + json.dumps(narr, ensure_ascii=False) + ";"
    html2, c1 = re.subn(r"const NARRATION = \[[\s\S]*?\];", narr_js, html, count=1)
    html2, c2 = re.subn(
        r"const CHAPTER_STARTS = \[[^\]]*\];",
        "const CHAPTER_STARTS = " + json.dumps(starts) + ";",
        html2,
        count=1,
    )
    html2, c3 = re.subn(r"const LAST_SLIDE = \d+;", f"const LAST_SLIDE = {n - 1};", html2, count=1)

    # Empty transcript — deck.js rebuilds sentence-level spans
    html2, c4 = re.subn(
        r'(<div class="transcript-body"[^>]*id="transcriptBody"[^>]*>)[\s\S]*?(</div>\s*</div>\s*</div>\s*</div>\s*<div class="chapter-nav")',
        r'\1\n        </div>\n             </div>\n            </div>\n           </div>\n           <div class="chapter-nav"',
        html2,
        count=1,
    )

    # Sentence highlight styles if missing
    if ".transcript-sentence.active" not in html2 or "transcript-sentence.past" not in html2:
        css = """
         .transcript-sentence { transition: color 0.2s ease, font-weight 0.2s ease; }
         .transcript-sentence.active { color: var(--navy); font-weight: 600; }
         .transcript-sentence.past { color: var(--navy); opacity: 0.75; }
"""
        html2 = html2.replace(
            ".transcript-para.current { border-left-color: var(--gold); background: rgba(200,170,110,0.1); }",
            ".transcript-para.current { border-left-color: var(--gold); background: rgba(200,170,110,0.1); }\n"
            + css,
            1,
        )

    # Bump narration count chrome
    html2 = re.sub(
        r"\d+ slides with synced narration",
        f"{n} slides with synced narration",
        html2,
    )

    HTML.write_text(html2, encoding="utf-8", newline="\n")
    print(f"synced narration={n} chapters={starts} LAST={n-1} N={c1} C={c2} L={c3} T={c4}")
    if c1 != 1 or c2 != 1 or c3 != 1 or c4 != 1:
        raise SystemExit(f"replace counts unexpected: {c1,c2,c3,c4}")


if __name__ == "__main__":
    main()
