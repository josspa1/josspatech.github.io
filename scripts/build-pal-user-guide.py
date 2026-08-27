#!/usr/bin/env python3
"""Build PAL unified user-guide index.html + narration-en.json (PBJ/HHH parity)."""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "videos" / "pal" / "user-guide"
INDEX = OUT_DIR / "index.html"
NARRATION_JSON = OUT_DIR / "narration-en.json"

ICON = "/assets/brand/pal-app-icon.svg"
HOME = "/assets/screenshots/pal/01-home.png"
HOME_QR = "/assets/screenshots/pal/01-home-quick-record.png"
BAL = "/assets/screenshots/pal/02-balances.png"
KID = "/assets/screenshots/pal/03-kid-web.png"
REP = "/assets/screenshots/pal/04-reports.png"
REP_TREND = "/assets/screenshots/pal/05-reports-trends.png"
CON = "/assets/screenshots/pal/06-contracts.png"
CON_DET = "/assets/screenshots/pal/07-contract-detail.png"
APP = "/assets/screenshots/pal/07-approvals.png"
SET = "/assets/screenshots/pal/08-settings.png"

# (narration, img, alt, tap dict or None)
# tap: x, y, label, show_at, duration — or None
def T(text, img=HOME, alt="PAL", tap=None):
    return {"n": text, "img": img, "alt": alt, "tap": tap}


def tap(x, y, label, show_at=1.0, dur=2.5):
    return {"x": x, "y": y, "label": label, "show_at": show_at, "dur": dur}


SLIDES: list[dict] = [
    # —— Welcome (0–3) ——
    T("Welcome to Pocket Allowance Ledger — PAL for short. This interactive user guide walks through every major parent and kid-web flow so you can run the app with confidence.", ICON, "PAL app icon"),
    T("PAL is a parent-managed token economy for ages six and up — local to the phone, with a kid companion on home Wi-Fi. It is not kid banking.", HOME, "Parent Home"),
    T("This guide uses a sample household named Reyes so you can follow along without setup. Kids Maya, about eight, and Jacob, about six.", HOME, "Home — Reyes sample"),
    T("When iOS asks for Local Network access, tap Allow — kid web requires it. Keep PAL in the foreground while a kid browser is connected; the local server pauses if the app is backgrounded.", SET, "Local Network permission", tap(50, 68, "Allow", 1.2, 2.8)),
    # —— Sample household (4–8) ——
    T("Open PAL. The sample Reyes household is already loaded — family name Reyes, two kids ready on Home.", HOME, "Home — Reyes"),
    T("Family password for kid web is reyes — lowercase. Kid PIN for both children is one-two-three-four. You can also find these in Settings under Reviewer guide.", SET, "Demo credentials", tap(50, 72, "Reviewer guide", 1.4, 2.6)),
    T("Use the chapter pills to jump ahead, or play straight through with synced narration. Previous and Next re-listen a single step.", ICON, "PAL chapters"),
    T("PAL stays on your device — no cloud sync required for the core token economy. PocketBudJet expense bridges are out of scope here.", SET, "Settings"),
    T("Next we open Settings for a quick orientation, then walk Home, Balances, kid web, Approvals, Reports, and Contracts.", SET, "Settings overview"),
    # —— Quick start (9–13) ——
    T("Open Settings from the gear icon or the Settings tab. Scroll to Reviewer guide for demo credentials and a short suggested path through the app.", SET, "Settings", tap(50, 88, "Settings", 0.8, 2.4)),
    T("Reviewer guide lists the sample household, suggested steps, design notes, and what PAL intentionally does not do.", SET, "Reviewer guide", tap(50, 55, "Reviewer guide", 1.0, 2.8)),
    T("Step one: Home — tap Done on a contract and confirm the coin lands in Balances.", HOME, "Home Done buttons", tap(50, 54, "Done", 1.0, 2.8)),
    T("Step two: Kid web — sign in with reyes, Maya, PIN one-two-three-four, then tap I did it on a job.", KID, "Kid web sign in", tap(50, 48, "Sign in", 1.0, 2.6)),
    T("Step three: Approvals — confirm or decline the kid report. Optional: request a reward from kid web and approve here.", APP, "Approvals", tap(50, 42, "Approve", 0.8, 2.6)),
    # —— Tab bar (14–17) ——
    T("The parent app has five bottom tabs: Home, Balances, Reports, Contracts, and Settings. Each tab maps to a major part of the token economy.", HOME, "Tab bar", tap(50, 94, "Tabs", 0.6, 3.0)),
    T("Home is where you tap Done on today's contracts — the core evening flow. Balances shows in-hand versus banked tokens per child.", HOME, "Home tab", tap(12, 94, "Home", 0.4, 2.0)),
    T("Reports holds charts, first-week versus now comparisons, and coaching nudges. Contracts lists behavioral contracts and thinning schedules.", REP, "Reports tab", tap(50, 94, "Reports", 1.8, 2.0)),
    T("Settings covers kid web, reviewer guide, kids list, backup export, and help. Nothing in Settings auto-changes schedules without your confirm.", SET, "Settings tab", tap(88, 94, "Settings", 2.2, 2.0)),
    # —— Home / Done (18–23) ——
    T("On Home, today's contracts appear as large Done buttons — one tap records the behavior and awards a gold token.", HOME, "Home contracts", tap(50, 54, "Done", 1.0, 2.8)),
    T("Each contract shows the child name, behavior label, and token amount. Maya's morning routine might be worth one token; evening jobs may differ.", HOME, "Contract row"),
    T("Tap Done on Maya's morning routine. Watch the coin animation land — immediate visual feedback for the parent.", HOME, "Tap Done", tap(50, 54, "Done", 0.4, 2.5)),
    T("After Done, tokens update immediately in Balances. Kids see feedback in the companion once you confirm their self-reports in Approvals.", HOME, "Coin animation"),
    T("Young contracts may show an extinction-burst callout on Home — coaching copy when behavior temporarily worsens after thinning. Read it as a heads-up to stay consistent, not to escalate.", HOME_QR, "Extinction burst callout", tap(50, 38, "Callout", 1.2, 2.6)),
    T("Personalization nudge cards may appear on Home — schedule thinning or saving-growth suggestions. Parents must confirm; PAL never auto-applies changes.", HOME, "Nudge card", tap(50, 72, "Nudge", 1.4, 2.4)),
    # —— Balances (24–28) ——
    T("Open the Balances tab. Each child shows in-hand tokens versus banked savings — two jars, not a bank account.", BAL, "Balances", tap(50, 94, "Balances", 0.6, 2.4)),
    T("Maya's row includes saving-growth maintenance operations in the demo — cadence coaching for bank deposits. Jacob's row stays simpler.", BAL, "Maya and Jacob balances", tap(50, 36, "Maya", 1.0, 2.6)),
    T("In-hand tokens are spendable now; banked tokens accumulate toward rewards. No sibling leaderboards or shame metrics — by design.", BAL, "In hand vs bank"),
    T("Tap a child row to see token history and saving cadence details. Interest accrual on banked tokens follows parent-configured rules.", BAL, "Child detail", tap(50, 36, "Maya", 0.8, 2.4)),
    T("Wish list items live under Balances — kids request rewards; parents approve redemptions in Approvals.", BAL, "Wish list"),
    # —— Kid web setup (29–35) ——
    T("Kid web runs on your home Wi-Fi only — not the public internet. Open Settings, then Kid web.", SET, "Settings", tap(50, 68, "Kid web", 1.2, 2.8)),
    T("PAL shows a LAN address and QR code when the local server is active. Phone and kid browser must share the same network.", SET, "Kid web LAN URL", tap(50, 58, "Copy link", 1.4, 2.6)),
    T("Tap Copy link and paste into a Chromebook or tablet browser on the same Wi-Fi. Or scan the QR code from the kid device camera.", SET, "Copy kid browser link", tap(50, 72, "Copy link", 1.0, 2.4)),
    T("Status reads Serving on your network when active. If PAL was backgrounded, reopen it — the server pauses until the parent app is foreground again.", SET, "Server status"),
    T("On iPhone, Local Network permission is required. If kid web fails to load, check Wi-Fi, foreground PAL, and that both devices are on the same subnet.", SET, "Troubleshooting kid web"),
    T("From Settings you can jump straight to Kid web whenever you need the LAN link or QR again.", SET, "Kid web screen"),
    T("Kids open the link once per browser session. The companion uses warm, kid-facing language — tokens and rewards, not banking UI.", KID, "Kid web landing"),
    # —— Kid companion (36–41) ——
    T("On the kid sign-in screen, enter family password reyes — lowercase.", KID, "Family password", tap(50, 38, "Password", 0.8, 2.4)),
    T("Tap Maya or Jacob, then enter PIN one-two-three-four. Each kid sees their own assignments and token balance.", KID, "Pick child", tap(50, 52, "Maya", 1.2, 2.4)),
    T("Assignments appear as friendly jobs — I did it confirms completion. Coins wait for parent approval; delayed verification is intentional.", KID, "Kid assignments", tap(50, 62, "I did it!", 1.0, 2.8)),
    T("Kids get immediate visual feedback when they tap I did it. You stay in control — nothing counts until you confirm in Approvals.", KID, "I did it tap", tap(50, 62, "I did it!", 0.4, 2.6)),
    T("From kid web, Maya can request a reward from her wish list. The request appears in parent Approvals — nothing auto-redeems.", KID, "Reward request"),
    T("Jacob's companion stays simpler in the demo — fewer saving-growth prompts. Compare whether age-appropriate defaults feel right.", KID, "Jacob view"),
    # —— Approvals (42–47) ——
    T("Switch back to the parent app. Open Approvals — badge count shows pending kid reports.", APP, "Approvals tab", tap(50, 94, "Approvals", 0.6, 2.4)),
    T("Each pending item shows the child, contract, and timestamp. Tap Approve to award tokens or Decline to send back without credit.", APP, "Pending report", tap(50, 42, "Approve", 0.8, 2.8)),
    T("Delayed verification path: kid self-report → parent Approvals. This mirrors token-economy practice — kids learn to report; parents verify.", APP, "Confirm or decline"),
    T("Reward requests from kid web appear here too. Approve deducts banked tokens; decline keeps the wish pending.", APP, "Reward approval", tap(50, 55, "Decline", 1.4, 2.4)),
    T("After approval, Balances updates and the kid companion reflects the new total on next refresh.", APP, "After approval"),
    T("Empty Approvals means everything is caught up — a good state on busy evenings.", APP, "Empty approvals"),
    # —— Reports (48–53) ——
    T("Open Reports for charts and coaching cards. Insights tab shows frequency trends and parent-facing schedule summaries.", REP, "Reports insights", tap(50, 94, "Reports", 0.6, 2.4)),
    T("First-week versus now comparison cards highlight behavior change over time so you can see progress at a glance.", REP, "First week vs now", tap(50, 48, "Insights", 1.0, 2.6)),
    T("Switch to Trends for longer-horizon charts. Thinning and saving-growth suggestions appear as nudges — parents must confirm.", REP_TREND, "Reports trends", tap(50, 32, "Trends", 0.8, 2.4)),
    T("Coaching cards use plain, literature-first language. Read them as optional suggestions — nothing changes until you confirm.", REP, "Coaching card"),
    T("Reports never auto-applies schedule changes. Every thinning or cadence adjustment requires explicit parent confirm.", REP, "Parent confirm gate"),
    T("Export from Settings if you need a local backup zip — no secrets are included in the archive.", REP, "Reports overview"),
    # —— Contracts (54–61) ——
    T("Open Contracts to review seeded behavioral contracts. Each lists behavior name, token amount, and schedule type.", CON, "Contracts list", tap(50, 94, "Contracts", 0.6, 2.4)),
    T("Tap a contract to open detail — thinning schedules, extinction-burst coaching on young contracts, and maintenance operations.", CON, "Contract row", tap(50, 44, "Contract", 0.8, 2.6)),
    T("Contract detail shows token amount, target frequency, and thinning ladder. Age bands set developmental defaults only — not permanent law.", CON_DET, "Contract detail", tap(50, 50, "Schedule", 1.0, 2.6)),
    T("Extinction-burst callouts on young contracts explain temporary behavior spikes after schedule changes — stay consistent through the bump.", CON_DET, "Extinction burst coaching"),
    T("Saving-growth maintenance operations on Maya's contracts demonstrate cadence coaching — Jacob's contracts stay simpler.", CON_DET, "Saving cadence"),
    T("Tap New contract to start from a template or from scratch. Wizard steps mirror behavioral contract best practices.", CON, "New contract", tap(88, 12, "New", 0.6, 2.4)),
    T("Templates include morning routine, homework block, and chore ladders — customize token amounts and schedules per child.", CON, "Contract templates"),
    T("Archived contracts remain readable for history but stop appearing on Home Done buttons.", CON, "Archived contracts"),
    # —— Settings / backup (62–67) ——
    T("Settings holds Kids list, Kid web, Reviewer guide, Help, About, and local backup export.", SET, "Settings hub", tap(50, 94, "Settings", 0.6, 2.4)),
    T("Kids list lets you review Maya and Jacob profiles — ages drive default schedules, not fixed rules.", SET, "Kids list", tap(50, 42, "Kids", 1.0, 2.4)),
    T("Help links to support email and this user guide. About shows version and design notes.", SET, "Help and About"),
    T("Export backup creates a local zip of contracts, tokens, and settings you control. No cloud sync required for everyday use.", SET, "Backup export", tap(50, 78, "Export", 1.6, 2.4)),
    T("Restore from backup on a new phone if you want to bring your household data with you.", SET, "Restore backup"),
    T("Open Kid web anytime you need the LAN URL or QR for a tablet or Chromebook on the same Wi-Fi.", SET, "Open Kid web link", tap(50, 68, "Kid web", 1.2, 2.4)),
    # —— Design notes (68–73) ——
    T("PAL uses token-economy language, not chore-tracker gamification. No streaks, leaderboards, or shame metrics.", HOME, "Design — language"),
    T("Schedule thinning and saving cadence appear as age priors plus performance nudges plus parent confirm — you stay in charge of every change.", REP, "Design — thinning"),
    T("Delayed verification is intentional: kid reports, parent confirms, then tokens land. That keeps parents in the loop.", APP, "Design — verification"),
    T("Extinction-burst coaching on Home and Contracts helps you stay consistent when behavior temporarily spikes after a schedule change.", HOME_QR, "Design — extinction burst"),
    T("Age bands are developmental defaults only — adjust schedules and reinforcers to fit your household.", SET, "Design — age bands"),
    T("Literature-first with room for real-family flexibility when household means require different reinforcer delivery.", SET, "Design boundary"),
    # —— Out of scope (74–76) ——
    T("PAL does not include debit or banking, a chatbot coach, cloud sync, ages under six, or a PocketBudJet expense bridge.", SET, "Out of scope list"),
    T("PAL is not kid banking — no real money, no debit cards. Tokens are symbolic reinforcers managed entirely by the parent.", ICON, "Not kid banking"),
    T("Questions or feedback: support at josspatech dot com.", ICON, "Feedback"),
    # —— Thank you (77) ——
    T("Thanks for watching. This guide lives at josspatech dot com slash videos slash pal slash user-guide. Tap any chapter pill to re-listen a section.", ICON, "Thank you"),
]

CHAPTERS = [
    (0, "Welcome"),
    (4, "Sample household"),
    (9, "Quick start"),
    (14, "Tab bar"),
    (18, "Home"),
    (24, "Balances"),
    (29, "Kid web"),
    (36, "Kid companion"),
    (42, "Approvals"),
    (48, "Reports"),
    (54, "Contracts"),
    (62, "Settings"),
    (68, "Design notes"),
    (74, "Out of scope"),
    (77, "Thank you"),
]


def slide_html(i: int, s: dict) -> str:
    tap = s.get("tap")
    attrs = f'data-index="{i}"'
    if tap:
        attrs += (
            f' data-tap-x="{tap["x"]}" data-tap-y="{tap["y"]}"'
            f' data-tap-label="{html.escape(tap["label"])}"'
            f' data-tap-show-at="{tap["show_at"]}" data-tap-duration="{tap["dur"]}"'
        )
    else:
        attrs += ' data-tap-none'
    loading = "eager" if i < 3 else "lazy"
    active = ' active' if i == 0 else ''
    return (
        f'                  <div class="slide{active}" {attrs}>\n'
        f'                    <img src="{s["img"]}" alt="{html.escape(s["alt"])}" loading="{loading}">\n'
        f'                  </div>\n'
    )


def chapter_buttons() -> str:
    lines = []
    for idx, (start, label) in enumerate(CHAPTERS):
        active = ' active' if idx == 0 else ''
        lines.append(
            f'        <button type="button" class="chapter-btn{active}" data-slide="{start}">{html.escape(label)}</button>'
        )
    return "\n".join(lines)


def narration_js_array() -> str:
    parts = [json.dumps(s["n"], ensure_ascii=False) for s in SLIDES]
    return "[\n    " + ",\n    ".join(parts) + "\n  ]"


def build_index() -> str:
    n = len(SLIDES) - 1
    chapter_starts = [str(c[0]) for c in CHAPTERS]
    slides_html = "".join(slide_html(i, s) for i, s in enumerate(SLIDES))

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Pocket Allowance Ledger — User Guide | JosspaTech</title>
  <meta name="description" content="Interactive PAL user guide — sample household, kid web on home Wi‑Fi, parent core flow through Contracts. {len(SLIDES)} slides with synced narration.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://josspatech.com/videos/pal/user-guide/">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Pocket Allowance Ledger — User Guide | JosspaTech">
  <meta property="og:description" content="Interactive PAL user guide — Home through Contracts, kid web, Approvals, and Reports with synced narration.">
  <meta property="og:url" content="https://josspatech.com/videos/pal/user-guide/">
  <meta property="og:site_name" content="JosspaTech">
  <meta property="og:image" content="https://josspatech.com/assets/brand/pal-app-icon.svg">
  <script>if(new URLSearchParams(location.search).get('embed')==='1')document.documentElement.classList.add('embed-mode');</script>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Sans+3:wght@300;400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/videos/shared/walkthrough.css">
  <link rel="stylesheet" href="walkthrough.css?v=pal-ug-2026-08-26">
  <link rel="stylesheet" href="/videos/shared/site-chrome.css?v=chrome-2026-07-28">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{ font-family: 'Source Sans 3', sans-serif; line-height: 1.6; background: var(--white); color: var(--navy); }}
    :root {{
      --navy: #1A4F7A; --navy-dark: #1A120E; --navy-medium: #2E6FA3;
      --gold: #E8B84A; --gold-dark: #C8942E;
      --slate: #5A7A9A; --slate-light: #8AAABB;
      --background: #F5EDE4; --white: #FFFFFF;
    }}
    nav {{ position: sticky; top: 0; z-index: 1000; padding: 1rem 2rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); background-color: var(--navy-dark); }}
    nav .container {{ max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; }}
    nav .logo {{ font-family: 'Playfair Display', serif; font-size: 1.5rem; font-weight: 700; color: var(--white); text-decoration: none; }}
    nav .nav-links {{ display: flex; gap: 1.5rem; align-items: center; list-style: none; flex-wrap: wrap; }}
    nav .nav-links a {{ color: var(--white); text-decoration: none; font-weight: 500; font-size: 0.95rem; }}
    nav .nav-links a:hover {{ color: var(--gold); }}
    .breadcrumbs {{ max-width: 1200px; margin: 0 auto; padding: 1rem 2rem 0; font-size: 0.95rem; color: var(--slate); }}
    .breadcrumbs a {{ color: var(--navy-medium); text-decoration: underline; text-decoration-color: var(--gold); text-underline-offset: 4px; font-weight: 700; }}
    .breadcrumbs span.sep {{ margin: 0 0.45rem; color: var(--slate-light); }}
    .breadcrumbs span.current {{ color: var(--navy); font-weight: 700; }}
    .hero {{ color: var(--white); padding: 2rem; text-align: center; background: linear-gradient(135deg, #1A120E 0%, #1A4F7A 100%); }}
    .hero h1 {{ font-family: 'Playfair Display', serif; font-size: clamp(1.8rem, 4vw, 2.5rem); font-weight: 900; margin-bottom: 0.75rem; }}
    .hero .subheader {{ font-size: 1.05rem; max-width: 760px; margin: 0 auto; opacity: 0.95; line-height: 1.55; }}
    .walkthrough {{ padding: 3rem 2rem; background: var(--background); }}
    .walkthrough .container {{ max-width: 1200px; margin: 0 auto; }}
    .walkthrough h2 {{ font-family: 'Playfair Display', serif; font-size: 2rem; text-align: center; margin-bottom: 0.5rem; color: var(--navy); }}
    .walkthrough .section-sub {{ text-align: center; color: var(--slate); margin-bottom: 1.5rem; max-width: 820px; margin-left: auto; margin-right: auto; }}
    .phone-frame {{ width: 300px; border: 3px solid var(--navy-dark); border-radius: 24px; overflow: hidden; background: #000; aspect-ratio: 9/19.5; position: relative; box-shadow: 0 16px 48px rgba(26,18,14,0.22); }}
    .slideshow {{ width: 100%; height: 100%; position: relative; }}
    .slide {{ position: absolute; inset: 0; opacity: 0; transition: opacity 0.6s; }}
    .slide.active {{ opacity: 1; }}
    .slide img {{ width: 100%; height: 100%; object-fit: contain; display: block; }}
    .cta-section {{ padding: 3rem 2rem; text-align: center; color: white; background: linear-gradient(135deg, #1A120E 0%, #1A4F7A 100%); }}
    .cta-section h2 {{ font-family: 'Playfair Display', serif; font-size: 2rem; margin-bottom: 0.75rem; }}
    .cta-section p {{ max-width: 640px; margin: 0 auto 1.25rem; opacity: 0.9; line-height: 1.6; }}
    .download-button {{ display: inline-block; padding: 0.9rem 2rem; border-radius: 6px; font-weight: 700; text-decoration: none; margin: 0.35rem; background: var(--gold); color: var(--navy-dark); border: 2px solid var(--gold); }}
    .download-button:hover {{ background: var(--gold-dark); }}
    .download-button.ghost {{ background: transparent; color: var(--gold); }}
    footer {{ padding: 2rem; text-align: center; color: white; font-size: 0.9rem; background: var(--navy-dark); }}
    footer a {{ color: var(--gold); }}
    @media (max-width: 768px) {{
      nav .nav-links {{ gap: 0.75rem; font-size: 0.85rem; }}
      .walkthrough {{ padding: 2rem 1rem; }}
    }}
  </style>
</head>
<body data-jt-product="pal">
  <nav>
    <div class="container">
      <a href="/" class="logo">JosspaTech</a>
      <ul class="nav-links">
        <li><a href="/">Home</a></li>
        <li><a href="/#pal">Pocket Allowance Ledger</a></li>
        <li><a href="/videos/pal/">PAL Videos</a></li>
        <li><a href="/how-to/">How To</a></li>
      </ul>
    </div>
  </nav>
  <div class="breadcrumbs" aria-label="Breadcrumb">
    <a href="/">Home</a><span class="sep">/</span>
    <a href="/#pal">Pocket Allowance Ledger</a><span class="sep">/</span>
    <a href="/videos/pal/">Videos</a><span class="sep">/</span>
    <span class="current">User Guide</span>
  </div>
  <div class="hero">
    <div class="container">
      <h1>Pocket Allowance Ledger — User Guide</h1>
      <p class="subheader">{len(SLIDES)} interactive slides with synced narration, gold tap guides, and chapter jumps. Parent app plus kid web on home Wi‑Fi — how to use PAL day to day.</p>
    </div>
  </div>
  <section class="user-manual walkthrough">
    <div class="container">
      <h2>Interactive User Guide</h2>
      <p class="section-sub">{len(SLIDES)} slides with synced narration and gold tap guides — Welcome through Contracts and kid web. Use the {len(CHAPTERS)} chapter pills to jump ahead, Previous/Next (or ← →) to re-listen a step, or tap any sentence in the transcript.</p>

      <div class="chapter-nav" id="chapterNav">
{chapter_buttons()}
      </div>

      <div class="user-manual-stage walkthrough-stage">
        <div class="video-wrapper">
          <div class="phone-column">
            <div class="phone-viewport">
              <div class="phone-frame">
                <div class="slideshow" id="slideshow">
                  <div class="tap-to-start" id="tapToStart">
                    <div class="tap-to-start-icon">&#9654;</div>
                    <div class="tap-to-start-label">Tap to play</div>
                  </div>
{slides_html}
                </div>
              </div>
            </div>
            <div class="progress-dots" id="dots"></div>
            <div class="playback-controls">
              <button type="button" class="nav-step-btn" id="prevBtn" title="Previous step" aria-label="Previous step">&#9664;</button>
              <button type="button" class="voice-btn" id="voiceBtn" title="Toggle narration" aria-label="Toggle narration">&#128266;</button>
              <button type="button" class="play-pause-btn" id="playPauseBtn" title="Play/Pause">&#9654;</button>
              <button type="button" class="nav-step-btn" id="nextBtn" title="Next step" aria-label="Next step">&#9654;&#9654;</button>
              <span class="speed-label" id="speedLabel">Tap play to start</span>
            </div>
          </div>
          <div class="narration-panel" id="narrationPanel">
            <div class="narration-panel-heading">Transcript</div>
            <div class="transcript-body" id="transcriptBody"></div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section class="cta-section">
    <div class="container">
      <h2>Ready to run a home token economy?</h2>
      <p>Questions or feedback: support@josspatech.com. Prefer notes on wording, timing, and what a parent might misuse — over feature wishlists.</p>
      <a href="mailto:support@josspatech.com?subject=PAL%20user%20guide" class="download-button">Email support</a>
      <a href="/#pal" class="download-button ghost">Back to PAL product page</a>
    </div>
  </section>

  <footer class="jt-site-footer">
    <ul class="jt-products" aria-label="JosspaTech products">
      <li><a href="/">Home</a></li>
      <li><a href="/#pbj">PocketBudJet</a></li>
      <li><a href="/#hhh">Handy Horology Helper</a></li>
      <li><a href="/#pal">Pocket Allowance Ledger</a></li>
      <li><a href="/#cvc">Curator's Vault: Classics</a></li>
    </ul>
    <p class="jt-copy">&copy; 2026 JosspaTech. All Rights Reserved.</p>
    <p class="jt-legal"><a href="mailto:support@josspatech.com">support@josspatech.com</a></p>
  </footer>

  <script>
  const NARRATION = {narration_js_array()};
  const CHAPTER_STARTS = [{", ".join(chapter_starts)}];
  const LAST_SLIDE = {n};
  const AUDIO_BASE = 'audio/';
  </script>
  <script src="/videos/shared/walkthrough.js?v=pal-ug-2026-08-26" defer></script>
  <script src="deck.js?v=pal-ug-2026-08-26" defer></script>
  <script src="/scripts/site-analytics-saas.js" defer></script>
</body>
</html>
"""


def main() -> None:
    narration = [s["n"] for s in SLIDES]
    NARRATION_JSON.write_text(json.dumps(narration, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    INDEX.write_text(build_index(), encoding="utf-8")
    print(f"Built {INDEX} — {len(SLIDES)} slides, {len(CHAPTERS)} chapters, {INDEX.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
