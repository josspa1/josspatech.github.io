#!/usr/bin/env python3
"""Dump Settings row labels while scrolling."""
import re, subprocess, time
from pathlib import Path

ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
S = "R5CXC2K4Z8F"
UI = Path(__file__).resolve().parents[1] / "assets/screenshots/hhh/_capture_verify/_ui.xml"


def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)


adb("shell", "am", "force-stop", "dev.mobile.maestro")
adb("shell", "input", "tap", "1260", "2920")
time.sleep(2)
keys = ("theme", "language", "security", "lock", "notif", "access", "encrypt", "backup", "share", "voice", "offline")
for i in range(8):
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    xml = UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""
    texts = re.findall(r'text="([^"]+)"', xml)
    interesting = [t for t in texts if any(k in t.lower() for k in keys)]
    print(f"--- swipe {i} ---")
    print(" | ".join(interesting[:30]))
    adb("shell", "input", "swipe", "720", "2200", "720", "1100", "350")
    time.sleep(0.7)
