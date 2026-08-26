#!/usr/bin/env python3
"""Generate EN MP3 narration for PAL reviewer walkthrough."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "pal" / "walkthrough" / "audio"
NARRATION = ROOT / "videos" / "pal" / "walkthrough" / "narration-en.json"
VOICE = "en-US-AndrewNeural"


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
    lines = json.loads(NARRATION.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    for i, text in enumerate(lines):
        out = OUT / f"slide-{i}.mp3"
        if out.exists() and out.stat().st_size > 5000:
            print(f"[{i + 1}/{len(lines)}] skip {out.name}")
            continue
        print(f"[{i + 1}/{len(lines)}] {out.name}")
        generate_one(text, out)
    print(f"Done — {len(lines)} files in {OUT}")


if __name__ == "__main__":
    main()
