#!/usr/bin/env python3
"""Demand Rolodex → Send to a dealer → PIN+QR. Focus-guarded."""
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
    line = next((l for l in out.splitlines() if "mcurrentfocus" in l), "")
    if PKG not in line:
        return False
    return not any(b in line for b in BAD)


def assert_hhh(step: str) -> None:
    if not focus_ok():
        line = next((l for l in adb("shell", "dumpsys", "window").stdout.splitlines() if "mCurrentFocus" in l), "?")
        raise SystemExit(f"ABORT {step}: {line.strip()}")


def dump() -> str:
    assert_hhh("dump")
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    assert_hhh("after dump")
    return UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""


def texts(xml: str):
    return [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip() and not t.startswith("&#")]


def find(xml, *labels, min_y=150, max_y=2750):
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
        score = -abs(cy - 1400)
        if best is None or score > best[2]:
            best = (cx, cy, score, text or desc)
    return best


def find_tab(xml, name):
    for node in re.findall(r"<node[^>]+>", xml):
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        if name not in desc:
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        cy = (t + b) // 2
        if cy < 2700:
            continue
        return ((l + r) // 2, cy, 0, desc)
    return None


def tap(hit, wait=1.8, step="tap"):
    print(f"{step}: {hit[3]!r} @ {hit[0]},{hit[1]}")
    adb("shell", "input", "tap", str(hit[0]), str(hit[1]))
    time.sleep(wait)
    assert_hhh(step)


def shot(name):
    assert_hhh("screencap")
    adb("shell", "screencap", "-p", "/sdcard/hhh-shot.png")
    dest = ST / name
    adb("pull", "/sdcard/hhh-shot.png", str(dest))
    (ST / name.replace(".png", "_texts.txt")).write_text("\n".join(texts(dump())[:80]), encoding="utf-8")
    assert_hhh("after shot")
    print(f"STAGED {name} ({dest.stat().st_size})")


adb("shell", "am", "force-stop", "com.samsung.android.dialer")
adb("shell", "am", "start", "-n", f"{PKG}/.MainActivity")
time.sleep(3)
assert_hhh("launch")

xml = dump()
tap(find_tab(xml, "Tools"), 1.8, "Tools")
xml = dump()
# search
hit = find(xml, "Find a tool")
if hit:
    tap(hit, 0.8, "search")
    adb("shell", "input", "text", "Demand")
    time.sleep(1.2)
    assert_hhh("typed Demand")
xml = dump()
hit = find(xml, "Demand Rolodex", "Demand")
if not hit:
    raise SystemExit("Demand not found")
tap(hit, 2.0, "Demand")

xml = dump()
print("demand:", texts(xml)[:25])
shot("23-demand-rolodex-board.CANDIDATE.png")

hit = find(xml, "Send to a dealer")
if not hit:
    raise SystemExit("Send to a dealer missing")
tap(hit, 2.2, "Send")

xml = dump()
print("send form:", texts(xml)[:35])
shot("21-demand-rolodex-send.CANDIDATE.png")

# If there's a continue / create / show PIN path, follow it
for label in ("Send", "Show PIN", "Continue", "Create card", "Share PIN", "Next"):
    hit = find(dump(), label)
    if hit and label != "Send to a dealer":
        # avoid re-tapping send to dealer
        if "dealer" in (hit[3] or "").lower():
            continue
        tap(hit, 2.0, label)
        xml = dump()
        joined = " ".join(texts(xml))
        if re.search(r"\b\d{4}\b", joined) or "PIN" in joined.upper() or "QR" in joined.upper():
            print("PIN/QR screen:", texts(xml)[:40])
            shot("21b-demand-pin-qr.CANDIDATE.png")
            break
else:
    print("No PIN/QR follow-up found on send form (keeper may already be the form)")
