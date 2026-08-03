#!/usr/bin/env python3
"""Put local walkthrough.css AFTER shared so full-phone layout wins."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUST = "layout-fix-2026-07-27b"
CODES = ["de", "es", "fr", "hi", "it", "pt", "zh"]

OLD = re.compile(
    r'<link rel="stylesheet" href="walkthrough\.css[^"]*">\s*'
    r'<link rel="stylesheet" href="/videos/shared/walkthrough\.css">',
    re.M,
)
NEW = (
    '<link rel="stylesheet" href="/videos/shared/walkthrough.css">\n'
    f'         <link rel="stylesheet" href="walkthrough.css?v={BUST}">'
)

# PBJ may use different indentation
OLD_PBJ = re.compile(
    r'<link rel="stylesheet" href="walkthrough\.css[^"]*">\s*'
    r'<link rel="stylesheet" href="/videos/shared/walkthrough\.css">',
    re.M,
)
NEW_PBJ = (
    '<link rel="stylesheet" href="/videos/shared/walkthrough.css">\n'
    f' <link rel="stylesheet" href="walkthrough.css?v={BUST}">'
)


def fix(path: Path, pbj: bool = False) -> None:
    t = path.read_text(encoding="utf-8")
    pat, repl = (OLD_PBJ, NEW_PBJ) if pbj else (OLD, NEW)
    t2, n = pat.subn(repl, t, count=1)
    if n == 0:
        # already reordered — just bump bust
        t2 = re.sub(
            r'href="walkthrough\.css\?v=[^"]+"',
            f'href="walkthrough.css?v={BUST}"',
            t,
            count=1,
        )
        if t2 == t:
            print(f"no-change {path}")
            return
    path.write_text(t2, encoding="utf-8")
    print(f"fixed {path}")


def main() -> None:
    fix(ROOT / "videos" / "user-guide-hhh" / "index.html")
    fix(ROOT / "videos" / "user-guide" / "index.html", pbj=True)
    for code in CODES:
        fix(ROOT / "videos" / f"user-guide-hhh-{code}" / "index.html")
        fix(ROOT / "videos" / f"user-guide-{code}" / "index.html", pbj=True)


if __name__ == "__main__":
    main()
