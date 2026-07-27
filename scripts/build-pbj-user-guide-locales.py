#!/usr/bin/env python3
"""Build PBJ user-manual locale decks from EN (translate + soft VO).

Same slides / taps / structure as English — only narration language changes.
Locales: de, es, fr, it, pt, zh, hi (same set as HHH).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import edge_tts
from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parents[1]
EN_DIR = ROOT / "videos" / "user-guide"
EN_NARR = EN_DIR / "narration-en.json"

LOCALES = {
    "de": ("de", "de-DE-ConradNeural", "PocketBudJet Benutzerhandbuch"),
    "es": ("es", "es-US-AlonsoNeural", "Manual de usuario de PocketBudJet"),
    "fr": ("fr", "fr-FR-DeniseNeural", "Manuel utilisateur PocketBudJet"),
    "it": ("it", "it-IT-ElsaNeural", "Manuale utente PocketBudJet"),
    "pt": ("pt", "pt-BR-FranciscaNeural", "Manual do usuário PocketBudJet"),
    "zh": ("zh-CN", "zh-CN-YunyangNeural", "PocketBudJet 用户手册"),
    "hi": ("hi", "hi-IN-SwaraNeural", "PocketBudJet उपयोगकर्ता मैनुअल"),
}

RATE = "+0%"
PITCH = "-1Hz"


def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "")[-800:])


def soften(src: Path, dest: Path) -> None:
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


def translate_batch(texts: list[str], target: str) -> list[str]:
    out: list[str] = []
    translator = GoogleTranslator(source="en", target=target)
    for i, text in enumerate(texts):
        for attempt in range(5):
            try:
                translated = translator.translate(text)
                out.append(translated or text)
                break
            except Exception as exc:  # noqa: BLE001
                if attempt == 4:
                    print(f"  keep EN for slide {i}: {exc}")
                    out.append(text)
                else:
                    time.sleep(1.2 * (attempt + 1))
        if (i + 1) % 10 == 0:
            print(f"  translated {i + 1}/{len(texts)}")
            time.sleep(0.4)
        else:
            time.sleep(0.12)
    return out


async def _tts_save(text: str, voice: str, raw: Path) -> None:
    """UTF-8-safe path (no CLI argv) — same rate/pitch polish as EN Andrew VO."""
    communicate = edge_tts.Communicate(text, voice, rate=RATE, pitch=PITCH)
    await communicate.save(str(raw))


def generate_one(text: str, voice: str, out_path: Path) -> None:
    raw = out_path.with_suffix(".raw.mp3")
    for attempt in range(6):
        try:
            raw.unlink(missing_ok=True)
            asyncio.run(_tts_save(text, voice, raw))
            if raw.exists() and raw.stat().st_size > 1500:
                soften(raw, out_path)
                raw.unlink(missing_ok=True)
                if out_path.exists() and out_path.stat().st_size > 1500:
                    return
        except Exception as e:  # noqa: BLE001
            print(f"  tts attempt {attempt + 1}: {e}")
        time.sleep(1.4 * (attempt + 1))
    raise SystemExit(f"edge-tts failed: {out_path}")


def patch_html(src_html: str, lang: str, title: str, narr: list[str], code: str) -> str:
    html = src_html
    html = re.sub(r'<html lang="[^"]*">', f'<html lang="{lang}">', html, count=1)
    html = re.sub(r"<title>.*?</title>", f"<title>{title} | JosspaTech</title>", html, count=1)
    html = re.sub(
        r"<h1>PocketBudJet User Manual</h1>",
        f"<h1>{title}</h1>",
        html,
        count=1,
    )
    html = re.sub(
        r"const NARRATION = \[.*?\];",
        "const NARRATION = " + json.dumps(narr, ensure_ascii=False) + ";",
        html,
        count=1,
        flags=re.S,
    )
    html = html.replace('href="/videos/user-guide/" style="color:var(--navy);font-weight:700;"', 'href="/videos/user-guide/" style="color:var(--navy-medium);font-weight:600;"')
    html = html.replace(
        f'href="/videos/user-guide-{code}/" target="_blank" rel="noopener" style="color:var(--navy-medium);font-weight:600;"',
        f'href="/videos/user-guide-{code}/" style="color:var(--navy);font-weight:700;"',
        1,
    )
    return html


def build_locale(code: str, force_audio: bool, skip_translate: bool) -> None:
    gt_code, voice, title = LOCALES[code]
    out_dir = ROOT / "videos" / f"user-guide-{code}"
    narr_path = out_dir / f"narration-{code}.json"
    audio_dir = out_dir / "audio"

    out_dir.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "walkthrough.css", "deck.js"):
        src = EN_DIR / name
        if src.exists():
            shutil.copy2(src, out_dir / name)

    en_texts = json.loads(EN_NARR.read_text(encoding="utf-8"))
    if skip_translate and narr_path.exists():
        texts = json.loads(narr_path.read_text(encoding="utf-8"))
        print(f"{code}: reuse {narr_path.name} ({len(texts)})")
    else:
        print(f"{code}: translating {len(en_texts)} slides -> {gt_code}")
        texts = translate_batch(en_texts, gt_code)
        for i, t in enumerate(texts):
            if "$9.99" in en_texts[i] and "$9.99" not in t:
                texts[i] = t.replace("9,99", "9.99").replace("9.99 USD", "$9.99")
            if "$74.99" in en_texts[i] and "$74.99" not in t:
                texts[i] = texts[i].replace("74,99", "74.99").replace("74.99 USD", "$74.99")
        narr_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    html = (out_dir / "index.html").read_text(encoding="utf-8")
    (out_dir / "index.html").write_text(
        patch_html(html, code if code != "zh" else "zh-CN", title, texts, code),
        encoding="utf-8",
        newline="\n",
    )

    # Language-only: tap coords / timing / images must match EN master
    def _tap_sig(h: str) -> list[str]:
        return re.findall(
            r'data-index="\d+"[^>]*(?:data-tap-none|data-tap-x="[^"]*"[^>]*data-tap-y="[^"]*"[^>]*(?:data-tap-show-at="[^"]*")?[^>]*(?:data-tap-duration="[^"]*")?)?',
            h,
        )

    en_html = (EN_DIR / "index.html").read_text(encoding="utf-8")
    loc_html = (out_dir / "index.html").read_text(encoding="utf-8")
    if _tap_sig(en_html) != _tap_sig(loc_html):
        raise SystemExit(f"{code}: tap attributes diverged from EN — aborting")
    if re.findall(r'<img src="[^"]+"', en_html) != re.findall(r'<img src="[^"]+"', loc_html):
        raise SystemExit(f"{code}: slide images diverged from EN — aborting")


    audio_dir.mkdir(parents=True, exist_ok=True)
    print(f"{code}: generating audio ({voice})")
    for i, text in enumerate(texts):
        out = audio_dir / f"slide-{i}.mp3"
        if not force_audio and out.exists() and out.stat().st_size > 2000:
            continue
        print(f"  [{i + 1}/{len(texts)}] {out.name}")
        generate_one(text, voice, out)
        time.sleep(0.3)
    print(f"{code}: done -> {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--locale", choices=sorted(LOCALES.keys()) + ["all"], default="all")
    parser.add_argument("--force-audio", action="store_true")
    parser.add_argument("--skip-translate", action="store_true")
    args = parser.parse_args()
    codes = sorted(LOCALES.keys()) if args.locale == "all" else [args.locale]
    for code in codes:
        build_locale(code, force_audio=args.force_audio, skip_translate=args.skip_translate)


if __name__ == "__main__":
    main()
