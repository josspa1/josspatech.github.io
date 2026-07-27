#!/usr/bin/env python3
"""HHH user-guide tap QA: tighten coords, soften verb+none, keep data-taps."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "user-guide-hhh"
HTML = OUT / "index.html"
NARR = OUT / "narration-en.json"
BUST = "taps-qa-2026-07-27"

# Single-tap coord fixes (preserve show-at/duration).
COORD_FIXES: dict[int, tuple[int, int, str]] = {
    6: (80, 12, "Clear samples"),
    37: (30, 85, "Save to Museum"),
    96: (18, 35, "My Museum list"),
    97: (50, 66, "Share QR"),
}

# Softened narration — no Tap/Open/Press/Choose/Pick/Select/Swipe/Go to.
NARR_FIXES: dict[int, str] = {
    9: (
        "Getting started path cards jump straight to Hunt on eBay, troubleshoot a clock, "
        "start your museum, or identify a piece."
    ),
    18: (
        "Repairs and Service logs cleanings, repairs, and costs — each entry updates your cost basis."
    ),
    23: (
        "Manual entry lets you fill details yourself instead of running AI Identify."
    ),
    25: (
        "Save adds the piece to your Owned collection immediately."
    ),
    29: (
        "When prompted, add a movement photo for better accuracy — or skip Identify now to proceed with dial only."
    ),
    31: (
        "Wristwatch, Pocket Watch, or Clock corrects the type when auto-detect is wrong."
    ),
    32: (
        "Identify reads your photo and searches reference databases — wait while it works."
    ),
    33: (
        "On the results screen, tap the top match to review confidence. "
        "Other possibilities lists alternatives when you want to compare."
    ),
    34: (
        "If the top match looks right, keep it. If not, another possibility from the list below may fit better."
    ),
    45: (
        "A product row or Shop on Clockworks opens the item in your browser."
    ),
    52: (
        "Any match opens the eBay listing in your browser."
    ),
    59: (
        "Under Repairs and Service, Add entry takes date, vendor, and cost — service spend adds to your cost basis."
    ),
    60: (
        "From More, Insurance Report builds a PDF-ready summary of pieces, values, and photos for your insurer."
    ),
    78: (
        "Manage cancels or changes your subscription through Google Play or the App Store."
    ),
    84: (
        "Trade Analyzer models a trade — your piece plus cash versus theirs — Pro feature. "
        "Find it further down the Tools list."
    ),
    88: (
        "Scan Barcode points the camera at a UPC or QR on packaging or paperwork. "
        "Find it further down the Tools list."
    ),
    89: (
        "Scan Papers photographs receipts, certificates, or appraisal documents and attaches them to a piece. "
        "Find it further down the Tools list."
    ),
    90: (
        "How Complex Is It rates movement complexity from the complications you mark. "
        "Find it further down the Tools list."
    ),
    91: (
        "Is It Accurate logs time checks against a reference and tracks daily rate over weeks. "
        "Find it further down the Tools list."
    ),
    92: (
        "What to Wear — Rotation Planner — assigns pieces for the week so nothing sits unworn too long. "
        "Find it further down the Tools list."
    ),
    93: (
        "Warranties stores expiry dates — HHH reminds you before they lapse. "
        "Find it further down the Tools list."
    ),
    96: (
        "On Print and Export List, tap My Museum, Wish list, or For sale, then set columns and generate a PDF."
    ),
    97: (
        "Tap the Share Nearby QR to show the piece summary — PIN is above; Bluetooth is optional. Pro feature."
    ),
    109: (
        "Browse the Demand Rolodex board — pieces your contacts who shared wish lists want to buy, "
        "grouped by make and model. Tap a board group for contacts, specs, and notes — no prices on the card."
    ),
    110: (
        "Phone or email reaches the buyer. A private one-to-ten rating on that contact stays on your phone only."
    ),
}


def patch_slide_attrs(html: str, idx: int, x: int, y: int, label: str) -> str:
    pat = re.compile(
        rf'(<div class="slide[^"]*" data-index="{idx}")([^>]*)(>)',
    )

    def repl(m: re.Match[str]) -> str:
        attrs = m.group(2)
        if "data-taps=" in attrs or "data-tap-none" in attrs:
            return m.group(0)
        show = re.search(r'data-tap-show-at="([^"]+)"', attrs)
        dur = re.search(r'data-tap-duration="([^"]+)"', attrs)
        show_at = show.group(1) if show else "0.2"
        duration = dur.group(1) if dur else "3.0"
        new_attrs = (
            f' data-tap-x="{x}" data-tap-y="{y}" data-tap-label="{label}" '
            f'data-tap-show-at="{show_at}" data-tap-duration="{duration}"'
        )
        return f"{m.group(1)}{new_attrs}{m.group(3)}"

    html2, n = pat.subn(repl, html, count=1)
    if n != 1:
        raise SystemExit(f"slide {idx} attrs not patched ({n})")
    return html2


def main() -> None:
    narr = json.loads(NARR.read_text(encoding="utf-8"))
    changed_slides: list[int] = []
    for idx, text in NARR_FIXES.items():
        if narr[idx] != text:
            narr[idx] = text
            changed_slides.append(idx)
    NARR.write_text(json.dumps(narr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "_audio_regen_slides.json").write_text(
        json.dumps(sorted(set(changed_slides)), indent=2) + "\n",
        encoding="utf-8",
    )

    html = HTML.read_text(encoding="utf-8")
    for idx, (x, y, label) in COORD_FIXES.items():
        html = patch_slide_attrs(html, idx, x, y, label)

    # Cache-bust screenshot query params for touched slides' images (best-effort).
    html = re.sub(
        r'(/assets/screenshots/hhh/manual/[^"?]+\.png)\?v=[^"]+',
        rf"\1?v={BUST}",
        html,
    )
    html = re.sub(
        r'(/videos/shared/walkthrough\.js)(?:\?v=[^"]*)?"',
        rf'\1?v={BUST}"',
        html,
        count=1,
    )

    # Sync inline NARRATION array
    narr_js = "const NARRATION = " + json.dumps(narr, ensure_ascii=False) + ";"
    html2, c = re.subn(r"const NARRATION = \[[\s\S]*?\];", narr_js, html, count=1)
    if c != 1:
        raise SystemExit(f"NARRATION sync failed ({c})")

    HTML.write_text(html2, encoding="utf-8", newline="\n")
    print(f"narr changed: {changed_slides}")
    print(f"coord fixes: {sorted(COORD_FIXES)}")
    print(f"bust={BUST}")


if __name__ == "__main__":
    main()
