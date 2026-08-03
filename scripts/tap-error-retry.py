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
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        if label.lower() not in f"{text} {desc}".lower():
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        cx = (int(m.group(1)) + int(m.group(3))) // 2
        cy = (int(m.group(2)) + int(m.group(4))) // 2
        print("tap", label, cx, cy)
        adb("shell", "input", "tap", str(cx), str(cy))
        time.sleep(2)
        return True
    print("miss", label)
    return False

tap("Try again")
xml = ui()
texts = [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]
print("after try again:", texts[:30])
if any("unexpected" in t.lower() for t in texts):
    tap("Go to Home")
    xml = ui()
    texts = [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]
    print("after go home:", texts[:30])
