#!/usr/bin/env python3
"""Regenerate any user-guide MP3 smaller than min_bytes."""
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "videos" / "user-guide" / "index.html"
OUT_DIR = ROOT / "videos" / "user-guide" / "audio"
VOICE = "en-US-AndrewNeural"
MIN_BYTES = 10000


def extract_narration_strings(html: str) -> list[str]:
    match = re.search(r"const NARRATION = \[(.*?)\];", html, flags=re.DOTALL)
    texts = re.findall(r'"((?:[^"\\]|\\.)*)"', match.group(1))
    return [t.replace('\\"', '"') for t in texts]


def generate_one(text: str, out_path: Path) -> None:
    cmd = [sys.executable, "-m", "edge_tts", "--voice", VOICE, "--text", text, "--write-media", str(out_path)]
    for attempt in range(5):
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            if out_path.stat().st_size >= MIN_BYTES:
                return
        except subprocess.CalledProcessError:
            pass
        time.sleep(1.5 * (attempt + 1))
    raise SystemExit(f"Failed: {out_path.name}")


def main() -> None:
    texts = extract_narration_strings(HTML.read_text(encoding="utf-8"))
    assert len(texts) == 28, f"Expected 28 narration strings, got {len(texts)}"
    for i, text in enumerate(texts):
        out = OUT_DIR / f"slide-{i}.mp3"
        if out.exists() and out.stat().st_size >= MIN_BYTES:
            print(f"OK {out.name}")
            continue
        print(f"REGEN {out.name} ({len(text)} chars)")
        generate_one(text, out)
        time.sleep(0.5)
    print("Done")


if __name__ == "__main__":
    main()
