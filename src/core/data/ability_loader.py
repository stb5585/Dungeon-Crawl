"""
Data-Driven Ability System

This module provides a factory for creating abilities from data files (YAML/JSON).
This allows for easy balancing and modding without changing code.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import yaml

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
    DynamicExtraDamageEffect,
    DynamicStatusDotEffect,
    StatusApplyEffect,
    LifestealEffect,
    ReflectDamageEffect,
    DispelEffect,
    ShieldEffect,
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
    MagicEffectToggleEffect,
    ScreechEffect,
    AcidSpitEffect,
    BreathDamageEffect,
    NightmareFuelEffect,
    WidowsWailEffect,
    GoblinPunchEffect,
    HexEffect,
    VulcanizeEffect,
    HolyFollowupEffect,
    TurnUndeadEffect,
    ShieldSlamEffect,
    KidneyPunchEffect,
    PoisonStrikeEffect,
    DimMakEffect,
    ExploitWeaknessEffect,
    GoldTossEffect,
    LickEffect,
    BrainGorgeEffect,
    DetonateEffect,
    CrushEffect,
    MaelstromEffect,
    DisintegrateEffect,
    InspectEffect,
    ResistImmunityEffect,
    ResurrectionEffect,
    RevealEffect,
    TransformEffect,
    StompEffect,
    ThrowRockEffect,
    StealEffect,
    MugEffect,
    CounterspellEffect,
    ElementalStrikeEffect,
    BlackjackEffect,
    DoublecastEffect,
    ChooseFateEffect,
    ShapeshiftEffect,
    TetraDisasterEffect,
    ConsumeItemEffect,
    DestroyMetalEffect,
    SlotMachineEffect,
    TotemEffect,
    ChargeEffect,
    CrushingBlowEffect,
    ArcaneBlastEffect,
    JumpEffect,
    ShadowStrikeEffect,
    TitanicSlamEffect,
    DevourEffect,
    AbsoluteZeroEffect,
    EruptionEffect,
    MaelstromVortexEffect,
    ThunderstrikeEffect,
    WindShrapnelEffect,
    DivineJudgmentEffect,
    OblivionEffect,
    GrandHeistEffect,
    CataclysmEffect,
)

if TYPE_CHECKING:
    from src.core.effects.base import Effect


class EffectFactory:
    """
    Factory for creating Effect objects from data definitions.
    """
    
    @staticmethod
    def create(effect_data: dict) -> Effect:
        """
        Create an Effect from a data dictionary.
        
        Args:
            effect_data: Dictionary containing effect definition
            
        Returns:
            Effect instance
            
        Example effect_data:
            {
                'type': 'damage',
                'base': 20,
                'scaling': {
                    'stat': 'strength',
                    'ratio': 1.5
                },
                'element': 'Fire'
            }
        """
        effect_type = effect_data.get('type', '').lower()
        
        _dispatch = {
            'damage': EffectFactory._create_damage,
            'heal': EffectFactory._create_heal,
            'regen': EffectFactory._create_regen,
            'status': EffectFactory._create_status,
            'buff': EffectFactory._create_buff,
            'debuff': EffectFactory._create_debuff,
            'dot': EffectFactory._create_dot,
            'composite': EffectFactory._create_composite,
            'chance': EffectFactory._create_chance,
            'stat_contest': EffectFactory._create_stat_contest,
            'dynamic_dot': EffectFactory._create_dynamic_dot,
            'dynamic_extra_damage': EffectFactory._create_dynamic_extra_damage,
            'dynamic_status_dot': EffectFactory._create_dynamic_status_dot,
            'status_apply': EffectFactory._create_status_apply,
            'lifesteal': EffectFactory._create_lifesteal,
            'reflect': EffectFactory._create_reflect,
            'shield': EffectFactory._create_shield,
            'dispel': EffectFactory._create_dispel,
            'resistance': EffectFactory._create_resistance,
            'multi_buff': EffectFactory._create_multi_buff,
            'magic_effect_apply': EffectFactory._create_magic_effect_apply,
            'dynamic_stat_buff': EffectFactory._create_dynamic_stat_buff,
            'dynamic_multi_debuff': EffectFactory._create_dynamic_multi_debuff,
            'cleanse': EffectFactory._create_cleanse,
            'full_dispel': EffectFactory._create_full_dispel,
            'mana_drain_on_hit': EffectFactory._create_mana_drain_on_hit,
            'resource_convert': EffectFactory._create_resource_convert,
            'physical_effect_apply': EffectFactory._create_physical_effect_apply,
            'set_flag': EffectFactory._create_set_flag,
            'instant_kill': EffectFactory._create_instant_kill,
            'stat_reduce': EffectFactory._create_stat_reduce,
            'power_up_activate': EffectFactory._create_power_up_activate,
            'ability_chain': EffectFactory._create_ability_chain,
            'drain': EffectFactory._create_drain,
            'magic_effect_toggle': EffectFactory._create_magic_effect_toggle,
            'screech': EffectFactory._create_screech,
            'acid_spit': EffectFactory._create_acid_spit,
            'breath_damage': EffectFactory._create_breath_damage,
            'nightmare_fuel': EffectFactory._create_nightmare_fuel,
            'widows_wail': EffectFactory._create_widows_wail,
            'goblin_punch': EffectFactory._create_goblin_punch,
            'hex': EffectFactory._create_hex,
            'vulcanize': EffectFactory._create_vulcanize,
            'holy_followup': EffectFactory._create_holy_followup,
            'turn_undead': EffectFactory._create_turn_undead,
            'shield_slam': EffectFactory._create_shield_slam,
            'kidney_punch': EffectFactory._create_kidney_punch,
            'poison_strike': EffectFactory._create_poison_strike,
            'dim_mak': EffectFactory._create_dim_mak,
            'exploit_weakness': EffectFactory._create_exploit_weakness,
            'gold_toss': EffectFactory._create_gold_toss,
            'lick': EffectFactory._create_lick,
            'brain_gorge': EffectFactory._create_brain_gorge,
            'detonate': EffectFactory._create_detonate,
            'crush': EffectFactory._create_crush,
            'maelstrom': EffectFactory._create_maelstrom,
            'disintegrate': EffectFactory._create_disintegrate,
            'inspect': EffectFactory._create_inspect,
            'resist_immunity': EffectFactory._create_resist_immunity,
            'resurrection': EffectFactory._create_resurrection,
            'reveal': EffectFactory._create_reveal,
            'transform': EffectFactory._create_transform,
            'stomp': EffectFactory._create_stomp,
            'throw_rock': EffectFactory._create_throw_rock,
            'steal': EffectFactory._create_steal,
            'mug': EffectFactory._create_mug,
            'counterspell': EffectFactory._create_counterspell,
            'elemental_strike': EffectFactory._create_elemental_strike,
            'blackjack': EffectFactory._create_blackjack,
            'doublecast': EffectFactory._create_doublecast,
            'choose_fate': EffectFactory._create_choose_fate,
            'shapeshift': EffectFactory._create_shapeshift,
            'tetra_disaster': EffectFactory._create_tetra_disaster,
            'consume_item': EffectFactory._create_consume_item,
            'destroy_metal': EffectFactory._create_destroy_metal,
            'slot_machine': EffectFactory._create_slot_machine,
            'totem': EffectFactory._create_totem,
            'charge_execute': EffectFactory._create_charge_execute,
            'crushing_blow': EffectFactory._create_crushing_blow,
            'arcane_blast': EffectFactory._create_arcane_blast,
            'jump_execute': EffectFactory._create_jump_execute,
            'shadow_strike_execute': EffectFactory._create_shadow_strike_execute,
            'titanic_slam': EffectFactory._create_titanic_slam,
            'devour': EffectFactory._create_devour,
            'absolute_zero': EffectFactory._create_absolute_zero,
            'eruption': EffectFactory._create_eruption,
            'maelstrom_vortex': EffectFactory._create_maelstrom_vortex,
            'thunderstrike': EffectFactory._create_thunderstrike,
            'wind_shrapnel': EffectFactory._create_wind_shrapnel,
            'divine_judgment': EffectFactory._create_divine_judgment,
            'oblivion': EffectFactory._create_oblivion,
            'grand_heist': EffectFactory._create_grand_heist,
            'cataclysm': EffectFactory._create_cataclysm,
        }
        creator = _dispatch.get(effect_type)
        if creator is None:
            raise ValueError(f"Unknown effect type: {effect_type}")
        return creator(effect_data)
    
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
        effect_list = data.get('effects', [])
        effects = [EffectFactory.create(e) for e in effect_list]
        return CompositeEffect(effects)
    
    @staticmethod
    def _create_chance(data: dict) -> ChanceEffect:
        """Create a chance-based effect."""
        chance = data.get('chance', 0.5)
        inner_effect_data = data.get('effect', {})
        inner_effect = EffectFactory.create(inner_effect_data)
        
        return ChanceEffect(inner_effect, chance)

    @staticmethod
    def _create_stat_contest(data: dict) -> StatContestEffect:
        """Create a stat-contest gated effect (e.g. intel vs wisdom)."""
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

    @staticmethod
    def _create_magic_effect_toggle(data: dict) -> MagicEffectToggleEffect:
        return MagicEffectToggleEffect(
            effect_name=data.get('effect_name', 'Mana Shield'),
            cost=data.get('cost', 0),
            reduction=data.get('reduction', 2),
            activate_message=data.get('activate_message'),
            deactivate_message=data.get('deactivate_message'),
        )

    @staticmethod
    def _create_screech(data: dict) -> ScreechEffect:
        return ScreechEffect(
            damage_message=data.get('damage_message',
                "The deafening screech hurts {target} for {damage} damage.\n"),
            silence_message=data.get('silence_message',
                "{target} has been silenced.\n"),
            fail_message=data.get('fail_message',
                "The spell is ineffective.\n"),
        )

    @staticmethod
    def _create_acid_spit(data: dict) -> AcidSpitEffect:
        return AcidSpitEffect(
            base_cost=data.get('base_cost', 6),
            dot_duration=data.get('dot_duration', 2),
            damage_message=data.get('damage_message',
                "{target} takes {damage} damage from the acid.\n"),
            dot_message=data.get('dot_message',
                "{target} is covered in a corrosive substance.\n"),
            miss_message=data.get('miss_message',
                "{actor} misses {target} with Acid Spit.\n"),
            ineffective_message=data.get('ineffective_message',
                "The acid is ineffective.\n"),
            dodge_message=data.get('dodge_message',
                "{target} partially dodges the attack, only taking half damage.\n"),
        )

    @staticmethod
    def _create_breath_damage(data: dict) -> BreathDamageEffect:
        return BreathDamageEffect(
            multiplier=data.get('multiplier', 1.5),
            element=data.get('element', 'Non-elemental'),
            announce_message=data.get('announce_message',
                "{actor} unleashes a breath of {element} energy!\n"),
            damage_message=data.get('damage_message',
                "{target} takes {damage} damage from the breath weapon.\n"),
            no_effect_message=data.get('no_effect_message',
                "The breath weapon has no effect on {target}.\n"),
        )

    @staticmethod
    def _create_nightmare_fuel(data: dict) -> NightmareFuelEffect:
        return NightmareFuelEffect(
            crit_chance=data.get('crit_chance', 0.5),
            damage_message=data.get('damage_message',
                "{actor} invades {target}'s dreams, dealing {damage} damage"),
            fail_message=data.get('fail_message',
                "{target} resists the spell.\n"),
            no_sleep_message=data.get('no_sleep_message',
                "The spell does nothing.\n"),
        )

    @staticmethod
    def _create_widows_wail(data: dict) -> WidowsWailEffect:
        return WidowsWailEffect(
            multiplier=data.get('multiplier', 20),
            max_damage=data.get('max_damage', 200),
            self_message=data.get('self_message',
                "Anguish overwhelms {name}, taking {damage} damage.\n"),
            target_message=data.get('target_message',
                "Anguish overwhelms {name}, taking {damage} damage.\n"),
        )

    @staticmethod
    def _create_goblin_punch(data: dict) -> GoblinPunchEffect:
        return GoblinPunchEffect(
            max_punches=data.get('max_punches', 5),
            hit_message=data.get('hit_message',
                "{actor} punches {target} for {damage} damage.\n"),
            miss_message=data.get('miss_message',
                "{actor} punches air, missing {target}.\n"),
        )

    @staticmethod
    def _create_hex(data: dict) -> HexEffect:
        return HexEffect(
            duration=data.get('duration', 3),
            announce_message=data.get('announce_message',
                "{caster} curses {target} with a hex.\n"),
            poison_message=data.get('poison_message',
                "{target} is poisoned.\n"),
            blind_message=data.get('blind_message',
                "{target} is blinded.\n"),
            silence_message=data.get('silence_message',
                "{target} is silenced.\n"),
            no_effect_message=data.get('no_effect_message',
                "The hex has no effect.\n"),
        )

    @staticmethod
    def _create_vulcanize(data: dict) -> VulcanizeEffect:
        return VulcanizeEffect(
            health_fraction=data.get('health_fraction', 0.1),
            buff_duration=data.get('buff_duration', 5),
            buff_lo_divisor=data.get('buff_lo_divisor', 4),
            buff_hi_divisor=data.get('buff_hi_divisor', 2),
            damage_message=data.get('damage_message',
                "{target} takes {damage} damage from the flames.\n"),
            heal_message=data.get('heal_message',
                "{target} is healed by the flames for {damage} hit points.\n"),
            buff_message=data.get('buff_message',
                "{target} is hardened by the flames.\n"),
        )

    @staticmethod
    def _create_holy_followup(data: dict) -> HolyFollowupEffect:
        return HolyFollowupEffect(
            resist_type=data.get('resist_type', 'Holy'),
            damage_message=data.get('damage_message',
                "{actor} smites {target} for {damage} hit points.\n"),
            ineffective_message=data.get('ineffective_message',
                "{name} was ineffective and does no damage.\n"),
            absorb_message=data.get('absorb_message',
                "{target} absorbs {subtyp} and is healed for {heal} health.\n"),
            con_save_message=data.get('con_save_message',
                "{target} shrugs off the {name} and only receives half of the damage.\n"),
        )

    @staticmethod
    def _create_turn_undead(data: dict) -> TurnUndeadEffect:
        return TurnUndeadEffect(
            luck_factor=data.get('luck_factor', 6),
            kill_message=data.get('kill_message',
                "The {target} has been rebuked, destroying the undead monster.\n"),
            no_undead_message=data.get('no_undead_message',
                "The spell does nothing.\n"),
            damage_message=data.get('damage_message',
                "{actor} damages {target} for {damage} hit points"),
        )

    # ── Batch 9 factory methods ──

    @staticmethod
    def _create_shield_slam(data: dict) -> ShieldSlamEffect:
        return ShieldSlamEffect()

    @staticmethod
    def _create_kidney_punch(data: dict) -> KidneyPunchEffect:
        return KidneyPunchEffect(cost=data.get('cost', 12))

    @staticmethod
    def _create_poison_strike(data: dict) -> PoisonStrikeEffect:
        return PoisonStrikeEffect(damage_pct=data.get('damage_pct', 0.1))

    @staticmethod
    def _create_dim_mak(data: dict) -> DimMakEffect:
        return DimMakEffect()

    @staticmethod
    def _create_exploit_weakness(data: dict) -> ExploitWeaknessEffect:
        return ExploitWeaknessEffect()

    @staticmethod
    def _create_gold_toss(data: dict) -> GoldTossEffect:
        return GoldTossEffect()

    @staticmethod
    def _create_lick(data: dict) -> LickEffect:
        return LickEffect()

    @staticmethod
    def _create_brain_gorge(data: dict) -> BrainGorgeEffect:
        return BrainGorgeEffect()

    @staticmethod
    def _create_detonate(data: dict) -> DetonateEffect:
        return DetonateEffect()

    @staticmethod
    def _create_crush(data: dict) -> CrushEffect:
        return CrushEffect()

    @staticmethod
    def _create_maelstrom(data: dict) -> MaelstromEffect:
        return MaelstromEffect(
            success_pct=data.get('success_pct', 0.10),
            fail_pct=data.get('fail_pct', 0.25),
        )

    @staticmethod
    def _create_disintegrate(data: dict) -> DisintegrateEffect:
        return DisintegrateEffect()

    @staticmethod
    def _create_inspect(data: dict) -> InspectEffect:
        return InspectEffect()

    @staticmethod
    def _create_resist_immunity(data: dict) -> ResistImmunityEffect:
        return ResistImmunityEffect(
            resist_type=data.get('resist_type', 'Poison'),
            min_resist=data.get('min_resist', 0.5),
            immunity_name=data.get('immunity_name', 'Poison'),
        )

    @staticmethod
    def _create_resurrection(data: dict) -> ResurrectionEffect:
        return ResurrectionEffect(
            revive_pct=data.get('revive_pct', 0.1),
        )

    @staticmethod
    def _create_reveal(data: dict) -> RevealEffect:
        return RevealEffect(
            resist_bonus=data.get('resist_bonus', 0.25),
        )

    @staticmethod
    def _create_transform(data: dict) -> TransformEffect:
        return TransformEffect(
            creature=data.get('creature', 'Panther'),
        )

    @staticmethod
    def _create_stomp(data: dict) -> StompEffect:
        return StompEffect()

    @staticmethod
    def _create_throw_rock(data: dict) -> ThrowRockEffect:
        return ThrowRockEffect()

    @staticmethod
    def _create_steal(data: dict) -> StealEffect:
        return StealEffect(
            gold_cap=data.get('gold_cap', 0.05),
        )

    @staticmethod
    def _create_mug(data: dict) -> MugEffect:
        return MugEffect()

    @staticmethod
    def _create_counterspell(data: dict) -> CounterspellEffect:
        return CounterspellEffect()

    @staticmethod
    def _create_elemental_strike(data: dict) -> ElementalStrikeEffect:
        return ElementalStrikeEffect()

    @staticmethod
    def _create_blackjack(data: dict) -> BlackjackEffect:
        return BlackjackEffect()

    @staticmethod
    def _create_doublecast(data: dict) -> DoublecastEffect:
        return DoublecastEffect(
            cast_count=data.get('cast_count', 2),
            exclude_spells=data.get('exclude_spells', ["Magic Missile"]),
            ability_cost=data.get('ability_cost', 0),
        )

    @staticmethod
    def _create_choose_fate(data: dict) -> ChooseFateEffect:
        return ChooseFateEffect(
            dmg_mod=data.get('dmg_mod', 1.5),
        )

    @staticmethod
    def _create_shapeshift(data: dict) -> ShapeshiftEffect:
        return ShapeshiftEffect(
            status_name=data.get('status_name', 'Shapeshifted'),
            status_duration=data.get('status_duration', 3),
        )

    @staticmethod
    def _create_tetra_disaster(data: dict) -> TetraDisasterEffect:
        return TetraDisasterEffect(
            elements=data.get('elements', ["Fire", "Water", "Wind", "Earth"]),
            power_up_duration=data.get('power_up_duration', 5),
        )

    @staticmethod
    def _create_consume_item(data: dict) -> ConsumeItemEffect:
        return ConsumeItemEffect()

    @staticmethod
    def _create_destroy_metal(data: dict) -> DestroyMetalEffect:
        return DestroyMetalEffect(
            metal_subtypes=data.get('metal_subtypes'),
        )

    @staticmethod
    def _create_slot_machine(data: dict) -> SlotMachineEffect:
        return SlotMachineEffect()

    @staticmethod
    def _create_totem(data: dict) -> TotemEffect:
        return TotemEffect(
            aspects=data.get('aspects'),
            unlock_requirements=data.get('unlock_requirements'),
            duration_base=data.get('duration_base', 5),
        )

    @staticmethod
    def _create_charge_execute(data: dict) -> ChargeEffect:
        return ChargeEffect(
            dmg_mod=data.get('dmg_mod', 1.25),
            stun_duration=data.get('stun_duration', 1),
        )

    @staticmethod
    def _create_crushing_blow(data: dict) -> CrushingBlowEffect:
        return CrushingBlowEffect(
            dmg_mod=data.get('dmg_mod', 3.0),
            crit_override=data.get('crit_override', 2),
            stun_chance=data.get('stun_chance', 0.5),
            stun_duration=data.get('stun_duration', 2),
        )

    @staticmethod
    def _create_arcane_blast(data: dict) -> ArcaneBlastEffect:
        return ArcaneBlastEffect(
            regen_turns=data.get('regen_turns', 4),
            regen_fraction=data.get('regen_fraction', 0.1),
        )

    @staticmethod
    def _create_jump_execute(data: dict) -> JumpEffect:
        return JumpEffect(
            base_dmg_mod=data.get('base_dmg_mod', 2.0),
        )

    @staticmethod
    def _create_shadow_strike_execute(data: dict) -> ShadowStrikeEffect:
        return ShadowStrikeEffect(
            dmg_mod=data.get('dmg_mod', 2.0),
            blind_chance=data.get('blind_chance', 0.6),
            blind_duration=data.get('blind_duration', 2),
        )

    @staticmethod
    def _create_titanic_slam(data: dict) -> TitanicSlamEffect:
        return TitanicSlamEffect(
            dmg_mod=data.get('dmg_mod', 4.0),
            crit_override=data.get('crit_override', 2),
            stun_duration=data.get('stun_duration', 2),
        )

    @staticmethod
    def _create_devour(data: dict) -> DevourEffect:
        return DevourEffect(
            num_bites=data.get('num_bites', 3),
            multiplier=data.get('multiplier', 1.5),
            element=data.get('element', 'Earth'),
        )

    @staticmethod
    def _create_absolute_zero(data: dict) -> AbsoluteZeroEffect:
        return AbsoluteZeroEffect(
            damage_mod=data.get('damage_mod', 3.0),
            stun_duration=data.get('stun_duration', 3),
            def_reduction=data.get('def_reduction', 5),
        )

    @staticmethod
    def _create_eruption(data: dict) -> EruptionEffect:
        return EruptionEffect(
            damage_mod=data.get('damage_mod', 3.5),
            burn_duration=data.get('burn_duration', 3),
            vulcanize_duration=data.get('vulcanize_duration', 3),
        )

    @staticmethod
    def _create_maelstrom_vortex(data: dict) -> MaelstromVortexEffect:
        return MaelstromVortexEffect(
            damage_mod=data.get('damage_mod', 3.0),
            status_duration=data.get('status_duration', 3),
        )

    @staticmethod
    def _create_thunderstrike(data: dict) -> ThunderstrikeEffect:
        return ThunderstrikeEffect(
            damage_mod=data.get('damage_mod', 3.0),
            chain_hits=data.get('chain_hits', 2),
            chain_multiplier=data.get('chain_multiplier', 0.5),
            stun_duration=data.get('stun_duration', 2),
        )

    @staticmethod
    def _create_wind_shrapnel(data: dict) -> WindShrapnelEffect:
        return WindShrapnelEffect(
            num_hits=data.get('num_hits', 5),
            damage_mod=data.get('damage_mod', 1.2),
            crit_chance=data.get('crit_chance', 0.25),
            crit_multiplier=data.get('crit_multiplier', 2.0),
        )

    @staticmethod
    def _create_divine_judgment(data: dict) -> DivineJudgmentEffect:
        return DivineJudgmentEffect(
            damage_mod=data.get('damage_mod', 3.0),
            undead_multiplier=data.get('undead_multiplier', 2.0),
            heal_fraction=data.get('heal_fraction', 0.5),
        )

    @staticmethod
    def _create_oblivion(data: dict) -> OblivionEffect:
        return OblivionEffect(
            damage_mod=data.get('damage_mod', 4.0),
            kill_chance=data.get('kill_chance', 0.2),
            stat_drain=data.get('stat_drain', 3),
        )

    @staticmethod
    def _create_grand_heist(data: dict) -> GrandHeistEffect:
        return GrandHeistEffect(
            gold_multiplier=data.get('gold_multiplier', 2.0),
            debuff_duration=data.get('debuff_duration', 3),
        )

    @staticmethod
    def _create_cataclysm(data: dict) -> CataclysmEffect:
        return CataclysmEffect(
            spell_count=data.get('spell_count', 3),
            breath_multiplier=data.get('breath_multiplier', 2.0),
            power_up_duration=data.get('power_up_duration', 3),
        )


class AbilityFactory:
    """
    Factory for creating Ability objects from data definitions.

    When ``combat_ready=True`` (the default), the factory produces
    ``DataDrivenSpell`` / ``DataDrivenSkill`` instances whose ``cast()``
    and ``use()`` methods replicate the core combat pipeline and execute
    the composed effects.  These are fully usable in combat.

    When ``combat_ready=False``, a lightweight ``SimpleAbility`` dataclass
    is returned instead (useful for config loading and analytics only).
    """
    
    @staticmethod
    def create_from_dict(ability_data: dict, *, combat_ready: bool = True):
        """
        Create an Ability from a data dictionary.
        
        Args:
            ability_data: Dictionary containing ability definition
            combat_ready: If True, produce a DataDrivenSpell/DataDrivenSkill
                         that works in combat.  If False, produce a lightweight
                         SimpleAbility for config loading only.
            
        Returns:
            Ability instance (DataDrivenSpell, DataDrivenSkill, or SimpleAbility)
        """
        name = ability_data.get('name', 'Unknown')
        description = ability_data.get('description', '')
        cost = ability_data.get('cost', 0)
        ability_type = ability_data.get('type', 'Skill')
        subtype = ability_data.get('subtype', 'Offensive')
        damage_mod = ability_data.get('damage_mod', 1.0)
        crit = ability_data.get('crit', 5)
        rank = ability_data.get('rank')
        charge_time = ability_data.get('charge_time')
        delay = ability_data.get('delay')
        telegraph_message = ability_data.get('telegraph_message')
        priority = ability_data.get('priority')
        notes = ability_data.get('notes')
        school = ability_data.get('school')
        weapon = ability_data.get('weapon', False)

        # Create Effect objects
        effects = []
        if 'effects' in ability_data:
            for effect_data in ability_data['effects']:
                effects.append(EffectFactory.create(effect_data))

        if not combat_ready:
            return AbilityFactory._create_simple(ability_data, effects)

        # ── Combat-ready instances ────────────────────────────────
        from src.core.data.data_driven_abilities import (
            DataDrivenSpell,
            DataDrivenSkill,
            DataDrivenHealSpell,
            DataDrivenSupportSpell,
            DataDrivenStatusSpell,
            DataDrivenStatusSkill,
            DataDrivenWeaponSpell,
            DataDrivenCustomSpell,
            DataDrivenChargingSkill,
            DataDrivenMagicMissileSpell,
            DataDrivenJumpSkill,
            DataDrivenMovementSpell,
        )

        if ability_type == 'Heal':
            ability = DataDrivenHealSpell(
                name=name,
                description=description,
                cost=cost,
                heal=ability_data.get('heal', 0.3),
                crit=crit,
                turns=ability_data.get('turns', 0),
                effects=effects,
                rank=rank,
                instant_heal=ability_data.get('instant_heal', False),
            )
        elif ability_type == 'Support':
            ability = DataDrivenSupportSpell(
                name=name,
                description=description,
                cost=cost,
                effects=effects,
                school=school,
                rank=rank,
                target_self=ability_data.get('target_self', True),
                wizard_free_cast=ability_data.get('wizard_free_cast', False),
                message=ability_data.get('message'),
                subtype=subtype,
            )
        elif ability_type == 'Status':
            ability = DataDrivenStatusSpell(
                name=name,
                description=description,
                cost=cost,
                effects=effects,
                rank=rank,
                wizard_free_cast=ability_data.get('wizard_free_cast', False),
                messages=ability_data.get('messages'),
                subtype=ability_data.get('subtype'),
                school=ability_data.get('school'),
            )
        elif ability_type == 'StatusSkill':
            ability = DataDrivenStatusSkill(
                name=name,
                description=description,
                cost=cost,
                effects=effects,
                subtyp=subtype,
                status_name=ability_data.get('status_name'),
                physical=ability_data.get('physical', False),
                actor_stat=ability_data.get('actor_stat', 'strength'),
                actor_lo_divisor=ability_data.get('actor_lo_divisor', 2),
                actor_hi_divisor=ability_data.get('actor_hi_divisor', 1),
                actor_use_check_mod=ability_data.get('actor_use_check_mod'),
                actor_stat_alt=ability_data.get('actor_stat_alt'),
                target_stat=ability_data.get('target_stat', 'wisdom'),
                target_lo_divisor=ability_data.get('target_lo_divisor', 2),
                target_hi_divisor=ability_data.get('target_hi_divisor', 1),
                target_use_check_mod=ability_data.get('target_use_check_mod'),
                duration=ability_data.get('duration', 3),
                duration_stat=ability_data.get('duration_stat'),
                duration_divisor=ability_data.get('duration_divisor', 5),
                duration_min=ability_data.get('duration_min', 3),
                skip_if_active=ability_data.get('skip_if_active', True),
                extend_if_active=ability_data.get('extend_if_active', 0),
                check_disarmable=ability_data.get('check_disarmable', False),
                check_flying=ability_data.get('check_flying', False),
                use_crit_multiplier=ability_data.get('use_crit_multiplier', False),
                messages=ability_data.get('messages'),
                add_luck_chance=ability_data.get('add_luck_chance', False),
                action_message=ability_data.get('action_message'),
            )
        elif ability_type == 'Spell':
            ability = DataDrivenSpell(
                name=name,
                description=description,
                cost=cost,
                dmg_mod=damage_mod,
                crit=crit,
                subtyp=subtype,
                effects=effects,
                school=school,
                rank=rank,
                charge_time=charge_time,
                delay=delay,
                telegraph_message=telegraph_message,
                priority=priority,
                notes=notes,
            )
        elif ability_type == 'WeaponSpell':
            ability = DataDrivenWeaponSpell(
                name=name,
                description=description,
                cost=cost,
                dmg_mod=damage_mod,
                crit=crit,
                subtyp=ability_data.get('subtype', 'Holy'),
                effects=effects,
                school=school,
                rank=rank,
            )
        elif ability_type == 'CustomSpell':
            ability = DataDrivenCustomSpell(
                name=name,
                description=description,
                cost=cost,
                dmg_mod=damage_mod,
                crit=crit,
                subtyp=ability_data.get('subtype', 'Holy'),
                effects=effects,
                school=school,
                rank=rank,
            )
        elif ability_type == 'ChargingSkill':
            ability = DataDrivenChargingSkill(
                name=name,
                description=description,
                cost=cost,
                weapon=weapon,
                dmg_mod=damage_mod,
                effects=effects,
                subtyp=subtype,
                charge_time=charge_time,
                delay=delay,
                telegraph_message=telegraph_message,
                priority=priority,
                notes=notes,
                requires_any_mana=ability_data.get('requires_any_mana', False),
            )
        elif ability_type == 'MagicMissile':
            ability = DataDrivenMagicMissileSpell(
                name=name,
                description=description,
                cost=cost,
                dmg_mod=damage_mod,
                crit=crit,
                subtyp=ability_data.get('subtype', 'Non-elemental'),
                missiles=ability_data.get('missiles', 1),
                effects=effects,
                school=school,
                rank=rank,
            )
        elif ability_type == 'JumpSkill':
            ability = DataDrivenJumpSkill(
                name=name,
                description=description,
                cost=cost,
                weapon=ability_data.get('weapon', True),
                dmg_mod=damage_mod,
                effects=effects,
                subtyp=subtype,
                charge_time=ability_data.get('charge_time', 1),
                telegraph_message=telegraph_message,
                prone_while_charging=ability_data.get(
                    'prone_while_charging', True
                ),
                unlock_requirements=ability_data.get(
                    'unlock_requirements'
                ),
                modifications_defaults=ability_data.get(
                    'modifications_defaults'
                ),
                unlocked_defaults=ability_data.get(
                    'unlocked_defaults'
                ),
                priority=priority,
                notes=notes,
            )
        elif ability_type == 'Movement':
            ability = DataDrivenMovementSpell(
                name=name,
                description=description,
                cost=cost,
                movement_type=ability_data.get(
                    'movement_type', 'sanctuary'
                ),
                combat=ability_data.get('combat', True),
                effects=effects,
                notes=notes,
            )
        else:
            ability = DataDrivenSkill(
                name=name,
                description=description,
                cost=cost,
                weapon=weapon,
                dmg_mod=damage_mod,
                effects=effects,
                subtyp=subtype,
                charge_time=charge_time,
                delay=delay,
                telegraph_message=telegraph_message,
                priority=priority,
                notes=notes,
                ignore_armor=ability_data.get('ignore_armor', False),
                guaranteed_hit=ability_data.get('guaranteed_hit', False),
                crit_override=ability_data.get('crit_override'),
                strikes=ability_data.get('strikes', 1),
                requires_incapacitated=ability_data.get('requires_incapacitated', False),
                intel_dmg_mod=ability_data.get('intel_dmg_mod', False),
                ice_block_check=ability_data.get('ice_block_check', False),
                self_target=ability_data.get('self_target', False),
                use_out_enabled=ability_data.get('use_out_enabled', False),
            )

        # Stash raw data for inspection / analytics
        ability._raw_data = ability_data
        # Carry over passive flag from YAML
        if ability_data.get('passive', False):
            ability.passive = True
        return ability

    @staticmethod
    def _create_simple(ability_data: dict, effects: list):
        """Produce a lightweight SimpleAbility (config loading only)."""
        from dataclasses import dataclass, field

        @dataclass
        class SimpleAbility:
            """Simplified ability structure for data-driven abilities."""
            name: str
            typ: str
            subtyp: str
            description: str
            cost: int
            dmg_mod: float
            effects: list = field(default_factory=list)
            charge_time: int | None = None
            delay: int | None = None
            telegraph_message: str | None = None
            priority: str | None = None
            prone_while_charging: bool | None = None
            notes: str | None = None
            raw_data: dict = field(default_factory=dict)

        return SimpleAbility(
            name=ability_data.get('name', 'Unknown'),
            typ=ability_data.get('type', 'Skill'),
            subtyp=ability_data.get('subtype', 'Offensive'),
            description=ability_data.get('description', ''),
            cost=ability_data.get('cost', 0),
            dmg_mod=ability_data.get('damage_mod', 1.0),
            effects=effects,
            charge_time=ability_data.get('charge_time'),
            delay=ability_data.get('delay'),
            telegraph_message=ability_data.get('telegraph_message'),
            priority=ability_data.get('priority'),
            prone_while_charging=ability_data.get('prone_while_charging'),
            notes=ability_data.get('notes'),
            raw_data=ability_data,
        )
    
    @staticmethod
    def create_from_yaml(file_path: str | Path, *, combat_ready: bool = True):
        """
        Load an ability from a YAML file.
        
        Args:
            file_path: Path to the YAML file
            combat_ready: If True, produce combat-ready instances.
            
        Returns:
            Ability instance
        """
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return AbilityFactory.create_from_dict(data, combat_ready=combat_ready)
    
    @staticmethod
    def load_abilities_from_directory(
        directory: str | Path, *, combat_ready: bool = True
    ) -> dict:
        """
        Load all abilities from a directory of YAML files.
        
        Args:
            directory: Path to directory containing ability definitions
            combat_ready: If True, produce combat-ready instances.
            
        Returns:
            Dictionary mapping ability names to Ability objects
        """
        directory_path = Path(directory)
        abilities = {}
        
        for file_path in directory_path.glob('*.yaml'):
            try:
                ability = AbilityFactory.create_from_yaml(
                    file_path, combat_ready=combat_ready
                )
                abilities[ability.name] = ability
            except Exception as e:
                print(f"Error loading ability from {file_path}: {e}")
        
        return abilities


# Example ability definitions for testing
EXAMPLE_ABILITIES = {
    'fireball': {
        'name': 'Fireball',
        'type': 'Spell',
        'subtype': 'Offensive',
        'description': 'Launches a ball of fire at the enemy',
        'cost': 15,
        'damage_mod': 1.5,
        'effects': [
            {
                'type': 'damage',
                'base': 25,
                'scaling': {
                    'stat': 'intelligence',
                    'ratio': 1.5
                },
                'element': 'Fire'
            },
            {
                'type': 'chance',
                'chance': 0.3,
                'effect': {
                    'type': 'dot',
                    'dot_type': 'Burn',
                    'damage_per_tick': 5,
                    'duration': 3,
                    'element': 'Fire'
                }
            }
        ]
    },
    'blessing': {
        'name': 'Blessing',
        'type': 'Spell',
        'subtype': 'Support',
        'description': 'Increases attack and defense',
        'cost': 12,
        'effects': [
            {
                'type': 'buff',
                'stat': 'attack',
                'amount': 10,
                'duration': 5
            },
            {
                'type': 'buff',
                'stat': 'defense',
                'amount': 8,
                'duration': 5
            }
        ]
    }
}


def save_example_abilities(output_dir: str | Path) -> None:
    """
    Save example ability definitions to YAML files.
    Useful for creating initial data files.
    
    Args:
        output_dir: Directory to save the files to
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for ability_id, ability_data in EXAMPLE_ABILITIES.items():
        file_path = output_path / f"{ability_id}.yaml"
        with open(file_path, 'w') as f:
            yaml.dump(ability_data, f, default_flow_style=False, sort_keys=False)
        print(f"Saved {ability_data['name']} to {file_path}")
