#!/usr/bin/env python3
"""Generate product_i18n_translations_bulk.py for missing curated keys."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from deep_translator import GoogleTranslator

ROOT = Path(__file__).parent
MISSING = ROOT / "_missing_keys.txt"
OUT = ROOT / "product_i18n_translations_bulk.py"
PARTIAL = ROOT / "product_i18n_bulk_partial.json"

BRANDS = [
    "PocketBudJet", "PBJ", "Handy Horology Helper", "HHH", "Curator's Vault",
    "Classics", "Unscribe", "JosspaTech", "Joss-pah-tech", "Coach", "Grail Radar",
    "Web Companion", "My Museum", "Clockworks.com", "Google Play", "App Store",
    "Apple", "Google", "CSV", "OFX", "QFX", "QIF", "XLSX", "PDF", "JSON", "AI",
    "Pro", "Premium",
]

LANGS = {"es": "es", "de": "de", "fr": "fr", "pt": "pt", "zh": "zh-CN", "it": "it", "hi": "hi"}


def protect(text: str) -> tuple[str, list[str]]:
    tokens: list[str] = []

    def keep(m):
        tokens.append(m.group(0))
        return f"⟦{len(tokens)-1}⟧"

    for b in sorted(BRANDS, key=len, reverse=True):
        text = re.sub(re.escape(b), keep, text)
    text = re.sub(r"\$[\d.,]+(?:/mo|/yr)?", keep, text)
    text = re.sub(r"\b14 free days on your phone\b", keep, text)
    text = re.sub(r"\bFirst five\b", keep, text)
    text = re.sub(r"\bfirst five\b", keep, text)
    return text, tokens


def restore(text: str, tokens: list[str]) -> str:
    for i, tok in enumerate(tokens):
        text = text.replace(f"⟦{i}⟧", tok)
    return text


def translate_batch(texts: list[str], target: str) -> list[str]:
    for attempt in range(5):
        try:
            protected = [protect(t) for t in texts]
            payload = [p[0] for p in protected]
            outs = GoogleTranslator(source="en", target=target).translate_batch(payload)
            return [restore(o or texts[i], protected[i][1]) for i, o in enumerate(outs)]
        except Exception as e:
            wait = 2 ** attempt
            print("retry", target, attempt, e, "sleep", wait)
            time.sleep(wait)
    return texts


def main() -> None:
    keys = [k for k in MISSING.read_text(encoding="utf-8").splitlines() if k.strip()]
    bulk: dict[str, dict] = {}
    if PARTIAL.is_file():
        bulk = json.loads(PARTIAL.read_text(encoding="utf-8"))

    for loc, code in LANGS.items():
        todo = [k for k in keys if k not in bulk or loc not in bulk[k]]
        print(loc, len(todo))
        batch_size = 20
        for i in range(0, len(todo), batch_size):
            chunk = todo[i : i + batch_size]
            outs = translate_batch(chunk, code)
            for k, out in zip(chunk, outs):
                bulk.setdefault(k, {})[loc] = out
            PARTIAL.write_text(json.dumps(bulk, ensure_ascii=False, indent=2), encoding="utf-8")
            time.sleep(2.5)

    lines = [
        '# -*- coding: utf-8 -*-',
        '"""Bulk translations for product landing pages."""',
        '',
        'BULK = ',
        json.dumps(bulk, ensure_ascii=False, indent=2),
        '',
    ]
    OUT.write_text('\n'.join(lines), encoding="utf-8")
    print('Wrote', OUT, len(bulk))


if __name__ == '__main__':
    main()