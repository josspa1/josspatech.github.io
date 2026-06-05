#!/usr/bin/env python3
"""Second-pass: replace leftover generic screenshots in feature videos."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ILLUS = "/assets/illustrations-pocketbudjet"
DASH = "/assets/screenshots/budget-setup/step-7-dashboard.png"

FILES: dict[str, dict[str, str]] = {
    "videos/pocketbudjet/mindful-features/index.html": {
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-savings-goal.svg",
    },
    "videos/pocketbudjet/data-management/index.html": {
        "/assets/screenshots/scanner.png": f"{ILLUS}/pbj-receipt-scan.svg",
    },
    "videos/pocketbudjet/reports/index.html": {
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-settings-export.svg",
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-settings-export.svg",
    },
    "videos/pocketbudjet/voice-shortcuts/index.html": {
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-add-transaction.svg",
        "/assets/screenshots/budget.png": f"{ILLUS}/pbj-ai-coach.svg",
    },
    "videos/pocketbudjet/transaction-rules/index.html": {
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-search-filters.svg",
    },
    "videos/pocketbudjet/net-worth/index.html": {
        "/assets/screenshots/ai-coach.png": f"{ILLUS}/pbj-debt-planner.svg",
    },
    "videos/pocketbudjet/retirement-planning/index.html": {
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-savings-goal.svg",
    },
    "videos/import/index.html": {
        "/assets/screenshots/budget.png": f"{ILLUS}/pbj-import-csv.svg",
    },
    "videos/pocketbudjet/pc-dashboard/index.html": {
        "/assets/screenshots/scanner.png": f"{ILLUS}/pbj-import-csv.svg",
        "/assets/screenshots/ai-coach.png": f"{ILLUS}/pbj-pc-dashboard.svg",
    },
    "videos/pocketbudjet/search/index.html": {
        "/assets/screenshots/budget.png": f"{ILLUS}/pbj-search-filters.svg",
    },
    "videos/pocketbudjet/calendar-view/index.html": {
        "/assets/screenshots/budget.png": f"{ILLUS}/pbj-bills-calendar.svg",
    },
    "videos/pocketbudjet/bills-recurring/index.html": {
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-bills-calendar.svg",
    },
    "videos/pocketbudjet/export-sharing/index.html": {
        "/assets/screenshots/dashboard.png": f"{ILLUS}/pbj-settings-export.svg",
    },
    "videos/pocketbudjet/adding-transactions/index.html": {
        "/assets/screenshots/dashboard.png": DASH,
    },
    "videos/pocketbudjet/share-statements/index.html": {
        "/assets/screenshots/dashboard.png": DASH,
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-import-receiving.svg",
    },
    "videos/pocketbudjet/privacy-pitch/index.html": {
        "/assets/screenshots/privacy.png": f"{ILLUS}/pbj-settings-export.svg",
        "/assets/screenshots/scanner.png": f"{ILLUS}/pbj-import-csv.svg",
        "/assets/screenshots/dashboard.png": DASH,
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-settings-export.svg",
    },
    "videos/pocketbudjet/digital-receipt-import/index.html": {
        "/assets/screenshots/transactions.png": f"{ILLUS}/pbj-import-receiving.svg",
        "/assets/screenshots/scanner.png": f"{ILLUS}/pbj-import-csv.svg",
    },
}


def main() -> None:
    for rel, mapping in FILES.items():
        path = ROOT / rel
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        orig = html
        for old, new in mapping.items():
            html = html.replace(old, new)
        if html != orig:
            path.write_text(html, encoding="utf-8", newline="\n")
            print("fixed", rel)


if __name__ == "__main__":
    main()
