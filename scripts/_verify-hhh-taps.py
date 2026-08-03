#!/usr/bin/env python3
"""Draw tap crosshairs on slide screenshots for visual review."""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "videos" / "user-guide-hhh" / "index.html"
OUT = ROOT / "videos" / "user-guide-hhh" / "_tap_verify"
OUT.mkdir(exist_ok=True)

# Priority slides from the fix pass + a few neighbors
FOCUS = {
    6, 8, 9, 10, 11, 12, 14, 15, 19, 20, 21, 22, 26, 27, 28,
    40, 47, 48, 51, 70, 79, 80, 81, 82, 83, 85, 86, 87,
    94, 95, 96, 97, 98, 99, 100,
    103, 104, 105, 106, 107, 108, 109, 110,
}


def parse_slides(html: str) -> list[dict]:
    pattern = re.compile(
        r'<div class="slide[^"]*"([^>]*)>\s*<img[^>]+src="([^"]+)"',
        re.MULTILINE,
    )
    slides = []
    for attrs, src in pattern.findall(html):
        idx_m = re.search(r'data-index="(\d+)"', attrs)
        if not idx_m:
            continue
        idx = int(idx_m.group(1))
        tx = re.search(r'data-tap-x="([^"]+)"', attrs)
        ty = re.search(r'data-tap-y="([^"]+)"', attrs)
        lab = re.search(r'data-tap-label="([^"]+)"', attrs)
        none = "data-tap-none" in attrs
        slides.append(
            {
                "idx": idx,
                "src": src,
                "x": float(tx.group(1)) if tx else None,
                "y": float(ty.group(1)) if ty else None,
                "label": lab.group(1) if lab else "",
                "none": none,
            }
        )
    return slides


def draw_cross(im: Image.Image, x_pct: float, y_pct: float, label: str) -> Image.Image:
    im = im.convert("RGBA")
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    w, h = im.size
    cx, cy = int(w * x_pct / 100), int(h * y_pct / 100)
    r = max(28, int(min(w, h) * 0.035))
    # ring
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 40, 40, 230), width=6)
    d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=(255, 40, 40, 230))
    # crosshair
    d.line((cx - r * 2, cy, cx + r * 2, cy), fill=(255, 40, 40, 180), width=3)
    d.line((cx, cy - r * 2, cx, cy + r * 2), fill=(255, 40, 40, 180), width=3)
    # label banner
    text = f"{label} @ {x_pct:.0f},{y_pct:.0f}"
    tw = max(220, len(text) * 14)
    d.rectangle((20, 20, 20 + tw, 70), fill=(0, 0, 0, 180))
    d.text((30, 32), text, fill=(255, 255, 255, 255))
    return Image.alpha_composite(im, overlay).convert("RGB")


def main() -> None:
    html = HTML.read_text(encoding="utf-8")
    slides = parse_slides(html)
    print(f"parsed {len(slides)} slides")
    for s in slides:
        if s["idx"] not in FOCUS:
            continue
        if s["none"] or s["x"] is None:
            print(f"  skip {s['idx']} (no tap)")
            continue
        # src like ../../assets/screenshots/hhh/manual/01-home....png?v=...
        rel = s["src"].split("?", 1)[0]
        if rel.startswith("../../"):
            img_path = ROOT / rel[len("../../") :]
        elif rel.startswith("/"):
            img_path = ROOT / rel.lstrip("/")
        else:
            img_path = (HTML.parent / rel).resolve()
        if not img_path.exists():
            print(f"  MISSING {s['idx']} {img_path}")
            continue
        im = Image.open(img_path)
        out = draw_cross(im, s["x"], s["y"], f"{s['idx']}:{s['label']}")
        dest = OUT / f"slide-{s['idx']:03d}-{s['label'].replace(' ', '_').replace(':', '')}.png"
        # shrink for review
        max_w = 540
        if out.width > max_w:
            ratio = max_w / out.width
            out = out.resize((max_w, int(out.height * ratio)), Image.Resampling.LANCZOS)
        out.save(dest, optimize=True)
        print(f"  wrote {dest.name} from {img_path.name}")


if __name__ == "__main__":
    main()
