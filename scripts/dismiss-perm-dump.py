#!/usr/bin/env python3
import os, re, subprocess, sys, time
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

def tap(label):
    xml = ui()
    for node in re.findall(r"<node[^>]+>", xml):
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        if label.lower() not in text.lower():
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        cx = (int(m.group(1)) + int(m.group(3))) // 2
        cy = (int(m.group(2)) + int(m.group(4))) // 2
        print("tap", text, cx, cy)
        adb("shell", "input", "tap", str(cx), str(cy))
        time.sleep(1.5)
        return True
    print("miss", label)
    return False

tap("Don't allow") or tap("Don’t allow") or tap("Allow")
time.sleep(2)
# Maybe terms gate
tap("I Accept") or tap("Accept") or tap("Continue")
time.sleep(2)
xml = ui()
texts = [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]
print("TEXTS:")
for t in texts:
    print(" -", t)
adb("shell", "screencap", "-p", "/sdcard/boot3.png")
adb("pull", "/sdcard/boot3.png", r"C:\Users\jossp\Documents\GitHub\josspatech.github.io\assets\screenshots\hhh\_capture_2026-07-24\boot3.png")
