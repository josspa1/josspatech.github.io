#!/usr/bin/env python3
"""Generate professional PNGs for PBJ manual slides that lack device captures."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "screenshots" / "pbj" / "manual"
HERO = ROOT / "assets" / "screenshots" / "import" / "step-10-home-dashboard.png"
TRANSACTIONS = ROOT / "assets" / "screenshots" / "transactions.png"

W, H = 1080, 2400
NAVY = (12, 51, 88)
NAVY_MED = (26, 79, 122)
NAVY_LIGHT = (46, 111, 163)
GOLD = (232, 184, 74)
CREAM = (237, 242, 247)
SLATE = (90, 122, 154)
WHITE = (255, 255, 255)
GREEN = (34, 160, 96)


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


def status_bar(draw: ImageDraw.ImageDraw, title: str = "PocketBudJet") -> None:
    draw.rectangle((0, 0, W, 96), fill=NAVY)
    draw.text((48, 30), "9:41", fill=WHITE, font=load_font(34, True))
    tw = draw.textlength(title, font=load_font(30, True))
    draw.text(((W - tw) / 2, 32), title, fill=WHITE, font=load_font(30, True))


def screen_card(title: str, body_lines: list[str], primary: str, secondary: str | None = None) -> Image.Image:
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    status_bar(draw)

    rounded_rect(draw, (56, 180, W - 56, 520), 32, WHITE)
    title_font = load_font(44, True)
    body_font = load_font(32)
    draw.text((96, 220), title, fill=NAVY, font=title_font)
    y = 300
    for line in body_lines:
        for wrapped in wrap_text(draw, line, body_font, W - 192):
            draw.text((96, y), wrapped, fill=SLATE, font=body_font)
            y += 42

    btn_y = H - 420
    rounded_rect(draw, (96, btn_y, W - 96, btn_y + 96), 24, GOLD)
    lf = load_font(36, True)
    tw = draw.textlength(primary, font=lf)
    draw.text(((W - tw) / 2, btn_y + 26), primary, fill=NAVY, font=lf)

    if secondary:
        sf = load_font(30)
        tw2 = draw.textlength(secondary, font=sf)
        draw.text(((W - tw2) / 2, btn_y + 130), secondary, fill=SLATE, font=sf)

    return img


def notification_optin() -> None:
    img = screen_card(
        "Stay on top of bills",
        [
            "PocketBudJet can send reminders before bills are due and alert you to unusual spending.",
            "You can change this anytime in Settings.",
        ],
        "Allow notifications",
        "Not now",
    )
    img.save(OUT / "notification-opt-in.png", optimize=True)
    print("wrote notification-opt-in.png")


def pay_stub_review() -> None:
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    status_bar(draw, "Pay Stub Review")

    rounded_rect(draw, (56, 160, W - 56, 620), 28, WHITE)
    draw.text((96, 200), "Pay Stub Review", fill=NAVY, font=load_font(40, True))
    rows = [
        ("Gross pay", "$4,200.00"),
        ("Federal tax", "$620.00"),
        ("State tax", "$180.00"),
        ("401(k)", "$210.00"),
        ("Net pay", "$3,190.00"),
    ]
    y = 290
    for label, val in rows:
        draw.text((96, y), label, fill=SLATE, font=load_font(30))
        draw.text((W - 280, y), val, fill=NAVY, font=load_font(30, True))
        y += 56

    rounded_rect(draw, (96, H - 360, W - 96, H - 264), 24, GOLD)
    label = "Save to Income"
    lf = load_font(34, True)
    draw.text(((W - draw.textlength(label, font=lf)) / 2, H - 326), label, fill=NAVY, font=lf)
    img.save(OUT / "pay-stub-review.png", optimize=True)
    print("wrote pay-stub-review.png")


def direct_deposit_advisor() -> None:
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    status_bar(draw, "Direct Deposit Advisor")

    draw.text((96, 180), "Split your paycheck", fill=NAVY, font=load_font(42, True))
    splits = [
        ("Checking", "60%", "$1,914"),
        ("Savings", "20%", "$638"),
        ("Bills envelope", "20%", "$638"),
    ]
    y = 280
    for name, pct, amt in splits:
        rounded_rect(draw, (56, y, W - 56, y + 120), 20, WHITE)
        draw.text((96, y + 24), name, fill=NAVY, font=load_font(32, True))
        draw.text((96, y + 68), pct, fill=SLATE, font=load_font(28))
        draw.text((W - 220, y + 40), amt, fill=GREEN, font=load_font(34, True))
        y += 140

    hint = load_font(28)
    draw_centered_lines(
        draw,
        ["Suggested split based on your bills, goals, and envelopes."],
        y + 20,
        hint,
        SLATE,
    )
    img.save(OUT / "direct-deposit-advisor.png", optimize=True)
    print("wrote direct-deposit-advisor.png")


def widgets_watch() -> None:
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)
    status_bar(draw, "Widgets & Watch")

    draw.text((96, 180), "Home screen widgets", fill=WHITE, font=load_font(38, True))
    widgets = [
        ("Safe to spend", "$842"),
        ("Bills due", "3 this week"),
        ("Quick add", "+ Log expense"),
    ]
    y = 280
    for title, val in widgets:
        rounded_rect(draw, (56, y, W - 56, y + 130), 24, NAVY_MED)
        draw.text((96, y + 24), title, fill=GOLD, font=load_font(28, True))
        draw.text((96, y + 68), val, fill=WHITE, font=load_font(36, True))
        y += 150

    rounded_rect(draw, (56, y + 40, W - 56, y + 220), 24, (20, 40, 64))
    draw.text((96, y + 70), "Apple Watch / Wear OS", fill=GOLD, font=load_font(30, True))
    draw.text((96, y + 120), "Safe-to-spend · Bills · Quick-add", fill=WHITE, font=load_font(28))
    img.save(OUT / "widgets-watch.png", optimize=True)
    print("wrote widgets-watch.png")


def activity_filters() -> None:
    if TRANSACTIONS.exists():
        base = Image.open(TRANSACTIONS).convert("RGB")
        base = ImageOps.fit(base, (W, H), method=Image.Resampling.LANCZOS)
    else:
        base = Image.new("RGB", (W, H), CREAM)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    rounded_rect(draw, (36, 120, W - 36, 340), 24, (255, 255, 255, 245))
    draw.text((72, 150), "Filters", fill=NAVY + (255,), font=load_font(36, True))
    chips = ["Last 30 days", "Dining", "Checking"]
    x = 72
    for chip in chips:
        tw = draw.textlength(chip, font=load_font(26, True)) + 48
        rounded_rect(draw, (x, 220, x + tw, 280), 18, GOLD + (255,))
        draw.text((x + 24, 234), chip, fill=NAVY + (255,), font=load_font(26, True))
        x += tw + 16
    draw.text((72, 300), "Running balance shown per account", fill=SLATE + (255,), font=load_font(26))
    out = Image.alpha_composite(base.convert("RGBA"), overlay).convert("RGB")
    out.save(OUT / "activity-filters.png", optimize=True)
    print("wrote activity-filters.png")


def fallback_screen() -> None:
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    status_bar(draw)
    title = load_font(48, True)
    body = load_font(32)
    draw_centered_lines(draw, ["PocketBudJet"], 900, title, NAVY)
    draw_centered_lines(draw, ["User manual screen"], 980, body, SLATE)
    img.save(OUT / "fallback-screen.png", optimize=True)
    print("wrote fallback-screen.png")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    notification_optin()
    pay_stub_review()
    direct_deposit_advisor()
    widgets_watch()
    activity_filters()
    fallback_screen()
    print(f"Done — 6 slides in {OUT}")


if __name__ == "__main__":
    main()
