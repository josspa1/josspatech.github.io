#!/usr/bin/env python3
"""Regenerate English partner-showcase narration MP3s from locales.json."""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ROOT / "videos" / "pocketbudjet" / "partner-showcase" / "locales.json"
OUT = ROOT / "videos" / "pocketbudjet" / "partner-showcase" / "audio" / "en"
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
    for attempt in range(5):
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            if out_path.exists() and out_path.stat().st_size > 2000:
                return
        except subprocess.CalledProcessError:
            pass
        time.sleep(1.5 * (attempt + 1))
    raise SystemExit(f"edge-tts failed: {out_path.name}")


def main() -> None:
    pack = json.loads(LOCALES.read_text(encoding="utf-8"))["locales"]["en"]
    texts = pack["narrations"]
    OUT.mkdir(parents=True, exist_ok=True)
    for i, text in enumerate(texts):
        out = OUT / f"slide-{i}.mp3"
        print(f"[{i + 1}/{len(texts)}] {out.name}")
        generate_one(text, out)
        time.sleep(0.3)
    print("Done", OUT)


if __name__ == "__main__":
    main()
