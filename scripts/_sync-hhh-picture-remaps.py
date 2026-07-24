#!/usr/bin/env python3
"""Sync EN index.html + shot-map to verified keepers (selective polish 2026-07-24b)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "user-guide-hhh"
HTML = OUT / "index.html"
MAP = OUT / "_shot-map.json"
MANUAL = ROOT / "assets" / "screenshots" / "hhh" / "manual"

# Slide index → (asset, optional alt)
REMAP: dict[int, tuple[str, str | None]] = {
    4: ("19-sample-loading.png", "Sample collection loading"),
    5: ("19-sample-home-banner.png", "Sample mode banner"),
    6: ("26-clear-ludwig-sample.png", None),
    32: ("07-identify-results.png", None),
    33: ("07-identify-results.png", None),
    34: ("07d-identify-insights.png", None),
    35: ("07c-identify-confidence.png", None),
    36: ("07b-identify-review.png", None),
    37: ("07-identify-results.png", None),
    39: ("25-offline-show-pack.png", None),
    63: ("09-web-companion.png", None),
    64: ("09-web-companion.png", None),
    65: ("09-web-companion.png", None),
    69: ("24-device-sync.png", None),
    70: ("10-settings.png", "Settings tab"),
    71: ("10c-settings-theme-detail.png", "Theme Light Dark System"),
    72: ("10d-settings-language.png", "Language picker"),
    73: ("10e-settings-security.png", "App lock Security"),
    74: ("10e-settings-security.png", "Database encryption status"),
    # 75 Notifications → eBay match notification (real behavior; narration updated separately)
    75: ("05b-ebay-match-notification.png", "eBay Grail Radar match notification"),
    76: ("12-trial-subscription.png", None),
    77: ("12-trial-subscription.png", None),
    78: ("12-trial-subscription.png", None),
    81: ("16-compare.png", None),
    83: ("15-finances-pl.png", None),
    94: ("17-atomic-clock.png", "Exact Time atomic clock"),
    95: ("18-moon-phase.png", "Moon Phase tool"),
    97: ("27b-share-nearby-active.png", "Share Nearby PIN and QR"),
    98: ("25-offline-show-pack.png", "Offline Show Pack"),
    # 99 LAN Report — remapped after capture (placeholder until file exists)
    103: ("21-demand-rolodex-send.png", None),
    104: ("21-demand-rolodex-send.png", None),
    105: ("21-demand-rolodex-send.png", None),
    106: ("21b-demand-pin-qr.png", "Send want list PIN and QR"),
    107: ("22-demand-rolodex-receive.png", None),
    108: ("22-demand-rolodex-receive.png", None),
    109: ("23-demand-rolodex-board.png", None),
    110: ("23-demand-rolodex-board.png", "Demand board contact rating"),
}

# Selective tool captures — applied when files exist
OPTIONAL_WHEN_PRESENT: dict[int, tuple[str, str]] = {
    54: ("28-ebay-listings.png", "eBay Listings tool"),
    84: ("29-trade-analyzer.png", "Trade Analyzer Pro"),
    85: ("30-ai-chat.png", "Ask the Expert AI Chat"),
    86: ("31-photo-coach.png", "Photo Coach Pro"),
    87: ("32-digital-id-card.png", "Digital ID Card Pro"),
    96: ("33-print-export.png", "Print and Export List"),
    99: ("34-lan-report.png", "LAN Report big screen"),
}

BASE = "/assets/screenshots/hhh/manual/"
VER = "picture-audit-2026-07-24b"


def strip_q(src: str) -> str:
    return src.split("?")[0]


def main() -> None:
    remap = dict(REMAP)
    for idx, (name, alt) in OPTIONAL_WHEN_PRESENT.items():
        if (MANUAL / name).exists():
            remap[idx] = (name, alt)

    html = HTML.read_text(encoding="utf-8")
    slides = json.loads(MAP.read_text(encoding="utf-8"))
    by_i = {s["i"]: s for s in slides}

    pattern = re.compile(
        r'(<div class="slide[^"]*" data-index="(\d+)"[^>]*>\s*<img src=")([^"]+)(" alt=")([^"]*)(")',
        re.M,
    )

    def repl(m: re.Match[str]) -> str:
        idx = int(m.group(2))
        entry = remap.get(idx)
        if not entry:
            src = strip_q(m.group(3))
            if "manual/" in src:
                src = f"{src}?v={VER}"
            return f"{m.group(1)}{src}{m.group(4)}{m.group(5)}{m.group(6)}"
        name, alt = entry
        new_alt = alt if alt else m.group(5)
        return f"{m.group(1)}{BASE}{name}?v={VER}{m.group(4)}{new_alt}{m.group(6)}"

    html2, n = pattern.subn(repl, html)
    print(f"html img remaps applied in {n} slide blocks")

    missing = []
    for idx, (name, alt) in remap.items():
        exists = (MANUAL / name).exists()
        if not exists:
            missing.append(f"{idx}:{name}")
        if idx in by_i:
            by_i[idx]["src"] = f"{BASE}{name}"
            by_i[idx]["exists"] = exists
            if alt:
                by_i[idx]["alt"] = alt

    MAP.write_text(json.dumps(slides, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    HTML.write_text(html2, encoding="utf-8")
    print("updated shot-map + index.html")
    if missing:
        print("MISSING assets (still remapped):", ", ".join(missing))
    else:
        print("all remapped assets present")


if __name__ == "__main__":
    main()
