"""Print WRONG/CHECK rows + WC/Share slide mapping."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "user-guide-hhh"
audit = (OUT / "_PICTURE_AUDIT_2026-07-24.md").read_text(encoding="utf-8")
print("=== Audit flags ===")
for line in audit.splitlines():
    if any(x in line for x in ("| WRONG", "| CHECK", "| **WRONG**", "| **MISSING**", "| **CHECK**")):
        print(line)

html = (OUT / "index.html").read_text(encoding="utf-8")
# simpler: per-slide blocks
blocks = re.findall(
    r'data-index="(\d+)"[^>]*>\s*<img src="([^"]+)"[^>]*alt="([^"]*)"',
    html,
)
print(f"\nhtml img tags: {len(blocks)}")
m = {x["i"]: x for x in json.loads((OUT / "_shot-map.json").read_text(encoding="utf-8"))}
mism = 0
for i_s, src, alt in blocks:
    i = int(i_s)
    row = m.get(i)
    if row and row.get("src") != src:
        mism += 1
        print(f"mismatch {i}: map={row.get('src')} html={src}")
print(f"shot-map vs html mismatches: {mism}")

print("\n=== Slides using 09-web-companion.png ===")
for x in m.values():
    if "09-web-companion" in (x.get("src") or ""):
        print(f"{x['i']:3d}  {x['n'][:120]}")
