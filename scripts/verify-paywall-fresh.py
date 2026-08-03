#!/usr/bin/env python3
"""Reliable Upgrade-to-Pro check: delete UI xml before dump; verify via screencap."""
import os, re, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ADB = os.path.join(os.environ["LOCALAPPDATA"], "Android", "Sdk", "platform-tools", "adb.exe")
S = "R5CXC2K4Z8F"
XML = r"C:\Users\jossp\Documents\GitHub\josspatech.github.io\assets\screenshots\hhh\_ui.xml"
OUT = r"C:\Users\jossp\Documents\GitHub\josspatech.github.io\assets\screenshots\hhh\_capture_2026-07-24"
PKG = "com.josspatech.handyhorology"

def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)

def ui():
    # Force fresh dump — stale /sdcard/ui.xml caused false ErrorBoundary reads
    adb("shell", "rm", "-f", "/sdcard/ui.xml")
    try:
        os.remove(XML)
    except OSError:
        pass
    r = adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    if r.returncode != 0:
        print("DUMP FAIL", r.stderr or r.stdout)
    adb("pull", "/sdcard/ui.xml", XML)
    if not os.path.exists(XML) or os.path.getsize(XML) < 50:
        raise RuntimeError("UI dump missing/empty")
    return open(XML, encoding="utf-8", errors="ignore").read()

def shot(name):
    path = os.path.join(OUT, name)
    adb("shell", "screencap", "-p", "/sdcard/shot.png")
    adb("pull", "/sdcard/shot.png", path)
    print(f"shot {name} bytes={os.path.getsize(path)}")
    return path

def tap_label(label, prefer_bottom=False):
    xml = ui()
    best = None
    for node in re.findall(r"<node[^>]+>", xml):
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        if text != label and desc != label and label.lower() not in f"{text} {desc}".lower():
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        cx, cy = (l + r) // 2, (t + b) // 2
        score = cy if prefer_bottom else -abs(cy - 400)
        if best is None or (prefer_bottom and cy > best[1]) or (not prefer_bottom and score > best[2]):
            best = (cx, cy, score, text, desc)
    if not best:
        print("MISS", label)
        return False
    print(f"TAP {label!r} @ {best[0]},{best[1]} text={best[3]!r} desc={best[4]!r}")
    adb("shell", "input", "tap", str(best[0]), str(best[1]))
    time.sleep(2)
    return True

def main():
    texts = [t for t in re.findall(r'text="([^"]+)"', ui()) if t.strip()]
    print("start texts:", texts[:25])
    if "Something went wrong" in " ".join(texts):
        print("WARN: dump still shows error — trusting screencap")
    shot("upgrade-start.png")
    tap_label("Settings", prefer_bottom=True)
    time.sleep(1)
    shot("upgrade-settings.png")
    texts = [t for t in re.findall(r'text="([^"]+)"', ui()) if t.strip()]
    print("settings texts:", [t for t in texts if any(k in t for k in ("Upgrade", "Pro", "trial", "Theme", "Settings", "Unlock"))][:20])
    if not tap_label("Upgrade to Pro"):
        tap_label("Upgrade")
    time.sleep(2)
    shot("upgrade-paywall.png")
    texts = [t for t in re.findall(r'text="([^"]+)"', ui()) if t.strip()]
    print("AFTER texts:")
    for t in texts:
        print(" -", t)
    joined = " ".join(texts)
    print("has_error", "unexpected error" in joined.lower())
    print("has_paywall", any(k in joined for k in ("Unlock Pro", "Subscribe Now", "Annual", "Monthly", "74.99", "9.99")))

if __name__ == "__main__":
    main()
