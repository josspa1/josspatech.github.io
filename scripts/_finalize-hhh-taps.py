#!/usr/bin/env python3
from pathlib import Path
import re

html_path = Path(__file__).resolve().parents[1] / "videos" / "user-guide-hhh" / "index.html"
html = html_path.read_text(encoding="utf-8")

for m in re.finditer(r'data-index="(\d+)"([^>]*)>', html):
    idx = m.group(1)
    attrs = m.group(2)
    if "data-tap-none" in attrs:
        print(f"{idx} NONE")
        continue
    ty = re.search(r'data-tap-y="([^"]+)"', attrs)
    tx = re.search(r'data-tap-x="([^"]+)"', attrs)
    lab = re.search(r'data-tap-label="([^"]+)"', attrs)
    if not ty:
        continue
    y = float(ty.group(1))
    x = float(tx.group(1)) if tx else -1
    if y >= 94 or y <= 4:
        print(idx, x, y, lab.group(1) if lab else "")

print("none-count", html.count("data-tap-none"))
print("tap-count", html.count("data-tap-x="))

old = "wishlist-sellers-2026-07-24"
new = "taps-accurate-2026-07-24"
if old in html:
    n = html.count(old)
    html_path.write_text(html.replace(old, new), encoding="utf-8", newline="\n")
    print(f"bumped {n} cache busts to {new}")
else:
    busts = sorted(set(re.findall(r"\?v=([^\"]+)", html)))
    print("old bust not found; current:", busts[:10])
