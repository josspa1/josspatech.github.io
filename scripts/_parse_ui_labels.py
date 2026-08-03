#!/usr/bin/env python3
import re
from pathlib import Path

xml = Path("assets/screenshots/hhh/_ui-dump.xml").read_text(encoding="utf-8", errors="ignore")
seen = set()
for node in re.findall(r"<node[^>]+>", xml):
    t = re.search(r'text="([^"]*)"', node)
    d = re.search(r'content-desc="([^"]*)"', node)
    b = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
    label = ((t.group(1) if t else "") or (d.group(1) if d else "")).strip()
    if not label or not b or len(label) > 90:
        continue
    if label in seen:
        continue
    seen.add(label)
    print(f"{label!r:55s} {b.groups()}")
