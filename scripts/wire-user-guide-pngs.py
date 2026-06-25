#!/usr/bin/env python3
"""Restore real PocketBudJet PNG screenshots on user-guide slides (reverse wire-user-guide-illustrations)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASH = "/assets/screenshots/budget-setup/step-7-dashboard.png"

# alt text substring (case-insensitive) -> PNG src
ALT_MAP: list[tuple[str, str]] = [
    ("pc dashboard", "/assets/screenshots/pbj/07-web-companion.png"),
    ("panel pc", "/assets/screenshots/pbj/07-web-companion.png"),
    ("电脑", "/assets/screenshots/pbj/07-web-companion.png"),
    ("dashboard", "/assets/screenshots/pbj/01-home-dashboard.png"),
    ("panel principal", "/assets/screenshots/pbj/01-home-dashboard.png"),
    ("仪表板", "/assets/screenshots/pbj/01-home-dashboard.png"),
    ("transaccion", "/assets/screenshots/transactions.png"),
    ("transaction", "/assets/screenshots/transactions.png"),
    ("交易", "/assets/screenshots/transactions.png"),
    ("scan", "/assets/screenshots/scanner.png"),
    ("escáner", "/assets/screenshots/scanner.png"),
    ("扫描", "/assets/screenshots/scanner.png"),
    ("scanning", "/assets/screenshots/scanner.png"),
    ("budget", "/assets/screenshots/pbj/03-budget-envelopes.png"),
    ("presupuesto", "/assets/screenshots/pbj/03-budget-envelopes.png"),
    ("预算", "/assets/screenshots/pbj/03-budget-envelopes.png"),
    ("bill", "/assets/screenshots/bills.png"),
    ("factura", "/assets/screenshots/bills.png"),
    ("账单", "/assets/screenshots/bills.png"),
    ("recurring", "/assets/screenshots/bills.png"),
    ("saving", "/assets/screenshots/pbj/06-goals-languages.png"),
    ("ahorro", "/assets/screenshots/pbj/06-goals-languages.png"),
    ("储蓄", "/assets/screenshots/pbj/06-goals-languages.png"),
    ("goal", "/assets/screenshots/pbj/06-goals-languages.png"),
    ("debt", "/assets/screenshots/debt.png"),
    ("deuda", "/assets/screenshots/debt.png"),
    ("债务", "/assets/screenshots/debt.png"),
    ("invest", "/assets/screenshots/net-worth/net-worth.png"),
    ("inversion", "/assets/screenshots/net-worth/net-worth.png"),
    ("投资", "/assets/screenshots/net-worth/net-worth.png"),
    ("report", "/assets/screenshots/dashboard.png"),
    ("informe", "/assets/screenshots/dashboard.png"),
    ("报告", "/assets/screenshots/dashboard.png"),
    ("coach", "/assets/screenshots/pbj/05-ai-coach.png"),
    ("assistant", "/assets/screenshots/pbj/05-ai-coach.png"),
    ("教练", "/assets/screenshots/pbj/05-ai-coach.png"),
    ("asistente", "/assets/screenshots/pbj/05-ai-coach.png"),
    ("助手", "/assets/screenshots/pbj/05-ai-coach.png"),
    ("search", "/assets/screenshots/pbj/01-home-dashboard.png"),
    ("búsqueda", "/assets/screenshots/pbj/01-home-dashboard.png"),
    ("搜索", "/assets/screenshots/pbj/01-home-dashboard.png"),
    ("export", "/assets/screenshots/privacy.png"),
    ("导出", "/assets/screenshots/privacy.png"),
    ("import", "/assets/screenshots/pbj/02-import-center.png"),
    ("impuesto", "/assets/screenshots/pbj/02-import-center.png"),
    ("税务", "/assets/screenshots/pbj/02-import-center.png"),
    ("flexibility", "/assets/screenshots/pbj/02-import-center.png"),
    ("household", "/assets/screenshots/household-sync/household-sync.png"),
    ("hogar", "/assets/screenshots/household-sync/household-sync.png"),
    ("家庭", "/assets/screenshots/household-sync/household-sync.png"),
    ("calendar", "/assets/screenshots/bills.png"),
    ("calendario", "/assets/screenshots/bills.png"),
    ("日历", "/assets/screenshots/bills.png"),
    ("rule", "/assets/screenshots/transactions.png"),
    ("regla", "/assets/screenshots/transactions.png"),
    ("规则", "/assets/screenshots/transactions.png"),
    ("mindful", "/assets/screenshots/pbj/06-goals-languages.png"),
    ("conscient", "/assets/screenshots/pbj/06-goals-languages.png"),
    ("正念", "/assets/screenshots/pbj/06-goals-languages.png"),
    ("retirement", "/assets/screenshots/pbj/06-goals-languages.png"),
    ("jubilación", "/assets/screenshots/pbj/06-goals-languages.png"),
    ("退休", "/assets/screenshots/pbj/06-goals-languages.png"),
    ("voice", "/assets/screenshots/pbj/05-ai-coach.png"),
    ("voz", "/assets/screenshots/pbj/05-ai-coach.png"),
    ("语音", "/assets/screenshots/pbj/05-ai-coach.png"),
    ("pricing", DASH),
    ("precio", DASH),
    ("定价", DASH),
    ("privacy", "/assets/screenshots/privacy.png"),
    ("privacidad", "/assets/screenshots/privacy.png"),
    ("隐私", "/assets/screenshots/privacy.png"),
    ("security", "/assets/screenshots/privacy.png"),
    ("data", "/assets/screenshots/pbj/02-import-center.png"),
    ("storage", "/assets/screenshots/pbj/02-import-center.png"),
    ("almacenamiento", "/assets/screenshots/pbj/02-import-center.png"),
    ("datos", "/assets/screenshots/pbj/02-import-center.png"),
    ("数据", "/assets/screenshots/pbj/02-import-center.png"),
    ("存储", "/assets/screenshots/pbj/02-import-center.png"),
    ("help", DASH),
    ("ayuda", DASH),
    ("帮助", DASH),
    ("accessib", DASH),
    ("无障碍", DASH),
    ("accesibilidad", DASH),
]

# Slide 0 (Welcome & Onboarding) uses budget-setup finale, not home dashboard
SLIDE0_SRC = DASH

OLD_SECTION_SUB = "Real screens, gold pulse on where to tap, step-by-step narration."
NEW_SECTION_SUB = (
    "PocketBudJet app screenshots with gold pulse tap guides and step-by-step narration. "
    "Some slides reuse the nearest feature screenshot until dedicated per-step captures ship."
)

LOCALIZED_OLD_SUBS = [
    "असली स्क्रीन, सुन्‍हरा पल्स जहाँ टैप करें, कदम-दर-कदम कथन।",
    "Real screens, gold pulse on where to tap, step-by-step narration.",
]


def pick_src(alt: str, slide_index: int) -> str:
    if slide_index == 0:
        return SLIDE0_SRC
    low = alt.lower()
    for needle, src in ALT_MAP:
        if needle in low:
            return src
    return DASH


def wire_file(path: Path) -> int:
    html = path.read_text(encoding="utf-8")
    count = 0
    slide_index = 0

    def repl(m: re.Match) -> str:
        nonlocal count, slide_index
        src = m.group(1)
        alt = m.group(2)
        if not (src.endswith(".svg") or "/illustrations-pocketbudjet/" in src):
            slide_index += 1
            return m.group(0)
        new_src = pick_src(alt, slide_index)
        slide_index += 1
        count += 1
        return f'<img src="{new_src}" alt="{alt}"'

    new_html = re.sub(
        r'<img src="([^"]+)" alt="([^"]*)"',
        repl,
        html,
    )

    for old in LOCALIZED_OLD_SUBS:
        if old in new_html:
            # Keep Hindi sub localized but honest
            if "असली" in old:
                new_html = new_html.replace(
                    old,
                    "PocketBudJet ऐप स्क्रीनशॉट, टैप गाइड के लिए सुनहरी पल्स, और चरण-दर-चरण कथन। "
                    "कुछ स्लाइडें निकटतम फीचर स्क्रीनशॉट दोहराती हैं।",
                )
            else:
                new_html = new_html.replace(old, NEW_SECTION_SUB)

    if new_html != html:
        path.write_text(new_html, encoding="utf-8", newline="\n")
    return count


def main() -> None:
    guides = sorted((ROOT / "videos").glob("user-guide*/index.html"))
    total = 0
    for path in guides:
        n = wire_file(path)
        total += n
        print(f"{path.parent.name}: {n} PNGs restored")
    print(f"\nTotal replacements: {total}")


if __name__ == "__main__":
    main()
