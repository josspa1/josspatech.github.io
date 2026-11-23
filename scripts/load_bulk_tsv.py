#!/usr/bin/env python3
"""Load product_i18n_bulk.tsv -> product_i18n_translations_bulk.py"""
from pathlib import Path

TSV = Path(__file__).parent / "product_i18n_bulk.tsv"
OUT = Path(__file__).parent / "product_i18n_translations_bulk.py"


def esc(s: str) -> str:
    return repr(s)


def main() -> None:
    bulk = {}
    for line in TSV.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 8:
            raise SystemExit(f"bad line ({len(parts)} cols): {line[:80]}")
        en, es, de, fr, pt, zh, it, hi = parts
        bulk[en] = {"es": es, "de": de, "fr": fr, "pt": pt, "zh": zh, "it": it, "hi": hi}
    lines = ["# -*- coding: utf-8 -*-", '"""Bulk translations from product_i18n_bulk.tsv."""', "", "BULK = {"]
    for en in sorted(bulk.keys(), key=lambda s: (s.lower(), s)):
        v = bulk[en]
        lines.append(f"    {esc(en)}: {{")
        for loc in ("es", "de", "fr", "pt", "zh", "it", "hi"):
            lines.append(f"        {esc(loc)}: {esc(v[loc])},")
        lines.append("    },")
    lines.append("}")
    lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(len(bulk), "->", OUT.name)


if __name__ == "__main__":
    main()