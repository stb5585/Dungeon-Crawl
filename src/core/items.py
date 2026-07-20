###########################################
""" item manager """
from __future__ import annotations

import random
from textwrap import wrap
from typing import TYPE_CHECKING

import numpy as np

from . import abilities
from .character import StatusEffect

if TYPE_CHECKING:
    from typing import Any

    from .character import Character
    from .combat.combat_result import CombatResultGroup


# Functions
_rarity_table_cache: dict[str, list[type[Item]]] | None = None
_RARITY_BUCKETS = np.array([1.0, 0.9, 0.8, 0.75, 0.50, 0.4, 0.2, 0.0])
_STAT_THEME_PREFIXES = {
    "strength": "Mighty",
    "intelligence": "Arcane",
    "wisdom": "Sage",
    "constitution": "Stalwart",
    "charisma": "Fortunate",
    "dexterity": "Swift",
    "resistance": "Warded",
}


def stat_theme_for_item(item: object) -> str | None:
    """Infer the primary stat theme for an item without mutating it."""
    explicit_theme = getattr(item, "stat_theme", None)
    if explicit_theme:
        return str(explicit_theme)

    name = str(getattr(item, "name", ""))
    mod = str(getattr(item, "mod", ""))
    subtyp = str(getattr(item, "subtyp", ""))
    typ = str(getattr(item, "typ", ""))

    if "Strength" in name or "Physical Damage" in mod:
        return "strength"
    if "Intelligence" in name or "Magic Damage" in mod or subtyp in {"Staff", "Tome", "Rod"}:
        return "intelligence"
    if "Wisdom" in name or "Magic Defense" in mod or "Status-" in mod:
        return "wisdom"
    if "Constitution" in name or "Physical Defense" in mod or typ in {"Armor", "Helmet"}:
        return "constitution"
    if "Charisma" in name or "Luck" in mod:
        return "charisma"
    if "Dexterity" in name or mod in {"Accuracy", "Dodge"} or subtyp in {"Dagger", "Ninja Blade"}:
        return "dexterity"
    if "Resist-" in mod or getattr(item, "element", None):
        return "resistance"
    if typ == "Weapon" and getattr(item, "damage", 0):
        return "strength"
    return None


def stat_themed_item_name(item: object) -> str:
    """Return a generated display name that reflects the item's stat theme."""
    name = str(getattr(item, "name", "Unknown Item"))
    theme = stat_theme_for_item(item)
    prefix = _STAT_THEME_PREFIXES.get(theme or "")
    if not prefix or name.startswith(f"{prefix} "):
        return name
    return f"{prefix} {name}"


def item_metadata_lines(item: object) -> list[str]:
    """Return concise presentation metadata for item descriptions."""
    lines: list[str] = []

    element = getattr(item, "element", None)
    if element:
        lines.append(f"Element: {element}")

    name = str(getattr(item, "name", "") or "")
    if name == "Svalinn":
        lines.append("Resistance: Fire +25%")
    if name == "Palangina":
        lines.append("Resistance: Fire +25%, Water +25%")

    resist_mod = getattr(item, "resist_mod", None)
    if resist_mod is not None and element:
        try:
            percent = int(float(resist_mod) * 100)
        except (TypeError, ValueError):
            percent = 0
        if percent:
            lines.append(f"Resistance: {element} +{percent}%")

    mod = str(getattr(item, "mod", "") or "")
    if mod.startswith("Resist-"):
        lines.append(f"Resistance: {mod.removeprefix('Resist-')} +50%")
    elif mod.startswith("Immune-"):
        lines.append(f"Immunity: {mod.removeprefix('Immune-')}")

    return lines


def _build_rarity_table() -> dict[str, list[type[Item]]]:
    """Build and cache the rarity-bucketed loot table from items_dict."""
    global _rarity_table_cache
    if _rarity_table_cache is not None:
        return _rarity_table_cache

    rarity_table: dict[str, list[type[Item]]] = {str(i): [] for i in range(1, 9)}
    for typ, typ_dict in items_dict.items():
        if typ == "Weapon":
            for handed in ["1-Handed", "2-Handed"]:
                for lst in items_dict[typ][handed].values():
                    for item_cls in lst:
                        rarity = np.digitize(item_cls().rarity, _RARITY_BUCKETS)
                        rarity_table[str(rarity)].append(item_cls)
        elif typ == "Accessory":
            for acc in ["Ring", "Pendant"]:
                for item_cls in items_dict[typ][acc]:
                    rarity = np.digitize(item_cls().rarity, _RARITY_BUCKETS)
                    rarity_table[str(rarity + 1)].append(item_cls)
        else:
            for value in typ_dict.values():
                for item_cls in value:
                    rarity = np.digitize(item_cls().rarity, _RARITY_BUCKETS)
                    rarity_table[str(rarity + 1)].append(item_cls)
    _rarity_table_cache = rarity_table
    return _rarity_table_cache


def random_item(z: int) -> type[Item]:
    """
    Returns a random item based on the given integer.
    Clamps z to the valid range [1, 8].
    """
    # Clamp z to valid range to prevent KeyError
    z = max(1, min(z, 8))
    rarity_table = _build_rarity_table()
    return random.choice(rarity_table[str(z)])


def remove_equipment(typ: str) -> Item:
    typ_dict = {
        'Weapon': NoWeapon,
        'OffHand': NoOffHand,
        'Armor': NoArmor,
        'Helmet': NoHelmet,
        'Pendant': NoPendant,
        'Ring': NoRing,
    }
    return typ_dict[typ]()


def equipment_slots_for_item(item: object, player: object | None = None) -> list[str]:
    """Return equipment slots that can hold this item, optionally filtered by player rules."""
    typ = getattr(item, "typ", None)
    subtyp = getattr(item, "subtyp", None)
    slots: list[str] = []

    if typ == "Weapon":
        slots.append("Weapon")
        if getattr(item, "off", False):
            slots.append("OffHand")
    elif typ in {"Armor", "Helmet", "OffHand"}:
        slots.append(str(typ))
    elif typ == "Accessory" and subtyp in {"Ring", "Pendant"}:
        slots.append(str(subtyp))

    if player is None:
        return slots

    can_equip = getattr(player, "can_equip_item", None)
    if callable(can_equip):
        return [slot for slot in slots if can_equip(item, slot)]

    equip_check = getattr(getattr(player, "cls", None), "equip_check", None)
    if callable(equip_check):
        return [slot for slot in slots if equip_check(item, slot)]
    return slots


class Item:
    """
    name: name of the item
    description: description of the item
    value: price in gold; sale price will be half this amount
    rarity: represented as a value between 0 and 1 and indicates the chance of dropping
    subtyp: the subtype of the item (i.e. Sword would be a subtype of Weapon)
    """

    def __init__(self, name: str, description: str, value: int, rarity: float, subtyp: str) -> None:
        self.name = name
        self.description = '\n'.join(wrap(description, 35, break_on_hyphens=False))
        self.value = value
        self.rarity = rarity
        self.subtyp = subtyp
        self.mod = 0
        self.weight = 0
        self.restriction = []
        self.restricted_against = []
        self.ultimate = False

    def __str__(self) -> str:
        return (f"{'=' * ((35 - len(self.name)) // 2)}{self.name}{'=' * ((36 - len(self.name)) // 2)}\n"
                f"{self.description}\n"
                f"{35*'-'}\n"
                f"Sub-type: {'Special' if 'Summon' in self.subtyp else self.subtyp}\n"
                f"{35*'='}")

    def use(self, user: Character, target: Character | None = None, tile: Any = None) -> str:
        return ""

    def special_effect(self, results: CombatResultGroup) -> None:
        return


class Weapon(Item):
    """
    Subclass of the Item class
    damage: the base damage for each weapon
    crit: legacy storage for critical-hit chance as a 0..1 ratio
    crit_chance: preferred alias for critical-hit chance as a 0..1 ratio
    handed: identifies weapon as 1-handed or 2-handed; 2-handed weapons prohibit the ability to use a shield
    unequip: boolean parameter indicating whether the object the base class used when an item is unequipped
    off: whether the weapon can be equipped in the offhand
    typ: the item type; 'Weapon' for this class
    disarm: boolean indicating whether the weapon can be disarmed; default is True
    ignore: boolean indicating whether the weapon automatically ignores armor when calculating damage
    """

    def __init__(
        self,
        name: str,
        description: str,
        value: int,
        rarity: float,
        damage: int,
        crit: float | None,
        handed: int,
        subtyp: str,
        unequip: bool,
        off: bool,
        *,
        crit_chance: float | None = None,
    ) -> None:
        super().__init__(name, description, value, rarity, subtyp)
        self.damage = damage
        self.crit = crit if crit_chance is None else crit_chance
        self.handed = handed
        self.unequip = unequip
        self.off = off
        self.typ = "Weapon"
        self.disarm = True
        if subtyp == 'Fist':
            self.disarm = False
        self.ignore = False
        self.element = None

    @property
    def crit_chance(self) -> float:
        """Critical-hit chance as a 0..1 ratio."""
        return self.crit

    @crit_chance.setter
    def crit_chance(self, value: float) -> None:
        self.crit = value

    def __str__(self) -> str:
        return (f"{'=' * ((35 - len(self.name)) // 2)}{self.name}{'=' * ((36 - len(self.name)) // 2)}\n"
                f"{self.description}\n"
                f"{35*'-'}\n"
                f"Type: {self.subtyp}\n"
                f"{self.handed}-handed\n"
                f"Damage: {self.damage}\n"
                f"Critical Chance: {int(self.crit_chance * 100)}%\n"
                f"Weight: {self.weight}\n"
                f"{35*'='}")

    def special_effect(self, results: CombatResultGroup) -> None:
        return


class Armor(Item):
    """
    armor: base armor for the item
    unequip: boolean parameter indicating whether the object the base class used when an item is unequipped
    typ: the item type; 'Armor' for this class
    """

    def __init__(self, name: str, description: str, value: int, rarity: float,
                 armor: int, subtyp: str, unequip: bool) -> None:
        super().__init__(name, description, value, rarity, subtyp)
        self.armor = armor
        self.unequip = unequip
        self.typ = 'Armor'
        self.element = None

    def __str__(self) -> str:
        return (f"{'=' * ((35 - len(self.name)) // 2)}{self.name}{'=' * ((36 - len(self.name)) // 2)}\n"
                f"{self.description}\n"
                f"{35*'-'}\n"
                f"Type: {self.subtyp}\n"
                f"Armor: {self.armor}\n"
                f"Weight: {self.weight}\n"
                f"{35*'='}")


class Helmet(Armor):
    """Head-slot armor that contributes to the normal Defense modifier."""

    def __init__(self, name: str, description: str, value: int, rarity: float,
                 armor: int, subtyp: str, unequip: bool) -> None:
        super().__init__(name, description, value, rarity, armor, subtyp, unequip)
        self.typ = 'Helmet'

    def special_effect(self, results: CombatResultGroup) -> None:
        return


class OffHand(Item):
    """
    mod: stat depends on the off-hand item; mod for shields is block and spell damage modifier for tomes
        block: determines block chance, calculated as 1 / mod parameter (i.e. 1/2 or 50%)
        spell damage: base attack spell modifier
    unequip: boolean parameter indicating whether the object the base class used when an item is unequipped
    typ: the item type; 'OffHand' for this class
    """

    def __init__(self, name: str, description: str, value: int, rarity: float,
                 mod: float, subtyp: str, unequip: bool) -> None:
        super().__init__(name, description, value, rarity, subtyp)
        self.mod = mod
        self.unequip = unequip
        self.typ = 'OffHand'

    def __str__(self) -> str:
        if self.subtyp == 'Shield':
            return (f"{'=' * ((35 - len(self.name)) // 2)}{self.name}{'=' * ((36 - len(self.name)) // 2)}\n"
                    f"{self.description}\n"
                    f"{35*'-'}\n"
                    f"Type: {self.subtyp}\n"
                    f"Block: {int(self.mod * 100)}%\n"
                    f"Weight: {self.weight}\n"
                    f"{35*'='}")
        return (f"{'=' * ((35 - len(self.name)) // 2)}{self.name}{'=' * ((36 - len(self.name)) // 2)}\n"
                f"{self.description}\n"
                f"{35*'-'}\n"
                f"Type: {self.subtyp}\n"
                f"Spell Damage Mod: {self.mod}\n"
                f"Weight: {self.weight}\n"
                f"{35*'='}")


class Accessory(Item):
    """
    Each character can equip 1 ring and 1 pendant
    Rings improve physical capabilities (either attack or defense)
    Pendants improve magical capabilities (either magic damage or defense)
    All modifications are considered magical and can't be ignored
    mod: defines the specific mod for each item; string that will be parsed later
    unequip: boolean parameter indicating whether the object the base class used when an item is unequipped
    typ: the item type; 'Accessory' for this class
    """

    def __init__(self, name: str, description: str, value: int, rarity: float,
                 mod: str, subtyp: str, unequip: bool) -> None:
        super().__init__(name, description, value, rarity, subtyp)
        self.mod = mod
        self.unequip = unequip
        self.typ = "Accessory"

    def __str__(self) -> str:
        return (f"{'=' * ((35 - len(self.name)) // 2)}{self.name}{'=' * ((36 - len(self.name)) // 2)}\n"
                f"{self.description}\n"
                f"{35*'-'}\n"
                f"Mod: {self.mod}\n"
                f"Weight: {self.weight}\n"
                f"{35*'='}")


class Potion(Item):
    """
    typ: the item type; 'Potion' for this class
    """

    def __init__(self, name: str, description: str, value: int, rarity: float, subtyp: str) -> None:
        super().__init__(name, description, value, rarity, subtyp)
        self.typ = "Potion"
        self.weight = 0.1

    def __str__(self) -> str:
        return (f"{'=' * ((35 - len(self.name)) // 2)}{self.name}{'=' * ((36 - len(self.name)) // 2)}\n"
                f"{self.description}\n"
                f"{35*'-'}\n"
                f"Weight: {self.weight}\n"
                f"{35*'='}")
    

class Misc(Item):
    """
    typ: the item type; 'Misc' for this class
    """

    def __init__(self, name: str, description: str, value: int, rarity: float, subtyp: str) -> None:
        super().__init__(name, description, value, rarity, subtyp)
        self.typ = "Misc"


# Weapons
# One-handed weapons
class NoWeapon(Weapon):

    def __init__(self):
        super().__init__(name="Bare Hands", description="Nothing but good ol' lefty and righty.",
                         value=0, rarity=0, damage=2, crit=0.025, handed=1, subtyp='None', unequip=True,
                         off=True)


class NaturalWeapon(Weapon):

    def __init__(self, name: str, damage: int, crit: float, description: str, off: bool) -> None:
        super().__init__(name=name, damage=damage, crit=crit, subtyp='Natural', description=description, handed=1,
                         off=off, rarity=0, unequip=False, value=0)
        self.att_name = 'attacks'


class BrassKnuckles(Weapon):

    def __init__(self):
        super().__init__(name="Brass Knuckles", description="Brass knuckles are pieces of metal shaped to fit around "
                                                            "the knuckles to add weight during hand-to-hand combat.",
                         value=2000, rarity=0.85, damage=12, crit=0.1, handed=1, subtyp='Fist', unequip=False,
                         off=True)
        self.weight = 1


class Cestus(Weapon):

    def __init__(self):
        super().__init__(name="Cestus", description="A cestus is a battle glove that is typically used in gladiatorial "
                                                    "events.",
                         value=7500, rarity=0.75, damage=16, crit=0.15, handed=1, subtyp='Fist', unequip=False,
                         off=True)
        self.weight = 1


class BattleGauntlet(Weapon):

    def __init__(self):
        super().__init__(name="Battle Gauntlet", description="A battle gauntlet is a type of glove that protects the "
                                                             "hand and wrist of a combatant, constructed with metal "
                                                             "platings to inflict additional damage.",
                         value=20000, rarity=0.5, damage=24, crit=0.2, handed=1, subtyp='Fist', unequip=False,
                         off=True)
        self.weight = 3


class BaghNahk(Weapon):

    def __init__(self):
        super().__init__(name="Bagh Nahk", description="The bagh nahk is a 'fist-load, claw-like' dagger designed to "
                                                       "fit over the knuckles or be concealed under and against the "
                                                       "palm.",
                         value=45000, rarity=0.4, damage=30, crit=0.25, handed=1, subtyp='Fist', unequip=False,
                         off=True)
        self.weight = 1


class IndrasFist(Weapon):
    """
    Electric element
    """

    def __init__(self):
        super().__init__(name="Indra's Fist", description="Indra's Fist is a powerful weapon named after the Hindu god"
                                                          " of thunder and lightning and is said to embody the sheer "
                                                          "force and power of a thunderstorm. The weapon crackles with"
                                                          " electric energy, emitting a faint glow as if it holds the "
                                                          "essence of a storm within.",
                         value=80000, rarity=0.2, damage=40, crit=0.3, handed=1, subtyp='Fist', unequip=False,
                         off=True)
        self.weight = 1
        self.element = "Electric"

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not any(["Stun" in result.target.status_immunity,
                    f"Status-Stun" in result.target.equipment["Pendant"].mod,
                    "Status-All" in result.target.equipment["Pendant"].mod]):
            if result.crit > 1:
                att_roll = random.randint(result.actor.stats.strength // 2, result.actor.stats.strength)
                def_roll = random.randint(result.target.stats.con // 2, result.target.stats.con)
                if result.target.stun_contest_success(result.actor, att_roll, def_roll):
                    duration = max(1, result.actor.stats.strength // 10)
                    if result.target.apply_stun(duration, source=self.name, applier=result.actor):
                        result.effects_applied['Stun'] = True


class GodsHand(Weapon):
    """
    Ultimate weapon; deals additional holy damage that won't heal even if the enemy would normally heal with holy damage
    Holy element
    """

    def __init__(self):
        super().__init__(name="God's Hand", description="With the appearance of an ordinary white glove, this weapon is"
                                                        " said to be imbued with the power of God.",
                         value=0, rarity=0, damage=52, crit=0.33, handed=1, subtyp='Fist', unequip=False,
                         off=True)
        self.ultimate = True
        self.element = "Holy"

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        resist = result.target.check_mod('resist', enemy=result.actor, typ=self.element)
        damage = int(random.randint(result.damage // 2, result.damage) * (1 - resist))
        if damage > 0:
            result.target.health.current -= damage
            result.damage += damage
            result.extra["Holy Damage"] = True


class Dirk(Weapon):

    def __init__(self):
        super().__init__(name="Dirk", description="A dirk is a long bladed thrusting dagger with a smooth jumpshot.",
                         value=125, rarity=0.95, damage=4, crit=0.15, handed=1, subtyp='Dagger', unequip=False,
                         off=True)
        self.weight = 2


class Baselard(Weapon):

    def __init__(self):
        super().__init__(name="Baselard", description="A baselard is a short bladed weapon with an H-shaped hilt.",
                         value=1500, rarity=0.85, damage=10, crit=0.2, handed=1, subtyp='Dagger', unequip=False,
                         off=True)
        self.weight = 3


class Kris(Weapon):

    def __init__(self):
        super().__init__(name="Kris", description="A Kris is an asymmetrical dagger with distinctive blade-patterning "
                                                  "achieved through alternating laminations of iron and nickelous iron,"
                                                  " easily identified by its distinct wavy blade.",
                         value=5000, rarity=0.75, damage=14, crit=0.25, handed=1, subtyp='Dagger', unequip=False,
                         off=True)
        self.weight = 3


class Rondel(Weapon):

    def __init__(self):
        super().__init__(name="Rondel", description="A type of dagger with a stiff-blade, named for the round hand "
                                                    "guard and round or spherical pommel.",
                         value=17000, rarity=0.5, damage=22, crit=0.33, handed=1, subtyp='Dagger', unequip=False,
                         off=True)
        self.weight = 3


class Kukri(Weapon):

    def __init__(self):
        super().__init__(name="Kukri", description="A kukri is a traditional Nepalese knife, recognized for its "
                                                   "distinctive inwardly curved blade that widens towards the tip. "
                                                   "The blade's unique design delivers powerful strikes, making it "
                                                   "ideal for combat, especially in close quarters.",
                         value=42000, rarity=0.4, damage=26, crit=0.4, handed=1, subtyp='Dagger', unequip=False,
                         off=True)
        self.weight = 4


class Khanjar(Weapon):

    def __init__(self):
        super().__init__(name="Khanjar", description="A khanjar is a curved dagger of Middle Eastern origin, known for"
                                                     " its distinctive double-edged blade that tapers to a sharp "
                                                     "point. It is designed for swift, precise strikes, making it "
                                                     "ideal for close-quarters encounters.",
                         value=75000, rarity=0.2, damage=36, crit=0.45, handed=1, subtyp='Dagger', unequip=False,
                         off=True)
        self.weight = 3


class Carnwennan(Weapon):
    """
    Ultimate weapon; chance to stun target on critical
    """

    def __init__(self):
        super().__init__(name="Carnwennan", description="King Arthur's dagger, sometimes described to shroud the user "
                                                        "in shadow.",
                         value=0, rarity=0, damage=48, crit=0.5, handed=1, subtyp='Dagger', unequip=False,
                         off=True)
        self.weight = 2
        self.ultimate = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not any(["Stun" in result.target.status_immunity,
                    f"Status-Stun" in result.target.equipment["Pendant"].mod,
                    "Status-All" in result.target.equipment["Pendant"].mod]):
            if result.crit > 1:
                spd = result.actor.check_mod("speed", enemy=result.target)
                att_roll = random.randint(spd // 2, spd)
                def_roll = random.randint(result.target.stats.con // 2, result.target.stats.con)
                if result.target.stun_contest_success(result.actor, att_roll, def_roll):
                    duration = max(1, result.actor.check_mod("speed", enemy=result.target) // 10)
                    if result.target.apply_stun(duration, source=self.name, applier=result.actor):
                        result.effects_applied['Stun'] = True
        return results


class Rapier(Weapon):

    def __init__(self):
        super().__init__(name="Rapier", description="A rapier is a slender and sharply pointed two-edged blade with a "
                                                    "protective hilt.",
                         value=125, rarity=0.95, damage=6, crit=0.075, handed=1, subtyp='Sword', unequip=False,
                         off=True)
        self.weight = 5


class Jian(Weapon):

    def __init__(self):
        super().__init__(name="Jian", description="A jian is a double-edged straight sword with a guard that protects "
                                                  "the wielder from opposing blades,",
                         value=2000, rarity=0.85, damage=14, crit=0.1, handed=1, subtyp='Sword', unequip=False,
                         off=True)
        self.weight = 6


class Talwar(Weapon):

    def __init__(self):
        super().__init__(name="Talwar", description="A talwar is curved, single-edged sword with an iron disc hilt and "
                                                    "knucklebow, and a fullered blade.",
                         value=5500, rarity=0.75, damage=20, crit=0.15, handed=1, subtyp='Sword', unequip=False,
                         off=True)
        self.weight = 8


class Shamshir(Weapon):

    def __init__(self):
        super().__init__(name="Shamshir", description="A shamshir has a radically curved blade featuring a slim blade "
                                                      "with almost no taper until the very tip.",
                         value=21000, rarity=0.5, damage=28, crit=0.2, handed=1, subtyp='Sword', unequip=False,
                         off=True)
        self.weight = 10


class Khopesh(Weapon):

    def __init__(self):
        super().__init__(name="Khopesh", description="A khopesh is a sickle-shaped sword that evolved from battle axes"
                                                     " and that can be used to disarm an opponent.",
                         value=47000, rarity=0.4, damage=36, crit=0.25, handed=1, subtyp='Sword', unequip=False,
                         off=True)
        self.weight = 10

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not result.target.physical_effects["Disarm"].active:
            if result.target.can_be_disarmed():
                chance = result.target.check_mod('luck', enemy=result.actor, luck_factor=10)
                if random.randint(result.actor.stats.strength // 2, result.actor.stats.strength) \
                        > random.randint(result.target.check_mod("speed", enemy=result.actor) // 2, 
                                         result.target.check_mod("speed", enemy=result.actor)) + chance:
                    result.target.physical_effects["Disarm"].active = True
                    result.target.physical_effects["Disarm"].duration = result.actor.stats.strength // 10
                    result.effects_applied['Physical'].append('Disarm')
        return results


class Falchion(Weapon):

    def __init__(self):
        super().__init__(name="Falchion", description="A falchion is a one-handed sword with a broad, curved blade "
                                                      "that is designed to deliver powerful cleaving and chopping "
                                                      "blows. Its slight curve and weight distribution make it capable"
                                                      " of delivering decisive strikes, while the sturdy design "
                                                      "provides balance for quick, fluid attacks.",
                         value=90000, rarity=0.2, damage=46, crit=0.3, handed=1, subtyp='Sword', unequip=False,
                         off=True)
        self.weight = 10


class Excalibur(Weapon):
    """
    Ultimate weapon; chance on crit to add a bleed on target
    """

    def __init__(self):
        super().__init__(name="Excalibur", description="The legendary sword of King Arthur, bestowed upon him by the "
                                                       "Lady of the Lake.",
                         value=0, rarity=0, damage=60, crit=0.35, handed=1, subtyp='Sword', unequip=False,
                         off=True)
        self.weight = 8
        self.ultimate = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if result.crit > 1:
            if random.randint((result.actor.stats.strength // 2), result.actor.stats.strength) \
                    > random.randint(result.target.stats.con // 2, result.target.stats.con):
                duration = max(1, result.actor.stats.strength // 10)
                bleed_dmg = max(result.actor.stats.strength // 2, result.damage)
                if not result.target.physical_effects["Bleed"].active:
                    result.target.physical_effects["Bleed"].active = True
                    result.effects_applied['Physical'].append('Bleed')
                else:
                    result.effects_applied['Physical'].append('Bleed+')
                result.target.physical_effects["Bleed"].duration = max(duration, result.target.physical_effects["Bleed"].duration)
                result.target.physical_effects["Bleed"].extra = max(bleed_dmg, result.target.physical_effects["Bleed"].extra)
        return results


class Excalibur2(Excalibur):
    """
    TODO Upgraded version of the sword; obtained by bringing Excalibur to the UndergroundSpring
    Ideas for upgrade
    - increased damage and/or crit chance
    - different/additional status effect
    - 
    """

    def __init__(self):
        super().__init__()
        self.description = "\n".join(wrap("An upgraded version of the legendary sword of King Arthur, bestowed upon "
                                          "him by the Lady of the Lake.", 35, break_on_hyphens=False))


class Mace(Weapon):

    def __init__(self):
        super().__init__(name="Mace", description="A mace is a blunt weapon, a type of club or virge that uses a heavy"
                                                  " head on the end of a handle to deliver powerful strikes. A mace "
                                                  "typically consists of a strong, heavy, wooden or metal shaft, often"
                                                  " reinforced with metal, featuring a head made of iron.",
                         value=2000, rarity=0.85, damage=18, crit=0.05, handed=1, subtyp='Club', unequip=False,
                         off=True)
        self.weight = 6


class WarHammer(Weapon):

    def __init__(self):
        super().__init__(name="War Hammer", description="A war hammer is a club with a head featuring both a blunt end "
                                                        "and a spike on the other end.",
                         value=4500, rarity=0.75, damage=26, crit=0.075, handed=1, subtyp='Club', unequip=False,
                         off=True)
        self.weight = 10


class Pernach(Weapon):

    def __init__(self):
        super().__init__(name="Pernach", description="A pernach is a type of flanged mace used to penetrate even heavy "
                                                     "armor plating.",
                         value=18000, rarity=0.5, damage=36, crit=0.1, handed=1, subtyp='Club', unequip=False,
                         off=True)
        self.weight = 10


class Morgenstern(Weapon):

    def __init__(self):
        super().__init__(name="Morgenstern", description="A morgenstern, or morning star, is a club-like weapon "
                                                         "consisting of a shaft with an attached ball adorned with "
                                                         "several spikes.",
                         value=43500, rarity=0.4, damage=48, crit=0.15, handed=1, subtyp='Club', unequip=False,
                         off=True)
        self.weight = 10


class Shishpar(Weapon):

    def __init__(self):
        super().__init__(name="Shishpar", description="A shishpar is a heavy, spiked mace traditionally used "
                                                      " to crush armor and bone in combat. Its distinctive feature is "
                                                      "the large head adorned with several protruding flanges or "
                                                      "spikes, designed to maximize the impact force while easily "
                                                      "breaking through defenses.",
                         value=85000, rarity=0.2, damage=62, crit=0.2, handed=1, subtyp='Club', unequip=False,
                         off=True)
        self.weight = 9


class Mjolnir(Weapon):
    """
    Ultimate weapon; chance to stun on a critical hit based on strength
    """

    def __init__(self):
        super().__init__(name="Mjolnir", description="Mjolnir, wielded by the Thunder god Thor, is depicted in Norse "
                                                     "mythology as one of the most fearsome and powerful weapons in "
                                                     "existence, capable of leveling mountains.",
                         value=0, rarity=0, damage=76, crit=0.25, handed=1, subtyp='Club', unequip=False,
                         off=True)
        self.weight = 8
        self.ultimate = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not any(["Stun" in result.target.status_immunity,
                    f"Status-Stun" in result.target.equipment["Pendant"].mod,
                    "Status-All" in result.target.equipment["Pendant"].mod]):
            if not result.target.status_effects["Stun"].active:
                if result.crit > 1:
                    att_roll = random.randint(result.actor.stats.strength // 2, result.actor.stats.strength)
                    def_roll = random.randint(result.target.stats.con // 2, result.target.stats.con)
                    if result.target.stun_contest_success(result.actor, att_roll, def_roll):
                        duration = max(1, result.actor.stats.strength // 10)
                        if result.target.apply_stun(duration, source=self.name, applier=result.actor):
                            result.effects_applied['Status'].append('Stun')
        return results


class Tanto(Weapon):

    def __init__(self):
        super().__init__(name="Tanto", description="A tanto is a double-edged, straight blade, designed primarily as a "
                                                   "stabbing weapon, but the edge can be used for slashing as well.",
                         value=44000, rarity=0.4, damage=28, crit=0.33, handed=1, subtyp='Ninja Blade', unequip=False,
                         off=True)
        self.weight = 5
        self.restriction = ['Ninja']


class Wakizashi(Weapon):

    def __init__(self):
        super().__init__(name="Wakizashi", description="A wakizashi is a curved, single-edged blade with a narrow "
                                                       "cross-section, producing a deadly strike.",
                         value=87000, rarity=0.2, damage=38, crit=0.4, handed=1, subtyp='Ninja Blade', unequip=False,
                         off=True)
        self.weight = 7
        self.restriction = ['Ninja']


class Ninjato(Weapon):
    """
    Ultimate weapon; chance on crit to kill target
    """

    def __init__(self):
        super().__init__(name="Ninjato", description="A mythical blade used by ninjas said to be possessed by a demon "
                                                     "who steals the soul of those slain by the weapon.",
                         value=0, rarity=0, damage=50, crit=0.5, handed=1, subtyp='Ninja Blade', unequip=False,
                         off=True)
        self.weight = 5
        self.restriction = ['Ninja']
        self.ultimate = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if result.crit > 1:
            if not "Death" in result.target.status_immunity:
                w_chance = result.actor.check_mod('luck', enemy=result.target, luck_factor=10)
                t_chance = result.target.check_mod('luck', enemy=result.actor, luck_factor=10)
                if random.randint(0, result.actor.check_mod("speed", enemy=result.target)) + w_chance > \
                        random.randint(result.target.stats.con // 2, result.target.stats.con) + t_chance:
                    result.extra['Instant Death'] = True
        return results


# Two-handed weapons
class Bastard(Weapon):

    def __init__(self):
        super().__init__(name="Bastard Sword", description="The bastard sword, also referred to as a hand-and-a-half "
                                                           "sword, is a type of longsword that typically requires two "
                                                           "hands to wield but can be wielded in one if the need "
                                                           "arises.",
                         value=700, rarity=0.9, damage=10, crit=0.125, handed=2, subtyp='Longsword', unequip=False,
                         off=False)
        self.weight = 14


class Claymore(Weapon):

    def __init__(self):
        super().__init__(name="Claymore", description="The claymore is a two-handed sword featuring quillons "
                                                      "(crossguards between the hilt and the blade) are angled in "
                                                      "towards the blade and end in quatrefoils, and a tongue of metal"
                                                      " protrudes down either side of the blade.",
                         value=4200, rarity=0.85, damage=28, crit=0.15, handed=2, subtyp='Longsword', unequip=False,
                         off=False)
        self.weight = 20


class Zweihander(Weapon):

    def __init__(self):
        super().__init__(name="Zweihander", description="German for 'two-handed', the zweihander is a double-edged, "
                                                        "straight blade with a cruciform hilt.",
                         value=9500, rarity=0.75, damage=38, crit=0.2, handed=2, subtyp='Longsword', unequip=False,
                         off=False)
        self.weight = 18


class Changdao(Weapon):

    def __init__(self):
        super().__init__(name="Changdao", description="A single-edged two-hander over seven feet long, roughly "
                                                      "translates to 'long saber'.",
                         value=28000, rarity=0.5, damage=50, crit=0.25, handed=2, subtyp='Longsword', unequip=False,
                         off=False)
        self.weight = 16


class Flamberge(Weapon):
    """
    Fire element
    """

    def __init__(self):
        super().__init__(name="Flamberge", description="The flamberge is a type of flame-bladed sword featuring a "
                                                       "signature wavy blade.",
                         value=61000, rarity=0.4, damage=62, crit=0.33, handed=2, subtyp='Longsword', unequip=False,
                         off=False)
        self.weight = 18
        self.element = "Fire"


class Katana(Weapon):

    def __init__(self):
        super().__init__(name="Katana", description="The katana is a traditional Japanese sword characterized by its "
                                                    "curved, slender, single-edged blade, circular or squared guard, "
                                                    "and long grip suitable for two-handed use. Renowned for its "
                                                    "sharpness, the katana was crafted with exceptional skill, "
                                                    "incorporating a folded steel forging process that produced both "
                                                    "resilience and flexibility.",
                         value=100000, rarity=0.2, damage=78, crit=0.4, handed=2, subtyp='Longsword', unequip=False,
                         off=False)
        self.weight = 18


class Executioner(Weapon):

    def __init__(self):
        super().__init__(name="Executioner's Blade", description="Designed specifically for decapitation, the "
                                                                 "Executioner's Blade is a large, two-handed sword "
                                                                 "with a broad blade that is highly efficient at "
                                                                 "killing.",
                         value=0, rarity=0, damage=100, crit=0.4, handed=2, subtyp='Longsword', unequip=False,
                         off=False)
        self.weight = 20
        self.ultimate = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if result.crit > 1:
            if not "Death" in result.target.status_immunity:
                w_chance = result.actor.check_mod('luck', enemy=result.target, luck_factor=10)
                t_chance = result.target.check_mod('luck', enemy=result.actor, luck_factor=10)
                if random.randint(0, result.actor.stats.strength) + w_chance > \
                        random.randint(result.target.stats.con // 2, result.target.stats.con) + t_chance:
                    result.extra['Instant Death'] = True
        return results


class Mattock(Weapon):

    def __init__(self):
        super().__init__(name="Mattock", description="A mattock is a hand tool used for digging, prying, and chopping, "
                                                     "similar to the pickaxe.",
                         value=800, rarity=0.9, damage=12, crit=0.1, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)
        self.weight = 15


class Broadaxe(Weapon):

    def __init__(self):
        super().__init__(name="Broadaxe", description="A broadaxe is broad-headed axe with a large flared blade.",
                         value=4500, rarity=0.85, damage=30, crit=0.15, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)
        self.weight = 17


class DoubleAxe(Weapon):

    def __init__(self):
        super().__init__(name="Double Axe", description="The double axe is basically a broadaxe but with a blade on "
                                                        "each side of the axehead.",
                         value=10000, rarity=0.75, damage=42, crit=0.2, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)
        self.weight = 22


class Parashu(Weapon):

    def __init__(self):
        super().__init__(name="Parashu", description="A parashu is a single-bladed battle axe with an arced edge "
                                                     "extending beyond 180 degrees and paired with a spike on the non-"
                                                     "cutting edge.",
                         value=27500, rarity=0.5, damage=56, crit=0.25, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)
        self.weight = 20


class Greataxe(Weapon):

    def __init__(self):
        super().__init__(name="Greataxe", description="A greataxe is a scaled up version of the double axe with greater"
                                                      " mass and killing power.",
                         value=59000, rarity=0.4, damage=68, crit=0.3, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)
        self.weight = 26


class Tabarzin(Weapon):

    def __init__(self):
        super().__init__(name="Tabarzin", description="The tabarzin is notable for its single-bladed axe head, "
                                                      "accompanied by a spike on the opposite side. Typically adorned "
                                                      "with intricate carvings or inlays, the tabarzin reflects the "
                                                      "a unique artistry, blending practical lethality with cultural "
                                                      "craftsmanship.",
                         value=100000, rarity=0.2, damage=86, crit=0.33, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)
        self.weight = 24


class Jarnbjorn(Weapon):
    """
    Ultimate weapon; chance on critical hit to cause bleed
    """

    def __init__(self):
        super().__init__(name="Jarnbjorn", description="Legendary axe of Thor Odinson. Old Norse for \"iron bear\".",
                         value=0, rarity=0, damage=110, crit=0.33, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)
        self.weight = 20
        self.ultimate = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if result.crit > 1:
            if random.randint((result.actor.stats.strength // 2), result.actor.stats.strength) \
                    > random.randint(result.target.stats.con // 2, result.target.stats.con):
                duration = max(1, result.actor.stats.strength // 10)
                bleed_dmg = max(result.actor.stats.strength // 2, result.damage)
                if not result.target.physical_effects["Bleed"].active:
                    result.target.physical_effects["Bleed"].active = True
                    result.effects_applied['Physical'].append('Bleed')
                else:
                    result.effects_applied['Physical'].append('Bleed+')
                result.target.physical_effects["Bleed"].duration = max(duration, result.target.physical_effects["Bleed"].duration)
                result.target.physical_effects["Bleed"].extra = max(bleed_dmg, result.target.physical_effects["Bleed"].extra)
        return results

class Framea(Weapon):

    def __init__(self):
        super().__init__(name="Framea", description="A type of spear used by the ancient Germanic tribes and is a "
                                                    "versatile weapon used in both melee combat and as a projectile.",
                         value=800, rarity=0.9, damage=10, crit=0.15, handed=2, subtyp='Polearm', unequip=False,
                         off=False)
        self.weight = 10


class Partisan(Weapon):

    def __init__(self):
        super().__init__(name="Partisan", description="A partisan consists of a spearhead mounted on a long wooden "
                                                      "shaft, with protrusions on the sides which aid in parrying "
                                                      "sword thrusts.",
                         value=3500, rarity=0.85, damage=26, crit=0.2, handed=2, subtyp='Polearm', unequip=False,
                         off=False)
        self.weight = 12


class Halberd(Weapon):

    def __init__(self):
        super().__init__(name="Halberd", description="A halberd is a two-handed pole weapon consisting of an axe blade "
                                                     "topped with a spike mounted on a long shaft.",
                         value=9000, rarity=0.75, damage=36, crit=0.25, handed=2, subtyp='Polearm', unequip=False,
                         off=False)
        self.weight = 15


class Naginata(Weapon):

    def __init__(self):
        super().__init__(name="Naginata", description="A naginata consists of a wooden or metal pole with a curved "
                                                      "single-edged blade on the end that has a round handguard between"
                                                      " the blade and shaft.",
                         value=26500, rarity=0.5, damage=50, crit=0.3, handed=2, subtyp='Polearm', unequip=False,
                         off=False)
        self.weight = 14


class Trident(Weapon):
    """
    Water element
    """

    def __init__(self):
        super().__init__(name="Trident", description="A trident is a 3-pronged spear, the preferred weapon of the Sea"
                                                     " god Poseidon.",
                         value=57000, rarity=0.4, damage=62, crit=0.33, handed=2, subtyp='Polearm', unequip=False,
                         off=False)
        self.weight = 16
        self.element = "Water"


class Ranseur(Weapon):

    def __init__(self):
        super().__init__(name="Ranseur", description="A ranseur is a polearm characterized by a central spearhead "
                                                     "flanked by two outward-curving prongs, giving it a trident-like "
                                                     "appearance. Its primary purpose was to parry or entangle an "
                                                     "opponent's weapon while still maintaining the thrusting "
                                                     "capability of a spear.",
                         value=95000, rarity=0.2, damage=76, crit=0.35, handed=2, subtyp='Polearm', unequip=False,
                         off=False)
        self.weight = 15

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not result.target.physical_effects["Disarm"].active:
            if result.target.can_be_disarmed():
                chance = result.target.check_mod('luck', enemy=result.actor, luck_factor=10)
                if random.randint(result.actor.stats.strength // 2, result.actor.stats.strength) \
                        > random.randint(result.target.check_mod("speed", enemy=result.actor) // 2,
                                         result.target.check_mod("speed", enemy=result.actor)) + chance:
                    result.target.physical_effects["Disarm"].active = True
                    result.target.physical_effects["Disarm"].duration = result.actor.stats.strength // 10
                    result.effects_applied['Physical'].append('Disarm')
        return results


class Gungnir(Weapon):
    """
    Ultimate weapon; ignores armor
    """

    def __init__(self):
        super().__init__(name="Gungnir", description="Legendary spear of the god Odin. Old Norse for \"swaying one\".",
                         value=0, rarity=0, damage=96, crit=0.4, handed=2, subtyp='Polearm', unequip=False,
                         off=False)
        self.weight = 14
        self.ignore = True
        self.ultimate = True


class Quarterstaff(Weapon):

    def __init__(self):
        super().__init__(name="Quarterstaff", description="A quarterstaff is a shaft of hardwood about eight feet long"
                                                          " fitted with metal tips on each end.",
                         value=250, rarity=0.95, damage=4, crit=0.025, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 6


class Baston(Weapon):

    def __init__(self):
        super().__init__(name="Baston", description="A baston is a long, light, and flexible staff weapon that is ideal"
                                                    " for speed and precision.",
                         value=800, rarity=0.9, damage=8, crit=0.05, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 6


class IronshodStaff(Weapon):

    def __init__(self):
        super().__init__(name="Ironshod Staff", description="An iron walking stick, making it ideal for striking.",
                         value=4000, rarity=0.85, damage=18, crit=0.1, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 10


class SerpentStaff(Weapon):

    def __init__(self):
        super().__init__(name="Serpent Staff", description="A magic staff, shaped to appear as a snake.",
                         value=8000, rarity=0.75, damage=26, crit=0.12, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 8


class HolyStaff(Weapon):

    def __init__(self):
        super().__init__(name="Holy Staff", description="A staff that emits a holy light. Only equipable by priests"
                                                        " and archbishops.",
                         value=25000, rarity=0.5, damage=30, crit=0.15, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 6
        self.restriction = ['Priest', 'Archbishop']
        self.element = "Holy"

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        t_chance = result.target.check_mod('luck', enemy=result.target, luck_factor=5) / 100
        if 0.05 + t_chance > random.random():  # 5% chance plus charisma // 5
            heal = min(result.actor.health.max - result.actor.health.current, result.damage)
            result.actor.health.current += heal
            result.healing += heal
        return results


class RuneStaff(Weapon):

    def __init__(self):
        super().__init__(name="Rune Staff", description="A wooden staff with a magical rune embedded in the handle.",
                         value=27500, rarity=0.5, damage=36, crit=0.18, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 7


class MithrilshodStaff(Weapon):

    def __init__(self):
        super().__init__(name="Mithrilshod Staff", description="A mithril walking stick, making it ideal for striking.",
                         value=65000, rarity=0.4, damage=44, crit=0.2, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 8


class Khatvanga(Weapon):

    def __init__(self):
        super().__init__(name="Khatvanga", description="A khatvanga is a ritual staff that consists of a wooden or "
                                                       "metal shaft adorned with a trident or skull, symbolizing its "
                                                       "esoteric nature.",
                         value=100000, rarity=0.2, damage=56, crit=0.25, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 7


class DragonStaff(Weapon):
    """
    Ultimate weapon; regen mana based on damage
    """

    def __init__(self):
        super().__init__(name="Dragon Staff", description="A magic staff, shaped to appear as a dragon.",
                         value=0, rarity=0, damage=70, crit=0.3, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 9
        self.restriction = ['Wizard', 'Necromancer', 'Master Monk', 'Lycan', 'Astromancer', 'Soulcatcher']
        self.ultimate = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        mana_heal = random.randint(result.damage // 2, result.damage)
        if result.actor.mana.current + mana_heal > result.actor.mana.max:
            mana_heal = result.actor.mana.max - result.actor.mana.current
        if mana_heal > 0:
            result.actor.mana.current += mana_heal
            result.extra['Mana'] = mana_heal
        return results


class PrincessGuard(Weapon):
    """
    Ultimate weapon; regen health based on damage
    """

    def __init__(self):
        super().__init__(name="Princess Guard", description="A mythical staff from another world.",
                         value=0, rarity=0, damage=74, crit=0.25, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 4
        self.restriction = ['Archbishop']
        self.ultimate = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        heal = random.randint(result.damage // 2, result.damage)
        if result.actor.health.current + heal > result.actor.health.max:
            heal = result.actor.health.max - result.actor.health.current
        if heal > 0:
            result.actor.mana.current += heal
            result.healing += heal
        return results


class RuyiJinguBang(Weapon):
    """
    Ultimate weapon; Master Monk chi-conduit staff.
    """

    def __init__(self):
        super().__init__(
            name="Ruyi Jingu Bang",
            description=(
                "A legendary iron staff that changes weight with the wielder's "
                "breath and carries chi cleanly through every strike."
            ),
            value=0,
            rarity=0,
            damage=72,
            crit=0.28,
            handed=2,
            subtyp='Staff',
            unequip=False,
            off=False,
        )
        self.weight = 8
        self.restriction = ['Master Monk']
        self.ultimate = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        actor = result.actor
        try:
            from .classes import promotion_kits

            if promotion_kits.class_name(actor) != "Master Monk":
                return
            state = promotion_kits.combat_state(actor)
            cap = promotion_kits.cap_for(actor, "ki")
            if int(state.get("ki", 0) or 0) >= cap:
                return
            if random.random() < 0.35:
                result.message += promotion_kits.gain_meter(actor, "ki", 1, self.name)
        except Exception:
            return


class Sledgehammer(Weapon):

    def __init__(self):
        super().__init__(name="Sledgehammer", description="A sledgehammer is a tool with a large, flat, metal head, "
                                                          "attached to a long handle that gathers momentum during a "
                                                          "swing to apply a large force upon the target.",
                         value=800, rarity=0.9, damage=14, crit=0.075, handed=2, subtyp='Hammer', unequip=False,
                         off=False)
        self.weight = 20


class SpikeMaul(Weapon):

    def __init__(self):
        super().__init__(name="Spike Maul", description="A spike maul is similar to a sledgehammer except for having a"
                                                        " more narrow face for increased damage.",
                         value=7500, rarity=0.75, damage=36, crit=0.12, handed=2, subtyp='Hammer', unequip=False,
                         off=False)
        self.weight = 22


class EarthHammer(Weapon):

    def __init__(self):
        super().__init__(name="Earth Hammer", description="A large, 2-handed hammer infused with the power of Gaia.",
                         value=29000, rarity=0.5, damage=50, crit=0.15, handed=2, subtyp='Hammer', unequip=False,
                         off=False)
        self.weight = 20
        self.element = "Earth"


class GreatMaul(Weapon):

    def __init__(self):
        super().__init__(name="Great Maul", description="A great maul looks similar to a sledgehammer but is "
                                                        "significantly larger in all aspects.",
                         value=60000, rarity=0.4, damage=72, crit=0.2, handed=2, subtyp='Hammer', unequip=False,
                         off=False)
        self.weight = 30


class Streithammer(Weapon):

    def __init__(self):
        super().__init__(name="Streithammer", description="The streithammer is a fearsome, two-handed war hammer "
                                                          "designed for battle, particularly against heavily armored "
                                                          "foes. Its solid steel head features a broad, flat face for "
                                                          "crushing blows and a sharp, opposing spike for piercing "
                                                          "armor or breaking shields.",
                         value=98000, rarity=0.2, damage=94, crit=0.25, handed=2, subtyp='Hammer', unequip=False,
                         off=False)
        self.weight = 26


class Skullcrusher(Weapon):
    """
    Ultimate weapon; chance to stun on critical based on strength
    """

    def __init__(self):
        super().__init__(name="Skullcrusher", description="A massive hammer with the power to pulverize an enemy's "
                                                          "skull to powder.",
                         value=0, rarity=0, damage=120, crit=0.25, handed=2, subtyp='Hammer', unequip=False,
                         off=False)
        self.weight = 25
        self.ultimate = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not any(["Stun" in result.target.status_immunity,
                    f"Status-Stun" in result.target.equipment["Pendant"].mod,
                    "Status-All" in result.target.equipment["Pendant"].mod]):
            if not result.target.status_effects["Stun"].active:
                if result.crit > 1:
                    att_roll = random.randint(result.actor.stats.strength // 2, result.actor.stats.strength)
                    def_roll = random.randint(result.target.stats.con // 2, result.target.stats.con)
                    if result.target.stun_contest_success(result.actor, att_roll, def_roll):
                        duration = max(1, result.actor.stats.strength // 10)
                        if result.target.apply_stun(duration, source=self.name, applier=result.actor):
                            result.effects_applied['Status'].append('Stun')
        return results


# Summon weapons
class GiantClub(Weapon):
    """
    Summon Patagon weapon
    """

    def __init__(self):
        super().__init__(name="Giant's Club", description="A massive club wielded by Patagon, the giant summon "
                                                          "creature.",
                         value=0, rarity=0, damage=50, crit=0.1, handed=2, subtyp="Summon", unequip=False, off=False)


class EarthMaw(NaturalWeapon):
    """
    Summon Dilong weapon
    """

    def __init__(self):
        super().__init__(name="Earth Maw", damage=60, crit=0.2, description="", off=False)
        self.att_name = "bites"
        self.element = "Earth"

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if result.crit > 1:
            abilities.Sandstorm().cast(result.actor, result.target, special=True)
        return results


class IceShard(NaturalWeapon):
    """
    Summon Agloolik weapon
    """

    def __init__(self):
        super().__init__(name="Ice Shard", damage=30, crit=0.33, description="", off=False)
        self.att_name = "throws ice shards at"
        self.element = "Ice"

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        shards = random.randint(0, result.actor.intel // 8) * round(1 + result.crit)
        if 'Shards' not in result.extra:
            result.extra['Shards'] = shards
        else:
            result.extra['Shards'] += shards
        for _ in range(shards):
            result.damage += int(random.randint(1, result.actor.intel) * random.uniform(-1, 1))
        return results


class VulcansHammer(Weapon):
    """
    Summon Cacus weapon
    """

    def __init__(self):
        super().__init__(name="Vulcan's Hammer", description="A blacksmith's hammer that allegedly belonged to the fire god Vulcan.",
                         value=0, rarity=0, damage=45, crit=0.25, handed=2, subtyp="Summon", unequip=False, off=False)


class Scythe(Weapon):
    """
    Summon Bardi weapon
    """

    def __init__(self):
        super().__init__(name="Scythe", description="",
                         value=0, rarity=0, damage=80, crit=0.3, handed=2, subtyp="Summon", unequip=False, off=False)

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if result.crit > 1:
            result = abilities.Desoul(result, special=True)
        return results


class KoboldDagger(Weapon):
    """
    Used by the Kobalos Summon; has random affect on crit  TODO
    """

    def __init__(self):
        super().__init__(name="Kobold Dagger", description="",
                         value=0, rarity=0, damage=50, crit=0.4, handed=1, subtyp="Summon", unequip=False, off=False)

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if result.crit > 1:
            effects = []
        return results


# Natural weapons
class Bite(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Bite", damage=6, crit=0.05, description="", off=False)
        self.special = True
        self.att_name = 'bites'

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if self.crit > random.random():
            result.extra['Disease'] = False
            if not random.randint(0, 39 // result.crit):
                result.target.stats.con -= 1
                result.extra['Disease'] = True
        return results


class Bite2(Bite):

    def __init__(self):
        super().__init__()
        self.damage = 30
        self.crit = 0.2

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if self.crit > random.random():
            result.extra['Disease'] = False
            if not random.randint(0, 19 // result.crit):
                result.extra['Disease'] = True
                result.target.stats.con -= 1
        return results


class VampireBite(Bite):

    def __init__(self):
        super().__init__()
        self.damage = 20
        self.crit = 0.15

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if self.crit > random.random():
            result.actor.health.current += result.damage
            result.actor.health.current = min(result.actor.health.current, result.actor.health.max)
            result.extra['Drain'] = True
        return results


class Claw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Claw", damage=8, crit=0.2, description="", off=True)
        self.att_name = 'swipes'


class Claw2(Claw):

    def __init__(self):
        super().__init__()
        self.damage = 20
        self.crit = 0.25


class Claw3(Claw):

    def __init__(self):
        super().__init__()
        self.special = True
        self.damage = 36
        self.crit = 0.33

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        resist = result.target.check_mod('resist', enemy=result.actor, typ='Physical')
        if resist < 1:
            if random.randint((result.actor.check_mod("speed", enemy=result.target) // 2) * result.crit,
                              result.actor.check_mod("speed", enemy=result.target) * result.crit) \
                    > random.randint(result.target.stats.con // 2, result.target.stats.con):
                if not result.target.physical_effects["Bleed"].active:
                    result.target.physical_effects["Bleed"].active = True
                    result.effects_applied['Physical'].append('Bleed')
                else:
                    result.effects_applied['Physical'].append('Bleed+')
                duration = max(1, result.actor.check_mod("speed", enemy=result.target) // 10)
                bleed_dmg = int(max(result.actor.check_mod("speed", enemy=result.target) // 2, result.damage) * (1 - resist))
                bleed_dmg = max(1, int(random.randint(bleed_dmg // 4, bleed_dmg) * 0.75))
                result.target.physical_effects["Bleed"] = StatusEffect(True,
                                                              max(duration, result.target.physical_effects["Bleed"].duration),
                                                              max(bleed_dmg, result.target.physical_effects["Bleed"].extra))
        return results


class BearClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Bear Claw", damage=24, crit=0.2, description="", off=True)
        self.special = True
        self.att_name = 'mauls'

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        resist = result.target.check_mod('resist', enemy=result.actor, typ='Physical')
        if resist < 1:
            if random.randint((result.actor.stats.strength // 2) * result.crit, result.actor.stats.strength * result.crit) \
                    > random.randint(result.target.stats.con // 2, result.target.stats.con):
                if not result.target.physical_effects["Bleed"].active:
                    result.target.physical_effects["Bleed"].active = True
                    result.effects_applied['Physical'].append('Bleed')
                else:
                    result.effects_applied['Physical'].append('Bleed+')
                duration = max(1, result.actor.stats.strength // 10)
                bleed_dmg = int(max(result.actor.stats.strength // 2, result.damage) * (1 - resist))
                bleed_dmg = max(1, int(random.randint(bleed_dmg // 4, bleed_dmg) * 0.75))
                result.target.physical_effects["Bleed"] = StatusEffect(True,
                                                              max(duration, result.target.physical_effects["Bleed"].duration),
                                                              max(bleed_dmg, result.target.physical_effects["Bleed"].extra))
        return results


class Stinger(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Stinger", damage=10, crit=0.25, description="", off=False)
        self.special = True
        self.att_name = 'stings'

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        resist = result.target.check_mod('resist', enemy=result.actor, typ="Poison")
        if resist < 1 and not any(["Status-Poison" in result.target.status_immunity, "Status-All" in result.target.status_immunity]):
            if random.randint((result.actor.check_mod("speed", enemy=result.target) * result.crit) // 2,
                              (result.actor.check_mod("speed", enemy=result.target) * result.crit)) \
                    > random.randint(result.target.stats.con // 2, result.target.stats.con):
                if not result.target.status_effects["Poison"].active:
                    result.target.status_effects["Poison"].active = True
                    result.effects_applied['Status'].append('Poison')
                else:
                    result.effects_applied['Status'].append('Poison+')
                duration = max(1, result.actor.check_mod("speed", enemy=result.target) // 10)
                damage = int(result.target.health.max * 0.01)
                pois_dmg = max(1, int(damage * (1 - resist)))
                result.target.status_effects["Poison"] = StatusEffect(True,
                                                               max(duration, result.target.status_effects["Poison"].duration),
                                                               max(pois_dmg, result.target.status_effects["Poison"].extra))
        return results


class Pincers(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Pincers", damage=8, crit=0.15, description="", off=True)
        self.special = True
        self.att_name = 'bites'

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not result.hit or not result.damage:
            return results
        if random.randint(result.actor.check_mod("speed", enemy=result.target) // 2, result.actor.check_mod("speed", enemy=result.target)) \
            > random.randint(result.target.stats.con // 2, result.target.stats.con):
            resist = result.target.check_mod('resist', enemy=result.actor, typ="Poison")
            if resist < 1 and not any(["Status-Poison" in result.target.status_immunity,
                                       "Status-All" in result.target.status_immunity]):
                if not result.target.status_effects["Poison"].active:
                    result.target.status_effects["Poison"].active = True
                    result.effects_applied['Status'].append('Poison')
                else:
                    result.effects_applied['Status'].append('Poison+')
                duration = max(1, result.actor.check_mod("speed", enemy=result.target) // 10)
                damage = int(result.target.health.max * 0.01)
                pois_dmg = max(1, int(damage * (1 - resist)))
                result.target.status_effects["Poison"] = StatusEffect(True,
                                                               max(duration, result.target.status_effects["Poison"].duration),
                                                               max(pois_dmg, result.target.status_effects["Poison"].extra))
            if not any(["Stun" in result.target.status_immunity,
                        f"Status-Stun" in result.target.equipment["Pendant"].mod,
                        "Status-All" in result.target.equipment["Pendant"].mod]):
                if not result.target.status_effects["Stun"].active:
                    p_resist = result.target.check_mod('resist', enemy=result.actor, typ='Physical')
                    if result.crit > 1:
                        att_roll = int(
                            random.randint(result.actor.stats.strength // 2, result.actor.stats.strength) * (1 - p_resist)
                        )
                        def_roll = random.randint(result.target.stats.con // 2, result.target.stats.con)
                        if result.target.stun_contest_success(result.actor, att_roll, def_roll):
                            s_duration = max(1, result.actor.stats.strength // 10)
                            if result.target.apply_stun(s_duration, source=self.name, applier=result.actor):
                                result.effects_applied['Status'].append('Stun')
        return results


class Pincers2(Pincers):

    def __init__(self):
        super().__init__()
        self.damage = 12
        self.crit = 0.2


class DemonClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Demon Claw", damage=10, crit=0.25, description="", off=True)
        self.special = True
        self.att_name = 'claws'

    def special_effect(self, results: CombatResultGroup) -> None:
        # Extract caster and target from combat results
        if results.results:
            caster = results.results[0].actor
            target = results.results[0].target
            if caster and target:
                doom_message = abilities.Doom().cast(caster, target, special=True)
                if doom_message:
                    results.results[0].message += str(doom_message)
        return results


class DemonClaw2(DemonClaw):

    def __init__(self):
        super().__init__()
        self.damage = 30
        self.crit = 0.33
        self.special = True

    def special_effect(self, results: CombatResultGroup) -> None:
        if results.results:
            caster = results.results[0].actor
            target = results.results[0].target
            if caster and target:
                abilities.Desoul().cast(caster, target, special=True)
        return results


class SnakeFang(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Snake Fang", damage=10, crit=0.25, description="", off=False)
        self.special = True
        self.att_name = 'strikes'

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        resist = result.target.check_mod('resist', enemy=result.actor, typ="Poison")
        if resist < 1 and not any(["Status-Poison" in result.target.status_immunity, "Status-All" in result.target.status_immunity]):
            if random.randint((result.actor.check_mod("speed", enemy=result.target) * result.crit) // 2,
                              (result.actor.check_mod("speed", enemy=result.target) * result.crit)) \
                    > random.randint(result.target.stats.con // 2, result.target.stats.con):
                if not result.target.status_effects["Poison"].active:
                    result.target.status_effects["Poison"].active = True
                    result.effects_applied['Status'].append('Poison')
                else:
                    result.effects_applied['Status'].append('Poison+')
                duration = max(1, result.actor.check_mod("speed", enemy=result.target) // 10)
                damage = int(result.target.health.max * 0.005)
                pois_dmg = max(1, int(damage * (1 - resist)))
                result.target.status_effects["Poison"] = StatusEffect(True,
                                                               max(duration, result.target.status_effects["Poison"].duration),
                                                               max(pois_dmg, result.target.status_effects["Poison"].extra))
        return results


class SnakeFang2(SnakeFang):

    def __init__(self):
        super().__init__()
        self.damage = 32
        self.crit = 0.33


class AlligatorTail(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Alligator Tail", damage=24, crit=0.1, description="", off=False)
        self.special = True
        self.att_name = 'swipes'

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not any(["Stun" in result.target.status_immunity,
                    f"Status-Stun" in result.target.equipment["Pendant"].mod,
                    "Status-All" in result.target.equipment["Pendant"].mod]):
            if not result.target.status_effects["Stun"].active:
                resist = result.target.check_mod('resist', enemy=result.actor, typ='Physical')
                if resist < 1:
                    if result.crit > 1:
                        att_roll = int(
                            random.randint(result.actor.stats.strength // 2, result.actor.stats.strength) * (1 - resist)
                        )
                        def_roll = random.randint(result.target.stats.con // 2, result.target.stats.con)
                        if result.target.stun_contest_success(result.actor, att_roll, def_roll):
                            duration = max(1, result.actor.stats.strength // 10)
                            if result.target.apply_stun(duration, source=self.name, applier=result.actor):
                                result.effects_applied['Status'].append('Stun')
        return results


class LionPaw(NaturalWeapon):
    """
    Chance to berserk enemy
    """

    def __init__(self):
        super().__init__(name="Lion Paw", damage=34, crit=0.15, description="", off=True)
        self.att_name = 'swipes'

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not any(["Berserk" in result.target.status_immunity,
                "Status-Berserk" in result.target.equipment["Pendant"].mod,
                "Status-All" in result.target.equipment["Pendant"].mod]):
            if not result.target.status_effects["Berserk"].active:
                if result.crit > 1:
                    if random.randint(0, result.actor.stats.strength) > random.randint(result.target.stats.con // 2, result.target.stats.con):
                        duration = max(3, result.actor.stats.strength // 10)
                        result.target.status_effects["Berserk"] = StatusEffect(True, duration)
                        result.effects_applied['Status'].append('Berserk')
        return results


class Laser(NaturalWeapon):
    """
    ignores armor
    """

    def __init__(self):
        super().__init__(name="Laser", damage=40, crit=0.25, description="", off=True)
        self.ignore = True
        self.att_name = 'zaps'


class Laser2(Laser):
    """
    Chance on crit to permanently damage the enemy, reducing a random stat by 1
    """

    def __init__(self):
        super().__init__()
        self.damage = 70
        self.crit = 0.4
        self.special = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        # Luck should reduce proc chance, but it shouldn't fully shut off the effect.
        # Cap the luck term so the threshold never reaches/exceeds 1.0 (which would disable procs).
        t_chance = min(0.015, result.target.check_mod('luck', enemy=result.actor, luck_factor=20) / 100)
        if result.crit > 1:
            # Balance tuning: permanent primary-stat damage is swingy and can
            # be punishing in long runs. Convert to a temporary combat-stat
            # debuff that matters immediately, with a lower proc chance.
            #
            # Proc chance ~ 2% on crit at low-CHA targets, reduced by luck.
            if random.random() > 0.98 + t_chance:
                stat_list = ["Attack", "Defense", "Magic", "Magic Defense", "Speed"]
                stat_name = random.choice(stat_list)
                eff = result.target.stat_effects.get(stat_name)
                if eff is not None:
                    duration = 5
                    amount = 10
                    eff.active = True
                    eff.duration = max(duration, eff.duration)
                    # Negative extra applies as a debuff in check_mod().
                    eff.extra = min(int(getattr(eff, "extra", 0) or 0), -amount) if eff.extra < 0 else -amount
                    result.effects_applied['Stat'].append(f"{stat_name} Down")
        return results


class Gaze(NaturalWeapon):
    """
    Attempts to turn the player_char to stone
    """

    def __init__(self):
        super().__init__(name="Gaze", damage=0, crit=0, description="", off=False)
        self.special = True
        self.att_name = 'leers'

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results.results[-1]
        result.extra[self.att_name] = True
        # Cast Petrify with proper actor and target from the combat result
        abilities.Petrify().cast(result.actor, result.target, special=True)
        return results


class DragonClaw(NaturalWeapon):
    """
    ignores armor
    """

    def __init__(self):
        super().__init__(name="Dragon Claw", damage=28, crit=0.2, description="", off=True)
        self.ignore = True
        self.att_name = 'rakes'


class DragonClaw2(DragonClaw):

    def __init__(self):
        super().__init__()
        self.damage = 70
        self.crit = 0.33
        self.special = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        resist = result.target.check_mod('resist', enemy=result.actor, typ='Physical')
        if resist < 1:
            if random.randint(0, result.actor.stats.strength * result.crit) \
                    > random.randint(result.target.stats.con // 2, result.target.stats.con):
                if not result.target.physical_effects["Bleed"].active:
                    result.target.physical_effects["Bleed"].active = True
                    result.effects_applied['Physical'].append('Bleed')
                else:
                    result.effects_applied['Physical'].append('Bleed+')
                duration = max(1, result.actor.stats.strength // 10)
                bleed_dmg = int(max(result.actor.stats.strength // 2, result.damage) * (1 - resist))
                bleed_dmg = max(1, int(random.randint(bleed_dmg // 4, bleed_dmg) * 0.75))
                result.target.physical_effects["Bleed"] = StatusEffect(True,
                                                              max(duration, result.target.physical_effects["Bleed"].duration),
                                                              max(bleed_dmg, result.target.physical_effects["Bleed"].extra))
        return results


class DragonTail(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Dragon Tail", damage=40, crit=0.15, description="", off=True)
        self.att_name = 'swipes'


class DragonTail2(DragonTail):

    def __init__(self):
        super().__init__()
        self.damage = 90
        self.crit = 0.3
        self.special = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not any(["Stun" in result.target.status_immunity,
                    f"Status-Stun" in result.target.equipment["Pendant"].mod,
                    "Status-All" in result.target.equipment["Pendant"].mod]):
            if not result.target.status_effects["Stun"].active:
                resist = result.target.check_mod('resist', enemy=result.actor, typ='Physical')
                if resist < 1:
                    if result.crit > 1:
                        att_roll = int(
                            random.randint(0, int(result.actor.stats.strength * result.crit)) * (1 - resist)
                        )
                        def_roll = random.randint(result.target.stats.con // 2, result.target.stats.con)
                        if result.target.stun_contest_success(result.actor, att_roll, def_roll):
                            duration = max(1, result.actor.stats.strength // 10)
                            if result.target.apply_stun(duration, source=self.name, applier=result.actor):
                                result.effects_applied['Status'].append('Stun')
        return results


class NightmareHoof(NaturalWeapon):
    """
    Natural weapon of Nightmare; additional fire damage
    """

    def __init__(self):
        super().__init__(name="Nightmare Hoof", damage=26, crit=0.25, description="", off=True)
        self.special = True
        self.att_name = 'attacks'
        self.element = "Fire"

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        resist = result.target.check_mod('resist', enemy=result.actor, typ=self.element)
        damage = int(random.randint(result.actor.stats.intel // 2, result.actor.stats.intel) * (1 - resist))
        result.target.health.current -= damage
        if damage > 0:
            pass
        elif damage < 0:
            result.healing[-1] = abs(damage)
        return results


class ElementalBlade(NaturalWeapon):
    """
    Innate weapon possessed by Myrmidons; does elemental damage based on the enemy type
    """

    def __init__(self):
        super().__init__(name="Elemental Blade", damage=30, crit=0.25, description="", off=True)
        self.special = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        elemental_type = max(result.actor.resistance, key=result.actor.resistance.get)
        resist = result.target.check_mod('resist', enemy=result.actor, typ=elemental_type)
        damage = int(result.damage * (1 - resist))
        if damage < 0:
            result.healing = abs(damage)
        elif damage > 0:
            result.damage += damage
        result.target.health.current -= damage
        if damage > 0 and elemental_type == "Fire" and result.target.is_alive():
            if not result.target.magic_effects["DOT"].active:
                result.target.magic_effects["DOT"].active = True
                result.effects_applied['Magic'].append('Burn')
            result.target.magic_effects["DOT"] = StatusEffect(
                True,
                3,
                max(int(damage // 2), result.target.magic_effects["DOT"].extra),
                "Burn",
            )
        return results


class Tentacle(NaturalWeapon):
    """
    Chance to trip and leave prone
    """

    def __init__(self):
        super().__init__(name="Tentacle", damage=24, crit=0.2, description="A slender, flexible limb or appendage in an "
                                                                          "animal, especially around the mouth of an "
                                                                          "invertebrate, used for grasping or moving "
                                                                          "about, or bearing sense organs.",
                         off=True)
        self.special = True

    def special_effect(self, results: CombatResultGroup) -> None:
        # Weapon special effects operate on CombatResultGroup; data-driven skills
        # expect (user, target). Apply the effect to the last hit's actor/target
        # and append the generated message.
        result = results[-1]
        try:
            from .constants import TENTACLE_TRIP_PROC_CHANCE
            if random.random() > float(TENTACLE_TRIP_PROC_CHANCE):
                return results
        except Exception:
            # If the tuning constant can't be loaded, fall back to current behavior.
            pass
        try:
            msg = abilities.Trip().use(result.actor, target=result.target, fam=True)
            if msg:
                result.message += str(msg)
        except Exception:
            pass
        return results


class Tentacle2(Tentacle):
    """
    Chance to stun
    """

    def __init__(self):
        super().__init__()
        self.damage = 48
        self.crit = 0.3
        self.special = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not any(["Stun" in result.target.status_immunity,
                    f"Status-Stun" in result.target.equipment["Pendant"].mod,
                    "Status-All" in result.target.equipment["Pendant"].mod]):
            if not result.target.status_effects["Stun"].active:
                resist = result.target.check_mod('resist', enemy=result.actor, typ='Physical')
                if resist < 1:
                    if result.crit > 1:
                        att_roll = int(
                            random.randint(result.actor.stats.strength // 2, result.actor.stats.strength) * (1 - resist)
                        )
                        def_roll = random.randint(result.target.stats.con // 2, result.target.stats.con)
                        if result.target.stun_contest_success(result.actor, att_roll, def_roll):
                            duration = max(1, result.actor.stats.strength // 10)
                            result.target.apply_stun(duration, source=self.name, applier=result.actor)
        return results


class InvisibleBlade(NaturalWeapon):
    """
    Shadow element
    Only stuns on crit
    """

    def __init__(self):
        super().__init__(name="Invisible Blade", damage=18, crit=0.25, description="", off=True)
        self.special = True
        self.element = "Shadow"

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not any(["Stun" in result.target.status_immunity,
                    f"Status-Stun" in result.target.equipment["Pendant"].mod,
                    "Status-All" in result.target.equipment["Pendant"].mod]):
            if not result.target.status_effects["Stun"].active:
                resist = result.target.check_mod('resist', enemy=result.actor, typ='Physical')
                if resist < 1:
                    if result.crit > 1:
                        spd = result.actor.check_mod("speed", enemy=result.target)
                        att_roll = int(random.randint(0, spd // 2) * (1 - resist))
                        def_roll = random.randint(result.target.stats.con // 2, result.target.stats.con)
                        if result.target.stun_contest_success(result.actor, att_roll, def_roll):
                            duration = 1
                            result.target.apply_stun(duration, source=self.name, applier=result.actor)
        return results


class CerberusClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name='claws', damage=40, crit=0.25, description="", off=True)
        self.special = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        resist = result.target.check_mod('resist', enemy=result.actor, typ='Physical')
        if resist < 1:
            if random.randint((result.actor.stats.strength // 2) * result.crit, result.actor.stats.strength * result.crit) \
                    > random.randint(result.target.stats.con // 2, result.target.stats.con):
                if not result.target.physical_effects["Bleed"].active:
                    result.target.physical_effects["Bleed"].active = True
                    result.effects_applied['Physical'].append('Bleed')
                else:
                    result.effects_applied['Physical'].append('Bleed+')
                duration = max(1, result.actor.stats.strength // 10)
                bleed_dmg = int(max(result.actor.stats.strength // 2, result.damage) * (1 - resist))
                bleed_dmg = max(1, int(random.randint(bleed_dmg // 4, bleed_dmg) * 0.75))
                result.target.physical_effects["Bleed"] = StatusEffect(
                    True, max(duration, result.target.physical_effects["Bleed"].duration),
                    max(bleed_dmg, result.target.physical_effects["Bleed"].extra))
        return results


class CerberusBite(NaturalWeapon):

    def __init__(self):
        super().__init__(name="bites", damage=60, crit=0.25, description="", off=False)
        self.special = True
        self.element = "Fire"

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        resist = result.target.check_mod('resist', enemy=result.actor, typ=self.element)
        damage = int(random.randint(result.damage // 2, result.damage) * (1 - resist))
        result.target.health.current -= damage
        if damage > 0:
            result.damage += damage
        elif damage < 0:
            result.healing = abs(damage)
        return results


class LichHand(NaturalWeapon):
    """
    Chance to paralyze (stun) enemy
    """

    def __init__(self):
        super().__init__(name="touches", damage=35, crit=0.2, description="", off=True)
        self.special = True
        self.element = "Ice"

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not any(["Stun" in result.target.status_immunity,
                    f"Status-Stun" in result.target.equipment["Pendant"].mod,
                    "Status-All" in result.target.equipment["Pendant"].mod]):
            if not result.target.status_effects["Stun"].active:
                if result.crit > 1:
                    att_roll = random.randint(result.actor.stats.intel // 4, result.actor.stats.intel)
                    def_roll = random.randint(result.target.stats.wisdom // 2, result.target.stats.wisdom)
                    if result.target.stun_contest_success(result.actor, att_roll, def_roll):
                        duration = max(1, result.actor.stats.intel // 10)
                        result.target.apply_stun(duration, source=self.name, applier=result.actor)
        return results


class Cannon(NaturalWeapon):
    """
    Chance to stun the target
    """

    def __init__(self):
        super().__init__(name="attacks", damage=80, crit=0.15, description="", off=True)
        self.special = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not any(["Stun" in result.target.status_immunity,
                    f"Status-Stun" in result.target.equipment["Pendant"].mod,
                    "Status-All" in result.target.equipment["Pendant"].mod]):
            if not result.target.status_effects["Stun"].active:
                if result.crit > 1:
                    att_roll = random.randint(result.actor.stats.strength // 4, result.actor.stats.strength)
                    def_roll = random.randint(result.target.stats.con // 2, result.target.stats.con)
                    if result.target.stun_contest_success(result.actor, att_roll, def_roll):
                        duration = max(1, result.actor.stats.strength // 10)
                        result.target.apply_stun(duration, source=self.name, applier=result.actor)
        return results


class DevilBlade(NaturalWeapon):
    """
    Chance on crit to apply one of the following status effects: Silence, Stun, Doom, Blind, Sleep, Poison, or Berserk
    """

    def __init__(self):
        super().__init__(name='attacks', damage=100, crit=0.33, description="", off=True)
        self.special = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not result.hit or not result.damage:
            return results
        w_chance = result.actor.check_mod('luck', enemy=result.target, luck_factor=10)
        t_chance = result.target.check_mod('luck', enemy=result.actor, luck_factor=20)
        if result.crit > 1:
            # Only 25% chance for status effect to apply even on crit
            if random.random() < 0.1:
                if random.randint(0, w_chance) > random.randint(0, t_chance):
                    effect = random.choice(list(result.target.status_effects.keys()))
                    if any([effect in result.target.status_immunity,
                            f"Status-{effect}" in result.target.equipment["Pendant"].mod,
                            "Status-All" in result.target.equipment["Pendant"].mod]):
                        return results
                    result.target.status_effects[effect] = StatusEffect(
                        True, max(random.randint(1, 5), result.target.status_effects[effect].duration))
                    if effect == "Poison":
                        damage = int(result.target.health.max * 0.05)
                        result.target.status_effects["Poison"].extra += damage  # damage builds over time
        return results


# Armor items
class NoArmor(Armor):

    def __init__(self):
        super().__init__(name="No Armor", description="No armor equipped.", value=0, rarity=0, armor=0,
                         subtyp='None', unequip=True)


class NoHelmet(Helmet):

    def __init__(self):
        super().__init__(name="No Helmet", description="No helmet equipped.", value=0, rarity=0, armor=0,
                         subtyp='None', unequip=True)


class ClothCap(Helmet):

    def __init__(self):
        super().__init__(name="Cloth Cap", description="A simple padded cap that offers modest protection without "
                                                        "interfering with spellcasting.",
                         value=45, rarity=0.95, armor=1, subtyp='Cloth', unequip=False)
        self.weight = 1


class Jaapi(Helmet):

    def __init__(self):
        super().__init__(name="Jaapi", description="A quilted cloth head wrap that cushions blows while staying light "
                                                  "enough for spellwork.",
                         value=180, rarity=0.9, armor=2, subtyp='Cloth', unequip=False)
        self.weight = 1


class Turban(Helmet):

    def __init__(self):
        super().__init__(name="Turban", description="Layered cloth wound into a protective wrap that softens glancing "
                                                    "strikes.",
                         value=550, rarity=0.8, armor=3, subtyp='Cloth', unequip=False)
        self.weight = 1


class WitchHat(Helmet):

    def __init__(self):
        super().__init__(name="Witch Hat", description="A tall enchanted hat stiffened with hidden ribs and protective "
                                                       "wards.",
                         value=1600, rarity=0.65, armor=4, subtyp='Cloth', unequip=False)
        self.weight = 1


class EnchantedHood(Helmet):

    def __init__(self):
        super().__init__(name="Enchanted Hood", description="A hood embroidered with protective thread that turns "
                                                            "aside glancing blows.",
                         value=3500, rarity=0.5, armor=5, subtyp='Cloth', unequip=False)
        self.weight = 1


class MitreHat(Helmet):

    def __init__(self):
        super().__init__(name="Mitre Hat", description="A ceremonial mitre reinforced with sacred thread and geomantic "
                                                       "sigils.",
                         value=10000, rarity=0.4, armor=9, subtyp='Cloth', unequip=False)
        self.weight = 1
        self.restriction = ['Priest', 'Archbishop', 'Diviner', 'Astromancer']


class Circlet(Helmet):

    def __init__(self):
        super().__init__(name="Circlet", description="A thin metal circlet that focuses the wearer's will into a "
                                                     "protective halo.",
                         value=12000, rarity=0.4, armor=8, subtyp='Cloth', unequip=False)
        self.weight = 2
        self.restricted_against = ['Priest', 'Archbishop', 'Diviner', 'Astromancer']


class CohuleenDruith(Helmet):

    def __init__(self):
        super().__init__(name="Cohuleen Druith", description="A fey cap steeped in old river magic and woven with "
                                                            "reeds from a hidden ford.",
                         value=40000, rarity=0.2, armor=10, subtyp='Cloth', unequip=False)
        self.weight = 1
        self.element = "Water"
        self.resist_mod = 0.5


class AriadnesDiadem(Helmet):

    def __init__(self):
        super().__init__(name="Ariadne's Diadem", description="A legendary diadem whose threadlike filigree guides the "
                                                             "wearer safely through impossible danger.",
                         value=0, rarity=0, armor=12, subtyp='Cloth', unequip=False)
        self.weight = 1
        self.special = True


class LeatherCap(Helmet):

    def __init__(self):
        super().__init__(name="Leather Cap", description="A boiled leather cap that protects the head while keeping "
                                                         "movement light.",
                         value=80, rarity=0.95, armor=2, subtyp='Light', unequip=False)
        self.weight = 2


class PithHelmet(Helmet):

    def __init__(self):
        super().__init__(name="Pith Helmet", description="A stiffened light helmet with a broad brim and padded crown.",
                         value=700, rarity=0.85, armor=3, subtyp='Light', unequip=False)
        self.weight = 3


class WarMask(Helmet):

    def __init__(self):
        super().__init__(name="War Mask", description="A hardened leather mask shaped to intimidate and deflect cuts.",
                         value=1800, rarity=0.75, armor=4, subtyp='Light', unequip=False)
        self.weight = 2


class ArmingCap(Helmet):

    def __init__(self):
        super().__init__(name="Arming Cap", description="A reinforced cap worn under heavier helms or alone by light "
                                                       "fighters.",
                         value=8500, rarity=0.5, armor=5, subtyp='Light', unequip=False)
        self.weight = 3


class Katapu(Helmet):

    def __init__(self):
        super().__init__(name="Katapu", description="A light protective headpiece built from layered plates and lacquered "
                                                   "leather.",
                         value=18000, rarity=0.4, armor=7, subtyp='Light', unequip=False)
        self.weight = 2


class Somen(Helmet):

    def __init__(self):
        super().__init__(name="Sōmen", description="A full-face light helm that protects without sacrificing agility.",
                         value=48000, rarity=0.2, armor=10, subtyp='Light', unequip=False)
        self.weight = 4


class DemonCowl(Helmet):

    def __init__(self):
        super().__init__(name="Demon Cowl", description="A sinister cowl threaded with funereal charms and ash-dark "
                                                       "silk.",
                         value=0, rarity=0, armor=16, subtyp='Light', unequip=False)
        self.weight = 4
        self.special = True
        self.element = "Death"
        self.resist_mod = 0.5


class ScaleHelm(Helmet):

    def __init__(self):
        super().__init__(name="Scale Helm", description="A sturdy helmet of overlapping metal scales.",
                         value=120, rarity=0.95, armor=3, subtyp='Medium', unequip=False)
        self.weight = 4


class ChainCoif(Helmet):

    def __init__(self):
        super().__init__(name="Chain Coif", description="A hood of interlocking metal rings worn under or instead of "
                                                        "a helmet.",
                         value=900, rarity=0.85, armor=4, subtyp='Medium', unequip=False)
        self.weight = 5


class KulahKhud(Helmet):

    def __init__(self):
        super().__init__(name="Kulah Khud", description="A domed medium helm with cheek guards and a mail aventail.",
                         value=2400, rarity=0.75, armor=6, subtyp='Medium', unequip=False)
        self.weight = 4


class Cervelliere(Helmet):

    def __init__(self):
        super().__init__(name="Cervelliere", description="A close-fitting steel skullcap that can be worn beneath other "
                                                        "headgear.",
                         value=10000, rarity=0.5, armor=8, subtyp='Medium', unequip=False)
        self.weight = 8


class VisoredSallet(Helmet):

    def __init__(self):
        super().__init__(name="Visored Sallet", description="A fitted steel helmet with a narrow visor and strong "
                                                            "neck guard.",
                         value=22000, rarity=0.4, armor=10, subtyp='Medium', unequip=False)
        self.weight = 6


class Tolga(Helmet):

    def __init__(self):
        super().__init__(name="Tolga", description="A heavy medium helm with reinforced bands and a high nasal guard.",
                         value=22000, rarity=0.4, armor=10, subtyp='Medium', unequip=False)
        self.weight = 6


class Tarnhelm(Helmet):

    def __init__(self):
        super().__init__(name="Tarnhelm", description="A mythic helm that bends sight around its wearer and grants "
                                                     "invisibility.",
                         value=55000, rarity=0.2, armor=13, subtyp='Medium', unequip=False)
        self.weight = 11
        self.special = True


class HelmOfRostam(Helmet):

    def __init__(self):
        super().__init__(name="Helm of Rostam", description="A heroic medium helm whose crest steadies the wearer "
                                                            "against panic and stunning blows.",
                         value=0, rarity=0, armor=19, subtyp='Medium', unequip=False)
        self.weight = 8
        self.mod = "Status-Berserk Status-Stun"
        self.special = True


class IronHelm(Helmet):

    def __init__(self):
        super().__init__(name="Iron Helm", description="A heavy iron helmet that favors protection over comfort.",
                         value=160, rarity=0.95, armor=4, subtyp='Heavy', unequip=False)
        self.weight = 6


class KettleHelm(Helmet):

    def __init__(self):
        super().__init__(name="Kettle Helm", description="A brimmed iron helmet that sheds blows away from the face and "
                                                        "neck.",
                         value=1200, rarity=0.85, armor=6, subtyp='Heavy', unequip=False)
        self.weight = 5


class Barbute(Helmet):

    def __init__(self):
        super().__init__(name="Barbute", description="A heavy helm with a T-shaped opening and strong cheek protection.",
                         value=3200, rarity=0.75, armor=8, subtyp='Heavy', unequip=False)
        self.weight = 7


class GreatHelm(Helmet):

    def __init__(self):
        super().__init__(name="Great Helm", description="A full steel helm with narrow eye slits and thick plates.",
                         value=13000, rarity=0.5, armor=10, subtyp='Heavy', unequip=False)
        self.weight = 8


class PlateHelm(Helmet):

    def __init__(self):
        super().__init__(name="Plate Helm", description="A masterwork plate helmet that completes a knight's "
                                                        "heavy armor kit.",
                         value=28000, rarity=0.4, armor=12, subtyp='Heavy', unequip=False)
        self.weight = 9


class CloseHelm(Helmet):

    def __init__(self):
        super().__init__(name="Close Helm", description="A fully enclosing heavy helm with a fitted visor and reinforced "
                                                       "gorget.",
                         value=62000, rarity=0.2, armor=18, subtyp='Heavy', unequip=False)
        self.weight = 14


class Kabuto(Helmet):

    def __init__(self):
        super().__init__(name="Kabuto", description="A legendary heavy helm with layered plates and a commanding crest.",
                         value=0, rarity=0, armor=25, subtyp='Heavy', unequip=False)
        self.weight = 16
        self.special = True


class Tunic(Armor):

    def __init__(self):
        super().__init__(name="Tunic", description="A close-fitting short coat as part of a uniform, especially a "
                                                   "police or military uniform.",
                         value=60, rarity=0.95, armor=2, subtyp='Cloth', unequip=False)
        self.weight = 2


class ClothCloak(Armor):

    def __init__(self):
        super().__init__(name="Cloth Cloak", description="An outdoor cloth garment, typically sleeveless, that hangs "
                                                         "loosely from the shoulders.",
                         value=200, rarity=0.9, armor=4, subtyp='Cloth', unequip=False)
        self.weight = 2


class SilverCloak(Armor):

    def __init__(self):
        super().__init__(name="Silver Cloak", description="A cloak weaved with strands of silver to improve protective "
                                                          "power.",
                         value=2500, rarity=0.85, armor=6, subtyp='Cloth', unequip=False)
        self.weight = 3


class GoldCloak(Armor):

    def __init__(self):
        super().__init__(name="Gold Cloak", description="A cloak weaved with strands of gold to improve protective "
                                                        "power.",
                         value=7000, rarity=0.75, armor=10, subtyp='Cloth', unequip=False)
        self.weight = 4


class CloakEnchantment(Armor):

    def __init__(self):
        super().__init__(name="Cloak of Enchantment", description="A magical cloak that shields the wearer from all "
                                                                  "forms of attack.",
                         value=22000, rarity=0.5, armor=14, subtyp='Cloth', unequip=False)
        self.weight = 3


class WizardRobe(Armor):

    def __init__(self):
        super().__init__(name="Wizard's Robe", description="A knee-length, long-sleeved robe with an impressive hood "
                                                           "designed to add a mysterious feel to magic users.",
                         value=45000, rarity=0.4, armor=20, subtyp='Cloth', unequip=False)
        self.weight = 4


class Tarnkappe(Armor):

    def __init__(self):
        super().__init__(name="Tarnkappe", description="A tarnkappe is a mythical garment that grants its wearer the "
                                                       "power to become invisible and move undetected. The Tarnkappe "
                                                       "is depicted as a dark, enchanted cloak or hood, embodying the "
                                                       "idea of secrecy, stealth, and mysticism.",
                         value=90000, rarity=0.2, armor=24, subtyp='Cloth', unequip=False)
        self.weight = 1


class MerlinRobe(Armor):

    def __init__(self):
        super().__init__(name="Robes of Merlin", description="The enchanted robes of Merlin the enchanter.",
                         value=0, rarity=0., armor=30, subtyp='Cloth', unequip=False)
        self.weight = 2

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        mana = getattr(result.target, "mana", None)
        if mana is None:
            return results
        amount = max(1, int((result.damage or 0) * 0.25))
        before = mana.current
        mana.current = min(mana.max, mana.current + amount)
        restored = mana.current - before
        if restored > 0:
            result.extra["Mana Restored"] = restored
            result.message += f"{result.target.name}'s Robes of Merlin restore {restored} mana.\n"
        return results


class PaddedArmor(Armor):

    def __init__(self):
        super().__init__(name="Padded Armor", description="Consists of quilted layers of cloth and feathers to provide"
                                                          " some protection from attack.",
                         value=75, rarity=0.95, armor=4, subtyp='Light', unequip=False)
        self.weight = 4


class LeatherArmor(Armor):

    def __init__(self):
        super().__init__(name="Leather Armor", description="A protective covering made of animal hide, boiled to make "
                                                           "it tough and rigid and worn over the torso to protect it "
                                                           "from injury.",
                         value=600, rarity=0.85, armor=6, subtyp='Light', unequip=False)
        self.weight = 5


class Cuirboulli(Armor):

    def __init__(self):
        super().__init__(name="Cuirboulli", description="French for \"boiled leather\", this armor has increased "
                                                        "rigidity for add protection",
                         value=3000, rarity=0.75, armor=8, subtyp='Light', unequip=False)
        self.weight = 6


class StuddedLeather(Armor):

    def __init__(self):
        super().__init__(name="Studded Leather", description="Leather armor embedded with iron studs to improve "
                                                             "defensive capabilities.",
                         value=20000, rarity=0.5, armor=16, subtyp='Light', unequip=False)
        self.weight = 7


class StuddedCuirboulli(Armor):

    def __init__(self):
        super().__init__(name="Studded Cuirboulli", description="Boiled leather armor embedded with iron studs to "
                                                                "improve defensive capabilities.",
                         value=42000, rarity=0.4, armor=24, subtyp='Light', unequip=False)
        self.weight = 8


class MithrilCoat(Armor):

    def __init__(self):
        super().__init__(name="Mithril Coat", description="A mithril coat is a lightweight, shimmering shirt of armor "
                                                          "made from mithril, a rare and incredibly strong metal. "
                                                          "Known for its silver-like appearance and superior "
                                                          "durability, the mithril coat offers exceptional protection"
                                                          " while remaining much lighter than traditional steel armor.",
                         value=95000, rarity=0.2, armor=28, subtyp='Light', unequip=False)
        self.weight = 2


class DragonHide(Armor):

    def __init__(self):
        super().__init__(name="Dragon Hide", description="Hide armor made from the scales of a red dragon, "
                                                         "inconceivably light for this type of armor.",
                         value=0, rarity=0., armor=36, subtyp='Light', unequip=False)
        self.weight = 10
        self.special = True
        self.element = "Fire"

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not result.actor or not result.target:
            return results
        try:
            resist = result.actor.check_mod('resist', enemy=result.target, typ=self.element)
        except KeyError:
            resist = 0
        damage = max(0, int((result.damage or 0) * 0.25 * (1 - resist)))
        if damage > 0:
            result.actor.health.current -= damage
            result.extra["Dragon Hide Damage"] = damage
            result.effects_applied['Magic'].append(self.element)
            result.message += f"{result.target.name}'s Dragon Hide scorches {result.actor.name} for {damage} fire damage.\n"
        return results


class HideArmor(Armor):

    def __init__(self):
        super().__init__(name="Hide Armor", description="A crude armor made from thick furs and pelts.",
                         value=100, rarity=0.95, armor=6, subtyp='Medium', unequip=False)
        self.weight = 9


class ChainShirt(Armor):

    def __init__(self):
        super().__init__(name="Chain Shirt", description="A type of armor consisting of small metal rings linked "
                                                         "together in a pattern to form a mesh.",
                         value=800, rarity=0.85, armor=8, subtyp='Medium', unequip=False)
        self.weight = 12


class ScaleMail(Armor):

    def __init__(self):
        super().__init__(name="Scale Mail", description="Armor consisting of a coat and leggings of leather covered"
                                                        " with overlapping pieces of metal, mimicking the scales of a "
                                                        "fish.",
                         value=4000, rarity=0.75, armor=10, subtyp='Medium', unequip=False)
        self.weight = 10


class Breastplate(Armor):

    def __init__(self):
        super().__init__(name="Breastplate", description="Armor consisting of a fitted metal chest piece worn with "
                                                         "supple leather. Although it leaves the legs and arms "
                                                         "relatively unprotected, this armor provides good protection "
                                                         "for the wearer's vital organs while leaving the wearer "
                                                         "relatively unencumbered.",
                         value=23500, rarity=0.5, armor=18, subtyp='Medium', unequip=False)
        self.weight = 15


class HalfPlate(Armor):

    def __init__(self):
        super().__init__(name="Half Plate", description="Armor consisting of shaped metal plates that cover most of the"
                                                        " wearer's body. It does not include leg Protection beyond "
                                                        "simple greaves that are attached with leather straps.",
                         value=46000, rarity=0.4, armor=26, subtyp='Medium', unequip=False)
        self.weight = 20


class Kusari(Armor):

    def __init__(self):
        super().__init__(name="Kusari", description="Kusari armor is made from interconnected metal rings, providing "
                                                    "excellent flexibility and mobility. This chain mail offers robust"
                                                    " protection while allowing for ease of movement, making it ideal "
                                                    "for both ranged and close combat.",
                         value=100000, rarity=0.2, armor=32, subtyp='Medium', unequip=False)
        self.weight = 17


class Klivanion(Armor):

    def __init__(self):
        super().__init__(name="Klivanion", description="A lamellar breastplate whose charged plates lash attackers with "
                                                       "lightning and can stun them in place.",
                         value=0, rarity=0., armor=36, subtyp='Medium', unequip=False)
        self.weight = 18
        self.special = True
        self.element = "Electric"

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not result.actor or not result.target:
            return results
        damage = result.damage or 0
        if damage <= 0:
            return results
        try:
            resist = result.actor.check_mod('resist', enemy=result.target, typ=self.element)
        except KeyError:
            resist = 0
        shock_damage = max(0, int(damage * 0.15 * (1 - resist)))
        if shock_damage > 0:
            result.actor.health.current -= shock_damage
            result.extra["Klivanion Shock Damage"] = shock_damage
            result.effects_applied['Magic'].append(self.element)
            result.message += f"{result.target.name}'s Klivanion shocks {result.actor.name} for {shock_damage} lightning damage.\n"
        if shock_damage > 0 and random.random() < 0.25:
            stun = result.actor.status_effects.get("Stun")
            if stun and not stun.active and result.actor.apply_stun(1, source=self.name, applier=result.target):
                result.effects_applied['Status'].append('Stun')
                result.message += f"{result.actor.name} is stunned by the Klivanion.\n"
        return results


class RingMail(Armor):

    def __init__(self):
        super().__init__(name="Ring Mail", description="Leather armor with heavy rings sewn into it. The rings help "
                                                       "reinforce the armor against blows from Swords and axes.",
                         value=200, rarity=0.95, armor=8, subtyp='Heavy', unequip=False)
        self.weight = 15


class ChainMail(Armor):

    def __init__(self):
        super().__init__(name="Chain Mail", description="Made of interlocking metal rings, includes a layer of quilted "
                                                        "fabric worn underneath the mail to prevent chafing and to "
                                                        "cushion the impact of blows. The suit includes gauntlets.",
                         value=1000, rarity=0.85, armor=10, subtyp='Heavy', unequip=False)
        self.weight = 18


class Splint(Armor):

    def __init__(self):
        super().__init__(name="Splint Mail", description="Armor made of narrow vertical strips of metal riveted to a "
                                                         "backing of leather that is worn over cloth padding. Flexible "
                                                         "chain mail protects the joints.",
                         value=6000, rarity=0.75, armor=14, subtyp='Heavy', unequip=False)
        self.weight = 20


class PlateMail(Armor):

    def __init__(self):
        super().__init__(name="Plate Mail", description="Armor consisting of shaped, interlocking metal plates to "
                                                        "cover most of the body.",
                         value=27500, rarity=0.5, armor=20, subtyp='Heavy', unequip=False)
        self.weight = 25


class Palangina(Armor):

    def __init__(self):
        super().__init__(name="Palangina",
                         description="A Persian lamellar cuirass worked with fire-red and water-blue inlays.",
                         value=55000, rarity=0.4, armor=30, subtyp='Heavy', unequip=False)
        self.weight = 30
        self.resistances = {"Fire": 0.25, "Water": 0.25}


class Maximilian(Armor):

    def __init__(self):
        super().__init__(name="Maximilian", description="Maximilian armor is characterized by its intricate designs "
                                                        "and full-coverage plates. Known for its effectiveness in both"
                                                        " defense and mobility, this armor often features a "
                                                        "distinctive fluted design, which not only enhances its "
                                                        "aesthetic appeal but also reinforces the structure, providing"
                                                        " extra strength without adding excessive weight.",
                         value=110000, rarity=0.2, armor=40, subtyp='Heavy', unequip=False)
        self.weight = 30


class Genji(Armor):

    def __init__(self):
        super().__init__(name="Genji Armor", description="Mythical armor crafted by an unknown master blacksmith and "
                                                         "embued with protective enchantments that allow the user to "
                                                         "shrug off damage.",
                         value=0, rarity=0., armor=50, subtyp='Heavy', unequip=False)
        self.weight = 25
        self.special = True

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        if not result.target:
            return results
        reduction = max(1, int((result.damage or 0) * 0.20))
        result.target.health.current = min(result.target.health.max, result.target.health.current + reduction)
        result.healing = (result.healing or 0) + reduction
        result.extra["Genji Damage Recovered"] = reduction
        result.message += f"{result.target.name}'s Genji Armor shrugs off {reduction} damage.\n"
        return results


# Natural armor
class NaturalArmor(Armor):

    def __init__(self, name: str, armor: int, description: str) -> None:
        super().__init__(name=name, armor=armor, description=description, rarity=0, subtyp="Natural",
                         unequip=False, value=0)


class AnimalHide(NaturalArmor):

    def __init__(self):
        super().__init__(name='Animal Hide', armor=4, description="")


class AnimalHide2(AnimalHide):

    def __init__(self):
        super().__init__()
        self.armor = 12


class Carapace(NaturalArmor):

    def __init__(self):
        super().__init__(name='Carapace', armor=6, description="")


class StoneArmor(NaturalArmor):

    def __init__(self):
        super().__init__(name='Stone Armor', armor=8, description="")


class StoneArmor2(StoneArmor):

    def __init__(self):
        super().__init__()
        self.armor = 18


class SnakeScales(NaturalArmor):

    def __init__(self):
        super().__init__(name="Snake Scales", armor=6, description="")


class SnakeScales2(SnakeScales):

    def __init__(self):
        super().__init__()
        self.armor = 6


class DemonArmor(NaturalArmor):

    def __init__(self):
        super().__init__(name='Demon Armor', armor=8, description="")


class DemonArmor2(DemonArmor):
    """
    Deals additional shadow damage to attacker
    """

    def __init__(self):
        super().__init__()
        self.armor = 20
        self.special = True
        self.shadow_damage = 25

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        resist = result.actor.check_mod('resist', enemy=result.target, typ='Shadow')
        damage = int(random.randint(self.shadow_damage // 2, self.shadow_damage) * (1 - resist))
        result.actor.health.current -= damage
        if damage > 0:
            result.damage += damage
        elif damage < 0:
            result.healing = abs(damage)
        return results


class MetalPlating(NaturalArmor):

    def __init__(self):
        super().__init__(name='Metal Plating', armor=10, description="")


class DragonScale(NaturalArmor):

    def __init__(self):
        super().__init__(name='Dragon Scales', armor=12, description="")


class CerberusHide(NaturalArmor):
    """
    deals additional fire damage to attacker
    """

    def __init__(self):
        super().__init__(name='Cerberus Hide', armor=36, description="")
        self.special = True
        self.fire_damage = 50

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        resist = result.actor.check_mod('resist', enemy=result.target, typ='Fire')
        damage = int(random.randint(self.fire_damage // 2, self.fire_damage) * (1 - resist))
        result.actor.health.current -= damage
        if damage > 0:
            pass
        elif damage < 0:
            result.healing[-1] = abs(damage)
        return results


class DevilSkin(NaturalArmor):
    """
    deals additional non-elemental damage to attacker
    """

    def __init__(self):
        super().__init__(name='Devil Skin', armor=80, description="")
        self.special = True
        self.damage = 100

    def special_effect(self, results: CombatResultGroup) -> None:
        result = results[-1]
        a_chance = result.actor.check_mod('luck', enemy=result.target, luck_factor=10)
        damage = random.randint(self.damage // (1 + a_chance), self.damage)
        result.actor.health.current -= damage
        return results


# OffHand items
class NoOffHand(OffHand):

    def __init__(self):
        super().__init__(name="No OffHand", description="No off-hand equipped.", value=0, rarity=0, mod=0,
                         subtyp='None', unequip=True)


class Buckler(OffHand):

    def __init__(self):
        super().__init__(name="Buckler", description="A small round shield held by a handle or worn on the forearm.",
                         value=25, rarity=0.95, mod=0.05, subtyp='Shield', unequip=False)
        self.weight = 2


class Aspis(OffHand):

    def __init__(self):
        super().__init__(name="Aspis", description="An aspis is a heavy wooden shield with a handle at the edge and is "
                                                   "strapped to the forearm for greater mobility.",
                         value=100, rarity=0.9, mod=0.1, subtyp='Shield', unequip=False)
        self.weight = 10


class Targe(OffHand):

    def __init__(self):
        super().__init__(name="Targe", description="A targe is a circular, concave shield fitted with straps on the "
                                                   "inside to be attached to the forearm, featuring metal studs on the "
                                                   "face for durability and additional offensive power.",
                         value=500, rarity=0.85, mod=0.15, subtyp='Shield', unequip=False)
        self.weight = 7


class Glagwa(OffHand):

    def __init__(self):
        super().__init__(name="Glagwa", description="A glagwa is a bell-shaped shield made from iron and covered with "
                                                    "leather for improved durability.",
                         value=2500, rarity=0.75, mod=0.2, subtyp='Shield', unequip=False)
        self.weight = 13


class KiteShield(OffHand):

    def __init__(self):
        super().__init__(name="Kite Shield", description="A kite shield is a large, almond-shaped shield rounded at the"
                                                         " top and curving down to a point or rounded point at the "
                                                         "bottom. The term \"kite shield\" is a reference to the "
                                                         "shield's unique shape, and is derived from its supposed "
                                                         "similarity to a flying kite.",
                         value=15000, rarity=0.5, mod=0.25, subtyp='Shield', unequip=False)
        self.weight = 15


class Pavise(OffHand):

    def __init__(self):
        super().__init__(name="Pavise", description="A pavise is an oblong shield similar to a tower shield that "
                                                    "features a spike at the bottom to hold it in place to provide full"
                                                    " body protection.",
                         value=42000, rarity=0.4, mod=0.3, subtyp='Shield', unequip=False)
        self.weight = 20


class Svalinn(OffHand):

    def __init__(self):
        super().__init__(name="Svalinn", description="The svalinn is a mythical shield that symbolizes protection "
                                                     "and strength, often depicted as an essential element in the "
                                                     "cosmic balance.",
                         value=75000, rarity=0.2, mod=0.35, subtyp='Shield', unequip=False)
        self.weight = 18


class MedusaShield(OffHand):

    def __init__(self):
        super().__init__(name="Medusa Shield", description="A shield that has been polished to resemble a mirror. Said"
                                                           " to be used to defeat the Gorgon Medusa. Reflects back some"
                                                           " magic.",
                         value=150000, rarity=0.05, mod=0.4, subtyp='Shield', unequip=False)
        self.weight = 25


# Natural Shield
class NaturalShield(OffHand):

    def __init__(self, name: str, mod: float, subtyp: str) -> None:
        super().__init__(name=name, mod=mod, subtyp=subtyp, description="", rarity=0, unequip=False, value=0)
        self.name = name
        self.mod = mod
        self.subtyp = subtyp


class ForceField(NaturalShield):

    def __init__(self):
        super().__init__(name="Force Field", mod=0.1, subtyp="Shield")


class ForceField2(ForceField):

    def __init__(self):
        super().__init__()
        self.mod = 0.2


class ForceField3(ForceField):

    def __init__(self):
        super().__init__()
        self.mod = 0.3


# Tomes
class Book(OffHand):

    def __init__(self):
        super().__init__(name="Book", description="A book of notes taken during the character's apprenticeship.",
                         value=25, rarity=0.95, mod=6, subtyp='Tome', unequip=False)
        self.weight = 1


class TomeKnowledge(OffHand):

    def __init__(self):
        super().__init__(name="Tome of Knowledge", description="A tome containing secrets to enhancing spells.",
                         value=500, rarity=0.9, mod=14, subtyp='Tome', unequip=False)
        self.weight = 3


class InfernalGrimoire(OffHand):

    def __init__(self):
        super().__init__(name="Infernal Grimoire", description="A blackened, flame-wreathed book that burns to the "
                                                                "touch but never turns to ash.",
                         value=2500, rarity=0.85, mod=22, subtyp='Tome', unequip=False)
        self.weight = 3


class ElementalPrimer(OffHand):

    def __init__(self):
        super().__init__(name="Elemental Primer", description="A multi-colored tome that shifts between elemental "
                                                              "motifs depending on its surroundings.",
                         value=10000, rarity=0.75, mod=30, subtyp='Tome', unequip=False)
        self.weight = 2


class TreatiseBalance(OffHand):

    def __init__(self):
        super().__init__(name="Treatise of Balance", description="A weathered tome, marked with a taijitu, better "
                                                                 "known as the yin and yang symbol. The pages are "
                                                                 "filled with intricate diagrams illustrating the "
                                                                 "harmony of opposing forces.",
                         value=16000, rarity=0.6, mod=36, subtyp='Tome', unequip=False)
        self.weight = 3


class DragonRouge(OffHand):

    def __init__(self):
        super().__init__(name="Dragon Rouge", description="French for \"Red Dragon\", this mythical tome contains "
                                                          "ancient knowledge passed down through the ages.",
                         value=21000, rarity=0.5, mod=42, subtyp='Tome', unequip=False)
        self.weight = 4


class Vedas(OffHand):

    def __init__(self):
        super().__init__(name="Vedas", description="A large body of religious texts, consisting of some of the oldest "
                                                   "holy teachings.",
                         value=50000, rarity=0.4, mod=54, subtyp='Tome', unequip=False)
        self.weight = 4


class CompendiumAncients(OffHand):

    def __init__(self):
        super().__init__(name="Compendium of the Ancients", description="A colossal tome filled with records of "
                                                                        "forgotten civilizations, written in a "
                                                                        "language lost to time.",
                         value=65000, rarity=0.2, mod=65, subtyp='Tome', unequip=False)
        self.weight = 5


class Necronomicon(OffHand):

    def __init__(self):
        super().__init__(name="Necronomicon", description="The Book of the Dead, a mystical grimoire written by an "
                                                          "unknown author.",
                         value=72000, rarity=0.2, mod=75, subtyp='Tome', unequip=False)
        self.weight = 6
        self.restriction = ['Warlock', 'Necromancer']


class Magus(OffHand):

    def __init__(self):
        super().__init__(name="Magus", description="A book of magical art written by a powerful wizard.",
                         value=90000, rarity=0.05, mod=90, subtyp='Tome', unequip=False)
        self.weight = 3


class CodexEternity(OffHand):
    """
    Rare drop from Merzhin in Realm of Cambion
    """

    def __init__(self):
        super().__init__(name="Codex of Eternity", description="A shimmering tome bound in starlight, with pages that "
                                                               "shift and reform endlessly.",
                         value=150000, rarity=0.01, mod=130, subtyp='Tome', unequip=False)


# Rod items
class WillowDiviningRod(OffHand):

    def __init__(self):
        super().__init__(name="Willow Divining Rod", description="A fresh willow switch wrapped in copper thread. "
                                                                 "It is humble work, but the forked tip answers "
                                                                 "many questions.",
                         value=12000, rarity=0.6, mod=30, subtyp='Rod', unequip=False)
        self.weight = 1


class CopperLeyRod(OffHand):

    def __init__(self):
        super().__init__(name="Copper Ley Rod", description="A straight copper rod etched with ley-line marks. "
                                                            "It steadies minor omens and strengthens early rune work.",
                         value=19000, rarity=0.5, mod=38, subtyp='Rod', unequip=False)
        self.weight = 2


class MoonlitHazelRod(OffHand):

    def __init__(self):
        super().__init__(name="Moonlit Hazel Rod", description="Hazel harvested under a clear moon and capped with "
                                                               "silver. It answers elemental signs with a quieter, "
                                                               "stronger pulse.",
                         value=45000, rarity=0.4, mod=45, subtyp='Rod', unequip=False)
        self.weight = 2


class DowsingRod(OffHand):

    def __init__(self):
        super().__init__(name="Dowsing Rod", description="Also known as a divining rod, this oak Y-shaped branch "
                                                         "is thought to help locate natural sources of water. But "
                                                         "this is no normal dowsing rod, enhanced by the power of "
                                                         "Poseidon. All water-based spells gain double the bonus to "
                                                         "spell damage.",
                         value=75000, rarity=0.2, mod=50, subtyp='Rod', unequip=False)
        self.weight = 2


class ScepterIfrit(OffHand):

    def __init__(self):
        super().__init__(name="Scepter of Ifrit", description="A flaming scepter imbued by the wrath of Ifrit. All "
                                                              "fire-based spells gain double the bonus to spell "
                                                              "damage.",
                         value=75000, rarity=0.2, mod=50, subtyp='Rod', unequip=False)
        self.weight = 3


class GaiasBranch(OffHand):

    def __init__(self):
        super().__init__(name="Gaia's Branch", description="Mother Earth embodies all the living things, including the"
                                                           " tree of life. As a sacrifice to combat those who try to "
                                                           "hurt her, a single branch was removed and infused with the "
                                                           "power of her domain. All earth-based spells gain double "
                                                           "the bonus to spell damage.",
                         value=75000, rarity=0.2, mod=50, subtyp='Rod', unequip=False)
        self.weight = 3


class Zephyruswand(OffHand):

    def __init__(self):
        super().__init__(name="Zephyruswand", description="As the God of the West Wind, Zephyrus lends his power to "
                                                          "user. All wind-based spells gain double the bonus to spell "
                                                          "damage.",
                         value=75000, rarity=0.2, mod=50, subtyp='Rod', unequip=False)
        self.weight = 1


class RainbowRod(OffHand):

    def __init__(self):
        super().__init__(name="Rainbow Rod", description="A radiant rod imbued with the essence of every elemental "
                                                         "power, the Rainbow Rod amplifies the user's spells across"
                                                         " all types, enhancing each with a vibrant, prismatic aura. "
                                                         "All elemental spells gain double the bonus to spell damage.",
                         value=200000, rarity=0.05, mod=80, subtyp='Rod', unequip=False)
        self.weight = 3


class UltimaScepter(OffHand):

    def __init__(self):
        super().__init__(name="Ultima Scepter", description="Crafted to harness the pure, devastating power of the "
                                                            "Ultima spell, this scepter is an artifact of forbidden "
                                                            "magic and unparalleled potency. The Ultima Scepter "
                                                            "channels immense energy directly into the spell, "
                                                            "making it a weapon of unmatched finality in battle, "
                                                            "doubling the bonus to spell damage.",
                         value=250000, rarity=0.01, mod=100, subtyp='Rod', unequip=False)
        self.weight = 5


# Musical instruments
class Lute(OffHand):

    def __init__(self):
        super().__init__(name="Lute", description="",
                         value=5000, rarity=0.75, mod=20, subtyp="Musical Instrument", unequip=False)


class Mbira(OffHand):

    def __init__(self):
        super().__init__(name="Mbira", description="",
                         value=8000, rarity=0.6, mod=25, subtyp="Musical Instrument", unequip=False)


class Lyre(OffHand):

    def __init__(self):
        super().__init__(name="Lyre", description="",
                         value=16000, rarity=0.5, mod=30, subtyp="Musical Instrument", unequip=False)

class Tambourine(OffHand):

    def __init__(self):
        super().__init__(name="Tambourine", description="",
                         value=55000, rarity=0.4, mod=50, subtyp="Musical Instrument", unequip=False)


class Accordina(OffHand):

    def __init__(self):
        super().__init__(name="Accordina", description="",
                         value=70000, rarity=0.3, mod=75, subtyp="Musical Instrument", unequip=False)


class Didgeridoo(OffHand):

    def __init__(self):
        super().__init__(name="Didgeridoo", description="",
                         value=90000, rarity=0.2, mod=100, subtyp="Musical Instrument", unequip=False)


class Sitar(OffHand):

    def __init__(self):
        super().__init__(name="Sitar", description="",
                         value=125000, rarity=0.1, mod=130, subtyp="Musical Instrument", unequip=False)


class Bagpipes(OffHand):

    def __init__(self):
        super().__init__(name="Bagpipes", description="",
                         value=200000, rarity=0.05, mod=150, subtyp="Musical Instrument", unequip=False)


class Shamisen(OffHand):

    def __init__(self):
        super().__init__(name="Shamisen", description="",
                         value=300000, rarity=0.01, mod=200, subtyp="Musical Instrument", unequip=False)


class GrandPiano(OffHand):
    """
    TODO: remove this once implemented
    Not a lootable/equipable item; must be found and played in Cambion Realm to make Ultimate Score
    """

    def __init__(self):
        super().__init__(name="GrandPiano", description="",
                         value=0, rarity=0, mod=0, subtyp="Musical Instrument", unequip=False)


# Rings
class NoRing(Accessory):

    def __init__(self):
        super().__init__(name="No Ring", description="No ring equipped.", value=0, rarity=0, mod="No Mod",
                         subtyp='None', unequip=True)


class IronRing(Accessory):

    def __init__(self):
        super().__init__(name="Iron Ring", description="A ring that improves the wearer's defense.",
                         value=2000, rarity=0.85, mod="+4 Physical Defense", subtyp="Ring", unequip=False)
        self.weight = 0.1


class PowerRing(Accessory):

    def __init__(self):
        super().__init__(name="Power Ring", description="A ring that improves the wearer's attack damage.",
                         value=5000, rarity=0.75, mod="+10 Physical Damage", subtyp="Ring", unequip=False)
        self.weight = 0.1


class BarrierRing(Accessory):
    """
    Increases block chance by 25%, even without a shield
    """

    def __init__(self):
        super().__init__(name="Barrier Ring", description="A ring that increases the wearer's chance to block attacks "
                                                          "by 25%, even without having a shield equipped.",
                         value=16000, rarity=0.5, mod="Block", subtyp="Ring", unequip=False)
        self.weight = 0.1


class SteelRing(Accessory):

    def __init__(self):
        super().__init__(name="Steel Ring", description="A ring that greatly improves the wearer's defense.",
                         value=20000, rarity=0.4, mod="+10 Physical Defense", subtyp="Ring", unequip=False)
        self.weight = 0.1


class MightRing(Accessory):

    def __init__(self):
        super().__init__(name="Might Ring", description="A ring that greatly improves the wearer's attack damage.",
                         value=24000, rarity=0.4, mod="+20 Physical Damage", subtyp="Ring", unequip=False)
        self.weight = 0.1


class AccuracyRing(Accessory):

    def __init__(self):
        super().__init__(name="Accuracy Ring", description="A ring that improves the wearer's weapon accuracy by 10%.",
                         value=25000, rarity=0.4, mod="Accuracy", subtyp="Ring", unequip=False)
        self.weight = 0.1


class EvasionRing(Accessory):
    """
    Increases chance to dodge
    """

    def __init__(self):
        super().__init__(name="Evasion Ring", description="A ring that improves the wearer's chance to dodge.",
                         value=40000, rarity=0.2, mod="Dodge", subtyp="Ring", unequip=False)
        self.weight = 0.1


class TitaniumRing(Accessory):

    def __init__(self):
        super().__init__(name="Titanium Ring", description="A ring that massively improves the wearer's defense.",
                         value=45000, rarity=0.2, mod="+20 Physical Defense", subtyp="Ring", unequip=False)
        self.weight = 0.1


class ForceRing(Accessory):

    def __init__(self):
        super().__init__(name="Force Ring", description="A ring that massively improves the wearer's attack damage.",
                         value=50000, rarity=0.1, mod="+50 Physical Damage", subtyp="Ring", unequip=False)
        self.weight = 0.1


class ClassRing(Accessory):

    def __init__(self):
        super().__init__(name="Class Ring", description="A ring that changes depending on the wearer's specialty.",
                         value=0, rarity=0, mod="Special", subtyp="Ring", unequip=False)
        self.weight = 0.1

    def get_description(self, player_char=None):
        """Get dynamic description based on player's class."""
        if player_char is None:
            return self.description
        
        cls_name = player_char.cls.name
        from .classes import class_rings
        if class_rings.is_legacy_class(cls_name):
            return class_rings.description(player_char)

        descriptions = {
            "Berserker": "A ring that grants +15% Critical Hit Chance when worn by a Berserker.",
            "Weapon Master": self._grandmaster_description(player_char),
            "Grandmaster of Arms": self._grandmaster_description(player_char),
            "Crusader": "A ring that grants +10% Holy damage when worn by a Crusader.",
            "Dragoon": "A ring that unlocks an additional Jump modification slot (max 6) when worn by a Dragoon.",
            "Stalwart Defender": "A ring that reduces damage taken by 10% when worn by a Stalwart Defender.",
            "Wizard": "A ring that increases the chance to trigger Arcane and elemental spell special effects when worn by a Wizard.",
            "Shadowcaster": "A ring that grants Shadow Bolt a special effect that heals the caster based on damage dealt when worn by a Shadowcaster.",
            "Demonologist": self._demonologist_description(player_char),
            "Knight Enchanter": "A ring that increases Mana Tap effectiveness (turns 10% mana into 20% heal) when worn by a Knight Enchanter.",
            "Grand Summoner": "A ring that increases HP and damage of summoned creatures by 30% when worn by a Grand Summoner.",
            "Rogue": "A ring that grants +2 Luck bonus when worn by a Rogue.",
            "Seeker": "A ring that grants a chance to find rare items based on dungeon level when worn by a Seeker.",
            "Ninja": "A ring that grants first round standard attack double damage if you have initiative when worn by a Ninja.",
            "Arcane Trickster": "A ring that grants a buff increasing Magic damage and dodge chance when a spell is stolen, when worn by an Arcane Trickster.",
            "Templar": "A ring that provides random blessings in combat (health/mana regen, attack/defense boost) when worn by a Templar.",
            "Hierophant": "A ring that preserves Devotion after a clean Consecrated Conduit payoff and improves staff-conduit holy damage when worn by a Hierophant.",
            "Master Monk": "A ring that increases damage and armor by 50% when unarmed and not wearing armor when worn by a Master Monk.",
            "Archbishop": "A ring that grants a random chance to heal 25% of health when below 50% health when worn by an Archbishop.",
            "Troubadour": "A ring that doubles the intelligence bonus to all songs when worn by a Troubadour.",
            "Lycan": "A ring that grants an attack bonus immediately after transforming when worn by a Lycan.",
            "Archdruid": self._archdruid_description(player_char),
            "Astromancer": "A ring that strengthens active-sign fate and rune boosts when worn by an Astromancer.",
            "Soulcatcher": "A ring that unlocks the Soul Aspect of the Totem ability when worn by a Soulcatcher, granting +20% Weapon damage and +20% Critical damage.",
            "Beast Master": "A ring that increases defense for you and your companion when covering the other when worn by a Beast Master.",
        }
        return descriptions.get(cls_name, self.description)

    def _grandmaster_description(self, player_char):
        from .classes import grandmaster
        from .classes import class_rings

        state = grandmaster.normalize_state(getattr(player_char, "grandmaster_discipline", None))
        if getattr(getattr(player_char, "cls", None), "name", None) == "Weapon Master":
            ranks = [
                f"{weapon_type} {grandmaster.discipline_rank(player_char, weapon_type)}"
                for weapon_type in grandmaster.WEAPON_TYPES
                if grandmaster.discipline_rank(player_char, weapon_type)
            ]
            progress = ", ".join(ranks) if ranks else "no ranked disciplines yet"
            return (
                f"A dormant Class Ring for a Weapon Master. {class_rings.presentation_summary(player_char, awakened=False)} "
                "Awakened effect: Grandmaster binding is not available until Grandmaster of Arms. "
                f"Current ranks: {progress}."
            )
        if not state["activated"]:
            return (
                f"A dormant Class Ring for a Grandmaster of Arms. {class_rings.presentation_summary(player_char, awakened=False)} "
                "Activation: Secret Master trial. Awakened effect: bind one weapon discipline. "
                f"{class_rings.active_effect_summary(player_char, awakened=False)}"
            )
        bound_weapon = state["bound_weapon"] or "chosen weapon"
        rank = grandmaster.discipline_rank(player_char, bound_weapon)
        chance = int(grandmaster.proc_chance(player_char, bound_weapon) * 100)
        accuracy = int(grandmaster.accuracy_bonus(player_char, bound_weapon) * 100)
        return (
            f"An awakened Class Ring for a Grandmaster of Arms. {class_rings.presentation_summary(player_char, awakened=True)} "
            f"bound to {bound_weapon} Discipline. Bound weapon: {bound_weapon}. "
            "Awakened effect: doubles that discipline's mastery bonus "
            f"while equipped (rank {rank}, +{accuracy}% accuracy, {chance}% technique chance) "
            f"and perfects that weapon's active art. {class_rings.active_effect_summary(player_char, awakened=True)}"
        )

    def _demonologist_description(self, player_char):
        from .classes import demonologist
        from .classes import class_rings

        state = demonologist.normalize_state(getattr(player_char, "demonologist_contracts", None))
        active = state["active_patron"] or "no active patron"
        if not state["ring_awakened"]:
            return (
                f"A dormant Class Ring for a Demonologist. {class_rings.presentation_summary(player_char, awakened=False)} "
                "Activation: hidden crypt familiar imprisonment. Basic contracts are available, "
                f"but empowered contracts are inactive. Active patron: {active}. "
                f"{class_rings.active_effect_summary(player_char, awakened=False)}"
            )
        familiar = state.get("imprisoned_familiar") or {}
        echo = familiar.get("race") or familiar.get("spec") or "familiar"
        return (
            f"An awakened Class Ring for a Demonologist. {class_rings.presentation_summary(player_char, awakened=True)} "
            f"Imprisoned echo: {echo}. Awakened effect: the ring has empowered fiend contracts. "
            f"Active patron: {active}."
        )

    def _archdruid_description(self, player_char):
        from .classes import archdruid
        from .classes import class_rings

        state = archdruid.normalize_state(getattr(player_char, "archdruid_attunement", None))
        attunement = ", ".join(
            f"{affinity} {state['attunement'][affinity]}"
            for affinity in archdruid.AFFINITIES
        )
        if not state["grove_unlocked"]:
            return (
                f"A dormant Class Ring for an Archdruid. {class_rings.presentation_summary(player_char, awakened=False)} "
                "Activation: Fourfold Balance and Ancient Grove rituals. "
                f"Attunement: {attunement}."
            )
        if not state["ring_awakened"]:
            aspects = archdruid.aspect_summary(player_char)
            return (
                f"A dormant Class Ring for an Archdruid. {class_rings.presentation_summary(player_char, awakened=False)} "
                "Activation: complete all four Grove aspects. "
                f"Aspects: {aspects}. {class_rings.active_effect_summary(player_char, awakened=False)}"
            )
        bonus = int(archdruid.harmony_bonus(player_char) * 100)
        total_attunement = sum(int(state["attunement"][affinity]) for affinity in archdruid.AFFINITIES)
        potential = (total_attunement // 25) * 0.01
        if all(int(state["attunement"][affinity]) >= 75 for affinity in archdruid.AFFINITIES):
            potential *= 2
        potential_bonus = int(min(0.40, potential) * 100)
        return (
            f"An awakened Class Ring for an Archdruid. {class_rings.presentation_summary(player_char, awakened=True)} "
            "Awakened through Venom, Stone, Growth, and Storm. "
            f"Current Harmony Bonus: +{bonus}%. Potential while equipped: +{potential_bonus}%. "
            f"{class_rings.active_effect_summary(player_char, awakened=True)}"
        )

    def class_mod(self, player_char):
        """Apply class-specific bonuses to the wearer."""
        cls_name = player_char.cls.name

        from .classes import class_rings
        if class_rings.is_legacy_class(cls_name):
            player_char.equipment["Ring"].mod = class_rings.ring_mod(player_char)
            if cls_name == "Soulcatcher" and class_rings.is_awakened(player_char, "Soulcatcher"):
                try:
                    totem = player_char.spellbook.get("Skills", {}).get("Totem")
                    if totem is None:
                        totem = player_char.spellbook.get("Totem")
                    if totem is not None:
                        totem.unlocked_aspects["Soul"] = True
                except (AttributeError, KeyError):
                    pass
            return
        
        # Warrior Branch
        if cls_name == "Berserker":
            # +15% Critical Hit Chance
            if "Crit" not in player_char.equipment["Ring"].mod:
                player_char.equipment["Ring"].mod = "+15% Crit"

        elif cls_name in {"Weapon Master", "Grandmaster of Arms"}:
            from .classes import grandmaster

            state = grandmaster.normalize_state(getattr(player_char, "grandmaster_discipline", None))
            bound_weapon = state["bound_weapon"]
            if cls_name == "Grandmaster of Arms" and state["activated"] and bound_weapon:
                player_char.equipment["Ring"].mod = f"{bound_weapon} Discipline x2"
            else:
                player_char.equipment["Ring"].mod = "Weapon Discipline"
        
        elif cls_name == "Crusader":
            # +10% Holy damage
            player_char.equipment["Ring"].mod = "+10% Holy Damage"
        
        elif cls_name == "Dragoon":
            # Unlock additional Jump modification slot (max 6)
            player_char.equipment["Ring"].mod = "+1 Jump Mod"
        
        elif cls_name == "Stalwart Defender":
            # Reduce damage taken by 10%
            player_char.equipment["Ring"].mod = "Damage Reduction"
        
        # Mage Branch
        elif cls_name == "Wizard":
            # Increased chance to trigger Arcane and elemental spell special effects
            player_char.equipment["Ring"].mod = "Spell Effect"
        
        elif cls_name == "Shadowcaster":
            # Shadow Bolt gains special effect that heals based on damage
            player_char.equipment["Ring"].mod = "Shadow Bolt Heal"

        elif cls_name == "Demonologist":
            from .classes import demonologist

            state = demonologist.normalize_state(getattr(player_char, "demonologist_contracts", None))
            if state["ring_awakened"]:
                player_char.equipment["Ring"].mod = "Empowered Contracts"
            else:
                player_char.equipment["Ring"].mod = "Dormant Contract"
        
        elif cls_name == "Knight Enchanter":
            # Increase effectiveness of Mana Tap (10% mana → 20% heal)
            player_char.equipment["Ring"].mod = "Mana Tap+"
        
        elif cls_name == "Grand Summoner":
            # Increase HP and damage of summoned creatures by 30%
            player_char.equipment["Ring"].mod = "+30% Summons"
        
        # Footpad Branch
        elif cls_name == "Rogue":
            # +2 luck bonus
            player_char.stats.charisma += 2
            player_char.equipment["Ring"].mod = "+2 Luck"
        
        elif cls_name == "Seeker":
            # Chance to find rare items based on dungeon level
            player_char.equipment["Ring"].mod = "Rare Find"
        
        elif cls_name == "Ninja":
            # First round standard attack deals double damage if player has initiative
            player_char.equipment["Ring"].mod = "First Strike"
        
        elif cls_name == "Arcane Trickster":
            # Gain buff when spell is stolen (Magic damage + dodge)
            player_char.equipment["Ring"].mod = "Spell Steal Buff"
        
        # Healer Branch
        elif cls_name == "Templar":
            # Provides random blessing in combat
            player_char.equipment["Ring"].mod = "Random Blessing"
        
        elif cls_name == "Master Monk":
            # Damage and armor increased by 50% when unarmed and not wearing armor
            player_char.equipment["Ring"].mod = "Martial Master"
        
        elif cls_name == "Archbishop":
            # Random chance to heal 25% of health when below 50% health
            player_char.equipment["Ring"].mod = "Divine Intervention"
        
        elif cls_name == "Troubadour":
            # Double the intelligence bonus to all songs
            player_char.equipment["Ring"].mod = "Amplified Song"
        
        # Pathfinder Branch
        elif cls_name == "Lycan":
            # Gain attack bonus immediately after transforming
            player_char.equipment["Ring"].mod = "Transform Boost"

        elif cls_name == "Archdruid":
            from .classes import archdruid

            state = archdruid.normalize_state(getattr(player_char, "archdruid_attunement", None))
            if state["ring_awakened"]:
                bonus = int(archdruid.harmony_bonus(player_char) * 100)
                player_char.equipment["Ring"].mod = f"Harmony +{bonus}%"
            elif state["grove_unlocked"]:
                player_char.equipment["Ring"].mod = "Grove Dormant"
            else:
                player_char.equipment["Ring"].mod = "Dormant Balance"
        
        elif cls_name == "Astromancer":
            # Boost terrain effect of spells
            player_char.equipment["Ring"].mod = "Terrain Master"
        
        elif cls_name == "Soulcatcher":
            # Unlock Soul Aspect of Totem ability
            try:
                if "Totem" in player_char.spellbook:
                    totem = player_char.spellbook["Totem"]
                    totem.unlocked_aspects["Soul"] = True
                player_char.equipment["Ring"].mod = "Soul Aspect Unlock"
            except (AttributeError, KeyError):
                player_char.equipment["Ring"].mod = "Soul Aspect Unlock"
        
        elif cls_name == "Beast Master":
            # Increased defense for wearer and companion when covering the other
            player_char.equipment["Ring"].mod = "Pack Bond"


class NoPendant(Accessory):

    def __init__(self):
        super().__init__(name="No Pendant", description="No pendant equipped.", value=0, rarity=0, mod="No Mod",
                         subtyp="None", unequip=True)


class VisionPendant(Accessory):

    def __init__(self):
        super().__init__(name="Pendant of Vision", description="A pendant that that gives information about the enemy.",
                         value=1200, rarity=0.9, mod="Vision", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class RubyLocket(Accessory):

    def __init__(self):
        super().__init__(name="Ruby Locket", description="A ruby necklace that improves the wearer's magic defense.",
                         value=1800, rarity=0.85, mod="+10 Magic Defense", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class SilverNecklace(Accessory):

    def __init__(self):
        super().__init__(name="Silver Necklace", description="A silver-chained necklace that improves the wearer's "
                                                             "magic damage.",
                         value=8000, rarity=0.75, mod="+10 Magic Damage", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class AntidotePendant(Accessory):

    def __init__(self):
        super().__init__(name="Antidote Pendant", description="Protects the wearer against the effects of poison.",
                         value=2500, rarity=0.85, mod="Status-Poison", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class CalmingPendant(Accessory):

    def __init__(self):
        super().__init__(name="Calming Pendant", description="Protects the wearer against the effects of berserk.",
                         value=5000, rarity=0.7, mod="Status-Berserk", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class ElementChain(Accessory):

    def __init__(self):
        super().__init__(name="Element Chain", description="Base class for the various element chains, each forged "
                                                           "around a focused elemental core.",
                         value=8000, rarity=0.6, mod="None", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class FireChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Fire Chain"
        self.description = ("A necklace set with a warm ember-stone that glows brighter near open flame.")
        self.mod = "Resist-Fire"


class IceChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Ice Chain"
        self.description = ("A necklace of pale crystal links that stay cold even in midsummer heat.")
        self.mod = "Resist-Ice"

class ElectricChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Electric Chain"
        self.description = ("A necklace strung with storm glass that hums softly before lightning strikes.")
        self.mod = "Resist-Electric"

class WaterChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Water Chain"
        self.description = ("A necklace of blue-green links that beads with dew in dry air.")
        self.mod = "Resist-Water"

class EarthChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Earth Chain"
        self.description = ("A necklace carved from polished stone, heavy with the patience of deep caverns.")
        self.mod = "Resist-Earth"

class WindChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Wind Chain"
        self.description = ("A necklace of feather-light silver links that stir when no breeze is present.")
        self.mod = "Resist-Wind"


class ElementalChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Elemental Chain"
        self.description = ("Fashioned from the cores of elementals, this necklace shifts color as nearby magic "
                            "changes shape.")
        self.value = 15000
        self.rarity = 0.4
        self.mod = "Resist-Elemental"


class SapphireLocket(Accessory):

    def __init__(self):
        super().__init__(name="Sapphire Locket", description="A sapphire necklace that greatly improves the wearer's "
                                                             "magic defense.",
                         value=16000, rarity=0.5, mod="+20 Magic Defense", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class GoldNecklace(Accessory):

    def __init__(self):
        super().__init__(name="Gold Necklace", description="A gold-chained necklace that greatly improves the "
                                                           "wearer's magic damage.",
                         value=22000, rarity=0.4, mod="+20 Magic Damage", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class GorgonPendant(Accessory):

    def __init__(self):
        super().__init__(name="Gorgon Pendant", description="Made from the scale of a Gorgon, this ring protects the "
                                                            "wearer against petrification.",
                         value=20000, rarity=0.4, mod="Status-Stone", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class GarfunkelPendant(Accessory):

    def __init__(self):
        super().__init__(name="Garfunkel Pendant", description="The Sound of Silence can be deafening but not with "
                                                              "this necklace.",
                         value=23000, rarity=0.3, mod="Status-Silence", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class DharmaPendant(Accessory):

    def __init__(self):
        super().__init__(name="Dharma Pendant", description="No need to fear the reaper while wearing this amulet, "
                                                            "giving the wearer immunity against instant death.",
                         value=25000, rarity=0.25, mod="Status-Death", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class DraconitePendant(Accessory):
    """Kaelenon's crafted pendant. Strengthens Jump Recover restoration."""

    def __init__(self):
        super().__init__(
            name="Draconite Pendant",
            description="A pendant cut from Kaelenon's Draconite. It strengthens the Recover Jump modification, "
                        "restoring more health and mana when the wearer lands.",
            value=0,
            rarity=0,
            mod="Jump Recover+",
            subtyp="Pendant",
            unequip=False,
        )
        self.weight = 0.1


class LevitationPendant(Accessory):

    def __init__(self):
        super().__init__(name="Levitation Pendant", description="Gives the wearer the ability to fly, making them "
                                                                 "harder to hit and immune to ground-based spells. "
                                                                 "The downfall is that Wind spells will hurt more.",
                         value=30000, rarity=0.25, mod="Flying", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class ElementAmulet(Accessory):

    def __init__(self):
        super().__init__(name="Element Amulet", description="Base class for the various element amulets, each shaped "
                                                           "around a concentrated warding jewel.",
                         value=40000, rarity=0.2, mod="None", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class FireAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Fire Amulet"
        self.description = ("An amulet with a ruby heart that burns like a banked coal.")
        self.mod = "Immune-Fire"


class IceAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Ice Amulet"
        self.description = ("An amulet with a frost-white gem that leaves a chill on the skin.")
        self.mod = "Immune-Ice"

class ElectricAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Electric Amulet"
        self.description = ("An amulet with a storm-bright gem that clicks with tiny sparks.")
        self.mod = "Immune-Electric"

class WaterAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Water Amulet"
        self.description = ("An amulet with a deep blue gem that seems to ripple beneath its surface.")
        self.mod = "Immune-Water"

class EarthAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Earth Amulet"
        self.description = ("An amulet with a dense green gem veined like ancient bedrock.")
        self.mod = "Immune-Earth"

class WindAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Wind Amulet"
        self.description = ("An amulet with a clear gem that feels almost weightless in the hand.")
        self.mod = "Immune-Wind"


class ElementalAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Elemental Amulet"
        self.description = ("Legend claims the jewel of this amulet is actually the heart of a god, still turning "
                            "with every color of creation.")
        self.value = 100000
        self.rarity = 0.05
        self.mod = "Immune-Elemental"


class InvisibilityPendant(Accessory):

    def __init__(self):
        super().__init__(name="Invisibility Pendant", description="Makes the wearer invisible and harder to hit.",
                         value=50000, rarity=0.1, mod="Invisible", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class DiamondLocket(Accessory):

    def __init__(self):
        super().__init__(name="Diamond Locket", description="A diamond necklace that massively improves the wearer's "
                                                            "magic damage.",
                         value=55000, rarity=0.1, mod="+50 Magic Defense", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class PlatinumNecklace(Accessory):

    def __init__(self):
        super().__init__(name="Platinum Necklace", description="A platinum-chained necklace that massively improves "
                                                               "the wearer's magic damage.",
                         value=60000, rarity=0.1, mod="+50 Magic Damage", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class RibbonPendant(Accessory):
    """
    Provides immunity to the following status effects: "Berserk", "Blind", "Doom", "Poison", "Silence", "Sleep", "Stun"
    """

    def __init__(self):
        super().__init__(name="Ribbon Pendant", description="Forged from a rare mineral, this pendant provides the "
                                                            "wearer with immunity from all negative status effects.",
                         value=150000, rarity=0.01, mod="Status-All", subtyp="Pendant", unequip=False)



class MagicPendant(Accessory):
    """
    Increases chance to dodge spells by 25%.
    """

    def __init__(self):
        super().__init__(name="Magic Pendant", description="An amulet that makes the wearer harder to hit with magic spells.",
                         value=150000, rarity=0.01, mod="Magic Dodge", subtyp="Pendant", unequip=False)
        self.weight = 0.2


# Potions
class HealthPotion(Potion):

    def __init__(self):
        super().__init__(name="Health Potion", description="A potion that restores up to 25% of your health.",
                         value=100, rarity=0.99, subtyp='Health')
        self.percent = 0.25
        self.minimum_heal = 25

    def _base_heal_amount(self, user: Character) -> int:
        return max(int(getattr(self, "minimum_heal", 0) or 0), int(user.health.max * self.percent))

    def use(self, user: Character, target: Character | None = None, tile: Any = None) -> str:
        use_str = ""
        if user.health.current == user.health.max:
            use_str += "You are already at full health.\n"
            return use_str
        user.modify_inventory(self, subtract=True)
        # Dwarf Temperance/Gluttony: combat consumables are stronger, but may cause hangover.
        is_dwarf = getattr(getattr(user, "race", None), "name", None) == "Dwarf"
        if user.state != 'fight':
            # Out of combat: 80-110% of base amount for variance and improved usefulness
            base_heal = self._base_heal_amount(user)
            heal = int(random.uniform(0.8, 1.1) * base_heal)
        else:
            # In combat: 50-100% with luck modifier
            rand_heal = self._base_heal_amount(user)
            heal_cap = max(1, rand_heal)
            heal_floor = min(heal_cap, int(getattr(self, "minimum_heal", 0) or 0))
            heal = random.randint(rand_heal // 2, rand_heal) * max(1, user.check_mod('luck', luck_factor=12))
            heal = max(min(heal, heal_cap), heal_floor)
        if is_dwarf:
            from .constants import (
                DWARF_COMBAT_CONSUMABLE_MULTIPLIER,
                DWARF_HANGOVER_COMBAT_DURATION,
                DWARF_HANGOVER_MAX_STEPS,
                DWARF_HANGOVER_STEPS_PER_USE,
            )
            heal = int(heal * DWARF_COMBAT_CONSUMABLE_MULTIPLIER)
            if user.state == "fight":
                h = user.status_effects.get("Hangover")
                if h is not None:
                    h.active = True
                    h.duration = max(int(h.duration or 0), DWARF_HANGOVER_COMBAT_DURATION)
            else:
                user.dwarf_hangover_steps = min(
                    DWARF_HANGOVER_MAX_STEPS,
                    int(getattr(user, "dwarf_hangover_steps", 0) or 0) + DWARF_HANGOVER_STEPS_PER_USE,
                )
        use_str += f"The potion healed you for {heal} life.\n"
        user.health.current += heal
        if user.health.current >= user.health.max:
            user.health.current = user.health.max
            use_str += "You are at max health.\n"
        return use_str


class GreatHealthPotion(HealthPotion):

    def __init__(self):
        super().__init__()
        self.name = "Great Health Potion"
        self.description = "\n".join(wrap("A potion that restores up to 50% of your health.", 35, break_on_hyphens=False))
        self.value = 600
        self.rarity = 0.7
        self.percent = 0.50
        self.minimum_heal = 60


class SuperHealthPotion(HealthPotion):

    def __init__(self):
        super().__init__()
        self.name = "Super Health Potion"
        self.description = "\n".join(wrap("A potion that restores up to 75% of your health.", 35, break_on_hyphens=False))
        self.value = 3000
        self.rarity = 0.5
        self.percent = 0.75
        self.minimum_heal = 120


class MasterHealthPotion(HealthPotion):

    def __init__(self):
        super().__init__()
        self.name = "Master Health Potion"
        self.description = "\n".join(wrap("A potion that restores up to 100% of your health.", 35, break_on_hyphens=False))
        self.value = 10000
        self.rarity = 0.3
        self.percent = 1.0
        self.minimum_heal = 250


class ManaPotion(Potion):

    def __init__(self):
        super().__init__(name="Mana Potion", description="A potion that restores up to 25% of your mana.",
                         value=250, rarity=0.9, subtyp='Mana')
        self.percent = 0.25

    def use(self, user: Character, target: Character | None = None, tile: Any = None) -> str:
        use_str = ""
        if user.mana.current == user.mana.max:
            use_str += "You are already at full mana.\n"
            return use_str
        user.modify_inventory(self, subtract=True)
        is_dwarf = getattr(getattr(user, "race", None), "name", None) == "Dwarf"
        if user.state != 'fight':
            # Out of combat: 80-110% of base amount for variance and improved usefulness
            base_heal = int(user.mana.max * self.percent)
            heal = int(random.uniform(0.8, 1.1) * base_heal)
        else:
            # In combat: 50-100% with luck modifier
            rand_res = int(user.mana.max * self.percent)
            heal = random.randint(rand_res // 2, rand_res) * max(1, user.check_mod('luck', luck_factor=12))
        if is_dwarf:
            from .constants import (
                DWARF_COMBAT_CONSUMABLE_MULTIPLIER,
                DWARF_HANGOVER_COMBAT_DURATION,
                DWARF_HANGOVER_MAX_STEPS,
                DWARF_HANGOVER_STEPS_PER_USE,
            )
            heal = int(heal * DWARF_COMBAT_CONSUMABLE_MULTIPLIER)
            if user.state == "fight":
                h = user.status_effects.get("Hangover")
                if h is not None:
                    h.active = True
                    h.duration = max(int(h.duration or 0), DWARF_HANGOVER_COMBAT_DURATION)
            else:
                user.dwarf_hangover_steps = min(
                    DWARF_HANGOVER_MAX_STEPS,
                    int(getattr(user, "dwarf_hangover_steps", 0) or 0) + DWARF_HANGOVER_STEPS_PER_USE,
                )
        use_str += f"The potion restored {heal} mana points.\n"
        user.mana.current += heal
        if user.mana.current >= user.mana.max:
            user.mana.current = user.mana.max
            use_str += "You are at full mana.\n"
        return use_str


class GreatManaPotion(ManaPotion):

    def __init__(self):
        super().__init__()
        self.name = "Great Mana Potion"
        self.description = "\n".join(wrap("A potion that restores up to 50% of your mana.", 35, break_on_hyphens=False))
        self.value = 1500
        self.rarity = 0.45
        self.percent = 0.50


class SuperManaPotion(ManaPotion):

    def __init__(self):
        super().__init__()
        self.name = "Super Mana Potion"
        self.description = "\n".join(wrap("A potion that restores up to 75% of your mana.", 35, break_on_hyphens=False))
        self.value = 8000
        self.rarity = 0.3
        self.percent = 0.75


class MasterManaPotion(ManaPotion):

    def __init__(self):
        super().__init__()
        self.name = "Master Mana Potion"
        self.description = "\n".join(wrap("A potion that restores up to 100% of your mana.", 35, break_on_hyphens=False))
        self.value = 35000
        self.rarity = 0.15
        self.percent = 1.0


class Elixir(Potion):

    def __init__(self):
        super().__init__(name="Elixir", description="A potion that restores up to 50% of your health and mana.",
                         value=20000, rarity=0.2, subtyp='Elixir')
        self.percent = 0.5

    def use(self, user: Character, target: Character | None = None, tile: Any = None) -> str:
        use_str = ""
        if user.health.current == user.health.max and user.mana.current == user.mana.max:
            use_str += "You are already at full health and mana.\n"
            return use_str
        user.modify_inventory(self, subtract=True)
        is_dwarf = getattr(getattr(user, "race", None), "name", None) == "Dwarf"
        if user.state != 'fight':
            health_heal = int(user.health.max * self.percent)
            mana_heal = int(user.mana.max * self.percent)
        else:
            rand_heal = int(user.health.max * self.percent)
            rand_res = int(user.mana.max * self.percent)
            health_heal = random.randint(rand_heal // 2, rand_heal) * max(1, user.check_mod('luck', luck_factor=12))
            mana_heal = random.randint(rand_res // 2, rand_res) * max(1, user.check_mod('luck', luck_factor=12))
        if is_dwarf:
            from .constants import (
                DWARF_COMBAT_CONSUMABLE_MULTIPLIER,
                DWARF_HANGOVER_COMBAT_DURATION,
                DWARF_HANGOVER_MAX_STEPS,
                DWARF_HANGOVER_STEPS_PER_USE,
            )
            health_heal = int(health_heal * DWARF_COMBAT_CONSUMABLE_MULTIPLIER)
            mana_heal = int(mana_heal * DWARF_COMBAT_CONSUMABLE_MULTIPLIER)
            if user.state == "fight":
                h = user.status_effects.get("Hangover")
                if h is not None:
                    h.active = True
                    h.duration = max(int(h.duration or 0), DWARF_HANGOVER_COMBAT_DURATION)
            else:
                user.dwarf_hangover_steps = min(
                    DWARF_HANGOVER_MAX_STEPS,
                    int(getattr(user, "dwarf_hangover_steps", 0) or 0) + DWARF_HANGOVER_STEPS_PER_USE,
                )
        use_str += f"The potion restored {health_heal} health points and {mana_heal} mana points.\n"
        user.health.current += health_heal
        user.mana.current += mana_heal
        if user.health.current >= user.health.max:
            user.health.current = user.health.max
            use_str += "You are at max health.\n"
        if user.mana.current >= user.mana.max:
            user.mana.current = user.mana.max
            use_str += "You are at full mana.\n"
        return use_str


class Megalixir(Elixir):

    def __init__(self):
        super().__init__()
        self.name = "Megalixir"
        self.description = "\n".join(wrap("A potion that restores up to 100% of your health and mana.", 35, break_on_hyphens=False))
        self.value = 50000
        self.rarity = 0.05
        self.percent = 1.0


class HPPotion(Potion):

    def __init__(self):
        super().__init__(name="HP Potion", description="A potion that permanently increases your max health by 10.",
                         value=10000, rarity=0.7, subtyp='Stat')
        self.mod = 10

    def use(
        self,
        user: Character,
        target: Character | None = None,
        tile: Any = None,
    ) -> str:
        user.modify_inventory(self, subtract=True)
        user.health.max += self.mod
        if user.in_town():
            user.health.current = user.health.max
        use_str = f"{user.name}'s HP has increased by {self.mod}!\n"
        return use_str


class MPPotion(Potion):

    def __init__(self):
        super().__init__(name="MP Potion", description="A potion that permanently increases your max mana by 10.",
                         value=15000, rarity=0.6, subtyp='Stat')
        self.mod = 10

    def use(
        self,
        user: Character,
        target: Character | None = None,
        tile: Any = None,
    ) -> str:
        user.modify_inventory(self, subtract=True)
        user.mana.max += self.mod
        if user.in_town():
            user.mana.current = user.mana.max
        use_str = f"{user.name}'s MP has increased by {self.mod}!\n"
        return use_str


class StrengthPotion(Potion):

    def __init__(self):
        super().__init__(name="Strength Potion", description="A potion that permanently increases your strength by 1.",
                         value=50000, rarity=0.3, subtyp='Stat')

    def use(
        self,
        user: Character,
        target: Character | None = None,
        tile: Any = None,
    ) -> str:
        user.modify_inventory(self, subtract=True)
        user.stats.strength += 1
        use_str = f"{user.name}'s strength has increased by 1!\n"
        return use_str


class IntelPotion(Potion):

    def __init__(self):
        super().__init__(name="Intelligence Potion", description="A potion that permanently increases your intelligence"
                                                                 " by 1.",
                         value=50000, rarity=0.3, subtyp='Stat')

    def use(
        self,
        user: Character,
        target: Character | None = None,
        tile: Any = None,
    ) -> str:
        user.modify_inventory(self, subtract=True)
        user.stats.intel += 1
        use_str = f"{user.name}'s intelligence has increased by 1!\n"
        return use_str


class WisdomPotion(Potion):

    def __init__(self):
        super().__init__(name="Wisdom Potion", description="A potion that permanently increases your wisdom by 1.",
                         value=50000, rarity=0.3, subtyp='Stat')

    def use(
        self,
        user: Character,
        target: Character | None = None,
        tile: Any = None,
    ) -> str:
        user.modify_inventory(self, subtract=True)
        user.stats.wisdom += 1
        use_str = f"{user.name}'s wisdom has increased by 1!\n"
        return use_str


class ConPotion(Potion):

    def __init__(self):
        super().__init__(name="Constitution Potion", description="A potion that permanently increases your constitution"
                                                                 " by 1.",
                         value=50000, rarity=0.3, subtyp='Stat')

    def use(
        self,
        user: Character,
        target: Character | None = None,
        tile: Any = None,
    ) -> str:
        user.modify_inventory(self, subtract=True)
        user.stats.con += 1
        use_str = f"{user.name}'s constitution has increased by 1!\n"
        return use_str


class CharismaPotion(Potion):

    def __init__(self):
        super().__init__(name="Charisma Potion", description="A potion that permanently increases your charisma by 1.",
                         value=50000, rarity=0.3, subtyp='Stat')

    def use(
        self,
        user: Character,
        target: Character | None = None,
        tile: Any = None,
    ) -> str:
        user.modify_inventory(self, subtract=True)
        user.stats.charisma += 1
        use_str = f"{user.name}'s charisma has increased by 1!\n"
        return use_str


class DexterityPotion(Potion):

    def __init__(self):
        super().__init__(name="Dexterity Potion", description="A potion that permanently increases your dexterity by "
                                                              "1.",
                         value=50000, rarity=0.3, subtyp='Stat')

    def use(
        self,
        user: Character,
        target: Character | None = None,
        tile: Any = None,
    ) -> str:
        user.modify_inventory(self, subtract=True)
        user.stats.dex += 1
        use_str = f"{user.name}'s dexterity has increased by 1!\n"
        return use_str


class AardBeing(Potion):

    def __init__(self):
        super().__init__(name="Aard of Being", description="A potion that permanently increases all stats by 1.",
                         value=250000, rarity=0.01, subtyp='Stat')

    def use(
        self,
        user: Character,
        target: Character | None = None,
        tile: Any = None,
    ) -> str:
        user.modify_inventory(self, subtract=True)
        user.stats.strength += 1
        user.stats.intel += 1
        user.stats.wisdom += 1
        user.stats.con += 1
        user.stats.charisma += 1
        user.stats.dex += 1
        use_str = f"All of {user.name}'s stats have been increased by 1!\n"
        return use_str


class Status(Potion):

    def __init__(self):
        super().__init__(name="Status", description="Base class for status items.",
                         value=0, rarity=0, subtyp="Status")
        self.status = None

    def use(self, user: Character, target: Character | None = None, tile: Any = None) -> str:
        use_str = ""
        if not user.status_effects[self.status].active:
            use_str += f"You are not affected by {self.status.lower()}.\n"
            return use_str
        user.modify_inventory(self, subtract=True)
        if getattr(getattr(user, "race", None), "name", None) == "Dwarf":
            from .constants import (
                DWARF_HANGOVER_COMBAT_DURATION,
                DWARF_HANGOVER_MAX_STEPS,
                DWARF_HANGOVER_STEPS_PER_USE,
            )
            if user.state == "fight":
                h = user.status_effects.get("Hangover")
                if h is not None:
                    h.active = True
                    h.duration = max(int(h.duration or 0), DWARF_HANGOVER_COMBAT_DURATION)
            else:
                user.dwarf_hangover_steps = min(
                    DWARF_HANGOVER_MAX_STEPS,
                    int(getattr(user, "dwarf_hangover_steps", 0) or 0) + DWARF_HANGOVER_STEPS_PER_USE,
                )
        user.status_effects[self.status].active = False
        user.status_effects[self.status].duration = 0
        try:
            user.status_effects[self.status].extra = 0
        except IndexError:
            pass
        use_str += f"You have been cured of {self.status.lower()}.\n"
        if user.health.current < user.health.max:
            heal = int(0.1 * user.health.max)
            heal = random.randint(heal // 2, heal)
            heal = min(heal, user.health.max - user.health.current)
            user.health.current += heal
            use_str += f"You have been healed for {heal} health.\n"
        return use_str


class Antidote(Status):

    def __init__(self):
        super().__init__()
        self.name = "Antidote"
        self.description = "\n".join(wrap("A potion that will cure poison.", 35, break_on_hyphens=False))
        self.value = 250
        self.rarity = 0.9
        self.status = "Poison"


class EyeDrop(Status):

    def __init__(self):
        super().__init__()
        self.name = "Eye Drop"
        self.description = "\n".join(wrap("A potion that will cure blindness.", 35, break_on_hyphens=False))
        self.value = 250
        self.rarity = 0.9
        self.status = "Blind"


class EchoScreen(Status):

    def __init__(self):
        super().__init__()
        self.name = "Echo Screen"
        self.description = "\n".join(wrap("A potion that will cure silence.", 35, break_on_hyphens=False))
        self.value = 1000
        self.rarity = 0.8
        self.status = "Silence"


class Bandage(Status):

    def __init__(self):
        super().__init__()
        self.name = "Bandage"
        self.description = "\n".join(wrap("A linen bandage that will stop bleeding.", 35, break_on_hyphens=False))
        self.value = 1000
        self.rarity = 0.8
        self.status = "Bleed"

    def use(
        self,
        user: Character,
        target: Character | None = None,
        tile: Any = None,
    ) -> str:
        use_str = ""
        if not user.physical_effects[self.status].active:
            use_str += f"You are not affected by {self.status.lower()}.\n"
            return use_str
        user.modify_inventory(self, subtract=True)
        user.physical_effects[self.status].active = False
        user.physical_effects[self.status].duration = 0
        user.physical_effects[self.status].extra = 0
        use_str += f"You have been cured of {self.status.lower()}.\n"
        if user.health.current < user.health.max:
            heal = int(0.1 * user.health.max)
            heal = random.randint(heal // 2, heal)
            heal = min(heal, user.health.max - user.health.current)
            user.health.current += heal
            use_str += f"You have been healed for {heal} health.\n"
        return use_str

class PhoenixDown(Status):

    def __init__(self):
        super().__init__()
        self.name = "Phoenix Down"
        self.description = "\n".join(wrap("A potion that will cure doom status.", 35, break_on_hyphens=False))
        self.value = 2000
        self.rarity = 0.7
        self.status = "Doom"


class Remedy(Status):
    # Silence, Doom, Blind, Poison

    def __init__(self):
        super().__init__()
        self.name = "Remedy"
        self.description = "\n".join(wrap("A potion that will cure all negative status effects.", 35, break_on_hyphens=False))
        self.value = 5000
        self.rarity = 0.2
        self.status = ["Poison", "Blind", "Silence", "Doom"]

    def use(
        self,
        user: Character,
        target: Character | None = None,
        tile: Any = None,
    ) -> str:
        use_str = ""
        if not any([user.status_effects[x].active for x in self.status]):
            use_str += f"You are not affected by any negative status effects.\n"
            return use_str
        user.modify_inventory(self, subtract=True)
        for status in self.status:
            user.status_effects[status].active = False
            user.status_effects[status].duration = 0
            try:
                user.status_effects[status].extra = 0
            except IndexError:
                pass
            use_str += f"You have been cured of {status.lower()}.\n"
        if user.health.current < user.health.max:
            heal = int(0.1 * user.health.max)
            heal = random.randint(heal // 2, heal)
            heal = min(heal, user.health.max - user.health.current)
            user.health.current += heal
            use_str += f"You have been healed for {heal} health.\n"
        return use_str


class Key(Misc):
    """
    Opens locked chests
    """

    def __init__(self):
        super().__init__(name="Key", description="Unlocks a locked chest but is consumed.", value=500, rarity=0.9,
                         subtyp='Key')


class OldKey(Misc):
    """
    Opens locked doors
    """

    def __init__(self):
        super().__init__(name="Old Key", description="Unlocks doors that may lead to either valuable treasure or to "
                                                     "powerful enemies.",
                         value=50000, rarity=0.5, subtyp='Key')


class MasterKey(Misc):
    """
    Special item; Opens locked chest and doors; is not consumed upon use
    """

    def __init__(self):
        super().__init__(name="Master Key", description="Unlocks doors that may lead to either valuable treasure or to "
                                                     "powerful enemies.",
                         value=0, rarity=0, subtyp='Key')


class CrypticKey(Misc):
    """
    A mysterious key of unknown purpose; appears to be crafted with care and precision
    """

    def __init__(self):
        super().__init__(name="Cryptic Key", 
                         description="A pristine key forged by Griswold. Its purpose is shrouded in mystery, "
                                     "but it feels important.",
                         value=0, rarity=0, subtyp='Key')


class LockpickKit(Misc):
    """
    Reusable tools required for Lockpick and Master Lockpick skills.
    """

    def __init__(self, charges: int = 3):
        self.charges = max(1, int(charges))
        super().__init__(
            name="Lockpick Kit",
            description=(
                "A compact set of picks, tension wrenches, and shims required to use "
                f"lockpicking skills. Durability: {self.charges}."
            ),
            value=1500,
            rarity=0.55,
            subtyp="Tool",
        )


class SmokeBomb(Misc):
    """
    One-use tool required for Smoke Screen.
    """

    def __init__(self):
        super().__init__(
            name="Smoke Bomb",
            description="A packed clay pellet that bursts into concealing smoke. Required and consumed by Smoke Screen.",
            value=750,
            rarity=0.65,
            subtyp="Tool",
        )


class Oculus(Misc):
    """
    Expensive magic lens that reveals fake walls.
    """

    def __init__(self):
        super().__init__(
            name="Oculus",
            description="An expensive arcane lens that reveals the telltale shimmer of fake walls.",
            value=35000,
            rarity=0.25,
            subtyp="Magic Tool",
        )


def _inventory_stack(character, item_name: str):
    inventory = getattr(character, "inventory", {}) or {}
    stack = inventory.get(item_name, [])
    return stack if isinstance(stack, list) else []


def has_lockpick_kit(character) -> bool:
    """Return whether a character carries the reusable lockpicking tools."""
    return bool(_inventory_stack(character, "Lockpick Kit"))


def has_smoke_bomb(character) -> bool:
    """Return whether a character carries a Smoke Bomb."""
    return bool(_inventory_stack(character, "Smoke Bomb"))


def has_oculus(character) -> bool:
    """Return whether a character carries an Oculus."""
    return bool(_inventory_stack(character, "Oculus"))


def can_detect_fake_walls(character) -> bool:
    """Return whether passive dungeon perception reveals nearby fake walls."""
    skills = getattr(character, "spellbook", {}).get("Skills", {})
    return "Keen Eye" in skills or has_oculus(character)


def lockpick_break_chance(character, *, master: bool = False) -> float:
    """Chance that a Lockpick Kit breaks after a successful lockpick use."""
    stats = getattr(character, "stats", None)
    dex = getattr(stats, "dex", getattr(stats, "dexterity", 10))
    try:
        dex_score = int(dex)
    except (TypeError, ValueError):
        dex_score = 10
    base = 0.18 if master else 0.35
    floor = 0.04 if master else 0.08
    chance = base - max(0, dex_score - 10) * 0.01
    return max(floor, min(base, chance))


def use_lockpick_kit(character, *, master: bool = False, roll: float | None = None) -> tuple[bool, str]:
    """Spend durability on a Lockpick Kit and possibly break it."""
    stack = _inventory_stack(character, "Lockpick Kit")
    if not stack:
        return False, "You need a Lockpick Kit."

    kit = stack[0]
    charges = int(getattr(kit, "charges", 3) or 3)
    kit.charges = max(0, charges - 1)
    if hasattr(kit, "description"):
        kit.description = (
            "A compact set of picks, tension wrenches, and shims required to use "
            f"lockpicking skills. Durability: {kit.charges}."
        )

    chance = lockpick_break_chance(character, master=master)
    break_roll = random.random() if roll is None else float(roll)
    if kit.charges <= 0 or break_roll < chance:
        character.modify_inventory(kit, subtract=True)
        return True, "The Lockpick Kit breaks."
    return True, f"The Lockpick Kit holds together. Durability: {kit.charges}."


def consume_smoke_bomb(character) -> tuple[bool, str]:
    """Consume one Smoke Bomb for Smoke Screen."""
    stack = _inventory_stack(character, "Smoke Bomb")
    if not stack:
        return False, "Smoke Screen requires a Smoke Bomb.\n"
    character.modify_inventory(stack[0], subtract=True)
    return True, "A Smoke Bomb bursts open.\n"


class JesterToken(Misc):
    """
    A shimmering token from the funhouse; collect all four to unlock the Jester's chamber
    """

    def __init__(self):
        super().__init__(name="Jester Token", 
                         description="A carnival token that shimmers with magical energy. These are required to breach "
                                     "the Jester's inner sanctum.",
                         value=0, rarity=0, subtyp='Quest')


class Scroll(Misc):
    """
    Scrolls allow for a one-time use of a spell; scrolls can only be used in combat
    """

    def __init__(self):
        super().__init__(name="Scroll", description="Base class for scrolls.", value=0, rarity=0, subtyp='Scroll')
        self.spell = None
        self.charges = random.randint(2, 10)

    def use(self, user: Character, target: Character | None = None, tile: Any = None) -> str:
        use_str = f"{user.name} uses {self.name}.\n"
        use_str += str(self.spell.cast(user, target=target, special=True))
        self.charges -= 1
        if not self.charges:
            use_str += "The scroll crumbles to dust in your hands!\n"
            user.modify_inventory(self, subtract=True)
        return use_str


class BlessScroll(Scroll):
    """
    Bless
    """

    def __init__(self):
        super().__init__()
        self.name = "Bless Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast Bless, which"
                                          " increases attack damage for several turns. The scroll will be consumed "
                                          "when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 1000
        self.rarity = 0.9
        self.spell = abilities.Bless()


class SleepScroll(Scroll):
    """
    Sleep
    """

    def __init__(self):
        super().__init__()
        self.name = "Sleep Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast Sleep. The "
                                          "scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 2000
        self.rarity = 0.85
        self.spell = abilities.Sleep()


class FireScroll(Scroll):
    """
    Firebolt
    """

    def __init__(self):
        super().__init__()
        self.name = "Fire Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the fire "
                                          "spell Firebolt. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 3000
        self.rarity = 0.75
        self.spell = abilities.Firebolt()


class IceScroll(Scroll):
    """
    Ice Lance
    """

    def __init__(self):
        super().__init__()
        self.name = "Ice Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the ice "
                                          "spell Ice Lance. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 3000
        self.rarity = 0.75
        self.spell = abilities.IceLance()


class ElectricScroll(Scroll):
    """
    Shock
    """

    def __init__(self):
        super().__init__()
        self.name = "Electric Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the electric"
                                          " spell Shock. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 3000
        self.rarity = 0.75
        self.spell = abilities.Shock()


class WaterScroll(Scroll):
    """
    Water Jet
    """

    def __init__(self):
        super().__init__()
        self.name = "Water Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the water "
                                          "spell Water Jet. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 3000
        self.rarity = 0.75
        self.spell = abilities.WaterJet()


class EarthScroll(Scroll):
    """
    Tremor
    """

    def __init__(self):
        super().__init__()
        self.name = "Earth Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the earth "
                                          "spell Tremor. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 3000
        self.rarity = 0.75
        self.spell = abilities.Tremor()


class WindScroll(Scroll):
    """
    Gust
    """

    def __init__(self):
        super().__init__()
        self.name = "Wind Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the wind "
                                          "spell Gust. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 3000
        self.rarity = 0.75
        self.spell = abilities.Gust()


class ShadowScroll(Scroll):
    """
    Shadow Bolt
    """

    def __init__(self):
        super().__init__()
        self.name = "Shadow Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the "
                                          "shadow spell Shadow Bolt. The scroll will be consumed when it is out of "
                                          "charges.", 35, break_on_hyphens=False))
        self.value = 4000
        self.rarity = 0.7
        self.spell = abilities.ShadowBolt()


class HolyScroll(Scroll):
    """
    Holy
    """

    def __init__(self):
        super().__init__()
        self.name = "Holy Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the holy "
                                          "spell Holy. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 4000
        self.rarity = 0.7
        self.spell = abilities.Holy()


class CleanseScroll(Scroll):
    """
    Cleanse
    """

    def __init__(self):
        super().__init__()
        self.name = "Cleanse Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the holy"
                                          " spell Cleanse. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 4000
        self.rarity = 0.7
        self.spell = abilities.Cleanse()


class BoostScroll(Scroll):
    """
    Boost
    """

    def __init__(self):
        super().__init__()
        self.name = "Boost Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the heal "
                                          "spell Boost. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 8000
        self.rarity = 0.6
        self.spell = abilities.Boost()


class ShellScroll(Scroll):
    """
    Shell
    """

    def __init__(self):
        super().__init__()
        self.name = "Shell Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the heal "
                                          "spell Shell. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 8000
        self.rarity = 0.6
        self.spell = abilities.Shell()


class SilenceScroll(Scroll):
    """
    Silence
    """

    def __init__(self):
        super().__init__()
        self.name = "Silence Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast Silence, "
                                          "which can prevent an target from casting spell for a time. The scroll will"
                                          " be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 8000
        self.rarity = 0.6
        self.spell = abilities.Silence()


class DispelScroll(Scroll):
    """
    Dispel
    """

    def __init__(self):
        super().__init__()
        self.name = "Dispel Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast Dispel, "
                                          "which can remove all positive status effects from the target. The scroll"
                                          " will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 10000
        self.rarity = 0.5
        self.spell = abilities.Dispel()


class DeathScroll(Scroll):
    """
    Desoul
    """

    def __init__(self):
        super().__init__()
        self.name = "Death Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast Desoul, "
                                          "which can kill the target. The scroll will be consumed when it is out "
                                          "of charges.", 35, break_on_hyphens=False))
        self.value = 15000
        self.rarity = 0.4
        self.spell = abilities.Desoul()


class SanctuaryScroll(Scroll):
    """
    Sanctuary
    """

    def __init__(self):
        super().__init__()
        self.name = "Sanctuary Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast Sanctuary,"
                                          " which can return the user to town. The scroll will be consumed when it is"
                                          " out of charges.", 35, break_on_hyphens=False))
        self.value = 50000
        self.rarity = 0.25
        self.spell = abilities.Sanctuary()

    def use(
        self,
        user: Character,
        target: Character | None = None,
        tile: Any = None,
    ) -> str:
        use_str = f"{user.name} uses {self.name}.\n"
        use_str += self.spell.cast_out(user=user)
        self.charges -= 1
        if not self.charges:
            use_str += "The scroll crumbles to dust in your hands!\n"
            user.modify_inventory(self, subtract=True)
        return use_str


class UltimaScroll(Scroll):
    """
    Ultima
    """

    def __init__(self):
        super().__init__()
        self.name = "Ultima Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the powerful"
                                          " Ultima. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 100000
        self.rarity = 0.01
        self.spell = abilities.Ultima()


# Reagents
class SheetMusic(Misc):
    """
    Base sheet music item; sheet music is not purchasable, only created
    """

    def __init__(self, name: str, description: str, value: int, rarity: float, subtyp: str) -> None:
        super().__init__(name, description, value, rarity, subtyp)
        self.song_name = name.replace("Sheet Music: ", "")

    def use(
        self,
        user: Character,
        target: Character | None = None,
        tile: Any = None,
    ) -> str:
        from .classes import bard

        success, message = bard.start_song(user, self.song_name, target=target)
        if success:
            user.modify_inventory(self, subtract=True)
            message += f"The sheet music for {self.song_name} is spent.\n"
        return message


class BattleHymnSheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Battle Hymn", "A martial hymn for battle.", 2500, 0, "Scroll")


class RampartsOdeSheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Ode to the Ramparts", "A protective ode.", 2500, 0, "Scroll")


class DysfunctionSymphonySheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Symphony of Disfunction", "A discordant enemy-breaking score.", 2500, 0, "Scroll")


class LowDefenseRhapsodySheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Low-defense-ian Rhapsody", "A tune that lowers defenses.", 2500, 0, "Scroll")


class SlowRideSheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Slow Ride", "A dragging song.", 2500, 0, "Scroll")


class BonesThugsHarmonySheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Bones, Thugs, and Harmony", "A graveyard harmony.", 2500, 0, "Scroll")


class ScoresAndScoresScoreSheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Scores and Scores Score", "A score about scoring.", 2500, 0, "Scroll")


class GoldTriggerSheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Gold Trigger", "A glittering trigger phrase.", 2500, 0, "Scroll")


class ChorusTimeSheet(SheetMusic):
    def __init__(self):
        super().__init__("Sheet Music: Chorus Time", "A looping chorus.", 2500, 0, "Scroll")


class BlankScroll(Misc):
    """
    Blank scroll used by Spell Stealer/Arcane Trickster to store spells.
    """

    def __init__(
        self,
        name: str = "Blank Scroll",
        description: str | None = None,
        value: int = 2500,
        rarity: float = 0.45,
        subtyp: str = "Scroll",
    ) -> None:
        super().__init__(
            name=name,
            description=description or "\n".join(wrap(
                    "A prepared scroll with enough receptive ink to hold one stolen spell.",
                    35,
                    break_on_hyphens=False,
                )),
            value=value,
            rarity=rarity,
            subtyp=subtyp,
        )


class InscribedSpellScroll(Scroll):
    """
    A stolen-spell scroll that preserves the original spell identity.
    """

    def __init__(self, spell_class_name: str = "MagicMissile", charges: int | None = None) -> None:
        super().__init__()
        self.spell_class_name = spell_class_name
        spell_cls = getattr(abilities, spell_class_name, abilities.MagicMissile)
        self.spell = spell_cls()
        self.name = f"Stolen {self.spell.name} Scroll"
        if charges is not None:
            self.charges = max(1, int(charges))
        self._refresh_description()
        self.value = max(3000, int(getattr(self.spell, "cost", 0) or 0) * 1000)
        self.rarity = 0.2

    def _refresh_description(self) -> None:
        self.description = (
            f"Scroll inscribed with a stolen copy of {self.spell.name}. "
            f"Charges: {self.charges}. The scroll crumbles when its charges run out."
        )

    def use(self, user: Character, target: Character | None = None, tile: Any = None) -> str:
        use_str = super().use(user, target=target, tile=tile)
        if self.charges > 0:
            self._refresh_description()
        return use_str


# Enemy quest items
class RatTail(Misc):

    def __init__(self):
        super().__init__(name="Rat Tail", description="The tail of a rat.",
                         value=0, rarity=1, subtyp="Quest")


class MysteryMeat(Misc):

    def __init__(self):
        super().__init__(name="Mystery Meat", description="Unknown meat with a strange smell. Maybe you could do "
                                                          "something with this.",
                         value=0, rarity=0.5, subtyp="Quest")


class TicketPiece(Misc):

    def __init__(self):
        super().__init__(name="Ticket Piece", description="A scrap of a lottery ticket with a few numbers on it.",
                         value=0, rarity=0, subtyp="Quest")


class DeadSoldier(Misc):

    def __init__(self):
        super().__init__(name="Dead Soldier", description="The partially eaten body of a very green soldier. He never "
                                                          "stood a chance...",
                         value=0, rarity=0, subtyp="Quest")
        self.weight = 100


class Leather(Misc):

    def __init__(self):
        super().__init__(name="Leather", description="The dried skin of an animal, used for various purposes.",
                         value=0, rarity=0.5, subtyp="Quest")


class Feather(Misc):

    def __init__(self):
        super().__init__(name="Feather", description="The feather of a bird.",
                         value=0, rarity=0.5, subtyp="Quest")


class SnakeSkin(Misc):

    def __init__(self):
        super().__init__(name="Snake Skin", description="The skin of a snake.",
                         value=0, rarity=1, subtyp="Quest")


class ScrapMetal(Misc):

    def __init__(self):
        super().__init__(name="Scrap Metal", description="A chunk of metal.",
                         value=0, rarity=0.5, subtyp="Quest")


class CursedHops(Misc):

    def __init__(self):
        super().__init__(name="Cursed Hops", description="Hops from a cursed tree, these flower are used primarily in"
                                                         " the creation of beer and other beverages, as well as herbal "
                                                         "medicines.",
                         value=0, rarity=1, subtyp="Quest")


class BirdFat(Misc):

    def __init__(self):
        super().__init__(name="Bird Fat", description="The fat from a bird, used as a fuel for lamps.",
                         value=0, rarity=0.1, subtyp="Quest")


class ElementalMote(Misc):

    def __init__(self):
        super().__init__(name="Elemental Mote", description="The elemental core of a Myrmidon.",
                         value=0, rarity=1, subtyp="Quest")


class Acorn(Misc):

    def __init__(self):
        super().__init__(name="Acorn", description="A hardy oak seed prized by druids for growth rites.",
                         value=25, rarity=0.5, subtyp="Reagent")


class VineSeed(Misc):

    def __init__(self):
        super().__init__(name="Vine Seed", description="A coiled seed that hums with grasping green life.",
                         value=25, rarity=0.5, subtyp="Reagent")


class FungusSpore(Misc):

    def __init__(self):
        super().__init__(name="Fungus Spore", description="A powdery spore bundle useful in poison and decay rites.",
                         value=25, rarity=0.5, subtyp="Reagent")


class HemlockRoot(Misc):

    def __init__(self):
        super().__init__(name="Hemlock Root", description="A bitter root gathered for dangerous druidic mixtures.",
                         value=25, rarity=0.5, subtyp="Reagent")


class PowerCore(Misc):

    def __init__(self):
        super().__init__(name="Power Core", description="The power source of a Golem.",
                         value=0, rarity=1, subtyp="Quest")


class Phylactery(Misc):

    def __init__(self):
        super().__init__(name="Phylactery", description="The soul artifcat of a Lich, given up willingly to achieve "
                                                        "immortality.",
                         value=0, rarity=0.05, subtyp="Quest")


# Special quest items
class LuckyLocket(Misc):
    """
    Momento given to the warrior Joffrey by the waitress, his betrothed
    """

    def __init__(self):
        super().__init__(name="Lucky Locket", description="A simple gold necklace with a locket containing the picture "
                                                          "of a fair lass.",
                         value=0, rarity=0, subtyp="Special")


class BrassKey(Misc):
    """
    Special key believed to be for opening the tavern but actually opens Joffrey's locker in barracks
    """

    def __init__(self):
        super().__init__(name="Brass Key", description="A brass key, similar to the key for your storage locker in the"
                                                       " barracks.",
                         value=0, rarity=0, subtyp="Special")


class ThievesGuildSignet(Misc):
    """
    Proof recovered from the Thieves Guild initiation trial.
    """

    def __init__(self):
        super().__init__(
            name="Thieves Guild Signet",
            description="A blackened silver signet taken from the guild's hidden initiation trial.",
            value=0,
            rarity=1,
            subtyp="Special",
        )


class JoffreysLetter(Misc):
    """
    A letter written from Joffrey to the waitress; maybe there is some use of this
    """

    def __init__(self):
        super().__init__(name="Joffrey's Letter", description="A letter written from Joffrey to the waitress; maybe "
                                                              "there is some use of this.",
                         value=0, rarity=0, subtyp="Special")


class EmptyVial(Misc):
    """
    Given by Alchemist; used to collect Spring Water from Underground Spring
    """

    def __init__(self):
        super().__init__(name="Empty Vial", description="An empty vial, perfect for storing liquids and other "
                                                        "tinctures.",
                         value=0, rarity=0, subtyp='Special')


class SpringWater(Misc):
    """
    Obtained when you visit the Underground Spring during quest Naivete from Alchemist
    """

    def __init__(self):
        super().__init__(name="Spring Water", description="A vial of the finest spring water.",
                         value=0, rarity=0, subtyp='Special')


class Unobtainium(Misc):
    """
    Magical ore that can be used to forge ultimate weapons at the blacksmith; only one in the game
    """

    def __init__(self):
        super().__init__(name="Unobtainium", description="The legendary ore that has only been theorized. Can be used "
                                                         "to create ultimate weapons.",
                         value=0, rarity=0, subtyp='Special')


class Relic1(Misc):
    """
    The first of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="Triangulus", description="The holy trinity of mind, body, and spirit are represented by "
                                                        "the Triangulus relic.",
                         value=0, rarity=0, subtyp='Special')


class Relic2(Misc):
    """
    The second of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="Quadrata", description="The Quadrata relic symbolizes order, trust, stability, and "
                                                      "logic, the hallmarks of a well-balanced person.",
                         value=0, rarity=0, subtyp='Special')


class Relic3(Misc):
    """
    The third of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="Hexagonum", description="The Hexagonum relic represents the natural world, since the "
                                                       "hexagon is the considered the strongest shape and regularly "
                                                       "found in nature.",
                         value=0, rarity=0, subtyp='Special')


class Relic4(Misc):
    """
    The fourth of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="Luna", description="The Moon, our celestial partner, is the inspiration for the Luna "
                                                  "relic and represents love for others.",
                         value=0, rarity=0, subtyp='Special')


class Relic5(Misc):
    """
    The fifth of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="Polaris", description="The Polaris relic resembles the shape of a star and represents "
                                                     "the guiding light of the North Star.",
                         value=0, rarity=0, subtyp='Special')


class Relic6(Misc):
    """
    The sixth and final of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="Infinitas", description="Shaped like a circle, the Infinitas relic represents the never-"
                                                       "ending struggle between good and evil.",
                         value=0, rarity=0, subtyp='Special')


class Excaliper(Misc):
    """
    item used to summon Maid of the Spring Nimue at the UndergroundSpring at 3:E10
    """

    def __init__(self):
        super().__init__(name="Excaliper", description="The broken fragments of a failed experiment. It appears "
                                                       "someone tried to forge the legendary sword Excalibur using "
                                                       "a caliper tool. It did not go well...",
                        value=0, rarity=0, subtyp="Special")


class ChaliceMap(Misc):
    """
    A worn map tied to the Golden Chalice questline.
    """

    def __init__(self):
        super().__init__(
            name="Chalice Map",
            description="A weathered map whose ink appears almost completely faded.",
            value=0,
            rarity=0,
            subtyp="Special",
        )


class GoldenChalice(Misc):
    """
    Quest item to complete "The Holy Grail of Quests"; requires visiting several locations in town and in the dungeon to uncover the hidden location

    Places to visit with quest active to get location:
    - talk with Hooded Figure at tavern in town; tells player to locate map last seen with adventurer carrying an ugly sword
    - revisit boulder where Excaliper was found; find map hidden in crevice
    - visit Sergeant at barracks with map in inventory; Sergeant tells player to find the adventurer
    - find adventurer at secret location at 3:12,14; adventurer gives player the location of the Golden Chalice
    - visit location at 6:2,17 to find Golden Chalice and complete quest
    """

    def __init__(self):
        super().__init__(name="Golden Chalice", description="A golden chalice that once held the Holy Grail. It is said "
                                                          "that the chalice can grant immense power to those who drink "
                                                          "from it, but it is also cursed with a terrible thirst.",
                         value=0, rarity=0, subtyp="Special")


class SerpentVenomHeart(Misc):
    """Archdruid Venom ritual catalyst."""

    def __init__(self):
        super().__init__(
            name="Serpent Venom Heart",
            description="A pulsing knot of venom that refuses to die.",
            value=0,
            rarity=0,
            subtyp="Special",
        )


class HeartstoneShard(Misc):
    """Archdruid Stone ritual catalyst."""

    def __init__(self):
        super().__init__(
            name="Heartstone Shard",
            description="A mineral fragment that beats once when held still.",
            value=0,
            rarity=0,
            subtyp="Special",
        )


class VerdantSeed(Misc):
    """Archdruid Growth ritual catalyst."""

    def __init__(self):
        super().__init__(
            name="Verdant Seed",
            description="A sleeping seed warm with impossible spring.",
            value=0,
            rarity=0,
            subtyp="Special",
        )


class StormglassFeather(Misc):
    """Archdruid Storm ritual catalyst."""

    def __init__(self):
        super().__init__(
            name="Stormglass Feather",
            description="A translucent feather with lightning trapped along its spine.",
            value=0,
            rarity=0,
            subtyp="Special",
        )


# Ability-related items
class Joker(Misc):
    """
    Dropped by Jester; used to obtain the trickster summon Kobalos
    """

    def __init__(self):
        super().__init__(name="Joker", description="They say that Joker's are wild; you'll see how wild this one is.",
                         value=0, rarity=1, subtyp="Special")
        self.restricted_classes = ["Summoner", "Grand Summoner", "Spell Stealer", "Arcane Trickster"]


class ChiryuKoma(Misc):
    """
    Needed to unlock Dilong summon; visit 1:I17 with item in inventory
    """

    def __init__(self):
        super().__init__(name="Chiryu Koma", description="A game piece used for shogi, depicting an earth dragon.",
                         value=0, rarity=0.1, subtyp="Summon - Dilong")
        self.restricted_classes = ["Summoner", "Grand Summoner"]


class BlacksmithsHammer(Misc):
    """
    Needed to unlock Cacus summon; gained after obtaining first 2 relics and visiting Griswold; visit 2:F13 with item 
      in inventory
    """

    def __init__(self):
        super().__init__(name="Blacksmith's Hammer", description="It looks like a normal blacksmithing hammer but "
                                                                 "something seems...special about this one.",
                         value=0, rarity=0, subtyp="Summon - Cacus")
        self.restricted_classes = ["Summoner", "Grand Summoner"]


class DragonTear(Misc):
    """
    Super rare drop from Dragon-type enemies. Unlocks the Recover modification for the Jump ability.
    Only available to Lancer and Dragoon classes.
    """

    def __init__(self):
        super().__init__(name="Dragon's Tear", 
                         description="A crystallized tear shed by a dragon. Said to contain the essence "
                                   "of draconic vitality and regeneration. Extremely rare.",
                         value=0, rarity=0.01, subtyp="Ability")
        self.restricted_classes = ["Lancer", "Dragoon"]


class KaelenonPortalKey(Misc):
    """Quest item used to return Kaelenon home."""

    def __init__(self):
        super().__init__(
            name="Kaelenon's Portal Key",
            description="A glass-dark key printed from the Realm of Cambion terminal for Kaelenon's return home.",
            value=0,
            rarity=0,
            subtyp="Special",
        )


class Draconite(Misc):
    """Quest material left by Kaelenon after returning home."""

    def __init__(self):
        super().__init__(
            name="Draconite",
            description="A red-black shard from Kaelenon's home realm, warm with restored draconic power.",
            value=0,
            rarity=0,
            subtyp="Special",
        )


# items_dict used by shops
items_dict = {
    'Weapon': {
        "1-Handed": {
            'Dagger': [Dirk, Baselard, Kris, Rondel, Kukri, Khanjar], 
            'Sword': [Rapier, Jian, Talwar, Shamshir, Khopesh, Falchion],
            'Club': [Mace, WarHammer, Pernach, Morgenstern, Shishpar],
            'Fist': [BrassKnuckles, Cestus, BattleGauntlet, BaghNahk, IndrasFist],
            'Ninja Blade': [Tanto, Wakizashi]},
        "2-Handed": {
            'Longsword': [Bastard, Claymore, Zweihander, Changdao, Flamberge, Katana],
            'Battle Axe': [Mattock, Broadaxe, DoubleAxe, Parashu, Greataxe, Tabarzin],
            'Polearm': [Framea, Partisan, Halberd, Naginata, Trident, Ranseur],
            'Staff': [Quarterstaff, Baston, IronshodStaff, SerpentStaff, HolyStaff,
                    RuneStaff, MithrilshodStaff, Khatvanga],
            'Hammer': [Sledgehammer, SpikeMaul, EarthHammer, GreatMaul, Streithammer]}},
    'OffHand': {
        'Shield': [Buckler, Aspis, Targe, Glagwa, KiteShield, Pavise, Svalinn], 
        'Tome': [Book, TomeKnowledge, InfernalGrimoire, ElementalPrimer, TreatiseBalance, DragonRouge,
                 Vedas, CompendiumAncients, Necronomicon],
        'Rod': [WillowDiviningRod, CopperLeyRod, MoonlitHazelRod, DowsingRod, ScepterIfrit, GaiasBranch, Zephyruswand]},
    'Armor': {
        'Cloth': [Tunic, ClothCloak, SilverCloak, GoldCloak, CloakEnchantment, WizardRobe, Tarnkappe],
        'Light': [PaddedArmor, LeatherArmor, Cuirboulli, StuddedLeather, StuddedCuirboulli, MithrilCoat],
        'Medium': [HideArmor, ChainShirt, ScaleMail, Breastplate, HalfPlate, Kusari],
        'Heavy': [RingMail, ChainMail, Splint, PlateMail, Palangina, Maximilian]},
    'Helmet': {
        'Cloth': [ClothCap, Jaapi, Turban, WitchHat, EnchantedHood, MitreHat, Circlet,
                  CohuleenDruith, AriadnesDiadem],
        'Light': [LeatherCap, PithHelmet, WarMask, ArmingCap, Katapu, Somen, DemonCowl],
        'Medium': [ScaleHelm, ChainCoif, KulahKhud, Cervelliere, Tolga, Tarnhelm, HelmOfRostam],
        'Heavy': [IronHelm, KettleHelm, Barbute, GreatHelm, PlateHelm, CloseHelm, Kabuto]},
    'Accessory': {
        'Ring': [IronRing, PowerRing, AccuracyRing, BarrierRing, SteelRing, MightRing, EvasionRing,
                 TitaniumRing, ForceRing],
        'Pendant': [VisionPendant, RubyLocket, SilverNecklace, AntidotePendant, CalmingPendant,
                    FireChain, IceChain, ElectricChain, WaterChain, EarthChain, WindChain,
                    SapphireLocket, GoldNecklace, ElementalChain, GorgonPendant, GarfunkelPendant,
                    DharmaPendant, LevitationPendant, FireAmulet, IceAmulet, ElectricAmulet,
                    WaterAmulet, EarthAmulet, WindAmulet, InvisibilityPendant, DiamondLocket,
                    PlatinumNecklace, ElementalAmulet, RibbonPendant]},
    'Potion': {
        'Health': [HealthPotion, GreatHealthPotion, SuperHealthPotion, MasterHealthPotion],
        'Mana': [ManaPotion, GreatManaPotion, SuperManaPotion, MasterManaPotion],
        'Elixir': [Elixir, Megalixir],
        'Stat': [HPPotion, MPPotion, StrengthPotion, IntelPotion, WisdomPotion, ConPotion,
                 CharismaPotion, DexterityPotion, AardBeing],
        'Status': [Antidote, EyeDrop, EchoScreen, Bandage, PhoenixDown]},
    'Misc': {
        'Key': [Key, OldKey],
        'Tool': [LockpickKit, SmokeBomb],
        'Magic Tool': [Oculus],
        'Scroll': [BlankScroll, BlessScroll, SleepScroll, FireScroll, IceScroll, ElectricScroll, WaterScroll,
                   EarthScroll, WindScroll, ShadowScroll, HolyScroll, CleanseScroll, BoostScroll,
                   ShellScroll, SilenceScroll, DispelScroll, DeathScroll, SanctuaryScroll, UltimaScroll,
                   BattleHymnSheet, RampartsOdeSheet, DysfunctionSymphonySheet,
                   LowDefenseRhapsodySheet, SlowRideSheet, BonesThugsHarmonySheet,
                   ScoresAndScoresScoreSheet, GoldTriggerSheet, ChorusTimeSheet],
        'Reagents': []}
}

ultimate_weapons = {'Dagger': Carnwennan,
                   'Sword': Excalibur,
                   'Mace': Mjolnir,
                   'Fist': GodsHand,
                   'Axe': Jarnbjorn,
                   'Polearm': Gungnir,
                   'Staff': [PrincessGuard, RuyiJinguBang, DragonStaff],
                   'Hammer': Skullcrusher,
                   'Ninja Blade': Ninjato}


def ultimate_weapon_options_for(player: Any) -> list[tuple[str, type[Weapon]]]:
    """Return craftable ultimate weapon choices for the player's class."""
    options: list[tuple[str, type[Weapon]]] = []
    equip_check = getattr(getattr(player, "cls", None), "equip_check", None)
    if not callable(equip_check):
        return options

    for typ, weapon_entry in ultimate_weapons.items():
        weapon_classes = weapon_entry if isinstance(weapon_entry, (list, tuple)) else [weapon_entry]
        for weapon_cls in weapon_classes:
            if equip_check(weapon_cls, "Weapon"):
                options.append((typ, weapon_cls))
                break
    return options
