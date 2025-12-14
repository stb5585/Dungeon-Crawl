# effects/damage.py
from __future__ import annotations
from typing import TYPE_CHECKING

from .base import Effect

if TYPE_CHECKING:
    from character import Character
    from combat_result import CombatResult


class DamageEffect(Effect):
    """Effect that applies damage to a target character."""

    def __init__(self, base_damage: int, scaling: float = 1.0):
        self.base_damage = base_damage
        self.scaling = scaling

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        damage = int(self.base_damage + actor.strength * self.scaling)
        target.hp -= damage
        result.damage = damage
