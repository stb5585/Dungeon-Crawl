from __future__ import annotations

from dataclasses import dataclass

from src.core.player import DIRECTIONS


@dataclass(frozen=True)
class VisibleDepth:
    depth: int
    source_tile: object | None
    center: object | None
    left: object | None
    right: object | None
    left_branch: object | None
    right_branch: object | None
    left_forward: object | None
    right_forward: object | None
    left_forward_outer: object | None
    right_forward_outer: object | None


@dataclass(frozen=True)
class VisibleScene:
    depths: tuple[VisibleDepth, ...]


def is_wall(tile) -> bool:
    """Return whether a tile should be rendered as a blocking wall."""
    if tile is None:
        return True

    tile_type = type(tile).__name__

    if tile_type == "FakeWall":
        return not getattr(tile, "visited", False)

    if tile_type in ("FunhouseWall", "MirrorWall"):
        return True

    if tile_type == "OreVaultDoor":
        return not (getattr(tile, "open", False) or getattr(tile, "detected", False))

    # Doors now render on structural wall planes instead of the old sprite path.
    # Treat them as walls for scene extraction so the renderer emits the matching
    # back-wall / blocker geometry for both open and closed door tiles.
    if "Door" in tile_type:
        return True

    if any(name in tile_type for name in ("Chest", "Relic", "Boulder", "GoldenChaliceRoom", "SecretShop")):
        return False

    return getattr(tile, "enter", False) is False


def _perpendicular_offsets(facing: str) -> tuple[tuple[int, int], tuple[int, int]]:
    if facing == "north":
        return (-1, 0), (1, 0)
    if facing == "south":
        return (1, 0), (-1, 0)
    if facing == "east":
        return (0, -1), (0, 1)
    return (0, 1), (0, -1)


def extract_visible_scene(player_char, world_dict, max_depth: int = 3) -> VisibleScene:
    """Extract the forward scene for the current player position and facing."""
    x = player_char.location_x
    y = player_char.location_y
    z = player_char.location_z
    facing = player_char.facing

    dx, dy = DIRECTIONS[facing]["move"]
    (left_dx, left_dy), (right_dx, right_dy) = _perpendicular_offsets(facing)

    depths: list[VisibleDepth] = []

    for depth in range(1, max_depth + 1):
        source_x = x + dx * (depth - 1)
        source_y = y + dy * (depth - 1)
        center_x = x + dx * depth
        center_y = y + dy * depth

        source_tile = world_dict.get((source_x, source_y, z))
        center = world_dict.get((center_x, center_y, z))
        left = world_dict.get((source_x + left_dx, source_y + left_dy, z))
        right = world_dict.get((source_x + right_dx, source_y + right_dy, z))
        left_branch = world_dict.get((source_x + (left_dx * 2), source_y + (left_dy * 2), z))
        right_branch = world_dict.get((source_x + (right_dx * 2), source_y + (right_dy * 2), z))
        left_forward = world_dict.get((center_x + left_dx, center_y + left_dy, z))
        right_forward = world_dict.get((center_x + right_dx, center_y + right_dy, z))
        left_forward_outer = world_dict.get((center_x + (left_dx * 2), center_y + (left_dy * 2), z))
        right_forward_outer = world_dict.get((center_x + (right_dx * 2), center_y + (right_dy * 2), z))

        depths.append(
            VisibleDepth(
                depth=depth,
                source_tile=source_tile,
                center=center,
                left=left,
                right=right,
                left_branch=left_branch,
                right_branch=right_branch,
                left_forward=left_forward,
                right_forward=right_forward,
                left_forward_outer=left_forward_outer,
                right_forward_outer=right_forward_outer,
            )
        )

    return VisibleScene(tuple(depths))
