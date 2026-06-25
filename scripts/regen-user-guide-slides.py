#!/usr/bin/env python3
"""Regenerate specific user-guide MP3 slides from narration-card text."""
import argparse
import re
import subprocess
import sys
import time
from html import unescape
from pathlib import Path

VOICES = {
    "en": "en-US-AndrewNeural",
    "hi": "hi-IN-SwaraNeural",
}


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def extract_narrations(html: str) -> list[str]:
    cards = re.findall(
        r'<div class="narration-card(?: active)?"[^>]*>\s*'
        r'<span class="narration-step-badge">.*?</span>\s*'
        r"<h3>.*?</h3>\s*<p>(.*?)</p>",
        html,
        flags=re.DOTALL,
    )
    return [strip_html(p) for p in cards]


def generate_one(text: str, out_path: Path, voice: str) -> None:
    cmd = [
        sys.executable, "-m", "edge_tts",
        "--voice", voice, "--text", text,
        "--write-media", str(out_path),
    ]
    for attempt in range(5):
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            return
        except subprocess.CalledProcessError as exc:
            last_err = exc.stderr or exc.stdout or str(exc)
            time.sleep(1.5 * (attempt + 1))
    raise SystemExit(f"edge-tts failed: {last_err}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("locale", choices=["en", "hi"])
    parser.add_argument("slides", type=int, nargs="+", help="0-based slide indices")
    args = parser.parse_args()
    folder = "user-guide" if args.locale == "en" else "user-guide-hi"
    html_path = Path(__file__).resolve().parents[1] / "videos" / folder / "index.html"
    out_dir = html_path.parent / "audio"
    texts = extract_narrations(html_path.read_text(encoding="utf-8"))
    voice = VOICES[args.locale]
    for i in args.slides:
        out = out_dir / f"slide-{i}.mp3"
        print(f"slide-{i}.mp3 ({len(texts[i])} chars)")
        generate_one(texts[i], out, voice)
        time.sleep(0.4)


if __name__ == "__main__":
    main()
