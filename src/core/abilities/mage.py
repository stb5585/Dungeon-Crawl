"""Bespoke Mage-tree spells and trained passives."""

from __future__ import annotations

import math
import random
from typing import Any

from .base import PowerUp, Spell


class _MagePassive(PowerUp):
    """Small passive wrapper used by authored Mage ability nodes."""

    def __init__(self, name: str, description: str) -> None:
        super().__init__(name, description)
        self.passive = True


class _SchoolEnhancement(_MagePassive):
    """Mage passive presented inside every spell of one school."""

    def __init__(self, name: str, description: str, school: str) -> None:
        super().__init__(name, description)
        self.presentation_modifier = True
        self.modifies_school = school


class FireInside(_SchoolEnhancement):
    def __init__(self) -> None:
        super().__init__(
            "Fire Inside",
            "Fire spells have a 20% chance to grant +25% critical chance to "
            "the next attack. The charge expires after 3 turns and is consumed "
            "by the next attack regardless of its result.",
            "Fire",
        )


class FrozenArmor(_SchoolEnhancement):
    def __init__(self) -> None:
        super().__init__(
            "Frozen Armor",
            "Ice spells have a 20% chance to grant +10 Defense and 25% Ice "
            "resistance for one turn.",
            "Ice",
        )


class Electrified(_SchoolEnhancement):
    def __init__(self) -> None:
        super().__init__(
            "Electrified",
            "Electric spells have a 20% chance to electrify the caster for 3 "
            "turns; successful melee attacks against them trigger an "
            "Intelligence-scaled jolt.",
            "Electric",
        )


class WindCurrents(_SchoolEnhancement):
    def __init__(self) -> None:
        super().__init__(
            "Wind Currents",
            "Wind spells have a 20% chance to grant +3 Speed and +10% melee "
            "accuracy for 3 turns.",
            "Wind",
        )


class Refreshment(_SchoolEnhancement):
    def __init__(self) -> None:
        super().__init__(
            "Refreshment",
            "Water spells have a 20% chance to restore 5% of maximum HP and MP.",
            "Water",
        )


class TerraFirma(_SchoolEnhancement):
    def __init__(self) -> None:
        super().__init__(
            "Terra Firma",
            "Earth spells have a 20% chance to increase melee damage by 50% "
            "for 3 turns.",
            "Earth",
        )


class ClassicalForce(_MagePassive):
    def __init__(self) -> None:
        super().__init__(
            "Classical Force",
            "Specialize School Affinity in elemental magic. Arcane spell "
            "damage, control, barriers, and enhancements operate at 50% potency.",
        )


class ArcaneTradition(_MagePassive):
    def __init__(self) -> None:
        super().__init__(
            "Arcane Tradition",
            "Specialize School Affinity in Arcane magic. Elemental spell "
            "damage operates at 50% potency and Enhancement proc chances are halved.",
        )


class Polymorph(Spell):
    """Temporarily transform a target, with bosses strongly resisting it."""

    BOSS_SUCCESS_CHANCE = 0.10

    def __init__(self) -> None:
        super().__init__(
            "Polymorph",
            "Transform an enemy into a harmless bunny that cannot act for 2 "
            "turns. Bosses resist the transformation 90% of the time.",
            school="Arcane",
        )
        self.cost = 12
        self.subtyp = "Arcane"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del kwargs
        if target is None:
            return "There is no target to polymorph.\n"
        user.mana.current -= self.cost
        from ..enemies.catalog import is_boss_enemy

        if is_boss_enemy(target) and random.random() >= self.BOSS_SUCCESS_CHANCE:
            return f"{target.name} resists the polymorph.\n"
        duration = 2
        try:
            from ..classes import mage_mechanics

            duration = max(1, int(duration * mage_mechanics.spell_potency_multiplier(user, self)))
        except Exception:
            pass
        effect = target.status_effects["Polymorph"]
        effect.active = True
        effect.duration = max(effect.duration, duration)
        effect.source = "Polymorph"
        return f"{target.name} is transformed into a harmless bunny for {duration} turns.\n"


class InflateHealth(Spell):
    def __init__(self) -> None:
        super().__init__(
            "Inflate Health",
            "Grant temporary HP that is consumed before real HP for 3 turns.",
            school="Shadow",
        )
        self.cost = 12
        self.subtyp = "Shadow"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del target, kwargs
        user.mana.current -= self.cost
        amount = max(5, int(user.health.max * 0.25) + int(user.stats.intel))
        user.temporary_health = {"amount": amount, "turns": 3}
        return f"{user.name} gains {amount} temporary HP for 3 turns.\n"


class EnlivenDead(Spell):
    def __init__(self) -> None:
        super().__init__(
            "Enliven Dead",
            "Outside combat, raise an undead version of the last defeated "
            "non-boss enemy after a Charisma/Luck check.",
            school="Shadow",
        )
        self.cost = 18
        self.combat = False
        self.subtyp = "Shadow"

    def cast_out(self, user: Any) -> str:
        snapshot = getattr(user, "last_defeated_enemy", None)
        if not isinstance(snapshot, dict):
            return "No defeated non-boss enemy can answer the rite.\n"
        user.mana.current -= self.cost
        luck = int(user.check_mod("luck", luck_factor=10))
        if random.randint(1, 20) + int(user.stats.charisma) + luck < 18:
            return "The corpse rejects the enlivening rite.\n"
        from ..classes import mage_mechanics

        mage_mechanics.set_transient_companion(
            user,
            name=f"Undead {snapshot['name']}",
            kind="undead",
            source="Enliven Dead",
            damage=max(2, int(snapshot.get("level", 1)) + user.stats.intel // 2),
        )
        return (
            f"Undead {snapshot['name']} will fight beside {user.name} for "
            f"{mage_mechanics.TRANSIENT_SUMMON_STEPS} steps.\n"
        )

    cast = cast_out


class ConjureBlade(Spell):
    def __init__(self) -> None:
        super().__init__(
            "Conjure Blade",
            "Call a level-scaled blade from another dimension; its damage uses "
            "the caster's Intelligence instead of Strength.",
            school="Arcane",
        )
        self.cost = 5
        self.subtyp = "Arcane"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del kwargs
        if target is None:
            return "There is no target for the conjured blade.\n"
        user.mana.current -= self.cost
        level = max(1, int(user.level.level))
        damage = max(1, random.randint(level, level * 2) + int(user.stats.intel))
        critical = False
        try:
            from ..classes import mage_mechanics
            from ..classes import wizard

            critical = (
                mage_mechanics.fire_inside_critical_bonus(user) > random.random()
            )
            mage_mechanics.consume_fire_inside(user)
            critical_multiplier = 2.0 if critical else 1.0
            critical_multiplier = mage_mechanics.arcane_critical_multiplier(
                user,
                critical_multiplier,
            )
            damage = int(
                damage
                * critical_multiplier
                * mage_mechanics.spell_potency_multiplier(user, self)
                * (1 + wizard.affinity_damage_bonus(user, "Arcane"))
            )
        except Exception:
            pass
        _, reduction_message, damage = target.damage_reduction(
            damage,
            user,
            typ="Magic",
        )
        from ..classes import promotion_kits

        damage, shield_message, _fully_absorbed = promotion_kits.absorb_novel_shield(
            target,
            damage,
            source="spell",
        )
        target.health.current -= damage
        user._emit_damage_event(
            target,
            damage,
            damage_type="Arcane",
            source="spell",
            ability_name=self.name,
            is_critical=critical,
        )
        critical_text = " (Critical hit!)" if critical else ""
        return (
            reduction_message
            + shield_message
            + f"A conjured blade strikes {target.name} for {damage} damage"
            f"{critical_text}, then vanishes.\n"
        )


class ConjureAnimal(Spell):
    category = "Animal"

    def __init__(self) -> None:
        super().__init__(
            "Conjure Animal",
            "Outside combat, call a local animal that fights independently for "
            "a short time.",
            school="Arcane",
        )
        self.cost = 12
        self.combat = True
        self.self_target = True
        self.subtyp = "Calling"

    def cast_out(self, user: Any) -> str:
        from ..classes import mage_mechanics

        companion = mage_mechanics.conjure_standard_companion(
            user,
            "Animal",
            source="Conjure Animal",
        )
        if companion is None:
            return "No local animal answers the conjuration.\n"
        user.mana.current -= self.cost
        return (
            f"A {companion['name']} answers the call and will fight beside "
            f"{user.name} for "
            f"{mage_mechanics.TRANSIENT_SUMMON_STEPS} steps.\n"
        )

    def cast(
        self,
        user: Any,
        target: Any | None = None,
        *,
        battle_engine: Any | None = None,
        **kwargs: Any,
    ) -> str:
        del target, kwargs
        class_name = str(getattr(getattr(user, "cls", None), "name", ""))
        if class_name != "Thaumaturgist":
            return self.cast_out(user)
        from .. import companions

        xenid_name = companions.chosen_xenid(user, self.category)
        if not xenid_name:
            choices = " or ".join(companions.XENID_PAIRS[self.category])
            return f"Choose {choices} as the permanent animal Xenid first.\n"
        if battle_engine is None:
            return "Calling a Xenid requires an active battle.\n"
        xenid = user.summons[xenid_name]
        prior_cost = getattr(xenid, "summon_mana_cost", None)
        xenid.summon_mana_cost = 0
        try:
            message, success, _xenid = battle_engine._execute_summon(xenid_name)
        finally:
            xenid.summon_mana_cost = prior_cost
        if success:
            user.mana.current -= self.cost
        return message.replace("summons", "calls")


class ConjureShackles(Spell):
    def __init__(self) -> None:
        super().__init__(
            "Conjure Shackles",
            "Attempt to hold an enemy prone with dimensional shackles for up "
            "to 3 turns. It resists with Dexterity, then attempts to break free "
            "with Strength each turn.",
            school="Arcane",
        )
        self.cost = 15
        self.subtyp = "Arcane"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del kwargs
        if target is None:
            return "There is no target to shackle.\n"
        user.mana.current -= self.cost
        attack = random.randint(user.stats.intel // 2, max(user.stats.intel, 1))
        defense = random.randint(target.stats.dex // 2, max(target.stats.dex, 1))
        if defense >= attack:
            return f"{target.name} evades the conjured shackles.\n"
        target.conjured_shackles = {
            "turns": 3,
            "difficulty": max(1, int(user.stats.intel)),
        }
        target.physical_effects["Prone"].active = True
        target.physical_effects["Prone"].duration = 3
        target.physical_effects["Prone"].source = "Conjure Shackles"
        return f"Dimensional shackles hold {target.name} prone.\n"


class ConjurePotion(Spell):
    def __init__(self) -> None:
        super().__init__(
            "Conjure Potion",
            "Conjure a location-scaled Health or Mana potion. It cannot be "
            "used in town and enters a 50-step cooldown.",
            school="Arcane",
        )
        self.cost = 20
        self.combat = True
        self.subtyp = "Arcane"

    def is_available(self, user: Any, target: Any | None = None) -> bool:
        del target
        in_town = getattr(user, "in_town", False)
        in_town = in_town() if callable(in_town) else bool(in_town)
        return (
            not in_town
            and int(getattr(user, "conjure_potion_cooldown", 0) or 0) <= 0
        )

    def cast_out(self, user: Any) -> str:
        in_town = getattr(user, "in_town", False)
        in_town = in_town() if callable(in_town) else bool(in_town)
        if in_town:
            return "Conjure Potion cannot be used in town.\n"
        cooldown = int(getattr(user, "conjure_potion_cooldown", 0) or 0)
        if cooldown > 0:
            return f"Conjure Potion will recover in {cooldown} steps.\n"
        from .. import items

        depth = max(0, int(getattr(user, "location_z", 0) or 0))
        tiers = (
            (items.HealthPotion, items.ManaPotion),
            (items.GreatHealthPotion, items.GreatManaPotion),
            (items.SuperHealthPotion, items.SuperManaPotion),
            (items.MasterHealthPotion, items.MasterManaPotion),
        )
        tier = tiers[min(len(tiers) - 1, depth // 10)]
        potion = random.choice(tier)()
        user.mana.current -= self.cost
        user.modify_inventory(potion)
        user.conjure_potion_cooldown = 50
        return f"{user.name} conjures {potion.name}; the spell needs 50 steps to recover.\n"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del target, kwargs
        return self.cast_out(user)


class FloatingCrystal(Spell):
    """Create a mana-fed construct that eventually bursts at an enemy."""

    def __init__(self) -> None:
        super().__init__(
            "Floating Crystal",
            "Conjure a crystal that siphons 10% of maximum MP after each "
            "caster turn. At 30% it explodes, scaling the stored mana by the "
            "caster's spell power.",
            school="Conjuration",
        )
        self.cost = 0
        self.subtyp = "Construct"
        self.self_target = True

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del target, kwargs
        if getattr(user, "floating_crystal", None):
            return "A floating crystal is already gathering mana.\n"
        maximum_mana = max(1, int(getattr(user.mana, "max", 1) or 1))
        user.floating_crystal = {
            "mana": 0,
            "siphon_percent": 0.10,
            "threshold": max(1, math.ceil(maximum_mana * 0.30)),
            "threshold_percent": 0.30,
        }
        return f"A giant crystal begins orbiting {user.name}.\n"


class ExplosiveDecoy(Spell):
    """Detonate one active Mirror Image into an Arcane attack."""

    def __init__(self) -> None:
        super().__init__(
            "Explosive Decoy",
            "Sacrifice one remaining Mirror Image, causing it to explode and "
            "deal Arcane damage to the target.",
            school="Arcane",
        )
        self.cost = 18
        self.subtyp = "Illusion"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del kwargs
        if target is None:
            return "There is no target for Explosive Decoy.\n"
        effect = user.magic_effects.get("Duplicates")
        image_count = int(getattr(effect, "duration", 0) or 0)
        if effect is None or not effect.active or image_count <= 0:
            return "Explosive Decoy requires a remaining Mirror Image.\n"
        user.mana.current -= self.cost
        effect.duration = image_count - 1
        if effect.duration <= 0:
            effect.active = False
            effect.duration = 0
        damage = max(1, int(user.check_mod("magic", enemy=target) * 1.25))
        from ..classes import promotion_kits

        damage, shield_message, _fully_absorbed = promotion_kits.absorb_novel_shield(
            target,
            damage,
            source="spell",
        )
        target.health.current -= damage
        user._emit_damage_event(
            target,
            damage,
            damage_type="Arcane",
            source="spell",
            ability_name=self.name,
        )
        return (
            shield_message
            + f"One of {user.name}'s mirror images rushes {target.name} and "
            f"explodes for {damage} Arcane damage.\n"
        )


class _MiracleSpell(Spell):
    """Reality-breaking conjuration that consumes a Reality Fragment."""

    reagent_name = "Reality Fragment"

    def _consume_reagent(self, user: Any) -> str | None:
        stack = getattr(user, "inventory", {}).get(self.reagent_name, [])
        if not stack:
            return f"{user.name} needs a {self.reagent_name} to cast {self.name}.\n"
        user.modify_inventory(stack[0], subtract=True)
        return None

    def is_available(self, user: Any, target: Any | None = None) -> bool:
        del target
        return bool(getattr(user, "inventory", {}).get(self.reagent_name, []))


class MiracleBlade(_MiracleSpell):
    """Cut through defenses and causality with an impossible blade."""

    def __init__(self) -> None:
        super().__init__(
            "Miracle Blade",
            "Consume a Reality Fragment to make an unavoidable blade that "
            "ignores defense, evasion, shields, and resistance.",
            school="Conjuration",
        )
        self.cost = 45
        self.subtyp = "Miracle"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del kwargs
        if target is None:
            return "There is no target for Miracle Blade.\n"
        failed = self._consume_reagent(user)
        if failed:
            return failed
        user.mana.current -= self.cost
        spell_power = int(user.check_mod("magic", enemy=target))
        damage = max(
            1,
            spell_power * 2,
            int(max(1, target.health.max) * 0.25),
        )
        from ..classes import promotion_kits

        damage, shield_message, _fully_absorbed = promotion_kits.absorb_novel_shield(
            target,
            damage,
            source="spell",
        )
        target.health.current = max(0, target.health.current - damage)
        user._emit_damage_event(
            target,
            damage,
            damage_type="Reality",
            source="spell",
            ability_name=self.name,
        )
        return (
            shield_message
            + f"An impossible blade cuts through every protection around "
            f"{target.name} for {damage} reality damage.\n"
        )


class MiracleShackles(_MiracleSpell):
    """Bind one target to a fixed point in reality without a saving throw."""

    def __init__(self) -> None:
        super().__init__(
            "Miracle Shackles",
            "Consume a Reality Fragment to hold a target prone for 3 turns "
            "without an evasion check, immunity check, or escape roll.",
            school="Conjuration",
        )
        self.cost = 55
        self.subtyp = "Miracle"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del kwargs
        if target is None:
            return "There is no target for Miracle Shackles.\n"
        failed = self._consume_reagent(user)
        if failed:
            return failed
        user.mana.current -= self.cost
        target.conjured_shackles = {
            "turns": 3,
            "difficulty": 0,
            "unbreakable": True,
        }
        prone = target.physical_effects["Prone"]
        prone.active = True
        prone.duration = 3
        prone.source = self.name
        return (
            f"Miraculous shackles fix {target.name} in place for 3 turns; "
            "nothing can break them early.\n"
        )


class MiraclePotion(_MiracleSpell):
    """Create both maximum-tier restorative potion types without cooldown."""

    def __init__(self) -> None:
        super().__init__(
            "Miracle Potion",
            "Consume a Reality Fragment to create both a Master Health Potion "
            "and Master Mana Potion, even in town and without a cooldown.",
            school="Conjuration",
        )
        self.cost = 60
        self.combat = True
        self.subtyp = "Miracle"

    def cast_out(self, user: Any) -> str:
        failed = self._consume_reagent(user)
        if failed:
            return failed
        from .. import items

        user.mana.current -= self.cost
        health_potion = items.MasterHealthPotion()
        mana_potion = items.MasterManaPotion()
        user.modify_inventory(health_potion)
        user.modify_inventory(mana_potion)
        return (
            f"{user.name} contradicts conservation itself and conjures "
            f"{health_potion.name} and {mana_potion.name}.\n"
        )

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del target, kwargs
        return self.cast_out(user)


class MiracleCrystal(_MiracleSpell):
    """Create mana from nothing before bursting across every hostile target."""

    def __init__(self) -> None:
        super().__init__(
            "Miracle Crystal",
            "Consume a Reality Fragment to create a crystal that generates "
            "mana from nothing and bursts across every enemy after 4 turns.",
            school="Conjuration",
        )
        self.cost = 75
        self.subtyp = "Miracle"
        self.self_target = True

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del target, kwargs
        if getattr(user, "floating_crystal", None):
            return "A floating crystal is already gathering mana.\n"
        failed = self._consume_reagent(user)
        if failed:
            return failed
        user.mana.current -= self.cost
        maximum_mana = max(1, int(getattr(user.mana, "max", 1) or 1))
        user.floating_crystal = {
            "mana": 0,
            "siphon_percent": 0.0,
            "threshold": maximum_mana,
            "threshold_percent": 1.0,
            "miracle": True,
            "generated_per_turn": max(1, math.ceil(maximum_mana * 0.25)),
        }
        return (
            "A miraculous crystal begins creating mana where none existed.\n"
        )


class Torchlight(Spell):
    """Suppress random encounters with a conjured exploration light."""

    def __init__(self) -> None:
        super().__init__(
            "Torchlight",
            "Conjure a bright light for 50 steps, halving the random encounter "
            "rate while it remains active.",
            school="Conjuration",
        )
        self.cost = 12
        self.combat = False
        self.subtyp = "Construct"

    def cast_out(self, user: Any) -> str:
        from ..classes import mage_mechanics

        user.mana.current -= self.cost
        mage_mechanics.activate_torchlight(user)
        return (
            f"A brilliant conjured light surrounds {user.name}, driving away "
            f"enemies for {mage_mechanics.TORCHLIGHT_STEPS} steps.\n"
        )

    cast = cast_out


class ConjureElixir(Spell):
    """Create a restorative elixir on a travel cooldown."""

    def __init__(self) -> None:
        super().__init__(
            "Conjure Elixir",
            "Conjure an Elixir. The spell then requires 100 travel steps to recover.",
            school="Conjuration",
        )
        self.cost = 28
        self.combat = False
        self.subtyp = "Construct"

    def is_available(self, user: Any, target: Any | None = None) -> bool:
        del target
        return int(getattr(user, "conjure_elixir_cooldown", 0) or 0) <= 0

    def cast_out(self, user: Any) -> str:
        cooldown = int(getattr(user, "conjure_elixir_cooldown", 0) or 0)
        if cooldown > 0:
            return f"Conjure Elixir will recover in {cooldown} steps.\n"
        from .. import items

        user.mana.current -= self.cost
        user.modify_inventory(items.Elixir())
        user.conjure_elixir_cooldown = 100
        return f"{user.name} conjures an Elixir.\n"

    cast = cast_out


class BarrierWall(Spell):
    """Create a destructible construct that intercepts enemy attacks."""

    def __init__(self) -> None:
        super().__init__(
            "Barrier Wall",
            "Conjure a wall that enemies must destroy before they can target "
            "the caster again.",
            school="Conjuration",
        )
        self.cost = 35
        self.subtyp = "Construct"
        self.self_target = True

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del target, kwargs
        user.mana.current -= self.cost
        hit_points = max(
            30,
            int(getattr(getattr(user, "level", None), "level", 1))
            + int(user.stats.intel) * 2,
        )
        user.barrier_wall_hp = hit_points
        return f"A barrier wall with {hit_points} HP rises before {user.name}.\n"


class Banish(Spell):
    """Eject a fiend or fey from the current battle."""

    def __init__(self) -> None:
        super().__init__(
            "Banish",
            "Send a fiend or fey away from this realm. Banished enemies grant no rewards.",
            school="Conjuration",
        )
        self.cost = 24
        self.subtyp = "Binding"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        battle_engine = kwargs.get("battle_engine")
        if target is None:
            return "There is no target to banish.\n"
        creature_type = str(getattr(target, "enemy_typ", "")).lower()
        if creature_type not in {"fiend", "fey"}:
            return f"{target.name} is neither a fiend nor a fey.\n"
        user.mana.current -= self.cost
        target.health.current = 0
        target._banished_without_rewards = True
        if battle_engine is not None:
            from ..combat.encounter import EnemyResolution

            member = battle_engine._member_for_character(target)
            if member is not None and member.resolution is None:
                battle_engine.encounter.resolve_enemy(
                    member.combatant_id,
                    EnemyResolution.EJECTED,
                    cause="Banish",
                )
        return f"{target.name} is banished from this realm.\n"


class ManaBarbs(Spell):
    """Punish a target whenever it spends mana."""

    def __init__(self) -> None:
        super().__init__(
            "Mana Barbs",
            "For 3 turns, mana spent by the target deals the same amount of "
            "damage back to it.",
            school="Conjuration",
        )
        self.cost = 30
        self.subtyp = "Binding"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del kwargs
        if target is None:
            return "There is no target for Mana Barbs.\n"
        user.mana.current -= self.cost
        target.mana_barbs = {"turns": 3, "source": user}
        return f"Mana barbs coil around {target.name} for 3 turns.\n"


class _CallXenid(Spell):
    """Call ordinary transients until Thaumaturgist training unlocks Xenids."""

    category = ""

    def __init__(self, category: str, cost: int) -> None:
        self.category = category
        super().__init__(
            f"Conjure {category}",
            f"Conjure a nearby {category.lower()} creature as a transient ally. "
            "Thaumaturgists instead call their permanently chosen Xenid.",
            school="Conjuration",
        )
        self.cost = cost
        self.subtyp = "Calling"
        self.self_target = True

    def cast(
        self,
        user: Any,
        target: Any | None = None,
        *,
        battle_engine: Any | None = None,
        **kwargs: Any,
    ) -> str:
        del target, kwargs
        class_name = str(getattr(getattr(user, "cls", None), "name", ""))
        if class_name != "Thaumaturgist":
            from ..classes import mage_mechanics

            companion = mage_mechanics.conjure_standard_companion(
                user,
                self.category,
                source=self.name,
            )
            if companion is None:
                return (
                    f"No suitable {self.category.lower()} creature answers "
                    "the conjuration.\n"
                )
            user.mana.current -= self.cost
            return (
                f"{companion['name']} answers {self.name} and will fight "
                f"independently for {mage_mechanics.TRANSIENT_SUMMON_STEPS} "
                "steps.\n"
            )

        from .. import companions

        xenid_name = companions.chosen_xenid(user, self.category)
        if not xenid_name:
            choices = " or ".join(companions.XENID_PAIRS[self.category])
            return (
                f"Choose {choices} as the permanent {self.category.lower()} "
                "Xenid before casting this spell.\n"
            )
        if battle_engine is None:
            return "Calling a Xenid requires an active battle.\n"
        xenid = user.summons[xenid_name]
        prior_cost = getattr(xenid, "summon_mana_cost", None)
        xenid.summon_mana_cost = 0
        try:
            message, success, _xenid = battle_engine._execute_summon(xenid_name)
        finally:
            xenid.summon_mana_cost = prior_cost
        if success:
            user.mana.current -= self.cost
        return message.replace("summons", "calls")


class ConjureHumanoid(_CallXenid):
    def __init__(self) -> None:
        super().__init__("Humanoid", 12)


class ConjureMonster(_CallXenid):
    def __init__(self) -> None:
        super().__init__("Monster", 16)


class ConjureSpirit(_CallXenid):
    def __init__(self) -> None:
        super().__init__("Spirit", 20)


class ConjureFiend(_CallXenid):
    def __init__(self) -> None:
        super().__init__("Fiend", 24)


class ConjureCelestial(_CallXenid):
    def __init__(self) -> None:
        super().__init__("Celestial", 28)


class ConjureDragon(_CallXenid):
    def __init__(self) -> None:
        super().__init__("Dragon", 34)
