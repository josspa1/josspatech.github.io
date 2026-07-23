#!/usr/bin/env python3
"""Capture priority HHH manual shots from Joe's physical phone (R5CXC2K4Z8F).

Also copies keepers to NAS catalogue and site assets/screenshots/hhh/manual/.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(line_buffering=True)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "screenshots" / "hhh" / "manual"
UI = ROOT / "assets" / "screenshots" / "hhh" / "_ui-dump.xml"
STAGING = ROOT / "assets" / "screenshots" / "hhh" / "_capture_2026-07-23"
NAS = Path(r"\\Cerberus\MobileApps\HHH\screenshots\manual")
NAS_ARCHIVE = Path(r"\\Cerberus\MobileApps\HHH\screenshots\archive") / f"{date.today().isoformat()}-phone-retake"
SERIAL = os.environ.get("ANDROID_SERIAL", "R5CXC2K4Z8F")
PKG = "com.josspatech.handyhorology"
W, H = 1440, 3120
TAB_Y = 2860

ADB = os.environ.get(
    "ADB",
    str(Path(os.environ.get("LOCALAPPDATA", "")) / "Android/Sdk/platform-tools/adb.exe"),
)


def adb(*args: str, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run([ADB, "-s", SERIAL, *args], check=check, capture_output=True, text=True)


def tap(x: int, y: int, wait: float = 1.6) -> None:
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(wait)


def back(n: int = 1) -> None:
    for _ in range(n):
        adb("shell", "input", "keyevent", "4")
        time.sleep(1.0)


def swipe_up(n: int = 1) -> None:
    for _ in range(n):
        adb("shell", "input", "swipe", str(W // 2), str(int(H * 0.78)), str(W // 2), str(int(H * 0.28)), "350")
        time.sleep(0.55)


def swipe_down(n: int = 1) -> None:
    for _ in range(n):
        adb("shell", "input", "swipe", str(W // 2), str(int(H * 0.28)), str(W // 2), str(int(H * 0.78)), "350")
        time.sleep(0.45)


def wake_and_launch() -> None:
    adb("shell", "input", "keyevent", "KEYCODE_WAKEUP")
    adb("shell", "am", "start", "-n", f"{PKG}/.MainActivity")
    time.sleep(2.5)


def ui(retries: int = 5) -> str:
    for attempt in range(retries):
        adb("shell", "rm", "-f", "/sdcard/ui.xml")
        time.sleep(0.3)
        proc = adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
        blob = (proc.stdout or "") + (proc.stderr or "")
        if "could not get idle state" in blob.lower():
            time.sleep(1.5 + attempt)
            continue
        adb("pull", "/sdcard/ui.xml", str(UI))
        if UI.exists() and UI.stat().st_size > 400:
            return UI.read_text(encoding="utf-8", errors="ignore")
        time.sleep(0.8)
    return UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""


def tap_label(*labels: str, partial: bool = False) -> bool:
    xml = ui()
    for label in labels:
        esc = re.escape(label)
        for node in re.findall(r"<node[^>]+>", xml):
            text_m = re.search(r'text="([^"]*)"', node)
            desc_m = re.search(r'content-desc="([^"]*)"', node)
            text = text_m.group(1) if text_m else ""
            desc = desc_m.group(1) if desc_m else ""
            hay = f"{text} {desc}"
            if partial:
                ok = label.lower() in hay.lower()
            else:
                ok = bool(re.search(rf'(?:text|content-desc)="{esc}"', node)) or text == label or desc == label
            if not ok:
                continue
            m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
            if not m:
                continue
            cx = (int(m.group(1)) + int(m.group(3))) // 2
            cy = (int(m.group(2)) + int(m.group(4))) // 2
            # Prefer tappable mid-screen nodes over tiny icons
            if cy < 80:
                continue
            print(f"  tap {label!r} @ {cx},{cy} ({text or desc})")
            tap(cx, cy)
            return True
    print(f"  MISS labels={labels}")
    return False


def has(*patterns: str) -> bool:
    xml = ui()
    return any(re.search(p, xml, re.I) for p in patterns)


def tab(name: str) -> None:
    if tap_label(name):
        return
    # 1.0.88 = 4 tabs: Home | My Museum | Tools | Settings
    tabs = {
        "Home": W // 8,
        "My Museum": W * 3 // 8,
        "My Pieces": W * 3 // 8,
        "Tools": W * 5 // 8,
        "Settings": W * 7 // 8,
        "Collectors": W * 5 // 8,  # fallback → Tools era; real Collectors tab not in 1.0.88
    }
    tap(tabs.get(name, W // 8), TAB_Y)


OS_DENY = (
    r"com\.samsung\.android\.app\.contacts",
    r"com\.android\.contacts",
    r"All contacts",
    r"Contact details",
    r"com\.sec\.android\.app\.launcher",
    r"com\.google\.android\.googlequicksearchbox",
    r"Quick Search Box",
    # Samsung launcher / app drawer (not HHH)
    r'text="Personal"[^>]*selected="true"',
    r'text="Work"[^>]*resource-id=".*launcher',
)


def foreground_ok() -> tuple[bool, str]:
    """Require HHH in-app UI; reject launcher / Contacts / gallery pickers."""
    xml = ui()
    if not xml:
        return False, "empty UI dump"
    for pat in OS_DENY:
        if re.search(pat, xml, re.I):
            return False, f"OS chrome matched: {pat}"
    # Positive markers: HHH tab bar or sample banner / tools
    if not re.search(
        r"handyhorology|My Museum|Exploring with sample|QUICK COMMANDS|Demand Rolodex|Offline Show Pack|Exact Time|Moon Phase|File backup|Clear samples",
        xml,
        re.I,
    ):
        # also accept Settings lists that mention HHH strings
        if not re.search(r"Collector Network|Device Sync|Web Companion|Grail Radar", xml, re.I):
            return False, "no HHH in-app markers"
    return True, "ok"


def shot(name: str, *, review_only: bool = True, allow_dialog: bool = False) -> Path | None:
    """Capture to staging only. Never write canonical manual/ or NAS until review pass."""
    STAGING.mkdir(parents=True, exist_ok=True)
    ok, reason = foreground_ok()
    if not ok:
        xml = UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""
        dialogish = allow_dialog and re.search(
            r"Cancel|Clear samples|Remove sample|Are you sure|OK|Keep",
            xml,
            re.I,
        )
        # Still reject hard OS chrome
        for pat in OS_DENY:
            if re.search(pat, xml, re.I):
                print(f"REJECT pre-check {name}: OS chrome matched: {pat}")
                return None
        if not dialogish:
            print(f"REJECT pre-check {name}: {reason}")
            return None
        print(f"  allow_dialog override for {name}")
    remote = f"/sdcard/{name}.png"
    staged = STAGING / f"HHH_manual_{name}_{date.today().strftime('%Y%m%d')}.png"
    time.sleep(0.8)
    adb("shell", "screencap", "-p", remote)
    adb("pull", remote, str(staged))
    size = staged.stat().st_size if staged.exists() else 0
    print(f"STAGED {staged.name} ({size} bytes) — awaiting visual review before label/save")
    if not review_only:
        OUT.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, OUT / f"{name}.png")
    return staged


def dismiss_noise() -> None:
    if has(r"Allow|While using|Don.t allow|NOT NOW|Not now|Skip"):
        tap_label("While using the app", "Allow", "Don't allow", "NOT NOW", "Not now", "Skip", partial=True)


def go_home() -> None:
    """Stay inside HHH — never Back out to the launcher."""
    wake_and_launch()
    # If already on a nested screen, one or two backs max, then re-assert HHH
    for _ in range(2):
        ok, _ = foreground_ok()
        if ok and has(r"QUICK COMMANDS|Exploring with sample|Good morning"):
            return
        adb("shell", "input", "keyevent", "4")
        time.sleep(0.8)
    wake_and_launch()
    ok, reason = foreground_ok()
    if not ok:
        print(f"WARN go_home still not in HHH: {reason}")
        return
    if not has(r"QUICK COMMANDS|Exploring with sample"):
        tab("Home")
        time.sleep(1.0)


def capture_home_sample() -> None:
    go_home()
    dismiss_noise()
    if has(r"Exploring with sample|sample data|Clear samples"):
        shot("19-sample-loading")  # sample-active confirmation (banner on Home)
    else:
        print("WARN: sample banner not visible — still shooting Home for 19")
        shot("19-sample-loading")


def capture_clear_ludwig() -> None:
    go_home()
    if tap_label("Clear samples", "Clear sample data", partial=True):
        time.sleep(0.8)
        # Don't confirm clear — capture the confirm dialog if any, else Settings row
        if has(r"Clear|Remove|Cancel|Ludwig|sample"):
            shot("26-clear-ludwig-sample")
            tap_label("Cancel", "No", "Keep", partial=True)
            return
    tab("Settings")
    swipe_up(6)
    if tap_label("Clear sample", "Clear samples", "sample data", "Ludwig", partial=True):
        time.sleep(0.8)
        shot("26-clear-ludwig-sample")
        tap_label("Cancel", "No", "Keep", partial=True)
    else:
        print("WARN: clear Ludwig control not found — Settings fallback")
        shot("26-clear-ludwig-sample")


def capture_collectors_network() -> None:
    """1.0.88 has no Collectors tab — shoot Collector Network from Settings."""
    tab("Settings")
    swipe_down(3)
    swipe_up(2)
    if not tap_label("Collector Network", "Collectors", "My Network", "Network", partial=True):
        swipe_up(4)
        tap_label("Collector Network", "Collectors", "Network", partial=True)
    time.sleep(1.2)
    shot("20-collectors-tab")


def capture_demand() -> None:
    tab("Tools")
    swipe_down(4)
    for _ in range(10):
        if has(r"Demand Rolodex|Demand"):
            break
        swipe_up(1)
    if not tap_label("Demand Rolodex", "Demand", partial=True):
        print("WARN: Demand Rolodex tile missing")
        shot("21-demand-rolodex-send")
        return
    time.sleep(1.5)
    # Board first if mock cards present
    if has(r"board|make|model|Seiko|Rolex|Omega|want", r"Demand"):
        shot("23-demand-rolodex-board")
    # Send path
    if tap_label("Send", "Share want", "want list", "Send want", partial=True):
        time.sleep(1.2)
        shot("21-demand-rolodex-send")
        back(1)
    else:
        # Maybe already on share flow from Tools deep link naming
        shot("21-demand-rolodex-send")
    if tap_label("Receive", "Paste QR", "Nearby", partial=True):
        time.sleep(1.2)
        shot("22-demand-rolodex-receive")
        back(1)
    else:
        # Try from hub again
        back(1)
        if tap_label("Demand Rolodex", "Demand", partial=True):
            tap_label("Receive", partial=True)
            time.sleep(1.0)
            shot("22-demand-rolodex-receive")
    if not (OUT / "23-demand-rolodex-board.png").exists():
        back(2)
        tab("Tools")
        tap_label("Demand Rolodex", "Demand", partial=True)
        time.sleep(1.0)
        shot("23-demand-rolodex-board")


def capture_device_sync_and_offline() -> None:
    tab("Settings")
    swipe_down(3)
    for _ in range(8):
        if has(r"File backup|Backup|Device Sync"):
            break
        swipe_up(1)
    if tap_label("File backup", "Backup", partial=True):
        time.sleep(1.2)
        if tap_label("Device Sync", partial=True):
            time.sleep(1.2)
            shot("24-device-sync")
            back(1)
        else:
            swipe_up(3)
            if tap_label("Device Sync", partial=True):
                time.sleep(1.2)
                shot("24-device-sync")
                back(1)
            else:
                print("WARN: Device Sync not found — shooting backup screen")
                shot("24-device-sync")
        back(1)
    tab("Settings")
    swipe_down(2)
    for _ in range(10):
        if has(r"Offline Show Pack|Offline"):
            break
        swipe_up(1)
    if tap_label("Offline Show Pack", "Offline", partial=True):
        time.sleep(1.4)
        shot("25-offline-show-pack")
    else:
        print("WARN: Offline Show Pack not found")
        shot("25-offline-show-pack")


def capture_atomic_moon() -> None:
    tab("Tools")
    swipe_down(3)
    for _ in range(12):
        if has(r"Exact Time|Atomic|Moon Phase"):
            break
        swipe_up(1)
    if tap_label("Exact Time", "Atomic", partial=True):
        time.sleep(1.5)
        shot("17-atomic-clock")
        back(1)
    if not has(r"Moon Phase"):
        swipe_up(2)
    if tap_label("Moon Phase", "Moon", partial=True):
        time.sleep(1.5)
        shot("18-moon-phase")
        back(1)


def capture_identify_results() -> None:
    go_home()
    if not tap_label("Identify"):
        tab("Tools")
        swipe_down(2)
        for _ in range(6):
            if has(r"Identify"):
                break
            swipe_up(1)
        tap_label("Identify", partial=True)
    time.sleep(1.5)
    dismiss_noise()
    # Prefer Choose Photo over live camera
    if not tap_label("Choose Photo", "Choose from gallery", "Gallery", partial=True):
        swipe_up(2)
        tap_label("Choose Photo", "Gallery", "Photos", partial=True)
    time.sleep(2.0)
    dismiss_noise()
    # Pick first gallery thumbnail roughly
    tap(W // 4, int(H * 0.35), wait=1.5)
    tap(W // 2, int(H * 0.92), wait=1.0)  # possible Done/Select
    if tap_label("Identify this timepiece", "Identify", "Use photo", "Done", "Select", partial=True):
        pass
    print("Waiting for Identify AI...")
    for i in range(24):
        time.sleep(5)
        if has(r"confidence|%|Likely|Match|Alternative|Save to|Add to museum|Wristwatch|Seiko|Omega"):
            print(f"  results-ish UI after {(i+1)*5}s")
            break
        print(f"  ...{(i+1)*5}s")
    shot("07-identify-results")
    back(3)


def promote_reviewed(names: list[str]) -> None:
    """Copy only after visual review. Staging → manual/ → NAS."""
    NAS.mkdir(parents=True, exist_ok=True)
    NAS_ARCHIVE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    for name in names:
        # prefer newest staged file
        staged_hits = sorted(STAGING.glob(f"HHH_manual_{name}_*.png"), reverse=True)
        src = staged_hits[0] if staged_hits else None
        if not src or not src.exists():
            print(f"promote skip missing staged {name}")
            continue
        dest_local = OUT / f"{name}.png"
        shutil.copy2(src, dest_local)
        dest_nas = NAS / f"{name}.png"
        if dest_nas.exists():
            NAS_ARCHIVE.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dest_nas, NAS_ARCHIVE / f"{name}.png")
        shutil.copy2(src, dest_nas)
        print(f"PROMOTED {name} -> manual/ + NAS")


def main() -> None:
    print("Do not auto-run full capture. Use one-shot helpers + visual review.")
    print(f"SERIAL={SERIAL} STAGING={STAGING}")
    print("Example: python -c \"from capture... import *; wake_and_launch(); capture_home_sample()\"")


if __name__ == "__main__":
    main()
