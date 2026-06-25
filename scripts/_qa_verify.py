#!/usr/bin/env python3
"""Verify walkthrough img src paths exist and user guides have tapToStart + 28 slides."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []


def check_imgs(html_path: Path) -> None:
    text = html_path.read_text(encoding="utf-8", errors="ignore")
    for m in re.finditer(r'src="(/[^"]+)"', text):
        rel = m.group(1).lstrip("/")
        if rel.startswith("http"):
            continue
        if not (ROOT / rel).exists():
            errors.append(f"MISSING IMG {rel} in {html_path.relative_to(ROOT)}")


for html in ROOT.rglob("*.html"):
    if "videos" in html.parts or "how-to" in html.parts:
        check_imgs(html)

print("USER GUIDES:")
for d in sorted((ROOT / "videos").glob("user-guide*")):
    idx = d / "index.html"
    if not idx.exists():
        continue
    html = idx.read_text(encoding="utf-8", errors="ignore")
    slides = len(re.findall(r'class="slide', html))
    tap = "tapToStart" in html
    ok = slides == 28 and tap
    print(f"  {d.name}: slides={slides} tapToStart={tap} {'OK' if ok else 'FAIL'}")
    if not ok:
        errors.append(f"USER GUIDE QA fail: {d.name}")

if errors:
    print("\nERRORS:")
    for e in errors:
        print(" ", e)
    sys.exit(1)
print("\nAll checks passed.")
