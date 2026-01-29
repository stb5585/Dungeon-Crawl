# effects/base.py
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from character import Character
    from combat_result import CombatResult


class Effect(ABC):
    """Base class for all effects that can be applied in combat."""

    @abstractmethod
    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        """Apply the effect to the target character."""
        pass
