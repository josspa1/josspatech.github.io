#!/usr/bin/env python3
"""Enable Simulate Premium if available, then capture remaining selective tools."""
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
ST.mkdir(parents=True, exist_ok=True)


def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)


def focus_line():
    return next((l for l in adb("shell", "dumpsys", "window").stdout.splitlines() if "mCurrentFocus" in l), "")


def ensure_hhh(step=""):
    line = focus_line()
    if PKG not in line or "launcher" in line.lower() or "dialer" in line.lower():
        print(f"relaunch ({step}): {line.strip()}")
        adb("shell", "am", "start", "-n", f"{PKG}/.MainActivity")
        time.sleep(3.0)
    if PKG not in focus_line():
        raise SystemExit(f"cannot focus HHH: {focus_line()}")


def dump():
    ensure_hhh("dump")
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    return UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""


def texts(xml):
    return [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]


def find(xml, *labels, min_y=120, max_y=2700):
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
    if not hit:
        raise SystemExit(f"missing {step}")
    print(f"{step}: {(hit[3] or '')[:50]!r} @ {hit[0]},{hit[1]}")
    adb("shell", "input", "tap", str(hit[0]), str(hit[1]))
    time.sleep(wait)
    ensure_hhh(step)


def go_tools():
    ensure_hhh("tools")
    tap(find_tab(dump(), "Tools") or (900, 2863, 0, "Tools"), 2.0, "Tools")


def scroll_find(labels, max_swipes=12):
    for i in range(max_swipes):
        xml = dump()
        hit = find(xml, *labels)
        if hit:
            return hit
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
    print(f"STAGED {name} size={dest.stat().st_size} texts={t[:15]}")
    return t


def soft_back():
    """Stay in HHH — never KEYCODE_BACK from root."""
    adb("shell", "input", "keyevent", "KEYCODE_BACK")
    time.sleep(0.8)
    if PKG not in focus_line():
        ensure_hhh("soft_back recover")
        go_tools()


adb("shell", "cmd", "statusbar", "collapse")
adb("shell", "am", "start", "-n", f"{PKG}/.MainActivity")
time.sleep(3)
ensure_hhh("launch")

# Simulate Premium from Settings if present
tap(find_tab(dump(), "Settings") or (1260, 2863, 0, "Settings"), 2.0, "Settings")
for _ in range(6):
    hit = find(dump(), "Simulate Premium", "Simulate premium")
    if hit:
        tap(hit, 1.5, "Simulate Premium")
        break
    adb("shell", "input", "swipe", "720", "2300", "720", "900", "350")
    time.sleep(0.55)
else:
    print("Simulate Premium not found — continuing")

go_tools()

# Remaining shots (ebay already OK)
remaining = [
    ("29-trade-analyzer", ["Is This Trade Fair?", "Is This Trade Fair"], ["Trade", "Fair", "Your", "cash", "piece"]),
    ("30-ai-chat", ["Horology Coach"], ["Coach", "Horology", "Ask", "Chat", "message", "Pro"]),
    ("31-photo-coach", ["Photo Coach"], ["Photo", "Coach", "shot", "Dial", "checklist", "Studio"]),
    ("33-print-export", ["Print & Export List", "Print & Export"], ["Print", "Export", "PDF", "list"]),
    ("34-lan-report", ["Museum Report"], ["Museum Report", "Report", "TV", "HTML", "Start", "screen"]),
]

for name, labels, expect in remaining:
    print(f"\n=== {name} ===")
    go_tools()
    for _ in range(2):
        adb("shell", "input", "swipe", "720", "900", "720", "2300", "280")
        time.sleep(0.35)
    hit = scroll_find(labels)
    if not hit:
        print("NOT FOUND", labels)
        continue
    tap(hit, 2.5, labels[0])
    joined = " ".join(texts(dump()))
    if "Something went wrong" in joined or "unexpected error" in joined.lower():
        print("error screen — Try again then skip if still broken")
        hit = find(dump(), "Try again")
        if hit:
            tap(hit, 2.0, "Try again")
            joined = " ".join(texts(dump()))
        if "Something went wrong" in joined:
            soft_back()
            continue
    if "Unlock Pro" in joined or "$74.99" in joined:
        print("paywall — back")
        soft_back()
        continue
    t = shot(name)
    ok = any(e.lower() in " ".join(t).lower() for e in expect)
    print("OK" if ok else "WEAK")
    soft_back()

# Digital ID from piece
print("\n=== 32-digital-id-card ===")
tap(find_tab(dump(), "My Museum") or (540, 2863, 0, "Museum"), 2.0, "Museum")
hit = find(dump(), "Speedmaster", "Omega", "Rolex")
if not hit:
    adb("shell", "input", "swipe", "720", "2200", "720", "1200", "350")
    time.sleep(0.7)
    hit = find(dump(), "Speedmaster", "Omega", "Rolex", "Seiko")
if hit:
    tap(hit, 2.2, "piece")
    opened = False
    for _ in range(4):
        xml = dump()
        for lab in ("Digital ID", "Watch Passport", "Passport", "ID Card", "Proof"):
            hit = find(xml, lab)
            if hit:
                tap(hit, 2.5, lab)
                opened = True
                break
        if opened:
            break
        adb("shell", "input", "swipe", "720", "2200", "720", "1100", "350")
        time.sleep(0.6)
    if not opened:
        # overflow / more on piece
        hit = find(dump(), "More")
        if hit:
            tap(hit, 1.2, "More")
            hit = find(dump(), "Digital ID", "Passport", "Watch Passport")
            if hit:
                tap(hit, 2.5, hit[3])
                opened = True
    joined = " ".join(texts(dump()))
    if "Unlock Pro" in joined:
        soft_back()
    else:
        shot("32-digital-id-card")
else:
    print("no piece")

print("\nDone candidates:")
for p in sorted(ST.glob("2*-*.CANDIDATE.png")) + sorted(ST.glob("3*-*.CANDIDATE.png")):
    print(p.name, p.stat().st_size)
