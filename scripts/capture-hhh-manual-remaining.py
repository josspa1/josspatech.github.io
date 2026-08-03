#!/usr/bin/env python3
"""Capture remaining HHH EN manual keepers (4-tab layout). Prefer screencap truth."""
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
MANUAL = ROOT / "assets" / "screenshots" / "hhh" / "manual"
INTRO = ROOT / "assets" / "screenshots" / "hhh" / "intro"
STAGING = ROOT / "assets" / "screenshots" / "hhh" / f"_capture_{date.today().isoformat()}"
UI = ROOT / "assets" / "screenshots" / "hhh" / "_ui.xml"
LOG = STAGING / "_capture_log.txt"
SERIAL = os.environ.get("ANDROID_SERIAL", "R5CXC2K4Z8F")
PKG = "com.josspatech.handyhorology"
ADB = str(Path(os.environ.get("LOCALAPPDATA", "")) / "Android/Sdk/platform-tools/adb.exe")

# Live 4-tab chrome on SM-S938 (~1440x3120)
TABS = {"Home": 180, "My Museum": 540, "Tools": 900, "Settings": 1260}
TAB_Y = 2920


def log(msg: str) -> None:
    STAGING.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def adb(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([ADB, "-s", SERIAL, *args], capture_output=True, text=True)


def focus_ok() -> bool:
    out = adb("shell", "dumpsys", "window").stdout
    return PKG in out and "mCurrentFocus" in out


def wake() -> None:
    adb("shell", "am", "force-stop", "dev.mobile.maestro")
    adb("shell", "am", "force-stop", "dev.mobile.maestro.test")
    if not focus_ok():
        adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
        time.sleep(5)
    # dismiss notif permission if any
    for y in (2350, 2450, 2200):
        if "permissioncontroller" in adb("shell", "dumpsys", "window").stdout:
            adb("shell", "input", "tap", "720", str(y))
            time.sleep(1)


def ui() -> str:
    adb("shell", "rm", "-f", "/sdcard/ui.xml")
    try:
        UI.unlink(missing_ok=True)
    except TypeError:
        if UI.exists():
            UI.unlink()
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    if not UI.exists() or UI.stat().st_size < 80:
        return ""
    return UI.read_text(encoding="utf-8", errors="ignore")


def texts() -> list[str]:
    xml = ui()
    return [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]


def tap_xy(x: int, y: int, wait: float = 1.6) -> None:
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(wait)


def tab(name: str) -> None:
    tap_xy(TABS[name], TAB_Y)
    log(f"tab {name}")


def tap_label(*labels: str) -> bool:
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
        # refuse wrong apps
        if "whisker" in hay.lower() or "maestro" in hay.lower():
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        cx, cy = (l + r) // 2, (t + b) // 2
        if cy < 120:
            continue
        score = -abs(cy - 900)
        if best is None or score > best[2]:
            best = (cx, cy, score, text, desc)
    if not best:
        log(f"MISS {labels}")
        return False
    log(f"tap {labels[0]!r} @ {best[0]},{best[1]} ({best[3] or best[4]})")
    tap_xy(best[0], best[1])
    return True


def swipe_up(n: int = 1) -> None:
    for _ in range(n):
        adb("shell", "input", "swipe", "720", "2200", "720", "900", "350")
        time.sleep(0.7)


def back(n: int = 1) -> None:
    for _ in range(n):
        adb("shell", "input", "keyevent", "4")
        time.sleep(0.8)


def shot(canonical: str, note: str) -> None:
    STAGING.mkdir(parents=True, exist_ok=True)
    MANUAL.mkdir(parents=True, exist_ok=True)
    remote = "/sdcard/hhh-shot.png"
    adb("shell", "screencap", "-p", remote)
    staged = STAGING / f"HHH_manual_{canonical.replace('.png', '')}_{date.today().isoformat()}.png"
    adb("pull", remote, str(staged))
    dest = MANUAL / canonical
    if staged.exists() and staged.stat().st_size > 20000:
        dest.write_bytes(staged.read_bytes())
        log(f"SHOT {canonical} ({staged.stat().st_size} bytes) — {note}")
    else:
        log(f"FAIL shot {canonical} size={staged.stat().st_size if staged.exists() else 0}")


def main() -> None:
    wake()
    if not focus_ok():
        log("ABORT: HHH not focused")
        return

    # --- Unlock Pro (confirm live) ---
    log("=== Unlock Pro ===")
    tab("Settings")
    time.sleep(1)
    tap_label("Upgrade to Pro")
    time.sleep(2)
    t = " ".join(texts())
    if any(k in t for k in ("Unlock Pro", "Subscribe Now", "74.99", "9.99", "Annual")) or True:
        # screencap is source of truth even if dump is flaky
        shot("12-trial-subscription.png", "Unlock Pro live")
        intro = INTRO / "10-trial-pro.png"
        intro.write_bytes((MANUAL / "12-trial-subscription.png").read_bytes())
    back(2)

    # --- Web Companion URL + code ---
    log("=== Web Companion ===")
    tab("Tools")
    swipe_up(2)
    tap_label("Web Companion")
    time.sleep(1)
    tap_label("Start Web Companion", "Start")
    time.sleep(2)
    # scroll a little so code + URL visible
    adb("shell", "input", "swipe", "720", "1800", "720", "1400", "250")
    time.sleep(0.8)
    shot("09-web-companion.png", "WC URL + pairing code")
    back(2)

    # --- Settings Theme / Language / Security / Notifications ---
    log("=== Settings sections ===")
    tab("Settings")
    time.sleep(1)
    swipe_up(1)
    shot("10b-settings-theme.png", "Theme row visible")
    if tap_label("Theme"):
        time.sleep(1)
        shot("10c-settings-theme-detail.png", "Theme detail")
        back(1)
    swipe_up(1)
    if tap_label("Language"):
        time.sleep(1)
        shot("10d-settings-language.png", "Language")
        back(1)
    swipe_up(1)
    if tap_label("Security", "App Lock", "Security & App Lock"):
        time.sleep(1)
        shot("10e-settings-security.png", "Security")
        back(1)
    swipe_up(2)
    # Prefer exact Settings notifications — avoid Whisker
    xml = ui()
    if "Whisker" not in xml and tap_label("Notifications"):
        time.sleep(1)
        shot("10f-settings-notifications.png", "Notifications in HHH")
        back(1)
    else:
        log("SKIP Notifications (Whisker risk or miss)")
    # overview scroll with several sections
    tab("Settings")
    swipe_up(2)
    shot("10-settings.png", "Settings mid scroll (theme/language area)")

    # --- Share Nearby entry ---
    log("=== Share Nearby ===")
    tab("Tools")
    swipe_up(2)
    if tap_label("Share Nearby", "Nearby"):
        time.sleep(1.5)
        shot("27-share-nearby-entry.png", "Share Nearby")
        back(1)

    # --- Demand board ---
    log("=== Demand ===")
    tab("Tools")
    swipe_up(1)
    if tap_label("Demand Rolodex", "Demand"):
        time.sleep(1.5)
        shot("23-demand-rolodex-board.png", "Demand board")
        back(1)

    # --- Sample banner / clear path ---
    log("=== Sample mode ===")
    tab("Home")
    time.sleep(1)
    shot("19-sample-home-banner.png", "Sample data banner on Home")

    log("DONE")


if __name__ == "__main__":
    main()
