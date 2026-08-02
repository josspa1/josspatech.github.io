"""Generate OG / logo PNGs for SEO (no site design change)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path(__file__).resolve().parents[1]
out_dir = root / "assets" / "brand"
out_dir.mkdir(parents=True, exist_ok=True)

navy = (12, 51, 88)
gold = (240, 192, 64)
white = (255, 255, 255)

candidates = [
    root / "assets" / "screenshots" / "hub-catalog-hero.png",
    root / "assets" / "josspatech-fb-cover.png",
    root / "assets" / "brand" / "josspatech-cosmos-iconic.png",
]
src = next((p for p in candidates if p.exists()), None)

W, H = 1200, 630
canvas = Image.new("RGB", (W, H), navy)
draw = ImageDraw.Draw(canvas)

if src:
    im = Image.open(src).convert("RGB")
    scale = max(W / im.width, H / im.height)
    nw, nh = int(im.width * scale), int(im.height * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left, top = (nw - W) // 2, (nh - H) // 2
    canvas.paste(im.crop((left, top, left + W, top + H)), (0, 0))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for x in range(0, 720):
        a = int(170 * (1 - x / 720))
        od.line([(x, 0), (x, H)], fill=(8, 34, 58, a))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(canvas)


def font(size, bold=False):
    paths = (
        [r"C:\Windows\Fonts\georgiab.ttf", r"C:\Windows\Fonts\georgia.ttf"]
        if bold
        else [r"C:\Windows\Fonts\georgia.ttf", r"C:\Windows\Fonts\segoeui.ttf"]
    )
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


draw.text((72, 180), "JosspaTech", fill=white, font=font(72, bold=True))
draw.rectangle([72, 270, 340, 276], fill=gold)
draw.text((72, 300), "Private mobile software", fill=(220, 220, 220), font=font(28))
draw.text((72, 350), "Pronounced Joss-pah-tech", fill=gold, font=font(22))
draw.text(
    (72, 520),
    "Handy Horology Helper  ·  PocketBudJet  ·  Curator's Vault",
    fill=(200, 210, 220),
    font=font(20),
)

og = out_dir / "og-josspatech.png"
canvas.save(og, "PNG", optimize=True)
print("wrote", og, og.stat().st_size)

mark_candidates = [
    root / "assets" / "josspatech-fb-profile.png",
    root / "assets" / "brand" / "josspatech-cosmos-iconic.png",
]
mark_src = next((p for p in mark_candidates if p.exists()), None)
if mark_src:
    m = Image.open(mark_src).convert("RGBA")
    side = 512
    sq = Image.new("RGBA", (side, side), (*navy, 255))
    m.thumbnail((int(side * 0.78), int(side * 0.78)), Image.Resampling.LANCZOS)
    sq.paste(m, ((side - m.width) // 2, (side - m.height) // 2), m)
    logo = out_dir / "josspatech-logo-512.png"
    sq.convert("RGB").save(logo, "PNG", optimize=True)
    apple = out_dir / "apple-touch-icon.png"
    sq.resize((180, 180), Image.Resampling.LANCZOS).convert("RGB").save(apple, "PNG", optimize=True)
    print("wrote", logo, logo.stat().st_size)
    print("wrote", apple, apple.stat().st_size)
