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
            ) -> None:
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
            ) -> None:
        """
        Args:
            name (str): name of the ability
            description (str): description of the ability that explains what it does in so many words
            weapon (bool): boolean indicating whether the ability is a weapon skill
        """
        super().__init__(name, description)
        self.typ = "Skill"
        self.weapon = weapon

    def use(
        self,
        user: Character,
        target: Character | None = None,
        **kwargs: Any,
    ) -> CombatResult:
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
        return self._reset_result(actor=user, target=target)


class CallContract(Skill):
    """Demonologist class skill for bargaining with the active fiend patron."""

    def __init__(self) -> None:
        super().__init__(
            name="Call Contract",
            description="Call on the active fiend patron and bargain for aid.",
        )
        self.subtyp = "Class"
        self.cost = 0

    def use(
        self,
        user: Character,
        target: Character | None = None,
        **kwargs: Any,
    ) -> str:
        from .classes import demonologist

        super().use(user, target, **kwargs)
        intent = kwargs.get("intent") or getattr(self, "pending_intent", None) or "Harm"
        if hasattr(self, "pending_intent"):
            self.pending_intent = None
        return demonologist.resolve_contract(user, target, intent)


class Redeem(Skill):
    """Vow of Redemption skill that attempts a mercy victory."""

    def __init__(self) -> None:
        super().__init__(
            name="Redeem",
            description="Attempt a mercy victory against a wounded non-boss foe.",
        )
        self.subtyp = "Class"
        self.cost = 0

    def use(
        self,
        user: Character,
        target: Character | None = None,
        **kwargs: Any,
    ) -> str:
        from .classes import paladin

        super().use(user, target, **kwargs)
        if target is None:
            return "There is no foe to redeem.\n"
        return paladin.attempt_redeem(user, target, rng=kwargs.get("rng"))


class Challenge(Skill):
    """Vow of Conquest skill that names a challenged foe."""

    def __init__(self) -> None:
        super().__init__(
            name="Challenge",
            description="Mark the current enemy as your Challenged Foe for 3 turns.",
        )
        self.subtyp = "Class"
        self.cost = 0

    def use(
        self,
        user: Character,
        target: Character | None = None,
        **kwargs: Any,
    ) -> str:
        from .classes import paladin

        super().use(user, target, **kwargs)
        if target is None:
            return "There is no foe to challenge.\n"
        return paladin.start_challenge(user, target)


class Interpose(Skill):
    """Vow of Protection skill that prepares a guarded block."""

    def __init__(self) -> None:
        super().__init__(
            name="Interpose",
            description="Enter a guarded stance for 2 turns and strengthen the next block.",
        )
        self.subtyp = "Class"
        self.cost = 0

    def use(
        self,
        user: Character,
        target: Character | None = None,
        **kwargs: Any,
    ) -> str:
        from .classes import paladin

        super().use(user, target, **kwargs)
        return paladin.start_interpose(user)


class JudgmentRiposte(Skill):
    """Vow of Retribution skill that prepares a retaliatory strike."""

    def __init__(self) -> None:
        super().__init__(
            name="Judgment Riposte",
            description="Prepare a Holy counterattack against the next enemy attack.",
        )
        self.subtyp = "Class"
        self.cost = 0

    def use(
        self,
        user: Character,
        target: Character | None = None,
        **kwargs: Any,
    ) -> str:
        from .classes import paladin

        super().use(user, target, **kwargs)
        return paladin.start_riposte(user)


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
            ) -> None:
        """
        Args:
            name (str): name of the ability
            description (str): description of the ability that explains what it does in so many words
            school (str | None): the school of magic to which this spell belongs
        """
        super().__init__(name, description)
        self.typ: str = "Spell"
        self.school = school

    def cast(
        self,
        user: Character,
        target: Character | None = None,
        **kwargs: Any,
    ) -> CombatResult:
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
        return self._reset_result(actor=user, target=target)


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
    """Data-driven (shield_slam.yaml) - str+shield damage + stun."""
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
    """Data-driven (jump.yaml) - leap attack with full modification system."""
    def __new__(cls):
        return _load_yaml_ability("jump.yaml", cls_name="Jump")


class Doublecast:
    """Data-driven (doublecast.yaml) - cast 2 spells in a single turn."""
    def __new__(cls):
        return _load_yaml_ability("doublecast.yaml", cls_name="Doublecast")


class Triplecast:
    """Data-driven (triplecast.yaml) - cast 3 spells in a single turn."""
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


class _PassiveSkill(Class):
    def __init__(self, name: str, description: str) -> None:
        super().__init__(name=name, description=description)
        self.passive = True
        self.cost = 0


class MonkeyGrip(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Monkey Grip",
            "Your two-handed dual wielding becomes steadier, reducing its accuracy and damage penalties.",
        )


class MonkeyGrip2(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Monkey Grip 2",
            "Your two-handed dual wielding is fully stabilized, removing its accuracy and damage penalties.",
        )


class PolearmProficiency(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Polearm Proficiency",
            "You can wield a two-handed polearm with a shield, but your accuracy and damage suffer.",
        )


class PolearmExcellence(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Polearm Excellence",
            "You can wield a two-handed polearm with a shield without accuracy or damage penalties.",
        )


class PolearmMastery(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Polearm Mastery",
            "Your one-handed polearm technique grants bonus accuracy and damage.",
        )


class _WeaponArt(Class):
    def __init__(self, name: str, description: str):
        super().__init__(name=name, description=description)
        self.cost = {
            "Iron Palm": 6,
            "Hemorrhage": 7,
            "Riposte Line": 7,
            "Low Sweep": 7,
            "Guard Cleaver": 9,
            "Reaver's Mark": 9,
            "Brace": 8,
            "Anvil Strike": 10,
        }.get(name, 0)
        self.weapon = True

    def use(
        self,
        user: Character,
        target: Character | None = None,
        **kwargs: Any,
    ) -> str:
        from .classes import grandmaster

        super().use(user, target, **kwargs)
        if target is None:
            return f"{self.name} needs a target.\n"
        return grandmaster.perform_weapon_art(user, target, self.name)


class IronPalm(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Iron Palm",
            "A fist discipline art that disrupts the target's attack and hardens your stance as mastery grows.",
        )


class Hemorrhage(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Hemorrhage",
            "A dagger discipline art that opens and worsens bleeding wounds.",
        )


class RiposteLine(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Riposte Line",
            "A sword discipline art that strikes and prepares a brief counter line.",
        )


class LowSweep(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Low Sweep",
            "A club discipline art that disrupts footing with speed pressure and prone chances.",
        )


class GuardCleaver(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Guard Cleaver",
            "A longsword discipline art that cuts through and weakens guard.",
        )


class ReaversMark(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Reaver's Mark",
            "A battle axe discipline art that marks a foe to take increased weapon pressure.",
        )


class Brace(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Brace",
            "A polearm discipline art that prepares a defensive counter stance.",
        )


class AnvilStrike(_WeaponArt):
    def __init__(self):
        super().__init__(
            "Anvil Strike",
            "A hammer discipline art that crushes defense and can suppress guard at mastery.",
        )


class FavoredEnemy(_PassiveSkill):
    def __init__(self):
        super().__init__("Favored Enemy", "You fight your most hunted enemy type with practiced precision.")


class FinalAssault(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Final Assault",
            "When a melee blow would kill you, counterattack; if the attacker falls, stabilize at 1 HP.",
        )


class LastStand(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Last Stand",
            "Increase defense and block strength at the expense of attack power.",
        )


class _MartialStrike(MartialArts):
    status_name: str | None = None
    damage_mod: float = 1.0

    def __init__(self, name: str, description: str, cost: int = 8):
        super().__init__(name=name, description=description, weapon=True)
        self.cost = cost

    def _has_martial_weapon(self, user: Character) -> bool:
        return any(
            getattr(user.equipment.get(slot), "subtyp", None) in {"Fist", "None"}
            for slot in ("Weapon", "OffHand")
        )

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        super().use(user, target, **kwargs)
        if target is None:
            return "There is no target.\n"
        if not self._has_martial_weapon(user):
            return f"{user.name} needs a free hand or fist weapon to use {self.name}.\n"
        user.mana.current -= self.cost
        msg, hit, _crit = user.weapon_damage(target, dmg_mod=self.damage_mod, use_offhand=False)
        if hit and self.status_name and target.is_alive() and not target.has_status_protection(self.status_name):
            effect_dict = target.effect_handler(self.status_name)
            effect_dict[self.status_name].active = True
            effect_dict[self.status_name].duration = max(effect_dict[self.status_name].duration, 2)
            msg += f"{target.name} is affected by {self.status_name.lower()}.\n"
        return msg


class Uppercut(_MartialStrike):
    damage_mod = 1.25
    def __init__(self): super().__init__("Uppercut", "A rising martial strike that deals increased damage.", 8)


class Headbutt(_MartialStrike):
    status_name = "Stun"
    damage_mod = 1.0
    def __init__(self): super().__init__("Headbutt", "A close strike that can stun.", 6)


class DrunkenBrawler(_PassiveSkill):
    def __init__(self):
        super().__init__(
            "Drunken Brawler",
            "After using a potion, your next turn gains bonus damage and critical chance.",
        )


class Hyakuretsukyaku(_MartialStrike):
    def __init__(self): super().__init__("Hyakuretsukyaku", "A rushing flurry of kicks.", 14)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        MartialArts.use(self, user, target, **kwargs)
        if target is None:
            return "There is no target.\n"
        if not self._has_martial_weapon(user):
            return f"{user.name} needs a free hand or fist weapon to use {self.name}.\n"
        user.mana.current -= self.cost
        msg = ""
        for _ in range(4):
            hit_msg, _hit, _crit = user.weapon_damage(target, dmg_mod=0.45, use_offhand=False)
            msg += hit_msg
            if not target.is_alive():
                break
        return msg


class SpinningBackElbow(_MartialStrike):
    status_name = "Blind"
    damage_mod = 1.2
    def __init__(self): super().__init__("Spinning Back Elbow", "A turning blow that can blind.", 10)


class Suplex(_MartialStrike):
    status_name = "Prone"
    damage_mod = 1.35
    def __init__(self): super().__init__("Suplex", "A crushing throw that can knock the target prone.", 12)


class Hadouken(_MartialStrike):
    damage_mod = 1.4
    def __init__(self): super().__init__("Hadouken", "A focused chi strike delivered at range.", 16)


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


class StealSpell(Class):
    """Steal an enemy spell onto a Blank Scroll."""

    def __init__(self):
        super().__init__(
            name="Steal Spell",
            description="Inscribes one of the target's spells onto a Blank Scroll.",
        )
        self.cost = 8

    def use(
        self,
        user: Character,
        target: Character | None = None,
        **kwargs: Any,
    ) -> str:
        from .classes import spell_stealer

        if target is None:
            return "There is no spell to steal.\n"
        _success, message = spell_stealer.steal_spell(user, target)
        if _success:
            from .classes import promotion_kits

            message += promotion_kits.gain_stolen_charge(user, "Steal Spell")
        return message


class StealSpell2(Class):
    """Chance to permanently learn one stealable enemy spell."""

    def __init__(self):
        super().__init__(
            name="Steal Spell 2",
            description="Attempt to permanently learn one of the target's stealable spells.",
        )
        self.cost = 22

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import spell_stealer

        super().use(user, target, **kwargs)
        if target is None:
            return "There is no spell to steal.\n"
        spell_classes = spell_stealer.eligible_spell_classes(target)
        spell_classes = [
            spell_cls for spell_cls in spell_classes
            if spell_cls().name not in user.spellbook.get("Spells", {})
        ]
        if not spell_classes:
            return f"{target.name} has no new spell to learn.\n"
        user.mana.current -= self.cost
        chance = min(0.75, 0.20 + ((user.stats.intel + user.stats.dex) * 0.01))
        if random.random() > chance:
            return f"{user.name} fails to bind the stolen spell.\n"
        spell_cls = random.choice(spell_classes)
        spell = spell_cls()
        user.spellbook["Spells"][spell.name] = spell
        from .classes import promotion_kits

        return (
            f"{user.name} permanently learns {spell.name}.\n"
            + promotion_kits.gain_stolen_charge(user, "Steal Spell 2")
        )


class StealAsWell(Class):
    """Marker skill used by the Steal As Well combat action."""

    def __init__(self):
        super().__init__(
            name="Steal As Well",
            description="Cast an attack spell and attempt to steal after it lands.",
        )
        self.cost = 0

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        return "Choose Steal As Well from the combat action menu to weave theft into a spell.\n"


class SongValor(Class):
    """Begin Song of Valor."""

    def __init__(self):
        super().__init__(
            name="Song of Valor",
            description="Perform a 3-turn song that raises weapon and magic damage.",
        )
        self.cost = 0

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import bard

        _success, message = bard.start_song(user, "Valor")
        return message


class SongShelter(Class):
    """Begin Song of Shelter."""

    def __init__(self):
        super().__init__(
            name="Song of Shelter",
            description="Perform a 3-turn song that reduces incoming damage.",
        )
        self.cost = 0

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import bard

        _success, message = bard.start_song(user, "Shelter")
        return message


class SongRenewal(Class):
    """Begin Song of Renewal."""

    def __init__(self):
        super().__init__(
            name="Song of Renewal",
            description="Perform a 3-turn song that restores HP and MP each turn.",
        )
        self.cost = 0

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import bard

        _success, message = bard.start_song(user, "Renewal")
        return message


class _ComposeSong(Class):
    sheet_cls_name = ""

    def __init__(self, name: str, sheet_cls_name: str):
        song_name = name.removeprefix("Compose ")
        super().__init__(
            name=name,
            description=f"Compose {song_name} into one-use sheet music from the character menu.",
        )
        self.cost = 0
        self.song_name = song_name
        self.sheet_cls_name = sheet_cls_name

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import bard

        _success, message = bard.compose_sheet_music(user, self.song_name)
        return message

    def use_out(self, game_or_user) -> str:
        user = getattr(game_or_user, "player_char", game_or_user)
        return self.use(user)


class ComposeBattleHymn(_ComposeSong):
    def __init__(self): super().__init__("Compose Battle Hymn", "BattleHymnSheet")


class ComposeOdeToTheRamparts(_ComposeSong):
    def __init__(self): super().__init__("Compose Ode to the Ramparts", "RampartsOdeSheet")


class ComposeSymphonyOfDisfunction(_ComposeSong):
    def __init__(self): super().__init__("Compose Symphony of Disfunction", "DysfunctionSymphonySheet")


class ComposeLowDefenseRhapsody(_ComposeSong):
    def __init__(self): super().__init__("Compose Low-defense-ian Rhapsody", "LowDefenseRhapsodySheet")


class ComposeSlowRide(_ComposeSong):
    def __init__(self): super().__init__("Compose Slow Ride", "SlowRideSheet")


class ComposeBonesThugsHarmony(_ComposeSong):
    def __init__(self): super().__init__("Compose Bones, Thugs, and Harmony", "BonesThugsHarmonySheet")


class ComposeScoresAndScoresScore(_ComposeSong):
    def __init__(self): super().__init__("Compose Scores and Scores Score", "ScoresAndScoresScoreSheet")


class ComposeGoldTrigger(_ComposeSong):
    def __init__(self): super().__init__("Compose Gold Trigger", "GoldTriggerSheet")


class ComposeChorusTime(_ComposeSong):
    def __init__(self): super().__init__("Compose Chorus Time", "ChorusTimeSheet")


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


class ThreadedCast(_PromotionActive):
    def __init__(self):
        super().__init__("Threaded Cast", "Spend Foresight Threads to mark the next eligible spell payoff.", 8)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import promotion_kits

        return promotion_kits.threaded_cast(user)


class Eclipse(_PromotionActive):
    def __init__(self):
        super().__init__("Eclipse", "Spend Umbral Debt to enter a short shadow form.", 0)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import promotion_kits

        return promotion_kits.eclipse(user)


class HoldTheLine(_PromotionActive):
    def __init__(self):
        super().__init__("Hold the Line", "Enter a shield stance that improves block and mitigation.", 0)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import promotion_kits

        return promotion_kits.hold_the_line(user)


class Bulwark(_PromotionActive):
    def __init__(self):
        super().__init__("Bulwark", "Spend Resolve for a short mitigation barrier.", 0)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import promotion_kits

        return promotion_kits.bulwark(user)


class ShieldRiposte(_PromotionActive):
    def __init__(self):
        super().__init__("Shield Riposte", "Spend Resolve for a controlled shield counter.", 0)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import promotion_kits

        return promotion_kits.shield_riposte(user, target)


class SanctuaryWard(_PromotionActive):
    def __init__(self):
        super().__init__("Sanctuary Ward", "Spend Devotion for a brief protective ward.", 8)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import promotion_kits

        return promotion_kits.sanctuary_ward(user)


class RelicAegis(_PromotionActive):
    def __init__(self):
        super().__init__("Relic Aegis", "Spend Templar Devotion for stronger shielded protection.", 12)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import promotion_kits

        return promotion_kits.relic_aegis(user)


class Supplication(_PromotionActive):
    def __init__(self):
        super().__init__("Supplication", "Spend Prayer on a targeted divine support pulse.", 10)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import promotion_kits

        return promotion_kits.supplication(user, target)


class GreatBenediction(_PromotionActive):
    def __init__(self):
        super().__init__("Great Benediction", "Spend Prayer for several turns of proactive divine support.", 18)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import promotion_kits

        return promotion_kits.great_benediction(user)


class DimMak(_PromotionActive):
    def __init__(self):
        super().__init__("Dim Mak", "Spend full Ki for a high-impact martial finisher.", 18)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import promotion_kits

        return promotion_kits.dim_mak(user, target)


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
        from .classes import promotion_kits

        return promotion_kits.fourfold_surge(user, target)


class TotemSurge(_PromotionActive):
    def __init__(self):
        super().__init__("Totem Surge", "Spend Totem Resonance to force the active Totem pulse.", 10)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import promotion_kits

        return promotion_kits.totem_surge(user, target)


class ConduitCommand(_PromotionActive):
    def __init__(self):
        super().__init__("Conduit Command", "Empower the active summon's next non-Recall action.", 10)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import promotion_kits

        return promotion_kits.conduit_command(user)


class _InvokeSummon(_PromotionActive):
    summon_name = ""

    def __init__(self, summon_name: str):
        self.summon_name = summon_name
        super().__init__(f"Invoke {summon_name}", f"Borrow {summon_name}'s trusted invocation.", 12)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import promotion_kits

        return promotion_kits.invoke_summon(user, target, self.summon_name)


class InvokePatagon(_InvokeSummon):
    def __init__(self): super().__init__("Patagon")


class InvokeDilong(_InvokeSummon):
    def __init__(self): super().__init__("Dilong")


class InvokeAgloolik(_InvokeSummon):
    def __init__(self): super().__init__("Agloolik")


class InvokeCacus(_InvokeSummon):
    def __init__(self): super().__init__("Cacus")


class InvokeFuath(_InvokeSummon):
    def __init__(self): super().__init__("Fuath")


class InvokeIzulu(_InvokeSummon):
    def __init__(self): super().__init__("Izulu")


class InvokeHala(_InvokeSummon):
    def __init__(self): super().__init__("Hala")


class InvokeGrigori(_InvokeSummon):
    def __init__(self): super().__init__("Grigori")


class InvokeBardi(_InvokeSummon):
    def __init__(self): super().__init__("Bardi")


class InvokeKobalos(_InvokeSummon):
    def __init__(self): super().__init__("Kobalos")


class InvokeZahhak(_InvokeSummon):
    def __init__(self): super().__init__("Zahhak")


class _BeastCommand(_PromotionActive):
    command_name = ""

    def __init__(self, name: str):
        self.command_name = name
        super().__init__(name, f"Order the tamed companion to {name.lower()}.", 0)

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import promotion_kits

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
        from .classes import promotion_kits

        return promotion_kits.winged_pounce(user, target)


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
    """Data-driven (kidney_punch.yaml) - weapon hit + stun."""
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
    """Data-driven (poison_strike.yaml) - weapon hit + poison."""
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


class Zephyrstrike(Offensive):
    """
    Passive martial timing; future tuning may hook this into wind/polearm crits.
    """

    def __init__(self):
        super().__init__(
            name="Zephyrstrike",
            description="You strike with the timing of a sudden gale.",
        )
        self.passive = True


class Retaliate(Defensive):
    """
    Passive counter-stance marker for Sentinel follow-up tuning.
    """

    def __init__(self):
        super().__init__(
            name="Retaliate",
            description="Your skill with a shield makes quick responses your forte.",
        )
        self.passive = True


class DefensiveRegen(Defensive):
    """
    Passive endurance marker for defensive regeneration follow-up tuning.
    """

    def __init__(self):
        super().__init__(
            name="Defensive Regen",
            description="You recover best when holding a defensive line.",
        )
        self.passive = True


class Posturing(Defensive):
    """
    Passive guard-presence marker for Crusader follow-up tuning.
    """

    def __init__(self):
        super().__init__(
            name="Posturing",
            description="You know how to present an impossible target.",
        )
        self.passive = True


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
        self.cost = 0

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import ability_mechanics

        super().use(user, target, **kwargs)
        user.mana.current -= self.cost
        return ability_mechanics.attempt_tame(user, target, rng=kwargs.get("rng", random))


class HealSummon(Class):
    def __init__(self):
        super().__init__("Heal Summon", "Restore HP and MP to all owned summons.")
        self.cost = 18

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import ability_mechanics

        super().use(user, target, **kwargs)
        user.mana.current -= self.cost
        return ability_mechanics.heal_all_summons(user)

    def use_out(self, game_or_user) -> str:
        user = getattr(game_or_user, "player_char", game_or_user)
        return self.use(user)


class RaiseSummon(Class):
    def __init__(self):
        super().__init__("Raise Summon", "Revive all fallen owned summons.")
        self.cost = 30

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import ability_mechanics

        super().use(user, target, **kwargs)
        user.mana.current -= self.cost
        return ability_mechanics.raise_all_summons(user)

    def use_out(self, game_or_user) -> str:
        user = getattr(game_or_user, "player_char", game_or_user)
        return self.use(user)


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
    """Data-driven (exploit_weakness.yaml) - weakness detection + weapon."""
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


class ThirdEye(Truth):
    """
    Passive insight marker for future Seeker/Inquisitor perception tuning.
    """

    def __init__(self):
        super().__init__(
            name="Third Eye",
            description="You sense threats and hidden truths before they fully reveal themselves.",
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
    """Sweep the leg, trip the enemy - data-driven (Batch 4)."""
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


class PiousBounty(Class):
    """
    Passive divine-reward marker for future Healer-line bounty tuning.
    """

    def __init__(self):
        super().__init__(
            name="Pious Bounty",
            description="Your devotion draws extra providence from righteous victories.",
        )
        self.passive = True


# Luck
class GoldToss:
    """Data-driven (gold_toss.yaml) - gold-based unblockable damage."""
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


class FrozenArmor(PowerUp):
    """Sorcerer passive: Ice mastery hardens into a small defensive ward."""

    def __init__(self):
        super().__init__(
            name="Frozen Armor",
            description="Ice mastery sheaths the Sorcerer in a thin frost ward, "
            "slightly reducing incoming damage while Ice affinity is mastered.",
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


class AbyssalCovenant(PowerUp):
    """Skill — data-driven (abyssal_covenant.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("abyssal_covenant.yaml", cls_name="AbyssalCovenant")


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
        from .classes import promotion_kits

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


# Enemy skills
class Lick:
    """Data-driven (lick.yaml) - weapon hit + random status."""
    def __new__(cls):
        return _load_yaml_ability("lick.yaml", cls_name="Lick")


class AcidSpit:
    """Data-driven (acid_spit.yaml) - magic damage + DOT."""
    def __new__(cls):
        return _load_yaml_ability("acid_spit.yaml", cls_name="AcidSpit")


class Web:
    """Spider web that causes prone - data-driven (Batch 4)."""
    def __new__(cls):
        return _load_yaml_ability("web.yaml", cls_name="Web")


class Howl:
    """Wolf howl that stuns - data-driven (Batch 4)."""
    def __new__(cls):
        return _load_yaml_ability("howl.yaml", cls_name="Howl")


class Shapeshift:
    """Data-driven (shapeshift.yaml) - enemy transforms into random creature."""
    def __new__(cls):
        return _load_yaml_ability("shapeshift.yaml", cls_name="Shapeshift")


class Trip:
    """Trip the enemy prone - data-driven (Batch 4)."""
    def __new__(cls):
        return _load_yaml_ability("trip.yaml", cls_name="Trip")


class NightmareFuel:
    """Data-driven (nightmare_fuel.yaml) - sleep-conditional damage."""
    def __new__(cls):
        return _load_yaml_ability("nightmare_fuel.yaml", cls_name="NightmareFuel")


class WidowsWail:
    """Data-driven (widows_wail.yaml) - inverse-HP damage to both."""
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
    """Knocks prone on a critical - data-driven (Batch 4)."""
    def __new__(cls):
        return _load_yaml_ability("slam.yaml", cls_name="Slam")


class Screech:
    """Data-driven (screech.yaml) - damage + permanent Silence."""
    def __new__(cls):
        return _load_yaml_ability("screech.yaml", cls_name="Screech")


class Detonate:
    """Data-driven (detonate.yaml) - self-destruct massive damage."""
    def __new__(cls):
        return _load_yaml_ability("detonate.yaml", cls_name="Detonate")


class Crush:
    """Data-driven (crush.yaml) - grab + crush + throw."""
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
    """Data-driven (goblin_punch.yaml) - multi-hit str-diff damage."""
    def __new__(cls):
        return _load_yaml_ability("goblin_punch.yaml", cls_name="GoblinPunch")


class BrainGorge:
    """Data-driven (brain_gorge.yaml) - weapon hit + latch + intel drain."""
    def __new__(cls):
        return _load_yaml_ability("brain_gorge.yaml", cls_name="BrainGorge")


class Counterspell:
    """Data-driven (counterspell.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("counterspell.yaml", cls_name="Counterspell")


class ChooseFate:
    """Data-driven (choose_fate.yaml) - Devil lets player pick his action."""
    def __new__(cls):
        return _load_yaml_ability("choose_fate.yaml", cls_name="ChooseFate")


class VesperionChooseFate:
    """Data-driven (vesperion_choose_fate.yaml) - Vesperion's choice pressure."""
    def __new__(cls):
        return _load_yaml_ability("vesperion_choose_fate.yaml", cls_name="VesperionChooseFate")


class BreatheFire:
    """Data-driven (breathe_fire.yaml) - stat-based elemental breath."""
    def __new__(cls):
        return _load_yaml_ability("breathe_fire.yaml", cls_name="BreatheFire")


class DragonBreathFire:
    """Data-driven (dragon_breath_fire.yaml) - charging fire breath."""
    def __new__(cls):
        return _load_yaml_ability("dragon_breath_fire.yaml", cls_name="DragonBreathFire")


class DragonBreathWater:
    """Data-driven (dragon_breath_water.yaml) - charging water breath."""
    def __new__(cls):
        return _load_yaml_ability("dragon_breath_water.yaml", cls_name="DragonBreathWater")


class DragonBreathWind:
    """Data-driven (dragon_breath_wind.yaml) - charging wind breath."""
    def __new__(cls):
        return _load_yaml_ability("dragon_breath_wind.yaml", cls_name="DragonBreathWind")


# ── Companion Ultimate Attacks ────────────────────────────────────────


class TitanicSlam:
    """Data-driven (titanic_slam.yaml) - Patagon ultimate."""
    def __new__(cls):
        return _load_yaml_ability("titanic_slam.yaml", cls_name="TitanicSlam")


class Devour:
    """Data-driven (devour.yaml) - Dilong ultimate."""
    def __new__(cls):
        return _load_yaml_ability("devour.yaml", cls_name="Devour")


class AbsoluteZero:
    """Data-driven (absolute_zero.yaml) - Agloolik ultimate."""
    def __new__(cls):
        return _load_yaml_ability("absolute_zero.yaml", cls_name="AbsoluteZero")


class Eruption:
    """Data-driven (eruption.yaml) - Cacus ultimate."""
    def __new__(cls):
        return _load_yaml_ability("eruption.yaml", cls_name="Eruption")


class MaelstromVortex:
    """Data-driven (maelstrom_vortex.yaml) - Fuath ultimate."""
    def __new__(cls):
        return _load_yaml_ability("maelstrom_vortex.yaml", cls_name="MaelstromVortex")


class Thunderstrike:
    """Data-driven (thunderstrike.yaml) - Izulu ultimate."""
    def __new__(cls):
        return _load_yaml_ability("thunderstrike.yaml", cls_name="Thunderstrike")


class WindShrapnel:
    """Data-driven (wind_shrapnel.yaml) - Hala ultimate."""
    def __new__(cls):
        return _load_yaml_ability("wind_shrapnel.yaml", cls_name="WindShrapnel")


class DivineJudgment:
    """Data-driven (divine_judgment.yaml) - Grigori ultimate."""
    def __new__(cls):
        return _load_yaml_ability("divine_judgment.yaml", cls_name="DivineJudgment")


class Oblivion:
    """Data-driven (oblivion.yaml) - Bardi ultimate."""
    def __new__(cls):
        return _load_yaml_ability("oblivion.yaml", cls_name="Oblivion")


class GrandHeist:
    """Data-driven (grand_heist.yaml) - Kobalos ultimate."""
    def __new__(cls):
        return _load_yaml_ability("grand_heist.yaml", cls_name="GrandHeist")


class Cataclysm:
    """Data-driven (cataclysm.yaml) - Zahhak ultimate."""
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
            ) -> None:
        super().__init__(name, description)
        self.cost = cost
        self.dmg_mod = dmg_mod
        self.crit = crit
        self.turns = None

    def cast(
        self,
        caster: Character,
        target: Character | None = None,
        cover: bool = False,
        special: bool = False,
        fam: bool = False,
    ) -> str:
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

    def _apply_instant_healing(
        self,
        caster: Character,
        target: Character,
        heal: int,
    ) -> int:
        """Apply a rolled heal after target modifiers and return actual healing."""
        heal = int(heal * target.healing_received_multiplier())
        actual_heal = max(0, min(heal, target.health.max - target.health.current))
        target.health.current += actual_heal
        caster._emit_healing_event(actual_heal, source=self.name)
        return actual_heal

    def cast(
        self,
        caster: Character,
        target: Character | None = None,
        cover: bool = False,
        special: bool = False,
        fam: bool = False,
    ) -> str:
        """Heal calculation while in combat"""
        cast_message = ""
        if not fam:
            target = caster
        if not (special or fam):
            caster.mana.current -= self.cost
        crit = 1
        heal_mod = caster.check_mod("heal")
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
            actual_heal = self._apply_instant_healing(caster, target, heal)
            cast_message += (
                f"{caster.name} heals {target.name} for {actual_heal} hit points.\n"
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


def _inventory_count(character: Character, item_name: str) -> int:
    return len(getattr(character, "inventory", {}).get(item_name, []) or [])


def _consume_inventory_item(character: Character, item_name: str) -> bool:
    stack = getattr(character, "inventory", {}).get(item_name, [])
    if not stack:
        return False
    character.modify_inventory(stack[0], subtract=True)
    return True


def _simple_spell_damage(caster: Character, target: Character, *, dmg_mod: float, typ: str) -> tuple[str, int]:
    if target is None:
        return "There is no target.\n", 0
    if target.magic_effects["Ice Block"].active or target.tunnel:
        return "It has no effect.\n", 0
    guaranteed = bool(getattr(caster, "_twist_fate_success", False))
    if guaranteed:
        caster._twist_fate_success = False
    if not guaranteed and target.dodge_chance(caster, spell=True) > random.random():
        return f"{target.name} dodged the spell and was unhurt.\n", 0
    spell_mod = caster.check_mod("magic", enemy=target)
    damage = max(1, int(spell_mod * dmg_mod))
    hit, msg, damage = target.damage_reduction(damage, caster, typ=typ)
    if not hit:
        return msg, 0
    variance = random.uniform(DAMAGE_VARIANCE_LOW, DAMAGE_VARIANCE_HIGH)
    damage = max(0, int(damage * variance))
    target.health.current -= damage
    return msg + f"{caster.name} damages {target.name} for {damage} hit points.\n", damage


class _ReagentSpell(Spell):
    required_items: tuple[str, ...] = ()

    def _consume_reagents(self, user: Character) -> str | None:
        missing = [item for item in self.required_items if _inventory_count(user, item) <= 0]
        if missing:
            return f"{user.name} needs {', '.join(missing)} to cast {self.name}.\n"
        for item in self.required_items:
            _consume_inventory_item(user, item)
        return None

    def _consume_reagent(self, user: Character, item_name: str) -> str | None:
        if _inventory_count(user, item_name) <= 0:
            return f"{user.name} needs {item_name} to cast {self.name}.\n"
        _consume_inventory_item(user, item_name)
        return None


class PlantSeeds(_ReagentSpell):
    reagent_effects = ("Acorn", "Vine Seed", "Fungus Spore")

    def __init__(self):
        super().__init__(
            "Plant Seeds",
            "Spread seeds of life around the battlefield; each seed changes the growth.",
            school="Nature",
        )
        self.cost = 0
        self.subtyp = "Earth"

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        super().cast(user, target, **kwargs)
        user.mana.current -= self.cost
        if target is None:
            return "The seeds find no soil.\n"
        selected = kwargs.get("reagent") or kwargs.get("seed")
        if selected is None:
            selected = next((name for name in self.reagent_effects if _inventory_count(user, name) > 0), None)
        if selected not in self.reagent_effects:
            return f"{selected or 'That reagent'} cannot be planted with Plant Seeds.\n"
        failed = self._consume_reagent(user, selected)
        if failed:
            return failed

        if selected == "Acorn":
            msg, damage = _simple_spell_damage(user, target, dmg_mod=1.15, typ="Earth")
            if damage > 0 and not target.has_status_protection("Stun"):
                target.apply_stun(1, source="Plant Seeds", applier=user)
                msg += f"A mighty oak bashes {target.name} senseless.\n"
            return msg or f"A mighty oak erupts beneath {target.name}.\n"

        if selected == "Vine Seed":
            target.physical_effects["Prone"].active = True
            target.physical_effects["Prone"].duration = max(target.physical_effects["Prone"].duration, 3)
            return f"Fast-growing vines strangle {target.name}, restricting movement.\n"

        if target.has_status_protection("Poison"):
            return f"Deadly mushroom caps bloom, but {target.name} resists the poison.\n"
        target.status_effects["Poison"].active = True
        target.status_effects["Poison"].duration = max(target.status_effects["Poison"].duration, 4)
        target.status_effects["Poison"].extra = max(int(target.status_effects["Poison"].extra or 0), max(1, user.check_mod("magic", enemy=target) // 4))
        return f"Deadly mushroom caps bloom around {target.name}, spreading poison.\n"


class TreeOfLife(Spell):
    def __init__(self):
        super().__init__(
            "Tree of Life",
            "Transform into a giant oak tree for 3 turns, becoming a living bastion.",
            school="Nature",
        )
        self.cost = 28
        self.subtyp = "Support"

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import archdruid

        super().cast(user, user, **kwargs)
        if not archdruid.mastery_unlocked(user, "Growth"):
            return f"{user.name} has not mastered Growth attunement.\n"
        user.mana.current -= self.cost
        tree = user.magic_effects["Tree of Life"]
        tree.active = True
        tree.duration = max(tree.duration, 3)
        return f"{user.name} transforms into a giant oak tree.\n"


class VilePotion(_ReagentSpell):
    required_items = ("Hemlock Root", "Fungus Spore")

    def __init__(self):
        super().__init__("Vile Potion", "Imbibe rot and spew putrid vomitus at a foe.", school="Nature")
        self.cost = 0
        self.subtyp = "Poison"

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        super().cast(user, target, **kwargs)
        failed = self._consume_reagents(user)
        if failed:
            return failed
        if target is None:
            return "The potion spills harmlessly.\n"
        health_cost = max(1, int(user.health.max * 0.10))
        user.health.current = max(1, user.health.current - health_cost)
        msg = f"{user.name} chokes down rot and loses {health_cost} HP.\n"
        damage_msg, damage = _simple_spell_damage(user, target, dmg_mod=1.0, typ="Poison")
        msg += damage_msg
        if damage > 0 and not target.has_status_protection("Poison") and random.random() < 0.65:
            target.status_effects["Poison"].active = True
            target.status_effects["Poison"].duration = max(target.status_effects["Poison"].duration, 4)
            target.status_effects["Poison"].extra = max(target.status_effects["Poison"].extra, max(1, damage // 3))
            msg += f"{target.name} is poisoned.\n"
        return msg


class Foretell(Spell):
    def __init__(self):
        super().__init__("Foretell", "Read the enemy's next likely action.", school="Time")
        self.cost = 16
        self.subtyp = "Time"

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import ability_mechanics

        super().cast(user, target, **kwargs)
        engine = kwargs.get("battle_engine")
        if engine is None:
            return "There is no combat thread to foretell.\n"
        user.mana.current -= self.cost
        action = "Attack"
        stack = getattr(getattr(engine, "enemy", None), "action_stack", []) or []
        if stack:
            entry = stack[0]
            if isinstance(entry, dict):
                action = str(entry.get("ability") or entry.get("action") or action)
            else:
                action = str(entry)
        return f"{user.name} foresees {engine.enemy.name}'s next action: {action}.\n"


class Rewind(Spell):
    def __init__(self):
        super().__init__("Rewind", "Return combat to the previous player choice point.", school="Time")
        self.cost = 40
        self.subtyp = "Time"

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import ability_mechanics

        super().cast(user, target, **kwargs)
        engine = kwargs.get("battle_engine")
        if engine is None:
            return "There is no combat thread to rewind.\n"
        user.mana.current -= self.cost
        return ability_mechanics.restore_rewind_snapshot(engine)


class TwistFate(Spell):
    def __init__(self):
        super().__init__("Twist Fate", "Guarantee the success of your next action.", school="Time")
        self.cost = 18
        self.subtyp = "Time"

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        super().cast(user, user, **kwargs)
        user.mana.current -= self.cost
        user._twist_fate_success = True
        return f"Fate bends toward {user.name}'s next action.\n"


class Wormhole(Spell):
    def __init__(self):
        super().__init__("Wormhole", "Send a spell two turns into the future.", school="Time")
        self.cost = 10
        self.subtyp = "Time"

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        super().cast(user, target, **kwargs)
        engine = kwargs.get("battle_engine")
        spell_name = kwargs.get("spell_name") or kwargs.get("choice")
        user.mana.current -= self.cost
        if engine is None:
            return f"{user.name} opens a wormhole, but it collapses without a battle thread.\n"
        spellbook = user.spellbook.get("Spells", {})
        if not spell_name:
            candidates = [
                name for name, spell in spellbook.items()
                if name != self.name and getattr(spell, "subtyp", "") != "Support"
            ]
            spell_name = candidates[0] if candidates else None
        if not spell_name or spell_name not in spellbook or spell_name == self.name:
            return "No spell is shaped into the wormhole.\n"
        spell = spellbook[spell_name]
        if user.mana.current < getattr(spell, "cost", 0):
            return f"{user.name} does not have enough mana to send {spell_name} through time.\n"
        user.mana.current -= getattr(spell, "cost", 0)
        engine.delayed_spells.append({"turns": 2, "caster": user, "spell": spell})
        return f"{user.name} sends {spell_name} two turns into the future.\n"


class Volitation(MovementSpell):
    def __init__(self):
        super().__init__("Volitation", "Float above hazardous ground for a short time.", 16)

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        return self.cast_out(user)

    def cast_out(self, game_or_user) -> str:
        from .classes import ability_mechanics

        user = getattr(game_or_user, "player_char", game_or_user)
        user.mana.current -= self.cost
        ability_mechanics.apply_exploration_effect(user, "volitation", 40)
        return f"{user.name} rises gently above the ground.\n"


class EnterWall(MovementSpell):
    def __init__(self):
        super().__init__("Enter Wall", "Pass through ordinary walls for a few steps.", 75)

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        return "Enter Wall has no combat use.\n"

    def cast_out(self, game_or_user) -> str:
        from .classes import ability_mechanics

        user = getattr(game_or_user, "player_char", game_or_user)
        user.mana.current -= self.cost
        ability_mechanics.apply_exploration_effect(user, "enter_wall", 8)
        return f"{user.name} slips partly into the stone.\n"


class Invisibility(IllusionSpell):
    def __init__(self):
        super().__init__("Invisibility", "Fade from sight for surprise and defense.", 18)

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        return self.cast_out(user)

    def cast_out(self, game_or_user) -> str:
        from .classes import ability_mechanics

        user = getattr(game_or_user, "player_char", game_or_user)
        user.mana.current -= self.cost
        ability_mechanics.apply_exploration_effect(user, "invisibility", 30)
        return f"{user.name} fades from sight.\n"


class _ResistElement(Spell):
    element = "Fire"

    def __init__(self, name: str, element: str):
        super().__init__(name, f"Raise {element} resistance for several turns.", school="Abjuration")
        self.cost = 12
        self.subtyp = "Support"
        self.element = element

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        super().cast(user, user, **kwargs)
        user.mana.current -= self.cost
        effect = user.magic_effects[f"Resist {self.element}"]
        effect.active = True
        effect.duration = max(effect.duration, 5)
        effect.extra = max(float(effect.extra or 0), 0.5)
        return f"{user.name} gains resistance to {self.element.lower()}.\n"


class ResistFire(_ResistElement):
    def __init__(self): super().__init__("Resist Fire", "Fire")


class ResistIce(_ResistElement):
    def __init__(self): super().__init__("Resist Ice", "Ice")


class ResistElectric(_ResistElement):
    def __init__(self): super().__init__("Resist Electric", "Electric")


class ResistWater(_ResistElement):
    def __init__(self): super().__init__("Resist Water", "Water")


class ResistEarth(_ResistElement):
    def __init__(self): super().__init__("Resist Earth", "Earth")


class ResistWind(_ResistElement):
    def __init__(self): super().__init__("Resist Wind", "Wind")


class Corruption2(Spell):
    replaces = "Corruption"

    def __init__(self):
        super().__init__(
            "Corruption 2",
            "A stronger corruption that damages over time, fed by fiend contracts.",
            school="Shadow",
        )
        self.cost = 22
        self.subtyp = "Shadow"

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        from .classes import ability_mechanics, demonologist

        super().cast(user, target, **kwargs)
        user.mana.current -= self.cost
        if target is None:
            return "Corruption finds no soul to cling to.\n"
        contracts = ability_mechanics.abyssal_contract_count(
            user,
            len(demonologist.ensure_state(user).get("unlocked_contracts", [])),
        )
        msg, damage = _simple_spell_damage(user, target, dmg_mod=0.9 + (0.12 * contracts), typ="Shadow")
        if damage > 0 and "DOT" not in getattr(target, "status_immunity", []):
            dot = target.magic_effects["DOT"]
            dot.active = True
            dot.duration = max(dot.duration, 3 + min(2, contracts // 2))
            dot.extra = max(int(dot.extra or 0), max(1, damage // 3 + contracts))
            dot.source = "Corruption"
            msg += f"{target.name} is deeply corrupted.\n"
        return msg


class Nightmare(Spell):
    def __init__(self):
        super().__init__("Nightmare", "Twist fear into shadow damage against the enemy.", school="Shadow")
        self.cost = 24
        self.subtyp = "Shadow"

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        super().cast(user, target, **kwargs)
        user.mana.current -= self.cost
        msg, damage = _simple_spell_damage(user, target, dmg_mod=1.2, typ="Shadow")
        if target and damage > 0 and not target.has_status_protection("Sleep"):
            target.status_effects["Sleep"].active = True
            target.status_effects["Sleep"].duration = max(target.status_effects["Sleep"].duration, 2)
            msg += f"{target.name} is trapped in a nightmare.\n"
        return msg


class BadBreath(Skill):
    def __init__(self):
        super().__init__("Bad Breath", "Exhale a foul cloud of debilitating statuses.")
        self.subtyp = "Enemy"
        self.cost = 32

    def use(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        super().use(user, target, **kwargs)
        if target is None:
            return "The foul breath hits nothing.\n"
        msg = ""
        for status in ("Poison", "Blind", "Silence"):
            if target.has_status_protection(status):
                msg += f"{target.name} is immune to {status.lower()}.\n"
                continue
            effect = target.status_effects[status]
            effect.active = True
            effect.duration = max(effect.duration, 3)
            if status == "Poison":
                effect.extra = max(effect.extra, max(1, user.stats.con // 3))
            msg += f"{target.name} suffers {status.lower()}.\n"
        return msg


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
            target.magic_effects["DOT"].source = "Burn"
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
    """Data-driven (blizzard.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("blizzard.yaml", cls_name="IceBlizzard")


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
                applied = target.apply_stun(
                    max(1 + crit, target.status_effects["Stun"].duration),
                    source=self.name,
                    applier=caster,
                )
                if applied:
                    special_str += f"{target.name} gets shocked and is stunned.\n"
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


class Bolt:
    """Data-driven (bolt.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("bolt.yaml", cls_name="Bolt")


class BallLightning(Spell):
    def __init__(self):
        super().__init__("Ball Lightning", "Conjure a ball of electricity that repeatedly zaps the target.", school="Nature")
        self.cost = 34
        self.subtyp = "Electric"

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        super().cast(user, target, **kwargs)
        user.mana.current -= self.cost
        if target is None:
            return "The ball lightning crackles without a target.\n"
        msg = ""
        for _ in range(3):
            zap_msg, _damage = _simple_spell_damage(user, target, dmg_mod=0.65, typ="Electric")
            msg += zap_msg
            if not target.is_alive():
                break
        return msg


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


class SoulDrain:
    """Soul spell — data-driven (soul_drain.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("soul_drain.yaml", cls_name="SoulDrain")


class PoisonDart:
    """Nature spell — data-driven (poison_dart.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("poison_dart.yaml", cls_name="PoisonDart")


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
    """Data-driven (smite.yaml) - weapon strike + holy follow-up."""
    def __new__(cls):
        return _load_yaml_ability("smite.yaml", cls_name="Smite")


class Smite2:
    """Data-driven (smite_2.yaml) - upgraded Smite."""
    def __new__(cls):
        return _load_yaml_ability("smite_2.yaml", cls_name="Smite2")


class Smite3:
    """Data-driven (smite_3.yaml) - upgraded Smite."""
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
    """Data-driven (turn_undead.yaml) - undead-only kill or holy damage."""
    def __new__(cls):
        return _load_yaml_ability("turn_undead.yaml", cls_name="TurnUndead")


class TurnUndead2:
    """Data-driven (turn_undead_2.yaml) - upgraded Turn Undead."""
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
    """Data-driven (vulcanize.yaml) - self fire-damage + defense buff."""
    def __new__(cls):
        return _load_yaml_ability("vulcanize.yaml", cls_name="Vulcanize")


class WindSpeed:
    def __new__(cls):
        return _load_yaml_ability("wind_speed.yaml", cls_name="WindSpeed")


class Haste:
    """Data-driven (haste.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("haste.yaml", cls_name="Haste")


class StoneSkin(Spell):
    def __init__(self):
        super().__init__("Stone Skin", "Transform your skin into solid rock, reducing melee damage and resisting fire.", school="Nature")
        self.cost = 21
        self.subtyp = "Support"

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        super().cast(user, user, **kwargs)
        user.mana.current -= self.cost
        effect = user.magic_effects["Stone Skin"]
        effect.active = True
        effect.duration = max(effect.duration, 5)
        return f"{user.name}'s skin hardens into living stone.\n"


class CalmingBreeze(Spell):
    def __init__(self):
        super().__init__("Calming Breeze", "Conjure a gentle breeze that grants peaceful focus.", school="Nature")
        self.cost = 18
        self.subtyp = "Support"

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        super().cast(user, user, **kwargs)
        if user.status_effects["Berserk"].active:
            return f"{user.name} is too berserk to call a calming breeze.\n"
        user.mana.current -= self.cost
        peaceful = user.status_effects["Peaceful"]
        peaceful.active = True
        peaceful.duration = max(peaceful.duration, 5)
        return f"A calming breeze steadies {user.name}.\n"


class Windswept(Spell):
    def __init__(self):
        super().__init__("Windswept", "Launch the target on a mighty gust of wind.", school="Nature")
        self.cost = 15
        self.subtyp = "Wind"

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        super().cast(user, target or user, **kwargs)
        user.mana.current -= self.cost
        engine = kwargs.get("battle_engine")
        target = target or user
        if target is user:
            user.flying = True
            return f"The wind lifts {user.name} away from danger.\n"
        chance = min(0.70, 0.25 + (user.stats.wisdom * 0.01))
        if random.random() < chance:
            target.health.current = 0
            if engine is not None:
                target.windswept_ejected = True
            return f"{target.name} is swept out of the battle by a mighty gust.\n"
        msg, damage = _simple_spell_damage(user, target, dmg_mod=1.1, typ="Wind")
        return msg + (f"{target.name} crashes back down from the gust.\n" if damage > 0 else "")


class Regrowth:
    """Data-driven (regrowth.yaml)"""
    def __new__(cls):
        return _load_yaml_ability("regrowth.yaml", cls_name="Regrowth")


class NatureShield(Spell):
    def __init__(self):
        super().__init__("Nature Shield", "Conjure life-orbs that intercept attack spells and heal you.", school="Nature")
        self.cost = 28
        self.subtyp = "Support"

    def cast(self, user: Character, target: Character | None = None, **kwargs: Any) -> str:
        super().cast(user, user, **kwargs)
        user.mana.current -= self.cost
        shield = user.magic_effects["Nature Shield"]
        shield.active = True
        shield.duration = max(shield.duration, 6)
        shield.extra = max(int(shield.extra or 0), 3)
        return f"Three living orbs circle {user.name}.\n"


# Movement spells
class Sanctuary:
    """Data-driven (sanctuary.yaml) - return to town, full heal."""
    def __new__(cls):
        return _load_yaml_ability("sanctuary.yaml", cls_name="Sanctuary")


class Teleport:
    """Data-driven (teleport.yaml) - set/restore location."""
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
    """Data-driven (hex.yaml) - multi-status spell (Poison/Blind/Silence)."""
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


def ability_classes_for(entry):
    """Normalize one or more ability classes stored for a single level."""
    if entry is None:
        return []
    if isinstance(entry, (list, tuple)):
        return list(entry)
    return [entry]


def ability_classes_for_level(source: dict, class_name: str, level: int | str):
    return ability_classes_for(source.get(class_name, {}).get(str(level)))


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
    "Weapon Master": {
        "1": MortalStrike,
        "6": DoubleStrike,
        "21": TruePiercingStrike,
        },
    "Berserker": {
        "3": FinalAssault,
        "5": MortalStrike2,
        "10": MonkeyGrip,
        "20": MonkeyGrip2,
        "30": TripleStrike,
        },
    "Paladin": {
        "6": ShieldBlock,
        "13": Goad,
        "18": DoubleStrike,
        },
    "Crusader": {
        "1": Posturing,
        "5": MortalStrike,
        "22": TripleStrike,
        "30": TruePiercingStrike,
        },
    "Lancer": {
        "1": [Jump, PolearmProficiency],
        "12": Zephyrstrike,
        },
    "Dragoon": {
        "1": PolearmExcellence,
        "5": TruePiercingStrike,
        "10": ShieldBlock,
        },
    "Sentinel": {
        "1": ShieldBlock,
        "3": Goad,
        "5": HoldTheLine,
        "9": Retaliate,
        },
    "Stalwart Defender": {
        "5": Bulwark,
        "9": ShieldRiposte,
        "18": LastStand,
        },
    "Mage": {
        "25": ManaShield,
        },
    "Sorcerer": {
        "1": FrozenArmor,
        "10": Doublecast,
        "18": MirrorImage,
        },
    "Wizard": {
        "5": ManaShield2,
        "15": Triplecast,
        "30": MirrorImage2,
        },
    "Warlock": {
        "1": Familiar,
        "5": HealthDrain,
        "9": LifeTap,
        "15": ManaDrain,
        "20": Familiar2,
    },
    "Shadowcaster": {
        "4": ManaTap,
        "6": Eclipse,
        "10": HealthManaDrain,
        "20": Familiar3,
        },
    "Demonologist": {
        "1": CallContract,
        },
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
    "Summoner": {
        "1": Summon,
        "12": HealSummon,
    },
    "Grand Summoner": {
        "1": Summon2,
        "2": ConduitCommand,
        "3": [InvokePatagon, InvokeDilong, InvokeAgloolik, InvokeCacus, InvokeFuath, InvokeIzulu, InvokeHala, InvokeGrigori, InvokeBardi, InvokeKobalos, InvokeZahhak],
        "8": RaiseSummon,
    },
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
    "Thief": {
        "1": ScavengersEye,
        "5": Lockpick,
        "12": GoldToss,
        "15": Mug,
        "20": PoisonStrike,
    },
    "Rogue": {
        "1": FindersKeepers,
        "3": Zephyrstrike,
        "4": CheatDeath,
        "5": SneakAttack,
        "8": KeenEye,
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
    "Seeker": {
        "1": Cartography,
        "3": Wayfinding,
        "5": ThirdEye,
        "16": TripleStrike,
        "25": TruePiercingStrike,
        },
    "Assassin": {
        "1": DeathMark,
        "8": PoisonStrike,
        "15": Lockpick,
        "18": TripleStrike,
        },
    "Ninja": {
        "8": Mug,
        "25": FlurryBlades,
        },
    "Spell Stealer": {
        "1": StealSpell,
        "12": StealAsWell,
        "18": ImbueWeapon,
        },
    "Arcane Trickster": {
        "1": StealSpell2,
        "4": ThirdEye,
        },
    "Healer": {},
    "Cleric": {
        "6": ShieldSlam,
        "8": SanctuaryWard,
        "12": ShieldBlock,
        "24": PiousBounty,
        "27": TrueStrike,
        },
    "Templar": {
        "1": Parry,
        "4": PiercingStrike,
        "6": Goad,
        "8": RelicAegis,
        "14": Charge,
        "22": DoubleStrike,
        "30": TruePiercingStrike,
    },
    "Priest": {
        "4": DefensiveRegen,
        "6": Supplication,
        "10": ManaShield,
        },
    "Archbishop": {
        "5": Doublecast,
        "8": GreatBenediction,
        "15": ManaShield2,
        },
    "Monk": {
        "1": ChiHeal,
        "3": DoubleStrike,
        "5": LegSweep,
        "7": TrueStrike,
        "10": PurityBody,
        "11": CenteredGuard,
        "12": Uppercut,
        "14": MirrorBreath,
        "16": Headbutt,
        "18": PurgingKata,
        "20": DrunkenBrawler,
        "25": Parry,
    },
    "Master Monk": {
        "1": Evasion,
        "5": Hyakuretsukyaku,
        "10": TripleStrike,
        "12": SpinningBackElbow,
        "15": PurityBody2,
        "18": MartialMastery,
        "20": Suplex,
        "25": Hadouken,
        "30": DimMak,
        },
    "Bard": {
        "1": SongValor,
        "2": SongShelter,
        "3": SongRenewal,
        },
    "Troubadour": {},
    "Pathfinder": {},
    "Druid": {
        "1": Transform,
        "15": Transform2,
        "17": MortalStrike,
        },
    "Archdruid": {
        "10": FourfoldSurge,
    },
    "Lycan": {
        "1": Transform3,
        "11": Charge,
        "15": BattleCry,
        "18": WingedPounce,
        "25": MortalStrike2,
        },
    "Diviner": {
        "1": LearnSpell,
        "18": Doublecast,
        },
    "Astromancer": {
        "1": LearnSpell2,
        "12": ThreadedCast,
        "25": Triplecast,
        },
    "Shaman": {
        "1": Totem,
        "3": TotemSurge,
        "4": ElementalStrike,
        "6": PiercingStrike,
        "10": MaelstromWeapon,
        "19": TrueStrike,
        "24": DoubleStrike,
    },
    "Soulcatcher": {
        "1": AbsorbEssence,
        "2": Parry,
        "3": TotemSurge,
        "9": TripleStrike,
        "29": TruePiercingStrike,
    },
    "Ranger": {
        "1": Tame,
        "10": FavoredEnemy,
    },
    "Beast Master": {
        "5": Cover,
        "7": Zephyrstrike,
        "9": PackStrike,
        "10": GuardPartner,
        "11": HarryPrey,
        "12": MendWounds,
    },
}

spell_dict = {
    "Warrior": {},
    "Weapon Master": {},
    "Berserker": {},
    "Paladin": {
        "1": Heal,
        "4": Smite,
        "24": DivineProtection,
        },
    "Crusader": {
        "3": Smite2,
        "8": Heal2,
        "16": Cleanse,
        "18": Smite3,
        "20": Dispel,
        },
    "Lancer": {},
    "Dragoon": {},
    "Sentinel": {},
    "Stalwart Defender": {},
    "Mage": {
        "1": Firebolt,
        "4": Tremor,
        "5": MagicMissile,
        "8": IceLance,
        "13": Shock,
        "15": WaterJet,
        "16": Enfeeble,
        "19": Gust,
    },
    "Sorcerer": {
        "6": Reflect,
        "10": Sleep,
        "16": Dispel,
        "20": WeakenMind,
        "30": IceBlock,
    },
    "Wizard": {
        "7": Boost,
        "16": Volitation,
        "20": Teleport,
    },
    "Warlock": {
        "1": ShadowBolt,
        "4": Corruption,
        "10": Terrify,
        "12": ShadowBolt2,
        "15": Doom,
        "19": Dispel,
    },
    "Shadowcaster": {
        "8": ShadowBolt3,
        "12": Invisibility,
        "16": Nightmare,
        "18": Desoul,
        },
    "Demonologist": {
        "8": Corruption2,
        },
    "Spellblade": {
        "20": Reflect,
        },
    "Knight Enchanter": {},
    "Summoner": {},
    "Grand Summoner": {},
    "Footpad": {},
    "Thief": {},
    "Rogue": {},
    "Inquisitor": {
        "3": Dispel,
        "8": Silence,
        "12": Enfeeble,
        "15": Reflect,
        "18": ResistFire,
        "19": ResistIce,
        "20": ResistElectric,
        "21": ResistWater,
        "22": ResistEarth,
        "23": ResistWind,
        },
    "Seeker": {
        "1": Teleport,
        "4": ResistAll,
        "10": Sanctuary,
        "12": Volitation,
        "14": EnterWall,
        "16": WeakenMind,
        },
    "Assassin": {
        "10": Invisibility,
        },
    "Ninja": {
        "12": Haste,
        "20": Desoul,
        },
    "Spell Stealer": {
        "8": WindSpeed,
        "27": Silence,
        },
    "Arcane Trickster": {
        "4": WeakenMind,
        },
    "Healer": {
        "1": Heal,
        "3": Holy,
        "8": Regen,
        "10": TurnUndead,
        "26": Heal2,
        },
    "Cleric": {
        "1": Smite,
        "5": Bless,
        "14": Cleanse,
        "15": Silence,
        "16": Smite2,
        "19": TurnUndead2,
    },
    "Templar": {
        "6": Regen2,
        "10": Smite3,
        "18": Dispel,
        },
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
    "Monk": {
        "15": Shell,
        },
    "Master Monk": {
        "2": Reflect,
        "12": Dispel,
        },
    "Bard": {},
    "Troubadour": {},
    "Pathfinder": {
        "1": Tremor,
        "7": WaterJet,
        "14": Gust,
        "19": Scorch,
        },
    "Druid": {
        "1": PoisonDart,
        "5": StoneSkin,
        "9": Regrowth,
        "17": CalmingBreeze,
        },
    "Archdruid": {
        "1": PlantSeeds,
        "4": Bolt,
        "6": VilePotion,
        "8": Windswept,
        "12": NatureShield,
        "16": BallLightning,
        },
    "Lycan": {
        "8": Dispel,
        },
    "Diviner": {
        "3": Enfeeble,
        "8": Haste,
        "14": Dispel,
        "23": Berserk,
        },
    "Astromancer": {
        "1": Vulcanize,
        "6": Foretell,
        "10": WeakenMind,
        "15": Boost,
        "18": TwistFate,
        "22": Wormhole,
        "28": Rewind,
        },
    "Shaman": {
        "2": Hex,
        "9": Hydration,
        "16": AstralShift,
        },
    "Soulcatcher": {
        "4": SoulDrain,
        "6": Dispel,
        "12": Desoul,
        },
    "Ranger": {},
    "Beast Master": {},
}
