#!/usr/bin/env python3
"""
HHH user-guide post-launch pass:
- Drop Android/iOS install slides (how-to starts after install)
- Fix tab-bar copy (5 tabs incl. Collectors)
- Fix trial copy (15-day; no internal-testing wording)
- Keep Ludwig demo naming
- Renumber slides, transcript, dots, audio files
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "videos" / "user-guide-hhh"
NARR_PATH = OUT / "narration-en.json"
HTML_PATH = OUT / "index.html"
AUDIO = OUT / "audio"
DROP = 2  # remove first two install slides

NARR_PATCHES_AFTER_DROP = {
    # indices are NEW (post-drop)
    0: "Open Handy Horology Helper. Swipe the welcome slides — identify pieces, track your collection, hunt on eBay. Tap Continue on each slide.",
    2: "Tap Explore with sample collection to tour Ludwig's demo gallery — recommended for first launch.",
    4: "If you picked sample collection, wait while Ludwig's demo watches load, then tap Get Started on the confirmation screen.",
    10: "The bottom tab bar has five tabs: Home, My Pieces, Tools, Collectors, and Settings. Tap any tab to switch.",
    76: "HHH includes a 15-day Pro trial with full access — cancel anytime.",
    77: "After the trial, tap Upgrade in Settings. Choose $9.99 per month or $74.99 per year.",
}


def main() -> None:
    old = json.loads(NARR_PATH.read_text(encoding="utf-8"))
    new = old[DROP:]
    for i, text in NARR_PATCHES_AFTER_DROP.items():
        if i < len(new):
            new[i] = text
    NARR_PATH.write_text(json.dumps(new, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    html = HTML_PATH.read_text(encoding="utf-8")

    # Strip install slides 0 and 1 from slideshow
    html = re.sub(
        r'\s*<div class="slide(?:\s+active)?"[^>]*data-index="0"[^>]*>[\s\S]*?</div>\s*'
        r'<div class="slide"[^>]*data-index="1"[^>]*>[\s\S]*?</div>',
        "",
        html,
        count=1,
    )

    # Renumber remaining data-index on slides (old i -> i-DROP)
    def renum_slide_open(m: re.Match) -> str:
        attrs = m.group(1)
        idx = int(re.search(r'data-index="(\d+)"', attrs).group(1))
        if idx < DROP:
            return m.group(0)  # shouldn't remain
        new_idx = idx - DROP
        attrs2 = re.sub(r'data-index="\d+"', f'data-index="{new_idx}"', attrs)
        cls = "slide active" if new_idx == 0 else "slide"
        # force class
        return f'<div class="{cls}"{attrs2}>'

    html = re.sub(r'<div class="slide(?:\s+active)?"([^>]*)>', renum_slide_open, html)

    # Chapter pills only (not dots/transcript — those are rebuilt below)
    html = re.sub(
        r'(<button class="chapter-btn[^"]*" data-slide=")(\d+)(")',
        lambda m: m.group(1) + str(max(0, int(m.group(2)) - DROP)) + m.group(3)
        if int(m.group(2)) >= DROP
        else m.group(0),
        html,
    )

    # Rebuild dots
    dots = "\n".join(
        f'         <span class="dot{" active" if i == 0 else ""}" data-slide="{i}"></span>'
        for i in range(len(new))
    )
    html = re.sub(
        r'(<div class="progress-dots"[^>]*>)[\s\S]*?(</div>\s*<div class="playback-controls")',
        lambda m: m.group(1) + "\n" + dots + "\n        " + m.group(2),
        html,
        count=1,
    )

    # Rebuild transcript paras
    paras = []
    for i, line in enumerate(new):
        esc = (
            line.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        cls = "transcript-para current" if i == 0 else "transcript-para"
        paras.append(f' <p class="{cls}" data-slide="{i}">{esc}</p>')
    html = re.sub(
        r'(<div class="transcript-body"[^>]*>)[\s\S]*?(</div>\s*</div>\s*</div>\s*</div>\s*<div class="progress)',
        lambda m: m.group(1) + "\n" + "\n".join(paras) + "\n" + m.group(2),
        html,
        count=1,
    )

    # Embedded NARRATION array
    html = re.sub(
        r"const NARRATION = \[[\s\S]*?\];",
        "const NARRATION = " + json.dumps(new, ensure_ascii=False) + ";",
        html,
        count=1,
    )

    # Copy / counts in chrome
    html = html.replace("113 slides", f"{len(new)} slides")
    html = html.replace(
        "install through every shipped v1 feature",
        "post-install through every shipped v1 feature",
    )
    html = html.replace(
        "Detailed user manual — install through every shipped v1 feature in app order.",
        "Detailed user manual — after install through every shipped v1 feature in app order.",
    )
    html = re.sub(
        r"Try HHH free for 14 days on Google Play open testing or request iOS TestFlight from josspatech.com\.",
        "Try HHH free for 15 days on Google Play, or join iOS early access on TestFlight from josspatech.com.",
        html,
    )

    HTML_PATH.write_text(html, encoding="utf-8")

    # Shift audio: slide-N.mp3 (N>=2) -> slide-(N-2).mp3
    tmp = AUDIO / "_shift_tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir()
    shifted = 0
    for p in sorted(AUDIO.glob("slide-*.mp3")):
        m = re.fullmatch(r"slide-(\d+)\.mp3", p.name)
        if not m:
            continue
        idx = int(m.group(1))
        if idx < DROP:
            continue
        dest = tmp / f"slide-{idx - DROP}.mp3"
        shutil.copy2(p, dest)
        shifted += 1
    # wipe old numbered mp3s then move back
    for p in AUDIO.glob("slide-*.mp3"):
        p.unlink()
    for p in tmp.glob("slide-*.mp3"):
        shutil.move(str(p), str(AUDIO / p.name))
    shutil.rmtree(tmp)

    # Mark Ludwig + patched lines for audio regen (new indices)
    regen = sorted(set(NARR_PATCHES_AFTER_DROP.keys()) | {2, 4})
    (OUT / "_audio_regen_slides.json").write_text(json.dumps(regen, indent=2) + "\n", encoding="utf-8")

    print(f"narration {len(old)} -> {len(new)}")
    print(f"audio shifted {shifted} files")
    print(f"regen slides: {regen}")


if __name__ == "__main__":
    main()
