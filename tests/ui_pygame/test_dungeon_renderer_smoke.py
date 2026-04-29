from __future__ import annotations

import os
from dataclasses import dataclass

import pygame

from src.ui_pygame.gui.dungeon.assets import TextureLibrary
from src.ui_pygame.gui.dungeon.geometry import build_depth_rect, build_next_depth_rect, build_zone_geometry
from src.ui_pygame.gui.dungeon.geometry import Quad
from src.ui_pygame.gui.dungeon.projector import project_texture_to_quad
from src.ui_pygame.gui.dungeon.renderer import SceneRenderer
from src.ui_pygame.gui.dungeon.scene import extract_visible_scene
from src.ui_pygame.gui.dungeon_renderer import DungeonRenderer


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


class OpenTile:
    enter = True


class WallTile:
    enter = False


class FakeWall:
    enter = True

    def __init__(self, visited=True):
        self.visited = visited


class LockedDoor:
    enter = False
    open = False


class OpenDoor:
    enter = True
    open = True


class ChestRoom:
    enter = True
    locked = False
    open = False


class LadderUp:
    enter = True


class LadderDown:
    enter = True


class StairsDown:
    enter = True


class UndergroundSpring:
    enter = True


class Portal:
    enter = True


class Boulder:
    enter = True

    def __init__(self, read=False):
        self.read = read


class DeadBody:
    enter = True

    def __init__(self, read=False):
        self.read = read


class RelicRoom:
    enter = False

    def __init__(self, read=False):
        self.read = read


class GoldenChaliceRoom:
    enter = False

    def __init__(self, read=False):
        self.read = read


class UnobtainiumRoom:
    enter = True

    def __init__(self, visited=False):
        self.visited = visited


class SecretShop:
    enter = False


class WarpPoint:
    enter = True


class BossRoom:
    enter = False

    def __init__(self, enemy=None, defeated=False):
        self.enemy = enemy
        self.defeated = defeated


class DummyEnemy:
    def __init__(self, name="Minotaur"):
        self.name = name

    def is_alive(self):
        return True


@dataclass
class DummyPlayer:
    location_x: int = 0
    location_y: int = 0
    location_z: int = 1
    facing: str = "east"
    warp_point: bool = False


@dataclass
class DummyPresenter:
    width: int
    height: int
    screen: pygame.Surface


def _build_scene_commands(scene_renderer: SceneRenderer, player, world):
    view_w, view_h = scene_renderer._get_viewport_size()
    scene = extract_visible_scene(player, world, max_depth=3)
    zones = {
        depth: build_zone_geometry(
            build_depth_rect(view_w, view_h, depth),
            build_next_depth_rect(build_depth_rect(view_w, view_h, depth)),
            depth=depth,
        )
        for depth in (1, 2, 3)
    }
    return scene_renderer._build_render_commands(scene, zones), zones


def test_dungeon_renderer_smoke():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    renderer = DungeonRenderer(presenter)
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (2, 0, 1): OpenTile(),
        (3, 0, 1): WallTile(),
        (0, -1, 1): OpenTile(),
        (1, -1, 1): WallTile(),
        (0, 1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
    }

    renderer.render_dungeon_view(player, world)
    renderer.render_message_area(["Line 1", "Line 2"], scroll_offset=0, lines_per_page=2)
    renderer.trigger_damage_flash(duration_ms=100, alpha=128)
    renderer.render_damage_flash()

    pygame.quit()


def test_dungeon_renderer_special_tiles_smoke():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    renderer = DungeonRenderer(presenter)
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): ChestRoom(),
        (2, 0, 1): LockedDoor(),
        (3, 0, 1): StairsDown(),
        (0, -1, 1): OpenTile(),
        (0, 1, 1): OpenTile(),
        (1, -1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (2, -1, 1): OpenTile(),
        (2, 1, 1): OpenTile(),
        (3, -1, 1): OpenTile(),
        (3, 1, 1): OpenTile(),
    }

    world[(0, 0, 1)] = LadderUp()
    renderer.render_dungeon_view(player, world)

    pixel_data = pygame.image.tostring(screen, "RGBA")
    assert any(channel != 0 for channel in pixel_data)

    pygame.quit()


def test_dungeon_renderer_applies_soft_vignette_to_viewport():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    renderer = DungeonRenderer(presenter)
    screen.fill((220, 220, 220))

    renderer.overlays.render_vignette()

    left_corner = screen.get_at((2, 2))
    center = screen.get_at((150, 150))
    divider = screen.get_at((int(640 * 0.65) - 1, 150))
    right_hud = screen.get_at((500, 150))

    assert left_corner.r < center.r
    assert left_corner.g < center.g
    assert left_corner.b < center.b
    assert divider.r < center.r
    assert right_hud.r == 220 and right_hud.g == 220 and right_hud.b == 220

    pygame.quit()


def test_texture_library_does_not_tile_ladder_pit_panels():
    pygame.init()
    textures = TextureLibrary()

    ceiling = textures.get_texture("ceiling_pit")
    floor = textures.get_texture("floor_pit")

    assert textures.get_ceiling_key(LadderUp()) == "ceiling_pit"
    assert textures.get_panel_texture("d2:center_ceiling", "ceiling_pit").get_size() == (ceiling.get_width() * 5, ceiling.get_height())
    assert textures.get_panel_texture("d2:center_floor", "floor_pit").get_size() == (floor.get_width() * 5, floor.get_height())
    assert textures.get_panel_texture("d2:right_corridor_outer_ceiling", "ceiling_pit").get_size() == ceiling.get_size()
    assert textures.get_panel_texture("d2:right_corridor_outer_floor", "floor_pit").get_size() == floor.get_size()

    pygame.quit()


def test_texture_library_resolves_repo_assets_when_cwd_changes(tmp_path, monkeypatch):
    pygame.init()
    monkeypatch.chdir(tmp_path)

    textures = TextureLibrary()

    assert textures.get_texture("wall").get_width() > 0
    assert textures.get_special_texture("stairs_down") is not None
    assert textures.get_enemy_texture("Minotaur", size=32) is not None

    pygame.quit()


def test_texture_library_records_missing_asset_fallbacks(tmp_path):
    pygame.init()
    textures = TextureLibrary(tileset_base=tmp_path / "missing_tiles")

    wall = textures.get_texture("wall")
    special = textures.get_special_texture("stairs_down", size=24)
    enemy = textures.get_enemy_texture("Missing Enemy", size=24)
    fallbacks = textures.get_asset_fallbacks()

    assert wall.get_size() == (128, 128)
    assert special is not None
    assert max(special.get_size()) == 24
    assert enemy is None
    assert fallbacks["texture:wall"].endswith("walls/brick.png")
    assert fallbacks["special:stairs_down"].endswith("special_tiles/stairs_down.png")
    assert fallbacks["enemy:Missing Enemy"].endswith("sprites/enemies/missing_enemy.png")

    fallbacks.clear()
    assert "texture:wall" in textures.get_asset_fallbacks()

    pygame.quit()


def test_texture_library_limits_projected_surface_cache():
    pygame.init()
    pygame.display.set_mode((1, 1))
    textures = TextureLibrary(projected_cache_limit=2)
    quad = Quad(((0.0, 0.0), (64.0, 0.0), (64.0, 64.0), (0.0, 64.0)))

    for width in (128, 129, 130):
        textures.get_projected_surface(
            panel_id="d1:center_floor",
            texture_key="floor",
            quad=quad,
            darkness=0.0,
            view_size=(width, 128),
        )

    assert len(textures._projected_cache) == 2
    assert all(cache_key[0] != (128, 128) for cache_key in textures._projected_cache)

    pygame.quit()


def test_texture_library_describes_floor_slot_ids():
    textures = TextureLibrary()

    assert textures.describe_floor_slot_ids("d2:center_floor") == (
        "floor:visible:d2:xm2",
        "floor:visible:d2:xm1",
        "floor:visible:d2:x0",
        "floor:visible:d2:xp1",
        "floor:visible:d2:xp2",
    )
    assert textures.describe_floor_slot_ids("d3:center_floor") == (
        "floor:visible:d3:xm4",
        "floor:visible:d3:xm3",
        "floor:visible:d3:xm2",
        "floor:visible:d3:xm1",
        "floor:visible:d3:x0",
        "floor:visible:d3:xp1",
        "floor:visible:d3:xp2",
        "floor:visible:d3:xp3",
        "floor:visible:d3:xp4",
    )
    assert textures.describe_floor_slot_ids("d2:right_corridor_outer_floor") == (
        "floor:corridor_outer:right:d2:tile",
    )


def test_texture_library_describes_depth3_center_slot_spans():
    textures = TextureLibrary()

    assert textures.describe_surface_slot_spans("d3:center_floor", texture_key="floor") == (
        (-1.0 / 7.0, 0.0),
        (0.0, 1.0 / 7.0),
        (1.0 / 7.0, 2.0 / 7.0),
        (2.0 / 7.0, 3.0 / 7.0),
        (3.0 / 7.0, 4.0 / 7.0),
        (4.0 / 7.0, 5.0 / 7.0),
        (5.0 / 7.0, 6.0 / 7.0),
        (6.0 / 7.0, 1.0),
        (1.0, 8.0 / 7.0),
    )
    assert textures.describe_surface_slot_spans("d3:center_ceiling", texture_key="ceiling") == (
        (-1.0 / 7.0, 0.0),
        (0.0, 1.0 / 7.0),
        (1.0 / 7.0, 2.0 / 7.0),
        (2.0 / 7.0, 3.0 / 7.0),
        (3.0 / 7.0, 4.0 / 7.0),
        (4.0 / 7.0, 5.0 / 7.0),
        (5.0 / 7.0, 6.0 / 7.0),
        (6.0 / 7.0, 1.0),
        (1.0, 8.0 / 7.0),
    )


def test_scene_renderer_preserves_overscan_for_depth3_slot_slices():
    quad = Quad(
        (
            (-249.0, 288.0),
            (913.0, 288.0),
            (581.0, 336.0),
            (83.0, 336.0),
        )
    )

    left_slot = SceneRenderer._slice_quad_horizontal_region(quad, -1.0 / 7.0, 0.0)
    right_slot = SceneRenderer._slice_quad_horizontal_region(quad, 1.0, 8.0 / 7.0)

    assert left_slot.points[0][0] < quad.points[0][0]
    assert left_slot.points[3][0] < quad.points[3][0]
    assert right_slot.points[1][0] > quad.points[1][0]
    assert right_slot.points[2][0] > quad.points[2][0]


def test_texture_library_describes_ceiling_and_wall_slot_ids():
    textures = TextureLibrary()

    assert textures.describe_ceiling_slot_ids("d2:center_ceiling") == (
        "ceiling:visible:d2:xm2",
        "ceiling:visible:d2:xm1",
        "ceiling:visible:d2:x0",
        "ceiling:visible:d2:xp1",
        "ceiling:visible:d2:xp2",
    )
    assert textures.describe_ceiling_slot_ids("d3:center_ceiling") == (
        "ceiling:visible:d3:xm4",
        "ceiling:visible:d3:xm3",
        "ceiling:visible:d3:xm2",
        "ceiling:visible:d3:xm1",
        "ceiling:visible:d3:x0",
        "ceiling:visible:d3:xp1",
        "ceiling:visible:d3:xp2",
        "ceiling:visible:d3:xp3",
        "ceiling:visible:d3:xp4",
    )
    assert textures.describe_ceiling_slot_ids("d2:right_corridor_outer_ceiling") == (
        "ceiling:corridor_outer:right:d2:tile",
    )
    assert textures.describe_wall_slot_ids("d1:back_wall") == (
        "wall:visible:d1:center",
    )
    assert textures.describe_wall_slot_ids("d1:right_wall") == (
        "wall:visible:d1:right:right:near",
        "wall:visible:d1:right:right:far",
    )
    assert textures.describe_wall_slot_ids("d2:right_corridor_outer_wall") == (
        "wall:visible:d2:corridor_outer:right:near",
        "wall:visible:d2:corridor_outer:right:far",
    )


def test_texture_library_loads_migrated_special_and_enemy_sprites():
    pygame.init()
    textures = TextureLibrary()

    for key in (
        "portal",
        "boulder",
        "boulder_sword",
        "dead_body",
        "burial_site",
        "empty_altar",
        "luna_altar",
        "golden_chalice_altar",
        "secret_shop",
        "unobtainium",
    ):
        assert textures.get_special_texture(key) is not None

    assert textures.get_enemy_texture("Minotaur") is not None

    pygame.quit()


def test_texture_library_can_override_individual_floor_slots():
    pygame.init()
    textures = TextureLibrary()

    baseline = textures.get_panel_texture("d2:right_corridor_outer_floor", "floor")
    textures.set_floor_slot_override("floor:corridor_outer:right:d2:tile", "floor_pit")
    overridden = textures.get_panel_texture("d2:right_corridor_outer_floor", "floor")

    assert overridden.get_size() == baseline.get_size()
    assert pygame.image.tostring(overridden, "RGBA") != pygame.image.tostring(baseline, "RGBA")

    textures.clear_floor_slot_overrides()
    restored = textures.get_panel_texture("d2:right_corridor_outer_floor", "floor")
    assert restored.get_size() == baseline.get_size()

    pygame.quit()


def test_texture_library_can_override_individual_ceiling_and_wall_slots():
    pygame.init()
    textures = TextureLibrary()

    baseline_ceiling = textures.get_panel_texture("d2:center_ceiling", "ceiling")
    textures.set_ceiling_slot_override("ceiling:visible:d2:xp1", "ceiling_pit")
    overridden_ceiling = textures.get_panel_texture("d2:center_ceiling", "ceiling")
    assert pygame.image.tostring(overridden_ceiling, "RGBA") != pygame.image.tostring(baseline_ceiling, "RGBA")

    textures.clear_surface_slot_overrides()

    baseline_wall = textures.get_panel_texture("d1:right_wall", "wall")
    textures.set_wall_slot_override("wall:visible:d1:right:right:near", "floor_funhouse")
    overridden_wall = textures.get_panel_texture("d1:right_wall", "wall")
    assert pygame.image.tostring(overridden_wall, "RGBA") != pygame.image.tostring(baseline_wall, "RGBA")

    textures.clear_surface_slot_overrides()
    pygame.quit()


def test_scene_renderer_can_disable_darkness_via_env():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    player = DummyPlayer()
    world = {(0, 0, 1): OpenTile()}
    previous = os.environ.get("DUNGEON_RENDERER_DISABLE_DARKNESS")
    os.environ["DUNGEON_RENDERER_DISABLE_DARKNESS"] = "1"

    try:
        scene_renderer = SceneRenderer(presenter, TextureLibrary())
        commands, _ = _build_scene_commands(scene_renderer, player, world)

        assert scene_renderer._get_layer_darkness(1) == 0.0
        assert scene_renderer._get_layer_darkness(2) == 0.0
        assert scene_renderer._get_layer_darkness(3) == 0.0
        assert all(command.darkness == 0.0 for command in commands)
    finally:
        if previous is None:
            os.environ.pop("DUNGEON_RENDERER_DISABLE_DARKNESS", None)
        else:
            os.environ["DUNGEON_RENDERER_DISABLE_DARKNESS"] = previous

    pygame.quit()


def test_scene_renderer_adds_endcaps_for_center_wall_with_blocked_side_corridors():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (1, -1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (2, 0, 1): WallTile(),
        (2, -1, 1): WallTile(),
        (2, 1, 1): WallTile(),
        (2, -2, 1): WallTile(),
        (2, 2, 1): WallTile(),
    }

    commands, _ = _build_scene_commands(scene_renderer, player, world)

    assert any(command.panel_id == "d2:left_back_wall_endcap" for command in commands)
    assert any(command.panel_id == "d2:right_back_wall_endcap" for command in commands)

    pygame.quit()


def test_scene_renderer_adds_endcap_for_open_center_side_blocker_with_outer_wall():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (2, 0, 1): OpenTile(),
        (0, -1, 1): WallTile(),
        (1, -1, 1): WallTile(),
        (2, -1, 1): WallTile(),
        (0, 1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (2, 1, 1): WallTile(),
        (2, 2, 1): WallTile(),
    }

    commands, _ = _build_scene_commands(scene_renderer, player, world)

    assert any(command.panel_id == "d2:right_blocker" for command in commands)
    assert any(command.panel_id == "d2:right_back_wall_endcap" for command in commands)

    pygame.quit()


def test_scene_renderer_renders_side_corridor_outer_wall_in_side_wall_layer():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): WallTile(),
        (0, 1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (1, 2, 1): WallTile(),
    }

    commands, _ = _build_scene_commands(scene_renderer, player, world)

    corridor_wall = next(command for command in commands if command.panel_id == "d2:right_corridor_outer_wall")
    assert corridor_wall.order == 3

    pygame.quit()


def test_scene_renderer_keeps_outer_side_corridor_door_state_on_outer_wall():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (0, 1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (1, 2, 1): LockedDoor(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d2:right_corridor_outer_wall", "door_closed") in calls
    assert ("d2:right_corridor_outer_wall", "wall") not in calls

    pygame.quit()


def test_scene_renderer_keeps_outer_side_corridor_open_door_state_on_outer_wall():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (0, 1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (1, 2, 1): OpenDoor(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d2:right_corridor_outer_wall", "door_open") in calls
    assert ("d2:right_corridor_outer_wall", "wall") not in calls

    pygame.quit()


def test_scene_renderer_adds_three_depth3_endcaps_per_side_for_full_back_wall():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (2, 0, 1): OpenTile(),
        (2, -1, 1): OpenTile(),
        (2, 1, 1): OpenTile(),
        (3, 0, 1): WallTile(),
        (3, -1, 1): WallTile(),
        (3, 1, 1): WallTile(),
        (2, -2, 1): WallTile(),
        (2, 2, 1): WallTile(),
        (3, -2, 1): WallTile(),
        (3, 2, 1): WallTile(),
    }

    commands, _ = _build_scene_commands(scene_renderer, player, world)

    assert any(command.panel_id == "d3:left_back_wall_endcap" for command in commands)
    assert any(command.panel_id == "d3:left_back_wall_endcap1" for command in commands)
    assert any(command.panel_id == "d3:left_back_wall_endcap2" for command in commands)
    assert any(command.panel_id == "d3:right_back_wall_endcap" for command in commands)
    assert any(command.panel_id == "d3:right_back_wall_endcap1" for command in commands)
    assert any(command.panel_id == "d3:right_back_wall_endcap2" for command in commands)

    pygame.quit()


def test_scene_renderer_skips_special_tiles_hidden_behind_center_wall():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): WallTile(),
        (2, 0, 1): ChestRoom(),
        (0, -1, 1): OpenTile(),
        (0, 1, 1): OpenTile(),
        (1, -1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (2, -1, 1): OpenTile(),
        (2, 1, 1): OpenTile(),
    }

    rendered_tiles = []
    original_render_special_tile = scene_renderer._render_special_tile

    def recording_render_special_tile(tile, rect, darkness, depth, side=None, lateral_view=False):
        rendered_tiles.append((type(tile).__name__ if tile else None, depth, side, lateral_view))
        return original_render_special_tile(
            tile,
            rect,
            darkness,
            depth,
            side=side,
            lateral_view=lateral_view,
        )

    scene_renderer._render_special_tile = recording_render_special_tile

    scene_renderer.render(player, world)

    assert ("WallTile", 1, None, False) in rendered_tiles
    assert ("ChestRoom", 2, None, False) not in rendered_tiles

    pygame.quit()


def test_scene_renderer_renders_side_special_tiles_in_opening():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): WallTile(),
        (0, -1, 1): OpenTile(),
        (1, -1, 1): ChestRoom(),
        (0, 1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
    }

    rendered_tiles = []
    original_render_special_tile = scene_renderer._render_special_tile

    def recording_render_special_tile(tile, rect, darkness, depth, side=None, lateral_view=False):
        rendered_tiles.append((type(tile).__name__ if tile else None, depth, side, lateral_view))
        return original_render_special_tile(
            tile,
            rect,
            darkness,
            depth,
            side=side,
            lateral_view=lateral_view,
        )

    scene_renderer._render_special_tile = recording_render_special_tile

    scene_renderer.render(player, world)

    assert ("ChestRoom", 2, "left", True) in rendered_tiles

    pygame.quit()


def test_scene_renderer_advances_side_floor_sprite_depth_when_next_zone_is_visible():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): WallTile(),
        (0, -1, 1): OpenTile(),
        (1, -1, 1): ChestRoom(),
        (0, 1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (2, 0, 1): OpenTile(),
        (2, -1, 1): OpenTile(),
        (2, 1, 1): OpenTile(),
    }

    rendered_tiles = []
    original_render_special_tile = scene_renderer._render_special_tile

    def recording_render_special_tile(tile, rect, darkness, depth, side=None, lateral_view=False):
        rendered_tiles.append((type(tile).__name__ if tile else None, depth, side, lateral_view))
        return original_render_special_tile(
            tile,
            rect,
            darkness,
            depth,
            side=side,
            lateral_view=lateral_view,
        )

    scene_renderer._render_special_tile = recording_render_special_tile

    scene_renderer.render(player, world)

    assert ("ChestRoom", 2, "left", True) in rendered_tiles

    pygame.quit()


def test_scene_renderer_renders_side_door_in_opening():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): WallTile(),
        (0, -1, 1): OpenTile(),
        (1, -1, 1): LockedDoor(),
        (0, 1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d1:left_blocker_slot0", "door_closed") in calls
    assert ("d1:left_blocker", "wall") not in calls

    pygame.quit()


def test_scene_renderer_hides_side_doors_behind_center_wall():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): WallTile(),
        (0, -1, 1): OpenTile(),
        (0, 1, 1): OpenTile(),
        (1, -1, 1): LockedDoor(),
        (1, 1, 1): LockedDoor(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d1:left_blocker_slot0", "door_closed") not in calls
    assert ("d1:right_blocker_slot0", "door_closed") not in calls

    pygame.quit()


def test_scene_renderer_keeps_single_side_door_and_other_side_special_behind_center_wall():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): WallTile(),
        (0, -1, 1): OpenTile(),
        (0, 1, 1): OpenTile(),
        (1, -1, 1): LockedDoor(),
        (1, 1, 1): ChestRoom(),
    }

    projected_calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        projected_calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    rendered_tiles = []
    original_render_special_tile = scene_renderer._render_special_tile

    def recording_render_special_tile(tile, rect, darkness, depth, side=None, lateral_view=False):
        rendered_tiles.append((type(tile).__name__ if tile else None, depth, side, lateral_view))
        return original_render_special_tile(
            tile,
            rect,
            darkness,
            depth,
            side=side,
            lateral_view=lateral_view,
        )

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface
    scene_renderer._render_special_tile = recording_render_special_tile

    scene_renderer.render(player, world)

    assert ("d1:left_blocker_slot0", "door_closed") in projected_calls
    assert ("ChestRoom", 2, "right", True) in rendered_tiles

    pygame.quit()


def test_scene_renderer_hides_only_deeper_side_specials_after_depth2_center_wall():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (2, 0, 1): WallTile(),
        (1, -1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (2, -1, 1): LockedDoor(),
        (2, 1, 1): OpenTile(),
        (3, -1, 1): LockedDoor(),
        (3, 1, 1): LockedDoor(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d2:left_blocker_slot0", "door_closed") in calls
    assert calls.count(("d2:left_blocker_slot0", "door_closed")) == 1
    assert ("d2:right_blocker_slot0", "door_closed") not in calls

    pygame.quit()


def test_scene_renderer_keeps_both_depth2_side_doors_when_center_wall_is_deeper():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (2, 0, 1): WallTile(),
        (0, -1, 1): WallTile(),
        (0, 1, 1): WallTile(),
        (1, -1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (2, -1, 1): LockedDoor(),
        (2, 1, 1): LockedDoor(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d2:left_blocker_slot0", "door_closed") in calls
    assert ("d2:right_blocker_slot0", "door_closed") in calls

    pygame.quit()


def test_scene_renderer_does_not_render_current_tile_door():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenDoor(),
        (1, 0, 1): OpenTile(),
        (2, 0, 1): LockedDoor(),
        (0, -1, 1): OpenTile(),
        (0, 1, 1): OpenTile(),
        (1, -1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (2, -1, 1): OpenTile(),
        (2, 1, 1): OpenTile(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d2:back_wall_slot0", "door_closed") in calls
    assert ("d1:back_wall_slot0", "door_open") not in calls

    pygame.quit()


def test_scene_renderer_renders_center_special_tiles_back_to_front():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): LadderUp(),
        (2, 0, 1): LockedDoor(),
        (0, -1, 1): OpenTile(),
        (0, 1, 1): OpenTile(),
        (1, -1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (2, -1, 1): OpenTile(),
        (2, 1, 1): OpenTile(),
    }

    rendered_tiles = []
    original_render_special_tile = scene_renderer._render_special_tile

    def recording_render_special_tile(tile, rect, darkness, depth, side=None, lateral_view=False):
        rendered_tiles.append((type(tile).__name__ if tile else None, depth, side, lateral_view))
        return original_render_special_tile(
            tile,
            rect,
            darkness,
            depth,
            side=side,
            lateral_view=lateral_view,
        )

    scene_renderer._render_special_tile = recording_render_special_tile

    scene_renderer.render(player, world)

    center_draws = [entry for entry in rendered_tiles if entry[2] is None and not entry[3] and entry[1] > 0]
    assert center_draws[:2] == [("LockedDoor", 2, None, False), ("LadderUp", 1, None, False)]

    pygame.quit()


def test_scene_renderer_builds_skewed_lateral_floor_sprite_quads():
    rect = pygame.Rect(100, 200, 80, 60)

    left_quad = SceneRenderer._get_lateral_floor_sprite_quad(rect, "left")
    right_quad = SceneRenderer._get_lateral_floor_sprite_quad(rect, "right")

    assert left_quad.points[0][1] == left_quad.points[1][1]
    assert left_quad.points[0][0] > rect.left
    assert left_quad.points[2][0] == rect.right

    assert right_quad.points[0][1] == right_quad.points[1][1]
    assert right_quad.points[1][0] < rect.right
    assert right_quad.points[3][0] == rect.left


def test_project_texture_to_quad_preserves_transparent_sprite_background():
    pygame.init()
    texture = pygame.Surface((32, 32), pygame.SRCALPHA)
    texture.fill((0, 0, 0, 0))
    pygame.draw.circle(texture, (255, 200, 50, 255), (16, 16), 8)

    projected = project_texture_to_quad(
        texture,
        Quad(((2, 2), (28, 4), (30, 30), (0, 28))),
    )

    assert projected.surface.get_at((0, 0)).a == 0

    pygame.quit()


def test_trim_transparent_sprite_removes_empty_padding():
    pygame.init()
    texture = pygame.Surface((40, 20), pygame.SRCALPHA)
    texture.fill((0, 0, 0, 0))
    pygame.draw.rect(texture, (255, 255, 255, 255), pygame.Rect(10, 3, 18, 14))

    trimmed = SceneRenderer._trim_transparent_sprite(texture)

    assert trimmed.get_size() == (18, 14)

    pygame.quit()


def test_lateral_door_sprite_rect_biases_toward_outer_wall():
    rect = pygame.Rect(249, 336, 41, 96)

    left_rect = SceneRenderer._get_lateral_door_sprite_rect(rect, "left")
    right_rect = SceneRenderer._get_lateral_door_sprite_rect(rect, "right")

    assert left_rect.left < rect.left
    assert left_rect.width > rect.width
    assert right_rect.right > rect.right
    assert right_rect.width > rect.width


def test_lateral_stairs_sprite_rect_uses_extra_overscan():
    rect = pygame.Rect(415, 192, 83, 384)

    right_rect = SceneRenderer._get_lateral_stairs_sprite_rect(rect, "right")
    left_rect = SceneRenderer._get_lateral_stairs_sprite_rect(rect, "left")
    generic_right = SceneRenderer._get_special_sprite_rect(rect, side="right", lateral_view=True)

    assert right_rect.width > generic_right.width
    assert right_rect.left == rect.left
    assert left_rect.right == rect.right


def test_side_floor_special_clip_rect_keeps_chest_behind_blocking_corner():
    rect = pygame.Rect(100, 200, 80, 60)
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (0, -1, 1): WallTile(),
        (0, 1, 1): OpenTile(),
        (1, 1, 1): ChestRoom(),
        (2, 1, 1): WallTile(),
    }

    _, zones = _build_scene_commands(scene_renderer, player, world)
    left_render = scene_renderer._get_side_special_render_rect(
        rect,
        ChestRoom(),
        "left",
        center_tile=OpenTile(),
        zone=zones[1],
        next_zone=zones[2],
        depth=1,
    )
    right_render = scene_renderer._get_side_special_render_rect(
        rect,
        ChestRoom(),
        "right",
        center_tile=OpenTile(),
        zone=zones[1],
        next_zone=zones[2],
        depth=1,
    )
    walled_render = scene_renderer._get_side_special_render_rect(rect, ChestRoom(), "left", center_tile=WallTile())
    left_clip = SceneRenderer._get_side_special_clip_rect(rect, Boulder(), "left", center_tile=WallTile())
    right_clip = SceneRenderer._get_side_special_clip_rect(rect, Boulder(), "right", center_tile=WallTile())
    portal_clip = SceneRenderer._get_side_special_clip_rect(rect, Portal(), "left", center_tile=WallTile())
    chest_clip = SceneRenderer._get_side_special_clip_rect(rect, ChestRoom(), "left", center_tile=WallTile())
    unclipped_boulder = SceneRenderer._get_side_special_clip_rect(rect, Boulder(), "left", center_tile=OpenTile())

    assert left_render.w > rect.width
    assert right_render.w > rect.width
    assert left_render.h == rect.height
    assert right_render.h == rect.height

    assert walled_render == rect

    assert left_clip.width > rect.width
    assert left_clip.left == rect.left
    assert left_clip.right > rect.right

    assert right_clip.width > rect.width
    assert right_clip.right == rect.right
    assert right_clip.left < rect.left

    assert portal_clip == rect
    assert chest_clip == rect
    assert unclipped_boulder is None

    pygame.quit()


def test_texture_library_floor_slot_override_changes_projected_corridor_floor_surface():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): WallTile(),
        (0, -1, 1): WallTile(),
        (1, -1, 1): WallTile(),
        (0, 1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
    }

    _, zones = _build_scene_commands(scene_renderer, player, world)
    corridor_quad = scene_renderer._push_outer_floor_quad(
        zones[2].center_floor_right,
        "right",
        float(zones[1].rect.w) * 0.25,
        float(zones[1].rect.w) * 0.5,
    )

    baseline = scene_renderer.textures.get_projected_surface(
        panel_id="d2:right_corridor_outer_floor",
        texture_key="floor",
        quad=corridor_quad,
        darkness=0.0,
        view_size=scene_renderer._get_viewport_size(),
    )

    scene_renderer.textures.set_floor_slot_override("floor:corridor_outer:right:d2:tile", "floor_pit")
    overridden = scene_renderer.textures.get_projected_surface(
        panel_id="d2:right_corridor_outer_floor",
        texture_key="floor",
        quad=corridor_quad,
        darkness=0.0,
        view_size=scene_renderer._get_viewport_size(),
    )

    assert pygame.image.tostring(overridden.surface, "RGBA") != pygame.image.tostring(baseline.surface, "RGBA")

    scene_renderer.textures.clear_floor_slot_overrides()

    pygame.quit()


def test_scene_renderer_routes_side_ladder_floor_through_center_floor_slot_override():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): WallTile(),
        (0, -1, 1): WallTile(),
        (1, -1, 1): WallTile(),
        (0, 1, 1): OpenTile(),
        (1, 1, 1): LadderDown(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d2:center_floor", "floor") not in calls
    assert ("d2:center_floor_slot3", "floor_pit") in calls
    assert ("d1:right_opening_special_floor", "floor_pit") not in calls
    assert scene_renderer.textures.get_floor_slot_overrides() == {
        "floor:visible:d2:xp1": "floor_pit",
    }

    pygame.quit()


def test_scene_renderer_localizes_current_underground_spring_floor_to_center_slot():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): UndergroundSpring(),
        (1, 0, 1): WallTile(),
        (0, -1, 1): OpenTile(),
        (0, 1, 1): OpenTile(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d1:center_floor", "floor") not in calls
    assert ("d1:center_floor_slot1", "floor_spring") in calls
    assert scene_renderer.textures.get_floor_slot_overrides() == {
        "floor:visible:d1:x0": "floor_spring",
    }

    pygame.quit()


def test_scene_renderer_maps_adjacent_side_spring_to_left_visible_floor_slot():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer(location_x=4, location_y=8, facing="west")
    world = {
        (4, 8, 1): OpenTile(),
        (3, 8, 1): WallTile(),
        (4, 9, 1): UndergroundSpring(),
        (4, 7, 1): OpenTile(),
        (3, 9, 1): WallTile(),
        (3, 7, 1): LockedDoor(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d1:center_floor", "floor") not in calls
    assert ("d1:center_floor_slot0", "floor_spring") in calls
    assert scene_renderer.textures.get_floor_slot_overrides()["floor:visible:d1:xm1"] == "floor_spring"

    pygame.quit()


def test_scene_renderer_hides_side_ladder_beyond_max_visible_depth():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (2, 0, 1): OpenTile(),
        (3, 0, 1): OpenTile(),
        (0, -1, 1): WallTile(),
        (1, -1, 1): WallTile(),
        (2, -1, 1): WallTile(),
        (3, -1, 1): WallTile(),
        (0, 1, 1): WallTile(),
        (1, 1, 1): WallTile(),
        (2, 1, 1): OpenTile(),
        (3, 1, 1): LadderDown(),
    }

    calls = []
    rendered_tiles = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface
    original_render_special_tile = scene_renderer._render_special_tile

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    def recording_render_special_tile(tile, rect, darkness, depth, side=None, lateral_view=False):
        rendered_tiles.append((type(tile).__name__ if tile else None, depth, side, lateral_view))
        return original_render_special_tile(
            tile,
            rect,
            darkness,
            depth,
            side=side,
            lateral_view=lateral_view,
        )

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface
    scene_renderer._render_special_tile = recording_render_special_tile

    scene_renderer.render(player, world)

    assert ("d3:center_floor", "floor") not in calls
    assert any(panel_id.startswith("d3:center_floor_slot") for panel_id, _ in calls)
    assert not any(panel_id.startswith("d3:center_floor_slot") and texture_key == "floor_pit" for panel_id, texture_key in calls)
    assert ("LadderDown", 3, "right", True) not in rendered_tiles
    assert scene_renderer.textures.get_floor_slot_overrides() == {}

    pygame.quit()


def test_scene_renderer_routes_far_right_floor_special_to_outer_depth3_slot():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): BossRoom(enemy=DummyEnemy("Cockatrice"), defeated=True),
        (2, 0, 1): OpenTile(),
        (3, 0, 1): None,
        (0, -1, 1): WallTile(),
        (0, 1, 1): WallTile(),
        (0, -2, 1): WallTile(),
        (0, 2, 1): ChestRoom(),
        (1, -1, 1): ChestRoom(),
        (1, 1, 1): ChestRoom(),
        (1, -2, 1): WallTile(),
        (1, 2, 1): WallTile(),
        (2, -1, 1): WallTile(),
        (2, 1, 1): LadderDown(),
        (2, -2, 1): WallTile(),
        (2, 2, 1): LockedDoor(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d3:center_floor", "floor") not in calls
    assert any(panel_id.startswith("d3:center_floor_slot") for panel_id, _ in calls)
    assert ("d3:center_floor_slot5", "floor_pit") in calls
    assert scene_renderer.textures.get_floor_slot_overrides()["floor:visible:d3:xp1"] == "floor_pit"

    pygame.quit()


def test_scene_renderer_renders_depth3_center_ceiling_through_slot_commands_without_overrides():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (2, 0, 1): OpenTile(),
        (0, -1, 1): OpenTile(),
        (0, 1, 1): OpenTile(),
        (1, -1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (2, -1, 1): OpenTile(),
        (2, 1, 1): OpenTile(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d3:center_ceiling", "ceiling") not in calls
    assert any(panel_id.startswith("d3:center_ceiling_slot") for panel_id, _ in calls)
    assert ("d3:center_ceiling_slot0", "ceiling") in calls
    assert ("d3:center_ceiling_slot8", "ceiling") in calls

    pygame.quit()


def test_scene_renderer_renders_migrated_special_tile_sprites():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    scene_renderer.player_char = DummyPlayer(location_z=3)
    rect = pygame.Rect(120, 120, 160, 160)

    special_calls = []
    enemy_calls = []
    original_get_special_texture = scene_renderer.textures.get_special_texture
    original_get_enemy_texture = scene_renderer.textures.get_enemy_texture

    def recording_get_special_texture(texture_key, size=None):
        special_calls.append((texture_key, size))
        return original_get_special_texture(texture_key, size)

    def recording_get_enemy_texture(enemy_name, size=None):
        enemy_calls.append((enemy_name, size))
        return original_get_enemy_texture(enemy_name, size)

    scene_renderer.textures.get_special_texture = recording_get_special_texture
    scene_renderer.textures.get_enemy_texture = recording_get_enemy_texture

    tiles = (
        Portal(),
        Boulder(read=False),
        Boulder(read=True),
        DeadBody(read=False),
        DeadBody(read=True),
        RelicRoom(read=False),
        RelicRoom(read=True),
        GoldenChaliceRoom(read=False),
        GoldenChaliceRoom(read=True),
        UnobtainiumRoom(visited=False),
        SecretShop(),
        WarpPoint(),
        BossRoom(enemy=DummyEnemy("Minotaur")),
    )

    for tile in tiles:
        scene_renderer._render_special_tile(tile, rect, darkness=0.0, depth=1)

    assert ("portal", None) in special_calls
    assert ("boulder_sword", 112) in special_calls
    assert ("boulder", 112) in special_calls
    assert ("dead_body", 120) in special_calls
    assert ("burial_site", 120) in special_calls
    assert ("triangulus_altar", 96) in special_calls
    assert ("empty_altar", 96) in special_calls
    assert ("golden_chalice_altar", 96) in special_calls
    assert ("empty_golden_chalice_altar", 96) in special_calls
    assert ("unobtainium", 72) in special_calls
    assert ("secret_shop", None) in special_calls
    assert ("teleporter", 172) in special_calls
    assert ("Minotaur", 80) in enemy_calls

    pygame.quit()


def test_scene_renderer_renders_defeated_boss_replacement_visual():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    rect = pygame.Rect(120, 120, 160, 160)

    special_calls = []
    enemy_calls = []
    original_get_special_texture = scene_renderer.textures.get_special_texture
    original_get_enemy_texture = scene_renderer.textures.get_enemy_texture

    def recording_get_special_texture(texture_key, size=None):
        special_calls.append((texture_key, size))
        return original_get_special_texture(texture_key, size)

    def recording_get_enemy_texture(enemy_name, size=None):
        enemy_calls.append((enemy_name, size))
        return original_get_enemy_texture(enemy_name, size)

    scene_renderer.textures.get_special_texture = recording_get_special_texture
    scene_renderer.textures.get_enemy_texture = recording_get_enemy_texture

    before = pygame.image.tostring(screen, "RGBA")
    scene_renderer._render_special_tile(
        BossRoom(enemy=DummyEnemy("Minotaur"), defeated=True),
        rect,
        darkness=0.0,
        depth=1,
    )
    after = pygame.image.tostring(screen, "RGBA")

    assert ("burial_site", 112) in special_calls
    assert enemy_calls == []
    assert before != after

    pygame.quit()


def test_scene_renderer_renders_active_warp_point_with_active_sprite():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    scene_renderer.player_char = DummyPlayer(warp_point=True)
    rect = pygame.Rect(120, 120, 160, 160)

    before = pygame.image.tostring(screen, "RGBA")
    scene_renderer._render_special_tile(WarpPoint(), rect, darkness=0.0, depth=1)
    after = pygame.image.tostring(screen, "RGBA")

    assert before != after

    pygame.quit()


def test_scene_renderer_centers_warp_point_effects_on_sprite():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())

    rect = pygame.Rect(200, 300, 180, 96)
    effect_rect = scene_renderer._get_warp_point_effect_rect(rect)

    assert effect_rect.centerx == rect.centerx
    assert effect_rect.centery < rect.bottom
    assert effect_rect.centery > rect.y
    assert effect_rect.width > round(rect.width * 0.35)

    pygame.quit()


def test_scene_renderer_scales_warp_point_down_with_distance():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    scene_renderer.player_char = DummyPlayer(warp_point=True)
    rect = pygame.Rect(120, 120, 160, 160)

    special_calls = []
    original_get_special_texture = scene_renderer.textures.get_special_texture

    def recording_get_special_texture(texture_key, size=None):
        special_calls.append((texture_key, size))
        return original_get_special_texture(texture_key, size)

    scene_renderer.textures.get_special_texture = recording_get_special_texture

    scene_renderer._render_special_tile(WarpPoint(), rect, darkness=0.0, depth=1)
    scene_renderer._render_special_tile(WarpPoint(), rect, darkness=0.0, depth=2)

    teleporter_sizes = [size for texture_key, size in special_calls if texture_key == "teleporter"]
    assert teleporter_sizes[0] > teleporter_sizes[1]

    pygame.quit()


def test_scene_renderer_renders_current_tile_warp_point_on_front_floor_band():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    scene_renderer.player_char = DummyPlayer(location_z=1, warp_point=True)
    world = {
        (0, 0, 1): WarpPoint(),
        (1, 0, 1): OpenTile(),
        (2, 0, 1): OpenTile(),
        (0, -1, 1): OpenTile(),
        (0, 1, 1): OpenTile(),
        (1, -1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (2, -1, 1): OpenTile(),
        (2, 1, 1): OpenTile(),
    }

    teleporter_rect = None
    original_render_center_floor_warp_point = scene_renderer._render_center_floor_warp_point

    def recording_render_center_floor_warp_point(quad, darkness, depth):
        nonlocal teleporter_rect
        sprite = scene_renderer._trim_transparent_sprite(scene_renderer.textures.get_special_texture("teleporter"))
        teleporter_rect = scene_renderer._get_center_floor_warp_point_rect(quad, sprite)
        return original_render_center_floor_warp_point(quad, darkness, depth)

    scene_renderer._render_center_floor_warp_point = recording_render_center_floor_warp_point

    try:
        player = DummyPlayer(location_z=1, warp_point=True)
        scene_renderer.render(player, world)
    finally:
        scene_renderer._render_center_floor_warp_point = original_render_center_floor_warp_point

    assert teleporter_rect is not None

    view_w, view_h = scene_renderer._get_viewport_size()
    zone = build_zone_geometry(
        build_depth_rect(view_w, view_h, 1),
        build_next_depth_rect(build_depth_rect(view_w, view_h, 1)),
        depth=1,
    )
    slot_quad = scene_renderer._get_center_floor_slot_quad(zone, depth=1, slot_suffix="x0")
    sprite = scene_renderer._trim_transparent_sprite(scene_renderer.textures.get_special_texture("teleporter"))
    expected_rect = scene_renderer._get_center_floor_warp_point_rect(slot_quad, sprite)
    assert teleporter_rect == expected_rect

    slot_bounds = slot_quad.bounding_rect()
    assert teleporter_rect.width == round(slot_bounds.w * 0.66)
    assert teleporter_rect.height == round(slot_bounds.h)
    assert teleporter_rect.centerx == round(slot_bounds.x + (slot_bounds.w / 2.0))
    assert teleporter_rect.bottom == round(slot_bounds.y + slot_bounds.h)

    pygame.quit()


def test_scene_renderer_does_not_route_warp_point_to_floor_texture_override():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): WarpPoint(),
        (2, 0, 1): OpenTile(),
        (0, -1, 1): OpenTile(),
        (0, 1, 1): OpenTile(),
        (1, -1, 1): OpenTile(),
        (1, 1, 1): OpenTile(),
        (2, -1, 1): OpenTile(),
        (2, 1, 1): OpenTile(),
    }

    commands, _ = _build_scene_commands(scene_renderer, player, world)

    assert not any(command.texture_key == "floor_teleporter" for command in commands)

    pygame.quit()


def test_scene_renderer_renders_secret_shop_overlay_in_center_view():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): SecretShop(),
        (0, -1, 1): OpenTile(),
        (0, 1, 1): OpenTile(),
    }

    calls = []
    original_get_special_texture = scene_renderer.textures.get_special_texture

    def recording_get_special_texture(texture_key, size=None):
        calls.append((texture_key, size))
        return original_get_special_texture(texture_key, size)

    scene_renderer.textures.get_special_texture = recording_get_special_texture

    scene_renderer.render(player, world)

    assert ("secret_shop", None) in calls

    pygame.quit()


def test_scene_renderer_treats_secret_shop_like_center_floor_overlay_for_structure():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): SecretShop(),
        (2, 0, 1): WallTile(),
        (0, -1, 1): OpenTile(),
        (0, 1, 1): WallTile(),
        (1, -1, 1): OpenTile(),
        (1, 1, 1): WallTile(),
        (2, -1, 1): OpenTile(),
        (2, 1, 1): WallTile(),
    }

    commands, _ = _build_scene_commands(scene_renderer, player, world)

    assert not any(command.panel_id == "d1:back_wall" for command in commands)
    assert any(command.panel_id == "d2:back_wall" for command in commands)

    rendered_tiles = []
    original_render_special_tile = scene_renderer._render_special_tile

    def recording_render_special_tile(tile, rect, darkness, depth, side=None, lateral_view=False):
        rendered_tiles.append((type(tile).__name__ if tile else None, depth, side, lateral_view))
        return original_render_special_tile(
            tile,
            rect,
            darkness,
            depth,
            side=side,
            lateral_view=lateral_view,
        )

    scene_renderer._render_special_tile = recording_render_special_tile

    scene_renderer.render(player, world)

    assert ("SecretShop", 1, None, False) in rendered_tiles

    pygame.quit()


def test_scene_renderer_routes_side_ladder_ceiling_through_center_ceiling_slot_override():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): WallTile(),
        (0, -1, 1): WallTile(),
        (1, -1, 1): WallTile(),
        (0, 1, 1): OpenTile(),
        (1, 1, 1): LadderUp(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d2:center_ceiling_slot3", "ceiling_pit") in calls
    assert ("d2:center_ceiling", "ceiling") not in calls
    assert not any(panel_id == "d1:right_opening_special_ceiling" for panel_id, _ in calls)
    assert scene_renderer.textures.get_surface_slot_overrides() == {
        "ceiling:visible:d2:xp1": "ceiling_pit",
    }

    pygame.quit()


def test_scene_renderer_routes_side_wall_through_wall_slot_commands():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    scene_renderer.textures.set_wall_slot_override("wall:visible:d1:right:right:near", "floor_funhouse")
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (0, -1, 1): OpenTile(),
        (1, -1, 1): OpenTile(),
        (0, 1, 1): WallTile(),
        (1, 1, 1): WallTile(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d1:right_wall_slot0", "floor_funhouse") in calls
    assert ("d1:right_wall_slot1", "wall") in calls
    assert ("d1:right_wall", "wall") not in calls

    pygame.quit()


def test_scene_renderer_renders_adjacent_side_wall_door_through_wall_slots():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (0, -1, 1): OpenTile(),
        (1, -1, 1): OpenTile(),
        (0, 1, 1): LockedDoor(),
        (1, 1, 1): WallTile(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d1:right_wall", "door_closed") in calls
    assert ("d1:right_wall_slot0", "door_closed") not in calls
    assert ("d1:right_wall_slot1", "door_closed") not in calls

    pygame.quit()


def test_scene_renderer_open_adjacent_side_wall_door_keeps_side_blocker_visible():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    presenter = DummyPresenter(width=640, height=480, screen=screen)
    scene_renderer = SceneRenderer(presenter, TextureLibrary())
    player = DummyPlayer()
    world = {
        (0, 0, 1): OpenTile(),
        (1, 0, 1): OpenTile(),
        (0, -1, 1): OpenTile(),
        (1, -1, 1): OpenTile(),
        (0, 1, 1): OpenDoor(),
        (1, 1, 1): WallTile(),
    }

    calls = []
    original_get_projected_surface = scene_renderer.textures.get_projected_surface

    def recording_get_projected_surface(panel_id, texture_key, quad, darkness, view_size):
        calls.append((panel_id, texture_key))
        return original_get_projected_surface(panel_id, texture_key, quad, darkness, view_size)

    scene_renderer.textures.get_projected_surface = recording_get_projected_surface

    scene_renderer.render(player, world)

    assert ("d1:right_wall", "door_open") in calls
    assert ("d1:right_blocker", "wall") in calls

    pygame.quit()
