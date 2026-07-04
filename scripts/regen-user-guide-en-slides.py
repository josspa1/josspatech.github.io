#!/usr/bin/env python3
"""Regenerate user-guide MP3s for given slide indices."""
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "videos" / "user-guide" / "index.html"
OUT = HTML.parent / "audio"
VOICE = "en-US-AndrewNeural"

def texts():
    html = HTML.read_text(encoding="utf-8")
    m = re.search(r"const NARRATION = \[(.*?)\];", html, re.S)
    block = m.group(1)
    return [t.replace('\\"', '"') for t in re.findall(r'"((?:[^"\\]|\\.)*)"', block)]

def gen(text, out):
    for attempt in range(6):
        try:
            subprocess.run(
                [sys.executable, "-m", "edge_tts", "--voice", VOICE, "--text", text, "--write-media", str(out)],
                check=True, capture_output=True, text=True,
            )
            if out.exists() and out.stat().st_size > 5000:
                return
        except subprocess.CalledProcessError:
            pass
        time.sleep(2 * (attempt + 1))
    raise SystemExit(f"failed {out.name}")

indices = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else list(range(89))
all_texts = texts()
for i in indices:
    out = OUT / f"slide-{i}.mp3"
    print(f"gen slide-{i}.mp3")
    gen(all_texts[i], out)
    time.sleep(0.5)
print("done")
