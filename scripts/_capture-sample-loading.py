#!/usr/bin/env python3
"""Clear samples → Load Demo → burst-capture loading spinner. Focus-guarded."""
from __future__ import annotations

import re
import subprocess
import threading
import time
from pathlib import Path

ADB = str(Path.home() / "AppData/Local/Android/Sdk/platform-tools/adb.exe")
S = "R5CXC2K4Z8F"
PKG = "com.josspatech.handyhorology"
ST = Path(__file__).resolve().parents[1] / "assets/screenshots/hhh/_capture_verify"
BURST = ST / "_loading_burst"
UI = ST / "_ui.xml"
BAD = ("dialer", "contacts", "whisker", "maestro", "dialtacts")

BURST.mkdir(parents=True, exist_ok=True)
for p in BURST.glob("*.png"):
    p.unlink()


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


def find(xml, *labels, min_y=120, max_y=2750, prefer_exact=None):
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
        score = -abs(cy - 1500) + (r - l) // 20
        if prefer_exact and prefer_exact.lower() == label.lower():
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


def tap(hit, wait=1.5, step="tap"):
    if hit is None:
        raise SystemExit(f"missing {step}")
    safe = (hit[3] or "").encode("ascii", "replace").decode("ascii")
    print(f"{step}: {safe!r} @ {hit[0]},{hit[1]}")
    adb("shell", "input", "tap", str(hit[0]), str(hit[1]))
    time.sleep(wait)
    assert_hhh(step)


def scroll_until(label: str, max_swipes=10):
    for i in range(max_swipes):
        xml = dump()
        hit = find(xml, label, prefer_exact=label)
        if hit and label.lower() in (hit[3] or "").lower():
            return hit
        print(f"scroll for {label} #{i+1}")
        adb("shell", "input", "swipe", "720", "2300", "720", "900", "350")
        time.sleep(0.65)
    return find(dump(), label, prefer_exact=label)


stop_burst = threading.Event()


def burst_loop():
    n = 0
    while not stop_burst.is_set() and n < 80:
        n += 1
        remote = f"/sdcard/hhh-burst-{n:03d}.png"
        adb("shell", "screencap", "-p", remote)
        dest = BURST / f"{n:03d}.png"
        adb("pull", remote, str(dest))
        adb("shell", "rm", remote)
        # don't assert every frame — keep cadence
        time.sleep(0.05)


adb("shell", "cmd", "statusbar", "collapse")
adb("shell", "am", "force-stop", PKG)
time.sleep(0.5)
adb("shell", "am", "start", "-n", f"{PKG}/.MainActivity")
time.sleep(3.5)
assert_hhh("launch")

xml = dump()
# Clear samples if banner present
hit = find(xml, "Clear samples", prefer_exact="Clear samples")
if hit:
    tap(hit, 1.2, "Clear samples")
    xml = dump()
    # confirm dialog — "Clear samples" or Remove
    for label in ("Clear samples", "Remove", "OK"):
        conf = find(xml, label, prefer_exact=label, min_y=800, max_y=2200)
        if conf:
            tap(conf, 2.5, f"confirm {label}")
            break
    time.sleep(1.0)
else:
    print("no Clear samples banner — may already be cleared")

# Settings → Demo Collection → Load Demo
tap(find_tab(dump(), "Settings"), 2.0, "Settings")
# Profile is the settings root in this app
hit = scroll_until("Load Demo Collection")
if not hit:
    # maybe still loaded — try Remove first
    hit = find(dump(), "Remove Demo Data", "Remove demo")
    if hit:
        tap(hit, 1.2, "Remove Demo")
        for label in ("Remove", "OK", "Clear"):
            conf = find(dump(), label, prefer_exact=label, min_y=800, max_y=2200)
            if conf:
                tap(conf, 2.5, f"confirm remove {label}")
                break
        hit = scroll_until("Load Demo Collection")
if not hit:
    raise SystemExit("Load Demo Collection not found")
tap(hit, 1.2, "Load Demo Collection")

# Confirm alert "Load Demo Data"
xml = dump()
print("alert texts:", [x.encode("ascii", "replace").decode("ascii") for x in texts(xml)[:30]])
conf = find(xml, "Load Demo Data", prefer_exact="Load Demo Data")
if not conf:
    conf = find(xml, "Load Demo Data")
if not conf:
    raise SystemExit("Load Demo Data confirm missing")

# Start burst, then confirm
t = threading.Thread(target=burst_loop, daemon=True)
t.start()
time.sleep(0.15)
tap(conf, 0.2, "Load Demo Data confirm")
# keep bursting while seed runs
time.sleep(4.5)
stop_burst.set()
t.join(timeout=8)

frames = sorted(BURST.glob("*.png"))
print(f"burst frames: {len(frames)}")
if not frames:
    raise SystemExit("no burst frames")

# Prefer frames where ProgressBar / spinner exists in a paired dump — we only have PNGs.
# Heuristic: pick mid frames (loading usually mid-burst), then verify visually.
# Also dump UI now — if still loading great; else pick frame ~40% through.
pick = frames[min(len(frames) - 1, max(2, len(frames) // 3))]
# Copy several candidates for visual pick
cands = []
for idx in sorted({2, len(frames) // 4, len(frames) // 3, len(frames) // 2, (2 * len(frames)) // 3}):
    if 0 <= idx < len(frames):
        cands.append(frames[idx])

from PIL import Image  # noqa: E402

# Spinner is gold-ish on cream — look for concentrated non-cream pixels in center card area
def spinner_score(path: Path) -> float:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    # Profile demo card roughly mid screen
    crop = im.crop((int(w * 0.2), int(h * 0.35), int(w * 0.8), int(h * 0.7)))
    px = list(crop.getdata())
    # gold/amber spinner-ish: high R+G relative, not cream
    gold = 0
    for r, g, b in px:
        if r > 160 and g > 120 and b < 100 and (r + g) > 2.2 * (b + 1):
            gold += 1
        # also navy ActivityIndicator sometimes uses theme gold — count saturated mid tones
        elif abs(r - g) < 40 and r > 140 and b < 120 and r < 230:
            gold += 0.3
    return gold / max(1, len(px)) * 10000


scored = sorted(((spinner_score(p), p) for p in frames), reverse=True)
print("top spinner scores:")
for sc, p in scored[:8]:
    print(f"  {sc:.1f} {p.name}")

best = scored[0][1]
# Also keep top 3 as review candidates
for i, (_sc, p) in enumerate(scored[:3]):
    dest = ST / f"19-sample-loading.CANDIDATE{'' if i == 0 else f'-alt{i}'}.png"
    dest.write_bytes(p.read_bytes())
    print(f"wrote {dest.name}")

# Sanity: dump current UI
xml = dump()
print("after load texts:", [x.encode("ascii", "replace").decode("ascii") for x in texts(xml)[:25]])
print("BEST", best.name, "score", scored[0][0])
if scored[0][0] < 1.0:
    print("WARN: low spinner score — verify candidates visually; load may have been too fast")
