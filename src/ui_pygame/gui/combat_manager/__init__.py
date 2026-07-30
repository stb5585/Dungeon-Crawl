"""Public exports for the combat manager package."""

import random

import pygame

from src.core import enemies
from src.core.classes import astromancer, demonologist
from src.core.combat.battle_engine import BattleEngine, STOLEN_SCROLL_CHOICE_PREFIX
from src.core.player import LIMINAL_GAP_ENTRY_FACING, LIMINAL_GAP_ENTRY_POS
from ..character_naming import CompanionNamingScreen
from ..combat_view import CombatView
from ..input_guards import release_guard_allows_input
from ..level_up import LevelUpScreen
from .constants import COMBAT_START_TRANSITION_FRAMES, POST_TURN_DELAY_FRAMES, SLOT_SYMBOL_ATLAS
from .manager import GUICombatManager


__all__ = [
    "astromancer",
    "BattleEngine",
    "COMBAT_START_TRANSITION_FRAMES",
    "CombatView",
    "CompanionNamingScreen",
    "demonologist",
    "enemies",
    "GUICombatManager",
    "LevelUpScreen",
    "LIMINAL_GAP_ENTRY_FACING",
    "LIMINAL_GAP_ENTRY_POS",
    "POST_TURN_DELAY_FRAMES",
    "pygame",
    "random",
    "release_guard_allows_input",
    "SLOT_SYMBOL_ATLAS",
    "STOLEN_SCROLL_CHOICE_PREFIX",
]
