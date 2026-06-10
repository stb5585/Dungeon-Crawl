"""Build the enemy render atlas from individual archetype source images."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


RENDER_KEYS = [
    "goblin",
    "kobold",
    "bandit",
    "cultist",
    "dark_knight",
    "orc",
    "skeleton",
    "skeleton_warrior",
    "zombie",
    "ghost",
    "wraith",
    "lich",
    "wolf",
    "dire_wolf",
    "bear",
    "boar",
    "giant_rat",
    "spider",
    "giant_spider",
    "scorpion",
    "insect",
    "slime",
    "ooze",
    "bat",
    "harpy",
    "gargoyle",
    "fire_elemental",
    "water_elemental",
    "earth_elemental",
    "air_elemental",
    "shadow_elemental",
    "demon",
    "greater_demon",
    "dragon",
    "wyrm",
    "boss",
    "generic_enemy",
]

FRAME_SIZE = (256, 320)
ATLAS_COLUMNS = 8
REVIEW_COLUMNS = 8
REVIEW_LABEL_HEIGHT = 32


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_asset_dir() -> Path:
    return project_root() / "src" / "ui_pygame" / "assets" / "enemy_renders"


def load_source_image(asset_dir: Path, key: str) -> Image.Image:
    path = asset_dir / f"{key}.png"
    if not path.exists():
        raise FileNotFoundError(f"Missing enemy render source image: {path}")
    image = Image.open(path).convert("RGBA")
    if image.size != FRAME_SIZE:
        image = image.resize(FRAME_SIZE, Image.Resampling.LANCZOS)
    return image


def build_atlas(asset_dir: Path) -> dict[str, dict[str, int]]:
    rows = (len(RENDER_KEYS) + ATLAS_COLUMNS - 1) // ATLAS_COLUMNS
    atlas = Image.new("RGBA", (ATLAS_COLUMNS * FRAME_SIZE[0], rows * FRAME_SIZE[1]), (0, 0, 0, 0))
    manifest: dict[str, dict[str, int]] = {}

    for index, key in enumerate(RENDER_KEYS):
        col = index % ATLAS_COLUMNS
        row = index // ATLAS_COLUMNS
        x = col * FRAME_SIZE[0]
        y = row * FRAME_SIZE[1]
        atlas.alpha_composite(load_source_image(asset_dir, key), (x, y))
        manifest[key] = {"x": x, "y": y, "w": FRAME_SIZE[0], "h": FRAME_SIZE[1]}

    atlas.save(asset_dir / "enemy_render_atlas.png")
    (asset_dir / "enemy_render_atlas.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def label_for_key(key: str) -> str:
    return key.replace("_", " ").title()


def build_review_sheet(asset_dir: Path) -> None:
    rows = (len(RENDER_KEYS) + REVIEW_COLUMNS - 1) // REVIEW_COLUMNS
    cell_width = FRAME_SIZE[0]
    cell_height = FRAME_SIZE[1] + REVIEW_LABEL_HEIGHT
    sheet = Image.new("RGB", (REVIEW_COLUMNS * cell_width, rows * cell_height), (11, 10, 9))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default()

    for index, key in enumerate(RENDER_KEYS):
        col = index % REVIEW_COLUMNS
        row = index // REVIEW_COLUMNS
        x = col * cell_width
        y = row * cell_height
        image = load_source_image(asset_dir, key).convert("RGB")
        sheet.paste(image, (x, y))
        draw.rectangle((x, y + FRAME_SIZE[1], x + cell_width - 1, y + cell_height - 1), fill=(16, 14, 12))
        draw.text((x + 8, y + FRAME_SIZE[1] + 10), label_for_key(key), fill=(214, 201, 177), font=font)

    sheet.save(asset_dir / "enemy_render_review_sheet.png")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--asset-dir",
        type=Path,
        default=default_asset_dir(),
        help="Directory containing one PNG per enemy render archetype.",
    )
    parser.add_argument(
        "--skip-review-sheet",
        action="store_true",
        help="Only rebuild the runtime atlas and manifest.",
    )
    args = parser.parse_args()

    asset_dir = args.asset_dir.resolve()
    build_atlas(asset_dir)
    if not args.skip_review_sheet:
        build_review_sheet(asset_dir)
    print(f"Built enemy render atlas in {asset_dir}")


if __name__ == "__main__":
    main()
