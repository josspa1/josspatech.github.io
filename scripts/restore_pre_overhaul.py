#!/usr/bin/env python3
"""Restore index.html from 9cf0830 + minimal stale fixes only."""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def git_show(commit: str) -> str:
    return subprocess.check_output(
        ["git", "show", f"{commit}:index.html"],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
    )


def extract_between(text: str, start: str, end: str) -> str:
    i = text.index(start)
    j = text.index(end, i)
    return text[i:j]


def replace_between(
    text: str, start: str, end: str, replacement: str, occurrence: int = 0
) -> str:
    i = text.index(start)
    for _ in range(occurrence):
        i = text.index(start, i + 1)
    j = text.index(end, i)
    return text[:i] + replacement + text[j:]


def strip_hero_shots(hero_block: str) -> str:
    return re.sub(
        r"\n    <div class=\"pbj-hero-shots\".*?</div>\n  </div>\n</section>",
        "\n  </div>\n</section>",
        hero_block,
        flags=re.DOTALL,
    )


def main() -> None:
    base = git_show("9cf0830")
    patch = git_show("3d2fb72")

    # --- PBJ: build number only ---
    base = base.replace("build 223", "build 236")

    # --- Company page cards ---
    hhh_card = extract_between(
        patch,
        "      <!-- Handy Horology Helper card -->\n",
        "      <!-- Curator's Vault: Classics card -->\n",
    )
    base = replace_between(
        base,
        "      <!-- Handy Horology Helper card -->\n",
        "      <!-- Curator's Vault: Classics card -->\n",
        hhh_card,
    )

    cvc_card = extract_between(
        patch,
        "      <!-- Curator's Vault: Classics card -->\n",
        "    </div>\n  </div>\n</section>\n\n<!--",
    )
    base = replace_between(
        base,
        "      <!-- Curator's Vault: Classics card -->\n",
        "    </div>\n  </div>\n</section>\n\n<!--",
        cvc_card,
    )

    hhh_page = patch[patch.index('<div class="page" id="page-hhh">') :]
    hhh_page = hhh_page[: hhh_page.index('<div class="page" id="page-cvc">')]

    # HHH hero (no screenshot strip)
    hhh_hero = strip_hero_shots(
        extract_between(
            hhh_page,
            '<div class="page" id="page-hhh">\n',
            '</div>\n</section>\n<div class="pstrip" style="background:rgba(200,170,110,0.06)',
        )
    )
    base = replace_between(
        base,
        '<div class="page" id="page-hhh">\n',
        '</div>\n</section>\n<div class="pstrip" style="background:rgba(200,170,110,0.06)',
        hhh_hero,
    )

    # HHH pstrip
    hhh_pstrip = extract_between(
        hhh_page,
        '<div class="pstrip" style="background:rgba(200,170,110,0.06);border-color:rgba(200,170,110,0.12);">\n',
        '\n</div>\n\n',
    )
    base = replace_between(
        base,
        '<div class="pstrip" style="background:rgba(200,170,110,0.06);border-color:rgba(200,170,110,0.12);">\n',
        '\n</div>\n\n<section class="sec" style="background:#0d1a28;padding:80px 24px;">\n',
        hhh_pstrip,
    )

    # HHH pricing through stay-updated (feature walls preserved in base)
    hhh_tail = extract_between(
        hhh_page,
        "<!-- Pricing Section -->\n",
        "<footer class=\"site-footer\" role=\"contentinfo\">\n",
    )
    base = replace_between(
        base,
        "<!-- Pricing Section -->\n",
        "<footer class=\"site-footer\" role=\"contentinfo\">\n",
        hhh_tail,
    )

    cvc_page = patch[patch.index('<div class="page" id="page-cvc">') :]

    cvc_hero = strip_hero_shots(
        extract_between(
            cvc_page,
            '<div class="page" id="page-cvc">\n',
            '</div>\n</section>\n<div class="pstrip" style="background:rgba(212,168,83,0.06)',
        )
    )
    base = replace_between(
        base,
        '<div class="page" id="page-cvc">\n',
        '</div>\n</section>\n<div class="pstrip" style="background:rgba(212,168,83,0.06)',
        cvc_hero,
    )

    cvc_pstrip = extract_between(
        cvc_page,
        '<div class="pstrip" style="background:rgba(212,168,83,0.06);border-color:rgba(212,168,83,0.12);">\n',
        '\n</div>\n\n',
    )
    base = replace_between(
        base,
        '<div class="pstrip" style="background:rgba(212,168,83,0.06);border-color:rgba(212,168,83,0.12);">\n',
        '\n</div>\n\n<section class="sec" style="background:#0d1a28;padding:80px 24px;">\n',
        cvc_pstrip,
    )

    cvc_tail = extract_between(
        cvc_page,
        "    <!-- Curator's Vault Badge -->\n",
        "<footer class=\"site-footer\" role=\"contentinfo\">\n",
    )
    base = replace_between(
        base,
        "    <!-- Curator's Vault Badge -->\n",
        "<footer class=\"site-footer\" role=\"contentinfo\">\n",
        cvc_tail,
    )

    for bad in ("shot-lightbox", "app-shots-sec", "shot-enlarge", "how-to-video"):
        if bad in base:
            raise SystemExit(f"Overhaul artifact still present: {bad}")

    INDEX.write_text(base, encoding="utf-8")
    print(f"Wrote {INDEX} ({len(base.splitlines())} lines)")


if __name__ == "__main__":
    main()
