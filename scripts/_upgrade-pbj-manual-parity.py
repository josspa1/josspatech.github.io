#!/usr/bin/env python3
"""Raise PBJ User Manual EN quality toward HHH parity (desk pass).

- Fix narration↔tap honesty (21 sync-audit issues)
- Fill empty alts
- Write _shot-map.json + picture audit artifacts
- Keep index.html NARRATION and narration-en.json in sync

Does not invent product methodology. Phone recapture still required for flagged slides.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "user-guide"
HTML = OUT / "index.html"
NARR_JSON = OUT / "narration-en.json"

# Narration rewrites keyed by slide index (full replacement strings).
NARR_FIXES: dict[int, str] = {
    # verb+none → overview (already on screen / wait / off-app)
    0: "PocketBudJet opens with a splash screen after install. Wait for it to finish, then continue.",
    5: "On first launch, the Terms of Service tab is open — scroll to the bottom.",
    37: "Category Manager lets you add, merge, or hide categories and sub-categories.",
    47: "Weekly Recap summarizes income, spending, and wins from Coach or your notification.",
    55: "The fastest path starts in your bank app: share the statement into PocketBudJet. Six taps total — no Downloads folder.",
    67: "On Bills, the calendar shows due dates with payday markers and a 30-day cash flow forecast.",
    74: "On Debt, enter balances, APR, and minimum payments.",
    79: "Spending Trends compares month over month. Spot seasonal spikes before they become habits.",
    84: "Net Worth tracks accounts, investments, property, and liabilities in one view.",
    106: "Retirement Planning asks for your target age, desired income, and current savings.",
    # coords+noVerb → ADD_VERB
    21: "Wizard step four: tap Income and enter gross pay and take-home pay. The difference becomes paycheck deductions you can itemize later.",
    25: "Wizard step eight: answer the colorblind-accessibility question, then tap Continue so charts use friendly palettes.",
    50: "Tap Amount and enter it first while it is fresh. Amount is the one field you must not forget.",
    78: "In Coach, tap Reports for spending by category, income vs expenses, and custom layouts.",
    95: "In Privacy and Backup, tap Backup to turn on encrypted cloud backup, set retention, and control app lock.",
    96: "Under Data Management, tap Storage to set how much history lives on-device, manage receipt image storage, and archive old years.",
    108: "In Settings, tap Mindful Features to enable spending pause, impulse check, cooling-off periods, and a mindful score before big purchases.",
    110: "Launch PC Web Companion from Toolbox. Tap Companion and scan the QR code to pair over your LAN — drag-and-drop import on a full-size screen.",
    117: "Tap App lock in Privacy settings to set biometric or passcode lock. Generate your recovery key once — store it safely offline.",
}

# Tap attribute fixes: None = data-tap-none; else (x, y, label)
TAP_FIXES: dict[int, tuple[int, int, str] | None] = {
    0: None,  # splash wait
    5: (28, 18, "Terms"),  # Terms tab on onboarding shot
    61: (50, 38, "History row"),
    75: (32, 42, "Avalanche"),
    # 37, 47, 55, 67, 74, 79, 84, 106 stay tap-none after reword
}

# Known picture problems for audit (idx → note). Heuristic audit also runs.
PICTURE_FLAGS: dict[int, tuple[str, str]] = {
    50: ("CHECK", "Add Transaction / scan hybrid — Amount visible; full manual form recapture preferred"),
    51: ("WRONG", "Narration wants merchant/category; shot is scan + quick amount only"),
    52: ("WRONG", "Narration wants Split; Split control not on this shot"),
    53: ("WRONG", "Narration wants Save; Save control not on this shot"),
    86: ("CHECK", "Connect Bank cluster may reuse generic bank-sync.png"),
    87: ("CHECK", "Connect Bank — confirm live search UI"),
    96: ("CHECK", "Data Management narrated on Privacy/Backup overview — scroll-capture needed"),
    98: ("CHECK", "Bank connect / trial cluster reuse"),
    99: ("CHECK", "Connect Bank account pick — recapture preferred"),
    100: ("CHECK", "Connect Bank — recapture preferred"),
    106: ("WRONG", "Retirement narrated; Goals/languages screenshot shown — must recapture"),
    108: ("CHECK", "Mindful Features narrated on Privacy/Backup overview — scroll-capture needed"),
    110: ("CHECK", "Verify current Web Companion pairing UX matches QR narration"),
    117: ("CHECK", "App lock narrated on Privacy/Backup overview — scroll-capture needed"),
}

EXPECT = [
    (("retirement",), ["retirement", "goals-languages"]),
    (("web companion", "qr code", "companion"), ["web-companion", "07-web"]),
    (("mindful",), ["mindful", "privacy-backup", "settings"]),
    (("app lock", "biometric", "recovery key"), ["privacy-backup", "security", "settings"]),
    (("data management", "storage"), ["privacy-backup", "settings", "data"]),
    (("connect bank", "quiltt", "link account"), ["bank-sync", "connect-bank"]),
    (("spending trends",), ["spending-trends", "reports"]),
    (("net worth",), ["net-worth"]),
    (("avalanche", "snowball", "debt"), ["debt-"]),
    (("bills", "calendar", "due dates"), ["bills-"]),
    (("import history",), ["import-history", "import"]),
    (("category manager",), ["category-manager"]),
    (("weekly recap",), ["weekly-recap", "coach"]),
    (("splash",), ["splash"]),
    (("terms of service",), ["onboarding-terms"]),
]


def js_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def alt_from_src(src: str | None, narr: str) -> str:
    if not src:
        return (narr[:72] + "…") if len(narr) > 72 else narr
    name = Path(src.split("?")[0]).stem.replace("-", " ").replace("_", " ")
    return name[:1].upper() + name[1:] if name else "PocketBudJet screen"


def parse_slides(html: str) -> list[dict]:
    slides = []
    for m in re.finditer(r'<div class="slide(?:\s+active)?"([^>]*)>', html):
        attrs = m.group(1)
        idx = int(re.search(r'data-index="(\d+)"', attrs).group(1))
        chunk = html[m.start() : m.start() + 1200]
        src_m = re.search(r'<img[^>]+src="([^"]+)', chunk)
        alt_m = re.search(r'alt="([^"]*)"', chunk)
        slides.append(
            {
                "idx": idx,
                "attrs": attrs,
                "start": m.start(),
                "full_open": m.group(0),
                "src": src_m.group(1) if src_m else None,
                "alt": alt_m.group(1) if alt_m else "",
                "img_tag": src_m.group(0) if src_m else None,
            }
        )
    return slides


def apply_tap_fixes(html: str) -> tuple[str, int]:
    changed = 0

    def repl(m: re.Match[str]) -> str:
        nonlocal changed
        full = m.group(0)
        idx = int(m.group(1))
        if idx not in TAP_FIXES:
            return full
        fix = TAP_FIXES[idx]
        show = re.search(r'data-tap-show-at="([^"]+)"', full)
        dur = re.search(r'data-tap-duration="([^"]+)"', full)
        show_at = show.group(1) if show else "0.3"
        duration = dur.group(1) if dur else "3.0"
        class_m = re.search(r'class="([^"]*)"', full)
        cls = class_m.group(1) if class_m else "slide"
        if fix is None:
            new = f'<div class="{cls}" data-index="{idx}" data-tap-none>'
        else:
            x, y, label = fix
            new = (
                f'<div class="{cls}" data-index="{idx}" '
                f'data-tap-x="{x}" data-tap-y="{y}" data-tap-label="{label}" '
                f'data-tap-show-at="{show_at}" data-tap-duration="{duration}">'
            )
        if new != full:
            changed += 1
        return new

    html2 = re.sub(
        r'<div class="slide[^"]*"[^>]*data-index="(\d+)"[^>]*>',
        repl,
        html,
    )
    return html2, changed


def replace_narration_array(html: str, narr: list[str]) -> str:
    block = ",\n".join(f'"{js_escape(t)}"' for t in narr)
    # Keep single-line style if original was single-line
    if "const NARRATION = [" in html and "\n" not in html.split("const NARRATION = [", 1)[1][:200]:
        block = ",".join(f'"{js_escape(t)}"' for t in narr)
    new_html, n = re.subn(
        r"const NARRATION = \[.*?\];",
        f"const NARRATION = [{block}];",
        html,
        count=1,
        flags=re.DOTALL,
    )
    if n != 1:
        raise SystemExit("Failed to replace NARRATION array in index.html")
    return new_html


def fill_alts(html: str, narr: list[str]) -> tuple[str, int]:
    slides = parse_slides(html)
    changed = 0
    # Replace empty alt="" on each slide img (first img after slide open)
    for s in slides:
        i = s["idx"]
        src = s["src"]
        if not src:
            continue
        desired = alt_from_src(src, narr[i] if i < len(narr) else "")
        # Find img tag after this slide open within next 800 chars
        region_start = s["start"]
        region = html[region_start : region_start + 900]
        m = re.search(r'(<img[^>]*\salt=")([^"]*)(")', region)
        if not m:
            continue
        if m.group(2).strip():
            continue
        abs_start = region_start + m.start(2)
        abs_end = region_start + m.end(2)
        html = html[:abs_start] + desired.replace('"', "") + html[abs_end:]
        changed += 1
    return html, changed


def write_shot_map(narr: list[str], html: str) -> list[dict]:
    slides = parse_slides(html)
    by = {s["idx"]: s for s in slides}
    rows = []
    for i, n in enumerate(narr):
        s = by.get(i, {})
        src = s.get("src")
        clean = src.split("?")[0] if src else None
        rows.append(
            {
                "i": i,
                "n": n,
                "src": clean,
                "alt": s.get("alt") or alt_from_src(clean, n),
                "exists": bool(clean and (ROOT / clean.lstrip("/")).exists()),
            }
        )
    (OUT / "_shot-map.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    return rows


def write_picture_audit(rows: list[dict]) -> tuple[int, int]:
    today = date.today().isoformat()
    lines = [
        "# PBJ User Manual — full picture audit (EN)",
        "",
        f"**Date:** {today}",
        "**Scope:** All slides in `videos/user-guide/` (source of truth before locale rebuild).",
        "**Rule:** Each PNG must match what the narration describes *and* current app UI.",
        "",
        "| # | Verdict | Shot file | Narration (short) | Notes |",
        "|--:|---------|-----------|-------------------|-------|",
    ]
    suspect = 0
    missing = 0
    for s in rows:
        i = s["i"]
        n = s["n"]
        src = s.get("src") or ""
        name = src.split("/")[-1] if src else "(none)"
        exists = s.get("exists", False)
        if not exists:
            missing += 1
            lines.append(f"| {i} | **MISSING** | `{name}` | {n[:70]} | File not on disk |")
            continue

        nl = n.lower()
        expected: list[str] = []
        for keys, shots in EXPECT:
            if any(k in nl for k in keys):
                expected.extend(shots)

        verdict = "OK"
        note = ""
        if expected and not any(e in src for e in expected):
            # goals-languages is expected for retirement only as known-wrong marker
            if "retirement" in nl and "goals-languages" in src:
                verdict = "WRONG"
                note = "Retirement UI missing — Goals/languages stand-in"
            else:
                verdict = "CHECK"
                note = f"Narration suggests one of: {', '.join(dict.fromkeys(expected))}; got `{name}`"
            suspect += 1

        if i in PICTURE_FLAGS:
            v, note2 = PICTURE_FLAGS[i]
            verdict = v
            note = note2
            if v in ("CHECK", "WRONG"):
                suspect += 1

        short = n.replace("|", "/")[:72]
        lines.append(f"| {i} | {verdict} | `{name}` | {short} | {note} |")

    lines.append("")
    lines.append(
        f"**Heuristic CHECK/WRONG count:** {suspect} · **Missing files:** {missing} · **Total slides:** {len(rows)}"
    )
    lines.append("")
    lines.append("## Next")
    lines.append("1. Visually confirm every CHECK/WRONG (do not trust heuristics alone).")
    lines.append("2. Recapture WRONG frames on EN only (Retirement, txn form Save/Split/Merchant, Settings depth, Connect Bank).")
    lines.append("3. Retarget gold taps only after pictures are correct.")
    lines.append("4. Rebuild locale decks from finished EN (current locale folders are 28-slide stubs).")
    lines.append("")

    audit_path = OUT / f"_PICTURE_AUDIT_{today}.md"
    audit_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Summary (HHH pattern)
    reuse = Counter(r["src"] for r in rows).most_common(15)
    summary = f"""# PBJ User Manual — EN picture audit summary ({today})

**Scope:** All **{len(rows)}** English slides in `videos/user-guide/`
**Rule:** Picture must match the narration **and** current app UI.
**Locales:** Frozen until this EN pass is acceptable (same policy as HHH).

---

## What this desk pass did

1. Cleared narration↔tap sync issues (reword overview / add verbs / add taps).
2. Filled empty `alt` text on all slides.
3. Generated `_shot-map.json` + this audit.
4. Flagged known WRONG/CHECK frames for phone recapture.

---

## Must recapture (phone)

| Topic | Slides | Why |
|-------|--------|-----|
| Retirement Planning | 106 | Goals/languages stand-in |
| Manual transaction form | 51–53 | Scan/quick-entry shot lacks merchant / Split / Save |
| Settings depth | 96, 108, 117 | Privacy overview reused for Data Mgmt / Mindful / App lock |
| Connect Bank | 87, 99–100 | Generic bank-sync reuse; `connect-bank/` folder empty |
| Web Companion | 110 | Confirm QR vs current pairing UX |

---

## Reuse hotspots (top files)

{chr(10).join(f"- {n}× `{src}`" for src, n in reuse if src)}

---

## Files for review

- `{audit_path.name}`
- `_shot-map.json`
- Re-run: `node scripts/_audit-pbj-guide-sync.js` (target tapIssues: 0)
"""
    (OUT / "_PICTURE_AUDIT_SUMMARY.md").write_text(summary, encoding="utf-8")
    return suspect, missing


def main() -> None:
    narr = json.loads(NARR_JSON.read_text(encoding="utf-8"))
    if not isinstance(narr, list):
        raise SystemExit("narration-en.json must be a JSON array")

    changed_narr = []
    for i, text in NARR_FIXES.items():
        if i >= len(narr):
            raise SystemExit(f"Narration fix index {i} out of range ({len(narr)})")
        if narr[i] != text:
            narr[i] = text
            changed_narr.append(i)

    NARR_JSON.write_text(json.dumps(narr, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    html = HTML.read_text(encoding="utf-8")
    html = replace_narration_array(html, narr)
    html, tap_changed = apply_tap_fixes(html)
    html, alt_changed = fill_alts(html, narr)
    HTML.write_text(html, encoding="utf-8", newline="\n")

    rows = write_shot_map(narr, html)
    suspect, missing = write_picture_audit(rows)

    regen = sorted(set(changed_narr))
    (OUT / "_audio_regen_slides.json").write_text(json.dumps(regen, indent=2) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "narr_fixed": changed_narr,
                "tap_changed": tap_changed,
                "alts_filled": alt_changed,
                "slides": len(rows),
                "unique_src": len({r["src"] for r in rows if r["src"]}),
                "audit_suspect": suspect,
                "audit_missing": missing,
                "audio_regen": regen,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
