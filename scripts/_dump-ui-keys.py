#!/usr/bin/env python3
import re
from pathlib import Path
import subprocess

ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
S = "R5CXC2K4Z8F"
UI = Path(__file__).resolve().parents[1] / "assets/screenshots/hhh/_capture_verify/_ui.xml"

subprocess.run([ADB, "-s", S, "shell", "uiautomator", "dump", "/sdcard/ui.xml"], capture_output=True)
subprocess.run([ADB, "-s", S, "pull", "/sdcard/ui.xml", str(UI)], capture_output=True)
xml = UI.read_text(encoding="utf-8", errors="ignore")
print("focus:", next((l for l in subprocess.run([ADB,"-s",S,"shell","dumpsys","window"],capture_output=True,text=True).stdout.splitlines() if "mCurrentFocus" in l), "?"))
keys = ("demand", "dealer", "send", "rolodex", "share", "want", "pin", "name", "patek", "tools")
for node in re.findall(r"<node[^>]+>", xml):
    text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
    desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
    hay = f"{text} {desc}".lower()
    if not any(k in hay for k in keys):
        continue
    m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
    print(repr(text or desc)[:70], m.groups() if m else None)
