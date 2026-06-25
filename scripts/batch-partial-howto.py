#!/usr/bin/env python3
"""Batch PARTIAL/OVERVIEW improvements for pocketbudjet how-to pages."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "videos" / "pocketbudjet"
SKIP = {"budget-setup"}

OLD_SUB = "Real screens, gold pulse on where to tap, step-by-step narration."

# topic -> (classification, section_sub, list of img src per slide in order)
# If img list shorter than slides, last PNG is reused for remaining slides that had .png
# SVG slides keep SVG unless listed

TOPIC_CONFIG = {
    "adding-transactions": (
        "PARTIAL",
        "Home, transaction form, and dashboard use real PNGs with measured taps; split/rules steps reuse one form screenshot until per-step captures ship (PARTIAL).",
        None,
    ),
    "connect-bank": (
        "OVERVIEW",
        "Step-by-step narration with measured taps. All steps reuse one bank-sync screenshot until dedicated Maestro captures ship — still OVERVIEW, not TRUE HOW-TO.",
        None,
    ),
    "ai-coach": (
        "PARTIAL",
        "Coach dashboard uses Play-store PNGs with measured taps; later steps reuse the same screenshot until dedicated coach captures ship (PARTIAL).",
        [
            "/assets/screenshots/pbj/05-ai-coach.png",
            "/assets/screenshots/pbj/05-ai-coach.png",
            "/assets/screenshots/pbj/05-ai-coach.png",
            "/assets/screenshots/pbj/05-ai-coach.png",
            "/assets/screenshots/pbj/05-ai-coach.png",
            "/assets/screenshots/privacy.png",
        ],
    ),
    "share-statements": (
        "PARTIAL",
        "Bank/share-sheet steps use designed illustrations; PocketBudJet steps use real PNGs with measured taps where screenshots exist (PARTIAL).",
        None,
    ),
    "debt-freedom": (
        "PARTIAL",
        "Debt planner and What-If screens use real PNGs with measured taps; intro steps reuse debt artwork until full capture sequence ships (PARTIAL).",
        [
            "/assets/screenshots/debt.png",
            "/assets/screenshots/debt.png",
            "/assets/screenshots/debt.png",
            "/assets/screenshots/debt.png",
            "/assets/screenshots/debt-freedom/what-if.png",
            "/assets/screenshots/pbj/05-ai-coach.png",
        ],
    ),
    "reports": (
        "PARTIAL",
        "Reports hub uses a real PNG with measured taps; detail views reuse it and coach PNG until per-report captures ship (PARTIAL).",
        [
            "/assets/screenshots/reports/reports.png",
            "/assets/screenshots/reports/reports.png",
            "/assets/screenshots/reports/reports.png",
            "/assets/screenshots/reports/reports.png",
            "/assets/screenshots/debt.png",
            "/assets/screenshots/pbj/05-ai-coach.png",
        ],
    ),
    "receipt-scanning": (
        "PARTIAL",
        "Receipt scan screen uses a real PNG with measured taps; setup and batch steps reuse it until dedicated captures ship (PARTIAL).",
        [
            "/assets/screenshots/receipt-scanning/receipt-scan.png",
            "/assets/screenshots/receipt-scanning/receipt-scan.png",
            "/assets/screenshots/receipt-scanning/receipt-scan.png",
            "/assets/screenshots/budget-setup/step-6-scan.png",
            "/assets/screenshots/receipt-scanning/receipt-scan.png",
            "/assets/screenshots/budget-setup/step-7-dashboard.png",
        ],
    ),
    "household-sync": (
        "PARTIAL",
        "Household sync screen uses a real PNG with measured taps; pairing and conflict steps reuse it until dedicated captures ship (PARTIAL).",
        [
            "/assets/screenshots/household-sync/household-sync.png",
            "/assets/screenshots/household-sync/household-sync.png",
            "/assets/screenshots/household-sync/household-sync.png",
            "/assets/screenshots/household-sync/household-sync.png",
            "/assets/screenshots/household-sync/household-sync.png",
            "/assets/screenshots/household-sync/household-sync.png",
        ],
    ),
    "net-worth": (
        "PARTIAL",
        "Net worth dashboard uses a real PNG with measured taps; asset-class steps reuse it until dedicated captures ship (PARTIAL).",
        [
            "/assets/screenshots/net-worth/net-worth.png",
            "/assets/screenshots/net-worth/net-worth.png",
            "/assets/screenshots/net-worth/net-worth.png",
            "/assets/screenshots/net-worth/net-worth.png",
            "/assets/screenshots/net-worth/net-worth.png",
            "/assets/screenshots/net-worth/net-worth.png",
        ],
    ),
    "bills-recurring": (
        "PARTIAL",
        "Bills calendar uses a real PNG with measured taps; add-bill and forecast steps reuse it until dedicated captures ship (PARTIAL).",
        [
            "/assets/screenshots/bills-recurring/bills-calendar.png",
            "/assets/screenshots/bills.png",
            "/assets/screenshots/bills-recurring/bills-calendar.png",
            "/assets/screenshots/bills-recurring/bills-calendar.png",
            "/assets/screenshots/bills-recurring/bills-calendar.png",
            "/assets/screenshots/bills.png",
            "/assets/screenshots/transactions.png",
            "/assets/screenshots/bills-recurring/bills-calendar.png",
        ],
    ),
    "privacy-pitch": (
        "OVERVIEW",
        "Marketing walkthrough mixing privacy and import PNGs with illustrations — OVERVIEW, not TRUE HOW-TO.",
        [
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/pbj/02-import-center.png",
            "/assets/screenshots/budget-setup/step-7-dashboard.png",
            "/assets/screenshots/privacy.png",
        ],
    ),
    "app-overview": (
        "OVERVIEW",
        "Marketing walkthrough using Play-store PNGs across core features — OVERVIEW, not TRUE HOW-TO.",
        [
            "/assets/screenshots/pbj/01-home-dashboard.png",
            "/assets/screenshots/transactions.png",
            "/assets/screenshots/pbj/02-import-center.png",
            "/assets/screenshots/debt.png",
            "/assets/screenshots/pbj/05-ai-coach.png",
            "/assets/screenshots/pbj/06-goals-languages.png",
            "/assets/screenshots/pbj/07-web-companion.png",
        ],
    ),
    "why-it-is-different": (
        "OVERVIEW",
        "Marketing comparison walkthrough reusing app PNGs and illustrations — OVERVIEW, not TRUE HOW-TO.",
        [
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/pbj/02-import-center.png",
            "/assets/screenshots/pbj/01-home-dashboard.png",
            "/assets/screenshots/pbj/03-budget-envelopes.png",
            "/assets/screenshots/pbj/04-shopping-intelligence.png",
        ],
    ),
    "voice-shortcuts": (
        "PARTIAL",
        "Voice flows reuse coach and transaction PNGs; no dedicated voice UI captures yet (PARTIAL).",
        [
            "/assets/screenshots/pbj/05-ai-coach.png",
            "/assets/screenshots/transactions.png",
            "/assets/screenshots/pbj/05-ai-coach.png",
            "/assets/screenshots/pbj/05-ai-coach.png",
            "/assets/screenshots/pbj/01-home-dashboard.png",
        ],
    ),
    "transaction-rules": (
        "PARTIAL",
        "Rules walkthrough reuses the transaction form PNG with measured taps until dedicated rules captures ship (PARTIAL).",
        ["/assets/screenshots/transactions.png"] * 8,
    ),
    "search": (
        "PARTIAL",
        "Search walkthrough reuses home dashboard PNG with measured taps until dedicated search captures ship (PARTIAL).",
        ["/assets/screenshots/pbj/01-home-dashboard.png"] * 8,
    ),
    "savings-goals": (
        "PARTIAL",
        "Goals walkthrough reuses Play-store goals PNG with measured taps until dedicated captures ship (PARTIAL).",
        ["/assets/screenshots/pbj/06-goals-languages.png"] * 8,
    ),
    "retirement-planning": (
        "PARTIAL",
        "Retirement walkthrough reuses goals and debt PNGs until dedicated retirement captures ship (PARTIAL).",
        [
            "/assets/screenshots/pbj/06-goals-languages.png",
            "/assets/screenshots/pbj/06-goals-languages.png",
            "/assets/screenshots/pbj/06-goals-languages.png",
            "/assets/screenshots/pbj/06-goals-languages.png",
            "/assets/screenshots/debt.png",
            "/assets/screenshots/debt.png",
            "/assets/screenshots/debt-freedom/what-if.png",
            "/assets/screenshots/pbj/06-goals-languages.png",
        ],
    ),
    "privacy-security": (
        "PARTIAL",
        "Security walkthrough reuses privacy settings PNG with measured taps until dedicated lock-screen captures ship (PARTIAL).",
        ["/assets/screenshots/privacy.png"] * 6,
    ),
    "pc-dashboard": (
        "PARTIAL",
        "PC companion walkthrough reuses web companion PNG with measured taps until desktop captures ship (PARTIAL).",
        [
            "/assets/screenshots/pbj/07-web-companion.png",
            "/assets/screenshots/household-sync/household-sync.png",
            "/assets/screenshots/pbj/07-web-companion.png",
            "/assets/screenshots/pbj/03-budget-envelopes.png",
            "/assets/screenshots/pbj/02-import-center.png",
            "/assets/screenshots/pbj/07-web-companion.png",
        ],
    ),
    "mindful-features": (
        "PARTIAL",
        "Mindful spending walkthrough reuses goals and coach PNGs until dedicated captures ship (PARTIAL).",
        [
            "/assets/screenshots/pbj/06-goals-languages.png",
            "/assets/screenshots/pbj/06-goals-languages.png",
            "/assets/screenshots/pbj/05-ai-coach.png",
            "/assets/screenshots/pbj/06-goals-languages.png",
            "/assets/screenshots/pbj/05-ai-coach.png",
            "/assets/screenshots/pbj/06-goals-languages.png",
            "/assets/screenshots/pbj/01-home-dashboard.png",
            "/assets/screenshots/pbj/06-goals-languages.png",
        ],
    ),
    "export-sharing": (
        "PARTIAL",
        "Export walkthrough reuses privacy and import PNGs with measured taps until dedicated export captures ship (PARTIAL).",
        [
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/pbj/02-import-center.png",
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/pbj/02-import-center.png",
            "/assets/screenshots/privacy.png",
        ],
    ),
    "digital-receipt-import": (
        "PARTIAL",
        "Digital receipt import reuses scanner and import-center PNGs with measured taps (PARTIAL).",
        [
            "/assets/screenshots/scanner.png",
            "/assets/screenshots/receipt-scanning/receipt-scan.png",
            "/assets/screenshots/pbj/02-import-center.png",
            "/assets/screenshots/pbj/02-import-center.png",
            "/assets/screenshots/budget-setup/step-7-dashboard.png",
        ],
    ),
    "data-management": (
        "PARTIAL",
        "Data management reuses privacy and import PNGs with measured taps until dedicated captures ship (PARTIAL).",
        [
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/pbj/02-import-center.png",
            "/assets/screenshots/import.png",
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/budget-setup/step-7-dashboard.png",
        ],
    ),
    "cloud-backup-setup": (
        "PARTIAL",
        "Cloud backup walkthrough reuses privacy PNG with measured taps until dedicated backup captures ship (PARTIAL).",
        [
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/privacy.png",
            "/assets/screenshots/budget-setup/step-5-accounts.png",
        ],
    ),
    "calendar-view": (
        "PARTIAL",
        "Calendar walkthrough reuses bills calendar PNG with measured taps until dedicated captures ship (PARTIAL).",
        ["/assets/screenshots/bills-recurring/bills-calendar.png"] * 8,
    ),
}

# Default tap coords for PNG slides by hint keywords in data-tap-label or slide title
DEFAULT_TAPS = {
    "Gold +": (50, 90),
    "Home": (12, 94),
    "Settings": (90, 8),
    "Plan tab": (38, 94),
    "Progress": (75, 94),
    "Amount": (50, 22),
    "Category": (50, 42),
    "Account": (50, 52),
    "Split": (72, 58),
    "Scan": (50, 88),
    "Import": (50, 55),
    "Share": (88, 33),
    "QR code": (50, 48),
    "Household": (50, 55),
    "Coach": (50, 38),
    "Cloud": (50, 38),
    "Calendar": (50, 45),
    "Search": (82, 9),
    "Confirm": (50, 91),
    "Export": (50, 55),
    "Filter": (50, 35),
}


def is_png_src(src: str) -> bool:
    return src.lower().endswith(".png")


def strip_tap_attrs(slide_html: str) -> str:
    return re.sub(
        r'\s*data-tap-(?:x|y|label|hint)="[^"]*"',
        "",
        slide_html,
    )


def slide_has_png(slide_html: str) -> bool:
    m = re.search(r'<img\s+src="([^"]+)"', slide_html)
    return bool(m and is_png_src(m.group(1)))


def ensure_tap_on_png(slide_html: str) -> str:
    if not slide_has_png(slide_html):
        return strip_tap_attrs(slide_html)
    if 'data-tap-x="' in slide_html:
        return slide_html
    label_m = re.search(r'data-tap-label="([^"]*)"', slide_html)
    label = label_m.group(1) if label_m else ""
    for key, (x, y) in DEFAULT_TAPS.items():
        if key.lower() in label.lower():
            insert = f' data-tap-x="{x}" data-tap-y="{y}"'
            if label and 'data-tap-label="' not in slide_html:
                insert += f' data-tap-label="{label}"'
            return re.sub(r'(<div class="slide[^"]*")', r"\1" + insert, slide_html, count=1)
    return re.sub(
        r'(<div class="slide[^"]*")',
        r'\1 data-tap-x="50" data-tap-y="45" data-tap-label="Here"',
        slide_html,
        count=1,
    )


def update_section_sub(html: str, new_sub: str) -> str:
    if OLD_SUB in html:
        html = html.replace(OLD_SUB, new_sub)
    elif '<p class="section-sub">' in html:
        html = re.sub(
            r'<p class="section-sub">[^<]*</p>',
            f"<p class=\"section-sub\">{new_sub}</p>",
            html,
            count=1,
        )
    return html


def update_first_slide_step(html: str, classification: str) -> str:
    badge = "OVERVIEW" if classification == "OVERVIEW" else "PARTIAL"
    return re.sub(
        r'(<span class="slide-step">)(STEP 1|OVERVIEW|PARTIAL)(</span>)',
        rf"\1{badge}\3",
        html,
        count=1,
    )


def apply_img_replacements(html: str, imgs: list[str]) -> str:
    slides = list(re.finditer(r'(<div class="slide[^>]*>)(.*?)(</div>\s*(?=<div class="slide|<div class="progress-dots|</div>\s*</div>\s*<div class="progress-dots))', html, re.DOTALL))
    if not slides:
        return html
    parts = []
    last_end = 0
    for i, m in enumerate(slides):
        slide_open, body, slide_close = m.group(1), m.group(2), m.group(3)
        src = imgs[min(i, len(imgs) - 1)]
        body = re.sub(r'(<img\s+src=")[^"]+(")', rf"\1{src}\2", body, count=1)
        full = slide_open + body + slide_close
        full = strip_tap_attrs(full) if not is_png_src(src) else ensure_tap_on_png(full)
        parts.append(html[last_end : m.start()])
        parts.append(full)
        last_end = m.end()
    parts.append(html[last_end:])
    return "".join(parts)


def process_file(path: Path, classification: str, section_sub: str, imgs: list[str] | None) -> bool:
    html = path.read_text(encoding="utf-8")
    original = html
    html = update_section_sub(html, section_sub)
    html = update_first_slide_step(html, classification)
    if imgs:
        html = apply_img_replacements(html, imgs)
    else:
        # Still strip taps from non-PNG slides
        def fix_slide(m):
            full = m.group(0)
            return strip_tap_attrs(full) if not slide_has_png(full) else ensure_tap_on_png(full)

        html = re.sub(
            r'<div class="slide[^>]*>.*?</div>\s*(?=<div class="slide|<div class="progress-dots|</div>\s*</div>\s*<div class="progress-dots)',
            fix_slide,
            html,
            flags=re.DOTALL,
        )
    if html != original:
        path.write_text(html, encoding="utf-8")
        return True
    return False


def main():
    changed = []
    for topic_dir in sorted(ROOT.iterdir()):
        if not topic_dir.is_dir() or topic_dir.name in SKIP:
            continue
        index = topic_dir / "index.html"
        if not index.exists():
            continue
        cfg = TOPIC_CONFIG.get(topic_dir.name)
        if not cfg:
            print(f"SKIP no config: {topic_dir.name}")
            continue
        classification, section_sub, imgs = cfg
        if process_file(index, classification, section_sub, imgs):
            changed.append(topic_dir.name)
            print(f"UPDATED {topic_dir.name}")
        else:
            print(f"UNCHANGED {topic_dir.name}")
    print(f"\nTotal changed: {len(changed)}")
    print(", ".join(changed))


if __name__ == "__main__":
    main()
