#!/usr/bin/env python3
"""Generate tap overlays for every HHH guide slide that has a tap."""
from __future__ import annotations

import re
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "videos" / "user-guide-hhh" / "index.html"
OUT = ROOT / "videos" / "user-guide-hhh" / "_tap_verify_all"
OUT.mkdir(exist_ok=True)


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
                "src": src.split("?", 1)[0],
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
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 40, 40, 230), width=6)
    d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=(255, 40, 40, 230))
    d.line((cx - r * 2, cy, cx + r * 2, cy), fill=(255, 40, 40, 180), width=3)
    d.line((cx, cy - r * 2, cx, cy + r * 2), fill=(255, 40, 40, 180), width=3)
    text = f"{label} @ {x_pct:.0f},{y_pct:.0f}"
    tw = max(240, len(text) * 12)
    d.rectangle((16, 16, 16 + tw, 64), fill=(0, 0, 0, 190))
    d.text((26, 28), text, fill=(255, 255, 255, 255))
    # flag suspicious ys
    flag = ""
    if y_pct >= 96:
        flag = "SYSTEM_NAV?"
    elif y_pct >= 94:
        flag = "near-system"
    if flag:
        d.rectangle((16, 70, 220, 110), fill=(180, 0, 0, 200))
        d.text((26, 82), flag, fill=(255, 255, 255, 255))
    return Image.alpha_composite(im, overlay).convert("RGB")


def main() -> None:
    slides = parse_slides(HTML.read_text(encoding="utf-8"))
    report = []
    for s in slides:
        if s["none"] or s["x"] is None:
            report.append(f"{s['idx']:3d} NONE  {s['label']}")
            continue
        rel = s["src"]
        if rel.startswith("/"):
            img_path = ROOT / rel.lstrip("/")
        elif rel.startswith("../../"):
            img_path = ROOT / rel[len("../../") :]
        else:
            img_path = (HTML.parent / rel).resolve()
        if not img_path.exists():
            report.append(f"{s['idx']:3d} MISSING {img_path.name}")
            continue
        im = Image.open(img_path)
        out = draw_cross(im, s["x"], s["y"], f"{s['idx']}:{s['label']}")
        max_w = 420
        if out.width > max_w:
            ratio = max_w / out.width
            out = out.resize((max_w, int(out.height * ratio)), Image.Resampling.LANCZOS)
        safe = re.sub(r"[^\w\-]+", "_", s["label"])[:40]
        dest = OUT / f"s{s['idx']:03d}_{safe}.png"
        out.save(dest, optimize=True)
        flag = ""
        if s["y"] >= 96:
            flag = " SYSTEM_NAV"
        elif s["y"] >= 94:
            flag = " near-system"
        report.append(
            f"{s['idx']:3d} {s['x']:5.1f},{s['y']:5.1f}{flag:12} {s['label'][:28]:28} {img_path.name}"
        )
    summary = OUT / "_report.txt"
    summary.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {len(slides)} rows -> {summary}")
    print(summary.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
