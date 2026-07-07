#!/usr/bin/env python3
"""Capture PBJ user-manual PNGs from Android emulator (1080x2400).

Outputs to assets/screenshots/pbj/manual/ for build-user-manual-slides.py.
Requires: PBJ debug build installed, emulator online.

Usage:
  python scripts/capture-pbj-manual-screenshots.py

Set ANDROID_SERIAL if not emulator-5554. Run gen-pbj-manual-missing-slides.py
for slides that cannot be reached in a headless capture session.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "screenshots" / "pbj" / "manual"
SERIAL = os.environ.get("ANDROID_SERIAL", "emulator-5554")
PKG = "com.josspatech.pocketbudjet"
PBJ_SRC = Path(os.environ.get("PBJ_SRC", r"C:\Users\jossp\Documents\MobileApps\PBJ\SourceCode"))

ADB = os.environ.get(
    "ADB",
    str(Path(os.environ.get("LOCALAPPDATA", "")) / "Android/Sdk/platform-tools/adb.exe"),
)


def adb(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [ADB, "-s", SERIAL, *args],
        check=False,
        capture_output=True,
        text=True,
    )


def device_online() -> bool:
    r = adb("get-state")
    return r.returncode == 0 and "device" in (r.stdout or "")


def shot(name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    dest = OUT / name
    tmp = "/sdcard/pbj-manual-capture.png"
    adb("shell", "screencap", "-p", tmp)
    adb("pull", tmp, str(dest))
    adb("shell", "rm", "-f", tmp)
    if dest.is_file():
        print(f"wrote {dest.relative_to(ROOT)}")
    else:
        print(f"FAILED {name}", file=sys.stderr)


def main() -> int:
    if not Path(ADB).is_file():
        print(f"adb not found: {ADB}", file=sys.stderr)
        return 1
    if not device_online():
        print(
            f"No device at {SERIAL}. Start emulator with PBJ installed, or run:\n"
            "  python scripts/gen-pbj-manual-missing-slides.py",
            file=sys.stderr,
        )
        return 1

    print(f"Capturing from {SERIAL} ({PKG}) …")
    adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
    # Extend with navigation steps per screenRegistry as captures are scripted.
    shot("_device-smoke.png")
    print(
        "Smoke capture OK. Add navigation steps for remaining screens, "
        "or use gen-pbj-manual-missing-slides.py for generated PNGs."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
