#!/usr/bin/env python3
"""Capture selective sales-visible Tools screens → _capture_verify/*.CANDIDATE.png"""
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
ST.mkdir(parents=True, exist_ok=True)

# (filename, search/tap labels on Tools hub, optional post-open labels to wait for)
SHOTS = [
    ("28-ebay-listings", ["Browse eBay", "eBay Listings", "Ebay Listings"], ["eBay", "Brand", "Search", "Browse"]),
    ("29-trade-analyzer", ["Is This Trade Fair?", "Is This Trade Fair", "Trade Analyzer"], ["Trade", "Your", "Their", "cash", "Fair"]),
    ("30-ai-chat", ["Horology Coach", "Ask the Expert", "AI Chat"], ["Coach", "Ask", "Chat", "message", "Horology", "Expert"]),
    ("31-photo-coach", ["Photo Coach", "Photo Studio"], ["Photo", "Coach", "Dial", "Case", "Studio", "shot", "checklist"]),
    ("33-print-export", ["Print & Export List", "Print and Export", "Print & Export"], ["Print", "Export", "PDF", "Museum", "Wish"]),
    ("34-lan-report", ["Museum Report", "View on Big Screen", "LAN Report", "Big Screen"], ["Museum Report", "LAN", "Big", "slideshow", "Start", "TV", "HTML", "Wi"]),
]


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


def find(xml, *labels, min_y=150, max_y=2700, prefer_exact=None):
    best = None
    for node in re.findall(r"<node[^>]+>", xml):
        text = (re.search(r'text="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        desc = (re.search(r'content-desc="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        cls = (re.search(r'class="([^"]*)"', node) or type("X", (), {"group": lambda s, n=1: ""})()).group(1)
        if "EditText" in cls:
            continue
        hay = f"{text} {desc}"
        if not any(lab.lower() in hay.lower() for lab in labels):
            continue
        m = re.search(r'bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"', node)
        if not m:
            continue
        l, t, r, b = map(int, m.groups())
        cx, cy = (l + r) // 2, (t + b) // 2
        if cy < min_y or cy > max_y:
            continue
        label = text or desc
        score = -abs(cy - 1500) + (r - l) // 10
        if prefer_exact and any(prefer_exact.lower() == (x or "").lower() for x in (text, desc)):
            score += 10000
        if best is None or score > best[2]:
            best = (cx, cy, score, label)
    return best


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
        raise SystemExit(f"missing {step}")
    safe = (hit[3] or "").encode("ascii", "replace").decode("ascii")
    print(f"{step}: {safe!r} @ {hit[0]},{hit[1]}")
    adb("shell", "input", "tap", str(hit[0]), str(hit[1]))
    time.sleep(wait)
    assert_hhh(step)


def back_to_tools():
    for _ in range(4):
        xml = dump()
        joined = " ".join(texts(xml)).lower()
        if "find a tool" in joined or ("tools" in joined and "compare" in joined):
            return
        adb("shell", "input", "keyevent", "KEYCODE_BACK")
        time.sleep(0.9)
        assert_hhh("back")
    tap(find_tab(dump(), "Tools"), 1.8, "Tools tab recover")


def scroll_find(labels, max_swipes=10):
    for i in range(max_swipes):
        xml = dump()
        for lab in labels:
            hit = find(xml, lab, prefer_exact=lab)
            if hit and lab.lower() in (hit[3] or "").lower():
                return hit
        hit = find(xml, *labels)
        if hit:
            return hit
        print(f"  scroll #{i+1} for {labels[0]}")
        adb("shell", "input", "swipe", "720", "2300", "720", "900", "350")
        time.sleep(0.65)
    return find(dump(), *labels)


def dismiss_paywall_if_any():
    xml = dump()
    joined = " ".join(texts(xml))
    if "Unlock Pro" in joined or "Upgrade to Pro" in joined or "$74.99" in joined:
        print("  paywall — trying Simulate / close")
        for lab in ("Simulate Premium", "Not now", "Close", "Maybe later", "X"):
            hit = find(xml, lab)
            if hit:
                tap(hit, 1.2, f"dismiss {lab}")
                return True
        # back out of paywall
        adb("shell", "input", "keyevent", "KEYCODE_BACK")
        time.sleep(1.0)
        return True
    return False


def shot(name: str):
    assert_hhh("shot")
    adb("shell", "screencap", "-p", "/sdcard/hhh-shot.png")
    dest = ST / f"{name}.CANDIDATE.png"
    adb("pull", "/sdcard/hhh-shot.png", str(dest))
    tlist = texts(dump())
    (ST / f"{name}.CANDIDATE_texts.txt").write_text("\n".join(tlist[:100]), encoding="utf-8")
    print(f"STAGED {dest.name} ({dest.stat().st_size})")
    return tlist


adb("shell", "cmd", "statusbar", "collapse")
adb("shell", "am", "force-stop", "com.samsung.android.dialer")
adb("shell", "am", "start", "-n", f"{PKG}/.MainActivity")
time.sleep(3.5)
assert_hhh("launch")
tap(find_tab(dump(), "Tools"), 2.0, "Tools")

results = {}
for fname, labels, expect in SHOTS:
    print(f"\n=== {fname} ===")
    back_to_tools()
    # scroll to top first
    for _ in range(3):
        adb("shell", "input", "swipe", "720", "900", "720", "2300", "300")
        time.sleep(0.4)
    hit = scroll_find(labels)
    if not hit:
        print(f"FAIL not found: {labels}")
        results[fname] = "NOT_FOUND"
        continue
    tap(hit, 2.2, labels[0])
    time.sleep(0.8)
    if dismiss_paywall_if_any():
        # if still on paywall after dismiss attempt, skip
        joined = " ".join(texts(dump()))
        if "Unlock Pro" in joined or "$74.99" in joined:
            print("FAIL still on paywall")
            results[fname] = "PAYWALL"
            adb("shell", "input", "keyevent", "KEYCODE_BACK")
            time.sleep(0.8)
            continue
    tlist = shot(fname)
    joined = " ".join(tlist)
    ok = any(e.lower() in joined.lower() for e in expect)
    # reject Tools hub
    if "Find a tool" in joined and "Compare Pieces" in joined and fname not in (""):
        # might still be hub if navigation failed
        if not any(e.lower() in joined.lower() for e in expect[:2]):
            print("WARN may still be Tools hub")
            results[fname] = "MAYBE_HUB"
            continue
    results[fname] = "OK" if ok else "WEAK"
    print(f"  verify={results[fname]} texts={ [x.encode('ascii','replace').decode('ascii') for x in tlist[:12]] }")

# Digital ID from piece detail (Watch Passport)
print("\n=== 32-digital-id-card ===")
tap(find_tab(dump(), "My Museum"), 2.0, "My Museum")
xml = dump()
hit = find(xml, "Speedmaster", "Omega", "Rolex", "Seiko")
if not hit:
    adb("shell", "input", "swipe", "720", "2200", "720", "1200", "350")
    time.sleep(0.8)
    hit = find(dump(), "Speedmaster", "Omega", "Rolex", "Seiko", "Tissot")
if hit:
    tap(hit, 2.2, "open piece")
    # look for Digital ID / Passport / Share menu
    for label in ("Digital ID", "ID Card", "Passport", "Proof of ownership", "Watch Passport"):
        hit = find(dump(), label)
        if hit:
            tap(hit, 2.2, label)
            break
    else:
        # scroll piece actions
        for _ in range(3):
            adb("shell", "input", "swipe", "720", "2200", "720", "1100", "350")
            time.sleep(0.6)
            hit = find(dump(), "Digital ID", "ID Card", "Passport", "Watch Passport", "Share")
            if hit and "Passport" in (hit[3] or "") or hit and "Digital" in (hit[3] or "") or hit and "ID" in (hit[3] or ""):
                tap(hit, 2.2, hit[3])
                break
        else:
            # More menu?
            hit = find(dump(), "More", "···", "...")
            if hit:
                tap(hit, 1.2, "More")
                hit = find(dump(), "Digital ID", "Passport", "ID Card")
                if hit:
                    tap(hit, 2.2, hit[3])
    dismiss_paywall_if_any()
    tlist = shot("32-digital-id-card")
    results["32-digital-id-card"] = "OK" if any(k in " ".join(tlist) for k in ("Passport", "Digital", "ID", "ownership", "Proof")) else "WEAK"
else:
    results["32-digital-id-card"] = "NO_PIECE"

print("\nRESULTS:")
for k, v in results.items():
    print(f"  {k}: {v}")
