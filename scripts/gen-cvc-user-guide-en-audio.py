#!/usr/bin/env python3
"""Generate en-US MP3 narration for videos/cvc/user-guide/ (same voice as HHH)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "hhh_guide_audio",
    HERE / "gen-user-guide-hhh-en-audio.py",
)
hhh = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(hhh)

hhh.NARRATION_JSON = HERE.parent / "videos" / "cvc" / "user-guide" / "narration-en.json"
hhh.OUT_DIR = HERE.parent / "videos" / "cvc" / "user-guide" / "audio"

if __name__ == "__main__":
    hhh.main()
