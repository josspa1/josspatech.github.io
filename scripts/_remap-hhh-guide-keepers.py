#!/usr/bin/env python3
"""Remap HHH guide slides onto better existing keepers (no new phone shots)."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = ROOT / "videos" / "user-guide-hhh" / "index.html"
M = "/assets/screenshots/hhh/manual/"
BUST = "?v=keeper-remap-2026-07-23"

# Only overrides that improve match with existing keepers.
OVERRIDES = {
    94: f"{M}17-atomic-clock.png",  # Exact Time (was tools-hub; moon/atomic were shifted)
    95: f"{M}18-moon-phase.png",  # Moon Phase
    96: f"{M}08-tools-hub.png",  # Print / Export (until dedicated shot)
    98: f"{M}10-settings.png",  # Offline Show Pack under Settings
    99: f"{M}09-web-companion.png",  # Big Screen / LAN — closest keeper
    100: f"{M}06-clockworks-parts.png",  # Movement to Parts
}


def main() -> None:
    html = HTML.read_text(encoding="utf-8")
    changed = []

    def repl_slide(m: re.Match) -> str:
        block = m.group(0)
        idx = int(m.group(1))
        if idx not in OVERRIDES:
            return block
        new_src = OVERRIDES[idx]
        img = re.search(r'(<img[^>]+src=")([^"]+)(")', block)
        if not img:
            return block
        old = img.group(2).split("?")[0]
        if old == new_src and BUST in img.group(2):
            return block
        replacement = img.group(1) + new_src + BUST + img.group(3)
        block2 = block[: img.start()] + replacement + block[img.end() :]
        changed.append((idx, old.replace(M, ""), new_src.replace(M, "")))
        return block2

    # Each slide: opening tag with data-index through the next slide opener or deck end.
    html2, n = re.subn(
        r'<div class="slide(?:\s+active)?"[^>]*data-index="(\d+)"[^>]*>[\s\S]*?(?=<div class="slide(?:\s+active)?"|</div>\s*<script|<!--\s*end slides)',
        repl_slide,
        html,
    )
    if n < 100:
        # Fallback: simpler per-slide non-greedy up to next slide class
        html2 = html
        changed.clear()
        pattern = re.compile(
            r'(<div class="slide(?:\s+active)?"[^>]*data-index="(\d+)"[^>]*>)([\s\S]*?)(?=<div class="slide|\Z)'
        )

        def repl2(m: re.Match) -> str:
            open_t, idx_s, body = m.group(1), m.group(2), m.group(3)
            idx = int(idx_s)
            if idx not in OVERRIDES:
                return m.group(0)
            new_src = OVERRIDES[idx]
            img = re.search(r'(<img[^>]+src=")([^"]+)(")', body)
            if not img:
                return m.group(0)
            old = img.group(2).split("?")[0]
            body2 = body[: img.start()] + img.group(1) + new_src + BUST + img.group(3) + body[img.end() :]
            changed.append((idx, old.replace(M, ""), new_src.replace(M, "")))
            return open_t + body2

        html2, n = pattern.subn(repl2, html)

    HTML.write_text(html2, encoding="utf-8")
    print(f"pattern hits~{n}; updated {len(changed)} slides:")
    for idx, old, new in changed:
        print(f"  {idx:03d}: {old} → {new}")


if __name__ == "__main__":
    main()
