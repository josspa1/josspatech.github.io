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
# Pixel_8 AVD @ 1080x2400
PKG = "com.josspatech.handyhorology"
W, H = 1080, 2400
TAB_Y = H - 32  # tab bar center
HHH_SRC = Path(os.environ.get("HHH_SRC", r"C:\Users\jossp\Documents\MobileApps\HHH\SourceCode"))
MAESTRO = HHH_SRC / ".tools" / "maestro" / "maestro" / "bin" / "maestro.bat"
SKIP_BOOT = os.environ.get("HHH_CAPTURE_SKIP_BOOT") == "1"


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
    adb("shell", "input", "swipe", str(W // 2), str(int(H * 0.82)), str(W // 2), str(int(H * 0.35)), "400")
    time.sleep(0.7)


def tab(name: str) -> None:
    if tap_label(name):
        return
    tabs = {"Home": W // 10, "My Pieces": W * 3 // 10, "Tools": W // 2, "Collectors": W * 7 // 10, "Settings": W * 9 // 10}
    x = tabs.get(name, W // 10)
    tap(x, TAB_Y)


def ui(retries: int = 4) -> str:
    for attempt in range(retries):
        adb("shell", "rm", "-f", "/sdcard/ui.xml")
        time.sleep(0.4)
        proc = subprocess.run(
            [ADB, "-s", SERIAL, "shell", "uiautomator", "dump", "/sdcard/ui.xml"],
            capture_output=True,
            text=True,
        )
        if "could not get idle state" in (proc.stdout + proc.stderr):
            time.sleep(2 + attempt)
            continue
        adb("pull", "/sdcard/ui.xml", str(UI))
        if UI.exists() and UI.stat().st_size > 500:
            return UI.read_text(encoding="utf-8", errors="ignore")
        time.sleep(1)
    # Stale dump fallback — return last pull if any
    return UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""


def on_home() -> bool:
    xml = ui()
    if "Welcome to Handy" in xml or "How do you want to start" in xml:
        return False
    return bool(re.search(r"COMMAND CENTER|Your horology companion|Enjoying HHH|Load Demo Collection", xml))


def tap_label(label: str) -> bool:
    esc = re.escape(label)
    xml = ui()
    for node in re.findall(r"<node[^>]+>", xml):
        if not re.search(rf'text="{esc}"|content-desc="{esc}"', node):
            if label not in node:
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


def has(*patterns: str) -> bool:
    xml = ui()
    return any(re.search(p, xml, re.I) for p in patterns)


def dismiss_system_dialogs() -> bool:
    """Dismiss Android permission / debugger overlays."""
    acted = False
    if has(r"send you notifications|POST_NOTIFICATIONS"):
        acted = (
            tap_label("Don't allow")
            or tap_label("Don\u2019t allow")
            or tap(540, 1470)
        )
    if has(r"Open debugger"):
        tap(W - 24, H - 48, 0.8)
        acted = True
    return acted


def grant_perms() -> None:
    for perm in (
        "android.permission.READ_MEDIA_IMAGES",
        "android.permission.READ_EXTERNAL_STORAGE",
        "android.permission.POST_NOTIFICATIONS",
    ):
        adb("shell", "pm", "grant", PKG, perm)


ADB = os.environ.get(
    "ADB",
    str(Path(os.environ.get("LOCALAPPDATA", "")) / "Android/Sdk/platform-tools/adb.exe"),
)


def prepare_app() -> None:
    """Fresh install + sample museum via Maestro (reliable on 1080x2400)."""
    env = {**os.environ, "MAESTRO_ALLOW_CAPTURE": "1", "MAESTRO_ALLOW_EMULATOR": "1", "ANDROID_SERIAL": SERIAL}
    adb("shell", "pm", "clear", PKG)
    time.sleep(2)
    grant_perms()
    if not MAESTRO.exists():
        raise RuntimeError(f"Maestro not found: {MAESTRO}")
    flow = HHH_SRC / ".maestro" / "load-demo-collection.yaml"
    print(f"Maestro prep: {flow.name}")
    subprocess.run([str(MAESTRO), "test", str(flow)], cwd=str(HHH_SRC), env=env, check=True)
    tab("Home")
    time.sleep(3)


def ensure_home() -> None:
    tab("Home")
    time.sleep(2)
    dismiss_system_dialogs()


def capture_all() -> None:
    if not SKIP_BOOT:
        prepare_app()
    else:
        tab("Home")
        time.sleep(2)
    ensure_home()
    shot("01-home-command-center")

    # My Museum / My Pieces
    tab("My Pieces")
    time.sleep(4)
    shot("02-museum-collection")
    # First piece in grid (sample collection)
    tap(W // 3, int(H * 0.32))
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

    tab("Home")
    time.sleep(3)
    # Hunt / eBay Grail Radar — quick command on home
    tap_label("Hunt") or tap(int(W * 0.13), int(H * 0.24))
    time.sleep(4)
    shot("05-ebay-grail-radar")

    ensure_home()
    # Clock Repair Help
    tap_label("Fix clock") or tap(int(W * 0.38), int(H * 0.24))
    time.sleep(4)
    if not has(r"What.s wrong|Won.t chime|symptom|Clock Repair"):
        tab("Tools")
        time.sleep(2)
        for _ in range(8):
            swipe_up()
        tap_label("Clock Repair Help")
        time.sleep(3)
    if has(r"What.s wrong|Won.t chime|symptom"):
        shot("06a-clock-repair-symptoms")
    tap_label("Won't chime") or tap_label("Won\u2019t chime") or tap(W // 2, int(H * 0.4))
    time.sleep(10)
    shot("06-clockworks-parts")

    # Identify
    for _ in range(4):
        back()
    ensure_home()
    tab("Tools")
    time.sleep(2)
    for _ in range(10):
        swipe_up()
    tap_label("Identify")
    time.sleep(3)
    if has(r"Choose Photo|Take Photo|Camera|Identify this"):
        shot("07a-identify-camera")
    if has(r"Choose Photo"):
        tap_label("Choose Photo") or tap(W // 2, int(H * 0.72))
        time.sleep(2)
        tap(W // 3, int(H * 0.32))
        time.sleep(2)
    tap_label("Identify this timepiece") or tap(W // 2, H - 120, 1.0)
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
    tab("Tools")
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
    tab("Settings")
    time.sleep(3)
    shot("10-settings")
    for _ in range(5):
        swipe_up()
    if has(r"Backup|Export|Restore"):
        tap_label("Backup & Restore") or tap_label("Backup") or tap_label("Backup and Restore")
        time.sleep(3)
        shot("11-backup-restore")
    tap_label("Subscription") or tap_label("Pro") or tap_label("Upgrade")
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
