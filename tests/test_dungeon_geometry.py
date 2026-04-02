from __future__ import annotations

from src.ui_pygame.gui.dungeon.geometry import (
    build_depth_rect,
    build_next_depth_rect,
    build_zone_geometry,
)


def test_build_depth_rects_are_centered():
    depth1 = build_depth_rect(1024, 600, 1)
    depth2 = build_depth_rect(1024, 600, 2)
    depth3 = build_depth_rect(1024, 600, 3)

    assert depth1.x == 0
    assert depth1.y == 0
    assert depth1.w == 1024
    assert depth1.h == 600

    assert abs(depth2.x - 256) < 1e-6
    assert abs(depth2.y - 150) < 1e-6
    assert abs(depth2.w - 512) < 1e-6
    assert abs(depth2.h - 300) < 1e-6

    assert abs(depth3.x - 384) < 1e-6
    assert abs(depth3.y - 225) < 1e-6
    assert abs(depth3.w - 256) < 1e-6
    assert abs(depth3.h - 150) < 1e-6


def test_zone_geometry_has_expected_perspective_shapes():
    rect = build_depth_rect(1024, 600, 1)
    next_rect = build_next_depth_rect(rect)
    zone = build_zone_geometry(rect, next_rect, depth=1)

    center_floor_bottom_width = zone.center_floor.points[1][0] - zone.center_floor.points[0][0]
    center_floor_top_width = zone.center_floor.points[2][0] - zone.center_floor.points[3][0]
    assert center_floor_bottom_width > center_floor_top_width
    assert zone.center_floor.points[0][0] < rect.left
    assert zone.center_floor.points[1][0] > rect.right
    assert zone.center_floor.points[3][0] < next_rect.left
    assert zone.center_floor.points[2][0] > next_rect.right

    left_floor_bottom_width = zone.left_floor_open.points[1][0] - zone.left_floor_open.points[0][0]
    left_floor_top_width = zone.left_floor_open.points[2][0] - zone.left_floor_open.points[3][0]
    right_floor_bottom_width = zone.right_floor_open.points[1][0] - zone.right_floor_open.points[0][0]
    right_floor_top_width = zone.right_floor_open.points[2][0] - zone.right_floor_open.points[3][0]

    assert left_floor_bottom_width > left_floor_top_width
    assert right_floor_bottom_width > right_floor_top_width
    assert abs(zone.left_wall.points[1][0] - zone.back_wall_rect.left) < 1e-6
    assert abs(zone.left_wall.points[2][0] - zone.back_wall_rect.left) < 1e-6
    assert abs(zone.right_wall.points[0][0] - zone.back_wall_rect.right) < 1e-6
    assert abs(zone.right_wall.points[3][0] - zone.back_wall_rect.right) < 1e-6
