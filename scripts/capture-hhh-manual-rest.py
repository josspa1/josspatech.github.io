#!/usr/bin/env python3
"""Capture HHH manual PNGs 05-12 via adb (demo must be loaded)."""
from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "screenshots" / "hhh" / "manual"
HHH_MANUAL = Path(r"C:\Users\jossp\Documents\MobileApps\HHH\SourceCode\manual")
SERIAL = "emulator-5554"
W, H = 1080, 2400
ADB = Path(__import__("os").environ.get("LOCALAPPDATA", "")) / "Android/Sdk/platform-tools/adb.exe"


def adb(*args: str) -> None:
    subprocess.run([ADB, "-s", SERIAL, *args], check=False)


def tap(x: int, y: int, wait: float = 2.0) -> None:
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(wait)


def back(n: int = 1) -> None:
    for _ in range(n):
        adb("shell", "input", "keyevent", "4")
        time.sleep(1.0)


def swipe_up() -> None:
    adb("shell", "input", "swipe", str(W // 2), str(int(H * 0.78)), str(W // 2), str(int(H * 0.32)), "350")
    time.sleep(0.6)


def tab(name: str) -> None:
    tabs = {"Home": W // 10, "My Pieces": W * 3 // 10, "Tools": W // 2, "Collectors": W * 7 // 10, "Settings": W * 9 // 10}
    tap(tabs[name], H - 70)


def shot(name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    remote = f"/sdcard/{name}.png"
    local = OUT / f"{name}.png"
    time.sleep(1.2)
    adb("shell", "screencap", "-p", remote)
    adb("pull", remote, str(local))
    print(f"SHOT {name} {local.stat().st_size if local.exists() else 0}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for src in HHH_MANUAL.glob("*.png"):
        shutil.copy2(src, OUT / src.name)
        print(f"copy {src.name}")

    tap(540, 1380, 0.5)  # dismiss dialog if open
    tab("Home")
    tap(int(W * 0.13), int(H * 0.24))  # Hunt quick command
    shot("05-ebay-grail-radar")

    tab("Home")
    tap(int(W * 0.38), int(H * 0.24))  # Fix clock
    time.sleep(3)
    shot("06a-clock-repair-symptoms")
    tap(W // 2, int(H * 0.42))  # Won't chime
    time.sleep(12)
    shot("06-clockworks-parts")

    back(2)
    tab("Tools")
    for _ in range(8):
        swipe_up()
    tap(W // 2, int(H * 0.55))  # Identify row
    time.sleep(3)
    shot("07a-identify-camera")
    tap(W // 2, int(H * 0.72))  # Choose Photo
    tap(W // 4, int(H * 0.35))  # first image
    tap(W // 2, H - 120)  # Identify this timepiece
    print("AI wait...")
    time.sleep(90)
    shot("07-identify-results")

    back(2)
    tab("Tools")
    shot("08-tools-hub")
    for _ in range(6):
        swipe_up()
    tap(W // 2, int(H * 0.72))
    time.sleep(3)
    shot("09-web-companion")

    back(2)
    tab("Settings")
    shot("10-settings")
    for _ in range(6):
        swipe_up()
    tap(W // 2, int(H * 0.55))
    time.sleep(2)
    shot("11-backup-restore")
    for _ in range(4):
        swipe_up()
    tap(W // 2, int(H * 0.45))
    time.sleep(2)
    shot("12-trial-subscription")
    print("Done")


if __name__ == "__main__":
    main()
