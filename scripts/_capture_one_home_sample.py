#!/usr/bin/env python3
"""Capture one verified in-app Home sample shot into staging only."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ["ANDROID_SERIAL"] = os.environ.get("ANDROID_SERIAL", "R5CXC2K4Z8F")

from importlib.machinery import SourceFileLoader

mod = SourceFileLoader(
    "cap",
    str(Path(__file__).resolve().parent / "capture-hhh-phone-priority-shots.py"),
).load_module()

mod.wake_and_launch()
mod.dismiss_noise()
ok, reason = mod.foreground_ok()
print("foreground:", ok, reason)
if not ok:
    raise SystemExit(1)
mod.go_home()
ok, reason = mod.foreground_ok()
print("home:", ok, reason)
path = mod.shot("19-sample-loading")
print("result:", path)
