#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sync(rel: str) -> None:
    out = ROOT / rel
    narr = json.loads((out / "narration-en.json").read_text(encoding="utf-8"))
    html_path = out / "index.html"
    html = html_path.read_text(encoding="utf-8")
    new_arr = json.dumps(narr, ensure_ascii=False)
    html2, n = re.subn(r"const NARRATION = \[.*?\];", "const NARRATION = " + new_arr + ";", html, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f"{rel}: NARRATION replace count={n}")
    html_path.write_text(html2, encoding="utf-8")
    print(rel, "slides", len(narr), "ok")


if __name__ == "__main__":
    sync("videos/cvc/user-guide")
    sync("videos/hhh/user-guide")
    sync("videos/pbj/user-guide")
