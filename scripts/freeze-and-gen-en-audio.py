#!/usr/bin/env python3
"""Extract 89 NARRATION strings from git 4b289c9 and regenerate all MP3s."""
import importlib.util
import json
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
raw = subprocess.check_output(["git", "show", "4b289c9:videos/user-guide/index.html"], cwd=ROOT)
for enc in ("utf-8", "utf-8-sig", "utf-16"):
    try:
        html = raw.decode(enc)
        break
    except UnicodeDecodeError:
        continue
else:
    html = raw.decode("utf-8", errors="replace")

m = re.search(r"const NARRATION = \[(.*?)\];", html, re.S)
if not m:
    raise SystemExit("NARRATION not found in 4b289c9")
texts = [t.replace('\\"', '"') for t in re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(1))]
out_json = ROOT / "videos" / "user-guide" / "narration-en.json"
out_json.write_text(json.dumps(texts, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Saved {len(texts)} strings -> {out_json}")

spec = importlib.util.spec_from_file_location("gen", ROOT / "scripts" / "gen-user-guide-en-audio.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

for i, text in enumerate(texts):
    out = gen.OUT_DIR / f"slide-{i}.mp3"
    print(f"[{i + 1}/{len(texts)}] {out.name} ({len(text)} chars)")
    gen.generate_one(text, out)
    time.sleep(0.45)

print("Done — all MP3s regenerated from frozen narration-en.json source")
