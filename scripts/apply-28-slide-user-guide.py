#!/usr/bin/env python3
"""DEPRECATED (Jul 2026 terminology): do not run.

Canonical product term is User Manual (not User Guide). Walkthrough =
partner-showcase overview only. This one-shot script would reverse live
branding back to "User Guide". Kept for history only.
"""
import sys
print("DEPRECATED: refuse to run — would reverse User Manual branding.", file=sys.stderr)
raise SystemExit(2)

# --- original script below (unreachable) ---
#!/usr/bin/env python3
"""Apply 28-slide user guide fixes to index.html from c34921c baseline."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "videos" / "user-guide" / "index.html"

raw = subprocess.check_output(
    ["git", "show", "c34921c:videos/user-guide/index.html"],
    cwd=ROOT,
    text=True,
    encoding="utf-8",
)

replacements = [
    (
        " <title>PocketBudJet User Guide | JosspaTech</title>",
        ' <title>PocketBudJet Detailed User Guide | JosspaTech</title>\n'
        ' <meta name="description" content="Full detailed user guide for PocketBudJet — 28 chapters with synced narration, gold tap pointers, and real app screenshots.">',
    ),
    (
        "Watch the full walkthrough — every screen, every feature, every setting.",
        "Full detailed user guide — every screen, every feature, every setting across 28 chapters.",
    ),
    (
        "<h2>Interactive Tour</h2>",
        "<h2>Interactive User Guide</h2>",
    ),
    (
        "The opening slides walk through the setup wizard screen by screen.",
        "The opening chapters cover the setup wizard screen by screen.",
    ),
    (
        'src="/assets/screenshots/budget-setup/step-7-dashboard.png" alt="Your dashboard"',
        'src="/assets/screenshots/dashboard.png" alt="Your dashboard"',
    ),
    (
        'src="/assets/screenshots/pbj/02-import-center.png" alt="Importing"',
        'src="/assets/screenshots/import.png" alt="Importing"',
    ),
    (
        'data-index="9" data-tap-none>\n <img src="/assets/screenshots/receipt-scanning/receipt-scan.png"',
        'data-index="9" data-tap-x="50" data-tap-y="22" data-tap-label="Receipt Scanner">\n <img src="/assets/screenshots/receipt-scanning/receipt-scan.png"',
    ),
    (
        'src="/assets/screenshots/pbj/03-budget-envelopes.png" alt="Budgets"',
        'src="/assets/screenshots/budget.png" alt="Budgets"',
    ),
    (
        ' <div class="slide" data-index="14">\n <img src="/assets/illustrations-pocketbudjet/pbj-debt-planner.svg" alt="Investments" loading="lazy">\n </div>\n <div class="slide" data-index="15">\n <img src="/assets/illustrations-pocketbudjet/pbj-settings-export.svg" alt="Reports" loading="lazy">\n </div>\n <div class="slide" data-index="16" data-tap-none>\n <img src="/assets/screenshots/pbj/05-ai-coach.png" alt="AI Coach" loading="lazy">\n </div>\n <div class="slide" data-index="17" data-tap-x="85" data-tap-y="24" data-tap-label="Ask">\n <img src="/assets/screenshots/pbj/05-ai-coach.png" alt="AI Assistant" loading="lazy">\n </div>\n <div class="slide" data-index="18" data-tap-none>\n <img src="/assets/screenshots/pbj/01-home-dashboard.png" alt="Search" loading="lazy">\n </div>\n <div class="slide" data-index="19" data-tap-none>\n <img src="/assets/screenshots/privacy.png" alt="Export" loading="lazy">\n </div>\n <div class="slide" data-index="20" data-tap-none>\n <img src="/assets/screenshots/pbj/07-web-companion.png" alt="PC Dashboard" loading="lazy">\n </div>\n <div class="slide" data-index="21" data-tap-x="50" data-tap-y="73" data-tap-label="Household sync">\n <img src="/assets/screenshots/pbj/06-goals-languages.png" alt="Household Sync" loading="lazy">\n </div>\n <div class="slide" data-index="22" data-tap-x="50" data-tap-y="36" data-tap-label="Transaction">\n <img src="/assets/screenshots/transactions.png" alt="Rules" loading="lazy">\n </div>\n <div class="slide" data-index="23" data-tap-x="91" data-tap-y="8" data-tap-label="Settings">\n <img src="/assets/screenshots/budget-setup/step-7-dashboard.png" alt="Accessibility" loading="lazy">\n </div>\n <div class="slide" data-index="24" data-tap-none>\n <img src="/assets/screenshots/pbj/06-goals-languages.png" alt="Mindful Features" loading="lazy">\n </div>\n <div class="slide" data-index="25" data-tap-none>\n <img src="/assets/screenshots/budget-setup/step-7-dashboard.png" alt="Pricing" loading="lazy">\n </div>\n <div class="slide" data-index="26" data-tap-none>\n <img src="/assets/screenshots/privacy.png" alt="Privacy &amp; Security" loading="lazy">\n </div>\n <div class="slide" data-index="27" data-tap-none>\n <img src="/assets/screenshots/budget-setup/step-7-dashboard.png" alt="Help" loading="lazy">\n </div>',
        ' <div class="slide" data-index="14" data-tap-x="50" data-tap-y="45" data-tap-label="Net worth">\n <img src="/assets/screenshots/net-worth/net-worth.png" alt="Investments &amp; net worth" loading="lazy">\n </div>\n <div class="slide" data-index="15" data-tap-x="50" data-tap-y="40" data-tap-label="Reports">\n <img src="/assets/screenshots/reports/reports.png" alt="Reports" loading="lazy">\n </div>\n <div class="slide" data-index="16" data-tap-none>\n <img src="/assets/screenshots/ai-coach.png" alt="AI Coach" loading="lazy">\n </div>\n <div class="slide" data-index="17" data-tap-x="85" data-tap-y="24" data-tap-label="Ask">\n <img src="/assets/screenshots/ai-coach.png" alt="AI Assistant" loading="lazy">\n </div>\n <div class="slide" data-index="18" data-tap-none>\n <img src="/assets/screenshots/dashboard.png" alt="Search" loading="lazy">\n </div>\n <div class="slide" data-index="19" data-tap-x="50" data-tap-y="55" data-tap-label="Export">\n <img src="/assets/screenshots/import/step-9-settings-export.png" alt="Export" loading="lazy">\n </div>\n <div class="slide" data-index="20" data-tap-none>\n <img src="/assets/screenshots/pbj/07-web-companion.png" alt="PC Dashboard" loading="lazy">\n </div>\n <div class="slide" data-index="21" data-tap-x="50" data-tap-y="73" data-tap-label="Household sync">\n <img src="/assets/screenshots/household-sync/household-sync.png" alt="Household Sync" loading="lazy">\n </div>\n <div class="slide" data-index="22" data-tap-x="50" data-tap-y="36" data-tap-label="Transaction">\n <img src="/assets/screenshots/transactions.png" alt="Rules" loading="lazy">\n </div>\n <div class="slide" data-index="23" data-tap-x="91" data-tap-y="8" data-tap-label="Settings">\n <img src="/assets/screenshots/dashboard.png" alt="Accessibility" loading="lazy">\n </div>\n <div class="slide" data-index="24" data-tap-none>\n <img src="/assets/screenshots/pbj/06-goals-languages.png" alt="Mindful Features" loading="lazy">\n </div>\n <div class="slide" data-index="25" data-tap-none>\n <img src="/assets/screenshots/dashboard.png" alt="Pricing" loading="lazy">\n </div>\n <div class="slide" data-index="26" data-tap-none>\n <img src="/assets/screenshots/privacy.png" alt="Privacy &amp; Security" loading="lazy">\n </div>\n <div class="slide" data-index="27" data-tap-none>\n <img src="/assets/screenshots/import/step-10-home-dashboard.png" alt="Help" loading="lazy">\n </div>',
    ),
    ('aria-label="Pause walkthrough"', 'aria-label="Pause user guide"'),
    (
        "start with the complete user guide walkthrough built right into the app.",
        "start with the full detailed user guide built right into the app.",
    ),
]

for old, new in replacements:
    if old not in raw:
        print(f"MISSING: {old[:60]}...", file=sys.stderr)
        sys.exit(1)
    raw = raw.replace(old, new, 1)

if raw.count('data-index=') != 28:
    print(f"Expected 28 slides, got {raw.count('data-index=')}", file=sys.stderr)
    sys.exit(1)

HTML.write_text(raw, encoding="utf-8", newline="\n")
print("Wrote 28-slide user guide index.html")
