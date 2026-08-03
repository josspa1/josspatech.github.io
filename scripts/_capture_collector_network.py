#!/usr/bin/env python3
"""Capture Collector Network (Settings) — demo contacts only; abort on OS Contacts."""
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


def abort_if_os() -> None:
    if mod.has(
        r"All contacts|Contact details|com\.android\.contacts|com\.samsung\.android\.app\.contacts|Favorites.*Recents"
    ):
        raise SystemExit("OS contacts — abort")


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
        if area < 4000 or y1 > 2700:
            continue
        score = area + (50000 if 'clickable="true"' in node else 0)
        if best is None or score > best[0]:
            best = (score, (x1 + x2) // 2, (y1 + y2) // 2)
    if not best:
        print(f"MISS {needle}")
        return False
    print(f"tap {needle!r} @ {best[1]},{best[2]}")
    mod.tap(best[1], best[2], wait=2.0)
    abort_if_os()
    return True


mod.wake_and_launch()
ok, reason = mod.foreground_ok()
print("start:", ok, reason)
mod.tab("Settings")
time.sleep(1.2)
mod.swipe_down(3)
for _ in range(12):
    if mod.has(r"Collector Network"):
        break
    mod.swipe_up(1)
if not tap_largest("Collector Network"):
    raise SystemExit("Collector Network missing")
time.sleep(1.5)
abort_if_os()
if not mod.has(r"Collector Network|Contacts|Places|Deals|Visits"):
    raise SystemExit("not on Collector Network screen")
# Do NOT tap Add / import / phone icon that could open OS contacts
p = mod.shot("20-collectors-tab")
print("collectors:", p)
mod.back(1)
print("done")
