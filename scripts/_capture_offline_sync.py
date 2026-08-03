#!/usr/bin/env python3
"""Capture Offline Show Pack + Device Sync (in-app only, staging)."""
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
    print(f"tap {needle!r} @ {best[1]},{best[2]} ({best[3]})")
    mod.tap(best[1], best[2], wait=2.0)
    return True


mod.wake_and_launch()
ok, reason = mod.foreground_ok()
print("start:", ok, reason)
if not ok:
    raise SystemExit(1)

# --- Offline Show Pack via Settings ---
mod.tab("Settings")
time.sleep(1.2)
mod.swipe_down(3)
found = False
for _ in range(12):
    if mod.has(r"Offline Show Pack"):
        found = True
        break
    mod.swipe_up(1)
if not found:
    raise SystemExit("Offline Show Pack row not found")
if not tap_largest("Offline Show Pack"):
    raise SystemExit("tap Offline failed")
time.sleep(1.0)
if not mod.has(r"Offline Show Pack|Download|Pack|offline"):
    raise SystemExit("not on Offline Show Pack screen")
# Reject if looks like OS downloads/files picker
if mod.has(r"All contacts|Downloads|Open from|Files"):
    # Files picker would be bad — but Downloads word might appear in-app
    if mod.has(r"All contacts|Recent files|Show roots"):
        raise SystemExit("OS file picker detected")
p_off = mod.shot("25-offline-show-pack")
print("offline:", p_off)
mod.back(1)
time.sleep(0.8)

# --- Device Sync via Tools → Sync my devices (avoid OS share) ---
mod.tab("Tools")
time.sleep(1.0)
mod.swipe_down(4)
for _ in range(14):
    if mod.has(r"Sync my devices|Device Sync"):
        break
    mod.swipe_up(1)
if not tap_largest("Sync my devices"):
    if not tap_largest("Device Sync"):
        # File backup path
        mod.tab("Settings")
        time.sleep(0.8)
        for _ in range(10):
            if mod.has(r"File backup|Backup"):
                break
            mod.swipe_up(1)
        tap_largest("File backup")
        time.sleep(1.0)
        for _ in range(6):
            if mod.has(r"Device Sync"):
                break
            mod.swipe_up(1)
        if not tap_largest("Device Sync"):
            raise SystemExit("Device Sync not found")
time.sleep(1.5)
if mod.has(r"All contacts|Share via|Bluetooth pair"):
    # BLE share sheet risk — only abort on contacts
    if mod.has(r"All contacts"):
        raise SystemExit("OS contacts detected on Device Sync path")
if not mod.has(r"Device Sync|Sync|peer|LAN|Wi-?Fi|Start|Listen|Join"):
    print("WARN: Device Sync markers weak — still staging for review")
p_sync = mod.shot("24-device-sync")
print("sync:", p_sync)
mod.back(2)
print("done")
