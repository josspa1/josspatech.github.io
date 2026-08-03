#!/usr/bin/env python3
"""Capture Device Sync only (in-app)."""
import os
import re
import sys
import time
from pathlib import Path
from importlib.machinery import SourceFileLoader

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

os.environ["ANDROID_SERIAL"] = os.environ.get("ANDROID_SERIAL", "R5CXC2K4Z8F")
mod = SourceFileLoader(
    "cap",
    str(Path(__file__).resolve().parent / "capture-hhh-phone-priority-shots.py"),
).load_module()


def tap_largest(needle: str) -> bool:
    xml = mod.ui()
    best = None
    for node in re.findall(r"<node[^>]+>", xml):
        text_m = re.search(r'text="([^"]*)"', node)
        desc_m = re.search(r'content-desc="([^"]*)"', node)
        hay = f"{text_m.group(1) if text_m else ''} {desc_m.group(1) if desc_m else ''}"
        if needle.lower() not in hay.lower():
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        x1, y1, x2, y2 = map(int, m.groups())
        area = (x2 - x1) * (y2 - y1)
        if area < 5000 or y1 > 2700:
            continue
        score = area + (50000 if 'clickable="true"' in node else 0)
        if best is None or score > best[0]:
            best = (score, (x1 + x2) // 2, (y1 + y2) // 2, hay[:70])
    if not best:
        print(f"MISS largest {needle}")
        return False
    label = best[3].encode("ascii", "replace").decode("ascii")
    print(f"tap {needle!r} @ {best[1]},{best[2]} ({label})")
    mod.tap(best[1], best[2], wait=2.0)
    return True


mod.wake_and_launch()
mod.tab("Tools")
time.sleep(1.0)
mod.swipe_down(4)
for _ in range(14):
    if mod.has(r"Sync my devices|Device Sync"):
        break
    mod.swipe_up(1)
if not tap_largest("Sync my devices"):
    raise SystemExit("Sync my devices missing")
time.sleep(1.5)
if mod.has(r"All contacts"):
    raise SystemExit("OS contacts — abort")
p = mod.shot("24-device-sync")
print("sync:", p)
mod.back(1)
print("done")
