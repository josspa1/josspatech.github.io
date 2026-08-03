#!/usr/bin/env python3
import re, subprocess, time
from pathlib import Path

ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
S = "R5CXC2K4Z8F"
ST = Path(__file__).resolve().parents[1] / "assets/screenshots/hhh/_capture_verify"
UI = ST / "_ui.xml"

def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)

adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
adb("pull", "/sdcard/ui.xml", str(UI))
xml = UI.read_text(encoding="utf-8", errors="ignore")
for node in re.findall(r"<node[^>]+>", xml):
    text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
    if "Print" not in text:
        continue
    m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
    print(repr(text)[:70], m.groups() if m else None)

# Left card center for Print
adb("shell", "input", "tap", "387", "2170")
time.sleep(2.8)
adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
adb("pull", "/sdcard/ui.xml", str(UI))
xml = UI.read_text(encoding="utf-8", errors="ignore")
texts = [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]
print("AFTER", [t.encode("ascii", "replace").decode("ascii") for t in texts[:25]])
adb("shell", "screencap", "-p", "/sdcard/hhh-shot.png")
dest = ST / "33-print-export.CANDIDATE.png"
adb("pull", "/sdcard/hhh-shot.png", str(dest))
(ST / "33-print-export.CANDIDATE_texts.txt").write_text("\n".join(texts[:80]), encoding="utf-8")
print("size", dest.stat().st_size)
if "Find a tool" in " ".join(texts):
    raise SystemExit("still on tools hub")
print("OK")
