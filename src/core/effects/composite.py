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
    from src.core.combat.combat_result import CombatResult


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


class StatContestEffect(Effect):
    """
    An effect that only triggers if the actor wins a stat contest vs the target.

    The contest rolls ``random(actor_lo, actor_stat // actor_div)`` against
    ``random(target_stat // target_lo_div, target_stat // target_hi_div)``
    and applies the inner effect when the actor wins.

    When ``use_crit_multiplier`` is True, the actor's stat value is multiplied
    by the crit value from the last damage roll before computing the range.

    When ``actor_lo_divisor`` is set, the actor's low roll is
    ``actor_stat // actor_lo_divisor`` instead of 0.

    Example: Fire DOT triggers on ``intel//2 > wisdom//4..wisdom``
    Example: Corruption DOT uses ``(charisma*crit)//2..(charisma*crit) > wisdom//2..wisdom``
    """

    def __init__(
        self,
        effect: Effect,
        actor_stat: str = "intel",
        actor_divisor: int = 2,
        target_stat: str = "wisdom",
        target_lo_divisor: int = 4,
        target_hi_divisor: int = 1,
        actor_lo_divisor: int | None = None,
        use_crit_multiplier: bool = False,
    ):
        self.effect = effect
        self.actor_stat = actor_stat
        self.actor_divisor = actor_divisor
        self.target_stat = target_stat
        self.target_lo_divisor = target_lo_divisor
        self.target_hi_divisor = target_hi_divisor
        self.actor_lo_divisor = actor_lo_divisor
        self.use_crit_multiplier = use_crit_multiplier

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random

        a_val = getattr(actor.stats, self.actor_stat, 10)
        t_val = getattr(target.stats, self.target_stat, 10)

        if self.use_crit_multiplier:
            crit = result.extra.get("last_crit", 1)
            a_val = int(a_val * crit)

        if self.actor_lo_divisor is not None:
            roll_lo = max(0, a_val // self.actor_lo_divisor)
        else:
            roll_lo = 0

        roll_actor = random.randint(roll_lo, max(1, a_val // self.actor_divisor))
        roll_target = random.randint(
            max(0, t_val // self.target_lo_divisor),
            max(1, t_val // self.target_hi_divisor),
        )

        if roll_actor > roll_target:
            self.effect.apply(actor, target, result)
            result.extra['stat_contest_won'] = True
        else:
            result.extra['stat_contest_won'] = False


class DynamicDotEffect(Effect):
    """
    A DOT effect whose damage_per_tick is computed from the last damage dealt.

    Used by fire spells that set DOT damage to ``random(damage//4, damage//2)``.
    """

    def __init__(
        self,
        dot_type: str = "DOT",
        duration: int = 2,
        damage_lo_fraction: float = 0.25,
        damage_hi_fraction: float = 0.5,
    ):
        self.dot_type = dot_type
        self.duration = duration
        self.damage_lo_fraction = damage_lo_fraction
        self.damage_hi_fraction = damage_hi_fraction

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random

        last_damage = result.extra.get("last_damage", 0)
        lo = max(1, int(last_damage * self.damage_lo_fraction))
        hi = max(lo, int(last_damage * self.damage_hi_fraction))
        dmg = random.randint(lo, hi)

        target.magic_effects[self.dot_type].active = True
        target.magic_effects[self.dot_type].duration = max(
            self.duration, target.magic_effects[self.dot_type].duration
        )
        target.magic_effects[self.dot_type].extra = max(
            dmg, target.magic_effects[self.dot_type].extra
        )
        result.effects_applied["Magic"].append(f"DOT ({self.dot_type})")

        try:
            actor._emit_status_event(
                target,
                self.dot_type,
                applied=True,
                duration=target.magic_effects[self.dot_type].duration,
                source=result.action,
            )
        except Exception:
            pass


class DynamicExtraDamageEffect(Effect):
    """
    Deals bonus damage computed as a fraction of the last damage dealt.

    Used by ice spells: ``random(damage//2, damage)`` extra chill damage.
    """

    def __init__(
        self,
        damage_lo_fraction: float = 0.5,
        damage_hi_fraction: float = 1.0,
        message_template: str = "{target} is chilled to the bone, taking an extra {damage} damage.\n",
    ):
        self.damage_lo_fraction = damage_lo_fraction
        self.damage_hi_fraction = damage_hi_fraction
        self.message_template = message_template

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random

        last_damage = result.extra.get("last_damage", 0)
        lo = max(1, int(last_damage * self.damage_lo_fraction))
        hi = max(lo, int(last_damage * self.damage_hi_fraction))
        dmg = random.randint(lo, hi)

        target.health.current -= dmg
        result.extra["extra_damage"] = dmg


class StatusApplyEffect(Effect):
    """
    Applies a status effect with immunity/pendant checks (like ElectricSpell stun).

    When ``crit_only`` is True, the effect only triggers on critical hits
    (e.g., Holy's Blind on crit).
    When ``skip_if_active`` is True, the effect is skipped if the target already
    has this status active (e.g., Sleep, Stupefy).
    When ``duration_stat`` is set, duration is computed from caster stats
    (e.g., Berserk uses intel-based random duration).
    """

    def __init__(
        self,
        status_name: str,
        duration: int = 1,
        use_crit_bonus: bool = False,
        crit_only: bool = False,
        skip_if_active: bool = False,
        duration_stat: str | None = None,
        duration_stat_divisor: int = 10,
        duration_min: int = 2,
        duration_random: bool = False,
    ):
        self.status_name = status_name
        self.duration = duration
        self.use_crit_bonus = use_crit_bonus
        self.crit_only = crit_only
        self.skip_if_active = skip_if_active
        self.duration_stat = duration_stat
        self.duration_stat_divisor = duration_stat_divisor
        self.duration_min = duration_min
        self.duration_random = duration_random

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        # If crit_only, skip when there's no critical hit
        crit = result.extra.get("last_crit", 1)
        if self.crit_only and crit <= 1:
            return

        # Check immunities
        if any([
            self.status_name in getattr(target, 'status_immunity', []),
            f"Status-{self.status_name}" in getattr(
                target.equipment.get("Pendant", None), 'mod', ''
            ) if hasattr(target, 'equipment') and target.equipment.get("Pendant") else False,
            "Status-All" in getattr(
                target.equipment.get("Pendant", None), 'mod', ''
            ) if hasattr(target, 'equipment') and target.equipment.get("Pendant") else False,
        ]):
            result.extra["status_immune"] = self.status_name
            return

        # Check already active
        if self.skip_if_active and target.status_effects[self.status_name].active:
            result.extra["status_already_active"] = self.status_name
            return

        # --- Resist check (WIS/CHA matter) ---
        # Historically many statuses applied deterministically (unless immune), which made
        # "dump" mental stats (WIS/CHA) feel nearly free for non-casters. Add a lightweight
        # saving-throw contest for high-impact control effects.
        if self.status_name in {"Stun", "Sleep", "Silence", "Blind", "Stupefy", "Stone"}:
            # Offense: caster intelligence + a bit of luck
            a_stat = int(getattr(actor.stats, "intel", 10) or 0)
            a_luck = int(actor.check_mod("luck", enemy=target, luck_factor=12) or 0)
            # Defense: target wisdom + luck (luck includes WIS/CHA via check_mod)
            t_stat = int(getattr(target.stats, "wisdom", 10) or 0)
            t_luck = int(target.check_mod("luck", enemy=actor, luck_factor=10) or 0)

            actor_roll = _rng.randint(0, max(1, a_stat)) + a_luck
            target_roll = _rng.randint(0, max(1, t_stat)) + t_luck
            # Human Lust (sin): slightly reduced status resistance.
            try:
                if getattr(getattr(target, "race", None), "name", None) == "Human":
                    from src.core.constants import HUMAN_STATUS_RESIST_MULTIPLIER
                    target_roll = int(target_roll * HUMAN_STATUS_RESIST_MULTIPLIER)
            except Exception:
                pass
            if actor_roll <= target_roll:
                result.extra.setdefault("messages", []).append(
                    f"{target.name} resists {self.status_name}.\n"
                )
                result.extra["status_resisted"] = self.status_name
                return

        # Calculate duration
        if self.duration_stat:
            stat_val = getattr(actor.stats, self.duration_stat, 10)
            dynamic = stat_val // self.duration_stat_divisor
            base_dur = max(self.duration_min, dynamic)
            dur = _rng.randint(1, base_dur) if self.duration_random else base_dur
        elif self.use_crit_bonus:
            dur = self.duration + crit
        else:
            dur = self.duration

        target.status_effects[self.status_name].active = True
        target.status_effects[self.status_name].duration = max(
            dur, target.status_effects[self.status_name].duration
        )
        result.effects_applied["Status"].append(self.status_name)

        try:
            actor._emit_status_event(
                target,
                self.status_name,
                applied=True,
                duration=target.status_effects[self.status_name].duration,
                source=result.action,
            )
        except Exception:
            pass


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
            heal_amount = int(heal_amount * actor.healing_received_multiplier())
            actual_heal = min(heal_amount, actor.health.max - actor.health.current)
            actor.health.current += actual_heal
            result.extra['lifesteal'] = actual_heal
            result.healing = actual_heal


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


class DynamicStatusDotEffect(Effect):
    """
    Applies a status-based DOT (e.g. Poison) whose damage scales from the
    last damage dealt.

    Unlike ``DynamicDotEffect`` which writes to ``target.magic_effects``,
    this writes to ``target.status_effects`` for statuses like Poison that
    have their own tick logic in the game loop.

    Optionally multiplies damage by a fraction of ``target.health.max``
    (e.g., PoisonBreath: ``damage * max_hp * 0.005``).

    The duration can be stat-based (e.g. ``max(duration_min, stat // 10)``).
    """

    def __init__(
        self,
        status_name: str = "Poison",
        duration: int = 2,
        duration_min: int = 2,
        duration_stat: str | None = None,
        duration_stat_divisor: int = 10,
        damage_lo_fraction: float = 1.0,
        damage_hi_fraction: float = 1.0,
        health_multiplier: float | None = None,
    ):
        self.status_name = status_name
        self.duration = duration
        self.duration_min = duration_min
        self.duration_stat = duration_stat
        self.duration_stat_divisor = duration_stat_divisor
        self.damage_lo_fraction = damage_lo_fraction
        self.damage_hi_fraction = damage_hi_fraction
        self.health_multiplier = health_multiplier

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random

        # Check immunities
        if any([
            self.status_name in getattr(target, 'status_immunity', []),
            f"Status-{self.status_name}" in getattr(
                target.equipment.get("Pendant", None), 'mod', ''
            ) if hasattr(target, 'equipment') and target.equipment.get("Pendant") else False,
            "Status-All" in getattr(
                target.equipment.get("Pendant", None), 'mod', ''
            ) if hasattr(target, 'equipment') and target.equipment.get("Pendant") else False,
        ]):
            return

        # Compute duration
        if self.duration_stat:
            stat_val = getattr(actor.stats, self.duration_stat, 10)
            dur = max(self.duration_min, stat_val // self.duration_stat_divisor)
        else:
            dur = self.duration

        # Compute damage per tick
        last_damage = result.extra.get("last_damage", 0)
        lo = max(1, int(last_damage * self.damage_lo_fraction))
        hi = max(lo, int(last_damage * self.damage_hi_fraction))
        dmg = random.randint(lo, hi) if lo != hi else lo

        if self.health_multiplier is not None:
            dmg = int(dmg * (target.health.max * self.health_multiplier))

        target.status_effects[self.status_name].active = True
        target.status_effects[self.status_name].duration = max(
            dur, target.status_effects[self.status_name].duration
        )
        target.status_effects[self.status_name].extra = max(
            dmg, target.status_effects[self.status_name].extra
        )
        result.effects_applied["Status"].append(self.status_name)

        try:
            actor._emit_status_event(
                target,
                self.status_name,
                applied=True,
                duration=target.status_effects[self.status_name].duration,
                source=result.action,
            )
        except Exception:
            pass


class MagicEffectApplyEffect(Effect):
    """
    Applies a named magic_effect to the target (IceBlock, Duplicates, Reflect,
    Astral Shift, etc.).  Duration can be fixed or stat-based.
    """

    def __init__(
        self,
        effect_name: str,
        duration: int = 3,
        duration_stat: str | None = None,
        duration_stat_divisor: int = 10,
        duration_stat_mode: str = "add",
    ):
        self.effect_name = effect_name
        self.duration = duration
        self.duration_stat = duration_stat
        self.duration_stat_divisor = duration_stat_divisor
        self.duration_stat_mode = duration_stat_mode  # "add" or "max"

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        if self.duration_stat:
            stat_val = getattr(actor.stats, self.duration_stat, 10)
            dynamic = stat_val // self.duration_stat_divisor
            if self.duration_stat_mode == "add":
                dur = self.duration + dynamic
            else:
                dur = max(self.duration, dynamic)
        else:
            dur = self.duration

        target.magic_effects[self.effect_name].active = True
        target.magic_effects[self.effect_name].duration = max(
            dur, target.magic_effects[self.effect_name].duration
        )
        result.effects_applied["Magic"].append(self.effect_name)

        try:
            actor._emit_status_event(
                target, self.effect_name, applied=True,
                duration=target.magic_effects[self.effect_name].duration,
                source=result.action,
            )
        except Exception:
            pass


class DynamicStatBuffEffect(Effect):
    """
    Applies a single-stat buff whose amount is computed from character stats
    at cast time.  Pattern: ``random(source_val // lo_div, source_val // hi_div)``.

    Used by Boost (Magic), Shell (Magic Defense), WindSpeed (Speed),
    DivineProtection (Defense).
    """

    def __init__(
        self,
        buff_stat: str,
        source: str = "target_combat",
        source_stat: str = "attack",
        lo_divisor: int = 4,
        hi_divisor: int = 2,
        duration: int = 3,
        duration_stat: str | None = None,
        duration_divisor: int = 10,
        duration_min: int = 3,
        apply_to_caster: bool = False,
    ):
        self.buff_stat = buff_stat
        self.source = source
        self.source_stat = source_stat
        self.lo_divisor = lo_divisor
        self.hi_divisor = hi_divisor
        self.duration = duration
        self.duration_stat = duration_stat
        self.duration_divisor = duration_divisor
        self.duration_min = duration_min
        self.apply_to_caster = apply_to_caster

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        if self.source == "target_combat":
            obj = actor.combat if self.apply_to_caster else target.combat
            source_val = getattr(obj, self.source_stat, 10)
        else:
            source_val = getattr(actor.stats, self.source_stat, 10)

        lo = max(1, source_val // self.lo_divisor)
        hi = max(lo, source_val // self.hi_divisor)
        amount = _rng.randint(lo, hi)

        if self.duration_stat:
            stat_val = getattr(actor.stats, self.duration_stat, 10)
            dur = max(self.duration_min, stat_val // self.duration_divisor)
        else:
            dur = self.duration

        apply_target = actor if self.apply_to_caster else target
        apply_target.stat_effects[self.buff_stat].active = True
        apply_target.stat_effects[self.buff_stat].duration = max(
            dur, apply_target.stat_effects[self.buff_stat].duration
        )
        apply_target.stat_effects[self.buff_stat].extra = amount

        result.effects_applied["Stat"].append(f"{self.buff_stat} Buff")
        result.extra.setdefault("buff_amounts", {})[self.buff_stat] = amount


class DynamicMultiDebuffEffect(Effect):
    """
    Applies multi-stat debuffs whose amounts scale with both target and caster
    stats.  Used by WeakenMind and Enfeeble.

    Formula per stat:
        amount   = target.combat.<combat_attr> // amount_divisor
        dv       = actor.stats.<scaling_stat> // scaling_divisor
        lo       = amount // max(2, 9 - dv)
        hi       = amount // max(1, 5 - dv)
        debuff   = random(lo, hi)
        duration = max(duration_min, dv)
    """

    def __init__(
        self,
        stats: list[dict],
        scaling_stat: str = "intel",
        scaling_divisor: int = 10,
        amount_divisor: int = 10,
        duration_min: int = 3,
    ):
        self.stats = stats
        self.scaling_stat = scaling_stat
        self.scaling_divisor = scaling_divisor
        self.amount_divisor = amount_divisor
        self.duration_min = duration_min

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        dv = getattr(actor.stats, self.scaling_stat, 10) // self.scaling_divisor
        dur = max(self.duration_min, dv)

        for spec in self.stats:
            stat_name = spec["stat_name"]
            combat_attr = spec["combat_attr"]
            amount = getattr(target.combat, combat_attr, 10) // self.amount_divisor
            lo = amount // max(2, 9 - dv)
            hi = amount // max(1, 5 - dv)
            stat_mod = _rng.randint(max(0, lo), max(1, hi))

            target.stat_effects[stat_name].active = True
            target.stat_effects[stat_name].duration = dur
            target.stat_effects[stat_name].extra = -stat_mod

            result.effects_applied["Stat"].append(f"{stat_name} Debuff")
            result.extra.setdefault("messages", []).append(
                f"{target.name}'s {stat_name.lower()} is lowered by {stat_mod}."
            )


class CleanseEffect(Effect):
    """Clears all ``status_effects`` (Blind, Stun, Sleep, Poison, etc.)."""

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        for name in list(target.status_effects):
            if target.status_effects[name].active:
                target.status_effects[name].active = False
                result.effects_applied.setdefault("Cleansed", []).append(name)


class FullDispelEffect(Effect):
    """
    Removes all positive buffs from the target: specified ``magic_effects``
    (Regen, Reflect by default) **and** all ``stat_effects``.
    """

    def __init__(
        self,
        magic_effects: list[str] | None = None,
    ):
        self.magic_effects_to_clear = magic_effects or ["Regen", "Reflect"]

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        for name in self.magic_effects_to_clear:
            if target.magic_effects[name].active:
                target.magic_effects[name].active = False
        for name in ["Attack", "Defense", "Magic", "Magic Defense", "Speed"]:
            if target.stat_effects[name].active:
                target.stat_effects[name].active = False


class ManaDrainOnHitEffect(Effect):
    """
    After a weapon hit, drain a fraction of the target's current mana and
    give it to the actor.  Used by ManaSlice / ManaSlice2.

    Formula: ``drain_percent = (dmg_mod * crit) / divisor``
             ``mana_gain = int(target.mana.current * drain_percent)``
    """

    def __init__(self, divisor: int = 5):
        self.divisor = divisor

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        crit = result.extra.get("last_crit", 1)
        dmg_mod = result.extra.get("dmg_mod", 1.0)
        drain_per = (dmg_mod * crit) / self.divisor
        mana_gain = int(target.mana.current * drain_per)
        if mana_gain > 0:
            target.mana.current -= mana_gain
            actor.mana.current = min(actor.mana.max, actor.mana.current + mana_gain)
            result.extra.setdefault("messages", []).append(
                f"{actor.name} steals {mana_gain} mana from {target.name}.\n"
            )


class ResourceConvertEffect(Effect):
    """
    Convert a percentage of one resource (health / mana) into the other.
    Used by LifeTap (health → mana) and ManaTap (mana → health).

    ``source``: ``"health"`` or ``"mana"``
    ``target_resource``: ``"mana"`` or ``"health"``
    ``percent``: fraction of source max to convert (default 0.1 = 10%)
    ``ring_mod``: optional equipment mod that doubles the percent
    """

    def __init__(
        self,
        source: str = "health",
        target_resource: str = "mana",
        percent: float = 0.1,
        ring_mod: str | None = None,
    ):
        self.source = source
        self.target_resource = target_resource
        self.percent = percent
        self.ring_mod = ring_mod

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        # Determine effective percent (may be doubled by ring mod)
        pct = self.percent
        if self.ring_mod and hasattr(actor, "equipment"):
            if self.ring_mod in actor.equipment.get("Ring", type("", (), {"mod": ""})()).mod:
                pct *= 2

        src_pool = getattr(actor, self.source)
        dst_pool = getattr(actor, self.target_resource)

        # Check: target resource already full
        if dst_pool.current >= dst_pool.max:
            result.extra["resource_full"] = True
            result.extra.setdefault("messages", []).append(
                f"You are already at full {self.target_resource}.\n"
            )
            return

        cost = int(src_pool.max * pct)

        # For health→mana (LifeTap): need enough health
        if self.source == "health" and actor.health.current < cost:
            result.extra["insufficient_source"] = True
            result.extra.setdefault("messages", []).append(
                f"Your {self.source} is too low to use this ability.\n"
            )
            return

        # For mana→health (ManaTap): cap at current mana
        if self.source == "mana":
            cost = int(min(src_pool.max * pct, src_pool.current))

        src_pool.current -= cost
        gained = min(cost, dst_pool.max - dst_pool.current)
        dst_pool.current += gained

        result.extra["converted_amount"] = cost
        result.extra["gained_amount"] = gained
        result.extra.setdefault("messages", []).append(
            f"{actor.name} sacrifices {cost} {self.source} to restore {self.target_resource}.\n"
        )


class PhysicalEffectApplyEffect(Effect):
    """
    Applies a physical effect (Bleed, Prone, Disarm) to the target via a
    stat contest.  Supports immunity checks and duration calculation.

    For ``Bleed``: damage is calculated from actor strength * crit.
    For ``Prone``: simple boolean, respects ``target.flying``.
    For ``Disarm``: respects ``target.can_be_disarmed()``.
    """

    def __init__(
        self,
        effect_name: str,
        actor_stat: str = "strength",
        actor_lo_divisor: int = 2,
        actor_hi_divisor: int = 1,
        target_stat: str = "con",
        target_lo_divisor: int = 2,
        target_hi_divisor: int = 1,
        duration: int = 3,
        duration_stat: str | None = None,
        duration_divisor: int = 10,
        duration_min: int = 1,
        skip_if_active: bool = False,
        requires_crit: bool = False,
        use_crit_multiplier: bool = False,
        damage_multiplier: float = 0.0,
        check_flying: bool = False,
        check_disarmable: bool = False,
    ):
        self.effect_name = effect_name
        self.actor_stat = actor_stat
        self.actor_lo_divisor = actor_lo_divisor
        self.actor_hi_divisor = actor_hi_divisor
        self.target_stat = target_stat
        self.target_lo_divisor = target_lo_divisor
        self.target_hi_divisor = target_hi_divisor
        self.duration = duration
        self.duration_stat = duration_stat
        self.duration_divisor = duration_divisor
        self.duration_min = duration_min
        self.skip_if_active = skip_if_active
        self.requires_crit = requires_crit
        self.use_crit_multiplier = use_crit_multiplier
        self.damage_multiplier = damage_multiplier
        self.check_flying = check_flying
        self.check_disarmable = check_disarmable

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng

        crit = result.extra.get("last_crit", 1)

        # Gate: requires crit for prone-on-crit pattern (Slam)
        if self.requires_crit and crit <= 1:
            return

        # Gate: flying creatures can't be knocked prone
        if self.check_flying and getattr(target, "flying", False):
            return

        # Gate: disarm check
        if self.check_disarmable:
            if not hasattr(target, "can_be_disarmed") or not target.can_be_disarmed():
                result.extra.setdefault("messages", []).append(
                    f"{target.name} cannot be disarmed.\n"
                )
                return

        # Gate: skip if already active
        if self.skip_if_active and target.physical_effects[self.effect_name].active:
            result.extra.setdefault("messages", []).append(
                f"{target.name} is already affected by {self.effect_name}.\n"
            )
            return

        # Stat contest
        actor_val = getattr(actor.stats, self.actor_stat, 10)
        if self.use_crit_multiplier:
            actor_val = int(actor_val * crit * self.damage_multiplier) if self.damage_multiplier else actor_val
        actor_roll = _rng.randint(
            actor_val // self.actor_lo_divisor, actor_val // max(1, self.actor_hi_divisor)
        )
        target_val = getattr(target.stats, self.target_stat, 10)
        target_roll = _rng.randint(
            target_val // self.target_lo_divisor, target_val // max(1, self.target_hi_divisor)
        )

        if actor_roll > target_roll:
            # Calculate duration
            if self.duration_stat:
                stat_val = getattr(actor.stats, self.duration_stat, 10)
                dur = max(self.duration_min, stat_val // self.duration_divisor)
            else:
                dur = self.duration

            target.physical_effects[self.effect_name].active = True
            target.physical_effects[self.effect_name].duration = max(
                dur, target.physical_effects[self.effect_name].duration
            )

            # For Bleed: set damage amount
            if self.damage_multiplier > 0 and self.effect_name == "Bleed":
                # Always compute from raw stat — actor_val may already include
                # crit & damage_multiplier when use_crit_multiplier is True.
                raw_stat = getattr(actor.stats, self.actor_stat, 10)
                base_dmg = int(raw_stat * crit * self.damage_multiplier)
                bleed_dmg = _rng.randint(max(1, base_dmg // 4), max(1, base_dmg))
                target.physical_effects[self.effect_name].extra = max(
                    bleed_dmg, target.physical_effects[self.effect_name].extra
                )

            result.extra.setdefault("messages", []).append(
                f"{target.name} is affected by {self.effect_name}.\n"
            )
            result.extra["physical_applied"] = self.effect_name
        else:
            result.extra.setdefault("messages", []).append(
                f"{target.name} resists {self.effect_name}.\n"
            )


class InstantKillEffect(Effect):
    """
    Instant-kill effect used by death spells (Desoul, Petrify).

    Pipeline:
      1. Optional **reflect_item** check — if the target wields a named item
         in the given slot the spell is reflected back at the caster.
      2. **Immunity** — either *resist-based* (``apply_resist_multiplier``,
         full resist ≥ 1 → immune) or *status-based* (``immunity_status``,
         e.g. ``"Stone"``).
      3. **Stat contest** — actor stat (optionally multiplied by ``1-resist``)
         versus target stat + luck.
      4. On **win** → ``target.health.current = 0`` and a success message is
         appended to ``result.extra["messages"]``.
      5. On **loss** → ``result.extra["stat_contest_won"] = False``.
    """

    def __init__(
        self,
        success_message: str = "{target} is slain.",
        actor_stat: str = "charisma",
        actor_divisor: int = 1,
        target_stat: str = "con",
        target_lo_divisor: int = 2,
        target_hi_divisor: int = 1,
        apply_resist_multiplier: bool = True,
        resist_type: str = "Death",
        luck_factor: int = 10,
        immunity_status: str | None = None,
        reflect_item: str | None = None,
        reflect_slot: str = "OffHand",
        reflect_message: str = "",
    ):
        self.success_message = success_message
        self.actor_stat = actor_stat
        self.actor_divisor = actor_divisor
        self.target_stat = target_stat
        self.target_lo_divisor = target_lo_divisor
        self.target_hi_divisor = target_hi_divisor
        self.apply_resist_multiplier = apply_resist_multiplier
        self.resist_type = resist_type
        self.luck_factor = luck_factor
        self.immunity_status = immunity_status
        self.reflect_item = reflect_item
        self.reflect_slot = reflect_slot
        self.reflect_message = reflect_message

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random

        # --- Reflect check (e.g. Medusa Shield) ---
        if self.reflect_item and self.reflect_slot:
            equip = getattr(target, "equipment", {})
            item = equip.get(self.reflect_slot) if isinstance(equip, dict) else getattr(equip, self.reflect_slot, None)
            if item and getattr(item, "name", None) == self.reflect_item:
                msg = self.reflect_message.format(
                    target=target.name, caster=actor.name, name=result.action,
                )
                result.extra.setdefault("messages", []).append(msg)
                target = actor  # reflected!

        # --- Status immunity check (e.g. "Stone" in status_immunity) ---
        if self.immunity_status:
            if self.immunity_status in getattr(target, "status_immunity", []):
                result.extra["status_immune"] = self.immunity_status
                return

        # --- Resist-based immunity ---
        resist = 0.0
        if self.apply_resist_multiplier:
            resist = target.check_mod("resist", enemy=actor, typ=self.resist_type)
            if resist >= 1:
                result.extra["status_immune"] = "Death"
                return

        # --- Luck modifier ---
        chance = target.check_mod("luck", enemy=actor, luck_factor=self.luck_factor)

        # --- Stat contest ---
        a_val = getattr(actor.stats, self.actor_stat, 10)
        t_val = getattr(target.stats, self.target_stat, 10)

        actor_roll = random.randint(0, max(1, a_val // self.actor_divisor))
        if self.apply_resist_multiplier:
            actor_roll = int(actor_roll * (1 - resist))

        target_roll = (
            random.randint(
                max(0, t_val // self.target_lo_divisor),
                max(1, t_val // self.target_hi_divisor),
            )
            + chance
        )

        if actor_roll > target_roll:
            target.health.current = 0
            msg = self.success_message.format(
                target=target.name, caster=actor.name,
            )
            result.extra.setdefault("messages", []).append(msg)
            result.extra["stat_contest_won"] = True
        else:
            result.extra["stat_contest_won"] = False


class StatReduceEffect(Effect):
    """
    Permanently reduce a target's stat (e.g. DiseaseBreath lowering CON).

    Has an internal two-stage contest:
      1. Actor stat contest — ``random(0, actor_stat // actor_divisor)`` vs
         ``random(target_stat // target_lo, target_stat // target_hi)``.
      2. Secondary chance — ``not random(0, target_stat_value + luck)`` must
         be True (i.e. the roll must be 0).

    On success, ``target.stats.<stat>`` is decremented by ``amount`` and a
    formatted ``success_message`` is added to ``result.extra["messages"]``.
    """

    def __init__(
        self,
        stat: str = "con",
        amount: int = 1,
        actor_stat: str = "intel",
        actor_divisor: int = 2,
        target_stat: str = "con",
        target_lo_divisor: int = 2,
        target_hi_divisor: int = 1,
        luck_factor: int = 10,
        success_message: str = "",
    ):
        self.stat = stat
        self.amount = amount
        self.actor_stat = actor_stat
        self.actor_divisor = actor_divisor
        self.target_stat = target_stat
        self.target_lo_divisor = target_lo_divisor
        self.target_hi_divisor = target_hi_divisor
        self.luck_factor = luck_factor
        self.success_message = success_message

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random

        # Stage 1: stat contest
        a_val = getattr(actor.stats, self.actor_stat, 10)
        t_val = getattr(target.stats, self.target_stat, 10)

        actor_roll = random.randint(0, max(1, a_val // self.actor_divisor))
        target_roll = random.randint(
            max(0, t_val // self.target_lo_divisor),
            max(1, t_val // self.target_hi_divisor),
        )

        if actor_roll > target_roll:
            # Stage 2: secondary luck-gated chance
            chance = target.check_mod("luck", enemy=actor, luck_factor=self.luck_factor)
            stat_val = getattr(target.stats, self.stat, 10)
            if not random.randint(0, stat_val + chance):
                setattr(target.stats, self.stat, stat_val - self.amount)
                msg = self.success_message.format(
                    target=target.name, caster=actor.name,
                )
                result.extra.setdefault("messages", []).append(msg)
                result.extra["stat_contest_won"] = True
                return

        result.extra["stat_contest_won"] = False


class SetFlagEffect(Effect):
    """
    Set a boolean attribute on the target character.

    Used by abilities like Tunnel (``tunnel = True``) and Surface
    (``tunnel = False``).  When the owning skill has ``self_target: true``,
    the *target* passed to :meth:`apply` is the actor themselves.

    ``flag``     – attribute name to set on the target (e.g. ``"tunnel"``)
    ``value``    – boolean value to assign (default ``True``)
    ``message``  – optional template; may contain ``{actor}`` and ``{target}``
    """

    def __init__(
        self,
        flag: str,
        value: bool = True,
        message: str | None = None,
    ):
        self.flag = flag
        self.value = value
        self.message = message

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        setattr(target, self.flag, self.value)
        if self.message:
            result.extra.setdefault("messages", []).append(
                self.message.format(actor=actor.name, target=target.name) + "\n"
            )


# ======================================================================
# PowerUpActivateEffect – activates class_effects["Power Up"]
# ======================================================================

class PowerUpActivateEffect:
    """
    Activate the actor's class-specific Power Up buff.

    Sets ``actor.power_up = True`` and configures
    ``actor.class_effects["Power Up"]`` with the given duration.  Optionally
    computes an ``extra`` value stored on the effect for use by the class's
    combat code:

    ``extra_mode``:
      - ``None`` – no extra value
      - ``"random_health"`` – random int between ``lo_frac * health.max``
        and ``hi_frac * health.max``
      - ``"sacrifice_health"`` – sacrifice ``sacrifice_pct`` of current
        health; ``extra = max(lost // divisor, minimum)``
    """

    def __init__(
        self,
        duration: int = 5,
        extra_mode: str | None = None,
        lo_frac: float = 0.25,
        hi_frac: float = 0.5,
        sacrifice_pct: float = 0.25,
        sacrifice_divisor: int = 5,
        sacrifice_minimum: int = 5,
        message: str | None = None,
    ):
        self.duration = duration
        self.extra_mode = extra_mode
        self.lo_frac = lo_frac
        self.hi_frac = hi_frac
        self.sacrifice_pct = sacrifice_pct
        self.sacrifice_divisor = sacrifice_divisor
        self.sacrifice_minimum = sacrifice_minimum
        self.message = message

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng

        if self.extra_mode == "sacrifice_health":
            per_health = int(actor.health.current * self.sacrifice_pct)
            actor.health.current -= per_health
            extra = max(per_health // self.sacrifice_divisor, self.sacrifice_minimum)
            actor.class_effects["Power Up"].extra = extra
        elif self.extra_mode == "random_health":
            extra = _rng.randint(
                int(actor.health.max * self.lo_frac),
                int(actor.health.max * self.hi_frac),
            )
            actor.class_effects["Power Up"].extra = extra

        actor.power_up = True
        actor.class_effects["Power Up"].active = True
        actor.class_effects["Power Up"].duration = self.duration

        if self.message:
            # Supports {actor}, {extra} placeholders
            extra_val = getattr(actor.class_effects["Power Up"], "extra", 0)
            result.extra.setdefault("messages", []).append(
                self.message.format(actor=actor.name, extra=extra_val) + "\n"
            )


# ======================================================================
# AbilityChainEffect – invoke another ability by name
# ======================================================================

class AbilityChainEffect:
    """
    Instantiate and execute another ability as part of this ability's
    effects.  The chained ability is looked up by class name in the
    ``src.core.abilities`` module, constructed, and invoked with
    ``special=True`` (to skip its own mana cost).

    ``use_method`` – ``"cast"`` for spells, ``"use"`` for skills,
    ``"auto"`` to pick based on whether the ability has a ``school``
    attribute (→ cast) or not (→ use).
    """

    def __init__(
        self,
        ability_name: str,
        target_self: bool = False,
        special: bool = True,
        use_method: str = "auto",
    ):
        self.ability_name = ability_name
        self.target_self = target_self
        self.special = special
        self.use_method = use_method

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import importlib

        mod = importlib.import_module("src.core.abilities")
        cls = getattr(mod, self.ability_name)
        ability = cls()
        actual_target = actor if self.target_self else target

        if self.use_method == "cast" or (
            self.use_method == "auto"
            and hasattr(ability, "school")
            and ability.school is not None
        ):
            msg = str(ability.cast(actor, actual_target, special=self.special))
        else:
            msg = str(ability.use(actor, actual_target, special=self.special))

        result.extra.setdefault("messages", []).append(msg)


# ======================================================================
# DrainEffect – drain health or mana from target to actor
# ======================================================================

class DrainEffect:
    """
    Drain a resource from the target and transfer it to the actor.

    The drain amount is calculated from actor stats:

        drain = randint((base_stat + secondary_stat) // lo_divisor,
                        (base_stat + secondary_stat) / hi_divisor)

    A wisdom-vs-wisdom contest (with luck) may halve the drain.
    The drain is capped at ``cap_percent`` of the target's max resource
    and at the target's current resource amount.
    """

    def __init__(
        self,
        resource: str = "health",
        base_stat: str = "health_current",
        secondary_stat: str = "charisma",
        lo_divisor: int = 5,
        hi_divisor: float = 1.5,
        luck_factor: int = 10,
        cap_percent: float = 0.18,
        message: str | None = None,
    ):
        self.resource = resource
        self.base_stat = base_stat
        self.secondary_stat = secondary_stat
        self.lo_divisor = lo_divisor
        self.hi_divisor = hi_divisor
        self.luck_factor = luck_factor
        self.cap_percent = cap_percent
        self.message = message

    def _get_stat(self, char: Character, stat_key: str) -> int:
        if stat_key == "health_current":
            return char.health.current
        elif stat_key == "health_max":
            return char.health.max
        elif stat_key == "mana_current":
            return char.mana.current
        elif stat_key == "mana_max":
            return char.mana.max
        return getattr(char.stats, stat_key, 0)

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng

        base = self._get_stat(actor, self.base_stat)
        secondary = self._get_stat(actor, self.secondary_stat)
        total = base + secondary

        lo = total // self.lo_divisor
        hi = int(total / self.hi_divisor)
        if hi < lo:
            hi = lo
        drain = _rng.randint(lo, hi)

        # Wisdom-vs-wisdom contest; losing halves the drain
        chance = target.check_mod("luck", enemy=actor, luck_factor=self.luck_factor)
        if not (
            _rng.randint(actor.stats.wisdom // 2, actor.stats.wisdom)
            > _rng.randint(0, target.stats.wisdom // 2) + chance
        ):
            drain = drain // 2

        # Cap at percent of target's max + target's current
        if self.resource == "health":
            cap = max(1, int(target.health.max * self.cap_percent))
            drain = min(drain, cap, target.health.current)
            target.health.current -= drain
            actor.health.current = min(
                actor.health.max, actor.health.current + drain
            )
            try:
                actor._emit_damage_event(
                    target, drain, damage_type="Drain", is_critical=False
                )
                actor._emit_healing_event(drain, source="Life Drain")
            except Exception:
                pass
        else:
            cap = max(1, int(target.mana.max * self.cap_percent))
            drain = min(drain, cap, target.mana.current)
            target.mana.current -= drain
            actor.mana.current = min(
                actor.mana.max, actor.mana.current + drain
            )

        msg = (
            self.message or "{actor} drains {amount} {resource} from {target}.\n"
        ).format(
            actor=actor.name,
            target=target.name,
            amount=drain,
            resource=self.resource,
        )
        result.extra.setdefault("messages", []).append(msg)


# ======================================================================
# MagicEffectToggleEffect – toggle a magic effect on/off
# ======================================================================

class MagicEffectToggleEffect:
    """
    Toggle a magic effect on the actor.  When the effect is already active,
    it is deactivated (no mana cost).  When inactive, mana is deducted and
    the effect is activated with ``duration`` set to *reduction* (used by
    ``_apply_mana_shield`` as the damage-reduction divisor, not a turn
    count).

    The ``cost`` is only charged on activation.  Set the parent skill's
    cost to 0 so the ``DataDrivenSkill`` pipeline does not double-charge.
    """

    def __init__(
        self,
        effect_name: str,
        cost: int = 0,
        reduction: int = 2,
        activate_message: str | None = None,
        deactivate_message: str | None = None,
    ):
        self.effect_name = effect_name
        self.cost = cost
        self.reduction = reduction
        self.activate_message = (
            activate_message or f"{effect_name} has been activated.\n"
        )
        self.deactivate_message = (
            deactivate_message or f"{effect_name} has been deactivated.\n"
        )

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        if actor.magic_effects[self.effect_name].active:
            actor.magic_effects[self.effect_name].active = False
            result.extra.setdefault("messages", []).append(
                self.deactivate_message
            )
            result.extra["toggled_off"] = True
        else:
            if self.cost:
                actor.mana.current -= self.cost
            actor.magic_effects[self.effect_name].active = True
            actor.magic_effects[self.effect_name].duration = self.reduction
            result.extra.setdefault("messages", []).append(
                self.activate_message
            )


# ======================================================================
# ScreechEffect – stat-contest damage + conditional permanent silence
# ======================================================================

class ScreechEffect:
    """
    Speed+intel vs con+wisdom stat contest.  On success, deal
    ``intel * (1 - Physical resist)`` damage and permanently silence the
    target (duration = -1) if the damage is positive and the target is not
    immune.
    """

    def __init__(
        self,
        damage_message: str = "The deafening screech hurts {target} for {damage} damage.\n",
        silence_message: str = "{target} has been silenced.\n",
        fail_message: str = "The spell is ineffective.\n",
    ):
        self.damage_message = damage_message
        self.silence_message = silence_message
        self.fail_message = fail_message

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng

        messages = result.extra.setdefault("messages", [])
        damage = 0

        # Stat contest: speed_check_mod + intel  vs  con(half-to-full) + wisdom
        actor_val = (
            _rng.randint(0, actor.check_mod("speed", enemy=actor))
            + actor.stats.intel
        )
        target_val = (
            _rng.randint(target.stats.con // 2, target.stats.con)
            + target.stats.wisdom
        )

        if actor_val > target_val:
            resist = target.check_mod("resist", enemy=actor, typ="Physical")
            damage = int(actor.stats.intel * (1 - resist))
            if damage > 0:
                target.health.current -= damage
                result.damage = damage
                messages.append(
                    self.damage_message.format(
                        target=target.name, damage=damage
                    )
                )
                # Silence check
                if not any([
                    "Silence" in getattr(target, "status_immunity", []),
                    "Status-Silence" in target.equipment["Pendant"].mod,
                    "Status-All" in target.equipment["Pendant"].mod,
                ]):
                    target.status_effects["Silence"].active = True
                    target.status_effects["Silence"].duration = -1
                    try:
                        actor._emit_status_event(
                            target, "Silence", applied=True,
                            duration=-1, source="Screech",
                        )
                    except Exception:
                        pass
                    messages.append(
                        self.silence_message.format(target=target.name)
                    )

        if damage <= 0:
            messages.append(self.fail_message)


# ======================================================================
# AcidSpitEffect – magic damage with armor curve + DOT chance
# ======================================================================

class AcidSpitEffect:
    """
    Intel-based magic damage with magic-defense armor curve, dodge
    halving, and a CON-based chance to apply DOT.

    Cost is ``base_cost * user.level.pro_level`` (deducted by the effect,
    so set the YAML ``cost: 0``).
    """

    def __init__(
        self,
        base_cost: int = 6,
        dot_duration: int = 2,
        damage_message: str = "{target} takes {damage} damage from the acid.\n",
        dot_message: str = "{target} is covered in a corrosive substance.\n",
        miss_message: str = "{actor} misses {target} with Acid Spit.\n",
        ineffective_message: str = "The acid is ineffective.\n",
        dodge_message: str = "{target} partially dodges the attack, only taking half damage.\n",
    ):
        self.base_cost = base_cost
        self.dot_duration = dot_duration
        self.damage_message = damage_message
        self.dot_message = dot_message
        self.miss_message = miss_message
        self.ineffective_message = ineffective_message
        self.dodge_message = dodge_message

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        from src.core.constants import (
            ARMOR_SCALING_FACTOR,
            DAMAGE_VARIANCE_LOW,
            DAMAGE_VARIANCE_HIGH,
        )

        messages = result.extra.setdefault("messages", [])

        # Dynamic mana cost
        actual_cost = self.base_cost * actor.level.pro_level
        actor.mana.current -= actual_cost

        # Intel-based magic damage with armor curve
        dmg = (actor.stats.intel // 2) + actor.combat.magic
        dam_red = target.check_mod("magic def", enemy=actor)
        damage = int(dmg * (1 - (dam_red / (dam_red + ARMOR_SCALING_FACTOR))))
        variance = _rng.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
        damage = int(damage * variance)

        if actor.hit_chance(target, typ="magic"):
            if target.dodge_chance(actor, spell=True):
                messages.append(
                    self.dodge_message.format(target=target.name)
                )
                damage //= 2
            if damage > 0:
                messages.append(
                    self.damage_message.format(
                        target=target.name, damage=damage
                    )
                )
                target.health.current -= damage
                result.damage = damage
                # DOT chance via con check
                if not _rng.randint(0, target.stats.con // 2):
                    target.magic_effects["DOT"].active = True
                    target.magic_effects["DOT"].duration = self.dot_duration
                    target.magic_effects["DOT"].extra = max(
                        damage, target.magic_effects["DOT"].extra
                    )
                    try:
                        actor._emit_status_event(
                            target, "DOT", applied=True,
                            duration=self.dot_duration,
                            source="Acid Splash",
                        )
                    except Exception:
                        pass
                    messages.append(
                        self.dot_message.format(target=target.name)
                    )
            else:
                messages.append(self.ineffective_message)
        else:
            messages.append(
                self.miss_message.format(
                    actor=actor.name, target=target.name
                )
            )


# ======================================================================
# BreathDamageEffect – stat-based elemental breath damage
# ======================================================================

class BreathDamageEffect:
    """
    Breath weapon: ``(strength + intel) * multiplier * variance``, then
    ``damage_reduction(typ=element)``.  The element can be set in YAML or
    overridden at call-time via ``result.extra["use_kwargs"]["typ"]``.
    """

    def __init__(
        self,
        multiplier: float = 1.5,
        element: str = "Non-elemental",
        announce_message: str = "{actor} unleashes a breath of {element} energy!\n",
        damage_message: str = "{target} takes {damage} damage from the breath weapon.\n",
        no_effect_message: str = "The breath weapon has no effect on {target}.\n",
    ):
        self.multiplier = multiplier
        self.element = element
        self.announce_message = announce_message
        self.damage_message = damage_message
        self.no_effect_message = no_effect_message

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        from src.core.constants import DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH

        messages = result.extra.setdefault("messages", [])

        # Allow element override from caller kwargs
        typ = result.extra.get("use_kwargs", {}).get("typ", self.element)

        base_damage = int(
            (actor.stats.strength + actor.stats.intel) * self.multiplier
        )
        variance = _rng.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
        damage = int(base_damage * variance)

        _, reduction_msg, damage = target.damage_reduction(damage, actor, typ=typ)

        messages.append(
            self.announce_message.format(actor=actor.name, element=typ)
        )
        if reduction_msg:
            messages.append(reduction_msg)

        if damage > 0:
            target.health.current -= damage
            result.damage = damage
            try:
                actor._emit_damage_event(
                    target, damage, damage_type=typ, is_critical=False
                )
            except Exception:
                pass
            messages.append(
                self.damage_message.format(target=target.name, damage=damage)
            )
        else:
            messages.append(
                self.no_effect_message.format(target=target.name)
            )


# ======================================================================
# NightmareFuelEffect – sleep-conditional intel-based damage
# ======================================================================

class NightmareFuelEffect:
    """
    Requires the target to be asleep.  ``damage = sleep_duration * intel
    * crit_multiplier * variance``.  Intel-vs-wisdom contest to land.
    50% crit chance.
    """

    def __init__(
        self,
        crit_chance: float = 0.5,
        damage_message: str = (
            "{actor} invades {target}'s dreams, dealing {damage} damage"
        ),
        fail_message: str = "{target} resists the spell.\n",
        no_sleep_message: str = "The spell does nothing.\n",
    ):
        self.crit_chance = crit_chance
        self.damage_message = damage_message
        self.fail_message = fail_message
        self.no_sleep_message = no_sleep_message

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        from src.core.constants import DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH

        messages = result.extra.setdefault("messages", [])

        if not target.status_effects["Sleep"].active:
            messages.append(self.no_sleep_message)
            return

        # Intel vs wisdom contest
        if _rng.randint(actor.stats.intel // 2, actor.stats.intel) > _rng.randint(
            target.stats.wisdom // 2, target.stats.wisdom
        ):
            crit = 2 if _rng.random() > self.crit_chance else 1
            variance = _rng.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
            damage = int(
                target.status_effects["Sleep"].duration
                * actor.stats.intel
                * crit
                * variance
            )
            target.health.current -= damage
            result.damage = damage

            dmg_msg = self.damage_message.format(
                actor=actor.name, target=target.name, damage=damage
            )
            if crit > 1:
                dmg_msg += " (Critical hit!)"
            messages.append(dmg_msg + ".\n")
        else:
            messages.append(
                self.fail_message.format(target=target.name)
            )


# ======================================================================
# WidowsWailEffect – inverse-HP damage to both actor and target
# ======================================================================

class WidowsWailEffect:
    """
    Damage = ``min(max_damage, (health.max / health.current) * multiplier)``.
    Independent intel-vs-wisdom contests for self-damage and target-damage.
    Ice Block / tunnel blocks target-damage only.
    """

    def __init__(
        self,
        multiplier: int = 20,
        max_damage: int = 200,
        self_message: str = "Anguish overwhelms {name}, taking {damage} damage.\n",
        target_message: str = "Anguish overwhelms {name}, taking {damage} damage.\n",
    ):
        self.multiplier = multiplier
        self.max_damage = max_damage
        self.self_message = self_message
        self.target_message = target_message

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng

        messages = result.extra.setdefault("messages", [])

        dmg = int((actor.health.max / max(1, actor.health.current)) * self.multiplier)
        damage = min(self.max_damage, dmg)

        # Self-damage: intel vs wisdom (actor vs self)
        if _rng.randint(actor.stats.intel // 2, actor.stats.intel) > _rng.randint(
            actor.stats.wisdom // 2, actor.stats.wisdom
        ):
            messages.append(
                self.self_message.format(name=actor.name, damage=damage)
            )
            actor.health.current -= damage

        # Target-damage: skip if ice block / tunnel
        if any([
            target.magic_effects["Ice Block"].active,
            getattr(target, "tunnel", False),
        ]):
            return

        # Target-damage: intel vs wisdom (actor vs target)
        if _rng.randint(actor.stats.intel // 2, actor.stats.intel) > _rng.randint(
            target.stats.wisdom // 2, target.stats.wisdom
        ):
            messages.append(
                self.target_message.format(name=target.name, damage=damage)
            )
            target.health.current -= damage
            result.damage = damage


# ======================================================================
# GoblinPunchEffect – multi-hit strength-difference damage
# ======================================================================

class GoblinPunchEffect:
    """
    ``num_attacks = randint(pro_level, max_punches)``.  Each punch deals
    ``str_diff = max(1 + pro_level, (target.str - user.str) // 2)`` damage
    if it hits (standard hit_chance).
    """

    def __init__(
        self,
        max_punches: int = 5,
        hit_message: str = "{actor} punches {target} for {damage} damage.\n",
        miss_message: str = "{actor} punches air, missing {target}.\n",
    ):
        self.max_punches = max_punches
        self.hit_message = hit_message
        self.miss_message = miss_message

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng

        messages = result.extra.setdefault("messages", [])

        num_attacks = max(1, _rng.randint(
            actor.level.pro_level, self.max_punches
        ))
        str_diff = max(
            1 + actor.level.pro_level,
            (target.stats.strength - actor.stats.strength) // 2,
        )
        total_damage = 0
        for _ in range(num_attacks):
            if actor.hit_chance(target, typ="weapon"):
                target.health.current -= str_diff
                total_damage += str_diff
                messages.append(
                    self.hit_message.format(
                        actor=actor.name, target=target.name,
                        damage=str_diff,
                    )
                )
            else:
                messages.append(
                    self.miss_message.format(
                        actor=actor.name, target=target.name,
                    )
                )
        result.damage = total_damage


# ======================================================================
# HexEffect – three independent status applications
# ======================================================================

class HexEffect:
    """
    Attempt to apply Poison, Blind, and Silence independently.  Each has
    its own immunity / pendant / already-active check and a separate stat
    contest (intel vs con for Poison & Blind, intel vs wisdom for Silence).
    """

    def __init__(
        self,
        duration: int = 3,
        announce_message: str = "{caster} curses {target} with a hex.\n",
        poison_message: str = "{target} is poisoned.\n",
        blind_message: str = "{target} is blinded.\n",
        silence_message: str = "{target} is silenced.\n",
        no_effect_message: str = "The hex has no effect.\n",
    ):
        self.duration = duration
        self.announce_message = announce_message
        self.poison_message = poison_message
        self.blind_message = blind_message
        self.silence_message = silence_message
        self.no_effect_message = no_effect_message

    def _is_immune(self, target: Character, status_name: str) -> bool:
        """Check immunity via status_immunity list and pendant."""
        return any([
            status_name in getattr(target, "status_immunity", []),
            f"Status-{status_name}" in target.equipment["Pendant"].mod,
            "Status-All" in target.equipment["Pendant"].mod,
        ])

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng

        messages = result.extra.setdefault("messages", [])
        messages.append(
            self.announce_message.format(caster=actor.name, target=target.name)
        )
        applied = False

        # ── Poison: intel vs con ──
        if not self._is_immune(target, "Poison"):
            if not target.status_effects["Poison"].active:
                if _rng.randint(actor.stats.intel // 2, actor.stats.intel) > _rng.randint(
                    target.stats.con // 2, target.stats.con
                ):
                    poison_damage = max(1, actor.stats.intel // 4)
                    target.status_effects["Poison"].active = True
                    target.status_effects["Poison"].duration = max(
                        self.duration,
                        target.status_effects["Poison"].duration,
                    )
                    target.status_effects["Poison"].extra = max(
                        poison_damage,
                        target.status_effects["Poison"].extra,
                    )
                    try:
                        actor._emit_status_event(
                            target, "Poison", applied=True,
                            duration=target.status_effects["Poison"].duration,
                            source="Hex",
                        )
                    except Exception:
                        pass
                    messages.append(
                        self.poison_message.format(target=target.name)
                    )
                    applied = True

        # ── Blind: intel vs con ──
        if not self._is_immune(target, "Blind"):
            if not target.status_effects["Blind"].active:
                if _rng.randint(actor.stats.intel // 2, actor.stats.intel) > _rng.randint(
                    target.stats.con // 2, target.stats.con
                ):
                    target.status_effects["Blind"].active = True
                    target.status_effects["Blind"].duration = max(
                        self.duration,
                        target.status_effects["Blind"].duration,
                    )
                    try:
                        actor._emit_status_event(
                            target, "Blind", applied=True,
                            duration=target.status_effects["Blind"].duration,
                            source="Hex",
                        )
                    except Exception:
                        pass
                    messages.append(
                        self.blind_message.format(target=target.name)
                    )
                    applied = True

        # ── Silence: intel vs wisdom ──
        if not self._is_immune(target, "Silence"):
            if not target.status_effects["Silence"].active:
                if _rng.randint(actor.stats.intel // 2, actor.stats.intel) > _rng.randint(
                    target.stats.wisdom // 2, target.stats.wisdom
                ):
                    target.status_effects["Silence"].active = True
                    target.status_effects["Silence"].duration = max(
                        self.duration,
                        target.status_effects["Silence"].duration,
                    )
                    try:
                        actor._emit_status_event(
                            target, "Silence", applied=True,
                            duration=target.status_effects["Silence"].duration,
                            source="Hex",
                        )
                    except Exception:
                        pass
                    messages.append(
                        self.silence_message.format(target=target.name)
                    )
                    applied = True

        if not applied:
            messages.append(self.no_effect_message)


# ======================================================================
# VulcanizeEffect – self fire damage + defense buff
# ======================================================================

class VulcanizeEffect:
    """
    Deals fire damage to the *caster* based on fire resistance and current
    health, then grants a defense buff if still alive.  Always targets
    self (ignores the ``target`` argument).
    """

    def __init__(
        self,
        health_fraction: float = 0.1,
        buff_duration: int = 5,
        buff_lo_divisor: int = 4,
        buff_hi_divisor: int = 2,
        damage_message: str = "{target} takes {damage} damage from the flames.\n",
        heal_message: str = "{target} is healed by the flames for {damage} hit points.\n",
        buff_message: str = "{target} is hardened by the flames.\n",
    ):
        self.health_fraction = health_fraction
        self.buff_duration = buff_duration
        self.buff_lo_divisor = buff_lo_divisor
        self.buff_hi_divisor = buff_hi_divisor
        self.damage_message = damage_message
        self.heal_message = heal_message
        self.buff_message = buff_message

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng

        # target is always self (set by DataDrivenSupportSpell)
        messages = result.extra.setdefault("messages", [])

        fire_resist = target.check_mod("resist", enemy=actor, typ="Fire")
        damage = int((1 - fire_resist) * (target.health.current * self.health_fraction))
        target.health.current -= damage
        try:
            actor._emit_damage_event(
                target, damage, damage_type="Fire", is_critical=False
            )
        except Exception:
            pass

        if damage > 0:
            messages.append(
                self.damage_message.format(target=target.name, damage=damage)
            )
        elif damage < 0:
            messages.append(
                self.heal_message.format(target=target.name, damage=abs(damage))
            )

        if target.is_alive():
            def_gain = target.combat.defense + actor.stats.intel
            target.stat_effects["Defense"].active = True
            target.stat_effects["Defense"].duration = self.buff_duration
            target.stat_effects["Defense"].extra = _rng.randint(
                def_gain // self.buff_lo_divisor,
                def_gain // self.buff_hi_divisor,
            )
            messages.append(
                self.buff_message.format(target=target.name)
            )


# ======================================================================
# HolyFollowupEffect – holy spell damage follow-up after weapon hit
# ======================================================================

class HolyFollowupEffect:
    """
    Holy spell damage pipeline executed after a successful weapon hit
    (used by Smite and its upgrades).

    Reads ``dmg_mod`` and ``last_crit`` from ``result.extra``.

    Pipeline: spell_mod (half-to-full) → dmg_mod × spell_mod × crit →
    Mana Shield / Crusader Shield → Holy resist → if absorbed: heal;
    else armor curve (magic def) → variance → CON save (half) → damage.
    """

    def __init__(
        self,
        resist_type: str = "Holy",
        damage_message: str = "{actor} smites {target} for {damage} hit points.\n",
        ineffective_message: str = "{name} was ineffective and does no damage.\n",
        absorb_message: str = "{target} absorbs {subtyp} and is healed for {heal} health.\n",
        con_save_message: str = "{target} shrugs off the {name} and only receives half of the damage.\n",
    ):
        self.resist_type = resist_type
        self.damage_message = damage_message
        self.ineffective_message = ineffective_message
        self.absorb_message = absorb_message
        self.con_save_message = con_save_message

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        from src.core.constants import (
            ARMOR_SCALING_FACTOR,
            DAMAGE_VARIANCE_LOW,
            DAMAGE_VARIANCE_HIGH,
        )

        messages = result.extra.setdefault("messages", [])
        dmg_mod = result.extra.get("dmg_mod", 1.0)
        crit = result.extra.get("last_crit", 1)

        spell_mod = actor.check_mod("magic", enemy=target)
        spell_mod = _rng.randint(spell_mod // 2, spell_mod)
        dam_red = target.check_mod("magic def", enemy=actor)
        resist = target.check_mod("resist", enemy=actor, typ=self.resist_type)

        damage = int(dmg_mod * spell_mod)
        damage *= crit

        # Mana Shield / Crusader Shield
        hit = True
        if target.magic_effects["Mana Shield"].active:
            hit, shield_msg, damage = target._apply_mana_shield(damage)
            messages.append(shield_msg)
        elif (
            target.cls.name == "Crusader"
            and getattr(target, "power_up", False)
            and target.class_effects["Power Up"].active
        ):
            hit, shield_msg, damage = target.handle_crusader_shield(damage)
            messages.append(shield_msg)

        # Holy resist
        damage = int(damage * (1 - resist))

        if damage < 0:
            target.health.current -= damage
            messages.append(
                self.absorb_message.format(
                    target=target.name,
                    subtyp=self.resist_type,
                    heal=abs(damage),
                )
            )
        else:
            # Armor curve
            damage = int(
                damage * (1 - (dam_red / (dam_red + ARMOR_SCALING_FACTOR)))
            )
            # Variance
            variance = _rng.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
            damage = int(damage * variance)

            if damage <= 0:
                damage = 0
                messages.append(
                    self.ineffective_message.format(name="Smite")
                )
            elif _rng.randint(0, target.stats.con // 2) > _rng.randint(
                (actor.stats.intel * crit) // 2,
                (actor.stats.intel * crit),
            ):
                # CON save → half damage
                damage //= 2
                if damage > 0:
                    messages.append(
                        self.con_save_message.format(
                            target=target.name, name="Smite"
                        )
                    )
                    messages.append(
                        self.damage_message.format(
                            actor=actor.name, target=target.name,
                            damage=damage,
                        )
                    )
                else:
                    messages.append(
                        self.ineffective_message.format(name="Smite")
                    )
            else:
                messages.append(
                    self.damage_message.format(
                        actor=actor.name, target=target.name,
                        damage=damage,
                    )
                )

            target.health.current -= damage
            result.damage = (result.damage or 0) + damage


# ======================================================================
# TurnUndeadEffect – undead-only kill chance or holy damage
# ======================================================================

class TurnUndeadEffect:
    """
    Only works on Undead targets.  Luck-based instant-kill chance, with
    a fallback holy-damage pipeline (spell_mod half-to-full, armor curve,
    Holy resist, variance).

    Reads ``dmg_mod`` and ``crit_chance`` from ``result.extra`` (set by
    the DataDriven wrapper).
    """

    def __init__(
        self,
        luck_factor: int = 6,
        kill_message: str = "The {target} has been rebuked, destroying the undead monster.\n",
        no_undead_message: str = "The spell does nothing.\n",
        damage_message: str = "{actor} damages {target} for {damage} hit points",
    ):
        self.luck_factor = luck_factor
        self.kill_message = kill_message
        self.no_undead_message = no_undead_message
        self.damage_message = damage_message

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        from src.core.constants import (
            ARMOR_SCALING_FACTOR,
            DAMAGE_VARIANCE_LOW,
            DAMAGE_VARIANCE_HIGH,
        )

        messages = result.extra.setdefault("messages", [])
        dmg_mod = result.extra.get("dmg_mod", 1.5)
        crit_chance = result.extra.get("crit_chance", 5)

        if getattr(target, "enemy_typ", None) != "Undead":
            messages.append(self.no_undead_message)
            return

        # Crit roll
        crit = 1
        if not _rng.randint(0, crit_chance):
            crit = 2

        # Kill chance (luck-based)
        chance = max(
            2,
            target.check_mod("luck", enemy=actor, luck_factor=self.luck_factor),
        )
        if crit > 1:
            chance -= 1
        if not _rng.randint(0, chance):
            target.health.current = 0
            result.damage = target.health.max
            messages.append(
                self.kill_message.format(target=target.name)
            )
            return

        # Fallback holy damage
        spell_mod = actor.check_mod("magic", enemy=target)
        spell_mod = _rng.randint(spell_mod // 2, spell_mod)
        dam_red = target.check_mod("magic def", enemy=actor)
        resist = target.check_mod("resist", enemy=actor, typ="Holy")

        damage = int(dmg_mod * spell_mod)
        damage *= crit
        damage = int(
            damage
            * (1 - resist)
            * (1 - (dam_red / (dam_red + ARMOR_SCALING_FACTOR)))
        )
        variance = _rng.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
        damage = int(damage * variance)

        target.health.current -= damage
        result.damage = damage

        dmg_msg = self.damage_message.format(
            actor=actor.name, target=target.name, damage=damage
        )
        if crit > 1:
            dmg_msg += " (Critical hit!)"
        messages.append(dmg_msg + ".\n")


# ---------------------------------------------------------------------------
# Batch 9 — Equipment-dependent skills, remaining enemy skills, gold/power-up
# ---------------------------------------------------------------------------

class ShieldSlamEffect(Effect):
    """Shield Slam: str + shield-weight damage with stun chance.

    Requires offhand shield.  Handles its own dodge/damage/stun pipeline.
    Expects: check_weapon=false in YAML; DataDrivenSkill handles mana + ice-block.
    """

    def __init__(self, **_kw):
        super().__init__()

    # noinspection PyMethodOverriding
    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        from src.core.constants import DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH
        messages = result.extra.setdefault("messages", [])

        # Shield requirement
        offhand = actor.equipment.get("OffHand") if hasattr(actor, "equipment") else None
        if offhand is None or getattr(offhand, "subtyp", None) != "Shield":
            messages.append(f"{actor.name} has no shield to slam with!\n")
            return

        # Dodge
        if target.dodge_chance(actor) > _rng.random():
            messages.append(f"{target.name} dodges {actor.name}'s shield slam!\n")
            return

        # Damage = strength + shield weight
        damage = max(1, actor.stats.strength + getattr(offhand, "weight", 0))
        variance = _rng.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
        damage = int(damage * variance)
        target.health.current -= damage
        result.damage = damage
        messages.append(
            f"{actor.name} slams {target.name} with their shield for {damage} damage!\n"
        )

        # Stun check
        if target.is_alive():
            if not any([
                "Stun" in getattr(target, "status_immunity", []),
                f"Status-Stun" in target.equipment["Pendant"].mod,
                "Status-All" in target.equipment["Pendant"].mod,
            ]):
                att_roll = _rng.randint(0, actor.stats.strength)
                def_roll = _rng.randint(target.stats.strength // 2, target.stats.strength)
                if target.stun_contest_success(actor, att_roll, def_roll):
                    turns = _rng.randint(1, max(1, actor.stats.strength // 8))
                    if target.apply_stun(turns, source="Shield Bash", applier=actor):
                        messages.append(f"{target.name} is stunned for {turns} turn(s)!\n")


class KidneyPunchEffect(Effect):
    """Kidney Punch: offhand-weapon check → weapon_damage → stun.

    Handles its own equipment check, weapon_damage call, and stun logic.
    Expects: check_weapon=false, cost=0 in YAML (effect manages mana).
    """

    def __init__(self, cost: int = 12, **_kw):
        super().__init__()
        self.cost = cost

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])

        # Offhand weapon requirement
        offhand = actor.equipment.get("OffHand") if hasattr(actor, "equipment") else None
        if not offhand or getattr(offhand, "typ", None) != "Weapon":
            messages.append(f"{actor.name} needs an off-hand weapon to use Kidney Punch.\n")
            return

        # Mana
        actor.mana.current -= self.cost

        # Weapon damage (main hand)
        use_str, hit, crit = actor.weapon_damage(target, dmg_mod=1.0, cover=False, use_offhand=False)
        messages.append(use_str)

        # Crusader Divine Aegis check
        crusader_aegis = (
            hasattr(target, "cls")
            and hasattr(target, "class_effects")
            and target.cls.name == "Crusader"
            and getattr(target, "power_up", False)
            and "Power Up" in target.class_effects
            and target.class_effects["Power Up"].active
        )

        if hit and target.is_alive() and not crusader_aegis:
            if not any([
                "Stun" in getattr(target, "status_immunity", []),
                f"Status-Stun" in target.equipment["Pendant"].mod,
                "Status-All" in target.equipment["Pendant"].mod,
            ]):
                speed = actor.check_mod("speed", enemy=actor)
                att_roll = _rng.randint(0, int(speed * crit))
                def_roll = _rng.randint(target.stats.con // 2, target.stats.con)
                if target.stun_contest_success(actor, att_roll, def_roll):
                    dur = max(2, speed // 8)
                    if target.apply_stun(dur, source="Kidney Punch", applier=actor):
                        messages.append(f"{target.name} is stunned.\n")
                else:
                    messages.append(f"{actor.name} fails to stun {target.name}.\n")
            else:
                messages.append(f"{target.name} is immune to stun.\n")


class PoisonStrikeEffect(Effect):
    """Poison Strike: after weapon hit, chance to poison (% of target max HP).

    Runs post-weapon_damage; checks result.extra['hit'].
    """

    def __init__(self, damage_pct: float = 0.1, **_kw):
        super().__init__()
        self.damage_pct = damage_pct

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])
        hit = getattr(result, 'hit', False)
        crit = result.extra.get("last_crit", 1)
        if not (hit and target.is_alive()):
            return

        if any([
            "Poison" in getattr(target, "status_immunity", []),
            "Status-Poison" in target.equipment["Pendant"].mod,
            "Status-All" in target.equipment["Pendant"].mod,
        ]):
            messages.append(f"{target.name} is immune to poison.\n")
            return

        resist = target.check_mod("resist", enemy=actor, typ="Poison")
        speed = actor.check_mod("speed", enemy=actor)
        if _rng.randint(0, speed) * crit * (1 - resist) > _rng.randint(
            target.stats.con // 2, target.stats.con
        ):
            turns = max(5, speed // 5)
            pois_dmg = int(target.health.max * self.damage_pct * (1 - resist))
            target.status_effects["Poison"].active = True
            target.status_effects["Poison"].duration = max(
                turns, target.status_effects["Poison"].duration
            )
            target.status_effects["Poison"].extra = max(
                pois_dmg, target.status_effects["Poison"].extra
            )
            try:
                actor._emit_status_event(
                    target, "Poison", applied=True,
                    duration=target.status_effects["Poison"].duration,
                    source="Poison Blade"
                )
            except Exception:
                pass
            messages.append(f"{target.name} is poisoned.\n")
        else:
            messages.append(f"{target.name} resists the poison.\n")


class DimMakEffect(Effect):
    """Dim Mak: after weapon hit — kill chance, stun fallback, essence absorb.

    Runs post-weapon_damage; checks target alive for kill/stun.
    On target death (from weapon or effect), absorbs essence.
    """

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])

        if target.is_alive():
            # Ice block / tunnel — no secondary effect
            if any([target.magic_effects["Ice Block"].active,
                    getattr(target, "tunnel", False)]):
                return

            # Instant kill check
            con_val = getattr(target.stats, "con", getattr(target, "con", 0))
            luck = target.check_mod("luck", enemy=actor, luck_factor=5)
            if (
                not (_rng.randint(0, con_val) + luck)
                and "Death" not in getattr(target, "status_immunity", [])
            ):
                messages.append(
                    f"{target.name} sustains a lethal blow and collapses to the ground.\n"
                )
                target.health.current = 0
            else:
                # Stun fallback
                if not any([
                    "Stun" in getattr(target, "status_immunity", []),
                    f"Status-Stun" in target.equipment["Pendant"].mod,
                    "Status-All" in target.equipment["Pendant"].mod,
                    target.check_mod("resist", enemy=actor, typ="Physical") > _rng.random(),
                ]):
                    dur = actor.stats.wisdom // 10
                    if target.apply_stun(dur, source="Devour", applier=actor):
                        messages.append(f"{target.name} is stunned.\n")

            if target.is_alive():
                return

        # Essence absorb (target is dead)
        actor.health.current = min(
            actor.health.max, actor.health.current + target.health.max
        )
        actor.mana.current = min(
            actor.mana.max, actor.mana.current + target.mana.max
        )
        messages.append(
            f"{actor.name} gains the essence of {target.name}, gaining health and mana.\n"
        )


class ExploitWeaknessEffect(Effect):
    """Exploit Weakness: find target's lowest resistance, boost weapon mod or
    apply random status.  Handles its own weapon_damage call.

    Expects: check_weapon=false in YAML.
    Fixes the original bug where list.append returned None.
    """

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])

        types = list(target.resistance)
        resists = list(target.resistance.values())
        weak = min(resists)

        if weak < 0:
            mod = 1 - weak
            idx = resists.index(weak)
            messages.append(
                f"{actor.name} targets {target.name}'s weakness to "
                f"{types[idx].lower()} to increase their attack!\n"
            )
        else:
            mod = 1
            # Build list with "None" sentinel (fixes original .append bug)
            effects = list(target.status_effects) + ["None"]
            chances = [actor.check_mod("luck", enemy=target, luck_factor=10)] * len(
                target.status_effects
            )
            chances.append(target.stats.con // 5)
            effect = _rng.choices(effects, weights=chances)[0]
            if effect == "None":
                messages.append(
                    f"{target.name} has no identifiable weakness. The skill is ineffective.\n"
                )
            else:
                if any([
                    effect in getattr(target, "status_immunity", []),
                    f"Status-{effect}" in target.equipment["Pendant"].mod,
                    "Status-All" in target.equipment["Pendant"].mod,
                ]):
                    messages.append(f"{target.name} is immune to {effect.lower()}.\n")
                else:
                    messages.append(f"{target.name} is affected by {effect.lower()}.\n")
                    target.status_effects[effect].active = True
                    target.status_effects[effect].duration = -1

        # Weapon damage with calculated mod
        wd_str, _, _ = actor.weapon_damage(target, dmg_mod=mod)
        messages.append(wd_str)


class GoldTossEffect(Effect):
    """Gold Toss: throw gold for unblockable damage, enemy may catch some.

    Handles all damage logic.  Ice block check done inside.
    Expects: check_weapon=false, cost=0 in YAML.
    """

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])

        if actor.gold == 0:
            messages.append("Nothing happens.\n")
            return

        max_thrown = min(target.health.current, actor.gold)
        gold_thrown = _rng.randint(1, max_thrown)
        actor.gold -= gold_thrown
        messages.append(f"{actor.name} throws {gold_thrown} gold at {target.name}.\n")

        if any([target.magic_effects["Ice Block"].active,
                getattr(target, "tunnel", False)]):
            messages.append("It has no effect.\n")
            return

        if not _rng.randint(0, 1) and not target.incapacitated():
            d_chance = target.check_mod("luck", enemy=actor, luck_factor=10)
            catch = _rng.randint(min(gold_thrown, d_chance), gold_thrown)
            gold_thrown -= catch
            if catch > 0:
                target.gold += catch
                if gold_thrown > 0:
                    messages.append(
                        f"{target.name} catches some of the gold thrown, gaining {catch} gold.\n"
                    )
                else:
                    messages.append(
                        f"{target.name} catches all of the gold thrown, gaining {catch} gold.\n"
                    )

        if gold_thrown > 0:
            d_chance = target.check_mod("luck", enemy=actor, luck_factor=10)
            damage = max(1, gold_thrown // (2 + d_chance))
            target.health.current -= damage
            result.damage = damage
            try:
                actor._emit_damage_event(
                    target, damage, damage_type="Gold", is_critical=False
                )
            except Exception:
                pass
            messages.append(f"{actor.name} does {damage} damage to {target.name}.\n")


class LickEffect(Effect):
    """Lick: after weapon hit, apply a random status effect.

    Silence/Blind get permanent duration (-1), Poison gets 5% HP extra.
    """

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])
        hit = getattr(result, 'hit', False)
        if not hit:
            return

        if _rng.randint(
            actor.stats.strength // 2, actor.stats.strength
        ) > _rng.randint(target.stats.con // 2, target.stats.con):
            random_effect = _rng.choice(list(target.status_effects))
            if not any([
                random_effect in getattr(target, "status_immunity", []),
                f"Status-{random_effect}" in target.equipment["Pendant"].mod,
                "Status-All" in target.equipment["Pendant"].mod,
            ]):
                if not target.status_effects[random_effect].active:
                    target.status_effects[random_effect].active = True
                    if random_effect in ["Silence", "Blind"]:
                        target.status_effects[random_effect].duration = -1
                    else:
                        target.status_effects[random_effect].duration = (
                            _rng.randint(2, max(3, actor.stats.strength // 8))
                        )
                        if random_effect == "Poison":
                            target.status_effects[random_effect].extra = int(
                                target.health.max * 0.05
                            )
                    messages.append(
                        f"{target.name} is affected by {random_effect.lower()}.\n"
                    )


class BrainGorgeEffect(Effect):
    """Brain Gorge: after weapon hit, latch + extra physical damage + intel drain.

    Ignores Mana Shield (original note).
    """

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])
        hit = getattr(result, 'hit', False)
        crit = result.extra.get("last_crit", 1)
        if not hit:
            return

        t_chance = target.check_mod("luck", enemy=actor, luck_factor=15)
        messages.append(f"{actor.name} latches onto {target.name}.\n")

        if target.incapacitated() or (
            _rng.randint(actor.stats.strength // 2, actor.stats.strength)
            > _rng.randint(target.stats.con // 2, target.stats.con) + t_chance
        ):
            resist = target.check_mod("resist", enemy=actor, typ="Physical")
            damage = int(
                _rng.randint(actor.stats.strength // 4, actor.stats.strength)
                * (1 - resist) * crit
            )
            target.health.current -= damage
            if damage > 0:
                messages.append(
                    f"{actor.name} does an additional {damage} damage to {target.name}.\n"
                )
                if not target.is_alive() or (
                    _rng.randint(actor.stats.intel // 2, actor.stats.intel)
                    > _rng.randint(target.stats.wisdom // 2, target.stats.wisdom)
                    + target.check_mod("magic def", enemy=actor)
                ):
                    target.stats.intel -= 1
                    messages.append(
                        f"{actor.name} eats a part of {target.name}'s brain, "
                        f"lowering their intelligence by 1.\n"
                    )


class DetonateEffect(Effect):
    """Detonate: self-destruct; deals massive physical damage.

    User HP → 0.  Damage = max(HP/2, HP*(1-resist)) * 1-4.
    Handles Mana Shield / Crusader Shield / dodge / ice block.
    """

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])
        messages.append(
            f"{actor.name} explodes, sending shrapnel in all directions.\n"
        )

        resist = target.check_mod("resist", enemy=actor, typ="Physical")
        damage = max(
            actor.health.current // 2,
            int(actor.health.current * (1 - resist)),
        ) * _rng.randint(1, 4)

        # Shield absorption
        if target.magic_effects["Mana Shield"].active:
            _, message, damage = target._apply_mana_shield(damage)
            messages.append(message)
        elif (
            hasattr(target, "cls")
            and target.cls.name == "Crusader"
            and getattr(target, "power_up", False)
            and target.class_effects["Power Up"].active
        ):
            _, message, damage = target.handle_crusader_shield(damage)
            messages.append(message)

        if damage > 0:
            if any([target.magic_effects["Ice Block"].active,
                    getattr(target, "tunnel", False)]):
                messages.append("It has no effect.\n")
            else:
                t_chance = target.check_mod("luck", enemy=actor, luck_factor=20)
                if (
                    _rng.randint(0, target.check_mod("speed", enemy=actor) // 15)
                    + t_chance
                ):
                    damage = max(1, damage // 2)
                    messages.append(
                        f"{target.name} dodges the shrapnel, only taking half damage.\n"
                    )
                target.health.current -= damage
                result.damage = damage
                messages.append(
                    f"{target.name} takes {damage} damage from the shrapnel.\n"
                )
        else:
            messages.append(f"{target.name} was unhurt by the explosion.\n")

        # Self-destruct
        actor.health.current = 0


class CrushEffect(Effect):
    """Crush: grab + crush + throw for physical damage.

    Custom hit/dodge, 25% target HP or str-based, throw for fall damage.
    Fixes original bug where use_str was unbound in Duplicates branch.
    """

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])

        resist = target.check_mod("resist", enemy=actor, typ="Physical")
        a_chance = actor.check_mod("luck", enemy=target, luck_factor=15)
        d_chance = target.check_mod("luck", enemy=actor, luck_factor=10)

        # Dodge
        dodge = (
            _rng.randint(0, target.check_mod("speed", enemy=actor) // 2) + d_chance
            > _rng.randint(0, actor.check_mod("speed", enemy=target)) + a_chance
        )
        if target.incapacitated():
            hit = True
            dodge = False
        else:
            a_hit = actor.stats.dex + actor.stats.strength
            d_hit = target.stats.dex + target.stats.strength
            hit = (
                _rng.randint(a_hit // 2, a_hit) + a_chance
                > _rng.randint(d_hit // 2, d_hit) + d_chance
            )

        if dodge:
            messages.append(f"{target.name} evades the attack.\n")
            return

        # Duplicates check
        if hit and target.magic_effects["Duplicates"].active:
            chance = target.magic_effects["Duplicates"].duration - actor.check_mod(
                "luck", luck_factor=15
            )
            if _rng.randint(0, max(0, chance)):
                hit = False
                messages.append(
                    f"{actor.name} grabs for {target.name} but gets a mirror image "
                    f"instead and it vanishes from existence.\n"
                )
                target.magic_effects["Duplicates"].duration -= 1
                if not target.magic_effects["Duplicates"].duration:
                    target.magic_effects["Duplicates"].active = False

        if hit:
            messages.append(f"{actor.name} grabs {target.name}.\n")
            crit = 1
            if (a_chance - d_chance) * 0.1 > _rng.random():
                crit = 2
            damage = max(
                int(target.health.current * 0.25),
                int(
                    _rng.randint(actor.stats.strength // 2, actor.stats.strength)
                    * (1 - resist) * crit
                ),
            )
            target.health.current -= damage
            result.damage = damage
            dmg_msg = (
                f"{actor.name} crushes {target.name}, dealing {damage} damage"
            )
            if crit > 1:
                dmg_msg += " (Critical hit!)"
            messages.append(dmg_msg + ".\n")

            # Throw
            if (
                _rng.randint(actor.stats.strength // 2, actor.stats.strength)
                > _rng.randint(0, target.check_mod("speed", enemy=actor)) + d_chance
            ):
                fall_damage = int(
                    _rng.randint(actor.stats.strength // 2, actor.stats.strength)
                    * (1 - resist)
                )
                target.health.current -= fall_damage
                messages.append(
                    f"{actor.name} throws {target.name} to the ground, "
                    f"dealing {fall_damage} damage.\n"
                )
            else:
                messages.append(
                    f"{target.name} rolls as they hit the ground, "
                    f"preventing any fall damage.\n"
                )
        else:
            messages.append(
                f"{actor.name} grabs for {target.name} but misses.\n"
            )


# =====================================================================
# Batch 10 effect types
# =====================================================================


class MaelstromEffect(Effect):
    """Maelstrom: reduce target HP to a percentage of max.

    Intel vs wisdom save determines severity (success_pct or fail_pct).
    Fixes original bug: uses actor.stats.intel instead of actor.intel.
    """

    def __init__(self, success_pct: float = 0.10, fail_pct: float = 0.25, **_kw):
        super().__init__()
        self.success_pct = success_pct
        self.fail_pct = fail_pct

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])

        if _rng.randint(0, actor.stats.intel) > _rng.randint(
            target.stats.wisdom // 2, target.stats.wisdom
        ):
            hp_cap = int(target.health.max * self.success_pct)
        else:
            hp_cap = int(target.health.max * self.fail_pct)

        target.health.current = min(target.health.current, hp_cap)
        # Original message logic (preserved faithfully, including quirks)
        if hp_cap > target.health.current:
            messages.append(
                f"{target.name} has their health reduced to "
                f"{int(self.fail_pct * 100)}%.\n"
            )
        else:
            messages.append("The spell is ineffective.\n")


class DisintegrateEffect(Effect):
    """Disintegrate: instant-kill attempt then % HP damage.

    Phase 1: if Death resist < 1 and charisma*(1-resist) beats con+luck → kill.
    Phase 2: if still alive, (charisma + 25% current HP) damage, luck halves.
    Bypasses Mana Shield and Reflect (handled by DataDrivenCustomSpell).
    """

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])

        resist = target.check_mod("resist", enemy=actor, typ="Death")
        chance = target.check_mod("luck", enemy=actor, luck_factor=15)

        # Phase 1: instant kill
        if resist < 1:
            if (
                _rng.randint(0, actor.stats.charisma) * (1 - resist)
                > _rng.randint(target.stats.con // 2, target.stats.con) + chance
            ):
                target.health.current = 0
                messages.append(
                    f"The intense blast from disintegrate leaves "
                    f"{target.name} in a heap of ashes.\n"
                )

        # Phase 2: damage (if still alive)
        if target.is_alive():
            damage = int(actor.stats.charisma + (target.health.current * 0.25))
            if _rng.randint(0, chance):
                messages.append(
                    f"{target.name} dodges the brunt of the blast, "
                    f"taking only half damage.\n"
                )
                damage //= 2
            target.health.current -= damage
            result.damage = damage
            messages.append(
                f"The blast from disintegrate hurts "
                f"{target.name} for {damage} damage.\n"
            )


class InspectEffect(Effect):
    """Inspect: call target.inspect() to reveal enemy details."""

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        messages = result.extra.setdefault("messages", [])
        inspect_text = target.inspect()
        messages.append(inspect_text + "\n")


class ResistImmunityEffect(Effect):
    """Set minimum resistance for a type + add status immunity.

    One-shot passive effect for PurityBody / PurityBody2.
    """

    def __init__(
        self,
        resist_type: str = "Poison",
        min_resist: float = 0.5,
        immunity_name: str = "Poison",
        **_kw,
    ):
        super().__init__()
        self.resist_type = resist_type
        self.min_resist = min_resist
        self.immunity_name = immunity_name

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        # target == user when self_target is true
        target.resistance[self.resist_type] = max(
            self.min_resist, target.resistance[self.resist_type]
        )
        if self.immunity_name not in getattr(target, "status_immunity", []):
            target.status_immunity.append(self.immunity_name)


class ResurrectionEffect(Effect):
    """Resurrection: mana-to-HP (self) or revive at % max HP (other).

    Self mode (actor == target): converts actor mana to health.
    Other mode (actor != target): sets target HP to revive_pct * max.
    """

    def __init__(self, revive_pct: float = 0.1, **_kw):
        super().__init__()
        self.revive_pct = revive_pct

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        messages = result.extra.setdefault("messages", [])

        if target is actor:
            # Self: convert mana to HP
            max_heal = target.health.max - target.health.current
            if target.mana.current > max_heal:
                target.health.current = target.health.max
                target.mana.current -= max_heal
                messages.append(
                    f"{target.name} expends mana and is healed to full life!"
                )
            else:
                heal_amount = target.mana.current
                target.health.current += heal_amount
                messages.append(
                    f"{target.name} expends all mana and is healed "
                    f"for {heal_amount} hit points!"
                )
                target.mana.current = 0
        else:
            # Revive other target
            heal = int(target.health.max * self.revive_pct)
            target.health.current = heal
            messages.append(
                f"{target.name} is brought back to life and is healed "
                f"for {heal} hit points.\n"
            )


# =====================================================================
# Batch 11 effect types
# =====================================================================


class RevealEffect(Effect):
    """Reveal: set sight, add shadow resistance, auto-unequip Pendant of Vision.

    Passive one-shot applied to the user (self_target=true).
    """

    def __init__(self, resist_bonus: float = 0.25, **_kw):
        super().__init__()
        self.resist_bonus = resist_bonus

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        messages = result.extra.setdefault("messages", [])
        target.sight = True
        target.resistance["Shadow"] += self.resist_bonus
        if (
            hasattr(target, "equipment")
            and target.equipment.get("Pendant") is not None
            and getattr(target.equipment["Pendant"], "name", "") == "Pendant of Vision"
        ):
            target.modify_inventory(target.equipment["Pendant"], 1)
            target.equipment["Pendant"] = target.unequip("Pendant")


class TransformEffect(Effect):
    """Transform: set user.transform_type to an enemy creature instance.

    The creature name maps to a class in src.core.enemies.
    """

    def __init__(self, creature: str = "Panther", **_kw):
        super().__init__()
        self.creature = creature

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        from src.core import enemies as _enemies
        messages = result.extra.setdefault("messages", [])
        creature_cls = getattr(_enemies, self.creature, None)
        if creature_cls is not None:
            target.transform_type = creature_cls()


class StompEffect(Effect):
    """Stomp: STR-based damage with dodge/hit/crit/duplicates + stun chance.

    Full combat pipeline: dodge → hit → duplicates → cover → crit →
    damage (with resist + mana shield + crusader shield) → stun.
    """

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])

        resist = target.check_mod("resist", enemy=actor, typ="Physical")
        a_chance = actor.check_mod("luck", enemy=target, luck_factor=10)
        d_chance = target.check_mod("luck", enemy=actor, luck_factor=15)

        # Dodge
        dodge = (
            _rng.randint(0, target.check_mod("speed", enemy=actor) // 2) + d_chance
            > _rng.randint(0, actor.check_mod("speed", enemy=actor)) + a_chance
        )
        if target.incapacitated():
            dodge = False
            hit = True
        else:
            hit = actor.hit_chance(target, typ="weapon")

        if dodge:
            messages.append(f"{target.name} evades the attack.\n")
            return

        # Duplicates check
        if hit and target.magic_effects["Duplicates"].active:
            chance = target.magic_effects["Duplicates"].duration - actor.check_mod(
                "luck", luck_factor=15
            )
            if _rng.randint(0, max(0, chance)):
                hit = False
                messages.append(
                    f"{actor.name} stomps but hits a mirror image of "
                    f"{target.name} and it vanishes from existence.\n"
                )
                target.magic_effects["Duplicates"].duration -= 1
                if not target.magic_effects["Duplicates"].duration:
                    target.magic_effects["Duplicates"].active = False

        cover = result.extra.get("use_kwargs", {}).get("cover", False)
        if cover and hit:
            messages.append(
                f"{target.familiar.name} steps in front of the attack, "
                f"absorbing the damage directed at {target.name}.\n"
            )
        elif hit:
            crit = 1
            if (a_chance - d_chance) * 0.1 > _rng.random():
                crit = 2
            damage = int(
                _rng.randint(actor.stats.strength // 2, actor.stats.strength)
                * (1 - resist) * crit
            )

            # Mana Shield
            if target.magic_effects["Mana Shield"].active:
                hit, message, damage = target._apply_mana_shield(damage)
                messages.append(message)
            elif (
                getattr(target, "cls", None)
                and target.cls.name == "Crusader"
                and getattr(target, "power_up", False)
                and target.class_effects["Power Up"].active
            ):
                hit, message, damage = target.handle_crusader_shield(damage)
                messages.append(message)

            if damage > 0:
                target.health.current -= damage
                result.damage = damage
                dmg_msg = (
                    f"{actor.name} stomps {target.name}, dealing "
                    f"{damage} damage"
                )
                if crit > 1:
                    dmg_msg += " (Critical hit!)"
                messages.append(dmg_msg + ".\n")

                # Stun check (with immunity)
                if not any([
                    "Stun" in getattr(target, "status_immunity", []),
                    f"Status-Stun" in getattr(
                        target.equipment.get("Pendant", None), "mod", ""
                    ) if hasattr(target, "equipment") else False,
                    "Status-All" in getattr(
                        target.equipment.get("Pendant", None), "mod", ""
                    ) if hasattr(target, "equipment") else False,
                ]):
                    if not target.status_effects["Stun"].active:
                        att_roll = _rng.randint(actor.stats.strength // 2, actor.stats.strength)
                        def_roll = _rng.randint(target.stats.con // 2, target.stats.con)
                        if target.stun_contest_success(actor, att_roll, def_roll):
                            turns = 1 + int(crit > 1)
                            if target.apply_stun(turns, source="Stomp", applier=actor):
                                messages.append(
                                    f"{actor.name} stunned {target.name}.\n"
                                )
            else:
                messages.append(
                    f"{actor.name} stomps {target.name} but deals no damage.\n"
                )
        else:
            messages.append(f"{actor.name} misses {target.name}.\n")


class ThrowRockEffect(Effect):
    """ThrowRock: random rock size → STR-based damage + prone chance.

    Full combat pipeline: dodge → hit → duplicates → cover → crit →
    damage (with armor + resist + mana shield + crusader shield) → prone.
    """

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])

        size = _rng.randint(0, 4)
        sizes = ["tiny", "small", "medium", "large", "massive"]
        messages.append(
            f"{actor.name} throws a {sizes[size]} rock at {target.name}.\n"
        )

        a_chance = actor.check_mod("luck", enemy=target, luck_factor=10)
        d_chance = target.check_mod("luck", enemy=actor, luck_factor=15)
        dam_red = target.check_mod("armor", enemy=actor)
        resist = target.check_mod("resist", enemy=actor, typ="Physical")

        # Dodge
        dodge = (
            _rng.randint(0, target.check_mod("speed", enemy=actor) // 2) + d_chance
            > _rng.randint(0, actor.check_mod("speed", enemy=actor)) + a_chance
        )
        hit = actor.hit_chance(target, typ="weapon")

        if target.incapacitated():
            dodge = False
            hit = True

        if dodge:
            messages.append(f"{target.name} evades the attack.\n")
            return

        # Duplicates check
        if hit and target.magic_effects["Duplicates"].active:
            chance = target.magic_effects["Duplicates"].duration - actor.check_mod(
                "luck", luck_factor=15
            )
            if _rng.randint(0, max(0, chance)):
                hit = False
                messages.append(
                    f"{actor.name} throws a rock but hits a mirror image "
                    f"of {target.name} and it vanishes from existence.\n"
                )
                target.magic_effects["Duplicates"].duration -= 1
                if not target.magic_effects["Duplicates"].duration:
                    target.magic_effects["Duplicates"].active = False

        cover = result.extra.get("use_kwargs", {}).get("cover", False)
        if hit and cover:
            messages.append(
                f"{target.familiar.name} steps in front of the attack, "
                f"absorbing the damage directed at {target.name}.\n"
            )
        elif hit:
            crit = 1
            if (a_chance - d_chance) * 0.1 > _rng.random():
                crit = 2
            damage = (
                _rng.randint(
                    actor.stats.strength // 4,
                    actor.stats.strength // 3,
                )
                * (size + 1)
                * crit
            )
            damage = max(0, int((damage - dam_red) * (1 - resist)))

            # Mana Shield
            if target.magic_effects["Mana Shield"].active:
                hit, message, damage = target._apply_mana_shield(damage)
                messages.append(message)
            elif (
                getattr(target, "cls", None)
                and target.cls.name == "Crusader"
                and getattr(target, "power_up", False)
                and target.class_effects["Power Up"].active
            ):
                hit, message, damage = target.handle_crusader_shield(damage)
                messages.append(message)

            if damage > 0:
                target.health.current -= damage
                result.damage = damage
                dmg_msg = (
                    f"{target.name} is hit by the rock and takes "
                    f"{damage} damage"
                )
                if crit > 1:
                    dmg_msg += " (Critical hit!)"
                messages.append(dmg_msg + ".\n")

                # Prone check
                if not target.physical_effects["Prone"].active:
                    if (
                        _rng.randint(
                            actor.stats.strength // 2,
                            actor.stats.strength,
                        )
                        > _rng.randint(
                            target.stats.strength // 2,
                            target.stats.strength,
                        )
                    ):
                        prone_dur = max(1, size)
                        target.physical_effects["Prone"].active = True
                        target.physical_effects["Prone"].duration = prone_dur
                        if hasattr(actor, "_emit_status_event"):
                            actor._emit_status_event(
                                target, "Prone",
                                applied=True,
                                duration=prone_dur,
                                source="Throw Rock",
                            )
                        messages.append(
                            f"{target.name} is knocked over and falls "
                            f"prone.\n"
                        )
            else:
                messages.append(f"{target.name} shrugs off the damage.\n")
        else:
            messages.append(
                f"{actor.name} misses {target.name} with the throw.\n"
            )


class StealEffect(Effect):
    """Steal: speed+luck contest to steal gold or a random item.

    Respects ice-block/tunnel, blind penalty, crit bonus.
    Activates "Steal Success" status on success.
    """

    def __init__(self, gold_cap: float = 0.05, **_kw):
        super().__init__()
        self.gold_cap = gold_cap

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])

        # Get crit from caller (Mug passes crit via use_kwargs)
        use_kw = result.extra.get("use_kwargs", {})
        crit = use_kw.get("crit", 1)

        gold_or_item = _rng.choice(["Gold", "Item"])
        chance = actor.check_mod("luck", enemy=target, luck_factor=16)
        dv = 1 + int(actor.status_effects["Blind"].active)

        if (
            _rng.randint(
                0, int(actor.check_mod("speed", enemy=actor) * crit) // dv
            ) + chance
            > _rng.randint(0, target.check_mod("speed", enemy=actor))
        ):
            if gold_or_item == "Item":
                if len(target.inventory) != 0:
                    item_key = _rng.choice(list(target.inventory))
                    item = target.inventory[item_key][0]
                    target.modify_inventory(item, subtract=True)
                    try:
                        actor.modify_inventory(item)
                    except AttributeError:
                        pass
                    steal_effect = actor.status_effects.get("Steal Success")
                    if steal_effect is not None:
                        steal_effect.active = True
                        steal_effect.duration = max(
                            steal_effect.duration, 2
                        )
                    messages.append(
                        f"{actor.name} steals {item_key} from "
                        f"{target.name}.\n"
                    )
                    return
                messages.append(
                    f"{target.name} doesn't have anything to steal.\n"
                )
                return
            else:
                gold_amount = _rng.randint(
                    1, max(1, int(target.gold * self.gold_cap))
                )
                actor.gold += gold_amount
                target.gold -= gold_amount
                steal_effect = actor.status_effects.get("Steal Success")
                if steal_effect is not None:
                    steal_effect.active = True
                    steal_effect.duration = max(steal_effect.duration, 2)
                messages.append(
                    f"{actor.name} steals {gold_amount} gold from "
                    f"{target.name}.\n"
                )
                return
        messages.append("Steal fails.\n")


class MugEffect(Effect):
    """Mug: after a weapon hit, attempt to steal from the target.

    Instantiates Steal() and calls use() with the crit from the weapon hit.
    Preserves original double-mana-cost (Mug + Steal).
    """

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        if not result.hit:
            return
        messages = result.extra.setdefault("messages", [])
        crit = result.extra.get("last_crit", 1)
        from src.core.abilities import Steal
        steal_result = Steal().use(actor, target, crit=crit, mug=True)
        if isinstance(steal_result, str):
            messages.append(steal_result)
        else:
            messages.append(str(steal_result))


class CounterspellEffect(Effect):
    """Counterspell: pick a random spell from the user's spellbook and cast it.

    If the chosen spell is a healing spell, target = actor (self-heal).
    """

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])
        spells = list(actor.spellbook["Spells"].values())
        if not spells:
            messages.append(f"{actor.name} has no spells to counter with.\n")
            return
        spell = _rng.choice(spells)
        cast_target = actor if spell.subtyp == "Heal" else target
        cover = result.extra.get("use_kwargs", {}).get("cover", False)
        cast_result = spell.cast(actor, target=cast_target, cover=cover)
        if isinstance(cast_result, str):
            messages.append(cast_result)
        else:
            messages.append(str(cast_result))


class ElementalStrikeEffect(Effect):
    """ElementalStrike: on weapon hit, cast a random elemental spell.

    Picks from a hardcoded list filtered by user's spellbook.
    On crit, casts the spell twice.
    """

    _SPELL_NAMES = [
        "Firebolt", "Ice Lance", "Shock", "Scorch",
        "Water Jet", "Tremor", "Gust",
    ]

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])
        if not result.hit:
            return
        if target is not None and not target.is_alive():
            return

        # Build list of available elemental spells from actor's spellbook
        from src.core import abilities as _abilities
        cast_list = []
        for spell_name in self._SPELL_NAMES:
            if spell_name in actor.spellbook.get("Spells", {}):
                # Look up the class by converting name to class name
                cls_name = spell_name.replace(" ", "")
                spell_cls = getattr(_abilities, cls_name, None)
                if spell_cls is not None:
                    cast_list.append(spell_cls())
        if not cast_list:
            return

        cover = result.extra.get("use_kwargs", {}).get("cover", False)
        spell = _rng.choice(cast_list)
        messages.append(
            f"The enemy is struck by the elemental force of "
            f"{spell.subtyp}.\n"
        )
        cast_result = spell.cast(
            actor, target=target, special=True, cover=cover
        )
        if isinstance(cast_result, str):
            messages.append(cast_result)
        else:
            messages.append(str(cast_result))

        crit = result.extra.get("last_crit", 1)
        if crit > 1 and target is not None and target.is_alive():
            cast_result = spell.cast(
                actor, target=target, special=True, cover=cover
            )
            if isinstance(cast_result, str):
                messages.append(cast_result)
            else:
                messages.append(str(cast_result))


class BlackjackEffect(Effect):
    """Blackjack: play a round of blackjack with random or callback-driven outcome.

    Outcomes: User Win, Target Win, Draw, User Break, Target Break.
    Currently stub effects (flavor text only per original implementation).
    """

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])

        use_kw = result.extra.get("use_kwargs", {})
        callback = use_kw.get("blackjack_callback", None)
        if callback is not None:
            outcome = callback(actor, target)
        else:
            outcome = _rng.choice([
                "User Win", "Target Win", "Draw",
                "User Break", "Target Break",
            ])

        if outcome == "Target Win":
            messages.append(f"{target.name} wins the hand!\n")
        elif outcome == "Target Break":
            messages.append(f"Oh no, {target.name} busted...\n")
        elif outcome == "User Break":
            messages.append(f"Oh no, {actor.name} busted...\n")
        elif outcome == "User Win":
            messages.append(f"{actor.name} wins the hand!\n")
        else:
            messages.append("It's a draw!\n")


# ======================================================================
# Batch 13 Effects – Doublecast / ChooseFate / Shapeshift / TetraDisaster
# ======================================================================


class DoublecastEffect(Effect):
    """Cast multiple spells from the user's spellbook in a single turn.

    Used by Doublecast (cast_count=2) and Triplecast (cast_count=3).

    Parameters (YAML):
        cast_count (int): Number of spells to cast (default 2).
        exclude_spells (list[str]): Spell names to exclude (default ["Magic Missile"]).
        ability_cost (int): The parent ability's mana cost, used for refund logic
            when no affordable spells are available.

    The UI may pass a ``spell_selector`` callback via ``use_kwargs``.  When
    present it is called as ``spell_selector(user, spell_list, cast_index)``
    returning the chosen spell key.  Without it a random spell is picked.
    """

    def __init__(self, cast_count: int = 2,
                 exclude_spells: list[str] | None = None,
                 ability_cost: int = 0):
        super().__init__()
        self.cast_count = cast_count
        self.exclude_spells = exclude_spells or ["Magic Missile"]
        self.ability_cost = ability_cost

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])
        use_kw = result.extra.get("use_kwargs", {})
        spell_selector = use_kw.get("spell_selector")
        cover = result.extra.get("cover", False)

        j = 0
        while j < self.cast_count:
            spell_list = []
            for entry in actor.spellbook.get("Spells", {}):
                spell_obj = actor.spellbook["Spells"][entry]
                if spell_obj.cost <= actor.mana.current and spell_obj.name not in self.exclude_spells:
                    if actor.cls != actor:
                        spell_list.append(f"{entry}  {spell_obj.cost}")
                    else:
                        spell_list.append(str(entry))
            if len(spell_list) == 0:
                messages.append(
                    f"{actor.name} does not have enough mana to cast any"
                    f" spells with {result.action}.\n"
                )
                actor.mana.current += self.ability_cost
                break
            # UI-agnostic spell selection
            if spell_selector is not None:
                spell_key = spell_selector(actor, spell_list, j)
                spell_key = spell_key.rsplit("  ", 1)[0]
            else:
                spell_key = _rng.choice(
                    [s.rsplit("  ", 1)[0] for s in spell_list]
                )
            spell = actor.spellbook["Spells"][spell_key]
            cast_message = spell.cast(actor, target=target, cover=cover)
            messages.append(str(cast_message))
            j += 1
            if not target.is_alive():
                break


class ChooseFateEffect(Effect):
    """Let the player choose the Devil's action for the turn.

    Presents three options (Attack / Hellfire / Crush) via a
    ``selection_callback`` passed through ``use_kwargs``.

    - *Attack*: weapon damage with ``dmg_mod``, user's ``damage_mod`` increases.
    - *Hellfire*: user's ``spell_mod`` increases, casts Hellfire on target.
    - *Crush*: uses Crush on target, both mods decrease.

    Parameters (YAML):
        dmg_mod (float): Weapon damage multiplier for Attack (default 1.5).
    """

    def __init__(self, dmg_mod: float = 1.5):
        super().__init__()
        self.dmg_mod = dmg_mod

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])
        use_kw = result.extra.get("use_kwargs", {})
        selection_callback = use_kw.get("selection_callback")

        choose_message = "I'm bored, you choose."
        options = ["Attack", "Hellfire", "Crush"]
        if selection_callback is not None:
            option_index = selection_callback(choose_message, options)
        else:
            option_index = _rng.randint(0, len(options) - 1)

        mod_up = _rng.randint(10, 25)
        if options[option_index] == "Attack":
            wd_str, _, _ = actor.weapon_damage(target, dmg_mod=self.dmg_mod)
            messages.append(wd_str)
            actor.damage_mod += mod_up
            messages.append("Hahaha, my power increases!\n")
        elif options[option_index] == "Hellfire":
            from src.core.abilities import Hellfire
            actor.spell_mod += mod_up
            cast_msg = Hellfire().cast(actor, target=target)
            messages.append(str(cast_msg))
            messages.append("The devastation will only get worse from here.\n")
        elif options[option_index] == "Crush":
            from src.core.abilities import Crush
            use_msg = Crush().use(actor, target)
            messages.append(str(use_msg))
            mod_down = _rng.randint(0, 10)
            if actor.damage_mod > 0:
                actor.damage_mod -= mod_down
            if actor.spell_mod > 0:
                actor.spell_mod -= mod_down
            messages.append("Interesting choice...maybe I'll show pity.\n")


class ShapeshiftEffect(Effect):
    """Transform the user into a random creature from their transform list.

    Copies all stats, equipment, spellbook, resistances, etc. from the
    chosen creature.  Re-adds Shapeshift to the new spellbook and applies
    a ``Shapeshifted`` status cooldown.

    This effect expects ``self_target: true`` in the YAML so that both
    *actor* and *target* refer to the shapeshifting entity.

    Parameters (YAML):
        status_name (str): Cooldown status to apply (default "Shapeshifted").
        status_duration (int): Duration of cooldown in turns (default 3).
    """

    def __init__(self, status_name: str = "Shapeshifted",
                 status_duration: int = 3):
        super().__init__()
        self.status_name = status_name
        self.status_duration = status_duration

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        # With self_target the effect_target == actor (the shapeshifter)
        user = target
        messages = result.extra.setdefault("messages", [])

        while True:
            s_creature = _rng.choice(user.transform)()
            if user.cls.name != s_creature.cls.name:
                break

        old_name = user.name
        user.cls = s_creature.cls
        user.stats = s_creature.stats
        user.equipment = s_creature.equipment
        user.spellbook = s_creature.spellbook
        user.resistance = s_creature.resistance
        user.flying = s_creature.flying
        user.invisible = s_creature.invisible
        user.sight = s_creature.sight
        user.name = s_creature.name
        user.picture = s_creature.picture

        # Re-add Shapeshift to new spellbook
        from src.core.abilities import Shapeshift as ShapeshiftAbility
        user.spellbook["Skills"]["Shapeshift"] = ShapeshiftAbility()

        # Apply cooldown status
        user.status_effects[self.status_name].active = True
        user.status_effects[self.status_name].duration = self.status_duration
        try:
            user._emit_status_event(
                user, self.status_name, applied=True,
                duration=self.status_duration, source="Shapeshift",
            )
        except Exception:
            pass

        messages.append(
            f"{old_name} changes shape, becoming a {s_creature.name}.\n"
        )


class TetraDisasterEffect(Effect):
    """Cast all elemental spells from the user's spellbook and activate Power Up.

    Iterates the user's Spells section for spells whose ``subtyp`` matches
    one of the configured elements, casts each with ``special=True``
    (no mana cost), then activates the Geomancer's Power Up for elemental
    resistance.

    Parameters (YAML):
        elements (list[str]): Element subtypes to match (default Fire/Water/Wind/Earth).
        power_up_duration (int): Duration of the Power Up buff (default 5).
    """

    def __init__(self, elements: list[str] | None = None,
                 power_up_duration: int = 5):
        super().__init__()
        self.elements = elements or ["Fire", "Water", "Wind", "Earth"]
        self.power_up_duration = power_up_duration

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        messages = result.extra.setdefault("messages", [])
        cover = result.extra.get("cover", False)

        for spell in list(actor.spellbook.get("Spells", {}).values()):
            if hasattr(spell, "subtyp") and spell.subtyp in self.elements:
                try:
                    cast_msg = spell.cast(
                        actor, target=target, cover=cover, special=True,
                    )
                    messages.append(str(cast_msg))
                except Exception:
                    pass

        # Activate Power Up for elemental resistance
        if hasattr(actor, "class_effects") and "Power Up" in actor.class_effects:
            actor.class_effects["Power Up"].active = True
            actor.class_effects["Power Up"].duration = self.power_up_duration


# ======================================================================
# Batch 14 Effects – ConsumeItem / DestroyMetal / SlotMachine / Totem
# ======================================================================


class ConsumeItemEffect(Effect):
    """Steal a random item from the target and consume it for a status effect.

    Performs a speed+luck contest.  On success, steals a random inventory
    item, removes it, and applies an effect based on item type:
      Weapon → Attack buff, Armor → Defense buff, OffHand/Tome → Magic buff,
      OffHand/other → Magic Defense buff, Accessory/Ring → random Attack/Defense,
      Accessory/other → random Magic/MagicDefense, Potion → Regen or Poison,
      else → random status (Berserk/Blind/Doom/Silence/Sleep/Stun).
    If the target has no items, steal gold and heal the user instead.

    Parameters (YAML):  (none – behaviour is fully self-contained)
    """

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])
        if target is None:
            return
        if any([target.magic_effects["Ice Block"].active,
                getattr(target, "tunnel", False)]):
            messages.append("It has no effect.\n")
            return

        u_chance = actor.check_mod("luck", enemy=target, luck_factor=10)
        t_chance = target.check_mod("luck", enemy=actor, luck_factor=10)

        if (_rng.randint(0, actor.check_mod("speed", enemy=actor)) + u_chance
                > _rng.randint(0, target.check_mod("speed", enemy=actor)) + t_chance):
            if len(target.inventory) != 0 and _rng.randint(0, u_chance):
                item_key = _rng.choice(list(target.inventory))
                item = target.inventory[item_key][0]
                target.modify_inventory(item, subtract=True)
                messages.append(
                    f"{actor.name} steals {item_key} from {target.name} and consumes it.\n"
                )
                duration = max(1, int(1 / item.rarity))
                amount = max(1, int(2 / item.rarity))

                if item.typ == "Weapon":
                    effect = "Attack"
                elif item.typ == "Armor":
                    effect = "Defense"
                elif item.typ == "OffHand":
                    effect = "Magic" if item.subtyp == "Tome" else "Magic Defense"
                elif item.typ == "Accessory":
                    effect = (_rng.choice(["Attack", "Defense"]) if item.subtyp == "Ring"
                              else _rng.choice(["Magic", "Magic Defense"]))
                elif item.typ == "Potion":
                    effect = "Regen" if item.subtyp != "Stat" else "Poison"
                else:
                    effect = _rng.choice(
                        ["Berserk", "Blind", "Doom", "Silence", "Sleep", "Stun"]
                    )

                # Immunity check
                status_effects = [
                    "Berserk", "Blind", "Doom", "Poison", "Silence", "Sleep", "Stun"
                ]
                if any([
                    effect in actor.status_immunity,
                    f"Status-{effect}" in actor.equipment["Pendant"].mod,
                    "Status-All" in actor.equipment["Pendant"].mod
                    and effect in status_effects,
                ]):
                    messages.append(f"{actor.name} is immune to {effect.lower()}.\n")
                else:
                    messages.append(
                        f"{actor.name} is affected by {effect.lower()}.\n"
                    )
                    effect_dict = actor.effect_handler(effect)
                    effect_dict[effect].active = True
                    if effect in ["Blind", "Disarm", "Silence"]:
                        effect_dict[effect].duration = -1
                    else:
                        effect_dict[effect].duration = max(
                            duration, effect_dict[effect].duration
                        )
                    if effect in ["Poison", "Regen"]:
                        amount = int((actor.health.max * 0.01) * amount)
                        effect_dict[effect].extra = amount
                    if effect in actor.stat_effects:
                        combat_effect = (
                            "magic_def" if effect == "Magic Defense"
                            else effect.lower()
                        )
                        amount *= actor.combat.__dict__[combat_effect] // 10
                        effect_dict[effect].extra = amount
                        messages.append(
                            f"{actor.name}'s {effect.lower()} is temporarily "
                            f"increased by {amount}.\n"
                        )
            else:
                gold = (_rng.randint(target.gold // 100, target.gold // 50)
                        * u_chance)
                regen = gold // 10
                messages.append(
                    f"{actor.name} steals {gold} gold from {target.name} "
                    f"and consumes it.\n"
                )
                messages.append(
                    f"{actor.name} regains {regen} health and mana.\n"
                )
                actor.health.current = min(
                    actor.health.current + regen, actor.health.max
                )
                actor.mana.current = min(
                    actor.mana.current + regen, actor.mana.max
                )
        else:
            messages.append(f"{actor.name} can't steal anything.\n")


class DestroyMetalEffect(Effect):
    """Target metal items in the enemy's inventory/equipment and destroy them.

    Searches inventory first, then equipment, for items with metal subtypes.
    Uses a luck-based chance to destroy the selected item.

    Parameters (YAML):
        metal_subtypes (list[str]): Subtypes considered "metal".
    """

    METAL_SUBTYPES_DEFAULT = [
        "Fist", "Dagger", "Club", "Sword", "Ninja Blade", "Longsword",
        "Battle Axe", "Polearm", "Shield", "Heavy", "Ring", "Pendant", "Key",
    ]

    def __init__(self, metal_subtypes: list[str] | None = None, **_kw):
        super().__init__()
        self.metal_subtypes = metal_subtypes or self.METAL_SUBTYPES_DEFAULT

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])
        if target is None:
            return

        from src.core.items import remove_equipment

        metal_items = self.metal_subtypes
        destroy_list: list = []
        destroy_loc = "inv"
        for item in [target.inventory[x][0] for x in target.inventory]:
            if item.subtyp in metal_items and not item.ultimate and item.rarity > 0:
                destroy_list.append(item)
        if len(destroy_list) == 0:
            destroy_loc = "equip"
            for item in target.equipment.values():
                if item.subtyp in metal_items and not item.ultimate and item.rarity > 0:
                    destroy_list.append(item)
        try:
            destroy_item = _rng.choice(destroy_list)
            t_chance = target.check_mod("luck", enemy=actor, luck_factor=5)
            if not _rng.randint(0, int(2 / destroy_item.rarity) + t_chance):
                if destroy_loc == "inv":
                    messages.append(
                        f"{actor.name} destroys a {destroy_item.name} out of "
                        f"{target.name}'s inventory.\n"
                    )
                    target.modify_inventory(destroy_item, subtract=True)
                elif destroy_loc == "equip":
                    if destroy_item.typ not in ["Weapon", "Accessory"]:
                        messages.append(
                            f"{actor.name} destroys {target.name}'s "
                            f"{destroy_item.typ}.\n"
                        )
                        target.equipment[destroy_item.typ] = remove_equipment(
                            destroy_item.typ
                        )
                    elif destroy_item.typ == "Accessory":
                        messages.append(
                            f"{actor.name} destroys {target.name}'s "
                            f"{destroy_item.subtyp}.\n"
                        )
                        target.equipment[destroy_item.subtyp] = remove_equipment(
                            destroy_item.subtyp
                        )
                    else:
                        if target.equipment["OffHand"] == destroy_item:
                            target.equipment["OffHand"] = remove_equipment("OffHand")
                            messages.append(
                                f"{actor.name} destroys {target.name}'s "
                                f"offhand weapon.\n"
                            )
                        else:
                            target.equipment[destroy_item.typ] = remove_equipment(
                                destroy_item.typ
                            )
                            messages.append(
                                f"{actor.name} destroys {target.name}'s "
                                f"{destroy_item.typ}.\n"
                            )
                else:
                    raise AssertionError("You shouldn't reach here.")
            else:
                messages.append(f"{actor.name} fails to destroy any items.\n")
        except IndexError:
            messages.append(f"{target.name} isn't carrying any metal items.\n")


class SlotMachineEffect(Effect):
    """Slot Machine: spin 3 digits and resolve outcomes.

    The UI may pass a ``slot_machine_callback`` and/or ``textbox_callback``
    via ``use_kwargs``.

    Outcomes: Death (666/999), Trips (full heal), Straight (product damage),
    Palindrome (cast high-level spell by middle digit), Pairs (random effect),
    Evens (gold), Odds (random item), Chance (weapon damage), Nothing.

    Parameters (YAML):  (none – behaviour is self-contained)
    """

    HANDS = {
        "Death": ["666", "999"],
        "Trips": ["000", "111", "222", "333", "444", "555", "777", "888"],
        "Straight": [
            "012", "123", "234", "345", "456", "567", "678", "789",
        ],
        "Palindrome": [
            f"{a}{b}{a}"
            for a in range(10) for b in range(10) if a != b
        ],
    }

    def __init__(self, **_kw):
        super().__init__()

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random as _rng
        messages = result.extra.setdefault("messages", [])
        if target is None:
            return

        use_kw = result.extra.get("use_kwargs", {})
        slot_machine_callback = use_kw.get("slot_machine_callback")
        textbox_callback = use_kw.get("textbox_callback")

        user_chance = actor.check_mod("luck", enemy=target, luck_factor=10)
        target_chance = target.check_mod("luck", enemy=actor, luck_factor=10)

        hands = self.HANDS
        success = False
        retries = 0

        while not success:
            if slot_machine_callback is not None:
                spin = slot_machine_callback(actor, target)
            else:
                spin = (f"{_rng.randint(0,9)}{_rng.randint(0,9)}"
                        f"{_rng.randint(0,9)}")

            if spin in hands["Death"]:
                messages.append("The mark of the beast!\n")
                success = True
                if target_chance > user_chance + 1:
                    target = actor
                if any([target.magic_effects["Ice Block"].active,
                        getattr(target, "tunnel", False)]):
                    messages.append("It has no effect.\n")
                elif "Death" not in target.status_immunity:
                    target.health.current = 0
                    messages.append(f"Death has come for {target.name}!\n")
                else:
                    messages.append(
                        f"{target.name} is immune to death spells.\n"
                    )

            elif spin in hands["Trips"]:
                messages.append("3 of a Kind!\n")
                success = True
                if any([target.magic_effects["Ice Block"].active,
                        _rng.randint(0, max(1, user_chance))]):
                    target = actor
                target.health.current = target.health.max
                target.mana.current = target.mana.max
                messages.append(
                    f"{target.name} has been revitalized! "
                    f"Health and mana are restored.\n"
                )
                from src.core import abilities as _abilities
                cleanse_result = _abilities.Cleanse().cast(target, special=True)
                messages.append(
                    str(cleanse_result) if not isinstance(cleanse_result, str)
                    else cleanse_result
                )

            elif "".join(sorted(spin)) in hands["Straight"]:
                messages.append("Straight!\n")
                success = True
                if target_chance > user_chance + 1:
                    target = actor
                ints = [int(x) for x in list(spin)]
                damage = 1
                for i in ints:
                    damage *= i
                if target.magic_effects["Ice Block"].active:
                    messages.append("It has no effect.\n")
                else:
                    target.health.current -= damage
                    messages.append(
                        f"{target.name} takes {damage} damage.\n"
                    )

            elif spin in hands["Palindrome"]:
                messages.append("Palindrome!\n")
                success = True
                if target_chance > user_chance + 1:
                    target = actor
                from src.core import abilities as _abilities
                spell_list = [
                    _abilities.MagicMissile3(),
                    _abilities.Firestorm(),
                    _abilities.IceBlizzard(),
                    _abilities.Electrocution(),
                    _abilities.Tsunami(),
                    _abilities.Earthquake(),
                    _abilities.Tornado(),
                    _abilities.ShadowBolt3(),
                    _abilities.Holy3(),
                    _abilities.Ultima(),
                ]
                spell = spell_list[int(spin[1])]
                messages.append(f"{spell.name} is cast!\n")
                if any([target.magic_effects["Ice Block"].active,
                        getattr(target, "tunnel", False)]):
                    messages.append("It has no effect.\n")
                else:
                    cast_result = spell.cast(actor, target=target, special=True)
                    messages.append(
                        str(cast_result) if not isinstance(cast_result, str)
                        else cast_result
                    )

            elif len(set(spin)) == 2:
                messages.append("Pairs!\n")
                success = True
                duration = int(min(set(list(spin)),
                                   key=list(spin).count))
                if duration == 0:
                    duration = 10
                amount = int(max(set(list(spin)),
                                 key=list(spin).count))
                if amount == 0:
                    amount = 10
                amount **= 2
                effects = [
                    "Berserk", "Blind", "Doom", "Poison", "Silence",
                    "Sleep", "Stun", "Bleed", "Disarm", "Prone",
                    "Attack", "Defense", "Magic", "Magic Defense", "Speed",
                    "DOT", "Reflect", "Regen",
                ]
                if not _rng.randint(0, 1):
                    target = actor
                effect = _rng.choice(effects)
                status_effects = [
                    "Berserk", "Blind", "Doom", "Poison", "Silence",
                    "Sleep", "Stun",
                ]
                if any([
                    effect in target.status_immunity,
                    f"Status-{effect}" in target.equipment["Pendant"].mod,
                    "Status-All" in target.equipment["Pendant"].mod
                    and effect in status_effects,
                ]):
                    messages.append(
                        f"{target.name} is immune to {effect.lower()}.\n"
                    )
                elif any([target.magic_effects["Ice Block"].active,
                          getattr(target, "tunnel", False)]):
                    messages.append("It has no effect.\n")
                else:
                    messages.append(
                        f"{effect} has been randomly selected to affect "
                        f"{target.name}.\n"
                    )
                    effect_dict = target.effect_handler(effect)
                    effect_dict[effect].active = True
                    if effect in ["Blind", "Disarm", "Silence"]:
                        effect_dict[effect].duration = -1
                    else:
                        effect_dict[effect].duration = max(
                            duration, effect_dict[effect].duration
                        )
                    if effect == ["Poison", "Bleed", "DOT"]:
                        amount *= int(target.health.max * 0.01)
                        effect_dict[effect].extra = amount
                    if effect in target.stat_effects:
                        combat_effect = (
                            "magic_def" if effect == "Magic Defense"
                            else effect.lower()
                        )
                        amount *= target.combat.__dict__[combat_effect] // 10
                        messages.append(
                            f"{target.name}'s {effect.lower()} is "
                            f"temporarily increased by {amount}.\n"
                        )
                        effect_dict[effect].extra = amount

            elif all(int(x) % 2 == 0 for x in list(spin)):
                messages.append("Evens!\n")
                success = True
                if any([target.magic_effects["Ice Block"].active,
                        getattr(target, "tunnel", False),
                        user_chance + 1 >= target_chance]):
                    target = actor
                target.gold += int(spin) * 10
                messages.append(f"{target.name} gains {int(spin)} gold!\n")

            elif all(int(x) % 2 == 1 for x in list(spin)):
                messages.append("Odds!\n")
                success = True
                level = min(list(spin))
                if any([user_chance + 1 >= target_chance,
                        target.magic_effects["Ice Block"].active,
                        getattr(target, "tunnel", False)]):
                    target = actor
                from src.core import items as _items
                item_cls = _items.random_item(int(level))
                item = item_cls() if isinstance(item_cls, type) else item_cls
                try:
                    target.modify_inventory(item)
                except AttributeError:
                    pass
                messages.append(f"{target.name} gains {item.name}.\n")

            elif _rng.randint(0, user_chance):
                messages.append("Chance!\n")
                success = True
                mod = int(_rng.choice(list(spin))) / 10
                messages.append(
                    f"{actor.name} gains {int(mod * 100)}% to attack.\n"
                )
                wd_str, _, _ = actor.weapon_damage(target, dmg_mod=1 + mod)
                messages.append(wd_str)

            else:
                if _rng.randint(0, user_chance) and retries < 2:
                    if textbox_callback is not None:
                        textbox_callback("No luck, try again.")
                    retries += 1
                else:
                    success = True
                    messages.append("Nothing happens.\n")


class TotemEffect(Effect):
    """Activate a totem magic effect with the selected sacred aspect.

    The active aspect is passed via ``use_kwargs["active_aspect"]``.
    Falls back to ``"Earth"`` if not provided.

    Stores aspect data in ``user.magic_effects["Totem"].extra`` for the
    combat engine to reference (bonuses, secondary effects).

    Parameters (YAML):
        aspects (dict): Aspect definitions keyed by name.
        unlock_requirements (dict): Level requirements per aspect.
        duration_base (int): Base totem duration in turns.
    """

    DEFAULT_ASPECTS = {
        "Earth": {
            "cost": 12,
            "attack_bonus": 0.0,
            "defense_bonus": 0.20,
            "secondary": "reflect",
            "description": "+20% Defense. Reflects 25% of damage back at attackers.",
        },
        "Water": {
            "cost": 14,
            "attack_bonus": 0.0,
            "defense_bonus": 0.0,
            "secondary": "healing",
            "description": "+50% healing effectiveness. Cleanses negative status effects.",
        },
        "Fire": {
            "cost": 16,
            "attack_bonus": 0.25,
            "defense_bonus": 0.0,
            "secondary": "elemental",
            "description": "+25% Attack damage. Adds elemental fire damage to your attacks.",
        },
        "Wind": {
            "cost": 15,
            "attack_bonus": 0.0,
            "defense_bonus": 0.0,
            "secondary": "speed",
            "description": "+15% Dodge chance and +10% Critical strike chance. Enhanced precision and evasion.",
        },
        "Soul": {
            "cost": 18,
            "attack_bonus": 0.20,
            "defense_bonus": 0.0,
            "secondary": "crit_damage",
            "description": "+20% Weapon damage and +20% Critical damage. Embodies the essence of conquered foes.",
        },
    }

    DEFAULT_UNLOCK_REQUIREMENTS = {
        "Earth": 1,
        "Water": 10,
        "Fire": 20,
        "Wind": 30,
        "Soul": 999,
    }

    def __init__(
        self,
        aspects: dict | None = None,
        unlock_requirements: dict | None = None,
        duration_base: int = 5,
        **_kw,
    ):
        super().__init__()
        self.aspects = aspects or dict(self.DEFAULT_ASPECTS)
        self.unlock_requirements = (
            unlock_requirements or dict(self.DEFAULT_UNLOCK_REQUIREMENTS)
        )
        self.duration_base = duration_base

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        messages = result.extra.setdefault("messages", [])
        use_kw = result.extra.get("use_kwargs", {})
        active_aspect = use_kw.get("active_aspect", "Earth")

        if active_aspect not in self.aspects:
            messages.append(f"Unknown aspect: {active_aspect}\n")
            return

        aspect = self.aspects[active_aspect]
        duration = self.duration_base + (actor.stats.wisdom // 10)

        # Activate the Totem magic effect
        actor.magic_effects["Totem"].active = True
        actor.magic_effects["Totem"].duration = duration
        actor.magic_effects["Totem"].extra = {
            "aspect": active_aspect,
            "attack_bonus": aspect["attack_bonus"],
            "defense_bonus": aspect["defense_bonus"],
            "secondary": aspect["secondary"],
        }

        messages.append(
            f"{actor.name} drives a {active_aspect.lower()} totem into "
            f"the ground!\n"
        )
        messages.append(f"{aspect['description']}\n")

        if aspect["attack_bonus"] > 0:
            messages.append(
                f"Attack increased by "
                f"{int(aspect['attack_bonus'] * 100)}%.\n"
            )
        if aspect["defense_bonus"] > 0:
            messages.append(
                f"Defense increased by "
                f"{int(aspect['defense_bonus'] * 100)}%.\n"
            )

        secondary_descriptions = {
            "reflect": "Attacks against you are reflected back at the attacker.\n",
            "healing": "Healing spells and effects are significantly more effective.\n",
            "elemental": "Your attacks burn with primal fire.\n",
            "speed": "Your reflexes and precision are heightened, granting increased dodge and critical strike chance.\n",
            "crit_damage": "The captured essence of fallen foes empowers your weapon with devastating critical strikes.\n",
        }
        desc = secondary_descriptions.get(aspect["secondary"])
        if desc:
            messages.append(desc)

        messages.append(
            f"The totem emanates power for {duration} turns.\n"
        )

        # Emit status event
        try:
            actor._emit_status_event(
                actor, "Totem", applied=True, duration=duration,
                source=f"{active_aspect} Totem",
            )
        except (AttributeError, Exception):
            pass


class ChargeEffect(Effect):
    """
    Charge execute phase: str-vs-con stun check BEFORE weapon damage.

    Stun is blocked by: status immunity, Pendant of Stun/All, tunnel,
    Mana Shield, already stunned.
    """

    def __init__(self, dmg_mod: float = 1.25, stun_duration: int = 1):
        self.dmg_mod = dmg_mod
        self.stun_duration = stun_duration

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random
        messages = result.extra.setdefault("messages", [])
        cover = result.extra.get("cover", False)

        # ── Stun check BEFORE damage ────────────────────────────────
        if not any([
            "Stun" in target.status_immunity,
            "Status-Stun" in target.equipment["Pendant"].mod,
            "Status-All" in target.equipment["Pendant"].mod,
            target.tunnel,
        ]):
            if (
                not target.magic_effects["Mana Shield"].active
                and target.stun_contest_success(
                    actor,
                    random.randint(actor.stats.strength // 2, actor.stats.strength),
                    random.randint(target.stats.con // 2, target.stats.con),
                )
            ):
                if target.apply_stun(self.stun_duration, source="Head Butt", applier=actor):
                    messages.append(f"{actor.name} stunned {target.name}.\n")

        # ── Weapon damage ───────────────────────────────────────────
        wd_str, hit, crit = actor.weapon_damage(
            target, cover=cover, dmg_mod=self.dmg_mod,
        )
        messages.append(wd_str)
        result.hit = hit
        result.crit = crit if crit > 1 else None


class CrushingBlowEffect(Effect):
    """
    Crushing Blow execute phase: weapon damage (3x, crit 2) then
    50 % chance to stun for 2 turns.
    """

    def __init__(
        self,
        dmg_mod: float = 3.0,
        crit_override: int = 2,
        stun_chance: float = 0.5,
        stun_duration: int = 2,
    ):
        self.dmg_mod = dmg_mod
        self.crit_override = crit_override
        self.stun_chance = stun_chance
        self.stun_duration = stun_duration

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random
        messages = result.extra.setdefault("messages", [])
        cover = result.extra.get("cover", False)

        # ── Weapon damage ───────────────────────────────────────────
        wd_str, hit, crit = actor.weapon_damage(
            target, cover=cover, dmg_mod=self.dmg_mod, crit=self.crit_override,
        )
        messages.append(wd_str)
        result.hit = hit
        result.crit = crit if crit > 1 else None

        # ── Post-hit stun check ─────────────────────────────────────
        if hit and target.is_alive():
            if not any([
                "Stun" in target.status_immunity,
                "Status-Stun" in target.equipment["Pendant"].mod,
                "Status-All" in target.equipment["Pendant"].mod,
            ]):
                if (
                    random.random() < self.stun_chance
                ):
                    if target.apply_stun(self.stun_duration, source="Crushing Blow", applier=actor):
                        messages.append(f"{target.name} is stunned!\n")


class ArcaneBlastEffect(Effect):
    """
    Arcane Blast execute phase: use all mana as magic damage via
    handle_defenses / damage_reduction, drain to 0, then queue
    Power Up for mana regen over N turns if the target survives.
    """

    def __init__(self, regen_turns: int = 4, regen_fraction: float = 0.1):
        self.regen_turns = regen_turns
        self.regen_fraction = regen_fraction

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random
        from src.core.constants import DAMAGE_VARIANCE_HIGH, DAMAGE_VARIANCE_LOW

        messages = result.extra.setdefault("messages", [])
        cover = result.extra.get("cover", False)
        charge_ctx = result.extra.get("charge_context", {})

        mana_spent = charge_ctx.get("mana", actor.mana.current)

        hit, message, damage = target.handle_defenses(
            actor, mana_spent, cover, typ="Magic",
        )
        messages.append(message)
        hit, message, damage = target.damage_reduction(
            damage, actor, typ="Arcane",
        )
        messages.append(message)
        actor.mana.current = 0

        if hit:
            variance = random.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
            damage = int(damage * variance)
            if damage > 0:
                target.health.current -= damage
                messages.append(
                    f"{actor.name} blasts {target.name} for {damage} damage, "
                    f"draining all remaining mana.\n"
                )
            result.hit = True
            result.damage = damage

        # Power Up for mana regen if target survived
        if target.is_alive():
            if hasattr(actor, "class_effects") and "Power Up" in actor.class_effects:
                actor.power_up = True
                actor.class_effects["Power Up"].active = True
                actor.class_effects["Power Up"].duration = self.regen_turns
                actor.class_effects["Power Up"].extra = max(
                    1, int(actor.mana.max * self.regen_fraction),
                )


class JumpEffect(Effect):
    """
    Jump execute phase: weapon damage with modification-dependent
    dmg_mod/crit, then apply active modification combat effects
    (Quake, Rend, Dragon's Fury, Skyfall, Thrust, Recover).

    Reads modification state from ``result.extra["modifications"]``.
    Reads retribution bonus from ``result.extra["retribution_damage"]``.
    """

    def __init__(self, base_dmg_mod: float = 2.0):
        self.base_dmg_mod = base_dmg_mod

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random
        messages = result.extra.setdefault("messages", [])
        cover = result.extra.get("cover", False)
        mods = result.extra.get("modifications", {})
        retribution_damage = result.extra.get("retribution_damage", 0)

        # ── Calculate dmg_mod / crit from active modifications ──────
        dmg_mod = self.base_dmg_mod
        crit = 1

        if mods.get("Crit"):
            dmg_mod = 1.5
            crit = 2

        if mods.get("Quick Dive"):
            dmg_mod = 1.25

        # Soaring Strike overrides Crit
        if mods.get("Soaring Strike"):
            dmg_mod = 3.0
            crit = 3

        # Retribution bonus
        if mods.get("Retribution") and retribution_damage > 0:
            dmg_mod += retribution_damage / 100
            messages.append(
                f"{actor.name}'s fury from taking damage empowers the strike!\n"
            )

        messages.append(
            f"{actor.name} descends from the air, weapon aimed at "
            f"{target.name}!\n"
        )

        # ── Main weapon damage ──────────────────────────────────────
        wd_str, hit, actual_crit = actor.weapon_damage(
            target, cover=cover, dmg_mod=dmg_mod, crit=crit,
        )
        messages.append(wd_str)
        result.hit = hit
        result.crit = actual_crit if actual_crit > 1 else None

        if hit and target.is_alive():
            # ── Quake (stun chance) ─────────────────────────────────
            if mods.get("Quake"):
                self._apply_quake(actor, target, messages)

            # ── Rend (bleed) ────────────────────────────────────────
            if mods.get("Rend"):
                self._apply_rend(actor, target, messages)

            # ── Dragon's Fury (elemental damage) ────────────────────
            if mods.get("Dragon's Fury"):
                self._apply_dragons_fury(actor, target, messages)

            # ── Skyfall (multi-hit debris) ──────────────────────────
            if mods.get("Skyfall"):
                self._apply_skyfall(actor, target, messages)

            # ── Thrust (follow-up weapon hit) ───────────────────────
            if mods.get("Thrust") and target.is_alive():
                self._apply_thrust(actor, target, cover, messages)

        # ── Recover (heal on landing, regardless of hit) ────────────
        if mods.get("Recover"):
            self._apply_recover(actor, messages)

    # ------------------------------------------------------------------
    # Modification sub-effects
    # ------------------------------------------------------------------
    @staticmethod
    def _apply_quake(actor: Character, target: Character, messages: list[str]) -> None:
        import random
        if any([
            "Stun" in target.status_immunity,
            "Status-Stun" in target.equipment["Pendant"].mod,
            "Status-All" in target.equipment["Pendant"].mod,
        ]):
            return
        att_roll = random.randint(actor.stats.strength // 2, actor.stats.strength)
        def_roll = random.randint(target.stats.con // 2, target.stats.con)
        if target.stun_contest_success(actor, att_roll, def_roll):
            if target.apply_stun(1, source="Jump (Quake)", applier=actor):
                messages.append(f"The impact stuns {target.name}!\n")

    @staticmethod
    def _apply_rend(actor: Character, target: Character, messages: list[str]) -> None:
        import random
        if target.physical_effects["Bleed"].active:
            return
        if random.randint(0, 100) < 40:  # 40% chance
            bleed_dmg = int(actor.stats.strength * 1.0)
            target.physical_effects["Bleed"].active = True
            target.physical_effects["Bleed"].duration = 2
            target.physical_effects["Bleed"].extra = bleed_dmg
            try:
                actor._emit_status_event(
                    target, "Bleed", applied=True, duration=2,
                    source="Jump (Rend)",
                )
            except (AttributeError, Exception):
                pass
            messages.append(
                f"{target.name} is bleeding from the vicious strike!\n"
            )

    @staticmethod
    def _apply_dragons_fury(actor: Character, target: Character, messages: list[str]) -> None:
        import random
        elements = ["Fire", "Ice", "Lightning"]
        element = random.choice(elements)
        elem_damage = int(actor.stats.intel * random.uniform(0.5, 1.0))
        elem_damage = max(1, elem_damage)

        resistance = target.check_mod(
            mod="resist", typ=f"{element}", enemy=actor,
        )
        elem_damage = max(1, elem_damage - resistance)

        target.health.current -= elem_damage
        messages.append(
            f"Draconic {element.lower()} energy erupts for "
            f"{elem_damage} damage!\n"
        )

    @staticmethod
    def _apply_skyfall(actor: Character, target: Character, messages: list[str]) -> None:
        import random
        num_hits = random.randint(2, 4)
        messages.append(f"Debris rains down on {target.name}!\n")
        for i in range(num_hits):
            if target.is_alive():
                sky_dmg = int(
                    actor.stats.strength * random.uniform(0.2, 0.4)
                )
                sky_dmg = max(1, sky_dmg)
                target.health.current -= sky_dmg
                messages.append(f"  Impact {i + 1}: {sky_dmg} damage!\n")

    @staticmethod
    def _apply_thrust(actor: Character, target: Character, cover: bool, messages: list[str]) -> None:
        messages.append(f"{actor.name} thrusts their weapon forward!\n")
        thrust_str, _, _ = actor.weapon_damage(
            target, cover=cover, dmg_mod=0.75,
        )
        messages.append(thrust_str)

    @staticmethod
    def _apply_recover(actor: Character, messages: list[str]) -> None:
        hp_recover = int(actor.health.max * 0.05)
        mp_recover = int(actor.mana.max * 0.05)
        actor.health.current = min(
            actor.health.max, actor.health.current + hp_recover,
        )
        actor.mana.current = min(
            actor.mana.max, actor.mana.current + mp_recover,
        )
        messages.append(
            f"{actor.name} recovers {hp_recover} HP and "
            f"{mp_recover} MP!\n"
        )


class ShadowStrikeEffect(Effect):
    """
    Shadow Strike execute phase: guaranteed-critical weapon damage
    followed by a chance to blind the target.

    Blind is blocked by: status immunity, Pendant of Blind/All,
    Mana Shield, already blinded.
    """

    def __init__(
        self,
        dmg_mod: float = 2.0,
        blind_chance: float = 0.6,
        blind_duration: int = 2,
    ):
        self.dmg_mod = dmg_mod
        self.blind_chance = blind_chance
        self.blind_duration = blind_duration

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random
        messages = result.extra.setdefault("messages", [])
        cover = result.extra.get("cover", False)

        # ── Guaranteed-crit weapon damage ───────────────────────────
        messages.append(
            f"{actor.name} strikes from the shadows!\n"
        )
        wd_str, hit, crit = actor.weapon_damage(
            target, cover=cover, dmg_mod=self.dmg_mod, crit=2,
        )
        messages.append(wd_str)
        result.hit = hit
        result.crit = crit if crit > 1 else None

        # ── Post-hit blind check ────────────────────────────────────
        if hit and target.is_alive():
            if not any([
                "Blind" in target.status_immunity,
                "Status-Blind" in target.equipment["Pendant"].mod,
                "Status-All" in target.equipment["Pendant"].mod,
            ]):
                if (
                    random.random() < self.blind_chance
                    and not target.status_effects["Blind"].active
                    and not target.magic_effects["Mana Shield"].active
                ):
                    target.status_effects["Blind"].active = True
                    target.status_effects["Blind"].duration = (
                        self.blind_duration
                    )
                    try:
                        actor._emit_status_event(
                            target, "Blind", applied=True,
                            duration=self.blind_duration,
                            source="Shadow Strike",
                        )
                    except (AttributeError, Exception):
                        pass
                    messages.append(
                        f"{target.name} is blinded by the attack!\n"
                    )


# ======================================================================
# Companion Ultimate Effects — 11 summon capstone abilities (level 10)
# ======================================================================


class TitanicSlamEffect(Effect):
    """
    Patagon ultimate: massive weapon strike (4x) + guaranteed stun 2 turns.

    Bypasses stun immunity checks — the sheer force overwhelms all defenses
    except Mana Shield (which absorbs the stun but not the damage).
    """

    def __init__(
        self,
        dmg_mod: float = 4.0,
        crit_override: int = 2,
        stun_duration: int = 2,
    ):
        self.dmg_mod = dmg_mod
        self.crit_override = crit_override
        self.stun_duration = stun_duration

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random
        messages = result.extra.setdefault("messages", [])
        cover = result.extra.get("cover", False)

        messages.append(
            f"{actor.name} raises both fists and brings them crashing "
            f"down on {target.name}!\n"
        )

        # ── Weapon damage ───────────────────────────────────────────
        wd_str, hit, crit = actor.weapon_damage(
            target, cover=cover, dmg_mod=self.dmg_mod,
            crit=self.crit_override,
        )
        messages.append(wd_str)
        result.hit = hit
        result.crit = crit if crit > 1 else None

        # ── Post-hit guaranteed stun ────────────────────────────────
        if hit and target.is_alive():
            if not target.magic_effects["Mana Shield"].active:
                if target.apply_stun(self.stun_duration, source="Titanic Slam", applier=actor):
                    messages.append(
                        f"The earth-shattering blow stuns {target.name} "
                        f"for {self.stun_duration} turns!\n"
                    )
            else:
                messages.append(
                    f"The mana shield absorbs the stunning force.\n"
                )


class DevourEffect(Effect):
    """
    Dilong ultimate: swallow the target, dealing % max HP damage over
    multiple bites plus a final spit-out with bonus damage.

    Mechanics: 3 hits at (str + con) * multiplier each, applied through
    Earth resistance. Ignores dodge/cover — the target is inside the worm.
    """

    def __init__(
        self,
        num_bites: int = 3,
        multiplier: float = 1.5,
        element: str = "Earth",
    ):
        self.num_bites = num_bites
        self.multiplier = multiplier
        self.element = element

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random
        from src.core.constants import DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH

        messages = result.extra.setdefault("messages", [])
        messages.append(
            f"{actor.name} lunges forward and swallows "
            f"{target.name} whole!\n"
        )

        total_damage = 0
        for i in range(self.num_bites):
            base = int(
                (actor.stats.strength + actor.stats.con) * self.multiplier
            )
            variance = random.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
            damage = int(base * variance)

            _, red_msg, damage = target.damage_reduction(
                damage, actor, typ=self.element,
            )
            if red_msg:
                messages.append(red_msg)

            if damage > 0:
                target.health.current -= damage
                total_damage += damage
                if i < self.num_bites - 1:
                    messages.append(
                        f"{actor.name} crushes {target.name} for "
                        f"{damage} damage!\n"
                    )

            if not target.is_alive():
                messages.append(
                    f"{actor.name} devours {target.name} completely!\n"
                )
                break

        if target.is_alive():
            messages.append(
                f"{actor.name} spits out {target.name}, dealing "
                f"{total_damage} total damage!\n"
            )

        result.damage = total_damage
        result.hit = total_damage > 0


class AbsoluteZeroEffect(Effect):
    """
    Agloolik ultimate: heavy ice damage (3x) + freeze (Stun 3 turns)
    + permanent defense reduction.
    """

    def __init__(
        self,
        damage_mod: float = 3.0,
        stun_duration: int = 3,
        def_reduction: int = 5,
    ):
        self.damage_mod = damage_mod
        self.stun_duration = stun_duration
        self.def_reduction = def_reduction

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random
        from src.core.constants import DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH

        messages = result.extra.setdefault("messages", [])
        messages.append(
            f"{actor.name} channels the essence of absolute cold!\n"
        )

        # ── Ice damage ──────────────────────────────────────────────
        base = int(actor.stats.intel * self.damage_mod)
        variance = random.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
        damage = int(base * variance)

        hit, def_msg, damage = target.handle_defenses(
            actor, damage, typ="Magic",
        )
        if def_msg:
            messages.append(def_msg)

        _, red_msg, damage = target.damage_reduction(
            damage, actor, typ="Ice",
        )
        if red_msg:
            messages.append(red_msg)

        if hit and damage > 0:
            target.health.current -= damage
            result.damage = damage
            result.hit = True
            messages.append(
                f"{target.name} takes {damage} ice damage as the "
                f"temperature plummets!\n"
            )
        else:
            messages.append(
                f"The freezing blast has no effect on {target.name}.\n"
            )
            return

        if not target.is_alive():
            return

        # ── Freeze (stun) ──────────────────────────────────────────
        if not target.magic_effects["Mana Shield"].active:
            if target.apply_stun(self.stun_duration, source="Absolute Zero", applier=actor):
                messages.append(
                    f"{target.name} is frozen solid for "
                    f"{self.stun_duration} turns!\n"
                )

        # ── Defense shatter ─────────────────────────────────────────
        if target.combat.defense > self.def_reduction:
            target.combat.defense -= self.def_reduction
            messages.append(
                f"{target.name}'s defense is permanently shattered "
                f"by {self.def_reduction}!\n"
            )


class EruptionEffect(Effect):
    """
    Cacus ultimate: massive fire damage (3.5x) + Burn DOT
    + self Vulcanize buff (defense +25% for 3 turns).
    """

    def __init__(
        self,
        damage_mod: float = 3.5,
        burn_duration: int = 3,
        vulcanize_duration: int = 3,
    ):
        self.damage_mod = damage_mod
        self.burn_duration = burn_duration
        self.vulcanize_duration = vulcanize_duration

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random
        from src.core.constants import DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH

        messages = result.extra.setdefault("messages", [])
        messages.append(
            f"{actor.name} erupts in a cataclysmic blaze of fire!\n"
        )

        # ── Fire damage ─────────────────────────────────────────────
        base = int(
            (actor.stats.strength + actor.stats.intel) * self.damage_mod
        )
        variance = random.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
        damage = int(base * variance)

        hit, def_msg, damage = target.handle_defenses(
            actor, damage, typ="Magic",
        )
        if def_msg:
            messages.append(def_msg)

        _, red_msg, damage = target.damage_reduction(
            damage, actor, typ="Fire",
        )
        if red_msg:
            messages.append(red_msg)

        if hit and damage > 0:
            target.health.current -= damage
            result.damage = damage
            result.hit = True
            messages.append(
                f"{target.name} is engulfed in flames for {damage} damage!\n"
            )
        else:
            messages.append(
                f"The eruption has no effect on {target.name}.\n"
            )
            return

        if not target.is_alive():
            return

        # ── Burn DOT ────────────────────────────────────────────────
        if (
            "DOT" not in target.status_immunity
            and not target.magic_effects["DOT"].active
        ):
            target.magic_effects["DOT"].active = True
            target.magic_effects["DOT"].duration = self.burn_duration
            target.magic_effects["DOT"].extra = max(
                1, actor.stats.intel // 4,
            )
            messages.append(
                f"{target.name} is set ablaze!\n"
            )

        # ── Self Vulcanize buff ─────────────────────────────────────
        if hasattr(actor, "stat_effects") and "Defense" in actor.stat_effects:
            actor.stat_effects["Defense"].active = True
            actor.stat_effects["Defense"].duration = self.vulcanize_duration
            actor.stat_effects["Defense"].extra = max(
                1, actor.combat.defense // 4,
            )
            messages.append(
                f"{actor.name}'s skin hardens into volcanic rock!\n"
            )


class MaelstromVortexEffect(Effect):
    """
    Fuath ultimate: heavy water damage (3x) + apply Blind, Silence,
    and Terrify — the maddening vortex overwhelms the senses.
    """

    def __init__(
        self,
        damage_mod: float = 3.0,
        status_duration: int = 3,
    ):
        self.damage_mod = damage_mod
        self.status_duration = status_duration

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random
        from src.core.constants import DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH

        messages = result.extra.setdefault("messages", [])
        messages.append(
            f"{actor.name} summons a maddening vortex of swirling water!\n"
        )

        # ── Water damage ────────────────────────────────────────────
        base = int(actor.stats.intel * self.damage_mod)
        variance = random.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
        damage = int(base * variance)

        hit, def_msg, damage = target.handle_defenses(
            actor, damage, typ="Magic",
        )
        if def_msg:
            messages.append(def_msg)

        _, red_msg, damage = target.damage_reduction(
            damage, actor, typ="Water",
        )
        if red_msg:
            messages.append(red_msg)

        if hit and damage > 0:
            target.health.current -= damage
            result.damage = damage
            result.hit = True
            messages.append(
                f"{target.name} is torn apart by the vortex for "
                f"{damage} damage!\n"
            )
        else:
            messages.append(
                f"The vortex has no effect on {target.name}.\n"
            )
            return

        if not target.is_alive():
            return

        # ── Apply triple debuff ─────────────────────────────────────
        for status_name, msg in [
            ("Blind", f"{target.name} is blinded by the churning waters!\n"),
            ("Silence", f"{target.name} is silenced by the roaring waves!\n"),
        ]:
            if (
                status_name not in target.status_immunity
                and f"Status-{status_name}" not in target.equipment["Pendant"].mod
                and "Status-All" not in target.equipment["Pendant"].mod
                and not target.status_effects[status_name].active
                and not target.magic_effects["Mana Shield"].active
            ):
                target.status_effects[status_name].active = True
                target.status_effects[status_name].duration = self.status_duration
                try:
                    actor._emit_status_event(
                        target, status_name, applied=True,
                        duration=self.status_duration,
                        source="Maelstrom Vortex",
                    )
                except (AttributeError, Exception):
                    pass
                messages.append(msg)

        # Terrify uses magic_effects
        if (
            not target.magic_effects.get("Terrify") is None
            and not target.magic_effects["Terrify"].active
        ):
            target.magic_effects["Terrify"].active = True
            target.magic_effects["Terrify"].duration = self.status_duration
            messages.append(
                f"{target.name} is terrified by the maelstrom!\n"
            )


class ThunderstrikeEffect(Effect):
    """
    Izulu ultimate: lightning damage (3x) + 2 chain hits at 50% damage
    + stun.  The lightning bird's devastating electrical assault.
    """

    def __init__(
        self,
        damage_mod: float = 3.0,
        chain_hits: int = 2,
        chain_multiplier: float = 0.5,
        stun_duration: int = 2,
    ):
        self.damage_mod = damage_mod
        self.chain_hits = chain_hits
        self.chain_multiplier = chain_multiplier
        self.stun_duration = stun_duration

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random
        from src.core.constants import DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH

        messages = result.extra.setdefault("messages", [])
        messages.append(
            f"{actor.name} screeches and calls down a devastating "
            f"bolt of lightning!\n"
        )

        total_damage = 0

        # ── Primary strike ──────────────────────────────────────────
        base = int(actor.stats.intel * self.damage_mod)
        variance = random.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
        damage = int(base * variance)

        hit, def_msg, damage = target.handle_defenses(
            actor, damage, typ="Magic",
        )
        if def_msg:
            messages.append(def_msg)

        _, red_msg, damage = target.damage_reduction(
            damage, actor, typ="Electric",
        )
        if red_msg:
            messages.append(red_msg)

        if hit and damage > 0:
            target.health.current -= damage
            total_damage += damage
            messages.append(
                f"The lightning strikes {target.name} for {damage} damage!\n"
            )
        else:
            messages.append(
                f"The lightning has no effect on {target.name}.\n"
            )
            result.damage = 0
            return

        # ── Chain hits ──────────────────────────────────────────────
        for i in range(self.chain_hits):
            if not target.is_alive():
                break
            chain_base = int(base * self.chain_multiplier)
            variance = random.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
            chain_dmg = int(chain_base * variance)

            _, red_msg, chain_dmg = target.damage_reduction(
                chain_dmg, actor, typ="Electric",
            )
            if red_msg:
                messages.append(red_msg)

            if chain_dmg > 0:
                target.health.current -= chain_dmg
                total_damage += chain_dmg
                messages.append(
                    f"The lightning chains through {target.name} for "
                    f"{chain_dmg} damage!\n"
                )

        result.damage = total_damage
        result.hit = total_damage > 0

        # ── Stun ────────────────────────────────────────────────────
        if target.is_alive() and total_damage > 0:
            if (
                "Stun" not in target.status_immunity
                and "Status-Stun" not in target.equipment["Pendant"].mod
                and "Status-All" not in target.equipment["Pendant"].mod
                and not target.magic_effects["Mana Shield"].active
            ):
                if target.apply_stun(self.stun_duration, source="Thunderstrike", applier=actor):
                    messages.append(
                        f"{target.name} is paralyzed by the electrical "
                        f"surge!\n"
                    )


class WindShrapnelEffect(Effect):
    """
    Hala ultimate: 5 wind-element hits, each with independent crit
    chance.  A storm of razor-sharp wind fragments.
    """

    def __init__(
        self,
        num_hits: int = 5,
        damage_mod: float = 1.2,
        crit_chance: float = 0.25,
        crit_multiplier: float = 2.0,
    ):
        self.num_hits = num_hits
        self.damage_mod = damage_mod
        self.crit_chance = crit_chance
        self.crit_multiplier = crit_multiplier

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random
        from src.core.constants import DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH

        messages = result.extra.setdefault("messages", [])
        messages.append(
            f"{actor.name} conjures a storm of razor-sharp wind blades!\n"
        )

        total_damage = 0
        total_crits = 0

        for i in range(self.num_hits):
            if not target.is_alive():
                break

            is_crit = random.random() < self.crit_chance
            crit_mod = self.crit_multiplier if is_crit else 1.0

            base = int(actor.stats.intel * self.damage_mod * crit_mod)
            variance = random.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
            damage = int(base * variance)

            _, red_msg, damage = target.damage_reduction(
                damage, actor, typ="Wind",
            )
            if red_msg:
                messages.append(red_msg)

            if damage > 0:
                target.health.current -= damage
                total_damage += damage
                if is_crit:
                    total_crits += 1
                crit_str = " (Critical!)" if is_crit else ""
                messages.append(
                    f"Wind blade hits {target.name} for "
                    f"{damage} damage!{crit_str}\n"
                )

        if total_damage > 0:
            messages.append(
                f"Total: {total_damage} damage across {self.num_hits} "
                f"hits ({total_crits} critical).\n"
            )

        result.damage = total_damage
        result.hit = total_damage > 0


class DivineJudgmentEffect(Effect):
    """
    Grigori ultimate: holy damage (3x, double vs undead) + heal the
    summoner + cleanse all status effects on the summoner.

    The angelic Watcher passes divine judgment on the enemy.
    """

    def __init__(
        self,
        damage_mod: float = 3.0,
        undead_multiplier: float = 2.0,
        heal_fraction: float = 0.5,
    ):
        self.damage_mod = damage_mod
        self.undead_multiplier = undead_multiplier
        self.heal_fraction = heal_fraction

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random
        from src.core.constants import DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH

        messages = result.extra.setdefault("messages", [])
        messages.append(
            f"{actor.name} raises a holy sword and passes "
            f"divine judgment!\n"
        )

        # ── Holy damage ─────────────────────────────────────────────
        mod = self.damage_mod
        is_undead = getattr(target, "enemy_typ", "") == "Undead"
        if is_undead:
            mod *= self.undead_multiplier
            messages.append(
                f"The holy light burns with terrible fury "
                f"against the undead!\n"
            )

        base = int(actor.stats.wisdom * mod)
        variance = random.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
        damage = int(base * variance)

        hit, def_msg, damage = target.handle_defenses(
            actor, damage, typ="Magic",
        )
        if def_msg:
            messages.append(def_msg)

        _, red_msg, damage = target.damage_reduction(
            damage, actor, typ="Holy",
        )
        if red_msg:
            messages.append(red_msg)

        if hit and damage > 0:
            target.health.current -= damage
            result.damage = damage
            result.hit = True
            messages.append(
                f"Divine light strikes {target.name} for "
                f"{damage} damage!\n"
            )
        else:
            messages.append(
                f"The divine judgment has no effect on {target.name}.\n"
            )

        # ── Heal the summoner (actor's owner) ───────────────────────
        # Summons are the actor; try to heal via owner reference,
        # otherwise heal self as fallback.
        healer = getattr(actor, "owner", actor)
        heal_amount = int(healer.health.max * self.heal_fraction)
        actual_heal = min(heal_amount, healer.health.max - healer.health.current)
        if actual_heal > 0:
            healer.health.current += actual_heal
            messages.append(
                f"Holy light restores {actual_heal} HP to "
                f"{healer.name}!\n"
            )

        # ── Cleanse status effects on the summoner ──────────────────
        cleansed = []
        for status_name, status in healer.status_effects.items():
            if status.active and status_name not in ("Regen",):
                status.active = False
                status.duration = 0
                cleansed.append(status_name)
        if cleansed:
            messages.append(
                f"{healer.name} is cleansed of "
                f"{', '.join(cleansed)}!\n"
            )


class OblivionEffect(Effect):
    """
    Bardi ultimate: massive shadow damage (4x) + % instant kill chance
    + permanent stat drain on survivor.  The bringer of death and darkness
    unleashes oblivion.
    """

    def __init__(
        self,
        damage_mod: float = 4.0,
        kill_chance: float = 0.2,
        stat_drain: int = 3,
    ):
        self.damage_mod = damage_mod
        self.kill_chance = kill_chance
        self.stat_drain = stat_drain

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random
        from src.core.constants import DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH

        messages = result.extra.setdefault("messages", [])
        messages.append(
            f"{actor.name} tears open a rift to the void, "
            f"unleashing pure oblivion!\n"
        )

        # ── Shadow damage ───────────────────────────────────────────
        base = int(actor.stats.intel * self.damage_mod)
        variance = random.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
        damage = int(base * variance)

        hit, def_msg, damage = target.handle_defenses(
            actor, damage, typ="Magic",
        )
        if def_msg:
            messages.append(def_msg)

        _, red_msg, damage = target.damage_reduction(
            damage, actor, typ="Shadow",
        )
        if red_msg:
            messages.append(red_msg)

        if hit and damage > 0:
            target.health.current -= damage
            result.damage = damage
            result.hit = True
            messages.append(
                f"The void consumes {target.name} for {damage} damage!\n"
            )
        else:
            messages.append(
                f"The void has no hold on {target.name}.\n"
            )
            return

        if not target.is_alive():
            return

        # ── Instant kill chance ─────────────────────────────────────
        if (
            "Death" not in target.status_immunity
            and random.random() < self.kill_chance
        ):
            resist = target.check_mod("resist", enemy=actor, typ="Death")
            if resist < 1:
                target.health.current = 0
                messages.append(
                    f"{target.name} is consumed by oblivion!\n"
                )
                return

        # ── Permanent stat drain ────────────────────────────────────
        stats_to_drain = ["strength", "intel", "wisdom", "con"]
        drained = []
        for stat in stats_to_drain:
            current = getattr(target.stats, stat, 0)
            if current > self.stat_drain:
                setattr(target.stats, stat, current - self.stat_drain)
                drained.append(stat)
        if drained:
            messages.append(
                f"The lingering void drains {target.name}'s "
                f"{', '.join(drained)} by {self.stat_drain}!\n"
            )


class GrandHeistEffect(Effect):
    """
    Kobalos ultimate: steal gold + steal item + random powerful debuff
    + Gold Toss finisher.  The ultimate trickster heist.
    """

    def __init__(
        self,
        gold_multiplier: float = 2.0,
        debuff_duration: int = 3,
    ):
        self.gold_multiplier = gold_multiplier
        self.debuff_duration = debuff_duration

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random

        messages = result.extra.setdefault("messages", [])
        messages.append(
            f"{actor.name} cackles and launches into the heist "
            f"of a lifetime!\n"
        )

        total_damage = 0

        # ── Steal gold ──────────────────────────────────────────────
        gold = getattr(target, "gold", 0)
        stolen_gold = int(gold * 0.3) if gold > 0 else 0
        if stolen_gold > 0:
            target.gold -= stolen_gold
            if hasattr(actor, "owner"):
                actor.owner.gold += stolen_gold
            else:
                actor.gold += stolen_gold
            messages.append(
                f"{actor.name} steals {stolen_gold} gold from "
                f"{target.name}!\n"
            )

        # ── Random debuff ───────────────────────────────────────────
        possible_debuffs = ["Blind", "Silence", "Poison"]
        debuff = random.choice(possible_debuffs)
        if (
            debuff not in target.status_immunity
            and f"Status-{debuff}" not in target.equipment["Pendant"].mod
            and "Status-All" not in target.equipment["Pendant"].mod
            and not target.status_effects[debuff].active
            and not target.magic_effects["Mana Shield"].active
        ):
            target.status_effects[debuff].active = True
            target.status_effects[debuff].duration = self.debuff_duration
            if debuff == "Poison":
                target.status_effects[debuff].extra = max(
                    1, actor.stats.dex // 4,
                )
            try:
                actor._emit_status_event(
                    target, debuff, applied=True,
                    duration=self.debuff_duration,
                    source="Grand Heist",
                )
            except (AttributeError, Exception):
                pass
            messages.append(
                f"{actor.name} inflicts {debuff} on {target.name}!\n"
            )

        # ── Gold Toss finisher ──────────────────────────────────────
        recipient = getattr(actor, "owner", actor)
        toss_gold = getattr(recipient, "gold", 0)
        if toss_gold > 0:
            gold_dmg = int(
                random.randint(1, max(1, int(toss_gold ** 0.5)))
                * self.gold_multiplier
            )
            _, red_msg, gold_dmg = target.damage_reduction(
                gold_dmg, actor, typ="Physical",
            )
            if red_msg:
                messages.append(red_msg)
            if gold_dmg > 0:
                target.health.current -= gold_dmg
                total_damage += gold_dmg
                messages.append(
                    f"{actor.name} hurls a shower of gold coins at "
                    f"{target.name} for {gold_dmg} damage!\n"
                )

        result.damage = total_damage
        result.hit = True


class CataclysmEffect(Effect):
    """
    Zahhak ultimate: cast 3 random high-tier spells from spellbook
    + Dragon Breath + Power Up self.  The dragon of apocalypse
    unleashes everything at once.
    """

    def __init__(
        self,
        spell_count: int = 3,
        breath_multiplier: float = 2.0,
        power_up_duration: int = 3,
    ):
        self.spell_count = spell_count
        self.breath_multiplier = breath_multiplier
        self.power_up_duration = power_up_duration

    def apply(self, actor: Character, target: Character, result: CombatResult) -> None:
        import random
        from src.core.constants import DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH

        messages = result.extra.setdefault("messages", [])
        messages.append(
            f"{actor.name} roars and unleashes total cataclysm!\n"
        )

        total_damage = 0

        # ── Cast spells from spellbook ──────────────────────────────
        spells = list(actor.spellbook.get("Spells", {}).items())
        if spells:
            chosen = random.sample(
                spells, min(self.spell_count, len(spells)),
            )
            for spell_name, spell in chosen:
                try:
                    cast_result = spell.cast(actor, target, special=True)
                    cast_msg = (
                        cast_result if isinstance(cast_result, str)
                        else str(cast_result)
                    )
                    messages.append(cast_msg)
                except Exception:
                    messages.append(
                        f"{actor.name} attempts {spell_name} "
                        f"but it fizzles.\n"
                    )

        # ── Dragon Breath ───────────────────────────────────────────
        base = int(
            (actor.stats.strength + actor.stats.intel)
            * self.breath_multiplier
        )
        variance = random.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
        breath_dmg = int(base * variance)

        _, red_msg, breath_dmg = target.damage_reduction(
            breath_dmg, actor, typ="Fire",
        )
        if red_msg:
            messages.append(red_msg)

        if breath_dmg > 0 and target.is_alive():
            target.health.current -= breath_dmg
            total_damage += breath_dmg
            messages.append(
                f"{actor.name} unleashes a devastating breath of fire "
                f"for {breath_dmg} damage!\n"
            )

        # ── Power Up self ───────────────────────────────────────────
        if (
            hasattr(actor, "stat_effects")
            and "Attack" in actor.stat_effects
        ):
            actor.stat_effects["Attack"].active = True
            actor.stat_effects["Attack"].duration = self.power_up_duration
            actor.stat_effects["Attack"].extra = max(
                1, actor.combat.attack // 4,
            )
            messages.append(
                f"{actor.name} surges with draconic power!\n"
            )

        result.damage = total_damage
        result.hit = True
