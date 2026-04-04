###########################################
"""ability manager"""
from __future__ import annotations

import random
from pathlib import Path
from textwrap import wrap
from typing import TYPE_CHECKING

from .combat.combat_result import CombatResult
from .constants import DAMAGE_VARIANCE_HIGH, DAMAGE_VARIANCE_LOW

if TYPE_CHECKING:
    from typing import Any

    from .character import Character


# ── YAML ability loader helper ──────────────────────────────────────────
_YAML_DIR = Path(__file__).parent / "data" / "abilities"


def _load_yaml_ability(filename: str, cls_name: str | None = None) -> Ability:
    """Load a combat-ready ability from a YAML file.

    If *cls_name* is provided it is stored on the returned instance as
    ``_class_name`` so the save-system serialiser can round-trip the
    original Python class name.
    """
    from .data.ability_loader import AbilityFactory
    ability = AbilityFactory.create_from_yaml(
        _YAML_DIR / filename, combat_ready=True
    )
    if cls_name:
        ability._class_name = cls_name
    return ability


class Ability:
    """
    Base class for all abilities

    Attributes:
        name: name of the ability
        description: description of the ability that explains what it does in so many words
        cost: amount of mana required to cast spell; default is 0
        combat: boolean indicating whether the ability can only be cast in combat
        passive: boolean indicating whether the ability is passively active
        typ: the type of the ability
        subtyp: the subtype of the ability
        dmg_mod: damage modifier for the ability
        result: the result of the ability
    -----------------------------------------------------------
    Methods:
        __init__: initializes the ability with the given attributes
        __str__: returns a string representation of the ability
        special_effect: applies a special effect to the ability
    """

    def __init__(
            self,
            name: str,
            description: str,
            cost: int = 0,
            combat: bool = True,
            passive: bool = False,
            typ: str = "",
            subtyp: str = "",
            dmg_mod: float = 1.0,
            ):
        """
        Args:
            name (str): name of the ability
            description (str): description of the ability that explains what it does in so many words
            cost (int): amount of mana required to cast spell; default is 0
            combat (bool): boolean indicating whether the ability can only be cast in combat
            passive (bool): boolean indicating whether the ability is passively active
            typ (str): the type of the ability
            subtyp (str): the subtype of the ability
            dmg_mod (float): damage modifier for the ability
            result (CombatResult): the result of the ability
        """
        self.name = name
        self.description = description
        self.cost = cost
        self.combat = combat
        self.passive = passive
        self.typ = typ
        self.subtyp = subtyp
        self.dmg_mod = dmg_mod
        self.result = CombatResult(
            action=name,
            extra={'cost': cost, "type": self.typ, "subtype": self.subtyp}
            )

    def _ensure_result(self) -> None:
        """
        Ensure self.result exists (for backward compatibility with old save files).
        Creates a new CombatResult if the attribute is missing.
        """
        if not hasattr(self, 'result'):
            self.result = CombatResult(
                action=self.name,
                extra={'cost': self.cost, "type": self.typ, "subtype": self.subtyp}
            )

    def _reset_result(
        self,
        *,
        actor: Character | None = None,
        target: Character | None = None,
    ) -> CombatResult:
        """
        Reset the reusable result object to per-cast defaults.

        Many ability instances are reused across turns (enemy spellbooks),
        so this clears transient fields (messages, effects, extra context)
        to prevent cross-cast leakage.
        """
        self._ensure_result()
        result = self.result
        result.action = self.name
        result.actor = actor
        result.target = target
        result.hit = None
        result.crit = None
        result.dodge = None
        result.block = None
        result.block_amount = None
        result.damage = 0
        result.healing = 0
        result.effects_applied = {
            "Status": [],
            "Physical": [],
            "Stat": [],
            "Magic": [],
            "Class": [],
        }
        result.extra = {"cost": self.cost, "type": self.typ, "subtype": self.subtyp}
        result.message = ""
        return result

    def __str__(self) -> str:
        """
        Returns:
            str: string representation of the ability

        Example:
            >>> ability = Ability("Fireball", "A powerful fire spell.")
            >>> print(ability)
            ================================
            Fireball
            A powerful fire spell.
            -----------------------------------
            Type: Spell
            Sub-Type: Offensive
            Mana Cost: 10
            ===================================
        """
        wrapped_description = wrap(self.description, 35, break_on_hyphens=False)
        description_text = "\n".join(wrapped_description)
        str_text = (
            f"{'=' * ((35 - len(self.name)) // 2)}{self.name}{'=' * ((36 - len(self.name)) // 2)}\n"
            f"{description_text}\n"
            f"{35*'-'}\n"
            f"Type: {self.typ}\n"
            f"Sub-Type: {self.subtyp}\n"
        )
        if not self.passive:
            str_text += f"Mana Cost: {self.cost}\n"
        else:
            str_text += "Passive\n"
        str_text += f"==================================="
        return str_text

    def special_effect(self, *args: Any, **kwargs: Any) -> CombatResult:
        """
        Applies a special effect to the ability.
        Args:
            *args: variable length argument list
            **kwargs: variable length keyword argument list
        Returns:
            CombatResult: the result of the special effect
        Raises:
            NotImplementedError: if the special effect is not implemented
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not implement special_effect method."
        )


class Skill(Ability):
    """
    Child class of Ability that handles skills

    Attributes:
        name: name of the ability
        description: description of the ability that explains what it does in so many words
        cost: amount of mana required to cast spell; default is 0
        combat: boolean indicating whether the ability can only be cast in combat
        passive: boolean indicating whether the ability is passively active
        typ: the type of these abilities is 'Skill'
        subtyp: the subtype of the ability; the options are: 
            'Offensive', 'Defensive', 'Stealth', 'Enhance', 'Drain', 'Class', 'Truth',
            'Martial Arts', 'Luck', or 'PowerUp'
        dmg_mod: damage modifier for the ability
        result: the result of the ability
        weapon: boolean indicating whether the ability is a weapon skill
    ------------------------------------------------------------
    Methods:
        __init__: initializes the ability with the given attributes
        __str__: returns a string representation of the ability
        special_effect: applies a special effect to the ability
        use: applies the skill to the target
    ------------------------------------------------------------
    Example:
        >>> skill = Skill("Double Strike", "Perform two melee attacks at normal damage.")
        >>> print(skill)
        ================================
        Double Strike
        Perform two melee attacks at normal damage.
        -----------------------------------
        Type: Skill
        Sub-Type: Offensive
        Mana Cost: 10
        ===================================
    """

    def __init__(
            self,
            name: str,
            description: str,
            weapon: bool = False
            ):
        """
        Args:
            name (str): name of the ability
            description (str): description of the ability that explains what it does in so many words
            weapon (bool): boolean indicating whether the ability is a weapon skill
        """
        super().__init__(name, description)
        self.typ = "Skill"
        self.weapon = weapon

    def use(self, user: Character, target: Character = None, **kwargs) -> CombatResult:
        """
        Applies the skill to the target.
        Ensures self.result exists and sets up basic properties.
        Subclasses should call super().use(user, target, **kwargs) first,
        then add their specific logic.
        
        Args:
            user: The character using the skill
            target: The target of the skill (optional)
            **kwargs: Additional keyword arguments
        Returns:
            CombatResult: the result of the skill
        """
        self._ensure_result()
        self.result.actor = user
        self.result.target = target
        self.result.damage = 0
        self.result.extra['cost'] = self.cost
        return self.result


class Spell(Ability):
    """
    Child class of Ability that handles spell casting

    Attributes:
        name: name of the ability
        description: description of the ability that explains what it does in so many words
        cost: amount of mana required to cast spell; default is 0
        combat: boolean indicating whether the ability can only be cast in combat
        passive: boolean indicating whether the ability is passively active
        typ: the type of the abilities is 'Spell'
        subtyp: the subtype of the ability; the options are:
            'Fire', 'Ice', 'Lightning', 'Earth', 'Water', 'Wind', 'Holy', 'Shadow', 'Poison',
            'Heal', 'Death', 'Support', 'Status', 'Movement', 'Illusion', or 'Non-elemental'
        dmg_mod: damage modifier for the ability
        result: the result of the ability
        school: the school of magic to which this spell belongs
    ------------------------------------------------------------
    Methods:
        __init__: initializes the ability with the given attributes
        __str__: returns a string representation of the ability
        special_effect: applies a special effect to the ability
        cast: applies the spell to the target
    ------------------------------------------------------------
    Example:
        >>> spell = Spell("Fireball", "A powerful fire spell.")
        >>> print(spell)
        ================================
        Fireball
        A powerful fire spell.
        -----------------------------------
        Type: Spell
        Sub-Type: Fire
        Mana Cost: 10
        ===================================
    """

    def __init__(
            self,
            name: str,
            description: str,
            school: str | None = None,
            ):
        """
        Args:
            name (str): name of the ability
            description (str): description of the ability that explains what it does in so many words
            school (str | None): the school of magic to which this spell belongs
        """
        super().__init__(name, description)
        self.typ: str = "Spell"
        self.school = school

    def cast(self, user: Character, target: Character = None, **kwargs: Any) -> CombatResult:
        """
        Applies the spell to the target.
        Ensures self.result exists and sets up basic properties.
        Subclasses should call super().cast(user, target, **kwargs) first,
        then add their specific logic.
        
        Args:
            user: The character casting the spell
            target: The target of the spell (optional)
            **kwargs: Additional keyword arguments
        Returns:
            CombatResult: the result of the spell
        """
        self._ensure_result()
        self.result.actor = user
        self.result.target = target
        self.result.damage = 0
        self.result.extra['cost'] = self.cost
        return self.result


"""
Skill section
"""


def _skill_subtype(cls_name: str, subtyp: str, description: str) -> type:
    """Generate a Skill subclass whose only distinction is *subtyp*."""
    def _init(self, name: str = "", description: str = "", **kwargs: Any) -> None:
        Skill.__init__(self, name, description, **kwargs)
        self.subtyp = subtyp
    return type(cls_name, (Skill,), {
        "__init__": _init,
        "__doc__": description,
    })


Offensive = _skill_subtype("Offensive", "Offensive",
    "Skill subtype for offensive skills that work to damage the enemy.")
Defensive = _skill_subtype("Defensive", "Defensive",
    "Skill subtype for defensive skills that work to protect the user.")
Stealth = _skill_subtype("Stealth", "Stealth",
    "Skill subtype for stealth skills that use subterfuge to surprise the enemy.")
Enhance = _skill_subtype("Enhance", "Enhance",
    "Skill subtype for enhance skills that enhance the user's abilities or equipment.")
Drain = _skill_subtype("Drain", "Drain",
    "Skill subtype for drain skills that drain the enemy's health or mana.")
Class = _skill_subtype("Class", "Class",
    "Skill subtype for class-specific skills.")
Truth = _skill_subtype("Truth", "Truth",
    "Skill subtype for truth skills that reveal secrets or hidden truths.")
MartialArts = _skill_subtype("MartialArts", "Martial Arts",
    "Skill subtype for martial arts skills specific to hand-to-hand combat.")
Luck = _skill_subtype("Luck", "Luck",
    "Skill subtype for luck-based skills.")
PowerUp = _skill_subtype("PowerUp", "Power Up",
    "Skill subtype for power-up skills obtained through training.")


# Skills #
# Offensive
class ShieldSlam:
    """Data-driven (shield_slam.yaml) – str+shield damage + stun."""
    def __new__(cls):
        return _load_yaml_ability("shield_slam.yaml", cls_name="ShieldSlam")


class DoubleStrike:
    """Data-driven (double_strike.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("double_strike.yaml", cls_name="DoubleStrike")


class TripleStrike:
    """Data-driven (triple_strike.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("triple_strike.yaml", cls_name="TripleStrike")


class FlurryBlades:
    """Data-driven (flurry_blades.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("flurry_blades.yaml", cls_name="FlurryBlades")


class PiercingStrike:
    """Data-driven (piercing_strike.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("piercing_strike.yaml", cls_name="PiercingStrike")


class TrueStrike:
    """Data-driven (true_strike.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("true_strike.yaml", cls_name="TrueStrike")


class TruePiercingStrike:
    """Data-driven (true_piercing_strike.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("true_piercing_strike.yaml", cls_name="TruePiercingStrike")


class Jump:
    """Data-driven (jump.yaml) – leap attack with full modification system."""
    def __new__(cls):
        return _load_yaml_ability("jump.yaml", cls_name="Jump")


class Doublecast:
    """Data-driven (doublecast.yaml) – cast 2 spells in a single turn."""
    def __new__(cls):
        return _load_yaml_ability("doublecast.yaml", cls_name="Doublecast")


class Triplecast:
    """Data-driven (triplecast.yaml) – cast 3 spells in a single turn."""
    def __new__(cls):
        return _load_yaml_ability("triplecast.yaml", cls_name="Triplecast")


class MortalStrike:
    """Data-driven (mortal_strike.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("mortal_strike.yaml", cls_name="MortalStrike")


class MortalStrike2:
    """Data-driven (mortal_strike_2.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("mortal_strike_2.yaml", cls_name="MortalStrike2")


class BattleCry:
    """Data-driven (battle_cry.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("battle_cry.yaml", cls_name="BattleCry")


class Charge(Offensive):
    """Data-driven (charge.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("charge.yaml", cls_name="Charge")


# Defensive skills
class ShieldBlock(Defensive):
    """
    Passive ability; increases damage blocked by 25% when using a shield
    """

    def __init__(self):
        super().__init__(
            name="Shield Block",
            description="You are much more proficient with a shield than most, "
            "increasing the amount of damage blocked by 25% when using "
            "a shield.",
        )
        self.passive = True


class Parry(Defensive):
    """
    Passive ability; chance to counterattack if an attack is successfully dodged
    """

    def __init__(self):
        super().__init__(
            name="Parry",
            description="Passive chance to counterattack if an attack is successfully "
            "dodged.",
        )
        self.passive = True


class Quickstep(Defensive):
    """
    Passive ability; improves dodge chance via DEX scaling.

    This is intended as a Footpad-line defensive baseline so DEX-forward builds
    have a meaningful mitigation path without relying on flee mechanics.
    """

    def __init__(self):
        super().__init__(
            name="Quickstep",
            description="You fight light on your feet, improving your ability to evade attacks.",
        )
        self.passive = True


class EvasiveGuard(Defensive):
    """
    Passive ability; stackable damage reduction against weapon hits (DEX-scaling).

    This is meant to give Footpad-line characters a way to mitigate damage without
    altering racial resistances or relying on flee mechanics.
    """

    def __init__(self):
        super().__init__(
            name="Evasive Guard",
            description="Each time you are hit, you learn and reduce future damage (stacks up to 3). "
                        "Stacks reset when you dodge an attack.",
        )
        self.passive = True


class Disarm:
    """Disarm the enemy - data-driven (Batch 4)."""
    def __new__(cls):
        return _load_yaml_ability("disarm.yaml", cls_name="Disarm")


class Cover(Defensive):
    """
    Familiar only skill; stand in the way of an attack, protecting your master from harm.
    """

    def __init__(self):
        super().__init__(
            name="Cover",
            description="You stand in the way in the face of attack, protecting your master"
            " from harm.",
        )
        self.passive = True


class Goad:
    """Data-driven (goad.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("goad.yaml", cls_name="Goad")


# Stealth skills
class Backstab:
    """Data-driven (backstab.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("backstab.yaml", cls_name="Backstab")


class PocketSand:
    """Data-driven (pocket_sand.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("pocket_sand.yaml", cls_name="PocketSand")


class SleepingPowder:
    """Data-driven (sleeping_powder.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("sleeping_powder.yaml", cls_name="SleepingPowder")


class KidneyPunch:
    """Data-driven (kidney_punch.yaml) – weapon hit + stun."""
    def __new__(cls):
        return _load_yaml_ability("kidney_punch.yaml", cls_name="KidneyPunch")


class SmokeScreen:
    """Data-driven (smoke_screen.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("smoke_screen.yaml", cls_name="SmokeScreen")


class Steal:
    """Data-driven (steal.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("steal.yaml", cls_name="Steal")


class Mug:
    """Data-driven (mug.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("mug.yaml", cls_name="Mug")


class ShadowStrike:
    """Data-driven (shadow_strike.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("shadow_strike.yaml", cls_name="ShadowStrike")


class Lockpick(Stealth):
    """
    Pick the lock on a chest, allowing you to open it.
    """

    def __init__(self):
        super().__init__(name="Lockpick", description="Unlock a locked chest.")
        self.passive = True


class MasterLockpick(Lockpick):
    """
    Replaces Lockpick; pick the lock on a chest or door, allowing you to open it.
    """

    def __init__(self):
        super().__init__()
        self.name = "Master Lockpick"
        self.description = "Unlock a locked chest or door."
        self.passive = True


class PoisonStrike:
    """Data-driven (poison_strike.yaml) – weapon hit + poison."""
    def __new__(cls):
        return _load_yaml_ability("poison_strike.yaml", cls_name="PoisonStrike")


class SneakAttack:
    """Data-driven (sneak_attack.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("sneak_attack.yaml", cls_name="SneakAttack")


# Enhance skills
class ImbueWeapon:
    """Data-driven (imbue_weapon.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("imbue_weapon.yaml", cls_name="ImbueWeapon")


class ManaSlice:
    """Data-driven (mana_slice.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("mana_slice.yaml", cls_name="ManaSlice")


class ManaSlice2:
    """Data-driven (mana_slice_2.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("mana_slice_2.yaml", cls_name="ManaSlice2")


class DispelSlash:
    """Data-driven (dispel_slash.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("dispel_slash.yaml", cls_name="DispelSlash")


class EnhanceBlade(Enhance):
    """
    Enhance your weapon with arcane energy, amplifying its strength in proportion to your mana reserves.
    - mod = weapon damage * int(4 * (mana.current / mana.max))
    """

    def __init__(self):
        super().__init__(
            name="Enhance Blade",
            description="Your blade thrums with arcane energy, amplifying its "
            "strength in proportion to your mana reserves. With each "
            "strike, you channel your magic into raw power, adding "
            "bonus damage equal to your weapon's base damage multiplied"
            " by your mana percentage. The greater your mana, the more "
            "devastating your attacks.",
        )
        self.passive = True


class EnhanceArmor(Enhance):
    """
    Enhance your armor with arcane energy, fortifying its strength in proportion to your health.
    - mod = armor rating * max(5, health.max / health.current)
    """

    def __init__(self):
        super().__init__(
            name="Enhance Armor",
            description="Your armor adapts to your dwindling arcane reserves, "
            "fortifying itself as your mana depletes. The less mana "
            "you have, the greater your ' defense rating becomes. "
            "This protective enchantment ensures you can endure even "
            "when your magic is nearly exhausted.",
        )
        self.passive = True


class ManaShield:
    """Skill — data-driven (mana_shield.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("mana_shield.yaml", cls_name="ManaShield")


class ManaShield2:
    """Skill — data-driven (mana_shield_2.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("mana_shield_2.yaml", cls_name="ManaShield2")


class ElementalStrike:
    """Data-driven (elemental_strike.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("elemental_strike.yaml", cls_name="ElementalStrike")


# Drain skills
class HealthDrain:
    """Skill — data-driven (health_drain.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("health_drain.yaml", cls_name="HealthDrain")


class ManaDrain:
    """Skill — data-driven (mana_drain.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("mana_drain.yaml", cls_name="ManaDrain")


class HealthManaDrain:
    """Skill — data-driven (health_mana_drain.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("health_mana_drain.yaml", cls_name="HealthManaDrain")


class LifeTap:
    """Data-driven (life_tap.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("life_tap.yaml", cls_name="LifeTap")


class ManaTap:
    """Data-driven (mana_tap.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("mana_tap.yaml", cls_name="ManaTap")


# Class skills
class LearnSpell(Class):
    """
    Enables a diviner to learn rank 1 enemy spells.
    """

    def __init__(self):
        super().__init__(
            name="Learn Spell",
            description="Enables a diviner to learn rank 1 enemy spells.",
        )
        self.passive = True


class LearnSpell2(LearnSpell):
    """
    Enables a diviner to learn rank 2 enemy spells.
    - replaces Learn Spell
    """

    def __init__(self):
        super().__init__()
        self.description = "Enables a diviner to learn rank 2 enemy spells."


class Transform:
    """Data-driven (transform.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("transform.yaml", cls_name="Transform")


class Transform2:
    """Data-driven (transform2.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("transform2.yaml", cls_name="Transform2")


class Transform3:
    """Data-driven (transform3.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("transform3.yaml", cls_name="Transform3")


class Transform4:
    """Data-driven (transform4.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("transform4.yaml", cls_name="Transform4")


class Totem:
    """Data-driven (totem.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("totem.yaml", cls_name="Totem")


class MaelstromWeapon(Class):
    """
    Shaman passive ability: Maelstrom Weapon
    
    Each successive hit increases critical strike chance.
    The critical strike chance boost resets on a critical hit or a miss.
    
    Mechanics:
    - Gain 5% critical strike chance per consecutive hit
    - Max 6 consecutive hits = 30% bonus crit chance
    - Resets when: landing a critical strike, missing an attack, or being hit
    """

    def __init__(self):
        super().__init__(
            name="Maelstrom Weapon",
            description="Successive strikes channel maelstrom energy into your weapon, "
            "increasing critical strike chance with each hit. The energy "
            "dissipates on a critical strike or if you miss.",
        )
        self.passive = True
        self.crit_bonus_per_hit = 0.05  # 5% per hit
        self.max_hits = 6  # Max bonus of 30%


class Familiar(Class):
    """
    Summon a familiar, a magic creature that serves as both a pet and a helper.
    """

    def __init__(self):
        super().__init__(
            name="Familiar",
            description="The warlock gains the assistance of a familiar, a magic serving "
            "as both a pet and a helper. The familiar's abilities rely on its"
            " master's statistics and resources.",
        )
        self.passive = True


class Familiar2(Familiar):

    def __init__(self):
        super().__init__()
        self.description = "The warlock's familiar gains strength, unlocking additional abilities."


class Familiar3(Familiar):

    def __init__(self):
        super().__init__()
        self.description = "The warlock's familiar gains additional strength, unlocking even more abilities."


class Summon(Class):

    def __init__(self):
        super().__init__(
            name="Summon",
            description="Call forth powerful allies to fight for you in combat. These "
            "creatures learn a variety of abilities and increase in power "
            "based on the Summoner's intel and charisma.",
        )
        self.passive = True


class Summon2(Summon):

    def __init__(self):
        super().__init__()


class Tame(Class):

    def __init__(self):
        super().__init__(
            name="Tame",
            description="Attempt to bring a wild beast over to your side. You cannot "
            "perform any actions while channeling this ability.",
        )
        self.passive = True


class AbsorbEssence(Class):
    """
    Currently 5% chance
    Different monster types improve different stats
    Reptile: increase strength
    Aberration: increase intelligence
    Slime: increase wisdom
    Construct: increase constitution
    Humanoid: increase charisma
    Insect: increase dexterity
    Animal: increase max health
    Monster: increase max mana
    Undead: increase level
    Dragon: increase gold
    """

    def __init__(self):
        super().__init__(
            name="Absorb Essence",
            description="When a Soulcatcher kills an enemy, there is a chance that "
            "they may absorb part of the enemy's essence. Different monster types "
            "improve different stats, allowing the Soulcatcher to grow stronger with"
            " each victory.",
        )
        self.passive = True


class Reveal:
    """Data-driven (reveal.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("reveal.yaml", cls_name="Reveal")


class Inspect:
    """Data-driven (inspect.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("inspect.yaml", cls_name="Inspect")


class ExploitWeakness:
    """Data-driven (exploit_weakness.yaml) – weakness detection + weapon."""
    def __new__(cls):
        return _load_yaml_ability("exploit_weakness.yaml", cls_name="ExploitWeakness")


class KeenEye(Truth):
    """
    Gives Inquisitor insights about their surroundings
    """

    def __init__(self):
        super().__init__(
            name="Keen Eye",
            description="As an Inquisitor, you can gain insights into your surroundings.",
        )
        self.passive = True


class Cartography(Truth):
    """
    Reveals minimap to Seeker, regardless of whether they have visited an area
    """

    def __init__(self):
        super().__init__(
            name="Cartography",
            description="Seekers are masters at map making and gain the ability to "
            "see all of the dungeon, regardless of whether an area has "
            "been visited.",
        )
        self.passive = True


# Martial Art Skills
class LegSweep:
    """Sweep the leg, trip the enemy – data-driven (Batch 4)."""
    def __new__(cls):
        return _load_yaml_ability("leg_sweep.yaml", cls_name="LegSweep")


class ChiHeal:
    """Skill — data-driven (chi_heal.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("chi_heal.yaml", cls_name="ChiHeal")


class PurityBody:
    """Data-driven (purity_body.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("purity_body.yaml", cls_name="PurityBody")


class PurityBody2:
    """Data-driven (purity_body2.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("purity_body2.yaml", cls_name="PurityBody2")


class Evasion(MartialArts):

    def __init__(self):
        super().__init__(
            name="Evasion",
            description="You have become highly attuned at your surroundings, anticipating "
            "other's actions and increasing your chance to dodge attacks.",
        )
        self.passive = True


# Luck
class GoldToss:
    """Data-driven (gold_toss.yaml) – gold-based unblockable damage."""
    def __new__(cls):
        return _load_yaml_ability("gold_toss.yaml", cls_name="GoldToss")


class SlotMachine:
    """Data-driven (slot_machine.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("slot_machine.yaml", cls_name="SlotMachine")


class Blackjack:
    """Data-driven (blackjack.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("blackjack.yaml", cls_name="Blackjack")


# Power Up skills
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


class DivineAegis:
    """Skill — data-driven (divine_aegis.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("divine_aegis.yaml", cls_name="DivineAegis")


class DragonsFury(PowerUp):
    """
    Dragoon Power Up
    attack and defense double for each successive hit; a miss resets this buff
    """

    def __init__(self):
        super().__init__(
            name="Dragon's Fury",
            description="The power up unleashed the dragon within, a power that "
            "continues to grow. With each successive hit, your attack "
            "and defense increase. A miss will reset this buff.",
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


class ArcaneBlast(PowerUp):
    """Data-driven (arcane_blast.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("arcane_blast.yaml", cls_name="ArcaneBlast")


# Passive ability for Summoner
class EternalConduit(Ability):
    """
    Eternal Conduit (Passive): The Summoner's bond with their summons is so strong that they gain a portion of all 
    healing and buffs their summons receive, and their summons gain a portion of all healing and buffs the Summoner 
    receives.
    """
    def __init__(self):
        super().__init__(
            name="Eternal Conduit",
            description="The Summoner's bond with their summons is so strong that "
            "they gain a portion of all healing and buffs their summons receive, "
            "and their summons gain a portion of all healing and buffs the Summoner"
            " receives.",
            passive=True,
            typ="Skill",
            subtyp="Power Up"
        )

    def special_effect(self, user: Character, *args: Any, **kwargs: Any) -> CombatResult:
        # TODO: actual shared healing/buff logic to be implemented
        return CombatResult(action=self.name, extra={"effect": "shared_healing_and_buffs"})


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


class BladeFatalities:
    """Skill — data-driven (blade_fatalities.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("blade_fatalities.yaml", cls_name="BladeFatalities")


class HolyRetribution:
    """Skill — data-driven (holy_retribution.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("holy_retribution.yaml", cls_name="HolyRetribution")


class GreatGospel:
    """Skill — data-driven (great_gospel.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("great_gospel.yaml", cls_name="GreatGospel")


class DimMak:
    """Data-driven (dim_mak.yaml) – weapon + kill/stun + absorb."""
    def __new__(cls):
        return _load_yaml_ability("dim_mak.yaml", cls_name="DimMak")


class SongInspiration(PowerUp):
    """
    Song of Inspiration (Passive): The Troubadour's presence inspires allies and self, granting a small bonus to all stats
    and occasionally removing negative status effects at the start of combat.
    """
    def __init__(self):
        super().__init__(
            name="Song of Inspiration",
            description="The Troubadour's presence inspires allies and self, granting "
            "a small bonus to all stats and occasionally removing negative status "
            "effects at the start of combat.",
            passive=True,
            typ="Skill",
            subtyp="Power Up"
        )

    def special_effect(self, user: Character, *args: Any, **kwargs: Any) -> CombatResult:
        # TODO: actual stat bonus and status removal logic to be implemented
        return CombatResult(action=self.name, extra={"effect": "stat_bonus_and_status_removal"})


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


class TetraDisaster:
    """Data-driven (tetra_disaster.yaml) – cast all 4 elemental spells + Power Up."""
    def __new__(cls):
        return _load_yaml_ability("tetra_disaster.yaml", cls_name="TetraDisaster")


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
            passive=True,
            typ="Skill",
            subtyp="Power Up"
        )

    def special_effect(self, user: Character, *args: Any, **kwargs: Any) -> CombatResult:
        # TODO: actual companion bonus and intercept/heal logic to be implemented
        return CombatResult(action=self.name, extra={"effect": "companion_bonus_and_intercept"})


# Enemy skills
class Lick:
    """Data-driven (lick.yaml) – weapon hit + random status."""
    def __new__(cls):
        return _load_yaml_ability("lick.yaml", cls_name="Lick")


class AcidSpit:
    """Data-driven (acid_spit.yaml) – magic damage + DOT."""
    def __new__(cls):
        return _load_yaml_ability("acid_spit.yaml", cls_name="AcidSpit")


class Web:
    """Spider web that causes prone – data-driven (Batch 4)."""
    def __new__(cls):
        return _load_yaml_ability("web.yaml", cls_name="Web")


class Howl:
    """Wolf howl that stuns – data-driven (Batch 4)."""
    def __new__(cls):
        return _load_yaml_ability("howl.yaml", cls_name="Howl")


class Shapeshift:
    """Data-driven (shapeshift.yaml) – enemy transforms into random creature."""
    def __new__(cls):
        return _load_yaml_ability("shapeshift.yaml", cls_name="Shapeshift")


class Trip:
    """Trip the enemy prone – data-driven (Batch 4)."""
    def __new__(cls):
        return _load_yaml_ability("trip.yaml", cls_name="Trip")


class NightmareFuel:
    """Data-driven (nightmare_fuel.yaml) – sleep-conditional damage."""
    def __new__(cls):
        return _load_yaml_ability("nightmare_fuel.yaml", cls_name="NightmareFuel")


class WidowsWail:
    """Data-driven (widows_wail.yaml) – inverse-HP damage to both."""
    def __new__(cls):
        return _load_yaml_ability("widows_wail.yaml", cls_name="WidowsWail")


class ThrowRock:
    """Data-driven (throw_rock.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("throw_rock.yaml", cls_name="ThrowRock")


class Stomp:
    """Data-driven (stomp.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("stomp.yaml", cls_name="Stomp")


class Slam:
    """Knocks prone on a critical – data-driven (Batch 4)."""
    def __new__(cls):
        return _load_yaml_ability("slam.yaml", cls_name="Slam")


class Screech:
    """Data-driven (screech.yaml) – damage + permanent Silence."""
    def __new__(cls):
        return _load_yaml_ability("screech.yaml", cls_name="Screech")


class Detonate:
    """Data-driven (detonate.yaml) – self-destruct massive damage."""
    def __new__(cls):
        return _load_yaml_ability("detonate.yaml", cls_name="Detonate")


class Crush:
    """Data-driven (crush.yaml) – grab + crush + throw."""
    def __new__(cls):
        return _load_yaml_ability("crush.yaml", cls_name="Crush")


class ConsumeItem:
    """Data-driven (consume_item.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("consume_item.yaml", cls_name="ConsumeItem")


class DestroyMetal:
    """Data-driven (destroy_metal.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("destroy_metal.yaml", cls_name="DestroyMetal")


class Turtle(Skill):

    def __init__(self):
        super().__init__(
            name="Turtle",
            description="Hunker down into a ball, reducing all damage to 0 and regenerating"
            " health.",
        )
        self.passive = True


class Tunnel:
    """Data-driven (tunnel.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("tunnel.yaml", cls_name="Tunnel")


class Surface:
    """Data-driven (surface.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("surface.yaml", cls_name="Surface")


class GoblinPunch:
    """Data-driven (goblin_punch.yaml) – multi-hit str-diff damage."""
    def __new__(cls):
        return _load_yaml_ability("goblin_punch.yaml", cls_name="GoblinPunch")


class BrainGorge:
    """Data-driven (brain_gorge.yaml) – weapon hit + latch + intel drain."""
    def __new__(cls):
        return _load_yaml_ability("brain_gorge.yaml", cls_name="BrainGorge")


class Counterspell:
    """Data-driven (counterspell.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("counterspell.yaml", cls_name="Counterspell")


class ChooseFate:
    """Data-driven (choose_fate.yaml) – Devil lets player pick his action."""
    def __new__(cls):
        return _load_yaml_ability("choose_fate.yaml", cls_name="ChooseFate")


class BreatheFire:
    """Data-driven (breathe_fire.yaml) – stat-based elemental breath."""
    def __new__(cls):
        return _load_yaml_ability("breathe_fire.yaml", cls_name="BreatheFire")


class DragonBreathFire:
    """Data-driven (dragon_breath_fire.yaml) – charging fire breath."""
    def __new__(cls):
        return _load_yaml_ability("dragon_breath_fire.yaml", cls_name="DragonBreathFire")


class DragonBreathWater:
    """Data-driven (dragon_breath_water.yaml) – charging water breath."""
    def __new__(cls):
        return _load_yaml_ability("dragon_breath_water.yaml", cls_name="DragonBreathWater")


class DragonBreathWind:
    """Data-driven (dragon_breath_wind.yaml) – charging wind breath."""
    def __new__(cls):
        return _load_yaml_ability("dragon_breath_wind.yaml", cls_name="DragonBreathWind")


# ── Companion Ultimate Attacks ────────────────────────────────────────


class TitanicSlam:
    """Data-driven (titanic_slam.yaml) – Patagon ultimate."""
    def __new__(cls):
        return _load_yaml_ability("titanic_slam.yaml", cls_name="TitanicSlam")


class Devour:
    """Data-driven (devour.yaml) – Dilong ultimate."""
    def __new__(cls):
        return _load_yaml_ability("devour.yaml", cls_name="Devour")


class AbsoluteZero:
    """Data-driven (absolute_zero.yaml) – Agloolik ultimate."""
    def __new__(cls):
        return _load_yaml_ability("absolute_zero.yaml", cls_name="AbsoluteZero")


class Eruption:
    """Data-driven (eruption.yaml) – Cacus ultimate."""
    def __new__(cls):
        return _load_yaml_ability("eruption.yaml", cls_name="Eruption")


class MaelstromVortex:
    """Data-driven (maelstrom_vortex.yaml) – Fuath ultimate."""
    def __new__(cls):
        return _load_yaml_ability("maelstrom_vortex.yaml", cls_name="MaelstromVortex")


class Thunderstrike:
    """Data-driven (thunderstrike.yaml) – Izulu ultimate."""
    def __new__(cls):
        return _load_yaml_ability("thunderstrike.yaml", cls_name="Thunderstrike")


class WindShrapnel:
    """Data-driven (wind_shrapnel.yaml) – Hala ultimate."""
    def __new__(cls):
        return _load_yaml_ability("wind_shrapnel.yaml", cls_name="WindShrapnel")


class DivineJudgment:
    """Data-driven (divine_judgment.yaml) – Grigori ultimate."""
    def __new__(cls):
        return _load_yaml_ability("divine_judgment.yaml", cls_name="DivineJudgment")


class Oblivion:
    """Data-driven (oblivion.yaml) – Bardi ultimate."""
    def __new__(cls):
        return _load_yaml_ability("oblivion.yaml", cls_name="Oblivion")


class GrandHeist:
    """Data-driven (grand_heist.yaml) – Kobalos ultimate."""
    def __new__(cls):
        return _load_yaml_ability("grand_heist.yaml", cls_name="GrandHeist")


class Cataclysm:
    """Data-driven (cataclysm.yaml) – Zahhak ultimate."""
    def __new__(cls):
        return _load_yaml_ability("cataclysm.yaml", cls_name="Cataclysm")


class CrushingBlow(Skill):
    """Data-driven (crushing_blow.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("crushing_blow.yaml", cls_name="CrushingBlow")


"""
Spell section
"""


# Spell types
class Attack(Spell):

    def __init__(
            self,
            name: str,
            description: str,
            cost: int,
            dmg_mod: float,
            crit: int,
            ):
        super().__init__(name, description)
        self.cost = cost
        self.dmg_mod = dmg_mod
        self.crit = crit
        self.turns = None

    def cast(self, caster: Character, target: Character=None, cover: bool=False, special: bool=False, fam: bool=False) -> str:
        cast_message = ""
        if not (special or fam 
                or (caster.cls.name == "Wizard" and caster.class_effects["Power Up"].active)
        ):
            caster.mana.current -= self.cost
        if any([target.magic_effects["Ice Block"].active, target.tunnel]):
            return "It has no effect.\n"
        reflect = target.magic_effects["Reflect"].active
        spell_mod = caster.check_mod("magic", enemy=target)
        dodge = target.dodge_chance(caster, spell=True)
        hit = caster.hit_chance(target, typ="magic")
        if target.incapacitated():
            dodge = False
            hit = True
        if dodge and not reflect:
            cast_message += f"{target.name} dodged the {self.name} and was unhurt.\n"
        else:
            if reflect:
                target = caster
                cast_message += f"{self.name} is reflected back at {caster.name}!\n"
            # Calculate base damage first
            crit = 1
            if not random.randint(0, self.crit):
                crit = 2
            crit_per = random.uniform(1, crit)
            damage = int(self.dmg_mod * spell_mod * crit_per)
            # Apply defenses and reductions
            hit, message, damage = target.handle_defenses(caster, damage, cover, typ="Magic")
            cast_message += message
            hit, message, damage = target.damage_reduction(damage, caster, typ=self.subtyp)
            cast_message += message
            if hit:
                if (
                    caster.cls.name == "Archbishop"
                    and caster.class_effects["Power Up"].active
                    and self.subtyp == "Holy"
                ):
                    damage = int(damage * 1.25)
                if damage < 0:
                    target.health.current -= damage
                    cast_message += f"{target.name} absorbs {self.subtyp} and is healed for {abs(damage)} health.\n"
                else:
                    variance = random.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
                    damage = int(damage * variance)
                    if damage <= 0:
                        cast_message += (
                            f"The spell was ineffective and does no damage.\n"
                        )
                        damage = 0
                    elif random.randint(0, target.stats.con // 2) > random.randint(
                        (caster.stats.intel * crit) // 2, (caster.stats.intel * crit)
                    ):
                        damage //= 2
                        if damage > 0:
                            cast_message += f"{target.name} shrugs off the spell and only receives half of the damage.\n"
                            damage_msg = f"{caster.name} damages {target.name} for {damage} hit points"
                            if crit > 1:
                                damage_msg += " (Critical hit!)"
                            cast_message += damage_msg + ".\n"
                        else:
                            cast_message += (
                                f"The spell was ineffective and does no damage.\n"
                            )
                    else:
                        damage_msg = f"{caster.name} damages {target.name} for {damage} hit points"
                        if crit > 1:
                            damage_msg += " (Critical hit!)"
                        cast_message += damage_msg + ".\n"
                    target.health.current -= damage
                    caster._emit_damage_event(
                        target,
                        damage,
                        damage_type=self.subtyp,
                        is_critical=(crit > 1),
                    )
                    if target.is_alive() and damage > 0 and not reflect:
                        cast_message += self.special_effect(
                            caster, target, damage, crit
                        )
                    elif target.is_alive() and damage > 0 and reflect:
                        cast_message += self.special_effect(
                            caster, caster, damage, crit
                        )
                if "Counterspell" in target.spellbook["Spells"] and not random.randint(
                    0, 4
                ):  # TODO
                    cast_message += f"{target.name} uses Counterspell.\n"
                    cast_message += Counterspell().use(target, caster)
            else:
                cast_message += f"The spell misses {target.name}.\n"
            if (
                caster.cls.name == "Wizard"
                and caster.class_effects["Power Up"].active
                and damage > 0
            ):
                cast_message += f"{caster.name} regens {damage} mana.\n"
                caster.mana.current += damage
                if caster.mana.current > caster.mana.max:
                    caster.mana.current = caster.mana.max
        return cast_message


class HolySpell(Spell):

    def __init__(self, name: str, description: str, cost: int, dmg_mod: float, crit: int) -> None:
        super().__init__(name, description)
        self.cost = cost
        self.dmg_mod = dmg_mod
        self.crit = crit
        self.subtyp = "Holy"


class SupportSpell(Spell):
    def __init__(self, name: str, description: str, cost: int) -> None:
        super().__init__(name, description)
        self.cost = cost
        self.subtyp = "Support"


class DeathSpell(Spell):
    def __init__(self, name: str, description: str, cost: int) -> None:
        super().__init__(name, description)
        self.cost = cost
        self.subtyp = "Death"


class StatusSpell(Spell):
    def __init__(self, name: str, description: str, cost: int) -> None:
        super().__init__(name, description)
        self.cost = cost
        self.subtyp = "Status"


class HealSpell(Spell):
    """
    Base class for all heal spells

    Attributes:
        heal(float): base heal amount equal to the percentage of the target's health
        - Heal 1: 0.3 (pro 1 lvl 1)
        - Heal 2: 0.45 (pro 1 lvl 26)
        - Heal 3: 0.6 (pro 3 lvl 1)
        - Hydration: 0.3 (pro 2 lvl 9)
        - Regen 1: 0.2 (pro 1 lvl 8)
        - Regen 2: 0.3 (pro 2 lvl 1)
        - Regen 3: 0.4 (pro 3 lvl 7)
    """

    def __init__(self, name: str, description: str, cost: int, heal: int, crit: int) -> None:
        super().__init__(name, description)
        self.cost = cost
        self.heal = heal
        self.crit = crit
        self.turns = 0
        self.subtyp = "Heal"
        self.combat = False

    def cast(self, caster: Character, target: Character=None, cover: bool=False, special: bool=False, fam: bool=False) -> str:
        """Heal calculation while in combat"""
        cast_message = ""
        if not fam:
            target = caster
        if not (special or fam):
            caster.mana.current -= self.cost
        crit = 1
        heal_mod = caster.check_mod("heal")
        base_heal = target.health.max * self.heal
        heal = int(
            (random.randint(target.health.max // 2, target.health.max) + heal_mod)
            * self.heal
        )
        if self.turns:
            self.hot(target, heal)
        else:
            if not random.randint(0, self.crit):
                cast_message += "Critical Heal!\n"
                crit = 2
            crit_per = random.uniform(1, crit)
            heal = int(heal * crit_per)
            target.health.current += heal
            caster._emit_healing_event(heal, source=self.name)
            cast_message += (
                f"{caster.name} heals {target.name} for {heal} hit points.\n"
            )
            if target.health.current >= target.health.max:
                target.health.current = target.health.max
                cast_message += f"{target.name} is at full health.\n"
        return cast_message


class MovementSpell(Spell):
    def __init__(self, name: str, description: str, cost: int) -> None:
        super().__init__(name, description)
        self.cost = cost
        self.subtyp = "Movement"


class IllusionSpell(Spell):
    """
    subtyp: the subtype of these abilities is 'Illusion', meaning they rely on deception
    """

    def __init__(self, name: str, description: str, cost: int) -> None:
        super().__init__(name, description)
        self.cost = cost
        self.subtyp = "Illusion"


# Spells
class MagicMissile(Attack):
    """Data-driven (magic_missile.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("magic_missile.yaml", cls_name="MagicMissile")


class MagicMissile2(MagicMissile):
    """Data-driven (magic_missile_2.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("magic_missile_2.yaml", cls_name="MagicMissile2")


class MagicMissile3(MagicMissile):
    """Data-driven (magic_missile_3.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("magic_missile_3.yaml", cls_name="MagicMissile3")


class Ultima:
    """Rank 2 Enemy Spell — data-driven (ultima.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("ultima.yaml", cls_name="Ultima")


class Maelstrom:
    """Data-driven (maelstrom.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("maelstrom.yaml", cls_name="Maelstrom")


class Meteor:
    """Data-driven (meteor.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("meteor.yaml", cls_name="Meteor")


class FireSpell(Attack):
    """
    Arcane and elemental fire spells have lower crit but hit harder on average; chance to apply damage over time
    """

    def __init__(self, name: str, description: str, cost: int, dmg_mod: float, crit: int) -> None:
        super().__init__(name, description, cost, dmg_mod, crit)
        self.subtyp = "Fire"

    def special_effect(self, caster: Character, target: Character, damage: int, crit: int) -> str:
        special_str = ""
        if random.randint(0, caster.stats.intel // 2) > random.randint(
            target.stats.wisdom // 4, target.stats.wisdom
        ):
            special_str += f"{target.name} is set ablaze.\n"
            dmg = random.randint(damage // 4, damage // 2)
            target.magic_effects["DOT"].active = True
            target.magic_effects["DOT"].duration = max(
                2, target.magic_effects["DOT"].duration
            )
            target.magic_effects["DOT"].extra = max(
                dmg, target.magic_effects["DOT"].extra
            )
            caster._emit_status_event(target, "DOT", applied=True, duration=target.magic_effects["DOT"].duration, source=self.name)
        return special_str


class Firebolt:
    """Data-driven (firebolt.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("firebolt.yaml", cls_name="Firebolt")


class Fireball:
    """Data-driven (fireball.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("fireball.yaml", cls_name="Fireball")


class Firestorm:
    """Data-driven (firestorm.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("firestorm.yaml", cls_name="Firestorm")


class Scorch:
    """Data-driven (scorch.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("scorch.yaml", cls_name="Scorch")


class MoltenRock:
    """Data-driven (molten_rock.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("molten_rock.yaml", cls_name="MoltenRock")


class Volcano:
    """Data-driven (volcano.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("volcano.yaml", cls_name="Volcano")


class IceSpell(Attack):
    """
    Arcane ice spells have lower average damage but have the highest chance to crit; chance to do extra damage
    """

    def __init__(self, name: str, description: str, cost: int, dmg_mod: float, crit: int) -> None:
        super().__init__(name, description, cost, dmg_mod, crit)
        self.subtyp = "Ice"

    def special_effect(self, caster: Character, target: Character, damage: int, crit: int) -> str:
        special_str = ""
        if random.randint(0, caster.stats.intel // 2) > random.randint(
            target.stats.wisdom // 4, target.stats.wisdom
        ):
            dmg = random.randint(damage // 2, damage)
            special_str += (
                f"{target.name} is chilled to the bone, taking an extra {dmg} damage.\n"
            )
            target.health.current -= dmg
        return special_str


class IceLance:
    """Data-driven (ice_lance.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("ice_lance.yaml", cls_name="IceLance")


class Icicle:
    """Data-driven (icicle.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("icicle.yaml", cls_name="Icicle")


class IceBlizzard:
    """Data-driven (ice_blizzard.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("ice_blizzard.yaml", cls_name="IceBlizzard")


class ElectricSpell(Attack):
    """
    Arcane electric spells have better crit than fire and better damage than ice; chance to stun
    """

    def __init__(self, name: str, description: str, cost: int, dmg_mod: float, crit: int) -> None:
        super().__init__(name, description, cost, dmg_mod, crit)
        self.subtyp = "Electric"

    def special_effect(self, caster: Character, target: Character, damage: int, crit: int) -> str:
        special_str = ""
        if not any(
            [
                "Stun" in target.status_immunity,
                f"Status-Stun" in target.equipment["Pendant"].mod,
                "Status-All" in target.equipment["Pendant"].mod,
            ]
        ):
            att_roll = random.randint(0, caster.stats.intel // 2)
            def_roll = random.randint(target.stats.wisdom // 4, target.stats.wisdom)
            if target.stun_contest_success(caster, att_roll, def_roll):
                special_str += f"{target.name} gets shocked and is stunned.\n"
                target.apply_stun(
                    max(1 + crit, target.status_effects["Stun"].duration),
                    source=self.name,
                    applier=caster,
                )
        return special_str


class Shock:
    """Data-driven (shock.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("shock.yaml", cls_name="Shock")


class Lightning:
    """Data-driven (lightning.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("lightning.yaml", cls_name="Lightning")


class Electrocution:
    """Data-driven (electrocution.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("electrocution.yaml", cls_name="Electrocution")


class WaterJet:
    """Data-driven (water_jet.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("water_jet.yaml", cls_name="WaterJet")


class Aqualung:
    """Rank 1 Enemy Spell — data-driven (aqualung.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("aqualung.yaml", cls_name="Aqualung")


class Tsunami:
    """Rank 2 Enemy Spell — data-driven (tsunami.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("tsunami.yaml", cls_name="Tsunami")


class Hydration:
    def __new__(cls):
        return _load_yaml_ability("hydration.yaml", cls_name="Hydration")


class Tremor:
    """Data-driven (tremor.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("tremor.yaml", cls_name="Tremor")


class Mudslide:
    """Rank 1 Enemy Spell — data-driven (mudslide.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("mudslide.yaml", cls_name="Mudslide")


class Earthquake:
    """Rank 2 Enemy Spell — data-driven (earthquake.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("earthquake.yaml", cls_name="Earthquake")


class Sandstorm:
    """Enemy Spell — data-driven (sandstorm.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("sandstorm.yaml", cls_name="Sandstorm")


class Gust:
    """Data-driven (gust.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("gust.yaml", cls_name="Gust")


class Hurricane:
    """Rank 1 Enemy Spell — data-driven (hurricane.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("hurricane.yaml", cls_name="Hurricane")


class Tornado:
    """Rank 2 Enemy Spell — data-driven (tornado.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("tornado.yaml", cls_name="Tornado")


# Shadow spells
class ShadowBolt:
    """Data-driven (shadow_bolt.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("shadow_bolt.yaml", cls_name="ShadowBolt")


class ShadowBolt2:
    """Data-driven (shadow_bolt_2.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("shadow_bolt_2.yaml", cls_name="ShadowBolt2")


class ShadowBolt3:
    """Data-driven (shadow_bolt_3.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("shadow_bolt_3.yaml", cls_name="ShadowBolt3")


class Corruption:
    """Data-driven (corruption.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("corruption.yaml", cls_name="Corruption")


class Terrify:
    """Data-driven (terrify.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("terrify.yaml", cls_name="Terrify")


# Death spells
class Doom:
    """Data-driven (doom.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("doom.yaml", cls_name="Doom")


class Desoul:
    """Death spell — data-driven (desoul.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("desoul.yaml", cls_name="Desoul")


class Petrify:
    """Death spell — data-driven (petrify.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("petrify.yaml", cls_name="Petrify")


class Disintegrate:
    """Data-driven (disintegrate.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("disintegrate.yaml", cls_name="Disintegrate")


# Holy spells
class Smite:
    """Data-driven (smite.yaml) – weapon strike + holy follow-up."""
    def __new__(cls):
        return _load_yaml_ability("smite.yaml", cls_name="Smite")


class Smite2:
    """Data-driven (smite_2.yaml) – upgraded Smite."""
    def __new__(cls):
        return _load_yaml_ability("smite_2.yaml", cls_name="Smite2")


class Smite3:
    """Data-driven (smite_3.yaml) – upgraded Smite."""
    def __new__(cls):
        return _load_yaml_ability("smite_3.yaml", cls_name="Smite3")


class Holy:
    """Data-driven (holy.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("holy.yaml", cls_name="Holy")


class Holy2:
    """Data-driven (holy_2.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("holy_2.yaml", cls_name="Holy2")


class Holy3:
    """Data-driven (holy_3.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("holy_3.yaml", cls_name="Holy3")


class TurnUndead:
    """Data-driven (turn_undead.yaml) – undead-only kill or holy damage."""
    def __new__(cls):
        return _load_yaml_ability("turn_undead.yaml", cls_name="TurnUndead")


class TurnUndead2:
    """Data-driven (turn_undead_2.yaml) – upgraded Turn Undead."""
    def __new__(cls):
        return _load_yaml_ability("turn_undead_2.yaml", cls_name="TurnUndead2")


# Heal spells
class Heal:
    def __new__(cls):
        return _load_yaml_ability("heal.yaml", cls_name="Heal")


class Heal2:
    def __new__(cls):
        return _load_yaml_ability("heal_2.yaml", cls_name="Heal2")


class Heal3:
    def __new__(cls):
        return _load_yaml_ability("heal_3.yaml", cls_name="Heal3")


class Regen:
    def __new__(cls):
        return _load_yaml_ability("regen.yaml", cls_name="Regen")


class Regen2:
    def __new__(cls):
        return _load_yaml_ability("regen_2.yaml", cls_name="Regen2")


class Regen3:
    def __new__(cls):
        return _load_yaml_ability("regen_3.yaml", cls_name="Regen3")


# Support spells
class Bless:
    def __new__(cls):
        return _load_yaml_ability("bless.yaml", cls_name="Bless")


class Boost:
    def __new__(cls):
        return _load_yaml_ability("boost.yaml", cls_name="Boost")


class Shell:
    def __new__(cls):
        return _load_yaml_ability("shell.yaml", cls_name="Shell")


class Reflect:
    def __new__(cls):
        return _load_yaml_ability("reflect.yaml", cls_name="Reflect")


class Resurrection:
    """Data-driven (resurrection.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("resurrection.yaml", cls_name="Resurrection")


class Cleanse:
    def __new__(cls):
        return _load_yaml_ability("cleanse.yaml", cls_name="Cleanse")


class ResistAll:
    """Data-driven (resist_all.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("resist_all.yaml", cls_name="ResistAll")


class DivineProtection:
    def __new__(cls):
        return _load_yaml_ability("divine_protection.yaml", cls_name="DivineProtection")


class IceBlock:
    def __new__(cls):
        return _load_yaml_ability("ice_block.yaml", cls_name="IceBlock")


class Vulcanize:
    """Data-driven (vulcanize.yaml) – self fire-damage + defense buff."""
    def __new__(cls):
        return _load_yaml_ability("vulcanize.yaml", cls_name="Vulcanize")


class WindSpeed:
    def __new__(cls):
        return _load_yaml_ability("wind_speed.yaml", cls_name="WindSpeed")


# Movement spells
class Sanctuary:
    """Data-driven (sanctuary.yaml) – return to town, full heal."""
    def __new__(cls):
        return _load_yaml_ability("sanctuary.yaml", cls_name="Sanctuary")


class Teleport:
    """Data-driven (teleport.yaml) – set/restore location."""
    def __new__(cls):
        return _load_yaml_ability("teleport.yaml", cls_name="Teleport")


# Illusion spells
class MirrorImage:
    def __new__(cls):
        return _load_yaml_ability("mirror_image.yaml", cls_name="MirrorImage")


class MirrorImage2:
    def __new__(cls):
        return _load_yaml_ability("mirror_image_2.yaml", cls_name="MirrorImage2")


class AstralShift:
    def __new__(cls):
        return _load_yaml_ability("astral_shift.yaml", cls_name="AstralShift")


# Status spells
class Hex:
    """Data-driven (hex.yaml) – multi-status spell (Poison/Blind/Silence)."""
    def __new__(cls):
        return _load_yaml_ability("hex.yaml", cls_name="Hex")


class BlindingFog:
    def __new__(cls):
        return _load_yaml_ability("blinding_fog.yaml", cls_name="BlindingFog")


class PoisonBreath:
    """Rank 2 Enemy Spell — data-driven (poison_breath.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("poison_breath.yaml", cls_name="PoisonBreath")


class DiseaseBreath:
    """Status spell — data-driven (disease_breath.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("disease_breath.yaml", cls_name="DiseaseBreath")


class Sleep:
    def __new__(cls):
        return _load_yaml_ability("sleep.yaml", cls_name="Sleep")


class Stupefy:
    def __new__(cls):
        return _load_yaml_ability("stupefy.yaml", cls_name="Stupefy")


class WeakenMind:
    def __new__(cls):
        return _load_yaml_ability("weaken_mind.yaml", cls_name="WeakenMind")


class Enfeeble:
    def __new__(cls):
        return _load_yaml_ability("enfeeble.yaml", cls_name="Enfeeble")


class Ruin:
    """Status spell — data-driven (ruin.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("ruin.yaml", cls_name="Ruin")


class Dispel:
    def __new__(cls):
        return _load_yaml_ability("dispel.yaml", cls_name="Dispel")


class Silence:
    def __new__(cls):
        return _load_yaml_ability("silence.yaml", cls_name="Silence")


class Berserk:
    def __new__(cls):
        return _load_yaml_ability("berserk.yaml", cls_name="Berserk")


# Enemy spells
class Hellfire:
    """Devil's spell — data-driven (hellfire.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("hellfire.yaml", cls_name="Hellfire")


# Parameters
skill_dict = {
    "Warrior": {
        "3": ShieldSlam,
        "8": PiercingStrike,
        "10": Disarm,
        "15": Charge,
        "23": Parry,
        "25": TrueStrike,
        "28": BattleCry,
    },
    "Weapon Master": {"1": MortalStrike, "6": DoubleStrike, "21": TruePiercingStrike},
    "Berserker": {"5": MortalStrike2, "20": TripleStrike},
    "Paladin": {"6": ShieldBlock, "13": Goad, "18": DoubleStrike},
    "Crusader": {"5": MortalStrike, "22": TripleStrike, "30": TruePiercingStrike},
    "Lancer": {"1": Jump},
    "Dragoon": {"5": TruePiercingStrike, "10": ShieldBlock},
    "Sentinel": {"1": ShieldBlock, "3": Goad},
    "Stalwart Defender": {},
    "Mage": {"25": ManaShield},
    "Sorcerer": {"10": Doublecast, "18": MirrorImage},
    "Wizard": {"5": ManaShield2, "15": Triplecast, "30": MirrorImage2},
    "Warlock": {
        "1": Familiar,
        "5": HealthDrain,
        "9": LifeTap,
        "15": ManaDrain,
        "20": Familiar2,
    },
    "Shadowcaster": {"4": ManaTap, "10": HealthManaDrain, "20": Familiar3},
    "Spellblade": {
        "1": EnhanceBlade,
        "6": ManaSlice,
        "10": ImbueWeapon,
        "15": Parry,
        "21": ElementalStrike,
        "28": TrueStrike,
    },
    "Knight Enchanter": {
        "1": EnhanceArmor,
        "6": ManaTap,
        "10": DoubleStrike,
        "14": ManaSlice2,
        "20": DispelSlash,
        "30": TruePiercingStrike,
    },
    "Summoner": {"1": Summon},
    "Grand Summoner": {"1": Summon2},
    "Footpad": {
        "2": Quickstep,
        "3": Disarm,
        "5": SmokeScreen,
        "6": PocketSand,
        "8": KidneyPunch,
        "10": Steal,
        "12": Backstab,
        "16": DoubleStrike,
        "19": SleepingPowder,
        "22": EvasiveGuard,
        "25": Parry,
    },
    "Thief": {"5": Lockpick, "12": GoldToss, "15": Mug, "20": PoisonStrike},
    "Rogue": {
        "5": SneakAttack,
        "10": SlotMachine,
        "12": TripleStrike,
        "15": MasterLockpick,
    },
    "Inquisitor": {
        "1": Reveal,
        "2": PiercingStrike,
        "5": Inspect,
        "10": ExploitWeakness,
        "14": KeenEye,
        "15": ShieldBlock,
        "22": TrueStrike,
    },
    "Seeker": {"1": Cartography, "16": TripleStrike, "25": TruePiercingStrike},
    "Assassin": {"8": PoisonStrike, "15": Lockpick, "18": TripleStrike},
    "Ninja": {"8": Mug, "25": FlurryBlades},
    "Spell Stealer": {"18": ImbueWeapon},
    "Arcane Trickster": {},
    "Healer": {},
    "Cleric": {"6": ShieldSlam, "12": ShieldBlock, "27": TrueStrike},
    "Templar": {
        "1": Parry,
        "4": PiercingStrike,
        "6": Goad,
        "14": Charge,
        "22": DoubleStrike,
        "30": TruePiercingStrike,
    },
    "Priest": {"10": ManaShield},
    "Archbishop": {"5": Doublecast, "15": ManaShield2},
    "Monk": {
        "1": ChiHeal,
        "3": DoubleStrike,
        "5": LegSweep,
        "7": TrueStrike,
        "10": PurityBody,
        "25": Parry,
    },
    "Master Monk": {"1": Evasion, "10": TripleStrike, "15": PurityBody2},
    "Bard": {},
    "Troubadour": {},
    "Pathfinder": {},
    "Druid": {"2": Transform, "10": Transform2, "15": MortalStrike},
    "Lycan": {"1": Transform3, "11": Charge, "15": BattleCry, "25": MortalStrike2},
    "Diviner": {"1": LearnSpell, "18": Doublecast},
    "Geomancer": {"1": LearnSpell2, "25": Triplecast},
    "Shaman": {
        "1": Totem,
        "4": ElementalStrike,
        "6": PiercingStrike,
        "10": MaelstromWeapon,
        "19": TrueStrike,
        "24": DoubleStrike,
    },
    "Soulcatcher": {
        "1": AbsorbEssence,
        "2": Parry,
        "9": TripleStrike,
        "29": TruePiercingStrike,
    },
    "Ranger": {},
    "Beast Master": {},
}

spell_dict = {
    "Warrior": {},
    "Weapon Master": {},
    "Berserker": {},
    "Paladin": {"1": Heal, "4": Smite, "24": DivineProtection},
    "Crusader": {"3": Smite2, "8": Heal2, "16": Cleanse, "18": Smite3, "20": Dispel},
    "Lancer": {},
    "Dragoon": {},
    "Sentinel": {},
    "Stalwart Defender": {},
    "Mage": {
        "1": Firebolt,
        "5": MagicMissile,
        "8": IceLance,
        "13": Shock,
        "16": Enfeeble,
    },
    "Sorcerer": {
        "2": Icicle,
        "6": Reflect,
        "8": Lightning,
        "10": Sleep,
        "15": Fireball,
        "16": Dispel,
        "18": MagicMissile2,
        "20": WeakenMind,
        "30": IceBlock,
    },
    "Wizard": {
        "4": Firestorm,
        "7": Boost,
        "10": IceBlizzard,
        "15": Electrocution,
        "20": Teleport,
        "25": MagicMissile3,
    },
    "Warlock": {
        "1": ShadowBolt,
        "4": Corruption,
        "10": Terrify,
        "12": ShadowBolt2,
        "15": Doom,
        "19": Dispel,
    },
    "Shadowcaster": {"8": ShadowBolt3, "18": Desoul},
    "Spellblade": {"20": Reflect},
    "Knight Enchanter": {},
    "Summoner": {},
    "Grand Summoner": {},
    "Footpad": {},
    "Thief": {},
    "Rogue": {},
    "Inquisitor": {"3": Dispel, "8": Silence, "12": Enfeeble, "15": Reflect},
    "Seeker": {"1": Teleport, "4": ResistAll, "10": Sanctuary, "16": WeakenMind},
    "Assassin": {},
    "Ninja": {"20": Desoul},
    "Spell Stealer": {"8": WindSpeed, "27": Silence},
    "Arcane Trickster": {"4": WeakenMind},
    "Healer": {"1": Heal, "3": Holy, "8": Regen, "10": TurnUndead, "26": Heal2},
    "Cleric": {
        "1": Smite,
        "5": Bless,
        "14": Cleanse,
        "15": Silence,
        "16": Smite2,
        "19": TurnUndead2,
    },
    "Templar": {"6": Regen2, "10": Smite3, "18": Dispel},
    "Priest": {
        "1": Regen2,
        "3": Holy2,
        "6": Shell,
        "11": Cleanse,
        "15": Bless,
        "17": Dispel,
        "21": Berserk,
    },
    "Archbishop": {
        "1": Heal3,
        "4": Holy3,
        "6": Silence,
        "7": Regen3,
        "20": Resurrection,
    },
    "Monk": {"15": Shell},
    "Master Monk": {"2": Reflect, "12": Dispel},
    "Bard": {},
    "Troubadour": {},
    "Pathfinder": {"1": Tremor, "7": WaterJet, "14": Gust, "19": Scorch},
    "Druid": {"5": Regen},
    "Lycan": {"8": Dispel},
    "Diviner": {"3": Enfeeble, "14": Dispel, "23": Berserk},
    "Geomancer": {"1": Vulcanize, "10": WeakenMind, "15": Boost},
    "Shaman": {"2": Hex,
               "9": Hydration,
               "16": AstralShift},
    "Soulcatcher": {"6": Dispel, "12": Desoul},
    "Ranger": {},
    "Beast Master": {},
}
