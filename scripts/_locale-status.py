#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
codes = ["de", "es", "fr", "hi", "it", "pt", "zh"]
for prefix, expect in [("user-guide-hhh", 111), ("user-guide", 120)]:
    print(f"\n{prefix} (expect {expect} audio slides)")
    for c in codes:
        d = ROOT / "videos" / f"{prefix}-{c}"
        a = len(list((d / "audio").glob("slide-*.mp3"))) if d.exists() else 0
        idx = (d / "index.html").exists()
        narr = (d / f"narration-{c}.json").exists()
        status = "COMPLETE" if a == expect and idx and narr else "INCOMPLETE"
        print(f"  {c}: index={idx} narr={narr} audio={a}/{expect} {status}")

# log tails
for name in ["hhh-locales.log", "pbj-locales.log"]:
    p = ROOT / "videos" / "_build-logs" / name
    if p.exists():
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        print(f"\n{name} tail:")
        for line in lines[-6:]:
            print(" ", line)
