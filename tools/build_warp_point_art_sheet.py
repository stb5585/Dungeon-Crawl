#!/usr/bin/env python3
"""Build a review sheet for generated Warp Point dungeon art."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DEFAULT_SPECIAL_ROOT = PROJECT_ROOT / "src" / "ui_pygame" / "assets" / "dungeon_tiles" / "special_tiles"
DEFAULT_OUTPUT = DEFAULT_SPECIAL_ROOT / "warp_point_art_review_sheet.png"
WARP_POINT_ASSETS = (
    ("active", "warp_point_active.png"),
    ("inactive", "warp_point_inactive.png"),
)
CELL_SIZE = (260, 300)
PREVIEW_SIZE = (220, 220)
HEADER_HEIGHT = 42
BACKGROUND = (24, 24, 28, 255)
LABEL = (232, 232, 238, 255)
BORDER = (78, 78, 88, 255)


def draw_review_sheet(asset_root: Path, output: Path) -> None:
    font = ImageFont.load_default()
    sheet = Image.new(
        "RGBA",
        (len(WARP_POINT_ASSETS) * CELL_SIZE[0], HEADER_HEIGHT + CELL_SIZE[1]),
        BACKGROUND,
    )
    draw = ImageDraw.Draw(sheet)
    draw.text((14, 14), "Warp Point art", fill=LABEL, font=font)

    for index, (label, filename) in enumerate(WARP_POINT_ASSETS):
        x = index * CELL_SIZE[0]
        y = HEADER_HEIGHT
        draw.rectangle(
            (x + 8, y + 8, x + CELL_SIZE[0] - 8, y + CELL_SIZE[1] - 8),
            outline=BORDER,
        )

        path = asset_root / filename
        if path.exists():
            sprite = Image.open(path).convert("RGBA")
            preview = sprite.copy()
            preview.thumbnail(PREVIEW_SIZE, Image.Resampling.LANCZOS)
            preview_x = x + (CELL_SIZE[0] - preview.width) // 2
            preview_y = y + 22 + (PREVIEW_SIZE[1] - preview.height) // 2
            sheet.alpha_composite(preview, (preview_x, preview_y))

        text = f"{label}: {filename}"
        text_width = draw.textlength(text, font=font)
        draw.text((x + (CELL_SIZE[0] - text_width) / 2, y + CELL_SIZE[1] - 34), text, fill=LABEL, font=font)

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-root", type=Path, default=DEFAULT_SPECIAL_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    draw_review_sheet(args.asset_root, args.output)
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
