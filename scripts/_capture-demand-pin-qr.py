#!/usr/bin/env python3
"""Demand → fill → Share all → real Send button → Share PIN+QR. Focus-guarded."""
from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
S = "R5CXC2K4Z8F"
PKG = "com.josspatech.handyhorology"
ST = Path(__file__).resolve().parents[1] / "assets/screenshots/hhh/_capture_verify"
UI = ST / "_ui.xml"
BAD = ("dialer", "contacts", "whisker", "maestro", "dialtacts")


def adb(*a):
    return subprocess.run([ADB, "-s", S, *a], capture_output=True, text=True)


def focus_ok() -> bool:
    line = next((l for l in adb("shell", "dumpsys", "window").stdout.splitlines() if "mCurrentFocus" in l), "")
    low = line.lower()
    return PKG in line and not any(b in low for b in BAD)


def assert_hhh(step: str) -> None:
    if not focus_ok():
        line = next((l for l in adb("shell", "dumpsys", "window").stdout.splitlines() if "mCurrentFocus" in l), "?")
        raise SystemExit(f"ABORT {step}: {line.strip()}")


def dump() -> str:
    assert_hhh("dump")
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    adb("pull", "/sdcard/ui.xml", str(UI))
    return UI.read_text(encoding="utf-8", errors="ignore") if UI.exists() else ""


def texts(xml: str):
    return [t for t in re.findall(r'text="([^"]+)"', xml) if t.strip() and not t.startswith("&#")]


def find(xml, *labels, min_y=150, max_y=2700, prefer_exact=None, require_class=None):
    best = None
    for node in re.findall(r"<node[^>]+>", xml):
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        cls = (re.search(r'class="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        hay = f"{text} {desc}"
        if not any(lab.lower() in hay.lower() for lab in labels):
            continue
        if "EditText" in cls and require_class != "EditText":
            continue
        if require_class and require_class not in cls:
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        cx, cy = (l + r) // 2, (t + b) // 2
        if cy < min_y or cy > max_y:
            continue
        label = text or desc
        score = -abs(cy - 1600) + (r - l) // 10
        if prefer_exact and prefer_exact.lower() == label.lower():
            score += 10000
        if best is None or score > best[2]:
            best = (cx, cy, score, label)
    return best


def find_class_a11y(xml, a11y_label: str, cls_substr: str):
    for node in re.findall(r"<node[^>]+>", xml):
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        cls = (re.search(r'class="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        if cls_substr not in cls:
            continue
        if a11y_label.lower() not in f"{text} {desc}".lower():
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        return ((l + r) // 2, (t + b) // 2, 0, text or desc)
    return None


def find_tab(xml, name):
    for node in re.findall(r"<node[^>]+>", xml):
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        if name not in desc:
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        if (t + b) // 2 < 2700:
            continue
        return ((l + r) // 2, (t + b) // 2, 0, desc)
    return None


def tap(hit, wait=1.6, step="tap"):
    if hit is None:
        raise SystemExit(f"missing hit for {step}")
    print(f"{step}: {hit[3]!r} @ {hit[0]},{hit[1]}")
    adb("shell", "input", "tap", str(hit[0]), str(hit[1]))
    time.sleep(wait)
    assert_hhh(step)


def scroll_until(label: str, max_swipes=8, **kwargs):
    for i in range(max_swipes):
        xml = dump()
        hit = find(xml, label, prefer_exact=label, **kwargs)
        if hit and label.lower() in (hit[3] or "").lower():
            return hit
        print(f"scroll for {label} #{i+1}")
        adb("shell", "input", "swipe", "720", "2300", "720", "900", "350")
        time.sleep(0.7)
    return find(dump(), label, prefer_exact=label, **kwargs)


def shot(name):
    assert_hhh("shot")
    adb("shell", "screencap", "-p", "/sdcard/hhh-shot.png")
    dest = ST / name
    adb("pull", "/sdcard/hhh-shot.png", str(dest))
    (ST / name.replace(".png", "_texts.txt")).write_text("\n".join(texts(dump())[:100]), encoding="utf-8")
    print(f"STAGED {name} ({dest.stat().st_size})")


# We're already on the form from last run — restart cleanly
adb("shell", "am", "force-stop", "com.samsung.android.dialer")
adb("shell", "am", "force-stop", PKG)
time.sleep(0.5)
adb("shell", "am", "start", "-n", f"{PKG}/.MainActivity")
time.sleep(3.5)
assert_hhh("launch")

xml = dump()
tap(find_tab(xml, "Tools"), 2.0, "Tools")
tap(scroll_until("Demand Rolodex"), 2.2, "Demand Rolodex")
tap(find(dump(), "Send to a dealer"), 2.2, "Send to a dealer")

xml = dump()
# Name — if not Ludwig already, type it
if "Ludwig" not in " ".join(texts(xml)):
    name_field = None
    for node in re.findall(r"<node[^>]+>", xml):
        cls = (re.search(r'class="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        if "EditText" not in cls:
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        cy = (t + b) // 2
        if 200 < cy < 1400:
            name_field = ((l + r) // 2, cy, 0, "EditText")
            break
    tap(name_field, 0.6, "name field")
    adb("shell", "input", "text", "Ludwig")
    time.sleep(0.5)

# Share all Switch (not the label)
sw = find_class_a11y(dump(), "Share all", "Switch")
if not sw:
    # scroll to Share all
    for i in range(4):
        sw = find_class_a11y(dump(), "Share all", "Switch")
        if sw:
            break
        adb("shell", "input", "swipe", "720", "2200", "720", "1100", "350")
        time.sleep(0.6)
tap(sw, 0.9, "Share all switch")

# Confirm at least one checkbox checked
xml = dump()
checked = [n for n in re.findall(r"<node[^>]+>", xml) if 'checked="true"' in n and "CheckBox" in n]
print(f"checked boxes: {len(checked)}")
if not checked:
    # tap first wish checkbox
    hit = find_class_a11y(xml, "Patek", "CheckBox") or find(xml, "Patek Philippe")
    tap(hit, 0.8, "first want")

# Scroll until Send want list BUTTON is below header (y>400) — prefer clickable button-sized
send_hit = None
for i in range(8):
    xml = dump()
    for node in re.findall(r"<node[^>]+>", xml):
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        if (text or desc) != "Send want list":
            continue
        clickable = 'clickable="true"' in node
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        cy = (t + b) // 2
        # Header crumb is ~y 220; real button is mid/lower
        if cy < 500:
            continue
        # Prefer larger / clickable
        score = (r - l) * (b - t) + (10000 if clickable else 0)
        cand = ((l + r) // 2, cy, score, text or desc)
        if send_hit is None or score > send_hit[2]:
            send_hit = cand
    if send_hit:
        break
    print(f"scroll for Send button #{i+1}")
    adb("shell", "input", "swipe", "720", "2300", "720", "900", "350")
    time.sleep(0.7)

if not send_hit:
    raise SystemExit("Send want list button not found below header")
tap(send_hit, 3.0, "Send want list button")

# Dismiss alert if needWants / error
xml = dump()
joined = " ".join(texts(xml))
if "OK" in texts(xml) and ("want" in joined.lower() or "error" in joined.lower() or "name" in joined.lower()):
    print("ALERT:", texts(xml)[:20])
    hit = find(xml, "OK", prefer_exact="OK")
    if hit:
        tap(hit, 1.0, "dismiss alert")
    raise SystemExit("Send failed with alert — fix selection/name")

# Scroll to Share PIN section
ok = False
for i in range(8):
    xml = dump()
    tlist = texts(xml)
    joined = " ".join(tlist)
    print(f"post-send #{i}:", tlist[:40])
    if "Share PIN" in joined:
        ok = True
        # try to bring PIN+QR into frame
        if "Show this PIN" in joined or re.search(r"\b\d{4}\b", joined):
            break
        adb("shell", "input", "swipe", "720", "2200", "720", "1100", "350")
        time.sleep(0.7)
        continue
    adb("shell", "input", "swipe", "720", "2300", "720", "900", "350")
    time.sleep(0.7)

if not ok:
    raise SystemExit("Share PIN not on screen — abort (no promote)")

shot("21b-demand-pin-qr.CANDIDATE.png")
final = Path(ST / "21b-demand-pin-qr.CANDIDATE_texts.txt").read_text(encoding="utf-8")
if "Share PIN" not in final:
    raise SystemExit("candidate texts missing Share PIN")
print("OK candidate has Share PIN")
