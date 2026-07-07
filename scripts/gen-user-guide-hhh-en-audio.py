#!/usr/bin/env python3
"""Generate en-US MP3 narration for videos/user-guide-hhh/."""
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
            if out_path.exists() and out_path.stat().st_size > 3000:
                return
        except subprocess.CalledProcessError:
            pass
        time.sleep(1.5 * (attempt + 1))
    raise SystemExit(f"edge-tts failed: {out_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    texts = json.loads(NARRATION_JSON.read_text(encoding="utf-8"))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating {len(texts)} slides -> {OUT_DIR}")
    for i, text in enumerate(texts):
        out = OUT_DIR / f"slide-{i}.mp3"
        if not args.force and out.exists() and out.stat().st_size > 3000:
            print(f"skip {out.name}")
            continue
        print(f"[{i + 1}/{len(texts)}] {out.name}")
        generate_one(text, out)
        time.sleep(0.4)
    print("Done")


if __name__ == "__main__":
    main()
