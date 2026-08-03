#!/usr/bin/env python3
"""Patch index.html SEO placement, OG JPGs, path links, PAGE_SEO.pal, display=swap."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "index.html"
text = path.read_text(encoding="utf-8")

# 1) display=swap on Google Fonts
text = text.replace(
    "family=IBM+Plex+Mono:wght@400;500;600\" rel=\"stylesheet\">",
    "family=IBM+Plex+Mono:wght@400;500;600&display=swap\" rel=\"stylesheet\">",
)

# 2) Extract SEO block (from comment through JSON-LD script end) and move after author meta
seo_re = re.compile(
    r"\n<!-- SEO & Social Meta Tags -->.*?</script>\n",
    re.S,
)
m = seo_re.search(text)
if not m:
    raise SystemExit("SEO block not found")
seo = m.group(0)
# Prefer JPEG OG
seo = seo.replace(
    "https://josspatech.com/assets/brand/og-josspatech.png",
    "https://josspatech.com/assets/brand/og-josspatech.jpg",
)
seo = seo.replace(
    '<meta property="og:image:type" content="image/png">',
    '<meta property="og:image:type" content="image/jpeg">',
)
seo = seo.replace(
    "https://josspatech.com/assets/screenshots/app-hhh-hero.png",
    "https://josspatech.com/assets/brand/og-hhh.jpg",
)
seo = seo.replace(
    "https://josspatech.com/assets/screenshots/app-pbj-hero.png",
    "https://josspatech.com/assets/brand/og-pbj.jpg",
)
seo = seo.replace(
    "https://josspatech.com/assets/screenshots/app-cvc-hero.png",
    "https://josspatech.com/assets/brand/og-cvc.jpg",
)

text = seo_re.sub("\n", text, count=1)

anchor = '<meta name="author" content="JosspaTech">\n'
if anchor not in text:
    raise SystemExit("author meta not found")
if "<!-- SEO & Social Meta Tags -->" not in text:
    text = text.replace(anchor, anchor + seo, 1)
else:
    print("SEO already early?")

# 3) Path links for crawlers (keep SPA onclick)
replacements = [
    (
        '<a href="#hhh" class="nav-mobile-link" onclick="showPage(\'hhh\');closeMenu();return false;">Handy Horology Helper</a>',
        '<a href="/hhh/" class="nav-mobile-link" onclick="showPage(\'hhh\');closeMenu();return false;">Handy Horology Helper</a>',
    ),
    (
        '<a href="#pbj" class="nav-mobile-link" onclick="showPage(\'pbj\');closeMenu();return false;">PocketBudJet</a>',
        '<a href="/pbj/" class="nav-mobile-link" onclick="showPage(\'pbj\');closeMenu();return false;">PocketBudJet</a>',
    ),
    (
        '<a href="#pbj" onclick="showPage(\'pbj\');return false;">PocketBudJet</a>',
        '<a href="/pbj/" onclick="showPage(\'pbj\');return false;">PocketBudJet</a>',
    ),
    (
        '<a href="#hhh" onclick="showPage(\'hhh\');return false;">Handy Horology Helper</a>',
        '<a href="/hhh/" onclick="showPage(\'hhh\');return false;">Handy Horology Helper</a>',
    ),
    (
        '<a href="#cvc" onclick="showPage(\'cvc\');return false;">Curator\'s Vault</a>',
        '<a href="/cvc/" onclick="showPage(\'cvc\');return false;">Curator\'s Vault</a>',
    ),
]
for old, new in replacements:
    text = text.replace(old, new)

# PAL / CVC CTA chips with em dashes
text = text.replace(
    'href="#pbj" onclick="showPage(\'pbj\');return false;" style="color:#E8B84A',
    'href="/pbj/" onclick="showPage(\'pbj\');return false;" style="color:#E8B84A',
)
text = text.replace(
    'href="#hhh" onclick="showPage(\'hhh\');return false;" style="color:#E8B84A',
    'href="/hhh/" onclick="showPage(\'hhh\');return false;" style="color:#E8B84A',
)
text = text.replace(
    'href="#cvc" onclick="showPage(\'cvc\');return false;" style="color:#E8B84A',
    'href="/cvc/" onclick="showPage(\'cvc\');return false;" style="color:#E8B84A',
)

# Hub cards: add crawlable data-href + change to use path when middle-click via wrapping isn't easy;
# inject hidden SEO links after hub-grid open
if 'id="hub-seo-product-links"' not in text:
    text = text.replace(
        '<div class="hub-grid">',
        '''<div class="hub-grid">
      <nav id="hub-seo-product-links" aria-label="Product pages" style="position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0">
        <a href="/pbj/">PocketBudJet</a>
        <a href="/hhh/">Handy Horology Helper</a>
        <a href="/cvc/">Curator\'s Vault: Classics</a>
      </nav>
''',
        1,
    )

# 4) PAGE_SEO updates
old_page_seo = """var PAGE_SEO = {
  company: {
    title: 'JosspaTech — Private Mobile Software',
    description: 'JosspaTech (pronounced Joss-pah-tech) builds private, finished mobile apps — Handy Horology Helper, PocketBudJet, and Curator\\'s Vault. Ad-free. Your data stays yours.',
    canonical: 'https://josspatech.com/',
    ogTitle: 'JosspaTech — Private Mobile Software',
    ogImage: 'https://josspatech.com/assets/brand/og-josspatech.png'
  },
  hhh: {
    title: 'Handy Horology Helper — Confirm your suspicions | JosspaTech',
    description: 'Handy Horology Helper for new or vintage watches and clocks. Floor or bench. Confirm your suspicions. Private horology app by JosspaTech (Joss-pah-tech).',
    canonical: 'https://josspatech.com/hhh/',
    ogTitle: 'Handy Horology Helper — Confirm your suspicions.',
    ogImage: 'https://josspatech.com/assets/screenshots/app-hhh-hero.png'
  },
  pbj: {
    title: 'PocketBudJet — Private Budgeting | JosspaTech',
    description: 'PocketBudJet: import statements, plan spending, and coach yourself privately on your device. 15-day Premium trial. Ad-free. By JosspaTech (Joss-pah-tech).',
    canonical: 'https://josspatech.com/pbj/',
    ogTitle: 'PocketBudJet — Import. Plan. Coach.',
    ogImage: 'https://josspatech.com/assets/screenshots/app-pbj-hero.png'
  },
  cvc: {
    title: 'Curator\\'s Vault: Classics — Collectibles Catalog | JosspaTech',
    description: 'Curator\\'s Vault: Classics — photograph, organize, and value coins, cards, stamps, paper money, and lighters. Private collectibles catalog by JosspaTech (Joss-pah-tech).',
    canonical: 'https://josspatech.com/cvc/',
    ogTitle: 'Curator\\'s Vault: Classics — Your vault. Your rules.',
    ogImage: 'https://josspatech.com/assets/screenshots/app-cvc-hero.png'
  }
};"""

new_page_seo = """var PAGE_SEO = {
  company: {
    title: 'JosspaTech — Private Mobile Software',
    description: 'JosspaTech (pronounced Joss-pah-tech) builds private, finished mobile apps — Handy Horology Helper, PocketBudJet, and Curator\\'s Vault. Ad-free. Your data stays yours.',
    canonical: 'https://josspatech.com/',
    ogTitle: 'JosspaTech — Private Mobile Software',
    ogImage: 'https://josspatech.com/assets/brand/og-josspatech.jpg'
  },
  hhh: {
    title: 'Handy Horology Helper — Confirm your suspicions | JosspaTech',
    description: 'Handy Horology Helper for new or vintage watches and clocks. Floor or bench. Confirm your suspicions. Private horology app by JosspaTech (Joss-pah-tech).',
    canonical: 'https://josspatech.com/hhh/',
    ogTitle: 'Handy Horology Helper — Confirm your suspicions.',
    ogImage: 'https://josspatech.com/assets/brand/og-hhh.jpg'
  },
  pbj: {
    title: 'PocketBudJet — Private Budgeting | JosspaTech',
    description: 'PocketBudJet: import statements, plan spending, and coach yourself privately on your device. 15-day Premium trial. Ad-free. By JosspaTech (Joss-pah-tech).',
    canonical: 'https://josspatech.com/pbj/',
    ogTitle: 'PocketBudJet — Import. Plan. Coach.',
    ogImage: 'https://josspatech.com/assets/brand/og-pbj.jpg'
  },
  cvc: {
    title: 'Curator\\'s Vault: Classics — Collectibles Catalog | JosspaTech',
    description: 'Curator\\'s Vault: Classics — photograph, organize, and value coins, cards, stamps, paper money, and lighters. Private collectibles catalog by JosspaTech (Joss-pah-tech).',
    canonical: 'https://josspatech.com/cvc/',
    ogTitle: 'Curator\\'s Vault: Classics — Your vault. Your rules.',
    ogImage: 'https://josspatech.com/assets/brand/og-cvc.jpg'
  },
  pal: {
    title: 'Pocket Allowance Ledger — Coming soon | JosspaTech',
    description: 'Pocket Allowance Ledger helps families coach homework, chores, and habits with gold tokens — parents stay in charge. By JosspaTech (Joss-pah-tech).',
    canonical: 'https://josspatech.com/',
    ogTitle: 'Pocket Allowance Ledger — Coming soon',
    ogImage: 'https://josspatech.com/assets/brand/og-josspatech.jpg'
  }
};"""

if old_page_seo not in text:
    # softer replace of og images in PAGE_SEO
    text = text.replace(
        "ogImage: 'https://josspatech.com/assets/brand/og-josspatech.png'",
        "ogImage: 'https://josspatech.com/assets/brand/og-josspatech.jpg'",
    )
    text = text.replace(
        "ogImage: 'https://josspatech.com/assets/screenshots/app-hhh-hero.png'",
        "ogImage: 'https://josspatech.com/assets/brand/og-hhh.jpg'",
    )
    text = text.replace(
        "ogImage: 'https://josspatech.com/assets/screenshots/app-pbj-hero.png'",
        "ogImage: 'https://josspatech.com/assets/brand/og-pbj.jpg'",
    )
    text = text.replace(
        "ogImage: 'https://josspatech.com/assets/screenshots/app-cvc-hero.png'",
        "ogImage: 'https://josspatech.com/assets/brand/og-cvc.jpg'",
    )
    if "pal: {" not in text and "var PAGE_SEO" in text:
        text = text.replace(
            "  cvc: {\n    title: 'Curator\\'s Vault: Classics — Collectibles Catalog | JosspaTech',",
            "  pal: {\n    title: 'Pocket Allowance Ledger — Coming soon | JosspaTech',\n    description: 'Pocket Allowance Ledger helps families coach homework, chores, and habits with gold tokens — parents stay in charge. By JosspaTech (Joss-pah-tech).',\n    canonical: 'https://josspatech.com/',\n    ogTitle: 'Pocket Allowance Ledger — Coming soon',\n    ogImage: 'https://josspatech.com/assets/brand/og-josspatech.jpg'\n  },\n  cvc: {\n    title: 'Curator\\'s Vault: Classics — Collectibles Catalog | JosspaTech',",
        )
    print("PAGE_SEO soft-patched")
else:
    text = text.replace(old_page_seo, new_page_seo)
    print("PAGE_SEO replaced")

path.write_text(text, encoding="utf-8")
print("wrote", path)
# sanity
assert "<!-- SEO & Social Meta Tags -->" in text
pos_seo = text.find("<!-- SEO & Social Meta Tags -->")
pos_style = text.find("<style>")
print("seo before first style?", pos_seo < pos_style, pos_seo, pos_style)
print("display=swap", "display=swap" in text)
print("og jpg", text.count("og-josspatech.jpg"))
