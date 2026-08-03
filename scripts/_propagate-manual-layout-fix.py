#!/usr/bin/env python3
"""Propagate layout/highlight/breadcrumb CSS fixes from EN masters to all locales.

Does NOT retranslate or regenerate audio — language content stays as-is.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODES = ["de", "es", "fr", "hi", "it", "pt", "zh"]
BUST = "layout-fix-2026-07-27"


def patch_hhh_html(html: str) -> str:
    html = re.sub(
        r"\.breadcrumbs \{ max-width: 1200px; margin: 0 auto; padding: 1rem 2rem 0; font-size: 0\.9rem; color: var\(--slate\); \}\s*"
        r"\.breadcrumbs a \{ color: var\(--navy-medium\); text-decoration: none; font-weight: 500; \}",
        ".breadcrumbs { max-width: 1200px; margin: 0 auto; padding: 1rem 2rem 0; font-size: 0.95rem; color: var(--slate); }\n"
        "         .breadcrumbs a { color: var(--navy-medium); text-decoration: underline; text-underline-offset: 3px; font-weight: 700; }\n"
        "         .breadcrumbs a:hover { color: var(--gold-dark); }\n"
        "         .breadcrumbs span.sep { margin: 0 0.45rem; color: var(--slate-light); }\n"
        "         .breadcrumbs span.current { color: var(--navy); font-weight: 700; }",
        html,
        count=1,
    )
    # If already patched to 0.95rem, leave; also force phone max-height none
    html = html.replace(
        "aspect-ratio: 9/19.5; max-height: 640px; position: relative;",
        "aspect-ratio: 9/19.5; max-height: none; position: relative;",
    )
    html = re.sub(
        r"\.transcript-sentence \{ transition: color 0\.2s ease, font-weight 0\.2s ease; \}\s*"
        r"\.transcript-sentence\.active \{ color: var\(--navy\); font-weight: 600; \}\s*"
        r"\.transcript-sentence\.past \{ color: var\(--navy\); opacity: 0\.75; \}",
        ".transcript-sentence { transition: color 0.2s ease, background-color 0.2s ease, font-weight 0.2s ease; border-radius: 3px; }\n"
        "         .transcript-sentence.active {\n"
        "           color: var(--navy-dark); font-weight: 700;\n"
        "           background: rgba(200, 170, 110, 0.42);\n"
        "           box-decoration-break: clone; -webkit-box-decoration-break: clone;\n"
        "           padding: 0.05em 0.2em;\n"
        "         }\n"
        "         .transcript-sentence.past { color: var(--slate); opacity: 0.9; }",
        html,
        count=1,
    )
    html = re.sub(
        r'href="walkthrough\.css"',
        f'href="walkthrough.css?v={BUST}"',
        html,
        count=1,
    )
    html = re.sub(
        r'deck\.js\?v=[^"]+',
        f"deck.js?v={BUST}",
        html,
        count=1,
    )
    return html


def patch_pbj_html(html: str) -> str:
    html = re.sub(
        r"\.breadcrumbs \{\s*max-width: 1200px; margin: 0 auto; padding: 1rem 2rem 0;\s*"
        r"font-size: 0\.9rem; color: var\(--slate\);\s*\}\s*"
        r"\.breadcrumbs a \{ color: var\(--navy-medium\); text-decoration: none; font-weight: 500; \}\s*"
        r"\.breadcrumbs a:hover \{ color: var\(--gold-dark\); text-decoration: underline; \}\s*"
        r"\.breadcrumbs span\.sep \{ margin: 0 0\.4rem; color: var\(--slate-light\); \}\s*"
        r"\.breadcrumbs span\.current \{ color: var\(--navy\); font-weight: 600; \}",
        ".breadcrumbs {\n"
        " max-width: 1200px; margin: 0 auto; padding: 1rem 2rem 0;\n"
        " font-size: 0.95rem; color: var(--slate);\n"
        " }\n"
        " .breadcrumbs a { color: var(--navy-medium); text-decoration: underline; text-underline-offset: 3px; font-weight: 700; }\n"
        " .breadcrumbs a:hover { color: var(--gold-dark); }\n"
        " .breadcrumbs span.sep { margin: 0 0.45rem; color: var(--slate-light); }\n"
        " .breadcrumbs span.current { color: var(--navy); font-weight: 700; }",
        html,
        count=1,
    )
    html = re.sub(
        r"\.transcript-sentence \{\s*transition: color 0\.2s ease, font-weight 0\.2s ease;\s*\}\s*"
        r"\.transcript-sentence\.active \{\s*color: var\(--navy\); font-weight: 600;\s*\}\s*"
        r"\.transcript-sentence\.past \{ color: var\(--navy\); \}",
        ".transcript-sentence {\n"
        " transition: color 0.2s ease, background-color 0.2s ease, font-weight 0.2s ease;\n"
        " border-radius: 3px;\n"
        " }\n"
        " .transcript-sentence.active {\n"
        " color: var(--navy); font-weight: 700;\n"
        " background: rgba(240, 192, 64, 0.42);\n"
        " box-decoration-break: clone; -webkit-box-decoration-break: clone;\n"
        " padding: 0.05em 0.2em;\n"
        " }\n"
        " .transcript-sentence.past { color: var(--slate); opacity: 0.9; }",
        html,
        count=1,
    )
    html = re.sub(
        r'href="walkthrough\.css"',
        f'href="walkthrough.css?v={BUST}"',
        html,
        count=1,
    )
    return html


def main() -> None:
    hhh_en = ROOT / "videos" / "user-guide-hhh"
    pbj_en = ROOT / "videos" / "user-guide"
    hhh_css = (hhh_en / "walkthrough.css").read_text(encoding="utf-8")
    pbj_css = (pbj_en / "walkthrough.css").read_text(encoding="utf-8")

    # Cache-bust EN too
    for en, patcher in ((hhh_en, patch_hhh_html), (pbj_en, patch_pbj_html)):
        p = en / "index.html"
        p.write_text(patcher(p.read_text(encoding="utf-8")), encoding="utf-8")

    for code in CODES:
        hhh = ROOT / "videos" / f"user-guide-hhh-{code}"
        if hhh.exists():
            shutil.copy2(hhh_en / "walkthrough.css", hhh / "walkthrough.css")
            # keep deck.js from locale but ensure identical to EN (tap sync)
            shutil.copy2(hhh_en / "deck.js", hhh / "deck.js")
            idx = hhh / "index.html"
            idx.write_text(patch_hhh_html(idx.read_text(encoding="utf-8")), encoding="utf-8")
            print(f"hhh-{code}: css+deck+highlight/breadcrumb")

        pbj = ROOT / "videos" / f"user-guide-{code}"
        if pbj.exists():
            shutil.copy2(pbj_en / "walkthrough.css", pbj / "walkthrough.css")
            if (pbj_en / "deck.js").exists():
                shutil.copy2(pbj_en / "deck.js", pbj / "deck.js")
            idx = pbj / "index.html"
            idx.write_text(patch_pbj_html(idx.read_text(encoding="utf-8")), encoding="utf-8")
            print(f"pbj-{code}: css+deck+highlight/breadcrumb")

    print("done")


if __name__ == "__main__":
    main()
