#!/usr/bin/env python3
"""Capture HHH manual keepers needed after 2026-07-24 picture audit.

Canonical names land in assets/screenshots/hhh/manual/.
Raw pulls also stay in _capture_2026-07-24/ with dated labels.
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
MANUAL = ROOT / "assets" / "screenshots" / "hhh" / "manual"
INTRO = ROOT / "assets" / "screenshots" / "hhh" / "intro"
STAGING = ROOT / "assets" / "screenshots" / "hhh" / f"_capture_{date.today().isoformat()}"
UI = ROOT / "assets" / "screenshots" / "hhh" / "_ui.xml"
LOG = STAGING / "_capture_log.txt"
NAS = Path(r"\\Cerberus\MobileApps\HHH\screenshots\manual")
SERIAL = os.environ.get("ANDROID_SERIAL", "R5CXC2K4Z8F")
PKG = "com.josspatech.handyhorology"
MAESTRO_PKGS = (
    "dev.mobile.maestro",
    "dev.mobile.maestro.test",
)
W, H = 1440, 3120
TAB_Y = 2860

ADB = os.environ.get(
    "ADB",
    str(Path(os.environ.get("LOCALAPPDATA", "")) / "Android/Sdk/platform-tools/adb.exe"),
)

# 5-tab layout (current)
TABS = {
    "Home": int(W * 0.10),
    "My Pieces": int(W * 0.30),
    "Tools": int(W * 0.50),
    "Collectors": int(W * 0.70),
    "Settings": int(W * 0.90),
}

OS_DENY = (
    r"dev\.mobile\.maestro",
    r"Maestro",
    r"com\.sec\.android\.app\.launcher",
    r'text="Personal"[^>]*selected="true"',
    r'text="Work"[^>]*resource-id=".*launcher',
    r"Quick Search Box",
    r"All apps",
    r"App drawer",
)

HHH_MARKERS = (
    r"com\.josspatech\.handyhorology",
    r"My Pieces",
    r"My Museum",
    r"Web Companion",
    r"Unlock Pro",
    r"Demand Rolodex",
    r"Offline Show Pack",
    r"Exploring with sample",
    r"Command Center",
    r"Grail Radar",
    r"File backup",
    r"Collector Network",
    r"Handy Horology",
)


def log(msg: str) -> None:
    STAGING.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def adb(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([ADB, "-s", SERIAL, *args], capture_output=True, text=True)


def tap(x: int, y: int, wait: float = 1.5) -> None:
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(wait)


def back(n: int = 1) -> None:
    for _ in range(n):
        adb("shell", "input", "keyevent", "4")
        time.sleep(0.9)


def swipe_up(n: int = 1) -> None:
    for _ in range(n):
        adb(
            "shell",
            "input",
            "swipe",
            str(W // 2),
            str(int(H * 0.75)),
            str(W // 2),
            str(int(H * 0.30)),
            "350",
        )
        time.sleep(0.55)


def focus_pkg() -> str:
    r = adb("shell", "dumpsys", "window")
    blob = (r.stdout or "") + (r.stderr or "")
    m = re.search(r"mCurrentFocus=Window\{[^ ]+ u0 ([^/}\s]+)", blob)
    return m.group(1) if m else ""


def stop_maestro() -> None:
    for p in MAESTRO_PKGS:
        adb("shell", "am", "force-stop", p)
        log(f"force-stop {p}")


def foreground_ok() -> tuple[bool, str]:
    pkg = focus_pkg()
    if pkg != PKG:
        return False, f"focus={pkg or '(none)'} (need {PKG})"
    if "maestro" in pkg.lower() or "launcher" in pkg.lower():
        return False, f"blocked pkg {pkg}"
    xml = ui()
    if not xml:
        return False, "empty UI dump"
    for pat in OS_DENY:
        if re.search(pat, xml, re.I):
            return False, f"OS/Maestro chrome: {pat}"
    if not any(re.search(p, xml, re.I) for p in HHH_MARKERS):
        return False, "no HHH in-app markers in UI dump"
    return True, "ok"


def wake_launch() -> None:
    adb("shell", "input", "keyevent", "KEYCODE_WAKEUP")
    adb("shell", "settings", "put", "system", "screen_off_timeout", "600000")
    stop_maestro()
    pkg = focus_pkg()
    if pkg != PKG:
        log(f"focus was {pkg or '(none)'} — launching HHH via monkey")
        adb("shell", "am", "force-stop", PKG)
        time.sleep(0.8)
        adb(
            "shell",
            "monkey",
            "-p",
            PKG,
            "-c",
            "android.intent.category.LAUNCHER",
            "1",
        )
        time.sleep(5.0)
        pkg = focus_pkg()
    if pkg != PKG:
        raise SystemExit(
            f"HHH not in foreground (focus={pkg}). "
            "Unlock the phone, open Handy Horology Helper, then re-run. "
            "Do not leave Maestro or the app drawer open."
        )
    ok, reason = foreground_ok()
    if not ok:
        raise SystemExit(f"HHH focus OK but UI check failed: {reason}")
    log(f"focus OK: {pkg} ({reason})")


def ui() -> str:
    adb("shell", "rm", "-f", "/sdcard/ui.xml")
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    return UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""


def tap_label(*labels: str, partial: bool = True) -> bool:
    xml = ui()
    for label in labels:
        for node in re.findall(r"<node[^>]+>", xml):
            text_m = re.search(r'text="([^"]*)"', node)
            desc_m = re.search(r'content-desc="([^"]*)"', node)
            text = text_m.group(1) if text_m else ""
            desc = desc_m.group(1) if desc_m else ""
            hay = f"{text} {desc}"
            if partial:
                ok = label.lower() in hay.lower()
            else:
                ok = text == label or desc == label
            if not ok:
                continue
            m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
            if not m:
                continue
            cx = (int(m.group(1)) + int(m.group(3))) // 2
            cy = (int(m.group(2)) + int(m.group(4))) // 2
            if cy < 90:
                continue
            log(f"  tap {label!r} @ {cx},{cy} ({text or desc})")
            tap(cx, cy)
            return True
    log(f"  MISS {labels}")
    return False


def has(*patterns: str) -> bool:
    xml = ui()
    return any(re.search(p, xml, re.I) for p in patterns)


def tab(name: str) -> None:
    if tap_label(name, partial=False) or tap_label(name):
        return
    tap(TABS.get(name, W // 2), TAB_Y)


def screencap(canonical: str, note: str, required: bool = True) -> Path | None:
    """Only save if HHH is focused and UI dump shows HHH markers — never OS/Maestro."""
    STAGING.mkdir(parents=True, exist_ok=True)
    MANUAL.mkdir(parents=True, exist_ok=True)
    ok, reason = foreground_ok()
    if not ok:
        msg = f"REFUSED {canonical}: not HHH UI ({reason})"
        if required:
            raise SystemExit(msg)
        log(f"  SKIP {msg}")
        return None
    dated = STAGING / f"HHH_manual_{Path(canonical).stem}_{date.today().isoformat()}.png"
    remote = "/sdcard/hhh_shot.png"
    adb("shell", "screencap", "-p", remote)
    adb("pull", remote, str(dated))
    if not dated.exists() or dated.stat().st_size < 20_000:
        msg = f"screencap failed: {canonical}"
        if required:
            raise SystemExit(msg)
        log(f"  SKIP {msg}")
        return None
    ok2, reason2 = foreground_ok()
    if not ok2:
        dated.unlink(missing_ok=True)
        msg = f"REFUSED after capture {canonical}: {reason2}"
        if required:
            raise SystemExit(msg)
        log(f"  SKIP {msg}")
        return None
    dest = MANUAL / canonical
    bak = dest.with_suffix(dest.suffix + f".bak-before-{date.today().isoformat()}")
    if dest.exists() and not bak.exists():
        shutil.copy2(dest, bak)
    shutil.copy2(dated, dest)
    if canonical == "12-trial-subscription.png":
        INTRO.mkdir(parents=True, exist_ok=True)
        intro = INTRO / "10-trial-pro.png"
        ibak = intro.with_suffix(intro.suffix + f".bak-before-{date.today().isoformat()}")
        if intro.exists() and not ibak.exists():
            shutil.copy2(intro, ibak)
        shutil.copy2(dated, intro)
    if NAS.exists():
        try:
            shutil.copy2(dated, NAS / canonical)
        except OSError as e:
            log(f"  NAS copy skipped: {e}")
    log(f"SHOT {canonical} ({dated.stat().st_size} bytes) — {note} [HHH verified]")
    return dest


def assert_ui(*need: str, label: str) -> bool:
    ok = has(*need)
    if not ok:
        log(f"  WARN {label}: expected UI markers {need}")
    return ok


def shot_web_companion() -> None:
    log("=== Web Companion (URL + pairing code) ===")
    tab("Tools")
    swipe_up(2)
    if not tap_label("Web Companion", "View on Big Screen"):
        swipe_up(2)
        tap_label("Web Companion")
    time.sleep(1.0)
    # Start if needed
    if has(r"Start Web Companion", r'text="Start"'):
        tap_label("Start Web Companion", "Start")
        time.sleep(2.5)
    assert_ui(r"Live dashboard", r"pairing|Enter this code|4-digit|Copy address|Copy code", label="WC")
    screencap("09-web-companion.png", "LAN URL + 4-digit pairing code (live)")


def shot_unlock_pro() -> None:
    log("=== Unlock Pro / trial paywall ===")
    tab("Settings")
    time.sleep(1.0)
    if not tap_label("Upgrade to Pro", "Upgrade"):
        swipe_up(1)
        tap_label("Upgrade to Pro", "Upgrade", "Subscribe")
    time.sleep(1.5)
    assert_ui(r"Unlock Pro|Subscribe|Annual|Monthly|74\.99|9\.99", label="paywall")
    screencap("12-trial-subscription.png", "Unlock Pro with $74.99/yr + $9.99/mo")


def shot_settings_sections() -> None:
    log("=== Settings sections (scroll captures) ===")
    back(2)
    tab("Settings")
    time.sleep(1.0)
    # Profile top already have as 10-settings; capture scrolled rows
    swipe_up(2)
    if tap_label("Theme", "Appearance"):
        time.sleep(1.0)
        screencap("10b-settings-theme.png", "Theme / appearance")
        back(1)
    swipe_up(1)
    if tap_label("Language"):
        time.sleep(1.0)
        screencap("10c-settings-language.png", "Language picker")
        back(1)
    swipe_up(2)
    if tap_label("Security", "App Lock", "Security & App Lock"):
        time.sleep(1.0)
        screencap("10d-settings-security.png", "Security & App Lock")
        # encryption status often on same screen
        if has(r"encryption|Not available|SQLCipher|Database"):
            screencap("10e-settings-encryption.png", "Database encryption status")
        back(1)
    swipe_up(1)
    if tap_label("Notifications"):
        time.sleep(1.0)
        screencap("10f-settings-notifications.png", "Notifications")
        back(1)
    # Refresh profile top keeper too
    tab("Settings")
    time.sleep(1.0)
    screencap("10-settings.png", "Profile / Settings top (trial badge)")


def shot_sample_loading() -> None:
    log("=== Sample loading (best-effort) ===")
    # If already in sample mode, clear first then re-enter path — heavy.
    # Prefer: open onboarding path if available, else capture clear-samples dialog path.
    tab("Home")
    time.sleep(1.0)
    if has(r"sample data", r"Clear samples"):
        log("  already in sample mode — capture Home banner as sample-active; loading needs reset")
        screencap("01-home-command-center.png", "Home with sample banner (refresh)")
        # Try clear flow for 26
        if tap_label("Clear samples"):
            time.sleep(1.0)
            screencap("26-clear-ludwig-sample.png", "Clear sample confirm")
            # Cancel to keep demo data for other shots
            if not tap_label("Cancel", "No"):
                back(1)
        return
    # Try start path from settings / more
    tab("Settings")
    swipe_up(3)
    if tap_label("Explore with sample", "sample collection", "Ludwig"):
        time.sleep(0.8)
        screencap("19-sample-loading.png", "Sample load / path (capture mid-flow)")
        return
    log("  SKIP sample loading — not in sample path; leave flagged for manual")


def shot_share_nearby() -> None:
    log("=== Share Nearby (QR + PIN) ===")
    tab("Tools")
    swipe_up(2)
    if not tap_label("Share Nearby", "Share & Connect", "Nearby"):
        swipe_up(2)
        tap_label("Share Nearby", "Share")
    time.sleep(1.5)
    # May need to pick share mode / item
    tap_label("Share", "QR", "Show QR", "Create")
    time.sleep(1.0)
    if has(r"QR|PIN|Share Nearby|Bluetooth"):
        screencap("27-share-nearby-qr-pin.png", "Share Nearby QR + PIN")
    else:
        screencap("27-share-nearby-entry.png", "Share Nearby entry (verify)")


def shot_demand_polish() -> None:
    log("=== Demand Rolodex polish ===")
    tab("Tools")
    swipe_up(1)
    if not tap_label("Demand Rolodex", "Rolodex"):
        swipe_up(2)
        tap_label("Demand Rolodex")
    time.sleep(1.2)
    screencap("23-demand-rolodex-board.png", "Demand board (5-tab chrome)")
    if tap_label("Send", "Send want", "Send to dealer"):
        time.sleep(1.0)
        screencap("21-demand-rolodex-send.png", "Send want list form")
        # If send produces QR/PIN, capture it
        if tap_label("Send want list", "Send list", "Continue", "Show QR"):
            time.sleep(1.5)
            if has(r"PIN|QR|digit"):
                screencap("21b-demand-rolodex-send-qr-pin.png", "Post-send PIN + QR")
        back(2)
    if tap_label("Receive", "Receive card"):
        time.sleep(1.0)
        screencap("22-demand-rolodex-receive.png", "Receive want card / PIN")
        back(1)


def shot_device_sync_offline() -> None:
    log("=== Device Sync + Offline Show Pack ===")
    tab("Tools")
    swipe_up(2)
    if tap_label("Device Sync", "Sync my devices", "Sync devices"):
        time.sleep(1.0)
        screencap("24-device-sync.png", "Device Sync")
        back(1)
    tab("Settings")
    swipe_up(3)
    if tap_label("Offline Show Pack", "Offline pack", "Show Pack"):
        time.sleep(1.0)
        screencap("25-offline-show-pack.png", "Offline Show Pack")
        back(1)


def main() -> None:
    STAGING.mkdir(parents=True, exist_ok=True)
    if LOG.exists():
        LOG.write_text("", encoding="utf-8")
    log(f"device={SERIAL} staging={STAGING}")
    wake_launch()
    if not has(r"Home|My Pieces|Tools|Settings|Command|Museum|Identify"):
        log("HHH UI not detected — check login/onboarding")
        # still try
    shot_web_companion()
    back(2)
    shot_unlock_pro()
    shot_settings_sections()
    shot_sample_loading()
    shot_share_nearby()
    back(3)
    shot_demand_polish()
    back(3)
    shot_device_sync_offline()
    # Return to Home
    tab("Home")
    log("DONE — review staging + manual keepers")


if __name__ == "__main__":
    main()
