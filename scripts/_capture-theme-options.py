#!/usr/bin/env python3
"""Capture Settings with Theme row + Light/Dark/System options visible."""
import re, subprocess, time
from pathlib import Path

ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
S = "R5CXC2K4Z8F"
ST = Path(__file__).resolve().parents[1] / "assets/screenshots/hhh/_capture_verify"
UI = ST / "_ui.xml"


def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)


def dump():
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    return UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""


def texts(xml):
    return [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip() and not t.startswith("&#")]


adb("shell", "am", "force-stop", "dev.mobile.maestro")
adb("shell", "input", "tap", "1260", "2920")
time.sleep(1.5)
# top
for _ in range(10):
    adb("shell", "input", "swipe", "720", "900", "720", "2300", "260")
    time.sleep(0.25)
# small scroll so Theme + options sit mid-frame (not under tab bar)
adb("shell", "input", "swipe", "720", "2000", "720", "1400", "300")
time.sleep(1.0)
xml = dump()
t = texts(xml)
print("visible:", t)
joined = " ".join(t)
# Theme options typically Light / Dark / System (or translated)
has_theme = "Theme" in joined
has_opts = sum(1 for k in ("Light", "Dark", "System", "light", "dark") if k in joined) >= 2
print("has_theme", has_theme, "has_opts", has_opts)
adb("shell", "screencap", "-p", "/sdcard/hhh-shot.png")
dest = ST / "10c-settings-theme-detail.CANDIDATE.png"
adb("pull", "/sdcard/hhh-shot.png", str(dest))
(ST / "10c-settings-theme-detail.CANDIDATE_texts.txt").write_text("\n".join(t), encoding="utf-8")
print("STAGED", dest.stat().st_size)
