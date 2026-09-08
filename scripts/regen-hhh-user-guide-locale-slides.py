#!/usr/bin/env python3
"""Regen changed HHH user-guide locale MP3s (canonical videos/hhh/user-guide)."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "hhh_locales", HERE / "build-hhh-user-guide-locales.py"
)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

ROOT = HERE.parent
GUIDE = ROOT / "videos" / "hhh" / "user-guide"
ONLY = {23, 24, 25, 27, 29, 31, 32, 36, 37}


def main() -> None:
    for code, (_gt, voice, _title) in mod.LOCALES.items():
        narr = json.loads((GUIDE / code / f"narration-{code}.json").read_text(encoding="utf-8"))
        audio = GUIDE / code / "audio"
        audio.mkdir(parents=True, exist_ok=True)
        print(f"{code} {voice}")
        for i in sorted(ONLY):
            out = audio / f"slide-{i}.mp3"
            print(f"  {out.name}")
            mod.generate_one(narr[i], voice, out)
    print("Done")


if __name__ == "__main__":
    main()
