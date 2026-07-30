"""Dynamic, resource, and state-oriented effect constructors."""

from __future__ import annotations

from src.core.effects import (
    DynamicExtraDamageEffect,
    DynamicStatusDotEffect,
    StatusApplyEffect,
    MagicEffectApplyEffect,
    DynamicStatBuffEffect,
    DynamicMultiDebuffEffect,
    CleanseEffect,
    FullDispelEffect,
    ManaDrainOnHitEffect,
    ResourceConvertEffect,
    PhysicalEffectApplyEffect,
    SetFlagEffect,
    InstantKillEffect,
    StatReduceEffect,
    PowerUpActivateEffect,
    AbilityChainEffect,
    DrainEffect,
)


class DynamicEffectFactoryMixin:
    @staticmethod
    def _create_dynamic_extra_damage(data: dict) -> DynamicExtraDamageEffect:
        """Create an extra-damage effect scaling from last damage dealt."""
        return DynamicExtraDamageEffect(
            damage_lo_fraction=data.get('damage_lo_fraction', 0.5),
            damage_hi_fraction=data.get('damage_hi_fraction', 1.0),
            message_template=data.get(
                'message_template',
                '{target} is chilled to the bone, taking an extra {damage} damage.\n',
            ),
        )

    @staticmethod
    def _create_dynamic_status_dot(data: dict) -> DynamicStatusDotEffect:
        """Create a status-based DOT (e.g. Poison) scaling from last damage."""
        return DynamicStatusDotEffect(
            status_name=data.get('status_name', 'Poison'),
            duration=data.get('duration', 2),
            duration_min=data.get('duration_min', 2),
            duration_stat=data.get('duration_stat'),
            duration_stat_divisor=data.get('duration_stat_divisor', 10),
            damage_lo_fraction=data.get('damage_lo_fraction', 1.0),
            damage_hi_fraction=data.get('damage_hi_fraction', 1.0),
            health_multiplier=data.get('health_multiplier'),
        )

    @staticmethod
    def _create_status_apply(data: dict) -> StatusApplyEffect:
        """Create a status-apply effect with immunity checks."""
        return StatusApplyEffect(
            status_name=data.get('status_name', 'Stun'),
            duration=data.get('duration', 1),
            use_crit_bonus=data.get('use_crit_bonus', False),
            crit_only=data.get('crit_only', False),
            skip_if_active=data.get('skip_if_active', False),
            duration_stat=data.get('duration_stat'),
            duration_stat_divisor=data.get('duration_stat_divisor', 10),
            duration_min=data.get('duration_min', 2),
            duration_random=data.get('duration_random', False),
        )

    @staticmethod
    def _create_magic_effect_apply(data: dict) -> MagicEffectApplyEffect:
        return MagicEffectApplyEffect(
            effect_name=data.get('effect_name', 'Reflect'),
            duration=data.get('duration', 3),
            duration_stat=data.get('duration_stat'),
            duration_stat_divisor=data.get('duration_stat_divisor', 10),
            duration_stat_mode=data.get('duration_stat_mode', 'add'),
        )

    @staticmethod
    def _create_dynamic_stat_buff(data: dict) -> DynamicStatBuffEffect:
        return DynamicStatBuffEffect(
            buff_stat=data.get('buff_stat', 'Attack'),
            source=data.get('source', 'target_combat'),
            source_stat=data.get('source_stat', 'attack'),
            lo_divisor=data.get('lo_divisor', 4),
            hi_divisor=data.get('hi_divisor', 2),
            duration=data.get('duration', 3),
            duration_stat=data.get('duration_stat'),
            duration_divisor=data.get('duration_divisor', 10),
            duration_min=data.get('duration_min', 3),
            apply_to_caster=data.get('apply_to_caster', False),
        )

    @staticmethod
    def _create_dynamic_multi_debuff(data: dict) -> DynamicMultiDebuffEffect:
        return DynamicMultiDebuffEffect(
            stats=data.get('stats', []),
            scaling_stat=data.get('scaling_stat', 'intel'),
            scaling_divisor=data.get('scaling_divisor', 10),
            amount_divisor=data.get('amount_divisor', 10),
            duration_min=data.get('duration_min', 3),
        )

    @staticmethod
    def _create_cleanse(data: dict) -> CleanseEffect:
        return CleanseEffect()

    @staticmethod
    def _create_full_dispel(data: dict) -> FullDispelEffect:
        return FullDispelEffect(
            magic_effects=data.get('magic_effects'),
        )

    @staticmethod
    def _create_mana_drain_on_hit(data: dict) -> ManaDrainOnHitEffect:
        return ManaDrainOnHitEffect(
            divisor=data.get('divisor', 5),
        )

    @staticmethod
    def _create_resource_convert(data: dict) -> ResourceConvertEffect:
        return ResourceConvertEffect(
            source=data.get('source', 'health'),
            target_resource=data.get('target_resource', 'mana'),
            percent=data.get('percent', 0.1),
            ring_mod=data.get('ring_mod'),
        )

    @staticmethod
    def _create_physical_effect_apply(data: dict) -> PhysicalEffectApplyEffect:
        return PhysicalEffectApplyEffect(
            effect_name=data.get('effect_name', 'Prone'),
            actor_stat=data.get('actor_stat', 'strength'),
            actor_lo_divisor=data.get('actor_lo_divisor', 2),
            actor_hi_divisor=data.get('actor_hi_divisor', 1),
            target_stat=data.get('target_stat', 'con'),
            target_lo_divisor=data.get('target_lo_divisor', 2),
            target_hi_divisor=data.get('target_hi_divisor', 1),
            duration=data.get('duration', 3),
            duration_stat=data.get('duration_stat'),
            duration_divisor=data.get('duration_divisor', 10),
            duration_min=data.get('duration_min', 1),
            skip_if_active=data.get('skip_if_active', False),
            requires_crit=data.get('requires_crit', False),
            use_crit_multiplier=data.get('use_crit_multiplier', False),
            damage_multiplier=data.get('damage_multiplier', 0.0),
            check_flying=data.get('check_flying', False),
            check_disarmable=data.get('check_disarmable', False),
        )

    @staticmethod
    def _create_set_flag(data: dict) -> SetFlagEffect:
        return SetFlagEffect(
            flag=data['flag'],
            value=data.get('value', True),
            message=data.get('message'),
        )

    @staticmethod
    def _create_instant_kill(data: dict) -> InstantKillEffect:
        return InstantKillEffect(
            success_message=data.get('success_message', '{target} is slain.'),
            actor_stat=data.get('actor_stat', 'charisma'),
            actor_divisor=data.get('actor_divisor', 1),
            target_stat=data.get('target_stat', 'con'),
            target_lo_divisor=data.get('target_lo_divisor', 2),
            target_hi_divisor=data.get('target_hi_divisor', 1),
            apply_resist_multiplier=data.get('apply_resist_multiplier', True),
            resist_type=data.get('resist_type', 'Death'),
            luck_factor=data.get('luck_factor', 10),
            immunity_status=data.get('immunity_status'),
            reflect_item=data.get('reflect_item'),
            reflect_slot=data.get('reflect_slot', 'OffHand'),
            reflect_message=data.get('reflect_message', ''),
        )

    @staticmethod
    def _create_stat_reduce(data: dict) -> StatReduceEffect:
        return StatReduceEffect(
            stat=data.get('stat', 'con'),
            amount=data.get('amount', 1),
            actor_stat=data.get('actor_stat', 'intel'),
            actor_divisor=data.get('actor_divisor', 2),
            target_stat=data.get('target_stat', 'con'),
            target_lo_divisor=data.get('target_lo_divisor', 2),
            target_hi_divisor=data.get('target_hi_divisor', 1),
            luck_factor=data.get('luck_factor', 10),
            success_message=data.get('success_message', ''),
        )

    @staticmethod
    def _create_power_up_activate(data: dict) -> PowerUpActivateEffect:
        return PowerUpActivateEffect(
            duration=data.get('duration', 5),
            extra_mode=data.get('extra_mode'),
            lo_frac=data.get('lo_frac', 0.25),
            hi_frac=data.get('hi_frac', 0.5),
            sacrifice_pct=data.get('sacrifice_pct', 0.25),
            sacrifice_divisor=data.get('sacrifice_divisor', 5),
            sacrifice_minimum=data.get('sacrifice_minimum', 5),
            message=data.get('message'),
        )

    @staticmethod
    def _create_ability_chain(data: dict) -> AbilityChainEffect:
        return AbilityChainEffect(
            ability_name=data.get('ability_name', ''),
            target_self=data.get('target_self', False),
            special=data.get('special', True),
            use_method=data.get('use_method', 'auto'),
        )

    @staticmethod
    def _create_drain(data: dict) -> DrainEffect:
        return DrainEffect(
            resource=data.get('resource', 'health'),
            base_stat=data.get('base_stat', 'health_current'),
            secondary_stat=data.get('secondary_stat', 'charisma'),
            lo_divisor=data.get('lo_divisor', 5),
            hi_divisor=data.get('hi_divisor', 1.5),
            luck_factor=data.get('luck_factor', 10),
            cap_percent=data.get('cap_percent', 0.18),
            message=data.get('message'),
        )
