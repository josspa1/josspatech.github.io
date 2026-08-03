#!/usr/bin/env python3
import re, subprocess, time
from pathlib import Path
ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
S = "R5CXC2K4Z8F"
PKG = "com.josspatech.handyhorology"
ST = Path(__file__).resolve().parents[1] / "assets/screenshots/hhh/_capture_verify"
UI = ST / "_ui.xml"

def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)

adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
adb("pull", "/sdcard/ui.xml", str(UI))
xml = UI.read_text(encoding="utf-8", errors="ignore")
for node in re.findall(r"<node[^>]+>", xml):
    text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
    if "Print" not in text and "Export" not in text:
        continue
    m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
    clickable = 'clickable="true"' in node
    print(repr(text)[:60], clickable, m.groups() if m else None)

# Prefer clickable Print & Export List
hit = None
for node in re.findall(r"<node[^>]+>", xml):
    text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
    if text != "Print & Export List":
        continue
    m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
    if not m:
        continue
    l,t,r,b = map(int, m.groups())
    # prefer larger parent by tapping below label into card - use card from description node
    hit = ((l+r)//2, (t+b)//2)
print("tap label", hit)
if hit:
    # also try card center from description node
    for node in re.findall(r"<node[^>]+>", xml):
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        if "PDF table" not in text:
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if m:
            l,t,r,b = map(int, m.groups())
            # tap mid of card area - use Print card container approx
            print("pdf text bounds", m.groups())
    # Tap the big card: from dump earlier card was ~70-1370 x 1916-2434
    adb("shell", "input", "tap", "720", "2170")
    time.sleep(2.5)
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    xml2 = UI.read_text(encoding="utf-8", errors="ignore")
    texts = [t for t in re.findall(r'text="([^"]+)"', xml2) if t.strip()]
    print("after", [t.encode("ascii","replace").decode("ascii") for t in texts[:20]])
    if any("Print" in t or "Export" in t or "PDF" in t for t in texts) and "Find a tool" not in " ".join(texts):
        adb("shell", "screencap", "-p", "/sdcard/hhh-shot.png")
        dest = ST / "33-print-export.CANDIDATE.png"
        adb("pull", "/sdcard/hhh-shot.png", str(dest))
        (ST / "33-print-export.CANDIDATE_texts.txt").write_text("\n".join(texts[:80]), encoding="utf-8")
        print("STAGED", dest.stat().st_size)
    else:
        # try exact label tap
        adb("shell", "input", "tap", str(hit[0]), str(hit[1]))
        time.sleep(2.5)
        adb("shell", "screencap", "-p", "/sdcard/hhh-shot.png")
        dest = ST / "33-print-export.CANDIDATE.png"
        adb("pull", "/sdcard/hhh-shot.png", str(dest))
        adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
        adb("pull", "/sdcard/ui.xml", str(UI))
        texts = [t for t in re.findall(r'text="([^"]+)"', UI.read_text(encoding="utf-8", errors="ignore")) if t.strip()]
        (ST / "33-print-export.CANDIDATE_texts.txt").write_text("\n".join(texts[:80]), encoding="utf-8")
        print("retry texts", [t.encode("ascii","replace").decode("ascii") for t in texts[:20]])
        print("STAGED", dest.stat().st_size)
