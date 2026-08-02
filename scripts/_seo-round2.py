#!/usr/bin/env python3
"""SEO round 2: sitemap rebuild, product OG crops, hub OG JPEG compress helper."""
from __future__ import annotations

import os
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]

# Canonical indexable URLs only (no redirect shells, no 404s).
# lastmod is honest only for pages we know we touched this round.
SITEMAP = [
    ("https://josspatech.com/", "2026-08-02"),
    ("https://josspatech.com/hhh/", "2026-08-02"),
    ("https://josspatech.com/pbj/", "2026-08-02"),
    ("https://josspatech.com/cvc/", "2026-08-02"),
    ("https://josspatech.com/for-professionals/", "2026-08-02"),
    ("https://josspatech.com/how-to/", "2026-08-02"),
    ("https://josspatech.com/how-to/faq/", "2026-08-02"),
    ("https://josspatech.com/getting-started/", "2026-08-02"),
    ("https://josspatech.com/videos/pocketbudjet/partner-showcase/", "2026-07-09"),
    ("https://josspatech.com/videos/user-guide/", "2026-08-02"),
    ("https://josspatech.com/videos/user-guide-es/", "2026-06-25"),
    ("https://josspatech.com/videos/user-guide-zh/", "2026-06-25"),
    ("https://josspatech.com/videos/user-guide-de/", "2026-06-25"),
    ("https://josspatech.com/videos/user-guide-fr/", "2026-06-25"),
    ("https://josspatech.com/videos/user-guide-pt/", "2026-06-25"),
    ("https://josspatech.com/videos/user-guide-it/", "2026-06-25"),
    ("https://josspatech.com/videos/user-guide-hi/", "2026-06-25"),
    ("https://josspatech.com/videos/hhh/", "2026-08-02"),
    ("https://josspatech.com/videos/hhh/walkthrough/", "2026-08-02"),
    ("https://josspatech.com/videos/user-guide-hhh/", "2026-07-24"),
    ("https://josspatech.com/docs/pocketbudjet/PocketBudJet_PrivacyPolicy.html", "2026-06-05"),
    ("https://josspatech.com/docs/pocketbudjet/PocketBudJet_TermsOfService.html", "2026-06-05"),
    ("https://josspatech.com/docs/pocketbudjet/PocketBudJet_EULA.html", "2026-06-05"),
    ("https://josspatech.com/docs/pocketbudjet/PocketBudJet_DataDeletion.html", "2026-06-05"),
    ("https://josspatech.com/docs/pocketbudjet/HowWeMakeMoney.html", "2026-06-05"),
    ("https://josspatech.com/docs/pocketbudjet/WhyLocalFirst.html", "2026-06-05"),
]


def write_sitemap() -> None:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, lastmod in SITEMAP:
        lines += [
            "  <url>",
            f"    <loc>{loc}</loc>",
            f"    <lastmod>{lastmod}</lastmod>",
            "  </url>",
        ]
    lines.append("</urlset>")
    out = ROOT / "sitemap.xml"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote sitemap ({len(SITEMAP)} urls)")


def font(size: int, bold: bool = False):
    paths = (
        [r"C:\Windows\Fonts\georgiab.ttf", r"C:\Windows\Fonts\georgia.ttf"]
        if bold
        else [r"C:\Windows\Fonts\georgia.ttf", r"C:\Windows\Fonts\segoeui.ttf"]
    )
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def crop_og(src: Path, dest: Path, title: str, subtitle: str, accent: tuple) -> None:
    W, H = 1200, 630
    canvas = Image.new("RGB", (W, H), (12, 51, 88))
    if src.exists():
        im = Image.open(src).convert("RGB")
        scale = max(W / im.width, H / im.height)
        nw, nh = int(im.width * scale), int(im.height * scale)
        im = im.resize((nw, nh), Image.Resampling.LANCZOS)
        left, top = (nw - W) // 2, (nh - H) // 2
        canvas.paste(im.crop((left, top, left + W, top + H)), (0, 0))
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        for x in range(0, 780):
            a = int(190 * (1 - x / 780))
            od.line([(x, 0), (x, H)], fill=(8, 34, 58, a))
        canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(canvas)
    draw.text((64, 190), title, fill=(255, 255, 255), font=font(54, bold=True))
    draw.rectangle([64, 270, 300, 276], fill=accent)
    draw.text((64, 300), subtitle, fill=(230, 230, 230), font=font(26))
    draw.text((64, 520), "JosspaTech · Joss-pah-tech", fill=accent, font=font(22))
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Prefer JPEG under ~300KB for WhatsApp/messenger previews
    jpg = dest.with_suffix(".jpg")
    canvas.save(jpg, "JPEG", quality=82, optimize=True, progressive=True)
    canvas.save(dest, "PNG", optimize=True)
    print("wrote", jpg, jpg.stat().st_size, "and", dest, dest.stat().st_size)


def make_product_ogs() -> None:
    shots = ROOT / "assets" / "screenshots"
    brand = ROOT / "assets" / "brand"
    specs = [
        (shots / "app-hhh-hero.png", brand / "og-hhh.png", "Handy Horology Helper", "Confirm your suspicions.", (200, 170, 110)),
        (shots / "app-pbj-hero.png", brand / "og-pbj.png", "PocketBudJet", "Import. Plan. Coach.", (240, 192, 64)),
        (shots / "app-cvc-hero.png", brand / "og-cvc.png", "Curator's Vault: Classics", "Your vault. Your rules.", (212, 168, 83)),
    ]
    for src, dest, title, sub, accent in specs:
        crop_og(src, dest, title, sub, accent)

    # Compress hub OG as JPEG companion; keep PNG for existing tags but rewrite to JPG in HTML separately
    hub_png = brand / "og-josspatech.png"
    if hub_png.exists():
        im = Image.open(hub_png).convert("RGB")
        hub_jpg = brand / "og-josspatech.jpg"
        im.save(hub_jpg, "JPEG", quality=82, optimize=True, progressive=True)
        print("wrote", hub_jpg, hub_jpg.stat().st_size)


def ensure_meta(path: Path, *, title: str | None, description: str, canonical: str, og_image: str) -> None:
    text = path.read_text(encoding="utf-8")
    if 'rel="canonical"' in text or "rel='canonical'" in text:
        # still ensure description if missing
        if 'name="description"' not in text and "name='description'" not in text:
            insert = f'<meta name="description" content="{description}">\n'
            text = re.sub(r"(<title>.*?</title>)", r"\1\n" + insert, text, count=1, flags=re.I | re.S)
            path.write_text(text, encoding="utf-8")
            print("added description", path)
        return

    block = f'''<meta name="description" content="{description}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title or path.name}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="JosspaTech">
<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title or path.name}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{og_image}">
'''
    if re.search(r"<title>.*?</title>", text, re.I | re.S):
        text2, n = re.subn(
            r"(<title>.*?</title>)",
            r"\1\n" + block,
            text,
            count=1,
            flags=re.I | re.S,
        )
        if n:
            path.write_text(text2, encoding="utf-8")
            print("added meta", path)
            return
    # fallback: after charset
    text2, n = re.subn(
        r'(<meta charset="UTF-8">)',
        r"\1\n" + block,
        text,
        count=1,
        flags=re.I,
    )
    if n:
        path.write_text(text2, encoding="utf-8")
        print("added meta (charset)", path)
    else:
        print("SKIP meta", path)


def patch_key_pages() -> None:
    og_hub = "https://josspatech.com/assets/brand/og-josspatech.jpg"
    og_pbj = "https://josspatech.com/assets/brand/og-pbj.jpg"
    og_hhh = "https://josspatech.com/assets/brand/og-hhh.jpg"
    pages = [
        (
            ROOT / "for-professionals" / "index.html",
            "For CPAs, Planners, Brokers — Hand Off Clean Data | PocketBudJet",
            "Banks make exports painful. PocketBudJet lets your client hand you a tax-ready packet, a refi-ready cash-flow file, or a planner-ready OFX in two taps.",
            "https://josspatech.com/for-professionals/",
            og_pbj,
        ),
        (
            ROOT / "getting-started" / "index.html",
            "Getting Started - PocketBudJet | JosspaTech",
            "Get started with PocketBudJet: install, import a statement, set a budget, and try Premium for 15 days. Private budgeting by JosspaTech.",
            "https://josspatech.com/getting-started/",
            og_pbj,
        ),
        (
            ROOT / "videos" / "user-guide" / "index.html",
            "PocketBudJet User Manual | JosspaTech",
            "PocketBudJet user manual — narrated chapters covering import, budgets, coach, bank sync, exports, and privacy.",
            "https://josspatech.com/videos/user-guide/",
            og_pbj,
        ),
        (
            ROOT / "videos" / "user-guide-hhh" / "index.html",
            "Handy Horology Helper User Manual | JosspaTech",
            "Handy Horology Helper user manual — install through Identify, Museum, Demand, Hunt, Clockworks, and Pro.",
            "https://josspatech.com/videos/user-guide-hhh/",
            og_hhh,
        ),
        (
            ROOT / "videos" / "hhh" / "index.html",
            None,
            "Handy Horology Helper video guides — short walkthrough and detailed user manual from JosspaTech.",
            "https://josspatech.com/videos/hhh/",
            og_hhh,
        ),
        (
            ROOT / "videos" / "hhh" / "walkthrough" / "index.html",
            None,
            "Short overview of Handy Horology Helper — museum, AI Identify, Clockworks, Grail Radar, finances, Web Companion, and Pro.",
            "https://josspatech.com/videos/hhh/walkthrough/",
            og_hhh,
        ),
        (
            ROOT / "videos" / "pocketbudjet" / "partner-showcase" / "index.html",
            None,
            "PocketBudJet partner showcase — see private budgeting, import, coach, and Premium trial features.",
            "https://josspatech.com/videos/pocketbudjet/partner-showcase/",
            og_pbj,
        ),
    ]
    for path, title, desc, can, img in pages:
        if path.exists():
            ensure_meta(path, title=title, description=desc, canonical=can, og_image=img)

    # Locale manuals — description + canonical + hreflang cluster
    locales = [
        ("", "en"),
        ("-es", "es"),
        ("-zh", "zh"),
        ("-de", "de"),
        ("-fr", "fr"),
        ("-pt", "pt"),
        ("-it", "it"),
        ("-hi", "hi"),
    ]
    hrefs = []
    for suffix, code in locales:
        folder = "user-guide" if not suffix else f"user-guide{suffix}"
        url = f"https://josspatech.com/videos/{folder}/"
        hrefs.append((code, url))
    href_block = "\n".join(
        f'<link rel="alternate" hreflang="{code}" href="{url}">' for code, url in hrefs
    )
    href_block += f'\n<link rel="alternate" hreflang="x-default" href="https://josspatech.com/videos/user-guide/">'

    for suffix, code in locales:
        folder = "user-guide" if not suffix else f"user-guide{suffix}"
        path = ROOT / "videos" / folder / "index.html"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if 'hreflang="' not in text:
            # insert after title if present
            insert = href_block + "\n"
            text2, n = re.subn(
                r"(<title>.*?</title>)",
                r"\1\n" + insert,
                text,
                count=1,
                flags=re.I | re.S,
            )
            if n:
                path.write_text(text2, encoding="utf-8")
                print("hreflang", path)
        ensure_meta(
            path,
            title=None,
            description=f"PocketBudJet user manual ({code}) — narrated chapters by JosspaTech.",
            canonical=f"https://josspatech.com/videos/{folder}/",
            og_image=og_pbj,
        )

    # Docs: light canonical + description
    docs = [
        ("PocketBudJet_PrivacyPolicy.html", "PocketBudJet Privacy Policy — how JosspaTech handles your data."),
        ("PocketBudJet_TermsOfService.html", "PocketBudJet Terms of Service."),
        ("PocketBudJet_EULA.html", "PocketBudJet End User License Agreement."),
        ("PocketBudJet_DataDeletion.html", "How to request PocketBudJet data deletion."),
        ("HowWeMakeMoney.html", "How PocketBudJet makes money — subscriptions, not ads or data sales."),
        ("WhyLocalFirst.html", "Why PocketBudJet is local-first — your financial data stays on your device."),
    ]
    for name, desc in docs:
        path = ROOT / "docs" / "pocketbudjet" / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if 'rel="canonical"' in text:
            continue
        can = f"https://josspatech.com/docs/pocketbudjet/{name}"
        block = f'<meta name="description" content="{desc}">\n<link rel="canonical" href="{can}">\n<meta name="robots" content="index, follow">\n'
        text2, n = re.subn(
            r"(<title>.*?</title>)",
            r"\1\n" + block,
            text,
            count=1,
            flags=re.I | re.S,
        )
        if n:
            path.write_text(text2, encoding="utf-8")
            print("docs meta", name)


if __name__ == "__main__":
    write_sitemap()
    make_product_ogs()
    patch_key_pages()
