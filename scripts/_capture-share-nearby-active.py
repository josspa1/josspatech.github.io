#!/usr/bin/env python3
"""Open Share Nearby with a Museum piece selected → QR+PIN if available."""
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


def find(xml, *labels, refuse=("whisker",)):
    best = None
    for node in re.findall(r"<node[^>]+>", xml):
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        hay = f"{text} {desc}"
        if any(r in hay.lower() for r in refuse):
            continue
        if not any(lab.lower() in hay.lower() for lab in labels):
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        cx, cy = (l + r) // 2, (t + b) // 2
        if cy < 180 or cy > 2850:
            continue
        score = -abs(cy - 1400)
        if best is None or score > best[2]:
            best = (cx, cy, score, text or desc)
    return best


def tap_hit(hit, wait=1.6):
    print(f"tap {hit[3]!r} @ {hit[0]},{hit[1]}")
    adb("shell", "input", "tap", str(hit[0]), str(hit[1]))
    time.sleep(wait)


def shot(name):
    adb("shell", "screencap", "-p", "/sdcard/hhh-shot.png")
    dest = ST / name
    adb("pull", "/sdcard/hhh-shot.png", str(dest))
    (ST / name.replace(".png", "_texts.txt")).write_text("\n".join(texts(dump())[:80]), encoding="utf-8")
    print(f"STAGED {name} ({dest.stat().st_size})")


adb("shell", "am", "force-stop", "dev.mobile.maestro")
# My Museum
adb("shell", "input", "tap", "540", "2920")
time.sleep(2)
xml = dump()
print("museum texts:", texts(xml)[:25])
# tap first piece-ish card — look for a brand or price or known demo names
hit = None
for label in ("Omega", "Rolex", "Hamilton", "Seamaster", "Tissot", "Audemars", "$", "Pieces"):
    hit = find(xml, label)
    if hit and label != "Pieces":
        break
if not hit:
    # fallback tap mid-list
    print("fallback mid list tap")
    adb("shell", "input", "tap", "720", "1100")
    time.sleep(2)
else:
    tap_hit(hit, 2.2)

xml = dump()
print("detail texts:", texts(xml)[:30])
# look for Share Nearby on piece detail / overflow
hit = find(xml, "Share Nearby", "Share", "Nearby")
if hit:
    tap_hit(hit, 2)
else:
    # Tools → search Share Nearby (piece selection may persist)
    adb("shell", "input", "tap", "900", "2920")
    time.sleep(1.5)
    xml = dump()
    hit = find(xml, "Find a tool", "Search")
    if hit:
        tap_hit(hit, 0.8)
        adb("shell", "input", "text", "Share")
        time.sleep(1.2)
    xml = dump()
    hit = find(xml, "Share Nearby")
    if hit:
        tap_hit(hit, 2)

xml = dump()
t = texts(xml)
joined = " ".join(t)
print("share screen:", t[:40])
has_pin = bool(re.search(r"\b\d{4}\b", joined)) or "PIN" in joined.upper()
has_qr = "QR" in joined.upper() or "Show this" in joined or "dealer" in joined.lower()
print("has_pin", has_pin, "has_qr_hint", has_qr)
shot("27b-share-nearby-active.CANDIDATE.png")
