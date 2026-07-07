#!/usr/bin/env python3
"""Generate professional PNGs for HHH manual slides that lack device captures."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "screenshots" / "hhh" / "manual"
HERO = ROOT / "assets" / "screenshots" / "hhh"
HHH_ICON = Path(r"C:\Users\jossp\Documents\MobileApps\HHH\SourceCode\assets\icon.png")

W, H = 1080, 2400
BURGUNDY = (91, 35, 51)
BURGUNDY_DARK = (61, 21, 34)
CREAM = (245, 237, 228)
GOLD = (200, 170, 110)
MUTED = (168, 152, 144)
WHITE = (255, 255, 255)
PLAY_GREEN = (24, 160, 88)
TF_BLUE = (13, 150, 255)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def rounded_rect(draw: ImageDraw.ImageDraw, box, radius: int, fill) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_centered_lines(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    y: int,
    font,
    fill,
    line_gap: int = 12,
) -> int:
    for line in lines:
        tw = draw.textlength(line, font=font)
        draw.text(((W - tw) / 2, y), line, fill=fill, font=font)
        y += font.size + line_gap
    return y


def paste_icon(base: Image.Image, size: int, cx: int, cy: int) -> None:
    icon = Image.open(HHH_ICON).convert("RGBA")
    icon = ImageOps.fit(icon, (size, size), method=Image.Resampling.LANCZOS)
    base.paste(icon, (cx - size // 2, cy - size // 2), icon)


def status_bar(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle((0, 0, W, 90), fill=BURGUNDY_DARK)
    draw.text((48, 28), "9:41", fill=WHITE, font=load_font(34, True))


def play_install() -> None:
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    status_bar(draw)

    paste_icon(img, 220, W // 2, 360)
    title = load_font(52, True)
    sub = load_font(34)
    draw_centered_lines(draw, ["Handy Horology Helper"], 500, title, BURGUNDY_DARK)
    draw_centered_lines(draw, ["Google Play internal testing"], 570, sub, MUTED)

    card_y = 700
    rounded_rect(draw, (80, card_y, W - 80, card_y + 980), 36, WHITE)
    badge = load_font(30, True)
    draw.text((130, card_y + 48), "Google Play", fill=PLAY_GREEN, font=badge)
    draw.text((130, card_y + 92), "Internal testing", fill=BURGUNDY_DARK, font=load_font(44, True))

    steps = [
        "1. Open josspatech.com/#hhh on your phone",
        "2. Tap Get on Google Play",
        "3. Opt in with your Google account",
        "4. Tap Install on the Play Store listing",
    ]
    y = card_y + 190
    body = load_font(32)
    for step in steps:
        for line in wrap_text(draw, step, body, W - 260):
            draw.text((130, y), line, fill=BURGUNDY, font=body)
            y += 44
        y += 18

    btn_y = card_y + 820
    rounded_rect(draw, (130, btn_y, W - 130, btn_y + 96), 24, PLAY_GREEN)
    label = "Install from Google Play"
    lf = load_font(36, True)
    draw.text(((W - draw.textlength(label, font=lf)) / 2, btn_y + 26), label, fill=WHITE, font=lf)

    hint = load_font(28)
    draw_centered_lines(
        draw,
        ["Free 14-day trial · Android 9.0+"],
        1780,
        hint,
        MUTED,
    )
    img.save(OUT / "00-play-internal-install.png", optimize=True)
    print("wrote 00-play-internal-install.png")


def testflight_install() -> None:
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    status_bar(draw)

    paste_icon(img, 220, W // 2, 360)
    title = load_font(52, True)
    sub = load_font(34)
    draw_centered_lines(draw, ["Handy Horology Helper"], 500, title, BURGUNDY_DARK)
    draw_centered_lines(draw, ["TestFlight beta"], 570, sub, MUTED)

    card_y = 700
    rounded_rect(draw, (80, card_y, W - 80, card_y + 1040), 36, WHITE)
    draw.text((130, card_y + 48), "TestFlight", fill=TF_BLUE, font=load_font(34, True))
    draw.text((130, card_y + 96), "Install on iPhone", fill=BURGUNDY_DARK, font=load_font(44, True))

    steps = [
        "1. Email support@josspatech.com for an invite",
        "2. Install TestFlight from the App Store",
        "3. Open the invite link in your email",
        "4. Tap Accept, then Install Handy Horology Helper",
    ]
    y = card_y + 200
    body = load_font(32)
    for step in steps:
        for line in wrap_text(draw, step, body, W - 260):
            draw.text((130, y), line, fill=BURGUNDY, font=body)
            y += 44
        y += 18

    btn_y = card_y + 860
    rounded_rect(draw, (130, btn_y, W - 130, btn_y + 96), 24, TF_BLUE)
    label = "Open in TestFlight"
    lf = load_font(36, True)
    draw.text(((W - draw.textlength(label, font=lf)) / 2, btn_y + 26), label, fill=WHITE, font=lf)

    hint = load_font(28)
    draw_centered_lines(draw, ["Invite required · iOS 16+"], 1780, hint, MUTED)
    img.save(OUT / "00-testflight-install.png", optimize=True)
    print("wrote 00-testflight-install.png")


def offline_queue() -> None:
    src = HERO / "_screen-home-tab.png"
    if not src.exists():
        src = HERO / "manual" / "01-home-command-center.png"
    base = Image.open(src).convert("RGB")
    base = ImageOps.fit(base, (W, H), method=Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    rounded_rect(draw, (48, 120, W - 48, 300), 24, (61, 21, 34, 230))
    title = load_font(34, True)
    body = load_font(28)
    draw.text((88, 150), "Offline — identification queued", fill=GOLD + (255,), font=title)
    draw.text((88, 205), "HHH will identify this piece when you are back online.", fill=WHITE + (255,), font=body)
    draw.text((88, 248), "Check this banner on Home.", fill=MUTED + (255,), font=body)
    out = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    out.save(OUT / "07b-offline-identify-queue.png", optimize=True)
    print("wrote 07b-offline-identify-queue.png")


def ebay_notification() -> None:
    src = HERO / "04-ebay-alerts.png"
    if src.exists():
        base = Image.new("RGB", (W, H), BURGUNDY_DARK)
        alert = Image.open(src).convert("RGBA")
        aw, ah = alert.size
        scale = min((W - 80) / aw, (H - 520) / ah)
        nw, nh = int(aw * scale), int(ah * scale)
        alert = alert.resize((nw, nh), Image.Resampling.LANCZOS)
        base.paste(alert, ((W - nw) // 2, 360), alert)
        img = base
    else:
        src = HERO / "manual" / "05-ebay-grail-radar.png"
        img = Image.open(src).convert("RGB")
        img = ImageOps.fit(img, (W, H), method=Image.Resampling.LANCZOS)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    rounded_rect(draw, (36, 110, W - 36, 290), 28, (255, 255, 255, 245))
    small = load_font(24)
    title = load_font(30, True)
    body = load_font(28)
    draw.text((72, 132), "HHH · Grail match", fill=MUTED + (255,), font=small)
    draw.text((72, 168), "Seiko 6139 Pogue — new eBay listing", fill=BURGUNDY_DARK + (255,), font=title)
    draw.text((72, 218), "Tap to open Grail Radar", fill=BURGUNDY + (255,), font=body)
    out = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    out.save(OUT / "05b-ebay-match-notification.png", optimize=True)
    print("wrote 05b-ebay-match-notification.png")


def main() -> None:
    if not HHH_ICON.exists():
        raise SystemExit(f"Missing HHH icon: {HHH_ICON}")
    OUT.mkdir(parents=True, exist_ok=True)
    play_install()
    testflight_install()
    offline_queue()
    ebay_notification()
    print(f"Done — 4 slides in {OUT}")


if __name__ == "__main__":
    main()
