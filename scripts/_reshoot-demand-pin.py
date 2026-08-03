#!/usr/bin/env python3
"""Reshoot current Demand PIN+QR view (already scrolled)."""
from __future__ import annotations
import re, subprocess
from pathlib import Path

ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
S = "R5CXC2K4Z8F"
PKG = "com.josspatech.handyhorology"
ST = Path(__file__).resolve().parents[1] / "assets/screenshots/hhh/_capture_verify"
UI = ST / "_ui.xml"

def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)

line = next((l for l in adb("shell", "dumpsys", "window").stdout.splitlines() if "mCurrentFocus" in l), "")
if PKG not in line:
    raise SystemExit(f"not HHH: {line}")

adb("shell", "screencap", "-p", "/sdcard/hhh-shot.png")
dest = ST / "21b-demand-pin-qr.CANDIDATE.png"
adb("pull", "/sdcard/hhh-shot.png", str(dest))
adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
adb("pull", "/sdcard/ui.xml", str(UI))
xml = UI.read_text(encoding="utf-8", errors="ignore")
texts = [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]
(ST / "21b-demand-pin-qr.CANDIDATE_texts.txt").write_text("\n".join(texts[:80]), encoding="utf-8")
joined = " ".join(texts)
print("size", dest.stat().st_size)
print("has Share PIN", "Share PIN" in joined)
print("has hint", "Show this PIN" in joined)
print("pin digits", re.findall(r"\b\d{4}\b", joined))
print("has Copy QR", "Copy QR" in joined)
if "Share PIN" not in joined or "Show this PIN" not in joined:
    raise SystemExit("bad frame")
print("OK")
