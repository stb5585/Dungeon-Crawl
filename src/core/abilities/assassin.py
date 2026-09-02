"""Assassin abilities and toxin crafting actions."""

from __future__ import annotations

import random
from typing import Any

from .base import Skill


class _AssassinPassive(Skill):
    def __init__(self, name: str, description: str):
        super().__init__(name, f"Passive: {description}")
        self.passive = True
        self.subtyp = "Passive"


class TwistTheKnife(_AssassinPassive):
    def __init__(self):
        super().__init__("Twist the Knife", "A successful Kidney Punch stun triggers Backstab.")


class OffHandExcellence(_AssassinPassive):
    def __init__(self):
        super().__init__("OffHand Excellence", "Reduces the damage penalty for off-hand attacks.")


class ForGoodMeasure(_AssassinPassive):
    def __init__(self):
        super().__init__("For Good Measure", "A successful Disarm is followed by an off-hand attack.")


class Cutthroat(_AssassinPassive):
    def __init__(self):
        super().__init__("Cutthroat", "Critical Backstab attacks have a chance to kill instantly.")


class Surprise(_AssassinPassive):
    def __init__(self):
        super().__init__(
            "Surprise!",
            "While Obscuration is active, an initiative-winning opening attack gains accuracy, "
            "critical chance, and 50% experience if it kills.",
        )


class MainGauche(_AssassinPassive):
    def __init__(self):
        super().__init__("Main Gauche", "Daggers and Ninja blades in the off hand improve Parry.")


class LiveAndLearn(_AssassinPassive):
    def __init__(self):
        super().__init__("Live and Learn", "Critical hits taken can increase dodge, stacking three times.")


class ApplyToxin(Skill):
    exploration_cast = True

    def __init__(self):
        super().__init__("Apply Toxin", "Apply an available toxin to an equipped dagger.")
        self.combat = False
        self.subtyp = "Utility"

    def cast_out(self, game_or_user: Any) -> str:
        from ..classes import footpad

        user = getattr(game_or_user, "player_char", game_or_user)
        return footpad.apply_toxin(user)

    def use(self, user: Any, target: Any = None, **kwargs: Any):
        del target, kwargs
        result = self._reset_result(actor=user)
        result.message = self.cast_out(user)
        return result


class MakeToxin(Skill):
    exploration_cast = True

    def __init__(self):
        super().__init__("Make Toxin", "Craft an available venom or Deathcap into its matching toxin.")
        self.combat = False
        self.subtyp = "Utility"

    def cast_out(self, game_or_user: Any) -> str:
        from ..classes import footpad

        user = getattr(game_or_user, "player_char", game_or_user)
        return footpad.make_toxin(user)

    def use(self, user: Any, target: Any = None, **kwargs: Any):
        del target, kwargs
        result = self._reset_result(actor=user)
        result.message = self.cast_out(user)
        return result


class ResistDeath(Skill):
    exploration_cast = True

    def __init__(self):
        super().__init__("Resist Death", "Increase resistance to Death magic for a duration.")
        self.combat = False
        self.subtyp = "Enhance"
        self.cost = 15

    def cast_out(self, game_or_user: Any) -> str:
        user = getattr(game_or_user, "player_char", game_or_user)
        user.resist_death_steps = 50
        return f"{user.name} steels themselves against Death magic.\n"

    def use(self, user: Any, target: Any = None, **kwargs: Any):
        del target, kwargs
        result = self._reset_result(actor=user)
        result.message = self.cast_out(user)
        return result


class Distract(Skill):
    def __init__(self):
        super().__init__(
            "Distract",
            "Create a diversion that costs the target two turns; attacking restores its focus.",
        )
        self.cost = 8
        self.subtyp = "Control"

    def use(self, user: Any, target: Any = None, **kwargs: Any):
        del kwargs
        result = self._reset_result(actor=user, target=target)
        if target is None:
            result.message = "Distract needs a target.\n"
        elif user.mana.current < self.cost:
            result.message = f"{user.name} does not have enough mana.\n"
        else:
            user.mana.current -= self.cost
            target._distracted_turns = 2
            result.message = f"{target.name} loses focus for two turns.\n"
        return result


class Disembowel(Skill):
    def __init__(self):
        super().__init__("Disembowel", "Slash with both weapons and open a bleeding wound.", weapon=True)
        self.cost = 12
        self.subtyp = "Offensive"

    def use(self, user: Any, target: Any = None, **kwargs: Any):
        del kwargs
        result = self._reset_result(actor=user, target=target)
        offhand = getattr(user, "equipment", {}).get("OffHand")
        if target is None or getattr(offhand, "typ", None) != "Weapon":
            result.message = "Disembowel requires a target and two weapons.\n"
            return result
        if user.mana.current < self.cost:
            result.message = f"{user.name} does not have enough mana.\n"
            return result
        user.mana.current -= self.cost
        before = int(target.health.current)
        message, hit, crit = user.weapon_damage(target, attack_slots=("Weapon", "OffHand"))
        if hit and target.is_alive() and "Bleed" in target.physical_effects:
            bleed = target.physical_effects["Bleed"]
            bleed.active = True
            bleed.duration = max(int(bleed.duration or 0), 4)
            bleed.extra = max(int(bleed.extra or 0), max(1, (before - target.health.current) // 8))
            message += f"{target.name} is disemboweled and bleeding.\n"
        result.hit, result.crit = hit, crit
        result.damage = max(0, before - int(target.health.current))
        result.message = message
        return result


class HiddenBlade(Skill):
    def __init__(self):
        super().__init__("Hidden Blade", "Attack normally, then follow with a concealed throwing dagger.", weapon=True)
        self.cost = 8
        self.subtyp = "Offensive"

    def use(self, user: Any, target: Any = None, **kwargs: Any):
        del kwargs
        from ..classes import footpad

        result = self._reset_result(actor=user, target=target)
        if target is None:
            result.message = "Hidden Blade needs a target.\n"
            return result
        ammunition = footpad.throwing_dagger_pack(user)
        if ammunition is None:
            result.message = "Hidden Blade requires Throwing Daggers.\n"
            return result
        if user.mana.current < self.cost:
            result.message = f"{user.name} does not have enough mana.\n"
            return result
        user.mana.current -= self.cost
        before = int(target.health.current)
        message, hit, crit = user.weapon_damage(target, use_offhand=False)
        if target.is_alive():
            thrown = max(1, int(user.check_mod("attack", enemy=target) * 0.65))
            thrown = max(1, int(thrown * (1 - target.check_mod("resist", typ="Physical"))))
            target.health.current -= thrown
            message += f"{user.name}'s hidden dagger strikes for {thrown} damage.\n"
            hit = True
        message += footpad.spend_throwing_dagger(user, ammunition, retrieve=random.random() < 0.35)
        result.hit, result.crit = hit, crit
        result.damage = max(0, before - int(target.health.current))
        result.message = message
        return result
