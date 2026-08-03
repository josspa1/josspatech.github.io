#!/usr/bin/env python3
from pathlib import Path
from PIL import Image

BASE = Path(__file__).resolve().parents[1] / "assets" / "screenshots" / "hhh" / "manual"
OUT = Path(__file__).resolve().parents[1] / "videos" / "user-guide-hhh" / "_tap_crops"
OUT.mkdir(exist_ok=True)


def crop(name: str, y0: float, y1: float, x0: float = 0.0, x1: float = 1.0, tag: str = "") -> None:
    im = Image.open(BASE / name)
    w, h = im.size
    box = (int(w * x0), int(h * y0), int(w * x1), int(h * y1))
    c = im.crop(box)
    dest = OUT / f"{Path(name).stem}_{tag}.png"
    c.save(dest)
    print(dest.name, c.size)


crop("01-home-command-center.png", 0.08, 0.16, tag="banner")
crop("01-home-command-center.png", 0.34, 0.52, tag="quick")
crop("01-home-command-center.png", 0.88, 0.99, tag="tabs")
crop("02-museum-collection.png", 0.40, 0.52, tag="segments")
crop("02-museum-collection.png", 0.52, 0.62, tag="search")
crop("02-museum-collection.png", 0.58, 0.72, tag="more-list")
crop("02-museum-collection.png", 0.78, 0.90, tag="fab")
crop("02-museum-collection.png", 0.88, 0.99, tag="tabs")
crop("04-wishlist-grails.png", 0.40, 0.55, tag="segments")
crop("04-wishlist-grails.png", 0.48, 0.58, tag="addwish")
crop("07a-identify-camera.png", 0.40, 0.60, tag="photo-btns")
crop("21-demand-rolodex-send.png", 0.10, 0.30, tag="top")
crop("21-demand-rolodex-send.png", 0.40, 0.70, tag="mid")
crop("22-demand-rolodex-receive.png", 0.40, 0.80, tag="mid")
crop("08-tools-hub.png", 0.20, 0.90, tag="grid")
print("done")
