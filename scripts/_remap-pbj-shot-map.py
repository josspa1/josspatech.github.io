#!/usr/bin/env python3
"""Rebuild PBJ _shot-map.json from index.html + narration-en.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "user-guide"
narr = json.loads((OUT / "narration-en.json").read_text(encoding="utf-8"))
html = (OUT / "index.html").read_text(encoding="utf-8")

rows = []
for m in re.finditer(r'<div class="slide(?:\s+active)?"([^>]*)>', html):
    attrs = m.group(1)
    idx = int(re.search(r'data-index="(\d+)"', attrs).group(1))
    chunk = html[m.start() : m.start() + 1200]
    src_m = re.search(r'<img[^>]+src="([^"]+)', chunk)
    alt_m = re.search(r'alt="([^"]*)"', chunk)
    src = src_m.group(1).split("?")[0] if src_m else None
    rows.append(
        {
            "i": idx,
            "n": narr[idx] if idx < len(narr) else "",
            "src": src,
            "alt": alt_m.group(1) if alt_m else "",
            "exists": bool(src and (ROOT / src.lstrip("/")).exists()),
        }
    )

# Ensure 0..n-1 order by index
rows.sort(key=lambda r: r["i"])
(OUT / "_shot-map.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
empty = sum(1 for r in rows if not (r.get("alt") or "").strip())
print(f"slides={len(rows)} emptyAlts={empty} missingFiles={sum(1 for r in rows if not r['exists'])}")
