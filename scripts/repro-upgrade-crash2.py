#!/usr/bin/env python3
"""Force Settings -> Upgrade and capture ReactNativeJS errors."""
import os, re, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ADB = os.path.join(os.environ["LOCALAPPDATA"], "Android", "Sdk", "platform-tools", "adb.exe")
S = "R5CXC2K4Z8F"
XML = r"C:\Users\jossp\Documents\GitHub\josspatech.github.io\assets\screenshots\hhh\_ui.xml"
PKG = "com.josspatech.handyhorology"

def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)

def ui():
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", XML)
    return open(XML, encoding="utf-8", errors="ignore").read()

def focus_pkg():
    out = adb("shell", "dumpsys", "window").stdout
    for line in out.splitlines():
        if "mCurrentFocus" in line or "mFocusedApp" in line:
            if PKG in line:
                return True
    return False

def tap_exact(label: str) -> bool:
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
        score = cy if label == "Settings" else -abs(cy - 400)
        if best is None or (label == "Settings" and cy > best[1]) or (label != "Settings" and score > best[2]):
            best = (cx, cy, score, text, desc, (l, t, r, b))
    if not best:
        print("MISS", label)
        return False
    cx, cy = best[0], best[1]
    print(f"TAP {label!r} @ {cx},{cy} text={best[3]!r} desc={best[4]!r} bounds={best[5]}")
    adb("shell", "input", "tap", str(cx), str(cy))
    time.sleep(2)
    return True

def swipe_up():
    adb("shell", "input", "swipe", "540", "1600", "540", "700", "300")
    time.sleep(0.8)

def main():
    adb("logcat", "-c")
    adb("shell", "am", "force-stop", PKG)
    time.sleep(1)
    adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
    time.sleep(5)
    if not focus_pkg():
        print("FAILED to focus HHH")
        return
    tap_exact("Settings")
    time.sleep(1.5)
    xml = ui()
    texts = [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]
    print("settings texts:", texts[:40])
    if "Upgrade to Pro" not in texts:
        for _ in range(4):
            swipe_up()
            xml = ui()
            texts = [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]
            if "Upgrade to Pro" in texts:
                break
        print("after scroll:", [t for t in texts if "Pro" in t or "Upgrade" in t or "trial" in t.lower()])
    tap_exact("Upgrade to Pro")
    time.sleep(3)
    xml = ui()
    texts = [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip()]
    print("AFTER UPGRADE texts:")
    for t in texts:
        print(" -", t)
    joined = " ".join(texts)
    print("has_error", any("unexpected" in t.lower() or "something went wrong" in t.lower() for t in texts))
    print("has_paywall", any(k in joined for k in ("Unlock Pro", "Subscribe Now", "Annual", "Monthly", "$74.99", "$9.99")))
    logs = adb("logcat", "-d", "-t", "400").stdout
    for line in logs.splitlines():
        if any(k in line for k in (
            "ReactNativeJS", "ErrorBoundary", "GlassPaywall", "TypeError",
            "Invariant", "undefined is not", "is not a function",
            "RangeError", "Maximum call", "BlurView", "paywall"
        )):
            print("LOG:", line[:400])

if __name__ == "__main__":
    main()
