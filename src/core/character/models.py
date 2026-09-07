##########################################
"""character manager"""

from __future__ import annotations

from dataclasses import dataclass
from math import exp

POISON_HEALING_MULTIPLIER = 0.70
BLEED_MELEE_DAMAGE_TAKEN_MULTIPLIER = 1.20
STUN_IMMUNITY_TURNS_AFTER_EXPIRY = 1
STUN_LEVEL_DIFF_SCALE = 0.04
STUN_LEVEL_DIFF_CAP = 8
STUN_LEVEL_DIFF_MULT_MIN = 0.70
STUN_LEVEL_DIFF_MULT_MAX = 1.30


def _class_name(ch: object) -> str:
    cls = getattr(ch, "cls", None)
    return str(getattr(cls, "name", cls) or "")


def _combat_level(ch: object) -> int:
    """
    Best-effort combat level accessor.

    Player: ``player.level.level``
    Enemy: often ``enemy.level`` (int)
    """
    lvl = getattr(ch, "level", 1)
    if hasattr(lvl, "level"):
        try:
            return int(lvl.level)
        except Exception:
            return 1
    try:
        return int(lvl)
    except Exception:
        return 1


def armor_spell_modifier(armor: object) -> int:
    """Return the spell-damage modifier granted by armor."""
    explicit_mod = getattr(armor, "spell_mod", None)
    if explicit_mod is not None:
        try:
            return int(explicit_mod)
        except (TypeError, ValueError):
            return 0
    if getattr(armor, "subtyp", None) == "Cloth":
        try:
            return max(0, int(getattr(armor, "armor", 0)) // 4)
        except (TypeError, ValueError):
            return 0
    return 0


def armor_resistance_modifier(armor: object, typ: str | None) -> float:
    """Return elemental resistance granted by armor metadata."""
    if typ is None:
        return 0.0
    explicit_resistances = getattr(armor, "resistances", None)
    if isinstance(explicit_resistances, dict):
        try:
            return float(explicit_resistances.get(typ, 0.0))
        except (TypeError, ValueError):
            return 0.0
    explicit_mod = getattr(armor, "resist_mod", None)
    if explicit_mod is not None and getattr(armor, "element", None) in [typ, "Elemental"]:
        try:
            return float(explicit_mod)
        except (TypeError, ValueError):
            return 0.0
    if getattr(armor, "element", None) == typ:
        return 0.25
    return 0.0


# functions
def sigmoid(x: float) -> float:
    return 1 / (1 + exp(-x))


def scaled_decay_function(x: float, rate: float = 0.1) -> float:
    """
    Returns a value between 0 and 1 that decreases as x increases.
    Used for shop price adjustments based on charisma.

    Args:
        x (float): The input value, must be >= 0.
        rate (float): The rate of decay; higher values make it decrease faster.

    Returns:
        float: A value between 0 and 1.
    """
    if x < 0:
        raise ValueError("x must be non-negative.")
    decay_value = 1 / (1 + rate * x)  # Exponential decay
    return 0.5 + decay_value * 0.75  # Scale and shift to fit [0.5, 1.25]


# Character dataclasses
@dataclass
class Stats:
    """
    Attributes:
        strength: The strength attribute of the character, influencing physical damage.
        intel: The intelligence attribute of a character, influencing magical damage.
        wisdom: The wisdom attribute of the character, influencing resistance to magical effects.
        con: The constitution attribute of the character, influencing resistance to certain effects.
        charisma: The charisma attribute of the character, influencing interactions with NPCs.
        dex: The dexterity attribute of the character, influencing speed and avoidance.
    """

    strength: int = 0
    intel: int = 0
    wisdom: int = 0
    con: int = 0
    charisma: int = 0
    dex: int = 0


@dataclass
class Combat:
    """
    Combat Stats:
        attack: base attack stat for calculating melee damage
        defense: base defense stat for calculating damage reduction
        magic: base stat for calculating magic damage
        magic_def: base stat for calculating magic damage reduction
    """

    attack: int = 0
    defense: int = 0
    magic: int = 0
    magic_def: int = 0


@dataclass
class Resource:
    max: int = 0
    current: int = 0

    def __setattr__(self, name, value):
        if name == "current":
            try:
                value = max(0, int(value))
            except (TypeError, ValueError):
                value = 0
        super().__setattr__(name, value)


@dataclass
class Level:
    level: int = 1
    pro_level: int = 1
    exp: int = 0
    exp_to_gain: int = 25


@dataclass
class StatusEffect:
    active: bool = False
    duration: int = 0
    extra: int = 0
    source: str = ""


EffectMap = dict[str, StatusEffect]
AbilityBook = dict[str, dict[str, object]]
InventoryMap = dict[str, list[object]]
WeaponDamageResult = tuple[str, bool, int]
DefenseResolution = tuple[bool, str, int]
AbsorptionResult = tuple[int, str, bool]
DamageReductionResult = tuple[int, str]
