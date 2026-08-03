"""Audit every HHH user-manual slide: narration vs assigned screenshot."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOT_MAP = ROOT / "videos" / "user-guide-hhh" / "_shot-map.json"
SHOTS = ROOT / "assets" / "screenshots" / "hhh" / "manual"
OUT = ROOT / "videos" / "user-guide-hhh" / "_PICTURE_AUDIT_2026-07-24.md"

# Heuristic keyword → expected shot substrings (any match OK)
EXPECT = [
    (("web companion", "pairing code", "four-digit pairing", "same wi-fi", "local address"), ["09-web-companion"]),
    (("share nearby", "qr + pin", "bluetooth optional"), ["21-demand", "22-demand", "share", "nearby"]),
    (("demand rolodex", "want list", "send want", "accept card"), ["21-demand", "22-demand", "23-demand"]),
    (("device sync",), ["24-device-sync"]),
    (("offline show pack", "offline identify", "airplane"), ["25-offline", "07b"]),
    (("unlock pro", "subscribe", "$9.99", "$74.99", "trial"), ["12-trial", "10-trial"]),
    (("atomic", "exact time"), ["17-atomic"]),
    (("moon phase",), ["18-moon"]),
    (("compare", "side-by-side"), ["16-compare"]),
    (("finances", "p&l", "budget tracker", "insurance report"), ["15-finances"]),
    (("backup", ".hhh", "save a copy", "bring a copy"), ["11-backup"]),
    (("settings", "theme", "language", "security", "notifications", "encryption"), ["10-settings"]),
    (("clockworks", "find parts", "symptom", "clock repair"), ["06-clockworks", "06a-clock"]),
    (("grail radar", "wish-list", "ebay"), ["05-ebay", "04-wishlist", "05b-ebay"]),
    (("identify", "take photo", "brand guess", "confidence"), ["07a-identify", "07-identify", "07b", "07c", "07d"]),
    (("collectors",), ["20-collectors"]),
    (("sample", "ludwig", "clear sample"), ["19-sample", "26-clear", "01-home", "13-onboarding", "14-onboarding"]),
    (("onboarding", "welcome", "get started", "explore with sample"), ["13-onboarding", "14-onboarding"]),
    (("play store", "testflight", "install"), ["00-play", "00-testflight"]),
    (("museum", "owned", "my pieces", "piece detail"), ["02-museum", "03-piece"]),
    (("tools", "toolkit"), ["08-tools"]),
    (("home", "command center", "hunt"), ["01-home"]),
]


def main() -> None:
    slides = json.loads(SHOT_MAP.read_text(encoding="utf-8"))
    lines: list[str] = []
    lines.append("# HHH User Manual — full picture audit (EN)")
    lines.append("")
    lines.append("**Date:** 2026-07-24")
    lines.append("**Scope:** All slides in `videos/user-guide-hhh/` (source of truth before locale rebuild).")
    lines.append("**Rule:** Each PNG must match what the narration describes *and* current app UI.")
    lines.append("")
    lines.append("| # | Verdict | Shot file | Narration (short) | Notes |")
    lines.append("|--:|---------|-----------|-------------------|-------|")

    suspect = 0
    missing = 0
    for s in slides:
        i = s["i"]
        n = s["n"]
        src = s.get("src") or ""
        name = src.split("/")[-1] if src else "(none)"
        path = SHOTS / name if name and not name.startswith("(") else None
        exists = path.exists() if path else False
        if not exists:
            missing += 1
            lines.append(f"| {i} | **MISSING** | `{name}` | {n[:70]}… | File not on disk |")
            continue

        nl = n.lower()
        expected: list[str] = []
        for keys, shots in EXPECT:
            if any(k in nl for k in keys):
                expected.extend(shots)

        verdict = "OK"
        note = ""
        if expected and not any(e in name for e in expected):
            verdict = "CHECK"
            note = f"Narration suggests one of: {', '.join(dict.fromkeys(expected))}; got `{name}`"
            suspect += 1

        # Hard known mismatches
        if "web companion" in nl and "09-web-companion" in name:
            # Always flag WC shot for visual: old QR-to-PC UI
            verdict = "WRONG"
            note = "Narration = LAN URL + 4-digit pairing code; PNG is old ‘Scan on your PC’ QR UI"
            suspect += 1
        if any(k in nl for k in ("$74.99", "subscribe", "unlock pro", "upgrade")) and "12-trial" in name:
            note = (note + "; ").lstrip("; ") + "Pricing mock patched 2026-07-24 ($74.99/yr hero) — recapture tomorrow"
        if "sample collection" in nl and "loading" in nl and "01-home" in name:
            verdict = "CHECK"
            note = "Loading narration uses Home shot; prefer `19-sample-loading.png` if present"
            suspect += 1
        if "clear sample" in nl and "10-settings" in name:
            # may be OK if clear is in settings
            note = note or "Confirm Clear samples control lives on this Settings scroll position"
        if "share nearby" in nl and "09-web-companion" in name:
            verdict = "WRONG"
            note = "Share Nearby (phone QR+PIN) must not reuse Web Companion PC shot"
            suspect += 1

        short = n.replace("|", "/")[:72]
        lines.append(f"| {i} | {verdict} | `{name}` | {short} | {note} |")

    lines.append("")
    lines.append(f"**Heuristic CHECK/WRONG count:** {suspect} · **Missing files:** {missing} · **Total slides:** {len(slides)}")
    lines.append("")
    lines.append("## Next")
    lines.append("1. Visually confirm every CHECK/WRONG (do not trust heuristics alone).")
    lines.append("2. Mockup or recapture WRONG frames on EN only.")
    lines.append("3. Retarget gold taps only after pictures are correct.")
    lines.append("4. Rebuild locale decks from finished EN.")
    lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"suspect={suspect} missing={missing} total={len(slides)}")


if __name__ == "__main__":
    main()
