"""Debug behavior for the renderer package."""

from __future__ import annotations

import pygame

from ..geometry import Quad
from ..scene import is_wall
from .models import RenderCommand


class RendererDebugMixin:
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
