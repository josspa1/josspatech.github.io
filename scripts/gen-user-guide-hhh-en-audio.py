#!/usr/bin/env python3
"""Generate en-US MP3 narration for videos/user-guide-hhh/ — Meta-ad voice polish.

Matches marketing/add-identify-ad-voiceover.py:
  AndrewNeural · rate +0% · pitch -1Hz · soft compressor chain.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NARRATION_JSON = ROOT / "videos" / "user-guide-hhh" / "narration-en.json"
OUT_DIR = ROOT / "videos" / "user-guide-hhh" / "audio"
VOICE = "en-US-AndrewNeural"
RATE = "+0%"
PITCH = "-1Hz"


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "")[-800:])


def soften(src: Path, dest: Path) -> None:
    """Same soft chain as Meta Identify ad VO."""
    run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(src),
            "-af",
            "highpass=f=80,lowpass=f=8200,"
            "acompressor=threshold=-18dB:ratio=2.2:attack=25:release=220,volume=1.06",
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "3",
            str(dest),
        ]
    )


def generate_one(text: str, out_path: Path) -> None:
    raw = out_path.with_suffix(".raw.mp3")
    cmd = [
        sys.executable,
        "-m",
        "edge_tts",
        "--voice",
        VOICE,
        "--rate",
        RATE,
        "--pitch",
        PITCH,
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
    raise SystemExit(f"edge-tts failed: {out_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    parser.add_argument(
        "--only",
        type=str,
        default="",
        help="Comma-separated slide indexes to regenerate (e.g. 76,77,78)",
    )
    parser.add_argument(
        "--only-changed",
        action="store_true",
        help="Only regenerate slides listed in _audio_regen_slides.json",
    )
    args = parser.parse_args()
    texts = json.loads(NARRATION_JSON.read_text(encoding="utf-8"))
    only: set[int] | None = None
    if args.only:
        only = {int(x.strip()) for x in args.only.split(",") if x.strip()}
    elif args.only_changed:
        regen_path = OUT_DIR.parent / "_audio_regen_slides.json"
        if regen_path.exists():
            only = {int(x) for x in json.loads(regen_path.read_text(encoding="utf-8"))}
        else:
            only = set()
        print(f"only-changed: {sorted(only) if only else '(none)'}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"generating {len(texts)} slides -> {OUT_DIR} ({VOICE} {RATE} {PITCH} + soften)")
    for i, text in enumerate(texts):
        out = OUT_DIR / f"slide-{i}.mp3"
        if only is not None and i not in only:
            continue
        if not args.force and only is None and out.exists() and out.stat().st_size > 3000:
            print(f"skip {out.name}")
            continue
        print(f"[{i + 1}/{len(texts)}] {out.name}")
        generate_one(text, out)
        time.sleep(0.35)
    print("Done")


if __name__ == "__main__":
    main()
