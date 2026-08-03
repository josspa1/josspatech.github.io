#!/usr/bin/env python3
import os, re, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ADB = os.path.join(os.environ["LOCALAPPDATA"], "Android", "Sdk", "platform-tools", "adb.exe")
S = "R5CXC2K4Z8F"
XML = r"C:\Users\jossp\Documents\GitHub\josspatech.github.io\assets\screenshots\hhh\_ui.xml"

def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)

def ui():
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", XML)
    return open(XML, encoding="utf-8", errors="ignore").read()

print("focus", [l for l in adb("shell", "dumpsys", "window").stdout.splitlines() if "mCurrentFocus" in l][:2])
xml = ui()
texts = [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]
print("ALL TEXTS:")
for t in texts:
    print(" -", t)
for t in texts:
    low = t.lower()
    if any(k in low for k in ("upgrade", "pro", "trial", "unexpected", "something went")):
        print("HIT:", t)
