from __future__ import annotations

import math
import os
from dataclasses import dataclass

import pygame

from src.core import map_tiles

from .assets import TextureLibrary
from .geometry import Quad, build_depth_rect, build_next_depth_rect, build_zone_geometry
from .projector import project_texture_to_quad
from .scene import extract_visible_scene, is_wall


@dataclass(frozen=True)
class RenderCommand:
    depth: int
    order: int
    panel_id: str
    texture_key: str
    quad: Quad
    darkness: float


class SceneRenderer:
    """Render the dungeon scene from explicit quads and cached panel projections."""

    def __init__(self, presenter, textures: TextureLibrary, debug_geometry: bool = False):
        self.presenter = presenter
        self.textures = textures
        self.debug_geometry = debug_geometry or os.getenv("DUNGEON_RENDERER_DEBUG_GEOMETRY") == "1"
        self.disable_darkness = os.getenv("DUNGEON_RENDERER_DISABLE_DARKNESS") == "1"
        self.debug_scene = os.getenv("DUNGEON_RENDERER_DEBUG_SCENE") == "1"
        self.debug_commands = os.getenv("DUNGEON_RENDERER_DEBUG_COMMANDS") == "1"
        self.debug_surface_slots = os.getenv("DUNGEON_RENDERER_DEBUG_SURFACE_SLOTS") == "1"
        self._last_debug_snapshot: str | None = None

    @property
    def screen(self) -> pygame.Surface:
        return self.presenter.screen

    def _get_viewport_size(self) -> tuple[int, int]:
        screen_w, screen_h = self.screen.get_size()
        return int(screen_w * 0.65), screen_h

    def render(self, player_char, world_dict) -> None:
        self.textures.ensure_loaded()
        self.player_char = player_char
        screen = self.screen
        view_w, view_h = self._get_viewport_size()
        screen.fill((0, 0, 0), pygame.Rect(0, 0, view_w, view_h))

        scene = extract_visible_scene(player_char, world_dict, max_depth=3)
        self._configure_surface_slot_overrides(scene)
        zones = {
            depth: build_zone_geometry(
                build_depth_rect(view_w, view_h, depth),
                build_next_depth_rect(build_depth_rect(view_w, view_h, depth)),
                depth=depth,
            )
            for depth in (1, 2, 3)
        }

        commands = self._build_render_commands(scene, zones)
        self._emit_debug_snapshot(scene, commands)
        for command in sorted(commands, key=lambda item: (-item.depth, item.order)):
            projected = self.textures.get_projected_surface(
                panel_id=command.panel_id,
                texture_key=command.texture_key,
                quad=command.quad,
                darkness=command.darkness,
                view_size=(view_w, view_h),
            )
            screen.blit(projected.surface, projected.topleft)

        self._render_special_tiles(scene, zones)

        if self.debug_geometry:
            self._render_debug_overlay(zones, scene)

    def _configure_surface_slot_overrides(self, scene) -> None:
        desired_overrides: dict[str, str] = {}
        max_visible_depth = scene.depths[-1].depth if scene.depths else 0
        last_floor_theme_tile = self._find_initial_floor_theme_tile(scene)

        for visible_depth in scene.depths:
            center_floor_key = self._get_center_floor_texture_key(
                depth=visible_depth.depth,
                source_tile=visible_depth.source_tile,
                fallback_tile=last_floor_theme_tile,
            )
            center_ceiling_key = self.textures.get_ceiling_key(visible_depth.source_tile)
            self._collect_visible_floor_slot_overrides(
                visible_depth=visible_depth,
                base_texture_key=center_floor_key,
                overrides=desired_overrides,
            )
            self._collect_center_wall_slot_override(
                depth=visible_depth.depth,
                center_tile=visible_depth.center,
                overrides=desired_overrides,
            )
            side_doors_hidden_by_center_wall = self._should_hide_side_doors_behind_center_wall(visible_depth)

            self._collect_visible_ceiling_slot_overrides(
                visible_depth=visible_depth,
                base_texture_key=center_ceiling_key,
                overrides=desired_overrides,
            )
            if not side_doors_hidden_by_center_wall:
                self._collect_side_wall_slot_override(
                    depth=visible_depth.depth,
                    side="left",
                    opening_tile=visible_depth.left,
                    forward_tile=visible_depth.left_forward,
                    overrides=desired_overrides,
                )
                self._collect_side_wall_slot_override(
                    depth=visible_depth.depth,
                    side="right",
                    opening_tile=visible_depth.right,
                    forward_tile=visible_depth.right_forward,
                    overrides=desired_overrides,
                )

            if self._should_advance_floor_theme(visible_depth.depth, visible_depth.source_tile):
                last_floor_theme_tile = visible_depth.source_tile

        self.textures.set_scene_surface_slot_overrides(desired_overrides)

    def _collect_center_wall_slot_override(
        self,
        depth: int,
        center_tile,
        overrides: dict[str, str],
    ) -> None:
        if not self._is_door_tile(center_tile):
            return

        panel_id = f"d{depth}:back_wall"
        slot_ids = self.textures.describe_wall_slot_ids(panel_id)
        if not slot_ids:
            return

        overrides[slot_ids[0]] = "door_open" if getattr(center_tile, "open", False) else "door_closed"

    def _collect_visible_floor_slot_overrides(
        self,
        visible_depth,
        base_texture_key: str,
        overrides: dict[str, str],
    ) -> None:
        panel_id = f"d{visible_depth.depth}:center_floor"
        slot_ids = self.textures.describe_floor_slot_ids(panel_id)
        row_tiles = self._get_visible_floor_row_tiles(visible_depth)

        for slot_id, tile in zip(slot_ids, row_tiles):
            texture_key = self._get_visible_floor_texture_key(
                tile=tile,
                base_texture_key=base_texture_key,
            )
            if texture_key != base_texture_key:
                overrides[slot_id] = texture_key

    def _get_visible_floor_row_tiles(self, visible_depth) -> tuple[object | None, ...]:
        depth = visible_depth.depth
        if depth == 1:
            return (
                visible_depth.left,
                visible_depth.source_tile,
                visible_depth.right,
            )
        if depth == 2:
            return (
                visible_depth.left_branch,
                visible_depth.left,
                visible_depth.source_tile,
                visible_depth.right,
                visible_depth.right_branch,
            )
        return (
            None,
            None,
            visible_depth.left_branch,
            visible_depth.left,
            visible_depth.source_tile,
            visible_depth.right,
            visible_depth.right_branch,
            None,
            None,
        )

    def _get_visible_floor_texture_key(self, tile, base_texture_key: str) -> str:
        if tile is None or is_wall(tile) or self.textures._is_floor_overlay_tile(tile):
            return base_texture_key
        return self.textures.get_floor_key(tile)

    def _collect_visible_ceiling_slot_overrides(
        self,
        visible_depth,
        base_texture_key: str,
        overrides: dict[str, str],
    ) -> None:
        panel_id = f"d{visible_depth.depth}:center_ceiling"
        slot_ids = self.textures.describe_ceiling_slot_ids(panel_id)
        row_tiles = self._get_visible_ceiling_row_tiles(visible_depth)

        for slot_id, tile in zip(slot_ids, row_tiles):
            texture_key = self._get_visible_ceiling_texture_key(
                tile=tile,
                base_texture_key=base_texture_key,
            )
            if texture_key != base_texture_key:
                overrides[slot_id] = texture_key

    def _get_visible_ceiling_row_tiles(self, visible_depth) -> tuple[object | None, ...]:
        depth = visible_depth.depth
        if depth == 1:
            return (
                visible_depth.left,
                visible_depth.source_tile,
                visible_depth.right,
            )
        if depth == 2:
            return (
                visible_depth.left_branch,
                visible_depth.left,
                visible_depth.source_tile,
                visible_depth.right,
                visible_depth.right_branch,
            )
        return (
            None,
            None,
            visible_depth.left_branch,
            visible_depth.left,
            visible_depth.source_tile,
            visible_depth.right,
            visible_depth.right_branch,
            None,
            None,
        )

    def _get_visible_ceiling_texture_key(self, tile, base_texture_key: str) -> str:
        if tile is None or is_wall(tile) or self.textures._is_floor_overlay_tile(tile):
            return base_texture_key
        return self.textures.get_ceiling_key(tile)

    def _collect_side_wall_slot_override(
        self,
        depth: int,
        side: str,
        opening_tile,
        forward_tile,
        overrides: dict[str, str],
    ) -> None:
        if self._opening_tile_blocks_view(opening_tile) or forward_tile is None or not self._is_door_tile(forward_tile):
            return

        panel_id = f"d{depth}:{side}_blocker"
        slot_ids = self.textures.describe_wall_slot_ids(panel_id)
        if not slot_ids:
            return

        overrides[slot_ids[0]] = "door_open" if getattr(forward_tile, "open", False) else "door_closed"
    def _build_render_commands(self, scene, zones) -> list[RenderCommand]:
        commands: list[RenderCommand] = []
        last_floor_theme_tile = self._find_initial_floor_theme_tile(scene)

        for visible_depth in scene.depths:
            depth = visible_depth.depth
            zone = zones[depth]
            darkness = self._get_layer_darkness(depth)

            center_floor_key = self._get_center_floor_texture_key(
                depth=depth,
                source_tile=visible_depth.source_tile,
                fallback_tile=last_floor_theme_tile,
            )
            center_ceiling_key = self.textures.get_ceiling_key(visible_depth.source_tile)

            if self._should_advance_floor_theme(depth, visible_depth.source_tile):
                last_floor_theme_tile = visible_depth.source_tile

            commands.extend(
                self._build_center_ceiling_commands(
                    depth=depth,
                    zone=zone,
                    texture_key=center_ceiling_key,
                    darkness=darkness,
                )
            )
            commands.extend(
                self._build_center_floor_commands(
                    depth=depth,
                    zone=zone,
                    texture_key=center_floor_key,
                    darkness=darkness,
                )
            )

            if is_wall(visible_depth.center):
                commands.extend(
                    self._build_wall_panel_commands(
                        depth=depth,
                        order=2,
                        panel_id=f"d{depth}:back_wall",
                        texture_key="wall",
                        quad=Quad.from_rect(zone.back_wall_rect),
                        darkness=darkness,
                    )
                )
                commands.extend(
                    self._build_center_wall_endcap_commands(
                        depth=depth,
                        zone=zone,
                        left_tile=visible_depth.left,
                        right_tile=visible_depth.right,
                        left_forward_tile=visible_depth.left_forward,
                        right_forward_tile=visible_depth.right_forward,
                        left_outer_tile=visible_depth.left_forward_outer,
                        right_outer_tile=visible_depth.right_forward_outer,
                        darkness=darkness,
                    )
                )

            commands.extend(
                self._build_side_commands(
                    depth,
                    zone,
                    "left",
                    visible_depth.left,
                    visible_depth.left_branch,
                    visible_depth.left_forward,
                    darkness,
                    outer_wall_tile=visible_depth.left_forward_outer,
                    next_zone=zones.get(depth + 1),
                    center_blocked=is_wall(visible_depth.center),
                )
            )
            commands.extend(
                self._build_side_special_surface_commands(
                    visible_depth=visible_depth,
                    zone=zone,
                    next_zone=zones.get(depth + 1),
                    side="left",
                    darkness=darkness,
                )
            )
            commands.extend(
                self._build_side_commands(
                    depth,
                    zone,
                    "right",
                    visible_depth.right,
                    visible_depth.right_branch,
                    visible_depth.right_forward,
                    darkness,
                    outer_wall_tile=visible_depth.right_forward_outer,
                    next_zone=zones.get(depth + 1),
                    center_blocked=is_wall(visible_depth.center),
                )
            )
            commands.extend(
                self._build_side_special_surface_commands(
                    visible_depth=visible_depth,
                    zone=zone,
                    next_zone=zones.get(depth + 1),
                    side="right",
                    darkness=darkness,
                )
            )

        return commands

    def _get_center_floor_texture_key(self, depth: int, source_tile, fallback_tile) -> str:
        if self._is_localized_current_floor_tile(depth, source_tile):
            if fallback_tile is not None:
                return self.textures.get_floor_key(fallback_tile)
            return "floor"
        return self.textures.get_floor_key(source_tile, fallback_tile=fallback_tile)

    def _should_advance_floor_theme(self, depth: int, source_tile) -> bool:
        if source_tile is None:
            return False
        if self.textures._is_floor_overlay_tile(source_tile):
            return False
        if self._is_localized_current_floor_tile(depth, source_tile):
            return False
        return True

    @staticmethod
    def _is_localized_current_floor_tile(depth: int, tile) -> bool:
        return depth == 1 and "UndergroundSpring" in type(tile).__name__

    def _build_center_floor_commands(self, depth: int, zone, texture_key: str, darkness: float) -> list[RenderCommand]:
        return self._build_center_surface_commands(
            depth=depth,
            panel_id=f"d{depth}:center_floor",
            texture_key=texture_key,
            quad=zone.center_floor,
            darkness=darkness,
            order=1,
            family="floor",
        )

    def _build_center_ceiling_commands(self, depth: int, zone, texture_key: str, darkness: float) -> list[RenderCommand]:
        return self._build_center_surface_commands(
            depth=depth,
            panel_id=f"d{depth}:center_ceiling",
            texture_key=texture_key,
            quad=zone.center_ceiling,
            darkness=darkness,
            order=0,
            family="ceiling",
        )

    def _build_center_surface_commands(
        self,
        depth: int,
        panel_id: str,
        texture_key: str,
        quad: Quad,
        darkness: float,
        order: int,
        family: str,
    ) -> list[RenderCommand]:
        if family == "floor":
            slot_ids = self.textures.describe_floor_slot_ids(panel_id)
            has_override = self.textures.has_floor_slot_override(panel_id)
        else:
            slot_ids = self.textures.describe_ceiling_slot_ids(panel_id)
            has_override = self.textures.has_ceiling_slot_override(panel_id)

        slot_spans = self.textures.describe_surface_slot_spans(panel_id, texture_key=texture_key)
        has_overscan_slots = any(start_ratio < 0.0 or end_ratio > 1.0 for start_ratio, end_ratio in slot_spans)
        should_split_slots = bool(slot_ids) and (has_override or has_overscan_slots)

        if not should_split_slots:
            return [
                RenderCommand(
                    depth=depth,
                    order=order,
                    panel_id=panel_id,
                    texture_key=texture_key,
                    quad=quad,
                    darkness=darkness,
                )
            ]

        overrides = self.textures.get_surface_slot_overrides()
        commands: list[RenderCommand] = []
        for index, (slot_id, (start_ratio, end_ratio)) in enumerate(zip(slot_ids, slot_spans)):
            slot_texture_key = overrides.get(slot_id, texture_key)
            slot_quad = self._slice_quad_horizontal_region(
                quad,
                start_ratio,
                end_ratio,
            )
            commands.append(
                RenderCommand(
                    depth=depth,
                    order=order,
                    panel_id=f"d{depth}:center_{family}_slot{index}",
                    texture_key=slot_texture_key,
                    quad=slot_quad,
                    darkness=darkness,
                )
            )
        return commands

    def _build_wall_panel_commands(
        self,
        depth: int,
        order: int,
        panel_id: str,
        texture_key: str,
        quad: Quad,
        darkness: float,
    ) -> list[RenderCommand]:
        if not self.textures.has_wall_slot_override(panel_id):
            return [
                RenderCommand(
                    depth=depth,
                    order=order,
                    panel_id=panel_id,
                    texture_key=texture_key,
                    quad=quad,
                    darkness=darkness,
                )
            ]

        slot_ids = self.textures.describe_wall_slot_ids(panel_id)
        if not slot_ids:
            return [
                RenderCommand(
                    depth=depth,
                    order=order,
                    panel_id=panel_id,
                    texture_key=texture_key,
                    quad=quad,
                    darkness=darkness,
                )
            ]

        overrides = self.textures.get_surface_slot_overrides()
        slot_count = len(slot_ids)
        commands: list[RenderCommand] = []
        for index, slot_id in enumerate(slot_ids):
            slot_texture_key = overrides.get(slot_id, texture_key)
            if slot_count == 1:
                slot_quad = quad
            else:
                slot_quad = self._slice_quad_horizontal_region(
                    quad,
                    index / slot_count,
                    (index + 1) / slot_count,
                )
            commands.append(
                RenderCommand(
                    depth=depth,
                    order=order,
                    panel_id=f"{panel_id}_slot{index}",
                    texture_key=slot_texture_key,
                    quad=slot_quad,
                    darkness=darkness,
                )
            )
        return commands

    def _build_side_special_surface_commands(
        self,
        visible_depth,
        zone,
        next_zone,
        side: str,
        darkness: float,
    ) -> list[RenderCommand]:
        opening_tile = visible_depth.left if side == "left" else visible_depth.right
        forward_tile = visible_depth.left_forward if side == "left" else visible_depth.right_forward

        if next_zone is None:
            return []

        if self._opening_tile_blocks_view(opening_tile) or forward_tile is None or is_wall(forward_tile):
            return []

        commands: list[RenderCommand] = []
        floor_key = self.textures.get_floor_key(forward_tile)
        if floor_key != "floor" and "LadderDown" not in type(forward_tile).__name__:
            floor_quad, _, surface_depth = self._get_side_special_surface_geometry(
                zone,
                next_zone,
                side=side,
                depth=visible_depth.depth,
            )
            commands.append(
                RenderCommand(
                    depth=surface_depth,
                    order=1,
                    panel_id=f"d{surface_depth}:{side}_corridor_outer_floor",
                    texture_key=floor_key,
                    quad=floor_quad,
                    darkness=darkness,
                )
            )

        ceiling_key = self.textures.get_ceiling_key(forward_tile)
        if ceiling_key != "ceiling" and "LadderUp" not in type(forward_tile).__name__:
            ceiling_quad, ceiling_depth, ceiling_panel_id = self._get_visible_side_special_ceiling_geometry(
                zone=zone,
                side=side,
                depth=visible_depth.depth,
                next_zone=next_zone,
            )
            commands.append(
                RenderCommand(
                    depth=ceiling_depth,
                    order=0,
                    panel_id=ceiling_panel_id,
                    texture_key=ceiling_key,
                    quad=ceiling_quad,
                    darkness=darkness,
                )
            )

        return commands

    @staticmethod
    def _build_center_wall_endcap_commands(
        depth: int,
        zone,
        left_tile,
        right_tile,
        left_forward_tile,
        right_forward_tile,
        left_outer_tile,
        right_outer_tile,
        darkness: float,
    ) -> list[RenderCommand]:
        commands: list[RenderCommand] = []
        commands.extend(
            SceneRenderer._build_side_back_wall_endcaps(
                depth=depth,
                side="left",
                side_tile=left_tile,
                forward_tile=left_forward_tile,
                outer_tile=left_outer_tile,
                blocker_rect=zone.left_side_blocker_rect,
                darkness=darkness,
            )
        )
        commands.extend(
            SceneRenderer._build_side_back_wall_endcaps(
                depth=depth,
                side="right",
                side_tile=right_tile,
                forward_tile=right_forward_tile,
                outer_tile=right_outer_tile,
                blocker_rect=zone.right_side_blocker_rect,
                darkness=darkness,
            )
        )

        return commands

    @staticmethod
    def _build_side_back_wall_endcaps(
        depth: int,
        side: str,
        side_tile,
        forward_tile,
        outer_tile,
        blocker_rect,
        darkness: float,
    ) -> list[RenderCommand]:
        if is_wall(side_tile) or not is_wall(forward_tile):
            return []

        if depth >= 3:
            endcap_count = 3
        else:
            endcap_count = 1 if is_wall(outer_tile) else 0

        if endcap_count <= 0:
            return []

        commands: list[RenderCommand] = []
        for index in range(endcap_count):
            if side == "left":
                rect = type(blocker_rect)(
                    blocker_rect.x - (blocker_rect.w * (index + 1)),
                    blocker_rect.y,
                    blocker_rect.w,
                    blocker_rect.h,
                )
            else:
                rect = type(blocker_rect)(
                    blocker_rect.x + (blocker_rect.w * (index + 1)),
                    blocker_rect.y,
                    blocker_rect.w,
                    blocker_rect.h,
                )

            panel_suffix = "" if index == 0 else str(index)
            commands.append(
                RenderCommand(
                    depth=depth,
                    order=2,
                    panel_id=f"d{depth}:{side}_back_wall_endcap{panel_suffix}",
                    texture_key="wall",
                    quad=Quad.from_rect(rect),
                    darkness=darkness,
                )
            )

        return commands

    def _find_initial_floor_theme_tile(self, scene) -> object | None:
        for visible_depth in scene.depths:
            for candidate in (
                visible_depth.source_tile,
                visible_depth.left,
                visible_depth.right,
                visible_depth.center,
                visible_depth.left_forward,
                visible_depth.right_forward,
            ):
                if candidate is None:
                    continue
                if self._is_localized_current_floor_tile(visible_depth.depth, candidate):
                    continue
                if is_wall(candidate):
                    continue
                if self.textures._is_floor_overlay_tile(candidate):
                    continue
                return candidate
        return None

    def _build_side_commands(
        self,
        depth: int,
        zone,
        side: str,
        side_tile,
        side_branch_tile,
        side_forward_tile,
        darkness: float,
        outer_wall_tile=None,
        next_zone=None,
        center_blocked: bool = False,
    ) -> list[RenderCommand]:
        if side == "left":
            wall_quad = zone.left_wall
            blocker_quad = Quad.from_rect(zone.left_side_blocker_rect)
            base_offset = float(zone.rect.w) * 0.25
            edge_offset = float(zone.rect.w) * 0.5
            continuation_depth = depth + 1 if next_zone is not None else depth
            continuation_quad = (
                self._push_outer_wall_quad(
                    next_zone.left_wall,
                    side="left",
                    base_offset=base_offset,
                    edge_offset=edge_offset,
                )
                if next_zone is not None
                else None
            )
            bridge_quad = (
                self._push_outer_bridge_quad(
                    Quad.from_rect(zone.left_side_blocker_rect),
                    side="left",
                    offset=edge_offset,
                )
                if next_zone is not None
                else None
            )
        else:
            wall_quad = zone.right_wall
            blocker_quad = Quad.from_rect(zone.right_side_blocker_rect)
            base_offset = float(zone.rect.w) * 0.25
            edge_offset = float(zone.rect.w) * 0.5
            continuation_depth = depth + 1 if next_zone is not None else depth
            continuation_quad = (
                self._push_outer_wall_quad(
                    next_zone.right_wall,
                    side="right",
                    base_offset=base_offset,
                    edge_offset=edge_offset,
                )
                if next_zone is not None
                else None
            )
            bridge_quad = (
                self._push_outer_bridge_quad(
                    Quad.from_rect(zone.right_side_blocker_rect),
                    side="right",
                    offset=edge_offset,
                )
                if next_zone is not None
                else None
            )

        commands: list[RenderCommand] = []
        side_tile_is_open_door = self._is_open_door_tile(side_tile)

        if is_wall(side_tile) and not side_tile_is_open_door:
            if self._is_door_tile(side_tile):
                commands.append(
                    RenderCommand(
                        depth=depth,
                        order=3,
                        panel_id=f"d{depth}:{side}_wall",
                        texture_key="door_open" if getattr(side_tile, "open", False) else "door_closed",
                        quad=wall_quad,
                        darkness=darkness,
                    )
                )
                return commands

            commands.extend(
                self._build_wall_panel_commands(
                    depth=depth,
                    order=3,
                    panel_id=f"d{depth}:{side}_wall",
                    texture_key="wall",
                    quad=wall_quad,
                    darkness=darkness,
                )
            )
            return commands

        if side_tile_is_open_door:
            commands.append(
                RenderCommand(
                    depth=depth,
                    order=4,
                    panel_id=f"d{depth}:{side}_wall",
                    texture_key="door_open",
                    quad=wall_quad,
                    darkness=darkness,
                )
            )

        if is_wall(side_forward_tile):
            commands.extend(
                self._build_wall_panel_commands(
                    depth=depth,
                    order=2,
                    panel_id=f"d{depth}:{side}_blocker",
                    texture_key="wall",
                    quad=blocker_quad,
                    darkness=darkness,
                )
            )
            if not center_blocked:
                commands.extend(
                    self._build_side_back_wall_endcaps(
                        depth=depth,
                        side=side,
                        side_tile=side_tile,
                        forward_tile=side_forward_tile,
                        outer_tile=outer_wall_tile,
                        blocker_rect=blocker_quad.bounding_rect(),
                        darkness=darkness,
                    )
                )
        elif is_wall(outer_wall_tile) and continuation_quad is not None:
            outer_texture_key = "wall"
            if self._is_door_tile(outer_wall_tile):
                outer_texture_key = "door_open" if getattr(outer_wall_tile, "open", False) else "door_closed"
            commands.extend(
                self._build_wall_panel_commands(
                    depth=continuation_depth,
                    order=3,
                    panel_id=f"d{continuation_depth}:{side}_corridor_outer_wall",
                    texture_key=outer_texture_key,
                    quad=continuation_quad,
                    darkness=darkness,
                )
            )
            if bridge_quad is not None and not is_wall(side_branch_tile):
                commands.append(
                    RenderCommand(
                        depth=depth,
                        order=3,
                        panel_id=f"d{depth}:{side}_corridor_outer_bridge",
                        texture_key="wall",
                        quad=bridge_quad,
                        darkness=darkness,
                    )
                )

        return commands

    @staticmethod
    def _push_outer_wall_quad(quad: Quad, side: str, base_offset: float, edge_offset: float) -> Quad:
        p0, p1, p2, p3 = quad.points

        if side == "left":
            # Left-wall quad order:
            # p0 outer-top, p1 inner-top, p2 inner-bottom, p3 outer-bottom
            return Quad(
                (
                    (p0[0] - edge_offset, p0[1]),
                    (p1[0] - base_offset, p1[1]),
                    (p2[0] - base_offset, p2[1]),
                    (p3[0] - edge_offset, p3[1]),
                )
            )

        # Right-wall quad order:
        # p0 inner-top, p1 outer-top, p2 outer-bottom, p3 inner-bottom
        return Quad(
            (
                (p0[0] + base_offset, p0[1]),
                (p1[0] + edge_offset, p1[1]),
                (p2[0] + edge_offset, p2[1]),
                (p3[0] + base_offset, p3[1]),
            )
        )

    @staticmethod
    def _push_outer_ceiling_quad(quad: Quad, side: str, base_offset: float, edge_offset: float) -> Quad:
        p0, p1, p2, p3 = quad.points
        outer_cover = base_offset * 0.04
        inner_cover = base_offset * 0.12
        if side == "left":
            return Quad(
                (
                    (p0[0] - edge_offset + outer_cover, p0[1]),
                    (p1[0] - base_offset + inner_cover, p1[1]),
                    (p2[0] - base_offset + inner_cover, p2[1]),
                    (p3[0] - edge_offset + outer_cover, p3[1]),
                )
            )
        return Quad(
            (
                (p0[0] + base_offset - inner_cover, p0[1]),
                (p1[0] + edge_offset - outer_cover, p1[1]),
                (p2[0] + edge_offset - outer_cover, p2[1]),
                (p3[0] + base_offset - inner_cover, p3[1]),
            )
        )

    @staticmethod
    def _push_outer_floor_quad(quad: Quad, side: str, base_offset: float, edge_offset: float) -> Quad:
        p0, p1, p2, p3 = quad.points
        outer_cover = base_offset * 0.04
        inner_cover = base_offset * 0.12
        if side == "left":
            return Quad(
                (
                    (p0[0] - edge_offset + outer_cover, p0[1]),
                    (p1[0] - base_offset + inner_cover, p1[1]),
                    (p2[0] - base_offset + inner_cover, p2[1]),
                    (p3[0] - edge_offset + outer_cover, p3[1]),
                )
            )
        return Quad(
            (
                (p0[0] + base_offset - inner_cover, p0[1]),
                (p1[0] + edge_offset - outer_cover, p1[1]),
                (p2[0] + edge_offset - outer_cover, p2[1]),
                (p3[0] + base_offset - inner_cover, p3[1]),
            )
        )

    @staticmethod
    def _slice_outer_corridor_quad(quad: Quad, side: str, outer_ratio: float = 0.5) -> Quad:
        outer_ratio = max(0.0, min(1.0, outer_ratio))
        p0, p1, p2, p3 = quad.points

        def lerp(a: tuple[float, float], b: tuple[float, float], t: float) -> tuple[float, float]:
            return (a[0] + ((b[0] - a[0]) * t), a[1] + ((b[1] - a[1]) * t))

        if side == "left":
            inner_front = lerp(p1, p0, outer_ratio)
            inner_back = lerp(p2, p3, outer_ratio)
            return Quad((p0, inner_front, inner_back, p3))

        inner_front = lerp(p0, p1, outer_ratio)
        inner_back = lerp(p3, p2, outer_ratio)
        return Quad((inner_front, p1, p2, inner_back))

    @staticmethod
    def _slice_quad_horizontal_region(quad: Quad, start_ratio: float, end_ratio: float) -> Quad:
        end_ratio = max(start_ratio, end_ratio)
        p0, p1, p2, p3 = quad.points

        def lerp(a: tuple[float, float], b: tuple[float, float], t: float) -> tuple[float, float]:
            return (a[0] + ((b[0] - a[0]) * t), a[1] + ((b[1] - a[1]) * t))

        return Quad(
            (
                lerp(p0, p1, start_ratio),
                lerp(p0, p1, end_ratio),
                lerp(p3, p2, end_ratio),
                lerp(p3, p2, start_ratio),
            )
        )

    @staticmethod
    def _slice_quad_region(
        quad: Quad,
        u_start: float,
        u_end: float,
        v_start: float,
        v_end: float,
    ) -> Quad:
        u_start = max(0.0, min(1.0, u_start))
        u_end = max(u_start, min(1.0, u_end))
        v_start = max(0.0, min(1.0, v_start))
        v_end = max(v_start, min(1.0, v_end))
        p0, p1, p2, p3 = quad.points

        def lerp(a: tuple[float, float], b: tuple[float, float], t: float) -> tuple[float, float]:
            return (a[0] + ((b[0] - a[0]) * t), a[1] + ((b[1] - a[1]) * t))

        left_start = lerp(p0, p3, v_start)
        right_start = lerp(p1, p2, v_start)
        left_end = lerp(p0, p3, v_end)
        right_end = lerp(p1, p2, v_end)

        return Quad(
            (
                lerp(left_start, right_start, u_start),
                lerp(left_start, right_start, u_end),
                lerp(left_end, right_end, u_end),
                lerp(left_end, right_end, u_start),
            )
        )

    @staticmethod
    def _push_outer_bridge_quad(quad: Quad, side: str, offset: float) -> Quad:
        direction = -offset if side == "left" else offset
        return Quad(tuple((x + direction, y) for x, y in quad.points))

    def _render_debug_overlay(self, zones, scene) -> None:
        colors = {
            "center_floor": (0, 128, 255),
            "side_floor": (0, 255, 128),
            "ceiling": (255, 128, 0),
            "wall": (255, 64, 64),
            "back": (255, 255, 0),
        }

        for visible_depth in scene.depths:
            zone = zones[visible_depth.depth]
            pygame.draw.polygon(self.screen, colors["center_floor"], zone.center_floor.as_int_points(), 1)
            pygame.draw.polygon(self.screen, colors["ceiling"], zone.center_ceiling.as_int_points(), 1)
            self._draw_surface_slot_overlay(
                panel_id=f"d{visible_depth.depth}:center_floor",
                quad=zone.center_floor,
                color=(0, 180, 255),
            )
            self._draw_surface_slot_overlay(
                panel_id=f"d{visible_depth.depth}:center_ceiling",
                quad=zone.center_ceiling,
                color=(255, 180, 0),
            )
            if is_wall(visible_depth.left):
                pygame.draw.polygon(self.screen, colors["wall"], zone.left_wall.as_int_points(), 1)
            else:
                pygame.draw.polygon(self.screen, colors["side_floor"], zone.left_floor_open.as_int_points(), 1)
                pygame.draw.polygon(self.screen, colors["ceiling"], zone.left_ceiling_open.as_int_points(), 1)
            if is_wall(visible_depth.right):
                pygame.draw.polygon(self.screen, colors["wall"], zone.right_wall.as_int_points(), 1)
            else:
                pygame.draw.polygon(self.screen, colors["side_floor"], zone.right_floor_open.as_int_points(), 1)
                pygame.draw.polygon(self.screen, colors["ceiling"], zone.right_ceiling_open.as_int_points(), 1)
            if is_wall(visible_depth.center):
                pygame.draw.rect(self.screen, colors["back"], zone.back_wall_rect.to_int_tuple(), 1)
                break

    def _draw_surface_slot_overlay(self, panel_id: str, quad: Quad, color: tuple[int, int, int]) -> None:
        if not self.debug_surface_slots:
            return

        if "floor" in panel_id:
            slot_ids = self.textures.describe_floor_slot_ids(panel_id)
        elif "ceiling" in panel_id:
            slot_ids = self.textures.describe_ceiling_slot_ids(panel_id)
        else:
            slot_ids = ()

        if not slot_ids:
            return

        font = getattr(self.presenter, "small_font", None)
        if font is None:
            font = pygame.font.Font(None, 14)

        slot_spans = self.textures.describe_surface_slot_spans(panel_id)
        for slot_id, (start_ratio, end_ratio) in zip(slot_ids, slot_spans):
            slot_quad = self._slice_quad_horizontal_region(
                quad,
                start_ratio,
                end_ratio,
            )
            pygame.draw.polygon(self.screen, color, slot_quad.as_int_points(), 1)

            bounds = slot_quad.bounding_rect()
            label = slot_id.rsplit(":", 1)[-1]
            text = font.render(label, True, color)
            text_pos = (
                round(bounds.x + (bounds.w * 0.5) - (text.get_width() * 0.5)),
                round(bounds.y + (bounds.h * 0.5) - (text.get_height() * 0.5)),
            )
            self.screen.blit(text, text_pos)

    def _get_layer_darkness(self, depth: int) -> float:
        if self.disable_darkness:
            return 0.0
        if depth == 1:
            return 0.0
        if depth == 2:
            return 0.4
        return 0.8

    def _emit_debug_snapshot(self, scene, commands: list[RenderCommand]) -> None:
        if not (self.debug_scene or self.debug_commands):
            return

        lines = ["[dungeon-renderer] snapshot"]
        if self.debug_scene:
            for visible_depth in scene.depths:
                lines.append(
                    "  "
                    + f"d{visible_depth.depth} "
                    + ", ".join(
                        (
                            f"src={self._tile_name(visible_depth.source_tile)}",
                            f"center={self._tile_name(visible_depth.center)}",
                            f"left={self._tile_name(visible_depth.left)}",
                            f"right={self._tile_name(visible_depth.right)}",
                            f"left_branch={self._tile_name(visible_depth.left_branch)}",
                            f"right_branch={self._tile_name(visible_depth.right_branch)}",
                            f"left_forward={self._tile_name(visible_depth.left_forward)}",
                            f"right_forward={self._tile_name(visible_depth.right_forward)}",
                            f"left_forward_outer={self._tile_name(visible_depth.left_forward_outer)}",
                            f"right_forward_outer={self._tile_name(visible_depth.right_forward_outer)}",
                        )
                    )
                )

        if self.debug_commands:
            surface_overrides = self.textures.get_surface_slot_overrides()
            for slot_id, texture_key in sorted(surface_overrides.items()):
                family = slot_id.split(":", 1)[0]
                lines.append("  " + f"{family}-override {slot_id}={texture_key}")
            if self.debug_surface_slots:
                for visible_depth in scene.depths:
                    for panel_id, texture_key, resolver in (
                        (
                            f"d{visible_depth.depth}:center_floor",
                            self._get_center_floor_texture_key(
                                depth=visible_depth.depth,
                                source_tile=visible_depth.source_tile,
                                fallback_tile=self._find_initial_floor_theme_tile(scene),
                            ),
                            self.textures.describe_floor_slot_ids,
                        ),
                        (
                            f"d{visible_depth.depth}:center_ceiling",
                            self.textures.get_ceiling_key(visible_depth.source_tile),
                            self.textures.describe_ceiling_slot_ids,
                        ),
                    ):
                        slot_ids = resolver(panel_id)
                        if not slot_ids:
                            continue
                        resolved = [
                            f"{slot_id.rsplit(':', 1)[-1]}={surface_overrides.get(slot_id, texture_key)}"
                            for slot_id in slot_ids
                        ]
                        lines.append("  " + f"resolved {panel_id} " + ", ".join(resolved))
            for command in sorted(commands, key=lambda item: (-item.depth, item.order, item.panel_id)):
                bounds = command.quad.bounding_rect()
                lines.append(
                    "  "
                    + f"cmd d{command.depth} o{command.order} {command.panel_id} "
                    + f"tex={command.texture_key} "
                    + f"bbox=({round(bounds.x)}, {round(bounds.y)}, {round(bounds.w)}, {round(bounds.h)}) "
                    + f"dark={command.darkness:.2f}"
                )

        snapshot = "\n".join(lines)
        if snapshot != self._last_debug_snapshot:
            print(snapshot)
            self._last_debug_snapshot = snapshot

    @staticmethod
    def _tile_name(tile) -> str:
        return type(tile).__name__ if tile is not None else "None"

    def _render_special_tiles(self, scene, zones) -> None:
        visible_center_depths = []
        center_path_open = True
        max_visible_depth = scene.depths[-1].depth if scene.depths else 0
        for visible_depth in scene.depths:
            if not center_path_open:
                break

            self._render_side_special_tiles(
                visible_depth,
                zones[visible_depth.depth],
                zones.get(visible_depth.depth + 1),
            )

            visible_center_depths.append(visible_depth)

            if is_wall(visible_depth.center):
                center_path_open = False

        for visible_depth in reversed(visible_center_depths):
            if visible_depth.depth == max_visible_depth and not is_wall(visible_depth.center):
                continue
            rect = pygame.Rect(zones[visible_depth.depth].back_wall_rect.to_int_tuple())
            if visible_depth.center is not None and "WarpPoint" in type(visible_depth.center).__name__:
                continue
            self._render_special_tile(
                visible_depth.center,
                rect,
                darkness=self._get_layer_darkness(visible_depth.depth),
                depth=visible_depth.depth,
            )

        self._render_center_floor_special_tiles(scene, zones)

        current_depth = scene.depths[0] if scene.depths else None
        if current_depth is None:
            return

        current_tile = current_depth.source_tile
        if current_tile is not None and "WarpPoint" in type(current_tile).__name__:
            return

        current_rect = pygame.Rect(zones[1].back_wall_rect.to_int_tuple())
        self._render_special_tile(
            current_tile,
            current_rect,
            darkness=self._get_layer_darkness(1),
            depth=0,
        )

    def _render_center_floor_special_tiles(self, scene, zones) -> None:
        for visible_depth in scene.depths:
            tile = visible_depth.source_tile
            if tile is None or "WarpPoint" not in type(tile).__name__:
                continue

            quad = self._get_center_floor_slot_quad(
                zone=zones[visible_depth.depth],
                depth=visible_depth.depth,
                slot_suffix="x0",
            )
            self._render_center_floor_warp_point(
                quad,
                darkness=self._get_layer_darkness(visible_depth.depth),
                depth=visible_depth.depth,
            )

    def _render_side_special_tiles(self, visible_depth, zone, next_zone=None) -> None:
        if next_zone is None:
            return

        if self._should_hide_side_doors_behind_center_wall(visible_depth):
            return

        darkness = self._get_layer_darkness(visible_depth.depth)
        left_rect = self._get_side_opening_rect(zone, "left")
        right_rect = self._get_side_opening_rect(zone, "right")
        self._render_side_special_tile(
            visible_depth.left_forward,
            left_rect,
            darkness=darkness,
            depth=visible_depth.depth,
            side="left",
            opening_tile=visible_depth.left,
            center_tile=visible_depth.center,
            zone=zone,
            next_zone=next_zone,
        )
        self._render_side_special_tile(
            visible_depth.right_forward,
            right_rect,
            darkness=darkness,
            depth=visible_depth.depth,
            side="right",
            opening_tile=visible_depth.right,
            center_tile=visible_depth.center,
            zone=zone,
            next_zone=next_zone,
        )

    def _get_side_special_surface_geometry(self, zone, next_zone, side: str, depth: int) -> tuple[Quad, Quad, int]:
        if next_zone is None:
            if side == "left":
                return zone.left_floor_open, zone.left_ceiling_open, depth
            return zone.right_floor_open, zone.right_ceiling_open, depth

        base_offset = float(zone.rect.w) * 0.25
        edge_offset = float(zone.rect.w) * 0.5

        if side == "left":
            return (
                self._slice_quad_horizontal_region(
                    self._push_outer_floor_quad(next_zone.center_floor_left, side, base_offset, edge_offset),
                    0.25,
                    0.75,
                ),
                self._slice_quad_horizontal_region(
                    self._push_outer_ceiling_quad(next_zone.center_ceiling_left, side, base_offset, edge_offset),
                    0.25,
                    0.75,
                ),
                depth + 1,
            )

        return (
            self._slice_quad_horizontal_region(
                self._push_outer_floor_quad(next_zone.center_floor_right, side, base_offset, edge_offset),
                0.25,
                0.75,
            ),
            self._slice_quad_horizontal_region(
                self._push_outer_ceiling_quad(next_zone.center_ceiling_right, side, base_offset, edge_offset),
                0.25,
                0.75,
            ),
            depth + 1,
        )

    def _get_visible_side_special_floor_geometry(self, zone, side: str, depth: int, next_zone=None) -> tuple[Quad, int, str]:
        base_quad = zone.left_floor_open if side == "left" else zone.right_floor_open
        if side == "left":
            sliced = self._slice_quad_region(base_quad, 0.10, 0.38, 0.45, 0.85)
        else:
            sliced = self._slice_quad_region(base_quad, 0.62, 0.90, 0.45, 0.85)
        return sliced, depth, f"d{depth}:{side}_opening_special_floor"

    def _get_visible_side_special_ceiling_geometry(self, zone, side: str, depth: int, next_zone=None) -> tuple[Quad, int, str]:
        base_quad = zone.left_ceiling_open if side == "left" else zone.right_ceiling_open
        if side == "left":
            sliced = self._slice_quad_region(base_quad, 0.10, 0.42, 0.15, 0.70)
        else:
            sliced = self._slice_quad_region(base_quad, 0.58, 0.90, 0.15, 0.70)
        return sliced, depth, f"d{depth}:{side}_opening_special_ceiling"

    def _render_side_special_tile(
        self,
        tile,
        rect: pygame.Rect,
        darkness: float,
        depth: int,
        side: str,
        opening_tile=None,
        center_tile=None,
        zone=None,
        next_zone=None,
    ) -> None:
        if self._opening_tile_blocks_view(opening_tile) or tile is None or (is_wall(tile) and not self._is_door_tile(tile)):
            return
        if self._is_door_tile(tile):
            return

        render_depth = depth
        if zone is not None and next_zone is not None and self._is_floor_sprite_tile(tile):
            render_depth = depth + 1

        render_rect = self._get_side_special_render_rect(
            rect,
            tile,
            side,
            center_tile=center_tile,
            zone=zone,
            next_zone=next_zone,
            depth=depth,
        )
        if not isinstance(render_rect, pygame.Rect):
            render_rect = pygame.Rect(
                round(render_rect.x),
                round(render_rect.y),
                max(1, round(render_rect.w)),
                max(1, round(render_rect.h)),
        )
        clip_rect = self._get_side_special_clip_rect(rect, tile, side, center_tile=center_tile)
        previous_clip = self.screen.get_clip()
        try:
            if clip_rect is not None:
                self.screen.set_clip(clip_rect)
            self._render_special_tile(
                tile,
                render_rect,
                darkness=darkness,
                depth=render_depth,
                side=side,
                lateral_view=True,
            )
        finally:
            self.screen.set_clip(previous_clip)

    def _render_special_tile(
        self,
        tile,
        rect: pygame.Rect,
        darkness: float,
        depth: int,
        side: str | None = None,
        lateral_view: bool = False,
    ) -> None:
        if tile is None:
            return

        tile_type = type(tile).__name__

        if depth <= 0 and "Door" in tile_type:
            return

        if tile_type == "OreVaultDoor":
            return

        if "Door" in tile_type:
            return

        if depth <= 0 and "WarpPoint" not in tile_type:
            return

        if "Chest" in tile_type:
            if getattr(tile, "opened", False) or getattr(tile, "open", False):
                sprite_key = "chest_open"
            elif getattr(tile, "locked", False):
                sprite_key = "chest_locked"
            else:
                sprite_key = "chest_closed"
            self._render_floor_sprite(
                sprite_key,
                rect,
                darkness=darkness,
                depth=depth,
                kind="chest",
                side=side,
                lateral_view=lateral_view,
            )
            return

        if "StairsUp" in tile_type:
            self._render_special_sprite("stairs_up", rect, darkness=darkness, side=side, lateral_view=lateral_view)
            return

        if "StairsDown" in tile_type:
            self._render_special_sprite("stairs_down", rect, darkness=darkness, side=side, lateral_view=lateral_view)
            return

        if "LadderUp" in tile_type:
            self._render_floor_sprite(
                "ladder_up",
                rect,
                darkness=darkness,
                depth=depth,
                kind="ladder_up",
                side=side,
                lateral_view=lateral_view,
            )
            return

        if "LadderDown" in tile_type:
            self._render_special_sprite("ladder_down", rect, darkness=darkness, side=side, lateral_view=lateral_view)
            return

        if "Portal" in tile_type:
            self._render_special_sprite("portal", rect, darkness=darkness, side=side, lateral_view=lateral_view)
            return

        if "WarpPoint" in tile_type:
            self._render_floor_sprite(
                "teleporter",
                rect,
                darkness=darkness,
                depth=depth,
                kind="warp_point",
                side=side,
                lateral_view=lateral_view,
            )
            if bool(getattr(self.player_char, "warp_point", False)):
                self._render_warp_point_sparks(
                    rect,
                    darkness=darkness,
                    depth=depth,
                    side=side,
                    lateral_view=lateral_view,
                )
            return

        if "Boulder" in tile_type:
            sprite_key = "boulder" if bool(getattr(tile, "read", False)) else "boulder_sword"
            self._render_floor_sprite(
                sprite_key,
                rect,
                darkness=darkness,
                depth=depth,
                kind="boulder",
                side=side,
                lateral_view=lateral_view,
            )
            return

        if "DeadBody" in tile_type:
            sprite_key = "burial_site" if bool(getattr(tile, "read", False)) else "dead_body"
            self._render_floor_sprite(
                sprite_key,
                rect,
                darkness=darkness,
                depth=depth,
                kind="dead_body",
                side=side,
                lateral_view=lateral_view,
            )
            return

        if "RelicRoom" in tile_type:
            sprite_key = self._get_relic_altar_sprite_key(tile)
            self._render_floor_sprite(
                sprite_key,
                rect,
                darkness=darkness,
                depth=depth,
                kind="altar",
                side=side,
                lateral_view=lateral_view,
            )
            return

        if "GoldenChaliceRoom" in tile_type:
            if hasattr(getattr(self, "player_char", None), "quest_dict") and not map_tiles.chalice_altar_visible(self.player_char):
                return
            sprite_key = "empty_golden_chalice_altar" if bool(getattr(tile, "read", False)) else "golden_chalice_altar"
            self._render_floor_sprite(
                sprite_key,
                rect,
                darkness=darkness,
                depth=depth,
                kind="altar",
                side=side,
                lateral_view=lateral_view,
            )
            return

        if "UnobtainiumRoom" in tile_type and not bool(getattr(tile, "visited", False)):
            self._render_floor_sprite(
                "unobtainium",
                rect,
                darkness=darkness,
                depth=depth,
                kind="unobtainium",
                side=side,
                lateral_view=lateral_view,
            )
            return

        if "SecretShop" in tile_type:
            self._render_special_sprite("secret_shop", rect, darkness=darkness, side=side, lateral_view=lateral_view)
            return

        if "BossRoom" in tile_type:
            self._render_boss_enemy(tile, rect, darkness=darkness, depth=depth, side=side, lateral_view=lateral_view)

    def _render_special_sprite(
        self,
        texture_key: str,
        rect: pygame.Rect,
        darkness: float,
        side: str | None = None,
        lateral_view: bool = False,
    ) -> None:
        sprite = self.textures.get_special_texture(texture_key)
        if sprite is None:
            return

        if lateral_view and texture_key.startswith("door_") and side is not None:
            target_rect = self._get_lateral_door_sprite_rect(rect, side)
        else:
            if lateral_view and texture_key.startswith("door_"):
                sprite = self._trim_transparent_sprite(sprite)
            target_rect = self._get_special_sprite_rect(
                rect,
                side=side,
                lateral_view=lateral_view,
                texture_key=texture_key,
            )
        scaled = pygame.transform.smoothscale(sprite, target_rect.size)
        shaded = self._apply_darkness_to_surface(scaled, darkness)
        self.screen.blit(shaded, target_rect.topleft)

    def _render_floor_sprite(
        self,
        texture_key: str,
        rect: pygame.Rect,
        darkness: float,
        depth: int,
        kind: str,
        side: str | None = None,
        lateral_view: bool = False,
    ) -> None:
        size_ratio = self._get_floor_sprite_ratio(depth, kind)
        if lateral_view:
            size_ratio *= 0.9
        sprite_size = max(8, int(rect.height * size_ratio))
        sprite = self.textures.get_special_texture(texture_key, sprite_size)
        if sprite is None:
            return

        sprite_rect = sprite.get_rect()
        sprite_rect.midbottom = self._get_floor_sprite_anchor(rect, side=side, lateral_view=lateral_view)

        if kind == "ladder_up":
            sprite_rect.y = rect.y + (rect.height - sprite_rect.height) // 2

        if lateral_view and side is not None:
            quad = self._get_lateral_floor_sprite_quad(sprite_rect, side)
            projected = project_texture_to_quad(sprite, quad, darkness=darkness)
            self.screen.blit(projected.surface, projected.topleft)
            return

        shaded = self._apply_darkness_to_surface(sprite, darkness)
        self.screen.blit(shaded, sprite_rect.topleft)

    def _render_boss_enemy(
        self,
        tile,
        rect: pygame.Rect,
        darkness: float,
        depth: int,
        side: str | None = None,
        lateral_view: bool = False,
    ) -> None:
        if bool(getattr(tile, "defeated", False)):
            self._render_floor_sprite(
                "burial_site",
                rect,
                darkness=darkness,
                depth=depth,
                kind="defeated_boss",
                side=side,
                lateral_view=lateral_view,
            )
            return

        enemy = getattr(tile, "enemy", None)
        if enemy is None:
            return

        if callable(enemy):
            try:
                enemy = enemy()
            except Exception:
                return

        enemy_name = getattr(enemy, "name", None)
        if not enemy_name:
            return

        if hasattr(enemy, "is_alive") and not enemy.is_alive():
            return

        apparent_depth = min(depth + 1, 3)
        size_ratio = {1: 0.8, 2: 0.5, 3: 0.3}.get(apparent_depth, 0.3)
        if lateral_view:
            size_ratio *= 0.9
        sprite_size = max(8, int(min(rect.width, rect.height) * size_ratio))
        sprite = self.textures.get_enemy_texture(enemy_name, sprite_size)

        if sprite is None:
            fallback = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
            fallback.fill((200, 50, 50, 255))
            sprite = fallback

        sprite_rect = sprite.get_rect()
        sprite_rect.midbottom = self._get_floor_sprite_anchor(rect, side=side, lateral_view=lateral_view)

        if lateral_view and side is not None:
            quad = self._get_lateral_floor_sprite_quad(sprite_rect, side)
            projected = project_texture_to_quad(sprite, quad, darkness=darkness)
            self.screen.blit(projected.surface, projected.topleft)
            return

        shaded = self._apply_darkness_to_surface(sprite, darkness)
        self.screen.blit(shaded, sprite_rect.topleft)

    @staticmethod
    def _is_floor_sprite_tile(tile) -> bool:
        if tile is None:
            return False

        tile_type = type(tile).__name__
        return any(
            name in tile_type
            for name in (
                "Chest",
                "Boulder",
                "DeadBody",
                "RelicRoom",
                "GoldenChaliceRoom",
                "UnobtainiumRoom",
                "BossRoom",
            )
        )

    @staticmethod
    def _is_chest_tile(tile) -> bool:
        return tile is not None and "Chest" in type(tile).__name__

    def _render_warp_point_sparks(
        self,
        rect: pygame.Rect,
        darkness: float,
        depth: int,
        side: str | None = None,
        lateral_view: bool = False,
    ) -> None:
        effect_rect = self._get_warp_point_effect_rect(rect, lateral_view=lateral_view, side=side)

        overlay = pygame.Surface(effect_rect.size, pygame.SRCALPHA)
        ticks = pygame.time.get_ticks() / 1000.0
        particle_count = 10 if depth <= 1 else 8 if depth == 2 else 6
        if lateral_view:
            particle_count = max(4, particle_count - 2)

        glow_alpha = int(70 * max(0.0, 1.0 - min(1.0, darkness)))
        glow_rect = pygame.Rect(
            round(effect_rect.width * 0.18),
            round(effect_rect.height * 0.305),
            round(effect_rect.width * 0.63),
            round(effect_rect.height * 0.53),
        )
        pygame.draw.ellipse(overlay, (90, 180, 255, glow_alpha), glow_rect)

        for index in range(particle_count):
            orbit = (index / particle_count) * math.tau
            rise_phase = (ticks * 0.9 + (index * 0.173)) % 1.0
            drift = math.sin((ticks * 2.8) + (index * 1.7))
            x = (effect_rect.width * 0.5) + (math.cos(orbit + (ticks * 1.7)) * effect_rect.width * 0.22) + (drift * effect_rect.width * 0.04)
            y = (effect_rect.height * 0.78) - (rise_phase * effect_rect.height * 0.62)
            radius = max(1, round((3 if depth <= 1 else 2) * (1.0 - (rise_phase * 0.55))))
            alpha = int((220 - (rise_phase * 110)) * max(0.0, 1.0 - min(1.0, darkness * 0.7)))
            color = (130, 220, 255, alpha)
            pygame.draw.circle(overlay, color, (round(x), round(y)), radius)
            if radius > 1:
                pygame.draw.circle(overlay, (220, 245, 255, min(255, alpha)), (round(x), round(y)), max(1, radius - 1))

        self.screen.blit(overlay, effect_rect.topleft)

    @staticmethod
    def _get_warp_point_effect_rect(
        rect: pygame.Rect,
        lateral_view: bool = False,
        side: str | None = None,
    ) -> pygame.Rect:
        if lateral_view:
            anchor_x, anchor_y = SceneRenderer._get_floor_sprite_anchor(rect, side=side, lateral_view=True)
            effect_width = max(16, int(rect.width))
            effect_height = max(16, int(rect.height))
            return pygame.Rect(
                round(anchor_x - (effect_width / 2)),
                round(anchor_y - effect_height),
                effect_width,
                effect_height,
            )

        effect_width = max(20, int(rect.width))
        effect_height = max(20, int(rect.height))
        effect_rect = pygame.Rect(0, 0, effect_width, effect_height)
        effect_rect.centerx = rect.centerx
        effect_rect.centery = round(rect.y + (rect.height * 0.3))
        return effect_rect

    def _render_center_floor_warp_point(self, quad: Quad, darkness: float, depth: int) -> None:
        sprite = self.textures.get_special_texture("teleporter")
        if sprite is None:
            return

        sprite = self._trim_transparent_sprite(sprite)
        target_rect = self._get_center_floor_warp_point_rect(quad, sprite)
        scaled = pygame.transform.smoothscale(sprite, target_rect.size)
        shaded = self._apply_darkness_to_surface(scaled, darkness)
        self.screen.blit(shaded, target_rect.topleft)

        if bool(getattr(self.player_char, "warp_point", False)):
            self._render_warp_point_sparks(
                target_rect,
                darkness=darkness,
                depth=depth,
            )

    @staticmethod
    def _get_center_floor_warp_point_rect(quad: Quad, sprite: pygame.Surface) -> pygame.Rect:
        bounds = quad.bounding_rect()
        rect = pygame.Rect(
            0,
            0,
            max(1, round(bounds.w * 0.66)),
            max(1, round(bounds.h)),
        )
        rect.centerx = round(bounds.x + (bounds.w / 2.0))
        rect.bottom = round(bounds.y + bounds.h)
        return rect

    def _get_relic_altar_sprite_key(self, tile) -> str:
        if bool(getattr(tile, "read", False)):
            return "empty_altar"

        relic_num = getattr(getattr(self, "player_char", None), "location_z", 1)
        return {
            1: "luna_altar",
            2: "polaris_altar",
            3: "triangulus_altar",
            4: "quadrata_altar",
            5: "hexagonum_altar",
            6: "infinitas_altar",
        }.get(relic_num, "empty_altar")

    @staticmethod
    def _get_floor_sprite_ratio(depth: int, kind: str) -> float:
        if kind == "ladder_up":
            return {1: 0.8, 2: 0.6, 3: 0.4}.get(depth, 0.4)
        if kind == "chest":
            return {1: 0.55, 2: 0.45, 3: 0.35}.get(depth, 0.35)
        if kind == "boulder":
            return {1: 0.70, 2: 0.58, 3: 0.46}.get(depth, 0.46)
        if kind == "dead_body":
            return {1: 0.75, 2: 0.60, 3: 0.46}.get(depth, 0.46)
        if kind == "defeated_boss":
            return {1: 0.70, 2: 0.56, 3: 0.42}.get(depth, 0.42)
        if kind == "altar":
            return {1: 0.60, 2: 0.50, 3: 0.40}.get(depth, 0.40)
        if kind == "unobtainium":
            return {1: 0.45, 2: 0.38, 3: 0.32}.get(depth, 0.32)
        if kind == "warp_point":
            return {1: 1.08, 2: 0.88, 3: 0.68}.get(depth, 0.68)
        return {1: 1.0, 2: 0.8, 3: 0.6}.get(depth, 0.6)

    @staticmethod
    def _is_door_tile(tile) -> bool:
        if tile is None:
            return False
        tile_type = type(tile).__name__
        if tile_type == "OreVaultDoor":
            return getattr(tile, "open", False) or getattr(tile, "detected", False)
        return "Door" in tile_type

    @staticmethod
    def _is_open_door_tile(tile) -> bool:
        return SceneRenderer._is_door_tile(tile) and bool(getattr(tile, "open", False))

    @staticmethod
    def _opening_tile_blocks_view(tile) -> bool:
        return is_wall(tile) and not SceneRenderer._is_open_door_tile(tile)

    def _should_hide_side_doors_behind_center_wall(self, visible_depth) -> bool:
        return (
            visible_depth.depth == 1
            and is_wall(visible_depth.center)
            and self._is_door_tile(visible_depth.left_forward)
            and self._is_door_tile(visible_depth.right_forward)
        )

    def _get_side_special_render_rect(
        self,
        rect: pygame.Rect,
        tile,
        side: str,
        center_tile=None,
        zone=None,
        next_zone=None,
        depth: int | None = None,
    ) -> pygame.Rect:
        if not self._is_floor_sprite_tile(tile) or is_wall(center_tile):
            return rect

        if zone is not None and next_zone is not None and depth is not None:
            floor_quad, _, _ = self._get_side_special_surface_geometry(
                zone=zone,
                next_zone=next_zone,
                side=side,
                depth=depth,
            )
            bounds = floor_quad.bounding_rect()
            return type(bounds)(
                bounds.x,
                rect.y,
                bounds.w,
                rect.height,
            )

        overscan = max(1, int(rect.width * 0.7))
        if side == "left":
            return pygame.Rect(rect.x, rect.y, rect.width + overscan, rect.height)
        return pygame.Rect(rect.x - overscan, rect.y, rect.width + overscan, rect.height)

    @staticmethod
    def _get_side_special_clip_rect(rect: pygame.Rect, tile, side: str, center_tile=None) -> pygame.Rect | None:
        if not is_wall(center_tile):
            return None

        if not SceneRenderer._is_floor_sprite_tile(tile):
            return rect

        if SceneRenderer._is_chest_tile(tile):
            return rect

        overscan = max(1, int(rect.width * 0.7))
        if side == "left":
            return pygame.Rect(rect.x, rect.y, rect.width + overscan, rect.height)
        return pygame.Rect(rect.x - overscan, rect.y, rect.width + overscan, rect.height)

    @staticmethod
    def _get_side_opening_rect(zone, side: str) -> pygame.Rect:
        if side == "left":
            inner_x = zone.left_wall.points[1][0]
            top_y = zone.left_wall.points[1][1]
            bottom_y = zone.left_wall.points[2][1]
            return pygame.Rect(
                round(zone.rect.x),
                round(top_y),
                max(1, round(inner_x - zone.rect.x)),
                max(1, round(bottom_y - top_y)),
            )

        inner_x = zone.right_wall.points[0][0]
        top_y = zone.right_wall.points[0][1]
        bottom_y = zone.right_wall.points[3][1]
        rect_right = zone.rect.x + zone.rect.w
        return pygame.Rect(
            round(inner_x),
            round(top_y),
            max(1, round(rect_right - inner_x)),
            max(1, round(bottom_y - top_y)),
        )

    def _get_center_floor_slot_quad(self, zone, depth: int, slot_suffix: str) -> Quad:
        panel_id = f"d{depth}:center_floor"
        slot_ids = self.textures.describe_floor_slot_ids(panel_id)
        slot_spans = self.textures.describe_surface_slot_spans(panel_id)
        target_slot_id = f"floor:visible:d{depth}:{slot_suffix}"

        for slot_id, (start_ratio, end_ratio) in zip(slot_ids, slot_spans):
            if slot_id != target_slot_id:
                continue
            return self._slice_quad_horizontal_region(
                zone.center_floor,
                start_ratio,
                end_ratio,
            )

        return zone.center_floor

    @staticmethod
    def _get_floor_sprite_anchor(
        rect: pygame.Rect,
        side: str | None = None,
        lateral_view: bool = False,
    ) -> tuple[int, int]:
        if not lateral_view or side is None:
            return rect.centerx, rect.bottom

        offset = int(rect.width * 0.28)
        if side == "left":
            return rect.right - offset, rect.bottom
        return rect.left + offset, rect.bottom

    @staticmethod
    def _get_lateral_floor_sprite_quad(sprite_rect: pygame.Rect, side: str) -> Quad:
        width = float(sprite_rect.width)
        height = float(sprite_rect.height)

        near_inset = width * 0.03
        far_inset = width * 0.12
        top_drop = height * 0.06
        bottom_lift = height * 0.02

        if side == "left":
            return Quad(
                (
                    (sprite_rect.left + far_inset, sprite_rect.top + top_drop),
                    (sprite_rect.right - near_inset, sprite_rect.top + top_drop),
                    (sprite_rect.right, sprite_rect.bottom),
                    (sprite_rect.left, sprite_rect.bottom - bottom_lift),
                )
            )

        return Quad(
            (
                (sprite_rect.left + near_inset, sprite_rect.top + top_drop),
                (sprite_rect.right - far_inset, sprite_rect.top + top_drop),
                (sprite_rect.right, sprite_rect.bottom - bottom_lift),
                (sprite_rect.left, sprite_rect.bottom),
            )
        )

    @staticmethod
    def _get_special_sprite_rect(
        rect: pygame.Rect,
        side: str | None = None,
        lateral_view: bool = False,
        texture_key: str | None = None,
    ) -> pygame.Rect:
        if not lateral_view or side is None:
            return rect

        if texture_key in {"stairs_up", "stairs_down"}:
            return SceneRenderer._get_lateral_stairs_sprite_rect(rect, side)

        width = max(1, int(rect.width * 1.15))
        height = rect.height
        if side == "left":
            x = rect.right - width
        else:
            x = rect.left
        return pygame.Rect(x, rect.y, width, height)

    @staticmethod
    def _get_lateral_door_sprite_rect(rect: pygame.Rect, side: str) -> pygame.Rect:
        width = max(1, int(rect.width * 1.45))
        height = rect.height
        overscan = max(1, int((width - rect.width) * 0.65))
        if side == "left":
            x = rect.left - overscan
        else:
            x = rect.right - width + overscan
        return pygame.Rect(x, rect.y, width, height)

    @staticmethod
    def _get_lateral_stairs_sprite_rect(rect: pygame.Rect, side: str) -> pygame.Rect:
        width = max(1, int(rect.width * 1.75))
        height = rect.height
        if side == "left":
            x = rect.right - width
        else:
            x = rect.left
        return pygame.Rect(x, rect.y, width, height)

    @staticmethod
    def _apply_darkness_to_surface(surface: pygame.Surface, darkness: float) -> pygame.Surface:
        darkness = max(0.0, min(1.0, darkness))
        if darkness <= 0.0:
            return surface.copy()

        shaded = surface.copy()
        factor = int(255 * (1.0 - darkness))
        shaded.fill((factor, factor, factor, 255), special_flags=pygame.BLEND_RGBA_MULT)
        return shaded

    @staticmethod
    def _trim_transparent_sprite(surface: pygame.Surface) -> pygame.Surface:
        bounds = surface.get_bounding_rect(min_alpha=1)
        if bounds.width <= 0 or bounds.height <= 0:
            return surface
        if bounds.size == surface.get_size():
            return surface
        return surface.subsurface(bounds).copy()
