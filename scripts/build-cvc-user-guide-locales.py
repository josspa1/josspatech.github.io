#!/usr/bin/env python3
"""Build CVC user-guide locale decks from EN (same voices as HHH)."""
from __future__ import annotations

import argparse
import asyncio
import json
import re
import shutil
import time
from pathlib import Path

import edge_tts
from deep_translator import GoogleTranslator

ROOT = Path(__file__).resolve().parents[1]
EN_DIR = ROOT / "videos" / "cvc" / "user-guide"
EN_NARR = EN_DIR / "narration-en.json"

LOCALES = {
    "de": ("de", "de-DE-ConradNeural", "Curator's Vault: Classics — Benutzerhandbuch"),
    "es": ("es", "es-US-AlonsoNeural", "Guía de usuario de Curator's Vault: Classics"),
    "fr": ("fr", "fr-FR-DeniseNeural", "Guide utilisateur Curator's Vault: Classics"),
    "it": ("it", "it-IT-ElsaNeural", "Guida utente Curator's Vault: Classics"),
    "pt": ("pt", "pt-BR-FranciscaNeural", "Manual do usuário Curator's Vault: Classics"),
    "zh": ("zh-CN", "zh-CN-YunyangNeural", "Curator's Vault: Classics 用户指南"),
    "hi": ("hi", "hi-IN-SwaraNeural", "Curator's Vault: Classics उपयोगकर्ता गाइड"),
}

RATE = "+0%"
PITCH = "-1Hz"

LANG_HREF = {
    "en": "/videos/cvc/user-guide/",
    "zh": "/videos/cvc/user-guide/zh/",
    "fr": "/videos/cvc/user-guide/fr/",
    "de": "/videos/cvc/user-guide/de/",
    "hi": "/videos/cvc/user-guide/hi/",
    "it": "/videos/cvc/user-guide/it/",
    "pt": "/videos/cvc/user-guide/pt/",
    "es": "/videos/cvc/user-guide/es/",
}


def soften(src: Path, dest: Path) -> None:
    import subprocess

    r = subprocess.run(
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
        ],
        capture_output=True,
        text=True,
    )
    if r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "")[-800:])


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


def protect_terms(en: str, translated: str) -> str:
    t = translated
    for keep in (
        "support@josspatech.com",
        "josspatech.com/videos/cvc/user-guide",
        "Curator's Vault: Classics",
        "Curator's Vault",
        "Scan individually",
        "Web Companion",
        "Grail Radar",
    ):
        if keep.lower() in en.lower() and keep not in t:
            # Leave translation if the phrase was adapted; restore emails/URLs always.
            if "@" in keep or "josspatech.com" in keep:
                t = re.sub(r"support@\S+", "support@josspatech.com", t, flags=re.I)
                t = t.replace("josspatech.com/videos/cvc/user-guide", keep)
    return t


async def _tts_save(text: str, voice: str, raw: Path) -> None:
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
        r"<h1>Curator's Vault: Classics — User Guide</h1>",
        f"<h1>{title}</h1>",
        html,
        count=1,
    )
    html = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="https://josspatech.com/videos/cvc/user-guide/{code}/">',
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
    html = html.replace(' class="is-current"', "")
    current_href = LANG_HREF[code]
    html = html.replace(
        f'href="{current_href}"',
        f'class="is-current" href="{current_href}"',
        1,
    )
    return html


def build_locale(code: str, force_audio: bool, skip_translate: bool) -> None:
    gt_code, voice, title = LOCALES[code]
    out_dir = EN_DIR / code
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
        texts = [protect_terms(en, tr) for en, tr in zip(en_texts, translate_batch(en_texts, gt_code))]
        narr_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    html = (out_dir / "index.html").read_text(encoding="utf-8")
    (out_dir / "index.html").write_text(
        patch_html(html, code if code != "zh" else "zh-CN", title, texts, code),
        encoding="utf-8",
    )

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
    parser.add_argument("--translate-only", action="store_true")
    args = parser.parse_args()
    codes = sorted(LOCALES.keys()) if args.locale == "all" else [args.locale]
    if not args.skip_translate and not args.translate_only:
        # EN index must already have the language picker.
        pass
    for code in codes:
        if args.translate_only:
            gt_code, _, _ = LOCALES[code]
            out_dir = EN_DIR / code
            out_dir.mkdir(parents=True, exist_ok=True)
            en_texts = json.loads(EN_NARR.read_text(encoding="utf-8"))
            print(f"{code}: translating only")
            texts = [protect_terms(en, tr) for en, tr in zip(en_texts, translate_batch(en_texts, gt_code))]
            (out_dir / f"narration-{code}.json").write_text(
                json.dumps(texts, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            continue
        build_locale(code, force_audio=args.force_audio, skip_translate=args.skip_translate)


if __name__ == "__main__":
    main()
