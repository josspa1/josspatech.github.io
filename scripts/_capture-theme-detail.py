#!/usr/bin/env python3
"""Open Theme detail and stage candidate only after breadcrumb confirms."""
import re, subprocess, time
from pathlib import Path

ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
S = "R5CXC2K4Z8F"
ST = Path(__file__).resolve().parents[1] / "assets/screenshots/hhh/_capture_verify"
UI = ST / "_ui.xml"


def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)


def dump():
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    return UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""


def texts(xml):
    return [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip() and not t.startswith("&#")]


def find(xml, label):
    for node in re.findall(r"<node[^>]+>", xml):
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        if label.lower() not in f"{text} {desc}".lower():
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        cy = (t + b) // 2
        if 200 < cy < 2800:
            return (l + r) // 2, cy, text or desc
    return None


adb("shell", "am", "force-stop", "dev.mobile.maestro")
adb("shell", "input", "tap", "1260", "2920")
time.sleep(1.5)
for _ in range(10):
    adb("shell", "input", "swipe", "720", "900", "720", "2300", "260")
    time.sleep(0.3)
time.sleep(0.8)
xml = dump()
hit = find(xml, "Theme")
print("hit", hit)
if not hit:
    raise SystemExit("Theme not found")
adb("shell", "input", "tap", str(hit[0]), str(hit[1]))
time.sleep(2.2)
xml2 = dump()
t = texts(xml2)
print("after tap:", t[:40])
joined = " ".join(t)
# Accept if we see theme options OR breadcrumb Language/Theme detail markers
ok = any(k in joined for k in ("Light", "Dark", "System", "Appearance", "theme")) and (
    "Upgrade to Pro" not in joined or "Light" in joined or "Dark" in joined
)
# Stronger: look for radio options
strong = any(k in joined for k in ("Always light", "Always dark", "Match system", "Light", "Dark"))
print("ok", ok, "strong", strong)
adb("shell", "screencap", "-p", "/sdcard/hhh-shot.png")
dest = ST / "10c-settings-theme-detail.CANDIDATE.png"
adb("pull", "/sdcard/hhh-shot.png", str(dest))
(ST / "10c-settings-theme-detail.CANDIDATE_texts.txt").write_text("\n".join(t), encoding="utf-8")
print("STAGED", dest.name, dest.stat().st_size)
