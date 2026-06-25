#!/usr/bin/env python3
"""Generate en-US MP3 narration from walkthrough HTML narration cards."""
import argparse
import re
import subprocess
import sys
import time
from html import unescape
from pathlib import Path

VOICE = "en-US-AndrewNeural"


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
    if not cards:
        cards = re.findall(
            r'<div class="narration-card(?: active)?"[^>]*>.*?<p>(.*?)</p>',
            html,
            flags=re.DOTALL,
        )
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
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path, help="Walkthrough index.html")
    args = parser.parse_args()
    html_path = args.html.resolve()
    out_dir = html_path.parent / "audio"
    html = html_path.read_text(encoding="utf-8")
    texts = extract_narrations(html)
    if not texts:
        raise SystemExit(f"No narration cards found in {html_path}")
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Generating {len(texts)} slides -> {out_dir}")
    for i, text in enumerate(texts):
        out = out_dir / f"slide-{i}.mp3"
        if out.exists() and out.stat().st_size > 10000:
            print(f"[{i + 1}/{len(texts)}] skip {out.name}")
            continue
        print(f"[{i + 1}/{len(texts)}] {out.name} ({len(text)} chars)")
        generate_one(text, out)
        time.sleep(0.4)
        if out.stat().st_size == 0:
            raise SystemExit(f"Empty MP3: {out}")
    print("Done")


if __name__ == "__main__":
    main()
