#!/usr/bin/env python3
"""Generate locale MP3 narration for user-guide-{locale} from narration-card paragraphs."""
import argparse
import re
import subprocess
import sys
import time
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LOCALES = {
    "fr": ("user-guide-fr", "fr-FR-DeniseNeural"),
    "pt": ("user-guide-pt", "pt-BR-FranciscaNeural"),
    "it": ("user-guide-it", "it-IT-ElsaNeural"),
    "hi": ("user-guide-hi", "hi-IN-SwaraNeural"),
    "de": ("user-guide-de", "de-DE-ConradNeural"),
    "es": ("user-guide-es", "es-US-AlonsoNeural"),
    "zh": ("user-guide-zh", "zh-CN-YunyangNeural"),
}


def strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


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


def generate_one(text: str, voice: str, out_path: Path) -> None:
    cmd = [
        sys.executable,
        "-m",
        "edge_tts",
        "--voice",
        voice,
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
    parser = argparse.ArgumentParser(description="Generate user-guide locale MP3s via edge-tts")
    parser.add_argument("locale", choices=sorted(LOCALES.keys()), help="Locale code (fr, pt, it, hi, de, es, zh)")
    parser.add_argument("--force", action="store_true", help="Regenerate even if file exists")
    args = parser.parse_args()

    folder, voice = LOCALES[args.locale]
    html_path = ROOT / "videos" / folder / "index.html"
    out_dir = ROOT / "videos" / folder / "audio"

    html = html_path.read_text(encoding="utf-8")
    texts = extract_narrations(html)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Locale: {args.locale} -> {folder}/audio/ ({voice})")
    for i, text in enumerate(texts):
        out = out_dir / f"slide-{i}.mp3"
        if not args.force and out.exists() and out.stat().st_size > 10000:
            print(f"[{i + 1}/28] skip {out.name} (exists)")
            continue
        print(f"[{i + 1}/28] {out.name} ({len(text)} chars)")
        generate_one(text, voice, out)
        time.sleep(0.4)
        if out.stat().st_size == 0:
            raise SystemExit(f"Empty MP3: {out}")

    sizes = [f.stat().st_size for f in sorted(out_dir.glob("slide-*.mp3"))]
    print(f"Done — {len(sizes)} files in {out_dir} (min {min(sizes)} bytes)")


if __name__ == "__main__":
    main()
