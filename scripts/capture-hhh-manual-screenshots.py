#!/usr/bin/env python3
"""Capture HHH user-manual PNGs from Android emulator (Pixel_8 @ 1440x3120).

Outputs to assets/screenshots/hhh/manual/ for build-hhh-user-manual-slides.py.
Requires: HHH debug/release build installed, emulator-5554 online.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "screenshots" / "hhh" / "manual"
UI = ROOT / "assets" / "screenshots" / "hhh" / "_ui-dump.xml"
SERIAL = os.environ.get("ANDROID_SERIAL", "emulator-5554")
# Pixel_8 AVD @ 1080x2400 (not 1440x3120 — scale Maestro coords ×0.75)
PKG = "com.josspatech.handyhorology"
ADB = os.environ.get(
    "ADB",
    str(Path(os.environ.get("LOCALAPPDATA", "")) / "Android/Sdk/platform-tools/adb.exe"),
)


def adb(*args: str) -> None:
    subprocess.run([ADB, "-s", SERIAL, *args], check=False, capture_output=True)


def tap(x: int, y: int, wait: float = 1.8) -> None:
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(wait)


def back(n: int = 1) -> None:
    for _ in range(n):
        adb("shell", "input", "keyevent", "4")
        time.sleep(1.2)


def swipe_up() -> None:
    adb("shell", "input", "swipe", "720", "2300", "720", "1100", "400")
    time.sleep(0.7)


def ui() -> str:
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    return UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""


def has(*patterns: str) -> bool:
    xml = ui()
    return any(re.search(p, xml, re.I) for p in patterns)


def tap_label(label: str) -> bool:
    esc = re.escape(label)
    xml = ui()
    for node in re.findall(r"<node[^>]+>", xml):
        if not re.search(rf'text="{esc}"|content-desc="{esc}"', node):
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        cx = (int(m.group(1)) + int(m.group(3))) // 2
        cy = (int(m.group(2)) + int(m.group(4))) // 2
        print(f"  tap {label!r} @ {cx},{cy}")
        tap(cx, cy)
        return True
    return False


def shot(name: str) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    remote = f"/sdcard/{name}.png"
    local = OUT / f"{name}.png"
    time.sleep(1.5)
    adb("shell", "screencap", "-p", remote)
    adb("pull", remote, str(local))
    size = local.stat().st_size if local.exists() else 0
    print(f"SHOT {name} {size}")
    return size


def grant_perms() -> None:
    for perm in (
        "android.permission.READ_MEDIA_IMAGES",
        "android.permission.READ_EXTERNAL_STORAGE",
        "android.permission.POST_NOTIFICATIONS",
    ):
        adb("shell", "pm", "grant", PKG, perm)


def launch_fresh() -> None:
    grant_perms()
    adb("shell", "pm", "clear", PKG)
    time.sleep(2)
    adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
    print("boot 20s")
    time.sleep(20)
    if has(r"Don't allow"):
        tap_label("Don't allow") or tap(720, 1750)
    if has(r"Open debugger"):
        tap(1356, 2929, 0.8)


def onboarding_sample() -> None:
    """Load Harold's sample collection for richer museum shots."""
    for _ in range(8):
        if has(r"COMMAND CENTER|Your horology companion|Good morning|Good evening"):
            return
        if has(r"Explore with sample collection"):
            tap_label("Explore with sample collection") or tap(720, 2098)
            time.sleep(3)
            if has(r"Get Started"):
                tap_label("Get Started") or tap(841, 2926)
                time.sleep(8)
                continue
        if has(r"How do you want to start"):
            tap_label("Explore with sample collection") or tap(720, 1750)
            time.sleep(3)
            continue
        if has(r"Continue|Welcome to Handy|Get Started"):
            tap_label("Continue") or tap_label("Get Started") or tap(841, 2926)
            time.sleep(3)
            continue
        if has(r"Skip"):
            tap_label("Skip") or tap(163, 2926)
            time.sleep(4)
            continue
        time.sleep(2)
    if not has(r"COMMAND CENTER|Your horology companion|Good morning|Good evening"):
        raise RuntimeError("Onboarding did not reach home")


def ensure_home() -> None:
    for _ in range(4):
        if has(r"COMMAND CENTER|Your horology companion|Good morning|Good evening"):
            tap(144, 3026)  # Home tab
            time.sleep(2)
            return
        back()
    raise RuntimeError("Could not reach home")


def capture_all() -> None:
    launch_fresh()
    onboarding_sample()
    ensure_home()
    shot("01-home-command-center")

    # My Museum / My Pieces
    tap(432, 3026)
    time.sleep(4)
    shot("02-museum-collection")
    # First piece in grid (sample collection)
    tap(360, 700)
    time.sleep(3)
    if has(r"Provenance|Service|Estimated|Purchase"):
        shot("03-piece-detail")
    else:
        back()
        shot("03-piece-detail")  # reuse list if detail fails

    # Wish list segment
    tap_label("Wish List") or tap(900, 450)
    time.sleep(2)
    shot("04-wishlist-grails")

    ensure_home()
    # Hunt / eBay Grail Radar
    tap_label("Hunt") or tap(250, 686)
    time.sleep(4)
    shot("05-ebay-grail-radar")

    ensure_home()
    # Clock Repair Help
    tap_label("Fix clock") or tap(520, 686)
    time.sleep(4)
    if not has(r"What's wrong|Won"):
        ensure_home()
        tap(720, 3026)  # Tools tab
        time.sleep(2)
        for _ in range(8):
            swipe_up()
        tap_label("Clock Repair Help")
        time.sleep(3)
    tap_label("Won't chime") or tap(720, 950)
    time.sleep(10)
    shot("06-clockworks-parts")

    # Identify
    for _ in range(4):
        back()
    ensure_home()
    tap(720, 3026)
    time.sleep(2)
    for _ in range(10):
        swipe_up()
    tap_label("Identify")
    time.sleep(3)
    if has(r"Choose Photo"):
        tap_label("Choose Photo") or tap(720, 2600)
        time.sleep(2)
        tap(360, 700)
        time.sleep(2)
    tap_label("Identify this timepiece") or tap(720, 2800, 1.0)
    print("AI wait up to 150s")
    for i in range(75):
        if has(r"Top match|confident|Save to collection|Looks right|%"):
            print(f"  identify ready @{i*2}s")
            break
        time.sleep(2)
    shot("07-identify-results")

    # Tools overview
    for _ in range(3):
        back()
    tap(720, 3026)
    time.sleep(2)
    shot("08-tools-hub")

    # Web Companion
    for _ in range(6):
        swipe_up()
    tap_label("Web Companion")
    time.sleep(4)
    shot("09-web-companion")

    # Settings + trial
    for _ in range(4):
        back()
    tap(1296, 3026)
    time.sleep(3)
    shot("10-settings")
    for _ in range(5):
        swipe_up()
    if has(r"Backup|Export"):
        tap_label("Backup") or tap_label("Backup & Restore")
        time.sleep(3)
        shot("11-backup-restore")
    tap_label("Subscription") or tap_label("Pro")
    time.sleep(2)
    shot("12-trial-subscription")

    # Publish hero copies for marketing parity
    hero = ROOT / "assets" / "screenshots" / "hhh"
    hero.mkdir(parents=True, exist_ok=True)
    mapping = {
        "02-museum-collection.png": "01-home-museum.png",
        "07-identify-results.png": "02-ai-identify.png",
        "06-clockworks-parts.png": "03-clockworks-wizard.png",
        "04-wishlist-grails.png": "08-wishlist-grails.png",
    }
    for src_name, dest_name in mapping.items():
        src = OUT / src_name
        if src.exists():
            (hero / dest_name).write_bytes(src.read_bytes())
            print(f"hero copy {dest_name}")


def main() -> int:
    if not Path(ADB).exists():
        print(f"adb not found: {ADB}", file=sys.stderr)
        return 1
    try:
        capture_all()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Done — outputs in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
