#!/usr/bin/env python3
"""Generate EN MP3 narration for the short HHH overview walkthrough."""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "hhh" / "walkthrough" / "audio"
VOICE = "en-US-AndrewNeural"

# Matches videos/hhh/intro/index.html SLIDES captions.
LINES = [
    "Command Center. Your collection's command center — museum, hunt, and repair in one place.",
    "My Museum. My Museum keeps every watch and clock with value at a glance.",
    "Piece detail. Open any piece for provenance, service history, and what it's worth.",
    "AI Identify. Snap a photo — AI Identify names the piece and scores the match.",
    "Clockworks and repair. Stuck clocks? Symptom wizard plus Clockworks parts in a few taps.",
    "Grail Radar. Grail Radar watches eBay so the next grail finds you.",
    "Finances. See profit, cost basis, and portfolio health — not just a pretty list.",
    "Pro tools. Pro tools, Photo Coach, Offline Show Pack, and Device Sync when you need them.",
    "Web Companion. Web Companion opens your museum on a PC — same Wi-Fi, address and four-digit code.",
    "Start free. Start free — unlock Pro when you're ready to go deeper.",
]


def generate_one(text: str, out_path: Path) -> None:
    cmd = [
        sys.executable,
        "-m",
        "edge_tts",
        "--voice",
        VOICE,
        "--text",
        text,
        "--write-media",
        str(out_path),
    ]
    last_err = None
    for attempt in range(5):
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return
        except subprocess.CalledProcessError as exc:
            last_err = exc.stderr or exc.stdout or str(exc)
            time.sleep(1.5 * (attempt + 1))
    raise SystemExit(f"edge-tts failed for {out_path.name}: {last_err}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for i, text in enumerate(LINES):
        out = OUT / f"slide-{i}.mp3"
        if out.exists() and out.stat().st_size > 5000:
            print(f"[{i + 1}/{len(LINES)}] skip {out.name}")
            continue
        print(f"[{i + 1}/{len(LINES)}] {out.name}")
        generate_one(text, out)
        time.sleep(0.35)
        if out.stat().st_size < 1000:
            raise SystemExit(f"Empty/short MP3: {out}")
    print("done", OUT)


if __name__ == "__main__":
    main()
