#!/usr/bin/env python3
"""Batch-enhance PocketBudJet video slideshows for tech-support walkthroughs."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIDEOS = ROOT / "videos"

SECTION_SUB = "Real screens, gold pulse on where to tap, step-by-step narration."

# (regex on slide title + narration, tap-x, tap-y, label, hint HTML)
TAP_RULES: list[tuple[str, str, str, str, str]] = [
    (r"settings|gear|toolbox", "88", "7", "Settings", "Tap the <strong>gear icon</strong> (top right) to open Settings."),
    (r"gold \+|\+ button|tap the \+", "50", "90", "Gold +", "Tap the <strong>gold + button</strong> at the bottom center."),
    (r"plan tab|setup wizard|first budget", "38", "94", "Plan tab", "Tap the <strong>Plan</strong> tab (calendar icon) in the bottom navigation."),
    (r"home tab|dashboard", "12", "94", "Home", "Tap the <strong>Home</strong> tab (house icon) at the bottom left."),
    (r"transactions tab|transactions screen", "50", "94", "Transactions", "Tap the <strong>Transactions</strong> tab in the bottom navigation."),
    (r"progress tab|debt", "75", "94", "Progress", "Tap the <strong>Progress</strong> tab, then open <strong>Debt</strong>."),
    (r"import receipt|import center|import screen", "50", "88", "Import", "Tap <strong>Import receipts</strong> from the + menu or Import Center."),
    (r"share icon|share sheet|share to", "88", "33", "Share", "Tap the <strong>Share</strong> icon (square with arrow up)."),
    (r"pocketbudjet icon|pick pocket", "53", "68", "PocketBudJet", "Tap the <strong>PocketBudJet</strong> icon on the share sheet."),
    (r"confirm", "50", "91", "Confirm", "Review the list, then tap <strong>Confirm</strong> at the bottom."),
    (r"export", "50", "55", "Export", "In Settings, tap <strong>Import &amp; Export</strong>, then <strong>Export</strong>."),
    (r"scan receipt|camera|receipt", "50", "88", "Scan", "Tap <strong>Scan Receipt</strong> from the + menu."),
    (r"search", "82", "9", "Search", "Tap the <strong>search icon</strong> at the top of Transactions."),
    (r"qr|pair", "50", "48", "QR code", "Scan the <strong>QR code</strong> shown on the other device."),
    (r"financial coach|ai coach|coach", "50", "50", "Coach", "Open <strong>Settings</strong> &rarr; <strong>Financial Coach</strong>."),
    (r"household", "50", "55", "Household", "Open <strong>Settings</strong> &rarr; <strong>Household Sync</strong>."),
    (r"storage|backup|cloud tab", "50", "38", "Cloud", "Open <strong>Settings</strong> &rarr; <strong>Storage &amp; Backup</strong> &rarr; <strong>Cloud</strong> tab."),
    (r"category", "50", "42", "Category", "Tap the <strong>Category</strong> field and pick a budget category."),
    (r"account", "50", "52", "Account", "Tap <strong>Account</strong> and choose checking, savings, or card."),
    (r"amount", "50", "22", "Amount", "Tap <strong>Amount</strong> first and enter what you paid."),
    (r"split", "72", "58", "Split", "Tap <strong>Split</strong> to divide across categories."),
    (r"rule", "78", "12", "Rules", "Open the transaction menu, then <strong>Transaction Rules</strong>."),
    (r"bill calendar|calendar", "50", "45", "Calendar", "Open the <strong>Bill Calendar</strong> from Plan or Bills."),
    (r"save", "85", "12", "Save", "Tap <strong>Save</strong> (top right) when the form looks right."),
    (r"filter", "50", "35", "Filter", "Tap <strong>Filter</strong> to narrow results."),
    (r"date range", "50", "28", "Dates", "Set the <strong>start and end dates</strong> for your export."),
    (r"download arrow", "87", "74", "Download", "Tap the <strong>download arrow</strong> on the attachment."),
    (r"pc dashboard|browser", "50", "40", "URL", "Open the dashboard <strong>URL</strong> shown in Settings &rarr; PC Dashboard."),
]

SKIP_TAP = re.compile(
    r"\b(done|intro|overview|finished|summary|result|ready|problem|freedom date|private by|why |watch|everything in)\b",
    re.I,
)


def slide_block_re(index: str) -> re.Pattern:
    return re.compile(
        rf'(<div class="slide[^"]*" data-index="{index}"[^>]*)>',
        re.I,
    )


def get_slide_title(block: str) -> str:
    m = re.search(r'class="slide-title"[^>]*>([^<]+)', block, re.I)
    return m.group(1) if m else ""


def get_narration_hint(index: str, html: str) -> str:
    m = re.search(
        rf'<div class="narration-card" data-index="{index}"[^>]*>.*?<p>(.*?)</p>',
        html,
        re.S | re.I,
    )
    if not m:
        return ""
    text = re.sub(r"\s+", " ", m.group(1)).strip()
    # Prefer sentence that mentions tap/open/go
    for sent in re.split(r"(?<=[.!?])\s+", text):
        if re.search(r"\b(tap|open|choose|select|scroll|scan|enter|go to)\b", sent, re.I):
            clean = sent.replace("—", "&mdash;").replace("'", "&rsquo;")
            return clean
    return text[:220].replace("—", "&mdash;")


def match_rule(title: str, narr: str) -> tuple[str, str, str, str] | None:
    blob = f"{title} {narr}".lower()
    if SKIP_TAP.search(title) and "tap" not in blob:
        return None
    for pattern, x, y, label, hint in TAP_RULES:
        if re.search(pattern, blob, re.I):
            return x, y, label, hint
    if re.search(r"\b(tap|open|select|choose)\b", narr, re.I):
        return "50", "45", "Here", get_narration_hint("", "") or narr[:180]
    return None


def upsert_attr(open_tag: str, name: str, value: str) -> str:
    if re.search(rf'\b{name}="', open_tag):
        return re.sub(rf'{name}="[^"]*"', f'{name}="{value}"', open_tag)
    return open_tag[:-1] + f' {name}="{value}">'


def clean_orphan_taps(html: str) -> str:
    return re.sub(
        r"<img([^>]*)>\s*<div class=\"tap-ring-outer\"></div>\s*<span class=\"tap-finger\">[^<]*</span>\s*</div>",
        r"<img\1>\n",
        html,
    )


def enhance_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    if "slideshow" not in html:
        return False

    original = html
    html = clean_orphan_taps(html)

    if 'class="section-sub"' in html:
        html = re.sub(
            r'<p class="section-sub">[^<]*</p>',
            f'<p class="section-sub">{SECTION_SUB}</p>',
            html,
            count=1,
        )

    for m in re.finditer(
        r'<div class="slide([^"]*)" data-index="(\d+)"([^>]*)>',
        html,
    ):
        full_open = m.group(0)
        index = m.group(2)
        attrs = m.group(3)

        # Grab title from following content until next slide
        start = m.end()
        chunk = html[start : start + 1200]
        title = get_slide_title(chunk)
        narr = get_narration_hint(index, html)

        new_open = full_open
        if 'data-tap-hint="' not in new_open:
            hint = narr
            rule = match_rule(title, narr)
            if rule:
                x, y, label, rule_hint = rule
                if "data-tap-x=" not in new_open:
                    new_open = upsert_attr(new_open, "data-tap-x", x)
                    new_open = upsert_attr(new_open, "data-tap-y", y)
                if "data-tap-label=" not in new_open:
                    new_open = upsert_attr(new_open, "data-tap-label", label)
                hint = rule_hint if rule_hint else hint
            if hint and not SKIP_TAP.search(title):
                esc = hint.replace('"', "&quot;")
                new_open = upsert_attr(new_open, "data-tap-hint", esc)

        if new_open != full_open:
            html = html.replace(full_open, new_open, 1)

    if html != original:
        path.write_text(html, encoding="utf-8", newline="\n")
        return True
    return False


def main() -> None:
    changed = 0
    for path in sorted(VIDEOS.rglob("index.html")):
        if enhance_file(path):
            changed += 1
            print(path.relative_to(ROOT))
    print(f"Enhanced {changed} files")


if __name__ == "__main__":
    main()
