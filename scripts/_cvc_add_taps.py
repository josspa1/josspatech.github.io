#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "cvc" / "user-guide"
html_path = OUT / "index.html"
html = html_path.read_text(encoding="utf-8")
narr = json.loads((OUT / "narration-en.json").read_text(encoding="utf-8"))

taps = {
    2: 'data-tap-x="50" data-tap-y="90" data-tap-label="Identify a piece" data-tap-show-at="0.3" data-tap-duration="2.8"',
    8: 'data-tap-x="82" data-tap-y="10" data-tap-label="Clear samples" data-tap-show-at="0.3" data-tap-duration="2.8"',
    11: 'data-tap-x="12" data-tap-y="42" data-tap-label="Identify" data-tap-show-at="0.3" data-tap-duration="2.8"',
    12: 'data-tap-x="30" data-tap-y="42" data-tap-label="Add" data-tap-show-at="0.3" data-tap-duration="2.6"',
    13: 'data-tap-x="88" data-tap-y="42" data-tap-label="Wish" data-tap-show-at="0.3" data-tap-duration="2.6"',
    14: 'data-tap-x="18" data-tap-y="30" data-tap-label="Coin" data-tap-show-at="0.3" data-tap-duration="2.8"',
    16: 'data-tap-x="50" data-tap-y="48" data-tap-label="Point camera" data-tap-show-at="0.3" data-tap-duration="2.8"',
    18: 'data-tap-x="50" data-tap-y="78" data-tap-label="Identify" data-tap-show-at="0.3" data-tap-duration="2.8"',
    24: 'data-tap-x="88" data-tap-y="12" data-tap-label="History" data-tap-show-at="0.3" data-tap-duration="2.8"',
    26: 'data-tap-x="38" data-tap-y="94" data-tap-label="My Collection" data-tap-show-at="0.3" data-tap-duration="2.8"',
    27: 'data-tap-x="22" data-tap-y="44" data-tap-label="Owned" data-tap-show-at="0.3" data-tap-duration="2.6"',
    31: 'data-tap-x="88" data-tap-y="72" data-tap-label="Plus" data-tap-show-at="0.3" data-tap-duration="2.6"',
    36: 'data-tap-x="78" data-tap-y="12" data-tap-label="+ New" data-tap-show-at="0.3" data-tap-duration="2.8"',
    37: 'data-tap-x="22" data-tap-y="12" data-tap-label="Check all" data-tap-show-at="0.3" data-tap-duration="2.8"',
    53: 'data-tap-x="50" data-tap-y="42" data-tap-label="Start" data-tap-show-at="0.3" data-tap-duration="2.8"',
    56: 'data-tap-x="88" data-tap-y="94" data-tap-label="Settings" data-tap-show-at="0.3" data-tap-duration="2.6"',
}

def repl_slide(m: re.Match) -> str:
    attrs = m.group(1)
    idx_m = re.search(r'data-index="(\d+)"', attrs)
    if not idx_m:
        return m.group(0)
    idx = int(idx_m.group(1))
    if idx not in taps:
        return m.group(0)
    attrs2 = re.sub(r'\s+data-tap-none', "", attrs)
    if "data-tap-x=" in attrs2:
        return m.group(0)
    return f'<div class="slide" data-index="{idx}" {taps[idx]}>'

html2 = re.sub(r'<div class="slide(?:\s+active)?"([^>]*)>', repl_slide, html)
new_arr = json.dumps(narr, ensure_ascii=False)
html2, n = re.subn(r"const NARRATION = \[.*?\];", "const NARRATION = " + new_arr + ";", html2, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f"NARRATION replace count={n}")
html_path.write_text(html2, encoding="utf-8")
print("taps", sorted(taps), "narr", len(narr))
