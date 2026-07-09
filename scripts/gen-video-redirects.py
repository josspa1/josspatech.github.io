#!/usr/bin/env python3
"""Generate meta-refresh redirect stubs for removed PocketBudJet feature videos."""
from __future__ import annotations

from pathlib import Path

ROOTS = [
    Path("C:/Users/jossp/Documents/MobileApps/WebSite/HostedFiles"),
    Path("C:/Users/jossp/Documents/GitHub/josspatech.github.io"),
]

# slug -> redirect target (path on josspatech.com)
REDIRECTS: dict[str, str] = {
    "videos/import": "/videos/user-guide/#chapter=54",
    "videos/quick-start": "/getting-started/",
    "gary-demo": "/#intro-tour",
    "videos/user-guide-hhh": "/how-to/",
    "videos/pocketbudjet/share-statements": "/videos/user-guide/#chapter=54",
    "videos/pocketbudjet/digital-receipt-import": "/videos/user-guide/#chapter=54",
    "videos/pocketbudjet/connect-bank": "/videos/user-guide/#chapter=98",
    "videos/pocketbudjet/budget-setup": "/videos/user-guide/#chapter=33",
    "videos/pocketbudjet/adding-transactions": "/videos/user-guide/#chapter=48",
    "videos/pocketbudjet/debt-freedom": "/videos/user-guide/#chapter=74",
    "videos/pocketbudjet/ai-coach": "/videos/user-guide/#chapter=44",
    "videos/pocketbudjet/receipt-scanning": "/videos/user-guide/#chapter=62",
    "videos/pocketbudjet/bills-recurring": "/videos/user-guide/#chapter=67",
    "videos/pocketbudjet/reports": "/videos/user-guide/#chapter=78",
    "videos/pocketbudjet/net-worth": "/videos/user-guide/#chapter=84",
    "videos/pocketbudjet/export-sharing": "/videos/user-guide/#chapter=86",
    "videos/pocketbudjet/retirement-planning": "/videos/user-guide/#chapter=106",
    "videos/pocketbudjet/voice-shortcuts": "/videos/user-guide/#chapter=104",
    "videos/pocketbudjet/search": "/videos/user-guide/#chapter=113",
    "videos/pocketbudjet/household-sync": "/videos/user-guide/#chapter=111",
    "videos/pocketbudjet/mindful-features": "/videos/user-guide/#chapter=108",
    "videos/pocketbudjet/pc-dashboard": "/videos/user-guide/#chapter=110",
    "videos/pocketbudjet/data-management": "/videos/user-guide/#chapter=96",
    "videos/pocketbudjet/transaction-rules": "/videos/user-guide/#chapter=101",
    "videos/pocketbudjet/savings-goals": "/videos/user-guide/#chapter=39",
    "videos/pocketbudjet/cloud-backup-setup": "/videos/user-guide/#chapter=95",
    "videos/pocketbudjet/privacy-pitch": "/videos/user-guide/#chapter=117",
    "videos/pocketbudjet/privacy-security": "/videos/user-guide/#chapter=117",
    "videos/pocketbudjet/why-it-is-different": "/videos/pocketbudjet/partner-showcase/",
    "videos/pocketbudjet/app-overview": "/videos/pocketbudjet/partner-showcase/",
    "videos/pocketbudjet/calendar-view": "/videos/user-guide/#chapter=27",
}


def html_for(target: str, title: str) -> str:
    safe = target.replace('"', "&quot;")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="0; url={safe}">
  <link rel="canonical" href="{safe}">
  <title>{title}</title>
  <script>location.replace("{safe}");</script>
</head>
<body style="font-family:system-ui,sans-serif;padding:2rem;text-align:center;color:#1A4F7A;">
  <p>This guide moved to the <a href="{safe}">PocketBudJet user manual</a>.</p>
</body>
</html>
"""


def main() -> None:
    for root in ROOTS:
        if not root.is_dir():
            continue
        for rel, target in REDIRECTS.items():
            out = root / rel / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            title = f"Redirect — {rel.split('/')[-1].replace('-', ' ').title()}"
            out.write_text(html_for(target, title), encoding="utf-8")
            print(out)
    print(f"Done — {len(REDIRECTS)} redirects × {sum(1 for r in ROOTS if r.is_dir())} roots")


if __name__ == "__main__":
    main()
