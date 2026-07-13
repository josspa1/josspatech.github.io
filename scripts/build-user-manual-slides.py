#!/usr/bin/env python3
"""Build PocketBudJet User Manual index.html from SLIDES + CHAPTER_PILLS data."""
from __future__ import annotations

import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "videos" / "user-guide" / "index.html"
NARRATION_JSON = ROOT / "videos" / "user-guide" / "narration-en.json"
COVERAGE_MD = ROOT / "docs" / "USER_MANUAL_COVERAGE.md"
PBJ_COVERAGE = Path(r"C:\PBJ\docs\USER_MANUAL_COVERAGE.md")

# Verified OK device captures
HOME = "/assets/screenshots/import/step-10-home-dashboard.png"
IMPORT_CENTER = "/assets/screenshots/import/step-4-import-center.png"
CONFIRM_IMPORT = "/assets/screenshots/import/step-5-confirm-import.png"
COACH = "/assets/screenshots/pbj/05-ai-coach.png"
BUDGET_ENV = "/assets/screenshots/pbj/03-budget-envelopes.png"
GOALS = "/assets/screenshots/pbj/06-goals-languages.png"
MINDFUL = "/assets/screenshots/pbj/04-shopping-intelligence.png"
WEB = "/assets/screenshots/pbj/07-web-companion.png"
RECEIPT = "/assets/screenshots/receipt-scanning/receipt-scan.png"
SCANNER = "/assets/screenshots/scanner.png"
HOUSEHOLD = "/assets/screenshots/household-sync/household-sync.png"
MANUAL = "/assets/screenshots/pbj/manual/"
SUB_INTRO = "/assets/screenshots/cold-start/subscription-intro.png"
NOTIF_OPTIN = f"{MANUAL}notification-opt-in.png"
ACTIVITY_FILTERS = f"{MANUAL}activity-filters.png"
BANK_SYNC = "/assets/screenshots/bank-sync.png"
EXPORT_HUB = "/assets/screenshots/export/export-hub.png"
TAX_CENTER = "/assets/screenshots/tax/tax-center.png"
PRIVACY = "/assets/screenshots/settings/privacy-backup.png"
PAY_STUB = f"{MANUAL}pay-stub-review.png"
DIRECT_DEP = f"{MANUAL}direct-deposit-advisor.png"
WIDGETS = f"{MANUAL}widgets-watch.png"
FALLBACK = f"{MANUAL}fallback-screen.png"

# (chapter, feature, narration, img|None, png_status, alt, tap|None)
# png_status: OK | interim | missing
# tap: (x, y, label) or None

def S(chapter, feature, narration, img=None, png_status="missing", alt="", tap=None):
    return {
        "chapter": chapter,
        "feature": feature,
        "narration": narration,
        "img": img,
        "png_status": png_status if img else "missing",
        "alt": alt or feature,
        "tap": tap,
    }


SLIDES: list[dict] = [
    # ── Cold Start (0–9) ──
    S("Cold Start", "Splash", "Open PocketBudJet after install. The splash screen appears while the app loads your local database.",
      "/assets/screenshots/cold-start/splash.png", "OK", "Splash screen on cold launch"),
    S("Cold Start", "Showcase 1", "Swipe the feature showcase. Slide one: control your money with envelopes, bills, and goals on your phone. Tap Next.",
      "/assets/screenshots/cold-start/showcase-1.png", "OK", "Feature showcase slide 1", (50, 88, "Next")),
    S("Cold Start", "Showcase 2", "Slide two: your AI financial coach learns your patterns and flags unusual spending. Tap Next.",
      "/assets/screenshots/cold-start/showcase-2.png", "OK", "Feature showcase slide 2 — AI coach", (50, 88, "Next")),
    S("Cold Start", "Showcase 3", "Slide three: crush your debt — watch loan progress and your debt-free date on the Quick Tour. Tap Next.",
      "/assets/screenshots/cold-start/showcase-3.png", "OK", "Feature showcase slide 3 — debt tools", (50, 88, "Next")),
    S("Cold Start", "Showcase 4", "Slide four: your data stays on your device — privacy first. Tap Get Started.",
      "/assets/screenshots/cold-start/showcase-4.png", "OK", "Feature showcase slide 4 — privacy", (50, 88, "Get Started")),
    S("Cold Start", "Terms of Service", "On first launch, open the Terms of Service tab and scroll to the bottom.",
      "/assets/screenshots/cold-start/terms-tos.png", "OK", "Terms — Terms of Service tab"),
    S("Cold Start", "Disclaimer tab", "Tap Disclaimer and scroll that tab to the bottom too.",
      "/assets/screenshots/cold-start/terms-tab.png", "OK", "Terms — Disclaimer tab", (72, 18, "Disclaimer")),
    S("Cold Start", "Accept terms", "When both tabs are reviewed, tap I Accept — Continue.",
      "/assets/screenshots/cold-start/terms-accept.png", "OK", "Terms — I Accept enabled", (50, 92, "Accept")),
    S("Cold Start", "Security setup", "On Secure Your Data, toggle app lock if you want PIN or biometrics, then tap Continue to Home.",
      "/assets/screenshots/cold-start/security-setup.png", "OK", "Secure Your Data", (50, 90, "Continue")),
    S("Cold Start", "First Home", "You land on Home. Income, spending, and net cards sit at the top with widgets below.",
      HOME, "OK", "Home after first launch"),
    # ── Wayfinding (10–14) ──
    S("Wayfinding", "Tab bar", "The wayfinding tour opens on first launch. Landmark one: the tab bar — Home, Activity, Budget, Goals, and Coach. Tap Next.",
      "/assets/screenshots/wayfinding/wayfinding-tab-bar.png", "OK", "Wayfinding — tab bar", (50, 94, "Tab bar")),
    S("Wayfinding", "Header", "Landmark two: the header — Universal Search and the Coach button on every screen. Tap Next.",
      "/assets/screenshots/wayfinding/wayfinding-header.png", "OK", "Wayfinding — header search and Coach", (82, 7, "Search & Coach")),
    S("Wayfinding", "Drawer", "Landmark three: the drawer — swipe from the left for Settings, Help, and the full nav map. Tap Next.",
      "/assets/screenshots/wayfinding/wayfinding-drawer.png", "OK", "Navigation drawer", (12, 24, "Open menu")),
    S("Wayfinding", "Toolbox", "Landmark four: the Toolbox — import, export, scanners, and utilities in one place. Tap Next.",
      IMPORT_CENTER, "OK", "Toolbox / Import Center", (72, 7, "Toolbox")),
    S("Wayfinding", "Quick-add", "Landmark five: the quick-add button logs a transaction, category, or goal depending on your tab. Tap Done to finish the tour.",
      "/assets/screenshots/wayfinding/wayfinding-quick-add.png", "OK", "Wayfinding — quick-add FAB", (88, 78, "Quick-add")),
    # ── Trial (15) ──
    S("Trial", "Subscription intro", "On your second app open — or after five transactions — you may see Choose Your Plan. Start the 21-day Premium trial with no card, or continue free.",
      SUB_INTRO, "OK", "Choose Your Plan — subscription intro", (50, 90, "Continue")),
    # ── Notifications (16) ──
    S("Notifications", "Notification opt-in", "After onboarding, PocketBudJet may ask to send bill reminders and spending alerts. Allow notifications to stay ahead of due dates.",
      NOTIF_OPTIN, "OK", "Notification opt-in screen"),
    # ── Wizard (17–26) ──
    S("Wizard", "Launch wizard", "Setup is optional and not shown by default. Tap the gear icon, open Settings, then tap Set Up PocketBudJet to launch the wizard any time.",
      "/assets/screenshots/import/step-9-settings-export.png", "interim", "Settings — open Setup Wizard", (91, 8, "Settings")),
    S("Wizard", "Name", "Wizard step one: enter your display name and tap Next.",
      "/assets/screenshots/budget-setup/step-1-name.png", "OK", "Wizard step 1 — display name", (50, 38, "Name")),
    S("Wizard", "Currency", "Wizard step two: choose your home currency and tap Next.",
      "/assets/screenshots/cold-start/wizard-currency.png", "OK", "Wizard step 2 — home currency", (50, 42, "Currency")),
    S("Wizard", "Accounts", "Wizard step three: add checking, savings, credit, or cash accounts — or tap Skip.",
      "/assets/screenshots/budget-setup/step-5-accounts.png", "OK", "Wizard step 3 — accounts", (50, 55, "Add account")),
    S("Wizard", "Income", "Wizard step four: enter gross pay and take-home pay. The difference becomes paycheck deductions you can itemize later.",
      "/assets/screenshots/budget-setup/step-2-income.png", "OK", "Wizard step 4 — income", (50, 42, "Income")),
    S("Wizard", "Bills", "Wizard step five: add recurring bills with name, amount, and due day — or tap Skip.",
      "/assets/screenshots/cold-start/wizard-bills.png", "OK", "Wizard step 5 — recurring bills", (50, 50, "Add bill")),
    S("Wizard", "Goals", "Wizard step six: pick your main financial goal to personalize the dashboard.",
      GOALS, "interim", "Wizard step 6 — main goal", (50, 48, "Goal")),
    S("Wizard", "Style", "Wizard step seven: choose a budgeting style — 50/30/20, Envelope, Zero-Based, or another template.",
      "/assets/screenshots/budget-setup/step-3-templates.png", "OK", "Wizard step 7 — budgeting style", (50, 55, "Style")),
    S("Wizard", "Accessibility", "Wizard step eight: answer the colorblind-accessibility question so charts use friendly palettes.",
      "/assets/screenshots/cold-start/wizard-accessibility.png", "OK", "Wizard step 8 — accessibility", (50, 55, "Continue")),
    S("Wizard", "Done", "Wizard step nine: review your personalized summary, then tap Finish. Your dashboard is configured.",
      "/assets/screenshots/budget-setup/step-7-dashboard.png", "OK", "Wizard step 9 — personalized reveal"),
    # ── Home (27) ──
    S("Home", "Dashboard", "On Home, scan hero cards for income, spending, and net worth. Widgets below show spending pace, bills due, and goal progress.",
      HOME, "OK", "Home dashboard overview"),
    # ── Activity (28–32) ──
    S("Activity", "Open Activity", "Tap the Activity tab — wallet icon at bottom left — to see every transaction.",
      "/assets/screenshots/activity/activity-tab.png", "OK", "Tap Activity tab", (12, 94, "Activity")),
    S("Activity", "Transaction list", "Activity lists income and expenses grouped by date. Use search and filters to narrow by merchant, category, or amount.",
      "/assets/screenshots/activity/activity-transaction-list.png", "OK", "Activity — transaction list"),
    S("Activity", "Filters", "Tap the filter icon to stack date, category, and account filters. Running balances update per account as you scroll.",
      ACTIVITY_FILTERS, "OK", "Activity — filters and running balances"),
    S("Activity", "Transaction detail", "Tap any row to open Transaction Detail — edit category, split, add notes, or attach a receipt.",
      "/assets/screenshots/activity/activity-transaction-detail.png", "OK", "Transaction detail screen"),
    S("Activity", "Approve imports", "When imports add uncertain rows, open Approve Transactions to accept or fix them before they hit your budget.",
      CONFIRM_IMPORT, "interim", "Approve Transactions screen"),
    # ── Budget (33–38) ──
    S("Budget", "Open Budget", "Tap the Budget tab — calendar icon — for envelope limits and monthly progress.",
      HOME, "interim", "Tap Budget tab", (38, 94, "Budget")),
    S("Budget", "Envelopes", "Budget shows category envelopes with color-coded progress bars and rollover amounts.",
      BUDGET_ENV, "OK", "Budget envelopes"),
    S("Budget", "Edit category", "Tap any category row to rename it or change the monthly limit.",
      "/assets/screenshots/budget-setup/step-4-categories.png", "OK", "Edit category limit", (50, 50, "Category")),
    S("Budget", "Templates", "Tap Change Template to switch frameworks like 50/30/20, Envelope, or Zero-Based.",
      "/assets/screenshots/budget-setup/step-3-templates.png", "OK", "Change budget template", (50, 55, "Template")),
    S("Budget", "Category manager", "Open Category Manager from Settings or Budget to add, merge, or hide categories and sub-categories.",
      "/assets/screenshots/budget/category-manager.png", "OK", "Category Manager"),
    S("Budget", "Spending plan", "Spending Plan shows how much is left per envelope after bills and goals — your safe-to-spend number.",
      "/assets/screenshots/budget/spending-plan.png", "OK", "Spending Plan screen"),
    # ── Goals (39–43) ──
    S("Goals", "Open Goals", "Tap the Goals tab — trending-up icon — for savings targets and sinking funds.",
      HOME, "interim", "Tap Goals tab", (62, 94, "Goals")),
    S("Goals", "Overview", "Goals tracks targets with progress rings, wishlist cool-offs, and sinking funds for irregular expenses.",
      GOALS, "interim", "Savings goals overview"),
    S("Goals", "New goal", "Tap the plus button. Enter a name, target amount, and date. PocketBudJet calculates your monthly contribution.",
      GOALS, "interim", "Create a savings goal", (50, 35, "New goal")),
    S("Goals", "Sinking funds", "Add sinking funds for annual expenses like insurance. Use the wishlist to cool off on impulse buys before committing.",
      GOALS, "interim", "Sinking funds and wishlist", (50, 55, "Sinking fund")),
    S("Goals", "Purchase wishlist", "Purchase Wishlist lets you queue wants with a cooling-off timer before money leaves your account.",
      "/assets/screenshots/goals/purchase-wishlist.png", "OK", "Purchase Wishlist"),
    # ── Coach (44–47) ──
    S("Coach", "Open Coach", "Tap the Coach tab — sparkles icon — for insights, reports, and AI chat.",
      HOME, "interim", "Tap Coach tab", (88, 94, "Coach")),
    S("Coach", "Today", "Coach's Today segment highlights anomalies, bill reminders, and nudges based on your data.",
      COACH, "OK", "Coach Today segment"),
    S("Coach", "Ask PBJ", "Tap Ask to chat in plain English — try \"How much did I spend on dining last month?\"",
      COACH, "OK", "Ask the Coach", (85, 24, "Ask")),
    S("Coach", "Weekly recap", "Weekly Recap summarizes income, spending, and wins — open it from Coach or your notification.",
      "/assets/screenshots/coach/weekly-recap.png", "OK", "Weekly Recap"),
    # ── Transactions (48–53) ──
    S("Transactions", "Manual entry intro", "To log spending manually, open Activity or tap the gold plus button from any screen.",
      HOME, "interim", "Activity list for manual entry"),
    S("Transactions", "Gold plus", "Tap the gold plus button at bottom center. You can finish in under ten seconds.",
      "/assets/screenshots/wayfinding/wayfinding-quick-add.png", "interim", "Tap gold plus button", (85, 82, "Gold +")),
    S("Transactions", "Amount", "Enter the amount first while it is fresh. Amount is the one field you must not forget.",
      "/assets/screenshots/budget-setup/step-6-scan.png", "interim", "Enter amount first", (50, 30, "Amount")),
    S("Transactions", "Category", "Type the merchant name consistently. Pick a category — PocketBudJet learns and suggests over time. Select the account.",
      "/assets/screenshots/budget-setup/step-6-scan.png", "interim", "Pick category and account", (50, 50, "Category")),
    S("Transactions", "Split", "For multi-category receipts, tap Split. Assign portions to Groceries, Household, or other categories — total stays locked.",
      "/assets/screenshots/budget-setup/step-6-scan.png", "interim", "Split across categories", (50, 65, "Split")),
    S("Transactions", "Save", "Tap Save. Your budget category, account balance, and dashboard update immediately — no sync wait.",
      "/assets/screenshots/budget-setup/step-6-scan.png", "interim", "Save transaction", (50, 92, "Save")),
    # ── Import (54–61) ──
    S("Import", "Import Center", "Open the Toolbox or Import Center to bring in bank history without a bank login.",
      IMPORT_CENTER, "OK", "Import Center", (50, 28, "Import")),
    S("Import", "Share path", "Fastest path: in your bank app, open the statement and tap Share, then PocketBudJet. Six taps total — no Downloads folder.",
      IMPORT_CENTER, "OK", "Share from bank app", (50, 40, "Share")),
    S("Import", "Share sheet", "Tap the PocketBudJet icon on the share sheet. After the first pick, Android pins it near the top.",
      CONFIRM_IMPORT, "OK", "Share sheet to PocketBudJet", (50, 55, "PocketBudJet")),
    S("Import", "Browse files", "Or tap Import from file for CSV, OFX, QFX, QIF, XLSX, or PDF. Smart Mapper detects columns automatically.",
      IMPORT_CENTER, "OK", "Import from file", (50, 65, "Browse files")),
    S("Import", "Confirm draft", "Review the draft — green rows are confident; flagged rows need a quick look. Tap Confirm when ready.",
      CONFIRM_IMPORT, "OK", "Confirm import draft", (50, 91, "Confirm")),
    S("Import", "History depth", "Grab at least three months of history — six months or a year is better. More data means smarter AI and sharper reports.",
      IMPORT_CENTER, "OK", "Import at least three months", (50, 45, "Date range")),
    S("Import", "PDF receipts", "Premium: when a store emails a PDF receipt, download it to your phone and import — no inbox access required.",
      IMPORT_CENTER, "OK", "Digital PDF receipt import", (50, 72, "PDF")),
    S("Import", "Import history", "Import History lists every file you brought in — re-open drafts or audit what changed.",
      "/assets/screenshots/import/import-history.png", "OK", "Import History"),
    # ── Scan (62–66) ──
    S("Scan", "Receipt scan", "Tap Scan Receipt and snap a photo. OCR fills merchant, amount, and date.",
      RECEIPT, "OK", "Receipt scanner camera", (50, 22, "Scan")),
    S("Scan", "OCR save", "Review OCR fields, pick a category if needed, then tap Save. Line items parse when visible on the receipt.",
      "/assets/screenshots/budget-setup/step-6-scan.png", "interim", "OCR auto-fill on save", (50, 45, "Save")),
    S("Scan", "WiFi ADF", "For stacks of paper, tap WiFi ADF Scanner. Connect your home document feeder over the network.",
      SCANNER, "interim", "WiFi ADF batch scanner", (50, 48, "WiFi ADF")),
    S("Scan", "Batch complete", "Load bank statements or receipts and walk away — every page gets read, categorized, and added to Activity.",
      SCANNER, "interim", "Batch scan complete"),
    S("Scan", "Universal scan", "Universal Scan handles statements, invoices, and mixed documents — crop corners and review before import.",
      SCANNER, "interim", "Universal Document Scan"),
    # ── Bills (67–70) ──
    S("Bills", "Bills calendar", "Open Bills from the drawer or Plan tab. The calendar shows due dates with payday markers and a 30-day cash flow forecast.",
      "/assets/screenshots/bills/bills-calendar.png", "OK", "Bills calendar"),
    S("Bills", "Add or mark paid", "Tap Add Bill for subscriptions and recurring payments. Tap a due date to mark paid or snooze a reminder.",
      "/assets/screenshots/bills.png", "interim", "Add or mark bill paid", (50, 70, "Mark paid")),
    S("Bills", "Subscription tracker", "Subscription Tracker surfaces recurring charges you might have forgotten — cancel leaks before they compound.",
      "/assets/screenshots/bills/subscription-tracker.png", "OK", "Subscription Tracker"),
    S("Bills", "Recurring hub", "Recurring Transactions links bills and income on one timeline for cash-flow planning.",
      "/assets/screenshots/income/recurring-income.png", "interim", "Recurring Transactions hub"),
    # ── Income (71–73) ──
    S("Income", "Recurring income", "Recurring Income stores paychecks and side gigs so forecasts know when money arrives.",
      "/assets/screenshots/income/recurring-income.png", "OK", "Recurring Income"),
    S("Income", "Pay stub review", "Import or photograph a pay stub — Pay Stub Review splits gross, taxes, and deductions automatically.",
      PAY_STUB, "OK", "Pay Stub Review"),
    S("Income", "Direct deposit advisor", "Direct Deposit Advisor suggests how to split paychecks across accounts and envelopes.",
      DIRECT_DEP, "OK", "Direct Deposit Advisor"),
    # ── Debt (74–77) ──
    S("Debt", "Debt planner", "Open Debt from Goals or the drawer. Enter balances, APR, and minimum payments.",
      "/assets/screenshots/debt/debt-planner.png", "OK", "Debt payoff planner"),
    S("Debt", "Strategy", "Choose avalanche — highest interest first — or snowball — smallest balance first. See your debt-free date and interest saved.",
      "/assets/screenshots/debt/debt-strategy.png", "OK", "Avalanche vs snowball"),
    S("Debt", "Loan calculator", "Loan Calculator models extra payments, refi scenarios, and payoff timelines.",
      "/assets/screenshots/debt/loan-calculator.png", "OK", "Loan Calculator"),
    S("Debt", "Debt progress", "Debt Progress Report charts how fast balances are falling month over month.",
      "/assets/screenshots/debt/debt-progress.png", "OK", "Debt Progress Report"),
    # ── Reports (78–83) ──
    S("Reports", "Report hub", "In Coach, switch to Reports for spending by category, income vs expenses, and custom layouts.",
      "/assets/screenshots/reports/reports-hub.png", "OK", "Coach Reports segment", (50, 18, "Reports")),
    S("Reports", "Spending trends", "Tap Spending Trends to compare month over month. Spot seasonal spikes before they become habits.",
      "/assets/screenshots/reports/spending-trends.png", "OK", "Spending trends"),
    S("Reports", "Category breakdown", "Category Breakdown shows where money went. Export any report segment as CSV or PDF from the share icon.",
      "/assets/screenshots/reports/category-breakdown.png", "OK", "Category breakdown"),
    S("Reports", "Merchant analysis", "Merchant Analysis ranks stores by spend — great for cutting subscriptions and dining.",
      "/assets/screenshots/reports/merchant-analysis.png", "OK", "Merchant Analysis"),
    S("Reports", "Financial health", "Financial Health Score grades savings rate, debt load, and budget adherence in one number.",
      "/assets/screenshots/reports/financial-health-score.png", "OK", "Financial Health Score"),
    S("Reports", "Custom reports", "Report Builder lets you save custom filters — reuse them for monthly reviews.",
      "/assets/screenshots/reports/custom-report-builder.png", "OK", "Custom Report Builder"),
    # ── Net Worth (84–85) ──
    S("Net Worth", "Net worth hub", "Open Net Worth from the Toolbox or drawer. Track accounts, investments, property, and liabilities in one view.",
      "/assets/screenshots/net-worth/net-worth-hub.png", "OK", "Net worth tracker"),
    S("Net Worth", "Assets & investments", "My Assets and Investment Portfolio track property, brokerage, and retirement accounts alongside cash.",
      "/assets/screenshots/net-worth/investment-portfolio.png", "OK", "Investment Portfolio"),
    # ── Export (86–88) ──
    S("Export", "Export hub", "Tap the gear icon, then Import and Export. Back up encrypted files or export CSV, XLSX, OFX, PDF, and JSON.",
      "/assets/screenshots/export/export-hub.png", "OK", "Import and Export settings", (50, 35, "Export")),
    S("Export", "Formats", "Premium exports include CSV, JSON, PDF, Excel, Word, OFX, and HTML. Files land in your Export folder for 30 days.",
      EXPORT_HUB, "interim", "Choose export format", (50, 55, "Format")),
    S("Export", "Tax export", "Tax Filing Export bundles categories and mileage for your accountant or tax software.",
      TAX_CENTER, "interim", "Tax Filing Export"),
    # ── Tax (89–91) ──
    S("Tax", "Tax center", "Tax Center groups mileage logs, deduction breakdowns, and annual summaries in one place.",
      "/assets/screenshots/tax/tax-center.png", "OK", "Tax Center"),
    S("Tax", "Mileage log", "Mileage Log tracks business miles with IRS-ready totals — start trips from the Toolbox or a widget.",
      "/assets/screenshots/tax/mileage-log.png", "OK", "Mileage Log"),
    S("Tax", "Deduction breakdown", "Deduction Breakdown summarizes tax-prep categories pulled from your categorized transactions.",
      TAX_CENTER, "interim", "Deduction Breakdown"),
    # ── Settings (92–97) ──
    S("Settings", "Open Settings", "Tap the gear icon for accounts, privacy, backups, data retention, and the setup wizard.",
      "/assets/screenshots/settings/settings-open.png", "OK", "Open Settings", (91, 8, "Settings")),
    S("Settings", "Profile & accounts", "My Profile and Accounts manage display name, institutions, and account types.",
      "/assets/screenshots/settings/profile-accounts.png", "OK", "Profile and Accounts"),
    S("Settings", "Subscription", "Subscription shows trial days left, Premium features, and bank-sync add-ons.",
      SUB_INTRO, "interim", "Subscription management"),
    S("Settings", "Privacy & backup", "In Privacy and Backup, turn on encrypted cloud backup, set retention, and control app lock.",
      "/assets/screenshots/settings/privacy-backup.png", "OK", "Privacy and backup", (50, 40, "Backup")),
    S("Settings", "Data management", "Under Data Management, set how much history lives on-device, manage receipt image storage, and archive old years.",
      IMPORT_CENTER, "interim", "Data and storage management", (50, 50, "Storage")),
    S("Settings", "How PBJ learns", "How PBJ Learns explains crowd-consensus categorization — your data stays private on-device.",
      "/assets/screenshots/settings/how-pbj-learns.png", "OK", "How PBJ learns"),
    # ── Connect Bank (98–100) ──
    S("Connect Bank", "Requirements", "Bank sync connects US institutions only via Teller. Requires paid Premium — not included in the 21-day trial. Two banks included; each extra is $3.99 per month.",
      BANK_SYNC, "interim", "Connect Bank requirements"),
    S("Connect Bank", "Link bank", "In Settings, tap Connect Bank. Search for your US bank. PocketBudJet never stores your bank password — Teller handles sign-in.",
      BANK_SYNC, "interim", "Tap Connect Bank", (50, 45, "Connect Bank")),
    S("Connect Bank", "Select accounts", "Choose checking, savings, or credit accounts to link. New transactions sync automatically and honor your categorization rules.",
      BANK_SYNC, "interim", "Select linked accounts", (50, 70, "Confirm")),
    # ── Rules (101–103) ──
    S("Rules", "Transaction rules", "Open Activity, tap a transaction, then Transaction Rules. Automate categorization for repeat merchants.",
      "/assets/screenshots/rules/transaction-rules.png", "OK", "Transaction rules"),
    S("Rules", "Create rule", "Set a rule: when merchant contains \"Coffee Shop\", assign Dining. Rules auto-apply to future imports and manual entries.",
      "/assets/screenshots/rules/transaction-rules.png", "interim", "Create a rule"),
    S("Rules", "Bookmarks", "Flag unusual rows with Bookmarks. Filter Activity to bookmarks only when reconciling at month end.",
      "/assets/screenshots/rules/bookmarks.png", "OK", "Bookmarks for review"),
    # ── Voice (104–105) ──
    S("Voice", "Voice shortcuts", "Say \"Hey Siri, log $12 coffee in PocketBudJet\" or use Google Assistant shortcuts. Hands-free entry while driving or cooking.",
      COACH, "interim", "Add transaction by voice", (50, 50, "Voice")),
    S("Voice", "Voice queries", "Ask \"How much is left in Groceries?\" or \"What's my net worth?\" Voice works for budgets, balances, and Coach questions.",
      HOME, "interim", "Check budget by voice"),
    # ── Retirement (106–107) ──
    S("Retirement", "Retirement planner", "Open Retirement Planning from the Toolbox. Enter your target age, desired income, and current savings.",
      GOALS, "interim", "Retirement planning target", (50, 40, "Retirement")),
    S("Retirement", "Gap analysis", "See your projection and gap analysis — how much more to save each month to close the shortfall.",
      "/assets/screenshots/debt-freedom/what-if.png", "interim", "Retirement gap analysis", (50, 55, "Projection")),
    # ── Mindful (108–109) ──
    S("Mindful", "Mindful features", "In Settings, enable Mindful Features: spending pause, impulse check, cooling-off periods, and a mindful score before big purchases.",
      MINDFUL, "interim", "Mindful spending tools", (50, 50, "Mindful")),
    S("Mindful", "Shopping intelligence", "Shopping Intelligence compares prices, tracks UPC history, and flags impulse patterns at checkout.",
      MINDFUL, "interim", "Shopping Intelligence"),
    # ── Web (110) ──
    S("Web", "PC companion", "Launch PC Web Companion from Toolbox. Scan the QR code to pair over your LAN — drag-and-drop import on a full-size screen.",
      WEB, "OK", "PC Web Companion"),
    # ── Household (111–112) ──
    S("Household", "Household sync", "Under Household Sync, pair family devices with QR for joint budgets over WiFi or Bluetooth — no cloud account.",
      HOUSEHOLD, "OK", "Household sync QR pair", (50, 55, "Pair")),
    S("Household", "Couples dashboard", "Couples Dashboard merges shared envelopes and shows who spent what — still stored locally on each phone.",
      HOUSEHOLD, "interim", "Couples Dashboard"),
    # ── Search (113–114) ──
    S("Search", "Universal search", "Tap Universal Search in the header. Find transactions by merchant or amount — or search features like \"mileage\" or \"voice.\"",
      "/assets/screenshots/import/step-9-settings-export.png", "interim", "Universal Search", (72, 8, "Search")),
    S("Search", "Filter stack", "Stack filters: merchant contains \"Amazon\", category is Dining, date last 30 days. Export results directly from the screen.",
      HOME, "interim", "Combine search filters"),
    # ── Notifications capture (115) ──
    S("Notifications", "Notification capture", "Notification Capture reads bank alerts from your notification shade and drafts transactions — opt in from Settings.",
      PRIVACY, "interim", "Notification Capture"),
    # ── Widgets (116) ──
    S("Widgets", "Widgets & watch", "Widgets and Watch complications show safe-to-spend, bills due, and quick-add — configure slots from Settings.",
      WIDGETS, "OK", "Widgets & Watch"),
    # ── Privacy (117–118) ──
    S("Privacy", "App lock", "Set biometric or passcode lock in Privacy settings. Generate your recovery key once — store it safely offline.",
      PRIVACY, "interim", "App lock and recovery key", (50, 35, "App lock")),
    S("Privacy", "Cloud backup", "Connect Google Drive, OneDrive, Dropbox, or iCloud for encrypted backup. Your cloud, your account, your control.",
      PRIVACY, "interim", "Encrypted cloud backup", (50, 60, "Cloud")),
    # ── Help (119) ──
    S("Help", "Help & support", "Need help? Email support@josspatech.com or use in-app feedback. This manual at josspatech.com/videos/user-guide/ covers every feature.",
      "/assets/screenshots/help/help-support.png", "OK", "Help and support"),
]

# Chapter pills: (label, first slide index)
CHAPTER_PILLS: list[tuple[str, int]] = []
_seen: set[str] = set()
for i, slide in enumerate(SLIDES):
    ch = slide["chapter"]
    if ch not in _seen:
        _seen.add(ch)
        CHAPTER_PILLS.append((ch, i))

PLACEHOLDER_STYLE = (
    'width:100%;height:100%;display:flex;flex-direction:column;align-items:center;'
    'justify-content:center;background:#EDF2F7;color:#1A4F7A;padding:1.5rem;text-align:center;'
)
PLACEHOLDER_TITLE = (
    "font-family:'Playfair Display',serif;font-size:1rem;font-weight:700;margin-bottom:0.5rem;"
)
PLACEHOLDER_BODY = "font-size:0.82rem;line-height:1.5;color:#5A7A9A;"


def placeholder_html(title: str, note: str = "") -> str:
    loading = "lazy"
    return f'<img src="{FALLBACK}" alt="{title}" loading="{loading}">'


def slide_inner(slide: dict, idx: int) -> str:
    if slide["img"]:
        loading = "eager" if idx == 0 else "lazy"
        return f'<img src="{slide["img"]}" alt="{slide["alt"]}" loading="{loading}">'
    return placeholder_html(slide["alt"])


def tap_attrs(tap: tuple | None) -> str:
    if tap is None:
        return " data-tap-none"
    x, y, label = tap
    label = label.replace("&", "&amp;")
    return f' data-tap-x="{x}" data-tap-y="{y}" data-tap-label="{label}"'


def render_slides() -> str:
    lines: list[str] = []
    for i, slide in enumerate(SLIDES):
        cls = "slide active" if i == 0 else "slide"
        inner = slide_inner(slide, i)
        lines.append(f' <div class="{cls}" data-index="{i}"{tap_attrs(slide["tap"])}>')
        lines.append(f" {inner}")
        lines.append(" </div>")
    return "\n".join(lines)


def render_chapter_btns() -> str:
    lines: list[str] = []
    for j, (label, start) in enumerate(CHAPTER_PILLS):
        active = " active" if j == 0 else ""
        lines.append(f' <button class="chapter-btn{active}" data-slide="{start}">{label}</button>')
    return "\n".join(lines)


def js_string(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def render_narration_js() -> str:
    items = ",\n ".join(js_string(s["narration"]) for s in SLIDES)
    return f"const NARRATION = [\n {items}\n\n ];"


def patch_tap_pulse_js(html: str) -> str:
    """Wire scheduleTapPulse / clearTapPulse on play (HHH deck.js parity)."""
    if "scheduleTapPulse(current)" in html:
        return html

    html = html.replace(
        " function goTo(index) {\n slides[current].classList.remove('active');",
        " function goTo(index) {\n if (window.PBJWalkthrough && window.PBJWalkthrough.clearTapPulse) {\n"
        " window.PBJWalkthrough.clearTapPulse();\n }\n slides[current].classList.remove('active');",
    )
    html = html.replace(
        " else { startSentenceSync(current, SLIDE_DURATION); }\n }",
        " else { startSentenceSync(current, SLIDE_DURATION); }\n"
        " if (playing && window.PBJWalkthrough && window.PBJWalkthrough.scheduleTapPulse) {\n"
        " window.PBJWalkthrough.scheduleTapPulse(current);\n }\n }",
        1,
    )
    html = html.replace(
        " stopAudio(); clearInterval(timer);\n }\n });",
        " stopAudio(); clearInterval(timer);\n"
        " if (window.PBJWalkthrough && window.PBJWalkthrough.clearTapPulse) {\n"
        " window.PBJWalkthrough.clearTapPulse();\n }\n }\n });",
        1,
    )
    html = html.replace(
        " playing = true; playPauseBtn.innerHTML = '&#10074;&#10074;'; speedLabel.textContent = 'Auto-playing';\n playSlideAudio(current);",
        " playing = true; playPauseBtn.innerHTML = '&#10074;&#10074;'; speedLabel.textContent = 'Auto-playing';\n"
        " playSlideAudio(current);\n"
        " if (window.PBJWalkthrough && window.PBJWalkthrough.scheduleTapPulse) {\n"
        " window.PBJWalkthrough.scheduleTapPulse(current);\n }",
        1,
    )
    html = html.replace(
        " if (voiceEnabled) playSlideAudio(current); else resetTimer();\n } else {",
        " if (voiceEnabled) playSlideAudio(current); else resetTimer();\n"
        " if (window.PBJWalkthrough && window.PBJWalkthrough.scheduleTapPulse) {\n"
        " window.PBJWalkthrough.scheduleTapPulse(current);\n }\n } else {",
        1,
    )
    if '<script src="deck.js" defer></script>' not in html:
        html = html.replace(
            '<script src="/videos/shared/walkthrough.js" defer></script>',
            '<script src="/videos/shared/walkthrough.js" defer></script>\n<script src="deck.js" defer></script>',
        )
    return html


def patch_index(html: str) -> str:
    n = len(SLIDES)
    last = n - 1
    starts = [str(start) for _, start in CHAPTER_PILLS]

    html = re.sub(
        r'<div class="slideshow" id="slideshow">.*?</div>\s*</div>\s*</div>\s*</div>\s*<div class="progress-dots"',
        lambda m: (
            '<div class="slideshow" id="slideshow">\n'
            ' <div class="tap-to-start" id="tapToStart">\n'
            ' <div class="tap-to-start-icon">&#9654;</div>\n'
            ' <div class="tap-to-start-label">Tap to play</div>\n'
            " </div>\n"
            + render_slides()
            + "\n </div>\n </div>\n </div>\n </div>\n <div class=\"progress-dots\""
        ),
        html,
        count=1,
        flags=re.S,
    )

    html = re.sub(
        r'<div class="chapter-nav" id="chapterNav">[\s\S]*?</div>\s*\n\s*</div>\s*\n\s*<div class="narration-panel"',
        f'<div class="chapter-nav" id="chapterNav">\n{render_chapter_btns()}\n\n</div>\n </div>\n\n <div class="narration-panel"',
        html,
        count=1,
    )

    html = re.sub(
        r"const LAST_SLIDE = previewMode \? 26 : \d+;",
        f"const LAST_SLIDE = previewMode ? 26 : {last};",
        html,
    )
    html = re.sub(
        r"const CHAPTER_STARTS = \[.*?\];",
        f"const CHAPTER_STARTS = [{', '.join(starts)}];",
        html,
        flags=re.S,
    )
    html = re.sub(
        r"const NARRATION = \[.*?\n \];",
        render_narration_js(),
        html,
        flags=re.S,
    )

    html = re.sub(
        r"<p class=\"section-sub\">.*?</p>",
        f"<p class=\"section-sub\">{n} slides with synced narration and gold tap guides — cold launch through every major feature. "
        f"Use the {len(CHAPTER_PILLS)} chapter pills to jump, or read along in the scrolling transcript beside the phone.</p>",
        html,
        count=1,
    )
    html = patch_tap_pulse_js(html)
    return html


def write_coverage() -> None:
    lines = [
        "# PocketBudJet User Manual — Coverage Inventory",
        "",
        f"**Generated:** build-user-manual-slides.py  ",
        f"**Live URL:** https://josspatech.github.io/videos/user-guide/  ",
        f"**Slide count:** {len(SLIDES)} (indices 0–{len(SLIDES) - 1})  ",
        f"**Chapter pills:** {len(CHAPTER_PILLS)}  ",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|------:|",
    ]
    ok = sum(1 for s in SLIDES if s["png_status"] == "OK")
    interim = sum(1 for s in SLIDES if s["png_status"] == "interim")
    missing = sum(1 for s in SLIDES if s["png_status"] == "missing" or not s["img"])
    lines += [
        f"| Slides with voice + narration | {len(SLIDES)} |",
        f"| PNG OK | {ok} |",
        f"| PNG interim (reuse / mockup) | {interim} |",
        f"| PNG missing (placeholder) | {missing} |",
        "",
        "## Slide inventory",
        "",
        "| Slide | Chapter | Feature | Voice | PNG | Feature covered |",
        "|------:|---------|---------|:-----:|:---:|:---------------:|",
    ]
    for i, s in enumerate(SLIDES):
        png = s["png_status"] if s["img"] else "missing"
        lines.append(
            f"| {i} | {s['chapter']} | {s['feature']} | Y | {png} | Y |"
        )

    lines += [
        "",
        "## Features needing device screenshots (Priority order)",
        "",
    ]
    seen_feat: set[str] = set()
    for s in SLIDES:
        if s["img"] and s["png_status"] == "OK":
            continue
        key = f"{s['chapter']} — {s['feature']}"
        if key in seen_feat:
            continue
        seen_feat.add(key)
        status = "interim reuse" if s["img"] else "no PNG"
        lines.append(f"- **{key}** ({status})")

    lines += [
        "",
        "## App features not yet in manual (minor / v2)",
        "",
        "These screens exist in screenRegistry but are grouped or deferred:",
        "",
        "- Glass Paywall / Trial Expired (transient states)",
        "- Funnel Inspector (tester-only)",
        "- Content Unavailable (deep-link fallback)",
        "- Carbon Footprint, Financial Literacy, Peer Benchmark (niche reports)",
        "- Business Entities, Labels (power-user settings)",
        "- Email Forwarding (Premium import path — add when capture ready)",
        "- Price Watch, UPC compare (Shopping sub-features)",
        "- Achievements, What's New (discovery surfaces)",
        "",
        "## Regenerate",
        "",
        "```bash",
        "cd josspatech.github.io",
        "python scripts/gen-pbj-manual-missing-slides.py",
        "python scripts/build-user-manual-slides.py",
        "python scripts/build-pbj-slide-deck-pdf.py",
        "python scripts/gen-user-guide-en-audio.py --force",
        "node scripts/render-user-guide-video.js",
        "```",
        "",
    ]
    text = "\n".join(lines) + "\n"
    COVERAGE_MD.parent.mkdir(parents=True, exist_ok=True)
    COVERAGE_MD.write_text(text, encoding="utf-8")
    if PBJ_COVERAGE.parent.is_dir():
        PBJ_COVERAGE.write_text(text, encoding="utf-8")


def patch_verify_js() -> None:
    path = ROOT / "scripts" / "verify-user-guide.js"
    text = path.read_text(encoding="utf-8")
    n = len(SLIDES)
    text = re.sub(
        r"process\.exit\(slides === \d+ && tapIndicators > 0 && audioOk \? 0 : 1\);",
        f"process.exit(slides === {n} && tapIndicators > 0 && audioOk ? 0 : 1);",
        text,
    )
    path.write_text(text, encoding="utf-8")


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")
    html = patch_index(html)
    INDEX.write_text(html, encoding="utf-8")

    narrations = [s["narration"] for s in SLIDES]
    NARRATION_JSON.write_text(
        json.dumps(narrations, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_coverage()
    patch_verify_js()
    print(f"Built {len(SLIDES)} slides, {len(CHAPTER_PILLS)} chapter pills")
    print(f"  OK={sum(1 for s in SLIDES if s['png_status']=='OK')} "
          f"interim={sum(1 for s in SLIDES if s['png_status']=='interim')} "
          f"missing={sum(1 for s in SLIDES if not s['img'])}")


if __name__ == "__main__":
    main()
