"""Active spirit and omen techniques for Shaman progression."""

from __future__ import annotations

from typing import Any

from ..combat.targeting import TargetScope
from .base import Class, Skill


def _spend_mana(user: Any, cost: int, action: str) -> str:
    if int(user.mana.current) < cost:
        return f"{user.name} does not have enough mana for {action}.\n"
    user.mana.current -= cost
    return ""


def _weapon_hit(result: Any, user: Any, target: Any, modifier: float) -> None:
    before = int(target.health.current)
    message, hit, critical = user.weapon_damage(
        target,
        dmg_mod=modifier,
        use_offhand=False,
    )
    result.hit = hit
    result.crit = critical if critical > 1 else None
    result.damage = max(0, before - int(target.health.current))
    result.message += message


class SpiritAnimal(Class):
    """Call a chosen undead animal spirit for a temporary personal blessing."""

    ANIMALS = ("Bear", "Wolf", "Owl", "Panther", "Eagle", "Turtle", "Toad", "Snake")

    def __init__(self) -> None:
        super().__init__(
            "Spirit Animal",
            "Call your chosen undead animal spirit for a four-turn combat blessing.",
        )
        self.cost = 7
        self.target_scope = TargetScope.SELF

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        del target
        result = super().use(user, user, **kwargs)
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        animal = str(getattr(user, "spirit_animal", "Bear"))
        if animal not in self.ANIMALS:
            animal = "Bear"
        stat, amount = {
            "Bear": ("Attack", 18),
            "Wolf": ("Speed", 18),
            "Owl": ("Magic", 18),
            "Panther": ("Attack", 15),
            "Eagle": ("Accuracy", 15),
            "Turtle": ("Defense", 18),
            "Toad": ("Magic Defense", 18),
            "Snake": ("Critical", 12),
        }[animal]
        effect = user.stat_effects[stat]
        effect.active = True
        from ..classes import nature_totems

        duration = 5 if nature_totems.has_nature_talent(user, "shaman.guardian-spirit") else 4
        effect.duration = max(int(effect.duration or 0), duration)
        effect.extra = max(int(effect.extra or 0), amount)
        effect.source = self.name
        result.hit = True
        result.effects_applied["Stat"].append(f"{stat} Buff")
        result.message = f"{user.name}'s {animal} spirit grants {amount} {stat}.\n"
        return result


class ResonantWard(Class):
    """Turn stored Totem Resonance into a short defensive ward."""

    resource_type = "Totem Resonance"

    def __init__(self) -> None:
        super().__init__(
            "Resonant Ward",
            "Spend all Totem Resonance to raise Defense and Magic Defense for three turns.",
        )
        self.cost = 6
        self.target_scope = TargetScope.SELF

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        del target
        result = super().use(user, user, **kwargs)
        from ..classes import promotion_kits

        resonance = promotion_kits.totem_resonance(user)
        if resonance <= 0:
            result.message = "Resonant Ward requires Totem Resonance.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        user.magic_effects["Totem"].extra["resonance"] = 0
        amount = 6 * resonance
        for stat in ("Defense", "Magic Defense"):
            effect = user.stat_effects[stat]
            effect.active = True
            effect.duration = max(int(effect.duration or 0), 3)
            effect.extra = max(int(effect.extra or 0), amount)
            effect.source = self.name
            result.effects_applied["Stat"].append(f"{stat} Buff")
        result.hit = True
        result.message = f"{user.name} shapes {resonance} Resonance into a +{amount} ward.\n"
        return result


class SpiritClaw(Skill):
    """Make a weapon strike reinforced by the active animal spirit."""

    def __init__(self) -> None:
        super().__init__("Spirit Claw", "Strike for 115% weapon damage; Spirit Animal raises it to 135%.", weapon=True)
        self.cost = 7
        self.subtyp = "Offensive"

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Spirit Claw needs a target.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        spirit_active = any(
            effect.active and effect.source == "Spirit Animal"
            for effect in user.stat_effects.values()
        )
        _weapon_hit(result, user, target, 1.35 if spirit_active else 1.15)
        return result


class SpiritMend(Class):
    """Ask the bound spirit to restore the Shaman's health."""

    def __init__(self) -> None:
        super().__init__("Spirit Mend", "Restore health, with stronger healing while Spirit Animal is active.")
        self.cost = 9
        self.target_scope = TargetScope.SELF

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        del target
        result = super().use(user, user, **kwargs)
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        spirit_active = any(
            effect.active and effect.source == "Spirit Animal"
            for effect in user.stat_effects.values()
        )
        amount = max(1, int(user.check_mod("magic") * (1.0 if spirit_active else 0.7)))
        before = int(user.health.current)
        user.health.current = min(int(user.health.max), before + amount)
        result.healing = int(user.health.current) - before
        result.hit = result.healing > 0
        result.message = f"{user.name}'s spirit restores {result.healing} health.\n"
        return result


class DreadfulSign(Class):
    """Place one Bad Omens dread stack on an enemy deliberately."""

    def __init__(self) -> None:
        super().__init__("Dreadful Sign", "Place one stack of dread on an enemy; three stacks Stun it.")
        self.cost = 8

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Dreadful Sign needs a target.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        from ..classes import nature_totems

        result.message = nature_totems.add_dread(user, target, "Dreadful Sign")
        result.hit = True
        result.effects_applied["Class"].append("Dread")
        return result


class OmenStrike(Skill):
    """Attack a dreaded enemy and hasten the omen on a critical hit."""

    def __init__(self) -> None:
        super().__init__("Omen Strike", "Strike for 110% weapon damage; critical hits add dread.", weapon=True)
        self.cost = 8
        self.subtyp = "Offensive"

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Omen Strike needs a target.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        _weapon_hit(result, user, target, 1.10)
        if result.hit and result.crit:
            from ..classes import nature_totems

            result.message += nature_totems.add_dread(user, target, "Omen Strike critical")
        return result


class SoulRend(Skill):
    """Follow Soul Drain with a physical strike that respects its nonlethal identity."""

    def __init__(self) -> None:
        super().__init__("Soul Rend", "Strike for 125% weapon damage and gain Resonance against a drained foe.", weapon=True)
        self.cost = 9
        self.subtyp = "Offensive"

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Soul Rend needs a target.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        _weapon_hit(result, user, target, 1.25)
        if result.hit:
            from ..classes import promotion_kits

            result.message += promotion_kits.gain_totem_resonance(user, "Soul Rend")
        return result


class AncestralAegis(ResonantWard):
    """Soulcatcher upgrade that also heals while shaping Resonance."""

    def __init__(self) -> None:
        super().__init__()
        self.name = "Ancestral Aegis"
        self.description = "Spend all Totem Resonance for a ward and restore 5% maximum health per stack."
        self.result.action = self.name

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        from ..classes import promotion_kits

        resonance = promotion_kits.totem_resonance(user)
        before = int(user.health.current)
        result = super().use(user, target, **kwargs)
        if result.hit and resonance:
            user.health.current = min(
                int(user.health.max),
                int(user.health.current) + int(user.health.max * 0.05 * resonance),
            )
            result.healing = int(user.health.current) - before
            result.message += f"The ancestors restore {result.healing} health.\n"
        return result


class Soulstorm(Class):
    """Spend Resonance to combine Soul Drain with a forced Soul Totem pulse."""

    resource_type = "Totem Resonance"

    def __init__(self) -> None:
        super().__init__("Soulstorm", "Spend all Resonance to force a strengthened Soul Totem pulse.")
        self.cost = 12

    def use(self, user: Any, target: Any | None = None, **kwargs: Any):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Soulstorm needs a target.\n"
            return result
        from ..classes import nature_totems, promotion_kits

        if nature_totems.active_totem_aspect(user) != "Soul":
            result.message = "Soulstorm requires an active Soul Totem.\n"
            return result
        resonance = promotion_kits.totem_resonance(user)
        if resonance <= 0:
            result.message = "Soulstorm requires Totem Resonance.\n"
            return result
        spell = user.spellbook.get("Spells", {}).get("Soul Drain")
        if spell is None:
            result.message = "Soulstorm requires Soul Drain.\n"
            return result
        result.message = _spend_mana(user, self.cost, self.name)
        if result.message:
            return result
        user.magic_effects["Totem"].extra["resonance"] = 0
        sentinel, prior = nature_totems._set_temp_attr(
            user,
            "_totem_pulse_potency",
            0.65 + (0.10 * resonance),
        )
        try:
            before = int(target.health.current)
            result.message += str(spell.cast(user, target=target, special=True))
            result.damage = max(0, before - int(target.health.current))
            result.hit = result.damage > 0
        finally:
            nature_totems._restore_temp_attr(user, "_totem_pulse_potency", sentinel, prior)
        return result
