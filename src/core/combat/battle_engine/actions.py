"""Compatibility composition for battle action behavior."""

import inspect as inspect
import random as random
import re as re

from .action_attacks import AttackActionMixin
from .action_inventory import InventoryActionMixin
from .action_skills import SkillActionMixin
from .action_spells import STOLEN_SCROLL_CHOICE_PREFIX as STOLEN_SCROLL_CHOICE_PREFIX
from .action_spells import SpellActionMixin

__all__ = [
    "BattleActionMixin",
    "inspect",
    "random",
    "re",
    "STOLEN_SCROLL_CHOICE_PREFIX",
]


class BattleActionMixin(
    AttackActionMixin,
    SpellActionMixin,
    SkillActionMixin,
    InventoryActionMixin,
):
    """Compose focused attack, spell, skill, and inventory actions."""
