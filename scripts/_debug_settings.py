#!/usr/bin/env python3
"""Quick test: Skip onboarding -> Settings -> find demo button."""
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = Path(__import__("os").environ.get("LOCALAPPDATA", "")) / "Android/Sdk/platform-tools/adb.exe"
UI = ROOT / "assets/screenshots/hhh/_ui-dump.xml"
PKG = "com.josspatech.handyhorology"
SERIAL = "emulator-5554"
W, H = 1080, 2400


def adb(*args):
    subprocess.run([ADB, "-s", SERIAL, *args], check=False)


def ui():
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    return UI.read_text(encoding="utf-8", errors="ignore")


def tap(x, y, w=2):
    print(f"tap {x},{y}")
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(w)


def tap_label(label):
    xml = ui()
    for node in re.findall(r"<node[^>]+>", xml):
        if label not in node:
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if m:
            cx = (int(m.group(1)) + int(m.group(3))) // 2
            cy = (int(m.group(2)) + int(m.group(4))) // 2
            tap(cx, cy)
            return True
    print(f"miss {label!r}")
    return False


def swipe_up():
    adb("shell", "input", "swipe", "540", "1970", "540", "840", "400")
    time.sleep(0.7)


adb("shell", "pm", "clear", PKG)
time.sleep(2)
for p in ("android.permission.POST_NOTIFICATIONS", "android.permission.READ_MEDIA_IMAGES"):
    adb("shell", "pm", "grant", PKG, p)
adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
time.sleep(18)
tap_label("Skip") or tap(163, 2206, 10)
xml = ui()
print("home?", "Hunt" in xml or "COMMAND" in xml or "horology" in xml)
tap_label("Settings") or tap(972, 2368, 3)
for i in range(12):
    swipe_up()
xml = ui()
for label in ("Load Demo Collection", "Load Demo Data", "Try it out", "Harold", "Theme", "Backup"):
    print(label, label in xml)
texts = re.findall(r'text="([^"]{2,70})"', xml)
for t in texts:
    if any(k in t for k in ("Demo", "Harold", "Try", "Backup", "Theme", "Settings")):
        print(" ", t)
