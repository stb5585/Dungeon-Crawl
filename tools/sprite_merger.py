#!/usr/bin/env python3
"""
Sprite merger - Combines two or more sprites into a single larger sprite.

Useful for combining fragmented sprites that were sliced too small.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def merge_sprites_horizontal(sprite_paths: list[Path], output_path: Path) -> None:
    """Merge sprites side-by-side (left-to-right)."""
    sprites = [Image.open(p).convert("RGBA") for p in sprite_paths]
    
    width = sum(s.width for s in sprites)
    height = max(s.height for s in sprites)
    
    merged = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    
    x_offset = 0
    for sprite in sprites:
        merged.paste(sprite, (x_offset, 0), sprite)
        x_offset += sprite.width
    
    merged.save(output_path, format="PNG")
    print(f"Merged {len(sprites)} sprites horizontally: {output_path}")


def merge_sprites_vertical(sprite_paths: list[Path], output_path: Path) -> None:
    """Merge sprites vertically (top-to-bottom)."""
    sprites = [Image.open(p).convert("RGBA") for p in sprite_paths]
    
    width = max(s.width for s in sprites)
    height = sum(s.height for s in sprites)
    
    merged = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    
    y_offset = 0
    for sprite in sprites:
        merged.paste(sprite, (0, y_offset), sprite)
        y_offset += sprite.height
    
    merged.save(output_path, format="PNG")
    print(f"Merged {len(sprites)} sprites vertically: {output_path}")


def merge_sprites_grid(
    sprite_paths: list[Path], output_path: Path, cols: int | None = None
) -> None:
    """Merge sprites into a grid (default: auto-calculate columns)."""
    sprites = [Image.open(p).convert("RGBA") for p in sprite_paths]
    
    if not sprites:
        print("No sprites to merge.")
        return
    
    if cols is None:
        # Auto-calculate columns: prefer 2x2, 3x3, etc.
        import math
        cols = max(2, int(math.ceil(math.sqrt(len(sprites)))))
    
    rows = (len(sprites) + cols - 1) // cols
    
    sprite_width = max(s.width for s in sprites)
    sprite_height = max(s.height for s in sprites)
    
    merged_width = cols * sprite_width
    merged_height = rows * sprite_height
    
    merged = Image.new("RGBA", (merged_width, merged_height), (0, 0, 0, 0))
    
    for idx, sprite in enumerate(sprites):
        row = idx // cols
        col = idx % cols
        x = col * sprite_width
        y = row * sprite_height
        
        # Center smaller sprites if needed
        x_offset = (sprite_width - sprite.width) // 2
        y_offset = (sprite_height - sprite.height) // 2
        
        merged.paste(sprite, (x + x_offset, y + y_offset), sprite)
    
    merged.save(output_path, format="PNG")
    print(f"Merged {len(sprites)} sprites into {rows}x{cols} grid: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge multiple sprites into a single image."
    )
    parser.add_argument(
        "sprites",
        nargs="+",
        help="Paths to sprite images to merge",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        required=True,
        help="Output sprite path",
    )
    parser.add_argument(
        "--mode",
        choices=["horizontal", "vertical", "grid"],
        default="horizontal",
        help="Merge mode: horizontal (left-right), vertical (top-bottom), or grid",
    )
    parser.add_argument(
        "--cols",
        type=int,
        default=None,
        help="Number of columns for grid mode (auto-calculated if omitted)",
    )
    
    args = parser.parse_args()
    
    sprite_paths = [Path(s) for s in args.sprites]
    output_path = Path(args.output)
    
    # Verify all input files exist
    for path in sprite_paths:
        if not path.exists():
            raise SystemExit(f"Sprite not found: {path}")
    
    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if args.mode == "horizontal":
        merge_sprites_horizontal(sprite_paths, output_path)
    elif args.mode == "vertical":
        merge_sprites_vertical(sprite_paths, output_path)
    elif args.mode == "grid":
        merge_sprites_grid(sprite_paths, output_path, args.cols)


if __name__ == "__main__":
    main()
