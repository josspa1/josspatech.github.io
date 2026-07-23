#!/usr/bin/env python3
"""Audit HHH user-guide slide→image map (print + JSON)."""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "videos" / "user-guide-hhh"
narr = json.loads((OUT / "narration-en.json").read_text(encoding="utf-8"))
html = (OUT / "index.html").read_text(encoding="utf-8")

slides = []
for m in re.finditer(r'<div class="slide(?:\s+active)?"([^>]*)>', html):
    a = m.group(1)
    idx = int(re.search(r'data-index="(\d+)"', a).group(1))
    chunk = html[m.start() : m.start() + 900]
    src_m = re.search(r'<img[^>]+src="([^"]+)', chunk)
    alt_m = re.search(r'alt="([^"]*)"', chunk)
    src = src_m.group(1).split("?")[0] if src_m else None
    slides.append({"idx": idx, "src": src, "alt": alt_m.group(1) if alt_m else ""})

by = {s["idx"]: s for s in slides}
rows = []
for i, n in enumerate(narr):
    s = by.get(i, {})
    src = s.get("src")
    rows.append(
        {
            "i": i,
            "n": n,
            "src": src,
            "alt": s.get("alt"),
            "exists": bool(src and (ROOT / src.lstrip("/")).exists()),
        }
    )

(OUT / "_shot-map.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
print(f"narr={len(narr)} slides={len(slides)}")
for r in rows[:15]:
    short = (r["src"] or "").replace("/assets/screenshots/hhh/", "")
    print(f"{r['i']:03d} | {short:40s} | {r['n'][:78]}")
print("--- reuse ---")
for src, n in Counter(r["src"] for r in rows).most_common(12):
    print(f"{n:3d}  {src}")
