"""Warlock curse, familiar, Shadowcaster, and Demonologist abilities."""

from __future__ import annotations

from typing import Any

from .. import curses
from ..combat.combat_result import CombatResult
from .base import PowerUp, Spell


class _WarlockPassive(PowerUp):
    """Passive skill used by the authored Warlock trees."""

    def __init__(self, name: str, description: str, *, modifies: tuple[str, ...] = ()) -> None:
        super().__init__(name, description)
        self.passive = True
        self.presentation_modifier = bool(modifies)
        self.modifies = modifies


class FamiliarBond(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__("Familiar Bond", "Increase the familiar action chance from 25% to 33%.")


class FamiliarBond2(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__("Familiar Bond II", "Increase the familiar action chance from 33% to 50%.")


class ThornByMySide(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Thorn By My Side",
            "Homunculus Cover redirects damage to the attacker.",
            modifies=("Cover",),
        )


class RestorativeBarrier(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Restorative Barrier",
            "Fairy direct healing also creates a barrier equal to the healing.",
            modifies=("Heal", "Heal II", "Heal III"),
        )


class InsultToInjury(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Insult to Injury",
            "Mephit Arcane spells deal 50% more damage to Corrupted targets.",
            modifies=(
                "Magic Missile",
                "Magic Missile II",
                "Magic Missile III",
                "Kinetic Explosion",
            ),
        )


class MasterLocator(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Master Locator", "Jinkin finds improve random post-combat loot by one rarity tier."
        )


class FesteringAnguish(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Festering Anguish",
            "Corruption damage increases by 25% on every tick.",
            modifies=("Corruption", "Corruption II"),
        )


class VimAndRigor(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Vim and Rigor",
            "Health drains are more potent when the target is at full health.",
            modifies=("Health Drain", "Health/Mana Drain"),
        )


class ImpendingDemise(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Impending Demise",
            "Shadow Bolt damage is increased by 50% divided by the turns left on Doom.",
            modifies=("Shadow Bolt", "Shadow Bolt II", "Shadow Bolt III"),
        )


class PennyDreadful(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__("Penny Dreadful", "Feared targets take increased Shadow damage.")


class ResourceAbuse(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Resource Abuse",
            "Double Mana Tap's effect and redirect overhealing to the next Shadow damage spell.",
            modifies=("Mana Tap",),
        )


class MortalShackles(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Mortal Shackles",
            "Soul Binding makes the target take 25% more damage and reduces damage shared to the caster.",
            modifies=("Soul Binding",),
        )


class TopOff(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Top Off",
            "Health/Mana Drain consumes all Umbral Debt to refill both pools or completely drain the target; Death-immune targets increase its effect by 50%.",
            modifies=("Health/Mana Drain",),
        )


class PiercingBolt(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Piercing Bolt",
            "Shadow Bolt bypasses half of resistance and increases the effect of weakness by 50%.",
            modifies=("Shadow Bolt", "Shadow Bolt II", "Shadow Bolt III"),
        )


class Sciophobia(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Sciophobia",
            "While Shadow Curtain is active, attackers may become haunted and risk Fear each turn.",
            modifies=("Shadow Curtain",),
        )


class DeathBecomesUs(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Death Becomes Us",
            "Desoul kills darken the dungeon, costing unsighted enemies initiative and increasing all Shadow damage.",
            modifies=("Desoul",),
        )


class IndiscriminateProvocation(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Indiscriminate Provocation",
            "Homunculus Goad succeeds more often and confuses its target into attacking allies.",
            modifies=("Goad",),
        )


class UnoReverseCard(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Uno Reverse Card",
            "Fairy Cleanse reverses cured status effects into beneficial effects.",
            modifies=("Cleanse",),
        )


class NightMoves(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Night Moves",
            "Mephit can cast two spells per turn while Shade of Ahool is active.",
        )


class Bullionaire(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Bullionaire",
            "Jinkin Gold Toss uses endless heavy bullion, deals double damage, and increases combat gold.",
            modifies=("Gold Toss",),
        )


class DanceOfTheDead(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Dance of the Dead",
            "Enemies killed by Doom return as temporary undead allies.",
            modifies=("Doom",),
        )


class SoulAsylum(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Soul Asylum", "Enemies killed by Desoul produce a Soul Gem.", modifies=("Desoul",)
        )


class ContractKiller(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Contract Killer",
            "Soul Gem contracts gain 25% more favor and bargain taint.",
            modifies=("Call Contract",),
        )


class MysticalVitality(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Mystical Vitality",
            "Spells cost 25% less mana for two turns after using Life Tap.",
            modifies=("Life Tap",),
        )


class ContagiousBlaze(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Contagious Blaze",
            "Fire spells detonate Corruption around the target and may spread it.",
            modifies=("Corruption", "Corruption II"),
        )


class PersistentCorruption(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Persistent Corruption",
            "Corruption lasts at least four turns and deals 25% more damage.",
            modifies=("Corruption", "Corruption II"),
        )


class GreaseMissile(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Grease Missile",
            "Shadow Bolt coats its target in flammable grease, slowing it and making it prone to falling and intense burns.",
            modifies=("Shadow Bolt", "Shadow Bolt II", "Shadow Bolt III"),
        )


class FlammableAffliction(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Flammable Affliction",
            "Curse of Umbra also reduces Fire resistance.",
            modifies=("Curse of Umbra",),
        )


class MonkeysPaw(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Monkey's Paw",
            "Increases the potency of all curses.",
            modifies=(
                "Curse of Umbra",
                "Curse of Frailty",
                "Curse of Swarms",
                "Hemorrhaging Curse",
                "Curse of Elijah",
                "Curse of Dysarthria",
                "Demon Eyes",
            ),
        )


class _CurseSpell(Spell):
    curse_name = ""

    def __init__(self, name: str, description: str, cost: int = 16) -> None:
        super().__init__(name, description, school="Shadow")
        self.cost = cost
        self.subtyp = "Curse"

    def cast(
        self, user: Any, target: Any | None = None, *, fam: bool = False, **kwargs: Any
    ) -> str:
        del kwargs
        if target is None:
            return "There is no target to curse.\n"
        if not fam:
            user.mana.current -= self.cost
        return curses.apply_curse(
            target,
            self.curse_name,
            source=self.name,
            caster=user,
        )


class CurseUmbra(_CurseSpell):
    curse_name = "Umbra"

    def __init__(self) -> None:
        super().__init__("Curse of Umbra", "Persistently lowers the target's Shadow resistance.")


class CurseFrailty(_CurseSpell):
    curse_name = "Frailty"

    def __init__(self) -> None:
        super().__init__(
            "Curse of Frailty", "Persistently weakens every Strength-based action and check."
        )


class CurseElijah(_CurseSpell):
    curse_name = "Elijah"

    def __init__(self) -> None:
        super().__init__(
            "Curse of Elijah",
            "Makes the target brittle, reducing armor and allowing fractures.",
            20,
        )


class CurseDysarthria(_CurseSpell):
    curse_name = "Dysarthria"

    def __init__(self) -> None:
        super().__init__(
            "Curse of Dysarthria", "Persistently adds one turn to every spell's casting time.", 20
        )


class CurseSwarms(_CurseSpell):
    curse_name = "Swarms"

    def __init__(self) -> None:
        super().__init__(
            "Curse of Swarms",
            "Curse the enemy with swarms of mosquitoes, which deal minimal damage "
            "many times per turn and may spread corruption, status effects, and "
            "curses to nearby enemies.",
            20,
        )

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        message = super().cast(user, target, **kwargs)
        if target is not None:
            target._curse_swarms_caster = user
        return message


class HemorrhagingCurse(_CurseSpell):
    curse_name = "Hemorrhaging"

    def __init__(self) -> None:
        super().__init__(
            "Hemorrhaging Curse",
            "Curse the enemy with open wounds that bleed, dealing periodic damage.",
            20,
        )


class DemonEyes(_CurseSpell):
    curse_name = "Demon Eyes"

    def __init__(self) -> None:
        super().__init__(
            "Demon Eyes",
            "Curse the enemy, making them enticing to Fiends; Contracts are more effective and damage from Fiends is increased.",
            24,
        )


class CursePolydipsia(_CurseSpell):
    curse_name = "Polydipsia"

    def __init__(self) -> None:
        super().__init__(
            "Curse of Polydipsia",
            "Afflicts the target with an escalating, unquenchable thirst.",
            22,
        )


class ExpelCurse(Spell):
    def __init__(self) -> None:
        super().__init__(
            "Expel Curse", "Remove all persistent curses from the target.", school="Holy"
        )
        self.cost = 24
        self.subtyp = "Healing"

    def cast(
        self, user: Any, target: Any | None = None, *, fam: bool = False, **kwargs: Any
    ) -> str:
        del kwargs
        target = target or user
        if not fam:
            cost = self.cost
            try:
                from ..progression import has_talent

                if has_talent(user, "archbishop.swift-exorcism"):
                    cost -= 6
            except (AttributeError, KeyError, TypeError, ValueError):
                pass
            user.mana.current -= cost
        return curses.cure_curses(target)


class ShadowCurtain(Spell):
    def __init__(self) -> None:
        super().__init__(
            "Shadow Curtain",
            "Cloak yourself in shadow, slowing nearby enemies and empowering attacks.",
            school="Shadow",
        )
        self.cost = 28
        self.subtyp = "Support"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del target, kwargs
        user.mana.current -= self.cost
        user.shadow_curtain_turns = 4
        encounter = getattr(user, "_combat_encounter", None)
        for member in getattr(encounter, "living_members", ()):
            effect = member.enemy.stat_effects["Speed"]
            effect.active, effect.duration, effect.extra = True, 4, -4
        return f"{user.name} draws a curtain of living shadow.\n"


class SoulBinding(Spell):
    def __init__(self) -> None:
        super().__init__(
            "Soul Binding",
            "Link two souls so damage suffered by either is shared by both.",
            school="Shadow",
        )
        self.cost = 30
        self.subtyp = "Status"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del kwargs
        if target is None:
            return "There is no soul to bind.\n"
        user.mana.current -= self.cost
        user.soul_bound_to = target
        target.soul_bound_to = user
        target._soul_binding_caster = user
        return f"{user.name} binds their soul to {target.name}.\n"


class SoulSiphon(Spell):
    def __init__(self) -> None:
        super().__init__(
            "Soul Siphon",
            "Mark a soul for three turns; its death yields a Soul Gem.",
            school="Shadow",
        )
        self.cost = 25
        self.subtyp = "Status"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del kwargs
        if target is None:
            return "There is no soul to mark.\n"
        user.mana.current -= self.cost
        target.soul_siphon = {"caster": user, "turns": 3}
        return f"{target.name}'s soul is marked for collection.\n"


class SoulVessel(PowerUp):
    def __init__(self) -> None:
        super().__init__(
            "Soul Vessel",
            "Use a Soul Gem to store your soul temporarily; fatal damage instead restores 25% health and mana.",
        )
        self.cost = 0

    def use(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del target, kwargs
        soul_gems = getattr(user, "inventory", {}).get("Soul Gem", [])
        if not soul_gems:
            return "Soul Vessel requires a Soul Gem.\n"
        user.modify_inventory(soul_gems[0], subtract=True)
        user.soul_vessel_turns = 5
        return f"{user.name} seals their soul in a vessel for 5 turns.\n"


class Netherchar(Spell):
    def __init__(self) -> None:
        super().__init__(
            "Netherchar",
            "Flames rise beneath the enemy, dealing Fire damage and setting it ablaze.",
            school="Fire",
        )
        self.cost = 28
        self.subtyp = "Fire"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> CombatResult:
        del kwargs
        from ..classes import mage_mechanics

        result = self._reset_result(actor=user, target=target)
        user.mana.current -= mage_mechanics.spell_mana_cost(user, self)
        if target is None:
            result.message = "Netherchar finds no target.\n"
            return result
        raw = max(1, int(user.check_mod("magic", enemy=target) * 1.35))
        damage = max(1, int(raw * (1.0 - target.check_mod("resist", typ="Fire"))))
        target.health.current = max(0, target.health.current - damage)
        burn = target.magic_effects["DOT"]
        burn.active = True
        burn.duration = max(3, int(burn.duration or 0))
        burn.extra = max(int(burn.extra or 0), max(1, damage // 3))
        burn.source = "Burn"
        result.hit = True
        result.damage = damage
        result.message = f"Netherchar burns {target.name} for {damage} Fire damage.\n"
        return result


class Napalm(Spell):
    def __init__(self) -> None:
        super().__init__(
            "Napalm",
            "Consume an active burn to deal most of its remaining damage immediately.",
            school="Fire",
        )
        self.cost = 24
        self.subtyp = "Fire"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> CombatResult:
        del kwargs
        from ..classes import mage_mechanics

        result = self._reset_result(actor=user, target=target)
        user.mana.current -= mage_mechanics.spell_mana_cost(user, self)
        burn = getattr(target, "magic_effects", {}).get("DOT") if target is not None else None
        if burn is None or not burn.active or str(getattr(burn, "source", "")).lower() != "burn":
            result.message = "Napalm finds no flames to consume.\n"
            return result
        damage = max(1, int(int(burn.extra or 0) * int(burn.duration or 0) * 0.80))
        target.health.current = max(0, target.health.current - damage)
        burn.active = False
        burn.duration = 0
        burn.extra = 0
        result.hit = True
        result.damage = damage
        result.message = f"Napalm consumes the blaze for {damage} Fire damage.\n"
        return result


class Eclipse(Spell):
    def __init__(self) -> None:
        super().__init__("Eclipse", "Enter a short shadow form.", school="Shadow")
        self.cost = 30
        self.subtyp = "Transformation"

    def cast(self, user: Any, target: Any | None = None, **kwargs: Any) -> str:
        del target, kwargs
        user.mana.current -= self.cost
        user.warlock_eclipse_turns = 3
        return f"{user.name} enters Eclipse for 3 turns.\n"


class NightTerror(_WarlockPassive):
    def __init__(self) -> None:
        super().__init__(
            "Night Terror",
            "Increase Terrify damage by 25%, or by 50% when the target is asleep.",
            modifies=("Terrify",),
        )
