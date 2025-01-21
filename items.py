###########################################
""" item manager """

# Imports
import random
from textwrap import wrap
import numpy as np

import abilities
from character import StatusEffect


# Functions
def random_item(z):
    """
    Returns a random item based on the given integer.
    """

    random_dict = {"1":[],"2":[],"3":[],"4":[],"5":[],"6":[],"7":[],"8":[]}
    buckets = np.array([1.0, 0.9, 0.8, 0.75, 0.50, 0.4, 0.2, 0.0])
    for typ, typ_dict in items_dict.items():
        if typ == "Weapon":
            for handed in ["1-Handed", "2-Handed"]:
                for lst in items_dict[typ][handed].values():
                    for item in lst:
                        rarity = np.digitize(item().rarity, buckets)
                        random_dict[str(rarity)].append(item)
        elif typ == "Accessory":
            for acc in ["Ring", "Pendant"]:
                for item in items_dict[typ][acc]:
                    rarity = np.digitize(item().rarity, buckets)
                    random_dict[str(rarity+1)].append(item)
        else:
            for value in typ_dict.values():
                for item in value:
                    rarity = np.digitize(item().rarity, buckets)
                    random_dict[str(rarity+1)].append(item)
    return random.choice(random_dict[str(z)])


def remove_equipment(typ):
    typ_dict = {'Weapon': NoWeapon, 'OffHand': NoOffHand, 'Armor': NoArmor, 'Pendant': NoPendant, 'Ring': NoRing}
    return typ_dict[typ]()


class Item:
    """
    name: name of the item
    description: description of the item
    value: price in gold; sale price will be half this amount
    rarity: represented as a value between 0 and 1 and indicates the chance of dropping
    subtyp: the subtype of the item (i.e. Sword would be a subtype of Weapon)
    """

    def __init__(self, name, description, value, rarity, subtyp):
        self.name = name
        self.description = '\n'.join(wrap(description, 35, break_on_hyphens=False))
        self.value = value
        self.rarity = rarity
        self.subtyp = subtyp
        self.mod = 0
        self.weight = 0
        self.restriction = []
        self.ultimate = False

    def __str__(self):
        return (f"{'=' * ((35 - len(self.name)) // 2)}{self.name}{'=' * ((36 - len(self.name)) // 2)}\n"
                f"{self.description}\n"
                f"{35*'-'}\n"
                f"Sub-type: {'Special' if 'Summon' in self.subtyp else self.subtyp}\n"
                f"{35*'='}")

    def use(self, user, target=None, tile=None):
        return "", True


class Weapon(Item):
    """
    Subclass of the Item class
    damage: the base damage for each weapon
    crit: chance to double damage; higher number means lower chance to crit (calculation: 1 / crit parameter)
    handed: identifies weapon as 1-handed or 2-handed; 2-handed weapons prohibit the ability to use a shield
    unequip: boolean parameter indicating whether the object the base class used when an item is unequipped
    off: whether the weapon can be equipped in the offhand
    typ: the item type; 'Weapon' for this class
    disarm: boolean indicating whether the weapon can be disarmed; default is True
    ignore: boolean indicating whether the weapon automatically ignores armor when calculating damage
    """

    def __init__(self, name, description, value, rarity, damage, crit, handed, subtyp, unequip, off):
        super().__init__(name, description, value, rarity, subtyp)
        self.damage = damage
        self.crit = crit
        self.handed = handed
        self.unequip = unequip
        self.off = off
        self.typ = "Weapon"
        self.disarm = True
        self.ignore = False
        self.element = None

    def __str__(self):
        return (f"{'=' * ((35 - len(self.name)) // 2)}{self.name}{'=' * ((36 - len(self.name)) // 2)}\n"
                f"{self.description}\n"
                f"{35*'-'}\n"
                f"Type: {self.subtyp}\n"
                f"{self.handed}-handed\n"
                f"Damage: {self.damage}\n"
                f"Critical Chance: {int(self.crit * 100)}%\n"
                f"Weight: {self.weight}\n"
                f"{35*'='}")

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        return special_str


class Armor(Item):
    """
    armor: base armor for the item
    unequip: boolean parameter indicating whether the object the base class used when an item is unequipped
    typ: the item type; 'Armor' for this class
    """

    def __init__(self, name, description, value, rarity, armor, subtyp, unequip):
        super().__init__(name, description, value, rarity, subtyp)
        self.armor = armor
        self.unequip = unequip
        self.typ = 'Armor'

    def __str__(self):
        return (f"{'=' * ((35 - len(self.name)) // 2)}{self.name}{'=' * ((36 - len(self.name)) // 2)}\n"
                f"{self.description}\n"
                f"{35*'-'}\n"
                f"Type: {self.subtyp}\n"
                f"Armor: {self.armor}\n"
                f"Weight: {self.weight}\n"
                f"{35*'='}")

    def special_effect(self, wearer, attacker):
        special_str = ""
        return special_str


class OffHand(Item):
    """
    mod: stat depends on the off-hand item; mod for shields is block and spell damage modifier for tomes
        block: determines block chance, calculated as 1 / mod parameter (i.e. 1/2 or 50%)
        spell damage: base attack spell modifier
    unequip: boolean parameter indicating whether the object the base class used when an item is unequipped
    typ: the item type; 'OffHand' for this class
    """

    def __init__(self, name, description, value, rarity, mod, subtyp, unequip):
        super().__init__(name, description, value, rarity, subtyp)
        self.mod = mod
        self.unequip = unequip
        self.typ = 'OffHand'

    def __str__(self):
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

    def __init__(self, name, description, value, rarity, mod, subtyp, unequip):
        super().__init__(name, description, value, rarity, subtyp)
        self.mod = mod
        self.unequip = unequip
        self.typ = "Accessory"

    def __str__(self):
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

    def __init__(self, name, description, value, rarity, subtyp):
        super().__init__(name, description, value, rarity, subtyp)
        self.typ = "Potion"
        self.weight = 0.1

    def __str__(self):
        return (f"{'=' * ((35 - len(self.name)) // 2)}{self.name}{'=' * ((36 - len(self.name)) // 2)}\n"
                f"{self.description}\n"
                f"{35*'-'}\n"
                f"Weight: {self.weight}\n"
                f"{35*'='}")
    

class Misc(Item):
    """
    typ: the item type; 'Misc' for this class
    """

    def __init__(self, name, description, value, rarity, subtyp):
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

    def __init__(self, name, damage, crit, description, off):
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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not any(["Stun" in target.status_immunity,
                    f"Status-Stun" in target.equipment["Pendant"].mod,
                    "Status-All" in target.equipment["Pendant"].mod]):
            if crit > 1:
                if random.randint(wielder.stats.strength // 2, wielder.stats.strength) \
                        > random.randint(target.stats.con // 2, target.stats.con):
                    duration = max(1, wielder.stats.strength // 10)
                    target.status_effects["Stun"].active = True
                    target.status_effects["Stun"].duration = duration
                    special_str += f"{target.name} is stunned for {duration} turns."
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ=self.element)
        damage = int(random.randint(damage // 2, damage) * (1 - resist))
        if damage > 0:
            special_str += f"Holy light burns {target.name}, dealing {damage} additional holy damage."
            target.health.current -= damage
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not any(["Stun" in target.status_immunity,
                    f"Status-Stun" in target.equipment["Pendant"].mod,
                    "Status-All" in target.equipment["Pendant"].mod]):
            if crit > 1:
                if random.randint(wielder.check_mod("speed", enemy=target) // 2, wielder.check_mod("speed", enemy=target)) \
                        > random.randint(target.stats.con // 2, target.stats.con):
                    duration = max(1, wielder.check_mod("speed", enemy=target) // 10)
                    target.status_effects["Stun"].active = True
                    target.status_effects["Stun"].duration = duration
                    special_str += f"{target.name} is stunned for {duration} turns."
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not target.physical_effects["Disarm"].active:
            if target.equipment['Weapon'].subtyp not in ["Natural", "None", "Summon"]:
                chance = target.check_mod('luck', enemy=wielder, luck_factor=10)
                if random.randint(wielder.stats.strength // 2, wielder.stats.strength) \
                        > random.randint(target.check_mod("speed", enemy=wielder) // 2, 
                                         target.check_mod("speed", enemy=wielder)) + chance:
                    target.physical_effects["Disarm"].active = True
                    target.physical_effects["Disarm"].duration = wielder.stats.strength // 10
                    special_str += f"{target.name} is disarmed."
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if crit > 1:
            if random.randint((wielder.stats.strength // 2), wielder.stats.strength) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                duration = max(1, wielder.stats.strength // 10)
                bleed_dmg = max(wielder.stats.strength // 2, damage)
                target.physical_effects["Bleed"].active = True
                target.physical_effects["Bleed"].duration = max(duration, target.physical_effects["Bleed"].duration)
                target.physical_effects["Bleed"].extra = max(bleed_dmg, target.physical_effects["Bleed"].extra)
                if not target.physical_effects["Bleed"].active:
                    special_str += f"{target.name} is bleeding.\n"
                else:
                    special_str += f"{target.name} continues to bleed.\n"
        return special_str

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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not any(["Stun" in target.status_immunity,
                    f"Status-Stun" in target.equipment["Pendant"].mod,
                    "Status-All" in target.equipment["Pendant"].mod]):
            if not target.status_effects["Stun"].active:
                if crit > 1:
                    if random.randint(wielder.stats.strength // 2, wielder.stats.strength) \
                            > random.randint(target.stats.con // 2, target.stats.con):
                        duration = max(1, wielder.stats.strength // 10)
                        target.status_effects["Stun"].active = True
                        target.status_effects["Stun"].duration = duration
                        special_str += f"{target.name} is stunned for {duration} turns."
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if crit > 1:
            if not "Death" in target.status_immunity:
                w_chance = wielder.check_mod('luck', enemy=target, luck_factor=10)
                t_chance = target.check_mod('luck', enemy=wielder, luck_factor=10)
                if random.randint(0, wielder.check_mod("speed", enemy=target)) + w_chance > \
                        random.randint(target.stats.con // 2, target.stats.con) + t_chance:
                    special_str += f"The {self.name} blade rips the soul from {target.name} and they drop dead to the ground!"
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if crit > 1:
            if not "Death" in target.status_immunity:
                w_chance = wielder.check_mod('luck', enemy=target, luck_factor=10)
                t_chance = target.check_mod('luck', enemy=wielder, luck_factor=10)
                if random.randint(0, wielder.stats.strength) + w_chance > \
                        random.randint(target.stats.con // 2, target.stats.con) + t_chance:
                    special_str += f"The {self.name} decapitates {target.name} and they drop dead to the ground!"
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if crit > 1:
            if random.randint((wielder.stats.strength // 2), wielder.stats.strength) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                duration = max(1, wielder.stats.strength // 10)
                bleed_dmg = max(wielder.stats.strength // 2, damage)
                target.physical_effects["Bleed"].active = True
                target.physical_effects["Bleed"].duration = max(duration, target.physical_effects["Bleed"].duration)
                target.physical_effects["Bleed"].extra = max(bleed_dmg, target.physical_effects["Bleed"].extra)
                if not target.physical_effects["Bleed"].active:
                    special_str += f"{target.name} is bleeding.\n"
                else:
                    special_str += f"{target.name} continues to bleed.\n"
        return special_str

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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not target.physical_effects["Disarm"].active:
            if target.equipment['Weapon'].subtyp not in ["Natural", "None", "Summon"]:
                chance = target.check_mod('luck', enemy=wielder, luck_factor=10)
                if random.randint(wielder.stats.strength // 2, wielder.stats.strength) \
                        > random.randint(target.check_mod("speed", enemy=wielder) // 2,
                                         target.check_mod("speed", enemy=wielder)) + chance:
                    target.physical_effects["Disarm"].active = True
                    target.physical_effects["Disarm"].duration = wielder.stats.strength // 10
                    special_str += f"{target.name} is disarmed."
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        t_chance = target.check_mod('luck', enemy=target, luck_factor=5) / 100
        if 0.05 + t_chance > random.random():  # 5% chance plus charisma // 5
            heal = min(wielder.health.max - wielder.health.current, damage)
            wielder.health.current += heal
            special_str += f"The Holy Staff heals {wielder.name} for {heal} health.\n"
        return special_str


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
        self.restriction = ['Wizard', 'Necromancer', 'Master Monk', 'Lycan', 'Geomancer', 'Soulcatcher']
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        mana_heal = random.randint(damage // 2, damage)
        if wielder.mana.current + mana_heal > wielder.mana.max:
            mana_heal = wielder.mana.max - wielder.mana.current
        if mana_heal > 0:
            wielder.mana.current += mana_heal
            special_str += f"{wielder.name}'s mana is regenerated by {mana_heal}."
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        heal = random.randint(damage // 2, damage)
        if wielder.health.current + heal > wielder.health.max:
            heal = wielder.health.max - wielder.health.current
        if heal > 0:
            wielder.mana.current += heal
            special_str += f"{wielder.name}'s health is regenerated by {heal}."
        return special_str


class Sledgehammer(Weapon):

    def __init__(self):
        super().__init__(name="Sledgehammer", description="A sledgehammer is a tool with a large, flat, metal head, "
                                                          "attached to a long handle that gathers momentum during a "
                                                          "swing to apply a large force upon the target.",
                         value=800, rarity=0.9, damage=14, crit=0.075, handed=2, subtyp='Hammer', unequip=False,
                         off=False)
        self.weight = 20


class Maul(Weapon):

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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not any(["Stun" in target.status_immunity,
                    f"Status-Stun" in target.equipment["Pendant"].mod,
                    "Status-All" in target.equipment["Pendant"].mod]):
            if not target.status_effects["Stun"].active:
                if crit > 1:
                    if random.randint(wielder.stats.strength // 2, wielder.stats.strength) \
                            > random.randint(target.stats.con // 2, target.stats.con):
                        duration = max(1, wielder.stats.strength // 10)
                        target.status_effects["Stun"].active = True
                        target.status_effects["Stun"].duration = duration
                        special_str += f"{target.name} is stunned."
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = "Out of the maw flies a massive sand storm!\n"
        if crit > 1:
            special_str += abilities.Sandstorm(wielder, target=target, special=True)
        return special_str


class IceShard(NaturalWeapon):
    """
    Summon Agloolik weapon
    """

    def __init__(self):
        super().__init__(name="Ice Shard", damage=30, crit=0.33, description="", off=False)
        self.att_name = "throws ice shards at"
        self.element = "Ice"

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        shards = random.randint(0, wielder.intel // 8) * round(1 + crit)
        for _ in range(shards):
            damage += int(random.randint(1, wielder.intel) * random.uniform(-1, 1))
            if damage != 0:
                special_str += f"An ice shard hits {target.name} for {damage} damage.\n"
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        if crit > 1:
            special_str = abilities.Desoul(wielder, target, special=True)
        return special_str


class KoboldDagger(Weapon):
    """
    Used by the Kobalos Summon; has random affect on crit  TODO
    """

    def __init__(self):
        super().__init__(name="Kobold Dagger", description="",
                         value=0, rarity=0, damage=50, crit=0.4, handed=1, subtyp="Summon", unequip=False, off=False)

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if crit > 1:
            effects = []
        return special_str


# Natural weapons
class Bite(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Bite", damage=6, crit=0.05, description="", off=False)
        self.special = True
        self.att_name = 'bites'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if self.crit > random.random():
            special_str += "The bite is diseased.\n"
            if not random.randint(0, 39 // crit):
                special_str += f"The bite is diseased, crippling {target.name} and lowering their constitution by 1.\n"
                target.stats.con -= 1
            else:
                special_str += f"{target.name} resists the disease.\n"
        return special_str


class Bite2(Bite):

    def __init__(self):
        super().__init__()
        self.damage = 30
        self.crit = 0.2

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if self.crit > random.random():
            special_str += "The bite is diseased.\n"
            if not random.randint(0, 19 // crit):
                special_str += f"The disease cripples {target.name}, lowering their constitution by 1.\n"
                target.stats.con -= 1
            else:
                special_str += f"{target.name} resists the disease.\n"
        return special_str


class VampireBite(Bite):

    def __init__(self):
        super().__init__()
        self.damage = 20
        self.crit = 0.15

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if self.crit > random.random():
            wielder.health.current += damage
            wielder.health.current = min(wielder.health.current, wielder.health.max)
            special_str += f"{wielder.name} drains {target.name} and gains {damage} life.\n"
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ='Physical')
        if resist < 1:
            if random.randint((wielder.check_mod("speed", enemy=target) // 2) * crit,
                              wielder.check_mod("speed", enemy=target) * crit) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                if not target.physical_effects["Bleed"].active:
                    special_str += f"{target.name} is bleeding.\n"
                else:
                    special_str += f"{target.name} continues to bleed.\n"
                duration = max(1, wielder.check_mod("speed", enemy=target) // 10)
                bleed_dmg = int(max(wielder.check_mod("speed", enemy=target) // 2, damage) * (1 - resist))
                bleed_dmg = random.randint(bleed_dmg // 4, bleed_dmg)
                target.physical_effects["Bleed"] = StatusEffect(True,
                                                              max(duration, target.physical_effects["Bleed"].duration),
                                                              max(bleed_dmg, target.physical_effects["Bleed"].extra))
        return special_str


class BearClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Bear Claw", damage=24, crit=0.2, description="", off=True)
        self.special = True
        self.att_name = 'mauls'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ='Physical')
        if resist < 1:
            if random.randint((wielder.stats.strength // 2) * crit, wielder.stats.strength * crit) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                if not target.physical_effects["Bleed"].active:
                    special_str += f"{target.name} is bleeding.\n"
                else:
                    special_str += f"{target.name} continues to bleed.\n"
                duration = max(1, wielder.stats.strength // 10)
                bleed_dmg = int(max(wielder.stats.strength // 2, damage) * (1 - resist))
                bleed_dmg = random.randint(bleed_dmg // 4, bleed_dmg)
                target.physical_effects["Bleed"] = StatusEffect(True,
                                                              max(duration, target.physical_effects["Bleed"].duration),
                                                              max(bleed_dmg, target.physical_effects["Bleed"].extra))
        return special_str


class Stinger(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Stinger", damage=10, crit=0.25, description="", off=False)
        self.special = True
        self.att_name = 'stings'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ="Poison")
        if resist < 1 and not any(["Status-Poison" in target.status_immunity, "Status-All" in target.status_immunity]):
            if random.randint((wielder.check_mod("speed", enemy=target) * crit) // 2,
                              (wielder.check_mod("speed", enemy=target) * crit)) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                if not target.status_effects["Poison"].active:
                    special_str += f"{target.name} is poisoned.\n"
                else:
                    special_str += "The poison persists.\n"
                duration = max(1, wielder.check_mod("speed", enemy=target) // 10)
                damage = int(target.health.max * 0.005)
                pois_dmg = max(1, int(damage * (1 - resist)))
                target.status_effects["Poison"] = StatusEffect(True,
                                                               max(duration, target.status_effects["Poison"].duration),
                                                               max(pois_dmg, target.status_effects["Poison"].extra))
        return special_str


class Pincers(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Pincers", damage=8, crit=0.15, description="", off=True)
        self.special = True
        self.att_name = 'bites'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if random.randint(wielder.check_mod("speed", enemy=target) // 2, wielder.check_mod("speed", enemy=target)) \
            > random.randint(target.stats.con // 2, target.stats.con):
            resist = target.check_mod('resist', enemy=wielder, typ="Poison")
            if resist < 1 and not any(["Status-Poison" in target.status_immunity,
                                       "Status-All" in target.status_immunity]):
                if not target.status_effects["Poison"].active:
                    special_str += f"{target.name} is poisoned.\n"
                else:
                    special_str += "The poison persists.\n"
                duration = max(1, wielder.check_mod("speed", enemy=target) // 10)
                damage = int(target.health.max * 0.005)
                pois_dmg = max(1, int(damage * (1 - resist)))
                target.status_effects["Poison"] = StatusEffect(True,
                                                               max(duration, target.status_effects["Poison"].duration),
                                                               max(pois_dmg, target.status_effects["Poison"].extra))
            if not any(["Stun" in target.status_immunity,
                        f"Status-Stun" in target.equipment["Pendant"].mod,
                        "Status-All" in target.equipment["Pendant"].mod]):
                if not target.status_effects["Stun"].active:
                    p_resist = target.check_mod('resist', enemy=wielder, typ='Physical')
                    if crit > 1:
                        if random.randint(wielder.stats.strength // 2, wielder.stats.strength) * (1 - p_resist) \
                                > random.randint(target.stats.con // 2, target.stats.con):
                            s_duration = max(1, wielder.stats.strength // 10)
                            target.status_effects["Stun"] = StatusEffect(True, s_duration)
                            special_str += f"{target.name} is stunned.\n"
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        special_str += abilities.Doom().cast(wielder, target=target, special=True)
        return special_str


class DemonClaw2(DemonClaw):

    def __init__(self):
        super().__init__()
        self.damage = 30
        self.crit = 0.33
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        special_str += abilities.Desoul().cast(wielder, target=target, special=True)
        return special_str


class SnakeFang(NaturalWeapon):

    def __init__(self):
        super().__init__(name="Snake Fang", damage=10, crit=0.25, description="", off=False)
        self.special = True
        self.att_name = 'strikes'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ="Poison")
        if resist < 1 and not any(["Status-Poison" in target.status_immunity, "Status-All" in target.status_immunity]):
            if random.randint((wielder.check_mod("speed", enemy=target) * crit) // 2,
                              (wielder.check_mod("speed", enemy=target) * crit)) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                if not target.status_effects["Poison"].active:
                    special_str += f"{target.name} is poisoned.\n"
                else:
                    special_str += "The poison persists.\n"
                duration = max(1, wielder.check_mod("speed", enemy=target) // 10)
                damage = int(target.health.max * 0.005)
                pois_dmg = max(1, int(damage * (1 - resist)))
                target.status_effects["Poison"] = StatusEffect(True,
                                                               max(duration, target.status_effects["Poison"].duration),
                                                               max(pois_dmg, target.status_effects["Poison"].extra))
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not any(["Stun" in target.status_immunity,
                    f"Status-Stun" in target.equipment["Pendant"].mod,
                    "Status-All" in target.equipment["Pendant"].mod]):
            if not target.status_effects["Stun"].active:
                resist = target.check_mod('resist', enemy=wielder, typ='Physical')
                if resist < 1:
                    if crit > 1:
                        if random.randint(wielder.stats.strength // 2, wielder.stats.strength) * (1 - resist) \
                                > random.randint(target.stats.con // 2, target.stats.con):
                            duration = max(1, wielder.stats.strength // 10)
                            target.status_effects["Stun"] = StatusEffect(True, duration)
                            special_str += f"{target.name} is stunned.\n"
        return special_str


class LionPaw(NaturalWeapon):
    """
    Chance to berserk enemy
    """

    def __init__(self):
        super().__init__(name="Lion Paw", damage=34, crit=0.15, description="", off=True)
        self.att_name = 'swipes'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not any(["Berserk" in target.status_immunity,
                "Status-Berserk" in target.equipment["Pendant"].mod,
                "Status-All" in target.equipment["Pendant"].mod]):
            if not target.status_effects["Berserk"].active:
                if crit > 1:
                    if random.randint(0, wielder.stats.strength) > random.randint(target.stats.con // 2, target.stats.con):
                        duration = max(3, wielder.stats.strength // 10)
                        target.status_effects["Berserk"] = StatusEffect(True, duration)
                        special_str += f"{target.name} is enraged.\n"
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        t_chance = target.check_mod('luck', enemy=wielder, luck_factor=5) / 100
        if crit > 1:
            if random.random() > 0.95 + t_chance:  # 5% chance minus charisma // 5
                stat_list = ['strength', 'intelligence', 'wisdom', 'constitution', 'charisma', 'dexterity']
                stat_name = random.choice(stat_list)
                if stat_name == 'strength':
                    target.stats.strength -= 1
                if stat_name == 'intelligence':
                    target.stats.intel -= 1
                if stat_name == 'wisdom':
                    target.stats.wisdom -= 1
                if stat_name == 'constitution':
                    target.stats.con -= 1
                if stat_name == 'charisma':
                    target.stats.charisma -= 1
                if stat_name == 'dexterity':
                    target.stats.dex -= 1
                special_str += (f"The attack is devastating, causing {target.name} to lose 1 {stat_name}.\n")
        return special_str


class Gaze(NaturalWeapon):
    """
    Attempts to turn the player_char to stone
    """

    def __init__(self):
        super().__init__(name="Gaze", damage=0, crit=0, description="", off=False)
        self.special = True
        self.att_name = 'leers'

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = f"{wielder.name} {self.name} at {target.name}.\n"
        special_str += abilities.Petrify().cast(wielder, target=target, special=True)
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ='Physical')
        if resist < 1:
            if random.randint((wielder.stats.strength // 2) * crit, wielder.stats.strength * crit) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                if not target.physical_effects["Bleed"].active:
                    special_str += f"{target.name} is bleeding.\n"
                else:
                    special_str += f"{target.name} continues to bleed.\n"
                duration = max(1, wielder.stats.strength // 10)
                bleed_dmg = int(max(wielder.stats.strength // 2, damage) * (1 - resist))
                bleed_dmg = random.randint(bleed_dmg // 4, bleed_dmg)
                target.physical_effects["Bleed"] = StatusEffect(True,
                                                              max(duration, target.physical_effects["Bleed"].duration),
                                                              max(bleed_dmg, target.physical_effects["Bleed"].extra))
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not any(["Stun" in target.status_immunity,
                    f"Status-Stun" in target.equipment["Pendant"].mod,
                    "Status-All" in target.equipment["Pendant"].mod]):
            if not target.status_effects["Stun"].active:
                resist = target.check_mod('resist', enemy=wielder, typ='Physical')
                if resist < 1:
                    if crit > 1:
                        if random.randint(wielder.stats.strength // 2, wielder.stats.strength) * (1 - resist) \
                                > random.randint(target.stats.con // 2, target.stats.con):
                            duration = max(1, wielder.stats.strength // 10)
                            target.status_effects["Stun"] = StatusEffect(True, duration)
                            special_str += f"{target.name} is stunned.\n"
        return special_str


class NightmareHoof(NaturalWeapon):
    """
    Natural weapon of Nightmare; additional fire damage
    """

    def __init__(self):
        super().__init__(name="Nightmare Hoof", damage=26, crit=0.25, description="", off=True)
        self.special = True
        self.att_name = 'attacks'
        self.element = "Fire"

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ=self.element)
        damage = int(random.randint(wielder.stats.intel // 2, wielder.stats.intel) * (1 - resist))
        target.health.current -= damage
        if damage > 0:
            special_str += f"The fire from {wielder.name}'s attack burns {target.name} for {damage} damage.\n"
        elif damage < 0:
            special_str += f"{target.name} absorbs the fire damage and is healed for {abs(damage)} hit points.\n"
        else:
            special_str += "The fire is ineffective, dealing no damage.\n"
        return special_str


class ElementalBlade(NaturalWeapon):
    """
    Innate weapon possessed by Myrmidons; does elemental damage based on the enemy type
    """

    def __init__(self):
        super().__init__(name="Elemental Blade", damage=30, crit=0.25, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        elemental_type = max(wielder.resistance, key=wielder.resistance.get)
        resist = target.check_mod('resist', enemy=wielder, typ=elemental_type)
        damage = int(damage * (1 - resist))
        if damage < 0:
            special_str += f"{target.name} absorbs the {elemental_type.lower()} damage, gaining {abs(damage)} hit points.\n"
        elif damage > 0:
            special_str += f"{wielder.name}'s blade deals {damage} additional {elemental_type.lower()} damage to {target.name}.\n"
        else:
            special_str += f"{elemental_type} damage was not effective against {target.name}.\n"
        target.health.current -= damage
        if damage > 0 and elemental_type == "Fire" and target.is_alive():
            if not target.magic_effects["DOT"].active:
                special_str += f"{target.name} is on fire.\n"
            target.magic_effects["DOT"] = StatusEffect(True, 3, 
                                                        max(int(damage // 2), target.magic_effects["DOT"].extra))
        return special_str


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

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        special_str += abilities.Trip().use(wielder, target, special=True)
        return special_str


class Tentacle2(Tentacle):
    """
    Chance to stun
    """

    def __init__(self):
        super().__init__()
        self.damage = 48
        self.crit = 0.3
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not any(["Stun" in target.status_immunity,
                    f"Status-Stun" in target.equipment["Pendant"].mod,
                    "Status-All" in target.equipment["Pendant"].mod]):
            if not target.status_effects["Stun"].active:
                resist = target.check_mod('resist', enemy=wielder, typ='Physical')
                if resist < 1:
                    if crit > 1:
                        if random.randint(wielder.stats.strength // 2, wielder.stats.strength) * (1 - resist) \
                                > random.randint(target.stats.con // 2, target.stats.con):
                            duration = max(1, wielder.stats.strength // 10)
                            target.status_effects["Stun"] = StatusEffect(True, duration)
                            special_str += f"{target.name} is stunned.\n"
        return special_str


class InvisibleBlade(NaturalWeapon):
    """
    Shadow element
    Only stuns on crit
    """

    def __init__(self):
        super().__init__(name="Invisible Blade", damage=18, crit=0.25, description="", off=True)
        self.special = True
        self.element = "Shadow"

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not any(["Stun" in target.status_immunity,
                    f"Status-Stun" in target.equipment["Pendant"].mod,
                    "Status-All" in target.equipment["Pendant"].mod]):
            if not target.status_effects["Stun"].active:
                resist = target.check_mod('resist', enemy=wielder, typ='Physical')
                if resist < 1:
                    if crit > 1:
                        if random.randint(0, wielder.check_mod("speed", enemy=target) // 2) * (1 - resist) \
                                > random.randint(target.stats.con // 2, target.stats.con):
                            duration = 1
                            target.status_effects["Stun"] = StatusEffect(True, duration)
                            special_str += f"{target.name} is stunned.\n"
        return special_str


class CerberusClaw(NaturalWeapon):

    def __init__(self):
        super().__init__(name='claws', damage=40, crit=0.25, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ='Physical')
        if resist < 1:
            if random.randint((wielder.stats.strength // 2) * crit, wielder.stats.strength * crit) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                if not target.physical_effects["Bleed"].active:
                    special_str += f"{target.name} is bleeding.\n"
                else:
                    special_str += f"{target.name} continues to bleed.\n"
                duration = max(1, wielder.stats.strength // 10)
                bleed_dmg = int(max(wielder.stats.strength // 2, damage) * (1 - resist))
                bleed_dmg = random.randint(bleed_dmg // 4, bleed_dmg)
                target.physical_effects["Bleed"] = StatusEffect(
                    True, max(duration, target.physical_effects["Bleed"].duration),
                    max(bleed_dmg, target.physical_effects["Bleed"].extra))
        return special_str


class CerberusBite(NaturalWeapon):

    def __init__(self):
        super().__init__(name="bites", damage=60, crit=0.25, description="", off=False)
        self.special = True
        self.element = "Fire"

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        resist = target.check_mod('resist', enemy=wielder, typ=self.element)
        damage = int(random.randint(damage // 2, damage) * (1 - resist))
        target.health.current -= damage
        if damage > 0:
            special_str += f"The fire from {wielder.name}'s bite burns {target.name} for {damage} damage.\n"
        elif damage < 0:
            special_str += f"{target.name} absorbs the fire damage and is healed for {abs(damage)} hit points.\n"
        else:
            special_str += f"The fire is ineffective, dealing {damage} damage.\n"
        return special_str


class LichHand(NaturalWeapon):
    """
    Chance to paralyze (stun) enemy
    """

    def __init__(self):
        super().__init__(name="touches", damage=35, crit=0.2, description="", off=True)
        self.special = True
        self.element = "Ice"

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not any(["Stun" in target.status_immunity,
                    f"Status-Stun" in target.equipment["Pendant"].mod,
                    "Status-All" in target.equipment["Pendant"].mod]):
            if not target.status_effects["Stun"].active:
                if crit > 1:
                    if random.randint(wielder.stats.intel // 4, wielder.stats.intel) \
                            > random.randint(target.stats.wisdom // 2, target.stats.wisdom):
                        duration = max(1, wielder.stats.intel // 10)
                        target.status_effects["Stun"] = StatusEffect(True, duration)
                        special_str += f"{target.name} is stunned.\n"
        return special_str


class Cannon(NaturalWeapon):
    """
    Chance to stun the target
    """

    def __init__(self):
        super().__init__(name="attacks", damage=80, crit=0.15, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        if not any(["Stun" in target.status_immunity,
                    f"Status-Stun" in target.equipment["Pendant"].mod,
                    "Status-All" in target.equipment["Pendant"].mod]):
            if not target.status_effects["Stun"].active:
                if crit > 1:
                    if random.randint(wielder.stats.strength // 4, wielder.stats.strength) \
                            > random.randint(target.stats.con // 2, target.stats.con):
                        duration = max(1, wielder.stats.strength // 10)
                        target.status_effects["Stun"] = StatusEffect(True, duration)
                        special_str += f"{target.name} is stunned.\n"
        return special_str


class DevilBlade(NaturalWeapon):
    """
    Chance on crit to apply one of the following status effects: Silence, Stun, Doom, Blind, Sleep, Poison, or Berserk
    """

    def __init__(self):
        super().__init__(name='attacks', damage=100, crit=0.33, description="", off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        special_str = ""
        w_chance = wielder.check_mod('luck', enemy=target, luck_factor=10)
        t_chance = target.check_mod('luck', enemy=wielder, luck_factor=20)
        if crit > 1:
            if random.randint(0, w_chance) > random.randint(0, t_chance):
                effect = random.choice(target.status_effects)
                if any([effect in target.status_immunity,
                        f"Status-{effect}" in target.equipment["Pendant"].mod,
                        "Status-All" in target.equipment["Pendant"].mod]):
                    return special_str
                target.status_effects[effect] = StatusEffect(
                    True, max(random.randint(1, 5), target.status_effects[effect].duration))
                if effect == "Poison":
                    damage = int(target.health.max * 0.005)
                    target.status_effects["Poison"].extra += damage  # damage builds over time
                special_str += f"The attack inflicts {effect.lower()} on {target.name}.\n"
        return special_str


# Armor items
class NoArmor(Armor):

    def __init__(self):
        super().__init__(name="No Armor", description="No armor equipped.", value=0, rarity=0, armor=0,
                         subtyp='None', unequip=True)


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

    def special_effect(self, wearer, attacker):
        return super().special_effect(wearer, attacker)


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


class Aegis(Armor):

    def __init__(self):
        super().__init__(name="Aegis Breastplate", description="The breastplate of Zeus, emboldened with a bolt of "
                                                               "lightning.",
                         value=0, rarity=0., armor=36, subtyp='Medium', unequip=False)
        self.weight = 18


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


class FullPlate(Armor):

    def __init__(self):
        super().__init__(name="Full Plate", description="Armor consisting of shaped, interlocking metal plates to "
                                                        "cover the entire body. Full plate includes gauntlets, "
                                                        "heavy leather boots, a visored helmet, and thick layers of "
                                                        "padding underneath the armor. Buckles and straps distribute "
                                                        "the weight over the body.",
                         value=55000, rarity=0.4, armor=30, subtyp='Heavy', unequip=False)
        self.weight = 30


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


# Natural armor
class NaturalArmor(Armor):

    def __init__(self, name, armor, description):
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
        self.shadow_damage = 100

    def special_effect(self, wearer, attacker):
        special_str = ""
        resist = attacker.check_mod('resist', enemy=wearer, typ='Shadow')
        damage = int(random.randint(self.shadow_damage // 2, self.shadow_damage) * (1 - resist))
        attacker.health.current -= damage
        if damage > 0:
            special_str += f"An aura of shadow emanates from {wearer.name}, dealing {damage} damage to {attacker.name}.\n"
        elif damage < 0:
            special_str += (
                f"{attacker.name} absorbs the shadow damage emanating from {wearer.name} and is healed for "
                f"{abs(damage)} hit points.\n")
        else:
            special_str += f"The shadow aura is ineffective, dealing {damage} damage.\n"
        return special_str


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

    def special_effect(self, wearer, attacker):
        special_str = ""
        resist = attacker.check_mod('resist', enemy=wearer, typ='Fire')
        damage = int(random.randint(self.fire_damage // 2, self.fire_damage) * (1 - resist))
        attacker.health.current -= damage
        if damage > 0:
            special_str += f"An aura of fire emanates from {wearer.name}, dealing {damage} damage to {attacker.name}.\n"
        elif damage < 0:
            special_str += (
                f"{attacker.name} absorbs the fire damage emanating from {wearer.name} and is healed for {abs(damage)} "
                f"hit points.\n")
        else:
            special_str += f"The fire is ineffective, dealing {damage} damage.\n"
        return special_str


class DevilSkin(NaturalArmor):
    """
    deals additional non-elemental damage to attacker
    """

    def __init__(self):
        super().__init__(name='Devil Skin', armor=80, description="")
        self.special = True
        self.damage = 100

    def special_effect(self, wearer, attacker):
        special_str = ""
        a_chance = attacker.check_mod('luck', enemy=wearer, luck_factor=10)
        damage = random.randint(self.damage // (1 + a_chance), self.damage)
        attacker.health.current -= damage
        if damage > 0:
            special_str += f"An aura emanates from {wearer.name}, dealing {damage} damage to {attacker.name}.\n"
        else:
            special_str += f"The aura is ineffective, dealing {damage} damage.\n"
        return special_str


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
                                                     "cosmic balance. Equipping this shield increase ones resistance "
                                                     "to fire by 25%.",
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

    def __init__(self, name, mod, subtyp):
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


class Grimoire(OffHand):

    def __init__(self):
        super().__init__(name="Grimoire", description="A book of magic and invocations.",
                         value=2500, rarity=0.85, mod=22, subtyp='Tome', unequip=False)
        self.weight = 3


class BookShadows(OffHand):

    def __init__(self):
        super().__init__(name="Book of Shadows", description="The Book of Shadows is a book containing religious text "
                                                             "and instructions for magical rituals found within the "
                                                             "Neopagan religion of Wicca, and in many pagan practices.",
                         value=10000, rarity=0.75, mod=30, subtyp='Tome', unequip=False)
        self.weight = 2


class DragonRouge(OffHand):

    def __init__(self):
        super().__init__(name="Dragon Rouge", description="French for \"Red Dragon\", this mythical tome contains "
                                                          "ancient knowledge passed down through the ages.",
                         value=21000, rarity=0.5, mod=36, subtyp='Tome', unequip=False)
        self.weight = 4


class Vedas(OffHand):

    def __init__(self):
        super().__init__(name="Vedas", description="A large body of religious texts, consisting of some of the oldest "
                                                   "holy teachings.",
                         value=50000, rarity=0.4, mod=54, subtyp='Tome', unequip=False)
        self.weight = 4


class Necronomicon(OffHand):

    def __init__(self):
        super().__init__(name="Necronomicon", description="The Book of the Dead, a mystical grimoire written by an "
                                                          "unknown author.",
                         value=65000, rarity=0.2, mod=60, subtyp='Tome', unequip=False)
        self.weight = 6
        self.restriction = ['Warlock', 'Necromancer']


class Magus(OffHand):

    def __init__(self):
        super().__init__(name="Magus", description="A book of magical art written by a powerful wizard.",
                         value=90000, rarity=0.05, mod=90, subtyp='Tome', unequip=False)
        self.weight = 3


# Rod items
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
                         value=5000, rarity=0.75, mod=10, subtyp="Musical Instrument", unequip=False)


class Lyre(OffHand):

    def __init__(self):
        super().__init__(name="Lyre", description="",
                         value=16000, rarity=0.5, mod=15, subtyp="Musical Instrument", unequip=False)


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

    def class_mod(self, player_char):
        pass  # TODO


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
        super().__init__(name="Ruby Locket", description="A ruby necklace that improves the wearer's magic damage.",
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
        super().__init__(name="Element Chain", description="Base class for the various element chains. The chain "
                                                           "provides an additional 50% resistance to the element(s).",
                         value=8000, rarity=0.6, mod="None", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class FireChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Fire Chain"
        self.description = ("This necklace increases the resistance for the wearer to fire by 50%.")
        self.mod = "Resist-Fire"


class IceChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Ice Chain"
        self.description = ("This necklace increases the resistance for the wearer to ice by 50%.")
        self.mod = "Resist-Ice"

class ElectricChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Electric Chain"
        self.description = ("This necklace increases the resistance for the wearer to electric by 50%.")
        self.mod = "Resist-Electric"

class WaterChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Water Chain"
        self.description = ("This necklace increases the resistance for the wearer to water by 50%.")
        self.mod = "Resist-Water"

class EarthChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Earth Chain"
        self.description = ("This necklace increases the resistance for the wearer to earth by 50%.")
        self.mod = "Resist-Earth"

class WindChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Wind Chain"
        self.description = ("This necklace increases the resistance for the wearer to wind by 50%.")
        self.mod = "Resist-Wind"


class ElementalChain(ElementChain):

    def __init__(self):
        super().__init__()
        self.name = "Elemental Chain"
        self.description = ("Fashioned from the cores of elementals, this necklace increases the resistance for the "
                            "wearer to the 6 main elemental types, fire, ice, electric, water, earth, and wind by 50%.")
        self.value = 15000
        self.rarity = 0.4
        self.mod = "Resist-Elemental"


class SapphireLocket(Accessory):

    def __init__(self):
        super().__init__(name="Sapphire Locket", description="A sapphire necklace that greatly improves the wearer's "
                                                             "magic damage.",
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


class LevitationPendant(Accessory):

    def __init__(self):
        super().__init__(name="Levitation Pendant", description="Gives the wearer the ability to fly, making them "
                                                                 "harder to hit and immunity from Earth spells. The "
                                                                 "downfall is that Wind spells will hurt more.",
                         value=30000, rarity=0.25, mod="Flying", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class ElementAmulet(Accessory):

    def __init__(self):
        super().__init__(name="Element Amulet", description="Base class for the various element amulets.",
                         value=40000, rarity=0.2, mod="None", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class FireAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Fire Amulet"
        self.description = ("This amulet increases the immunity for the wearer to fire by 100%.")
        self.mod = "Immune-Fire"


class IceAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Ice Amulet"
        self.description = ("This amulet increases the immunity for the wearer to ice by 100%.")
        self.mod = "Immune-Ice"

class ElectricAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Electric Amulet"
        self.description = ("This amulet increases the immunity for the wearer to electric by 100%.")
        self.mod = "Immune-Electric"

class WaterAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Water Amulet"
        self.description = ("This amulet increases the immunity for the wearer to water by 100%.")
        self.mod = "Immune-Water"

class EarthAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Earth Amulet"
        self.description = ("This amulet increases the immunity for the wearer to earth by 100%.")
        self.mod = "Immune-Earth"

class WindAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Wind Amulet"
        self.description = ("This amulet increases the immunity for the wearer to wind by 100%.")
        self.mod = "Immune-Wind"


class ElementalAmulet(ElementAmulet):

    def __init__(self):
        super().__init__()
        self.name = "Elemental Amulet"
        self.description = ("Legend claims the jewel of this amulet is actually the heart of a god. This amulet "
                            "increases the immunity for the wearer to the 6 main elemental types, fire, ice, "
                            "electric, water, earth, and wind by 100%.")
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


class HealthPotion(Potion):

    def __init__(self):
        super().__init__(name="Health Potion", description="A potion that restores up to 25% of your health.",
                         value=100, rarity=0.99, subtyp='Health')
        self.percent = 0.25

    def use(self, user, target=None):
        use_str = ""
        if user.health.current == user.health.max:
            use_str += "You are already at full health.\n"
            return use_str, False
        user.modify_inventory(self, subtract=True)
        if user.state != 'fight':
            heal = int(user.health.max * self.percent)
        else:
            rand_heal = int(user.health.max * self.percent)
            heal = random.randint(rand_heal // 2, rand_heal) * max(1, user.check_mod('luck', luck_factor=12))
            heal = max(heal, int(50 * self.percent))
        use_str += f"The potion healed you for {heal} life.\n"
        user.health.current += heal
        if user.health.current >= user.health.max:
            user.health.current = user.health.max
            use_str += "You are at max health.\n"
        return use_str, True


class GreatHealthPotion(HealthPotion):

    def __init__(self):
        super().__init__()
        self.name = "Great Health Potion"
        self.description = "\n".join(wrap("A potion that restores up to 50% of your health.", 35, break_on_hyphens=False))
        self.value = 600
        self.rarity = 0.7
        self.percent = 0.50


class SuperHealthPotion(HealthPotion):

    def __init__(self):
        super().__init__()
        self.name = "Super Health Potion"
        self.description = "\n".join(wrap("A potion that restores up to 75% of your health.", 35, break_on_hyphens=False))
        self.value = 3000
        self.rarity = 0.5
        self.percent = 0.75


class MasterHealthPotion(HealthPotion):

    def __init__(self):
        super().__init__()
        self.name = "Master Health Potion"
        self.description = "\n".join(wrap("A potion that restores up to 100% of your health.", 35, break_on_hyphens=False))
        self.value = 10000
        self.rarity = 0.3
        self.percent = 1.0


class ManaPotion(Potion):

    def __init__(self):
        super().__init__(name="Mana Potion", description="A potion that restores up to 25% of your mana.",
                         value=250, rarity=0.9, subtyp='Mana')
        self.percent = 0.25

    def use(self, user, target=None):
        use_str = ""
        if user.mana.current == user.mana.max:
            use_str += "You are already at full mana.\n"
            return use_str, False
        user.modify_inventory(self, subtract=True)
        if user.state != 'fight':
            heal = int(user.mana.max * self.percent)
        else:
            rand_res = int(user.mana.max * self.percent)
            heal = random.randint(rand_res // 2, rand_res) * max(1, user.check_mod('luck', luck_factor=12))
        use_str += f"The potion restored {heal} mana points.\n"
        user.mana.current += heal
        if user.mana.current >= user.mana.max:
            user.mana.current = user.mana.max
            use_str += "You are at full mana.\n"
        return use_str, True


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

    def use(self, user, target=None):
        use_str = ""
        if user.health.current == user.health.max and user.mana.current == user.mana.max:
            use_str += "You are already at full health and mana.\n"
            return use_str, False
        user.modify_inventory(self, subtract=True)
        if user.state != 'fight':
            health_heal = int(user.health.max * self.percent)
            mana_heal = int(user.mana.max * self.percent)
        else:
            rand_heal = int(user.health.max * self.percent)
            rand_res = int(user.mana.max * self.percent)
            health_heal = random.randint(rand_heal // 2, rand_heal) * max(1, user.check_mod('luck', luck_factor=12))
            mana_heal = random.randint(rand_res // 2, rand_res) * max(1, user.check_mod('luck', luck_factor=12))
        use_str += f"The potion restored {health_heal} health points and {mana_heal} mana points.\n"
        user.health.current += health_heal
        user.mana.current += mana_heal
        if user.health.current >= user.health.max:
            user.health.current = user.health.max
            use_str += "You are at max health.\n"
        if user.mana.current >= user.mana.max:
            user.mana.current = user.mana.max
            use_str += "You are at full mana.\n"
        return use_str, True


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

    def use(self, user, target=None):
        user.modify_inventory(self, subtract=True)
        user.health.max += self.mod
        if user.in_town():
            user.health.current = user.health.max
        use_str = f"{user.name}'s HP has increased by {self.mod}!\n"
        return use_str, True


class MPPotion(Potion):

    def __init__(self):
        super().__init__(name="MP Potion", description="A potion that permanently increases your max mana by 10.",
                         value=15000, rarity=0.6, subtyp='Stat')
        self.mod = 10

    def use(self, user, target=None):
        user.modify_inventory(self, subtract=True)
        user.mana.max += self.mod
        if user.in_town():
            user.mana.current = user.mana.max
        use_str = f"{user.name}'s MP has increased by {self.mod}!\n"
        return use_str, True


class StrengthPotion(Potion):

    def __init__(self):
        super().__init__(name="Strength Potion", description="A potion that permanently increases your strength by 1.",
                         value=50000, rarity=0.3, subtyp='Stat')

    def use(self, user, target=None):
        user.modify_inventory(self, subtract=True)
        user.stats.strength += 1
        use_str = f"{user.name}'s strength has increased by 1!\n"
        return use_str, True


class IntelPotion(Potion):

    def __init__(self):
        super().__init__(name="Intelligence Potion", description="A potion that permanently increases your intelligence"
                                                                 " by 1.",
                         value=50000, rarity=0.3, subtyp='Stat')

    def use(self, user, target=None):
        user.modify_inventory(self, subtract=True)
        user.stats.intel += 1
        use_str = f"{user.name}'s intelligence has increased by 1!\n"
        return use_str, True


class WisdomPotion(Potion):

    def __init__(self):
        super().__init__(name="Wisdom Potion", description="A potion that permanently increases your wisdom by 1.",
                         value=50000, rarity=0.3, subtyp='Stat')

    def use(self, user, target=None):
        user.modify_inventory(self, subtract=True)
        user.stats.wisdom += 1
        use_str = f"{user.name}'s wisdom has increased by 1!\n"
        return use_str, True


class ConPotion(Potion):

    def __init__(self):
        super().__init__(name="Constitution Potion", description="A potion that permanently increases your constitution"
                                                                 " by 1.",
                         value=50000, rarity=0.3, subtyp='Stat')

    def use(self, user, target=None):
        user.modify_inventory(self, subtract=True)
        user.stats.con += 1
        use_str = f"{user.name}'s constitution has increased by 1!\n"
        return use_str, True


class CharismaPotion(Potion):

    def __init__(self):
        super().__init__(name="Charisma Potion", description="A potion that permanently increases your charisma by 1.",
                         value=50000, rarity=0.3, subtyp='Stat')

    def use(self, user, target=None):
        user.modify_inventory(self, subtract=True)
        user.stats.charisma += 1
        use_str = f"{user.name}'s charisma has increased by 1!\n"
        return use_str, True


class DexterityPotion(Potion):

    def __init__(self):
        super().__init__(name="Dexterity Potion", description="A potion that permanently increases your dexterity by "
                                                              "1.",
                         value=50000, rarity=0.3, subtyp='Stat')

    def use(self, user, target=None):
        user.modify_inventory(self, subtract=True)
        user.stats.dex += 1
        use_str = f"{user.name}'s dexterity has increased by 1!\n"
        return use_str, True


class AardBeing(Potion):

    def __init__(self):
        super().__init__(name="Aard of Being", description="A potion that permanently increases all stats by 1.",
                         value=250000, rarity=0.01, subtyp='Stat')

    def use(self, user, target=None):
        user.modify_inventory(self, subtract=True)
        user.stats.strength += 1
        user.stats.intel += 1
        user.stats.wisdom += 1
        user.stats.con += 1
        user.stats.charisma += 1
        user.stats.dex += 1
        use_str = f"All of {user.name}'s stats have been increased by 1!\n"
        return use_str, True


class Status(Potion):

    def __init__(self):
        super().__init__(name="Status", description="Base class for status items.",
                         value=0, rarity=0, subtyp="Status")
        self.status = None

    def use(self, user, target=None):
        use_str = ""
        if not user.status_effects[self.status].active:
            use_str += f"You are not affected by {self.status.lower()}.\n"
            return use_str, False
        user.modify_inventory(self, subtract=True)
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
        return use_str, True


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

    def use(self, user, target=None):
        use_str = ""
        if not user.physical_effects[self.status].active:
            use_str += f"You are not affected by {self.status.lower()}.\n"
            return use_str, False
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
        return use_str, True

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

    def use(self, user, target=None):
        use_str = ""
        if not any([user.status_effects[x].active for x in self.status]):
            use_str += f"You are not affected by any negative status effects.\n"
            return use_str, False
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
        return use_str, True


class Key(Misc):
    """
    Opens locked chests
    """

    def __init__(self):
        super().__init__(name="Key", description="Unlocks a locked chest but is consumed.", value=500, rarity=0.9,
                         subtyp='Key')

    def use(self, user, target=None):
        use_str = ""
        tile = user.world_dict[(user.location_x, user.location_y, user.location_z)]
        if 'Chest' in str(tile):
            user.modify_inventory(self, subtract=True)
            tile.locked = False
            use_str += f"{user.name} unlocks the chest.\n"
        else:
            use_str += "The key does not fit in the door.\n"
        return use_str, True


class OldKey(Misc):
    """
    Opens locked doors
    """

    def __init__(self):
        super().__init__(name="Old Key", description="Unlocks doors that may lead to either valuable treasure or to "
                                                     "powerful enemies.",
                         value=50000, rarity=0.5, subtyp='Key')

    def use(self, user, target=None):
        use_str = ""
        tile = user.world_dict[(user.location_x, user.location_y, user.location_z)]
        if 'Door' in str(tile):
            user.modify_inventory(self, subtract=True)
            tile.locked = False
            use_str += f"{user.name} unlocks the door.\n"
        else:
            use_str += "The key does not fit in the chest.\n"
        return use_str, True


class Scroll(Misc):
    """
    Scrolls allow for a one-time use of a spell; scrolls can only be used in combat
    """

    def __init__(self):
        super().__init__(name="Scroll", description="Base class for scrolls.", value=0, rarity=0, subtyp='Scroll')
        self.spell = None
        self.charges = random.randint(2, 10)

    def use(self, user, target=None):
        use_str = f"{user.name} uses {self.name}.\n"
        use_str += self.spell.cast(user, target=target, special=True)
        self.charges -= 1
        if not self.charges:
            use_str += "The scroll crumbles to dust in your hands!\n"
            user.modify_inventory(self, subtract=True)
        return use_str, True


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
        self.value = 2500
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
        self.value = 2500
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
        self.value = 2500
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
        self.value = 2500
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
        self.value = 2500
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
        self.value = 2500
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
        self.value = 2500
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
        self.value = 2500
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
        self.value = 2500
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
        self.value = 5000
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
        self.value = 5000
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
        self.value = 5000
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
        self.value = 7500
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
        self.value = 10000
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
        self.value = 25000
        self.rarity = 0.25
        self.spell = abilities.Sanctuary()

    def use(self, user):
        use_str = f"{user.name} uses {self.name}.\n"
        use_str += self.spell.cast_out(user=user)
        self.charges -= 1
        if not self.charges:
            use_str += "The scroll crumbles to dust in your hands!\n"
            user.modify_inventory(self, subtract=True)
        return use_str, True


class UltimaScroll(Scroll):
    """
    Ultima
    """

    def __init__(self):
        super().__init__()
        self.name = "Ultima Scroll"
        self.description = "\n".join(wrap("Scroll inscribed with an incantation allowing the user to cast the powerful"
                                          " Ultima. The scroll will be consumed when it is out of charges.", 35, break_on_hyphens=False))
        self.value = 50000
        self.rarity = 0.01
        self.spell = abilities.Ultima()


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


class DeadBody(Misc):

    def __init__(self):
        super().__init__(name="Dead Body", description="The partially eaten body of a very green warrior. He never "
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


class PowerCore(Misc):

    def __init__(self):
        super().__init__(name="Power Core", description="The power source of a Golem.",
                         value=0, rarity=1, subtyp="Quest")


class Phylactery(Misc):

    def __init__(self):
        super().__init__(name="Phylactery", description="The soul artifcat of a Lich, given up willingly to achieve "
                                                        "immortality.",
                         value=0, rarity=0.05, subtyp="Quest")


class LuckyLocket(Misc):
    """
    Momento given to the warrior Joffrey by the waitress, his betrothed
    """

    def __init__(self):
        super().__init__(name="Lucky Locket", description="A simple gold necklace with a locket containing the picture "
                                                          "of a fair lass.",
                         value=0, rarity=0, subtyp="Special")


class OrnateKey(Misc):
    """
    Special key believed to be for opening the tavern but actually opens Joffrey's locker in barracks
    """

    def __init__(self):
        super().__init__(name="Ornate Key", description="A brass key with an ornate head, similar to the key for"
                                                        " your storage locker in the barracks.",
                         value=0, rarity=0, subtyp="Special")


class JoffreysLetter(Misc):
    """
    A letter written from Joffrey to the waitress; maybe there is some use of this
    """

    def __init__(self):
        super().__init__(name="Joffrey's Letter", description="A letter written from Joffrey to the waitress; maybe "
                                                              "there is some use of this.",
                         value=0, rarity=0, subtyp="Special")


class Joker(Misc):
    """
    Dropped by Jester; used to obtain the trickster summon Kobalos
    """

    def __init__(self):
        super().__init__(name="Joker", description="They say that Joker's are wild; you'll see how wild this one is.",
                         value=0, rarity=0, subtyp="Special")


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
        super().__init__(name="Excaliper", description="An old brake caliper reforged into the legendary Excalibur. It"
                                                       " did not go as planned...",
                        value=0, rarity=0, subtyp="Special")


class ChiryuKoma(Misc):
    """
    Needed to unlock Dilong summon; visit 1:I17 with item in inventory
    """

    def __init__(self):
        super().__init__(name="Chiryu Koma", description="A game piece used for shogi, depicting an earth dragon.",
                         value=0, rarity=0.1, subtyp="Summon - Dilong")


class BlacksmithsHammer(Misc):
    """
    Needed to unlock Cacus summon; gained after obtaining first 2 relics and visiting Griswold; visit 2:F13 with item 
      in inventory
    """

    def __init__(self):
        super().__init__(name="Blacksmith's Hammer", description="It looks like a normal blacksmithing hammer but "
                                                                 "something seems...special about this one.",
                         value=0, rarity=0, subtyp="Summon - Cacus")


class SheetMusic(Misc):
    """
    Base sheet music item  TODO
    """

    def __init__(self, name, description, value, rarity, subtyp):
        super().__init__(name, description, value, rarity, subtyp)


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
            'Hammer': [Sledgehammer, Maul, EarthHammer, GreatMaul, Streithammer]}},
    'OffHand': {
        'Shield': [Buckler, Aspis, Targe, Glagwa, KiteShield, Pavise, Svalinn], 
        'Tome': [Book, TomeKnowledge, Grimoire, BookShadows, DragonRouge, Vedas, Necronomicon],
        'Rod': [DowsingRod, ScepterIfrit, GaiasBranch, Zephyruswand]},
    'Armor': {
        'Cloth': [Tunic, ClothCloak, SilverCloak, GoldCloak, CloakEnchantment, WizardRobe, Tarnkappe],
        'Light': [PaddedArmor, LeatherArmor, Cuirboulli, StuddedLeather, StuddedCuirboulli, MithrilCoat],
        'Medium': [HideArmor, ChainShirt, ScaleMail, Breastplate, HalfPlate, Kusari],
        'Heavy': [RingMail, ChainMail, Splint, PlateMail, FullPlate, Maximilian]},
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
        'Scroll': [BlessScroll, SleepScroll, FireScroll, IceScroll, ElectricScroll, WaterScroll,
                   EarthScroll, WindScroll, ShadowScroll, HolyScroll, CleanseScroll, BoostScroll,
                   ShellScroll, SilenceScroll, DispelScroll, DeathScroll, SanctuaryScroll, UltimaScroll]}
}
