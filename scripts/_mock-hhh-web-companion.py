"""Build accurate Web Companion mockup: LAN URL + large 4-digit pairing code (not QR-to-PC)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "screenshots" / "hhh" / "manual" / "09-web-companion.png"
BAK = OUT.with_suffix(".png.bak-qr-to-pc")
REF = ROOT / "assets" / "screenshots" / "hhh" / "manual" / "01-home-command-center.png"


def font(size: int, bold: bool = False):
    for path in (
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    # Use current Home shot for chrome size / tab bar crop if available
    if REF.exists():
        base = Image.open(REF).convert("RGBA")
        w, h = base.size
    else:
        w, h = 1440, 3120
        base = Image.new("RGBA", (w, h), (245, 240, 232, 255))

    # Solid cream content canvas (keep status + nav from ref if possible)
    img = Image.new("RGBA", (w, h), (245, 240, 232, 255))
    draw = ImageDraw.Draw(img)

    navy = (91, 35, 51, 255)
    soft = (138, 112, 112, 255)
    gold = (200, 170, 110, 255)
    white = (255, 255, 255, 255)
    green = (46, 125, 50, 255)
    cream = (245, 240, 232, 255)

    # Status bar strip
    draw.rectangle([0, 0, w, int(h * 0.035)], fill=(245, 240, 232, 255))
    draw.text((int(w * 0.04), int(h * 0.008)), "12:41", font=font(28), fill=navy)

    # Header
    y = int(h * 0.05)
    draw.text((int(w * 0.04), y), "←  Web Companion", font=font(40, True), fill=navy)

    # Hero
    y = int(h * 0.12)
    draw.ellipse([w // 2 - 70, y, w // 2 + 70, y + 140], outline=navy, width=6)
    draw.text((w // 2 - 30, y + 40), "🌐", font=font(48), fill=navy)
    y += 170
    draw.text((w // 2 - 220, y), "Web Companion", font=font(52, True), fill=navy)
    y += 70
    for line in (
        "Shows YOUR phone collection on this",
        "computer — same Wi‑Fi only.",
        "This is not the public website.",
    ):
        bbox = draw.textbbox((0, 0), line, font=font(28))
        draw.text(((w - (bbox[2] - bbox[0])) // 2, y), line, font=font(28), fill=soft)
        y += 40

    # Live pill
    y += 30
    pill = [int(w * 0.08), y, int(w * 0.92), y + 90]
    draw.rounded_rectangle(pill, radius=24, outline=green, width=4, fill=white)
    draw.ellipse([pill[0] + 36, y + 30, pill[0] + 66, y + 60], fill=green)
    draw.text((pill[0] + 90, y + 22), "Live dashboard running", font=font(30, True), fill=navy)
    draw.text((pill[2] - 320, y + 28), "Auto-stops in ~59 min", font=font(24), fill=soft)

    # URL + code card
    y += 130
    card = [int(w * 0.06), y, int(w * 0.94), y + int(h * 0.42)]
    draw.rounded_rectangle(card, radius=28, fill=white, outline=(220, 200, 190, 255), width=2)

    cx = card[0] + 48
    cy = card[1] + 40
    draw.text((cx, cy), "1. Open this address on your PC", font=font(32, True), fill=navy)
    cy += 50
    draw.text((cx, cy), "Same Wi‑Fi. Type it in any browser.", font=font(26), fill=soft)
    cy += 55
    draw.rounded_rectangle([cx, cy, card[2] - 48, cy + 100], radius=16, fill=(250, 245, 240, 255), outline=gold, width=2)
    draw.text((cx + 28, cy + 28), "http://10.0.0.42:8787", font=font(36, True), fill=navy)

    cy += 130
    draw.text((cx, cy), "2. Enter this code", font=font(32, True), fill=navy)
    cy += 50
    draw.text((cx, cy), "On the PC page, type the 4-digit code.", font=font(26), fill=soft)
    cy += 60
    draw.rounded_rectangle([cx, cy, card[2] - 48, cy + 160], radius=20, fill=(91, 35, 51, 255))
    code = "4821"
    cf = font(96, True)
    cb = draw.textbbox((0, 0), code, font=cf)
    draw.text(
        (((card[0] + card[2]) - (cb[2] - cb[0])) // 2, cy + 30),
        code,
        font=cf,
        fill=gold,
    )

    cy += 190
    # Primary buttons
    draw.rounded_rectangle([cx, cy, card[2] - 48, cy + 80], radius=18, fill=navy)
    draw.text((cx + 40, cy + 20), "Copy address", font=font(30, True), fill=white)
    cy += 100
    draw.rounded_rectangle([cx, cy, card[2] - 48, cy + 80], radius=18, outline=navy, width=3, fill=cream)
    draw.text((cx + 40, cy + 20), "Copy code", font=font(30, True), fill=navy)

    # Optional one-click note (collapsed) — no primary QR
    cy += 110
    draw.text((cx, cy), "Optional: one-click link / QR (advanced)", font=font(24), fill=soft)

    # Bottom tabs (5) matching current app
    tab_y = int(h * 0.90)
    draw.rectangle([0, tab_y, w, h], fill=white)
    labels = ["Home", "My Pieces", "Tools", "Collectors", "Settings"]
    for i, lab in enumerate(labels):
        tx = int(w * (0.1 + i * 0.18))
        color = gold if lab == "Tools" else soft
        draw.text((tx, tab_y + 55), lab, font=font(22, lab == "Tools"), fill=color)

    if not BAK.exists() and OUT.exists():
        BAK.write_bytes(OUT.read_bytes())
        print(f"backup -> {BAK.name}")

    img.convert("RGB").save(OUT, quality=95)
    print(f"wrote {OUT} ({w}x{h})")


if __name__ == "__main__":
    main()
