"""Concrete effect factory composed from focused constructor groups."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .effect_base import BaseEffectFactoryMixin
from .effect_dynamic import DynamicEffectFactoryMixin
from .effect_enemy import EnemyEffectFactoryMixin
from .effect_special import SpecialEffectFactoryMixin

if TYPE_CHECKING:
    from src.core.effects.base import Effect


class EffectFactory(
    BaseEffectFactoryMixin,
    DynamicEffectFactoryMixin,
    EnemyEffectFactoryMixin,
    SpecialEffectFactoryMixin,
):
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
        effect_type = effect_data.get("type", "").lower()

        _dispatch = {
            "damage": EffectFactory._create_damage,
            "heal": EffectFactory._create_heal,
            "regen": EffectFactory._create_regen,
            "status": EffectFactory._create_status,
            "buff": EffectFactory._create_buff,
            "debuff": EffectFactory._create_debuff,
            "dot": EffectFactory._create_dot,
            "composite": EffectFactory._create_composite,
            "chance": EffectFactory._create_chance,
            "stat_contest": EffectFactory._create_stat_contest,
            "dynamic_dot": EffectFactory._create_dynamic_dot,
            "dynamic_extra_damage": EffectFactory._create_dynamic_extra_damage,
            "dynamic_status_dot": EffectFactory._create_dynamic_status_dot,
            "status_apply": EffectFactory._create_status_apply,
            "lifesteal": EffectFactory._create_lifesteal,
            "reflect": EffectFactory._create_reflect,
            "shield": EffectFactory._create_shield,
            "dispel": EffectFactory._create_dispel,
            "resistance": EffectFactory._create_resistance,
            "multi_buff": EffectFactory._create_multi_buff,
            "magic_effect_apply": EffectFactory._create_magic_effect_apply,
            "dynamic_stat_buff": EffectFactory._create_dynamic_stat_buff,
            "dynamic_multi_debuff": EffectFactory._create_dynamic_multi_debuff,
            "cleanse": EffectFactory._create_cleanse,
            "full_dispel": EffectFactory._create_full_dispel,
            "mana_drain_on_hit": EffectFactory._create_mana_drain_on_hit,
            "resource_convert": EffectFactory._create_resource_convert,
            "physical_effect_apply": EffectFactory._create_physical_effect_apply,
            "set_flag": EffectFactory._create_set_flag,
            "instant_kill": EffectFactory._create_instant_kill,
            "stat_reduce": EffectFactory._create_stat_reduce,
            "power_up_activate": EffectFactory._create_power_up_activate,
            "ability_chain": EffectFactory._create_ability_chain,
            "drain": EffectFactory._create_drain,
            "magic_effect_toggle": EffectFactory._create_magic_effect_toggle,
            "screech": EffectFactory._create_screech,
            "acid_spit": EffectFactory._create_acid_spit,
            "breath_damage": EffectFactory._create_breath_damage,
            "nightmare_fuel": EffectFactory._create_nightmare_fuel,
            "widows_wail": EffectFactory._create_widows_wail,
            "goblin_punch": EffectFactory._create_goblin_punch,
            "hex": EffectFactory._create_hex,
            "vulcanize": EffectFactory._create_vulcanize,
            "holy_followup": EffectFactory._create_holy_followup,
            "turn_undead": EffectFactory._create_turn_undead,
            "shield_slam": EffectFactory._create_shield_slam,
            "kidney_punch": EffectFactory._create_kidney_punch,
            "poison_strike": EffectFactory._create_poison_strike,
            "dim_mak": EffectFactory._create_dim_mak,
            "exploit_weakness": EffectFactory._create_exploit_weakness,
            "gold_toss": EffectFactory._create_gold_toss,
            "lick": EffectFactory._create_lick,
            "brain_gorge": EffectFactory._create_brain_gorge,
            "detonate": EffectFactory._create_detonate,
            "crush": EffectFactory._create_crush,
            "maelstrom": EffectFactory._create_maelstrom,
            "disintegrate": EffectFactory._create_disintegrate,
            "inspect": EffectFactory._create_inspect,
            "resist_immunity": EffectFactory._create_resist_immunity,
            "resurrection": EffectFactory._create_resurrection,
            "reveal": EffectFactory._create_reveal,
            "transform": EffectFactory._create_transform,
            "stomp": EffectFactory._create_stomp,
            "throw_rock": EffectFactory._create_throw_rock,
            "steal": EffectFactory._create_steal,
            "mug": EffectFactory._create_mug,
            "counterspell": EffectFactory._create_counterspell,
            "elemental_strike": EffectFactory._create_elemental_strike,
            "blackjack": EffectFactory._create_blackjack,
            "doublecast": EffectFactory._create_doublecast,
            "choose_fate": EffectFactory._create_choose_fate,
            "vesperion_choose_fate": EffectFactory._create_vesperion_choose_fate,
            "shapeshift": EffectFactory._create_shapeshift,
            "astral_judgment": EffectFactory._create_astral_judgment,
            "consume_item": EffectFactory._create_consume_item,
            "destroy_metal": EffectFactory._create_destroy_metal,
            "slot_machine": EffectFactory._create_slot_machine,
            "totem": EffectFactory._create_totem,
            "soul_drain": EffectFactory._create_soul_drain,
            "charge_execute": EffectFactory._create_charge_execute,
            "crushing_blow": EffectFactory._create_crushing_blow,
            "arcane_blast": EffectFactory._create_arcane_blast,
            "jump_execute": EffectFactory._create_jump_execute,
            "shadow_strike_execute": EffectFactory._create_shadow_strike_execute,
            "titanic_slam": EffectFactory._create_titanic_slam,
            "devour": EffectFactory._create_devour,
            "absolute_zero": EffectFactory._create_absolute_zero,
            "eruption": EffectFactory._create_eruption,
            "maelstrom_vortex": EffectFactory._create_maelstrom_vortex,
            "thunderstrike": EffectFactory._create_thunderstrike,
            "wind_shrapnel": EffectFactory._create_wind_shrapnel,
            "divine_judgment": EffectFactory._create_divine_judgment,
            "oblivion": EffectFactory._create_oblivion,
            "grand_heist": EffectFactory._create_grand_heist,
            "cataclysm": EffectFactory._create_cataclysm,
        }
        creator = _dispatch.get(effect_type)
        if creator is None:
            raise ValueError(f"Unknown effect type: {effect_type}")
        return creator(effect_data)
