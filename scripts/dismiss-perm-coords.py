#!/usr/bin/env python3
import os, re, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ADB = os.path.join(os.environ["LOCALAPPDATA"], "Android", "Sdk", "platform-tools", "adb.exe")
S = "R5CXC2K4Z8F"
XML = r"C:\Users\jossp\Documents\GitHub\josspatech.github.io\assets\screenshots\hhh\_ui.xml"
OUT = r"C:\Users\jossp\Documents\GitHub\josspatech.github.io\assets\screenshots\hhh\_capture_2026-07-24"

def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)

def ui():
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", XML)
    return open(XML, encoding="utf-8", errors="ignore").read()

def dump_texts(label):
    xml = ui()
    texts = [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]
    print(f"=== {label} ===")
    for t in texts:
        print(" -", t)
    return texts

# Permission dialog — tap Don't allow by approximate coords (S938 ~1440x3120)
# Try a few Y positions for the lower button
for y in (2350, 2450, 2550, 2200, 2100):
    print(f"tap Don't allow candidate @ 720,{y}")
    adb("shell", "input", "tap", "720", str(y))
    time.sleep(1.2)
    focus = [l for l in adb("shell", "dumpsys", "window").stdout.splitlines() if "mCurrentFocus" in l]
    print(focus[:1])
    if focus and "permissioncontroller" not in focus[0] and "GrantPermissions" not in focus[0]:
        break

time.sleep(2)
texts = dump_texts("after permission")
adb("shell", "screencap", "-p", "/sdcard/boot4.png")
adb("pull", "/sdcard/boot4.png", os.path.join(OUT, "boot4.png"))

# If terms/onboarding
for label in ("I Accept", "Accept", "Get Started", "Continue", "Skip"):
    xml = ui()
    if any(label.lower() in t.lower() for t in re.findall(r'text="([^"]+)"', xml)):
        # tap it
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
            time.sleep(2)
            break

dump_texts("final")
adb("shell", "screencap", "-p", "/sdcard/boot5.png")
adb("pull", "/sdcard/boot5.png", os.path.join(OUT, "boot5.png"))
