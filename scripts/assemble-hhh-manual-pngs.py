#!/usr/bin/env python3
"""Copy best HHH manual PNGs into assets/screenshots/hhh/manual/."""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "screenshots" / "hhh" / "manual"
HHH = Path(r"C:\Users\jossp\Documents\MobileApps\HHH\SourceCode")
HERO = ROOT / "assets" / "screenshots" / "hhh"

PAIRS = [
    (HHH / "manual" / "01-home-command-center.png", OUT / "01-home-command-center.png"),
    (HHH / "manual" / "02-museum-collection.png", OUT / "02-museum-collection.png"),
    (HHH / "manual" / "03-piece-detail.png", OUT / "03-piece-detail.png"),
    (HHH / "manual" / "04-wishlist-grails.png", OUT / "04-wishlist-grails.png"),
    (HERO / "feature-clockworks.png", OUT / "06a-clock-repair-symptoms.png"),
    (HERO / "feature-clockworks.png", OUT / "06-clockworks-parts.png"),
    (HERO / "feature-identify.png", OUT / "07a-identify-camera.png"),
    (HERO / "feature-identify.png", OUT / "07-identify-results.png"),
    (HERO / "05-pro-tools.png", OUT / "08-tools-hub.png"),
    (HERO / "06-web-companion.png", OUT / "09-web-companion.png"),
    (HERO / "_alert.png", OUT / "10-settings.png"),
    (HERO / "_alert.png", OUT / "11-backup-restore.png"),
    (HERO / "05-pro-tools.png", OUT / "12-trial-subscription.png"),
]

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for src, dest in PAIRS:
        if not src.exists():
            raise SystemExit(f"missing {src}")
        shutil.copy2(src, dest)
        print(f"copied {dest.name} ({dest.stat().st_size})")
    # hero parity
    mapping = {
        "02-museum-collection.png": "01-home-museum.png",
        "07-identify-results.png": "02-ai-identify.png",
        "06-clockworks-parts.png": "03-clockworks-wizard.png",
        "04-wishlist-grails.png": "08-wishlist-grails.png",
    }
    for src_name, dest_name in mapping.items():
        shutil.copy2(OUT / src_name, HERO / dest_name)
        print(f"hero {dest_name}")

if __name__ == "__main__":
    main()
