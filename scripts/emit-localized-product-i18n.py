#!/usr/bin/env python3
"""Emit localized-product-i18n.mjs from localized_product_i18n_strings.py"""
from __future__ import annotations

import json
from pathlib import Path

from localized_product_i18n_strings import FEATURE_FROM_APP, STRINGS

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "localized-product-i18n.mjs"


def j(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def emit_obj_obj(obj: dict, indent: int) -> str:
    pad = " " * indent
    lines = ["{"]
    for k, v in obj.items():
        if isinstance(v, dict) and all(x in v for x in ("es", "de", "fr", "pt", "zh", "it", "hi")):
            lines.append(f"{pad}  {j(k)}: {{")
            for loc in ("es", "de", "fr", "pt", "zh", "it", "hi"):
                lines.append(f"{pad}    {loc}: {j(v[loc])},")
            lines.append(f"{pad}  }},")
        else:
            lines.append(f"{pad}  {j(k)}: {emit_obj_obj(v, indent + 2)},")
    lines.append(f"{pad}}}")
    return "\n".join(lines)


def main() -> None:
    locale_meta = {
        "es": {"htmlLang": "es", "ogLocale": "es_ES", "label": "Español"},
        "de": {"htmlLang": "de", "ogLocale": "de_DE", "label": "Deutsch"},
        "fr": {"htmlLang": "fr", "ogLocale": "fr_FR", "label": "Français"},
        "pt": {"htmlLang": "pt", "ogLocale": "pt_PT", "label": "Português"},
        "zh": {"htmlLang": "zh-Hans", "ogLocale": "zh_CN", "label": "中文"},
        "it": {"htmlLang": "it", "ogLocale": "it_IT", "label": "Italiano"},
        "hi": {"htmlLang": "hi", "ogLocale": "hi_IN", "label": "हिन्दी"},
    }

    parts = [
        "/**",
        " * Localized UI strings for product landing pages:",
        " * PocketBudJet (pbj), Handy Horology Helper (hhh), Curator's Vault (cvc), Unscribe.",
        " * Keys match exact English source copy on the en pages.",
        " */",
        "",
        "export const LOCALES = ['es', 'de', 'fr', 'pt', 'zh', 'it', 'hi'];",
        "",
        "export const LOCALE_META = " + json.dumps(locale_meta, ensure_ascii=False, indent=2) + ";",
        "",
        "export const STRINGS = {",
    ]
    for key in sorted(STRINGS.keys(), key=lambda s: (s.lower(), s)):
        v = STRINGS[key]
        parts.append(f"  {j(key)}: {{")
        for loc in ("es", "de", "fr", "pt", "zh", "it", "hi"):
            parts.append(f"    {loc}: {j(v[loc])},")
        parts.append("  },")
    parts.append("};")
    parts.append("")
    parts.append("export const FEATURE_FROM_APP = {")
    for loc in ("es", "de", "fr", "pt", "zh", "it", "hi"):
        feats = FEATURE_FROM_APP[loc]
        parts.append(f"  {loc}: {{")
        for fk, fv in feats.items():
            parts.append(f"    {j(fk)}: {j(fv)},")
        parts.append("  },")
    parts.append("};")
    parts.append("")

    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"Wrote {OUT} ({len(STRINGS)} strings)")


if __name__ == "__main__":
    main()