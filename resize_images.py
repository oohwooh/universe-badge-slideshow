#!/usr/bin/env python3
"""Resize photos from input/ into 320x240 PNGs for the badge slideshow app.

Usage:
    nix-shell --run "python3 resize_images.py"

Crops each image to the badge's 4:3 aspect ratio (center crop) before
resizing, so photos don't get stretched or squished. Output filenames are
slugified (lowercase, spaces/underscores collapsed).
"""

import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

INPUT_DIR = Path(__file__).parent / "input"
OUTPUT_DIR = Path(__file__).parent / "app" / "images"
TARGET_SIZE = (320, 240)
SOURCE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif", ".tiff"}


def slugify(stem):
    slug = re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")
    return slug or "photo"


def cover_crop(img, target_size):
    target_w, target_h = target_size
    target_ratio = target_w / target_h
    w, h = img.size
    ratio = w / h

    if ratio > target_ratio:
        new_w = int(h * target_ratio)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    elif ratio < target_ratio:
        new_h = int(w / target_ratio)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))

    return img.resize(target_size, Image.LANCZOS)


def main():
    if not INPUT_DIR.exists():
        print(f"No input directory at {INPUT_DIR}")
        return 1

    sources = sorted(
        p for p in INPUT_DIR.iterdir()
        if p.suffix.lower() in SOURCE_EXTS and not p.name.startswith(".")
    )

    skipped = sorted(
        p.name for p in INPUT_DIR.iterdir()
        if p.is_file() and p.suffix.lower() not in SOURCE_EXTS and not p.name.startswith(".")
    )

    if not sources:
        print(f"No images found in {INPUT_DIR}")
        if skipped:
            print(f"Skipped unsupported files: {', '.join(skipped)}")
            print("Convert HEIC/other formats to JPEG or PNG first.")
        return 0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    used_names = set()
    written = 0
    for src in sources:
        try:
            img = Image.open(src)
            img = ImageOps.exif_transpose(img)  # respect phone camera orientation
            img = img.convert("RGB")
        except Exception as exc:
            print(f"Skipping {src.name}: {exc}")
            continue

        slug = slugify(src.stem)
        name = slug
        n = 2
        while name in used_names:
            name = f"{slug}_{n}"
            n += 1
        used_names.add(name)

        out_path = OUTPUT_DIR / f"{name}.png"
        cover_crop(img, TARGET_SIZE).save(out_path, "PNG")
        print(f"{src.name} -> {out_path.relative_to(Path(__file__).parent)}")
        written += 1

    print(f"\nWrote {written} image(s) to {OUTPUT_DIR}")
    if skipped:
        print(f"Skipped unsupported files: {', '.join(skipped)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
