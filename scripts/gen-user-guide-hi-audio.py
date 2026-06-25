#!/usr/bin/env python3
"""Generate hi-IN MP3 narration for user-guide-hi from narration-card paragraphs."""
import re
import subprocess
import sys
import time
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "videos" / "user-guide-hi" / "index.html"
OUT_DIR = ROOT / "videos" / "user-guide-hi" / "audio"
VOICE = "hi-IN-SwaraNeural"  # professional female Hindi; alt: hi-IN-MadhurNeural


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_narrations(html: str) -> list[str]:
    cards = re.findall(
        r'<div class="narration-card(?: active)?">\s*'
        r'<span class="narration-step-badge">.*?</span>\s*'
        r"<h3>.*?</h3>\s*<p>(.*?)</p>",
        html,
        flags=re.DOTALL,
    )
    if len(cards) != 28:
        raise SystemExit(f"Expected 28 narration paragraphs, got {len(cards)}")
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
    texts = extract_narrations(html)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for i, text in enumerate(texts):
        out = OUT_DIR / f"slide-{i}.mp3"
        if out.exists() and out.stat().st_size > 0:
            print(f"[{i + 1}/28] skip {out.name} (exists)")
            continue
        print(f"[{i + 1}/28] {out.name} ({len(text)} chars)")
        generate_one(text, out)
        time.sleep(0.4)
        if out.stat().st_size == 0:
            raise SystemExit(f"Empty MP3: {out}")

    print(f"Done — {len(texts)} files in {OUT_DIR}")


if __name__ == "__main__":
    main()
