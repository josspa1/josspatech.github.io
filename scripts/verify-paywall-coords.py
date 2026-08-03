#!/usr/bin/env python3
"""Navigate Upgrade via known coords; verify with screencap only."""
import os, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ADB = os.path.join(os.environ["LOCALAPPDATA"], "Android", "Sdk", "platform-tools", "adb.exe")
S = "R5CXC2K4Z8F"
OUT = r"C:\Users\jossp\Documents\GitHub\josspatech.github.io\assets\screenshots\hhh\_capture_2026-07-24"

def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)

def shot(name):
    path = os.path.join(OUT, name)
    adb("shell", "screencap", "-p", "/sdcard/shot.png")
    adb("pull", "/sdcard/shot.png", path)
    print(f"shot {name} bytes={os.path.getsize(path)}")

def tap(x, y, label=""):
    print(f"tap {label} @ {x},{y}")
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(1.8)

# From earlier successful dumps on this device (1440-ish width / ~3120 height)
# Settings tab
tap(1260, 2920, "Settings tab")
shot("v-settings.png")
# Upgrade to Pro in header (desc button) — was @ 1103,864
tap(1103, 864, "Upgrade to Pro header")
shot("v-paywall.png")
# Also try subscription row if still on settings
# (no-op if paywall already open)
print("focus", [l for l in adb("shell", "dumpsys", "window").stdout.splitlines() if "mCurrentFocus" in l][:1])
