#!/usr/bin/env python3
"""Continue HHH audit captures — only when HHH is verified in foreground."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "cap",
    ROOT / "scripts" / "capture-hhh-audit-shots-2026-07-24.py",
)
cap = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(cap)


def main() -> None:
    cap.wake_launch()

    # --- Web Companion: scroll so 4-digit code is visible ---
    cap.log("=== RETAKE Web Companion (show pairing code) ===")
    cap.tab("Tools")
    cap.swipe_up(2)
    cap.tap_label("Web Companion")
    cap.time.sleep(1.2)
    if cap.has(r"Start Web Companion"):
        cap.tap_label("Start Web Companion", "Start")
        cap.time.sleep(2.5)
    # Scroll within WC so code + buttons show
    cap.swipe_up(1)
    cap.time.sleep(0.8)
    if not cap.has(r"Enter this code|Copy code|pairing|Code copied|[0-9]{4}"):
        cap.swipe_up(1)
    cap.assert_ui(r"Live dashboard|Open this address|Enter this code|Copy address", label="WC")
    cap.screencap("09-web-companion.png", "WC with address + pairing code visible")

    # --- Unlock Pro paywall (must see Unlock Pro / Annual) ---
    cap.log("=== RETAKE Unlock Pro paywall ===")
    cap.back(2)
    cap.tab("Settings")
    cap.time.sleep(1.0)
    # Prefer subscription row
    if not cap.tap_label("Upgrade to Pro"):
        cap.swipe_up(1)
        cap.tap_label("Upgrade to Pro")
    cap.time.sleep(2.5)
    # If still on Settings, try again
    if not cap.has(r"Unlock Pro|Subscribe Now|Annual|BEST VALUE|74\.99|9\.99"):
        cap.log("  paywall not open — retry Upgrade")
        cap.tap_label("Upgrade to Pro")
        cap.time.sleep(3.0)
    if not cap.has(r"Unlock Pro|Subscribe Now|Annual|BEST VALUE"):
        cap.log("  WARN: paywall still not detected — capture whatever is on screen for review only to staging")
        # Stage-only path: temporary name so we don't overwrite good mock with Settings again
        cap.screencap("12-trial-subscription-ATTEMPT.png", "paywall attempt (review)", required=False)
    else:
        cap.screencap("12-trial-subscription.png", "Unlock Pro paywall live")

    # --- Settings Theme (exact) ---
    cap.log("=== Settings Theme / Language / Security ===")
    cap.back(2)
    cap.tab("Settings")
    cap.time.sleep(1.0)
    # Theme is visible on Settings root per prior shot
    if cap.tap_label("Theme", partial=False) or cap.tap_label("Theme"):
        cap.time.sleep(1.0)
        if cap.focus_pkg() == cap.PKG:
            cap.screencap("10b-settings-theme.png", "Theme settings")
        cap.back(1)
    cap.swipe_up(2)
    if cap.tap_label("Language", partial=False) or cap.tap_label("Language"):
        cap.time.sleep(1.0)
        if cap.focus_pkg() == cap.PKG and not cap.has(r"Whisker"):
            cap.screencap("10c-settings-language.png", "Language")
        cap.back(1)
    cap.swipe_up(2)
    if cap.tap_label("Security & App Lock", "App Lock", "Security"):
        cap.time.sleep(1.2)
        if cap.focus_pkg() == cap.PKG:
            cap.screencap("10d-settings-security.png", "Security & App Lock")
            if cap.has(r"encryption|Not available|Database"):
                cap.screencap("10e-settings-encryption.png", "Encryption status")
        cap.back(1)
    # Notifications — exact HHH settings row only (avoid OS / Whisker)
    cap.swipe_up(1)
    if cap.tap_label("Notifications", partial=False):
        cap.time.sleep(1.0)
        if cap.focus_pkg() == cap.PKG and cap.has(r"Grail|eBay|reminder|Notification"):
            cap.screencap("10f-settings-notifications.png", "HHH Notifications")
        else:
            cap.log("  skipped Notifications — left HHH or wrong screen")
            cap.back(1)

    # Refresh settings top
    cap.back(2)
    cap.tab("Settings")
    cap.time.sleep(1.0)
    cap.screencap("10-settings.png", "Settings top / trial badge")

    # Share Nearby + Demand + Device Sync + Offline
    cap.shot_share_nearby()
    cap.back(3)
    cap.ensure_hhh_foreground() if hasattr(cap, "ensure_hhh_foreground") else None
    if cap.focus_pkg() != cap.PKG:
        cap.wake_launch()
    cap.shot_demand_polish()
    cap.back(3)
    if cap.focus_pkg() != cap.PKG:
        cap.wake_launch()
    cap.shot_device_sync_offline()
    cap.tab("Home")
    cap.log("CONTINUE DONE")


if __name__ == "__main__":
    main()
