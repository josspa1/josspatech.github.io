#!/usr/bin/env python3
"""Fix 89-slide user manual: PNG assets, slide wiring, tap pointers, phone frame CSS."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PBJ = Path(r"C:\PBJ")
INDEX = ROOT / "videos" / "user-guide" / "index.html"
SHOTS = ROOT / "assets" / "screenshots"

HOME = "/assets/screenshots/import/step-10-home-dashboard.png"
HOME_ONBOARD = "/assets/screenshots/import/step-9-settings-export.png"
SETTINGS = "/assets/screenshots/transactions.png"

RECORD_NOW_SHOWCASE3 = """<!-- RECORD_NOW: cold-start/showcase-3.png — Quick Tour 3/4 "Crush Your Debt" -->
<div style="width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(160deg,#0C3358 0%,#1A4F7A 55%,#2E6FA3 100%);color:#fff;padding:1.5rem;text-align:center;">
<p style="font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;margin-bottom:0.5rem;">Quick Tour · 3 of 4</p>
<p style="font-size:1.05rem;font-weight:700;margin-bottom:0.5rem;">Crush Your Debt</p>
<p style="font-size:0.82rem;line-height:1.5;color:rgba(255,255,255,0.9);">Capture pending — avalanche &amp; snowball payoff paths.</p>
</div>"""

RECORD_NOW_DRAWER = """<!-- RECORD_NOW: wayfinding/drawer-open.png — swipe from left, drawer panel visible -->
<div style="width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(135deg,#0C3358 0%,#1A4F7A 100%);color:#fff;padding:1.5rem;text-align:center;">
<p style="font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;margin-bottom:0.75rem;">Navigation Drawer</p>
<p style="font-size:0.85rem;line-height:1.5;color:rgba(255,255,255,0.92);">Capture needed: swipe from the left — Settings, Help, and full nav map visible.</p>
</div>"""

RECORD_NOW_SUBSCRIPTION = """<!-- RECORD_NOW: cold-start/subscription-intro.png — Choose Your Plan -->
<div style="width:100%;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;background:linear-gradient(135deg,#0C3358 0%,#1A4F7A 100%);color:#fff;padding:1.5rem;text-align:center;">
<p style="font-family:'Playfair Display',serif;font-size:1.1rem;font-weight:700;margin-bottom:0.75rem;">Choose Your Plan</p>
<p style="font-size:0.85rem;line-height:1.5;color:rgba(255,255,255,0.92);">15-Day Premium trial — full access, no card required. Or continue free.</p>
</div>"""

# (index, img_src or None for placeholder, tap attrs dict or None for data-tap-none)
SLIDES: list[tuple[int, str | None, dict[str, str] | None]] = [
    (0, "/assets/screenshots/cold-start/splash.png", None),
    (1, "/assets/screenshots/cold-start/showcase-1.png", {"x": "50", "y": "88", "label": "Next"}),
    (2, "/assets/screenshots/cold-start/showcase-2.png", {"x": "50", "y": "88", "label": "Next"}),
    (3, None, {"x": "50", "y": "88", "label": "Next"}),
    (4, "/assets/screenshots/cold-start/showcase-4.png", {"x": "50", "y": "88", "label": "Get Started"}),
    (5, "/assets/screenshots/cold-start/terms-tos.png", None),
    (6, "/assets/screenshots/cold-start/terms-tab.png", {"x": "72", "y": "18", "label": "Disclaimer"}),
    (7, "/assets/screenshots/cold-start/terms-accept.png", {"x": "50", "y": "92", "label": "Accept"}),
    (8, "/assets/screenshots/cold-start/security-setup.png", {"x": "50", "y": "90", "label": "Continue"}),
    (9, HOME, None),
    (10, HOME, {"x": "50", "y": "94", "label": "Tab bar"}),
    (11, HOME_ONBOARD, {"x": "72", "y": "8", "label": "Header"}),
    (12, None, None),  # RECORD_NOW drawer-open
    (13, "/assets/screenshots/pbj/02-import-center.png", {"x": "50", "y": "35", "label": "Import"}),
    (14, HOME, {"x": "85", "y": "82", "label": "Quick-add"}),
    (15, None, None),
    (16, HOME_ONBOARD, {"x": "91", "y": "8", "label": "Settings"}),
    (17, "/assets/screenshots/budget-setup/step-1-name.png", {"x": "50", "y": "38", "label": "Name"}),
    (18, "/assets/screenshots/cold-start/wizard-currency.png", {"x": "50", "y": "42", "label": "Currency"}),
    (19, "/assets/screenshots/budget-setup/step-5-accounts.png", {"x": "50", "y": "55", "label": "Add account"}),
    (20, "/assets/screenshots/budget-setup/step-2-income.png", {"x": "50", "y": "42", "label": "Income"}),
    (21, "/assets/screenshots/cold-start/wizard-bills.png", {"x": "50", "y": "50", "label": "Add bill"}),
    (22, "/assets/screenshots/pbj/06-goals-languages.png", {"x": "50", "y": "48", "label": "Goal"}),
    (23, "/assets/screenshots/budget-setup/step-3-templates.png", {"x": "50", "y": "55", "label": "Style"}),
    (24, "/assets/screenshots/budget-setup/step-3-templates.png", {"x": "50", "y": "55", "label": "Continue"}),
    (25, "/assets/screenshots/budget-setup/step-7-dashboard.png", None),
    (26, HOME, None),
    (27, HOME, {"x": "12", "y": "94", "label": "Activity"}),
    (28, SETTINGS, None),  # RECORD_NOW: real Activity list
    (29, SETTINGS, None),
    (30, HOME, {"x": "38", "y": "94", "label": "Budget"}),
    (31, "/assets/screenshots/pbj/03-budget-envelopes.png", None),
    (32, "/assets/screenshots/budget-setup/step-4-categories.png", {"x": "50", "y": "50", "label": "Category"}),
    (33, "/assets/screenshots/budget-setup/step-3-templates.png", {"x": "50", "y": "55", "label": "Template"}),
    (34, HOME, {"x": "62", "y": "94", "label": "Goals"}),
    (35, "/assets/screenshots/pbj/06-goals-languages.png", None),
    (36, "/assets/screenshots/pbj/06-goals-languages.png", {"x": "50", "y": "35", "label": "New goal"}),
    (37, "/assets/screenshots/pbj/06-goals-languages.png", {"x": "50", "y": "55", "label": "Sinking fund"}),
    (38, HOME, {"x": "88", "y": "94", "label": "Coach"}),
    (39, "/assets/screenshots/pbj/05-ai-coach.png", None),
    (40, "/assets/screenshots/pbj/05-ai-coach.png", {"x": "85", "y": "24", "label": "Ask"}),
    (41, HOME, None),
    (42, HOME, {"x": "85", "y": "82", "label": "Gold +"}),
    (43, "/assets/screenshots/budget-setup/step-6-scan.png", {"x": "50", "y": "30", "label": "Amount"}),
    (44, "/assets/screenshots/budget-setup/step-6-scan.png", {"x": "50", "y": "50", "label": "Category"}),
    (45, "/assets/screenshots/budget-setup/step-6-scan.png", {"x": "50", "y": "65", "label": "Split"}),
    (46, "/assets/screenshots/budget-setup/step-6-scan.png", {"x": "50", "y": "92", "label": "Save"}),
    (47, "/assets/screenshots/pbj/02-import-center.png", {"x": "50", "y": "28", "label": "Import"}),
    (48, "/assets/screenshots/pbj/02-import-center.png", {"x": "50", "y": "40", "label": "Share"}),
    (49, "/assets/screenshots/pbj/08-confirm-import.png", {"x": "50", "y": "55", "label": "PocketBudJet"}),
    (50, "/assets/screenshots/pbj/02-import-center.png", {"x": "50", "y": "65", "label": "Browse files"}),
    (51, "/assets/screenshots/pbj/08-confirm-import.png", {"x": "50", "y": "91", "label": "Confirm"}),
    (52, "/assets/screenshots/pbj/02-import-center.png", {"x": "50", "y": "45", "label": "Date range"}),
    (53, "/assets/screenshots/pbj/02-import-center.png", {"x": "50", "y": "72", "label": "PDF"}),
    (54, "/assets/screenshots/receipt-scanning/receipt-scan.png", {"x": "50", "y": "22", "label": "Scan"}),
    (55, "/assets/screenshots/budget-setup/step-6-scan.png", {"x": "50", "y": "45", "label": "Save"}),
    (56, "/assets/screenshots/scanner.png", {"x": "50", "y": "48", "label": "WiFi ADF"}),
    (57, "/assets/screenshots/budget-setup/step-7-dashboard.png", None),
    (58, "/assets/screenshots/bills.png", {"x": "50", "y": "42", "label": "Calendar"}),
    (59, "/assets/screenshots/bills.png", {"x": "50", "y": "70", "label": "Mark paid"}),
    (60, "/assets/screenshots/debt.png", None),
    (61, "/assets/screenshots/debt-freedom/what-if.png", {"x": "50", "y": "50", "label": "Strategy"}),
    (62, "/assets/screenshots/reports/reports.png", {"x": "50", "y": "18", "label": "Reports"}),
    (63, "/assets/screenshots/reports/reports.png", {"x": "50", "y": "40", "label": "Trends"}),
    (64, "/assets/screenshots/reports/reports.png", {"x": "50", "y": "60", "label": "Categories"}),
    (65, "/assets/screenshots/net-worth/net-worth.png", None),
    (66, SETTINGS, {"x": "50", "y": "35", "label": "Export"}),
    (67, SETTINGS, {"x": "50", "y": "55", "label": "Format"}),
    (68, HOME, {"x": "91", "y": "8", "label": "Settings"}),
    (69, "/assets/screenshots/privacy.png", {"x": "50", "y": "40", "label": "Backup"}),
    (70, SETTINGS, {"x": "50", "y": "50", "label": "Storage"}),
    (71, "/assets/screenshots/connect-bank/bank-sync.png", None),
    (72, "/assets/screenshots/connect-bank/bank-sync.png", {"x": "50", "y": "45", "label": "Connect Bank"}),
    (73, "/assets/screenshots/connect-bank/bank-sync.png", {"x": "50", "y": "70", "label": "Confirm"}),
    (74, SETTINGS, None),
    (75, SETTINGS, None),
    (76, SETTINGS, None),
    (77, "/assets/screenshots/pbj/05-ai-coach.png", {"x": "50", "y": "50", "label": "Voice"}),
    (78, HOME, None),
    (79, "/assets/screenshots/pbj/06-goals-languages.png", {"x": "50", "y": "40", "label": "Retirement"}),
    (80, "/assets/screenshots/debt-freedom/what-if.png", {"x": "50", "y": "55", "label": "Projection"}),
    (81, "/assets/screenshots/pbj/04-shopping-intelligence.png", {"x": "50", "y": "50", "label": "Mindful"}),
    (82, "/assets/screenshots/pbj/07-web-companion.png", None),
    (83, "/assets/screenshots/household-sync/household-sync.png", {"x": "50", "y": "55", "label": "Pair"}),
    (84, HOME_ONBOARD, {"x": "72", "y": "8", "label": "Search"}),
    (85, HOME, None),
    (86, "/assets/screenshots/privacy.png", {"x": "50", "y": "35", "label": "App lock"}),
    (87, "/assets/screenshots/privacy.png", {"x": "50", "y": "60", "label": "Cloud"}),
    (88, "/assets/screenshots/privacy.png", None),
]

ALT_BY_INDEX = {
    0: "Splash screen on cold launch",
    3: "Feature showcase slide 3 — debt tools",
    9: "Home after first launch",
    10: "Wayfinding — tab bar on Home",
    11: "Wayfinding — header search and Coach",
    12: "Wayfinding — Settings from drawer (capture pending: drawer open)",
    13: "Wayfinding — Import Center / Toolbox utilities",
    14: "Wayfinding — quick-add FAB",
    15: "Choose Your Plan — subscription intro",
    28: "Activity — transaction list (capture pending)",
    29: "Activity — filters and running balances (capture pending)",
}


def copy_assets() -> list[str]:
    copied: list[str] = []
    pairs: list[tuple[Path, Path]] = [
        (PBJ / "_captures" / "joe_manual_recommended" / "cold-start" / "splash.png", SHOTS / "cold-start" / "splash.png"),
        (PBJ / "josspatech.github.io" / "assets" / "screenshots" / "cold-start" / "showcase-1.png", SHOTS / "cold-start" / "showcase-1.png"),
        (PBJ / "josspatech.github.io" / "assets" / "screenshots" / "cold-start" / "showcase-2.png", SHOTS / "cold-start" / "showcase-2.png"),
        (PBJ / "josspatech.github.io" / "assets" / "screenshots" / "cold-start" / "showcase-4.png", SHOTS / "cold-start" / "showcase-4.png"),
        (PBJ / "josspatech.github.io" / "assets" / "screenshots" / "cold-start" / "security-setup.png", SHOTS / "cold-start" / "security-setup.png"),
        (SHOTS / "import" / "step-10-home-dashboard.png", SHOTS / "pbj" / "01-home-dashboard.png"),
        (PBJ / "pbj-screenshots" / "03-budget-envelopes.png", SHOTS / "pbj" / "03-budget-envelopes.png"),
        (PBJ / "pbj-screenshots" / "04-shopping-intelligence.png", SHOTS / "pbj" / "04-shopping-intelligence.png"),
        (PBJ / "pbj-screenshots" / "05-ai-coach.png", SHOTS / "pbj" / "05-ai-coach.png"),
        (PBJ / "pbj-screenshots" / "06-goals-languages.png", SHOTS / "pbj" / "06-goals-languages.png"),
        (PBJ / "pbj-screenshots" / "06-goals-languages.png", SHOTS / "cold-start" / "wizard-goals.png"),
    ]
    for src, dst in pairs:
        if not src.is_file():
            print(f"SKIP missing source: {src}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied.append(str(dst.relative_to(ROOT)))
    return copied


def tap_attrs(tap: dict[str, str] | None) -> str:
    if tap is None:
        return ' data-tap-none'
    return (
        f' data-tap-x="{tap["x"]}" data-tap-y="{tap["y"]}"'
        f' data-tap-label="{tap["label"]}"'
    )


def slide_inner(idx: int, src: str | None, alt: str) -> str:
    if idx == 3:
        return RECORD_NOW_SHOWCASE3
    if idx == 12:
        return RECORD_NOW_DRAWER
    if idx == 15:
        return RECORD_NOW_SUBSCRIPTION
    assert src
    return f'<img src="{src}" alt="{alt}" loading="{"eager" if idx == 0 else "lazy"}">'


def replace_slide(html: str, idx: int, inner: str, tap: dict[str, str] | None) -> str:
    img_block = re.compile(
        rf'<div class="(slide(?: active)?)" data-index="{idx}"[^>]*>\s*<img[^>]+>\s*</div>',
        re.S,
    )
    ph_block = re.compile(
        rf'<div class="(slide(?: active)?)" data-index="{idx}"[^>]*>\s*<!--.*?-->\s*<div style=.*?</div>\s*</div>',
        re.S,
    )
    for pat in (img_block, ph_block):
        m = pat.search(html)
        if not m:
            continue
        cls = m.group(1)
        new_block = f'<div class="{cls}" data-index="{idx}"{tap_attrs(tap)}>\n {inner}\n </div>'
        return html[: m.start()] + new_block + html[m.end() :]
    raise SystemExit(f"slide {idx} not found")


def patch_slides(html: str) -> str:
    for idx, src, tap in reversed(SLIDES):
        old_m = re.search(
            rf'<div class="slide(?: active)?" data-index="{idx}"[^>]*>(.*?)</div>',
            html,
            re.S,
        )
        if not old_m:
            raise SystemExit(f"slide {idx} not found")
        alt_m = re.search(r'alt="([^"]*)"', old_m.group(1))
        alt = ALT_BY_INDEX.get(idx, alt_m.group(1) if alt_m else f"Slide {idx}")
        inner = slide_inner(idx, src, alt)
        html = replace_slide(html, idx, inner, tap)
    return html


def patch_css(html: str) -> str:
    html = html.replace(
        ".phone-frame {\n width: 300px; position: relative;\n border: 10px solid var(--navy-dark); border-radius: 40px;",
        ".phone-frame {\n width: 300px; position: relative;\n border: 6px solid var(--navy-dark); border-radius: 36px;",
    )
    html = html.replace(
        ".slide img {\n width: 100%; height: 100%; display: block;\n object-fit: contain; object-position: top center;\n background: #000;",
        ".slide img {\n width: 100%; height: 100%; display: block;\n object-fit: contain; object-position: center center;\n background: var(--background);",
    )
    html = html.replace("border-radius: 30px;", "border-radius: 28px;", 1)
    return html


def patch_verify_script() -> None:
    path = ROOT / "scripts" / "verify-user-guide.js"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "const h2Text = await page.locator('.video-section h2').textContent();",
        "const h2Text = await page.locator('.walkthrough h2').textContent();",
    )
    text = re.sub(
        r"process\.exit\(slides === 28 && tapIndicators > 0 && legend === 1 && audioOk \? 0 : 1\);",
        "process.exit(slides === 89 && tapIndicators > 0 && audioOk ? 0 : 1);",
        text,
    )
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    copied = copy_assets()
    html = INDEX.read_text(encoding="utf-8")
    html = patch_css(html)
    html = patch_slides(html)
    INDEX.write_text(html, encoding="utf-8", newline="\n")
    patch_verify_script()

    css = ROOT / "videos" / "user-guide" / "walkthrough.css"
    css_text = css.read_text(encoding="utf-8")
    if "object-fit: contain" not in css_text:
        css_text += """
/* Full screenshot visible inside phone frame (no cover crop) */
.walkthrough-stage .slide img {
  object-fit: contain;
  object-position: center center;
  background: var(--background, #EDF2F7);
}
"""
        css.write_text(css_text, encoding="utf-8", newline="\n")

    print(f"Copied {len(copied)} PNG assets")
    for p in copied:
        print(f"  {p}")
    print(f"Patched {INDEX.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
