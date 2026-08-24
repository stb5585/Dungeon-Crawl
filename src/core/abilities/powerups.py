"""Power-up and trained passive abilities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..combat.combat_result import CombatResult
from .base import Ability, Class, PowerUp, _load_yaml_ability

if TYPE_CHECKING:
    from typing import Any

    from ..character import Character


class BloodRage(PowerUp):
    """
    Berserker Power Up
    attack increases as health decreases; if below 30% health, bonus to defense
    """

    def __init__(self):
        super().__init__(
            name="Blood Rage",
            description="A berserker's rage knows no bounds, their power growing as "
            "their blood is spilled. Attack power increases as health "
            "decreases and gains an increase to defense below 30%.",
        )
        self.passive = True


class ArsenalMastery(PowerUp):
    """Skill — data-driven (arsenal_mastery.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("arsenal_mastery.yaml", cls_name="ArsenalMastery")


class DivineAegis(PowerUp):
    """Skill — data-driven (divine_aegis.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("divine_aegis.yaml", cls_name="DivineAegis")


class DraconicOnslaught(PowerUp):
    """
    Dragoon Power Up
    attack and defense double for each successive hit; a miss resets this buff
    """

    def __init__(self):
        super().__init__(
            name="Draconic Onslaught",
            description="The power up unleashed the dragon within, a power that "
            "continues to grow. With each successive hit, your attack "
            "and defense increase. A miss will reset this buff.",
        )
        self.passive = True


class ShieldMastery(PowerUp):
    """
    Stalwart Defender Power Up
    increase chance to block melee and spells, with a chance to reflect
    """

    def __init__(self):
        super().__init__(
            name="Shield Mastery",
            description="The Stalwart Defender is so skilled with a shield that they gain "
            "a bonus chance to block melee and spells, with a chance to reflect the spell back.",
        )
        self.passive = True


class SpellMastery(PowerUp):
    """
    Wizard Power Up
    automatically triggers when no spells can be cast due to low mana; all spells
        become free for a short time and mana regens based on damage dealt
    """

    def __init__(self):
        super().__init__(
            name="Spell Mastery",
            description="The Wizard is so good at spell casting that even running out"
            " of mana won't stop them. This ability automatically triggers"
            " when no spells can be cast due to low mana, making spells "
            "free for a time. While active mana is regenerated based on "
            "damage dealt.",
        )
        self.passive = True


class VeilShadows(PowerUp):
    """
    Shadowcaster Power Up
    become one with the darkness, making the player invisible to most enemies and making them harder to hit; increases
        damage of initial attack if first
    """

    def __init__(self):
        super().__init__(
            name="Veil of Shadows",
            description="Darkness becomes light and light falls to darkness, "
            "concealing the Shadowcaster from all but the most keen "
            "eyes. The player gains invisibility and a bonus to damage"
            " at the beginning of battle if they have initiative.",
        )
        self.passive = True


class Alacrity(PowerUp):
    """Passive speed increase while the caster is invisible."""

    def __init__(self):
        super().__init__(
            name="Alacrity",
            description="While invisible, increase Speed by 25%.",
        )
        self.passive = True


class _ContractModifier(PowerUp):
    """Passive modifier displayed with Call Contract instead of Specials."""

    def __init__(self, name: str, description: str):
        super().__init__(name=name, description=description)
        self.passive = True
        self.presentation_modifier = True
        self.modifies = ("Call Contract",)


class FinePrint(_ContractModifier):
    def __init__(self):
        super().__init__("Fine Print", "Reduce fiend-contract gold costs by 20%.")


class ControlledCorruption(_ContractModifier):
    def __init__(self):
        super().__init__(
            "Controlled Corruption",
            "Reduce bargain taint gained from fiend contracts by 25%.",
        )


class Patronage(_ContractModifier):
    def __init__(self):
        super().__init__(
            "Patronage",
            "Successful fiend contracts generate additional patron favor.",
        )


class AbyssalAuthority(_ContractModifier):
    def __init__(self):
        super().__init__(
            "Abyssal Authority",
            "Increase the strength of fiend-contract effects by 20%.",
        )


class AbyssalCovenant(PowerUp):
    """Skill — data-driven (abyssal_covenant.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("abyssal_covenant.yaml", cls_name="AbyssalCovenant")


class ArcaneBlast(PowerUp):
    """Data-driven (arcane_blast.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("arcane_blast.yaml", cls_name="ArcaneBlast")


# Passive ability for Thaumaturgist
class EternalConduit(Ability):
    """
    Eternal Conduit (Passive): The Thaumaturgist's bond with their Xenids is so strong that they gain a portion of all
    healing and buffs their Xenids receive, and their Xenids gain a portion of all healing and buffs the Thaumaturgist
    receives.
    """
    def __init__(self):
        super().__init__(
            name="Eternal Conduit",
            description="The Thaumaturgist's bond with their Xenids is so strong that "
            "they gain a portion of all healing and buffs their Xenids receive, "
            "and their Xenids gain a portion of all healing and buffs the Thaumaturgist"
            " receives.",
            passive=True,
            typ="Skill",
            subtyp="Power Up"
        )

    def special_effect(self, user: Character, *args: Any, **kwargs: Any) -> CombatResult:
        result = self._reset_result(actor=user)
        result.extra["effect"] = "shared_healing_and_buffs"
        return result


class StrokeLuck(PowerUp):
    """
    Rogue Power Up
    the Rogue is incredibly lucky, gaining bonuses to all luck-based checks, as well as dodge and critical chance
    """

    def __init__(self):
        super().__init__(
            name="Stroke of Luck",
            description="The master of tricks and subterfuge also has Lady Luck on "
            "its side, gaining a bonus to all luck-based rolls.",
        )
        self.passive = True


class EyesUnseen(PowerUp):
    """
    Seeker Power Up
    gain increased awareness of battle situations, increasing critical chance as well as chance to dodge/parry attacks
    """

    def __init__(self):
        super().__init__(
            name="Eyes of the Unseen",
            description="The Seeker excels at rooting out the evil that hides "
            "in the shadows. Studying these enemies has improved "
            "their own game, improving battle awareness and increasing"
            " both critical and dodge chance.",
        )
        self.passive = True


class BladeFatalities(PowerUp):
    """Skill — data-driven (blade_fatalities.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("blade_fatalities.yaml", cls_name="BladeFatalities")


class TrickstersGambit(PowerUp):
    """Skill — data-driven (tricksters_gambit.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("tricksters_gambit.yaml", cls_name="TrickstersGambit")


class HolyRetribution(PowerUp):
    """Skill — data-driven (holy_retribution.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("holy_retribution.yaml", cls_name="HolyRetribution")


class SacredOverchannel(PowerUp):
    """Skill — data-driven (sacred_overchannel.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("sacred_overchannel.yaml", cls_name="SacredOverchannel")


class GreatGospel(PowerUp):
    """Skill — data-driven (great_gospel.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("great_gospel.yaml", cls_name="GreatGospel")


class DimMak(Class):
    """Dim Mak keeps its legacy weapon skill behavior outside Master Monk."""

    def __init__(self):
        legacy = _load_yaml_ability("dim_mak.yaml", cls_name="DimMak")
        super().__init__(
            name=legacy.name,
            description=legacy.description,
        )
        self.cost = legacy.cost
        self.weapon = legacy.weapon
        self._legacy = legacy

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        if (
            promotion_kits.class_name(user) == "Master Monk"
            and int(promotion_kits.combat_state(user).get("ki", 0) or 0) >= promotion_kits.cap_for(user, "ki")
        ):
            return promotion_kits.dim_mak(user, target)
        return self._legacy.use(user, target, **kwargs)


class MelodyInspiration(PowerUp):
    """
    Melody of Inspiration (Passive): The Troubadour's presence inspires allies and self, granting a small bonus to all stats
    and occasionally removing negative status effects at the start of combat.
    """
    def __init__(self):
        super().__init__(
            name="Melody of Inspiration",
            description="The Troubadour's presence inspires allies and self, granting "
            "a small bonus to all stats and occasionally removing negative status "
            "effects at the start of combat.",
        )
        self.passive = True

    def special_effect(self, user: Character, *args: Any, **kwargs: Any) -> CombatResult:
        result = self._reset_result(actor=user)
        result.extra["effect"] = "stat_bonus_and_status_removal"
        return result


SongInspiration = MelodyInspiration


class PrimalAscendance(PowerUp):
    """
    Primal Ascendance (Passive): The Archdruid becomes a living embodiment of nature.
    """
    def __init__(self):
        super().__init__(
            name="Primal Ascendance",
            description="For several turns, gain bonuses from all Nature Aspects;"
            "increased healing (Growth), increased poison effectiveness (Venom),"
            "increased spell power (Storm), increased defense (Stone).",
        )
        self.passive = True

    def special_effect(self, user: Character, *args: Any, **kwargs: Any) -> CombatResult:
        result = self._reset_result(actor=user)
        return result


class LunarFrenzy(PowerUp):
    """
    Lycan Power Up
    the longer the Lycan is transformed, the further into madness they fall, increasing
          damage and regenerating health on critical hits; if the Lycan stays transformed for longer than 5 turns, they
          will be unable to transform back until after the battle
    """

    def __init__(self):
        super().__init__(
            name="Lunar Frenzy",
            description="Transformation is a powerful ability, achievable as a Druid "
            "but perfected by the Lycan. You gain an increased brutality "
            "while transformed, dealing increasing damage and healing on "
            "critical hits the longer you are changed. This does come at "
            "a cost, as you will reach a point where you can no longer "
            "change back until after combat.",
        )
        self.passive = True


class AstralJudgment(PowerUp):
    """Data-driven (astral_judgment.yaml) - active-sign fate judgment."""
    def __new__(cls):
        return _load_yaml_ability("astral_judgment.yaml", cls_name="AstralJudgment")


class SoulHarvest(PowerUp):
    """
    Soulcatcher Power Up
    each enemy killed of a particular type will improve conbat expertise against that enemy type, improving attack,
        defense, magic, and magic defense
    """

    def __init__(self):
        super().__init__(
            name="Soul Harvest",
            description="The souls of the dead contain traces of its host's power. "
            "The Soulcatcher knows this and uses it to their advantage. "
            "Each enemy killed of a particular type increases the combat "
            "effectiveness against that enemy type.",
        )
        self.passive = True


class PackBond(PowerUp):
    """
    Pack Bond (Passive): The Beast Master and their animal companion(s) share a deep bond, granting increased damage and defense
    when fighting alongside a companion. Occasionally, the companion will intercept attacks or provide a healing effect.
    """
    def __init__(self):
        super().__init__(
            name="Pack Bond",
            description="The Beast Master and their animal companion(s) share a deep "
            "bond, granting increased damage and defense when fighting alongside a "
            "companion. Occasionally, the companion will intercept attacks or provide"
            " a healing effect.",
        )
        self.passive = True

    def special_effect(self, user: Character, *args: Any, **kwargs: Any) -> CombatResult:
        result = self._reset_result(actor=user)
        result.extra["effect"] = "companion_bonus_and_intercept"
        return result
