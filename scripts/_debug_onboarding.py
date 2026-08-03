#!/usr/bin/env python3
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADB = Path(__import__("os").environ.get("LOCALAPPDATA", "")) / "Android/Sdk/platform-tools/adb.exe"
UI = ROOT / "assets/screenshots/hhh/_ui-dump.xml"
PKG = "com.josspatech.handyhorology"
SERIAL = "emulator-5554"


def adb(*args: str) -> None:
    subprocess.run([ADB, "-s", SERIAL, *args], check=False)


def ui() -> str:
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    return UI.read_text(encoding="utf-8", errors="ignore")


def tap(x: int, y: int, wait: float = 2.0) -> None:
    print(f"tap {x},{y}")
    adb("shell", "input", "tap", str(x), str(y))
    time.sleep(wait)


def tap_label(label: str) -> bool:
    xml = ui()
    for node in re.findall(r"<node[^>]+>", xml):
        if label not in node:
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if m:
            cx = (int(m.group(1)) + int(m.group(3))) // 2
            cy = (int(m.group(2)) + int(m.group(4))) // 2
            tap(cx, cy)
            return True
    print(f"miss {label!r}")
    return False


def main() -> None:
    adb("shell", "pm", "clear", PKG)
    time.sleep(2)
    for perm in ("android.permission.POST_NOTIFICATIONS", "android.permission.READ_MEDIA_IMAGES"):
        adb("shell", "pm", "grant", PKG, perm)
    adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
    time.sleep(18)
    tap_label("Continue") or tap(661, 2206)
    time.sleep(4)
    print("path screen")
    tap_label("Explore with sample collection") or tap(540, 1786, 15)
    time.sleep(5)
    xml = ui()
    print("Get Started" in xml, "COMMAND CENTER" in xml, "Hunt" in xml)
    tap_label("Get Started") or tap(661, 2206, 20)
    xml = ui()
    for label in ("COMMAND CENTER", "Hunt", "Home", "My Pieces", "Get Started", "Explore", "horology companion"):
        print(label, label in xml)
    texts = re.findall(r'text="([^"]{2,80})"', xml)
    for t in texts[:25]:
        print(" ", t.replace("&#10;", " "))


if __name__ == "__main__":
    main()
