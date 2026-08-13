"""Foundational and composed effect constructors."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.effects import (
    DamageEffect,
    HealEffect,
    RegenEffect,
    StatusEffect,
    AttackBuffEffect,
    AttackDebuffEffect,
    DefenseBuffEffect,
    DefenseDebuffEffect,
    MagicBuffEffect,
    MagicDebuffEffect,
    SpeedBuffEffect,
    SpeedDebuffEffect,
    MultiStatBuffEffect,
    ResistanceEffect,
    DamageOverTimeEffect,
    CompositeEffect,
    ChanceEffect,
    StatContestEffect,
    DynamicDotEffect,
    LifestealEffect,
    ReflectDamageEffect,
    DispelEffect,
    ShieldEffect,
)

if TYPE_CHECKING:
    from effect_base import Effect


class BaseEffectFactoryMixin:
    @staticmethod
    def _create_damage(data: dict) -> DamageEffect:
        """Create a damage effect."""
        base = data.get('base', 0)
        scaling = data.get('scaling', {})
        scaling_ratio = scaling.get('ratio', 0.0) if scaling else 0.0

        return DamageEffect(
            base_damage=base,
            scaling=scaling_ratio
        )

    @staticmethod
    def _create_heal(data: dict) -> HealEffect:
        """Create a healing effect."""
        base = data.get('base', 0)
        scaling = data.get('scaling', {})
        scaling_ratio = scaling.get('ratio', 0.0) if scaling else 0.0

        return HealEffect(
            base_healing=base,
            scaling=scaling_ratio
        )

    @staticmethod
    def _create_status(data: dict) -> StatusEffect:
        """Create a status effect."""
        name = data.get('name', 'Unknown')
        duration = data.get('duration', 1)

        return StatusEffect(name=name, duration=duration)

    @staticmethod
    def _create_regen(data: dict) -> RegenEffect:
        """Create a regen-over-time effect."""
        base = data.get('base', 0)
        duration = data.get('duration', 3)
        scaling = data.get('scaling', {})
        scaling_ratio = scaling.get('ratio', 0.0) if scaling else 0.0
        return RegenEffect(base_healing=base, duration=duration, scaling=scaling_ratio)

    @staticmethod
    def _create_buff(data: dict) -> Effect:
        """Create a buff effect."""
        stat = data.get('stat', 'attack').lower()
        amount = data.get('amount', 0)
        duration = data.get('duration', 3)

        _buff_map = {
            'attack': AttackBuffEffect,
            'defense': DefenseBuffEffect,
            'magic': MagicBuffEffect,
            'speed': SpeedBuffEffect,
        }
        cls = _buff_map.get(stat)
        if cls is None:
            raise ValueError(f"Unknown buff stat: {stat}")
        return cls(amount, duration)

    @staticmethod
    def _create_debuff(data: dict) -> Effect:
        """Create a debuff effect."""
        stat = data.get('stat', 'attack').lower()
        amount = data.get('amount', 0)
        duration = data.get('duration', 3)

        _debuff_map = {
            'attack': AttackDebuffEffect,
            'defense': DefenseDebuffEffect,
            'magic': MagicDebuffEffect,
            'speed': SpeedDebuffEffect,
        }
        cls = _debuff_map.get(stat)
        if cls is None:
            raise ValueError(f"Unknown debuff stat: {stat}")
        return cls(amount, duration)

    @staticmethod
    def _create_lifesteal(data: dict) -> LifestealEffect:
        """Create a lifesteal effect."""
        percent = data.get('percent', 0.25)
        return LifestealEffect(lifesteal_percent=percent)

    @staticmethod
    def _create_reflect(data: dict) -> ReflectDamageEffect:
        """Create a reflect damage effect."""
        percent = data.get('percent', 0.5)
        duration = data.get('duration', 3)
        return ReflectDamageEffect(reflect_percent=percent, duration=duration)

    @staticmethod
    def _create_shield(data: dict) -> ShieldEffect:
        """Create a shield (absorb) effect."""
        amount = data.get('amount', 50)
        duration = data.get('duration', 3)
        return ShieldEffect(shield_amount=amount, duration=duration)

    @staticmethod
    def _create_dispel(data: dict) -> DispelEffect:
        """Create a dispel effect."""
        dispel_type = data.get('dispel_type', 'all')
        return DispelEffect(dispel_type=dispel_type)

    @staticmethod
    def _create_resistance(data: dict) -> ResistanceEffect:
        """Create a resistance effect."""
        element = data.get('element', 'Physical')
        amount = data.get('amount', 0.25)
        duration = data.get('duration', 3)
        return ResistanceEffect(element=element, amount=amount, duration=duration)

    @staticmethod
    def _create_multi_buff(data: dict) -> MultiStatBuffEffect:
        """Create a multi-stat buff effect."""
        stats = data.get('stats', {})
        duration = data.get('duration', 3)
        return MultiStatBuffEffect(stat_modifiers=stats, duration=duration)

    @staticmethod
    def _create_dot(data: dict) -> DamageOverTimeEffect:
        """Create a damage-over-time effect."""
        dot_type = data.get('dot_type', 'Poison')
        damage_per_tick = data.get('damage_per_tick', 5)
        duration = data.get('duration', 3)
        element = data.get('element', 'Physical')

        return DamageOverTimeEffect(
            dot_type=dot_type,
            damage_per_tick=damage_per_tick,
            duration=duration,
            element=element
        )

    @staticmethod
    def _create_composite(data: dict) -> CompositeEffect:
        """Create a composite effect (multiple effects combined)."""
        from .effects import EffectFactory

        effect_list = data.get('effects', [])
        effects = [EffectFactory.create(e) for e in effect_list]
        return CompositeEffect(effects)

    @staticmethod
    def _create_chance(data: dict) -> ChanceEffect:
        """Create a chance-based effect."""
        chance = data.get('chance', 0.5)
        from .effects import EffectFactory

        inner_effect_data = data.get('effect', {})
        inner_effect = EffectFactory.create(inner_effect_data)

        return ChanceEffect(inner_effect, chance)

    @staticmethod
    def _create_stat_contest(data: dict) -> StatContestEffect:
        """Create a stat-contest gated effect (e.g. intel vs wisdom)."""
        from .effects import EffectFactory

        inner_effect_data = data.get('effect', {})
        inner_effect = EffectFactory.create(inner_effect_data)
        return StatContestEffect(
            effect=inner_effect,
            actor_stat=data.get('actor_stat', 'intel'),
            actor_divisor=data.get('actor_divisor', 2),
            target_stat=data.get('target_stat', 'wisdom'),
            target_lo_divisor=data.get('target_lo_divisor', 4),
            target_hi_divisor=data.get('target_hi_divisor', 1),
            actor_lo_divisor=data.get('actor_lo_divisor'),
            use_crit_multiplier=data.get('use_crit_multiplier', False),
            base_chance=data.get('base_chance'),
            chance_per_point=data.get('chance_per_point', 0.0),
            minimum_chance=data.get('minimum_chance', 0.0),
            maximum_chance=data.get('maximum_chance', 1.0),
        )

    @staticmethod
    def _create_dynamic_dot(data: dict) -> DynamicDotEffect:
        """Create a DOT whose damage scales from last damage dealt."""
        return DynamicDotEffect(
            dot_type=data.get('dot_type', 'DOT'),
            duration=data.get('duration', 2),
            damage_lo_fraction=data.get('damage_lo_fraction', 0.25),
            damage_hi_fraction=data.get('damage_hi_fraction', 0.5),
        )
