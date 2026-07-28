#!/usr/bin/env python3
"""Ensure every user-guide page has shared site chrome (header products, breadcrumbs, footer).

Also fixes: shared sticky cage, HHH deck idle sentence highlight, cache bust.
Does NOT restore from backup or retranslate locales.
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUST = "chrome-2026-07-28"
CODES = ["de", "es", "fr", "hi", "it", "pt", "zh"]

NAV_HHH = """           <ul class="nav-links">
            <li><a href="/">Home</a></li>
            <li><a href="/#hhh">Handy Horology Helper</a></li>
            <li><a href="/#pbj">PocketBudJet</a></li>
            <li><a href="/#pal">Pocket Allowance Ledger</a></li>
            <li><a href="/#cvc">Curator's Vault</a></li>
            <li><a href="/docs/handyhorology/HandyHorology_UserGuide.pdf">PDF</a></li>
           </ul>"""

NAV_PBJ = """ <ul class="nav-links">
 <li><a href="/">Home</a></li>
 <li><a href="/#pbj">PocketBudJet</a></li>
 <li><a href="/#hhh">Handy Horology Helper</a></li>
 <li><a href="/#pal">Pocket Allowance Ledger</a></li>
 <li><a href="/#cvc">Curator's Vault</a></li>
 <li><a href="/how-to/">How To</a></li>
 </ul>"""

CRUMB_HHH = """         <div class="breadcrumbs" aria-label="Breadcrumb">
          <a href="/">Home</a><span class="sep">/</span>
          <a href="/#hhh">Handy Horology Helper</a><span class="sep">/</span>
          <span class="current">User Manual</span>
         </div>"""

CRUMB_PBJ = """ <div class="breadcrumbs" aria-label="Breadcrumb">
 <a href="/">Home</a><span class="sep">/</span>
 <a href="/#pbj">PocketBudJet</a><span class="sep">/</span>
 <span class="current">User Manual</span>
 </div>"""

FOOTER = """         <footer class="jt-site-footer">
          <ul class="jt-products" aria-label="JosspaTech products">
           <li><a href="/">Home</a></li>
           <li><a href="/#pbj">PocketBudJet</a></li>
           <li><a href="/#hhh">Handy Horology Helper</a></li>
           <li><a href="/#pal">Pocket Allowance Ledger</a></li>
           <li><a href="/#cvc">Curator's Vault: Classics</a></li>
          </ul>
          <p class="jt-copy">&copy; 2026 JosspaTech. All Rights Reserved.</p>
          <p class="jt-legal">
           <a href="mailto:support@josspatech.com">support@josspatech.com</a>
          </p>
         </footer>"""


def ensure_body_product(html: str, product: str) -> str:
    if re.search(r"<body[^>]*data-jt-product=", html):
        return re.sub(
            r'(<body[^>]*data-jt-product=")[^"]*(")',
            rf"\1{product}\2",
            html,
            count=1,
        )
    return re.sub(r"<body([^>]*)>", rf'<body data-jt-product="{product}"\1>', html, count=1)


def ensure_chrome_assets(html: str) -> str:
    # site-chrome.css in <head>
    if "site-chrome.css" not in html.split("</head>", 1)[0]:
        html = html.replace(
            "</head>",
            f' <link rel="stylesheet" href="/videos/shared/site-chrome.css?v={BUST}">\n</head>',
            1,
        )
    else:
        html = re.sub(
            r'href="/videos/shared/site-chrome\.css[^"]*"',
            f'href="/videos/shared/site-chrome.css?v={BUST}"',
            html,
        )

    # site-chrome.js before </body> or after deck
    if "site-chrome.js" not in html:
        html = html.replace(
            "</body>",
            f' <script src="/videos/shared/site-chrome.js?v={BUST}" defer></script>\n</body>',
            1,
        )
    else:
        html = re.sub(
            r'src="/videos/shared/site-chrome\.js[^"]*"',
            f'src="/videos/shared/site-chrome.js?v={BUST}"',
            html,
        )
    return html


def ensure_nav(html: str, product: str) -> str:
    nav = NAV_HHH if product == "hhh" else NAV_PBJ
    if re.search(r'<ul class="nav-links">[\s\S]*?</ul>', html):
        html = re.sub(r'<ul class="nav-links">[\s\S]*?</ul>', nav.strip(), html, count=1)
    return html


def ensure_breadcrumbs(html: str, product: str) -> str:
    crumb = CRUMB_HHH if product == "hhh" else CRUMB_PBJ
    if re.search(r'<div class="breadcrumbs"[^>]*>[\s\S]*?</div>', html):
        html = re.sub(
            r'<div class="breadcrumbs"[^>]*>[\s\S]*?</div>',
            crumb.strip(),
            html,
            count=1,
        )
    else:
        html = re.sub(r"</nav>", "</nav>\n" + crumb, html, count=1)
    return html


def ensure_footer(html: str) -> str:
    if re.search(r'<footer class="jt-site-footer">[\s\S]*?</footer>', html):
        html = re.sub(
            r'<footer class="jt-site-footer">[\s\S]*?</footer>',
            FOOTER.strip(),
            html,
            count=1,
        )
    else:
        html = html.replace("</body>", FOOTER + "\n</body>", 1)
    return html


def bust_local_assets(html: str) -> str:
    html = re.sub(
        r'href="walkthrough\.css(\?v=[^"]*)?"',
        f'href="walkthrough.css?v={BUST}"',
        html,
        count=1,
    )
    html = re.sub(
        r'(src="deck\.js)(\?v=[^"]*)?"',
        rf'\1?v={BUST}"',
        html,
        count=1,
    )
    # Ensure shared walkthrough.css loads before local
    if 'href="/videos/shared/walkthrough.css"' not in html and "walkthrough.css?v=" in html:
        html = html.replace(
            f'href="walkthrough.css?v={BUST}"',
            f'href="/videos/shared/walkthrough.css">\n         <link rel="stylesheet" href="walkthrough.css?v={BUST}"',
            1,
        )
    return html


def strip_pbj_nav_hide(html: str) -> str:
    # Old rule hid Home + first product on small screens — remove it
    html = re.sub(
        r"\s*nav \.nav-links li:first-child,\s*nav \.nav-links li:nth-child\(2\)\s*\{\s*display:\s*none;\s*\}",
        "\n",
        html,
        flags=re.I,
    )
    return html


def strengthen_inline_crumbs(html: str) -> str:
    # Make any remaining weak breadcrumb rules still look like links
    html = re.sub(
        r"\.breadcrumbs a \{[^}]+\}",
        ".breadcrumbs a { color: var(--navy-medium); text-decoration: underline; text-decoration-color: var(--gold); text-underline-offset: 4px; text-decoration-thickness: 2px; font-weight: 700; }",
        html,
        count=1,
    )
    return html


def patch_pbj_goto(html: str) -> str:
    """Keep first sentence highlighted when paused / on load."""
    old = (
        "if (playing && audioUnlocked) {\n"
        " if (voiceEnabled) { clearInterval(timer); playSlideAudio(current); }\n"
        " else { resetTimer(); if (window.PBJWalkthrough) window.PBJWalkthrough.scheduleTapPulse(current); }\n"
        " } else { stopAllAudio(); if (window.PBJWalkthrough) window.PBJWalkthrough.clearTapPulse(); }"
    )
    # Broader patterns used across locales
    patterns = [
        (
            r"\} else \{\s*stopAllAudio\(\);\s*if \(window\.PBJWalkthrough\) window\.PBJWalkthrough\.clearTapPulse\(\);\s*\}",
            "} else { stopAllAudio(); if (window.PBJWalkthrough) window.PBJWalkthrough.clearTapPulse(); setActiveSentence(current, 0); }",
        ),
        (
            r"\} else \{\s*stopAudio\(\);\s*clearTimeout\(timer\);\s*\}",
            "} else { stopAudio(); clearTimeout(timer); setActiveSentence(current, 0); }",
        ),
    ]
    for pat, repl in patterns:
        html2, n = re.subn(pat, repl, html, count=1)
        if n:
            return html2
    # If goTo already calls setActiveSentence in else, leave it
    return html


def patch_page(path: Path, product: str) -> None:
    html = path.read_text(encoding="utf-8")
    html = ensure_body_product(html, product)
    html = ensure_chrome_assets(html)
    html = ensure_nav(html, product)
    html = ensure_breadcrumbs(html, product)
    html = ensure_footer(html)
    html = bust_local_assets(html)
    html = strip_pbj_nav_hide(html)
    html = strengthen_inline_crumbs(html)
    if product == "pbj":
        html = patch_pbj_goto(html)
    path.write_text(html, encoding="utf-8")
    print(f"patched {path.relative_to(ROOT)}")


def fix_hhh_deck(deck_path: Path) -> None:
    text = deck_path.read_text(encoding="utf-8")
    if "Keep the current sentence gold-highlighted" in text:
        print(f"deck already fixed: {deck_path.relative_to(ROOT)}")
        return
    old = """    } else {
      stopAudio();
      clearTimeout(timer);
    }
  }"""
    new = """    } else {
      stopAudio();
      clearTimeout(timer);
      // Keep the current sentence gold-highlighted while paused / on load
      setActiveSentence(current, 0);
    }
  }"""
    if old not in text:
        print(f"WARN: goTo else not found in {deck_path}")
        return
    text = text.replace(old, new, 1)
    text = text.replace(
        "  buildTranscript();\n  setActiveSentence(0, 0);\n  goTo(0);",
        "  buildTranscript();\n  goTo(0); // sets first-sentence highlight while idle",
    )
    deck_path.write_text(text, encoding="utf-8")
    print(f"fixed deck {deck_path.relative_to(ROOT)}")


def fix_shared_cage() -> None:
    css_path = ROOT / "videos" / "shared" / "walkthrough.css"
    text = css_path.read_text(encoding="utf-8")
    if "no sticky vh cage" in text or "full phone visible" in text.lower() and "overflow: visible" in text and "position: sticky" not in text.split("walkthrough-stage")[1][:400]:
        # Still rewrite if sticky remains
        pass
    if "position: sticky" not in text:
        print("shared walkthrough.css already non-sticky")
        return

    start = text.find("/* === Same-screen viewport:")
    if start < 0:
        start = text.find(".walkthrough-stage {\n    position: sticky")
    if start < 0:
        print("WARN: could not find sticky cage block")
        return

    # Replace from sticky stage block through end of letterbox media queries
    end_marker = "@media (max-width: 480px) {\n    .walkthrough-stage .phone-frame {\n        max-height: min(50vh, 100%);\n    }\n}"
    end = text.find(end_marker, start)
    if end < 0:
        end_marker = "@media (max-width: 480px) {"
        end = text.find(end_marker, start)
        if end > 0:
            # find closing of that media block
            close = text.find("\n}", end)
            end = close + 2 if close > 0 else -1
    if end < 0:
        print("WARN: could not find end of cage block")
        return
    end = end + len(end_marker) if end_marker.startswith("@media (max-width: 480px) {\n    .walkthrough-stage") else end

    replacement = """/* === Manual stage: full phone visible (no sticky vh cage — that clipped bezels) === */

.walkthrough-stage {
    position: static;
    height: auto;
    max-height: none;
    min-height: 0;
    overflow: visible;
    margin-top: 0.75rem;
    z-index: 2;
}

body.record-mode .walkthrough h2,
body.record-mode .walkthrough .section-sub {
    display: none;
}

.walkthrough-stage .video-wrapper {
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
    align-items: flex-start;
    gap: 1.25rem;
    height: auto;
    max-height: none;
    min-height: 0;
    width: 100%;
    overflow: visible;
}

.walkthrough-stage .phone-column {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    min-height: 0;
    min-width: 0;
    height: auto;
    max-height: none;
    overflow: visible;
    width: auto;
    max-width: 100%;
}

.walkthrough-stage .phone-viewport {
    flex: 0 0 auto;
    min-height: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    width: auto;
    height: auto;
    max-height: none;
    overflow: visible;
}

.walkthrough-stage .phone-frame {
  width: 340px;
  height: auto;
  max-height: none;
  max-width: 100%;
  flex-shrink: 0;
  aspect-ratio: 9 / 19.5;
}

.walkthrough-stage .progress-dots {
    flex-shrink: 0;
    margin-top: 0.45rem;
    max-width: 100%;
    flex-wrap: nowrap;
    overflow-x: auto;
    overflow-y: hidden;
    justify-content: flex-start;
    padding-bottom: 0.15rem;
    scrollbar-width: thin;
    -webkit-overflow-scrolling: touch;
}

.walkthrough-stage .progress-dots .dot {
    flex-shrink: 0;
}

.walkthrough-stage .playback-controls {
    flex-shrink: 0;
    margin-top: 0.35rem;
}

.walkthrough-stage .chapter-nav {
    flex-shrink: 0;
    margin-top: 0.45rem;
    width: 100%;
    max-width: 100%;
    flex-wrap: nowrap;
    overflow-x: auto;
    overflow-y: hidden;
    justify-content: flex-start;
    gap: 0.35rem;
    padding-bottom: 0.2rem;
    scrollbar-width: thin;
    -webkit-overflow-scrolling: touch;
}

.walkthrough-stage .chapter-btn {
    padding: 0.35rem 0.7rem;
    font-size: 0.72rem;
    white-space: nowrap;
    flex-shrink: 0;
}

.walkthrough-stage .narration-panel {
    height: auto;
    max-height: 720px;
    min-height: 0;
    min-width: 0;
    overflow-y: auto;
    overflow-x: hidden;
    align-self: stretch;
    flex: 1 1 auto;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
}

@media (max-width: 768px) {
    .walkthrough-stage .video-wrapper {
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }

    .walkthrough-stage .phone-frame {
        width: min(320px, 88vw);
        max-height: none;
    }

    .walkthrough-stage .narration-panel {
        width: 100%;
        max-height: 360px;
        flex: none;
    }
}

@media (max-width: 480px) {
    .walkthrough-stage .phone-frame {
        width: min(280px, 84vw);
        max-height: none;
    }
}
"""
    # Find precise end: after the 480px media block that caps phone at 50vh
    m = re.search(
        r"/\* === Same-screen viewport:.*?@media \(max-width: 480px\) \{.*?\n\}\n",
        text,
        flags=re.S,
    )
    if not m:
        m = re.search(
            r"\.walkthrough-stage \{\n    position: sticky;.*?@media \(max-width: 480px\) \{.*?\n\}\n",
            text,
            flags=re.S,
        )
    if not m:
        print("WARN: sticky cage regex miss")
        return
    text = text[: m.start()] + replacement + text[m.end() :]
    css_path.write_text(text, encoding="utf-8")
    print("rewrote shared walkthrough.css cage")


def main() -> None:
    fix_shared_cage()

    hhh_en = ROOT / "videos" / "user-guide-hhh"
    pbj_en = ROOT / "videos" / "user-guide"

    fix_hhh_deck(hhh_en / "deck.js")

    # Patch EN masters
    patch_page(hhh_en / "index.html", "hhh")
    patch_page(pbj_en / "index.html", "pbj")

    # Propagate deck + CSS from HHH EN, patch each locale HTML
    for code in CODES:
        loc = ROOT / "videos" / f"user-guide-hhh-{code}"
        if not loc.exists():
            continue
        shutil.copy2(hhh_en / "deck.js", loc / "deck.js")
        shutil.copy2(hhh_en / "walkthrough.css", loc / "walkthrough.css")
        patch_page(loc / "index.html", "hhh")

    for code in CODES:
        loc = ROOT / "videos" / f"user-guide-{code}"
        if not (loc / "index.html").exists():
            continue
        shutil.copy2(pbj_en / "walkthrough.css", loc / "walkthrough.css")
        patch_page(loc / "index.html", "pbj")

    print("done")


if __name__ == "__main__":
    main()
