#!/usr/bin/env python3
"""Wire illustrated UI scenes into feature video slideshows."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ILLUS = "/assets/illustrations-pocketbudjet"

# video path suffix -> {old screenshot fragment: new svg}
REPLACEMENTS: dict[str, dict[str, str]] = {
    "videos/pocketbudjet/export-sharing/index.html": {
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-settings-export.svg",
        "/assets/screenshots/budget.png": f"{ILLUS}/pbj-settings-export.svg",
    },
    "videos/pocketbudjet/debt-freedom/index.html": {
        "/assets/screenshots/debt.png": f"{ILLUS}/pbj-debt-planner.svg",
        "/assets/screenshots/budget.png": f"{ILLUS}/pbj-debt-planner.svg",
        "/assets/screenshots/ai-coach.png": f"{ILLUS}/pbj-debt-planner.svg",
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-debt-planner.svg",
    },
    "videos/pocketbudjet/household-sync/index.html": {
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-household-qr.svg",
        "/assets/screenshots/budget.png": f"{ILLUS}/pbj-household-qr.svg",
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-household-qr.svg",
        "/assets/screenshots/privacy.png": f"{ILLUS}/pbj-household-qr.svg",
    },
    "videos/pocketbudjet/bills-recurring/index.html": {
        "/assets/screenshots/bills.png": f"{ILLUS}/pbj-bills-calendar.svg",
        "/assets/screenshots/budget.png": f"{ILLUS}/pbj-bills-calendar.svg",
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-bills-calendar.svg",
    },
    "videos/pocketbudjet/calendar-view/index.html": {
        "/assets/screenshots/bills.png": f"{ILLUS}/pbj-bills-calendar.svg",
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-bills-calendar.svg",
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-bills-calendar.svg",
    },
    "videos/pocketbudjet/savings-goals/index.html": {
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-savings-goal.svg",
        "/assets/screenshots/budget.png": f"{ILLUS}/pbj-savings-goal.svg",
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-savings-goal.svg",
    },
    "videos/pocketbudjet/receipt-scanning/index.html": {
        "/assets/screenshots/scanner.png": f"{ILLUS}/pbj-receipt-scan.svg",
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-receipt-scan.svg",
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-receipt-scan.svg",
    },
    "videos/pocketbudjet/ai-coach/index.html": {
        "/assets/screenshots/ai-coach.png": f"{ILLUS}/pbj-ai-coach.svg",
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-ai-coach.svg",
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-ai-coach.svg",
        "/assets/screenshots/budget.png": f"{ILLUS}/pbj-ai-coach.svg",
        "/assets/screenshots/privacy.png": f"{ILLUS}/pbj-ai-coach.svg",
    },
    "videos/pocketbudjet/search/index.html": {
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-search-filters.svg",
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-search-filters.svg",
    },
    "videos/pocketbudjet/pc-dashboard/index.html": {
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-pc-dashboard.svg",
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-pc-dashboard.svg",
        "/assets/screenshots/budget.png": f"{ILLUS}/pbj-pc-dashboard.svg",
    },
    "videos/import/index.html": {
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-import-csv.svg",
        "/assets/screenshots/scanner.png": f"{ILLUS}/pbj-import-csv.svg",
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-import-csv.svg",
    },
    "videos/pocketbudjet/transaction-rules/index.html": {
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-search-filters.svg",
    },
    "videos/pocketbudjet/retirement-planning/index.html": {
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-savings-goal.svg",
        "/assets/screenshots/budget.png": f"{ILLUS}/pbj-savings-goal.svg",
    },
    "videos/pocketbudjet/net-worth/index.html": {
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-debt-planner.svg",
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-debt-planner.svg",
    },
    "videos/pocketbudjet/voice-shortcuts/index.html": {
        "/assets/screenshots/ai-coach.png": f"{ILLUS}/pbj-ai-coach.svg",
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-ai-coach.svg",
    },
    "videos/pocketbudjet/reports/index.html": {
        "/assets/screenshots/budget.png": f"{ILLUS}/pbj-settings-export.svg",
        "/assets/screenshots/debt.png": f"{ILLUS}/pbj-debt-planner.svg",
        "/assets/screenshots/ai-coach.png": f"{ILLUS}/pbj-ai-coach.svg",
    },
    "videos/pocketbudjet/data-management/index.html": {
        "/assets/screenshots/privacy.png": f"{ILLUS}/pbj-settings-export.svg",
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-settings-export.svg",
    },
    "videos/pocketbudjet/privacy-security/index.html": {
        "/assets/screenshots/privacy.png": f"{ILLUS}/pbj-settings-export.svg",
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-settings-export.svg",
    },
    "videos/pocketbudjet/mindful-features/index.html": {
        "/assets/screenshots/budget.png": f"{ILLUS}/pbj-savings-goal.svg",
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-savings-goal.svg",
    },
}


def main() -> None:
    for rel, mapping in REPLACEMENTS.items():
        path = ROOT / rel.replace("/", "\\") if "\\" in str(ROOT) else ROOT / Path(rel)
        if not path.exists():
            path = ROOT / rel
        if not path.exists():
            print("skip missing", rel)
            continue
        html = path.read_text(encoding="utf-8")
        original = html
        for old, new in mapping.items():
            html = html.replace(old, new)
        if html != original:
            path.write_text(html, encoding="utf-8", newline="\n")
            print("wired", rel)


if __name__ == "__main__":
    main()
