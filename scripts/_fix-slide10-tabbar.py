#!/usr/bin/env python3
import re
from pathlib import Path

HTML = Path(__file__).resolve().parents[1] / "videos/user-guide-hhh/index.html"
html = HTML.read_text(encoding="utf-8")
html2, n = re.subn(
    r'(data-index="10"[^>]*>\s*<img src=")[^"]+(")',
    r'\1/assets/screenshots/hhh/manual/01-home-command-center.png?v=picture-audit-2026-07-24b\2',
    html,
    count=1,
)
HTML.write_text(html2, encoding="utf-8")
m = re.search(r'data-index="10"[^>]*>\s*<img src="([^"]+)"', html2)
print("replacements", n, "slide10", m.group(1) if m else None)
