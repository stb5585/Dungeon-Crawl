"""Public player API.

Implementation, behavior mixins, and support helpers live in focused
submodules. Existing imports from ``src.core.player`` remain supported.
"""

from src.paths import MAP_FILES_DIR, PROJECT_ROOT
from .. import abilities
from ..constants import TOWN_LOCATION
from .config import (
    BASIC_BESTIARY_ACTIONS,
    DIRECTIONS,
    LIMINAL_GAP_ENTRY_FACING,
    LIMINAL_GAP_ENTRY_POS,
    LIMINAL_GAP_LEVEL,
    REALM_OF_CAMBION_LEVEL,
    RESISTANCE_DISPLAY_ORDER,
)
from .core import Player
from .maps import (
    _extract_tile_type,
    _load_tiled_map,
    _load_tiled_tileset,
    _parse_tiled_properties,
    _select_tiled_gameplay_layer,
    _tiled_bool,
)
from .persistence import load_char, os
from .stats import (
    GAMEPLAY_STATS_DEFAULTS,
    _upgrade_source_name,
    normalize_gameplay_stats,
    summarize_gameplay_stat_groups,
    summarize_gameplay_stats,
)
from .combat import random
