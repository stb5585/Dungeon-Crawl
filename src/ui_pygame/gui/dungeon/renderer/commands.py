"""Commands behavior for the renderer package."""

from __future__ import annotations

from ..geometry import Quad
from ..scene import is_wall
from .models import RenderCommand


class RendererCommandMixin:
    @staticmethod
    def _is_localized_current_floor_tile(depth: int, tile) -> bool:
        return depth == 1 and "UndergroundSpring" in type(tile).__name__

    def _build_center_floor_commands(
        self, depth: int, zone, texture_key: str, darkness: float
    ) -> list[RenderCommand]:
        return self._build_center_surface_commands(
            depth=depth,
            panel_id=f"d{depth}:center_floor",
            texture_key=texture_key,
            quad=zone.center_floor,
            darkness=darkness,
            order=1,
            family="floor",
        )

    def _build_center_ceiling_commands(
        self, depth: int, zone, texture_key: str, darkness: float
    ) -> list[RenderCommand]:
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
        has_overscan_slots = any(
            start_ratio < 0.0 or end_ratio > 1.0 for start_ratio, end_ratio in slot_spans
        )
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

        if (
            self._opening_tile_blocks_view(opening_tile)
            or forward_tile is None
            or is_wall(forward_tile)
        ):
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
            ceiling_quad, ceiling_depth, ceiling_panel_id = (
                self._get_visible_side_special_ceiling_geometry(
                    zone=zone,
                    side=side,
                    depth=visible_depth.depth,
                    next_zone=next_zone,
                )
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

    def _build_center_wall_endcap_commands(
        self,
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
            self._build_side_back_wall_endcaps(
                depth=depth,
                side="left",
                side_tile=left_tile,
                forward_tile=left_forward_tile,
                outer_tile=left_outer_tile,
                blocker_rect=zone.left_side_blocker_rect,
                darkness=darkness,
                texture_key=self.textures.get_wall_key(
                    left_outer_tile if is_wall(left_outer_tile) else left_forward_tile
                ),
            )
        )
        commands.extend(
            self._build_side_back_wall_endcaps(
                depth=depth,
                side="right",
                side_tile=right_tile,
                forward_tile=right_forward_tile,
                outer_tile=right_outer_tile,
                blocker_rect=zone.right_side_blocker_rect,
                darkness=darkness,
                texture_key=self.textures.get_wall_key(
                    right_outer_tile if is_wall(right_outer_tile) else right_forward_tile
                ),
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
        texture_key: str = "wall",
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
                    texture_key=texture_key,
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
                        texture_key=(
                            "door_open" if getattr(side_tile, "open", False) else "door_closed"
                        ),
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
                    texture_key=self.textures.get_wall_key(side_tile),
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
                    texture_key=self.textures.get_wall_key(side_forward_tile),
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
                        texture_key=self.textures.get_wall_key(
                            outer_wall_tile if is_wall(outer_wall_tile) else side_forward_tile
                        ),
                    )
                )
        elif is_wall(outer_wall_tile) and continuation_quad is not None:
            outer_texture_key = self.textures.get_wall_key(outer_wall_tile)
            if self._is_door_tile(outer_wall_tile):
                outer_texture_key = (
                    "door_open" if getattr(outer_wall_tile, "open", False) else "door_closed"
                )
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
                        texture_key=self.textures.get_wall_key(outer_wall_tile),
                        quad=bridge_quad,
                        darkness=darkness,
                    )
                )

        return commands

    @staticmethod
    def _push_outer_wall_quad(
        quad: Quad, side: str, base_offset: float, edge_offset: float
    ) -> Quad:
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
    def _push_outer_ceiling_quad(
        quad: Quad, side: str, base_offset: float, edge_offset: float
    ) -> Quad:
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
    def _push_outer_floor_quad(
        quad: Quad, side: str, base_offset: float, edge_offset: float
    ) -> Quad:
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
