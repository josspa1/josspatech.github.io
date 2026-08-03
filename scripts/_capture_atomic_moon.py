#!/usr/bin/env python3
"""Capture Atomic / Moon by tapping largest matching card bounds (no search)."""
import os
import re
import time
from pathlib import Path
from importlib.machinery import SourceFileLoader

os.environ["ANDROID_SERIAL"] = os.environ.get("ANDROID_SERIAL", "R5CXC2K4Z8F")
mod = SourceFileLoader(
    "cap",
    str(Path(__file__).resolve().parent / "capture-hhh-phone-priority-shots.py"),
).load_module()


def clear_tools_search() -> None:
    if mod.has(r"aExact|Exact Time|Moon Phase") and mod.has(r"Find a tool"):
        # tap search then delete
        mod.tap_label("Find a tool", partial=True)
        time.sleep(0.3)
        for _ in range(24):
            mod.adb("shell", "input", "keyevent", "67")  # DEL
        mod.adb("shell", "input", "keyevent", "4")  # hide keyboard
        time.sleep(0.5)


def largest_card(needle: str):
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
        w, h = x2 - x1, y2 - y1
        area = w * h
        # Prefer card-sized targets (not tiny text, not full-screen)
        if h < 80 or area < 30000 or area > 2_000_000:
            continue
        if y2 > 2750:  # tab bar
            continue
        clickable = 'clickable="true"' in node
        score = area + (100000 if clickable else 0)
        if best is None or score > best[0]:
            best = (score, (x1 + x2) // 2, (y1 + y2) // 2, w, h, hay[:60])
    return best


def open_tool(needle: str, detail_ok) -> bool:
    mod.tab("Tools")
    time.sleep(1.0)
    clear_tools_search()
    mod.swipe_down(5)
    time.sleep(0.4)
    # Scroll until a large card for needle exists
    for _ in range(18):
        hit = largest_card(needle)
        if hit:
            print(f"found {needle}: {hit}")
            mod.tap(hit[1], hit[2], wait=2.5)
            if detail_ok():
                return True
            print("tap did not open detail, continue scroll")
        mod.swipe_up(1)
    return False


def is_atomic() -> bool:
    return mod.has(r"Exact Time") and not mod.has(r"Find a tool")


def is_moon() -> bool:
    return mod.has(r"Moon Phase|illumination|Age of moon|Northern") and not mod.has(r"Find a tool")


mod.wake_and_launch()
ok, reason = mod.foreground_ok()
print("start:", ok, reason)
clear_tools_search()

if not open_tool("Exact Time", is_atomic):
    raise SystemExit("Exact Time failed")
p1 = mod.shot("17-atomic-clock")
print("atomic:", p1)
mod.back(1)
time.sleep(1.0)

if not open_tool("Moon Phase", is_moon):
    raise SystemExit("Moon Phase failed")
p2 = mod.shot("18-moon-phase")
print("moon:", p2)
mod.back(1)
print("done")
