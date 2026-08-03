#!/usr/bin/env python3
"""Recapture Share Nearby active QR+PIN — dismiss top popups first."""
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
MANUAL = Path(__file__).resolve().parents[1] / "assets/screenshots/hhh/manual"
BAD = ("dialer", "contacts", "whisker", "maestro", "dialtacts")


def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)


def focus_line() -> str:
    return next((l for l in adb("shell", "dumpsys", "window").stdout.splitlines() if "mCurrentFocus" in l), "")


def assert_hhh(step: str) -> None:
    line = focus_line()
    low = line.lower()
    if PKG not in line or any(b in low for b in BAD):
        raise SystemExit(f"ABORT {step}: {line.strip()}")


def dump() -> str:
    assert_hhh("dump")
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    return UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""


def texts(xml: str):
    return [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip() and not t.startswith("&#")]


def find(xml, *labels, min_y=150, max_y=2700):
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


def find_tab(xml, name):
    for node in re.findall(r"<node[^>]+>", xml):
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        if name not in desc:
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        if (t + b) // 2 < 2700:
            continue
        return ((l + r) // 2, (t + b) // 2, 0, desc)
    return None


def tap(hit, wait=1.6, step="tap"):
    if hit is None:
        raise SystemExit(f"missing {step}")
    print(f"{step}: {hit[3]!r} @ {hit[0]},{hit[1]}")
    adb("shell", "input", "tap", str(hit[0]), str(hit[1]))
    time.sleep(wait)
    assert_hhh(step)


def dismiss_top_junk():
    """Collapse shade, dismiss Android/RN alerts/toasts/permission dialogs."""
    adb("shell", "cmd", "statusbar", "collapse")
    time.sleep(0.3)
    xml = dump()
    t = texts(xml)
    print("pre-clean texts:", [x.encode("ascii", "replace").decode("ascii") for x in t[:25]])
    for label in ("While using the app", "Allow", "Only this time", "OK", "Got it"):
        hit = None
        for node in re.findall(r"<node[^>]+>", xml):
            text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
            if text != label:
                continue
            m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
            if not m:
                continue
            l, top, r, b = map(int, m.groups())
            cy = (top + b) // 2
            if cy < 100 or cy > 2200:
                continue
            hit = ((l + r) // 2, cy, 0, text)
            break
        if hit:
            print(f"dismissing dialog via {label}")
            tap(hit, 1.0, f"dismiss {label}")
            xml = dump()
            break
    line = focus_line()
    if "permissioncontroller" in line.lower() or "packageinstaller" in line.lower():
        raise SystemExit(f"stuck on system dialog: {line}")
    return dump()


# Clean start
adb("shell", "cmd", "statusbar", "collapse")
adb("shell", "am", "force-stop", PKG)
time.sleep(0.6)
adb("shell", "am", "start", "-n", f"{PKG}/.MainActivity")
time.sleep(3.5)
assert_hhh("launch")
dismiss_top_junk()

xml = dump()
tap(find_tab(xml, "My Museum"), 2.0, "My Museum")
xml = dump()
hit = find(xml, "Speedmaster", "Omega")
if not hit:
    adb("shell", "input", "swipe", "720", "2200", "720", "1200", "350")
    time.sleep(0.8)
    hit = find(dump(), "Speedmaster", "Omega")
tap(hit, 2.2, "open piece")

xml = dump()
hit = find(xml, "Swap meet")
if not hit:
    adb("shell", "input", "swipe", "720", "2200", "720", "1400", "300")
    time.sleep(0.8)
    hit = find(dump(), "Swap meet")
tap(hit, 2.8, "Swap meet")

# Wait for PIN/QR to settle; dismiss any top popup that appears on entry
time.sleep(1.5)
for i in range(4):
    dismiss_top_junk()
    xml = dump()
    joined = " ".join(texts(xml))
    print(f"settle #{i}:", [x.encode("ascii", "replace").decode("ascii") for x in texts(xml)[:30]])
    # Detect dialog-ish strings near top
    dialogish = any(
        s in joined
        for s in (
            "Allow",
            "Bluetooth",
            "Nearby devices",
            "permission",
            "While using",
            "Turn on",
            "Location",
        )
    )
    # Bluetooth instructional copy is OK; system permission is not
    if "Share PIN" in joined and re.search(r"\b\d{4}\b", joined):
        # If permission dialog packages not focused and no Allow button in tree, good
        has_allow_btn = False
        for node in re.findall(r"<node[^>]+>", xml):
            text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
            if text in ("Allow", "While using the app", "Only this time"):
                has_allow_btn = True
                break
        if not has_allow_btn:
            break
        print("permission still up — dismissing")
        time.sleep(0.5)
    else:
        time.sleep(0.8)

xml = dump()
joined = " ".join(texts(xml))
if "Share PIN" not in joined or "Pick a piece" in joined:
    raise SystemExit(f"not active share screen: {texts(xml)[:40]}")
if not re.search(r"\b\d{4}\b", joined):
    raise SystemExit("no PIN")

# Extra settle so transient toasts clear
time.sleep(2.0)
adb("shell", "cmd", "statusbar", "collapse")
assert_hhh("pre-shot")
line = focus_line()
print("focus:", line.strip())

adb("shell", "screencap", "-p", "/sdcard/hhh-shot.png")
cand = ST / "27b-share-nearby-active.CANDIDATE.png"
adb("pull", "/sdcard/hhh-shot.png", str(cand))
xml = dump()
t = texts(xml)
(ST / "27b-share-nearby-active.CANDIDATE_texts.txt").write_text("\n".join(t), encoding="utf-8")
print("STAGED", cand.name, cand.stat().st_size)
print("texts:", [x.encode("ascii", "replace").decode("ascii") for x in t[:35]])

# Hard fail if dialog remnants
joined = " ".join(t)
for bad in ("While using the app", "Only this time", "Allow Handy", "Nearby devices"):
    if bad in joined:
        raise SystemExit(f"popup remnant in tree: {bad}")
print("tree looks clean — verify image top before promote")
