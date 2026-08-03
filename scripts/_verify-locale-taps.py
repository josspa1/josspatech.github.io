#!/usr/bin/env python3
"""Verify locale manuals keep EN tap coords / images / slide structure."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def extract_taps(html: str) -> list[tuple]:
    slides = []
    for m in re.finditer(r'<div class="slide[^"]*"([^>]*)>', html):
        attrs = m.group(1)
        idx_m = re.search(r'data-index="(\d+)"', attrs)
        if not idx_m:
            continue
        i = int(idx_m.group(1))
        none = "data-tap-none" in attrs
        x = re.search(r'data-tap-x="([^"]*)"', attrs)
        y = re.search(r'data-tap-y="([^"]*)"', attrs)
        show = re.search(r'data-tap-show-at="([^"]*)"', attrs)
        dur = re.search(r'data-tap-duration="([^"]*)"', attrs)
        slides.append(
            (
                i,
                none,
                x.group(1) if x else None,
                y.group(1) if y else None,
                show.group(1) if show else None,
                dur.group(1) if dur else None,
            )
        )
    return slides


def extract_imgs(html: str) -> list[str]:
    return re.findall(r'<img src="([^"]+)"', html)


def check_pair(en_dir: Path, locale_prefix: str) -> int:
    en_html = (en_dir / "index.html").read_text(encoding="utf-8")
    en_t = extract_taps(en_html)
    en_imgs = extract_imgs(en_html)
    en_deck = en_dir / "deck.js"
    en_deck_txt = en_deck.read_text(encoding="utf-8") if en_deck.exists() else ""
    print(f"\n{en_dir.name}: EN slides={len(en_t)} imgs={len(en_imgs)}")
    errors = 0
    for code in ["de", "es", "fr", "hi", "it", "pt", "zh"]:
        loc_dir = ROOT / "videos" / f"{locale_prefix}-{code}"
        loc = loc_dir / "index.html"
        if not loc.exists():
            print(f"  {code}: not built yet")
            continue
        loc_html = loc.read_text(encoding="utf-8")
        loc_t = extract_taps(loc_html)
        loc_imgs = extract_imgs(loc_html)
        problems = []
        if len(loc_t) != len(en_t):
            problems.append(f"slide count {len(loc_t)}!={len(en_t)}")
        else:
            mism = sum(1 for a, b in zip(en_t, loc_t) if a != b)
            if mism:
                problems.append(f"{mism} tap coord/timing diffs")
        if loc_imgs != en_imgs:
            problems.append(f"img src mismatch ({len(loc_imgs)} vs {len(en_imgs)})")
        deck = loc_dir / "deck.js"
        if en_deck.exists() and deck.exists():
            # deck.js should be byte-identical (tap pulse logic)
            if deck.read_text(encoding="utf-8") != en_deck_txt:
                problems.append("deck.js differs from EN")
        if problems:
            errors += 1
            print(f"  {code}: FAIL — {'; '.join(problems)}")
        else:
            print(f"  {code}: OK taps+imgs+deck match EN ({len(loc_t)} slides)")
    return errors


def main() -> int:
    e = 0
    e += check_pair(ROOT / "videos" / "user-guide-hhh", "user-guide-hhh")
    e += check_pair(ROOT / "videos" / "user-guide", "user-guide")
    print(f"\n{'PASS' if e == 0 else f'{e} locale(s) with issues'}")
    return 1 if e else 0


if __name__ == "__main__":
    sys.exit(main())
