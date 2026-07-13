#!/usr/bin/env python3
"""Build the written PocketBudJet User Manual (PDF + HTML).

This is NOT the slide-deck builder. Output:
  docs/pocketbudjet/PocketBudJet_UserManual.pdf   (canonical)
  docs/pocketbudjet/PocketBudJet_UserGuide.pdf    (legacy alias, same bytes)
  docs/pocketbudjet/PocketBudJet_UserManual.html  (web TOC + sections)

PDF TOC entries are internal links; HTML TOC entries are in-page anchors
(plus optional Watch deep-links into /videos/user-guide/#chapter=N).
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "pocketbudjet"
CANONICAL = OUT_DIR / "PocketBudJet_UserManual.pdf"
LEGACY_ALIAS = OUT_DIR / "PocketBudJet_UserGuide.pdf"
HTML_OUT = OUT_DIR / "PocketBudJet_UserManual.html"

# Interactive player chapter starts for "Watch" deep-links (videos/user-guide/#chapter=N)
INTERACTIVE_CHAPTER: dict[str, int] = {
    "Getting Started": 0,
    "Dashboard Overview": 27,
    "Adding Transactions": 48,
    "Importing Data": 54,
    "Scanning Documents": 62,
    "Budget Management": 33,
    "Bills & Recurring Transactions": 67,
    "Savings & Goals": 39,
    "Debt Management": 74,
    "Investments & Net Worth": 84,
    "Reports & Analytics": 78,
    "AI Financial Coach": 44,
    "AI Assistant": 44,
    "Search": 113,
    "Export & Sharing": 86,
    "PC Web Dashboard": 110,
    "Tax Features": 89,
    "Household Sync": 111,
    "Calendar View": 67,
    "Transaction Bookmarks & Rules": 101,
    "Accessibility": 117,
    "Mindful Features": 108,
    "Retirement Planning": 106,
    "Voice Shortcuts": 104,
    "Pricing": 15,
    "Privacy & Security": 117,
    "Data & Storage Management": 117,
}

# Brand colors (navy / gold — match site, not purple defaults)
NAVY = (26, 54, 93)
GOLD = (212, 168, 67)
BODY = (40, 40, 40)
MUTED = (90, 90, 90)

SECTIONS: list[tuple[str, str, list[str]]] = [
    (
        "Getting Started",
        "Download and install PocketBudJet in minutes, then set up your first budget with our easy 9-step onboarding wizard.",
        [
            "Download from Google Play Store (iOS coming soon)",
            "Complete 9-step onboarding wizard on first launch",
            "Set up your first budget in minutes",
            "Enter your gross pay and take-home pay — the wizard automatically calculates your paycheck deductions",
            "Choose a budget template or create a custom budget",
            "Want to itemize deductions later? Tap any income transaction and choose Paycheck Breakdown",
            "Enjoy a 35-day free trial with full app access — no credit card required",
        ],
    ),
    (
        "Dashboard Overview",
        "Your dashboard gives you a complete snapshot of your finances at a glance. See your income, spending, and net position in real-time.",
        [
            "Income, Spent, and Net overview cards",
            "Spending pace indicator to track against your budget",
            "Available-to-spend daily number to guide daily decisions",
            "Customizable widget layout — arrange cards to your preference",
            "Quick access to key actions like adding transactions",
            "Historical trends and comparisons",
            "Anomaly alerts when unusual spending is detected",
        ],
    ),
    (
        "Adding Transactions",
        "Quickly log your spending and income. PocketBudJet makes it easy with manual entry, smart splits, and attachments.",
        [
            "Manual transaction entry with just a few taps",
            "Split bills across multiple people or categories",
            "Transfer transactions between accounts",
            "Attach photos and notes to track receipts and details",
            "Smart credit card payment splitting — automatically allocate to original purchase categories",
            "Quick-amount presets for common purchases",
        ],
    ),
    (
        "Importing Data",
        "Easily import your financial data from banks and other sources. PocketBudJet supports multiple file formats for maximum compatibility.",
        [
            "Universal CSV import — works with most financial institutions",
            "OFX/QFX/QIF/XLSX format support from banks and brokers",
            "PDF bank statement import with intelligent parsing",
            "Screenshot import — snap a photo of any financial screen",
            "Email receipt import — forward receipts to the app",
            "Notification capture — automatically detect transactions from banking app notifications",
            "Multi-month imports for comparing spending patterns",
            "Duplicate detection and conflict resolution",
            "No bank login or credentials required",
        ],
    ),
    (
        "Scanning Documents",
        "PocketBudJet features industry-leading document scanning. Transform paper receipts and bills into organized transactions.",
        [
            "Receipt scanning with item-level OCR — extract every purchase detail",
            "Bill and pay stub scanning for income documentation",
            "WiFi network scanner (eSCL) with ADF support — scan entire multi-page bank statements from your home printer in one tap",
            "No competitor offers home printer scanning at this scale",
            "Automatic categorization of scanned items",
            "Handwriting recognition for handwritten notes on receipts",
            "Universal document scanner for any financial paperwork",
        ],
    ),
    (
        "Budget Management",
        "Set spending limits, choose from proven budget templates, or create your own. Track your budget progress with visual overlays.",
        [
            "Create categories with custom spending limits",
            "5 built-in templates: 50/30/20, Zero-Based, Aggressive Saver, Envelope, and Freelancer",
            "Budget rollover — carry unused funds to next month",
            "Copy previous month's budget to save time",
            "Budget Health Overlay — visual progress indicators",
            "Annual budget view for long-term planning",
            "Budget variance reports — see exactly where you're over or under",
            "Adjust budgets mid-month as your priorities change",
        ],
    ),
    (
        "Bills & Recurring Transactions",
        "Never miss a payment. PocketBudJet tracks bills, recurring transactions, and subscriptions with smart predictions.",
        [
            "Bill calendar with payday markers for easy planning",
            "Recurring transactions (daily, weekly, biweekly, monthly, annual)",
            "Recurring income tracking with gross pay and deduction breakdowns",
            "Smart bill amount prediction — automatically adjusts based on history",
            "Subscription tracker with price-change alerts",
            "Cancellation links for easy subscription management",
            "Upcoming bills overview to reduce surprise overspending",
            "Recurring forecast — see your next 30 or 90 days of recurring costs",
        ],
    ),
    (
        "Savings & Goals",
        "Track savings progress, create sinking funds, and plan purchases. Build financial security step by step.",
        [
            "Savings goals with progress tracking and milestones",
            "Sinking funds for irregular expenses (car repairs, holidays, etc.)",
            "Purchase wishlist with 30-day cooling-off period to curb impulse buys",
            "What-if scenarios — explore different savings strategies",
            "Goal reminders and motivation tracking",
            "Visual progress bars and achievement badges",
        ],
    ),
    (
        "Debt Management",
        "Take control of debt with avalanche and snowball strategies, credit card insights, and payoff projections.",
        [
            "Track all debts in one place — credit cards, loans, mortgages",
            "Avalanche vs snowball strategy comparison and recommendations",
            "Credit card intelligence — deferred interest detection, rewards tracking",
            "Payoff timeline projections and scenario planning",
            "Interest calculation tools",
            "Debt consolidation insights",
            "What-if scenarios — see how extra payments accelerate payoff",
        ],
    ),
    (
        "Investments & Net Worth",
        "Comprehensive investment and net worth tracking in one app. Monitor stocks, crypto, real estate, and credit score.",
        [
            "Investment portfolio tracking — stocks, ETFs, mutual funds, bonds via Yahoo Finance",
            "Crypto tracking with 19 coins: Bitcoin, Ethereum, Solana, Cardano, Dogecoin, and more via CoinGecko",
            "Property and real estate tracking with Zillow search integration",
            "Credit score monitoring from 6 different sources",
            "Net worth tracker with monthly snapshots and trend analysis",
            "Asset allocation visualization",
            "Insurance policy tracker with renewal alerts",
        ],
    ),
    (
        "Reports & Analytics",
        "Deep dive into your spending and financial health with 10+ powerful report types and anomaly detection.",
        [
            "Budget Health Report — see where money goes vs. budget",
            "Financial Health Score — comprehensive wellness overview",
            "Projected Balance Report — forecast future cash position",
            "Spending Forecast Report — predict upcoming expenses",
            "Anomaly Dashboard — identify unusual transactions and patterns",
            "Year over Year Report — compare spending trends",
            "Tax Return Report — organize deductible expenses",
            "Annual Budget Report — yearly spending summary",
            "Net Worth History Report — track asset growth",
            "Merchant Analysis Report — identify spending by vendor",
            "Custom reports — build your own with flexible filters",
            "Automated spending anomaly alerts",
        ],
    ),
    (
        "AI Financial Coach",
        "Get personalized financial insights powered by your spending data. The coach learns your habits and suggests improvements.",
        [
            "Personalized insights based on aggregated data only",
            "Opt-in feature — you control what data is analyzed",
            "Spending pattern recognition and recommendations",
            "Budget adjustment suggestions based on trends",
            "Savings opportunity identification",
            "Financial goal progress tracking",
            "Weekly AI recap with spending highlights and insights",
        ],
    ),
    (
        "AI Assistant",
        'Ask questions about your finances in plain English. The AI Assistant understands natural language and queries your data directly — no menus to navigate.',
        [
            'Conversational Q&A — type questions like "How much did I spend on groceries last month?"',
            "Supports 11 query types: spending totals, category breakdowns, merchant lookups, income summaries, budget status, trends, comparisons, top merchants, recent transactions, net position, and custom date ranges",
            'Natural language date parsing — "last week", "this quarter", "January"',
            "Results displayed with formatted amounts, charts, and lists",
            "All processing happens on-device — your data never leaves your phone",
            "Quick-start example questions to get you going",
            "Available from any screen via the AI Assistant button",
        ],
    ),
    (
        "Search",
        "Quickly find any transaction with natural language search. Ask questions like a human.",
        [
            'Natural language search — type "coffee last week" to find coffee purchases',
            'Search by amount — "over $50" finds large transactions',
            "Search by date range, category, merchant, or tags",
            "Fuzzy matching for misspelled merchant names",
            "Saved search filters for frequent queries",
            "Universal search across all data types",
        ],
    ),
    (
        "Export & Sharing",
        "Share your financial data in multiple formats. Create reports for accountants or analyze data in Excel.",
        [
            "Export formats: CSV, JSON, PDF, Word, Excel, OFX, HTML",
            "Accountant report export with tax-deductible items highlighted",
            "LAN report server — view on any screen via QR code on your home network",
            "Share specific date ranges with partners or accountants",
            "Encrypted exports for sensitive data",
            "Scheduled exports to cloud storage",
        ],
    ),
    (
        "PC Web Dashboard",
        "Access your PocketBudJet data from any computer on your home WiFi network. Full dashboard with charts, editing, and real-time sync.",
        [
            "Open your dashboard in any web browser on your home network",
            "Scan a QR code or type the URL — no app install needed on your PC",
            "5 tabs: Dashboard overview, Transactions, Budget, Debt, and Reports",
            "Full CRUD — add, edit, and delete transactions, debts, goals, budgets, and sources from your browser",
            "Charts and visualizations: spending by category, income vs expenses, trends",
            "Session-based security with auto-timeout after 60 minutes of inactivity",
            "Real-time sync — changes on your phone appear instantly in the browser and vice versa",
            "Start and stop from Settings → Export → PC Dashboard",
        ],
    ),
    (
        "Tax Features",
        "Organize tax-deductible transactions and simplify tax time. Tag expenses and generate tax reports.",
        [
            "Tag transactions with 8 IRS categories for deductibility",
            "Tax-deductible transaction summary and category breakdown",
            "Tax return import and comparison to validate deductions",
            "Quarterly tax estimate calculator",
            "Mileage tracking for business use",
            "Self-employed income tracking",
        ],
    ),
    (
        "Household Sync",
        "Share finances with a partner using WiFi and Bluetooth. Keep both devices in sync without the internet.",
        [
            "WiFi and Bluetooth partner sync via secure QR code pairing",
            "No internet connection required — sync on your home network",
            "Real-time transaction sync between devices",
            "Joint budget management and visibility",
            "Separate or shared views of spending",
            "Conflict resolution for simultaneous edits",
        ],
    ),
    (
        "Calendar View",
        "See your financial life on a calendar. Bills, income, and spending laid out by date for easy planning.",
        [
            "Monthly calendar with transaction dots showing activity",
            "Tap any day to see that day's transactions",
            "Bill due dates and payday markers",
            "Recurring transaction indicators",
            "Color-coded: green for income, red for expenses",
            "Swipe between months for quick navigation",
        ],
    ),
    (
        "Transaction Bookmarks & Rules",
        "Save time with reusable bookmarks for frequent transactions and automated rules for categorization.",
        [
            "Bookmark frequent transactions — one tap to reuse",
            "Bookmarks remember description, amount, category, and source",
            "Usage counter tracks your most-used bookmarks",
            "Transaction rules — auto-categorize based on merchant name or patterns",
            "Rules apply to imported and manually entered transactions",
            "Bulk edit — change category or status for multiple transactions at once",
            "Labels management — rename employers, bill payees, and categories in one place",
        ],
    ),
    (
        "Accessibility",
        "PocketBudJet is built for everyone. Multiple accessibility features ensure you can manage your money comfortably.",
        [
            "Dark mode for comfortable viewing in all lighting",
            "High contrast mode for better readability",
            "Colorblind-friendly charts using Okabe-Ito color palette",
            "App lock with Face ID, Touch ID, or PIN protection",
            "Large text option for improved visibility",
            "Screen reader compatibility",
            "Font scaling support",
        ],
    ),
    (
        "Mindful Features",
        "Enjoy a healthier relationship with money. Mindful Budget View reframes overspending, and Time Cost Mode shows hours-of-work.",
        [
            'Mindful Budget View — reframes "over budget" as "fully used"',
            "Time Cost Mode — displays how many hours of work each purchase cost",
            "PBJ Stars badges — celebrate financial milestones and achievements",
            "Spending reflection prompts",
            "Financial wellness check-ins",
            "Motivational insights and encouragement",
        ],
    ),
    (
        "Retirement Planning",
        "Plan for retirement with milestone tracking. PocketBudJet uses Fidelity milestone bands and FIRE basics.",
        [
            "Retirement milestone tracker with Fidelity milestone bands",
            "FIRE (Financial Independence, Retire Early) basics tutorial",
            "Retirement savings goal planning",
            "Safe withdrawal rate calculations",
            "Retirement income projection",
            "Progress tracking toward retirement milestones",
        ],
    ),
    (
        "Voice Shortcuts",
        "Control PocketBudJet with your voice. Use Siri (iOS) or Google Assistant to log transactions hands-free.",
        [
            "6 built-in voice shortcuts accessible via Siri or Google Assistant",
            'Log transactions by voice — "Hey Siri, I spent $20 on coffee"',
            'Check budget status — "What\'s my monthly budget?"',
            'View current spending — "How much have I spent this month?"',
            "Create savings goals by voice",
            "Custom voice shortcuts for your most frequent actions",
        ],
    ),
    (
        "Pricing",
        "Flexible pricing plans to match your needs. Start free with a 21-day trial — no credit card required.",
        [
            "21-day free trial — full app access, no credit card needed",
            "Monthly: $9.99/month with auto-renew",
            "Annual: $74.99/year (37% off monthly rate)",
            "3-Year: $149.99/three years (58% off monthly rate, no auto-renew)",
            "All plans include full feature access",
            "Cancel anytime during free trial",
            "Money-back guarantee within 30 days",
        ],
    ),
    (
        "Privacy & Security",
        "Your data is yours alone. PocketBudJet uses on-device storage with no cloud requirement and no bank login needed.",
        [
            "All data stays on your device — no cloud upload by default",
            "No bank login or credentials required",
            "No cloud requirement for core functionality",
            "Encryption for exported files",
            "Optional cloud backup for device loss protection",
            "Transparent privacy policy — no ad tracking",
        ],
    ),
    (
        "Data & Storage Management",
        "Control how much history lives on your device, how long your backup keeps records, and free up space without losing a single dollar of financial history. Access via Settings → Data & Backup.",
        [],  # subsections below
    ),
]

# Extra blocks under Privacy & Security / Data & Storage (kept from prior PDF)
APP_LOCK = (
    "App Lock & Recovery Key",
    "Protect your financial data with biometric or passcode lock. PocketBudJet generates a recovery key so you can always regain access yourself — no support request needed.",
    [
        "App lock with Face ID, Touch ID, or a custom passcode",
        "Recovery key generated on your device when you enable a lock — shown once, store it safely",
        "Recovery key is stored only as a secure hash and never sent to any server",
        "Manage your key anytime: Settings → Security → Recovery Key (rotate or remove)",
        "Locked out? Enter your recovery key to reset instantly — no reinstall, data untouched",
        "Entire lock system works offline — fully self-contained, no account required",
    ],
)

DATA_SUBSECTIONS: list[tuple[str, list[str]]] = [
    (
        "Backup Retention",
        [
            "Choose how far back your backup keeps full transaction details: 6 months up to 7 years",
            "Data that ages out is summarized — annual totals, top categories, and net savings are locked permanently",
            "Summaries are yours forever regardless of which retention window you choose",
        ],
    ),
    (
        "On-Device Working Set",
        [
            "Controls how many months of transactions live on your phone for instant offline access",
            "Minimum 3 months — the floor PocketBudJet needs to reliably track budget patterns",
            "Extend up to 2 years if you want more history available without fetching from backup",
        ],
    ),
    (
        "Receipt Image Storage",
        [
            "Three-tier model: thumbnails always stay on device, full images live in backup, compressed previews are tiered",
            "Choose your preview window: 30, 60, 90, or 180 days on-device before moving to backup-only",
            "Tap any receipt to fetch the full image from backup whenever you need it",
        ],
    ),
    (
        "Annual Summaries",
        [
            "Year-by-year totals computed and locked permanently before any data ages out",
            "Income, expenses, and net savings for every year you've used the app — never deleted",
            "Power your all-time analysis even after underlying transactions have been archived",
        ],
    ),
    (
        "Free Up Space",
        [
            "Tap 'Review & Free Up Space' to preview exactly what would be removed before anything happens",
            "Preview shows transaction count, receipt image impact, and estimated space reclaimed",
            "Annual summaries are always computed and backup-confirmed before any data leaves the device",
        ],
    ),
    (
        "Archive History",
        [
            "Track the status of every archived year: transaction count, backup confirmation, and completion date",
            "Years show as 'Pending' until backup confirms receipt — data stays on device until confirmed",
            "Full audit trail so you always know what has been safely stored",
        ],
    ),
]


def _add_fonts(pdf: FPDF) -> None:
    """Use Windows Segoe UI (Unicode) for em dashes, bullets, and arrows."""
    windir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    regular = windir / "segoeui.ttf"
    bold = windir / "segoeuib.ttf"
    italic = windir / "segoeuii.ttf"
    if not regular.exists():
        raise SystemExit(f"Missing Unicode font: {regular}")
    pdf.add_font("Manual", "", fname=str(regular))
    pdf.add_font("Manual", "B", fname=str(bold if bold.exists() else regular))
    pdf.add_font("Manual", "I", fname=str(italic if italic.exists() else regular))


class ManualPDF(FPDF):
    def header(self) -> None:
        if self.page_no() <= 1:
            return
        self.set_font("Manual", "", 9)
        self.set_text_color(*MUTED)
        # Content pages: TOC is page 2 → printed "Page 1", etc.
        printed = self.page_no() - 1
        self.cell(0, 8, f"PocketBudJet User Manual — Page {printed}", align="L")
        self.ln(10)
        self.set_draw_color(*GOLD)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)

    def footer(self) -> None:
        if self.page_no() <= 1:
            return
        self.set_y(-15)
        self.set_font("Manual", "", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 8, f"{self.page_no()}", align="C")


def _ensure_space(pdf: ManualPDF, needed: float) -> None:
    if pdf.get_y() + needed > pdf.h - pdf.b_margin - 8:
        pdf.add_page()


def _write_bullets(pdf: ManualPDF, bullets: list[str]) -> None:
    pdf.set_font("Manual", "", 10)
    pdf.set_text_color(*BODY)
    for b in bullets:
        _ensure_space(pdf, 10)
        x = pdf.l_margin
        y = pdf.get_y()
        pdf.set_x(x)
        pdf.cell(6, 5, "•")
        pdf.set_xy(x + 6, y)
        pdf.multi_cell(pdf.epw - 6, 5, b)
        pdf.ln(1)


def _write_section_heading(pdf: ManualPDF, number: int | None, title: str, link_id: int | None) -> None:
    _ensure_space(pdf, 28)
    if link_id is not None:
        pdf.set_link(link_id, y=pdf.get_y())
    pdf.start_section(title if number is None else f"{number}. {title}", level=0)
    pdf.set_font("Manual", "B", 13)
    pdf.set_text_color(*NAVY)
    label = title if number is None else f"{number}. {title}"
    pdf.multi_cell(0, 7, label)
    pdf.ln(2)


def build() -> Path:
    pdf = ManualPDF(orientation="P", unit="mm", format="Letter")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(18, 16, 18)
    _add_fonts(pdf)
    pdf.set_title("PocketBudJet User Manual")
    pdf.set_author("JosspaTech")
    pdf.set_subject("PocketBudJet User Manual v1.2")
    pdf.set_creator("scripts/build-pbj-written-user-manual-pdf.py")

    # Pre-create internal destinations for TOC + bookmarks
    section_links = [pdf.add_link() for _ in SECTIONS]
    help_link = pdf.add_link()

    # --- Cover ---
    pdf.add_page()
    pdf.ln(55)
    pdf.set_font("Manual", "B", 32)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 14, "PocketBudJet", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    pdf.set_font("Manual", "I", 14)
    pdf.set_text_color(*GOLD)
    pdf.cell(0, 8, "Your Money. Your Device. Your Rules.", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(18)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.8)
    mid = pdf.w / 2
    pdf.line(mid - 40, pdf.get_y(), mid + 40, pdf.get_y())
    pdf.ln(14)
    pdf.set_font("Manual", "B", 22)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, "User Manual", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("Manual", "", 12)
    pdf.set_text_color(*MUTED)
    pdf.cell(0, 7, "Version 1.2 — April 2026", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(40)
    pdf.set_font("Manual", "", 10)
    pdf.cell(0, 6, "© 2026 JosspaTech. All Rights Reserved.", align="C", new_x="LMARGIN", new_y="NEXT")

    # --- TOC placeholder (filled after body so link destinations exist) ---
    pdf.add_page()
    toc_page = pdf.page_no()
    pdf.set_font("Manual", "B", 18)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 10, "Table of Contents", new_x="LMARGIN", new_y="NEXT")
    # Leave room; entries written after section links are assigned

    # --- Body ---
    pdf.add_page()
    for i, (title, intro, bullets) in enumerate(SECTIONS):
        _write_section_heading(pdf, i + 1, title, section_links[i])
        pdf.set_font("Manual", "", 10)
        pdf.set_text_color(*BODY)
        pdf.multi_cell(0, 5, intro)
        pdf.ln(2)
        if title == "Data & Storage Management":
            for sub_title, sub_bullets in DATA_SUBSECTIONS:
                _ensure_space(pdf, 16)
                pdf.set_font("Manual", "B", 11)
                pdf.set_text_color(*NAVY)
                pdf.multi_cell(0, 6, sub_title)
                pdf.ln(1)
                _write_bullets(pdf, sub_bullets)
                pdf.ln(2)
        else:
            _write_bullets(pdf, bullets)
            pdf.ln(3)

        if title == "Privacy & Security":
            _write_section_heading(pdf, None, APP_LOCK[0], None)
            pdf.set_font("Manual", "", 10)
            pdf.set_text_color(*BODY)
            pdf.multi_cell(0, 5, APP_LOCK[1])
            pdf.ln(2)
            _write_bullets(pdf, APP_LOCK[2])
            pdf.ln(3)

            # Need Help sits after Privacy in the prior PDF
            _ensure_space(pdf, 28)
            pdf.set_link(help_link, y=pdf.get_y())
            pdf.start_section("Need Help?", level=0)
            pdf.set_font("Manual", "B", 13)
            pdf.set_text_color(*NAVY)
            pdf.multi_cell(0, 7, "Need Help?")
            pdf.ln(2)
            pdf.set_font("Manual", "", 10)
            pdf.set_text_color(*BODY)
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 5, "Email: support@josspatech.com")
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 5, "Website: josspatech.github.io/how-to")
            pdf.ln(3)

    # --- Closing ---
    pdf.add_page()
    pdf.ln(60)
    pdf.set_font("Manual", "I", 12)
    pdf.set_text_color(*NAVY)
    pdf.multi_cell(
        0,
        8,
        "Thank you for using PocketBudJet. Your data. Your device. Your rules.",
        align="C",
    )

    # --- Fill TOC now that destinations have page numbers ---
    pdf.page = toc_page
    pdf.set_y(pdf.t_margin + 28)
    for i, (title, _intro, _bullets) in enumerate(SECTIONS):
        pdf.set_font("Manual", "", 11)
        pdf.set_text_color(*NAVY)
        label = f"{i + 1}. {title}"
        pdf.cell(0, 6.5, label, link=section_links[i], new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Manual", "B", 11)
    pdf.set_text_color(*NAVY)
    pdf.cell(0, 6.5, "Need Help?", link=help_link, new_x="LMARGIN", new_y="NEXT")
    # Restore to last page so output metadata is correct
    pdf.page = len(pdf.pages)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf.output(str(CANONICAL))
    shutil.copy2(CANONICAL, LEGACY_ALIAS)
    return CANONICAL


def _slug(title: str) -> str:
    out = []
    for ch in title.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in (" ", "&", "-", "/"):
            out.append("-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_html() -> Path:
    """Write web User Manual with clickable TOC (parity with PDF chapters)."""
    toc_items: list[tuple[str, str, str]] = []
    for i, (title, _intro, _bullets) in enumerate(SECTIONS):
        slug = _slug(title)
        toc_items.append((f"{i + 1}. {_esc(title)}", f"#{slug}", title))
    toc_items.append(("Need Help?", "#need-help", "Need Help?"))

    toc_html = "\n".join(
        f'      <li><a href="{href}">{label}</a>'
        + (
            f' <a class="watch" href="/videos/user-guide/#chapter={INTERACTIVE_CHAPTER[title]}">Watch</a>'
            if title in INTERACTIVE_CHAPTER
            else ""
        )
        + "</li>"
        for label, href, title in toc_items
    )

    body_parts: list[str] = []
    for i, (title, intro, bullets) in enumerate(SECTIONS):
        slug = _slug(title)
        body_parts.append(f'  <section id="{slug}">')
        body_parts.append(f"    <h2>{i + 1}. {_esc(title)}</h2>")
        body_parts.append(f"    <p>{_esc(intro)}</p>")
        if title == "Data & Storage Management":
            for sub_title, sub_bullets in DATA_SUBSECTIONS:
                body_parts.append(f"    <h3>{_esc(sub_title)}</h3>")
                body_parts.append("    <ul>")
                for b in sub_bullets:
                    body_parts.append(f"      <li>{_esc(b)}</li>")
                body_parts.append("    </ul>")
        else:
            body_parts.append("    <ul>")
            for b in bullets:
                body_parts.append(f"      <li>{_esc(b)}</li>")
            body_parts.append("    </ul>")
        if title == "Privacy & Security":
            body_parts.append(f"    <h3>{_esc(APP_LOCK[0])}</h3>")
            body_parts.append(f"    <p>{_esc(APP_LOCK[1])}</p>")
            body_parts.append("    <ul>")
            for b in APP_LOCK[2]:
                body_parts.append(f"      <li>{_esc(b)}</li>")
            body_parts.append("    </ul>")
        if title in INTERACTIVE_CHAPTER:
            n = INTERACTIVE_CHAPTER[title]
            body_parts.append(
                f'    <p class="watch-line"><a href="/videos/user-guide/#chapter={n}">'
                f"Open this chapter in the interactive User Manual →</a></p>"
            )
        body_parts.append("  </section>")

    body_parts.append('  <section id="need-help">')
    body_parts.append("    <h2>Need Help?</h2>")
    body_parts.append(
        '    <p>Email: <a href="mailto:support@josspatech.com">support@josspatech.com</a></p>'
    )
    body_parts.append(
        '    <p>Website: <a href="/how-to/">josspatech.com/how-to</a></p>'
    )
    body_parts.append(
        '    <p class="watch-line"><a href="/videos/user-guide/#chapter=119">'
        "Open Help in the interactive User Manual →</a></p>"
    )
    body_parts.append("  </section>")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>User Manual — PocketBudJet by JosspaTech</title>
<meta name="description" content="PocketBudJet User Manual — clickable table of contents covering every major feature.">
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Source+Sans+3:wght@300;400;600;700&display=swap');
:root{{--navy:#1A4F7A;--navy-dark:#0C3358;--navy-mid:#2E6FA3;--gold:#E8A820;--slate:#5A7A9A;--light-slate:#8AAABB;--bg:#EDF2F7;--white:#FFFFFF;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:"Source Sans 3",sans-serif;background:var(--bg);color:#222;line-height:1.8;font-size:16px;}}
header{{background:var(--navy-dark);padding:0 48px;height:64px;display:flex;align-items:center;justify-content:space-between;border-bottom:2px solid var(--gold);}}
.hdr-logo{{display:flex;align-items:center;gap:10px;text-decoration:none;}}
.hdr-name{{font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:#fff;}}
.hdr-name span{{color:var(--gold);}}
.hdr-back{{font-size:14px;color:var(--light-slate);text-decoration:none;letter-spacing:0.5px;}}
.hdr-back:hover{{color:var(--gold);}}
.doc-hero{{background:var(--navy-dark);padding:48px 48px 36px;border-bottom:1px solid rgba(232,168,32,0.2);}}
.doc-type{{font-size:12px;letter-spacing:4px;text-transform:uppercase;color:var(--gold);display:block;margin-bottom:10px;}}
.doc-hero h1{{font-family:'Playfair Display',serif;font-size:40px;font-weight:900;color:#fff;margin-bottom:8px;}}
.doc-meta{{font-size:15px;color:var(--light-slate);}}
.doc-meta a{{color:var(--gold);}}
main{{max-width:760px;margin:0 auto;padding:52px 24px 80px;}}
.summary-box{{background:var(--navy-dark);color:#fff;border-radius:6px;padding:18px 22px;margin-bottom:40px;font-size:16px;line-height:1.7;border-left:3px solid var(--gold);}}
.summary-box strong{{color:var(--gold);}}
.summary-box a{{color:var(--gold);}}
#toc{{margin-bottom:48px;}}
#toc h2{{font-family:'Playfair Display',serif;font-size:22px;color:var(--navy-dark);font-weight:700;margin:0 0 16px;padding-bottom:8px;border-bottom:2px solid var(--gold);}}
#toc ol{{list-style:none;margin:0;padding:0;columns:1;}}
@media(min-width:640px){{#toc ol{{columns:2;column-gap:2rem;}}}}
#toc li{{break-inside:avoid;margin:0 0 8px;font-size:16px;}}
#toc a{{color:var(--navy);font-weight:600;text-decoration:none;border-bottom:2px solid transparent;}}
#toc a:hover{{border-bottom-color:var(--gold);}}
#toc a.watch{{margin-left:8px;font-size:13px;font-weight:600;color:var(--navy-mid);border-bottom:none;}}
#toc a.watch:hover{{color:var(--gold);}}
section{{scroll-margin-top:24px;margin-bottom:36px;}}
h2{{font-family:'Playfair Display',serif;font-size:22px;color:var(--navy-dark);font-weight:700;margin:36px 0 12px;padding-bottom:8px;border-bottom:2px solid var(--navy-mid);}}
h3{{font-size:17px;color:var(--navy);font-weight:700;margin:18px 0 8px;}}
p{{font-size:17px;margin-bottom:14px;}}
ul{{margin:6px 0 14px 22px;}}
li{{font-size:17px;margin-bottom:6px;}}
.watch-line a{{color:var(--navy-mid);font-weight:700;text-decoration:none;border-bottom:2px solid var(--gold);}}
.watch-line a:hover{{color:var(--navy-dark);}}
.pdf-link{{margin-top:8px;display:inline-block;}}
footer{{background:var(--navy-dark);border-top:1px solid rgba(232,168,32,0.2);padding:24px 48px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;}}
footer p{{font-size:12px;color:var(--light-slate);}}
footer a{{color:var(--gold);}}
footer .fn{{font-family:'Playfair Display',serif;font-size:15px;color:#fff;}}
footer .fn span{{color:var(--gold);}}
@media(max-width:600px){{header,footer{{padding:0 20px;}}.doc-hero{{padding:36px 20px 28px;}}main{{padding:36px 20px 60px;}}.doc-hero h1{{font-size:30px;}}}}
</style>
</head>
<body>
<header>
  <a class="hdr-logo" href="/#pbj">
    <span class="hdr-name">Josspa<span>Tech</span>™</span>
  </a>
  <a class="hdr-back" href="/how-to/">← How To</a>
</header>

<div class="doc-hero">
  <span class="doc-type">PocketBudJet · User Manual</span>
  <h1>User Manual</h1>
  <div class="doc-meta">
    <span>Version 1.2 — April 2026</span>
    <span><a href="/docs/pocketbudjet/PocketBudJet_UserManual.pdf">Download PDF</a></span>
    <span><a href="/videos/user-guide/">Interactive presentation</a></span>
  </div>
</div>

<main>
  <div class="summary-box">
    <strong>How to use this page:</strong> Tap any chapter in the Table of Contents to jump to that section.
    Prefer screen-by-screen walkthroughs? Open the <a href="/videos/user-guide/">interactive User Manual</a>
    or use the Watch links next to each chapter.
  </div>

  <nav id="toc" aria-label="Table of Contents">
    <h2>Table of Contents</h2>
    <ol>
{toc_html}
    </ol>
  </nav>

{chr(10).join(body_parts)}
</main>

<footer>
  <p class="fn">Josspa<span>Tech</span>™</p>
  <p>&copy; 2026 JosspaTech. All Rights Reserved. · <a href="/how-to/">How To</a> · <a href="/docs/pocketbudjet/PocketBudJet_UserManual.pdf">PDF</a></p>
</footer>
</body>
</html>
"""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    HTML_OUT.write_text(html, encoding="utf-8")
    return HTML_OUT


def main() -> int:
    path = build()
    print(f"Wrote {path}")
    print(f"Legacy alias {LEGACY_ALIAS}")
    html_path = build_html()
    print(f"Wrote {html_path}")
    # Quick verify
    try:
        from pypdf import PdfReader

        r = PdfReader(str(path))
        print(f"pages={len(r.pages)} outline={len(r.outline or [])}")
        toc_annots = r.pages[1].get("/Annots")
        print(f"toc_annotations={len(toc_annots) if toc_annots else 0}")
    except Exception as exc:  # noqa: BLE001
        print(f"verify skipped: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
