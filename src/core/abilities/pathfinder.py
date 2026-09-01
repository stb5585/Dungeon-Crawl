"""Authored abilities for the Pathfinder base-class tree."""

from __future__ import annotations

import random
from typing import Any

from ..combat.targeting import TargetScope
from .base import Class, Skill, Spell


class _PathfinderPassive(Class):
    """Small passive wrapper for Pathfinder-tree mechanics."""

    def __init__(self, name: str, description: str) -> None:
        super().__init__(name=name, description=description)
        self.passive = True


class RayOfMoonlight(Spell):
    """Deal Nature damage and force a shapeshifter into its original form."""

    damage_types = ("Nature", "Holy")

    def __init__(self) -> None:
        super().__init__(
            "Ray of Moonlight",
            "Deal Nature damage and suppress an enemy's shapeshifting for this combat.",
            school="Nature",
        )
        self.cost = 8
        self.subtyp = "Nature"

    def cast(self, user, target=None, **kwargs):
        from ..classes import pathfinder

        result = super().cast(user, target, **kwargs)
        if target is None:
            result.message = "Ray of Moonlight needs a target.\n"
            return result
        if user.mana.current < self.cost:
            result.message = f"{user.name} does not have enough mana.\n"
            return result
        user.mana.current -= self.cost
        message, damage = pathfinder.spell_damage(
            user,
            target,
            self,
            damage_type="Nature",
            damage_modifier=1.20,
            rng=kwargs.get("rng"),
        )
        result.damage = damage
        result.hit = damage > 0
        if damage > 0:
            message += pathfinder.suppress_shapeshifting(target)
        result.message = message
        return result


class NullifyPoison(Spell):
    """Remove poison from one target."""

    damage_types = ("Nature",)

    def __init__(self) -> None:
        super().__init__("Nullify Poison", "Cure the target's poison effect.", school="Nature")
        self.cost = 6
        self.subtyp = "Support"

    def cast(self, user, target=None, **kwargs):
        target = target or user
        result = super().cast(user, target, **kwargs)
        if user.mana.current < self.cost:
            result.message = f"{user.name} does not have enough mana.\n"
            return result
        user.mana.current -= self.cost
        poison = target.status_effects["Poison"]
        was_poisoned = poison.active
        poison.active = False
        poison.duration = 0
        poison.extra = 0
        poison.source = ""
        result.message = (
            f"{target.name} is cured of poison.\n"
            if was_poisoned
            else f"{target.name} is not poisoned.\n"
        )
        return result


class ThornyVine(Spell):
    """Ensnare a target in a damaging living vine."""

    damage_types = ("Nature", "Earth")

    def __init__(self) -> None:
        super().__init__(
            "Thorny Vine",
            "Call forth a vine that deals Nature damage when escape attempts fail.",
            school="Nature",
        )
        self.cost = 9
        self.subtyp = "Nature"

    def cast(self, user, target=None, **kwargs):
        from ..classes import pathfinder

        result = super().cast(user, target, **kwargs)
        if target is None:
            result.message = "Thorny Vine needs a target.\n"
            return result
        if user.mana.current < self.cost:
            result.message = f"{user.name} does not have enough mana.\n"
            return result
        user.mana.current -= self.cost
        result.message = pathfinder.ensnare_with_vine(user, target)
        result.effects_applied["Physical"].append("Thorny Vine")
        return result


class PoisonStrike(Spell):
    """Partially transform and deliver a poisonous bite."""

    damage_types = ("Nature", "Poison", "Physical")

    def __init__(self) -> None:
        super().__init__(
            "Poison Strike",
            "Partially transform, biting the target for physical and poison damage.",
            school="Nature",
        )
        self.cost = 12
        self.subtyp = "Poison"

    def cast(self, user, target=None, **kwargs):
        from ..classes import pathfinder

        result = super().cast(user, target, **kwargs)
        if target is None:
            result.message = "Poison Strike needs a target.\n"
            return result
        if user.mana.current < self.cost:
            result.message = f"{user.name} does not have enough mana.\n"
            return result
        user.mana.current -= self.cost
        message, damage = pathfinder.poison_strike(
            user,
            target,
            self,
            rng=kwargs.get("rng"),
        )
        result.damage = damage
        result.hit = damage > 0
        result.message = message
        return result


class RazorTalons(_PathfinderPassive):
    def __init__(self) -> None:
        super().__init__(
            "Razor Talons",
            "Passive: Increase melee damage and Bleed damage caused by melee attacks.",
        )


class CallAnimal(Spell):
    """Call a local transient animal companion in or out of combat."""

    exploration_cast = True
    damage_types = ("Nature",)

    def __init__(self) -> None:
        super().__init__(
            "Call Animal",
            "Call a local animal companion to aid in combat for a time.",
            school="Nature",
        )
        self.cost = 10
        self.subtyp = "Calling"
        self.target_scope = TargetScope.NONE

    def cast_out(self, game_or_user):
        from ..classes import pathfinder

        user = getattr(game_or_user, "player_char", game_or_user)
        return pathfinder.call_animal(user, self.cost)

    def cast(self, user, target=None, **kwargs):
        del target, kwargs
        return self.cast_out(user)


class CreatureComforts(Spell):
    """Pacify animals during exploration or remove them from combat."""

    exploration_cast = True
    damage_types = ("Nature",)

    def __init__(self) -> None:
        super().__init__(
            "Creature Comforts",
            "Pacify nearby animals, reducing encounters or urging them from combat.",
            school="Nature",
        )
        self.cost = 10
        self.subtyp = "Support"
        self.target_scope = TargetScope.NONE

    def cast_out(self, game_or_user):
        from ..classes import pathfinder

        user = getattr(game_or_user, "player_char", game_or_user)
        return pathfinder.activate_creature_comforts(user, self.cost)

    def cast(self, user, target=None, **kwargs):
        from ..classes import pathfinder

        engine = kwargs.get("battle_engine")
        if engine is None:
            return self.cast_out(user)
        return pathfinder.pacify_combat_animals(user, engine, self.cost)


class CautiousAssault(_PathfinderPassive):
    def __init__(self) -> None:
        super().__init__(
            "Cautious Assault",
            "Passive: Increase dodge chance against counterattacks.",
        )


class UnnaturalPurge(Skill):
    """Strike unnatural enemies for additional damage."""

    def __init__(self) -> None:
        super().__init__(
            "Unnatural Purge",
            "Strike an enemy, dealing 50% more damage to unnatural creatures.",
            weapon=True,
        )
        self.cost = 10
        self.subtyp = "Offensive"

    def use(self, user, target=None, **kwargs):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Unnatural Purge needs a target.\n"
            return result
        if user.mana.current < self.cost:
            result.message = f"{user.name} does not have enough mana.\n"
            return result
        user.mana.current -= self.cost
        unnatural = str(getattr(target, "enemy_typ", "")) in {
            "Slime", "Monster", "Undead", "Aberration",
        }
        message, hit, crit = user.weapon_damage(
            target,
            dmg_mod=1.5 if unnatural else 1.0,
            use_offhand=False,
        )
        result.hit = hit
        result.crit = crit if crit > 1 else None
        result.damage = int(getattr(user, "_last_weapon_primary_damage", 0) or 0)
        if unnatural and hit:
            message += "Unnatural Purge exploits the creature's unnatural form.\n"
        result.message = message
        return result


class BounceBack(_PathfinderPassive):
    def __init__(self) -> None:
        super().__init__("Bounce Back", "Passive: Recover from Prone more quickly.")


class SpiritStrike(Skill):
    """Attack and add spirit damage when the user has higher Wisdom."""

    def __init__(self) -> None:
        super().__init__(
            "Spirit Strike",
            "Attack and deal additional spirit damage when your Wisdom is higher.",
            weapon=True,
        )
        self.cost = 7
        self.subtyp = "Offensive"

    def use(self, user, target=None, **kwargs):
        from ..classes import pathfinder

        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Spirit Strike needs a target.\n"
            return result
        if user.mana.current < self.cost:
            result.message = f"{user.name} does not have enough mana.\n"
            return result
        user.mana.current -= self.cost
        message, damage = pathfinder.spirit_strike(user, target)
        result.damage = damage
        result.hit = damage > 0
        result.message = message
        return result


class Conversion(_PathfinderPassive):
    def __init__(self) -> None:
        super().__init__(
            "Conversion",
            "Passive: Elemental spell damage empowers the next melee critical strike.",
        )


class VerySuperstitious(_PathfinderPassive):
    def __init__(self) -> None:
        super().__init__(
            "Very Superstitious",
            "Passive: Negative status effects may create a matching-duration damage barrier.",
        )


class PrimalTrance(Skill):
    """Charge, then automatically cast increasingly powerful elemental spells."""

    def __init__(self) -> None:
        super().__init__(
            "Primal Trance",
            "Charge for one turn, then automatically cast increasingly powerful elemental spells.",
        )
        self.cost = 18
        self.subtyp = "Enhance"
        self.charging = False
        self.charge_turns = 0
        self.charge_target = None
        self.trance_casts = 0

    def get_charge_time(self) -> int:
        return 1

    def cancel_charge(self, user) -> str:
        from ..classes import pathfinder

        self.charging = False
        self.charge_turns = 0
        self.charge_target = None
        self.trance_casts = 0
        pathfinder.end_primal_trance(user)
        return f"{user.name}'s Primal Trance ends.\n"

    def use(self, user, target=None, **kwargs):
        from ..classes import pathfinder

        if not self.charging:
            if user.mana.current < self.cost:
                return f"{user.name} does not have enough mana.\n"
            user.mana.current -= self.cost
            self.charging = True
            self.charge_turns = 1
            self.charge_target = target
            self.trance_casts = 0
            pathfinder.begin_primal_trance(user)
            return f"{user.name} sinks into a Primal Trance and begins charging.\n"
        self.charge_turns -= 1
        if self.charge_turns > 0:
            return f"{user.name} continues concentrating.\n"
        self.trance_casts += 1
        message = pathfinder.primal_trance_cast(
            user,
            self.charge_target or target,
            self.trance_casts,
            rng=kwargs.get("rng"),
        )
        if self.trance_casts >= 4 or target is None or not target.is_alive():
            return message + self.cancel_charge(user)
        self.charge_turns = 1
        self.charging = True
        return message


class FundamentalHarmony(_PathfinderPassive):
    def __init__(self) -> None:
        super().__init__(
            "Fundamental Harmony",
            "Passive: Increase damage from offensive Elemental spells.",
        )


class IntensifyElements(_PathfinderPassive):
    def __init__(self) -> None:
        super().__init__(
            "Intensify Elements",
            "Passive: Taking elemental damage empowers the next spell of that school.",
        )


class Chronology(_PathfinderPassive):
    def __init__(self) -> None:
        super().__init__(
            "Chronology",
            "Passive: Add the Intelligence modifier to initiative rolls.",
        )


class Geomancy(Spell):
    """Read useful combat information or point toward an unexplored location."""

    exploration_cast = True
    damage_types = ("Earth", "Nature")

    def __init__(self) -> None:
        super().__init__(
            "Geomancy",
            "Ask the earth for useful quest information or direction.",
            school="Earth",
        )
        self.cost = 8
        self.subtyp = "Divination"
        self.target_scope = TargetScope.NONE

    def cast(self, user, target=None, **kwargs):
        from ..classes import pathfinder

        if user.mana.current < self.cost:
            return f"{user.name} does not have enough mana.\n"
        user.mana.current -= self.cost
        return pathfinder.geomancy_combat(user, target)

    def cast_out(self, game_or_user):
        from ..classes import pathfinder

        user = getattr(game_or_user, "player_char", game_or_user)
        if user.mana.current < self.cost:
            return f"{user.name} does not have enough mana.\n"
        user.mana.current -= self.cost
        return pathfinder.geomancy_exploration(user)


class ControlZ(Spell):
    """Restore the player state from immediately before the last damaging action."""

    def __init__(self) -> None:
        super().__init__(
            "Control Z",
            "Undo the last damaging action against you as if it never happened.",
            school="Time",
        )
        self.cost = 20
        self.subtyp = "Time"
        self.target_scope = TargetScope.NONE

    def cast(self, user, target=None, **kwargs):
        from ..classes import pathfinder

        del target
        if user.mana.current < self.cost:
            return f"{user.name} does not have enough mana.\n"
        message = pathfinder.control_z(user)
        if message.startswith("Time rewinds"):
            user.mana.current = max(0, user.mana.current - self.cost)
        return message
