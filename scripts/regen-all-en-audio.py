#!/usr/bin/env python3
"""Delete and regenerate all 89 MP3s with validation."""
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "videos" / "user-guide" / "index.html"
AUDIO = HTML.parent / "audio"
VOICE = "en-US-AndrewNeural"


def ok(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 5000:
        return False
    return subprocess.run(["ffprobe", "-v", "error", "-i", str(path)], capture_output=True).returncode == 0


def main() -> None:
    if AUDIO.exists():
        shutil.rmtree(AUDIO)
    AUDIO.mkdir()

    html = HTML.read_text(encoding="utf-8")
    m = re.search(r"const NARRATION = \[(.*?)\];", html, re.S)
    texts = [t.replace('\\"', '"') for t in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))]
    print(f"Regenerating {len(texts)} MP3s")

    for i, text in enumerate(texts):
        out = AUDIO / f"slide-{i}.mp3"
        for attempt in range(8):
            try:
                subprocess.run(
                    [sys.executable, "-m", "edge_tts", "--voice", VOICE, "--text", text, "--write-media", str(out)],
                    check=True, capture_output=True, text=True,
                )
                if ok(out):
                    print(f"  [{i+1}/{len(texts)}] {out.name} {out.stat().st_size}b")
                    break
            except subprocess.CalledProcessError:
                pass
            time.sleep(1.5 * (attempt + 1))
        else:
            raise SystemExit(f"Failed slide-{i}")
        time.sleep(0.35)
    print("All MP3s OK")


if __name__ == "__main__":
    main()
