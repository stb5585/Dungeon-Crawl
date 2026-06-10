"""Validate enemy render atlas files and token crop metadata."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.build_enemy_render_atlas import FRAME_SIZE, RENDER_KEYS  # noqa: E402


def default_asset_dir() -> Path:
    return PROJECT_ROOT / "src" / "ui_pygame" / "assets" / "enemy_renders"


def _load_json(path: Path) -> tuple[dict[str, Any], list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}, [f"missing file: {path}"]
    except json.JSONDecodeError as exc:
        return {}, [f"invalid JSON in {path}: {exc}"]
    if not isinstance(data, dict):
        return {}, [f"expected object JSON in {path}"]
    return data, []


def _rect_from_entry(key: str, entry: Any) -> tuple[tuple[int, int, int, int] | None, list[str]]:
    if not isinstance(entry, dict):
        return None, [f"{key}: frame entry is not an object"]
    try:
        rect = (int(entry["x"]), int(entry["y"]), int(entry["w"]), int(entry["h"]))
    except (KeyError, TypeError, ValueError) as exc:
        return None, [f"{key}: invalid frame entry: {exc}"]
    return rect, []


def _crop_from_entry(key: str, entry: Any) -> tuple[tuple[int, int, int, int] | None, list[str]]:
    if not isinstance(entry, dict):
        return None, [f"{key}: crop entry is not an object"]
    try:
        rect = (int(entry["crop_x"]), int(entry["crop_y"]), int(entry["crop_w"]), int(entry["crop_h"]))
    except (KeyError, TypeError, ValueError) as exc:
        return None, [f"{key}: invalid crop entry: {exc}"]
    return rect, []


def _rects_overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def validate_enemy_render_atlas(asset_dir: Path) -> list[str]:
    """Return a list of validation issues for the runtime enemy render atlas."""
    issues: list[str] = []
    asset_dir = asset_dir.resolve()
    manifest_path = asset_dir / "enemy_render_atlas.json"
    atlas_path = asset_dir / "enemy_render_atlas.png"
    crop_path = asset_dir / "enemy_token_crop.json"

    manifest, manifest_errors = _load_json(manifest_path)
    issues.extend(manifest_errors)
    crops, crop_errors = _load_json(crop_path)
    issues.extend(crop_errors)

    try:
        atlas_size = Image.open(atlas_path).size
    except FileNotFoundError:
        issues.append(f"missing file: {atlas_path}")
        atlas_size = (0, 0)
    except OSError as exc:
        issues.append(f"could not read atlas image {atlas_path}: {exc}")
        atlas_size = (0, 0)

    expected_rows = (len(RENDER_KEYS) + 7) // 8
    expected_size = (8 * FRAME_SIZE[0], expected_rows * FRAME_SIZE[1])
    if atlas_size != (0, 0) and atlas_size != expected_size:
        issues.append(f"atlas size {atlas_size} does not match expected {expected_size}")

    missing_keys = [key for key in RENDER_KEYS if key not in manifest]
    extra_keys = [key for key in manifest if key not in RENDER_KEYS]
    if missing_keys:
        issues.append(f"manifest missing keys: {', '.join(missing_keys)}")
    if extra_keys:
        issues.append(f"manifest has unexpected keys: {', '.join(extra_keys)}")

    rects: dict[str, tuple[int, int, int, int]] = {}
    for key, entry in manifest.items():
        rect, rect_errors = _rect_from_entry(key, entry)
        issues.extend(rect_errors)
        if rect is None:
            continue
        x, y, w, h = rect
        rects[key] = rect
        if w <= 0 or h <= 0:
            issues.append(f"{key}: frame has non-positive size {w}x{h}")
        if (w, h) != FRAME_SIZE:
            issues.append(f"{key}: frame size {(w, h)} does not match {FRAME_SIZE}")
        if x < 0 or y < 0 or x + w > atlas_size[0] or y + h > atlas_size[1]:
            issues.append(f"{key}: frame {rect} is out of atlas bounds {atlas_size}")
        if x % FRAME_SIZE[0] != 0 or y % FRAME_SIZE[1] != 0:
            issues.append(f"{key}: frame {rect} is not aligned to the atlas grid")

    keys = list(rects)
    for index, key in enumerate(keys):
        for other_key in keys[index + 1 :]:
            if _rects_overlap(rects[key], rects[other_key]):
                issues.append(f"frames overlap: {key} and {other_key}")

    source_pngs = {path.stem for path in asset_dir.glob("*.png")}
    missing_sources = [key for key in RENDER_KEYS if key not in source_pngs]
    if missing_sources:
        issues.append(f"missing source PNGs: {', '.join(missing_sources)}")

    missing_crops = [key for key in RENDER_KEYS if key not in crops]
    if missing_crops:
        issues.append(f"crop JSON missing keys: {', '.join(missing_crops)}")
    for key, entry in crops.items():
        crop, crop_entry_errors = _crop_from_entry(key, entry)
        issues.extend(crop_entry_errors)
        if crop is None:
            continue
        if key not in RENDER_KEYS:
            issues.append(f"crop JSON has unexpected key: {key}")
        x, y, w, h = crop
        if w <= 0 or h <= 0:
            issues.append(f"{key}: crop has non-positive size {w}x{h}")
        if x < 0 or y < 0 or x + w > FRAME_SIZE[0] or y + h > FRAME_SIZE[1]:
            issues.append(f"{key}: token crop {crop} is out of frame bounds {FRAME_SIZE}")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--asset-dir",
        type=Path,
        default=default_asset_dir(),
        help="Enemy render asset directory to validate.",
    )
    args = parser.parse_args()

    issues = validate_enemy_render_atlas(args.asset_dir)
    if not issues:
        print("Enemy render atlas validation passed.")
        return 0

    print("Enemy render atlas validation failed:")
    for issue in issues:
        print(f"- {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
