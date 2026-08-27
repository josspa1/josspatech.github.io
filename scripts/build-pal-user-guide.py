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
    T("Welcome to Pocket Allowance Ledger — PAL for short. This guide shows you how to use the app day to day.", HOME, "PAL Home"),
    T("You use the PAL app on your phone. Your kids use a web page on a Chromebook, tablet, or phone at home — on the same Wi-Fi as your phone.", HOME, "Parent phone and kid page"),
    T("On your phone you mark jobs done, check balances, and approve what kids send you. On their screen kids see their jobs, tap when finished, and ask for rewards.", HOME, "Who does what"),
    T("This walkthrough uses a sample family named Reyes — kids Maya and Jacob — so you can try the steps right away. When you set up your own family, you choose your own password and each child's PIN.", HOME, "Sample family"),
    T("Along the top, tap a chapter button to jump ahead. Or press play and listen straight through. Previous and Next move one step.", HOME, "How to navigate this guide"),
    # —— Find your way (5–9) ——
    T("Open PAL. The bottom of the screen has five tabs: Record, Reports, Balances, Approvals, and Contracts.", HOME, "Bottom tabs", tap(50, 94, "Tabs", 0.6, 3.0)),
    T("Record is the Home screen — today's jobs with big Done buttons. That is where most evenings start.", HOME, "Record tab is Home", tap(12, 94, "Record", 0.4, 2.0)),
    T("Settings is not a bottom tab. Tap the gear icon to open Settings — kids, kid web, help, and backup live there.", SET, "Gear opens Settings", tap(88, 8, "Gear", 0.8, 2.4)),
    T("For practice, the sample family password is reyes — all lowercase. The sample PIN for Maya and Jacob is one two three four. When you set up your own family, you pick your own logins.", SET, "Sample password and PIN", tap(50, 72, "Guide", 1.4, 2.6)),
    T("If your iPhone asks for Local Network permission, tap Allow. That lets the kid web page reach your phone on home Wi-Fi. Keep PAL open while a kid is using that page.", SET, "Allow Local Network", tap(50, 68, "Allow", 1.2, 2.8)),
    # —— First evening (10–16) ——
    T("Here is a simple first evening — three steps you will use often.", HOME, "First evening"),
    T("Step one. On Record, find a job with a Done button. When the job is finished, tap Done. You should see a gold coin, and that child's balance goes up.", HOME, "Tap Done", tap(50, 54, "Done", 1.0, 2.8)),
    T("Step two. Open Settings with the gear, then tap Kid web. You will see a link and a QR code for the kid page.", SET, "Open Kid web", tap(50, 68, "Kid web", 1.2, 2.8)),
    T("On a computer or Chromebook, tap Copy link, then paste the address into the browser. Most PCs cannot scan a QR code.", SET, "Copy link for a computer", tap(50, 72, "Copy link", 1.0, 2.4)),
    T("On a phone or tablet, the child can scan the QR code with the camera if the device supports it. Many iPads can. Same Wi-Fi as your phone either way.", SET, "QR for phones and tablets"),
    T("On the kid page, type password reyes, tap Maya, enter PIN one two three four, then tap I did it on a job. That sends you a report. It does not add the coin by itself.", KID, "Kid reports a job", tap(50, 62, "I did it!", 1.0, 2.8)),
    T("Step three. Back on your phone, open the Approvals tab. Tap Approve to give the tokens, or Decline if the job should not count.", APP, "Approve the report", tap(50, 42, "Approve", 0.8, 2.8)),
    # —— Record / Home (17–23) ——
    T("Let's look closer at Record — your main evening screen. Today's jobs appear as large Done buttons.", HOME, "Record screen", tap(50, 54, "Done", 1.0, 2.8)),
    T("Each row shows the child's name, the job name, and how many tokens it is worth. You can set different amounts for different jobs.", HOME, "What each job shows"),
    T("Tap Done on Maya's morning routine. Watch the coin appear. That means the job was marked done and the tokens were added.", HOME, "Watch the coin", tap(50, 54, "Done", 0.4, 2.5)),
    T("When you tap Done yourself, Balances updates right away. When a kid taps I did it on their page, the tokens wait in Approvals until you say yes.", HOME, "When tokens appear"),
    T("Sometimes a tip appears on Home after you pay a job less often. It may say things can get bumpier for a little while. Stay steady — you do not need to add extra punishments.", HOME_QR, "Tip after a change", tap(50, 38, "Tip", 1.2, 2.6)),
    T("You may also see suggestion cards — for example, paying a job less often once it is going well, or encouraging saving. Read them if you want. Nothing changes unless you agree.", HOME, "Suggestion cards", tap(50, 72, "Suggestion", 1.4, 2.4)),
    T("When there are no Done buttons left for today, you are caught up. You can still open any other tab.", HOME, "Caught up for today"),
    # —— Balances (24–29) ——
    T("Open the Balances tab. Each child shows tokens in hand and tokens banked.", BAL, "Balances tab", tap(50, 94, "Balances", 0.6, 2.4)),
    T("In hand means ready for a sooner reward. Banked means saved toward a bigger goal. Think of two jars for each child.", BAL, "In hand and banked"),
    T("Tap a child's name to see recent token history and any saving tips for that child.", BAL, "Open a child", tap(50, 36, "Maya", 0.8, 2.4)),
    T("Wish-list rewards live here too. Kids can ask for them from the kid page. You approve or decline those asks under Approvals.", BAL, "Wish list"),
    T("In the sample, Maya may show more saving tips than Jacob. You can set each child differently when you set up your own family.", BAL, "Different kids"),
    T("Each child's tokens stay with that child.", BAL, "Separate totals"),
    # —— Kid web (30–37) ——
    T("Kid web is the page kids use. They do not install an app. They open a normal browser on a device that shares your home Wi-Fi.", SET, "What kid web is", tap(50, 68, "Kid web", 1.2, 2.8)),
    T("You stay in the PAL app on your phone. Kids use Chrome, Safari, or another browser on their device. Same home — two screens.", SET, "Two screens"),
    T("In Settings, open Kid web. When it is ready, the screen says Serving on your network. You will see the kid browser link and a QR code.", SET, "Kid web ready", tap(50, 58, "Copy link", 1.4, 2.6)),
    T("For a computer or Chromebook: tap Copy link, open the browser, paste into the address bar, and go.", SET, "Paste the link", tap(50, 72, "Copy link", 1.0, 2.4)),
    T("For a phone or tablet with a camera: open the camera or QR scanner, point at the code, and open the page. Desktops usually cannot do this — use Copy link instead.", SET, "Scan the QR code"),
    T("Both devices must be on the same home Wi-Fi. If the page will not load, check Wi-Fi, open PAL again on your phone, and retry the link.", SET, "Same Wi-Fi"),
    T("If you leave PAL or lock the phone for a long time, the kid page may stop working until you bring PAL back to the front.", SET, "Keep PAL open"),
    T("Need the link again later? Settings, then Kid web.", SET, "Find it again"),
    # —— Kid page (38–45) ——
    T("On the kid sign-in screen, enter the family password. For the sample, type reyes in lowercase.", KID, "Enter family password", tap(50, 38, "Password", 0.8, 2.4)),
    T("Tap the child's name — Maya or Jacob — then enter that child's PIN. Sample PIN is one two three four. Each child only sees their own jobs and tokens.", KID, "Pick child and PIN", tap(50, 52, "Maya", 1.2, 2.4)),
    T("These sample logins are only for practice. When you set up your own family, you choose your own password and PINs.", KID, "Your own logins later"),
    T("Jobs appear as simple tasks. When a child finishes one, they tap I did it. That tells you they are done. The coin still waits for you in Approvals.", KID, "Tap I did it", tap(50, 62, "I did it!", 1.0, 2.8)),
    T("After I did it, the kid page usually shows a quick thank-you. On your phone, open Approvals to finish the step.", KID, "What the kid sees", tap(50, 62, "I did it!", 0.4, 2.6)),
    T("A child can also ask for a reward from the wish list. That ask appears under Approvals on your phone. Tokens are not spent until you approve.", KID, "Ask for a reward"),
    T("If two kids share one tablet, sign in with the family password, then each child uses their own name and PIN.", KID, "Two kids, one tablet"),
    T("When you are done on the kid page, go back to the Approvals tab on your phone.", APP, "Back to Approvals"),
    # —— Approvals (46–51) ——
    T("Open the Approvals tab. A number on the tab shows how many kid reports are waiting.", APP, "Approvals tab", tap(50, 94, "Approvals", 0.6, 2.4)),
    T("Each item shows which child, which job, and when they reported. Read it, then decide.", APP, "Read the report"),
    T("Tap Approve to add the tokens. Tap Decline if the job should not count — for example if it was not really finished.", APP, "Approve or Decline", tap(50, 42, "Approve", 0.8, 2.8)),
    T("Reward asks from the kid page show up here too. Approve spends banked tokens toward that reward. Decline leaves the wish for later.", APP, "Reward asks", tap(50, 55, "Decline", 1.4, 2.4)),
    T("After you approve, Balances updates. When the kid refreshes their page, they see the new total.", APP, "After Approve"),
    T("If Approvals is empty, nothing is waiting on you.", APP, "Nothing waiting"),
    # —— Reports (52–56) ——
    T("Open the Reports tab to see how jobs are going over days and weeks — simple charts and short tips.", REP, "Reports tab", tap(50, 94, "Reports", 0.6, 2.4)),
    T("Insights can show how often jobs get done, and compare early days with lately.", REP, "Insights", tap(50, 48, "Insights", 1.0, 2.6)),
    T("Trends looks further out. You may see a suggestion to pay a job less often once it is going well.", REP_TREND, "Trends", tap(50, 32, "Trends", 0.8, 2.4)),
    T("Tips are optional. If PAL suggests changing a schedule, it asks you first. It will not change schedules by itself.", REP, "You agree first"),
    T("To save a copy of your data on your phone, use Export backup in Settings — next section.", SET, "Backup next"),
    # —— Contracts (57–64) ——
    T("Open the Contracts tab. This is the list of jobs and routines for each child — what earns tokens and how often.", CON, "Contracts tab", tap(50, 94, "Contracts", 0.6, 2.4)),
    T("Tap a job to open its details — how many tokens, how often it pays, and any tips for that job.", CON, "Open a job", tap(50, 44, "Job", 0.8, 2.6)),
    T("A new job can pay often at first, then less often as the habit sticks. Starting amounts follow the child's age as a starting point — you can change them.", CON_DET, "How often it pays", tap(50, 50, "Schedule", 1.0, 2.6)),
    T("If you pay a job less often, you might see a tip that things can get bumpier for a short time. Keep the plan steady through that stretch.", CON_DET, "After you change how often"),
    T("Some jobs include saving reminders. In the sample, Maya may have more of these than Jacob.", CON_DET, "Saving reminders"),
    T("Tap New when you want to add a job. Start from a template — morning routine or homework — or make one from scratch.", CON, "Add a job", tap(88, 12, "New", 0.6, 2.4)),
    T("Enter the name, which child, how many tokens, and how often. Save it. It can then show up on Record with a Done button.", CON, "Fill in and save"),
    T("Archive a job when you no longer want it on Record. It stays in history but stops showing Done buttons.", CON, "Archive a job"),
    # —— Settings (65–73) ——
    T("Open Settings with the gear icon. Here you manage kids, kid web, help, and a backup of your data.", SET, "Settings", tap(88, 8, "Gear", 0.6, 2.4)),
    T("Kids list shows each child's profile. Age helps pick starting schedules. You can change those schedules to fit your home.", SET, "Kids list", tap(50, 42, "Kids", 1.0, 2.4)),
    T("Kid web is where you copy the link or show the QR so kids can open their page.", SET, "Kid web again", tap(50, 68, "Kid web", 1.2, 2.4)),
    T("Help points to support and this user guide. About shows the app version number.", SET, "Help and About"),
    T("Export backup saves your jobs, tokens, and settings into a file on your phone. Passwords and PINs are not put in that file.", SET, "Export backup", tap(50, 78, "Export", 1.6, 2.4)),
    T("Use Restore if you move to a new phone and want your household data back.", SET, "Restore backup"),
    T("If PAL wants to change a schedule, it will ask for your confirmation first. It does not change schedules quietly in the background.", SET, "Ask first"),
    T("You have now seen Record, Balances, kid web, Approvals, Reports, Contracts, and Settings.", HOME, "What you covered"),
    T("To practice the main loop again: tap Done on Record, have a kid tap I did it, then Approve on Approvals.", HOME, "Practice the loop"),
    # —— Wrap (74–77) ——
    T("Use the chapter buttons anytime to jump back to a section.", HOME, "Jump anytime"),
    T("Questions: email support at josspatech dot com.", HOME, "Support"),
    T("That is how to use PAL. Open any chapter above when you need a refresher.", HOME, "End"),
    T("Thanks for watching.", HOME, "Thanks"),
]

CHAPTERS = [
    (0, "Welcome"),
    (5, "Find your way"),
    (10, "First evening"),
    (17, "Record"),
    (24, "Balances"),
    (30, "Kid web"),
    (38, "Kid page"),
    (46, "Approvals"),
    (52, "Reports"),
    (57, "Contracts"),
    (65, "Settings"),
    (74, "Wrap-up"),
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
  <link rel="stylesheet" href="walkthrough.css?v=pal-howto-2026-08-27">
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
