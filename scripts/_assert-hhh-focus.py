#!/usr/bin/env python3
"""Guard: abort unless HHH is focused. Refuse Contacts/Dialer/Whisker."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
S = "R5CXC2K4Z8F"
PKG = "com.josspatech.handyhorology"
BAD = (
    "contacts",
    "dialer",
    "dialtacts",
    "whisker",
    "maestro",
    "com.samsung.android.dialer",
    "com.android.contacts",
    "com.samsung.android.app.contacts",
)


def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)


def focus_line() -> str:
    out = adb("shell", "dumpsys", "window").stdout
    for line in out.splitlines():
        if "mCurrentFocus" in line:
            return line.strip()
    return ""


def main() -> int:
    line = focus_line()
    print(line)
    low = line.lower()
    if any(b in low for b in BAD) and PKG not in low:
        print("REFUSE: not HHH (Contacts/Dialer/other) — do not screenshot")
        return 2
    if PKG not in line:
        print("REFUSE: HHH not focused")
        return 2
    print("OK: HHH focused")
    return 0


if __name__ == "__main__":
    sys.exit(main())
