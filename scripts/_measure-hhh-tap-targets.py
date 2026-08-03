#!/usr/bin/env python3
"""Measure UI tap targets on HHH guide screenshots (1440x3120 keepers)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

BASE = Path(__file__).resolve().parents[1] / "assets" / "screenshots" / "hhh" / "manual"


def analyze_home() -> None:
    im = Image.open(BASE / "01-home-command-center.png").convert("RGB")
    w, h = im.size
    arr = np.array(im)
    print(f"home {w}x{h}")
    print("quick-command dark clusters:")
    for ypct in range(35, 55, 2):
        y = int(h * ypct / 100)
        row = arr[y]
        dark = np.where((row[:, 0] < 100) & (row[:, 1] < 80) & (row[:, 2] < 90))[0]
        if len(dark) <= 20:
            continue
        clusters: list[int] = []
        cur = [int(dark[0])]
        for x in dark[1:]:
            if x - cur[-1] < 40:
                cur.append(int(x))
            else:
                if len(cur) > 8:
                    clusters.append(int(np.mean(cur)))
                cur = [int(x)]
        if len(cur) > 8:
            clusters.append(int(np.mean(cur)))
        if clusters:
            print(f"  y={ypct}% x%={[round(100 * c / w, 1) for c in clusters]}")

    print("tab-bar orange/active:")
    for ypct in range(88, 99):
        y = int(h * ypct / 100)
        row = arr[y]
        orange = np.where(
            (row[:, 0] > 140)
            & (row[:, 1] > 50)
            & (row[:, 1] < 140)
            & (row[:, 2] < 100)
            & (row[:, 0] > row[:, 1])
        )[0]
        if len(orange) > 5:
            print(f"  y={ypct}% count={len(orange)} mean_x%={round(100 * orange.mean() / w, 1)}")


def analyze_museum() -> None:
    im = Image.open(BASE / "02-museum-collection.png").convert("RGB")
    w, h = im.size
    arr = np.array(im)
    print(f"\nmuseum {w}x{h}")
    print("Owned/Wish white pills:")
    for ypct in range(38, 52):
        y = int(h * ypct / 100)
        row = arr[y]
        white = np.where((row[:, 0] > 240) & (row[:, 1] > 240) & (row[:, 2] > 240))[0]
        if 50 < len(white) < 500:
            print(
                f"  y={ypct}% white len={len(white)} "
                f"mean_x%={round(100 * white.mean() / w, 1)} "
                f"[{round(100 * white.min() / w, 1)}-{round(100 * white.max() / w, 1)}]"
            )
    print("FAB maroon:")
    for ypct in range(78, 92):
        y = int(h * ypct / 100)
        row = arr[y]
        maroon = np.where(
            (row[:, 0] > 70)
            & (row[:, 0] < 160)
            & (row[:, 1] < 70)
            & (row[:, 2] < 90)
            & (row[:, 0] > row[:, 1] + 25)
        )[0]
        if len(maroon) > 30:
            print(f"  y={ypct}% count={len(maroon)} mean_x%={round(100 * maroon.mean() / w, 1)}")
    print("search bar light band:")
    for ypct in range(50, 62):
        y = int(h * ypct / 100)
        row = arr[y]
        white = np.where((row[:, 0] > 245) & (row[:, 1] > 245) & (row[:, 2] > 245))[0]
        if len(white) > 400:
            print(f"  y={ypct}% white={len(white)}")


def analyze_wishlist() -> None:
    im = Image.open(BASE / "04-wishlist-grails.png").convert("RGB")
    w, h = im.size
    arr = np.array(im)
    print(f"\nwishlist {w}x{h}")
    for ypct in range(38, 55):
        y = int(h * ypct / 100)
        row = arr[y]
        white = np.where((row[:, 0] > 240) & (row[:, 1] > 240) & (row[:, 2] > 240))[0]
        if 40 < len(white) < 500:
            print(
                f"  segment y={ypct}% white [{round(100 * white.min() / w, 1)}-"
                f"{round(100 * white.max() / w, 1)}] mean={round(100 * white.mean() / w, 1)}"
            )


if __name__ == "__main__":
    analyze_home()
    analyze_museum()
    analyze_wishlist()
