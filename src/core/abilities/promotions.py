"""Promotion-specific passive and active skills."""

from __future__ import annotations

from typing import TYPE_CHECKING

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
        super().__init__("Death Mark", "Stealth, poison, and opener setups mark foes for finisher pressure.")


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
        super().__init__("Threaded Cast", "Spend Foresight Threads to mark the next eligible spell payoff.", 8)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.threaded_cast(user)


class Eclipse(_PromotionActive):
    def __init__(self):
        super().__init__("Eclipse", "Spend Umbral Debt to enter a short shadow form.", 0)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.eclipse(user)


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


class ShieldBash(_ResolveActive):
    def __init__(self):
        super().__init__("Shield Check", "Spend Resolve to lower the enemy's Attack and Speed.", 10)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.shield_bash(user, target)


class BraceWall(_ResolveActive):
    def __init__(self):
        super().__init__("Brace Wall", "Spend Resolve to refresh Hold the Line and raise Defense.", 15)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.brace_wall(user)


class Bulwark(_ResolveActive):
    def __init__(self):
        super().__init__("Bulwark", "Spend Resolve to create a short-lived damage barrier.", 25)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.bulwark(user)


class ShieldRiposte(_ResolveActive):
    def __init__(self):
        super().__init__("Shield Riposte", "Spend Resolve for an immediate weapon counter.", 20)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.shield_riposte(user, target)


class CoveringGuard(_ResolveActive):
    def __init__(self):
        super().__init__("Covering Guard", "Spend Resolve to ward against the next dangerous hit.", 20)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.covering_guard(user)


class DeflectSpell(_ResolveActive):
    def __init__(self):
        super().__init__("Deflect Spell", "Spend Resolve to raise Magic Defense against hostile spells.", 20)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.deflect_spell(user)


class SpellReflection(_ResolveActive):
    def __init__(self):
        super().__init__(
            "Spell Reflection",
            (
                "Spend Resolve to raise Magic Defense and reflect the next "
                "compatible hostile spell."
            ),
            25,
        )

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.prepare_spell_reflection(user)


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
    """Crusader weapon judgment that can condemn wicked creatures."""

    def __init__(self):
        super().__init__(
            "Condemnation",
            (
                "Strike with holy vengeance for weapon and Holy damage, with "
                "a chance to condemn fiends and undead to disintegration by "
                "Repel the Wicked."
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


class CitadelAegis(_ResolveActive):
    def __init__(self):
        super().__init__("Citadel Aegis", "Consume full Resolve for a fortress barrier and defensive stance.", "Full")

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.citadel_aegis(user)


class IronwallReprisal(_ResolveActive):
    def __init__(self):
        super().__init__("Ironwall Reprisal", "Consume full Resolve for a crushing counterattack.", "Full")

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.ironwall_reprisal(user, target)


class LastBastionSurge(_ResolveActive):
    def __init__(self):
        super().__init__("Last Bastion", "Consume full Resolve to recover and rebuild your guard.", "Full")

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.last_bastion(user)


class SanctuaryWard(_PromotionActive):
    def __init__(self):
        super().__init__("Sanctuary Ward", "Spend Devotion for a brief protective ward.", 8)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.sanctuary_ward(user)


class RelicAegis(_PromotionActive):
    def __init__(self):
        super().__init__("Relic Aegis", "Spend Templar Devotion for stronger shielded protection.", 12)

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
        super().__init__("Supplication", "Spend Prayer on a targeted divine support pulse.", 0)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.supplication(user, target)


class GreatBenediction(_PromotionActive):
    def __init__(self):
        super().__init__("Great Benediction", "Spend Prayer for several turns of proactive divine support.", 18)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.great_benediction(user)


class CenteredGuard(_PromotionActive):
    def __init__(self):
        super().__init__("Centered Guard", "A chi guard replacing late Monk spell exceptions.", 8)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        user.enter_defensive_stance(duration=2)
        return f"{user.name} centers their guard.\n"


class MirrorBreath(_PromotionActive):
    def __init__(self):
        super().__init__("Mirror Breath", "Brief reflection and counter-ward support.", 10)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        user.magic_effects["Reflect"].active = True
        user.magic_effects["Reflect"].duration = 2
        return f"{user.name}'s breath becomes a mirror ward.\n"


class PurgingKata(_PromotionActive):
    def __init__(self):
        super().__init__("Purging Kata", "Cleanse hostile status through martial focus.", 10)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        removed = []
        for name in ("Poison", "Blind", "Silence", "Berserk"):
            effect = user.status_effects.get(name)
            if effect is not None and effect.active:
                effect.active = False
                effect.duration = 0
                removed.append(name)
        return f"{user.name} purges {', '.join(removed) if removed else 'no hostile status'}.\n"


class FourfoldSurge(_PromotionActive):
    def __init__(self):
        super().__init__("Fourfold Surge", "Spend represented Aspect Harmony for a nature payoff.", 14)

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


class WingedPounce(_PromotionActive):
    def __init__(self):
        super().__init__("Winged Pounce", "Dragon Essence Werewolf pounce with brief flight.", 12)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from ..classes import promotion_kits

        return promotion_kits.winged_pounce(user, target)
