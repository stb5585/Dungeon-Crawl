# effects/damage.py
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Effect

if TYPE_CHECKING:
    from src.core.character import Character
    from src.core.combat.combat_result import CombatResult


class DamageEffect(Effect):
    """Effect that applies damage to a target character."""

    def __init__(self, base_damage: int, scaling: float = 1.0):
        self.base_damage = base_damage
        self.scaling = scaling

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        stats = getattr(actor, "stats", None)
        strength = getattr(stats, "strength", getattr(actor, "strength", 0))
        damage = max(0, int(self.base_damage + strength * self.scaling))

        health = getattr(target, "health", None)
        if health is not None and hasattr(health, "current"):
            health.current = max(0, health.current - damage)
        elif hasattr(target, "hp"):
            target.hp = max(0, target.hp - damage)
        else:
            raise AttributeError("DamageEffect target requires health.current or hp")

        result.damage = (result.damage or 0) + damage
        result.extra["last_damage"] = damage
