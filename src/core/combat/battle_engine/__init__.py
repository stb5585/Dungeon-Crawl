"""Public battle-engine API.

The concrete engine composes focused turn-flow, action, and outcome behavior.
Existing imports from the battle-engine package remain supported.
"""

from .core import BattleEngine
from .models import ActionResult, BattleOutcome, ForcedAction, PostTurnResult, PreTurnResult

from ..battle_logger import BattleLogger
from ..encounter import CombatEncounter, EncounterEnemy, EnemyResolution, EnemyResolutionRecord
from ..initiative import determine_initiative
from ... import items, thieves_guild
from ...constants import SPECIAL_ATTACK_LUCK_FACTOR, SPECIAL_ATTACK_ROLL_MAX
from ...classes import (
    ability_mechanics,
    astromancer,
    bard,
    berserker,
    class_rings,
    dragoon,
    grandmaster,
    lycan,
    nature_totems,
    paladin,
    promotion_kits,
    wizard,
)
from ...enemies.identity import remember_defeat_identity, restore_defeat_identity
from ...events.event_bus import EventType, create_combat_event, get_event_bus
from .actions import STOLEN_SCROLL_CHOICE_PREFIX, inspect, random, re
