"""
Conditional and Composite Effects

This module contains advanced effect types that combine multiple effects
or trigger based on conditions.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Callable
from .base import Effect

if TYPE_CHECKING:
    from character import Character
    from combat_result import CombatResult


class ConditionalEffect(Effect):
    """
    An effect that only applies if a condition is met.
    
    Example: "Deal extra damage if target is poisoned"
    """
    
    def __init__(self, condition: Callable, effect: Effect):
        """
        Args:
            condition: Function that takes (actor, target, result) and returns bool
            effect: The effect to apply if condition is True
        """
        self.condition = condition
        self.effect = effect
    
    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        """Apply the effect only if the condition is met."""
        if self.condition(actor, target, result):
            self.effect.apply(actor, target, result)


class CompositeEffect(Effect):
    """
    Combines multiple effects into a single effect.
    
    Example: Fireball deals damage AND applies burn
    """
    
    def __init__(self, effects: list[Effect]):
        """
        Args:
            effects: List of effects to apply
        """
        self.effects = effects
    
    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        """Apply all effects in sequence."""
        for effect in self.effects:
            effect.apply(actor, target, result)


class ChanceEffect(Effect):
    """
    An effect that has a chance to apply based on probability.
    
    Example: "30% chance to stun"
    """
    
    def __init__(self, effect: Effect, chance: float):
        """
        Args:
            effect: The effect to potentially apply
            chance: Probability of applying (0.0 to 1.0)
        """
        self.effect = effect
        self.chance = chance
    
    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        """Apply the effect based on random chance."""
        import random
        
        if random.random() < self.chance:
            self.effect.apply(actor, target, result)
            result.extra['chance_effect_triggered'] = True
        else:
            result.extra['chance_effect_triggered'] = False


class ScalingEffect(Effect):
    """
    An effect whose magnitude scales with character stats or conditions.
    
    Example: "Damage scales with missing health"
    """
    
    def __init__(self, base_effect: Effect, scaling_func: Callable):
        """
        Args:
            base_effect: The base effect to apply
            scaling_func: Function that takes (actor, target) and returns a multiplier
        """
        self.base_effect = base_effect
        self.scaling_func = scaling_func
    
    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        """Apply the effect with scaling."""
        multiplier = self.scaling_func(actor, target)
        
        # Modify the base effect's magnitude
        if hasattr(self.base_effect, 'base_damage'):
            original_damage = self.base_effect.base_damage
            self.base_effect.base_damage = int(original_damage * multiplier)
            self.base_effect.apply(actor, target, result)
            self.base_effect.base_damage = original_damage  # Restore original
        elif hasattr(self.base_effect, 'base_healing'):
            original_healing = self.base_effect.base_healing
            self.base_effect.base_healing = int(original_healing * multiplier)
            self.base_effect.apply(actor, target, result)
            self.base_effect.base_healing = original_healing
        else:
            # Default: just apply the effect
            self.base_effect.apply(actor, target, result)


class LifestealEffect(Effect):
    """
    Heals the actor for a percentage of damage dealt.
    """
    
    def __init__(self, lifesteal_percent: float):
        """
        Args:
            lifesteal_percent: Percentage of damage to heal (0.0 to 1.0)
        """
        self.lifesteal_percent = lifesteal_percent
    
    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        """Heal actor based on damage dealt."""
        if result.damage and result.damage > 0:
            heal_amount = int(result.damage * self.lifesteal_percent)
            actor.health.current = min(
                actor.health.max,
                actor.health.current + heal_amount
            )
            result.extra['lifesteal'] = heal_amount
            result.healing = heal_amount


class ReflectDamageEffect(Effect):
    """
    Reflects a portion of damage back to the attacker.
    """
    
    def __init__(self, reflect_percent: float, duration: int):
        """
        Args:
            reflect_percent: Percentage of damage to reflect (0.0 to 1.0)
            duration: Number of turns the effect lasts
        """
        self.reflect_percent = reflect_percent
        self.duration = duration
    
    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        """Apply reflect buff to target."""
        target.magic_effects["Reflect"].active = True
        target.magic_effects["Reflect"].duration = self.duration
        target.magic_effects["Reflect"].extra = int(self.reflect_percent * 100)
        result.effects_applied['Magic'].append('Reflect')


class DamageOverTimeEffect(Effect):
    """
    Applies damage over multiple turns.
    
    Examples: Poison, Burn, Bleed
    """
    
    def __init__(
        self,
        dot_type: str,
        damage_per_tick: int,
        duration: int,
        element: str = 'Physical'
    ):
        """
        Args:
            dot_type: Type of DOT ('Poison', 'Burn', 'Bleed', etc.)
            damage_per_tick: Damage dealt each turn
            duration: Number of turns the effect lasts
            element: Damage type for resistance calculations
        """
        self.dot_type = dot_type
        self.damage_per_tick = damage_per_tick
        self.duration = duration
        self.element = element
    
    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        """Apply the DOT effect to target."""
        # Check if using status_effects (e.g., Poison) or magic_effects (DOT)
        if self.dot_type in target.status_effects:
            target.status_effects[self.dot_type].active = True
            target.status_effects[self.dot_type].duration = self.duration
            target.status_effects[self.dot_type].extra = self.damage_per_tick
            result.effects_applied['Status'].append(self.dot_type)
        else:
            # Use generic DOT magic effect
            target.magic_effects["DOT"].active = True
            target.magic_effects["DOT"].duration = self.duration
            target.magic_effects["DOT"].extra = self.damage_per_tick
            result.effects_applied['Magic'].append(f'DOT ({self.dot_type})')
            result.extra['dot_type'] = self.dot_type


class DispelEffect(Effect):
    """
    Removes buffs or debuffs from target.
    """
    
    def __init__(self, dispel_type: str = 'all'):
        """
        Args:
            dispel_type: What to dispel ('buffs', 'debuffs', 'all')
        """
        self.dispel_type = dispel_type
    
    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        """Remove effects from target."""
        dispelled = []
        
        # Dispel stat effects
        for stat_name, effect in target.stat_effects.items():
            if effect.active:
                if self.dispel_type == 'all':
                    effect.active = False
                    effect.duration = 0
                    effect.extra = 0
                    dispelled.append(stat_name)
                elif self.dispel_type == 'buffs' and effect.extra > 0:
                    effect.active = False
                    effect.duration = 0
                    effect.extra = 0
                    dispelled.append(stat_name)
                elif self.dispel_type == 'debuffs' and effect.extra < 0:
                    effect.active = False
                    effect.duration = 0
                    effect.extra = 0
                    dispelled.append(stat_name)
        
        result.extra['dispelled'] = dispelled


class ShieldEffect(Effect):
    """
    Grants a shield that absorbs damage.
    """
    
    def __init__(self, shield_amount: int, duration: int):
        """
        Args:
            shield_amount: Amount of damage the shield can absorb
            duration: Number of turns the shield lasts
        """
        self.shield_amount = shield_amount
        self.duration = duration
    
    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        """Apply shield to target."""
        target.magic_effects["Mana Shield"].active = True
        target.magic_effects["Mana Shield"].duration = self.duration
        # Note: Current implementation uses mana as shield, might need adjustment
        result.effects_applied['Magic'].append('Shield')
        result.extra['shield_amount'] = self.shield_amount
