"""Build deterministic dungeon rendering assets for the pygame renderer."""

from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageEnhance


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DUNGEON_ROOT = PROJECT_ROOT / "src" / "ui_pygame" / "assets" / "dungeon_tiles"
MAP_TILESET_ROOT = PROJECT_ROOT / "map_files" / "tileset"
SOURCE_BOARD = DUNGEON_ROOT / "source" / "dungeon_asset_board.png"
ORGANIC_FLOOR_ATLAS = DUNGEON_ROOT / "source" / "ai" / "roots_fungus_floor_atlas.png"
ORGANIC_OVERLAY_ATLAS = DUNGEON_ROOT / "source" / "ai" / "roots_fungus_overlay_chromakey_atlas.png"
SIZE = 512

TEXTURES = {
    "wall": "walls/brick.png",
    "wall_upper": "walls/stone_upper.png",
    "wall_middle": "walls/stone_middle.png",
    "wall_deep": "walls/stone_deep.png",
    "wall_funhouse": "walls/funhouse.png",
    "wall_funhouse_boundary": "walls/funhouse_boundary.png",
    "door_closed": "walls/closed_door.png",
    "door_open": "walls/opened_door.png",
    "floor": "floors/dirt.png",
    "floor_debris": "floors/debris.png",
    "floor_roots": "floors/roots.png",
    "floor_roots_sparse": "floors/roots_sparse.png",
    "floor_roots_dense": "floors/roots_dense.png",
    "floor_fungus": "floors/fungus.png",
    "floor_fungus_sparse": "floors/fungus_sparse.png",
    "floor_fungus_dense": "floors/fungus_dense.png",
    "floor_root_fungus_mixed": "floors/root_fungus_mixed.png",
    "floor_crystal": "floors/crystal.png",
    "floor_fire": "floors/firepath.png",
    "floor_spring": "floors/underground_spring.png",
    "floor_funhouse": "floors/funhouse.png",
    "floor_pit": "floors/dirt_pit.png",
    "ceiling": "ceilings/stone.png",
    "ceiling_fungus": "ceilings/fungus.png",
    "ceiling_fungus_upper": "ceilings/fungus_upper.png",
    "ceiling_crystal": "ceilings/crystal.png",
    "ceiling_funhouse": "ceilings/funhouse.png",
    "ceiling_pit": "ceilings/stone_pit.png",
}

SPECIAL_TEXTURES = {
    "rubble": "special_tiles/rubble.png",
    "root_growth": "special_tiles/root_growth.png",
    "root_growth_sparse": "special_tiles/root_growth_sparse.png",
    "root_growth_dense": "special_tiles/root_growth_dense.png",
    "fungus_patch": "special_tiles/fungus_patch.png",
    "fungus_patch_sparse": "special_tiles/fungus_patch_sparse.png",
    "fungus_patch_dense": "special_tiles/fungus_patch_dense.png",
    "ceiling_fungus_overlay": "special_tiles/ceiling_fungus_overlay.png",
    "root_fungus_patch": "special_tiles/root_fungus_patch.png",
    "crystal_cluster": "special_tiles/crystal_cluster.png",
    "bone_pile": "special_tiles/bone_pile.png",
    "broken_gear": "special_tiles/broken_gear.png",
    "torch_lit": "special_tiles/torch_lit.png",
    "sconce_unlit": "special_tiles/sconce_unlit.png",
    "sconce_broken": "special_tiles/sconce_broken.png",
}

MAP_ICONS = {
    "rubble_tile": (112, 104, 92),
    "root_growth_tile": (62, 98, 60),
    "fungus_patch_tile": (106, 76, 130),
    "crystal_cluster_tile": (82, 150, 188),
    "bone_pile_tile": (176, 164, 134),
    "broken_gear_tile": (132, 96, 70),
}

BOARD_CELL_MAP = {
    (0, 0): ("texture", "wall"),
    (1, 0): ("texture", "floor"),
    (2, 0): ("texture", "ceiling"),
    (3, 0): ("texture", "door_closed"),
    (0, 1): ("texture", "door_open"),
    (1, 1): ("texture", "floor_fire"),
    (2, 1): ("texture", "floor_spring"),
    (3, 1): ("texture", "floor_crystal"),
    (0, 2): ("special", "rubble"),
    (1, 2): ("special", "root_growth"),
    (2, 2): ("special", "fungus_patch"),
    (3, 2): ("special", "crystal_cluster"),
    (0, 3): ("special", "bone_pile"),
    (1, 3): ("special", "broken_gear"),
    (2, 3): ("special", "torch_lit"),
    (3, 3): ("special", "sconce_broken"),
}

DERIVED_TEXTURE_ALIASES = {
    "wall_upper": "wall",
    "wall_middle": "wall",
    "wall_deep": "ceiling",
    "wall_funhouse": "wall",
    "wall_funhouse_boundary": "wall",
    "floor_debris": "floor",
    "floor_roots": "floor",
    "floor_fungus": "floor",
    "floor_pit": "floor",
    "ceiling_fungus": "ceiling",
    "ceiling_crystal": "ceiling",
    "ceiling_funhouse": "ceiling",
    "ceiling_pit": "ceiling",
    "floor_funhouse": "floor",
}


def clamp(value: int) -> int:
    return max(0, min(255, value))


def jitter(color: tuple[int, int, int], amount: int, rng: random.Random) -> tuple[int, int, int, int]:
    return tuple(clamp(channel + rng.randint(-amount, amount)) for channel in color) + (255,)


def ensure_dirs() -> None:
    for rel_path in list(TEXTURES.values()) + list(SPECIAL_TEXTURES.values()):
        (DUNGEON_ROOT / rel_path).parent.mkdir(parents=True, exist_ok=True)
    MAP_TILESET_ROOT.mkdir(parents=True, exist_ok=True)
    (DUNGEON_ROOT / "source").mkdir(parents=True, exist_ok=True)


def _board_cell(board: Image.Image, col: int, row: int) -> Image.Image:
    starts_x = [22, 328, 633, 939]
    starts_y = [20, 326, 632, 938]
    cell = 286
    left = starts_x[col] + 8
    top = starts_y[row] + 8
    return board.crop((left, top, left + cell - 16, top + cell - 16)).convert("RGBA")


def _scale_texture(cell: Image.Image, inset: int = 22) -> Image.Image:
    if inset > 0 and cell.width > inset * 2 and cell.height > inset * 2:
        cell = cell.crop((inset, inset, cell.width - inset, cell.height - inset))
    return cell.resize((SIZE, SIZE), Image.Resampling.LANCZOS).filter(
        ImageFilter.UnsharpMask(radius=1.0, percent=110)
    )


def _make_seamless_texture(image: Image.Image, edge: int = 112, blur: int = 58) -> Image.Image:
    """Move texture wrap seams into a feathered center so projected wall edges meet cleanly."""
    base = image.convert("RGBA")
    shifted = ImageChops.offset(base, base.width // 2, base.height // 2)
    mask = Image.new("L", base.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle((edge, edge, base.width - edge, base.height - edge), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    return Image.composite(base, shifted, mask).filter(
        ImageFilter.UnsharpMask(radius=1.0, percent=105)
    )


def _dark_background_to_alpha(cell: Image.Image, threshold: int = 52) -> Image.Image:
    rgba = cell.convert("RGBA")
    pixels = rgba.load()
    width, height = rgba.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            brightness = max(r, g, b)
            if brightness < threshold:
                pixels[x, y] = (r, g, b, 0)
            elif brightness < threshold + 42:
                alpha = int(a * ((brightness - threshold) / 42.0))
                pixels[x, y] = (r, g, b, alpha)
    return rgba


def _scale_special(cell: Image.Image) -> Image.Image:
    alpha = _dark_background_to_alpha(cell)
    bounds = alpha.get_bounding_box() if hasattr(alpha, "get_bounding_box") else None
    if bounds is None:
        bounds = alpha.getbbox()
    trimmed = alpha.crop(bounds) if bounds else alpha
    trimmed.thumbnail((SIZE - 36, SIZE - 36), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    canvas.alpha_composite(trimmed, ((SIZE - trimmed.width) // 2, (SIZE - trimmed.height) // 2))
    return canvas.filter(ImageFilter.UnsharpMask(radius=1.0, percent=115))


def _tint_texture(image: Image.Image, color: tuple[int, int, int], strength: float) -> Image.Image:
    overlay = Image.new("RGBA", image.size, color + (0,))
    draw = ImageDraw.Draw(overlay, "RGBA")
    draw.rectangle((0, 0, image.width, image.height), fill=color + (round(255 * strength),))
    return Image.alpha_composite(image.convert("RGBA"), overlay)


def _cool_stone_palette(image: Image.Image, strength: float = 0.28) -> Image.Image:
    result = image.convert("RGBA").copy()
    pixels = result.load()
    for y in range(result.height):
        for x in range(result.width):
            r, g, b, a = pixels[x, y]
            if a <= 0:
                continue
            luminance = (r * 0.30) + (g * 0.58) + (b * 0.12)
            blue_gray = (
                clamp(round((luminance * 0.70) + 10)),
                clamp(round((luminance * 0.82) + 14)),
                clamp(round((luminance * 1.08) + 30)),
            )
            pixels[x, y] = (
                clamp(round((r * (1.0 - strength)) + (blue_gray[0] * strength))),
                clamp(round((g * (1.0 - strength)) + (blue_gray[1] * strength))),
                clamp(round((b * (1.0 - strength)) + (blue_gray[2] * strength))),
                a,
            )
    result = ImageEnhance.Color(result).enhance(0.88)
    return ImageEnhance.Contrast(result).enhance(1.04)


def _transparent_arch_door(closed_door: Image.Image) -> Image.Image:
    result = closed_door.convert("RGBA").copy()
    alpha = result.getchannel("A")
    mask = Image.new("L", result.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle((138, 178, 374, SIZE), fill=255)
    draw.pieslice((138, 42, 374, 278), 180, 360, fill=255)
    draw.rectangle((138, 160, 374, 278), fill=255)
    alpha_pixels = alpha.load()
    mask_pixels = mask.load()
    for y in range(result.height):
        for x in range(result.width):
            if mask_pixels[x, y]:
                alpha_pixels[x, y] = 0
    result.putalpha(alpha)
    frame = Image.new("RGBA", result.size, (0, 0, 0, 0))
    frame_draw = ImageDraw.Draw(frame, "RGBA")
    frame_draw.arc((126, 30, 386, 290), 180, 360, fill=(148, 162, 182, 145), width=5)
    frame_draw.line((126, 160, 126, SIZE), fill=(148, 162, 182, 120), width=5)
    frame_draw.line((386, 160, 386, SIZE), fill=(24, 30, 42, 130), width=6)
    return Image.alpha_composite(result, frame)


def _fit_door_panel(door: Image.Image, wall: Image.Image) -> Image.Image:
    panel = wall.convert("RGBA").copy()
    panel = _tint_texture(panel, (10, 14, 22), 0.14)
    fitted = door.convert("RGBA").resize((396, 500), Image.Resampling.LANCZOS)
    fitted = ImageEnhance.Color(fitted).enhance(0.74)
    fitted = ImageEnhance.Contrast(fitted).enhance(0.94)

    door_mask = Image.new("L", (SIZE, SIZE), 0)
    mask_draw = ImageDraw.Draw(door_mask)
    mask_draw.rectangle((138, 178, 374, SIZE), fill=255)
    mask_draw.pieslice((138, 42, 374, 278), 180, 360, fill=255)
    mask_draw.rectangle((138, 160, 374, 278), fill=255)
    door_layer = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    door_layer.alpha_composite(fitted, ((SIZE - fitted.width) // 2, 12))
    door_layer.putalpha(ImageChops.multiply(door_layer.getchannel("A"), door_mask))
    panel.alpha_composite(door_layer)

    frame = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    frame_draw = ImageDraw.Draw(frame, "RGBA")
    frame_draw.arc((126, 30, 386, 290), 180, 360, fill=(34, 42, 56, 210), width=10)
    frame_draw.arc((132, 36, 380, 284), 180, 360, fill=(128, 142, 164, 115), width=3)
    frame_draw.line((126, 160, 126, SIZE), fill=(34, 42, 56, 210), width=10)
    frame_draw.line((386, 160, 386, SIZE), fill=(16, 20, 30, 220), width=11)
    frame_draw.line((138, 506, 374, 506), fill=(18, 22, 30, 210), width=10)
    panel = Image.alpha_composite(panel, frame)
    return panel.filter(ImageFilter.UnsharpMask(radius=1.0, percent=105))


def _tint_alpha_preserving(image: Image.Image, color: tuple[int, int, int], strength: float) -> Image.Image:
    result = image.convert("RGBA").copy()
    pixels = result.load()
    for y in range(result.height):
        for x in range(result.width):
            r, g, b, a = pixels[x, y]
            if a <= 0:
                continue
            pixels[x, y] = (
                clamp(round((r * (1.0 - strength)) + (color[0] * strength))),
                clamp(round((g * (1.0 - strength)) + (color[1] * strength))),
                clamp(round((b * (1.0 - strength)) + (color[2] * strength))),
                a,
            )
    return result


def _add_roots_overlay(image: Image.Image) -> Image.Image:
    return draw_roots(image.copy(), 902, painterly=True)


def _crop_center_tile(canvas: Image.Image) -> Image.Image:
    return canvas.crop((SIZE, SIZE, SIZE * 2, SIZE * 2)).convert("RGBA")


def _draw_root_network(
    draw: ImageDraw.ImageDraw,
    origin_x: int,
    origin_y: int,
    rng: random.Random,
    *,
    density: int,
    floor_plane: bool = True,
) -> None:
    def sample_polyline(points: list[tuple[int, int]], t: float) -> tuple[float, float]:
        if len(points) < 2:
            return points[0]
        t = max(0.0, min(0.999, t))
        segment = t * (len(points) - 1)
        index = int(segment)
        local = segment - index
        x0, y0 = points[index]
        x1, y1 = points[index + 1]
        return x0 + (x1 - x0) * local, y0 + (y1 - y0) * local

    for index in range(density):
        start_x = origin_x + rng.randint(-120, SIZE + 80)
        start_y = origin_y + rng.randint(120 if floor_plane else -30, SIZE + 60)
        direction = rng.choice((-1, 1))
        length = rng.randint(310, 620)
        drift = rng.uniform(-0.22, 0.22)
        amp = rng.randint(14, 36)
        freq = rng.uniform(1.7, 3.4)
        phase = rng.uniform(0, math.tau)
        points = []
        for step in range(26):
            t = step / 25.0
            x = start_x + direction * length * t
            y = start_y + (drift * length * t) + math.sin((t * math.tau * freq) + phase) * amp
            y += math.sin((t * math.tau * (freq * 0.43)) + phase * 0.7) * (amp * 0.45)
            points.append((round(x), round(y)))

        width = rng.randint(5, 12) if floor_plane else rng.randint(3, 8)
        shadow = tuple((x + 3, y + 5) for x, y in points)
        draw.line(shadow, fill=(0, 0, 0, 40), width=width + 7, joint="curve")
        draw.line(points, fill=(18, 15, 12, 122), width=width + 3, joint="curve")
        draw.line(points, fill=(43, 33, 24, 216), width=width + 1, joint="curve")
        draw.line(tuple((x - 1, y - 1) for x, y in points), fill=(104, 82, 54, 94), width=max(1, width // 3), joint="curve")
        draw.line(tuple((x + 1, y + 2) for x, y in points), fill=(16, 12, 9, 70), width=max(1, width // 3), joint="curve")

        for _ in range(rng.randint(10, 22)):
            t = rng.random()
            px, py = sample_polyline(points, t)
            knot_w = rng.randint(max(2, width // 2), width + 5)
            knot_h = rng.randint(2, max(3, width // 2 + 1))
            angle = rng.uniform(-0.8, 0.8)
            draw.ellipse(
                (
                    round(px - knot_w),
                    round(py - knot_h),
                    round(px + knot_w),
                    round(py + knot_h),
                ),
                fill=(30, 22, 16, rng.randint(46, 88)),
            )
            draw.arc(
                (
                    round(px - knot_w),
                    round(py - knot_h - 1),
                    round(px + knot_w),
                    round(py + knot_h + 1),
                ),
                195,
                340,
                fill=(112, 88, 56, rng.randint(38, 80)),
                width=1,
            )

        for _ in range(rng.randint(12, 26)):
            t0 = rng.random()
            t1 = min(0.999, t0 + rng.uniform(0.025, 0.08))
            x0, y0 = sample_polyline(points, t0)
            x1, y1 = sample_polyline(points, t1)
            draw.line(
                (x0, y0 - rng.randint(1, 3), x1, y1 - rng.randint(1, 3)),
                fill=(128, 102, 66, rng.randint(28, 58)),
                width=1,
            )
            if rng.random() < 0.7:
                draw.line((x0, y0 + 2, x1, y1 + 2), fill=(8, 7, 5, rng.randint(34, 72)), width=1)

        branch_count = rng.randint(2, 5)
        for _ in range(branch_count):
            anchor_index = rng.randint(5, len(points) - 6)
            anchor_x, anchor_y = points[anchor_index]
            angle = rng.uniform(-1.5, 1.5)
            branch_len = rng.randint(34, 108)
            branch_points = []
            for step in range(5):
                t = step / 4.0
                branch_points.append(
                    (
                        anchor_x + round(math.cos(angle) * branch_len * t) + round(math.sin(t * math.pi) * rng.randint(-10, 10)),
                        anchor_y + round(math.sin(angle) * branch_len * t) + round(math.sin(t * math.tau + phase) * rng.randint(3, 12)),
                    )
                )
            branch_width = max(2, width // 2)
            draw.line(tuple((x + 2, y + 3) for x, y in branch_points), fill=(0, 0, 0, 28), width=branch_width + 3, joint="curve")
            draw.line(branch_points, fill=(22, 16, 11, 104), width=branch_width + 1, joint="curve")
            draw.line(branch_points, fill=(64, 48, 30, 146), width=branch_width, joint="curve")

    for _ in range(density * 4):
        x = origin_x + rng.randint(-30, SIZE + 30)
        y = origin_y + rng.randint(-20, SIZE + 40)
        length = rng.randint(12, 42)
        angle = rng.uniform(-1.0, 1.0)
        draw.line(
            (x, y, x + round(math.cos(angle) * length), y + round(math.sin(angle) * length)),
            fill=(70, 92, 50, rng.randint(36, 74)),
            width=1,
        )


def _draw_fungus_growth(
    draw: ImageDraw.ImageDraw,
    origin_x: int,
    origin_y: int,
    rng: random.Random,
    *,
    cluster_count: int,
    ceiling: bool = False,
) -> None:
    def shaded_ellipse(
        box: tuple[int, int, int, int],
        base: tuple[int, int, int],
        alpha: int,
        *,
        highlight: tuple[int, int, int] = (202, 178, 212),
    ) -> None:
        x0, y0, x1, y1 = box
        steps = 8
        draw.ellipse((x0 + 3, y0 + 4, x1 + 3, y1 + 6), fill=(0, 0, 0, 44))
        for step in range(steps):
            t = step / max(1, steps - 1)
            inset_x = round((x1 - x0) * 0.08 * t)
            inset_y = round((y1 - y0) * 0.18 * t)
            color = tuple(clamp(round(base[i] * (1 - t * 0.24) + highlight[i] * (t * 0.24))) for i in range(3))
            draw.pieslice(
                (x0 + inset_x, y0 + inset_y, x1 - inset_x, y1 - inset_y),
                180,
                360,
                fill=color + (round(alpha * (1 - t * 0.05)),),
            )
        underside_y = y0 + round((y1 - y0) * 0.52)
        draw.ellipse((x0 + 2, underside_y - 2, x1 - 2, y1 + 1), fill=(34, 28, 34, round(alpha * 0.42)))
        for line_index in range(5):
            x = x0 + round((x1 - x0) * (line_index + 1) / 6)
            draw.line((x, underside_y, (x0 + x1) // 2, y1), fill=(196, 176, 184, 42), width=1)

    for _ in range(cluster_count):
        cx = origin_x + rng.randint(-30, SIZE + 30)
        cy = origin_y + rng.randint(40, SIZE + 24)
        patch_rx = rng.randint(26, 72)
        patch_ry = rng.randint(12, 34)

        for _ in range(rng.randint(8, 16)):
            ox = rng.randint(-patch_rx, patch_rx)
            oy = rng.randint(-patch_ry, patch_ry)
            lobe_rx = rng.randint(9, 24)
            lobe_ry = rng.randint(4, 12)
            draw.ellipse(
                (cx + ox - lobe_rx, cy + oy - lobe_ry, cx + ox + lobe_rx, cy + oy + lobe_ry),
                fill=(10, 17, 15, rng.randint(28, 64)),
            )

        for _ in range(rng.randint(7, 14)):
            stem_h = rng.randint(10, 34 if not ceiling else 22)
            stem_x = cx + rng.randint(-patch_rx, patch_rx)
            stem_y = cy + rng.randint(-patch_ry // 2, patch_ry)
            if ceiling:
                stem_top = stem_y
                stem_bottom = stem_y + stem_h
            else:
                stem_top = stem_y - stem_h
                stem_bottom = stem_y
            stem_mid = stem_x + rng.randint(-2, 2)
            draw.line((stem_x + 2, stem_top + 3, stem_mid + 2, stem_bottom + 2), fill=(0, 0, 0, 42), width=3)
            draw.line((stem_x, stem_top, stem_mid, stem_bottom), fill=(126, 114, 94, 154), width=2)
            draw.line((stem_x - 1, stem_top, stem_mid - 1, stem_bottom), fill=(194, 178, 142, 50), width=1)
            cap_w = rng.randint(10, 27)
            cap_h = rng.randint(6, 14)
            cap_y = stem_top if not ceiling else stem_bottom
            cap_color = rng.choice(((66, 47, 78), (82, 50, 70), (54, 70, 62), (68, 64, 92), (88, 70, 56)))
            cap_box = (stem_x - cap_w, cap_y - cap_h, stem_x + cap_w, cap_y + cap_h)
            draw.ellipse((cap_box[0] + 2, cap_box[1] + 3, cap_box[2] + 2, cap_box[3] + 4), fill=(0, 0, 0, 48))
            shaded_ellipse(
                cap_box,
                cap_color,
                rng.randint(180, 232),
                highlight=(170, 154, 178),
            )
            for _ in range(rng.randint(2, 5)):
                spot_x = stem_x + rng.randint(-cap_w + 2, cap_w - 2)
                spot_y = cap_y + rng.randint(-cap_h + 1, max(1, cap_h // 3))
                spot_r = rng.randint(1, 3)
                draw.ellipse(
                    (spot_x - spot_r, spot_y - spot_r, spot_x + spot_r, spot_y + spot_r),
                    fill=(42, 32, 48, rng.randint(44, 92)),
                )
            draw.arc(
                (stem_x - cap_w + 2, cap_y - cap_h, stem_x + cap_w - 2, cap_y + cap_h),
                190,
                342,
                fill=(224, 198, 232, 78),
                width=1,
            )
            for line_index in range(3):
                offset = (line_index - 1) * cap_w * 0.28
                draw.line(
                    (
                        stem_x,
                        cap_y + cap_h - 1,
                        stem_x + round(offset),
                        cap_y + round(cap_h * 0.25),
                    ),
                    fill=(232, 210, 216, 34),
                    width=1,
                )

        for _ in range(rng.randint(18, 36)):
            x = cx + rng.randint(-patch_rx - 20, patch_rx + 20)
            y = cy + rng.randint(-patch_ry - 16, patch_ry + 18)
            length = rng.randint(8, 34)
            angle = rng.uniform(-0.9, 0.9)
            draw.line(
                (x, y, x + round(math.cos(angle) * length), y + round(math.sin(angle) * length)),
                fill=(92, 128, 104, rng.randint(22, 58)),
                width=1,
            )
        if rng.random() < 0.72:
            glow_r = rng.randint(1, 3)
            glow_x = cx + rng.randint(-patch_rx, patch_rx)
            glow_y = cy + rng.randint(-patch_ry, patch_ry)
            draw.ellipse(
                (glow_x - glow_r, glow_y - glow_r, glow_x + glow_r, glow_y + glow_r),
                fill=(92, 188, 156, rng.randint(42, 92)),
            )


def _add_pit_overlay(image: Image.Image) -> Image.Image:
    result = image.convert("RGBA").copy()
    overlay = Image.new("RGBA", result.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    outer = (74, 64, 438, 428)
    lip = (94, 84, 418, 408)
    inner = (128, 118, 384, 374)
    abyss = (150, 140, 362, 352)

    draw.ellipse(outer, fill=(24, 28, 34, 96))
    draw.ellipse(lip, fill=(66, 68, 72, 126), outline=(18, 22, 28, 190), width=7)
    draw.ellipse(inner, fill=(28, 31, 36, 218), outline=(100, 102, 106, 92), width=4)

    center = ((inner[0] + inner[2]) / 2.0, (inner[1] + inner[3]) / 2.0)
    for index in range(20):
        angle = math.tau * index / 20.0
        outer_point = (
            center[0] + math.cos(angle) * 156,
            center[1] + math.sin(angle) * 156,
        )
        inner_point = (
            center[0] + math.cos(angle) * 129,
            center[1] + math.sin(angle) * 129,
        )
        draw.line(
            (outer_point[0], outer_point[1], inner_point[0], inner_point[1]),
            fill=(18, 22, 28, 58),
            width=2,
        )

    draw.ellipse((136, 126, 376, 366), fill=(12, 15, 20, 190))
    draw.ellipse(abyss, fill=(0, 0, 0, 248))
    draw.arc(lip, 205, 338, fill=(148, 150, 156, 78), width=4)
    draw.arc(inner, 20, 170, fill=(2, 4, 8, 150), width=7)
    draw.arc((138, 128, 374, 364), 190, 330, fill=(74, 78, 86, 60), width=3)

    radial = Image.new("RGBA", result.size, (0, 0, 0, 0))
    radial_draw = ImageDraw.Draw(radial, "RGBA")
    for offset, alpha in ((0, 62), (18, 38), (36, 20)):
        radial_draw.ellipse(
            (outer[0] - offset, outer[1] - offset, outer[2] + offset, outer[3] + offset),
            outline=(0, 0, 0, alpha),
            width=6,
        )
    combined = Image.alpha_composite(result, radial.filter(ImageFilter.GaussianBlur(4)))
    return Image.alpha_composite(combined, overlay.filter(ImageFilter.GaussianBlur(0.25))).filter(
        ImageFilter.UnsharpMask(radius=1.0, percent=105)
    )


def _masonry_wall_texture(seed: int = 1210) -> Image.Image:
    rng = random.Random(seed)
    image = base_noise(seed, (68, 76, 90), 18)
    draw = ImageDraw.Draw(image, "RGBA")
    mortar = (18, 24, 34, 255)
    rows = [0, 72, 146, 224, 304, 392, SIZE]
    for row_index, (top, bottom) in enumerate(zip(rows, rows[1:])):
        offset = 0 if row_index % 2 == 0 else 48
        x = -offset
        while x < SIZE:
            width = rng.randint(70, 122)
            left = x
            right = x + width
            stone_base = tuple(clamp(channel + rng.randint(-12, 16)) for channel in (72, 82, 98))
            draw.rounded_rectangle(
                (left + 3, top + 3, right - 3, bottom - 3),
                radius=rng.randint(5, 12),
                fill=stone_base + (255,),
                outline=mortar,
                width=3,
            )
            draw.line((left + 10, top + 8, right - 12, top + 6), fill=(98, 112, 136, 255), width=1)
            draw.line((left + 8, bottom - 8, right - 10, bottom - 9), fill=(42, 50, 62, 255), width=1)
            x = right
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay, "RGBA")
    for _ in range(95):
        x = rng.randint(0, SIZE)
        y = rng.randint(0, SIZE)
        length = rng.randint(12, 70)
        angle = rng.uniform(-0.75, 0.75)
        end = (x + round(math.cos(angle) * length), y + round(math.sin(angle) * length))
        overlay_draw.line((x, y, *end), fill=(16, 20, 28, rng.randint(34, 82)), width=rng.randint(1, 2))
    for _ in range(42):
        x = rng.randint(0, SIZE)
        y = rng.randint(0, SIZE)
        radius = rng.randint(12, 42)
        overlay_draw.ellipse(
            (x - radius, y - radius // 2, x + radius, y + radius // 2),
            fill=(20, 28, 36, rng.randint(12, 30)),
        )
    image = Image.alpha_composite(image, overlay)
    image.putalpha(Image.new("L", image.size, 255))
    image = ImageEnhance.Color(image).enhance(0.82)
    image = ImageEnhance.Contrast(image).enhance(1.08)
    return image.filter(ImageFilter.UnsharpMask(radius=1.0, percent=110))


def _continuous_slate_wall(seed: int = 1200) -> Image.Image:
    rng = random.Random(seed)
    image = base_noise(seed, (58, 68, 84), 22).filter(ImageFilter.GaussianBlur(0.8))
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    for _ in range(170):
        x = rng.randint(-40, SIZE + 40)
        y = rng.randint(-40, SIZE + 40)
        length = rng.randint(50, 210)
        angle = rng.choice((-1, 1)) * rng.uniform(0.08, 0.72)
        end = (x + int(math.cos(angle) * length), y + int(math.sin(angle) * length))
        draw.line((x, y, *end), fill=(14, 18, 26, rng.randint(24, 70)), width=rng.randint(1, 3))
        if rng.random() < 0.32:
            draw.line((x + 1, y + 1, end[0] + 1, end[1] + 1), fill=(158, 174, 196, rng.randint(12, 30)), width=1)
    for _ in range(95):
        x = rng.randint(0, SIZE)
        y = rng.randint(0, SIZE)
        rx = rng.randint(18, 90)
        ry = rng.randint(8, 40)
        draw.ellipse((x - rx, y - ry, x + rx, y + ry), fill=(22, 30, 42, rng.randint(8, 24)))
    image = Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(0.25)))
    edge = Image.new("RGBA", image.size, (0, 0, 0, 0))
    edge_draw = ImageDraw.Draw(edge, "RGBA")
    for offset in range(54):
        alpha = round(30 * ((54 - offset) / 54.0) ** 2)
        edge_draw.rectangle((offset, offset, SIZE - offset - 1, SIZE - offset - 1), outline=(58, 68, 84, alpha), width=1)
    image = Image.alpha_composite(image, edge)
    alpha = Image.new("L", image.size, 255)
    image.putalpha(alpha)
    image = ImageEnhance.Contrast(image).enhance(1.08)
    return image.filter(ImageFilter.UnsharpMask(radius=1.0, percent=95))


def _add_fungus_overlay(image: Image.Image, seed: int = 940) -> Image.Image:
    result = _tint_texture(image.convert("RGBA"), (28, 44, 42), 0.05)
    rng = random.Random(seed)
    growth = Image.new("RGBA", (SIZE * 3, SIZE * 3), (0, 0, 0, 0))
    draw = ImageDraw.Draw(growth, "RGBA")
    for origin_x in (0, SIZE, SIZE * 2):
        for origin_y in (0, SIZE, SIZE * 2):
            _draw_fungus_growth(
                draw,
                origin_x,
                origin_y,
                rng,
                cluster_count=11,
                ceiling=seed % 2 == 1,
            )
    growth = _crop_center_tile(growth)
    shadow = Image.new("RGBA", result.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow, "RGBA").ellipse((72, 72, 440, 440), fill=(8, 14, 12, 24))
    result = Image.alpha_composite(result, shadow.filter(ImageFilter.GaussianBlur(32)))
    return Image.alpha_composite(result, growth.filter(ImageFilter.GaussianBlur(0.25))).filter(
        ImageFilter.UnsharpMask(radius=1.0, percent=110)
    )


def _write_board_assets() -> bool:
    if not SOURCE_BOARD.exists():
        return False

    board = Image.open(SOURCE_BOARD).convert("RGBA")
    extracted_textures: dict[str, Image.Image] = {}
    extracted_specials: dict[str, Image.Image] = {}

    for (col, row), (kind, key) in BOARD_CELL_MAP.items():
        cell = _board_cell(board, col, row)
        if kind == "texture":
            inset = 18 if key in {"wall", "floor", "ceiling"} else 20
            extracted_textures[key] = _scale_texture(cell, inset=inset)
        else:
            extracted_specials[key] = _scale_special(cell)

    cool_strengths = {
        "wall": 0.46,
        "floor": 0.40,
        "ceiling": 0.46,
        "floor_crystal": 0.36,
        "floor_fire": 0.14,
        "floor_spring": 0.22,
        "door_closed": 0.16,
    }
    for key, strength in cool_strengths.items():
        extracted_textures[key] = _cool_stone_palette(extracted_textures[key], strength=strength)

    for key in ("wall", "floor", "ceiling", "floor_crystal"):
        extracted_textures[key] = _make_seamless_texture(extracted_textures[key])

    extracted_textures["door_closed"] = _fit_door_panel(
        extracted_textures["door_closed"],
        extracted_textures["wall"],
    )
    extracted_textures["door_open"] = _transparent_arch_door(extracted_textures["door_closed"])
    extracted_textures["wall_upper"] = _tint_texture(extracted_textures["wall"], (44, 58, 78), 0.10)
    extracted_textures["wall_middle"] = _tint_texture(extracted_textures["wall"], (28, 42, 62), 0.18)
    extracted_textures["wall_deep"] = _tint_texture(extracted_textures["wall"], (18, 30, 48), 0.24)
    extracted_textures["floor_debris"] = _tint_texture(extracted_textures["floor"], (54, 66, 80), 0.14)
    extracted_textures["floor_roots"] = _add_roots_overlay(_tint_texture(extracted_textures["floor"], (28, 54, 46), 0.16))
    extracted_textures["floor_fungus"] = _add_fungus_overlay(extracted_textures["floor"], seed=940)
    extracted_textures["floor_pit"] = _add_pit_overlay(_tint_texture(extracted_textures["floor"], (12, 18, 28), 0.24))
    extracted_textures["ceiling_fungus"] = _add_fungus_overlay(extracted_textures["ceiling"], seed=941)
    extracted_textures["ceiling_crystal"] = _tint_texture(extracted_textures["ceiling"], (26, 84, 128), 0.20)
    extracted_textures["ceiling_pit"] = _add_pit_overlay(_tint_texture(extracted_textures["ceiling"], (0, 6, 14), 0.24))
    extracted_textures["floor_funhouse"] = funhouse()
    extracted_textures["wall_funhouse"] = funhouse_wall()
    extracted_textures["wall_funhouse_boundary"] = funhouse_boundary_wall()
    extracted_textures["ceiling_funhouse"] = funhouse_ceiling()

    extracted_specials["sconce_unlit"] = _tint_alpha_preserving(
        extracted_specials["sconce_broken"],
        (86, 82, 76),
        0.35,
    )

    for key, image in extracted_textures.items():
        image.save(DUNGEON_ROOT / TEXTURES[key])
    for key, image in extracted_specials.items():
        image.save(DUNGEON_ROOT / SPECIAL_TEXTURES[key])
    return True


def base_noise(seed: int, base: tuple[int, int, int], spread: int = 18) -> Image.Image:
    rng = random.Random(seed)
    image = Image.new("RGBA", (SIZE, SIZE), base + (255,))
    pixels = image.load()
    for y in range(SIZE):
        for x in range(SIZE):
            shade = int(math.sin((x + seed) / 23.0) * 7 + math.cos((y - seed) / 31.0) * 8)
            noise = rng.randint(-spread, spread)
            pixels[x, y] = tuple(clamp(c + shade + noise) for c in base) + (255,)
    return image.filter(ImageFilter.SMOOTH_MORE)


def stone_wall(seed: int, base: tuple[int, int, int], grime: tuple[int, int, int]) -> Image.Image:
    rng = random.Random(seed)
    image = base_noise(seed, base, 20)
    draw = ImageDraw.Draw(image, "RGBA")
    rows = [0, 96, 188, 286, 386, SIZE]
    for row_index, (top, bottom) in enumerate(zip(rows, rows[1:])):
        offset = 0 if row_index % 2 == 0 else 92
        x = -offset
        while x < SIZE:
            width = rng.randint(118, 184)
            rect = (x, top, x + width, bottom)
            draw.rectangle(rect, outline=(30, 30, 36, 150), width=4)
            draw.line((x + 4, bottom - 5, x + width - 4, bottom - 5), fill=(210, 210, 220, 38), width=2)
            x += width
    for _ in range(80):
        x = rng.randint(0, SIZE)
        y = rng.randint(0, SIZE)
        length = rng.randint(18, 92)
        angle = rng.uniform(-0.9, 0.9)
        end = (x + int(math.cos(angle) * length), y + int(math.sin(angle) * length))
        draw.line((x, y, *end), fill=(*grime, rng.randint(42, 100)), width=rng.randint(1, 3))
    for _ in range(34):
        x = rng.randint(0, SIZE)
        y = rng.randint(0, SIZE)
        radius = rng.randint(6, 24)
        stain = tuple(clamp(channel + 28) for channel in grime)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=(*stain, rng.randint(8, 24)))
    return image.filter(ImageFilter.UnsharpMask(radius=1.4, percent=120))


def floor_texture(seed: int, base: tuple[int, int, int], accent: tuple[int, int, int] | None = None) -> Image.Image:
    rng = random.Random(seed)
    image = base_noise(seed, base, 24)
    draw = ImageDraw.Draw(image, "RGBA")
    for _ in range(180):
        x = rng.randint(-20, SIZE)
        y = rng.randint(-20, SIZE)
        w = rng.randint(14, 82)
        h = rng.randint(5, 24)
        color = jitter(base, 28, rng)
        draw.ellipse((x, y, x + w, y + h), fill=color[:3] + (rng.randint(35, 105),))
    if accent:
        for _ in range(52):
            x = rng.randint(0, SIZE)
            y = rng.randint(0, SIZE)
            length = rng.randint(30, 150)
            draw.line((x, y, x + rng.randint(-50, 50), y + length), fill=(*accent, rng.randint(55, 140)), width=rng.randint(2, 6))
    return image.filter(ImageFilter.SMOOTH_MORE)


def ceiling_texture(seed: int, base: tuple[int, int, int], accent: tuple[int, int, int] | None = None) -> Image.Image:
    image = stone_wall(seed, base, (28, 27, 30)).filter(ImageFilter.GaussianBlur(0.3))
    overlay = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    for y in range(SIZE):
        alpha = int(90 * (y / SIZE))
        draw.line((0, y, SIZE, y), fill=(0, 0, 0, alpha))
    if accent:
        rng = random.Random(seed + 91)
        for _ in range(36):
            x = rng.randint(0, SIZE)
            y = rng.randint(0, SIZE)
            draw.ellipse((x - 20, y - 8, x + 20, y + 8), fill=(*accent, rng.randint(32, 90)))
    return Image.alpha_composite(image, overlay)


def draw_roots(image: Image.Image, seed: int, painterly: bool = False) -> Image.Image:
    rng = random.Random(seed)
    image = _tint_texture(image.convert("RGBA"), (28, 36, 34), 0.04)
    shadow = Image.new("RGBA", (SIZE * 3, SIZE * 3), (0, 0, 0, 0))
    draw = ImageDraw.Draw(shadow, "RGBA")
    for origin_x in (0, SIZE, SIZE * 2):
        for origin_y in (0, SIZE, SIZE * 2):
            _draw_root_network(
                draw,
                origin_x,
                origin_y,
                rng,
                density=12 if painterly else 18,
                floor_plane=True,
            )
    shadow = _crop_center_tile(shadow)
    return Image.alpha_composite(image, shadow.filter(ImageFilter.GaussianBlur(0.25 if painterly else 0))).filter(
        ImageFilter.UnsharpMask(radius=1.0, percent=105)
    )


def draw_glow_spots(image: Image.Image, seed: int, color: tuple[int, int, int]) -> Image.Image:
    rng = random.Random(seed)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    for _ in range(42):
        x = rng.randint(0, SIZE)
        y = rng.randint(0, SIZE)
        r = rng.randint(8, 38)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*color, rng.randint(28, 90)))
    return Image.alpha_composite(image, overlay.filter(ImageFilter.GaussianBlur(5)))


def door(opened: bool) -> Image.Image:
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    arch = (80, 34, 432, 500)
    draw.rounded_rectangle(arch, radius=150, fill=(92, 94, 104, 255), outline=(28, 28, 34, 255), width=8)
    inner = (118, 78, 394, 500)
    draw.rounded_rectangle(inner, radius=120, fill=(34, 32, 30, 255))
    if opened:
        draw.pieslice((126, 70, 466, 530), 86, 268, fill=(92, 58, 36, 255), outline=(24, 18, 14, 255), width=5)
        for x in (206, 278, 350):
            draw.line((x, 112, x - 42, 492), fill=(45, 27, 17, 130), width=4)
        draw.rectangle((330, 112, 356, 450), fill=(40, 28, 22, 150))
    else:
        draw.rounded_rectangle((130, 82, 382, 500), radius=84, fill=(112, 72, 42, 255), outline=(42, 28, 20, 255), width=6)
        for x in (172, 230, 288, 344):
            draw.line((x, 96, x, 492), fill=(56, 34, 20, 145), width=4)
        for y in (190, 330):
            draw.rectangle((132, y, 380, y + 22), fill=(62, 56, 58, 230))
            for x in range(150, 370, 42):
                draw.ellipse((x, y + 5, x + 12, y + 17), fill=(178, 150, 96, 255))
        draw.ellipse((342, 278, 362, 298), fill=(196, 156, 84, 255))
    return image.filter(ImageFilter.UnsharpMask(radius=1.2, percent=130))


def alpha_canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image, "RGBA")


def prop_rubble() -> Image.Image:
    rng = random.Random(410)
    image, draw = alpha_canvas()
    for _ in range(28):
        x = rng.randint(92, 420)
        y = rng.randint(260, 430)
        r = rng.randint(18, 58)
        color = jitter((110, 104, 94), 28, rng)
        draw.polygon(
            [(x - r, y + r // 2), (x - r // 3, y - r), (x + r, y - r // 3), (x + r // 2, y + r)],
            fill=color,
            outline=(42, 38, 34, 180),
        )
    return image.filter(ImageFilter.UnsharpMask(radius=1.1, percent=120))


def prop_roots() -> Image.Image:
    image, draw = alpha_canvas()
    rng = random.Random(411)
    _draw_root_network(draw, 0, 0, rng, density=11, floor_plane=True)
    for _ in range(56):
        x = rng.randint(78, 430)
        y = rng.randint(260, 450)
        length = rng.randint(8, 34)
        angle = rng.uniform(-0.9, 0.9)
        draw.line(
            (x, y, x + round(math.cos(angle) * length), y + round(math.sin(angle) * length)),
            fill=(82, 92, 58, rng.randint(18, 48)),
            width=1,
        )
    return image.filter(ImageFilter.UnsharpMask(radius=1.0, percent=115))


def prop_fungus() -> Image.Image:
    image, draw = alpha_canvas()
    rng = random.Random(412)

    def shaded_cap(cx: int, cy: int, cap_w: int, cap_h: int, color: tuple[int, int, int], alpha: int) -> None:
        draw.ellipse((cx - cap_w + 3, cy + 1, cx + cap_w + 3, cy + cap_h + 7), fill=(0, 0, 0, 54))
        for step in range(8):
            t = step / 7.0
            inset_x = round(cap_w * 0.16 * t)
            inset_y = round(cap_h * 0.32 * t)
            shade = tuple(clamp(round(color[i] * (1.0 - t * 0.24) + (176, 156, 188)[i] * (t * 0.24))) for i in range(3))
            draw.pieslice(
                (cx - cap_w + inset_x, cy - cap_h + inset_y, cx + cap_w - inset_x, cy + cap_h - inset_y),
                180,
                360,
                fill=shade + (alpha,),
            )
        underside_y = cy + round(cap_h * 0.45)
        draw.ellipse((cx - cap_w + 2, underside_y - 2, cx + cap_w - 2, cy + cap_h + 1), fill=(34, 28, 34, round(alpha * 0.44)))
        for line_index in range(5):
            x = cx - cap_w + round((cap_w * 2) * (line_index + 1) / 6)
            draw.line((x, underside_y, cx, cy + cap_h), fill=(216, 190, 198, 44), width=1)
        for _ in range(rng.randint(2, 5)):
            spot_x = cx + rng.randint(-cap_w + 3, cap_w - 3)
            spot_y = cy + rng.randint(-cap_h + 1, max(1, cap_h // 4))
            spot_r = rng.randint(1, 3)
            draw.ellipse(
                (spot_x - spot_r, spot_y - spot_r, spot_x + spot_r, spot_y + spot_r),
                fill=(36, 28, 42, rng.randint(48, 96)),
            )
        draw.arc((cx - cap_w + 2, cy - cap_h, cx + cap_w - 2, cy + cap_h), 188, 342, fill=(220, 196, 226, 70), width=1)

    for _ in range(9):
        cx = rng.randint(120, 392)
        cy = rng.randint(292, 430)
        rx = rng.randint(32, 76)
        ry = rng.randint(14, 34)
        for _ in range(rng.randint(9, 18)):
            ox = rng.randint(-rx, rx)
            oy = rng.randint(-ry, ry)
            lobe_rx = rng.randint(10, 25)
            lobe_ry = rng.randint(4, 13)
            draw.ellipse(
                (cx + ox - lobe_rx, cy + oy - lobe_ry, cx + ox + lobe_rx, cy + oy + lobe_ry),
                fill=(8, 14, 13, rng.randint(34, 74)),
            )
        for _ in range(rng.randint(9, 15)):
            x = cx + rng.randint(-rx, rx)
            y = cy + rng.randint(-ry, ry)
            h = rng.randint(12, 38)
            bend = rng.randint(-3, 3)
            draw.line((x + 2, y + 3, x + bend + 2, y - h + 3), fill=(0, 0, 0, 46), width=3)
            draw.line((x, y, x + bend, y - h), fill=(132, 118, 94, 178), width=2)
            draw.line((x - 1, y, x + bend - 1, y - h), fill=(206, 184, 144, 52), width=1)
            cap_w = rng.randint(11, 28)
            cap_h = rng.randint(7, 14)
            cap_y = y - h
            cap_color = rng.choice(((66, 48, 82), (86, 52, 74), (56, 78, 66), (74, 70, 98), (92, 72, 58)))
            shaded_cap(x + bend, cap_y, cap_w, cap_h, cap_color, 226)
        for _ in range(36):
            x = cx + rng.randint(-rx - 28, rx + 28)
            y = cy + rng.randint(-ry - 14, ry + 20)
            length = rng.randint(9, 36)
            angle = rng.uniform(-0.9, 0.9)
            draw.line(
                (x, y, x + round(math.cos(angle) * length), y + round(math.sin(angle) * length)),
                fill=(88, 132, 104, rng.randint(20, 58)),
                width=1,
            )
        if rng.random() < 0.8:
            glow_x = cx + rng.randint(-rx, rx)
            glow_y = cy + rng.randint(-ry, ry)
            draw.ellipse((glow_x - 3, glow_y - 3, glow_x + 3, glow_y + 3), fill=(90, 196, 166, 78))
    return image.filter(ImageFilter.UnsharpMask(radius=1.0, percent=120))


def prop_crystals() -> Image.Image:
    image, draw = alpha_canvas()
    rng = random.Random(413)
    for _ in range(18):
        x = rng.randint(130, 390)
        y = rng.randint(210, 430)
        h = rng.randint(74, 180)
        w = rng.randint(18, 48)
        color = jitter((92, 186, 220), 22, rng)
        draw.polygon(
            [(x, y - h), (x - w, y - h // 3), (x - w // 2, y), (x + w // 2, y), (x + w, y - h // 3)],
            fill=color[:3] + (210,),
            outline=(210, 244, 255, 180),
        )
        draw.line((x, y - h + 8, x, y - 6), fill=(238, 255, 255, 150), width=2)
    return draw_glow_spots(image, 513, (50, 170, 230))


def prop_bones() -> Image.Image:
    image, draw = alpha_canvas()
    rng = random.Random(414)
    for _ in range(16):
        x = rng.randint(110, 405)
        y = rng.randint(285, 430)
        length = rng.randint(65, 170)
        angle = rng.uniform(-0.7, 0.7)
        x2 = x + int(math.cos(angle) * length)
        y2 = y + int(math.sin(angle) * length)
        draw.line((x, y, x2, y2), fill=(196, 184, 150, 230), width=rng.randint(8, 14))
        for px, py in ((x, y), (x2, y2)):
            draw.ellipse((px - 14, py - 10, px + 14, py + 10), fill=(212, 200, 168, 230))
    return image.filter(ImageFilter.UnsharpMask(radius=1.0, percent=120))


def prop_gear() -> Image.Image:
    image, draw = alpha_canvas()
    rng = random.Random(415)
    for _ in range(8):
        x = rng.randint(120, 390)
        y = rng.randint(270, 420)
        w = rng.randint(44, 106)
        h = rng.randint(16, 40)
        draw.polygon(
            [(x - w, y), (x, y - h), (x + w, y + h // 2), (x + 10, y + h)],
            fill=(116, 92, 70, 225),
            outline=(44, 38, 32, 180),
        )
        draw.line((x - w + 8, y + 2, x + w - 8, y + h // 2), fill=(180, 160, 116, 130), width=3)
    for _ in range(6):
        x = rng.randint(120, 390)
        y = rng.randint(280, 410)
        r = rng.randint(18, 44)
        draw.ellipse((x - r, y - r, x + r, y + r), outline=(92, 88, 86, 220), width=8)
    return image


def torch(lit: bool, broken: bool = False) -> Image.Image:
    image, draw = alpha_canvas()
    if broken:
        draw.line((230, 122, 274, 328), fill=(74, 60, 52, 230), width=16)
        draw.line((260, 210, 330, 252), fill=(68, 58, 52, 180), width=10)
        return image
    draw.rectangle((242, 148, 270, 348), fill=(88, 62, 42, 245))
    draw.rectangle((220, 170, 292, 198), fill=(74, 68, 66, 235))
    if lit:
        glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow, "RGBA")
        gdraw.ellipse((164, 18, 348, 240), fill=(255, 136, 46, 70))
        image = Image.alpha_composite(image, glow.filter(ImageFilter.GaussianBlur(18)))
        draw = ImageDraw.Draw(image, "RGBA")
        draw.polygon((256, 48, 214, 160, 256, 214, 306, 158), fill=(245, 86, 30, 230))
        draw.polygon((256, 72, 232, 156, 256, 196, 286, 154), fill=(255, 214, 88, 235))
    return image


def pit(kind: str) -> Image.Image:
    image = floor_texture(730 if kind == "floor" else 731, (82, 72, 64))
    draw = ImageDraw.Draw(image, "RGBA")
    draw.ellipse((126, 116, 386, 398), fill=(8, 8, 10, 245), outline=(100, 88, 74, 220), width=12)
    draw.ellipse((180, 180, 332, 340), fill=(0, 0, 0, 255))
    return image


def _repeated_seamless_canvas(seed: int, base: tuple[int, int, int], spread: int = 12) -> Image.Image:
    tile = _make_seamless_texture(base_noise(seed, base, spread), edge=96, blur=52)
    canvas = Image.new("RGBA", (SIZE * 3, SIZE * 3), (0, 0, 0, 255))
    for row in range(3):
        for col in range(3):
            canvas.paste(tile, (col * SIZE, row * SIZE))
    return canvas


def funhouse() -> Image.Image:
    rng = random.Random(736)
    image = _repeated_seamless_canvas(735, (28, 26, 38), 10)
    draw = ImageDraw.Draw(image, "RGBA")

    x_lines = [-74, 34, 124, 218, 318, 424, 566]
    y_lines = [-66, 38, 128, 224, 328, 430, 572]

    def grid_point(origin_x: int, origin_y: int, col: int, row: int) -> tuple[int, int]:
        x_base = x_lines[col]
        y_base = y_lines[row]
        x = origin_x + x_base + round(math.sin((y_base / 67.0) + (col * 0.88)) * 18)
        y = origin_y + y_base + round(math.sin((x_base / 73.0) + (row * 0.72)) * 16)
        x += round(math.sin((row + col) * 1.6) * 6)
        y += round(math.cos((row - col) * 1.25) * 5)
        return x, y

    palette = (
        (78, 24, 70),
        (102, 28, 84),
        (34, 76, 82),
        (60, 84, 42),
        (62, 42, 98),
        (112, 38, 58),
    )

    for origin_x in (0, SIZE, SIZE * 2):
        for origin_y in (0, SIZE, SIZE * 2):
            for row in range(len(y_lines) - 1):
                for col in range(len(x_lines) - 1):
                    points = (
                        grid_point(origin_x, origin_y, col, row),
                        grid_point(origin_x, origin_y, col + 1, row),
                        grid_point(origin_x, origin_y, col + 1, row + 1),
                        grid_point(origin_x, origin_y, col, row + 1),
                    )
                    base = palette[(row * 3 + col * 2) % len(palette)]
                    shade = rng.randint(-12, 8)
                    color = tuple(clamp(channel + shade) for channel in base)
                    draw.polygon(points, fill=color + (148,))

                    if (row + col) % 3 == 0:
                        cx = sum(point[0] for point in points) / 4.0
                        cy = sum(point[1] for point in points) / 4.0
                        radius = rng.randint(18, 38)
                        draw.arc(
                            (
                                round(cx - radius),
                                round(cy - radius * 0.62),
                                round(cx + radius),
                                round(cy + radius * 0.62),
                            ),
                            rng.randint(20, 90),
                            rng.randint(205, 330),
                            fill=(166, 138, 194, 26),
                            width=2,
                        )

            for col in range(len(x_lines)):
                points = [grid_point(origin_x, origin_y, col, row) for row in range(len(y_lines))]
                draw.line(points, fill=(6, 6, 10, 230), width=7, joint="curve")
                draw.line(points, fill=(118, 88, 136, 42), width=1, joint="curve")

            for row in range(len(y_lines)):
                points = [grid_point(origin_x, origin_y, col, row) for col in range(len(x_lines))]
                draw.line(points, fill=(6, 6, 10, 232), width=7, joint="curve")
                draw.line([(x, y - 2) for x, y in points], fill=(136, 92, 132, 42), width=1, joint="curve")

    grime = Image.new("RGBA", image.size, (0, 0, 0, 0))
    grime_draw = ImageDraw.Draw(grime, "RGBA")
    for _ in range(180):
        x = rng.randint(0, SIZE - 1)
        y = rng.randint(0, SIZE - 1)
        length = rng.randint(22, 92)
        angle = rng.uniform(-0.8, 0.8)
        for ox in (0, SIZE, SIZE * 2):
            for oy in (0, SIZE, SIZE * 2):
                grime_draw.line(
                    (
                        x + ox,
                        y + oy,
                        x + ox + round(math.cos(angle) * length),
                        y + oy + round(math.sin(angle) * length),
                    ),
                    fill=(4, 4, 8, rng.randint(22, 58)),
                    width=rng.randint(1, 2),
                )

    image = Image.alpha_composite(image, grime.filter(ImageFilter.GaussianBlur(0.7)))
    image = _crop_center_tile(image)
    image = ImageEnhance.Color(image).enhance(0.78)
    image = ImageEnhance.Contrast(image).enhance(1.12)
    return image.filter(ImageFilter.UnsharpMask(radius=1.0, percent=110))


def funhouse_wall() -> Image.Image:
    rng = random.Random(746)
    image = _repeated_seamless_canvas(745, (34, 34, 48), 13)
    draw = ImageDraw.Draw(image, "RGBA")
    palette = ((50, 78, 52), (88, 30, 82), (36, 76, 92), (92, 38, 62))

    for origin_x in (0, SIZE, SIZE * 2):
        for origin_y in (0, SIZE, SIZE * 2):
            for band in range(-2, 8):
                x0 = origin_x + band * 92 - 42
                points = []
                for step in range(9):
                    y = origin_y + step * 76 - 52
                    x = x0 + round(math.sin(step * 0.9 + band * 0.65) * 24)
                    points.append((x, y))
                points_right = [(x + 56 + round(math.sin(y / 83.0) * 10), y) for x, y in reversed(points)]
                color = palette[band % len(palette)]
                draw.polygon(points + points_right, fill=color + (104,))
                draw.line(points, fill=(6, 6, 10, 170), width=5, joint="curve")
                draw.line(points_right, fill=(6, 6, 10, 150), width=4, joint="curve")

            for _ in range(10):
                cx = origin_x + rng.randint(-40, SIZE + 40)
                cy = origin_y + rng.randint(-36, SIZE + 36)
                rx = rng.randint(20, 54)
                ry = rng.randint(8, 20)
                draw.arc((cx - rx, cy - ry, cx + rx, cy + ry), 20, 330, fill=(156, 142, 190, 34), width=2)
                draw.line((cx - rx, cy, cx + rx, cy + rng.randint(-8, 8)), fill=(8, 8, 12, 62), width=2)

            for _ in range(24):
                x = origin_x + rng.randint(-32, SIZE + 32)
                y = origin_y + rng.randint(-28, SIZE + 28)
                length = rng.randint(24, 86)
                angle = rng.uniform(-0.7, 0.7)
                draw.line(
                    (x, y, x + round(math.cos(angle) * length), y + round(math.sin(angle) * length)),
                    fill=(4, 4, 8, rng.randint(34, 92)),
                    width=rng.randint(1, 3),
                )

    image = _crop_center_tile(image)
    image = ImageEnhance.Color(image).enhance(0.72)
    image = ImageEnhance.Contrast(image).enhance(1.16)
    return image.filter(ImageFilter.UnsharpMask(radius=1.0, percent=100))


def funhouse_boundary_wall() -> Image.Image:
    rng = random.Random(750)
    image = _repeated_seamless_canvas(749, (36, 38, 54), 12)
    draw = ImageDraw.Draw(image, "RGBA")
    palette = ((58, 74, 68), (72, 42, 76), (42, 68, 82), (80, 46, 58))

    for origin_x in (0, SIZE, SIZE * 2):
        for origin_y in (0, SIZE, SIZE * 2):
            rows = [-54, 58, 172, 294, 412, 566]
            for row, (top, bottom) in enumerate(zip(rows, rows[1:])):
                offset = -68 if row % 2 else 0
                col = -1
                x = offset
                while x < SIZE + 120:
                    width = rng.randint(124, 184)
                    wobble = rng.randint(-12, 12)
                    points = (
                        (origin_x + x + wobble, origin_y + top + rng.randint(-6, 6)),
                        (origin_x + x + width + rng.randint(-10, 10), origin_y + top + rng.randint(-8, 8)),
                        (origin_x + x + width + rng.randint(-10, 10), origin_y + bottom + rng.randint(-8, 8)),
                        (origin_x + x + wobble, origin_y + bottom + rng.randint(-6, 6)),
                    )
                    base = palette[(row + col) % len(palette)]
                    shade = rng.randint(-12, 8)
                    color = tuple(clamp(channel + shade) for channel in base)
                    draw.polygon(points, fill=color + (178,))
                    draw.line(points + (points[0],), fill=(5, 5, 10, 210), width=5, joint="curve")
                    draw.line(
                        (points[0][0] + 8, points[2][1] - 8, points[2][0] - 8, points[2][1] - 6),
                        fill=(150, 130, 168, 34),
                        width=2,
                    )
                    if (row + col) % 2 == 0:
                        cx = sum(point[0] for point in points) / 4
                        cy = sum(point[1] for point in points) / 4
                        radius = rng.randint(16, 34)
                        draw.arc(
                            (
                                round(cx - radius),
                                round(cy - radius * 0.55),
                                round(cx + radius),
                                round(cy + radius * 0.55),
                            ),
                            rng.randint(20, 80),
                            rng.randint(210, 340),
                            fill=(18, 14, 24, 70),
                            width=2,
                        )
                    x += width
                    col += 1

            for _ in range(42):
                x = origin_x + rng.randint(-32, SIZE + 32)
                y = origin_y + rng.randint(-28, SIZE + 28)
                length = rng.randint(26, 96)
                angle = rng.uniform(-0.65, 0.65)
                draw.line(
                    (x, y, x + round(math.cos(angle) * length), y + round(math.sin(angle) * length)),
                    fill=(3, 3, 7, rng.randint(42, 104)),
                    width=rng.randint(1, 3),
                )

    image = _crop_center_tile(image)
    image = _make_seamless_texture(image, edge=96, blur=46)
    image = ImageEnhance.Color(image).enhance(0.70)
    image = ImageEnhance.Contrast(image).enhance(1.20)
    return image.filter(ImageFilter.UnsharpMask(radius=1.0, percent=105))


def funhouse_ceiling() -> Image.Image:
    rng = random.Random(756)
    image = _repeated_seamless_canvas(755, (22, 22, 34), 10)
    draw = ImageDraw.Draw(image, "RGBA")

    for origin_x in (0, SIZE, SIZE * 2):
        for origin_y in (0, SIZE, SIZE * 2):
            for stripe in range(-2, 9):
                points = []
                for step in range(10):
                    x = origin_x + step * 66 - 56
                    y = origin_y + stripe * 72 + round(math.sin(step * 0.9 + stripe * 0.8) * 24)
                    points.append((x, y))
                points_lower = [(x, y + 34 + round(math.cos(x / 88.0) * 10)) for x, y in reversed(points)]
                color = (94, 28, 76) if stripe % 2 == 0 else (8, 8, 14)
                draw.polygon(points + points_lower, fill=color + (132,))
                draw.line(points, fill=(5, 5, 8, 150), width=5, joint="curve")

            for _ in range(8):
                cx = origin_x + rng.randint(-40, SIZE + 40)
                cy = origin_y + rng.randint(-40, SIZE + 40)
                rx = rng.randint(28, 62)
                ry = rng.randint(10, 22)
                draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=(128, 122, 162, 34), width=2)
                draw.ellipse((cx - 5, cy - 3, cx + 5, cy + 3), fill=(5, 5, 8, 58))

    image = _crop_center_tile(image)
    image = ImageEnhance.Color(image).enhance(0.70)
    image = ImageEnhance.Contrast(image).enhance(1.14)
    return image.filter(ImageFilter.UnsharpMask(radius=1.0, percent=105))


def firepath() -> Image.Image:
    image = floor_texture(720, (92, 54, 34))
    return draw_glow_spots(image, 721, (255, 96, 22))


def spring() -> Image.Image:
    image = floor_texture(722, (48, 86, 96), (72, 184, 206))
    return draw_glow_spots(image, 723, (98, 224, 238))


def _crop_atlas_cell(atlas: Image.Image, index: int, columns: int = 3, rows: int = 2) -> Image.Image:
    cell_width = atlas.width // columns
    cell_height = atlas.height // rows
    x = (index % columns) * cell_width
    y = (index // columns) * cell_height
    return atlas.crop((x, y, x + cell_width, y + cell_height)).convert("RGBA")


def _normalize_tile_edges(image: Image.Image, band: int = 24, match_band: int = 5) -> Image.Image:
    result = image.convert("RGBA").copy()
    pixels = result.load()
    width, height = result.size

    def mix(a, b, t):
        return tuple(round(a[channel] * (1 - t) + b[channel] * t) for channel in range(4))

    for y in range(height):
        for offset in range(band):
            t = ((band - offset) / band) ** 1.7 * 0.48
            pixels[offset, y] = mix(pixels[offset, y], pixels[min(width - 1, band + offset), y], t)
            pixels[width - 1 - offset, y] = mix(
                pixels[width - 1 - offset, y],
                pixels[max(0, width - 1 - band - offset), y],
                t,
            )

    for x in range(width):
        for offset in range(band):
            t = ((band - offset) / band) ** 1.7 * 0.42
            pixels[x, offset] = mix(pixels[x, offset], pixels[x, min(height - 1, band + offset)], t)
            pixels[x, height - 1 - offset] = mix(
                pixels[x, height - 1 - offset],
                pixels[x, max(0, height - 1 - band - offset)],
                t,
            )

    for y in range(height):
        for offset in range(match_band):
            t = ((match_band - offset) / match_band) ** 2.0 * 0.78
            left = offset
            right = width - 1 - offset
            average = tuple((pixels[left, y][channel] + pixels[right, y][channel]) // 2 for channel in range(4))
            pixels[left, y] = mix(pixels[left, y], average, t)
            pixels[right, y] = mix(pixels[right, y], average, t)

    for x in range(width):
        for offset in range(match_band):
            t = ((match_band - offset) / match_band) ** 2.0 * 0.78
            top = offset
            bottom = height - 1 - offset
            average = tuple((pixels[x, top][channel] + pixels[x, bottom][channel]) // 2 for channel in range(4))
            pixels[x, top] = mix(pixels[x, top], average, t)
            pixels[x, bottom] = mix(pixels[x, bottom], average, t)

    return result


def _cool_match_organic_tile(image: Image.Image) -> Image.Image:
    result = ImageEnhance.Color(image).enhance(0.86)
    result = ImageEnhance.Contrast(result).enhance(0.98)
    return _tint_texture(result, (22, 34, 48), 18 / 255)


def _organic_overlay_to_alpha(image: Image.Image) -> Image.Image:
    result = image.convert("RGBA").resize((256, 256), Image.Resampling.LANCZOS)
    pixels = result.load()
    width, height = result.size
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            distance = math.sqrt((r - 0) ** 2 + (g - 255) ** 2 + (b - 0) ** 2)
            green_bias = g - max(r, b)
            if distance < 36 or (g > 150 and green_bias > 54 and r < 116 and b < 116):
                alpha = 0
            elif distance < 150 and green_bias > 26:
                alpha = round(255 * ((distance - 36) / 114))
            else:
                alpha = 255

            if alpha > 0 and green_bias > 18:
                luminance = round(r * 0.30 + g * 0.55 + b * 0.15)
                strength = min(0.88, max(0.20, green_bias / 150))
                target = (
                    max(28, min(118, round(luminance * 0.50 + 24))),
                    max(42, min(124, round(luminance * 0.58 + 28))),
                    max(30, min(100, round(luminance * 0.45 + 24))),
                )
                r = round(r * (1 - strength) + target[0] * strength)
                g = round(g * (1 - strength) + target[1] * strength)
                b = round(b * (1 - strength) + target[2] * strength)

            pixels[x, y] = (r, g, b, round(a * alpha / 255))

    result.putalpha(result.getchannel("A").filter(ImageFilter.GaussianBlur(0.28)))
    return result.filter(ImageFilter.UnsharpMask(radius=0.55, percent=74))


def write_organic_atlas_assets() -> None:
    if ORGANIC_FLOOR_ATLAS.exists():
        floor_atlas = Image.open(ORGANIC_FLOOR_ATLAS).convert("RGBA")
        floor_targets = (
            ("floor_roots_sparse", "floor_roots"),
            ("floor_roots_dense", None),
            ("floor_fungus_sparse", "floor_fungus"),
            ("floor_fungus_dense", None),
            ("ceiling_fungus_upper", "ceiling_fungus"),
            ("floor_root_fungus_mixed", None),
        )
        for index, (texture_key, alias_key) in enumerate(floor_targets):
            tile = _crop_atlas_cell(floor_atlas, index).resize((256, 256), Image.Resampling.LANCZOS)
            tile = _cool_match_organic_tile(_normalize_tile_edges(tile)).filter(
                ImageFilter.UnsharpMask(radius=0.65, percent=70)
            )
            tile.save(DUNGEON_ROOT / TEXTURES[texture_key])
            if alias_key:
                tile.save(DUNGEON_ROOT / TEXTURES[alias_key])

    if ORGANIC_OVERLAY_ATLAS.exists():
        overlay_atlas = Image.open(ORGANIC_OVERLAY_ATLAS).convert("RGBA")
        overlay_targets = (
            ("root_growth_sparse", None),
            ("root_growth_dense", "root_growth"),
            ("fungus_patch_sparse", None),
            ("fungus_patch_dense", "fungus_patch"),
            ("ceiling_fungus_overlay", None),
            ("root_fungus_patch", None),
        )
        for index, (special_key, alias_key) in enumerate(overlay_targets):
            sprite = _organic_overlay_to_alpha(_crop_atlas_cell(overlay_atlas, index))
            sprite.save(DUNGEON_ROOT / SPECIAL_TEXTURES[special_key])
            if alias_key:
                sprite.save(DUNGEON_ROOT / SPECIAL_TEXTURES[alias_key])


def _save_generated_organic_texture(key: str, image: Image.Image) -> None:
    path = DUNGEON_ROOT / TEXTURES[key]
    if ORGANIC_FLOOR_ATLAS.exists() or not path.exists():
        image.save(path)


def _save_generated_organic_special(key: str, image: Image.Image) -> None:
    path = DUNGEON_ROOT / SPECIAL_TEXTURES[key]
    if ORGANIC_OVERLAY_ATLAS.exists() or not path.exists():
        image.save(path)


def write_textures() -> None:
    _masonry_wall_texture(100).save(DUNGEON_ROOT / TEXTURES["wall"])
    _tint_texture(_masonry_wall_texture(101), (44, 58, 78), 0.10).save(DUNGEON_ROOT / TEXTURES["wall_upper"])
    _tint_texture(_masonry_wall_texture(102), (28, 42, 62), 0.18).save(DUNGEON_ROOT / TEXTURES["wall_middle"])
    _tint_texture(_masonry_wall_texture(103), (18, 30, 48), 0.24).save(DUNGEON_ROOT / TEXTURES["wall_deep"])
    funhouse_wall().save(DUNGEON_ROOT / TEXTURES["wall_funhouse"])
    funhouse_boundary_wall().save(DUNGEON_ROOT / TEXTURES["wall_funhouse_boundary"])
    door(False).save(DUNGEON_ROOT / TEXTURES["door_closed"])
    door(True).save(DUNGEON_ROOT / TEXTURES["door_open"])

    floor_texture(200, (112, 96, 76)).save(DUNGEON_ROOT / TEXTURES["floor"])
    floor_texture(201, (96, 90, 82)).save(DUNGEON_ROOT / TEXTURES["floor_debris"])
    _save_generated_organic_texture("floor_roots", draw_roots(floor_texture(202, (88, 86, 68)), 202, painterly=True))
    _save_generated_organic_texture("floor_fungus", _add_fungus_overlay(floor_texture(203, (70, 86, 64)), 203))
    draw_glow_spots(floor_texture(204, (58, 78, 88)), 204, (70, 180, 226)).save(DUNGEON_ROOT / TEXTURES["floor_crystal"])
    firepath().save(DUNGEON_ROOT / TEXTURES["floor_fire"])
    spring().save(DUNGEON_ROOT / TEXTURES["floor_spring"])
    funhouse().save(DUNGEON_ROOT / TEXTURES["floor_funhouse"])
    pit("floor").save(DUNGEON_ROOT / TEXTURES["floor_pit"])

    ceiling_texture(300, (76, 76, 84)).save(DUNGEON_ROOT / TEXTURES["ceiling"])
    _save_generated_organic_texture("ceiling_fungus", _add_fungus_overlay(ceiling_texture(301, (64, 72, 66)), 301))
    ceiling_texture(302, (56, 66, 76), (72, 176, 226)).save(DUNGEON_ROOT / TEXTURES["ceiling_crystal"])
    funhouse_ceiling().save(DUNGEON_ROOT / TEXTURES["ceiling_funhouse"])
    pit("ceiling").save(DUNGEON_ROOT / TEXTURES["ceiling_pit"])


def write_specials() -> None:
    prop_rubble().save(DUNGEON_ROOT / SPECIAL_TEXTURES["rubble"])
    _save_generated_organic_special("root_growth", prop_roots())
    _save_generated_organic_special("fungus_patch", prop_fungus())
    prop_crystals().save(DUNGEON_ROOT / SPECIAL_TEXTURES["crystal_cluster"])
    prop_bones().save(DUNGEON_ROOT / SPECIAL_TEXTURES["bone_pile"])
    prop_gear().save(DUNGEON_ROOT / SPECIAL_TEXTURES["broken_gear"])
    torch(True).save(DUNGEON_ROOT / SPECIAL_TEXTURES["torch_lit"])
    torch(False).save(DUNGEON_ROOT / SPECIAL_TEXTURES["sconce_unlit"])
    torch(False, broken=True).save(DUNGEON_ROOT / SPECIAL_TEXTURES["sconce_broken"])


def write_manifest() -> None:
    manifest = {
        "textures": TEXTURES,
        "special_textures": SPECIAL_TEXTURES,
    }
    (DUNGEON_ROOT / "dungeon_texture_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_map_icons() -> None:
    for name, color in MAP_ICONS.items():
        image = Image.new("RGBA", (32, 32), (34, 34, 38, 255))
        draw = ImageDraw.Draw(image, "RGBA")
        draw.rectangle((1, 1, 30, 30), fill=color + (255,), outline=(12, 12, 14, 255))
        if "crystal" in name:
            draw.polygon((16, 4, 8, 20, 14, 29, 24, 20), fill=(106, 214, 244, 255), outline=(220, 250, 255, 210))
        elif "fungus" in name:
            draw.ellipse((7, 7, 25, 19), fill=(156, 92, 174, 255))
            draw.rectangle((14, 17, 18, 28), fill=(210, 190, 150, 255))
        elif "root" in name:
            draw.line((3, 24, 12, 18, 20, 21, 30, 11), fill=(72, 44, 24, 255), width=4)
        elif "bone" in name:
            draw.line((6, 22, 26, 12), fill=(220, 210, 176, 255), width=4)
            draw.ellipse((3, 19, 11, 27), fill=(220, 210, 176, 255))
        elif "gear" in name:
            draw.ellipse((8, 8, 24, 24), outline=(168, 152, 120, 255), width=4)
            draw.line((6, 24, 26, 10), fill=(104, 72, 50, 255), width=3)
        else:
            draw.polygon((6, 24, 13, 8, 27, 18, 21, 27), fill=(128, 124, 116, 255), outline=(44, 40, 36, 255))
        image.save(MAP_TILESET_ROOT / f"{name}.png")


def main() -> int:
    ensure_dirs()
    if not _write_board_assets():
        write_textures()
        write_specials()
    write_organic_atlas_assets()
    write_manifest()
    write_map_icons()
    print(f"Wrote dungeon render assets under {DUNGEON_ROOT}")
    print(f"Wrote decorative map icons under {MAP_TILESET_ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
