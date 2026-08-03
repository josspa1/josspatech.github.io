#!/usr/bin/env python3
"""Museum piece → Swap meet → QR+PIN. Never Back out of HHH; verify focus always."""
from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
S = "R5CXC2K4Z8F"
PKG = "com.josspatech.handyhorology"
ST = Path(__file__).resolve().parents[1] / "assets/screenshots/hhh/_capture_verify"
UI = ST / "_ui.xml"
BAD = ("dialer", "contacts", "whisker", "maestro", "dialtacts")


def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)


def focus_ok() -> bool:
    out = adb("shell", "dumpsys", "window").stdout.lower()
    if PKG not in out:
        return False
    for line in out.splitlines():
        if "mcurrentfocus" in line:
            if any(b in line for b in BAD):
                return False
            return PKG in line
    return False


def assert_hhh(step: str) -> None:
    if not focus_ok():
        line = next((l for l in adb("shell", "dumpsys", "window").stdout.splitlines() if "mCurrentFocus" in l), "?")
        raise SystemExit(f"ABORT at {step}: not HHH — {line.strip()} (will not screenshot)")


def dump() -> str:
    assert_hhh("before dump")
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    assert_hhh("after dump")
    return UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""


def texts(xml: str) -> list[str]:
    return [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip() and not t.startswith("&#")]


def find(xml: str, *labels: str, min_y: int = 200, max_y: int = 2750):
    best = None
    for node in re.findall(r"<node[^>]+>", xml):
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        hay = f"{text} {desc}"
        if not any(lab.lower() in hay.lower() for lab in labels):
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        cx, cy = (l + r) // 2, (t + b) // 2
        if cy < min_y or cy > max_y:
            continue
        score = -abs(cy - 1600)
        if best is None or score > best[2]:
            best = (cx, cy, score, text or desc)
    return best


def find_tab(xml: str, name: str):
    # Prefer content-desc tab hit targets in bottom bar
    for node in re.findall(r"<node[^>]+>", xml):
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        if name not in desc and text != name:
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        cy = (t + b) // 2
        if cy < 2700:
            continue
        return ((l + r) // 2, cy, 0, desc or text)
    return None


def tap(hit, wait=1.8, step="tap"):
    print(f"{step}: {hit[3]!r} @ {hit[0]},{hit[1]}")
    adb("shell", "input", "tap", str(hit[0]), str(hit[1]))
    time.sleep(wait)
    assert_hhh(step)


def ensure_hhh():
    adb("shell", "am", "force-stop", "com.samsung.android.dialer")
    adb("shell", "am", "force-stop", "com.samsung.android.app.contacts")
    adb("shell", "am", "force-stop", "dev.mobile.maestro")
    adb("shell", "am", "force-stop", "dev.mobile.maestro.test")
    adb("shell", "am", "start", "-n", f"{PKG}/.MainActivity")
    time.sleep(3)
    assert_hhh("launch")


ensure_hhh()
xml = dump()
tab = find_tab(xml, "My Museum")
if not tab:
    raise SystemExit("My Museum tab not found")
tap(tab, 2.0, "tab My Museum")

xml = dump()
print("museum sample:", texts(xml)[:20])
hit = find(xml, "Speedmaster", "Omega", "Carrera", "TAG Heuer")
if not hit:
    # scroll list a bit inside museum (not off app)
    adb("shell", "input", "swipe", "720", "2200", "720", "1200", "350")
    time.sleep(1)
    assert_hhh("museum scroll")
    xml = dump()
    hit = find(xml, "Speedmaster", "Omega", "Carrera", "TAG Heuer", "Tissot")
if not hit:
    raise SystemExit(f"piece not found. texts={texts(xml)[:30]}")
tap(hit, 2.2, "open piece")

xml = dump()
print("detail sample:", texts(xml)[:25])
hit = find(xml, "Swap meet", "Swap Meet")
if not hit:
    adb("shell", "input", "swipe", "720", "2200", "720", "1400", "300")
    time.sleep(0.9)
    assert_hhh("detail scroll")
    xml = dump()
    hit = find(xml, "Swap meet", "Swap Meet")
if not hit:
    raise SystemExit(f"Swap meet missing. texts={texts(xml)[:40]}")
tap(hit, 2.5, "Swap meet")

xml = dump()
t = texts(xml)
joined = " ".join(t)
print("share screen:", t[:40])
pin = re.search(r"\b(\d{4})\b", joined)
print("PIN?", pin.group(1) if pin else None)
# Must still be HHH before any screencap
assert_hhh("before screencap")
adb("shell", "screencap", "-p", "/sdcard/hhh-shot.png")
dest = ST / "27b-share-nearby-active.CANDIDATE.png"
adb("pull", "/sdcard/hhh-shot.png", str(dest))
(ST / "27b-share-nearby-active.CANDIDATE_texts.txt").write_text("\n".join(t), encoding="utf-8")
assert_hhh("after screencap")
print("STAGED", dest.name, dest.stat().st_size, "— verify before promote")
