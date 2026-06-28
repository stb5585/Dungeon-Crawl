# effects/status.py
from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Effect

if TYPE_CHECKING:
    from src.core.character import Character
    from src.core.combat.combat_result import CombatResult


class StatusEffect(Effect):
    """Base class for status effects that can be applied to characters."""

    def __init__(self, name: str, duration: int):
        self.name = name
        self.duration = duration

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        """Apply the status effect to the target character."""
        has_protection = getattr(target, "has_status_protection", None)
        if callable(has_protection) and has_protection(self.name):
            result.extra["status_immune"] = self.name
            return
        if self.name in target.status_effects:
            target.status_effects[self.name].active = True
            target.status_effects[self.name].duration = self.duration
            result.effects_applied.setdefault('Status', []).append(self.name)
            result.extra['status_effect'] = self.name
