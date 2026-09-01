"""Lancer and shield-defender progression abilities."""

from __future__ import annotations

from typing import Any

from ..combat.targeting import TargetLossPolicy, TargetScope
from .base import Class, Skill


class _ProgressionPassive(Class):
    """Simple learned passive used by authored progression trees."""

    def __init__(self, name: str, description: str):
        super().__init__(name=name, description=description)
        self.passive = True


class VigilantLanding(_ProgressionPassive):
    def __init__(self):
        super().__init__(
            "Vigilant Landing",
            "Landing from Jump has a Dexterity-based chance to enter a defensive stance.",
        )


class ExtendedReach(_ProgressionPassive):
    def __init__(self):
        super().__init__(
            "Extended Reach",
            "A main-hand polearm removes the accuracy penalty against flying creatures.",
        )


class Phalanx(_ProgressionPassive):
    def __init__(self):
        super().__init__(
            "Phalanx",
            "Gain defensive advantage while wielding a polearm in the main hand.",
        )


class CriticalVigor(_ProgressionPassive):
    def __init__(self):
        super().__init__(
            "Critical Vigor",
            "Critical weapon hits have a chance to restore health.",
        )


class DragonSoul(_ProgressionPassive):
    def __init__(self):
        super().__init__(
            "Dragon Soul",
            "Lethal damage has a chance to leave you at 1 HP and grant the next turn.",
        )


class Dragonheart(_ProgressionPassive):
    def __init__(self):
        super().__init__(
            "Dragonheart",
            "Improves Dragon Soul's trigger chance and restores 25% maximum HP.",
        )


class ShieldRiposte(_ProgressionPassive):
    def __init__(self):
        super().__init__(
            "Shield Riposte",
            "Fully blocking a weapon attack immediately attempts to knock the attacker prone.",
        )


class SpellReflection(_ProgressionPassive):
    def __init__(self):
        super().__init__(
            "Spell Reflection",
            "Spell Block has a chance to reflect a blocked projectile spell at its caster.",
        )


class SwingAndBash(Skill):
    """Follow a main-hand weapon strike with a shield impact."""

    def __init__(self):
        super().__init__(
            "Swing & Bash",
            "Follow a weapon attack with a shield attack.",
            weapon=True,
        )
        self.cost = 10
        self.subtyp = "Offensive"

    def use(self, user, target=None, **kwargs):
        result = super().use(user, target, **kwargs)
        if target is None:
            result.message = "Swing & Bash needs a target.\n"
            return result
        shield = user.equipment.get("OffHand")
        if getattr(shield, "subtyp", None) != "Shield":
            result.message = "Swing & Bash requires an equipped shield.\n"
            return result
        if user.mana.current < self.cost:
            result.message = f"{user.name} does not have enough mana to use Swing & Bash.\n"
            return result
        user.mana.current -= self.cost
        before = int(target.health.current)
        message, hit, crit = user.weapon_damage(
            target,
            use_offhand=False,
            attack_slots=("Weapon",),
        )
        if hit and target.is_alive():
            raw = max(1, int(user.check_mod("attack", enemy=target) * 0.5) + int(shield.mod))
            _hit, defense_message, damage = target.handle_defenses(
                user,
                raw,
                typ="Physical",
            )
            message += defense_message
            if damage > 0:
                damage, ward_message = target._apply_temporary_health(target, damage)
                message += ward_message
                target.health.current = max(0, int(target.health.current) - damage)
                user._emit_damage_event(
                    target,
                    damage,
                    damage_type="Physical",
                    ability_name=self.name,
                    attack_source="special_attack",
                    source="weapon_damage",
                )
                message += f"{user.name}'s shield follows through for {damage} damage.\n"
        result.hit = hit
        result.crit = crit if crit > 1 else None
        result.damage = max(0, before - int(target.health.current))
        result.message = message
        return result


class _ResolveAbility(Class):
    resource_type = "Resolve"

    def __init__(self, name: str, description: str, resolve_cost: int):
        super().__init__(name=name, description=description)
        self.resolve_cost = resolve_cost
        self.self_target = True


class SpellBlock(_ResolveAbility):
    def __init__(self):
        super().__init__(
            "Spell Block",
            "Prepare to block a projectile spell using its power and your shield strength.",
            25,
        )

    def use(self, user, target=None, **kwargs):
        del target, kwargs
        from ..classes import promotion_kits

        return promotion_kits.prepare_spell_block(user)


class BulwarkGuard(_ResolveAbility):
    def __init__(self):
        super().__init__(
            "Bulwark Guard",
            "Create a powerful barrier that lasts for one turn.",
            25,
        )

    def use(self, user, target=None, **kwargs):
        del target, kwargs
        from ..classes import promotion_kits

        return promotion_kits.bulwark_guard(user)


class PurgeWeakness(_ResolveAbility):
    def __init__(self):
        super().__init__(
            "Purge Weakness",
            "Remove negative effects and become immune to them for two turns.",
            40,
        )

    def use(self, user, target=None, **kwargs):
        del target, kwargs
        from ..classes import promotion_kits

        return promotion_kits.purge_weakness(user)


class Boast(_ResolveAbility):
    def __init__(self):
        super().__init__(
            "Boast",
            "Gain temporary health and increased Resolve generation for three turns.",
            20,
        )

    def use(self, user, target=None, **kwargs):
        del target, kwargs
        from ..classes import promotion_kits

        return promotion_kits.boast(user)


class FocusedAssault(_ResolveAbility):
    def __init__(self):
        super().__init__(
            "Focused Assault",
            "Improve hit chance and critical strike damage for three turns.",
            15,
        )

    def use(self, user, target=None, **kwargs):
        del target, kwargs
        from ..classes import promotion_kits

        return promotion_kits.focused_assault(user)


class Repercussion(_ResolveAbility):
    def __init__(self):
        super().__init__(
            "Repercussion",
            "Release a powerful blast wave against every enemy.",
            30,
        )
        self.target_scope = TargetScope.ALL_ENEMIES
        self.target_loss_policy = TargetLossPolicy.SNAPSHOT_ROSTER

    def use_group(self, user, targets, *, battle_engine, rng=None):
        from ..classes import promotion_kits

        return promotion_kits.repercussion(
            user,
            targets,
            battle_engine=battle_engine,
            rng=rng,
        )


class ShieldingWard(_ProgressionPassive):
    def __init__(self):
        super().__init__(
            "Shielding Ward",
            "Increase Magic Defense by 20 and halve damage remaining after Spell Block.",
        )


class Braggadocious(_ProgressionPassive):
    def __init__(self):
        super().__init__(
            "Braggadocious",
            "Increase HP by 50 and convert Boast's unused temporary HP into Resolve.",
        )


class CrushingVengeance(_ProgressionPassive):
    def __init__(self):
        super().__init__(
            "Crushing Vengeance",
            "Increase every Ironwall Revenge strike and make each debilitate its target.",
        )


class DoublePayback(_ProgressionPassive):
    def __init__(self):
        super().__init__(
            "Double Payback",
            "Ironwall Revenge makes one additional attack.",
        )


class TowerOffense(_ProgressionPassive):
    """Convert Shield Slam damage into Resolve."""

    def __init__(self):
        super().__init__(
            "Tower Offense",
            "Shield Slam generates Resolve based on the damage it deals.",
        )


class GetEven(_ProgressionPassive):
    """Discount a Resolve action after a successful Retaliate."""

    def __init__(self):
        super().__init__(
            "Get Even",
            (
                "Successful Retaliate counterattacks reduce the cost of the "
                "next non-Surge Resolve ability."
            ),
        )


class GeneratorShield(_ProgressionPassive):
    """Generate Resolve from Shield Ricochet impacts."""

    def __init__(self):
        super().__init__(
            "Generator Shield",
            (
                "Gain Resolve for each enemy hit by Shield Ricochet, doubled "
                "when that enemy is stunned."
            ),
        )


class BattleDetermination(_ProgressionPassive):
    """Generate Resolve immediately after Battle Cry."""

    def __init__(self):
        super().__init__(
            "Battle Determination",
            "Battle Cry immediately generates 20 Resolve.",
        )


class IronMaiden(_ProgressionPassive):
    def __init__(self):
        super().__init__(
            "Iron Maiden",
            "Attackers take damage while Stronghold is active.",
        )


class Stronghold(_ResolveAbility):
    def __init__(self):
        super().__init__(
            "Stronghold",
            "Consume full Resolve to reduce melee damage and increase block amount by 30%.",
            0,
        )
        self.resolve_cost = "Full"
        self.specials_hidden = True

    def use(self, user, target=None, **kwargs):
        del target, kwargs
        from ..classes import promotion_kits

        return promotion_kits.stronghold(user)
