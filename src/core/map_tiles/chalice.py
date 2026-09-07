"""Golden Chalice world-state transitions.

This module owns the concrete tile replacement needed by the Chalice quest.
Keeping it separate from :mod:`rules` lets foundational path tiles depend on
rules without rules importing path or room implementations back.
"""

from .paths import CavePath
from .rooms import GoldenChaliceRoom
from .rules import (
    CHALICE_LOCATION_POS,
    CHALICE_QUEST_NAME,
    _ensure_chalice_progress,
    _replace_tile,
    chalice_altar_visible,
    sync_chalice_map_description,
)


def update_chalice_location(game):
    """Hide or reveal the Golden Chalice altar based on quest progression."""
    player_char = game.player_char
    quest_data = player_char.quest_dict.get("Side", {}).get(CHALICE_QUEST_NAME)
    progress = _ensure_chalice_progress(quest_data)
    sync_chalice_map_description(player_char)
    pos = CHALICE_LOCATION_POS
    tile = player_char.world_dict.get(pos)
    if tile is None:
        return

    should_reveal = chalice_altar_visible(player_char)
    if should_reveal:
        if not isinstance(tile, GoldenChaliceRoom):
            new_tile = GoldenChaliceRoom(*pos)
            new_tile.enter = False
            _replace_tile(player_char.world_dict, pos, new_tile)
            if progress is not None:
                progress["Spawned"] = True
            if (player_char.location_x, player_char.location_y, player_char.location_z) == pos:
                game.special_event("Chalice Revealed")
        else:
            tile.enter = False
    elif isinstance(tile, GoldenChaliceRoom):
        tile.enter = True
        _replace_tile(player_char.world_dict, pos, CavePath(*pos))
