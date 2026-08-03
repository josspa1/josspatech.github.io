#!/usr/bin/env python3
"""Capture ONE HHH manual shot to staging. Never overwrite keepers.
Usage:
  python capture-hhh-one-verified.py wc
  python capture-hhh-one-verified.py settings-theme
  python capture-hhh-one-verified.py settings-language
  python capture-hhh-one-verified.py settings-security
  python capture-hhh-one-verified.py settings-notifications
  python capture-hhh-one-verified.py settings-overview
  python capture-hhh-one-verified.py share-nearby
  python capture-hhh-one-verified.py unlock-pro
  python capture-hhh-one-verified.py demand-board
  python capture-hhh-one-verified.py sample-home
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "assets" / "screenshots" / "hhh" / "_capture_verify"
UI = STAGING / "_ui.xml"
SERIAL = os.environ.get("ANDROID_SERIAL", "R5CXC2K4Z8F")
PKG = "com.josspatech.handyhorology"
ADB = str(Path(os.environ.get("LOCALAPPDATA", "")) / "Android/Sdk/platform-tools/adb.exe")
TABS = {"Home": 180, "My Museum": 540, "Tools": 900, "Settings": 1260}
TAB_Y = 2920


def adb(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([ADB, "-s", SERIAL, *args], capture_output=True, text=True)


def log(msg: str) -> None:
    print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)


def focus_ok() -> bool:
    out = adb("shell", "dumpsys", "window").stdout
    return PKG in out and ("mCurrentFocus" in out)


def wake() -> None:
    adb("shell", "am", "force-stop", "dev.mobile.maestro")
    adb("shell", "am", "force-stop", "dev.mobile.maestro.test")
    adb("shell", "input", "keyevent", "KEYCODE_WAKEUP")
    if not focus_ok():
        adb("shell", "am", "start", "-n", f"{PKG}/.MainActivity")
        time.sleep(4)
    # dismiss permission if shown
    for y in (2350, 2450, 2200):
        win = adb("shell", "dumpsys", "window").stdout
        if "permissioncontroller" in win:
            adb("shell", "input", "tap", "720", str(y))
            time.sleep(1)


def ui() -> str:
    STAGING.mkdir(parents=True, exist_ok=True)
    adb("shell", "rm", "-f", "/sdcard/ui.xml")
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    if not UI.exists() or UI.stat().st_size < 80:
        return ""
    return UI.read_text(encoding="utf-8", errors="ignore")


def texts() -> list[str]:
    return [t for t in re.findall(r'text="([^"]+)"', ui()) if t.strip()]


def tap_xy(x: int, y: int, wait: float = 1.6) -> None:
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(wait)


def tab(name: str) -> None:
    tap_xy(TABS[name], TAB_Y)
    log(f"tab {name}")


def swipe_up(n: int = 1) -> None:
    for _ in range(n):
        adb("shell", "input", "swipe", "720", "2200", "720", "900", "350")
        time.sleep(0.8)


def back(n: int = 1) -> None:
    for _ in range(n):
        adb("shell", "input", "keyevent", "4")
        time.sleep(0.9)


def find_tap(*labels: str, refuse: tuple[str, ...] = ("whisker", "maestro")) -> bool:
    xml = ui()
    if not xml:
        log("MISS (no ui dump)")
        return False
    best = None
    for node in re.findall(r"<node[^>]+>", xml):
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        hay = f"{text} {desc}"
        if not any(lab.lower() in hay.lower() for lab in labels):
            continue
        if any(r in hay.lower() for r in refuse):
            log(f"refuse {hay[:60]!r}")
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        cx, cy = (l + r) // 2, (t + b) // 2
        if cy < 140 or cy > 2850:
            continue
        # prefer mid-screen matches
        score = -abs(cy - 1400) - (0 if any(lab.lower() == text.lower() for lab in labels) else 80)
        if best is None or score > best[2]:
            best = (cx, cy, score, text, desc)
    if not best:
        log(f"MISS {labels}")
        return False
    log(f"tap {labels[0]!r} @ {best[0]},{best[1]} ({best[3] or best[4]})")
    tap_xy(best[0], best[1])
    return True


def shot_staging(name: str) -> Path:
    STAGING.mkdir(parents=True, exist_ok=True)
    remote = "/sdcard/hhh-shot.png"
    adb("shell", "screencap", "-p", remote)
    dest = STAGING / name
    adb("pull", remote, str(dest))
    size = dest.stat().st_size if dest.exists() else 0
    log(f"STAGED {dest.name} ({size} bytes) — DO NOT promote until visually verified")
    # also write a small marker of on-screen texts for review
    marker = STAGING / (name.replace(".png", "") + "_texts.txt")
    marker.write_text("\n".join(texts()[:80]), encoding="utf-8")
    return dest


def ensure_tools_search(query: str) -> None:
    """Use Tools search to jump to a tool — more reliable than scrolling."""
    tab("Tools")
    time.sleep(1)
    # tap search field
    if not find_tap("Find a tool", "Search"):
        # fallback: coords for search bar near top
        tap_xy(720, 280)
    time.sleep(0.8)
    adb("shell", "input", "text", query.replace(" ", "%s"))
    time.sleep(1.5)


def capture_wc() -> None:
    log("=== Web Companion (live URL + code) ===")
    ensure_tools_search("Web")
    if not find_tap("Web Companion"):
        # clear search and scroll
        back(1)
        tab("Tools")
        swipe_up(3)
        if not find_tap("Web Companion"):
            log("ABORT: Web Companion not found")
            return
    time.sleep(1.2)
    if not find_tap("Start Web Companion", "Start"):
        log("ABORT: Start button not found")
        shot_staging("FAIL_wc_before_start.png")
        return
    time.sleep(2.5)
    # nudge so code + URL sit in frame
    adb("shell", "input", "swipe", "720", "1900", "720", "1500", "250")
    time.sleep(0.8)
    t = " ".join(texts())
    log(f"ui texts hint: {t[:240]}")
    shot_staging("09-web-companion.CANDIDATE.png")
    # leave running for honest shot; stop after
    back(1)


def capture_settings_row(label: str, out_name: str, alts: tuple[str, ...] = ()) -> None:
    log(f"=== Settings → {label} ===")
    tab("Settings")
    time.sleep(1.2)
    # scroll from top
    for _ in range(6):
        labels = (label, *alts)
        if find_tap(*labels, refuse=("whisker", "maestro", "notificationlistener")):
            time.sleep(1.4)
            shot_staging(out_name)
            back(1)
            return
        swipe_up(1)
    log(f"ABORT: could not open {label}")
    shot_staging(f"FAIL_{out_name}")


def capture_settings_overview() -> None:
    log("=== Settings overview (Theme/Language area) ===")
    tab("Settings")
    time.sleep(1)
    swipe_up(2)
    time.sleep(0.8)
    shot_staging("10-settings.CANDIDATE.png")


def capture_share_nearby() -> None:
    log("=== Share Nearby ===")
    ensure_tools_search("Share")
    if not find_tap("Share Nearby", "Nearby"):
        back(1)
        tab("Tools")
        swipe_up(3)
        if not find_tap("Share Nearby", "Nearby"):
            log("ABORT: Share Nearby not found")
            return
    time.sleep(1.5)
    shot_staging("27-share-nearby-entry.CANDIDATE.png")
    back(1)


def capture_unlock() -> None:
    log("=== Unlock Pro ===")
    tab("Settings")
    time.sleep(1)
    if not find_tap("Upgrade to Pro"):
        log("ABORT: Upgrade to Pro missing")
        return
    time.sleep(2)
    shot_staging("12-trial-subscription.CANDIDATE.png")
    back(2)


def capture_demand() -> None:
    log("=== Demand board ===")
    ensure_tools_search("Demand")
    if not find_tap("Demand Rolodex", "Demand"):
        back(1)
        tab("Tools")
        swipe_up(2)
        if not find_tap("Demand Rolodex", "Demand"):
            log("ABORT")
            return
    time.sleep(1.5)
    shot_staging("23-demand-rolodex-board.CANDIDATE.png")
    back(1)


def capture_sample_home() -> None:
    log("=== Sample / Home banner ===")
    tab("Home")
    time.sleep(1.2)
    shot_staging("19-sample-home-banner.CANDIDATE.png")


ACTIONS = {
    "wc": capture_wc,
    "settings-theme": lambda: capture_settings_row("Theme", "10b-settings-theme.CANDIDATE.png", ("Appearance",)),
    "settings-theme-detail": lambda: capture_settings_row("Theme", "10c-settings-theme-detail.CANDIDATE.png", ("Appearance",)),
    "settings-language": lambda: capture_settings_row("Language", "10d-settings-language.CANDIDATE.png"),
    "settings-security": lambda: capture_settings_row(
        "Security & App Lock", "10e-settings-security.CANDIDATE.png", ("App Lock", "Security")
    ),
    "settings-notifications": lambda: capture_settings_row(
        "Notifications", "10f-settings-notifications.CANDIDATE.png"
    ),
    "settings-overview": capture_settings_overview,
    "share-nearby": capture_share_nearby,
    "unlock-pro": capture_unlock,
    "demand-board": capture_demand,
    "sample-home": capture_sample_home,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in ACTIONS:
        print(__doc__)
        sys.exit(1)
    wake()
    if not focus_ok():
        log("ABORT: HHH not focused")
        sys.exit(2)
    ACTIONS[sys.argv[1]]()
    log("DONE — review staging image before promoting to keepers")


if __name__ == "__main__":
    main()
