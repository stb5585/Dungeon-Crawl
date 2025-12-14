# effects/status.py
from __future__ import annotations
from typing import TYPE_CHECKING

from .base import Effect

if TYPE_CHECKING:
    from character import Character
    from combat_result import CombatResult


class StatusEffect(Effect):
    """Base class for status effects that can be applied to characters."""

    def __init__(self, name: str, duration: int):
        self.name = name
        self.duration = duration

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        """Apply the status effect to the target character."""
        if self.name in target.status_effects:
            target.status_effects[self.name].active = True
            target.status_effects[self.name].duration = self.duration
            result.effects_applied['Status'].append(self.name)
            result.extra['status_effect'] = self.name
