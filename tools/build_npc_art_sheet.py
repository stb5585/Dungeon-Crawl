"""Build a review sheet for approved NPC dialogue bust artwork."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ART_ROOT = PROJECT_ROOT / "src" / "ui_pygame" / "assets" / "npc_art"
DEFAULT_REVIEW_SHEET = PROJECT_ROOT / "docs" / "assets" / "review-sheets" / "npc-art.png"
CELL_SIZE = (220, 300)
PREVIEW_SIZE = (170, 230)
HEADER_HEIGHT = 42
BACKGROUND = (22, 22, 24, 255)
LABEL = (232, 232, 238, 255)
BORDER = (74, 74, 82, 255)


def mapped_npc_keys(art_root: Path) -> list[str]:
    map_path = art_root / "npc_art_map.json"
    keys: set[str] = set()
    if map_path.exists():
        data = json.loads(map_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            keys.update(str(key) for key in data.values())
    return sorted(keys)


def draw_review_sheet(art_root: Path, output: Path, *, columns: int = 4) -> None:
    keys = mapped_npc_keys(art_root)
    if not keys:
        raise SystemExit(f"No mapped NPC art found in {art_root}")

    font = ImageFont.load_default()
    rows = (len(keys) + columns - 1) // columns
    sheet = Image.new(
        "RGBA",
        (columns * CELL_SIZE[0], HEADER_HEIGHT + rows * CELL_SIZE[1]),
        BACKGROUND,
    )
    draw = ImageDraw.Draw(sheet)
    draw.text((14, 14), "NPC Art Review", fill=LABEL, font=font)

    for index, key in enumerate(keys):
        path = art_root / f"{key}.png"
        if not path.exists():
            continue
        col = index % columns
        row = index // columns
        x = col * CELL_SIZE[0]
        y = HEADER_HEIGHT + row * CELL_SIZE[1]
        draw.rectangle(
            (x + 8, y + 8, x + CELL_SIZE[0] - 8, y + CELL_SIZE[1] - 8),
            outline=BORDER,
        )

        sprite = Image.open(path).convert("RGBA")
        preview = sprite.copy()
        preview.thumbnail(PREVIEW_SIZE, Image.Resampling.LANCZOS)
        preview_x = x + (CELL_SIZE[0] - preview.width) // 2
        preview_y = y + 18 + (PREVIEW_SIZE[1] - preview.height) // 2
        sheet.alpha_composite(preview, (preview_x, preview_y))

        label = key.replace("_", " ")
        text_width = draw.textlength(label, font=font)
        draw.text(
            (x + (CELL_SIZE[0] - text_width) / 2, y + CELL_SIZE[1] - 34),
            label,
            fill=LABEL,
            font=font,
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.convert("RGB").save(output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--art-root", type=Path, default=DEFAULT_ART_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_REVIEW_SHEET)
    parser.add_argument("--columns", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    draw_review_sheet(args.art_root, args.output, columns=max(1, args.columns))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
