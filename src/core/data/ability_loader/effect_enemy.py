"""Enemy-specialty effect constructors."""

from __future__ import annotations

from src.core.effects import (
    AcidSpitEffect,
    BreathDamageEffect,
    GoblinPunchEffect,
    HexEffect,
    HolyFollowupEffect,
    MagicEffectToggleEffect,
    NightmareFuelEffect,
    ScreechEffect,
    TurnUndeadEffect,
    VulcanizeEffect,
    WidowsWailEffect,
)


class EnemyEffectFactoryMixin:
    @staticmethod
    def _create_magic_effect_toggle(data: dict) -> MagicEffectToggleEffect:
        return MagicEffectToggleEffect(
            effect_name=data.get("effect_name", "Mana Shield"),
            cost=data.get("cost", 0),
            reduction=data.get("reduction", 2),
            activate_message=data.get("activate_message"),
            deactivate_message=data.get("deactivate_message"),
        )

    @staticmethod
    def _create_screech(data: dict) -> ScreechEffect:
        return ScreechEffect(
            damage_message=data.get(
                "damage_message", "The deafening screech hurts {target} for {damage} damage.\n"
            ),
            silence_message=data.get("silence_message", "{target} has been silenced.\n"),
            fail_message=data.get("fail_message", "The spell is ineffective.\n"),
        )

    @staticmethod
    def _create_acid_spit(data: dict) -> AcidSpitEffect:
        return AcidSpitEffect(
            base_cost=data.get("base_cost", 6),
            dot_duration=data.get("dot_duration", 2),
            damage_message=data.get(
                "damage_message", "{target} takes {damage} damage from the acid.\n"
            ),
            dot_message=data.get("dot_message", "{target} is covered in a corrosive substance.\n"),
            miss_message=data.get("miss_message", "{actor} misses {target} with Acid Spit.\n"),
            ineffective_message=data.get("ineffective_message", "The acid is ineffective.\n"),
            dodge_message=data.get(
                "dodge_message", "{target} partially dodges the attack, only taking half damage.\n"
            ),
        )

    @staticmethod
    def _create_breath_damage(data: dict) -> BreathDamageEffect:
        return BreathDamageEffect(
            multiplier=data.get("multiplier", 1.5),
            element=data.get("element", "Non-elemental"),
            announce_message=data.get(
                "announce_message", "{actor} unleashes a breath of {element} energy!\n"
            ),
            damage_message=data.get(
                "damage_message", "{target} takes {damage} damage from the breath weapon.\n"
            ),
            no_effect_message=data.get(
                "no_effect_message", "The breath weapon has no effect on {target}.\n"
            ),
        )

    @staticmethod
    def _create_nightmare_fuel(data: dict) -> NightmareFuelEffect:
        return NightmareFuelEffect(
            crit_chance=data.get("crit_chance", 0.5),
            damage_message=data.get(
                "damage_message", "{actor} invades {target}'s dreams, dealing {damage} damage"
            ),
            fail_message=data.get("fail_message", "{target} resists the spell.\n"),
            no_sleep_message=data.get("no_sleep_message", "The spell does nothing.\n"),
        )

    @staticmethod
    def _create_widows_wail(data: dict) -> WidowsWailEffect:
        return WidowsWailEffect(
            multiplier=data.get("multiplier", 20),
            max_damage=data.get("max_damage", 200),
            self_message=data.get(
                "self_message", "Anguish overwhelms {name}, taking {damage} damage.\n"
            ),
            target_message=data.get(
                "target_message", "Anguish overwhelms {name}, taking {damage} damage.\n"
            ),
        )

    @staticmethod
    def _create_goblin_punch(data: dict) -> GoblinPunchEffect:
        return GoblinPunchEffect(
            max_punches=data.get("max_punches", 5),
            hit_message=data.get("hit_message", "{actor} punches {target} for {damage} damage.\n"),
            miss_message=data.get("miss_message", "{actor} punches air, missing {target}.\n"),
        )

    @staticmethod
    def _create_hex(data: dict) -> HexEffect:
        return HexEffect(
            duration=data.get("duration", 3),
            announce_message=data.get("announce_message", "{caster} curses {target} with a hex.\n"),
            poison_message=data.get("poison_message", "{target} is poisoned.\n"),
            blind_message=data.get("blind_message", "{target} is blinded.\n"),
            silence_message=data.get("silence_message", "{target} is silenced.\n"),
            no_effect_message=data.get("no_effect_message", "The hex has no effect.\n"),
        )

    @staticmethod
    def _create_vulcanize(data: dict) -> VulcanizeEffect:
        return VulcanizeEffect(
            health_fraction=data.get("health_fraction", 0.1),
            buff_duration=data.get("buff_duration", 5),
            buff_lo_divisor=data.get("buff_lo_divisor", 4),
            buff_hi_divisor=data.get("buff_hi_divisor", 2),
            damage_message=data.get(
                "damage_message", "{target} takes {damage} damage from the flames.\n"
            ),
            heal_message=data.get(
                "heal_message", "{target} is healed by the flames for {damage} hit points.\n"
            ),
            buff_message=data.get("buff_message", "{target} is hardened by the flames.\n"),
        )

    @staticmethod
    def _create_holy_followup(data: dict) -> HolyFollowupEffect:
        return HolyFollowupEffect(
            resist_type=data.get("resist_type", "Holy"),
            damage_message=data.get(
                "damage_message", "{actor} smites {target} for {damage} hit points.\n"
            ),
            ineffective_message=data.get(
                "ineffective_message", "{name} was ineffective and does no damage.\n"
            ),
            absorb_message=data.get(
                "absorb_message", "{target} absorbs {subtyp} and is healed for {heal} health.\n"
            ),
            con_save_message=data.get(
                "con_save_message",
                "{target} shrugs off the {name} and only receives half of the damage.\n",
            ),
        )

    @staticmethod
    def _create_turn_undead(data: dict) -> TurnUndeadEffect:
        return TurnUndeadEffect(
            luck_factor=data.get("luck_factor", 6),
            kill_message=data.get(
                "kill_message", "The {target} has been rebuked, destroying the undead monster.\n"
            ),
            no_undead_message=data.get("no_undead_message", "The spell does nothing.\n"),
            damage_message=data.get(
                "damage_message", "{actor} damages {target} for {damage} hit points"
            ),
        )
