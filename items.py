###########################################
""" item manager """

# Imports
import time
import random
from dataclasses import dataclass

import abilities


# Functions
def random_item(z, typ=None, subtyp=None):
    """
    Returns a random item based on the given integer.
    """

    def mod_chance(chances, z):
        lst = list(range(1, z+1))
        lst.extend([lst[-1]]*(len(chances)-len(lst)))
        mod_lst = list(zip(chances, lst))
        return [x*y for x, y in mod_lst]

    if typ is None and subtyp is not None:
        raise TypeError("If subtyp is given, typ must also be given.")

    while True:
        rand_group = typ if typ else random.choice(list(items_dict.keys()))
        rand_type = subtyp if subtyp else random.choice(list(items_dict[rand_group].keys()))
        
        items = items_dict[rand_group][rand_type]
        item_rarities = [item().rarity for item in items]
        chances = [rarity / sum(item_rarities) for rarity in item_rarities]

        # increase chance of rarer items as z increases
        chances = mod_chance(chances, z)
        selected_item = random.choices(items, chances)[0]
        
        if chances[items.index(selected_item)] > random.random():
            return selected_item


def remove(typ):
    typ_dict = {'Weapon': NoWeapon, 'OffHand': NoOffHand, 'Armor': NoArmor, 'Pendant': NoPendant, 'Ring': NoRing}
    return typ_dict[typ]


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
        self.description = description
        self.value = value
        self.rarity = rarity
        self.subtyp = subtyp
        self.weight = 0
        self.restriction = []
        self.ultimate = False

    def __str__(self):
        return f"\n=====\n{self.name}\n=====\n{self.description}\n=====\n"

    def use(self, user, target=None, tile=None):
        return True


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

    def __str__(self):
        return (f"\n=====\n{self.name}\n=====\n{self.description}\nType: {self.subtyp}\n{self.handed}-handed\n"
                f"Damage: {self.damage}\nCritical Chance: {self.crit * 100}%\nWeight: {self.weight}\n=====\n")

    def special_effect(self, wielder, target, damage=0, crit=1):
        pass


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
        return (f"\n=====\n{self.name}\n=====\n{self.description}\nType: {self.subtyp}\nArmor: {self.armor}\n"
               f"Weight: {self.weight}\n=====\n")

    def special_effect(self, wearer, attacker):
        pass


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
            return (f"\n=====\n{self.name}\n=====\n{self.description}\nType: {self.subtyp}\nBlock: "
                    f"{int(self.mod * 100)}%\nWeight: {self.weight}\n=====\n")
        return (f"\n=====\n{self.name}\n=====\n{self.description}\nType: {self.subtyp}\n"
                f"Spell Damage Mod: {self.mod}\nWeight: {self.weight}\n=====\n")


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
        return f"\n=====\n{self.name}\n=====\n{self.description}\nMod: {self.mod}\nWeight: {self.weight}\n=====\n"



class Potion(Item):
    """
    typ: the item type; 'Potion' for this class
    """

    def __init__(self, name, description, value, rarity, subtyp):
        super().__init__(name, description, value, rarity, subtyp)
        self.typ = "Potion"
        self.weight = 0.1

    def __str__(self):
        return f"\n=====\n{self.name}\n=====\n{self.description}\nWeight: {self.weight}\n=====\n"
    

class Misc(Item):
    """
    typ: the item type; 'Misc' for this class
    """

    def __init__(self, name, description, value, rarity, subtyp):
        super().__init__(name, description, value, rarity, subtyp)
        self.typ = "Misc"


# One-handed weapons
class NoWeapon(Weapon):

    def __init__(self):
        super().__init__(name="Bare Hands", description="Nothing but good ol' lefty and righty.",
                         value=0, rarity=0, damage=0, crit=0, handed=1, subtyp='None', unequip=True,
                         off=True)


class BrassKnuckles(Weapon):

    def __init__(self):
        super().__init__(name="Brass Knuckles", description="Brass knuckles are pieces of metal shaped to fit around "
                                                            "the knuckles to add weight during hand-to-hand combat.",
                         value=2000, rarity=0.8, damage=3, crit=0.1, handed=1, subtyp='Fist', unequip=False,
                         off=True)
        self.weight = 1


class Cestus(Weapon):

    def __init__(self):
        super().__init__(name="Cestus", description="A cestus is a battle glove that is typically used in gladiatorial "
                                                    "events.",
                         value=7500, rarity=0.5, damage=4, crit=0.15, handed=1, subtyp='Fist', unequip=False,
                         off=True)
        self.weight = 1


class BattleGauntlet(Weapon):

    def __init__(self):
        super().__init__(name="Battle Gauntlet", description="A battle gauntlet is a type of glove that protects the "
                                                             "hand and wrist of a combatant, constructed with metal "
                                                             "platings to inflict additional damage.",
                         value=10000, rarity=0.4, damage=6, crit=0.2, handed=1, subtyp='Fist', unequip=False,
                         off=True)
        self.weight = 3


class BaghNahk(Weapon):

    def __init__(self):
        super().__init__(name="Bagh Nahk", description="The bagh nahk is a 'fist-load, claw-like' dagger designed to "
                                                       "fit over the knuckles or be concealed under and against the "
                                                       "palm.",
                         value=30000, rarity=0.25, damage=8, crit=0.25, handed=1, subtyp='Fist', unequip=False,
                         off=True)
        self.weight = 1


class GodsHand(Weapon):
    """
    Ultimate weapon; deals additional holy damage that won't heal even if the enemy would normally heal with holy damage
    """

    def __init__(self):
        super().__init__(name="God's Hand", description="With the appearance of an ordinary white glove, this weapon is"
                                                        " said to be imbued with the power of God.",
                         value=0, rarity=0, damage=10, crit=0.33, handed=1, subtyp='Fist', unequip=False,
                         off=True)
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Holy')
        damage = int(random.randint(damage // 2, damage) * (1 - resist))
        if damage > 0:
            print(f"Holy light burns {target.name}, dealing {damage} additional holy damage.")
            target.health.current -= damage


class Dirk(Weapon):

    def __init__(self):
        super().__init__(name="Dirk", description="A dirk is a long bladed thrusting dagger with a smooth jumpshot.",
                         value=125, rarity=0.95, damage=1, crit=0.15, handed=1, subtyp='Dagger', unequip=False,
                         off=True)
        self.weight = 2


class Baselard(Weapon):

    def __init__(self):
        super().__init__(name="Baselard", description="A baselard is a short bladed weapon with an H-shaped hilt.",
                         value=1500, rarity=0.8, damage=3, crit=0.2, handed=1, subtyp='Dagger', unequip=False,
                         off=True)
        self.weight = 3


class Kris(Weapon):

    def __init__(self):
        super().__init__(name="Kris", description="A Kris is an asymmetrical dagger with distinctive blade-patterning "
                                                  "achieved through alternating laminations of iron and nickelous iron,"
                                                  " easily identified by its distinct wavy blade.",
                         value=5000, rarity=0.6, damage=5, crit=0.25, handed=1, subtyp='Dagger', unequip=False,
                         off=True)
        self.weight = 3


class Rondel(Weapon):

    def __init__(self):
        super().__init__(name="Rondel", description="A type of dagger with a stiff-blade, named for the round hand "
                                                    "guard and round or spherical pommel.",
                         value=8000, rarity=0.5, damage=8, crit=0.33, handed=1, subtyp='Dagger', unequip=False,
                         off=True)
        self.weight = 3


class Kukri(Weapon):

    def __init__(self):
        super().__init__(name="Kukri", description="A kukri is a type of dagger with a distinct recurve in its blade.",
                         value=20000, rarity=0.25, damage=10, crit=0.4, handed=1, subtyp='Dagger', unequip=False,
                         off=True)
        self.weight = 4


class Carnwennan(Weapon):
    """
    Ultimate weapon; chance to stun target on critical
    """

    def __init__(self):
        super().__init__(name="Carnwennan", description="King Arthur's dagger, sometimes described to shroud the user "
                                                        "in shadow.",
                         value=0, rarity=0, damage=15, crit=0.5, handed=1, subtyp='Dagger', unequip=False,
                         off=True)
        self.weight = 2
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if crit > 1:
            if random.randint(wielder.stats.dex // 2, wielder.stats.dex) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                duration = max(1, wielder.stats.dex // 10)
                target.status_effects['Stun'].active = True
                target.status_effects['Stun'].duration = duration
                print(f"{target.name} is stunned for {duration} turns.")


class Rapier(Weapon):

    def __init__(self):
        super().__init__(name="Rapier", description="A rapier is a slender and sharply pointed two-edged blade with a "
                                                    "protective hilt.",
                         value=125, rarity=0.95, damage=2, crit=0.05, handed=1, subtyp='Sword', unequip=False,
                         off=True)
        self.weight = 5


class Jian(Weapon):

    def __init__(self):
        super().__init__(name="Jian", description="A jian is a double-edged straight sword with a guard that protects "
                                                  "the wielder from opposing blades,",
                         value=2000, rarity=0.8, damage=5, crit=0.1, handed=1, subtyp='Sword', unequip=False,
                         off=True)
        self.weight = 6


class Talwar(Weapon):

    def __init__(self):
        super().__init__(name="Talwar", description="A talwar is curved, single-edged sword with an iron disc hilt and "
                                                    "knucklebow, and a fullered blade.",
                         value=5500, rarity=0.55, damage=7, crit=0.15, handed=1, subtyp='Sword', unequip=False,
                         off=True)
        self.weight = 8


class Shamshir(Weapon):

    def __init__(self):
        super().__init__(name="Shamshir", description="A shamshir has a radically curved blade featuring a slim blade "
                                                      "with almost no taper until the very tip.",
                         value=10000, rarity=0.4, damage=10, crit=0.2, handed=1, subtyp='Sword', unequip=False,
                         off=True)
        self.weight = 10


class Khopesh(Weapon):

    def __init__(self):
        super().__init__(name="Khopesh", description="A khopesh is a sickle-shaped sword that evolved from battle axes"
                                                     " and that can be used to disarm an opponent.",
                         value=22000, rarity=0.25, damage=12, crit=0.25, handed=1, subtyp='Sword', unequip=False,
                         off=True)
        self.weight = 10

    def special_effect(self, wielder, target, damage=0, crit=1):
        if not target.status_effects['Disarm'].active:
            if target.equipment['Weapon']().subtyp not in ["Natural", "None"]:
                chance = target.check_mod('luck', luck_factor=10)
                if random.randint(wielder.stats.strength // 2, wielder.stats.strength) \
                        > random.randint(target.stats.dex // 2, target.stats.dex) + chance:
                    target.status_effects['Disarm'].active = True
                    target.status_effects['Disarm'].duration = wielder.stats.strength // 10
                    print(f"{target.name} is disarmed.")


class Excalibur(Weapon):
    """
    Ultimate weapon; chance on crit to add a bleed on target
    """

    def __init__(self):
        super().__init__(name="Excalibur", description="The legendary sword of King Arthur, bestowed upon him by the "
                                                       "Lady of the Lake.",
                         value=0, rarity=0, damage=18, crit=0.33, handed=1, subtyp='Sword', unequip=False,
                         off=True)
        self.weight = 8
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if crit > 1:
            if random.randint((wielder.stats.strength // 2), wielder.stats.strength) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                if not target.status_effects['Bleed'].active:
                    print(f"{target.name} is bleeding.")
                duration = max(1, wielder.stats.strength // 10)
                bleed_dmg = max(wielder.stats.strength // 2, damage)
                target.status_effects['Bleed'].active = True
                target.status_effects['Bleed'].duration = max(duration, target.status_effects['Bleed'].duration)
                target.status_effects['Bleed'].extra = max(bleed_dmg, target.status_effects['Bleed'].extra)


class Mace(Weapon):

    def __init__(self):
        super().__init__(name="Mace", description="A mace is a blunt weapon, a type of club or virge that uses a heavy"
                                                  " head on the end of a handle to deliver powerful strikes. A mace "
                                                  "typically consists of a strong, heavy, wooden or metal shaft, often"
                                                  " reinforced with metal, featuring a head made of iron.",
                         value=2000, rarity=0.8, damage=6, crit=0.025, handed=1, subtyp='Club', unequip=False,
                         off=True)
        self.weight = 6


class WarHammer(Weapon):

    def __init__(self):
        super().__init__(name="War Hammer", description="A war hammer is a club with a head featuring both a blunt end "
                                                        "and a spike on the other end.",
                         value=4500, rarity=0.6, damage=8, crit=0.05, handed=1, subtyp='Club', unequip=False,
                         off=True)
        self.weight = 10


class Pernach(Weapon):

    def __init__(self):
        super().__init__(name="Pernach", description="A pernach is a type of flanged mace used to penetrate even heavy "
                                                     "armor plating.",
                         value=10000, rarity=0.45, damage=12, crit=0.1, handed=1, subtyp='Club', unequip=False,
                         off=True)
        self.weight = 10


class Morgenstern(Weapon):

    def __init__(self):
        super().__init__(name="Morgenstern", description="A morgenstern, or morning star, is a club-like weapon "
                                                         "consisting of a shaft with an attached ball adorned with "
                                                         "several spikes.",
                         value=21000, rarity=0.25, damage=14, crit=0.15, handed=1, subtyp='Club', unequip=False,
                         off=True)
        self.weight = 10


class Mjolnir(Weapon):
    """
    Ultimate weapon; chance to stun on a critical hit based on strength
    """

    def __init__(self):
        super().__init__(name="Mjolnir", description="Mjolnir, wielded by the Thunder god Thor, is depicted in Norse "
                                                     "mythology as one of the most fearsome and powerful weapons in "
                                                     "existence, capable of leveling mountains.",
                         value=0, rarity=0, damage=20, crit=0.25, handed=1, subtyp='Club', unequip=False,
                         off=True)
        self.weight = 8
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if not target.status_effects['Stun'].active:
            if crit > 1:
                if random.randint(wielder.stats.strength // 2, wielder.stats.strength) \
                        > random.randint(target.stats.con // 2, target.stats.con):
                    duration = max(1, wielder.stats.strength // 10)
                    target.status_effects['Stun'].active = True
                    target.status_effects['Stun'].duration = duration
                    print(f"{target.name} is stunned for {duration} turns.")


class Tanto(Weapon):

    def __init__(self):
        super().__init__(name="Tanto", description="A tanto is a double-edged, straight blade, designed primarily as a "
                                                   "stabbing weapon, but the edge can be used for slashing as well.",
                         value=15000, rarity=0.4, damage=8, crit=0.33, handed=1, subtyp='Ninja Blade', unequip=False,
                         off=True)
        self.weight = 5
        self.restriction = ['Ninja']


class Wakizashi(Weapon):

    def __init__(self):
        super().__init__(name="Wakizashi", description="A wakizashi is a curved, single-edged blade with a narrow "
                                                       "cross-section, producing a deadly strike.",
                         value=65000, rarity=0.2, damage=12, crit=0.4, handed=1, subtyp='Ninja Blade', unequip=False,
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
                         value=0, rarity=0, damage=18, crit=0.5, handed=1, subtyp='Ninja Blade', unequip=False,
                         off=True)
        self.weight = 5
        self.restriction = ['Ninja']
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if crit > 1:
            resist = target.check_mod('resist', 'Death')
            if resist < 1:
                w_chance = wielder.check_mod('luck', luck_factor=10)
                t_chance = target.check_mod('luck', luck_factor=10)
                if random.randint(0, wielder.stats.dex) + w_chance > \
                        random.randint(target.stats.con // 2, target.stats.con) + t_chance:
                    print(f"The {self.name} blade rips the soul from {target.name} and they drop dead to the ground!")


# Two-handed weapons
class Bastard(Weapon):
    """

    """

    def __init__(self):
        super().__init__(name="Bastard Sword", description="The bastard sword, also referred to as a hand-and-a-half "
                                                           "sword, is a type of longsword that typically requires two "
                                                           "hands to wield but can be wielded in one if the need "
                                                           "arises.",
                         value=700, rarity=0.9, damage=5, crit=0.1, handed=2, subtyp='Longsword', unequip=False,
                         off=False)
        self.weight = 14


class Claymore(Weapon):
    """

    """

    def __init__(self):
        super().__init__(name="Claymore", description="Coming from the Gaelic meaning 'Great Sword', the claymore is a "
                                                      "two-handed sword featuring quillons (crossguards between the "
                                                      "hilt and the blade) are angled in towards the blade and end in "
                                                      "quatrefoils, and a tongue of metal protrudes down either side of"
                                                      " the blade.",
                         value=4200, rarity=0.66, damage=9, crit=0.15, handed=2, subtyp='Longsword', unequip=False,
                         off=False)
        self.weight = 20


class Zweihander(Weapon):
    """

    """

    def __init__(self):
        super().__init__(name="Zweihander", description="German for 'two-handed', the zweihander is a double-edged, "
                                                        "straight blade with a cruciform hilt.",
                         value=9500, rarity=0.45, damage=11, crit=0.2, handed=2, subtyp='Longsword', unequip=False,
                         off=False)
        self.weight = 18


class Changdao(Weapon):
    """

    """

    def __init__(self):
        super().__init__(name="Changdao", description="A single-edged two-hander over seven feet long, roughly "
                                                      "translates to 'long saber'.",
                         value=16000, rarity=0.3, damage=13, crit=0.25, handed=2, subtyp='Longsword', unequip=False,
                         off=False)
        self.weight = 16


class Flamberge(Weapon):
    """

    """

    def __init__(self):
        super().__init__(name="Flamberge", description="The flamberge is a type of flame-bladed sword featuring a "
                                                       "signature wavy blade.",
                         value=31000, rarity=0.2, damage=15, crit=0.33, handed=2, subtyp='Longsword', unequip=False,
                         off=False)
        self.weight = 18


class Executioner(Weapon):
    """

    """

    def __init__(self):
        super().__init__(name="Executioner's Blade", description="Designed specifically for decapitation, the "
                                                                 "Executioner's Blade is a large, two-handed sword "
                                                                 "with a broad blade that is highly efficient at "
                                                                 "killing.",
                         value=0, rarity=0, damage=21, crit=0.4, handed=2, subtyp='Longsword', unequip=False,
                         off=False)
        self.weight = 20
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if crit > 1:
            resist = target.check_mod('resist', 'Death')
            if resist < 1:
                w_chance = wielder.check_mod('luck', luck_factor=10)
                t_chance = target.check_mod('luck', luck_factor=10)
                if random.randint(0, wielder.stats.strength) + w_chance > \
                        random.randint(target.stats.con // 2, target.stats.con) + t_chance:
                    print(f"The {self.name} decapitates {target.name} and they drop dead to the ground!")


class Mattock(Weapon):
    """

    """

    def __init__(self):
        super().__init__(name="Mattock", description="A mattock is a hand tool used for digging, prying, and chopping, "
                                                     "similar to the pickaxe.",
                         value=800, rarity=0.9, damage=6, crit=0.1, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)
        self.weight = 15


class Broadaxe(Weapon):

    def __init__(self):
        super().__init__(name="Broadaxe", description="A broadaxe is broad-headed axe with a large flared blade.",
                         value=4500, rarity=0.66, damage=10, crit=0.15, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)
        self.weight = 17


class DoubleAxe(Weapon):

    def __init__(self):
        super().__init__(name="Double Axe", description="The double axe is basically a broadaxe but with a blade on "
                                                        "each side of the axehead.",
                         value=10000, rarity=0.4, damage=12, crit=0.2, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)
        self.weight = 22


class Parashu(Weapon):

    def __init__(self):
        super().__init__(name="Parashu", description="A parashu is a single-bladed battle axe with an arced edge "
                                                     "extending beyond 180 degrees and paired with a spike on the non-"
                                                     "cutting edge.",
                         value=15000, rarity=0.3, damage=14, crit=0.25, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)
        self.weight = 20


class Greataxe(Weapon):

    def __init__(self):
        super().__init__(name="Greataxe", description="A greataxe is a scaled up version of the double axe with greater"
                                                      " mass and killing power.",
                         value=30000, rarity=0.2, damage=16, crit=0.3, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)
        self.weight = 26


class Jarnbjorn(Weapon):
    """
    Ultimate weapon; chance on critical hit to cause bleed
    """

    def __init__(self):
        super().__init__(name="Jarnbjorn", description="Legendary axe of Thor Odinson. Old Norse for \"iron bear\".",
                         value=0, rarity=0, damage=23, crit=0.33, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)
        self.weight = 20
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if crit > 1:
            if random.randint((wielder.stats.strength // 2), wielder.stats.strength) \
                    > random.randint(target.stats.con // 2, target.stats.con):
                if not target.status_effects['Bleed'].active:
                    print(f"{target.name} is bleeding.")
                duration = max(1, wielder.stats.strength // 10)
                bleed_dmg = max(wielder.stats.strength // 2, damage)
                target.status_effects['Bleed'].active = True
                target.status_effects['Bleed'].duration = max(duration, target.status_effects['Bleed'].duration)
                target.status_effects['Bleed'].extra = max(bleed_dmg, target.status_effects['Bleed'].extra)


class Framea(Weapon):

    def __init__(self):
        super().__init__(name="Framea", description="A type of spear used by the ancient Germanic tribes and is a versatile "
                                                    "weapon used in both melee combat and as a projectile.",
                         value=800, rarity=0.9, damage=5, crit=0.15, handed=2, subtyp='Polearm', unequip=False,
                         off=False)
        self.weight = 10


class Partisan(Weapon):

    def __init__(self):
        super().__init__(name="Partisan", description="A partisan consists of a spearhead mounted on a long wooden "
                                                      "shaft, with protrusions on the sides which aid in parrying "
                                                      "sword thrusts.",
                         value=3500, rarity=0.7, damage=9, crit=0.2, handed=2, subtyp='Polearm', unequip=False,
                         off=False)
        self.weight = 12


class Halberd(Weapon):

    def __init__(self):
        super().__init__(name="Halberd", description="A halberd is a two-handed pole weapon consisting of an axe blade "
                                                     "topped with a spike mounted on a long shaft.",
                         value=9000, rarity=0.45, damage=11, crit=0.25, handed=2, subtyp='Polearm', unequip=False,
                         off=False)
        self.weight = 15


class Naginata(Weapon):

    def __init__(self):
        super().__init__(name="Naginata", description="A naginata consists of a wooden or metal pole with a curved "
                                                      "single-edged blade on the end that has a round handguard between"
                                                      " the blade and shaft.",
                         value=13000, rarity=0.3, damage=13, crit=0.3, handed=2, subtyp='Polearm', unequip=False,
                         off=False)
        self.weight = 14


class Trident(Weapon):

    def __init__(self):
        super().__init__(name="Trident", description="A trident is a 3-pronged spear, the preferred weapon of the Sea"
                                                     " god Poseidon.",
                         value=26000, rarity=0.2, damage=15, crit=0.33, handed=2, subtyp='Polearm', unequip=False,
                         off=False)
        self.weight = 16


class Gungnir(Weapon):
    """
    Ultimate weapon; ignores armor
    """

    def __init__(self):
        super().__init__(name="Gungnir", description="Legendary spear of the god Odin. Old Norse for \"swaying one\".",
                         value=0, rarity=0, damage=22, crit=0.4, handed=2, subtyp='Polearm', unequip=False,
                         off=False)
        self.weight = 14
        self.ignore = True
        self.ultimate = True


class Quarterstaff(Weapon):

    def __init__(self):
        super().__init__(name="Quarterstaff", description="A quarterstaff is a shaft of hardwood about eight feet long"
                                                          " fitted with metal tips on each end.",
                         value=250, rarity=0.95, damage=2, crit=0.025, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 6


class Baston(Weapon):

    def __init__(self):
        super().__init__(name="Baston", description="A baston is a long, light, and flexible staff weapon that is ideal"
                                                    " for speed and precision.",
                         value=800, rarity=0.9, damage=3, crit=0.05, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 6


class IronshodStaff(Weapon):

    def __init__(self):
        super().__init__(name="Ironshod Staff", description="An iron walking stick, making it ideal for striking.",
                         value=2500, rarity=0.75, damage=6, crit=0.1, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 10


class SerpentStaff(Weapon):

    def __init__(self):
        super().__init__(name="Serpent Staff", description="A magic staff, shaped to appear as a snake.",
                         value=5000, rarity=0.6, damage=10, crit=0.12, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 8


class HolyStaff(Weapon):

    def __init__(self):
        super().__init__(name="Holy Staff", description="A staff that emits a holy light. Only equipable by priests"
                                                        " and archbishops.",
                         value=7500, rarity=0.5, damage=11, crit=0.15, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 6
        self.restriction = ['Priest', 'Archbishop']

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Holy')
        damage = int(damage * (1 - resist))
        if damage > 0:
            print(f"The {self.name} deals {damage} additional holy damage to {target.name}.")
        elif damage < 0:
            print(f"{target.name} absorbs the holy damage from the {self.name}.")
        target.health.current -= damage


class RuneStaff(Weapon):

    def __init__(self):
        super().__init__(name="Rune Staff", description="A wooden staff with a magical rune embedded in the handle.",
                         value=10000, rarity=0.4, damage=12, crit=0.18, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 7


class MithrilshodStaff(Weapon):

    def __init__(self):
        super().__init__(name="Mithrilshod Staff", description="A mithril walking stick, making it ideal for striking.",
                         value=20000, rarity=0.25, damage=14, crit=0.2, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 8


class DragonStaff(Weapon):
    """
    Ultimate weapon; regen mana based on damage
    """

    def __init__(self):
        super().__init__(name="Dragon Staff", description="A magic staff, shaped to appear as a dragon.",
                         value=0, rarity=0, damage=20, crit=0.3, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 9
        self.restriction = ['Berserker', 'Wizard', 'Necromancer', 'Master Monk', 'Lycan', 'Geomancer', 'Soulcatcher']
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        mana_heal = random.randint(damage // 2, damage)
        if wielder.mana.current + mana_heal > wielder.mana.max:
            mana_heal = wielder.mana.max - wielder.mana.current
        if mana_heal > 0:
            wielder.mana.current += mana_heal
            print(f"{wielder.name}'s mana is regenerated by {mana_heal}.")


class PrincessGuard(Weapon):
    """
    Ultimate weapon; regen health based on damage
    """

    def __init__(self):
        super().__init__(name="Princess Guard", description="A mythical staff from another world.",
                         value=0, rarity=0, damage=21, crit=0.25, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.weight = 4
        self.restriction = ['Archbishop']
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        heal = random.randint(damage // 2, damage)
        if wielder.health.current + heal > wielder.health.max:
            heal = wielder.health.max - wielder.health.current
        if heal > 0:
            wielder.mana.current += heal
            print(f"{wielder.name}'s heal is regenerated by {heal}.")


class Sledgehammer(Weapon):

    def __init__(self):
        super().__init__(name="Sledgehammer", description="A sledgehammer is a tool with a large, flat, metal head, "
                                                          "attached to a long handle that gathers momentum during a "
                                                          "swing to apply a large force upon the target.",
                         value=800, rarity=0.9, damage=6, crit=0.1, handed=2, subtyp='Hammer', unequip=False,
                         off=False)
        self.weight = 20


class Maul(Weapon):

    def __init__(self):
        super().__init__(name="Spike Maul", description="A spike maul is similar to a sledgehammer except for having a"
                                                        " more narrow face for increased damage.",
                         value=5000, rarity=0.6, damage=14, crit=0.12, handed=2, subtyp='Hammer', unequip=False,
                         off=False)
        self.weight = 22


class EarthHammer(Weapon):

    def __init__(self):
        super().__init__(name="Earth Hammer", description="A large, 2-handed hammer infused with the power of Gaia.",
                         value=12000, rarity=0.4, damage=18, crit=0.15, handed=2, subtyp='Hammer', unequip=False,
                         off=False)
        self.weight = 20

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Earth')
        damage = int(damage * (1 - resist))
        if damage > 0:
            print(f"The {self.name} deals {damage} additional earth damage to {target.name}.")
        elif damage < 0:
            print(f"{target.name} absorbs the earth damage from the {self.name}.")
        target.health.current -= damage


class GreatMaul(Weapon):

    def __init__(self):
        super().__init__(name="Great Maul", description="A great maul looks similar to a sledgehammer but is "
                                                        "significantly larger in all aspects.",
                         value=27000, rarity=0.2, damage=20, crit=0.2, handed=2, subtyp='Hammer', unequip=False,
                         off=False)
        self.weight = 30


class Skullcrusher(Weapon):
    """
    Ultimate weapon; chance to stun on critical based on strength
    """

    def __init__(self):
        super().__init__(name="Skullcrusher", description="A massive hammer with the power to pulverize an enemy's "
                                                          "skull to powder.",
                         value=0, rarity=0, damage=26, crit=0.25, handed=2, subtyp='Hammer', unequip=False,
                         off=False)
        self.weight = 25
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if not target.status_effects['Stun'].active:
            if crit > 1:
                if random.randint(wielder.stats.strength // 2, wielder.stats.strength) \
                        > random.randint(target.stats.con // 2, target.stats.con):
                    duration = max(1, wielder.stats.strength // 10)
                    target.status_effects['Stun'].active = True
                    target.status_effects['Stun'].duration = duration
                    print(f"{target.name} is stunned.")


class NoArmor(Armor):

    def __init__(self):
        super().__init__(name="No Armor", description="No armor equipped.", value=0, rarity=0, armor=0,
                         subtyp='None', unequip=True)


class Tunic(Armor):

    def __init__(self):
        super().__init__(name="Tunic", description="A close-fitting short coat as part of a uniform, especially a "
                                                   "police or military uniform.",
                         value=60, rarity=0.95, armor=1, subtyp='Cloth', unequip=False)
        self.weight = 2


class ClothCloak(Armor):

    def __init__(self):
        super().__init__(name="Cloth Cloak", description="An outdoor cloth garment, typically sleeveless, that hangs "
                                                         "loosely from the shoulders.",
                         value=200, rarity=0.8, armor=2, subtyp='Cloth', unequip=False)
        self.weight = 2


class SilverCloak(Armor):

    def __init__(self):
        super().__init__(name="Silver Cloak", description="A cloak weaved with strands of silver to improve protective "
                                                          "power.",
                         value=2500, rarity=0.66, armor=3, subtyp='Cloth', unequip=False)
        self.weight = 3


class GoldCloak(Armor):

    def __init__(self):
        super().__init__(name="Gold Cloak", description="A cloak weaved with strands of gold to improve protective "
                                                        "power.",
                         value=7000, rarity=0.5, armor=5, subtyp='Cloth', unequip=False)
        self.weight = 4


class CloakEnchantment(Armor):

    def __init__(self):
        super().__init__(name="Cloak of Enchantment", description="A magical cloak that shields the wearer from all "
                                                                  "forms of attack.",
                         value=15000, rarity=0.4, armor=7, subtyp='Cloth', unequip=False)
        self.weight = 3


class WizardRobe(Armor):

    def __init__(self):
        super().__init__(name="Wizard's Robe", description="A knee-length, long-sleeved robe with an impressive hood "
                                                           "designed to add a mysterious feel to magic users.",
                         value=25000, rarity=0.25, armor=10, subtyp='Cloth', unequip=False)
        self.weight = 4


class MerlinRobe(Armor):

    def __init__(self):
        super().__init__(name="Robes of Merlin", description="The enchanted robes of Merlin the enchanter.",
                         value=75000, rarity=0.1, armor=12, subtyp='Cloth', unequip=False)
        self.weight = 2


class PaddedArmor(Armor):

    def __init__(self):
        super().__init__(name="Padded Armor", description="Consists of quilted layers of cloth and batting to provide"
                                                          " some protection from attack.",
                         value=75, rarity=0.95, armor=2, subtyp='Light', unequip=False)
        self.weight = 4


class LeatherArmor(Armor):

    def __init__(self):
        super().__init__(name="Leather Armor", description="A protective covering made of animal hide, boiled to make "
                                                           "it tough and rigid and worn over the torso to protect it "
                                                           "from injury.",
                         value=600, rarity=0.75, armor=3, subtyp='Light', unequip=False)
        self.weight = 5


class Cuirboulli(Armor):

    def __init__(self):
        super().__init__(name="Cuirboulli", description="French for \"boiled leather\", this armor has increased "
                                                        "rigidity for add protection",
                         value=3000, rarity=0.5, armor=4, subtyp='Light', unequip=False)
        self.weight = 6


class StuddedLeather(Armor):

    def __init__(self):
        super().__init__(name="Studded Leather", description="Leather armor embedded with iron studs to improve "
                                                             "defensive capabilities.",
                         value=12000, rarity=0.4, armor=8, subtyp='Light', unequip=False)
        self.weight = 7


class StuddedCuirboulli(Armor):

    def __init__(self):
        super().__init__(name="Studded Cuirboulli", description="Boiled leather armor embedded with iron studs to "
                                                                "improve defensive capabilities.",
                         value=28000, rarity=0.25, armor=12, subtyp='Light', unequip=False)
        self.weight = 8


class DragonHide(Armor):

    def __init__(self):
        super().__init__(name="Dragon Hide", description="Hide armor made from the scales of a red dragon, "
                                                         "inconceivably light for this type of armor.",
                         value=80000, rarity=0.1, armor=16, subtyp='Light', unequip=False)
        self.weight = 10


class HideArmor(Armor):

    def __init__(self):
        super().__init__(name="Hide Armor", description="A crude armor made from thick furs and pelts.",
                         value=100, rarity=0.95, armor=3, subtyp='Medium', unequip=False)
        self.weight = 9


class ChainShirt(Armor):

    def __init__(self):
        super().__init__(name="Chain Shirt", description="A type of armor consisting of small metal rings linked "
                                                         "together in a pattern to form a mesh.",
                         value=800, rarity=0.75, armor=4, subtyp='Medium', unequip=False)
        self.weight = 12


class ScaleMail(Armor):

    def __init__(self):
        super().__init__(name="Scale Mail", description="Armor consisting of a coat and leggings of leather covered"
                                                        " with overlapping pieces of metal, mimicking the scales of a "
                                                        "fish.",
                         value=4000, rarity=0.5, armor=5, subtyp='Medium', unequip=False)
        self.weight = 10


class Breastplate(Armor):

    def __init__(self):
        super().__init__(name="Breastplate", description="Armor consisting of a fitted metal chest piece worn with "
                                                         "supple leather. Although it leaves the legs and arms "
                                                         "relatively unprotected, this armor provides good protection "
                                                         "for the wearer’s vital organs while leaving the wearer "
                                                         "relatively unencumbered.",
                         value=14000, rarity=0.4, armor=9, subtyp='Medium', unequip=False)
        self.weight = 15


class HalfPlate(Armor):

    def __init__(self):
        super().__init__(name="Half Plate", description="Armor consisting of shaped metal plates that cover most of the"
                                                        " wearer’s body. It does not include leg Protection beyond "
                                                        "simple greaves that are attached with leather straps.",
                         value=30000, rarity=0.25, armor=13, subtyp='Medium', unequip=False)
        self.weight = 20


class Aegis(Armor):

    def __init__(self):
        super().__init__(name="Aegis Breastplate", description="The breastplate of Zeus, emboldened with a bolt of "
                                                               "lightning.",
                         value=90000, rarity=0.1, armor=18, subtyp='Medium', unequip=False)
        self.weight = 18


class RingMail(Armor):

    def __init__(self):
        super().__init__(name="Ring Mail", description="Leather armor with heavy rings sewn into it. The rings help "
                                                       "reinforce the armor against blows from Swords and axes.",
                         value=200, rarity=0.95, armor=4, subtyp='Heavy', unequip=False)
        self.weight = 15


class ChainMail(Armor):

    def __init__(self):
        super().__init__(name="Chain Mail", description="Made of interlocking metal rings, includes a layer of quilted "
                                                        "fabric worn underneath the mail to prevent chafing and to "
                                                        "cushion the impact of blows. The suit includes gauntlets.",
                         value=1000, rarity=0.75, armor=5, subtyp='Heavy', unequip=False)
        self.weight = 18


class Splint(Armor):

    def __init__(self):
        super().__init__(name="Splint Mail", description="Armor made of narrow vertical strips of metal riveted to a "
                                                         "backing of leather that is worn over cloth padding. Flexible "
                                                         "chain mail protects the joints.",
                         value=6000, rarity=0.5, armor=7, subtyp='Heavy', unequip=False)
        self.weight = 20


class PlateMail(Armor):

    def __init__(self):
        super().__init__(name="Plate Mail", description="Armor consisting of shaped, interlocking metal plates to "
                                                        "cover most of the body.",
                         value=20000, rarity=0.4, armor=10, subtyp='Heavy', unequip=False)
        self.weight = 25


class FullPlate(Armor):

    def __init__(self):
        super().__init__(name="Full Plate", description="Armor consisting of shaped, interlocking metal plates to "
                                                        "cover the entire body. Full plate includes gauntlets, "
                                                        "heavy leather boots, a visored helmet, and thick layers of "
                                                        "padding underneath the armor. Buckles and straps distribute "
                                                        "the weight over the body.",
                         value=40000, rarity=0.25, armor=15, subtyp='Heavy', unequip=False)
        self.weight = 30


class Genji(Armor):

    def __init__(self):
        super().__init__(name="Genji Armor", description="Mythical armor crafted by an unknown master blacksmith and "
                                                         "embued with protective enchantments that allow the user to "
                                                         "shrug off damage.",
                         value=100000, rarity=0.1, armor=25, subtyp='Heavy', unequip=False)
        self.weight = 25


class NoOffHand(OffHand):

    def __init__(self):
        super().__init__(name="No Offhand", description="No off-hand equipped.", value=0, rarity=0, mod=0,
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
                         value=500, rarity=0.8, mod=0.15, subtyp='Shield', unequip=False)
        self.weight = 7


class Glagwa(OffHand):

    def __init__(self):
        super().__init__(name="Glagwa", description="A glagwa is a bell-shaped shield made from iron and covered with "
                                                    "leather for improved durability.",
                         value=2500, rarity=0.66, mod=0.2, subtyp='Shield', unequip=False)
        self.weight = 13


class KiteShield(OffHand):

    def __init__(self):
        super().__init__(name="Kite Shield", description="A kite shield is a large, almond-shaped shield rounded at the"
                                                         " top and curving down to a point or rounded point at the "
                                                         "bottom. The term \"kite shield\" is a reference to the "
                                                         "shield's unique shape, and is derived from its supposed "
                                                         "similarity to a flying kite.",
                         value=10000, rarity=0.5, mod=0.25, subtyp='Shield', unequip=False)
        self.weight = 15


class Pavise(OffHand):

    def __init__(self):
        super().__init__(name="Pavise", description="A pavise is an oblong shield similar to a tower shield that "
                                                    "features a spike at the bottom to hold it in place to provide full"
                                                    " body protection.",
                         value=25000, rarity=0.25, mod=0.3, subtyp='Shield', unequip=False)
        self.weight = 20


class MedusaShield(OffHand):

    def __init__(self):
        super().__init__(name="Medusa Shield", description="A shield that has been polished to resemble a mirror. Said"
                                                           " to be used to defeat the Gorgon Medusa. Reflects back some"
                                                           " magic.",
                         value=50000, rarity=0.1, mod=0.35, subtyp='Shield', unequip=False)
        self.weight = 8


class Book(OffHand):

    def __init__(self):
        super().__init__(name="Book", description="A book of notes taken during the character's apprenticeship.",
                         value=25, rarity=0.95, mod=2, subtyp='Tome', unequip=False)
        self.weight = 1


class TomeKnowledge(OffHand):

    def __init__(self):
        super().__init__(name="Tome of Knowledge", description="A tome containing secrets to enhancing spells.",
                         value=500, rarity=0.9, mod=5, subtyp='Tome', unequip=False)
        self.weight = 3


class Grimoire(OffHand):

    def __init__(self):
        super().__init__(name="Grimoire", description="A book of magic and invocations.",
                         value=2500, rarity=0.66, mod=7, subtyp='Tome', unequip=False)
        self.weight = 3


class BookShadows(OffHand):

    def __init__(self):
        super().__init__(name="Book of Shadows", description="The Book of Shadows is a book containing religious text "
                                                             "and instructions for magical rituals found within the "
                                                             "Neopagan religion of Wicca, and in many pagan practices.",
                         value=10000, rarity=0.5, mod=10, subtyp='Tome', unequip=False)
        self.weight = 2


class DragonRouge(OffHand):

    def __init__(self):
        super().__init__(name="Dragon Rouge", description="French for \"Red Dragon\", this mythical tome contains "
                                                          "ancient knowledge passed down through the ages.",
                         value=15000, rarity=0.4, mod=12, subtyp='Tome', unequip=False)
        self.weight = 4


class Vedas(OffHand):

    def __init__(self):
        super().__init__(name="Vedas", description="A large body of religious texts, consisting of some of the oldest "
                                                   "holy teachings.",
                         value=35000, rarity=0.25, mod=18, subtyp='Tome', unequip=False)
        self.weight = 4


class Necronomicon(OffHand):

    def __init__(self):
        super().__init__(name="Necronomicon", description="The Book of the Dead, a mystical grimoire written by an "
                                                          "unknown author.",
                         value=40000, rarity=0.1, mod=20, subtyp='Tome', unequip=False)
        self.weight = 6
        self.restriction = ['Warlock', 'Necromancer']


class Magus(OffHand):

    def __init__(self):
        super().__init__(name="Magus", description="A book of magical art written by a powerful wizard.",
                         value=75000, rarity=0.05, mod=30, subtyp='Tome', unequip=False)
        self.weight = 3


class NoRing(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="No Ring", description="No ring equipped.", value=0, rarity=0, mod="No Mod",
                         subtyp='None', unequip=True)


class IronRing(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Iron Ring", description="A ring that improves the wearer's defense.",
                         value=2000, rarity=0.8, mod="+2 Physical Defense", subtyp="Ring", unequip=False)
        self.weight = 0.1


class PowerRing(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Power Ring", description="A ring that improves the wearer's attack damage.",
                         value=5000, rarity=0.66, mod="+5 Physical Damage", subtyp="Ring", unequip=False)
        self.weight = 0.1


class AccuracyRing(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Accuracy Ring", description="A ring that improves the wearer's weapon accuracy by 25%.",
                         value=15000, rarity=0.5, mod="Accuracy", subtyp="Ring", unequip=False)
        self.weight = 0.1


class BarrierRing(Accessory):
    """
    Increases block chance, even without a shield
    """

    def __init__(self):
        super().__init__(name="Barrier Ring", description="A ring that increases the wearer's chance to block attacks, "
                                                          "even without having a shield equipped.",
                         value=16000, rarity=0.4, mod="Block", subtyp="Ring", unequip=False)
        self.weight = 0.1


class SteelRing(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Steel Ring", description="A ring that greatly improves the wearer's defense.",
                         value=18000, rarity=0.3, mod="+5 Physical Defense", subtyp="Ring", unequip=False)
        self.weight = 0.1


class MightRing(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Might Ring", description="A ring that greatly improves the wearer's attack damage.",
                         value=24000, rarity=0.25, mod="+10 Physical Damage", subtyp="Ring", unequip=False)
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
    """

    """

    def __init__(self):
        super().__init__(name="Titanium Ring", description="A ring that massively improves the wearer's defense.",
                         value=45000, rarity=0.1, mod="+10 Physical Defense", subtyp="Ring", unequip=False)
        self.weight = 0.1


class ForceRing(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Force Ring", description="A ring that massively improves the wearer's attack damage.",
                         value=50000, rarity=0.1, mod="+25 Physical Damage", subtyp="Ring", unequip=False)
        self.weight = 0.1


class ClassRing(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Class Ring", description="A ring that changes depending on the wearer's specialty.",
                         value=0, rarity=0, mod="Special", subtyp="Ring", unequip=False)
        self.weight = 0.1

    def class_mod(self, player_char):
        pass  # TODO


class NoPendant(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="No Pendant", description="No pendant equipped.", value=0, rarity=0, mod="No Mod",
                         subtyp="None", unequip=True)


class VisionPendant(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Pendant of Vision", description="A pendant that that gives information about the enemy.",
                         value=1200, rarity=0.9, mod="Vision", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class RubyAmulet(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Ruby Amulet", description="A ruby necklace that improves the wearer's magic damage.",
                         value=1800, rarity=0.75, mod="+5 Magic Defense", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class SilverPendant(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Silver Pendant", description="A silver-chained necklace that improves the wearer's magic"
                                                            " damage.",
                         value=8000, rarity=0.66, mod="+5 Magic Damage", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class AntidotePendant(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Antidote Pendant", description="Protects the wearer against the effects of poison.",
                         value=2500, rarity=0.7, mod="Poison", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class SapphireAmulet(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Sapphire Amulet", description="A sapphire necklace that greatly improves the wearer's "
                                                             "magic damage.",
                         value=16000, rarity=0.5, mod="+10 Magic Defense", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class GoldPendant(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Gold Pendant", description="A gold-chained necklace that greatly improves the wearer's "
                                                          "magic damage.",
                         value=22000, rarity=0.4, mod="+10 Magic Damage", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class GorgonPendant(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Gorgon Pendant", description="Made from the scale of a Gorgon, this ring protects the "
                                                            "wearer against petrification.",
                         value=20000, rarity=0.4, mod="Stone", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class DharmaPendant(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Dharma Pendant", description="No need to fear the reaper while wearing this ring, giving"
                                                            " the wearer immunity against instant death.",
                         value=25000, rarity=0.25, mod="Death", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class LevitationNecklace(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Levitation Necklace", description="Gives the wearer the ability to fly, making them "
                                                                 "harder to hit and immunity from Earth spells. The "
                                                                 "downfall is that Wind spells will hurt more.",
                         value=30000, rarity=0.25, mod="Flying", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class InvisibilityAmulet(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Invisibility Amulet", description="Makes the wearer invisible and harder to hit.",
                         value=50000, rarity=0.1, mod="Invisible", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class DiamondAmulet(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Diamond Amulet", description="A diamond necklace that massively improves the wearer's "
                                                            "magic damage.",
                         value=55000, rarity=0.1, mod="+25 Magic Defense", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class PlatinumPendant(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Platinum Pendant", description="A platinum-chained necklace that massively improves the "
                                                              "wearer's magic damage.",
                         value=60000, rarity=0.1, mod="+25 Magic Damage", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class ElementalAmulet(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="Elemental Amulet", description="Fashioned from the cores of elementals, this necklace "
                                                              "increases the resistance of the wearer to the 6 main "
                                                              "elemental types, fire, ice, electric, water, earth, "
                                                              "and wind.",
                         value=100000, rarity=0.05, mod="Elemental", subtyp="Pendant", unequip=False)
        self.weight = 0.2


class HealthPotion(Potion):

    def __init__(self):
        super().__init__(name="Health Potion", description="A potion that restores up to 25% of your health.",
                         value=100, rarity=0.75, subtyp='Health')
        self.percent = 0.25
        self.item = HealthPotion

    def use(self, user, target=None):
        if user.health.current == user.health.max:
            print("You are already at full health.")
            return False
        user.modify_inventory(self.item, num=1, subtract=True)
        if user.state != 'fight':
            heal = int(user.health.max * self.percent)
        else:
            rand_heal = int(user.health.max * self.percent)
            heal = random.randint(rand_heal // 2, rand_heal) * max(1, user.check_mod('luck', luck_factor=12))
        print(f"The potion healed you for {heal} life.")
        user.health.current += heal
        if user.health.current >= user.health.max:
            user.health.current = user.health.max
            print("You are at max health.")
        return True


class GreatHealthPotion(HealthPotion):

    def __init__(self):
        super().__init__()
        self.name = "Great Health Potion"
        self.description = "A potion that restores up to 50% of your health."
        self.value = 600
        self.rarity = 0.5
        self.percent = 0.50
        self.item = GreatHealthPotion


class SuperHealthPotion(HealthPotion):

    def __init__(self):
        super().__init__()
        self.name = "Super Health Potion"
        self.description = "A potion that restores up to 75% of your health."
        self.value = 3000
        self.rarity = 0.3
        self.percent = 0.75
        self.item = SuperHealthPotion


class MasterHealthPotion(HealthPotion):

    def __init__(self):
        super().__init__()
        self.name = "Master Health Potion"
        self.description = "A potion that restores up to 100% of your health."
        self.value = 10000
        self.rarity = 0.2
        self.percent = 1.0
        self.item = MasterHealthPotion


class ManaPotion(Potion):

    def __init__(self):
        super().__init__(name="Mana Potion", description="A potion that restores up to 25% of your mana.",
                         value=250, rarity=0.6, subtyp='Mana')
        self.percent = 0.25
        self.item = ManaPotion

    def use(self, user, target=None):
        if user.mana.current == user.mana.max:
            print("You are already at full mana.")
            return False
        user.modify_inventory(self.item, num=1, subtract=True)
        if user.state != 'fight':
            heal = int(user.mana.max * self.percent)
        else:
            rand_res = int(user.mana.max * self.percent)
            heal = random.randint(rand_res // 2, rand_res) * max(1, user.check_mod('luck', luck_factor=12))
        print(f"The potion restored {heal} mana points.")
        user.mana.current += heal
        if user.mana.current >= user.mana.max:
            user.mana.current = user.mana.max
            print("You are at full mana.")
        return True


class GreatManaPotion(ManaPotion):

    def __init__(self):
        super().__init__()
        self.name = "Great Mana Potion"
        self.description = "A potion that restores up to 50% of your mana."
        self.value = 1500
        self.rarity = 0.4
        self.percent = 0.50
        self.item = GreatManaPotion


class SuperManaPotion(ManaPotion):

    def __init__(self):
        super().__init__()
        self.name = "Super Mana Potion"
        self.description = "A potion that restores up to 75% of your mana."
        self.value = 8000
        self.rarity = 0.25
        self.percent = 0.75
        self.item = SuperManaPotion


class MasterManaPotion(ManaPotion):

    def __init__(self):
        super().__init__()
        self.name = "Master Mana Potion"
        self.description = "A potion that restores up to 100% of your mana."
        self.value = 35000
        self.rarity = 0.1
        self.percent = 1.0
        self.item = MasterManaPotion


class Elixir(Potion):

    def __init__(self):
        super().__init__(name="Elixir", description="A potion that restores up to 50% of your health and mana.",
                         value=20000, rarity=0.2, subtyp='Elixir')
        self.percent = 0.5
        self.item = Elixir

    def use(self, user, target=None):
        if user.health.current == user.health.max and user.mana.current == user.mana.max:
            print("You are already at full health and mana.")
            return False
        user.modify_inventory(self.item, num=1, subtract=True)
        if user.state != 'fight':
            health_heal = int(user.health.max * self.percent)
            mana_heal = int(user.mana.max * self.percent)
        else:
            rand_heal = int(user.health.max * self.percent)
            rand_res = int(user.mana.max * self.percent)
            health_heal = random.randint(rand_heal // 2, rand_heal) * max(1, user.check_mod('luck', luck_factor=12))
            mana_heal = random.randint(rand_res // 2, rand_res) * max(1, user.check_mod('luck', luck_factor=12))
        print(f"The potion restored {health_heal} health points and {mana_heal} mana points.")
        user.health.current += health_heal
        user.mana.current += mana_heal
        if user.health.current >= user.health.max:
            user.health.current = user.health.max
            print("You are at max health.")
        if user.mana.current >= user.mana.max:
            user.mana.current = user.mana.max
            print("You are at full mana.")
        return True


class Megalixir(Elixir):

    def __init__(self):
        super().__init__()
        self.name = "Megalixir"
        self.description = "A potion that restores up to 100% of your health and mana."
        self.value = 50000
        self.rarity = 0.05
        self.percent = 1.0
        self.item = Megalixir


class HPPotion(Potion):

    def __init__(self):
        super().__init__(name="HP Potion", description="A potion that permanently increases your max health by 10.",
                         value=10000, rarity=0.5, subtyp='Stat')
        self.mod = 10

    def use(self, user, target=None):
        user.modify_inventory(HPPotion, num=1, subtract=True)
        user.health.max += self.mod
        if user.in_town():
            user.health.current = user.health.max
        print(f"{user.name}'s HP has increased by {self.mod}!")
        return True


class MPPotion(Potion):

    def __init__(self):
        super().__init__(name="MP Potion", description="A potion that permanently increases your max mana by 10.",
                         value=15000, rarity=0.4, subtyp='Stat')
        self.mod = 10

    def use(self, user, target=None):
        user.modify_inventory(MPPotion, num=1, subtract=True)
        user.mana.max += self.mod
        if user.in_town():
            user.mana.current = user.mana.max
        print(f"{user.name}'s MP has increased by {self.mod}!")
        return True


class StrengthPotion(Potion):

    def __init__(self):
        super().__init__(name="Strength Potion", description="A potion that permanently increases your strength by 1.",
                         value=50000, rarity=0.1, subtyp='Stat')

    def use(self, user, target=None):
        user.modify_inventory(StrengthPotion, num=1, subtract=True)
        user.stats.strength += 1
        print(f"{user.name}'s strength has increased by 1!")
        return True


class IntelPotion(Potion):

    def __init__(self):
        super().__init__(name="Intelligence Potion", description="A potion that permanently increases your intelligence"
                                                                 " by 1.",
                         value=50000, rarity=0.1, subtyp='Stat')

    def use(self, user, target=None):
        user.modify_inventory(IntelPotion, num=1, subtract=True)
        user.stats.intel += 1
        print(f"{user.name}'s intelligence has increased by 1!")
        return True


class WisdomPotion(Potion):

    def __init__(self):
        super().__init__(name="Wisdom Potion", description="A potion that permanently increases your wisdom by 1.",
                         value=50000, rarity=0.1, subtyp='Stat')

    def use(self, user, target=None):
        user.modify_inventory(WisdomPotion, num=1, subtract=True)
        user.stats.wisdom += 1
        print(f"{user.name}'s wisdom has increased by 1!")
        return True


class ConPotion(Potion):

    def __init__(self):
        super().__init__(name="Constitution Potion", description="A potion that permanently increases your constitution"
                                                                 " by 1.",
                         value=50000, rarity=0.1, subtyp='Stat')

    def use(self, user, target=None):
        user.modify_inventory(ConPotion, num=1, subtract=True)
        user.stats.con += 1
        print(f"{user.name}'s constitution has increased by 1!")
        return True


class CharismaPotion(Potion):

    def __init__(self):
        super().__init__(name="Charisma Potion", description="A potion that permanently increases your charisma by 1.",
                         value=50000, rarity=0.1, subtyp='Stat')

    def use(self, user, target=None):
        user.modify_inventory(CharismaPotion, num=1, subtract=True)
        user.stats.charisma += 1
        print(f"{user.name}'s charisma has increased by 1!")
        return True


class DexterityPotion(Potion):

    def __init__(self):
        super().__init__(name="Dexterity Potion", description="A potion that permanently increases your dexterity by "
                                                              "1.",
                         value=50000, rarity=0.1, subtyp='Stat')

    def use(self, user, target=None):
        user.modify_inventory(DexterityPotion, num=1, subtract=True)
        user.stats.dex += 1
        print(f"{user.name}'s dexterity has increased by 1!")
        return True


class AardBeing(Potion):

    def __init__(self):
        super().__init__(name="Aard of Being", description="A potion that permanently increases all stats by 1.",
                         value=250000, rarity=0.01, subtyp='Stat')

    def use(self, user, target=None):
        user.modify_inventory(AardBeing, num=1, subtract=True)
        user.stats.strength += 1
        user.stats.intel += 1
        user.stats.wisdom += 1
        user.stats.con += 1
        user.stats.charisma += 1
        user.stats.dex += 1
        print(f"All of {user.name}'s stats have been increased by 1!")
        return True


class Status(Potion):
    """
    
    """

    def __init__(self):
        super().__init__(name="Status", description="Base class for status items.",
                         value=0, rarity=0, subtyp="Status")
        self.status = None
        self.item = Status

    def use(self, user, target=None):
        if not user.status_effects[self.status].active:
            print(f"You are not affected by {self.status.lower()}.")
            return False
        user.modify_inventory(self.item, num=1, subtract=True)
        user.status_effects[self.status].active = False
        user.status_effects[self.status].duration = 0
        try:
            user.status_effects[self.status].extra = 0
        except IndexError:
            pass
        print(f"You have been cured of {self.status.lower()}.")
        if user.health.current < user.health.max:
            heal = int(0.1 * user.health.max)
            heal = random.randint(heal // 2, heal)
            heal = min(heal, user.health.max - user.health.current)
            user.health.current += heal
            print(f"You have been healed for {heal} health.")
        return True


class Antidote(Status):
    """

    """

    def __init__(self):
        super().__init__()
        self.name = "Antidote"
        self.description = "A potion that will cure poison."
        self.value = 250
        self.rarity = 0.75
        self.status = 'Poison'
        self.item = Antidote


class EyeDrop(Status):
    """

    """

    def __init__(self):
        super().__init__()
        self.name = "Eye Drop"
        self.description = "Eye drops that will cure blindness."
        self.value = 250
        self.rarity = 0.75
        self.status = 'Blind'
        self.item = EyeDrop


class AntiCoagulant(Status):
    """

    """

    def __init__(self):
        super().__init__()
        self.name = "Anti-Coagulant"
        self.description = "Anti-coagulants will cure bleeding."
        self.value = 1000
        self.rarity = 0.5
        self.status = 'Bleed'
        self.item = AntiCoagulant


class PhoenixDown(Status):
    """

    """

    def __init__(self):
        super().__init__()
        self.name = "Phoenix Down"
        self.description = "A potion that will cure doom status."
        self.value = 15000
        self.rarity = 0.25
        self.status = 'Doom'
        self.item = PhoenixDown


class Key(Misc):
    """
    Opens locked chests
    """

    def __init__(self):
        super().__init__(name="Key", description="Unlocks a locked chest but is consumed.", value=500, rarity=0.25,
                         subtyp='Key')

    def use(self, user, target=None):
        tile = user.world_dict[(user.location_x, user.location_y, user.location_z)]
        if 'Chest' in str(tile):
            user.modify_inventory(Key, num=1, subtract=True)
            tile.locked = False
            print(f"{user.name} unlocks the chest.")
        else:
            print("The key does not fit in the door.")
        time.sleep(1)
        return True


class OldKey(Misc):
    """
    Opens locked doors
    """

    def __init__(self):
        super().__init__(name="Old Key", description="Unlocks doors that may lead to either valuable treasure or to "
                                                     "powerful enemies.",
                         value=50000, rarity=0.2, subtyp='Key')

    def use(self, user, target=None):
        tile = user.world_dict[(user.location_x, user.location_y, user.location_z)]
        if 'Door' in str(tile):
            user.modify_inventory(OldKey, num=1, subtract=True)
            tile.locked = False
            print(f"{user.name} unlocks the door.")
        else:
            print("The key does not fit in the chest.")
        time.sleep(1)
        return True


class Scroll(Misc):
    """
    Scrolls allow for a one-time use of a spell; scrolls can only be used in combat
    """

    def __init__(self):
        super().__init__(name="Scroll", description="Base class for scrolls.", value=0, rarity=0, subtyp='Scroll')
        self.spell = abilities.Spell
        self.item = Scroll
        self.charges = random.randint(2, 10)

    def use(self, user, target=None):
        print(f"{user.name} uses {self.name}.")
        self.spell().cast(user, target=target)
        self.charges -= 1
        if not self.charges:
            print("The scroll crumbles to dust in your hands!")
            user.modify_inventory(self.item, num=1, subtract=True)
        return True


class BlessScroll(Scroll):
    """
    Bless
    """

    def __init__(self):
        super().__init__()
        self.name = "Bless Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast Bless, which increases " \
                           "attack damage for several turns. The scroll will be consumed when it is out of charges."
        self.value = 1000
        self.rarity = 0.6
        self.spell = abilities.Bless
        self.item = BlessScroll


class SleepScroll(Scroll):
    """
    Sleep
    """

    def __init__(self):
        super().__init__()
        self.name = "Sleep Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast Sleep, which can put the " \
                           "enemy to sleep. The scroll will be consumed when it is out of charges."
        self.value = 2000
        self.rarity = 0.5
        self.spell = abilities.Sleep
        self.item = SleepScroll


class FireScroll(Scroll):
    """
    Firebolt
    """

    def __init__(self):
        super().__init__()
        self.name = "Fire Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the fire spell Firebolt. " \
                           "The scroll will be consumed when it is out of charges."
        self.value = 2500
        self.rarity = 0.33
        self.spell = abilities.Firebolt
        self.item = FireScroll


class IceScroll(Scroll):
    """
    Ice Lance
    """

    def __init__(self):
        super().__init__()
        self.name = "Ice Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the ice spell Ice Lance. " \
                           "The scroll will be consumed when it is out of charges."
        self.value = 2500
        self.rarity = 0.33
        self.spell = abilities.IceLance
        self.item = IceScroll


class ElectricScroll(Scroll):
    """
    Shock
    """

    def __init__(self):
        super().__init__()
        self.name = "Electric Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the electric spell Shock." \
                           " The scroll will be consumed when it is out of charges."
        self.value = 2500
        self.rarity = 0.33
        self.spell = abilities.Shock
        self.item = ElectricScroll


class WaterScroll(Scroll):
    """
    Water Jet
    """

    def __init__(self):
        super().__init__()
        self.name = "Water Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the water spell Water Jet" \
                           ". The scroll will be consumed when it is out of charges."
        self.value = 2500
        self.rarity = 0.33
        self.spell = abilities.WaterJet
        self.item = WaterScroll


class EarthScroll(Scroll):
    """
    Tremor
    """

    def __init__(self):
        super().__init__()
        self.name = "Earth Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the earth spell Tremor. " \
                           "The scroll will be consumed when it is out of charges."
        self.value = 2500
        self.rarity = 0.33
        self.spell = abilities.Tremor
        self.item = EarthScroll


class WindScroll(Scroll):
    """
    Gust
    """

    def __init__(self):
        super().__init__()
        self.name = "Wind Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the wind spell Gust. The" \
                           " scroll will be consumed when it is out of charges."
        self.value = 2500
        self.rarity = 0.33
        self.spell = abilities.Gust
        self.item = WindScroll


class ShadowScroll(Scroll):
    """
    Shadow Bolt
    """

    def __init__(self):
        super().__init__()
        self.name = "Shadow Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the shadow spell Shadow" \
                           " Bolt. The scroll will be consumed when it is out of charges."
        self.value = 2500
        self.rarity = 0.33
        self.spell = abilities.ShadowBolt
        self.item = ShadowScroll


class HolyScroll(Scroll):
    """
    Holy
    """

    def __init__(self):
        super().__init__()
        self.name = "Holy Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the holy spell Holy. The" \
                           " scroll will be consumed when it is out of charges."
        self.value = 2500
        self.rarity = 0.33
        self.spell = abilities.Holy
        self.item = HolyScroll


class CleanseScroll(Scroll):
    """
    Cleanse
    """

    def __init__(self):
        super().__init__()
        self.name = "Cleanse Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the holy spell Cleanse. The" \
                           " scroll will be consumed when it is out of charges."
        self.value = 2500
        self.rarity = 0.33
        self.spell = abilities.Cleanse
        self.item = CleanseScroll


class BoostScroll(Scroll):
    """
    Boost
    """

    def __init__(self):
        super().__init__()
        self.name = "Boost Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the heal spell Boost. " \
                           "The scroll will be consumed when it is out of charges."
        self.value = 5000
        self.rarity = 0.25
        self.spell = abilities.Boost
        self.item = BoostScroll


class ShellScroll(Scroll):
    """
    Regen
    """

    def __init__(self):
        super().__init__()
        self.name = "Shell Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the heal spell Shell. " \
                           "The scroll will be consumed when it is out of charges."
        self.value = 5000
        self.rarity = 0.25
        self.spell = abilities.Shell
        self.item = ShellScroll


class SilenceScroll(Scroll):
    """
    Silence
    """

    def __init__(self):
        super().__init__()
        self.name = "Silence Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast Silence, which can " \
                           "prevent an target from casting spell for a time. The scroll will be consumed when it " \
                           "is out of charges."
        self.value = 5000
        self.rarity = 0.25
        self.spell = abilities.Silence
        self.item = SilenceScroll


class DispelScroll(Scroll):
    """
    Dispel
    """

    def __init__(self):
        super().__init__()
        self.name = "Dispel Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast Dispel, which can remove " \
                           "all positive status effects from the target. The scroll will be consumed when it is out of" \
                           " charges."
        self.value = 7500
        self.rarity = 0.2
        self.spell = abilities.Dispel
        self.item = DispelScroll


class DeathScroll(Scroll):
    """
    Desoul
    """

    def __init__(self):
        super().__init__()
        self.name = "Death Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast Desoul, which can kill the" \
                           " target. The scroll will be consumed when it is out of charges."
        self.value = 10000
        self.rarity = 0.1
        self.spell = abilities.Desoul
        self.item = DeathScroll


class SanctuaryScroll(Scroll):
    """
    Sanctuary
    """

    def __init__(self):
        super().__init__()
        self.name = "Sanctuary Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast Sanctuary, which can " \
                           "return the user to town. The scroll will be consumed when it is out of charges."
        self.value = 25000
        self.rarity = 0.05
        self.spell = abilities.Sanctuary
        self.item = SanctuaryScroll


class UltimaScroll(Scroll):
    """
    Ultima
    """

    def __init__(self):
        super().__init__()
        self.name = "Ultima Scroll"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the powerful Ultima. The " \
                           "scroll will be consumed when it is out of charges."
        self.value = 50000
        self.rarity = 0.01
        self.spell = abilities.Ultima
        self.item = UltimaScroll


class RatTail(Misc):
    """

    """

    def __init__(self):
        super().__init__(name="Rat Tail", description="The tail of a rat.", value=0, rarity=1, subtyp='Enemy')


class MysteryMeat(Misc):
    """

    """

    def __init__(self):
        super().__init__(name="Mystery Meat", description="Unknown meat with a strange smell. Maybe you could do "
                                                          "something with this.",
                         value=0, rarity=0.5, subtyp='Enemy')


class Leather(Misc):
    """

    """

    def __init__(self):
        super().__init__(name="Leather", description="The dried skin of an animal, used for various purposes.",
                         value=0, rarity=0.5, subtyp='Enemy')


class Feather(Misc):
    """

    """

    def __init__(self):
        super().__init__(name="Feather", description="The feather of a bird.",
                         value=0, rarity=0.5, subtyp='Enemy')


class SnakeSkin(Misc):
    """

    """

    def __init__(self):
        super().__init__(name="Snake Skin", description="The skin of a snake.",
                         value=0, rarity=0.5, subtyp='Enemy')


class ScrapMetal(Misc):
    """

    """

    def __init__(self):
        super().__init__(name="Scrap Metal", description="A chunk of metal.",
                         value=0, rarity=0.5, subtyp='Enemy')


class ElementalMote(Misc):
    """

    """

    def __init__(self):
        super().__init__(name="Elemental Mote", description="The elemental core of a Myrmidon.",
                         value=0, rarity=0.5, subtyp='Enemy')


class PowerCore(Misc):
    """

    """

    def __init__(self):
        super().__init__(name="Power Core", description="The power source of the Golem guarding the stairs to level 5.",
                         value=0, rarity=1, subtyp='Enemy')


class LuckyLocket(Misc):
    """
    Momento given to the warrior Joffrey by the waitress, his betrothed
    """

    def __init__(self):
        super().__init__(name="Lucky Locket", description="A simple gold necklace with a locket containing the picture "
                                                          "of a fair lass.",
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


# items_dict used by shops
items_dict = {
    'Weapon': {
        'Dagger': [Dirk, Baselard, Kris, Rondel, Kukri], 
        'Sword': [Rapier, Jian, Talwar, Shamshir, Khopesh],
        'Club': [Mace, WarHammer, Pernach, Morgenstern],
        'Fist': [BrassKnuckles, Cestus, BattleGauntlet, BaghNahk],
        'Ninja Blade': [Tanto, Wakizashi],
        'Longsword': [Bastard, Claymore, Zweihander, Changdao, Flamberge],
        'Battle Axe': [Mattock, Broadaxe, DoubleAxe, Parashu, Greataxe],
        'Polearm': [Framea, Partisan, Halberd, Naginata, Trident],
        'Staff': [Quarterstaff, Baston, IronshodStaff, SerpentStaff, HolyStaff,
                  RuneStaff, MithrilshodStaff],
        'Hammer': [Sledgehammer, Maul, EarthHammer, GreatMaul]},
    'OffHand': {
        'Shield': [Buckler, Aspis, Targe, Glagwa, KiteShield, Pavise], 
        'Tome': [Book, TomeKnowledge, Grimoire, BookShadows, DragonRouge, Vedas, Necronomicon]},
    'Armor': {
        'Cloth': [Tunic, ClothCloak, SilverCloak, GoldCloak, CloakEnchantment, WizardRobe],
        'Light': [PaddedArmor, LeatherArmor, Cuirboulli, StuddedLeather, StuddedCuirboulli],
        'Medium': [HideArmor, ChainShirt, ScaleMail, Breastplate, HalfPlate],
        'Heavy': [RingMail, ChainMail, Splint, PlateMail, FullPlate]},
    'Accessory': {
        'Ring': [IronRing, PowerRing, AccuracyRing, BarrierRing, SteelRing, MightRing, EvasionRing,
                 TitaniumRing, ForceRing],
        'Pendant': [VisionPendant, RubyAmulet, SilverPendant, AntidotePendant, SapphireAmulet,
                    GoldPendant, GorgonPendant, DharmaPendant, LevitationNecklace,
                    InvisibilityAmulet, DiamondAmulet, PlatinumPendant]},
    'Potion': {
        'Health': [HealthPotion, GreatHealthPotion, SuperHealthPotion, MasterHealthPotion],
        'Mana': [ManaPotion, GreatManaPotion, SuperManaPotion, MasterManaPotion],
        'Elixir': [Elixir, Megalixir],
        'Stat': [HPPotion, MPPotion, StrengthPotion, IntelPotion, WisdomPotion, ConPotion,
                 CharismaPotion, DexterityPotion, AardBeing],
        'Status': [Antidote, EyeDrop, AntiCoagulant, PhoenixDown]},
    'Misc': {
        'Key': [Key, OldKey],
        'Scroll': [BlessScroll, SleepScroll, FireScroll, IceScroll, ElectricScroll, WaterScroll,
                   EarthScroll, WindScroll, ShadowScroll, HolyScroll, CleanseScroll, BoostScroll,
                   ShellScroll, SilenceScroll, DispelScroll, DeathScroll, SanctuaryScroll, UltimaScroll]}
}