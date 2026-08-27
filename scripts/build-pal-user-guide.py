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
    # —— Welcome (0–4) ——
    T("Welcome to Pocket Allowance Ledger — or PAL for short. This is a how-to guide. It shows you what you can do in the app and how to do it, step by step.", HOME, "PAL Home"),
    T("Here is the basic idea. You, the parent, use the PAL app on your phone. Your kids use a simple web page on a Chromebook, tablet, or another device at home — on the same Wi-Fi as your phone.", HOME, "Parent and kid"),
    T("You set up jobs and rewards, tap Done when something is finished, and approve what kids report. Kids see their jobs in a browser, tap when they are done, and ask for rewards. You stay in charge.", HOME, "How the two sides work"),
    T("This guide uses a sample family named Reyes so you can follow along right away. The kids are Maya and Jacob. Later, when you set up your own household, you will pick your own family password and each child's PIN.", HOME, "Sample family Reyes"),
    T("Use the chapter buttons along the top to jump to a topic. Or press play and listen straight through. Previous and Next move one step at a time.", HOME, "Chapter buttons"),
    # —— Sample logins (5–8) ——
    T("Open the app. You should see the Reyes sample household on Home — today's jobs ready to mark done.", HOME, "Home with sample jobs"),
    T("For kid web practice, the sample family password is reyes — all lowercase. The sample PIN for both kids is one two three four. These are only for this sample. You can customize logins later when you set up your own family.", SET, "Sample password and PIN", tap(50, 72, "Guide", 1.4, 2.6)),
    T("If your iPhone asks for Local Network access, tap Allow. That lets kids reach the companion page on your home Wi-Fi. Keep the PAL app open on your phone while a kid is using the web page — if you leave the app, the connection pauses.", SET, "Local Network", tap(50, 68, "Allow", 1.2, 2.8)),
    T("Along the bottom of the parent app you will see five tabs: Home, Balances, Reports, Contracts, and Settings. We will walk through each one.", HOME, "Bottom tabs", tap(50, 94, "Tabs", 0.6, 3.0)),
    # —— First evening path (9–14) ——
    T("Here is a simple first path — the kind of evening flow most families use.", HOME, "First path"),
    T("First, on Home, look for a job with a big Done button. Tap Done when that job is finished. A gold coin animation shows the token was logged, and the child's balance updates.", HOME, "Tap Done", tap(50, 54, "Done", 1.0, 2.8)),
    T("Second, open Settings, then Kid web. Copy the link, or show the QR code, so a kid device can open the companion page on the same Wi-Fi.", SET, "Open Kid web", tap(50, 68, "Kid web", 1.2, 2.8)),
    T("On the kid page, sign in with the sample password reyes, choose Maya, enter PIN one two three four, then tap I did it on a job. That sends a report to you — it does not award the coin by itself.", KID, "Kid signs in and reports", tap(50, 62, "I did it!", 1.0, 2.8)),
    T("Third, back in the parent app, open Approvals. You will see the kid's report. Tap Approve to award the tokens, or Decline if it should not count.", APP, "Approve or decline", tap(50, 42, "Approve", 0.8, 2.8)),
    T("That loop — you mark jobs, kids report from the web page, you approve — is the heart of daily use. Everything else builds on it.", HOME, "Daily loop"),
    # —— Home (15–22) ——
    T("Home is your main evening screen. Today's jobs show as large Done buttons — one tap logs the behavior and awards a gold token.", HOME, "Home jobs", tap(50, 54, "Done", 1.0, 2.8)),
    T("Each row shows which child, what the job is called, and how many tokens it is worth. Maya's morning routine might be one token; other jobs can be different amounts.", HOME, "Job row details"),
    T("Try tapping Done on Maya's morning routine. Watch the coin land. That is your quick feedback that the job was logged.", HOME, "Coin feedback", tap(50, 54, "Done", 0.4, 2.5)),
    T("After you tap Done, Balances updates right away for work you logged yourself. When a kid reports from the web page, the coin waits until you approve it.", HOME, "When tokens land"),
    T("Sometimes PAL shows a tip on Home after you ease up how often a job pays. Behavior can get bumpier for a short time before it settles. The tip is a reminder to stay steady — not to pile on extra consequences.", HOME_QR, "Steady-through tip", tap(50, 38, "Tip", 1.2, 2.6)),
    T("You may also see suggestion cards on Home — for example, easing a schedule or encouraging saving. Read them if you like. Nothing changes unless you agree.", HOME, "Suggestion cards", tap(50, 72, "Suggestion", 1.4, 2.4)),
    T("PAL will not quietly change schedules or token amounts in the background. Any change needs your confirmation.", HOME, "You confirm changes"),
    T("When Home is empty of pending jobs, you are caught up for the day. You can still open other tabs anytime.", HOME, "Caught up"),
    # —— Balances (23–28) ——
    T("Open the Balances tab. Each child has tokens in hand — ready to spend — and tokens banked toward longer-term rewards.", BAL, "Balances", tap(50, 94, "Balances", 0.6, 2.4)),
    T("Think of two jars, not a bank account. In-hand is for sooner rewards. Banked is for bigger goals the child is saving toward.", BAL, "In hand and banked"),
    T("Tap a child's row to see recent token history and any saving tips for that child.", BAL, "Child detail", tap(50, 36, "Maya", 0.8, 2.4)),
    T("Under Balances you will also find wish-list style rewards. Kids can ask for those from the web page. You approve or decline the ask in Approvals.", BAL, "Wish list rewards"),
    T("Maya's sample row may show extra saving tips. Jacob's stays simpler. You can tune each child differently when you set up your own household.", BAL, "Different kids"),
    T("There are no sibling scoreboards or shame charts. Each child's tokens are their own.", BAL, "No scoreboards"),
    # —— Kid web (29–37) ——
    T("Kid web is how children use PAL without installing an app. They open a normal web page on a device that shares your home Wi-Fi.", SET, "What kid web is", tap(50, 68, "Kid web", 1.2, 2.8)),
    T("You stay in the parent app on your phone. Kids use the browser on a Chromebook, tablet, or phone. Same household — two screens.", SET, "Parent phone, kid browser"),
    T("Open Settings, then Kid web. When it is working, you will see Serving on your network, a kid browser link, and a QR code.", SET, "Kid web screen", tap(50, 58, "Copy link", 1.4, 2.6)),
    T("For a computer or Chromebook, tap Copy link, then paste that address into the browser address bar. Most PCs cannot scan a QR code — the copied link is the easy path.", SET, "Copy link for computers", tap(50, 72, "Copy link", 1.0, 2.4)),
    T("The QR code is for a phone or tablet that can open the camera and scan. Point the kid device at the code to open the same page. Many iPads can scan; a desktop usually cannot.", SET, "QR for phones and tablets"),
    T("Phone and kid device must be on the same home Wi-Fi. If the page will not load, check Wi-Fi, bring PAL back to the front on your phone, and try again.", SET, "Same Wi-Fi"),
    T("If you switch away from PAL or lock the phone for a long time, the kid page may stop responding until you open PAL again.", SET, "Keep PAL open"),
    T("You can return to Settings, then Kid web, anytime you need the link or QR again.", SET, "Find Kid web again"),
    T("Once the page loads, kids see a friendly sign-in — not a banking screen. Next we walk through what they do there.", KID, "Kid landing"),
    # —— Kid companion (38–45) ——
    T("On the kid sign-in screen, enter the family password. For the sample, type reyes in lowercase.", KID, "Family password", tap(50, 38, "Password", 0.8, 2.4)),
    T("Then tap the child's name — Maya or Jacob — and enter that child's PIN. Sample PIN is one two three four for both. Each kid only sees their own jobs and tokens.", KID, "Pick child and PIN", tap(50, 52, "Maya", 1.2, 2.4)),
    T("Remember: these sample logins are for practice. When you set up your own family, you choose your own password and PINs.", KID, "Customize later"),
    T("Jobs show as simple tasks. When a child finishes one, they tap I did it. That tells you they are done — the coin still waits for your approval.", KID, "I did it", tap(50, 62, "I did it!", 1.0, 2.8)),
    T("Kids usually see a quick thank-you on their screen when they tap I did it. That feels immediate for them, while you stay the final say.", KID, "Kid feedback", tap(50, 62, "I did it!", 0.4, 2.6)),
    T("From the kid page, a child can also ask for a reward from the wish list. That ask shows up in your Approvals. Nothing spends tokens until you approve.", KID, "Ask for a reward"),
    T("If two kids share one tablet, they can switch users after signing in with the family password. Each uses their own PIN.", KID, "More than one kid"),
    T("When you are done practicing on the kid page, switch back to the parent app for Approvals.", APP, "Back to parent app"),
    # —— Approvals (46–52) ——
    T("Open Approvals in the parent app. A badge count shows how many kid reports are waiting.", APP, "Approvals waiting", tap(50, 94, "Approvals", 0.6, 2.4)),
    T("Each item shows which child, which job, and when they reported. Read it, then decide.", APP, "Pending item"),
    T("Tap Approve to award the tokens. Tap Decline if it should not count — for example if the job was not really done.", APP, "Approve or decline", tap(50, 42, "Approve", 0.8, 2.8)),
    T("This is on purpose: kids learn to report honestly, and you verify. Tokens land after your confirmation.", APP, "Why approve"),
    T("Reward asks from the kid page show up here too. Approve spends from banked tokens toward that reward. Decline leaves the wish for later.", APP, "Reward asks", tap(50, 55, "Decline", 1.4, 2.4)),
    T("After you approve, Balances updates. The next time the kid refreshes their page, they see the new total.", APP, "After you approve"),
    T("If Approvals is empty, you are caught up — nothing waiting on you.", APP, "Empty Approvals"),
    # —— Reports (53–58) ——
    T("Open Reports to see how things are going over time — charts and short tips, not a scoreboard.", REP, "Reports", tap(50, 94, "Reports", 0.6, 2.4)),
    T("Insights can show how often jobs are getting done, and simple comparisons like the first week versus lately.", REP, "Insights", tap(50, 48, "Insights", 1.0, 2.6)),
    T("Trends looks further out. You may see gentle suggestions, like easing how often a job pays once it is going well.", REP_TREND, "Trends", tap(50, 32, "Trends", 0.8, 2.4)),
    T("Treat tips as optional advice. If PAL suggests changing a schedule, it will ask you to confirm. It will not change things on its own.", REP, "Tips need your OK"),
    T("That confirmation step is so you stay in charge of what your family does.", REP, "You stay in charge"),
    T("When you want a copy of your data for safekeeping, use Export backup in Settings — we cover that in a moment.", SET, "Backup coming up"),
    # —— Contracts (59–66) ——
    T("Open Contracts to see the jobs and routines set up for each child — what earns tokens and how often.", CON, "Contracts list", tap(50, 94, "Contracts", 0.6, 2.4)),
    T("Tap a contract to open its details — token amount, schedule, and any tips tied to that job.", CON, "Open a contract", tap(50, 44, "Contract", 0.8, 2.6)),
    T("Schedules can start more generous and then ease off as a habit sticks. Starting points follow the child's age as a default — you can change them to fit your home.", CON_DET, "Schedules", tap(50, 50, "Schedule", 1.0, 2.6)),
    T("If you ease a schedule, you might see a tip that behavior can get bumpier for a bit. That is normal for this kind of plan. Stay consistent through the bump.", CON_DET, "Bumpy after change"),
    T("Some contracts include gentle saving reminders — especially in Maya's sample. Jacob's sample stays simpler so you can compare.", CON_DET, "Saving tips"),
    T("Tap New contract when you want to add a job. You can start from a template — like morning routine or homework — or build one from scratch.", CON, "New contract", tap(88, 12, "New", 0.6, 2.4)),
    T("Set the name, who it is for, how many tokens, and the schedule. Save it, and it can show up on Home as a Done button.", CON, "Fill in a new job"),
    T("Archived contracts stay in history but stop appearing on Home. Use archive when a job is no longer active.", CON, "Archive"),
    # —— Settings (67–74) ——
    T("Settings is where you manage kids, kid web, help, and a local backup of your data.", SET, "Settings", tap(50, 94, "Settings", 0.6, 2.4)),
    T("Kids list lets you review each child's profile. Ages help pick starting schedules — they are starting points, not locked rules.", SET, "Kids list", tap(50, 42, "Kids", 1.0, 2.4)),
    T("Kid web, as we covered, is where you copy the link or show the QR so kids can open the companion page.", SET, "Kid web again", tap(50, 68, "Kid web", 1.2, 2.4)),
    T("Help points to support and this user guide. About shows the app version.", SET, "Help and About"),
    T("Export backup saves a zip of your contracts, tokens, and settings onto your phone. Passwords and PINs are not stored in that zip.", SET, "Export backup", tap(50, 78, "Export", 1.6, 2.4)),
    T("Restore from backup if you move to a new phone and want your household data back.", SET, "Restore backup"),
    T("Nothing in Settings silently rewrites schedules. If a change needs to happen, you will be asked for your confirmation.", SET, "Confirmation"),
    T("You now have the full loop: Home, Balances, kid web, Approvals, Reports, Contracts, and Settings.", HOME, "Full loop"),
    # —— Wrap (75–77) ——
    T("To practice again: mark a job Done on Home, open kid web for a child report, then clear Approvals. Use chapter buttons anytime to re-listen to a section.", HOME, "Practice again"),
    T("Questions or feedback: support at josspatech dot com.", HOME, "Support"),
    T("That is the PAL how-to. Jump to any chapter above whenever you need a refresher.", HOME, "End"),
]

CHAPTERS = [
    (0, "Welcome"),
    (5, "Sample logins"),
    (9, "First path"),
    (15, "Home"),
    (23, "Balances"),
    (29, "Kid web"),
    (38, "Kid companion"),
    (46, "Approvals"),
    (53, "Reports"),
    (59, "Contracts"),
    (67, "Settings"),
    (75, "Wrap-up"),
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
  <meta name="description" content="How to use Pocket Allowance Ledger — parent app and kid web on home Wi‑Fi. Step-by-step user guide with synced narration.">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://josspatech.com/videos/pal/user-guide/">
  <meta property="og:type" content="website">
  <meta property="og:title" content="Pocket Allowance Ledger — User Guide | JosspaTech">
  <meta property="og:description" content="How to use PAL day to day — Home, kid web, Approvals, Reports, and Contracts.">
  <meta property="og:url" content="https://josspatech.com/videos/pal/user-guide/">
  <meta property="og:site_name" content="JosspaTech">
  <meta property="og:image" content="https://josspatech.com/assets/brand/pal-app-icon.svg">
  <script>if(new URLSearchParams(location.search).get('embed')==='1')document.documentElement.classList.add('embed-mode');</script>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Source+Sans+3:wght@300;400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/videos/shared/walkthrough.css">
  <link rel="stylesheet" href="walkthrough.css?v=pal-howto-2026-08-26">
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
      <p class="subheader">{len(SLIDES)} steps with synced narration. Learn what you can do in PAL and how to do it — parent phone plus kids on a home Wi‑Fi browser.</p>
    </div>
  </div>
  <section class="user-manual walkthrough">
    <div class="container">
      <h2>Interactive User Guide</h2>
      <p class="section-sub">Tap a chapter to jump ahead, or press play. Previous and Next move one step. Tap any sentence in the transcript to jump there.</p>

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
      <h2>Need a hand?</h2>
      <p>Questions: support@josspatech.com.</p>
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
