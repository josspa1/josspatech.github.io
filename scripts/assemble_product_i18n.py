#!/usr/bin/env python3
"""Assemble final localized-product-i18n.mjs with curated keys."""
from __future__ import annotations

import json
import re
from pathlib import Path

from localized_product_i18n_strings import FEATURE_FROM_APP, STRINGS as STRINGS_A
from localized_product_i18n_strings_ext import STRINGS_EXT
from localized_product_i18n_strings_ext_rest import STRINGS_EXT_REST

OUT = Path(__file__).parent / "localized-product-i18n.mjs"
EXTRACTED = Path(__file__).parent / "_extracted-strings.txt"

STRINGS = {**STRINGS_A, **STRINGS_EXT, **STRINGS_EXT_REST}

# Curated keys from first HTML extract (minus noise)
EXTRA_KEYS = []
if EXTRACTED.is_file():
    for block in EXTRACTED.read_text(encoding="utf-8").split("---\n"):
        s = block.strip()
        if not s or s.isdigit() or s.lstrip("\ufeff") == "270":
            continue
        s = s.lstrip("\ufeff")
        if s in {"#0C3358", "#FAF6EF", "1200", "630", "*", "en_US", "image/jpeg", "website", "summary_large_image"}:
            continue
        if s.startswith("index, follow") or s.startswith("width=device-width"):
            continue
        EXTRA_KEYS.append(s)

# Explicit additions missing from naive extract
EXTRA_KEYS += [
    "Private budgeting from JosspaTech (pronounced Joss-pah-tech). Import bank statements, plan spending, track debt, and coach yourself. Your budget is stored on your phone. No bank login. No account numbers. Ad-free — we don’t sell your data.",
    "Import — CSV, OFX, QFX, QIF, XLSX, and PDF statements worldwide.",
    "Plan — budgets, bills, debt planner, and reports.",
    "Stay private — no ads, no account, no bank login. Your budget is stored on your phone; we don’t sell your data.",
    "Bring in a statement — share a PDF or spreadsheet from the app that has it. The first screen shows the steps.",
    "See the list — each subscription, what it costs, when it renews, and how steady the charges have been.",
    "Get a reminder — the day before a renewal, a free trial ends, or the last day to cancel.",
    "Cancel — opens that company's current cancel page. Some pages have a button. Some only tell you to call, visit, or cancel with Apple or Google. If Apple or Google bills you, Unscribe opens that store's subscription list.",
    "The first five subscriptions stay free. Pro is $29.99 once, or $9.99 a year. No monthly plan. No free trial on the paid plan. Pro is the full list, reminders, price-increase and duplicate flags, cancel help for every subscription, and a CSV export.",
    "Plan and policy below. How-to chapters: watch the real app.",
    "How Identify and the vault work is in the how-to videos above. These are the plan and policy questions.",
    "How Identify and Museum work is in the how-to videos above. These are the plan and policy questions.",
    "You can see the piece. You often already have a gut read. What you do not have is time to dig through a reference library. HHH is that library in your pocket — answers, not a lecture.",
    "Identify — confirm a watch or clock from photos you take and the clues you already have (name on the dial, marks, era). Model, metal, rough worth, confidence.",
    "My Museum — organize your private collection on the device: photos, service notes, values. Not a public gallery.",
    "Clock Repair Help — interactive troubleshooting and a clock-parts database when a movement stops.",
    "Demand — a want list you can hand a dealer, so they see what you are looking for.",
    "Hunt / Grail Radar — listing alerts for pieces you actually want, at a price you set.",
    "Identify — series, era, and grading cues from a photo, with honest confidence.",
    "Vault — photos, condition, provenance, and value for five categories on the device.",
    "Value — portfolio view and cost basis so you buy, sell, or insure from a clearer number.",
    "Visit our friends at Clockworks.com for clock parts and repair supplies.",
    "Your information lives on your phone, and only on your phone. The app keeps it there so it can show it to you — and we never keep a copy of it anywhere, and we can't see it. There's no bank login, so the app never receives your bank password or account numbers. And there's no account and no sign-in, so nothing is tied to your name — to anyone but you, it's just numbers and transactions, with no name on them. When you show the app a statement, it reads it, does the math, and puts the results on your phone. That's the whole story.",
    "Coach and receipt scan briefly process spending you already entered when you ask — then that request is done. We don’t sell your data. Money comes from subscriptions, not your statement. See also the Privacy Policy.",
    "In plain English — Your information lives on your phone, and only on your phone. The app keeps it there so it can show it to you — and we never keep a copy of it anywhere, and we can't see it. There's no bank login, so the app never receives your bank password or account numbers. And there's no account and no sign-in, so nothing is tied to your name — to anyone but you, it's just numbers and transactions, with no name on them. When you show the app a statement, it reads it, does the math, and puts the results on your phone. That's the whole story. When you ask Coach or scan a receipt, we briefly look at the spending you already entered — like “store · $12” — so we can answer; that request isn’t how we keep your books, and we don’t sell it.",
]

# Import bulk auto translations
from product_i18n_translations_bulk import BULK  # noqa: E402

STRINGS.update(BULK)

for k in EXTRA_KEYS:
    if k not in STRINGS and k in BULK:
        STRINGS[k] = BULK[k]

missing = [k for k in EXTRA_KEYS if k not in STRINGS]

def j(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


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

    lines = [
        "/**",
        " * Localized UI strings for product landing pages:",
        " * PocketBudJet (pbj), Handy Horology Helper (hhh), Curator's Vault (cvc), Unscribe.",
        " */",
        "",
        "export const LOCALES = ['es', 'de', 'fr', 'pt', 'zh', 'it', 'hi'];",
        "",
        f"export const LOCALE_META = {json.dumps(locale_meta, ensure_ascii=False, indent=2)};",
        "",
        "export const STRINGS = {",
    ]
    for key in sorted(STRINGS.keys(), key=lambda s: (s.lower(), s)):
        v = STRINGS[key]
        lines.append(f"  {j(key)}: {{")
        for loc in ("es", "de", "fr", "pt", "zh", "it", "hi"):
            lines.append(f"    {loc}: {j(v[loc])},")
        lines.append("  },")
    lines.append("};")
    lines.append("")
    lines.append("export const FEATURE_FROM_APP = {")
    for loc in ("es", "de", "fr", "pt", "zh", "it", "hi"):
        feats = FEATURE_FROM_APP[loc]
        lines.append(f"  {loc}: {{")
        for fk, fv in feats.items():
            lines.append(f"    {j(fk)}: {j(fv)},")
        lines.append("  },")
    lines.append("};")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT.name}: {len(STRINGS)} strings; still missing {len(missing)} curated keys")
    if missing:
        for m in missing[:30]:
            print("  -", m[:100])


if __name__ == "__main__":
    main()