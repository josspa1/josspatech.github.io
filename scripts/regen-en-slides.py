#!/usr/bin/env python3
"""Regenerate specific user-guide EN MP3s from NARRATION array."""
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from gen_user_guide_en_audio import extract_narration_strings, generate_one, HTML, OUT_DIR, VOICE

import importlib.util
spec = importlib.util.spec_from_file_location("gen", ROOT / "scripts" / "gen-user-guide-en-audio.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

def main():
    indices = [int(x) for x in sys.argv[1:]]
    html = HTML.read_text(encoding="utf-8")
    texts = gen.extract_narration_strings(html)
    for i in indices:
        out = OUT_DIR / f"slide-{i}.mp3"
        print(f"Regenerating slide-{i}.mp3 ({len(texts[i])} chars)")
        gen.generate_one(texts[i], out)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
