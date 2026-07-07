#!/usr/bin/env python3
"""Capture HHH user-manual PNGs from Android emulator (Pixel_8 @ 1080x2400).

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
PKG = "com.josspatech.handyhorology"
W, H = 1080, 2400
TAB_Y = H - 32
HHH_SRC = Path(os.environ.get("HHH_SRC", r"C:\Users\jossp\Documents\MobileApps\HHH\SourceCode"))
MAESTRO = HHH_SRC / ".tools" / "maestro" / "maestro" / "bin" / "maestro.bat"
SKIP_BOOT = os.environ.get("HHH_CAPTURE_SKIP_BOOT") == "1"
SKIP_ONBOARDING = os.environ.get("HHH_CAPTURE_SKIP_ONBOARDING") == "1"

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
    adb("shell", "input", "swipe", str(W // 2), str(int(H * 0.82)), str(W // 2), str(int(H * 0.35)), "400")
    time.sleep(0.7)


def tab(name: str) -> None:
    if tap_label(name):
        return
    tabs = {
        "Home": W // 10,
        "My Pieces": W * 3 // 10,
        "Tools": W // 2,
        "Collectors": W * 7 // 10,
        "Settings": W * 9 // 10,
    }
    tap(tabs.get(name, W // 10), TAB_Y)


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
    return UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""


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


def has(*patterns: str) -> bool:
    xml = ui()
    return any(re.search(p, xml, re.I) for p in patterns)


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


def dismiss_system_dialogs() -> bool:
    acted = False
    if has(r"send you notifications|POST_NOTIFICATIONS"):
        acted = tap_label("Don't allow") or tap_label("Don\u2019t allow") or tap(540, 1470)
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


def launch_fresh() -> None:
    adb("shell", "pm", "clear", PKG)
    time.sleep(2)
    grant_perms()
    adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
    time.sleep(4)
    dismiss_system_dialogs()


def capture_onboarding() -> None:
    """Fresh install screens before demo load."""
    if SKIP_ONBOARDING:
        print("SKIP onboarding captures")
        return
    print("=== Phase A: onboarding ===")
    launch_fresh()
    for _ in range(3):
        if has(r"Welcome to Handy|Horology Helper|Continue"):
            break
        time.sleep(2)
    shot("13-onboarding-welcome")
    tap_label("Continue") or tap(540, int(H * 0.92))
    time.sleep(2)
    tap_label("Continue") or tap(540, int(H * 0.92))
    time.sleep(2)
    tap_label("Get Started") or tap(540, int(H * 0.92))
    time.sleep(3)
    if has(r"How do you want to start"):
        shot("14-onboarding-path")


def prepare_app(*, skip_clear: bool = False) -> None:
    """Fresh install + sample museum via Maestro (fallback: Settings → Load Demo)."""
    env = {**os.environ, "MAESTRO_ALLOW_CAPTURE": "1", "MAESTRO_ALLOW_EMULATOR": "1", "ANDROID_SERIAL": SERIAL}
    if not skip_clear:
        adb("shell", "pm", "clear", PKG)
        time.sleep(2)
        grant_perms()
    adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
    time.sleep(5)
    dismiss_system_dialogs()
    if not MAESTRO.exists():
        raise RuntimeError(f"Maestro not found: {MAESTRO}")
    flow = HHH_SRC / ".maestro" / "load-demo-collection.yaml"
    print(f"Maestro prep: {flow.name}")
    result = subprocess.run([str(MAESTRO), "test", str(flow)], cwd=str(HHH_SRC), env=env, check=False)
    if result.returncode != 0:
        print("Maestro failed — manual demo load fallback")
        _manual_load_demo()
    tab("Home")
    time.sleep(3)


def _manual_load_demo() -> None:
    """Settings → Load Demo Collection when Maestro launch fails."""
    adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
    time.sleep(4)
    dismiss_system_dialogs()
    for _ in range(4):
        if has(r"COMMAND CENTER|Your horology companion|How do you want"):
            break
        tap_label("Continue") or tap(540, int(H * 0.92))
        time.sleep(2)
    if has(r"Explore with sample"):
        tap_label("Explore with sample collection") or tap(540, int(H * 0.55))
        time.sleep(3)
        tap_label("Get Started") or tap(540, int(H * 0.92))
        time.sleep(8)
    tab("Settings")
    time.sleep(2)
    for _ in range(8):
        if tap_label("Load Demo Collection"):
            break
        swipe_up()
    tap_label("Load Demo Data") or tap(540, int(H * 0.55))
    time.sleep(15)
    tap_label("OK") or tap(540, int(H * 0.55))
    time.sleep(3)


def ensure_home() -> None:
    tab("Home")
    time.sleep(2)
    dismiss_system_dialogs()


def open_tool(label: str, max_swipes: int = 12) -> None:
    tab("Tools")
    time.sleep(2)
    for _ in range(max_swipes):
        if tap_label(label):
            return
        swipe_up()
    tap_label(label)


def capture_main() -> None:
    print("=== Phase B: main manual ===")
    ensure_home()
    shot("01-home-command-center")

    tab("My Pieces")
    time.sleep(4)
    shot("02-museum-collection")
    tap(W // 3, int(H * 0.32))
    time.sleep(3)
    if has(r"Provenance|Service|Estimated|Purchase|Brand"):
        shot("03-piece-detail")
    else:
        back()
        shot("03-piece-detail")

    tap_label("Wish List") or tap_label("Wish") or tap(900, 450)
    time.sleep(2)
    shot("04-wishlist-grails")

    # Finances via More menu
    tap_label("More") or tap(W - 60, 120)
    time.sleep(1.5)
    tap_label("Finances") or tap_label("Gains") or tap(W // 2, int(H * 0.55))
    time.sleep(3)
    if has(r"Financ|Gain|Loss|Cost basis|Portfolio"):
        shot("15-finances-pl")
    back(2)

    tab("Home")
    time.sleep(2)
    tap_label("Hunt") or tap(int(W * 0.13), int(H * 0.24))
    time.sleep(4)
    shot("05-ebay-grail-radar")

    ensure_home()
    tap_label("Fix clock") or tap(int(W * 0.38), int(H * 0.24))
    time.sleep(4)
    if not has(r"What.s wrong|Won.t chime|symptom|Clock Repair"):
        open_tool("Clock Repair Help")
        time.sleep(3)
    if has(r"What.s wrong|Won.t chime|symptom"):
        shot("06a-clock-repair-symptoms")
    tap_label("Won't chime") or tap_label("Won\u2019t chime") or tap(W // 2, int(H * 0.4))
    time.sleep(10)
    shot("06-clockworks-parts")

    for _ in range(4):
        back()
    ensure_home()
    open_tool("Identify")
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
            print(f"  identify ready @{i * 2}s")
            break
        time.sleep(2)
    shot("07-identify-results")

    for _ in range(3):
        back()
    tab("Tools")
    time.sleep(2)
    shot("08-tools-hub")

    open_tool("Compare")
    time.sleep(3)
    if has(r"Compare|Select|Pick"):
        shot("16-compare")
    back()

    open_tool("Exact Time") or open_tool("Atomic")
    time.sleep(3)
    shot("17-atomic-clock")
    back()

    open_tool("Moon Phase") or open_tool("Moon")
    time.sleep(3)
    shot("18-moon-phase")
    back()

    tab("Tools")
    for _ in range(8):
        swipe_up()
    tap_label("Web Companion")
    time.sleep(4)
    shot("09-web-companion")

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
        if not SKIP_BOOT:
            if not SKIP_ONBOARDING:
                capture_onboarding()
                prepare_app(skip_clear=True)
            else:
                prepare_app()
        else:
            tab("Home")
            time.sleep(2)
        capture_main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    print(f"Done — outputs in {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
