#!/usr/bin/env python3
"""Picture-honest CVC how-to: remount stills, rewrite EN, gold taps."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "cvc" / "user-guide"
HTML = OUT / "index.html"
NARR_PATH = OUT / "narration-en.json"
MAP_PATH = OUT / "_shot-map.json"

HOME = "/assets/screenshots/cvc/manual/01-home-command-center.png"
IDENT = "/assets/screenshots/cvc/manual/05-identify.png"
COLL = "/assets/screenshots/cvc/manual/02-collection-gallery.png"
WISH = "/assets/screenshots/cvc/manual/26-wish-list.png"
PORT = "/assets/screenshots/cvc/manual/06-portfolio-pl.png"
ALERT = "/assets/screenshots/cvc/manual/07-grail-radar.png"
CMP = "/assets/screenshots/cvc/manual/04-compare.png"
GRADE = "/assets/screenshots/cvc/manual/08-grading-guide.png"
CERT = "/assets/screenshots/cvc/manual/30-cert-tracker.png"
PHOTO = "/assets/screenshots/cvc/manual/32-photo-studio.png"
WEB = "/assets/screenshots/cvc/manual/09-web-companion.png"
SET = "/assets/screenshots/cvc/manual/37-settings.png"
LANG = "/assets/screenshots/cvc/manual/10-language.png"
PRIV = "/assets/screenshots/cvc/manual/11-privacy.png"
BACK = "/assets/screenshots/cvc/manual/12-backup-sync.png"
ZIP = "/assets/screenshots/cvc/manual/40-zippo-decoder.png"

SRCS = {
    **{i: HOME for i in list(range(0, 14)) + [25, 43, 44, 51, 52, 64]},
    **{i: IDENT for i in range(14, 25)},
    **{i: COLL for i in [26, 27, 28, 29, 30, 31, 45, 50]},
    32: PORT,
    33: PORT,
    34: PORT,
    35: WISH,
    **{i: ALERT for i in range(36, 42)},
    42: CMP,
    46: GRADE,
    47: CERT,
    48: ZIP,
    49: PHOTO,
    53: WEB,
    54: WEB,
    55: WEB,
    56: SET,
    57: LANG,
    58: PRIV,
    59: BACK,
    60: PRIV,
    61: SET,
    62: SET,
    63: SET,
}

ALTS = {
    HOME: "Home",
    IDENT: "Identify",
    COLL: "My Collection",
    WISH: "Wish list",
    PORT: "Portfolio",
    ALERT: "Price Alerts",
    CMP: "Compare",
    GRADE: "Grading Guide",
    CERT: "Certifications",
    PHOTO: "Photo Studio",
    WEB: "Web Companion",
    SET: "Settings",
    LANG: "Language",
    PRIV: "Privacy",
    BACK: "Backup",
    ZIP: "Zippo decoder",
}

NARR = [
    "With Curator's Vault you can identify a piece, keep a private vault, and hunt grails. Here's Home.",
    "Here's step by step. You land on Home. The banner says you are exploring sample data.",
    "Tap Identify a piece when you are ready — it is marked Recommended.",
    "The command row is Identify, Add, Tools, Settings, and Wish.",
    "The green card is collection value — an estimate for what is in the vault.",
    "If you'd like a demo, leave samples on. That banner stays at the top.",
    "You can Identify or add a piece anytime from this same Home.",
    "When samples are on, the banner stays up so you do not mix demo pieces with yours.",
    "Tap Clear samples when you are ready for your own vault.",
    "The status line shows how many pieces are in the vault and on your wish list.",
    "The bottom bar has four tabs: Home, My Collection, Tools, and Settings.",
    "With Curator's Vault you can identify a piece from a photo. Tap Identify — the camera on the command row.",
    "Add Item opens My Collection if you want to type a piece in yourself.",
    "Wish List is the heart. Tools is the arrow. Settings is the gear.",
    "Here's Identify. Step one: pick Coin, Paper Money, Trading Card, Stamp, or Lighter.",
    "Lay the piece flat and keep it fully in frame. One still photo is enough.",
    "Tap Point camera at item — or describe the piece if you already know it.",
    "What you already know is optional. Authentication clues can stay closed.",
    "When you have a photo, tap Identify. You can leave the other fields blank.",
    "You might want a faster job. A photo plus a category is enough — then tap Identify.",
    "Identify is the dark bar at the bottom. History is the clock at the top right.",
    "Photograph one piece, laid flat, then come back here and tap Identify.",
    "One piece per photo. Point camera at that one item.",
    "Tap Identify when you are ready. That starts the job from this screen.",
    "History is the clock at the top right — past reports live there.",
    "Home is where you come back. Identify and Add are right here when you have a signal again.",
    "Tap My Collection — the briefcase, second from the left.",
    "Owned is what you have. Wish is what you are hunting. For Sale is what you are selling.",
    "Each row is a piece — name, in the vault, and a value. Tap a row to open it.",
    "The green card is your vault total. Print inventory list sits on that card.",
    "Manage your vault has Timeline, Insights, and Portfolio P and L. Swipe that row for more.",
    "To add a piece yourself, tap the plus. It lands in Owned.",
    "Here's Portfolio. Cost, estimated value, and gain or loss across the vault.",
    "Value by category is the ring. Each slice is a type in the vault.",
    "The big number is portfolio P and L — profit or loss from the prices you entered.",
    "You might want a grail. Tap Wish. Each row is a target and a price you set.",
    "This is Price Alerts. Tap plus New to add a hunt.",
    "Each row is a hunt. Turn it on, or tap Delete if you are done with it.",
    "Tap Check all to search now. Search on eBay opens that listing in your browser.",
    "When a new match lands, a notification brings you back here.",
    "If you'd like, tap Search on eBay on any row to see the live listings.",
    "Check all runs every hunt at once. Plus New starts another.",
    "Here's Compare. Pick a category, then search and choose two pieces side by side.",
    "Tap Tools on the bottom bar when you want Compare, Web Companion, and the rest of the floor.",
    "From Home, Tools is also the arrow on the command row.",
    "Back on My Collection, the plus adds a piece. A box of pieces is just adding them one at a time.",
    "Here's Grading Guide. Pick Coins or Cards, then read the condition language.",
    "Certifications tracks grading certs. Tap plus when you have a number to store.",
    "If you'd like, here's Zippo decoder. Type the bottom stamp, then tap Decode.",
    "Here's Photo Studio. Pick a category, then name the piece and follow the shots.",
    "The vault list is also where you open a piece for notes and photos.",
    "From Home you can jump back to Identify, Add, or Wish anytime.",
    "Backup now sits on Home when the vault is not backed up yet.",
    "If you'd like to edit on a PC, tap Start Web Companion. Same Wi-Fi only.",
    "Here's how. Start on the phone, then open the address on a PC and type the four-digit code.",
    "This is not a public website. Stop on the phone when you are done.",
    "Tap Settings — gear at the bottom right.",
    "Language switches the menus. Eight languages ship in this version.",
    "Privacy is what to include when you export a backup — contacts, prices, and the rest. Turn a row on only if you want it in the file.",
    "File backup: tap Save a Copy to Drive, Files, or email. On another phone, Bring a Copy Back.",
    "The same Privacy screen lets you leave prices and deal history out of a backup.",
    "Curator's Vault includes a 14-day Pro trial from first open — no card. Upgrade is at the top of Settings.",
    "After the trial, tap Upgrade to Pro — monthly or yearly through Google Play or the App Store.",
    "Questions? Email support@josspatech.com.",
    "This user guide lives at josspatech.com/videos/cvc/user-guide.",
]

TAPS = {
    2: 'data-tap-x="50" data-tap-y="90" data-tap-label="Identify a piece" data-tap-show-at="0.3" data-tap-duration="2.8"',
    8: 'data-tap-x="82" data-tap-y="10" data-tap-label="Clear samples" data-tap-show-at="0.3" data-tap-duration="2.8"',
    11: 'data-tap-x="12" data-tap-y="42" data-tap-label="Identify" data-tap-show-at="0.3" data-tap-duration="2.8"',
    12: 'data-tap-x="30" data-tap-y="42" data-tap-label="Add" data-tap-show-at="0.3" data-tap-duration="2.6"',
    13: 'data-tap-x="88" data-tap-y="42" data-tap-label="Wish" data-tap-show-at="0.3" data-tap-duration="2.6"',
    14: 'data-tap-x="18" data-tap-y="30" data-tap-label="Coin" data-tap-show-at="0.3" data-tap-duration="2.8"',
    16: 'data-tap-x="50" data-tap-y="48" data-tap-label="Point camera" data-tap-show-at="0.3" data-tap-duration="2.8"',
    18: 'data-tap-x="50" data-tap-y="78" data-tap-label="Identify" data-tap-show-at="0.3" data-tap-duration="2.8"',
    20: 'data-tap-x="50" data-tap-y="82" data-tap-label="Identify" data-tap-show-at="0.3" data-tap-duration="2.6"',
    23: 'data-tap-x="50" data-tap-y="82" data-tap-label="Identify" data-tap-show-at="0.3" data-tap-duration="2.6"',
    24: 'data-tap-x="88" data-tap-y="12" data-tap-label="History" data-tap-show-at="0.3" data-tap-duration="2.8"',
    26: 'data-tap-x="38" data-tap-y="94" data-tap-label="My Collection" data-tap-show-at="0.3" data-tap-duration="2.8"',
    27: 'data-tap-x="22" data-tap-y="44" data-tap-label="Owned" data-tap-show-at="0.3" data-tap-duration="2.6"',
    28: 'data-tap-x="50" data-tap-y="78" data-tap-label="Open piece" data-tap-show-at="0.3" data-tap-duration="2.6"',
    31: 'data-tap-x="88" data-tap-y="78" data-tap-label="Plus" data-tap-show-at="0.3" data-tap-duration="2.6"',
    35: 'data-tap-x="50" data-tap-y="44" data-tap-label="Wish" data-tap-show-at="0.3" data-tap-duration="2.6"',
    36: 'data-tap-x="78" data-tap-y="12" data-tap-label="+ New" data-tap-show-at="0.3" data-tap-duration="2.8"',
    37: 'data-tap-x="82" data-tap-y="32" data-tap-label="Delete" data-tap-show-at="0.3" data-tap-duration="2.6"',
    38: 'data-tap-x="22" data-tap-y="12" data-tap-label="Check all" data-tap-show-at="0.3" data-tap-duration="2.8"',
    40: 'data-tap-x="22" data-tap-y="36" data-tap-label="Search on eBay" data-tap-show-at="0.3" data-tap-duration="2.6"',
    41: 'data-tap-x="22" data-tap-y="12" data-tap-label="Check all" data-tap-show-at="0.3" data-tap-duration="2.6"',
    42: 'data-tap-x="50" data-tap-y="78" data-tap-label="Search" data-tap-show-at="0.3" data-tap-duration="2.6"',
    43: 'data-tap-x="62" data-tap-y="94" data-tap-label="Tools" data-tap-show-at="0.3" data-tap-duration="2.6"',
    44: 'data-tap-x="50" data-tap-y="42" data-tap-label="Tools" data-tap-show-at="0.3" data-tap-duration="2.6"',
    46: 'data-tap-x="28" data-tap-y="28" data-tap-label="Coins" data-tap-show-at="0.3" data-tap-duration="2.6"',
    47: 'data-tap-x="88" data-tap-y="88" data-tap-label="Plus" data-tap-show-at="0.3" data-tap-duration="2.6"',
    48: 'data-tap-x="50" data-tap-y="48" data-tap-label="Decode" data-tap-show-at="0.3" data-tap-duration="2.6"',
    49: 'data-tap-x="12" data-tap-y="32" data-tap-label="Coins" data-tap-show-at="0.3" data-tap-duration="2.6"',
    52: 'data-tap-x="82" data-tap-y="18" data-tap-label="Back up now" data-tap-show-at="0.3" data-tap-duration="2.6"',
    53: 'data-tap-x="50" data-tap-y="42" data-tap-label="Start" data-tap-show-at="0.3" data-tap-duration="2.8"',
    56: 'data-tap-x="88" data-tap-y="94" data-tap-label="Settings" data-tap-show-at="0.3" data-tap-duration="2.6"',
    59: 'data-tap-x="50" data-tap-y="28" data-tap-label="Save a Copy" data-tap-show-at="0.3" data-tap-duration="2.6"',
    61: 'data-tap-x="82" data-tap-y="16" data-tap-label="Upgrade" data-tap-show-at="0.3" data-tap-duration="2.6"',
    62: 'data-tap-x="50" data-tap-y="28" data-tap-label="Upgrade to Pro" data-tap-show-at="0.3" data-tap-duration="2.6"',
}

assert len(NARR) == 65
assert set(SRCS) == set(range(65))


def strip_taps(attrs: str) -> str:
    return re.sub(
        r'\s+data-tap-(?:none|x|y|label|show-at|duration)(?:=(?:"[^"]*"|\'[^\']*\'))?',
        "",
        attrs,
    )


def main() -> None:
    html = HTML.read_text(encoding="utf-8")

    def repl_slide(m: re.Match) -> str:
        inner = m.group(0)
        idx_m = re.search(r'data-index="(\d+)"', inner)
        if not idx_m:
            return inner
        idx = int(idx_m.group(1))
        src = SRCS[idx]
        alt = ALTS[src]
        inner = re.sub(
            r'<img src="[^"]+" alt="[^"]+"',
            f'<img src="{src}" alt="{alt}"',
            inner,
            count=1,
        )
        head = re.match(r"<div class=\"slide(?:\s+active)?\"([^>]*)>", inner)
        if not head:
            return inner
        attrs = strip_taps(head.group(1))
        extra = TAPS.get(idx, "data-tap-none")
        new_head = f'<div class="slide{" active" if " active" in inner[:80] else ""}"{attrs} {extra}>'
        return inner.replace(head.group(0), new_head, 1)

    html2 = re.sub(
        r'<div class="slide(?:\s+active)?"[^>]*>\s*<img src="[^"]+" alt="[^"]+"[^>]*>\s*</div>',
        repl_slide,
        html,
        flags=re.S,
    )
    new_arr = json.dumps(NARR, ensure_ascii=False)
    html2, n = re.subn(
        r"const NARRATION = \[.*?\];",
        "const NARRATION = " + new_arr + ";",
        html2,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit(f"NARRATION replace count={n}")
    HTML.write_text(html2, encoding="utf-8")
    NARR_PATH.write_text(json.dumps(NARR, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if MAP_PATH.exists():
        rows = json.loads(MAP_PATH.read_text(encoding="utf-8"))
        for row in rows:
            i = int(row["i"])
            src = SRCS[i]
            row["n"] = NARR[i]
            row["src"] = src
            row["alt"] = ALTS[src]
        MAP_PATH.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("slides", len(NARR), "taps", len(TAPS), "srcs", len(set(SRCS.values())))


if __name__ == "__main__":
    main()
