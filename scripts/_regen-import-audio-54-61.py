#!/usr/bin/env python3
import re, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "videos/user-guide/index.html"
OUT = ROOT / "videos/user-guide/audio"
VOICE = "en-US-AndrewNeural"
html = HTML.read_text(encoding="utf-8")
m = re.search(r"const NARRATION = \[(.*?)\];", html, flags=re.DOTALL)
texts = [t.replace('\\"', '"') for t in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))]
for i in range(54, 62):
    out = OUT / f"slide-{i}.mp3"
    if out.exists() and out.stat().st_size > 8000 and i == 54:
        print(i, "skip existing")
        continue
    # always regen 55-61; skip 54 if good
    if i == 54 and out.exists() and out.stat().st_size > 8000:
        print(i, "skip")
        continue
    text = texts[i]
    print(i, text[:70])
    for attempt in range(5):
        try:
            subprocess.run([sys.executable, "-m", "edge_tts", "--voice", VOICE, "--text", text, "--write-media", str(out)], check=True)
            if out.exists() and out.stat().st_size > 5000:
                print(" ", out.stat().st_size); break
        except Exception as e:
            print(" retry", attempt, e)
            time.sleep(2 * (attempt + 1))
    else:
        raise SystemExit(f"failed {i}")
    time.sleep(0.5)
print("done")
