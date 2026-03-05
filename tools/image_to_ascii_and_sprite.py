#!/usr/bin/env python3
"""
Image -> ASCII + Sprite converter

Takes a source image and generates:
1) ASCII art text file (for curses)
2) Pixel sprite PNG (for pygame)

Designed for artist images so sprites keep more detail than ASCII-based generation.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps

ASCII_CHARS = " .:-=+*#%@"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def image_to_ascii(img: Image.Image, cols: int, invert: bool) -> str:
    # Convert to grayscale
    gray = ImageOps.grayscale(img)
    if invert:
        gray = ImageOps.invert(gray)

    width, height = gray.size
    aspect_ratio = height / max(width, 1)
    # Adjust height for character aspect (approx 2:1)
    rows = max(1, int(cols * aspect_ratio * 0.5))

    resized = gray.resize((cols, rows), Image.Resampling.LANCZOS)

    pixels = list(resized.getdata())
    ascii_str = ""
    for i, px in enumerate(pixels):
        idx = int(px / 255 * (len(ASCII_CHARS) - 1))
        ascii_str += ASCII_CHARS[idx]
        if (i + 1) % cols == 0:
            ascii_str += "\n"
    return ascii_str


def image_to_sprite(img: Image.Image, size: int, colors: int, dither: bool) -> Image.Image:
    # Center-crop to square, then resize
    img = ImageOps.exif_transpose(img)
    width, height = img.size
    min_dim = min(width, height)
    left = (width - min_dim) // 2
    top = (height - min_dim) // 2
    img = img.crop((left, top, left + min_dim, top + min_dim))

    resized = img.resize((size, size), Image.Resampling.LANCZOS)

    # Quantize to reduce colors and create pixel-art feel
    dither_mode = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE
    quantized = resized.convert("RGBA").quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=dither_mode)

    return quantized.convert("RGBA")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert image to ASCII art and pixel sprite.")
    parser.add_argument("image", type=str, help="Path to input image")
    parser.add_argument("--name", type=str, default=None, help="Output base name (without extension)")
    parser.add_argument("--ascii-cols", type=int, default=64, help="ASCII art width in characters")
    parser.add_argument("--invert", action="store_true", help="Invert brightness for ASCII")
    parser.add_argument("--sprite-size", type=int, default=128, help="Sprite output size in pixels")
    parser.add_argument("--colors", type=int, default=32, help="Number of colors for sprite quantization")
    parser.add_argument("--dither", action="store_true", help="Enable dithering for sprite")
    parser.add_argument("--ascii-out", type=str, default="ascii_files", help="ASCII output directory")
    parser.add_argument("--sprite-out", type=str, default="src/ui_pygame/assets/sprites", help="Sprite output directory")

    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        raise SystemExit(f"Image not found: {image_path}")

    base_name = args.name or image_path.stem

    ascii_dir = Path(args.ascii_out)
    sprite_dir = Path(args.sprite_out)
    _ensure_dir(ascii_dir)
    _ensure_dir(sprite_dir)

    with Image.open(image_path) as img:
        ascii_art = image_to_ascii(img, cols=args.ascii_cols, invert=args.invert)
        sprite_img = image_to_sprite(img, size=args.sprite_size, colors=args.colors, dither=args.dither)

    ascii_path = ascii_dir / f"{base_name}.txt"
    sprite_path = sprite_dir / f"{base_name}.png"

    ascii_path.write_text(ascii_art, encoding="utf-8")
    sprite_img.save(sprite_path, format="PNG")

    print(f"ASCII saved: {ascii_path}")
    print(f"Sprite saved: {sprite_path}")


if __name__ == "__main__":
    main()
