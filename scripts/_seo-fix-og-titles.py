#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
for path in ROOT.rglob("*.html"):
    if "admin" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    if 'content="index.html"' not in text:
        continue
    m = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
    if not m:
        continue
    title = re.sub(r"\s+", " ", m.group(1)).strip()
    title = title.replace("&", "&amp;").replace('"', "&quot;")
    new = text.replace('content="index.html"', f'content="{title}"')
    if new != text:
        path.write_text(new, encoding="utf-8")
        print("fixed", path.relative_to(ROOT))
