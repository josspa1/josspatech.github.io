#!/usr/bin/env python3
"""Scroll Settings from top; find App Lock / Notifications; capture verified candidates."""
from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
S = "R5CXC2K4Z8F"
STAGING = Path(__file__).resolve().parents[1] / "assets/screenshots/hhh/_capture_verify"
UI = STAGING / "_ui.xml"


def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)


def dump() -> str:
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    return UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""


def texts(xml: str) -> list[str]:
    return [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip() and not t.startswith("&#")]


def find_bounds(xml: str, *labels: str, refuse=("whisker",)):
    best = None
    for node in re.findall(r"<node[^>]+>", xml):
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        hay = f"{text} {desc}"
        if any(r in hay.lower() for r in refuse):
            continue
        if not any(lab.lower() in hay.lower() for lab in labels):
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        cx, cy = (l + r) // 2, (t + b) // 2
        if cy < 200 or cy > 2800:
            continue
        score = -abs(cy - 1500)
        if best is None or score > best[2]:
            best = (cx, cy, score, text or desc)
    return best


def shot(name: str):
    STAGING.mkdir(parents=True, exist_ok=True)
    adb("shell", "screencap", "-p", "/sdcard/hhh-shot.png")
    dest = STAGING / name
    adb("pull", "/sdcard/hhh-shot.png", str(dest))
    print(f"STAGED {name} ({dest.stat().st_size if dest.exists() else 0})")
    (STAGING / name.replace(".png", "_texts.txt")).write_text("\n".join(texts(dump())[:60]), encoding="utf-8")


def main():
    adb("shell", "am", "force-stop", "dev.mobile.maestro")
    # Settings tab
    adb("shell", "input", "tap", "1260", "2920")
    time.sleep(1.5)
    # ensure top
    for _ in range(10):
        adb("shell", "input", "swipe", "720", "900", "720", "2300", "280")
        time.sleep(0.35)
    time.sleep(0.8)

    targets = [
        ("App Lock", ("App Lock", "Security"), "10e-settings-security.CANDIDATE.png"),
        ("Notifications", ("Notifications",), "10f-settings-notifications.CANDIDATE.png"),
        ("Theme detail", ("Theme",), "10c-settings-theme-detail.CANDIDATE.png"),
    ]

    for label, aliases, out in targets:
        print(f"\n=== looking for {label} ===")
        # back to settings top between captures
        adb("shell", "input", "tap", "1260", "2920")
        time.sleep(1)
        for _ in range(8):
            adb("shell", "input", "swipe", "720", "900", "720", "2300", "280")
            time.sleep(0.3)
        found = False
        for swipe_i in range(10):
            xml = dump()
            print(f" swipe {swipe_i}: {[t for t in texts(xml) if any(a.lower() in t.lower() for a in aliases + ('Theme','Language','Accessibility','Offline','Voice','Share'))]}")
            hit = find_bounds(xml, *aliases)
            if hit:
                print(f" tap {hit[3]!r} @ {hit[0]},{hit[1]}")
                adb("shell", "input", "tap", str(hit[0]), str(hit[1]))
                time.sleep(1.8)
                # verify we're not on Whisker / wrong app
                now = " ".join(texts(dump()))
                if "Whisker" in now and label == "Notifications":
                    print("REFUSE Whisker — abort notifications")
                    adb("shell", "input", "keyevent", "4")
                    time.sleep(0.8)
                    break
                shot(out)
                adb("shell", "input", "keyevent", "4")
                time.sleep(0.9)
                found = True
                break
            adb("shell", "input", "swipe", "720", "2200", "720", "1200", "320")
            time.sleep(0.7)
        if not found:
            print(f"MISS {label}")


if __name__ == "__main__":
    main()
