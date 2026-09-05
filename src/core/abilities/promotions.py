"""Promotion-specific passive and active skills."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..combat.targeting import TargetLossPolicy, TargetScope
from .base import Class
from .skills import _PassiveSkill

if TYPE_CHECKING:
    from typing import Any

    from ..character import Character


class _PromotionPassive(_PassiveSkill):
    pass


class ScavengersEye(_PromotionPassive):
    def __init__(self):
        super().__init__("Scavenger's Eye", "Modestly improves ordinary loot odds and rarity without creating restricted drops.")


class FindersKeepers(_PromotionPassive):
    def __init__(self):
        super().__init__("Finders Keepers", "Occasionally finds extra eligible loot after ordinary defeated enemies.")


class CheatDeath(_PromotionPassive):
    def __init__(self):
        super().__init__("Cheat Death", "Once per combat, Misfortune can help turn fatal damage into survival at 1 HP.")


class DeathMark(_PromotionPassive):
    def __init__(self):
        super().__init__(
            "Death Mark",
            "Setup attacks mark foes and grant Deathblow to spend those marks.",
        )


class Wayfinding(_PromotionPassive):
    def __init__(self):
        super().__init__("Wayfinding", "Studied routes and cases smooth Seeker movement magic.")


class MartialMastery(_PromotionPassive):
    def __init__(self):
        super().__init__("Martial Mastery", "Improves Ki discipline and readies the Dim Mak finisher.")


class _PromotionActive(Class):
    helper_name = ""
    skill_cost = 0

    def __init__(self, name: str, description: str, cost: int = 0):
        super().__init__(name=name, description=description)
        self.cost = cost


class _ResolveActive(_PromotionActive):
    resource_type = "Resolve"

    def __init__(self, name: str, description: str, resolve_cost: int | str):
        super().__init__(name, description, 0)
        self.resource_type = "Resolve"
        self.resolve_cost = resolve_cost


class ThreadedCast(_PromotionActive):
    def __init__(self):
        super().__init__(
            "Threaded Cast",
            "Spend all Threads on the next validated spell or Runic Boost: each grants "
            "+5 accuracy/reliability points and +6% output.",
            8,
        )

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.threaded_cast(user)


class ShadeOfAhool(_PromotionActive):
    def __init__(self):
        super().__init__("Shade of Ahool", "Become a flying shadow beast for three turns.", 0)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.shade_of_ahool(user)


class HoldTheLine(_ResolveActive):
    def __init__(self):
        super().__init__("Hold the Line", "Enter a shield stance that improves block and mitigation.", 0)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.hold_the_line(user)

    def is_available(self, user: Character, target: Character | None = None) -> bool:
        """Return whether the stance is not already active."""
        del target
        from ..classes import promotion_kits

        return not promotion_kits.hold_the_line_active(user)


class BraceWall(_ResolveActive):
    def __init__(self):
        super().__init__("Brace Wall", "Spend Resolve to raise Defense; also refreshes Hold the Line.", 15)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.brace_wall(user)


class OathsJudgment(_PromotionActive):
    def __init__(self):
        super().__init__(
            "Oath's Judgment",
            "Spend all Oath Conviction on a weapon technique shaped by the sworn vow.",
            0,
        )
        self.resource_type = "Oath Conviction"

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import paladin

        return paladin.oaths_judgment(user, target)


class OathsShelter(_PromotionActive):
    def __init__(self):
        super().__init__(
            "Oath's Shelter",
            "Spend all Oath Conviction on protection shaped by the sworn vow.",
            0,
        )
        self.resource_type = "Oath Conviction"

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import paladin

        return paladin.oaths_shelter(user)


class Condemnation(_PromotionActive):
    """Crusader weapon judgment dealing physical and Holy damage."""

    def __init__(self):
        super().__init__(
            "Condemnation",
            (
                "Strike with holy vengeance for weapon and Holy damage."
            ),
            10,
        )
        self.weapon = True

    def use(
        self,
        user: Character,
        target: Character | None = None,
        **kwargs: Any,
    ) -> str:
        from ..classes import paladin

        return paladin.condemnation(
            user,
            target,
            rng=kwargs.get("rng"),
        )


class Censure(_PromotionActive):
    """Shield-style weapon strike that can interrupt a charged action."""

    def __init__(self):
        super().__init__(
            "Censure",
            "Attack with a chance to interrupt an enemy charge ability.",
            12,
        )
        self.weapon = True

    def use(self, user, target=None, **kwargs):
        from ..classes import paladin

        return paladin.censure(
            user,
            target,
            battle_engine=kwargs.get("battle_engine"),
            rng=kwargs.get("rng"),
        )


class ShieldRicochet(_PromotionActive):
    """Strike every enemy with a thrown shield."""

    def __init__(self):
        super().__init__(
            "Shield Ricochet",
            "Throw your shield through all enemies, dealing physical damage "
            "with a chance to stun each target for 1 turn.",
            16,
        )
        self.target_scope = TargetScope.ALL_ENEMIES
        self.target_loss_policy = TargetLossPolicy.SNAPSHOT_ROSTER

    def use_group(self, user, targets, *, battle_engine, rng=None):
        from ..classes import paladin

        return paladin.shield_ricochet(
            user,
            targets,
            battle_engine=battle_engine,
            rng=rng,
        )


class PrayerOfFaith(_PromotionActive):
    """Invoke one of three desperate protective miracles."""

    def __init__(self):
        super().__init__(
            "Prayer of Faith",
            "Below 10% health, invoke a random miracle: heal to full, gain a "
            "brief all-damage barrier, or unleash Holy damage on all enemies.",
            20,
        )
        self.target_scope = TargetScope.ALL_ENEMIES
        self.target_loss_policy = TargetLossPolicy.SNAPSHOT_ROSTER

    def is_available(self, user, target=None):
        del target
        return user.health.current * 10 < user.health.max

    def use_group(self, user, targets, *, battle_engine, rng=None):
        from ..classes import paladin

        return paladin.prayer_of_faith(
            user,
            targets,
            battle_engine=battle_engine,
            rng=rng,
        )


class Sanctification(_PromotionPassive):
    """Increase all outgoing Holy damage."""

    def __init__(self):
        super().__init__(
            "Sanctification",
            "Passive: Increase Holy damage by 50%.",
        )


class RadiantHealing(_PromotionPassive):
    """Turn successful combat healing into Holy damage."""

    def __init__(self):
        super().__init__(
            "Radiant Healing",
            (
                "Passive: Healing spells cast in combat damage an enemy for "
                "10% of the amount healed as Holy damage."
            ),
        )


class UndeadHunter(_PromotionPassive):
    """Become faster and more precise when facing undead enemies."""

    def __init__(self):
        super().__init__(
            "Undead Hunter",
            (
                "Passive: The presence of Undead enemies increases Speed, "
                "initiative, and critical strike chance."
            ),
        )


class BeyondReproach(_PromotionPassive):
    """Allow Condemnation to prepare wicked targets for disintegration."""

    def __init__(self):
        super().__init__(
            "Beyond Reproach",
            (
                "Passive: Condemnation can mark undead and fiends, causing a "
                "successful Repel the Wicked to disintegrate them."
            ),
        )


class Penalization(_PromotionPassive):
    """Enter a wrath state after Mortal Strike connects."""

    def __init__(self):
        super().__init__(
            "Penalization",
            (
                "Passive: Successful Mortal Strike hits trigger wrath, "
                "increasing critical strike chance and Holy damage for the "
                "rest of combat."
            ),
        )


class CitadelAegis(_ResolveActive):
    def __init__(self):
        super().__init__("Citadel Aegis", "Consume full Resolve for a fortress barrier and defensive stance.", "Full")
        self.specials_hidden = True

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.citadel_aegis(
            user,
            battle_engine=kwargs.get("battle_engine"),
        )


class IronwallReprisal(_ResolveActive):
    def __init__(self):
        super().__init__("Ironwall Revenge", "Consume full Resolve for a three-hit counterattack.", "Full")
        self.specials_hidden = True

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.ironwall_reprisal(user, target)


class LastBastionSurge(_ResolveActive):
    def __init__(self):
        super().__init__("Last Bastion", "Consume full Resolve to recover and rebuild your guard.", "Full")
        self.specials_hidden = True

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.last_bastion(user)


class SanctuaryWard(_PromotionActive):
    def __init__(self):
        super().__init__(
            "Sanctuary Ward",
            "Spend all Devotion for a two-turn shield; larger spends cleanse and regenerate.",
            8,
        )

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.sanctuary_ward(user)


class RelicAegis(_PromotionActive):
    def __init__(self):
        super().__init__(
            "Relic Aegis",
            "Spend all Devotion for stronger shielded protection and a Holy counter.",
            12,
        )

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.relic_aegis(user)


class ConsecratedConduit(_PromotionActive):
    def __init__(self):
        super().__init__(
            "Consecrated Conduit",
            "Spend Hierophant Devotion to empower the next staff or holy attack.",
            10,
        )

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.consecrated_conduit(user)


class Supplication(_PromotionActive):
    def __init__(self):
        super().__init__(
            "Supplication",
            "Spend all Prayer to heal, shield, and possibly cleanse a living target.",
            10,
        )

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.supplication(user, target)


class GreatBenediction(_PromotionActive):
    def __init__(self):
        super().__init__(
            "Great Benediction",
            "Spend at least 3 Prayer for healing, defense, status resistance, and MP sustain.",
            18,
        )

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.great_benediction(user)


class CenteredGuard(_PromotionActive):
    def __init__(self):
        super().__init__(
            "Centered Guard",
            "Enter a defensive stance for two turns; later talents extend it and add protection.",
            8,
        )

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        user.mana.current -= self.cost
        duration = 3 if promotion_kits._has_track_talent(user, "monk.steadfast-center") else 2
        user.enter_defensive_stance(duration=duration)
        if promotion_kits._has_track_talent(user, "monk.guarded-purity"):
            promotion_kits.combat_state(user)["purge_immunity_turns"] = max(
                2,
                int(promotion_kits.combat_state(user).get("purge_immunity_turns", 0) or 0),
            )
        return f"{user.name} centers their guard.\n"


class MirrorBreath(_PromotionActive):
    def __init__(self):
        super().__init__("Mirror Breath", "Brief reflection and counter-ward support.", 10)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        user.mana.current -= self.cost
        user.magic_effects["Reflect"].active = True
        duration = 3 if promotion_kits._has_track_talent(user, "monk.mirror-stillness") else 2
        if promotion_kits._has_track_talent(user, "master-monk.reflecting-soul"):
            duration += 1
        user.magic_effects["Reflect"].duration = duration
        return f"{user.name}'s breath becomes a mirror ward.\n"


class PurgingKata(_PromotionActive):
    def __init__(self):
        super().__init__(
            "Purging Kata",
            "Cleanse Blind and Berserk through martial focus.",
            10,
        )

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        user.mana.current -= self.cost
        removed = []
        for name in ("Blind", "Berserk"):
            effect = user.status_effects.get(name)
            if effect is not None and effect.active:
                effect.active = False
                effect.duration = 0
                removed.append(name)
        return f"{user.name} purges {', '.join(removed) if removed else 'no hostile status'}.\n"


class FourfoldSurge(_PromotionActive):
    def __init__(self):
        super().__init__(
            "Fourfold Surge",
            "Spend at least two distinct Harmony aspects for their typed nature riders.",
            14,
        )

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.fourfold_surge(user, target)


class TotemSurge(_PromotionActive):
    def __init__(self):
        super().__init__("Totem Surge", "Spend Totem Resonance to force the active Totem pulse.", 10)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.totem_surge(user, target)


class ConduitCommand(_PromotionActive):
    def __init__(self):
        super().__init__("Conduit Command", "Empower the active summon's next non-Recall action.", 10)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.conduit_command(user)


class _InvokeSummon(_PromotionActive):
    summon_name = ""

    def __init__(self, summon_name: str):
        self.summon_name = summon_name
        super().__init__(f"Invoke {summon_name}", f"Borrow {summon_name}'s trusted invocation.", 12)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.invoke_summon(user, target, self.summon_name)


class InvokeHodag(_InvokeSummon):
    def __init__(self): super().__init__("Hodag")


class InvokeCaladrius(_InvokeSummon):
    def __init__(self): super().__init__("Caladrius")


class InvokePatagon(_InvokeSummon):
    def __init__(self): super().__init__("Patagon")


class InvokeDilong(_InvokeSummon):
    def __init__(self): super().__init__("Dilong")


class InvokeAgloolik(_InvokeSummon):
    def __init__(self): super().__init__("Agloolik")


class InvokeCacus(_InvokeSummon):
    def __init__(self): super().__init__("Cacus")


class InvokeIzulu(_InvokeSummon):
    def __init__(self): super().__init__("Izulu")


class InvokeHala(_InvokeSummon):
    def __init__(self): super().__init__("Hala")


class InvokeLamashtu(_InvokeSummon):
    def __init__(self): super().__init__("Lamashtu")


class InvokeSeraphim(_InvokeSummon):
    def __init__(self): super().__init__("Seraphim")


class InvokeBardi(_InvokeSummon):
    def __init__(self): super().__init__("Bardi")


class InvokeKobalos(_InvokeSummon):
    def __init__(self): super().__init__("Kobalos")


class InvokeZahhak(_InvokeSummon):
    def __init__(self): super().__init__("Zahhak")


class InvokeTiamat(_InvokeSummon):
    def __init__(self): super().__init__("Tiamat")


class _BeastCommand(_PromotionActive):
    command_name = ""

    def __init__(self, name: str):
        self.command_name = name
        super().__init__(name, f"Order the tamed companion to {name.lower()}.", 0)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.beast_command(user, self.command_name)


class PackStrike(_BeastCommand):
    def __init__(self): super().__init__("Pack Strike")


class GuardPartner(_BeastCommand):
    def __init__(self): super().__init__("Guard Partner")


class HarryPrey(_BeastCommand):
    def __init__(self): super().__init__("Harry Prey")


class MendWounds(_BeastCommand):
    def __init__(self): super().__init__("Mend Wounds")


class UnleashInstinct(_BeastCommand):
    """Spend the companion action on its species-specific bonded trait."""

    def __init__(self):
        super().__init__("Unleash Instinct")


class RallyPartner(_BeastCommand):
    """Spend the companion action restoring its partner's fighting condition."""

    def __init__(self):
        super().__init__("Rally Partner")


class GrandFinale(_PromotionActive):
    """End the current song immediately and resolve its accumulated coda."""

    def __init__(self):
        super().__init__(
            "Grand Finale",
            "End the active combat song immediately and spend its Crescendo on the coda.",
            8,
        )

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        del target, kwargs
        from ..classes import bard

        return bard.grand_finale(user, cost=self.cost)


class WingedPounce(_PromotionActive):
    def __init__(self):
        super().__init__("Winged Pounce", "Dragon Essence Werewolf pounce with brief flight.", 12)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.winged_pounce(user, target)
