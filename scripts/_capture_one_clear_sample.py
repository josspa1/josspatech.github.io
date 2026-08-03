#!/usr/bin/env python3
"""Capture Clear-samples confirm dialog into staging (stay in HHH)."""
import os
import sys
import time
from pathlib import Path
from importlib.machinery import SourceFileLoader

os.environ["ANDROID_SERIAL"] = os.environ.get("ANDROID_SERIAL", "R5CXC2K4Z8F")
mod = SourceFileLoader(
    "cap",
    str(Path(__file__).resolve().parent / "capture-hhh-phone-priority-shots.py"),
).load_module()

mod.wake_and_launch()
mod.go_home()
ok, reason = mod.foreground_ok()
print("home:", ok, reason)
if not ok:
    raise SystemExit(1)

if not mod.tap_label("Clear samples", partial=True):
    print("MISS Clear samples")
    raise SystemExit(2)
time.sleep(1.2)
ok, reason = mod.foreground_ok()
print("after tap:", ok, reason)
# Dialog may not match positive markers — allow alert with Cancel/Clear
xml = mod.ui()
if not (
    mod.has(r"Clear|Remove|sample|Ludwig|Cancel|Exploring")
    or "Clear samples" in xml
):
    print("unexpected UI after Clear samples")
    raise SystemExit(3)

path = mod.shot("26-clear-ludwig-sample", allow_dialog=True)
# Cancel so we don't wipe demo mid-session
mod.tap_label("Cancel", "No", "Keep", "Keep samples", partial=True)
time.sleep(0.8)
print("result:", path)
