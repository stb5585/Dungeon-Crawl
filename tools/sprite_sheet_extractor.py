#!/usr/bin/env python3
"""
Sprite sheet extractor.

Slices a sheet into fixed-size sprites and skips fully transparent tiles.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def _is_empty_sprite(sprite: Image.Image, alpha_threshold: int) -> bool:
    if sprite.mode != "RGBA":
        sprite = sprite.convert("RGBA")

    alpha = sprite.getchannel("A")
    if alpha_threshold <= 0:
        return alpha.getbbox() is None

    mask = alpha.point(lambda a: 255 if a > alpha_threshold else 0)
    return mask.getbbox() is None


def _alpha_coverage(sprite: Image.Image, alpha_threshold: int) -> float:
    if sprite.mode != "RGBA":
        sprite = sprite.convert("RGBA")

    alpha = sprite.getchannel("A")
    pixels = alpha.getdata()
    total = len(pixels)
    if total == 0:
        return 0.0

    if alpha_threshold <= 0:
        active = sum(1 for a in pixels if a > 0)
    else:
        active = sum(1 for a in pixels if a > alpha_threshold)
    return active / total


def report_sizes(
    image_path: Path,
    sizes: list[int],
    alpha_threshold: int,
) -> None:
    with Image.open(image_path) as img:
        img = img.convert("RGBA")
        width, height = img.size

        for sprite_size in sizes:
            if sprite_size <= 0:
                continue
            if width % sprite_size != 0 or height % sprite_size != 0:
                continue

            cols = width // sprite_size
            rows = height // sprite_size
            tiles = cols * rows
            empty = 0
            coverage_sum = 0.0
            non_empty = 0

            for row in range(rows):
                for col in range(cols):
                    left = col * sprite_size
                    top = row * sprite_size
                    right = left + sprite_size
                    bottom = top + sprite_size
                    sprite = img.crop((left, top, right, bottom))

                    if _is_empty_sprite(sprite, alpha_threshold):
                        empty += 1
                        continue

                    non_empty += 1
                    coverage_sum += _alpha_coverage(sprite, alpha_threshold)

            avg_coverage = coverage_sum / max(non_empty, 1)
            empty_ratio = empty / max(tiles, 1)
            print(
                f"size={sprite_size:>3} tiles={tiles:>6} empty={empty:>6} "
                f"empty_ratio={empty_ratio:>6.2%} avg_coverage={avg_coverage:>6.2%}"
            )


def create_contact_sheet(
    sprites: list[dict],
    output_path: Path,
    sprite_size: int,
    cols: int,
    label: bool,
) -> None:
    if not sprites:
        print("No sprites available for contact sheet.")
        return

    rows = (len(sprites) + cols - 1) // cols
    label_height = 12 if label else 0
    cell_height = sprite_size + label_height

    sheet_width = cols * sprite_size
    sheet_height = rows * cell_height

    sheet = Image.new("RGBA", (sheet_width, sheet_height), (0, 0, 0, 0))
    font = ImageFont.load_default() if label else None

    def fit_label(text: str, max_width: int, draw: ImageDraw.ImageDraw) -> str:
        if font is None:
            return text
        if draw.textlength(text, font=font) <= max_width:
            return text
        trimmed = text
        while trimmed:
            candidate = f"{trimmed[:-1]}"
            if draw.textlength(candidate, font=font) <= max_width:
                return candidate
            trimmed = trimmed[:-1]
        return ""

    for index, entry in enumerate(sprites):
        row = index // cols
        col = index % cols

        sprite_path = Path(entry["path"])
        with Image.open(sprite_path) as sprite:
            sprite = sprite.convert("RGBA")
            x = col * sprite_size
            y = row * cell_height
            sheet.paste(sprite, (x, y))

            if label and font is not None:
                label_text = f"{entry['row']},{entry['col']}"
                label_box = Image.new("RGBA", (sprite_size, label_height), (0, 0, 0, 160))
                label_draw = ImageDraw.Draw(label_box)
                fitted = fit_label(label_text, sprite_size - 2, label_draw)
                label_draw.text((1, 0), fitted, fill=(255, 255, 255, 255), font=font)
                sheet.paste(label_box, (x, y + sprite_size), label_box)

    sheet.save(output_path, format="PNG")
    print(f"Contact sheet saved: {output_path}")


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def extract_sprites(
    image_path: Path,
    output_dir: Path,
    tile_size: int | None,
    sprite_tiles: int | None,
    sprite_size: int | None,
    prefix: str,
    alpha_threshold: int,
    write_manifest: bool,
    write_contact_sheet: bool,
    contact_cols: int,
    contact_labels: bool,
) -> None:
    if sprite_size is None:
        if tile_size is None or sprite_tiles is None:
            raise SystemExit("Provide --sprite-size or both --tile-size and --sprite-tiles")
        sprite_size = tile_size * sprite_tiles
    else:
        if tile_size is None:
            tile_size = sprite_size
        if sprite_tiles is None:
            sprite_tiles = 1

    with Image.open(image_path) as img:
        img = img.convert("RGBA")
        width, height = img.size

        cols = width // sprite_size
        rows = height // sprite_size

        if width % sprite_size != 0 or height % sprite_size != 0:
            print(
                f"Warning: sheet size {width}x{height} is not an even multiple of "
                f"sprite size {sprite_size}. Remainder pixels will be ignored."
            )

        _ensure_dir(output_dir)

        manifest = {
            "source": str(image_path),
            "tile_size": tile_size,
            "sprite_tiles": sprite_tiles,
            "sprite_size": sprite_size,
            "rows": rows,
            "cols": cols,
            "sprites": [],
        }

        saved_count = 0
        for row in range(rows):
            for col in range(cols):
                left = col * sprite_size
                top = row * sprite_size
                right = left + sprite_size
                bottom = top + sprite_size

                sprite = img.crop((left, top, right, bottom))

                if _is_empty_sprite(sprite, alpha_threshold):
                    continue

                filename = f"{prefix}_r{row:03d}_c{col:03d}.png"
                output_path = output_dir / filename
                sprite.save(output_path, format="PNG")

                manifest["sprites"].append(
                    {
                        "row": row,
                        "col": col,
                        "box": [left, top, right, bottom],
                        "path": str(output_path),
                    }
                )
                saved_count += 1

    if write_manifest:
        manifest_path = output_dir / f"{prefix}_manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"Manifest saved: {manifest_path}")

        if write_contact_sheet:
            contact_path = output_dir / f"{prefix}_contact_sheet.png"
            create_contact_sheet(
                sprites=manifest["sprites"],
                output_path=contact_path,
                sprite_size=sprite_size,
                cols=contact_cols,
                label=contact_labels,
            )

    print(f"Saved {saved_count} sprites to {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract fixed-size sprites from a sheet.")
    parser.add_argument(
        "image",
        type=str,
        help="Path to sprite sheet image",
    )
    parser.add_argument(
        "--report-sizes",
        action="store_true",
        help="Print stats for common sprite sizes and exit",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="src/ui_pygame/assets/sprites/sheet_extracted",
        help="Output directory for sprites",
    )
    parser.add_argument(
        "--tile-size",
        type=int,
        default=None,
        help="Base tile size in pixels (use with --sprite-tiles)",
    )
    parser.add_argument(
        "--sprite-tiles",
        type=int,
        default=None,
        help="Sprite size in tiles (sprite size = tile size * sprite tiles)",
    )
    parser.add_argument(
        "--sprite-size",
        type=int,
        default=32,
        help="Sprite size in pixels (overrides --tile-size/--sprite-tiles)",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="sheet",
        help="Output filename prefix",
    )
    parser.add_argument(
        "--alpha-threshold",
        type=int,
        default=0,
        help="Alpha threshold (0-255) for empty sprite detection",
    )
    parser.add_argument(
        "--no-contact-sheet",
        action="store_true",
        help="Do not write a contact sheet image",
    )
    parser.add_argument(
        "--contact-cols",
        type=int,
        default=32,
        help="Number of columns in the contact sheet",
    )
    parser.add_argument(
        "--contact-no-labels",
        action="store_true",
        help="Disable row/col labels on the contact sheet",
    )
    parser.add_argument(
        "--no-manifest",
        action="store_true",
        help="Do not write a JSON manifest",
    )

    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        raise SystemExit(f"Image not found: {image_path}")

    if args.report_sizes:
        common_sizes = [8, 12, 16, 20, 24, 32, 40, 48, 64]
        report_sizes(
            image_path=image_path,
            sizes=common_sizes,
            alpha_threshold=args.alpha_threshold,
        )
        return

    output_dir = Path(args.output_dir)

    extract_sprites(
        image_path=image_path,
        output_dir=output_dir,
        tile_size=args.tile_size,
        sprite_tiles=args.sprite_tiles,
        sprite_size=args.sprite_size,
        prefix=args.prefix,
        alpha_threshold=args.alpha_threshold,
        write_manifest=not args.no_manifest,
        write_contact_sheet=not args.no_contact_sheet,
        contact_cols=args.contact_cols,
        contact_labels=not args.contact_no_labels,
    )


if __name__ == "__main__":
    main()
