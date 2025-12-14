"""
Buff and Debuff Effects

This module contains effects that modify character stats temporarily.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from .base import Effect

if TYPE_CHECKING:
    from character import Character
    from combat_result import CombatResult


class StatModifierEffect(Effect):
    """
    Base class for effects that modify character stats.
    
    Attributes:
        stat_name: Name of the stat to modify ('attack', 'defense', 'magic', etc.)
        modifier: Amount to modify (can be negative for debuffs)
        duration: Number of turns the effect lasts
        is_percentage: If True, modifier is a percentage multiplier
    """
    
    def __init__(
        self,
        stat_name: str,
        modifier: int | float,
        duration: int,
        is_percentage: bool = False
    ):
        self.stat_name = stat_name
        self.modifier = modifier
        self.duration = duration
        self.is_percentage = is_percentage
    
    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        """Apply the stat modification to the target."""
        # Check if target already has this effect
        effect_key = self.stat_name.title()
        
        if target.stat_effects[effect_key].active:
            # Effect already active, refresh or stack
            target.stat_effects[effect_key].duration = max(
                target.stat_effects[effect_key].duration,
                self.duration
            )
            # Stack the modifier
            target.stat_effects[effect_key].extra += self.modifier
        else:
            # Apply new effect
            target.stat_effects[effect_key].active = True
            target.stat_effects[effect_key].duration = self.duration
            target.stat_effects[effect_key].extra = self.modifier
        
        result.effects_applied['Stat'].append(f"{effect_key} {'Buff' if self.modifier > 0 else 'Debuff'}")


class AttackBuffEffect(StatModifierEffect):
    """Increases target's attack stat."""
    
    def __init__(self, amount: int, duration: int):
        super().__init__('attack', amount, duration)


class AttackDebuffEffect(StatModifierEffect):
    """Decreases target's attack stat."""
    
    def __init__(self, amount: int, duration: int):
        super().__init__('attack', -amount, duration)


class DefenseBuffEffect(StatModifierEffect):
    """Increases target's defense stat."""
    
    def __init__(self, amount: int, duration: int):
        super().__init__('defense', amount, duration)


class DefenseDebuffEffect(StatModifierEffect):
    """Decreases target's defense stat."""
    
    def __init__(self, amount: int, duration: int):
        super().__init__('defense', -amount, duration)


class MagicBuffEffect(StatModifierEffect):
    """Increases target's magic stat."""
    
    def __init__(self, amount: int, duration: int):
        super().__init__('magic', amount, duration)


class MagicDebuffEffect(StatModifierEffect):
    """Decreases target's magic stat."""
    
    def __init__(self, amount: int, duration: int):
        super().__init__('magic', -amount, duration)


class SpeedBuffEffect(StatModifierEffect):
    """Increases target's speed stat."""
    
    def __init__(self, amount: int, duration: int):
        super().__init__('speed', amount, duration)


class SpeedDebuffEffect(StatModifierEffect):
    """Decreases target's speed stat."""
    
    def __init__(self, amount: int, duration: int):
        super().__init__('speed', -amount, duration)


class MultiStatBuffEffect(Effect):
    """
    Applies buffs to multiple stats at once.
    Useful for abilities like "Blessing" or "Rally".
    """
    
    def __init__(self, stat_modifiers: dict[str, int], duration: int):
        """
        Args:
            stat_modifiers: Dict mapping stat names to modifier amounts
                           e.g., {'attack': 10, 'defense': 5}
            duration: Number of turns the effect lasts
        """
        self.stat_modifiers = stat_modifiers
        self.duration = duration
    
    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        """Apply all stat modifications to the target."""
        for stat_name, modifier in self.stat_modifiers.items():
            effect = StatModifierEffect(stat_name, modifier, self.duration)
            effect.apply(actor, target, result)


class ResistanceEffect(Effect):
    """
    Modifies elemental or damage type resistance.
    
    Attributes:
        element: Type of resistance ('Fire', 'Ice', 'Physical', etc.)
        amount: Resistance value (0.0 to 1.0, where 1.0 = immune)
        duration: Number of turns the effect lasts
    """
    
    def __init__(self, element: str, amount: float, duration: int):
        self.element = element
        self.amount = amount
        self.duration = duration
    
    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        """Apply the resistance modification."""
        effect_key = f"Resist {self.element}"
        
        if target.magic_effects[effect_key].active:
            # Refresh duration and stack resistance
            target.magic_effects[effect_key].duration = max(
                target.magic_effects[effect_key].duration,
                self.duration
            )
            # Don't exceed 100% resistance from stacking
            current_resist = target.magic_effects[effect_key].extra
            target.magic_effects[effect_key].extra = min(1.0, current_resist + self.amount)
        else:
            target.magic_effects[effect_key].active = True
            target.magic_effects[effect_key].duration = self.duration
            target.magic_effects[effect_key].extra = self.amount
        
        result.effects_applied['Magic'].append(f"{effect_key}")
