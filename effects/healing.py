# effects/healing.py
from __future__ import annotations
from typing import TYPE_CHECKING

from .base import Effect

if TYPE_CHECKING:
    from character import Character
    from combat_result import CombatResult


class HealEffect(Effect):
    """Effect that applies healing to a target character."""

    def __init__(self, base_healing: int, scaling: float = 1.0):
        self.base_healing = base_healing
        self.scaling = scaling

    def apply(self, user: Character, target: Character, result: CombatResult) -> None:
        heal_amount = int(self.base_healing + user.stats.wisdom * self.scaling)
        target.health.current = min(target.health.max, target.health.current + heal_amount)
        result.healing = heal_amount


class RegenEffect(Effect):
    """Effect that applies regeneration to a target character over time."""

    def __init__(self, base_healing: int, duration: int, scaling: float = 1.0):
        self.base_healing = base_healing
        self.duration = duration
        self.scaling = scaling

    def apply(self, user: Character, target: Character, result: CombatResult) -> None:
        healing_per_tick = int(self.base_healing + user.stats.wisdom * self.scaling)
        target.magic_effects["Regen"].active = True
        target.magic_effects["Regen"].duration = self.duration
        target.magic_effects["Regen"].extra = healing_per_tick
        result.effects_applied['Magic'].append('Regen')
