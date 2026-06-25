#!/usr/bin/env python3
"""Patch connect-bank/index.html from budget-setup copy."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "videos" / "pocketbudjet" / "connect-bank" / "index.html"
html = path.read_text(encoding="utf-8")

html = html.replace("Budget Setup - PocketBudJet", "Connect Bank (Teller) - PocketBudJet")
html = html.replace("<span class=\"current\">Budget Setup</span>", "<span class=\"current\">Connect Bank</span>")
html = html.replace(
    "<h1>Set Up Your Budget in 2 Minutes</h1>",
    "<h1>Connect Your US Bank (Teller)</h1>",
)
html = html.replace(
    "<p class=\"subheader\">Pick a template, customize your categories, add your accounts, and start tracking. No spreadsheets. No stress.</p>",
    "<p class=\"subheader\">Automatic bank sync for <strong>US institutions only</strong> — paid Premium required (not included in the 21-day trial). Two banks included; $3.99/mo per extra bank. Connections disconnect if your subscription lapses.</p>",
)
html = html.replace("<h2>Watch It in Action</h2>", "<h2>How to connect a bank</h2>")

slides = '''                            <div class="tap-to-start" id="tapToStart">
                                <div class="tap-to-start-icon">&#9654;</div>
                                <div class="tap-to-start-label">Tap to play</div>
                            </div>
                            <div class="slide active" data-index="0">
                                <img src="/assets/screenshots/connect-bank/bank-sync.png" alt="Connect Bank overview" loading="lazy">
                                <div class="slide-overlay">
                                    <span class="slide-step">OVERVIEW</span>
                                    <div class="slide-title">US bank sync — Premium paid only</div>
                                </div>
                            </div>
                            <div class="slide" data-index="1" data-tap-x="90" data-tap-y="8" data-tap-label="Settings" data-tap-hint="Tap the <strong>gear icon</strong> (top right) to open Settings.">
                                <img src="/assets/screenshots/connect-bank/bank-sync.png" alt="Open Settings" loading="lazy">
                                <div class="slide-overlay">
                                    <span class="slide-step">STEP 1</span>
                                    <div class="slide-title">Tap Settings (gear, top-right)</div>
                                </div>
                            </div>
                            <div class="slide" data-index="2" data-tap-x="50" data-tap-y="35" data-tap-label="Connect Bank" data-tap-hint="Tap <strong>Connect Bank</strong> or <strong>Bank Sync</strong> in Settings.">
                                <img src="/assets/screenshots/connect-bank/bank-sync.png" alt="Connect Bank menu" loading="lazy">
                                <div class="slide-overlay">
                                    <span class="slide-step">STEP 2</span>
                                    <div class="slide-title">Open Connect Bank</div>
                                </div>
                            </div>
                            <div class="slide" data-index="3" data-tap-x="50" data-tap-y="45" data-tap-label="Search" data-tap-hint="Search for your <strong>US bank or credit union</strong> — EU institutions are not supported.">
                                <img src="/assets/screenshots/connect-bank/bank-sync.png" alt="Search for your bank" loading="lazy">
                                <div class="slide-overlay">
                                    <span class="slide-step">STEP 3</span>
                                    <div class="slide-title">Search your US institution</div>
                                </div>
                            </div>
                            <div class="slide" data-index="4" data-tap-x="50" data-tap-y="55" data-tap-label="Sign in" data-tap-hint="Sign in through Teller&rsquo;s secure window — PocketBudJet never stores your bank password.">
                                <img src="/assets/screenshots/connect-bank/bank-sync.png" alt="Teller secure sign-in" loading="lazy">
                                <div class="slide-overlay">
                                    <span class="slide-step">STEP 4</span>
                                    <div class="slide-title">Sign in via Teller (secure)</div>
                                </div>
                            </div>
                            <div class="slide" data-index="5" data-tap-x="50" data-tap-y="70" data-tap-label="Confirm" data-tap-hint="Choose accounts to link, then tap <strong>Confirm</strong>. Premium includes <strong>two banks</strong>; extra banks are $3.99/mo each.">
                                <img src="/assets/screenshots/connect-bank/bank-sync.png" alt="Select accounts" loading="lazy">
                                <div class="slide-overlay">
                                    <span class="slide-step">STEP 5</span>
                                    <div class="slide-title">Pick accounts — 2 banks included</div>
                                </div>
                            </div>
                            <div class="slide" data-index="6">
                                <img src="/assets/screenshots/connect-bank/bank-sync.png" alt="Bank connected" loading="lazy">
                                <div class="slide-overlay">
                                    <span class="slide-step">DONE</span>
                                    <div class="slide-title">Transactions sync automatically</div>
                                </div>
                            </div>'''

import re
html = re.sub(
    r'<div class="tap-to-start" id="tapToStart">.*?</div>\s*</div>\s*</div>\s*</div>\s*<div class="slide active" data-index="0".*?</div>\s*</div>\s*</div>\s*<div class="progress-dots"',
    slides + '\n                        </div>\n                    </div>\n                    </div>\n                    <div class="progress-dots"',
    html,
    count=1,
    flags=re.DOTALL,
)

narration = '''                <div class="narration-panel" id="narrationPanel">
                    <div class="narration-card" data-index="0">
                        <span class="narration-step-badge">Step 1 of 7</span>
                        <h3>Before you connect</h3>
                        <p>Bank sync connects to <strong>US institutions only</strong> through Teller — not available in the EU. It requires a <strong>paid Premium subscription</strong>; it is <strong>not</strong> included in the 21-day trial. You can still import statements without any bank login during the trial. Premium includes two linked banks; each additional bank is $3.99 per month. If your subscription lapses, bank connections disconnect automatically.</p>
                        <div class="narration-timer"></div>
                    </div>
                    <div class="narration-card" data-index="1">
                        <span class="narration-step-badge">Step 2 of 7</span>
                        <h3>Open Settings</h3>
                        <p>From Home, tap the <strong>gear icon</strong> in the top-right corner. This is where bank sync, exports, and privacy controls live.</p>
                        <div class="narration-timer"></div>
                    </div>
                    <div class="narration-card" data-index="2">
                        <span class="narration-step-badge">Step 3 of 7</span>
                        <h3>Tap Connect Bank</h3>
                        <p>In Settings, tap <strong>Connect Bank</strong> (or Bank Sync). If you are still on the trial, PocketBudJet will explain that sync unlocks after you subscribe — import still works without a login.</p>
                        <div class="narration-timer"></div>
                    </div>
                    <div class="narration-card" data-index="3">
                        <span class="narration-step-badge">Step 4 of 7</span>
                        <h3>Find your institution</h3>
                        <p>Search for your US bank or credit union. Teller supports major US banks; if yours is missing, use <a href="/videos/pocketbudjet/share-statements/" style="color:#1A4F7A;font-weight:600">Share to import</a> or CSV import instead — no bank password needed.</p>
                        <div class="narration-timer"></div>
                    </div>
                    <div class="narration-card" data-index="4">
                        <span class="narration-step-badge">Step 5 of 7</span>
                        <h3>Sign in securely</h3>
                        <p>Teller opens a secure sign-in window. PocketBudJet never stores your bank username or password — Teller handles authentication and sends read-only transaction data to your device.</p>
                        <div class="narration-timer"></div>
                    </div>
                    <div class="narration-card" data-index="5">
                        <span class="narration-step-badge">Step 6 of 7</span>
                        <h3>Select accounts</h3>
                        <p>Choose which checking, savings, or credit accounts to link. Premium includes <strong>two banks</strong>; link a third or fourth for $3.99 per month each. Tap Confirm when ready.</p>
                        <div class="narration-timer"></div>
                    </div>
                    <div class="narration-card" data-index="6">
                        <span class="narration-step-badge">Step 7 of 7</span>
                        <h3>You are connected</h3>
                        <p>New transactions appear automatically and categorize using your rules. Keep Premium active — if your subscription lapses, connections disconnect to avoid ongoing Teller fees. Prefer manual control? Import anytime without bank login.</p>
                        <div class="narration-timer"></div>
                    </div>
                </div>'''

html = re.sub(
    r'<div class="narration-panel" id="narrationPanel">.*?</div>\s*</div>\s*</div>\s*</section>',
    narration + '\n            </div>\n        </div>\n    </section>',
    html,
    count=1,
    flags=re.DOTALL,
)

html = html.replace("<h2>Your Budget Setup Steps</h2>", "<h2>Connect Bank checklist</h2>")
html = html.replace("Enter Your Income", "Confirm Premium (paid)")
html = html.replace("Tell us what you earn each month", "Bank sync is not on the 21-day trial")
html = html.replace("Pick a Template", "Open Settings")
html = html.replace("Zero-Based, 50/30/20, Envelope, or custom", "Gear icon, top-right from Home")
html = html.replace("Customize Categories", "Connect Bank")
html = html.replace("Adjust amounts or add your own", "Settings &rarr; Connect Bank / Bank Sync")
html = html.replace("Add Your Accounts", "US institution only")
html = html.replace("Checking, savings, credit cards, cash", "Search Teller — EU banks not supported")
html = html.replace("Log a Transaction", "Two banks included")
html = html.replace("Snap a receipt or type it in", "Extra banks $3.99/mo each on Premium")
html = html.replace("Start Tracking", "Stay subscribed")
html = html.replace("Your dashboard updates in real time", "Lapse disconnects bank links automatically")

html = html.replace(
    "Need help? See our <a href=\"/getting-started/\">Getting Started guide</a> or <a href=\"/how-to/\">Help Center</a>.",
    "Prefer no bank login? See <a href=\"/videos/import/\">Import Bank Data</a> or <a href=\"/videos/pocketbudjet/share-statements/\">Share Statements</a>. Full policy: <a href=\"/docs/pocketbudjet/HowWeMakeMoney.html\">How We Make Money</a>.",
)

# Remove budget-setup audio paths — use timer-only until VO recorded
html = re.sub(
    r"const audioPaths = \[.*?\];",
    "const audioPaths = [];",
    html,
    count=1,
    flags=re.DOTALL,
)

path.write_text(html, encoding="utf-8")
print("Patched", path)
