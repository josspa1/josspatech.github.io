#!/usr/bin/env python3
"""Map user-guide and quick-start slides to illustrated UI scenes."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ILLUS = "/assets/illustrations-pocketbudjet"
DASH = "/assets/screenshots/budget-setup/step-7-dashboard.png"

# alt text substring (case-insensitive) -> image src
ALT_MAP: list[tuple[str, str]] = [
    ("pc dashboard", f"{ILLUS}/pbj-pc-dashboard.svg"),
    ("panel pc", f"{ILLUS}/pbj-pc-dashboard.svg"),
    ("电脑", f"{ILLUS}/pbj-pc-dashboard.svg"),
    ("dashboard", DASH),
    ("panel principal", DASH),
    ("仪表板", DASH),
    ("transaccion", f"{ILLUS}/pbj-add-transaction.svg"),
    ("transaction", f"{ILLUS}/pbj-add-transaction.svg"),
    ("交易", f"{ILLUS}/pbj-add-transaction.svg"),
    ("scan", f"{ILLUS}/pbj-receipt-scan.svg"),
    ("escáner", f"{ILLUS}/pbj-receipt-scan.svg"),
    ("扫描", f"{ILLUS}/pbj-receipt-scan.svg"),
    ("budget", f"{ILLUS}/pbj-savings-goal.svg"),
    ("presupuesto", f"{ILLUS}/pbj-savings-goal.svg"),
    ("预算", f"{ILLUS}/pbj-savings-goal.svg"),
    ("bill", f"{ILLUS}/pbj-bills-calendar.svg"),
    ("factura", f"{ILLUS}/pbj-bills-calendar.svg"),
    ("账单", f"{ILLUS}/pbj-bills-calendar.svg"),
    ("saving", f"{ILLUS}/pbj-savings-goal.svg"),
    ("ahorro", f"{ILLUS}/pbj-savings-goal.svg"),
    ("储蓄", f"{ILLUS}/pbj-savings-goal.svg"),
    ("debt", f"{ILLUS}/pbj-debt-planner.svg"),
    ("deuda", f"{ILLUS}/pbj-debt-planner.svg"),
    ("债务", f"{ILLUS}/pbj-debt-planner.svg"),
    ("invest", f"{ILLUS}/pbj-debt-planner.svg"),
    ("投资", f"{ILLUS}/pbj-debt-planner.svg"),
    ("report", f"{ILLUS}/pbj-settings-export.svg"),
    ("informe", f"{ILLUS}/pbj-settings-export.svg"),
    ("报告", f"{ILLUS}/pbj-settings-export.svg"),
    ("coach", f"{ILLUS}/pbj-ai-coach.svg"),
    ("assistant", f"{ILLUS}/pbj-ai-coach.svg"),
    ("教练", f"{ILLUS}/pbj-ai-coach.svg"),
    ("asistente", f"{ILLUS}/pbj-ai-coach.svg"),
    ("助手", f"{ILLUS}/pbj-ai-coach.svg"),
    ("accessib", DASH),
    ("无障碍", DASH),
    ("accesibilidad", DASH),
    ("inversion", f"{ILLUS}/pbj-debt-planner.svg"),
    ("search", f"{ILLUS}/pbj-search-filters.svg"),
    ("búsqueda", f"{ILLUS}/pbj-search-filters.svg"),
    ("搜索", f"{ILLUS}/pbj-search-filters.svg"),
    ("export", f"{ILLUS}/pbj-settings-export.svg"),
    ("导出", f"{ILLUS}/pbj-settings-export.svg"),
    ("import", f"{ILLUS}/pbj-import-csv.svg"),
    ("impuesto", f"{ILLUS}/pbj-import-csv.svg"),
    ("税务", f"{ILLUS}/pbj-import-csv.svg"),
    ("household", f"{ILLUS}/pbj-household-qr.svg"),
    ("hogar", f"{ILLUS}/pbj-household-qr.svg"),
    ("家庭", f"{ILLUS}/pbj-household-qr.svg"),
    ("calendar", f"{ILLUS}/pbj-bills-calendar.svg"),
    ("calendario", f"{ILLUS}/pbj-bills-calendar.svg"),
    ("日历", f"{ILLUS}/pbj-bills-calendar.svg"),
    ("rule", f"{ILLUS}/pbj-search-filters.svg"),
    ("regla", f"{ILLUS}/pbj-search-filters.svg"),
    ("规则", f"{ILLUS}/pbj-search-filters.svg"),
    ("mindful", f"{ILLUS}/pbj-savings-goal.svg"),
    ("conscient", f"{ILLUS}/pbj-savings-goal.svg"),
    ("正念", f"{ILLUS}/pbj-savings-goal.svg"),
    ("retirement", f"{ILLUS}/pbj-savings-goal.svg"),
    ("jubilación", f"{ILLUS}/pbj-savings-goal.svg"),
    ("退休", f"{ILLUS}/pbj-savings-goal.svg"),
    ("voice", f"{ILLUS}/pbj-ai-coach.svg"),
    ("voz", f"{ILLUS}/pbj-ai-coach.svg"),
    ("语音", f"{ILLUS}/pbj-ai-coach.svg"),
    ("pricing", DASH),
    ("precio", DASH),
    ("定价", DASH),
    ("privacy", f"{ILLUS}/pbj-settings-export.svg"),
    ("privacidad", f"{ILLUS}/pbj-settings-export.svg"),
    ("隐私", f"{ILLUS}/pbj-settings-export.svg"),
    ("data", f"{ILLUS}/pbj-settings-export.svg"),
    ("storage", f"{ILLUS}/pbj-settings-export.svg"),
    ("help", DASH),
    ("ayuda", DASH),
    ("帮助", DASH),
    ("accessib", DASH),
    ("wizard", f"{ILLUS}/pbj-savings-goal.svg"),
    ("setup", f"{ILLUS}/pbj-savings-goal.svg"),
    ("bank data", f"{ILLUS}/pbj-import-csv.svg"),
    ("color", f"{ILLUS}/pbj-savings-goal.svg"),
    ("payoff", f"{ILLUS}/pbj-ai-coach.svg"),
]

GUIDE_FILES = [
    "videos/user-guide/index.html",
    "videos/user-guide-de/index.html",
    "videos/user-guide-es/index.html",
    "videos/user-guide-zh/index.html",
    "videos/quick-start/index.html",
]


def pick_src(alt: str) -> str | None:
    low = alt.lower()
    for needle, src in ALT_MAP:
        if needle in low:
            return src
    return None


def wire_file(path: Path) -> int:
    html = path.read_text(encoding="utf-8")
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        alt = m.group(1)
        src = pick_src(alt)
        if not src:
            return m.group(0)
        count += 1
        return f'<img src="{src}" alt="{alt}"'

    new_html = re.sub(
        r'<img src="/assets/screenshots/[^"]+" alt="([^"]*)"',
        lambda m: repl(m) if pick_src(m.group(1)) else m.group(0),
        html,
    )
    # quick-start: also replace remaining generic paths by alt
    new_html = re.sub(
        r'<img src="([^"]+)" alt="([^"]*)"',
        lambda m: (
            f'<img src="{pick_src(m.group(2))}" alt="{m.group(2)}"'
            if pick_src(m.group(2)) and "/screenshots/" in m.group(1)
            else m.group(0)
        ),
        new_html,
    )
    if new_html != html:
        path.write_text(new_html, encoding="utf-8", newline="\n")
    return count


def main() -> None:
    for rel in GUIDE_FILES:
        path = ROOT / rel.replace("/", "\\")
        if not path.exists():
            path = ROOT / rel
        n = wire_file(path)
        print(f"{rel}: {n} images wired")


if __name__ == "__main__":
    main()
