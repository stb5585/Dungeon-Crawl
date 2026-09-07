"""Public save-system API.

Serialization responsibilities and filesystem persistence live in focused
modules. Existing imports from the save-system package remain supported.
"""

from .enemy import EnemyStateSerializer
from .item_serialization import AbilitySerializer, ItemSerializer
from .manager import SaveLoadResult, SaveManager
from .migrations import (
    CURRENT_SAVE_VERSION,
    SUPPORTED_LEGACY_SAVE_VERSIONS,
    InvalidSaveDataError,
    SaveMigration,
    UnsupportedSaveVersionError,
    migrate_save_data,
)
from .models import CombatData, LevelData, ResourceData, StatsData, StatusEffectData
from .player import PlayerDataSerializer
from .quests import QuestDataSerializer
from .summons import SummonSerializer
from .tiles import TileStateSerializer

from .. import (
    abilities,
    enemies,
    items,
    main_story,
    quest_progress,
    thieves_guild,
    town as town_core,
)
from ..character import Combat, Level, Resource, Stats
from ..classes import promotion_kits
from .manager import json, os
