###########################################
""" item manager """

# Imports
import random

import spells


# Functions
def reciprocal(x: int) -> float:
    return 1.0 / x


def random_item(z: int):
    """
    Returns a random item based on the given integer
    """

    item_dict = {'Weapon': {'Dagger': [[Dirk, Baselard, Kris, Rondel, Kukri],
                                       [reciprocal(Dirk().rarity), reciprocal(Baselard().rarity),
                                        reciprocal(Kris().rarity), reciprocal(Rondel().rarity),
                                        reciprocal(Kukri().rarity)],
                                       ['1', '1', '2', '3', '4']],
                            'Sword': [[Rapier, Jian, Talwar, Shamshir, Khopesh],
                                      [reciprocal(Rapier().rarity), reciprocal(Jian().rarity),
                                       reciprocal(Talwar().rarity), reciprocal(Shamshir().rarity),
                                       reciprocal(Khopesh().rarity)],
                                      ['1', '1', '2', '3', '4']],
                            'Club': [[Mace, WarHammer, Pernach, Morgenstern],
                                     [reciprocal(Mace().rarity), reciprocal(WarHammer().rarity),
                                      reciprocal(Pernach().rarity), reciprocal(Morgenstern().rarity)],
                                     ['1', '2', '3', '4']],
                            'Fist': [[BrassKnuckles, Cestus, BattleGauntlet, BaghNahk],
                                     [reciprocal(BrassKnuckles().rarity), reciprocal(Cestus().rarity),
                                      reciprocal(BattleGauntlet().rarity), reciprocal(BaghNahk().rarity)],
                                     ['2', '3', '4', '5']],
                            'Ninja Blade': [[Tanto, Wakizashi],
                                            [reciprocal(Tanto().rarity), reciprocal(Wakizashi().rarity)],
                                            ['4', '5']],
                            'Longsword': [[Bastard, Claymore, Zweihander, Changdao, Flamberge],
                                          [reciprocal(Bastard().rarity), reciprocal(Claymore().rarity),
                                           reciprocal(Zweihander().rarity), reciprocal(Changdao().rarity),
                                           reciprocal(Flamberge().rarity)],
                                          ['1', '2', '2', '3', '4']],
                            'Battle Axe': [[Mattock, Broadaxe, DoubleAxe, Parashu, Greataxe],
                                           [reciprocal(Mattock().rarity), reciprocal(Broadaxe().rarity),
                                            reciprocal(DoubleAxe().rarity), reciprocal(Parashu().rarity),
                                            reciprocal(Greataxe().rarity)],
                                           ['1', '2', '2', '3', '4']],
                            'Polearm': [[Voulge, Partisan, Halberd, Naginata, Trident],
                                        [reciprocal(Voulge().rarity), reciprocal(Partisan().rarity),
                                         reciprocal(Halberd().rarity), reciprocal(Naginata().rarity),
                                         reciprocal(Trident().rarity)],
                                        ['1', '2', '2', '3', '4']],
                            'Staff': [[Quarterstaff, Baston, IronshodStaff, SerpentStaff, HolyStaff, RuneStaff,
                                       MithrilshodStaff],
                                      [reciprocal(Quarterstaff().rarity), reciprocal(Baston().rarity),
                                       reciprocal(IronshodStaff().rarity), reciprocal(SerpentStaff().rarity),
                                       reciprocal(HolyStaff().rarity), reciprocal(RuneStaff().rarity),
                                       reciprocal(MithrilshodStaff().rarity)],
                                      ['1', '1', '2', '3', '3', '4', '4']],
                            'Hammer': [[Sledgehammer, Maul, EarthHammer, GreatMaul],
                                       [reciprocal(Sledgehammer().rarity), reciprocal(Maul().rarity),
                                        reciprocal(EarthHammer().rarity), reciprocal(GreatMaul().rarity)],
                                       ['1', '2', '3', '4']],
                            },
                 'OffHand': {'Shield': [[Buckler, Aspis, Targe, Glagwa, KiteShield, Pavise],
                                        [reciprocal(Buckler().rarity), reciprocal(Aspis().rarity),
                                         reciprocal(Targe().rarity), reciprocal(Glagwa().rarity),
                                         reciprocal(KiteShield().rarity), reciprocal(Pavise().rarity)],
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
                               'Pendant': [[VisionPendant, SilverPendant, RubyPendant, AntidotePendant, GorgonPendant,
                                            DharmaPendant],
                                           [reciprocal(VisionPendant().rarity), reciprocal(SilverPendant().rarity),
                                            reciprocal(RubyPendant().rarity), reciprocal(AntidotePendant().rarity),
                                            reciprocal(GorgonPendant().rarity), reciprocal(DharmaPendant().rarity)],
                                           ['1', '2', '2', '2', '4', '4']],
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
                                     ['1', '1', '2', '2', '2', '2', '2', '2', '6']],
                            'Status': [[Antidote, EyeDrop, AntiCoagulant, PhoenixDown],
                                       [reciprocal(Antidote().rarity), reciprocal(EyeDrop().rarity),
                                        reciprocal(AntiCoagulant().rarity), reciprocal(PhoenixDown().rarity)],
                                       ['1', '1', '2', '4']]
                            },
                 'Misc': {'Key': [[Key, OldKey],
                                  [reciprocal(Key().rarity), reciprocal(OldKey().rarity)],
                                  ['1', '2']],
                          'Scroll': [[BlessScroll, SleepScroll, FireScroll, IceScroll, ElectricScroll, WaterScroll,
                                     EarthScroll, WindScroll, ShadowScroll, HolyScroll, RegenScroll, SilenceScroll,
                                     DispelScroll, DeathScroll, SanctuaryScroll, UltimaScroll],
                                     [reciprocal(BlessScroll().rarity), reciprocal(SleepScroll().rarity),
                                      reciprocal(FireScroll().rarity), reciprocal(IceScroll().rarity),
                                      reciprocal(ElectricScroll().rarity), reciprocal(WaterScroll().rarity),
                                      reciprocal(EarthScroll().rarity), reciprocal(WindScroll().rarity),
                                      reciprocal(ShadowScroll().rarity), reciprocal(HolyScroll().rarity),
                                      reciprocal(RegenScroll().rarity), reciprocal(SilenceScroll().rarity),
                                      reciprocal(DispelScroll().rarity), reciprocal(DeathScroll().rarity),
                                      reciprocal(SanctuaryScroll().rarity), reciprocal(UltimaScroll().rarity)],
                                     ['1', '2', '2', '2', '2', '2', '2', '2', '2', '2', '3', '3', '4', '4', '5', '6']]
                          }
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
    name: name of the item (currently capitalized) TODO
    description: description of the item
    value: price in gold; sale price will be half this amount
    rarity: higher number means more rare
    subtyp: the sub-type of the item (i.e. Sword would be a sub-type of Weapon)
    """

    def __init__(self, name, description, value, rarity, subtyp):
        self.name = name
        self.description = description
        self.value = value
        self.rarity = rarity
        self.subtyp = subtyp
        self.restriction = list()
        self.special = False
        self.ultimate = False

    def __str__(self):
        return "{}\n=====\n{}\nValue: {}\n".format(self.name, self.description, self.value)

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
        return "{}\n=====\n{}\nType: {}\nValue: {}\nDamage: {}\nCritical Chance: {}%\n{}-handed".format(
            self.name, self.description, self.subtyp, self.value, self.damage, int(1 / float(self.crit + 1) * 100),
            self.handed)

    def special_effect(self, wielder, target, damage=0, crit=1):
        pass


# One-handed weapons
class NoWeapon(Weapon):

    def __init__(self):
        super().__init__(name="BARE HANDS", description="Nothing but your fists.",
                         value=0, rarity=99, damage=0, crit=10, handed=1, subtyp='None', unequip=True,
                         off=True)


class BrassKnuckles(Weapon):

    def __init__(self):
        super().__init__(name="BRASS KNUCKLES", description="Brass knuckles are pieces of metal shaped to fit around "
                                                            "the knuckles to add weight during hand-to-hand combat.",
                         value=2000, rarity=10, damage=3, crit=6, handed=1, subtyp='Fist', unequip=False,
                         off=True)


class Cestus(Weapon):

    def __init__(self):
        super().__init__(name="CESTUS", description="A cestus is a battle glove that is typically used in gladiatorial "
                                                    "events.",
                         value=7500, rarity=25, damage=4, crit=5, handed=1, subtyp='Fist', unequip=False,
                         off=True)


class BattleGauntlet(Weapon):

    def __init__(self):
        super().__init__(name="BATTLE GAUNTLET", description="A battle gauntlet is a type of glove that protects the "
                                                             "hand and wrist of a combatant, constructed with metal "
                                                             "platings to inflict additional damage.",
                         value=10000, rarity=40, damage=6, crit=3, handed=1, subtyp='Fist', unequip=False,
                         off=True)


class BaghNahk(Weapon):

    def __init__(self):
        super().__init__(name="BAGH NAHK", description="The bagh nahk is a 'fist-load, claw-like' dagger designed to "
                                                       "fit over the knuckles or be concealed under and against the "
                                                       "palm.",
                         value=30000, rarity=50, damage=8, crit=2, handed=1, subtyp='Fist', unequip=False,
                         off=True)


class GodsHand(Weapon):
    """
    Ultimate weapon; deals additional holy damage that won't heal even if the enemy would normally heal with holy damage
    """

    def __init__(self):
        super().__init__(name="GOD'S HAND", description="With the appearance of an ordinary white glove, this weapon is"
                                                        " said to be imbued with the power of God.",
                         value=0, rarity=99, damage=10, crit=1, handed=1, subtyp='Fist', unequip=False,
                         off=True)
        self.special = True
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Holy')
        damage = int(random.randint(damage // 2, damage) * (1 - resist))
        if damage > 0:
            print("Holy light burns {}, dealing {} additional holy damage.".format(target.name, damage))
            target.health -= damage


class Dirk(Weapon):

    def __init__(self):
        super().__init__(name="DIRK", description="A dirk is a long bladed thrusting dagger.",
                         value=125, rarity=3, damage=1, crit=5, handed=1, subtyp='Dagger', unequip=False,
                         off=True)


class Baselard(Weapon):

    def __init__(self):
        super().__init__(name="BASELARD", description="A baselard is a short bladed weapon with an H-shaped hilt.",
                         value=1500, rarity=7, damage=3, crit=4, handed=1, subtyp='Dagger', unequip=False,
                         off=True)


class Kris(Weapon):

    def __init__(self):
        super().__init__(name="KRIS", description="A Kris is an asymmetrical dagger with distinctive blade-patterning "
                                                  "achieved through alternating laminations of iron and nickelous iron,"
                                                  " easily identified by its distinct wavy blade.",
                         value=5000, rarity=15, damage=5, crit=3, handed=1, subtyp='Dagger', unequip=False,
                         off=True)


class Rondel(Weapon):

    def __init__(self):
        super().__init__(name="RONDEL", description="A type of dagger with a stiff-blade, named for the round hand "
                                                    "guard and round or spherical pommel.",
                         value=8000, rarity=25, damage=8, crit=2, handed=1, subtyp='Dagger', unequip=False,
                         off=True)


class Kukri(Weapon):

    def __init__(self):
        super().__init__(name="KUKRI", description="A kukri is a type of dagger with a distinct recurve in its blade.",
                         value=20000, rarity=40, damage=10, crit=2, handed=1, subtyp='Dagger', unequip=False,
                         off=True)


class Carnwennan(Weapon):
    """
    Ultimate weapon; chance to stun target on critical
    """

    def __init__(self):
        super().__init__(name="CARNWENNAN", description="King Arthur's dagger, sometimes described to shroud the user "
                                                        "in shadow.",
                         value=0, rarity=99, damage=15, crit=1, handed=1, subtyp='Dagger', unequip=False,
                         off=True)
        self.special = True
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if crit > 1:
            if random.randint(0, wielder.dex) \
                    > random.randint(target.con // 2, target.con):
                duration = max(1, wielder.dex // 10)
                target.status_effects['Stun'][0] = True
                target.status_effects['Stun'][1] = duration
                print("{} is stunned for {} turns.".format(target.name, duration))


class Rapier(Weapon):

    def __init__(self):
        super().__init__(name="RAPIER", description="A rapier is a slender and sharply pointed two-edged blade with a "
                                                    "protective hilt.",
                         value=125, rarity=3, damage=2, crit=8, handed=1, subtyp='Sword', unequip=False,
                         off=True)


class Jian(Weapon):

    def __init__(self):
        super().__init__(name="JIAN", description="A jian is a double-edged straight sword with a guard that protects "
                                                  "the wielder from opposing blades,",
                         value=2000, rarity=8, damage=5, crit=6, handed=1, subtyp='Sword', unequip=False,
                         off=True)


class Talwar(Weapon):

    def __init__(self):
        super().__init__(name="TALWAR", description="A talwar is curved, single-edged sword with an iron disc hilt and "
                                                    "knucklebow, and a fullered blade.",
                         value=5500, rarity=15, damage=7, crit=5, handed=1, subtyp='Sword', unequip=False,
                         off=True)


class Shamshir(Weapon):

    def __init__(self):
        super().__init__(name="SHAMSHIR", description="A shamshir has a radically curved blade featuring a slim blade "
                                                      "with almost no taper until the very tip.",
                         value=10000, rarity=25, damage=10, crit=4, handed=1, subtyp='Sword', unequip=False,
                         off=True)


class Khopesh(Weapon):

    def __init__(self):
        super().__init__(name="KHOPESH", description="A khopesh is a sickle-shaped sword that evolved from battle axes"
                                                     " and that can be used to disarm an opponent.",
                         value=22000, rarity=40, damage=12, crit=4, handed=1, subtyp='Sword', unequip=False,
                         off=True)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if target.equipment['Weapon']().subtyp != "Natural" and target.equipment['Weapon']().subtyp != "None":
            chance = target.check_mod('luck', luck_factor=10)
            if random.randint(wielder.strength // 2, wielder.strength) \
                    > random.randint(target.dex // 2, target.dex) + chance:
                turns = wielder.strength // 10
                target.status_effects['Disarm'][0] = True
                target.status_effects['Disarm'][1] = turns
                print("{} is disarmed for {} turns.".format(target.name, turns))


class Excalibur(Weapon):
    """
    Ultimate weapon; chance on crit to add a bleed on target
    """

    def __init__(self):
        super().__init__(name="EXCALIBUR", description="The legendary sword of King Arthur, bestowed upon him by the "
                                                       "Lady of the Lake.",
                         value=0, rarity=99, damage=18, crit=3, handed=1, subtyp='Sword', unequip=False,
                         off=True)
        self.special = True
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if crit > 1:
            if random.randint((wielder.strength // 2), wielder.strength) \
                    > random.randint(target.con // 2, target.con):
                duration = max(1, wielder.strength // 10)
                bleed_dmg = max(wielder.strength // 2, damage)
                target.status_effects['Bleed'][0] = True
                target.status_effects['Bleed'][1] = duration
                target.status_effects['Bleed'][2] = bleed_dmg
                print("{} is bleeding for {} turns.".format(target.name, duration))


class Mace(Weapon):

    def __init__(self):
        super().__init__(name="MACE", description="A mace is a blunt weapon, a type of club or virge that uses a heavy"
                                                  " head on the end of a handle to deliver powerful strikes. A mace "
                                                  "typically consists of a strong, heavy, wooden or metal shaft, often"
                                                  " reinforced with metal, featuring a head made of iron.",
                         value=2000, rarity=7, damage=6, crit=9, handed=1, subtyp='Club', unequip=False,
                         off=True)


class WarHammer(Weapon):

    def __init__(self):
        super().__init__(name="WAR HAMMER", description="A war hammer is a club with a head featuring both a blunt end "
                                                        "and a spike on the other end.",
                         value=4500, rarity=15, damage=8, crit=8, handed=1, subtyp='Club', unequip=False,
                         off=True)


class Pernach(Weapon):

    def __init__(self):
        super().__init__(name="PERNACH", description="A pernach is a type of flanged mace used to penetrate even heavy "
                                                     "armor plating.",
                         value=10000, rarity=25, damage=12, crit=7, handed=1, subtyp='Club', unequip=False,
                         off=True)


class Morgenstern(Weapon):

    def __init__(self):
        super().__init__(name="MORGENSTERN", description="A morgenstern, or morning star, is a club-like weapon "
                                                         "consisting of a shaft with an attached ball adorned with "
                                                         "several spikes.",
                         value=21000, rarity=40, damage=14, crit=6, handed=1, subtyp='Club', unequip=False,
                         off=True)


class Mjolnir(Weapon):
    """
    Ultimate weapon; chance to stun on a critical hit based on strength
    """

    def __init__(self):
        super().__init__(name="MJOLNIR", description="Mjolnir, wielded by the Thunder god Thor, is depicted in Norse "
                                                     "mythology as one of the most fearsome and powerful weapons in "
                                                     "existence, capable of leveling mountains.",
                         value=0, rarity=99, damage=20, crit=5, handed=1, subtyp='Club', unequip=False,
                         off=True)
        self.special = True
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if crit > 1:
            if random.randint(0, wielder.strength) \
                    > random.randint(target.con // 2, target.con):
                duration = max(1, wielder.strength // 10)
                target.status_effects['Stun'][0] = True
                target.status_effects['Stun'][1] = duration
                print("{} is stunned for {} turns.".format(target.name, duration))


class Tanto(Weapon):

    def __init__(self):
        super().__init__(name="TANTO", description="A tanto is a double-edged, straight blade, designed primarily as a "
                                                   "stabbing weapon, but the edge can be used for slashing as well.",
                         value=15000, rarity=40, damage=8, crit=3, handed=1, subtyp='Ninja Blade', unequip=False,
                         off=True)
        self.restriction = ['Ninja']


class Wakizashi(Weapon):

    def __init__(self):
        super().__init__(name="WAKIZASHI", description="A wakizashi is a curved, single-edged blade with a narrow "
                                                       "cross-section, producing a deadly strike.",
                         value=65000, rarity=60, damage=12, crit=2, handed=1, subtyp='Ninja Blade', unequip=False,
                         off=True)
        self.restriction = ['Ninja']


class Ninjato(Weapon):
    """
    Ultimate weapon; chance on crit to kill target
    """

    def __init__(self):
        super().__init__(name="NINJATO", description="A mythical blade used by ninjas said to be possessed by a demon "
                                                     "who steals the soul of those slain by the weapon.",
                         value=0, rarity=99, damage=18, crit=1, handed=1, subtyp='Ninja Blade', unequip=False,
                         off=True)
        self.restriction = ['Ninja']
        self.special = True
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if crit > 1:
            resist = target.check_mod('resist', 'Death')
            if resist < 1:
                w_chance = wielder.check_mod('luck', luck_factor=10)
                t_chance = target.check_mod('luck', luck_factor=10)
                if random.randint(0, wielder.dex) + w_chance > \
                        random.randint(target.con // 2, target.con) + t_chance:
                    print("The {} blade rips the soul from {} and they drop dead to the ground!".format(
                        self.name, target.name))


# Two-handed weapons
class Bastard(Weapon):
    """

    """

    def __init__(self):
        super().__init__(name="BASTARD SWORD", description="The bastard sword, also referred to as a hand-and-a-half "
                                                           "sword, is a type of longsword that typically requires two "
                                                           "hands to wield but can be wielded in one if the need "
                                                           "arises.",
                         value=700, rarity=6, damage=5, crit=7, handed=2, subtyp='Longsword', unequip=False, off=False)


class Claymore(Weapon):
    """

    """

    def __init__(self):
        super().__init__(name="CLAYMORE", description="Coming from the Gaelic meaning 'Great Sword', the claymore is a "
                                                      "two-handed sword featuring quillons (crossguards between the "
                                                      "hilt and the blade) are angled in towards the blade and end in "
                                                      "quatrefoils, and a tongue of metal protrudes down either side of"
                                                      " the blade.",
                         value=4200, rarity=13, damage=9, crit=6, handed=2, subtyp='Longsword', unequip=False,
                         off=False)


class Zweihander(Weapon):
    """

    """

    def __init__(self):
        super().__init__(name="ZWEIHANDER", description="German for 'two-handed', the zweihander is a double-edged, "
                                                        "straight blade with a cruciform hilt.",
                         value=9500, rarity=25, damage=11, crit=5, handed=2, subtyp='Longsword', unequip=False,
                         off=False)


class Changdao(Weapon):
    """

    """

    def __init__(self):
        super().__init__(name="CHANGDAO", description="A single-edged two-hander over seven feet long, roughly "
                                                      "translates to 'long saber'.",
                         value=16000, rarity=30, damage=13, crit=4, handed=2, subtyp='Longsword', unequip=False,
                         off=False)


class Flamberge(Weapon):
    """

    """

    def __init__(self):
        super().__init__(name="FLAMBERGE", description="The flamberge is a type of flame-bladed sword featuring a "
                                                       "signature wavy blade.",
                         value=31000, rarity=40, damage=15, crit=3, handed=2, subtyp='Longsword', unequip=False,
                         off=False)


class Executioner(Weapon):
    """

    """

    def __init__(self):
        super().__init__(name="EXECUTIONER'S BLADE", description="Designed specifically for decapitation, the "
                                                                 "Executioner's Blade is a large, two-handed sword with"
                                                                 " a broad blade that is highly efficient at killing.",
                         value=0, rarity=99, damage=21, crit=2, handed=2, subtyp='Longsword', unequip=False, off=False)
        self.special = True
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if crit > 1:
            resist = target.check_mod('resist', 'Death')
            if resist < 1:
                w_chance = wielder.check_mod('luck', luck_factor=10)
                t_chance = target.check_mod('luck', luck_factor=10)
                if random.randint(0, wielder.strength) + w_chance > \
                        random.randint(target.con // 2, target.con) + t_chance:
                    print("The {} decapitates {} and they drop dead to the ground!".format(
                        self.name, target.name))


class Mattock(Weapon):
    """

    """

    def __init__(self):
        super().__init__(name="MATTOCK", description="A mattock is a hand tool used for digging, prying, and chopping, "
                                                     "similar to the pickaxe.",
                         value=800, rarity=6, damage=6, crit=8, handed=2, subtyp='Battle Axe', unequip=False, off=False)


class Broadaxe(Weapon):

    def __init__(self):
        super().__init__(name="BROADAXE", description="A broadaxe is broad-headed axe with a large flaring blade.",
                         value=4500, rarity=13, damage=10, crit=7, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)


class DoubleAxe(Weapon):

    def __init__(self):
        super().__init__(name="DOUBLE AXE", description="The double axe is basically a broadaxe but with a blade on "
                                                        "each side of the axehead.",
                         value=10000, rarity=25, damage=12, crit=5, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)


class Parashu(Weapon):

    def __init__(self):
        super().__init__(name="PARASHU", description="A parashu is a single-bladed battle axe with an arced edge "
                                                     "extending beyond 180 degrees and paired with a spike on the non-"
                                                     "cutting edge.",
                         value=15000, rarity=30, damage=14, crit=4, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)


class Greataxe(Weapon):

    def __init__(self):
        super().__init__(name="GREATAXE", description="A greataxe is a scaled up version of the double axe with greater"
                                                      " mass and killing power.",
                         value=30000, rarity=40, damage=16, crit=4, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)


class Jarnbjorn(Weapon):
    """
    Ultimate weapon; chance on critical hit to cause bleed
    """

    def __init__(self):
        super().__init__(name="JARNBJORN", description="Legendary axe of Thor Odinson. Old Norse for \"iron bear\".",
                         value=0, rarity=99, damage=23, crit=3, handed=2, subtyp='Battle Axe', unequip=False,
                         off=False)
        self.special = True
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if crit > 1:
            if random.randint((wielder.strength // 2), wielder.strength) \
                    > random.randint(target.con // 2, target.con):
                duration = max(1, wielder.strength // 10)
                bleed_dmg = max(wielder.strength // 2, damage)
                target.status_effects['Bleed'][0] = True
                target.status_effects['Bleed'][1] = duration
                target.status_effects['Bleed'][2] = bleed_dmg
                print("{} is bleeding for {} turns.".format(target.name, duration))


class Voulge(Weapon):

    def __init__(self):
        super().__init__(name="VOULGE", description="A voulge is a basic polearm with a narrow single-edged blade "
                                                    "mounted with a socket on a shaft.",
                         value=800, rarity=6, damage=5, crit=6, handed=2, subtyp='Polearm', unequip=False,
                         off=False)


class Partisan(Weapon):

    def __init__(self):
        super().__init__(name="PARTISAN", description="A partisan consists of a spearhead mounted on a long wooden "
                                                      "shaft, with protrusions on the sides which aid in parrying "
                                                      "sword thrusts.",
                         value=3500, rarity=12, damage=9, crit=5, handed=2, subtyp='Polearm', unequip=False,
                         off=False)


class Halberd(Weapon):

    def __init__(self):
        super().__init__(name="HALBERD", description="A halberd is a two-handed pole weapon consisting of an axe blade "
                                                     "topped with a spike mounted on a long shaft.",
                         value=9000, rarity=25, damage=11, crit=4, handed=2, subtyp='Polearm', unequip=False,
                         off=False)


class Naginata(Weapon):

    def __init__(self):
        super().__init__(name="NAGINATA", description="A naginata consists of a wooden or metal pole with a curved "
                                                      "single-edged blade on the end that has a round handguard between"
                                                      " the blade and shaft.",
                         value=13000, rarity=30, damage=13, crit=3, handed=2, subtyp='Polearm', unequip=False,
                         off=False)


class Trident(Weapon):

    def __init__(self):
        super().__init__(name="TRIDENT", description="A trident is a 3-pronged spear, the preferred weapon of the Sea"
                                                     " god Poseidon.",
                         value=26000, rarity=40, damage=15, crit=3, handed=2, subtyp='Polearm', unequip=False,
                         off=False)


class Gungnir(Weapon):
    """
    Ultimate weapon; ignores armor
    """

    def __init__(self):
        super().__init__(name="GUNGNIR", description="Legendary spear of the god Odin. Old Norse for \"swaying one\".",
                         value=0, rarity=99, damage=22, crit=2, handed=2, subtyp='Polearm', unequip=False,
                         off=False)
        self.ignore = True
        self.ultimate = True


class Quarterstaff(Weapon):

    def __init__(self):
        super().__init__(name="QUARTERSTAFF", description="A quarterstaff is a shaft of hardwood about eight feet long"
                                                          " fitted with metal tips on each end.",
                         value=250, rarity=4, damage=2, crit=12, handed=2, subtyp='Staff', unequip=False,
                         off=False)


class Baston(Weapon):

    def __init__(self):
        super().__init__(name="BASTON", description="A baston is a long, light, and flexible staff weapon that is ideal"
                                                    " for speed and precision.",
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
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Holy')
        damage = int(damage * (1 - resist))
        if damage > 0:
            print("The {} deals {} additional holy damage to {}.".format(self.name, damage, target.name))
        elif damage < 0:
            print("{} absorbs the holy damage from the {}.".format(target.name, self.name))
        target.health -= damage


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
    """
    Ultimate weapon; regen mana based on damage
    """

    def __init__(self):
        super().__init__(name="DRAGON STAFF", description="A magic staff, shaped to appear as a dragon.",
                         value=0, rarity=99, damage=20, crit=5, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.restriction = ['Berserker', 'Wizard', 'Necromancer', 'Master Monk', 'Lycan', 'Geomancer', 'Soulcatcher']
        self.special = True
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        mana_heal = random.randint(damage // 2, damage)
        if wielder.mana + mana_heal > wielder.mana_max:
            mana_heal = wielder.mana_max - wielder.mana
        if mana_heal > 0:
            wielder.mana += mana_heal
            print("{}'s mana is regenerated by {}.".format(wielder.name, mana_heal))


class PrincessGuard(Weapon):
    """
    Ultimate weapon; regen health based on damage
    """

    def __init__(self):
        super().__init__(name="PRINCESS GUARD", description="A mythical staff from another world.",
                         value=0, rarity=99, damage=21, crit=6, handed=2, subtyp='Staff', unequip=False,
                         off=False)
        self.restriction = ['Archbishop']
        self.special = True
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        heal = random.randint(damage // 2, damage)
        if wielder.health + heal > wielder.health_max:
            heal = wielder.health_max - wielder.health
        if heal > 0:
            wielder.mana += heal
            print("{}'s heal is regenerated by {}.".format(wielder.name, heal))


class Sledgehammer(Weapon):

    def __init__(self):
        super().__init__(name="SLEDGEHAMMER", description="A sledgehammer is a tool with a large, flat, metal head, "
                                                          "attached to a long handle that gathers momentum during a "
                                                          "swing to apply a large force upon the target.",
                         value=800, rarity=7, damage=6, crit=9, handed=2, subtyp='Hammer', unequip=False,
                         off=False)


class Maul(Weapon):

    def __init__(self):
        super().__init__(name="SPIKE MAUL", description="A spike maul is similar to a sledgehammer except for having a"
                                                        " more narrow face for increased damage.",
                         value=5000, rarity=14, damage=14, crit=7, handed=2, subtyp='Hammer', unequip=False,
                         off=False)


class EarthHammer(Weapon):

    def __init__(self):
        super().__init__(name="EARTH HAMMER", description="A large, 2-handed hammer infused with the power of Gaia.",
                         value=12000, rarity=32, damage=18, crit=6, handed=2, subtyp='Hammer', unequip=False,
                         off=False)
        self.special = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        resist = target.check_mod('resist', 'Earth')
        damage = int(damage * (1 - resist))
        if damage > 0:
            print("The {} deals {} additional earth damage to {}.".format(self.name, damage, target.name))
        elif damage < 0:
            print("{} absorbs the earth damage from the {}.".format(target.name, self.name))
        target.health -= damage


class GreatMaul(Weapon):

    def __init__(self):
        super().__init__(name="GREAT MAUL", description="A great maul looks similar to a sledgehammer but is "
                                                        "significantly larger in all aspects.",
                         value=27000, rarity=40, damage=20, crit=6, handed=2, subtyp='Hammer', unequip=False,
                         off=False)


class Skullcrusher(Weapon):
    """
    Ultimate weapon; chance to stun on critical based on strength
    """

    def __init__(self):
        super().__init__(name="SKULLCRUSHER", description="A massive hammer with the power to pulverize an enemy's "
                                                          "skull to powder.",
                         value=0, rarity=99, damage=26, crit=5, handed=2, subtyp='Hammer', unequip=False,
                         off=False)
        self.special = True
        self.ultimate = True

    def special_effect(self, wielder, target, damage=0, crit=1):
        if crit > 1:
            if random.randint(0, wielder.strength) \
                    > random.randint(target.con // 2, target.con):
                duration = max(1, wielder.strength // 10)
                target.status_effects['Stun'][0] = True
                target.status_effects['Stun'][1] = duration
                print("{} is stunned for {} turns.".format(target.name, duration))


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
        return "{}\n=====\n{}\nType: {}\nValue: {}\nArmor: {}".format(self.name, self.description, self.subtyp,
                                                                      self.value, self.armor)

    def special_effect(self, wearer, attacker):
        pass


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


class NoOffHand(OffHand):

    def __init__(self):
        super().__init__(name="NO OFFHAND", description="No off-hand equipped.", value=0, rarity=99, mod=0,
                         subtyp='None', unequip=True)


class Buckler(OffHand):

    def __init__(self):
        super().__init__(name="BUCKLER", description="A small round shield held by a handle or worn on the forearm.",
                         value=25, rarity=2, mod=10, subtyp='Shield', unequip=False)

    def __str__(self):
        return "{}\n=====\n{}\nType: {}\nValue: {}\nBlock: {}%".format(
            self.name, self.description, self.subtyp, self.value, int(round(1 / self.mod, 2) * 100))


class Aspis(OffHand):

    def __init__(self):
        super().__init__(name="ASPIS", description="An aspis is a heavy wooden shield with a handle at the edge and is "
                                                   "strapped to the forearm for greater mobility.",
                         value=100, rarity=4, mod=8, subtyp='Shield', unequip=False)

    def __str__(self):
        return "{}\n=====\n{}\nType: {}\nValue: {}\nBlock: {}%".format(
            self.name, self.description, self.subtyp, self.value, int(round(1 / self.mod, 2) * 100))


class Targe(OffHand):

    def __init__(self):
        super().__init__(name="TARGE", description="A targe is a circular, concave shield fitted with straps on the "
                                                   "inside to be attached to the forearm, featuring metal studs on the "
                                                   "face for durability and additional offensive power.",
                         value=500, rarity=10, mod=6, subtyp='Shield', unequip=False)

    def __str__(self):
        return "{}\n=====\n{}\nType: {}\nValue: {}\nBlock: {}%".format(
            self.name, self.description, self.subtyp, self.value, int(round(1 / self.mod, 2) * 100))


class Glagwa(OffHand):

    def __init__(self):
        super().__init__(name="GLAGWA", description="A glagwa is a bell-shaped shield made from iron and covered with "
                                                    "leather for improved durability.",
                         value=2500, rarity=20, mod=5, subtyp='Shield', unequip=False)

    def __str__(self):
        return "{}\n=====\n{}\nType: {}\nValue: {}\nBlock: {}%".format(
            self.name, self.description, self.subtyp, self.value, int(round(1 / self.mod, 2) * 100))


class KiteShield(OffHand):

    def __init__(self):
        super().__init__(name="KITE SHIELD", description="A kite shield is a large, almond-shaped shield rounded at the"
                                                         " top and curving down to a point or rounded point at the "
                                                         "bottom. The term \"kite shield\" is a reference to the "
                                                         "shield's unique shape, and is derived from its supposed "
                                                         "similarity to a flying kite.",
                         value=10000, rarity=35, mod=4, subtyp='Shield', unequip=False)

    def __str__(self):
        return "{}\n=====\n{}\nType: {}\nValue: {}\nBlock: {}%".format(
            self.name, self.description, self.subtyp, self.value, int(round(1 / self.mod, 2) * 100))


class Pavise(OffHand):

    def __init__(self):
        super().__init__(name="PAVISE", description="A pavise is an oblong shield similar to a tower shield that "
                                                    "features a spike at the bottom to hold it in place to provide full"
                                                    " body protection.",
                         value=25000, rarity=40, mod=3, subtyp='Shield', unequip=False)

    def __str__(self):
        return "{}\n=====\n{}\nType: {}\nValue: {}\nBlock: {}%".format(
            self.name, self.description, self.subtyp, self.value, int(round(1 / self.mod, 2) * 100))


class MedusaShield(OffHand):

    def __init__(self):
        super().__init__(name="MEDUSA SHIELD", description="A shield that has been polished to resemble a mirror. Said"
                                                           " to be used to defeat the Gorgon Medusa. Reflects back some"
                                                           " magic.",
                         value=50000, rarity=50, mod=2, subtyp='Shield', unequip=False)

    def __str__(self):
        return "{}\n=====\n{}\nType: {}\nValue: {}\nBlock: {}%".format(
            self.name, self.description, self.subtyp, self.value, int(round(1 / self.mod, 2) * 100))


class Book(OffHand):

    def __init__(self):
        super().__init__(name="BOOK", description="A random book.", value=25, rarity=2, mod=2, subtyp='Tome',
                         unequip=False)

    def __str__(self):
        return "{}\n=====\n{}\nType: {}\nValue: {}\nSpell Damage Mod: {}".format(
            self.name, self.description, self.subtyp, self.value, self.mod)


class TomeKnowledge(OffHand):

    def __init__(self):
        super().__init__(name="TOME OF KNOWLEDGE", description="A tome containing secrets to enhancing spells.",
                         value=500, rarity=5, mod=5, subtyp='Tome', unequip=False)

    def __str__(self):
        return "{}\n=====\n{}\nType: {}\nValue: {}\nSpell Damage Mod: {}".format(
            self.name, self.description, self.subtyp, self.value, self.mod)


class Grimoire(OffHand):

    def __init__(self):
        super().__init__(name="GRIMOIRE", description="A book of magic and invocations.",
                         value=2500, rarity=20, mod=7, subtyp='Tome', unequip=False)

    def __str__(self):
        return "{}\n=====\n{}\nType: {}\nValue: {}\nSpell Damage Mod: {}".format(
            self.name, self.description, self.subtyp, self.value, self.mod)


class BookShadows(OffHand):

    def __init__(self):
        super().__init__(name="BOOK OF SHADOWS", description="The Book of Shadows is a book containing religious text "
                                                             "and instructions for magical rituals found within the "
                                                             "Neopagan religion of Wicca, and in many pagan practices.",
                         value=10000, rarity=35, mod=10, subtyp='Tome', unequip=False)

    def __str__(self):
        return "{}\n=====\n{}\nType: {}\nValue: {}\nSpell Damage Mod: {}".format(
            self.name, self.description, self.subtyp, self.value, self.mod)


class DragonRouge(OffHand):

    def __init__(self):
        super().__init__(name="DRAGON ROUGE", description="French for \"Red Dragon\", this mythical tome contains "
                                                          "ancient knowledge passed down through the ages.",
                         value=15000, rarity=40, mod=12, subtyp='Tome', unequip=False)

    def __str__(self):
        return "{}\n=====\n{}\nType: {}\nValue: {}\nSpell Damage Mod: {}".format(
            self.name, self.description, self.subtyp, self.value, self.mod)


class Vedas(OffHand):

    def __init__(self):
        super().__init__(name="VEDAS", description="A large body of religious texts, consisting of some of the oldest "
                                                   "holy teachings.",
                         value=35000, rarity=45, mod=18, subtyp='Tome', unequip=False)

    def __str__(self):
        return "{}\n=====\n{}\nType: {}\nValue: {}\nSpell Damage Mod: {}".format(
            self.name, self.description, self.subtyp, self.value, self.mod)


class Necronomicon(OffHand):

    def __init__(self):
        super().__init__(name="NECRONOMICON", description="The Book of the Dead, a mystical grimoire written by an "
                                                          "unknown author.",
                         value=40000, rarity=50, mod=20, subtyp='Tome', unequip=False)
        self.restriction = ['Warlock', 'Necromancer']

    def __str__(self):
        return "{}\n=====\n{}\nType: {}\nValue: {}\nSpell Damage Mod: {}".format(
            self.name, self.description, self.subtyp, self.value, self.mod)


class Magus(OffHand):

    def __init__(self):
        super().__init__(name="MAGUS", description="A book of magical art written by a powerful wizard.",
                         value=75000, rarity=60, mod=30, subtyp='Tome', unequip=False)

    def __str__(self):
        return "{}\n=====\n{}\nType: {}\nValue: {}\nSpell Damage Mod: {}".format(
            self.name, self.description, self.subtyp, self.value, self.mod)


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
        return "{}\n=====\n{}\nValue: {}\nMod: {}".format(self.name, self.description, self.value, self.mod)


class NoRing(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="NO RING", description="No ring equipped.", value=0, rarity=99, mod="No Mod",
                         subtyp='None', unequip=True)


class IronRing(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="IRON RING", description="A ring that improves the wearer's defense.",
                         value=2000, rarity=12, mod="+5 Physical Defense", subtyp="Ring", unequip=False)


class PowerRing(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="POWER RING", description="A ring that improves the wearer's attack damage.",
                         value=5000, rarity=18, mod="+5 Physical Damage", subtyp="Ring", unequip=False)


class NoPendant(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="NO PENDANT", description="No pendant equipped.", value=0, rarity=99, mod="No Mod",
                         subtyp="None", unequip=True)


class VisionPendant(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="PENDANT OF VISION", description="A pendant that that gives information about the enemy.",
                         value=1200, rarity=7, mod="Vision", subtyp="Pendant", unequip=False)


class RubyPendant(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="RUBY PENDANT", description="A ruby necklace that improves the wearer's magic damage.",
                         value=1800, rarity=10, mod="+5 Magic Defense", subtyp="Pendant", unequip=False)


class SilverPendant(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="SILVER PENDANT", description="A necklace that improves the wearer's magic damage.",
                         value=8000, rarity=22, mod="+5 Magic Damage", subtyp="Pendant", unequip=False)


class AntidotePendant(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="ANTIDOTE PENDANT", description="Protects the wearer against the effects of poison.",
                         value=2500, rarity=15, mod="Poison", subtyp="Pendant", unequip=False)


class GorgonPendant(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="GORGON PENDANT", description="Made from the scale of a Gorgon, this ring protects the "
                                                            "wearer against petrification.",
                         value=20000, rarity=35, mod="Stone", subtyp="Pendant", unequip=False)


class DharmaPendant(Accessory):
    """

    """

    def __init__(self):
        super().__init__(name="DHARMA PENDANT", description="No need to fear the reaper while wearing this ring, giving"
                                                            " the wearer immunity against instant death.",
                         value=25000, rarity=40, mod="Death", subtyp="Pendant", unequip=False)


class Potion(Item):
    """
    typ: the item type; 'Potion' for this class
    """

    def __init__(self, name, description, value, rarity, subtyp):
        super().__init__(name, description, value, rarity, subtyp)
        self.typ = "Potion"


class HealthPotion(Potion):

    def __init__(self):
        super().__init__(name="HEALTH POTION", description="A potion that restores up to 25% of your health.",
                         value=100, rarity=5, subtyp='Health')
        self.percent = 0.25
        self.item = HealthPotion

    def use(self, user, target=None, tile=None):
        if user.health == user.health_max:
            print("You are already at full health.")
            return False
        user.modify_inventory(self.item, num=1, subtract=True)
        if user.state != 'fight':
            heal = int(user.health_max * self.percent)
        else:
            rand_heal = int(user.health_max * self.percent)
            heal = random.randint(rand_heal // 2, rand_heal) * max(1, user.check_mod('luck', luck_factor=12))
        print("The potion healed you for {} life.".format(heal))
        user.health += heal
        if user.health >= user.health_max:
            user.health = user.health_max
            print("You are at max health.")
        return True


class GreatHealthPotion(HealthPotion):

    def __init__(self):
        super().__init__()
        self.name = "GREAT HEALTH POTION"
        self.description = "A potion that restores up to 50% of your health."
        self.value = 600
        self.rarity = 10
        self.percent = 0.50
        self.item = GreatHealthPotion


class SuperHealthPotion(HealthPotion):

    def __init__(self):
        super().__init__()
        self.name = "SUPER HEALTH POTION"
        self.description = "A potion that restores up to 75% of your health."
        self.value = 3000
        self.rarity = 15
        self.percent = 0.75
        self.item = SuperHealthPotion


class MasterHealthPotion(HealthPotion):

    def __init__(self):
        super().__init__()
        self.name = "MASTER HEALTH POTION"
        self.description = "A potion that restores up to 100% of your health."
        self.value = 10000
        self.rarity = 35
        self.percent = 1.0
        self.item = MasterHealthPotion


class ManaPotion(Potion):

    def __init__(self):
        super().__init__(name="MANA POTION", description="A potion that restores up to 25% of your mana.",
                         value=250, rarity=10, subtyp='Mana')
        self.percent = 0.25
        self.item = ManaPotion

    def use(self, user, target=None, tile=None):
        if user.mana == user.mana_max:
            print("You are already at full mana.")
            return False
        user.modify_inventory(self.item, num=1, subtract=True)
        if user.state != 'fight':
            heal = int(user.mana_max * self.percent)
        else:
            rand_res = int(user.mana_max * self.percent)
            heal = random.randint(rand_res // 2, rand_res) * max(1, user.check_mod('luck', luck_factor=12))
        print("The potion restored {} mana points.".format(heal))
        user.mana += heal
        if user.mana >= user.mana_max:
            user.mana = user.mana_max
            print("You are at full mana.")
        return True


class GreatManaPotion(ManaPotion):

    def __init__(self):
        super().__init__()
        self.name = "GREAT MANA POTION"
        self.description = "A potion that restores up to 50% of your mana."
        self.value = 1500
        self.rarity = 20
        self.percent = 0.50
        self.item = GreatManaPotion


class SuperManaPotion(ManaPotion):

    def __init__(self):
        super().__init__()
        self.name = "SUPER MANA POTION"
        self.description = "A potion that restores up to 75% of your mana."
        self.value = 8000
        self.rarity = 35
        self.percent = 0.75
        self.item = SuperManaPotion


class MasterManaPotion(ManaPotion):

    def __init__(self):
        super().__init__()
        self.name = "MASTER MANA POTION"
        self.description = "A potion that restores up to 100% of your mana."
        self.value = 20000
        self.rarity = 50
        self.percent = 1.0
        self.item = MasterManaPotion


class Elixir(Potion):

    def __init__(self):
        super().__init__(name="ELIXIR", description="A potion that restores up to 50% of your health and mana.",
                         value=10000, rarity=35, subtyp='Elixir')
        self.percent = 0.5
        self.item = Elixir

    def use(self, user, target=None, tile=None):
        if user.health == user.health_max and user.mana == user.mana_max:
            print("You are already at full health and mana.")
            return False
        user.modify_inventory(self.item, num=1, subtract=True)
        if user.state != 'fight':
            health_heal = int(user.health_max * self.percent)
            mana_heal = int(user.mana_max * self.percent)
        else:
            rand_heal = int(user.health_max * self.percent)
            rand_res = int(user.mana_max * self.percent)
            health_heal = random.randint(rand_heal // 2, rand_heal) * max(1, user.check_mod('luck', luck_factor=12))
            mana_heal = random.randint(rand_res // 2, rand_res) * max(1, user.check_mod('luck', luck_factor=12))
        print("The potion restored {} health points and {} mana points.".format(health_heal, mana_heal))
        user.health += health_heal
        user.mana += mana_heal
        if user.health >= user.health_max:
            user.health = user.health_max
            print("You are at max health.")
        if user.mana >= user.mana_max:
            user.mana = user.mana_max
            print("You are at full mana.")
        return True


class Megalixir(Elixir):

    def __init__(self):
        super().__init__()
        self.name = "MEGALIXIR"
        self.description = "A potion that restores up to 100% of your health and mana."
        self.value = 30000
        self.rarity = 60
        self.percent = 1.0
        self.item = Megalixir


class HPPotion(Potion):

    def __init__(self):
        super().__init__(name="HP POTION", description="A potion that permanently increases your max health by 10.",
                         value=10000, rarity=20, subtyp='Stat')
        self.mod = 10

    def use(self, user, target=None, tile=None):
        user.modify_inventory(HPPotion, num=1, subtract=True)
        user.health_max += self.mod
        print("{}'s HP has increased by {}!".format(user.name, self.mod))
        return True


class MPPotion(Potion):

    def __init__(self):
        super().__init__(name="MP POTION", description="A potion that permanently increases your max mana by 10.",
                         value=10000, rarity=20, subtyp='Stat')
        self.mod = 10

    def use(self, user, target=None, tile=None):
        user.modify_inventory(MPPotion, num=1, subtract=True)
        user.mana_max += self.mod
        print("{}'s MP has increased by {}!".format(user.name, self.mod))
        return True


class StrengthPotion(Potion):

    def __init__(self):
        super().__init__(name="STRENGTH POTION", description="A potion that permanently increases your strength by 1.",
                         value=20000, rarity=35, subtyp='Stat')
        
    def use(self, user, target=None, tile=None):
        user.modify_inventory(StrengthPotion, num=1, subtract=True)
        user.strength += 1
        print("{}'s strength has increased by 1!".format(user.name))
        return True


class IntelPotion(Potion):

    def __init__(self):
        super().__init__(name="INTELLIGENCE POTION", description="A potion that permanently increases your intelligence"
                                                                 " by 1.",
                         value=20000, rarity=35, subtyp='Stat')

    def use(self, user, target=None, tile=None):
        user.modify_inventory(IntelPotion, num=1, subtract=True)
        user.intel += 1
        print("{}'s intelligence has increased by 1!".format(user.name))
        return True
    

class WisdomPotion(Potion):

    def __init__(self):
        super().__init__(name="WISDOM POTION", description="A potion that permanently increases your wisdom by 1.",
                         value=20000, rarity=35, subtyp='Stat')

    def use(self, user, target=None, tile=None):
        user.modify_inventory(WisdomPotion, num=1, subtract=True)
        user.wisdom += 1
        print("{}'s wisdom has increased by 1!".format(user.name))
        return True
    

class ConPotion(Potion):

    def __init__(self):
        super().__init__(name="CONSTITUTION POTION", description="A potion that permanently increases your constitution"
                                                                 " by 1.",
                         value=20000, rarity=35, subtyp='Stat')

    def use(self, user, target=None, tile=None):
        user.modify_inventory(ConPotion, num=1, subtract=True)
        user.con += 1
        print("{}'s constitution has increased by 1!".format(user.name))
        return True


class CharismaPotion(Potion):

    def __init__(self):
        super().__init__(name="CHARISMA POTION", description="A potion that permanently increases your charisma by 1.",
                         value=20000, rarity=35, subtyp='Stat')

    def use(self, user, target=None, tile=None):
        user.modify_inventory(CharismaPotion, num=1, subtract=True)
        user.charisma += 1
        print("{}'s charisma has increased by 1!".format(user.name))
        return True
    

class DexterityPotion(Potion):

    def __init__(self):
        super().__init__(name="DEXTERITY POTION", description="A potion that permanently increases your dexterity by "
                                                              "1.",
                         value=20000, rarity=35, subtyp='Stat')

    def use(self, user, target=None, tile=None):
        user.modify_inventory(DexterityPotion, num=1, subtract=True)
        user.dex += 1
        print("{}'s dexterity has increased by 1!".format(user.name))
        return True
    

class AardBeing(Potion):

    def __init__(self):
        super().__init__(name="AARD of BEING", description="A potion that permanently increases all stats by 1.",
                         value=200000, rarity=75, subtyp='Stat')

    def use(self, user, target=None, tile=None):
        user.modify_inventory(AardBeing, num=1, subtract=True)
        user.strength += 1
        user.intel += 1
        user.wisdom += 1
        user.con += 1
        user.charisma += 1
        user.dex += 1
        print("All of {}'s stats have been increased by 1!".format(user.name))
        return True
    

class Status(Potion):
    """
    
    """
    
    def __init__(self):
        super().__init__(name="Status", description="Base class for status items.",
                         value=0, rarity=99, subtyp="Status")
        self.status = None
        self.item = Status

    def use(self, user, target=None, tile=None):
        if not user.status_effects[self.status][0]:
            print("You are not affected by {}.".format(self.status.lower()))
            return False
        user.modify_inventory(self.item, num=1, subtract=True)
        user.status_effects[self.status][0] = False
        print("You have been cured of {}.".format(self.status.lower()))
        return True
    
    
class Antidote(Status):
    """

    """
    def __init__(self):
        super().__init__()
        self.name = "ANTIDOTE"
        self.description = "A potion that will cure poison."
        self.value = 250
        self.rarity = 10
        self.status = 'Poison'
        self.item = Antidote


class EyeDrop(Status):
    """

    """

    def __init__(self):
        super().__init__()
        self.name = "EYE DROP"
        self.description = "Eye drops that will cure blindness."
        self.value = 250
        self.rarity = 10
        self.status = 'Blind'
        self.item = EyeDrop


class AntiCoagulant(Status):
    """

    """

    def __init__(self):
        super().__init__()
        self.name = "ANTI-COAGULANT"
        self.description = "Anti-coagulants will cure bleeding."
        self.value = 1000
        self.rarity = 20
        self.status = 'Bleed'
        self.item = AntiCoagulant


class PhoenixDown(Status):
    """

    """

    def __init__(self):
        super().__init__()
        self.name = "PHOENIX DOWN"
        self.description = "A potion that will cure doom status."
        self.value = 15000
        self.rarity = 35
        self.status = 'Doom'
        self.item = PhoenixDown


class Misc(Item):
    """
    typ: the item type; 'Misc' for this class
    """

    def __init__(self, name, description, value, rarity, subtyp):
        super().__init__(name, description, value, rarity, subtyp)
        self.typ = "Misc"


class Key(Misc):
    """
    Opens locked chests
    """

    def __init__(self):
        super().__init__(name="KEY", description="Unlocks a locked chest but is consumed.", value=500, rarity=20,
                         subtyp='Key')

    def use(self, user, target=None, tile=None):
        user.modify_inventory(Key, num=1, subtract=True)
        tile.locked = False
        print("{} unlocks the chest.".format(user.name))
        return True


class OldKey(Misc):
    """
    Opens locked doors
    """

    def __init__(self):
        super().__init__(name="OLDKEY", description="Unlocks doors that may lead to either valuable treasure or to "
                                                    "powerful enemies.",
                         value=50000, rarity=40, subtyp='Key')

    def use(self, user, target=None, tile=None):
        user.modify_inventory(OldKey, num=1, subtract=True)
        tile.locked = False
        print("{} unlocks the door.".format(user.name))
        return True


class Scroll(Misc):
    """
    Scrolls allow for a one-time use of a spell; scrolls can only be used in combat
    """

    def __init__(self):
        super().__init__(name="SCROLL", description="Base class for scrolls.", value=0, rarity=99, subtyp='Scroll')
        self.spell = None
        self.item = Scroll

    def use(self, user, target=None, tile=None):
        user.modify_inventory(self.item, num=1, subtract=True)
        print("{} uses {}.".format(user.name, self.name))
        self.spell().cast(user, target)
        return True


class BlessScroll(Scroll):
    """
    Bless
    """

    def __init__(self):
        super().__init__()
        self.name = "BLESS SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast Bless, which increases " \
                           "attack damage for several turns. The scroll will be consumed upon use."
        self.value = 1000
        self.rarity = 15
        self.spell = spells.Bless
        self.item = BlessScroll


class SleepScroll(Scroll):
    """
    Sleep
    """

    def __init__(self):
        super().__init__()
        self.name = "SLEEP SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast Sleep, which can put the " \
                           "enemy to sleep. The scroll will be consumed upon use."
        self.value = 2000
        self.rarity = 25
        self.spell = spells.Sleep
        self.item = SleepScroll


class FireScroll(Scroll):
    """
    Firebolt
    """

    def __init__(self):
        super().__init__()
        self.name = "FIRE SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the fire spell Firebolt. " \
                           "The scroll will be consumed upon use."
        self.value = 2500
        self.rarity = 30
        self.spell = spells.Firebolt
        self.item = FireScroll


class IceScroll(Scroll):
    """
    Ice Lance
    """

    def __init__(self):
        super().__init__()
        self.name = "ICE SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the ice spell Ice Lance. " \
                           "The scroll will be consumed upon use."
        self.value = 2500
        self.rarity = 30
        self.spell = spells.IceLance
        self.item = IceScroll


class ElectricScroll(Scroll):
    """
    Shock
    """

    def __init__(self):
        super().__init__()
        self.name = "ELECTRIC SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the electric spell Shock." \
                           " The scroll will be consumed upon use."
        self.value = 2500
        self.rarity = 30
        self.spell = spells.Shock
        self.item = ElectricScroll


class WaterScroll(Scroll):
    """
    Water Jet
    """

    def __init__(self):
        super().__init__()
        self.name = "WATER SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the water spell Water Jet" \
                           ". The scroll will be consumed upon use."
        self.value = 2500
        self.rarity = 30
        self.spell = spells.WaterJet
        self.item = WaterScroll


class EarthScroll(Scroll):
    """
    Tremor
    """

    def __init__(self):
        super().__init__()
        self.name = "EARTH SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the earth spell Tremor. " \
                           "The scroll will be consumed upon use."
        self.value = 2500
        self.rarity = 30
        self.spell = spells.Tremor
        self.item = EarthScroll


class WindScroll(Scroll):
    """
    Gust
    """

    def __init__(self):
        super().__init__()
        self.name = "WIND SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the wind spell Gust. The" \
                           " scroll will be consumed upon use."
        self.value = 2500
        self.rarity = 30
        self.spell = spells.Gust
        self.item = WindScroll


class ShadowScroll(Scroll):
    """
    Shadow Bolt
    """

    def __init__(self):
        super().__init__()
        self.name = "SHADOW SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the shadow spell Shadow" \
                           " Bolt. The scroll will be consumed upon use."
        self.value = 2500
        self.rarity = 30
        self.spell = spells.ShadowBolt
        self.item = ShadowScroll


class HolyScroll(Scroll):
    """
    Holy
    """

    def __init__(self):
        super().__init__()
        self.name = "HOLY SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the holy spell Holy. The" \
                           " scroll will be consumed upon use."
        self.value = 2500
        self.rarity = 30
        self.spell = spells.Holy
        self.item = HolyScroll


class RegenScroll(Scroll):
    """
    Regen
    """

    def __init__(self):
        super().__init__()
        self.name = "REGEN SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the heal spell Regen, " \
                           "which can heal the target over time. The scroll will be consumed upon use."
        self.value = 5000
        self.rarity = 35
        self.spell = spells.Regen
        self.item = RegenScroll


class SilenceScroll(Scroll):
    """
    Silence
    """

    def __init__(self):
        super().__init__()
        self.name = "SILENCE SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast Silence, which can " \
                           "prevent an target from casting spell for a time. The scroll will be consumed upon use."
        self.value = 5000
        self.rarity = 35
        self.spell = spells.Silence
        self.item = SilenceScroll


class DispelScroll(Scroll):
    """
    Dispel
    """

    def __init__(self):
        super().__init__()
        self.name = "DISPEL SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast Dispel, which can remove " \
                           "all positive status effects from the target. The scroll will be consumed upon use."
        self.value = 7500
        self.rarity = 40
        self.spell = spells.Dispel
        self.item = DispelScroll


class DeathScroll(Scroll):
    """
    Desoul
    """

    def __init__(self):
        super().__init__()
        self.name = "DEATH SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast Desoul, which can kill the" \
                           " target. The scroll will be consumed upon use."
        self.value = 10000
        self.rarity = 45
        self.spell = spells.Desoul
        self.item = DeathScroll


class SanctuaryScroll(Scroll):
    """
    Sanctuary
    """

    def __init__(self):
        super().__init__()
        self.name = "SANCTUARY SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast Sanctuary, which can " \
                           "return the user to town. The scroll will be consumed upon use."
        self.value = 25000
        self.rarity = 50
        self.spell = spells.Sanctuary
        self.item = SanctuaryScroll


class UltimaScroll(Scroll):
    """
    Ultima
    """

    def __init__(self):
        super().__init__()
        self.name = "ULTIMA SCROLL"
        self.description = "Scroll inscribed with an incantation allowing the user to cast the powerful Ultima. The " \
                           "scroll will be consumed upon use."
        self.value = 50000
        self.rarity = 65
        self.spell = spells.Ultima
        self.item = UltimaScroll


class Unobtainium(Misc):
    """
    Magical ore that can be used to forge ultimate weapons at the blacksmith; only one in the game
    """

    def __init__(self):
        super().__init__(name="UNOBTAINIUM", description="The legendary ore that has only been theorized. Can be used "
                                                         "to create ultimate weapons.",
                         value=0, rarity=99, subtyp='Special')


class Relic1(Misc):
    """
    The first of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="TRIANGULUS", description="The holy trinity of mind, body, and spirit are represented by "
                                                        "the Triangulus relic.",
                         value=0, rarity=99, subtyp='Special')


class Relic2(Misc):
    """
    The second of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="QUADRATA", description="The Quadrata relic symbolizes order, trust, stability, and "
                                                      "logic, the hallmarks of a well-balanced person.",
                         value=0, rarity=99, subtyp='Special')


class Relic3(Misc):
    """
    The third of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="HEXAGONUM", description="The Hexagonum relic represents the natural world, since the "
                                                       "hexagon is the considered the strongest shape and regularly "
                                                       "found in nature.",
                         value=0, rarity=99, subtyp='Special')


class Relic4(Misc):
    """
    The fourth of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="LUNA", description="The Moon, our celestial partner, is the inspiration for the Luna "
                                                  "relic and represents love for others.",
                         value=0, rarity=99, subtyp='Special')


class Relic5(Misc):
    """
    The fifth of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="POLARIS", description="The Polaris relic resembles the shape of a star and represents "
                                                     "the guiding light of the North Star.",
                         value=0, rarity=99, subtyp='Special')


class Relic6(Misc):
    """
    The sixth and final of six relics required to unlock the final boss
    """

    def __init__(self):
        super().__init__(name="INFINITAS", description="Shaped like a circle, the Infinitas relic represents the never-"
                                                       "ending struggle between good and evil.",
                         value=0, rarity=99, subtyp='Special')


# Parameters
items_dict = {'Weapon': {'Fist': [BrassKnuckles, Cestus, BattleGauntlet, BaghNahk, GodsHand],
                         'Dagger': [Dirk, Baselard, Kris, Rondel, Kukri, Carnwennan],
                         'Sword': [Rapier, Jian, Talwar, Shamshir, Khopesh, Excalibur],
                         'Club': [Mace, WarHammer, Pernach, Morgenstern, Mjolnir],
                         'Ninja Blade': [Tanto, Wakizashi, Ninjato],
                         'Longsword': [Bastard, Claymore, Zweihander, Changdao, Flamberge, Executioner],
                         'Battle Axe': [Mattock, Broadaxe, DoubleAxe, Parashu, Greataxe, Jarnbjorn],
                         'Polearm': [Voulge, Partisan, Halberd, Naginata, Trident, Gungnir],
                         'Staff': [Quarterstaff, Baston, IronshodStaff, SerpentStaff, HolyStaff, RuneStaff,
                                   MithrilshodStaff, DragonStaff, PrincessGuard],
                         'Hammer': [Sledgehammer, Maul, EarthHammer, GreatMaul, Skullcrusher]},
              'OffHand': {'Shield': [Buckler, Aspis, Targe, Glagwa, KiteShield, Pavise, MedusaShield],
                          'Tome': [Book, TomeKnowledge, Grimoire, BookShadows, DragonRouge, Vedas, Necronomicon,
                                   Magus]},
              'Armor': {'Cloth': [Tunic, ClothCloak, SilverCloak, GoldCloak, WizardRobe, CloakEnchantment, MerlinRobe],
                        'Light': [PaddedArmor, LeatherArmor, Cuirboulli, StuddedLeather, StuddedCuirboulli, DragonHide],
                        'Medium': [HideArmor, ChainShirt, ScaleMail, Breastplate, HalfPlate, Aegis],
                        'Heavy': [RingMail, ChainMail, Splint, PlateMail, FullPlate, Genji]},
              'Accessory': {'Ring': [IronRing, PowerRing],
                            'Pendant': [VisionPendant, SilverPendant, RubyPendant, AntidotePendant, GorgonPendant,
                                        DharmaPendant]},
              'Potion': {'Health': [HealthPotion, GreatHealthPotion, SuperHealthPotion, MasterHealthPotion],
                         'Mana': [ManaPotion, GreatManaPotion, SuperManaPotion, MasterManaPotion],
                         'Elixir': [Elixir, Megalixir],
                         'Stat': [HPPotion, MPPotion, StrengthPotion, IntelPotion, WisdomPotion, ConPotion,
                                  CharismaPotion, DexterityPotion, AardBeing],
                         'Status': [Antidote, EyeDrop, AntiCoagulant, PhoenixDown]},
              'Misc': {'Key': [Key, OldKey],
                       'Scroll': [BlessScroll, SleepScroll, FireScroll, IceScroll, ElectricScroll, WaterScroll,
                                  EarthScroll, WindScroll, ShadowScroll, HolyScroll, RegenScroll, SilenceScroll,
                                  DispelScroll, DeathScroll, SanctuaryScroll, UltimaScroll]}}
