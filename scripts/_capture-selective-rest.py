#!/usr/bin/env python3
"""Capture Photo Coach, Print Export, LAN Report, Watch Passport — ASCII-safe logs."""
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


def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)


def focus_line():
    return next((l for l in adb("shell", "dumpsys", "window").stdout.splitlines() if "mCurrentFocus" in l), "")


def ensure_hhh(step=""):
    if PKG not in focus_line():
        adb("shell", "am", "start", "-n", f"{PKG}/.MainActivity")
        time.sleep(3)
    if PKG not in focus_line():
        raise SystemExit(f"no HHH {step}: {focus_line()}")


def dump():
    ensure_hhh("dump")
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    return UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""


def texts(xml):
    return [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]


def asc(xs):
    return [x.encode("ascii", "replace").decode("ascii") for x in xs]


def find(xml, *labels, min_y=100, max_y=2700):
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
        score = -abs(cy - 1500) + (r - l) // 10
        if best is None or score > best[2]:
            best = (cx, cy, score, text or desc)
    return best


def find_tab(name):
    xml = dump()
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
    # fallback coords
    return {"Home": (180, 2863), "My Museum": (540, 2863), "Tools": (900, 2863), "Settings": (1260, 2863)}[name] + (0, name)


def tap(hit, wait=1.7, step="tap"):
    print(step, hit[0], hit[1])
    adb("shell", "input", "tap", str(hit[0]), str(hit[1]))
    time.sleep(wait)
    ensure_hhh(step)


def go_tools():
    ensure_hhh()
    tap(find_tab("Tools"), 2.0, "Tools")


def scroll_find(labels, max_swipes=12):
    for i in range(max_swipes):
        hit = find(dump(), *labels)
        if hit:
            return hit
        print("scroll", i + 1, labels[0])
        adb("shell", "input", "swipe", "720", "2300", "720", "900", "350")
        time.sleep(0.6)
    return None


def shot(name):
    ensure_hhh("shot")
    adb("shell", "screencap", "-p", "/sdcard/hhh-shot.png")
    dest = ST / f"{name}.CANDIDATE.png"
    adb("pull", "/sdcard/hhh-shot.png", str(dest))
    t = texts(dump())
    (ST / f"{name}.CANDIDATE_texts.txt").write_text("\n".join(t[:100]), encoding="utf-8")
    print("STAGED", name, dest.stat().st_size, asc(t[:12]))
    return t


def soft_back_to_tools():
    adb("shell", "input", "keyevent", "KEYCODE_BACK")
    time.sleep(0.9)
    if PKG not in focus_line():
        ensure_hhh("recover")
    go_tools()


adb("shell", "cmd", "statusbar", "collapse")
adb("shell", "am", "start", "-n", f"{PKG}/.MainActivity")
time.sleep(3)
go_tools()

jobs = [
    ("31-photo-coach", ["Photo Coach"], ["Photo", "Coach", "shot", "Dial", "checklist"]),
    ("33-print-export", ["Print & Export List", "Print & Export"], ["Print", "Export", "PDF"]),
    ("34-lan-report", ["Museum Report"], ["Museum Report", "Report", "TV", "HTML", "Start"]),
]

for name, labels, expect in jobs:
    print("===", name)
    go_tools()
    for _ in range(2):
        adb("shell", "input", "swipe", "720", "900", "720", "2300", "280")
        time.sleep(0.3)
    hit = scroll_find(labels)
    if not hit:
        print("NOT FOUND")
        continue
    tap(hit, 2.4, labels[0])
    joined = " ".join(texts(dump()))
    if "Something went wrong" in joined or "Unlock Pro" in joined:
        print("bad state", asc(texts(dump())[:8]))
        soft_back_to_tools()
        continue
    t = shot(name)
    print("verify", "OK" if any(e.lower() in " ".join(t).lower() for e in expect) else "WEAK")
    soft_back_to_tools()

# Watch Passport via piece More actions (dots)
print("=== 32-digital-id-card")
tap(find_tab("My Museum"), 2.0, "Museum")
hit = find(dump(), "Speedmaster", "Omega", "Rolex")
if not hit:
    adb("shell", "input", "swipe", "720", "2200", "720", "1200", "350")
    time.sleep(0.7)
    hit = find(dump(), "Speedmaster", "Omega", "Rolex")
if not hit:
    print("no piece")
else:
    tap(hit, 2.2, "piece")
    # header right dots — often top-right ~1320, 220
    xml = dump()
    hit = find(xml, "More actions", "more actions", "More")
    if not hit:
        # tap typical header overflow
        print("tap header dots fallback")
        adb("shell", "input", "tap", "1320", "220")
        time.sleep(1.2)
    else:
        tap(hit, 1.2, "more actions")
    hit = find(dump(), "Watch Passport", "Passport")
    if hit:
        tap(hit, 2.5, "Watch Passport")
        joined = " ".join(texts(dump()))
        if "Unlock Pro" not in joined and "Something went wrong" not in joined:
            shot("32-digital-id-card")
        else:
            print("passport blocked", asc(texts(dump())[:10]))
    else:
        print("passport menu item missing", asc(texts(dump())[:20]))

print("done")
