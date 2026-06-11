"""Build a side-by-side review sheet for enemy visual layers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.build_enemy_render_atlas import RENDER_KEYS, label_for_key, project_root


SOURCE_SIZE = (128, 160)
TOKEN_SIZE = (96, 96)
COMBAT_SIZE = (160, 200)
LABEL_HEIGHT = 42
HEADER_HEIGHT = 26
CELL_PAD = 12
CELL_WIDTH = SOURCE_SIZE[0] + TOKEN_SIZE[0] + COMBAT_SIZE[0] + (CELL_PAD * 5)
CELL_HEIGHT = max(SOURCE_SIZE[1], TOKEN_SIZE[1], COMBAT_SIZE[1]) + LABEL_HEIGHT + HEADER_HEIGHT
REVIEW_COLUMNS = 3


def default_render_dir() -> Path:
    return project_root() / "src" / "ui_pygame" / "assets" / "enemy_renders"


def default_combat_art_dir() -> Path:
    return project_root() / "src" / "ui_pygame" / "assets" / "enemy_combat_art"


def fit_image(path: Path, target: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    scale = min(target[0] / image.width, target[1] / image.height)
    size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    fitted = image.resize(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", target, (0, 0, 0, 0))
    canvas.alpha_composite(fitted, ((target[0] - size[0]) // 2, (target[1] - size[1]) // 2))
    return canvas


def load_crop_overrides(render_dir: Path) -> dict[str, dict[str, int]]:
    crop_path = render_dir / "enemy_token_crop.json"
    try:
        data = json.loads(crop_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {str(key): value for key, value in data.items() if isinstance(value, dict)}


def token_image(render_path: Path, crop: dict[str, Any] | None) -> Image.Image:
    source = Image.open(render_path).convert("RGBA")
    if crop:
        try:
            box = (
                int(crop["crop_x"]),
                int(crop["crop_y"]),
                int(crop["crop_x"]) + int(crop["crop_w"]),
                int(crop["crop_y"]) + int(crop["crop_h"]),
            )
        except (KeyError, TypeError, ValueError):
            box = None
    else:
        box = None

    if box is None:
        crop_size = int(min(source.size) * 0.72)
        x = (source.width - crop_size) // 2
        y = int(source.height * 0.12)
        box = (x, y, x + crop_size, min(source.height, y + crop_size))

    cropped = source.crop(box).resize(TOKEN_SIZE, Image.Resampling.LANCZOS)
    mask = Image.new("L", TOKEN_SIZE, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((4, 4, TOKEN_SIZE[0] - 4, TOKEN_SIZE[1] - 4), fill=255)
    token = Image.new("RGBA", TOKEN_SIZE, (0, 0, 0, 0))
    token.alpha_composite(cropped)
    token.putalpha(mask)
    return token


def draw_centered_label(
    draw: ImageDraw.ImageDraw,
    font: ImageFont.ImageFont,
    text: str,
    box: tuple[int, int, int, int],
    fill: tuple[int, int, int],
) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    x = box[0] + ((box[2] - box[0] - width) // 2)
    y = box[1] + ((box[3] - box[1] - height) // 2)
    draw.text((x, y), text, fill=fill, font=font)


def build_review_sheet(render_dir: Path, combat_art_dir: Path, output_path: Path) -> None:
    rows = (len(RENDER_KEYS) + REVIEW_COLUMNS - 1) // REVIEW_COLUMNS
    sheet = Image.new("RGB", (REVIEW_COLUMNS * CELL_WIDTH, rows * CELL_HEIGHT), (11, 10, 9))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()
    crops = load_crop_overrides(render_dir)

    headers = (
        ("Render", SOURCE_SIZE[0]),
        ("Token", TOKEN_SIZE[0]),
        ("Combat Art", COMBAT_SIZE[0]),
    )

    for index, key in enumerate(RENDER_KEYS):
        col = index % REVIEW_COLUMNS
        row = index // REVIEW_COLUMNS
        x = col * CELL_WIDTH
        y = row * CELL_HEIGHT
        draw.rectangle((x + 2, y + 2, x + CELL_WIDTH - 3, y + CELL_HEIGHT - 3), outline=(56, 48, 36))
        draw.rectangle((x + 3, y + 3, x + CELL_WIDTH - 4, y + LABEL_HEIGHT - 1), fill=(18, 16, 14))
        draw.text((x + 10, y + 14), label_for_key(key), fill=(224, 211, 184), font=font)

        content_y = y + LABEL_HEIGHT
        cursor_x = x + CELL_PAD
        for header, width in headers:
            draw_centered_label(
                draw,
                font,
                header,
                (cursor_x, content_y, cursor_x + width, content_y + HEADER_HEIGHT),
                (156, 142, 116),
            )
            cursor_x += width + CELL_PAD

        art_y = content_y + HEADER_HEIGHT
        render_path = render_dir / f"{key}.png"
        combat_path = combat_art_dir / f"{key}.png"

        render = fit_image(render_path, SOURCE_SIZE).convert("RGB")
        sheet.paste(render, (x + CELL_PAD, art_y), render.convert("RGBA"))

        token = token_image(render_path, crops.get(key))
        token_x = x + CELL_PAD + SOURCE_SIZE[0] + CELL_PAD
        token_y = art_y + ((COMBAT_SIZE[1] - TOKEN_SIZE[1]) // 2)
        sheet.paste(token.convert("RGB"), (token_x, token_y), token)

        combat = fit_image(combat_path, COMBAT_SIZE).convert("RGB")
        combat_x = token_x + TOKEN_SIZE[0] + CELL_PAD
        sheet.paste(combat, (combat_x, art_y), combat.convert("RGBA"))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-dir", type=Path, default=default_render_dir())
    parser.add_argument("--combat-art-dir", type=Path, default=default_combat_art_dir())
    parser.add_argument(
        "--output",
        type=Path,
        default=default_combat_art_dir() / "enemy_combat_art_review_sheet.png",
    )
    args = parser.parse_args()
    build_review_sheet(args.render_dir.resolve(), args.combat_art_dir.resolve(), args.output.resolve())
    print(f"Built enemy combat art review sheet: {args.output.resolve()}")


if __name__ == "__main__":
    main()
