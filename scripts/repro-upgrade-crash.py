#!/usr/bin/env python3
"""Reproduce GlassPaywall crash from Settings -> Upgrade to Pro."""
import os
import re
import subprocess
import time

ADB = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Android", "Sdk", "platform-tools", "adb.exe")
S = "R5CXC2K4Z8F"
XML = r"C:\Users\jossp\Documents\GitHub\josspatech.github.io\assets\screenshots\hhh\_ui.xml"
PKG = "com.josspatech.handyhorology"


def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)


def ui():
    adb("shell", "rm", "-f", "/sdcard/ui.xml")
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", XML)
    return open(XML, encoding="utf-8", errors="ignore").read()


def tap_label(label, require_hhh=True):
    xml = ui()
    if require_hhh and PKG not in adb("shell", "dumpsys", "window").stdout:
        print("NOT_HHH")
        return False
    for node in re.findall(r"<node[^>]+>", xml):
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        hay = f"{text} {desc}".lower()
        if label.lower() not in hay:
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        cx = (int(m.group(1)) + int(m.group(3))) // 2
        cy = (int(m.group(2)) + int(m.group(4))) // 2
        if cy < 90:
            continue
        print(f"tap {label!r} @ {cx},{cy}")
        adb("shell", "input", "tap", str(cx), str(cy))
        time.sleep(1.8)
        return True
    print(f"miss {label!r}")
    return False


def main():
    adb("logcat", "-c")
    adb("shell", "am", "force-stop", PKG)
    time.sleep(1)
    adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
    time.sleep(5)
    tap_label("Settings")
    time.sleep(1)
    tap_label("Upgrade to Pro")
    time.sleep(3)
    xml = ui()
    texts = [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]
    print("unexpected_error", "unexpected error" in xml.lower())
    print("texts:", texts[:50])
    # JS / React Native logs
    logs = adb("logcat", "-d", "-t", "300").stdout
    keys = ("ErrorBoundary", "GlassPaywall", "TypeError", "ReactNativeJS", "Invariant", "undefined is not")
    for line in logs.splitlines():
        if any(k in line for k in keys):
            print("LOG:", line[:300])


if __name__ == "__main__":
    main()
