#!/usr/bin/env python3
"""
Smoke tests for core dungeon navigation behavior.
"""

from src.core.character import Combat, Level, Resource, Stats
from src.core.player import DIRECTIONS, Player


def _make_player():
    player = Player(
        5,
        10,
        1,
        level=Level(),
        health=Resource(20, 20),
        mana=Resource(10, 10),
        stats=Stats(10, 10, 10, 10, 10, 10),
        combat=Combat(attack=10, defense=10, magic=5, magic_def=5),
        gold=100,
        resistance={},
    )
    player.facing = "east"
    player.load_tiles()
    return player


def test_movement():
    player = _make_player()

    assert (player.location_x, player.location_y, player.location_z) == (5, 10, 1)
    assert player.facing == "east"
    assert len(player.world_dict) > 0

    current_tile = player.world_dict.get((player.location_x, player.location_y, player.location_z))
    assert current_tile is not None

    dx, dy = DIRECTIONS[player.facing]["move"]
    ahead_pos = (player.location_x + dx, player.location_y + dy, player.location_z)
    tile_ahead = player.world_dict.get(ahead_pos)
    assert tile_ahead is not None
    assert getattr(tile_ahead, "enter", True) is True

    old_pos = (player.location_x, player.location_y)
    player.location_x += dx
    player.location_y += dy
    new_pos = (player.location_x, player.location_y)
    new_tile = player.world_dict.get((player.location_x, player.location_y, player.location_z))

    assert new_pos != old_pos
    assert new_pos == ahead_pos[:2]
    assert new_tile is not None

    player.location_x, player.location_y = 5, 10
    movable_directions = []
    for direction in ["north", "east", "south", "west"]:
        ddx, ddy = DIRECTIONS[direction]["move"]
        tile = player.world_dict.get((5 + ddx, 10 + ddy, 1))
        if tile and getattr(tile, "enter", True):
            movable_directions.append(direction)

    assert "east" in movable_directions
    assert player.quit is False
    assert player.in_town() is False
