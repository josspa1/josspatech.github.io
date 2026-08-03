#!/usr/bin/env python3
import re, subprocess
from pathlib import Path
ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
S = "R5CXC2K4Z8F"
UI = Path(__file__).resolve().parents[1] / "assets/screenshots/hhh/_capture_verify/_ui.xml"
subprocess.run([ADB, "-s", S, "shell", "uiautomator", "dump", "/sdcard/ui.xml"], capture_output=True)
subprocess.run([ADB, "-s", S, "pull", "/sdcard/ui.xml", str(UI)], capture_output=True)
xml = UI.read_text(encoding="utf-8", errors="ignore")
for node in re.findall(r"<node[^>]+>", xml):
    text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
    desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
    if not text and not desc:
        continue
    m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
    if not m:
        continue
    l,t,r,b = map(int, m.groups())
    if b < 150 or t > 2950:
        continue
    line = f"{t:4d}-{b:4d}  {(text or desc)[:80]}"
    print(line.encode("ascii", "replace").decode("ascii"))
