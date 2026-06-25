#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
updates = {
    "videos/pocketbudjet/bills-recurring/index.html": (
        "/assets/illustrations-pocketbudjet/pbj-bills-calendar.svg",
        "/assets/screenshots/bills-recurring/bills-calendar.png",
        1,
    ),
    "videos/pocketbudjet/household-sync/index.html": (
        "/assets/illustrations-pocketbudjet/pbj-household-qr.svg",
        "/assets/screenshots/household-sync/household-sync.png",
        1,
    ),
    "videos/pocketbudjet/net-worth/index.html": (
        "/assets/illustrations-pocketbudjet/pbj-debt-planner.svg",
        "/assets/screenshots/net-worth/net-worth.png",
        1,
    ),
    "videos/pocketbudjet/receipt-scanning/index.html": (
        "/assets/illustrations-pocketbudjet/pbj-receipt-scan.svg",
        "/assets/screenshots/receipt-scanning/receipt-scan.png",
        1,
    ),
    "videos/pocketbudjet/reports/index.html": (
        "/assets/illustrations-pocketbudjet/pbj-settings-export.svg",
        "/assets/screenshots/reports/reports.png",
        1,
    ),
}
for rel, (old, new, n) in updates.items():
    p = root / rel
    text = p.read_text(encoding="utf-8")
    if new in text:
        print("skip", rel)
        continue
    text = text.replace(old, new, n)
    p.write_text(text, encoding="utf-8")
    print("wired", rel)

p = root / "videos/pocketbudjet/debt-freedom/index.html"
text = p.read_text(encoding="utf-8")
needle = "/assets/screenshots/debt-freedom/what-if.png"
if needle not in text:
    text = text.replace(
        'src="/assets/illustrations-pocketbudjet/pbj-debt-planner.svg" alt="What-If scenarios"',
        f'src="{needle}" alt="What-If scenarios"',
        1,
    )
    p.write_text(text, encoding="utf-8")
    print("wired debt-freedom what-if")
