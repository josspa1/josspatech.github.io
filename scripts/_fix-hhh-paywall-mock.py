"""Patch Unlock Pro screenshot: hero price = $74.99/yr (not $6.25/mo)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "assets" / "screenshots" / "hhh" / "manual" / "12-trial-subscription.png"
INTRO = ROOT / "assets" / "screenshots" / "hhh" / "intro" / "10-trial-pro.png"


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


def patch(path: Path) -> None:
    bak = path.with_suffix(".png.bak-old-625")
    if not bak.exists():
        bak.write_bytes(path.read_bytes())
        print(f"backup -> {bak.name}")

    # Always patch from the pre-$6.25-hero backup so re-runs stay clean.
    img = Image.open(bak).convert("RGBA")
    w, h = img.size
    draw = ImageDraw.Draw(img)

    # Annual price block — covers "$6.25 /mo" + old small "$74.99/yr" lines.
    ax0, ay0, ax1, ay1 = int(w * 0.08), int(h * 0.352), int(w * 0.78), int(h * 0.445)
    sample = img.getpixel((int(w * 0.12), int(h * 0.348)))
    draw.rectangle([ax0, ay0, ax1, ay1], fill=sample)

    gold = (242, 200, 150, 255)
    soft = (200, 170, 150, 255)

    price_font = font(72, bold=True)
    unit_font = font(36, bold=False)
    sub_font = font(28, bold=False)

    px, py = int(w * 0.11), int(h * 0.362)
    draw.text((px, py), "$74.99", font=price_font, fill=gold)
    bbox = draw.textbbox((px, py), "$74.99", font=price_font)
    draw.text((bbox[2] + 14, py + 28), "/yr", font=unit_font, fill=soft)
    draw.text((px, bbox[3] + 8), "About $6.25/mo · billed yearly", font=sub_font, fill=soft)

    img.convert("RGB").save(path, quality=95)
    print(f"patched {path.name} ({w}x{h})")


def main() -> None:
    patch(MANUAL)
    if INTRO.exists():
        patch(INTRO)
    # Preview crop for visual check
    preview = Image.open(MANUAL)
    w, h = preview.size
    preview.crop((int(w * 0.05), int(h * 0.22), int(w * 0.95), int(h * 0.58))).save(
        MANUAL.parent / "_price_crop_after.png"
    )
    print("preview -> _price_crop_after.png")


if __name__ == "__main__":
    main()
