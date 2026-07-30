"""Overlays behavior for the renderer package."""

from __future__ import annotations

import math
import os

import pygame

from ..geometry import Quad
from ..scene import is_fake_wall, is_wall
from .specials import RendererSpecialTileMixin


class RendererOverlayMixin:
    @staticmethod
    def _is_side_surface_only_ladder(tile) -> bool:
        tile_type = type(tile).__name__ if tile is not None else ""
        return "LadderDown" in tile_type or "LadderUp" in tile_type

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
            anchor_x, anchor_y = RendererOverlayMixin._get_floor_sprite_anchor(rect, side=side, lateral_view=True)
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
        sprite = self.textures.get_special_texture(self._warp_point_sprite_key())
        if sprite is None:
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
    def _special_texture_available(texture_library, texture_key: str) -> bool:
        rel_path = getattr(texture_library, "special_texture_paths", {}).get(texture_key)
        if not rel_path:
            return False
        resolver = getattr(texture_library, "_resolve_asset_path", None)
        if not callable(resolver):
            return True
        return os.path.exists(resolver(rel_path))

    def _warp_point_sprite_key(self) -> str:
        preferred = "warp_point_active" if bool(getattr(self.player_char, "warp_point", False)) else "warp_point_inactive"
        if self._special_texture_available(self.textures, preferred):
            return preferred
        return "teleporter"

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
        if kind == "stairs_down":
            return {1: 1.15, 2: 0.95, 3: 0.72}.get(depth, 0.72)
        if kind == "ladder_up":
            return {1: 0.8, 2: 0.6, 3: 0.4}.get(depth, 0.4)
        if kind == "ladder_down":
            return {1: 0.8, 2: 0.6, 3: 0.4}.get(depth, 0.4)
        if kind == "chest":
            return {1: 0.55, 2: 0.45, 3: 0.35}.get(depth, 0.35)
        if kind == "boulder":
            return {1: 0.70, 2: 0.58, 3: 0.46}.get(depth, 0.46)
        if kind == "dead_body":
            return {1: 0.54, 2: 0.43, 3: 0.33}.get(depth, 0.33)
        if kind == "dead_soldier_item":
            return {1: 0.42, 2: 0.34, 3: 0.26}.get(depth, 0.26)
        if kind == "defeated_boss":
            return {1: 0.70, 2: 0.56, 3: 0.42}.get(depth, 0.42)
        if kind == "altar":
            return {1: 0.60, 2: 0.50, 3: 0.40}.get(depth, 0.40)
        if kind == "unobtainium":
            return {1: 0.45, 2: 0.38, 3: 0.32}.get(depth, 0.32)
        if kind == "warp_point":
            return {1: 1.08, 2: 0.88, 3: 0.68}.get(depth, 0.68)
        if kind == "rotator":
            return {1: 0.56, 2: 0.46, 3: 0.34}.get(depth, 0.34)
        if kind == "decorative_prop":
            return {1: 0.62, 2: 0.50, 3: 0.38}.get(depth, 0.38)
        return {1: 1.0, 2: 0.8, 3: 0.6}.get(depth, 0.6)

    @staticmethod
    def _get_floor_sprite_texture_scale(texture_key: str) -> float:
        return {
            "bone_pile": 1.55,
        }.get(texture_key, 1.0)

    @staticmethod
    def _get_decorative_floor_sprite_key(tile_type: str) -> str | None:
        return {
            "RubbleTile": "rubble",
            "RootGrowthTile": "root_growth",
            "FungusPatchTile": "fungus_patch",
            "CrystalClusterTile": "crystal_cluster",
            "BonePileTile": "bone_pile",
            "BrokenGearTile": "broken_gear",
        }.get(tile_type)

    def _render_wall_overlays(self, scene, zones) -> None:
        for visible_depth in scene.depths:
            depth = visible_depth.depth
            zone = zones[depth]
            darkness = self._get_layer_darkness(depth)

            if not is_wall(visible_depth.center):
                self._render_surface_blood_overlay(
                    visible_depth.center,
                    zone.center_floor.bounding_rect(),
                    darkness=darkness,
                    depth=depth,
                    surface="floor",
                )
                self._render_surface_blood_overlay(
                    visible_depth.center,
                    zone.center_ceiling.bounding_rect(),
                    darkness=darkness,
                    depth=depth,
                    surface="ceiling",
                )

            if is_wall(visible_depth.center):
                if not self._is_door_tile(visible_depth.center):
                    self._render_wall_overlay_for_tile(
                        visible_depth.center,
                        pygame.Rect(zone.back_wall_rect.to_int_tuple()),
                        darkness=darkness,
                        depth=depth,
                    )
                # A center wall occludes its side surfaces and every deeper wall.
                # Wall decorations are a late rendering pass, so continuing here
                # would otherwise paint sconces through the blocking wall.
                break

            if is_wall(visible_depth.left) and not self._is_door_tile(visible_depth.left):
                self._render_wall_overlay_for_tile(
                    visible_depth.left,
                    zone.left_wall.bounding_rect(),
                    darkness=darkness,
                    depth=depth,
                    side="left",
                )

            if is_wall(visible_depth.right) and not self._is_door_tile(visible_depth.right):
                self._render_wall_overlay_for_tile(
                    visible_depth.right,
                    zone.right_wall.bounding_rect(),
                    darkness=darkness,
                    depth=depth,
                    side="right",
                )

    def _render_surface_blood_overlay(
        self,
        tile,
        rect,
        darkness: float,
        depth: int,
        surface: str,
    ) -> None:
        texture_key = self._get_blood_overlay_key(tile, surface)
        if texture_key is None:
            return

        if not isinstance(rect, pygame.Rect):
            rect = pygame.Rect(
                round(rect.x),
                round(rect.y),
                max(1, round(rect.w)),
                max(1, round(rect.h)),
            )

        max_size = max(16, round(min(rect.width, rect.height) * (0.42 if surface == "floor" else 0.34)))
        sprite = self.textures.get_special_texture(texture_key, max_size)
        if sprite is None:
            return

        sprite_rect = sprite.get_rect()
        if surface == "ceiling":
            sprite_rect.center = (rect.centerx, round(rect.y + rect.height * 0.52))
        else:
            sprite_rect.center = (rect.centerx, round(rect.y + rect.height * 0.62))
        shaded = self._apply_darkness_to_surface(sprite, darkness)
        self.screen.blit(shaded, sprite_rect.topleft)

    def _render_wall_overlay_for_tile(
        self,
        tile,
        rect,
        darkness: float,
        depth: int,
        side: str | None = None,
    ) -> None:
        texture_key = self._get_wall_overlay_key(tile, depth)
        if texture_key is None:
            return

        if not isinstance(rect, pygame.Rect):
            rect = pygame.Rect(
                round(rect.x),
                round(rect.y),
                max(1, round(rect.w)),
                max(1, round(rect.h)),
            )

        max_size = max(10, round(min(rect.width, rect.height) * (0.30 if side else 0.22)))
        sprite = self.textures.get_special_texture(texture_key, max_size)
        if sprite is None:
            return

        sprite_rect = sprite.get_rect()
        if side == "left":
            sprite_rect.midtop = (round(rect.x + rect.width * 0.64), round(rect.y + rect.height * 0.24))
        elif side == "right":
            sprite_rect.midtop = (round(rect.x + rect.width * 0.36), round(rect.y + rect.height * 0.24))
        else:
            sprite_rect.midtop = (rect.centerx, round(rect.y + rect.height * 0.22))

        shaded = self._apply_darkness_to_surface(sprite, darkness)
        self.screen.blit(shaded, sprite_rect.topleft)

    @staticmethod
    def _get_wall_overlay_key(tile, depth: int) -> str | None:
        if tile is None:
            return None
        blood_key = RendererOverlayMixin._get_blood_overlay_key(tile, "wall")
        if blood_key is not None:
            return blood_key
        if is_fake_wall(tile) or type(tile).__name__ in {"FunhouseWall", "MirrorWall"}:
            return None
        z = getattr(tile, "z", 1)
        seed = (getattr(tile, "x", 0) * 31) + (getattr(tile, "y", 0) * 17) + (z * 13)
        if z <= 1:
            return "torch_lit" if seed % 3 == 0 else None
        if z <= 3:
            if seed % 5 == 0:
                return "torch_lit"
            if seed % 4 == 0:
                return "sconce_broken"
            return None
        if seed % 4 == 0:
            return "sconce_unlit"
        if seed % 5 == 0:
            return "sconce_broken"
        return None

    @staticmethod
    def _get_blood_overlay_key(tile, surface: str) -> str | None:
        if tile is None:
            return None
        overlay = getattr(tile, "blood_overlay", None)
        overlays = getattr(tile, "blood_overlays", None)
        if overlay is True or overlay == surface:
            return f"blood_{surface}_overlay"
        if isinstance(overlays, (set, list, tuple)) and surface in overlays:
            return f"blood_{surface}_overlay"
        if getattr(tile, f"blood_{surface}_overlay", False):
            return f"blood_{surface}_overlay"
        return None

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
        return RendererOverlayMixin._is_door_tile(tile) and bool(getattr(tile, "open", False))

    @staticmethod
    def _opening_tile_blocks_view(tile) -> bool:
        return is_wall(tile) and not RendererOverlayMixin._is_open_door_tile(tile)

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
        if not self._is_floor_sprite_tile(tile, getattr(self, "player_char", None)) or is_wall(center_tile):
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

        if not RendererSpecialTileMixin._is_floor_sprite_tile(tile):
            return rect

        if "BossRoom" in type(tile).__name__:
            return rect

        if RendererOverlayMixin._is_chest_tile(tile):
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

    def _get_center_stairs_up_render_rect(self, zones, depth: int) -> pygame.Rect:
        zone = zones[depth]
        base_rect = pygame.Rect(zone.back_wall_rect.to_int_tuple())

        sprite = self.textures.get_special_texture("stairs_up")
        if sprite is None:
            return base_rect

        source_bounds = sprite.get_bounding_rect(min_alpha=128)
        if source_bounds.height <= 0 or sprite.get_height() <= 0:
            return base_rect

        source_top_ratio = source_bounds.top / sprite.get_height()
        source_bottom_ratio = source_bounds.bottom / sprite.get_height()
        source_visible_ratio = source_bottom_ratio - source_top_ratio
        if source_visible_ratio <= 0:
            return base_rect

        floor_bounds = zone.center_floor.bounding_rect()
        ceiling_bounds = zone.center_ceiling.bounding_rect()
        visible_top = ceiling_bounds.top + (ceiling_bounds.h * 0.4)
        visible_bottom = floor_bounds.bottom
        visible_height = visible_bottom - visible_top
        if visible_height <= 0:
            return base_rect

        target_height = visible_height / source_visible_ratio
        target_top = visible_top - (source_top_ratio * target_height)
        target_width = round(base_rect.width * 1.9)
        target_x = round(base_rect.centerx - (target_width / 2))
        return pygame.Rect(
            target_x,
            round(target_top),
            max(1, target_width),
            max(1, round(target_height)),
        )

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
    def _apply_stairs_up_ascend_gradient(surface: pygame.Surface) -> pygame.Surface:
        if surface.get_width() <= 0 or surface.get_height() <= 0:
            return surface

        shaded = surface.copy()
        gradient = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        height = max(1, surface.get_height() - 1)
        for y in range(surface.get_height()):
            t = y / height
            factor = round(52 + (203 * t))
            pygame.draw.line(
                gradient,
                (factor, factor, factor, 255),
                (0, y),
                (surface.get_width(), y),
            )
        shaded.blit(gradient, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return shaded

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
            return RendererOverlayMixin._get_lateral_stairs_sprite_rect(rect, side)

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
