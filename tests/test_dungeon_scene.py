from __future__ import annotations

from dataclasses import dataclass

from src.ui_pygame.gui.dungeon.scene import extract_visible_scene


class OpenTile:
    enter = True


class WallTile:
    enter = False


@dataclass
class DummyPlayer:
    location_x: int = 0
    location_y: int = 0
    location_z: int = 1
    facing: str = "east"


def test_extract_visible_scene_straight_corridor():
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (2, 0, 1): OpenTile(),
        (3, 0, 1): OpenTile(),
        (0, -1, 1): WallTile(),
        (0, 1, 1): WallTile(),
        (1, -1, 1): WallTile(),
        (1, 1, 1): WallTile(),
    }

    scene = extract_visible_scene(player, world)

    assert len(scene.depths) == 3
    assert isinstance(scene.depths[0].source_tile, OpenTile)
    assert isinstance(scene.depths[0].center, OpenTile)
    assert isinstance(scene.depths[1].center, OpenTile)
    assert isinstance(scene.depths[2].center, OpenTile)
    assert isinstance(scene.depths[0].left, WallTile)
    assert isinstance(scene.depths[0].right, WallTile)


def test_extract_visible_scene_open_side_with_blocker():
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (2, 0, 1): OpenTile(),
        (0, -1, 1): OpenTile(),
        (1, -1, 1): WallTile(),
        (0, 1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
    }

    scene = extract_visible_scene(player, world)
    depth1 = scene.depths[0]

    assert isinstance(depth1.left, OpenTile)
    assert depth1.left_branch is None
    assert isinstance(depth1.left_forward, WallTile)
    assert isinstance(depth1.right, OpenTile)
    assert depth1.right_branch is None
    assert isinstance(depth1.right_forward, OpenTile)


def test_extract_visible_scene_tracks_outer_side_corridor_walls():
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (0, 1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (1, 2, 1): WallTile(),
    }

    scene = extract_visible_scene(player, world)
    depth1 = scene.depths[0]

    assert isinstance(depth1.right, OpenTile)
    assert depth1.right_branch is None
    assert isinstance(depth1.right_forward, OpenTile)
    assert isinstance(depth1.right_forward_outer, WallTile)


def test_extract_visible_scene_tracks_side_branch_corridor_tiles():
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (0, -1, 1): OpenTile(),
        (0, -2, 1): OpenTile(),
        (1, -1, 1): OpenTile(),
        (1, -2, 1): WallTile(),
    }

    scene = extract_visible_scene(player, world)
    depth1 = scene.depths[0]

    assert isinstance(depth1.left, OpenTile)
    assert isinstance(depth1.left_branch, OpenTile)
    assert isinstance(depth1.left_forward, OpenTile)
    assert isinstance(depth1.left_forward_outer, WallTile)
