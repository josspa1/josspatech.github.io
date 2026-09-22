#!/usr/bin/env python3
"""Regenerate PBJ EN user-guide MP3s (AndrewNeural)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NARR = json.loads((ROOT / "videos" / "pbj" / "user-guide" / "narration-en.json").read_text(encoding="utf-8"))
OUT = ROOT / "videos" / "pbj" / "user-guide" / "audio"
VOICE = "en-US-AndrewNeural"


def soften(src: Path, dest: Path) -> None:
    r = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-af",
            "highpass=f=80,lowpass=f=8200,acompressor=threshold=-18dB:ratio=2.2:attack=25:release=220,volume=1.06",
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "3",
            str(dest),
        ],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "")[-800:])


def generate_one(text: str, out_path: Path) -> None:
    raw = out_path.with_suffix(".raw.mp3")
    cmd = [
        sys.executable,
        "-m",
        "edge_tts",
        "--voice",
        VOICE,
        "--rate",
        "+0%",
        "--pitch",
        "-1Hz",
        "--text",
        text,
        "--write-media",
        str(raw),
    ]
    for attempt in range(6):
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            if raw.exists() and raw.stat().st_size > 2000:
                soften(raw, out_path)
                raw.unlink(missing_ok=True)
                if out_path.exists() and out_path.stat().st_size > 2000:
                    return
        except (subprocess.CalledProcessError, RuntimeError) as e:
            print(f"  attempt {attempt + 1} failed: {e}")
        time.sleep(1.5 * (attempt + 1))
    raise SystemExit(f"failed {out_path.name}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--only", default="")
    args = p.parse_args()
    indexes = [int(x) for x in args.only.split(",") if x.strip()] if args.only else list(range(len(NARR)))
    for i in indexes:
        print(f"{i}/{len(NARR) - 1} {NARR[i][:64]}")
        generate_one(NARR[i], OUT / f"slide-{i}.mp3")
    print("done", len(indexes))


if __name__ == "__main__":
    main()
