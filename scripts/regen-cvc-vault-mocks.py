#!/usr/bin/env python3
"""
Regenerate CVC marketing phone mocks with an antique bank-vault door mark
(Mosler / Diebold era: heavy door + combination dial + spoked wheel),
not a treasure chest / lockbox.

Writes into assets/screenshots/cvc/.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "screenshots" / "cvc"

W, H = 1080, 1920

BG = (10, 42, 32)
CARD = (28, 72, 56)
CARD_SOFT = (34, 82, 64)
CREAM = (246, 240, 228)
BRASS = (212, 168, 83)
BRASS_DK = (168, 128, 55)
BRASS_HI = (232, 196, 120)
STEEL = (210, 214, 208)
STEEL_DK = (150, 156, 148)
MUTED = (180, 196, 188)
WHITE = (255, 255, 255)
INK_GREEN = (18, 58, 44)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def rounded(draw: ImageDraw.ImageDraw, box, r: int, fill) -> None:
    draw.rounded_rectangle(box, radius=r, fill=fill)


def draw_antique_vault(
    img: Image.Image,
    cx: float,
    cy: float,
    scale: float,
    *,
    filled: bool = True,
) -> None:
    """
    Antique bank vault door — room-scale door in a thick wall opening.
    Mosler / Diebold cues: deep jamb, rivets, combination dial,
    large spoked boltwork wheel, visible locking bolts.
    """
    d = ImageDraw.Draw(img)
    s = scale

    # Tall door set in a deep surround (reads as vault room, not a box)
    door_w = 72 * s
    door_h = 112 * s
    wall = 16 * s
    jamb = 7 * s
    x0 = cx - door_w / 2
    y0 = cy - door_h / 2
    x1 = x0 + door_w
    y1 = y0 + door_h

    # Wall opening / surround
    if filled:
        rounded(
            d,
            (x0 - wall, y0 - wall * 0.85, x1 + wall, y1 + wall * 0.85),
            int(12 * s),
            INK_GREEN,
        )
        rounded(
            d,
            (x0 - jamb - 3 * s, y0 - jamb, x1 + jamb + 3 * s, y1 + jamb),
            int(9 * s),
            BRASS_DK,
        )
    else:
        d.rounded_rectangle(
            (x0 - wall, y0 - wall * 0.85, x1 + wall, y1 + wall * 0.85),
            radius=int(12 * s),
            outline=CREAM,
            width=max(2, int(2 * s)),
        )

    # Door slab
    if filled:
        rounded(d, (x0, y0, x1, y1), int(6 * s), CREAM)
        inset = 4.5 * s
        rounded(
            d,
            (x0 + inset, y0 + inset, x1 - inset, y1 - inset),
            int(4 * s),
            (236, 230, 216),
        )
        for frac in (0.30, 0.52, 0.74):
            yy = y0 + door_h * frac
            d.line(
                (x0 + inset + 2, yy, x1 - inset - 2, yy),
                fill=STEEL_DK,
                width=max(1, int(1.1 * s)),
            )
        # Corner bosses
        boss = 4.5 * s
        for bx, by in (
            (x0 + 10 * s, y0 + 10 * s),
            (x1 - 10 * s, y0 + 10 * s),
            (x0 + 10 * s, y1 - 10 * s),
            (x1 - 10 * s, y1 - 10 * s),
        ):
            d.ellipse((bx - boss, by - boss, bx + boss, by + boss), fill=BRASS_DK)
            d.ellipse(
                (bx - boss * 0.4, by - boss * 0.4, bx + boss * 0.4, by + boss * 0.4),
                fill=BRASS_HI,
            )
    else:
        d.rounded_rectangle(
            (x0, y0, x1, y1),
            radius=int(6 * s),
            outline=CREAM,
            width=max(2, int(2 * s)),
        )

    # Hinge barrels (left) — chunky antique hinges
    for frac in (0.2, 0.5, 0.8):
        hy = y0 + door_h * frac
        hx = x0 - jamb * 0.15
        hr = 4.2 * s
        if filled:
            d.rounded_rectangle(
                (hx - 5 * s, hy - 3.2 * s, hx + 2 * s, hy + 3.2 * s),
                radius=int(2 * s),
                fill=BRASS_DK,
            )
            d.ellipse((hx - hr, hy - hr, hx + hr * 0.4, hy + hr), fill=BRASS)
            d.ellipse(
                (hx - hr * 0.35, hy - hr * 0.35, hx + hr * 0.05, hy + hr * 0.35),
                fill=BRASS_HI,
            )
        else:
            d.ellipse(
                (hx - hr, hy - hr, hx + hr, hy + hr),
                outline=CREAM,
                width=max(1, int(1.2 * s)),
            )

    # Locking bolts protruding from right edge
    for frac in (0.28, 0.5, 0.72):
        by = y0 + door_h * frac
        bx0 = x1 - 2 * s
        bx1 = x1 + jamb + 5 * s
        if filled:
            rounded(d, (bx0, by - 2.4 * s, bx1, by + 2.4 * s), int(2 * s), BRASS_DK)
            d.ellipse(
                (bx1 - 3.2 * s, by - 3.2 * s, bx1 + 3.2 * s, by + 3.2 * s),
                fill=BRASS,
                outline=BRASS_HI,
                width=max(1, int(0.8 * s)),
            )
        else:
            d.line((bx0, by, bx1, by), fill=CREAM, width=max(2, int(2 * s)))

    # Rivets
    rivet_r = max(1.5, 1.9 * s)
    rivet_pts = []
    for i in range(6):
        t = (i + 0.5) / 6
        rivet_pts.append((x0 + 6.5 * s, y0 + door_h * t))
        rivet_pts.append((x1 - 6.5 * s, y0 + door_h * t))
    for i in range(4):
        t = (i + 1) / 5
        rivet_pts.append((x0 + door_w * t, y0 + 6.5 * s))
        rivet_pts.append((x0 + door_w * t, y1 - 6.5 * s))
    for px, py in rivet_pts:
        if filled:
            d.ellipse(
                (px - rivet_r, py - rivet_r, px + rivet_r, py + rivet_r),
                fill=BRASS_DK,
            )
        else:
            d.ellipse(
                (px - rivet_r, py - rivet_r, px + rivet_r, py + rivet_r),
                outline=CREAM,
                width=1,
            )

    # Brass nameplate
    if filled:
        px0 = x0 + door_w * 0.16
        px1 = x1 - door_w * 0.16
        py0 = y0 + door_h * 0.10
        py1 = py0 + 6.5 * s
        rounded(d, (px0, py0, px1, py1), int(2 * s), BRASS_DK)
        d.rectangle(
            (px0 + 2 * s, py0 + 1.6 * s, px1 - 2 * s, py1 - 1.6 * s),
            fill=BRASS,
        )

    # Combination dial — large antique face
    dcx = cx - 1 * s
    dcy = y0 + door_h * 0.36
    outer = 18 * s
    if filled:
        d.ellipse(
            (dcx - outer - 2, dcy - outer - 2, dcx + outer + 2, dcy + outer + 2),
            fill=STEEL_DK,
        )
        d.ellipse(
            (dcx - outer, dcy - outer, dcx + outer, dcy + outer),
            fill=BRASS_DK,
            outline=BRASS_HI,
            width=max(1, int(1.5 * s)),
        )
        mid = outer * 0.8
        d.ellipse(
            (dcx - mid, dcy - mid, dcx + mid, dcy + mid),
            fill=(42, 36, 28),
            outline=BRASS,
            width=max(1, int(1.3 * s)),
        )
        inner = outer * 0.44
        d.ellipse(
            (dcx - inner, dcy - inner, dcx + inner, dcy + inner),
            fill=BRASS,
            outline=BRASS_HI,
            width=max(1, int(1 * s)),
        )
        hub = outer * 0.16
        d.ellipse(
            (dcx - hub, dcy - hub, dcx + hub, dcy + hub),
            fill=(30, 26, 20),
        )
    else:
        d.ellipse(
            (dcx - outer, dcy - outer, dcx + outer, dcy + outer),
            outline=CREAM,
            width=max(2, int(1.8 * s)),
        )

    tick_r0 = outer * 0.56
    tick_r1 = outer * 0.74
    for i in range(24):
        ang = math.radians(i * 15 - 90)
        major = i % 2 == 0
        r0 = tick_r0 if major else tick_r0 + 1.5 * s
        x_a = dcx + math.cos(ang) * r0
        y_a = dcy + math.sin(ang) * r0
        x_b = dcx + math.cos(ang) * tick_r1
        y_b = dcy + math.sin(ang) * tick_r1
        d.line(
            (x_a, y_a, x_b, y_b),
            fill=BRASS_HI if filled else CREAM,
            width=max(1, int((1.5 if major else 0.8) * s)),
        )

    # Large spoked ship-wheel handle
    wcx = cx + 1 * s
    wcy = y0 + door_h * 0.70
    wr = 26 * s
    rim_w = max(2, int(2.8 * s))
    if filled:
        d.ellipse(
            (wcx - wr - 2, wcy - wr - 2, wcx + wr + 2, wcy + wr + 2),
            outline=STEEL_DK,
            width=max(2, int(2 * s)),
        )
        d.ellipse(
            (wcx - wr, wcy - wr, wcx + wr, wcy + wr),
            outline=BRASS_DK,
            width=rim_w + 1,
        )
        d.ellipse(
            (wcx - wr + 3, wcy - wr + 3, wcx + wr - 3, wcy + wr - 3),
            outline=BRASS,
            width=rim_w,
        )
        # Inner ring
        d.ellipse(
            (wcx - wr * 0.55, wcy - wr * 0.55, wcx + wr * 0.55, wcy + wr * 0.55),
            outline=BRASS_DK,
            width=max(1, int(1.4 * s)),
        )
    else:
        d.ellipse(
            (wcx - wr, wcy - wr, wcx + wr, wcy + wr),
            outline=CREAM,
            width=rim_w,
        )

    for i in range(8):
        ang = math.radians(i * 45 - 12)
        x_b = wcx + math.cos(ang) * (wr - 3.5 * s)
        y_b = wcy + math.sin(ang) * (wr - 3.5 * s)
        d.line(
            (wcx, wcy, x_b, y_b),
            fill=BRASS if filled else CREAM,
            width=max(2, int(2.4 * s)),
        )
        kr = 3.6 * s
        if filled:
            d.ellipse(
                (x_b - kr, y_b - kr, x_b + kr, y_b + kr),
                fill=BRASS_DK,
                outline=BRASS_HI,
                width=max(1, int(0.9 * s)),
            )
        else:
            d.ellipse(
                (x_b - kr, y_b - kr, x_b + kr, y_b + kr),
                outline=CREAM,
                width=max(1, int(1 * s)),
            )

    hub_r = 7.5 * s
    if filled:
        d.ellipse(
            (wcx - hub_r, wcy - hub_r, wcx + hub_r, wcy + hub_r),
            fill=BRASS_DK,
            outline=BRASS_HI,
            width=max(1, int(1.3 * s)),
        )
        d.ellipse(
            (wcx - hub_r * 0.42, wcy - hub_r * 0.42, wcx + hub_r * 0.42, wcy + hub_r * 0.42),
            fill=BRASS_HI,
        )
    else:
        d.ellipse(
            (wcx - hub_r, wcy - hub_r, wcx + hub_r, wcy + hub_r),
            outline=CREAM,
            width=max(1, int(1.4 * s)),
        )


def make_mock(
    *,
    title: str,
    subtitle: str,
    bullets: list[str],
    filename: str,
) -> Path:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    brand_f = font(22)
    title_f = font(54, bold=True)
    sub_f = font(28)
    bullet_f = font(30)
    label_f = font(22)

    d.text((48, 72), "Curator's Vault: Classics", fill=BRASS, font=brand_f)
    draw_antique_vault(img, W - 78, 96, 0.72)

    d.text((48, 168), title, fill=WHITE, font=title_f)
    # wrap subtitle
    d.text((48, 248), subtitle, fill=MUTED, font=sub_f)

    y = 340
    for bullet in bullets:
        rounded(d, (44, y, W - 44, y + 108), 22, CARD)
        d.ellipse((68, y + 38, 100, y + 70), fill=BRASS)
        d.text((124, y + 34), bullet, fill=WHITE, font=bullet_f)
        y += 124

    y = max(y + 36, 1180)
    d.text((48, y), "Your collection", fill=BRASS, font=label_f)
    y += 48

    gap = 20
    card_w = (W - 88 - gap * 2) // 3
    card_h = 280
    for i in range(3):
        cx0 = 44 + i * (card_w + gap)
        rounded(d, (cx0, y, cx0 + card_w, y + card_h), 22, CARD_SOFT)
        draw_antique_vault(img, cx0 + card_w / 2, y + card_h / 2, 1.55)

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / filename
    img.save(path, "PNG", optimize=True)
    return path


SCREENS = [
    {
        "filename": "02-collection.png",
        "title": "Your Collection",
        "subtitle": "Photo-first gallery for serious collectors.",
        "bullets": [
            "Collection · Wish List · For Sale",
            "Insurance-ready item detail",
            "Timeline & compare tools",
        ],
    },
    {
        "filename": "03-identify.png",
        "title": "AI Identification",
        "subtitle": "Snap a photo. Get structured results.",
        "bullets": [
            "Confidence-scored candidates",
            "Grading & rarity context",
            "Save straight to collection",
        ],
    },
    {
        "filename": "04-analytics.png",
        "title": "Analytics & P&L",
        "subtitle": "Track value, ROI, and portfolio health.",
        "bullets": [
            "P&L dashboard (Pro)",
            "Budget tracker & insights",
            "Set completion progress",
        ],
    },
]


def main() -> None:
    for spec in SCREENS:
        path = make_mock(**spec)
        print(f"Wrote {path}")


if __name__ == "__main__":
    main()
