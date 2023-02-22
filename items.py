###########################################
""" item manager """

# Imports
import random


# Functions
def reciprocal(x: int) -> float:
    return 1.0 / x


def random_item(z: int):
    item_dict = {'Weapon': {'Dagger': [[BronzeDagger, IronDagger, SteelDagger, AdamantiteDagger, MithrilDagger],
                                       [reciprocal(BronzeDagger().rarity), reciprocal(IronDagger().rarity),
                                        reciprocal(SteelDagger().rarity), reciprocal(AdamantiteDagger().rarity),
                                        reciprocal(MithrilDagger().rarity)],
                                       ['1', '1', '2', '3', '4']],
                            'Sword': [[BronzeSword, IronSword, SteelSword, AdamantiteSword, MithrilSword],
                                      [reciprocal(BronzeSword().rarity), reciprocal(IronSword().rarity),
                                       reciprocal(SteelSword().rarity), reciprocal(AdamantiteSword().rarity),
                                       reciprocal(MithrilSword().rarity)],
                                      ['1', '1', '2', '3', '4']],
                            'Mace': [[BronzeMace, IronMace, SteelMace, AdamantiteMace, MithrilMace],
                                     [reciprocal(BronzeMace().rarity), reciprocal(IronMace().rarity),
                                      reciprocal(SteelMace().rarity), reciprocal(AdamantiteMace().rarity),
                                      reciprocal(MithrilMace().rarity)],
                                     ['1', '1', '2', '3', '4']],
                            'Fist': [[BronzeFist, IronFist, SteelFist, AdamantiteFist, MithrilFist],
                                     [reciprocal(BronzeFist().rarity), reciprocal(IronFist().rarity),
                                      reciprocal(SteelFist().rarity), reciprocal(AdamantiteFist().rarity),
                                      reciprocal(MithrilFist().rarity)],
                                     ['1', '2', '3', '4', '5']],
                            'Ninja Blades': [[Tanto, Wakizashi],
                                             [reciprocal(Tanto().rarity), reciprocal(Wakizashi().rarity)],
                                             ['4', '5']],
                            'Axe': [[Axe, BattleAxe, GreatAxe, AdamantiteAxe, MithrilAxe],
                                    [reciprocal(Axe().rarity), reciprocal(BattleAxe().rarity),
                                     reciprocal(GreatAxe().rarity), reciprocal(AdamantiteAxe().rarity),
                                     reciprocal(MithrilAxe().rarity)],
                                    ['1', '1', '2', '3', '4']],
                            'Polearm': [[Spear, Lance, Pike, Halberd, Trident],
                                        [reciprocal(Spear().rarity), reciprocal(Lance().rarity),
                                         reciprocal(Pike().rarity), reciprocal(Halberd().rarity),
                                         reciprocal(Trident().rarity)],
                                        ['1', '1', '2', '3', '4']],
                            'Staff': [[PineStaff, OakStaff, IronshodStaff, SerpentStaff, HolyStaff, RuneStaff,
                                       MithrilshodStaff],
                                      [reciprocal(PineStaff().rarity), reciprocal(OakStaff().rarity),
                                       reciprocal(IronshodStaff().rarity), reciprocal(SerpentStaff().rarity),
                                       reciprocal(HolyStaff().rarity), reciprocal(RuneStaff().rarity),
                                       reciprocal(MithrilshodStaff().rarity)],
                                      ['1', '1', '2', '3', '3', '4', '4']],
                            'Hammer': [[OakHammer, Maul, IronHammer, EarthHammer, WarHammer, GreatMaul],
                                       [reciprocal(OakHammer().rarity), reciprocal(Maul().rarity),
                                        reciprocal(IronHammer().rarity), reciprocal(EarthHammer().rarity),
                                        reciprocal(WarHammer().rarity), reciprocal(GreatMaul().rarity)],
                                       ['1', '1', '2', '2', '3', '4']],
                            },
                 'OffHand': {'Shield': [[WoodShield, BronzeShield, IronShield, SteelShield, KiteShield, TowerShield],
                                        [reciprocal(WoodShield().rarity), reciprocal(BronzeShield().rarity),
                                         reciprocal(IronShield().rarity), reciprocal(SteelShield().rarity),
                                         reciprocal(KiteShield().rarity), reciprocal(TowerShield().rarity)],
                                        ['1', '1', '2', '3', '4', '4']],
                             'Tome': [[Book, TomeKnowledge, Grimoire, BookShadows, DragonRouge, Vedas, Necronomicon],
                                      [reciprocal(Book().rarity), reciprocal(TomeKnowledge().rarity),
                                       reciprocal(Grimoire().rarity), reciprocal(BookShadows().rarity),
                                       reciprocal(DragonRouge().rarity), reciprocal(Vedas().rarity),
                                       reciprocal(Necronomicon().rarity)],
                                      ['1', '2', '3', '3', '4', '4', '5']]},
                 'Armor': {'Cloth': [[Tunic, ClothCloak, SilverCloak, GoldCloak, CloakEnchantment, WizardRobe],
                                     [reciprocal(Tunic().rarity), reciprocal(ClothCloak().rarity),
                                      reciprocal(SilverCloak().rarity), reciprocal(GoldCloak().rarity),
                                      reciprocal(CloakEnchantment().rarity), reciprocal(WizardRobe().rarity)],
                                     ['1', '1', '2', '3', '4', '5']],
                           'Light': [[PaddedArmor, LeatherArmor, Cuirboulli, StuddedLeather, StuddedCuirboulli],
                                     [reciprocal(PaddedArmor().rarity), reciprocal(LeatherArmor().rarity),
                                      reciprocal(Cuirboulli().rarity), reciprocal(StuddedLeather().rarity),
                                      reciprocal(StuddedCuirboulli().rarity)],
                                     ['1', '1', '2', '3', '4']],
                           'Medium': [[HideArmor, ChainShirt, ScaleMail, Breastplate, HalfPlate],
                                      [reciprocal(HideArmor().rarity), reciprocal(ChainShirt().rarity),
                                       reciprocal(ScaleMail().rarity), reciprocal(Breastplate().rarity),
                                       reciprocal(HalfPlate().rarity)],
                                      ['1', '1', '2', '3', '4']],
                           'Heavy': [[RingMail, ChainMail, Splint, PlateMail, FullPlate],
                                     [reciprocal(RingMail().rarity), reciprocal(ChainMail().rarity),
                                      reciprocal(Splint().rarity), reciprocal(PlateMail().rarity),
                                      reciprocal(FullPlate().rarity)],
                                     ['1', '1', '2', '3', '4']]},
                 'Accessory': {'Ring': [[IronRing, PowerRing],
                                        [reciprocal(IronRing().rarity), reciprocal(PowerRing().rarity)],
                                        ['1', '2']],
                               'Pendant': [[SilverPendant, RubyPendant, VisionPendant],
                                           [reciprocal(SilverPendant().rarity), reciprocal(RubyPendant().rarity),
                                            reciprocal(VisionPendant().rarity)],
                                           ['2', '2', '1']],

                               },
                 'Potion': {'Health': [[HealthPotion, GreatHealthPotion, SuperHealthPotion, MasterHealthPotion],
                                       [reciprocal(HealthPotion().rarity), reciprocal(GreatHealthPotion().rarity),
                                        reciprocal(SuperHealthPotion().rarity),
                                        reciprocal(MasterHealthPotion().rarity)],
                                       ['1', '2', '3', '4']],
                            'Mana': [[ManaPotion, GreatManaPotion, SuperManaPotion, MasterManaPotion],
                                     [reciprocal(ManaPotion().rarity), reciprocal(GreatManaPotion().rarity),
                                      reciprocal(SuperManaPotion().rarity), reciprocal(MasterManaPotion().rarity)],
                                     ['1', '2', '3', '4']],
                            'Elixir': [[Elixir, Megalixir],
                                       [reciprocal(Elixir().rarity), reciprocal(Megalixir().rarity)],
                                       ['3', '5']],
                            'Stat': [[HPPotion, MPPotion, StrengthPotion, IntelPotion, WisdomPotion, ConPotion,
                                      CharismaPotion, DexterityPotion, AardBeing],
                                     [reciprocal(HPPotion().rarity), reciprocal(MPPotion().rarity),
                                      reciprocal(StrengthPotion().rarity), reciprocal(IntelPotion().rarity),
                                      reciprocal(WisdomPotion().rarity), reciprocal(ConPotion().rarity),
                                      reciprocal(CharismaPotion().rarity), reciprocal(DexterityPotion().rarity),
                                      reciprocal(AardBeing().rarity)],
                                     ['1', '1', '2', '2', '2', '2', '2', '2', '5']]
                            },
                 'Misc': {'Key': [[Key, OldKey],
                                  [reciprocal(Key().rarity), reciprocal(OldKey().rarity)],
                                  ['1', '2']]}
                 }

    while True:
        rand_group = random.choice(list(item_dict))
        rand_type = random.choice(list(item_dict[rand_group]))
        treasure = random.choices(item_dict[rand_group][rand_type][0], item_dict[rand_group][rand_type][1])[0]
        item_index = item_dict[rand_group][rand_type][0].index(treasure)
        item_loc = int(item_dict[rand_group][rand_type][2][item_index])
        if int(z) >= item_loc >= (int(z) - 2):
            rand_item = treasure
            break
    return rand_item


def remove(typ):
    typ_dict = dict(Weapon=NoWeapon, OffHand=NoOffHand, Armor=NoArmor, Pendant=NoPendant, Ring=NoRing)
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
        self.restriction = list()

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\n".format(self.name, self.description, self.value)


class Weapon(Item):

    def __init__(self, name, description, value, rarity, damage, crit, handed, subtyp, unequip, off):
        super().__init__(name, description, value)
        self.rarity = rarity
        self.damage = damage
        self.crit = crit
        self.handed = handed
        self.subtyp = subtyp
        self.unequip = unequip
        self.off = off
        self.typ = "Weapon"
        self.ignore = False
        self.disarm = True

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\nDamage: {}\nCritical Chance: {}\n{}-handed".format(self.name,
                                                                                             self.description,
                                                                                             self.value, self.damage,
                                                                                             self.crit, self.handed)


class NoWeapon(Weapon):

    def __init__(self):
        super().__init__(name="BARE HANDS", description="Nothing but your fists.",
                         value=0, rarity=99, damage=0, crit=10, handed=1, subtyp='None', unequip=True,
                         off=True)


class BronzeFist(Weapon):

    def __init__(self):
        super().__init__(name="BRONZE FIST", description="Bronze knuckles designed to focus a punch's force toward a "
                                                         "harder and smaller contact area, increasing the chance of "
                                                         "cuts and fractures.",
                         value=150, rarity=5, damage=1, crit=7, handed=1, subtyp='Fist', unequip=False,
                         off=True)


class IronFist(Weapon):

    def __init__(self):
        super().__init__(name="IRON FIST", description="An iron studded leather glove with the finger tips removed.",
                         value=2000, rarity=10, damage=3, crit=6, handed=1, subtyp='Fist', unequip=False,
                         off=True)


class SteelFist(Weapon):

    def __init__(self):
        super().__init__(name="STEEL FIST", description="Steel knuckles designed similar to bronze knuckles with"
                                                        " added spikes that protrude out for increased damage.",
                         value=7500, rarity=25, damage=4, crit=5, handed=1, subtyp='Fist', unequip=False,
                         off=True)


class AdamantiteFist(Weapon):

    def __init__(self):
        super().__init__(name="ADAMANTITE FIST", description="A punching dagger made from hard adamantite meant for "
                                                             "close quarter combat.",
                         value=10000, rarity=40, damage=6, crit=3, handed=1, subtyp='Fist', unequip=False,
                         off=True)


class MithrilFist(Weapon):

    def __init__(self):
        super().__init__(name="MITHRIL FIST", description="A lightweight mesh glove made from mithril, providing added"
                                                          "non-elemental magic damage.",
                         value=30000, rarity=50, damage=8, crit=2, handed=1, subtyp='Fist', unequip=False,
                         off=True)


class GodsHand(Weapon):

    def __init__(self):
        super().__init__(name="GOD'S HAND", description="With the appearance of an ordinary white glove, this weapon is"
                                                        " said to be imbued with the power of God.",
                         value=75000, rarity=60, damage=10, crit=1, handed=1, subtyp='Fist', unequip=False,
                         off=True)


class BronzeDagger(Weapon):

    def __init__(self):
        super().__init__(name="BRONZE DAGGER", description="A bronze knife with a very sharp point and usually two "
                                                           "sharp edges, typically designed or capable of being used as"
                                                           " a thrusting or stabbing weapon.",
                         value=125, rarity=3, damage=1, crit=5, handed=1, subtyp='Dagger', unequip=False,
                         off=True)


class IronDagger(Weapon):

    def __init__(self):
        super().__init__(name="IRON DAGGER", description="An iron knife with a very sharp point and usually two "
                                                         "sharp edges, typically designed or capable of being used as"
                                                         " a thrusting or stabbing weapon.",
                         value=1500, rarity=7, damage=3, crit=4, handed=1, subtyp='Dagger', unequip=False,
                         off=True)


class SteelDagger(Weapon):

    def __init__(self):
        super().__init__(name="STEEL DAGGER", description="A steel knife with a very sharp point and usually two "
                                                          "sharp edges, typically designed or capable of being used as"
                                                          " a thrusting or stabbing weapon.",
                         value=5000, rarity=15, damage=5, crit=3, handed=1, subtyp='Dagger', unequip=False,
                         off=True)


class AdamantiteDagger(Weapon):

    def __init__(self):
        super().__init__(name="ADAMANTITE DAGGER", description="An adamantite knife with a very sharp point and usually"
                                                               " two sharp edges, typically designed or capable of "
                                                               "being used as a thrusting or stabbing weapon.",
                         value=8000, rarity=25, damage=8, crit=2, handed=1, subtyp='Dagger', unequip=False,
                         off=True)


class MithrilDagger(Weapon):

    def __init__(self):
        super().__init__(name="MITHRIL DAGGER", description="An ultra-light blade made from the most prized of all "
                                                            "metals, mithril.",
                         value=20000, rarity=40, damage=10, crit=2, handed=1, subtyp='Dagger', unequip=False,
                         off=True)


class Carnwennan(Weapon):

    def __init__(self):
        super().__init__(name="CARNWENNAN", description="King Arthur's dagger, sometimes described to shroud the user "
                                                        "in shadow.",
                         value=0, rarity=99, damage=15, crit=1, handed=1, subtyp='Dagger', unequip=False,
                         off=True)


class BronzeSword(Weapon):

    def __init__(self):
        super().__init__(name="BRONZE SWORD", description="A weapon with a long bronze blade and a hilt with a hand "
                                                          "guard, used for thrusting or striking and now typically "
                                                          "worn as part of ceremonial dress.",
                         value=125, rarity=3, damage=2, crit=8, handed=1, subtyp='Sword', unequip=False,
                         off=True)


class IronSword(Weapon):

    def __init__(self):
        super().__init__(name="IRON SWORD", description="A weapon with a long iron blade and a hilt with a hand "
                                                        "guard, used for thrusting or striking and now typically worn "
                                                        "as part of ceremonial dress.",
                         value=2000, rarity=8, damage=5, crit=6, handed=1, subtyp='Sword', unequip=False,
                         off=True)


class SteelSword(Weapon):

    def __init__(self):
        super().__init__(name="STEEL SWORD", description="A weapon with a long steel blade and a hilt with a hand "
                                                         "guard, used for thrusting or striking and now typically worn "
                                                         "as part of ceremonial dress.",
                         value=5500, rarity=15, damage=7, crit=5, handed=1, subtyp='Sword', unequip=False,
                         off=True)


class AdamantiteSword(Weapon):

    def __init__(self):
        super().__init__(name="ADAMANTITE SWORD", description="A weapon with a long adamantite blade and a hilt with "
                                                              "a hand guard, used for thrusting or striking and now "
                                                              "typically worn as part of ceremonial dress.",
                         value=10000, rarity=25, damage=10, crit=4, handed=1, subtyp='Sword', unequip=False,
                         off=True)


class MithrilSword(Weapon):

    def __init__(self):
        super().__init__(name="MITHRIL SWORD", description="A weapon with a long mithril blade and a hilt with "
                                                           "a hand guard, used for thrusting or striking and now "
                                                           "typically worn as part of ceremonial dress.",
                         value=22000, rarity=40, damage=12, crit=4, handed=1, subtyp='Sword', unequip=False,
                         off=True)


class Excalibur(Weapon):

    def __init__(self):
        super().__init__(name="EXCALIBUR", description="The legendary sword of King Arthur, bestowed upon him by the "
                                                       "Lady of the Lake.",
                         value=0, rarity=99, damage=18, crit=3, handed=1, subtyp='Sword', unequip=False,
                         off=True)


class BronzeMace(Weapon):

    def __init__(self):
        super().__init__(name="BRONZE MACE", description="A mace is a blunt weapon, a type of club or virge that uses a"
                                                         " heavy head on the end of a handle to deliver powerful "
                                                         "strikes. A mace typically consists of a strong, heavy, wooden"
                                                         " or metal shaft, often reinforced with metal, featuring a "
                                                         "head made of bronze.",
                         value=125, rarity=3, damage=3, crit=10, handed=1, subtyp='Mace', unequip=False,
                         off=True)


class IronMace(Weapon):

    def __init__(self):
        super().__init__(name="IRON MACE", description="A mace is a blunt weapon, a type of club or virge that uses a"
                                                       " heavy head on the end of a handle to deliver powerful "
                                                       "strikes. A mace typically consists of a strong, heavy, wooden"
                                                       " or metal shaft, often reinforced with metal, featuring a "
                                                       "head made of iron.",
                         value=2000, rarity=7, damage=6, crit=9, handed=1, subtyp='Mace', unequip=False,
                         off=True)


class SteelMace(Weapon):

    def __init__(self):
        super().__init__(name="STEEL MACE", description="A mace is a blunt weapon, a type of club or virge that uses a"
                                                        " heavy head on the end of a handle to deliver powerful "
                                                        "strikes. A mace typically consists of a strong, heavy, wooden"
                                                        " or metal shaft, often reinforced with metal, featuring a "
                                                        "head made of steel.",
                         value=4500, rarity=15, damage=8, crit=8, handed=1, subtyp='Mace', unequip=False,
                         off=True)


class AdamantiteMace(Weapon):

    def __init__(self):
        super().__init__(name="ADAMANTITE MACE", description="A mace is a blunt weapon, a type of club or virge that "
                                                             "uses a heavy head on the end of a handle to deliver "
                                                             "powerful strikes. A mace typically consists of a strong, "
                                                             "heavy, wooden or metal shaft, often reinforced with "
                                                             "metal, featuring a head made of adamantite.",
                         value=10000, rarity=25, damage=12, crit=7, handed=1, subtyp='Mace', unequip=False,
                         off=True)


class MithrilMace(Weapon):

    def __init__(self):
        super().__init__(name="MITHRIL MACE", description="A mace is a blunt weapon, a type of club or virge that "
                                                          "uses a heavy head on the end of a handle to deliver "
                                                          "powerful strikes. A mace typically consists of a strong, "
                                                          "heavy, wooden or metal shaft, often reinforced with "
                                                          "metal, featuring a head made of mithril.",
                         value=21000, rarity=40, damage=14, crit=7, handed=1, subtyp='Mace', unequip=False,
                         off=True)


class Mjolnir(Weapon):

    def __init__(self):
        super().__init__(name="MJOLNIR", description="Mjolnir, wielded by the Thunder god Thor, is depicted in Norse "
                                                     "mythology as one of the most fearsome and powerful weapons in "
                                                     "existence, capable of leveling mountains.",
                         value=0, rarity=99, damage=20, crit=6, handed=1, subtyp='Mace', unequip=False,
                         off=True)


class Axe(Weapon):

    def __init__(self):
        super().__init__(name="AXE", description="An axe specifically designed for combat.",
                         value=800, rarity=6, damage=6, crit=8, handed=2, subtyp='Axe', unequip=False,
                         off=False)


class BattleAxe(Weapon):

    def __init__(self):
        super().__init__(name="BATTLE AXE", description="A double-bladed, two-handed melee weapon.",
                         value=4500, rarity=13, damage=10, crit=7, handed=2, subtyp='Axe', unequip=False,
                         off=False)


class GreatAxe(Weapon):

    def __init__(self):
        super().__init__(name="GREAT AXE", description="An enlarged battle axe, providing additional damaging power.",
                         value=10000, rarity=25, damage=12, crit=5, handed=2, subtyp='Axe', unequip=False,
                         off=False)


class AdamantiteAxe(Weapon):

    def __init__(self):
        super().__init__(name="ADAMANTITE AXE", description="A double-bladed, two-handed melee weapon made from "
                                                            "adamantite.",
                         value=15000, rarity=30, damage=14, crit=4, handed=2, subtyp='Axe', unequip=False,
                         off=False)


class MithrilAxe(Weapon):

    def __init__(self):
        super().__init__(name="MITHRIL AXE", description="A double-bladed, two-handed melee weapon made from "
                                                         "mithril.",
                         value=30000, rarity=40, damage=16, crit=4, handed=2, subtyp='Axe', unequip=False,
                         off=False)


class Jarnbjorn(Weapon):

    def __init__(self):
        super().__init__(name="JARNBJORN", description="Legendary axe of Thor Odinson. Old Norse for \"iron bear\".",
                         value=0, rarity=99, damage=23, crit=3, handed=2, subtyp='Axe', unequip=False,
                         off=False)


class Spear(Weapon):

    def __init__(self):
        super().__init__(name="SPEAR", description="A pole weapon consisting of a shaft, usually of wood, with a "
                                                   "pointed head.",
                         value=800, rarity=6, damage=5, crit=6, handed=2, subtyp='Polearm', unequip=False,
                         off=False)


class Lance(Weapon):

    def __init__(self):
        super().__init__(name="LANCE", description="A pole weapon designed for thrusting.",
                         value=3500, rarity=12, damage=9, crit=5, handed=2, subtyp='Polearm', unequip=False,
                         off=False)


class Pike(Weapon):

    def __init__(self):
        super().__init__(name="PIKE", description="A very long pole weapon designed for thrusting.",
                         value=9000, rarity=25, damage=11, crit=4, handed=2, subtyp='Polearm', unequip=False,
                         off=False)


class Halberd(Weapon):

    def __init__(self):
        super().__init__(name="HALBERD", description="A combined spear and battle axe.",
                         value=13000, rarity=30, damage=13, crit=3, handed=2, subtyp='Polearm', unequip=False,
                         off=False)


class Trident(Weapon):

    def __init__(self):
        super().__init__(name="TRIDENT", description="A trident is a 3-pronged spear, the preferred weapon of the Sea"
                                                     " god Poseidon.",
                         value=26000, rarity=40, damage=15, crit=3, handed=2, subtyp='Polearm', unequip=False,
                         off=False)


class Gungnir(Weapon):

    def __init__(self):
        super().__init__(name="GUNGNIR", description="Legendary spear of the god Odin. Old Norse for \"swaying one\".",
                         value=0, rarity=99, damage=22, crit=2, handed=2, subtyp='Polearm', unequip=False,
                         off=False)


class PineStaff(Weapon):

    def __init__(self):
        super().__init__(name="PINE STAFF", description="A pine walking stick wielded in 2 hands and used to strike the"
                                                        "opponent, typically used by magic users.",
                         value=250, rarity=4, damage=2, crit=12, handed=2, subtyp='Staff', unequip=False,
                         off=False)


class OakStaff(Weapon):

    def __init__(self):
        super().__init__(name="OAK STAFF", description="An oak walking stick wielded in 2 hands and used to strike the"
                                                       "opponent, typically used by magic users.",
                         value=800, rarity=6, damage=3, crit=10, handed=2, subtyp='Staff', unequip=False,
                         off=False)


class IronshodStaff(Weapon):

    def __init__(self):
        super().__init__(name="IRONSHOD STAFF", description="An iron walking stick, making it ideal for striking.",
                         value=2500, rarity=8, damage=6, crit=9, handed=2, subtyp='Staff', unequip=False,
                         off=False)


class SerpentStaff(Weapon):

    def __init__(self):
        super().__init__(name="SERPENT STAFF", description="A magic staff, shaped to appear as a snake.",
                         value=5000, rarity=15, damage=10, crit=8, handed=2, subtyp='Staff', unequip=False,
                         off=False)


class HolyStaff(Weapon):

    def __init__(self):
        super().__init__(name="HOLY STAFF", description="A staff that emits a holy light. Only equipable by priests"
                                                        " and archbishops.",
                         value=7500, rarity=20, damage=11, crit=8, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.restricted = ['Priest', 'Archbishop']


class RuneStaff(Weapon):

    def __init__(self):
        super().__init__(name="RUNE STAFF", description="A wooden staff with a magical rune embedded in the handle.",
                         value=10000, rarity=25, damage=12, crit=7, handed=2, subtyp='Staff', unequip=False,
                         off=False)


class MithrilshodStaff(Weapon):

    def __init__(self):
        super().__init__(name="MITHRILSHOD STAFF", description="A mithril walking stick, making it ideal for striking.",
                         value=20000, rarity=40, damage=14, crit=7, handed=2, subtyp='Staff', unequip=False,
                         off=False)


class DragonStaff(Weapon):

    def __init__(self):
        super().__init__(name="DRAGON STAFF", description="A magic staff, shaped to appear as a dragon.",
                         value=0, rarity=99, damage=20, crit=5, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.restriction = ['Berserker', 'Wizard', 'Necromancer', 'Master Monk', 'Lycan', 'Geomancer', 'Soulcatcher']


class PrincessGuard(Weapon):

    def __init__(self):
        super().__init__(name="PRINCESS GUARD", description="A mythical staff from another world.",
                         value=0, rarity=99, damage=21, crit=6, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.restriction = ['Archbishop']


class OakHammer(Weapon):

    def __init__(self):
        super().__init__(name="OAK HAMMER", description="A large, 2-handed hammer made entirely of oak.",
                         value=250, rarity=5, damage=3, crit=11, handed=2, subtyp='Hammer', unequip=False,
                         off=False)


class Maul(Weapon):

    def __init__(self):
        super().__init__(name="MAUL", description="A maul is a tool with a large, flat, often metal head, attached to a"
                                                  " long handle.",
                         value=800, rarity=7, damage=6, crit=9, handed=2, subtyp='Hammer', unequip=False,
                         off=False)


class IronHammer(Weapon):

    def __init__(self):
        super().__init__(name="IRON HAMMER", description="A large, 2-handed hammer made entirely of iron.",
                         value=2500, rarity=10, damage=8, crit=8, handed=2, subtyp='Hammer', unequip=False,
                         off=False)


class EarthHammer(Weapon):

    def __init__(self):
        super().__init__(name="EARTH HAMMER", description="A large, 2-handed hammer infused with the power of Gaia.",
                         value=5000, rarity=14, damage=14, crit=7, handed=2, subtyp='Hammer', unequip=False,
                         off=False)


class WarHammer(Weapon):

    def __init__(self):
        super().__init__(name="WAR HAMMER", description="A war hammer is a late medieval weapon of war primarily used "
                                                        "for close combat action, whose design resembles the hammer. ",
                         value=12000, rarity=32, damage=18, crit=6, handed=2, subtyp='Hammer', unequip=False,
                         off=False)


class GreatMaul(Weapon):

    def __init__(self):
        super().__init__(name="GREAT MAUL", description="A great maul is a tool with a massive, flat, often metal "
                                                        "head, attached to a long handle.",
                         value=27000, rarity=40, damage=20, crit=6, handed=2, subtyp='Hammer', unequip=False,
                         off=False)


class Skullcrusher(Weapon):

    def __init__(self):
        super().__init__(name="SKULLCRUSHER", description="A massive hammer with the power to pulverize an enemy's "
                                                          "skull to powder.",
                         value=0, rarity=99, damage=26, crit=5, handed=2, subtyp='Hammer', unequip=False,
                         off=False)


class Tanto(Weapon):

    def __init__(self):
        super().__init__(name="TANTO", description="",
                         value=15000, rarity=40, damage=8, crit=3, handed=1, subtyp='Ninja', unequip=False,
                         off=True)
        self.restriction = ['Ninja']


class Wakizashi(Weapon):

    def __init__(self):
        super().__init__(name="WAKIZASHI", description="",
                         value=65000, rarity=60, damage=12, crit=2, handed=1, subtyp='Ninja', unequip=False,
                         off=True)
        self.restriction = ['Ninja']


class Ninjato(Weapon):

    def __init__(self):
        super().__init__(name="NINJATO", description="",
                         value=0, rarity=99, damage=18, crit=1, handed=1, subtyp='Ninja', unequip=False,
                         off=True)
        self.restriction = ['Ninja']


class Armor(Item):

    def __init__(self, name, description, value, rarity, armor, subtyp, unequip):
        super().__init__(name, description, value)
        self.rarity = rarity
        self.armor = armor
        self.subtyp = subtyp
        self.unequip = unequip
        self.typ = 'Armor'

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\nArmor: {}".format(self.name, self.description, self.value, self.armor)


class NoArmor(Armor):

    def __init__(self):
        super().__init__(name="NO ARMOR", description="No armor equipped.", value=0, rarity=99, armor=0,
                         subtyp='None', unequip=True)


class Tunic(Armor):

    def __init__(self):
        super().__init__(name="TUNIC", description="A close-fitting short coat as part of a uniform, especially a "
                                                   "police or military uniform.",
                         value=60, rarity=2, armor=1, subtyp='Cloth', unequip=False)


class ClothCloak(Armor):

    def __init__(self):
        super().__init__(name="CLOTH CLOAK", description="An outdoor cloth garment, typically sleeveless, that hangs"
                                                         "loosely from the shoulders.",
                         value=200, rarity=4, armor=2, subtyp='Cloth', unequip=False)


class SilverCloak(Armor):

    def __init__(self):
        super().__init__(name="SILVER CLOAK", description="A cloak weaved with strands of silver to improve protective"
                                                          "power.",
                         value=2500, rarity=8, armor=3, subtyp='Cloth', unequip=False)


class GoldCloak(Armor):

    def __init__(self):
        super().__init__(name="GOLD CLOAK", description="A cloak weaved with strands of gold to improve protective"
                                                        "power.",
                         value=7000, rarity=12, armor=5, subtyp='Cloth', unequip=False)


class CloakEnchantment(Armor):

    def __init__(self):
        super().__init__(name="CLOAK OF ENCHANTMENT", description="A magical cloak that shields the wearer from all "
                                                                  "forms of attack.",
                         value=15000, rarity=35, armor=7, subtyp='Cloth', unequip=False)


class WizardRobe(Armor):

    def __init__(self):
        super().__init__(name="WIZARD'S ROBE", description="A knee-length, long-sleeved robe with an impressive hood "
                                                           "designed to add a mysterious feel to magic users.",
                         value=25000, rarity=40, armor=10, subtyp='Cloth', unequip=False)


class MerlinRobe(Armor):

    def __init__(self):
        super().__init__(name="ROBES OF MERLIN", description="The enchanted robes of Merlin the enchanter.",
                         value=75000, rarity=50, armor=12, subtyp='Cloth', unequip=False)


class PaddedArmor(Armor):

    def __init__(self):
        super().__init__(name="PADDED ARMOR", description="Consists of quilted layers of cloth and batting to provide"
                                                          " some protection from attack.",
                         value=75, rarity=2, armor=2, subtyp='Light', unequip=False)


class LeatherArmor(Armor):

    def __init__(self):
        super().__init__(name="LEATHER ARMOR", description="A protective covering made of animal hide, boiled to make "
                                                           "it tough and rigid and worn over the torso to protect it "
                                                           "from injury.",
                         value=600, rarity=5, armor=3, subtyp='Light', unequip=False)


class Cuirboulli(Armor):

    def __init__(self):
        super().__init__(name="CUIRBOULLI", description="French for \"boiled leather\", this armor has increased "
                                                        "rigidity for add protection",
                         value=3000, rarity=15, armor=4, subtyp='Light', unequip=False)


class StuddedLeather(Armor):

    def __init__(self):
        super().__init__(name="STUDDED LEATHER", description="Leather armor embedded with iron studs to improve "
                                                             "defensive capabilities.",
                         value=12000, rarity=35, armor=8, subtyp='Light', unequip=False)


class StuddedCuirboulli(Armor):

    def __init__(self):
        super().__init__(name="STUDDED CUIRBOULLI", description="Boiled leather armor embedded with iron studs to "
                                                                "improve defensive capabilities.",
                         value=28000, rarity=40, armor=12, subtyp='Light', unequip=False)


class DragonHide(Armor):

    def __init__(self):
        super().__init__(name="DRAGON HIDE", description="Hide armor made from the scales of a red dragon, "
                                                         "inconceivably light for this type of armor.",
                         value=80000, rarity=50, armor=16, subtyp='Light', unequip=False)


class HideArmor(Armor):

    def __init__(self):
        super().__init__(name="HIDE ARMOR", description="A crude armor made from thick furs and pelts.",
                         value=100, rarity=2, armor=3, subtyp='Medium', unequip=False)


class ChainShirt(Armor):

    def __init__(self):
        super().__init__(name="CHAIN SHIRT", description="A type of armor consisting of small metal rings linked "
                                                         "together in a pattern to form a mesh.",
                         value=800, rarity=6, armor=4, subtyp='Medium', unequip=False)


class ScaleMail(Armor):

    def __init__(self):
        super().__init__(name="SCALE MAIL", description="Armor consisting of a coat and leggings of leather covered"
                                                        " with overlapping pieces of metal, mimicking the scales of a "
                                                        "fish.",
                         value=4000, rarity=15, armor=5, subtyp='Medium', unequip=False)


class Breastplate(Armor):

    def __init__(self):
        super().__init__(name="BREASTPLATE", description="Armor consisting of a fitted metal chest piece worn with "
                                                         "supple leather. Although it leaves the legs and arms "
                                                         "relatively unprotected, this armor provides good protection "
                                                         "for the wearer’s vital organs while leaving the wearer "
                                                         "relatively unencumbered.",
                         value=14000, rarity=35, armor=9, subtyp='Medium', unequip=False)


class HalfPlate(Armor):

    def __init__(self):
        super().__init__(name="HALF PLATE", description="Armor consisting of shaped metal plates that cover most of the"
                                                        " wearer’s body. It does not include leg Protection beyond "
                                                        "simple greaves that are attached with leather straps.",
                         value=30000, rarity=40, armor=13, subtyp='Medium', unequip=False)


class Aegis(Armor):

    def __init__(self):
        super().__init__(name="AEGIS BREASTPLATE", description="The breastplate of Zeus, emboldened with a bolt of "
                                                               "lightning.",
                         value=90000, rarity=50, armor=18, subtyp='Medium', unequip=False)


class RingMail(Armor):

    def __init__(self):
        super().__init__(name="RING MAIL", description="Leather armor with heavy rings sewn into it. The rings help "
                                                       "reinforce the armor against blows from Swords and axes.",
                         value=200, rarity=3, armor=4, subtyp='Heavy', unequip=False)


class ChainMail(Armor):

    def __init__(self):
        super().__init__(name="CHAIN MAIL", description="Made of interlocking metal rings, includes a layer of quilted "
                                                        "fabric worn underneath the mail to prevent chafing and to "
                                                        "cushion the impact of blows. The suit includes gauntlets.",
                         value=1000, rarity=7, armor=5, subtyp='Heavy', unequip=False)


class Splint(Armor):

    def __init__(self):
        super().__init__(name="SPLINT MAIL", description="Armor made of narrow vertical strips of metal riveted to a "
                                                         "backing of leather that is worn over cloth padding. Flexible "
                                                         "chain mail protects the joints.",
                         value=6000, rarity=20, armor=7, subtyp='Heavy', unequip=False)


class PlateMail(Armor):

    def __init__(self):
        super().__init__(name="PLATE MAIL", description="Armor consisting of shaped, interlocking metal plates to "
                                                        "cover most of the body.",
                         value=20000, rarity=35, armor=10, subtyp='Heavy', unequip=False)


class FullPlate(Armor):

    def __init__(self):
        super().__init__(name="FULL PLATE", description="Armor consisting of shaped, interlocking metal plates to "
                                                        "cover the entire body. Full plate includes gauntlets, "
                                                        "heavy leather boots, a visored helmet, and thick layers of "
                                                        "padding underneath the armor. Buckles and straps distribute "
                                                        "the weight over the body.",
                         value=40000, rarity=40, armor=15, subtyp='Heavy', unequip=False)


class Genji(Armor):

    def __init__(self):
        super().__init__(name="GENJI ARMOR", description="Mythical armor crafted by an unknown master blacksmith and "
                                                         "embued with protective enchantments that allow the user to "
                                                         "shrug off damage.",
                         value=100000, rarity=50, armor=25, subtyp='Heavy', unequip=False)


class OffHand(Item):
    """
    mod stat depends on the off-hand item; mod for shields is block and spell damage modifier for tomes
    """

    def __init__(self, name, description, value, rarity, mod, subtyp, unequip):
        super().__init__(name, description, value)
        self.rarity = rarity
        self.mod = mod
        self.subtyp = subtyp
        self.unequip = unequip
        self.typ = 'OffHand'

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\nBlock: {}".format(self.name, self.description, self.value, self.mod)


class NoOffHand(OffHand):

    def __init__(self):
        super().__init__(name="NO OFFHAND", description="No off-hand equipped.", value=0, rarity=99, mod=0,
                         subtyp='None', unequip=True)


class Buckler(OffHand):

    def __init__(self):
        super().__init__(name="BUCKLER", description="A small round shield held by a handle or worn on the forearm.",
                         value=25, rarity=2, mod=10, subtyp='Shield', unequip=False)


class WoodShield(OffHand):

    def __init__(self):
        super().__init__(name="WOOD SHIELD", description="A broad piece of wood, held by straps used as a protection "
                                                         "against blows or missiles.",
                         value=100, rarity=4, mod=8, subtyp='Shield', unequip=False)


class BronzeShield(OffHand):

    def __init__(self):
        super().__init__(name="BRONZE SHIELD", description="A broad piece of bronze, held by a handle attached on one "
                                                           "side, used as a protection against blows or missiles.",
                         value=250, rarity=6, mod=7, subtyp='Shield', unequip=False)


class IronShield(OffHand):

    def __init__(self):
        super().__init__(name="IRON SHIELD", description="A broad piece of iron, held by a handle attached on one "
                                                         "side, used as a protection against blows or missiles.",
                         value=500, rarity=10, mod=6, subtyp='Shield', unequip=False)


class SteelShield(OffHand):

    def __init__(self):
        super().__init__(name="STEEL SHIELD", description="A broad piece of steel, held by a handle attached on one "
                                                          "side, used as a protection against blows or missiles.",
                         value=2500, rarity=20, mod=5, subtyp='Shield', unequip=False)


class KiteShield(OffHand):

    def __init__(self):
        super().__init__(name="KITE SHIELD", description="A kite shield is a large, almond-shaped shield rounded at the"
                                                         " top and curving down to a point or rounded point at the "
                                                         "bottom. The term \"kite shield\" is a reference to the "
                                                         "shield's unique shape, and is derived from its supposed "
                                                         "similarity to a flying kite.",
                         value=10000, rarity=35, mod=4, subtyp='Shield', unequip=False)


class TowerShield(OffHand):

    def __init__(self):
        super().__init__(name="TOWER SHIELD", description="A defensive bulwark, an impenetrable wall.",
                         value=25000, rarity=40, mod=3, subtyp='Shield', unequip=False)


class MedusaShield(OffHand):

    def __init__(self):
        super().__init__(name="MEDUSA SHIELD", description="A shield that has been polished to resemble a mirror. Said"
                                                           " to be used to defeat the Gorgon Medusa. Reflects back some"
                                                           " magic.",
                         value=50000, rarity=50, mod=2, subtyp='Shield', unequip=False)


class Book(OffHand):

    def __init__(self):
        super().__init__(name="BOOK", description="A random book.", value=25, rarity=2, mod=2, subtyp='Tome',
                         unequip=False)


class TomeKnowledge(OffHand):

    def __init__(self):
        super().__init__(name="TOME OF KNOWLEDGE", description="A tome containing secrets to enhancing spells.",
                         value=500, rarity=5, mod=5, subtyp='Tome', unequip=False)


class Grimoire(OffHand):

    def __init__(self):
        super().__init__(name="GRIMOIRE", description="A book of magic and invocations.",
                         value=2500, rarity=20, mod=7, subtyp='Tome', unequip=False)


class BookShadows(OffHand):

    def __init__(self):
        super().__init__(name="BOOK OF SHADOWS", description="The Book of Shadows is a book containing religious text "
                                                             "and instructions for magical rituals found within the "
                                                             "Neopagan religion of Wicca, and in many pagan practices.",
                         value=10000, rarity=35, mod=10, subtyp='Tome', unequip=False)


class DragonRouge(OffHand):

    def __init__(self):
        super().__init__(name="DRAGON ROUGE", description="French for \"Red Dragon\", this mythical tome contains "
                                                          "ancient knowledge passed down through the ages.",
                         value=15000, rarity=40, mod=12, subtyp='Tome', unequip=False)


class Vedas(OffHand):

    def __init__(self):
        super().__init__(name="VEDAS", description="A large body of religious texts, consisting of some of the oldest "
                                                   "holy teachings.",
                         value=35000, rarity=45, mod=18, subtyp='Tome', unequip=False)


class Necronomicon(OffHand):

    def __init__(self):
        super().__init__(name="NECRONOMICON", description="The Book of the Dead, a mystical grimoire written by an "
                                                          "unknown author.",
                         value=40000, rarity=50, mod=20, subtyp='Tome', unequip=False)
        self.restriction = ['Warlock', 'Necromancer']


class Magus(OffHand):

    def __init__(self):
        super().__init__(name="MAGUS", description="A book of magical art written by a powerful wizard.",
                         value=75000, rarity=60, mod=30, subtyp='Tome', unequip=False)


class Accessory(Item):
    """
    Each character can equip 1 ring and 1 pendant
    Rings improve physical capabilities (either attack or defense)
    Pendants improve magical capabilities (either magic damage or defense)
    All modifications are considered magical and can't be ignored
    """

    def __init__(self, name, description, value, rarity, mod, subtyp, unequip):
        super().__init__(name, description, value)
        self.rarity = rarity
        self.mod = mod
        self.subtyp = subtyp
        self.unequip = unequip
        self.typ = "Accessory"

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\nMod: {}".format(self.name, self.description, self.value, self.mod)


class NoPendant(Accessory):

    def __init__(self):
        super().__init__(name="NO PENDANT", description="No pendant equipped.", value=0, rarity=99, mod="No Mod",
                         subtyp='Pendant', unequip=True)


class NoRing(Accessory):

    def __init__(self):
        super().__init__(name="NO RING", description="No ring equipped.", value=0, rarity=99, mod="No Mod",
                         subtyp='Ring', unequip=True)


class IronRing(Accessory):

    def __init__(self):
        super().__init__(name="IRON RING", description="A ring that improves the wearer's defense.",
                         value=2000, rarity=12, mod="+5 Physical Defense", subtyp='Ring', unequip=False)


class PowerRing(Accessory):

    def __init__(self):
        super().__init__(name="POWER RING", description="A ring that improves the wearer's attack damage.",
                         value=5000, rarity=18, mod="+5 Physical Damage", subtyp='Ring', unequip=False)


class SilverPendant(Accessory):

    def __init__(self):
        super().__init__(name="SILVER PENDANT", description="A necklace that improves the wearer's magic damage.",
                         value=8000, rarity=22, mod="+5 Magic Damage", subtyp='Pendant', unequip=False)


class RubyPendant(Accessory):

    def __init__(self):
        super().__init__(name="RUBY PENDANT", description="A ruby necklace that improves the wearer's magic damage.",
                         value=1800, rarity=10, mod="+5 Magic Defense", subtyp='Pendant', unequip=False)


class VisionPendant(Accessory):

    def __init__(self):
        super().__init__(name="PENDANT OF VISION", description="A pendant that that gives information about the enemy.",
                         value=1200, rarity=7, mod="Vision", subtyp='Pendant', unequip=False)


class Potion(Item):

    def __init__(self, name, description, value, rarity, subtyp):
        super().__init__(name, description, value)
        self.rarity = rarity
        self.subtyp = subtyp
        self.typ = "Potion"


class HealthPotion(Potion):

    def __init__(self):
        super().__init__(name="HEALTH POTION", description="A potion that restores up to 25% of your health.",
                         value=100, rarity=5, subtyp='Health')
        self.percent = 0.25


class GreatHealthPotion(Potion):

    def __init__(self):
        super().__init__(name="GREAT HEALTH POTION", description="A potion that restores up to 50% of your health.",
                         value=600, rarity=10, subtyp='Health')
        self.percent = 0.50


class SuperHealthPotion(Potion):

    def __init__(self):
        super().__init__(name="SUPER HEALTH POTION", description="A potion that restores up to 75% of your health.",
                         value=3000, rarity=15, subtyp='Health')
        self.percent = 0.75


class MasterHealthPotion(Potion):

    def __init__(self):
        super().__init__(name="MASTER HEALTH POTION", description="A potion that restores up to 100% of your health.",
                         value=10000, rarity=35, subtyp='Health')
        self.percent = 1.0


class ManaPotion(Potion):

    def __init__(self):
        super().__init__(name="MANA POTION", description="A potion that restores up to 25% of your mana.",
                         value=250, rarity=10, subtyp='Mana')
        self.percent = 0.25


class GreatManaPotion(Potion):

    def __init__(self):
        super().__init__(name="GREAT MANA POTION", description="A potion that restores up to 50% of your mana.",
                         value=1500, rarity=20, subtyp='Mana')
        self.percent = 0.50


class SuperManaPotion(Potion):

    def __init__(self):
        super().__init__(name="SUPER MANA POTION", description="A potion that restores up to 75% of your mana.",
                         value=8000, rarity=35, subtyp='Mana')
        self.percent = 0.75


class MasterManaPotion(Potion):

    def __init__(self):
        super().__init__(name="MASTER MANA POTION", description="A potion that restores up to 100% of your mana.",
                         value=20000, rarity=50, subtyp='Mana')
        self.percent = 1.0


class Elixir(Potion):

    def __init__(self):
        super().__init__(name="ELIXIR", description="A potion that restores up to 50% of your health and mana.",
                         value=10000, rarity=35, subtyp='Elixir')
        self.percent = 0.5


class Megalixir(Potion):

    def __init__(self):
        super().__init__(name="MEGALIXIR", description="A potion that restores up to 100% of your health and mana.",
                         value=30000, rarity=75, subtyp='Elixir')
        self.percent = 1.0


class HPPotion(Potion):

    def __init__(self):
        super().__init__(name="HP POTION", description="A potion that permanently increases your strength by 1",
                         value=10000, rarity=20, subtyp='Stat')
        self.stat = 'hp'


class MPPotion(Potion):

    def __init__(self):
        super().__init__(name="MP POTION", description="A potion that permanently increases your strength by 1",
                         value=10000, rarity=20, subtyp='Stat')
        self.stat = 'mp'


class StrengthPotion(Potion):

    def __init__(self):
        super().__init__(name="STRENGTH POTION", description="A potion that permanently increases your strength by 1",
                         value=20000, rarity=35, subtyp='Stat')
        self.stat = 'str'


class IntelPotion(Potion):

    def __init__(self):
        super().__init__(name="INTELLIGENCE POTION", description="A potion that permanently increases your intelligence"
                                                                 " by 1",
                         value=20000, rarity=35, subtyp='Stat')
        self.stat = 'int'


class WisdomPotion(Potion):

    def __init__(self):
        super().__init__(name="WISDOM POTION", description="A potion that permanently increases your wisdom by 1",
                         value=20000, rarity=35, subtyp='Stat')
        self.stat = 'wis'


class ConPotion(Potion):

    def __init__(self):
        super().__init__(name="CONSTITUTION POTION", description="A potion that permanently increases your constitution"
                                                                 " by 1",
                         value=20000, rarity=35, subtyp='Stat')
        self.stat = 'con'


class CharismaPotion(Potion):

    def __init__(self):
        super().__init__(name="CHARISMA POTION", description="A potion that permanently increases your strength by 1",
                         value=20000, rarity=35, subtyp='Stat')
        self.stat = 'cha'


class DexterityPotion(Potion):

    def __init__(self):
        super().__init__(name="DEXTERITY POTION", description="A potion that permanently increases your dexterity by 1",
                         value=20000, rarity=35, subtyp='Stat')
        self.stat = 'dex'


class AardBeing(Potion):

    def __init__(self):
        super().__init__(name="AARD of BEING", description="A potion that permanently increases all stats by 1",
                         value=200000, rarity=100, subtyp='Stat')
        self.stat = 'all'


class Misc(Item):

    def __init__(self, name, description, value, rarity, subtyp):
        super().__init__(name, description, value)
        self.rarity = rarity
        self.subtyp = subtyp
        self.typ = "Misc"


class Key(Misc):
    """
    Opens locked chests
    """
    def __init__(self):
        super().__init__(name="KEY", description="Unlocks a locked chest but is consumed.", value=500, rarity=20,
                         subtyp='Key')


class OldKey(Misc):
    """
    Opens locked doors
    """
    def __init__(self):
        super().__init__(name="OLDKEY", description="Unlocks doors that may lead to either valuable treasure or to "
                                                    "powerful enemies.",
                         value=5000, rarity=40, subtyp='Key')


class Unobtainium(Misc):
    """
    Magical ore that can be used to forge ultimate weapons at the blacksmith; only one in the game
    """
    def __init__(self):
        super().__init__(name="UNOBTAINIUM", description="The legendary ore that has only been theorized. Can be used "
                                                         "to create ultimate weapons.",
                         value=0, rarity=99, subtyp='Special')


# Parameters
items_dict = {'Weapon': {'Dagger': [BronzeDagger, IronDagger, SteelDagger, AdamantiteDagger, MithrilDagger, Carnwennan],
                         'Sword': [BronzeSword, IronSword, SteelSword, AdamantiteSword, MithrilSword, Excalibur],
                         'Mace': [BronzeMace, IronMace, SteelMace, AdamantiteMace, MithrilMace, Mjolnir],
                         'Fist': [BronzeFist, IronFist, SteelFist, AdamantiteFist, MithrilFist, GodsHand],
                         'Axe': [Axe, BattleAxe, GreatAxe, AdamantiteAxe, MithrilAxe, Jarnbjorn],
                         'Polearm': [Spear, Lance, Pike, Halberd, Trident, Gungnir],
                         'Staff': [PineStaff, OakStaff, IronshodStaff, SerpentStaff, HolyStaff, RuneStaff,
                                   MithrilshodStaff, DragonStaff, PrincessGuard],
                         'Hammer': [OakHammer, Maul, IronHammer, EarthHammer, WarHammer, GreatMaul, Skullcrusher],
                         'Ninja Blades': [Tanto, Wakizashi, Ninjato]},
              'OffHand': {'Shield': [WoodShield, BronzeShield, IronShield, SteelShield, KiteShield, TowerShield,
                                     MedusaShield],
                          'Tome': [Book, TomeKnowledge, Grimoire, BookShadows, DragonRouge, Vedas, Necronomicon,
                                   Magus]},
              'Armor': {'Cloth': [Tunic, ClothCloak, SilverCloak, GoldCloak, WizardRobe, CloakEnchantment, MerlinRobe],
                        'Light': [PaddedArmor, LeatherArmor, Cuirboulli, StuddedLeather, StuddedCuirboulli, DragonHide],
                        'Medium': [HideArmor, ChainShirt, ScaleMail, Breastplate, HalfPlate, Aegis],
                        'Heavy': [RingMail, ChainMail, Splint, PlateMail, FullPlate, Genji]},
              'Accessory': {'Ring': [IronRing, PowerRing],
                            'Pendant': [VisionPendant, SilverPendant, RubyPendant]},
              'Potion': {'Health': [HealthPotion, GreatHealthPotion, SuperHealthPotion, MasterHealthPotion],
                         'Mana': [ManaPotion, GreatManaPotion, SuperManaPotion, MasterManaPotion],
                         'Elixir': [Elixir, Megalixir],
                         'Stat': [HPPotion, MPPotion, StrengthPotion, IntelPotion, WisdomPotion, ConPotion,
                                  CharismaPotion, DexterityPotion, AardBeing]},
              'Misc': {'Key': [Key, OldKey, Unobtainium]}}
