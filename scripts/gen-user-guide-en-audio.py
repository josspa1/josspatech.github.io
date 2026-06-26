#!/usr/bin/env python3
"""Generate en-US MP3 narration for videos/user-guide/ from the NARRATION JS array."""
import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "videos" / "user-guide" / "index.html"
OUT_DIR = ROOT / "videos" / "user-guide" / "audio"
VOICE = "en-US-AndrewNeural"


def extract_narration_strings(html: str) -> list[str]:
    match = re.search(r"const NARRATION = \[(.*?)\];", html, flags=re.DOTALL)
    if not match:
        raise SystemExit(f"No NARRATION array found in {HTML}")
    block = match.group(1)
    texts = re.findall(r'"((?:[^"\\]|\\.)*)"', block)
    if not texts:
        raise SystemExit("NARRATION array is empty")
    return [t.replace('\\"', '"') for t in texts]


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
    parser = argparse.ArgumentParser(description="Generate user-guide EN MP3s via edge-tts")
    parser.add_argument("--force", action="store_true", help="Regenerate even if file exists")
    args = parser.parse_args()

    html = HTML.read_text(encoding="utf-8")
    texts = extract_narration_strings(html)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Generating {len(texts)} slides -> {OUT_DIR} ({VOICE})")
    for i, text in enumerate(texts):
        out = OUT_DIR / f"slide-{i}.mp3"
        if not args.force and out.exists() and out.stat().st_size > 10000:
            print(f"[{i + 1}/{len(texts)}] skip {out.name}")
            continue
        print(f"[{i + 1}/{len(texts)}] {out.name} ({len(text)} chars)")
        generate_one(text, out)
        time.sleep(0.4)
        if out.stat().st_size == 0:
            raise SystemExit(f"Empty MP3: {out}")

    sizes = [f.stat().st_size for f in sorted(OUT_DIR.glob("slide-*.mp3"))]
    print(f"Done — {len(sizes)} files (min {min(sizes)} bytes)")


if __name__ == "__main__":
    main()
