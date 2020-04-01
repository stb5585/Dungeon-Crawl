###########################################
""" item manager """

# Imports
import random


# Functions
def random_item(item_dict):
    rand_type = random.choice(list(item_dict))
    treasure_list = item_dict[rand_type]
    treasure = random.choices(treasure_list[0], treasure_list[1])[0]
    return treasure


def remove(typ):
    typ_dict = dict(Weapon=NoWeapon, OffHand=NoOffHand, Armor=NoArmor)
    return typ_dict[typ]


class Item:
    """
    value: price in gold; sale price will be half this amount
    rarity: higher number means more rare
    crit: chance to double damage; higher number means lower chance to crit
    handed: identifies weapon as 1-handed or 2-handed; 2-handed weapons prohibit the ability to use a shield
    block: higher number means lower chance to block; if block is successful, damage mitigation will be decided randomly
    """

    def __init__(self, name, description, value):
        self.name = name
        self.description = description
        self.value = value

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\n".format(self.name, self.description, self.value)


class Weapon(Item):

    def __init__(self, name, description, value, rarity, damage, crit, handed, unequip, **kwargs):
        super().__init__(name, description, value)
        self.rarity = rarity
        self.damage = damage
        self.crit = crit
        self.handed = handed
        self.unequip = unequip
        self.typ = "Weapon"

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\nDamage: {}\nCritical Chance: {}\n{}-handed".format(self.name,
                                                                                             self.description,
                                                                                             self.value, self.damage,
                                                                                             self.crit, self.handed)


class NoWeapon(Weapon):

    def __init__(self):
        super().__init__(name="BARE HANDS", description="Nothing but your fists.", value=0, rarity=0, damage=0, crit=10,
                         handed=1, unequip=True)


class BronzeSword(Weapon):

    def __init__(self):
        super().__init__(name="BRONZE SWORD", description="A weapon with a long bronze blade and a hilt with a hand "
                                                          "guard, used for thrusting or striking and now typically "
                                                          "worn as part of ceremonial dress.",
                         value=125, rarity=3, damage=2, crit=8, handed=1, subtyp='Sword', unequip=False)


class IronSword(Weapon):

    def __init__(self):
        super().__init__(name="IRON SWORD", description="A weapon with a long iron blade and a hilt with a hand "
                                                        "guard, used for thrusting or striking and now typically worn "
                                                        "as part of ceremonial dress.",
                         value=1000, rarity=8, damage=5, crit=5, handed=1, subtyp='Sword', unequip=False)


class SteelSword(Weapon):

    def __init__(self):
        super().__init__(name="STEEL SWORD", description="A weapon with a long steel blade and a hilt with a hand "
                                                         "guard, used for thrusting or striking and now typically worn "
                                                         "as part of ceremonial dress.",
                         value=2000, rarity=15, damage=7, crit=4, handed=1, subtyp='Sword', unequip=False)


class Excalibur(Weapon):

    def __init__(self):
        super().__init__(name="EXCALIBUR", description="The legendary sword of King Arthur, bestowed upon him by the "
                                                       "Lady of the Lake.", value=10000, rarity=50, damage=15, crit=2,
                         handed=1, subtyp='Sword', unequip=False)


class BattleAxe(Weapon):

    def __init__(self):
        super().__init__(name="BATTLE AXE", description="An axe specifically designed for combat.", value=500, rarity=6,
                         damage=6, crit=8, handed=2, subtyp='Axe', unequip=False)


class GreatAxe(Weapon):

    def __init__(self):
        super().__init__(name="GREAT AXE", description="A double-bladed, two-handed melee weapon.", value=1500,
                         rarity=12, damage=10, crit=5, handed=2, subtyp='Axe', unequip=False)


class Jarnbjorn(Weapon):

    def __init__(self):
        super().__init__(name="JARNBJORN", description="Legendary axe of Thor Odinson. Old Norse for \"iron bear\".",
                         value=12000, rarity=50, damage=20, crit=3, handed=2, subtyp='Axe', unequip=False)


class Armor(Item):

    def __init__(self, name, description, value, rarity, armor, unequip, **kwargs):
        super().__init__(name, description, value)
        self.rarity = rarity
        self.armor = armor
        self.unequip = unequip
        self.typ = 'Armor'

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\nArmor: {}".format(self.name, self.description, self.value, self.armor)


class NoArmor(Armor):

    def __init__(self):
        super().__init__(name="NO ARMOR", description="No armor equipped.", value=0, rarity=0, armor=0, unequip=True)


class Tunic(Armor):

    def __init__(self):
        super().__init__(name="TUNIC", description="A close-fitting short coat as part of a uniform, especially a "
                                                   "police or military uniform.", value=60, rarity=2, armor=1,
                         subtyp='Cloth', unequip=False)


class LeatherArmor(Armor):

    def __init__(self):
        super().__init__(name="LEATHER ARMOR", description="A protective covering made of animal hide, boiled to make "
                                                           "it tough and rigid and worn over the torso to protect it "
                                                           "from injury.", value=150, rarity=4, armor=2,
                         subtyp='Light', unequip=False)


class ChainMail(Armor):

    def __init__(self):
        super().__init__(name="CHAIN MAIL", description="A type of armour consisting of small metal rings linked "
                                                        "together in a pattern to form a mesh.", value=350, rarity=6,
                         armor=3, subtyp='Medium', unequip=False)


class Breastplate(Armor):

    def __init__(self):
        super().__init__(name="BREASTPLATE", description="A device made of iron, worn over the torso to protect it from"
                                                         " injury.", value=800, rarity=10, armor=4, subtyp='Medium',
                         unequip=False)


class PlateArmor(Armor):

    def __init__(self):
        super().__init__(name="PLATE ARMOR", description="A type of personal body armour made from iron or steel "
                                                         "plates, covering the wearer's torso.",
                         value=2500, rarity=20, armor=8, subtyp='Heavy', unequip=False)


class FullPlate(Armor):

    def __init__(self):
        super().__init__(name="FULL PLATE", description="A type of personal body armour made from iron or steel "
                                                        "plates, culminating in the iconic suit of armour entirely "
                                                        "encasing the wearer.",
                         value=8000, rarity=40, armor=12, subtyp='Heavy', unequip=False)


class OffHand(Item):

    def __init__(self, name, description, value, rarity, block, unequip, **kwargs):
        super().__init__(name, description, value)
        self.rarity = rarity
        self.block = block
        self.unequip = unequip
        self.typ = 'OffHand'

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\nBlock: {}".format(self.name, self.description, self.value, self.block)


class NoOffHand(OffHand):

    def __init__(self):
        super().__init__(name="NO OFFHAND", description="No off-hand equipped.", value=0, rarity=0, block=25,
                         unequip=True)


class Buckler(OffHand):

    def __init__(self):
        super().__init__(name="BUCKLER", description="A small round shield held by a handle or worn on the forearm.",
                         value=25, rarity=2, block=10, subtyp='Shield', unequip=False)


class WoodShield(OffHand):

    def __init__(self):
        super().__init__(name="WOOD SHIELD", description="A broad piece of wood, held by straps used as a protection "
                                                         "against blows or missiles.", value=100, rarity=4, block=8,
                         subtyp='Shield', unequip=False)


class BronzeShield(OffHand):

    def __init__(self):
        super().__init__(name="BRONZE SHIELD", description="A broad piece of bronze, held by a handle attached on one "
                                                           "side, used as a protection against blows or missiles.",
                         value=250, rarity=6, block=6, subtyp='Shield', unequip=False)


class IronShield(OffHand):

    def __init__(self):
        super().__init__(name="IRON SHIELD", description="A broad piece of iron, held by a handle attached on one "
                                                         "side, used as a protection against blows or missiles.",
                         value=500, rarity=10, block=4, subtyp='Shield', unequip=False)


class TowerShield(OffHand):

    def __init__(self):
        super().__init__(name="TOWER SHIELD", description="A defensive bulwark, an impenetrable wall.", value=5000,
                         rarity=30, block=2, subtyp='Shield', unequip=False)


class Potion(Item):

    def __init__(self, name, description, value, rarity, percent, **kwargs):
        super().__init__(name, description, value)
        self.rarity = rarity
        self.percent = percent
        self.typ = "Potion"


class HealthPotion(Potion):

    def __init__(self):
        super().__init__(name="HEALTH POTION", description="A potion that restores 25% of your health", value=100,
                         rarity=10, percent=0.25, subtyp='Health')


class SuperHealthPotion(Potion):

    def __init__(self):
        super().__init__(name="SUPER HEALTH POTION", description="A potion that restores 50% of your health", value=600,
                         rarity=20, percent=0.5, subtyp='Health')


class MasterHealthPotion(Potion):

    def __init__(self):
        super().__init__(name="MASTER HEALTH POTION", description="A potion that restores 100% of your health",
                         value=1000, rarity=30, percent=1.0, subtyp='Health')


class ManaPotion(Potion):

    def __init__(self):
        super().__init__(name="MANA POTION", description="A potion that restores 25% of your mana", value=250,
                         rarity=10, percent=0.25, subtyp='Mana')
        self.typ = "Potion"


class SuperManaPotion(Potion):

    def __init__(self):
        super().__init__(name="SUPER MANA POTION", description="A potion that restores 50% of your mana", value=1500,
                         rarity=20, percent=0.5, subtyp='Mana')


class MasterManaPotion(Potion):

    def __init__(self):
        super().__init__(name="MASTER MANA POTION", description="A potion that restores 100% of your mana",
                         value=2500, rarity=30, percent=1.0, subtyp='Mana')


# Parameters
items_dict = {'Weapon': [[BronzeSword, IronSword, SteelSword, Excalibur, BattleAxe, GreatAxe, Jarnbjorn],
                         [1 / int(BronzeSword().rarity), 1 / int(IronSword().rarity), 1 / int(SteelSword().rarity),
                          1 / int(Excalibur().rarity), 1 / int(BattleAxe().rarity), 1 / int(GreatAxe().rarity),
                          1 / int(Jarnbjorn().rarity)]],
              'OffHand': [[Buckler, WoodShield, BronzeShield, IronShield, TowerShield],
                          [1 / int(Buckler().rarity), 1 / int(WoodShield().rarity), 1 / int(BronzeShield().rarity),
                           1 / int(IronShield().rarity), 1 / int(TowerShield().rarity)]],
              'Armor': [[Tunic, LeatherArmor, ChainMail, Breastplate, PlateArmor, FullPlate],
                        [1 / int(Tunic().rarity), 1 / int(LeatherArmor().rarity), 1 / int(ChainMail().rarity),
                         1 / int(Breastplate().rarity), 1 / int(PlateArmor().rarity), 1 / int(FullPlate().rarity)]],
              'Potion': [[HealthPotion, SuperHealthPotion, MasterHealthPotion, ManaPotion, SuperManaPotion,
                          MasterManaPotion],
                         [1 / int(HealthPotion().rarity), 1 / int(SuperHealthPotion().rarity),
                          1 / int(MasterHealthPotion().rarity), 1 / int(ManaPotion().rarity),
                          1 / int(SuperManaPotion().rarity), 1 / int(MasterManaPotion().rarity)]],
              }
