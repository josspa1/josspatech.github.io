#!/usr/bin/env python3
"""Generate en-US MP3 narration for videos/import/ walkthrough (step-card text)."""
import re
import subprocess
import sys
import time
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "videos" / "import" / "index.html"
OUT_DIR = ROOT / "videos" / "import" / "audio"
VOICE = "en-US-AndrewNeural"


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def extract_step_cards(html: str) -> list[str]:
    cards = re.findall(
        r'<div class="step-card(?: active)?"[^>]*>\s*'
        r'<span class="step-card-num">.*?</span>\s*'
        r"<h3>.*?</h3>\s*<p>(.*?)</p>",
        html,
        flags=re.DOTALL,
    )
    if not cards:
        raise SystemExit(f"No step-card paragraphs found in {HTML}")
    return [strip_html(p) for p in cards]


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
    html = HTML.read_text(encoding="utf-8")
    texts = extract_step_cards(html)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating {len(texts)} slides -> {OUT_DIR}")
    for i, text in enumerate(texts):
        out = OUT_DIR / f"slide-{i}.mp3"
        print(f"[{i + 1}/{len(texts)}] {out.name} ({len(text)} chars)")
        generate_one(text, out)
        time.sleep(0.4)
        if out.stat().st_size == 0:
            raise SystemExit(f"Empty MP3: {out}")
    print("Done")


if __name__ == "__main__":
    main()
