#!/usr/bin/env python3
"""Capture Print & Export List only."""
from __future__ import annotations
import re, subprocess, time
from pathlib import Path

ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
S = "R5CXC2K4Z8F"
PKG = "com.josspatech.handyhorology"
ST = Path(__file__).resolve().parents[1] / "assets/screenshots/hhh/_capture_verify"
UI = ST / "_ui.xml"

def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)

def ensure():
    if PKG not in adb("shell", "dumpsys", "window").stdout:
        adb("shell", "am", "start", "-n", f"{PKG}/.MainActivity"); time.sleep(3)

def dump():
    ensure()
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    return UI.read_text(encoding="utf-8", errors="ignore")

def find(xml, *labels):
    best = None
    for node in re.findall(r"<node[^>]+>", xml):
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        hay = f"{text} {desc}"
        if not any(l.lower() in hay.lower() for l in labels):
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m: continue
        l,t,r,b = map(int, m.groups())
        cy = (t+b)//2
        if cy < 150 or cy > 2700: continue
        score = -abs(cy-1600)+(r-l)//10
        if best is None or score > best[2]:
            best = ((l+r)//2, cy, score, text or desc)
    return best

adb("shell", "cmd", "statusbar", "collapse")
adb("shell", "am", "start", "-n", f"{PKG}/.MainActivity"); time.sleep(2.5)
ensure()
adb("shell", "input", "tap", "900", "2863"); time.sleep(2)
# clear search if any
xml = dump()
hit = find(xml, "Find a tool")
if hit:
    adb("shell", "input", "tap", str(hit[0]), str(hit[1])); time.sleep(0.4)
    # clear with deletes
    for _ in range(20):
        adb("shell", "input", "keyevent", "67")
    time.sleep(0.5)

for i in range(10):
    xml = dump()
    hit = find(xml, "Print & Export List", "Print & Export")
    if hit:
        print("found", hit)
        adb("shell", "input", "tap", str(hit[0]), str(hit[1])); time.sleep(2.5)
        break
    print("scroll", i+1)
    adb("shell", "input", "swipe", "720", "2300", "720", "900", "350"); time.sleep(0.65)
else:
    raise SystemExit("Print not found")

ensure()
adb("shell", "screencap", "-p", "/sdcard/hhh-shot.png")
dest = ST / "33-print-export.CANDIDATE.png"
adb("pull", "/sdcard/hhh-shot.png", str(dest))
xml = dump()
texts = [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]
(ST / "33-print-export.CANDIDATE_texts.txt").write_text("\n".join(texts[:80]), encoding="utf-8")
print("STAGED", dest.stat().st_size, [t.encode("ascii","replace").decode("ascii") for t in texts[:15]])
