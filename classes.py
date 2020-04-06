###########################################
""" class manager """

# Imports
import time

import storyline
import items
import character


# Functions
def define_class():
    """
    Allows user to select desired class and returns the object
    """
    class_list = [Warrior, Mage, Footpad]
    option_list = [('Warrior', 0), ('Mage', 1), ('Footpad', 2)]
    class_index = storyline.get_response(option_list)
    print(class_list[class_index]())
    return class_list[class_index]()


def equip_check(item, class_name):
    """
    Checks if the class allows the item type to be equipped
    """
    class_list = [('WARRIOR', Warrior), ('MAGE', Mage), ('FOOTPAD', Footpad)]
    for cls in class_list:
        if class_name == cls[0]:
            if item[0]().subtyp in cls[1]().restrictions[item[0]().typ]:
                return True
            else:
                print("%s's cannot equip %s." % (class_name, item[0]().name))
                return False


def promotion(player: object):
    class_dict = {Warrior().name: [WeaponMaster(), Paladin(), Lancer()],
                  WeaponMaster().name: [Berserker()],
                  Paladin().name: [Crusader()],
                  Lancer().name: [Dragoon()],
                  Mage().name: [Sorcerer(), Warlock()],
                  Sorcerer().name: [Wizard()],
                  Warlock().name: [Necromancer()],
                  Footpad().name: [Thief(), Ranger(), Assassin()],
                  Thief().name: [Rogue()],
                  Ranger().name: [Seeker()],
                  Assassin().name: [Ninja()]
                  }
    current_class = player.cls
    if current_class in class_dict:
        class_options = []
        i = 0
        for cls in class_dict[current_class]:
            class_options.append((cls.name, i))
            i += 1
        print("Choose your path.")
        class_index = storyline.get_response(class_options)
        new_class = class_dict[current_class][class_index]
        print("You have chosen to promote from %s to %s." % (current_class, new_class.name))
        promote = input("Do you wish to continue? (Y or N) ").lower()
        if promote == 'y':
            promoted_player = player
            promoted_player.level = 1
            promoted_player.experience = 0
            promoted_player.cls = new_class.name
            player.equip(unequip=True)
            promoted_player.equipment = new_class.equipment
            if new_class.min_str > promoted_player.strength:
                promoted_player.strength = new_class.min_str
            if new_class.min_int > promoted_player.intel:
                promoted_player.intel = new_class.min_int
            if new_class.min_wis > promoted_player.wisdom:
                promoted_player.wisdom = new_class.min_wis
            if new_class.min_con > promoted_player.con:
                promoted_player.con = new_class.min_con
            if new_class.min_cha > promoted_player.charisma:
                promoted_player.charisma = new_class.min_cha
            if new_class.min_dex > promoted_player.dex:
                promoted_player.dex = new_class.min_dex
            time.sleep(1)
            print("Congratulations! %s has been promoted from a %s to a %s!" % (player.name, current_class,
                                                                                new_class.name))
        else:
            print("If you change your mind, you know where to find us.")


class Job:
    """
    Base definition for the Class class
    min_* parameters set the minimum value the player will start out with, regardless of roll
    equipment lists the items the player starts out with for the selected class
    restrictions list the allowable item types the class can equip
    """

    def __init__(self, name, description, min_str, min_int, min_wis, min_con, min_cha, min_dex, equipment,
                 restrictions):
        self.name = name
        self.description = description
        self.min_str = min_str
        self.min_int = min_int
        self.min_wis = min_wis
        self.min_con = min_con
        self.min_cha = min_cha
        self.min_dex = min_dex
        self.equipment = equipment
        self.restrictions = restrictions

    def __str__(self):
        return "Name: {}\n" \
               "Description: {}\n" \
               "Minimum Stats\n" \
               "Strength: {}\n" \
               "Intelligence: {}\n" \
               "Wisdom: {}\n" \
               "Constitution: {}\n" \
               "Charisma: {}\n" \
               "Dexterity: {}".format(self.name, self.description, self.min_str, self.min_int, self.min_wis,
                                      self.min_con, self.min_cha, self.min_dex)


class Warrior(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
                       |
                       -> Paladin -> Crusader
                       |
                       -> Lancer  -> Dragoon
    """

    def __init__(self):
        super().__init__(name="WARRIOR", description="A warrior is a weapon specialist that relies on strength and \n"
                                                     "defense.",
                         min_str=12, min_int=7, min_wis=5, min_con=10, min_cha=6, min_dex=7,
                         equipment=dict(Weapon=items.BronzeSword, OffHand=items.WoodShield, Armor=items.HideArmor),
                         restrictions={'Weapon': ['Dagger', 'Sword', 'Axe', 'Hammer', 'Polearm'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Light', 'Medium', 'Heavy']})


class WeaponMaster(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
    Pros: Can dual wield and can equip light armor
    Cons: Cannot use shields or heavy armor
    """

    def __init__(self):
        super().__init__(name="WEAPON MASTER", description="",
                         min_str=15, min_int=10, min_wis=8, min_con=11, min_cha=7, min_dex=12,
                         equipment=dict(Weapon=items.GreatAxe, OffHand=items.NoOffHand, Armor=items.Cuirboulli),
                         restrictions={'Weapon': ['Dagger', 'Sword', 'Axe', 'Hammer', 'Polearm', 'Staff'],
                                       'OffHand': ['Dagger', 'Sword'],
                                       'Armor': ['Light', 'Medium']})


class Berserker(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
    Pros: Can dual wield, use all weapons, and can equip light armor
    Cons: Cannot use shields or heavy armor
    """

    def __init__(self):
        super().__init__(name="BERSERKER", description="",
                         min_str=18, min_int=12, min_wis=11, min_con=12, min_cha=8, min_dex=14,
                         equipment=dict(Weapon=items.AdamantiteAxe, OffHand=items.NoOffHand, Armor=items.Studded),
                         restrictions={'Weapon': ['Dagger', 'Sword', 'Axe', 'Hammer', 'Polearm', 'Staff'],
                                       'OffHand': ['Dagger', 'Sword'],
                                       'Armor': ['Light', 'Medium']})


class Paladin(Job):
    """
    Promotion: Warrior -> Paladin -> Crusader
    Pros: Can use shields and heavy armor; can cast healing spells TODO
    Cons: Cannot equip 2-handed weapons or dual wield
    """

    def __init__(self):
        super().__init__(name="PALADIN", description="",
                         min_str=13, min_int=13, min_wis=14, min_con=14, min_cha=10, min_dex=8,
                         equipment=dict(Weapon=items.SteelSword, OffHand=items.IronShield, Armor=items.Splint),
                         restrictions={'Weapon': ['Sword'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']})


class Crusader(Job):
    """
    Promotion: Warrior -> Paladin -> Crusader
    Pros: Can use shields and heavy armor; can cast healing spells TODO
    Cons: Cannot equip 2-handed weapons or dual wield
    """

    def __init__(self):
        super().__init__(name="CRUSADER", description="",
                         min_str=15, min_int=14, min_wis=16, min_con=16, min_cha=13, min_dex=9,
                         equipment=dict(Weapon=items.AdamantiteSword, OffHand=items.TowerShield,
                                        Armor=items.PlateArmor),
                         restrictions={'Weapon': ['Sword'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']})


class Lancer(Job):
    """
    Promotion: Warrior -> Lancer -> Dragoon
    Pros: Can use polearms as 1-handed weapons; can equip shields and heavy armor
    Cons: Cannot equip 2-handed weapons or dual wield
    """

    def __init__(self):
        super().__init__(name="LANCER", description="",
                         min_str=14, min_int=11, min_wis=11, min_con=12, min_cha=8, min_dex=10,
                         equipment=dict(Weapon=items.Pike, OffHand=items.IronShield, Armor=items.Breastplate),
                         restrictions={'Weapon': ['Sword', 'Polearm'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']})


class Dragoon(Job):
    """
    Promotion: Warrior -> Lancer -> Dragoon
    Pros: Can use polearms as 1-handed weapons; can equip shields and heavy armor
    Cons: Cannot equip 2-handed weapons or dual wield
    """

    def __init__(self):
        super().__init__(name="DRAGOON", description="",
                         min_str=16, min_int=13, min_wis=13, min_con=14, min_cha=10, min_dex=12,
                         equipment=dict(Weapon=items.Halberd, OffHand=items.TowerShield, Armor=items.PlateArmor),
                         restrictions={'Weapon': ['Sword', 'Polearm'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']})


class Mage(Job):
    """
    Promotion: Mage -> Sorcerer -> Wizard
                    |
                    ->  Warlock -> Necromancer
    """

    def __init__(self):
        super().__init__(name="MAGE", description="Mages possess exceptional aptitude for spell casting, able to \n"
                                                  "destroy an enemy with the wave of a finger. Weaker and more \n"
                                                  "vulnerable than any other class, they more than make up for it \n"
                                                  "with powerful magics.",
                         min_str=5, min_int=13, min_wis=11, min_con=5, min_cha=10, min_dex=6,
                         equipment=dict(Weapon=items.PineStaff, OffHand=items.NoOffHand, Armor=items.Tunic),
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Grimoire'],
                                       'Armor': ['Cloth']})


class Sorcerer(Job):
    """
    Promotion: Mage -> Sorcerer -> Wizard
    Pros: Higher intelligence; earlier access to spells and access to higher level spells TODO
    Cons: Lower strength and constitution
    """

    def __init__(self):
        super().__init__(name="SORCERER", description="",
                         min_str=7, min_int=17, min_wis=14, min_con=7, min_cha=11, min_dex=8,
                         equipment=dict(Weapon=items.IronshodStaff, OffHand=items.NoOffHand, Armor=items.GoldCloak),
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Grimoire'],
                                       'Armor': ['Cloth']})


class Wizard(Job):
    """
    Promotion: Mage -> Sorcerer -> Wizard
    Pros: Higher intelligence; earlier access to spells and access to higher level spells TODO
    Cons: Lower strength and constitution
    """

    def __init__(self):
        super().__init__(name="WIZARD", description="",
                         min_str=9, min_int=20, min_wis=16, min_con=10, min_cha=13, min_dex=10,
                         equipment=dict(Weapon=items.SerpentStaff, OffHand=items.NoOffHand, Armor=items.WizardRobe),
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Grimoire'],
                                       'Armor': ['Cloth']})


class Warlock(Job):
    """
    Promotion: Mage -> Warlock -> Necromancer
    Pros: Higher strength and constitution; access to additional skills TODO
    Cons: Lower intelligence and limited access to higher level spells
    """

    def __init__(self):
        super().__init__(name="WARLOCK", description="",
                         min_str=10, min_int=14, min_wis=14, min_con=9, min_cha=10, min_dex=9,
                         equipment=dict(Weapon=items.SteelDagger, OffHand=items.TomeKnowledge, Armor=items.GoldCloak),
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Grimoire'],
                                       'Armor': ['Cloth']})


class Necromancer(Job):
    """
    Promotion: Mage -> Warlock -> Necromancer
    Pros: Higher strength and constitution; access to additional skills TODO
    Cons: Lower intelligence and limited access to higher level spells
    """

    def __init__(self):
        super().__init__(name="NECROMANCER", description="",
                         min_str=12, min_int=16, min_wis=16, min_con=12, min_cha=11, min_dex=12,
                         equipment=dict(Weapon=items.AdamantiteDagger, OffHand=items.Necronomicon,
                                        Armor=items.CloakEnchantment),
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Grimoire'],
                                       'Armor': ['Cloth']})


class Footpad(Job):
    """
    Promotion: Footpad ->  Thief   -> Rogue
                       |
                       ->  Ranger  -> Seeker
                       |
                       -> Assassin -> Ninja
    """

    def __init__(self):
        super().__init__(name="FOOTPAD", description="Footpads are agile and perceptive, with an natural ability of \n"
                                                     "deftness. While more than capable of holding their own in hand-\n"
                                                     "to-hand combat, they truly excel at subterfuge.",
                         min_str=8, min_int=10, min_wis=8, min_con=7, min_cha=5, min_dex=11,
                         equipment=dict(Weapon=items.BronzeDagger, OffHand=items.BronzeDagger, Armor=items.PaddedArmor),
                         restrictions={'Weapon': ['Dagger', 'Sword'],
                                       'OffHand': ['Dagger'],
                                       'Armor': ['Light']})


class Thief(Job):
    """
    Promotion: Footpad -> Thief-> Rogue
    Pros: Ability to dual wield and access to certain abilities (including stealing TODO)
    Cons:
    """

    def __init__(self):
        super().__init__(name="THIEF", description="",
                         min_str=10, min_int=14, min_wis=12, min_con=9, min_cha=6, min_dex=16,
                         equipment=dict(Weapon=items.SteelDagger, OffHand=items.SteelDagger, Armor=items.Cuirboulli),
                         restrictions={'Weapon': ['Dagger', 'Sword'],
                                       'OffHand': ['Dagger'],
                                       'Armor': ['Light']})


class Rogue(Job):
    """
    Promotion: Footpad -> Thief -> Rogue
    """

    def __init__(self):
        super().__init__(name="ROGUE", description="",
                         min_str=12, min_int=16, min_wis=13, min_con=12, min_cha=8, min_dex=18,
                         equipment=dict(Weapon=items.AdamantiteDagger, OffHand=items.AdamantiteDagger,
                                        Armor=items.Studded),
                         restrictions={'Weapon': ['Dagger', 'Sword'],
                                       'OffHand': ['Dagger'],
                                       'Armor': ['Light']})


class Ranger(Job):
    """
    Promotion: Footpad -> Ranger -> Seeker
    Pros: Increased strength and constitution; ability to perceive enemy status and weaknesses; access to medium armor,
          shields, and some spells
    Cons: Much lower dexterity
    """

    def __init__(self):
        super().__init__(name="RANGER", description="",
                         min_str=11, min_int=14, min_wis=14, min_con=11, min_cha=8, min_dex=11,
                         equipment=dict(Weapon=items.SteelSword, OffHand=items.IronShield, Armor=items.ScaleMail),
                         restrictions={'Weapon': ['Dagger', 'Sword'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Light', 'Medium']})


class Seeker(Job):
    """
    Promotion: Footpad -> Ranger -> Seeker
    Pros: Increased strength and constitution; ability to perceive enemy status and weaknesses; access to medium armor,
          shields, and some spells
    Cons: Much lower dexterity
    """

    def __init__(self):
        super().__init__(name="SEEKER", description="",
                         min_str=14, min_int=16, min_wis=16, min_con=14, min_cha=10, min_dex=13,
                         equipment=dict(Weapon=items.AdamantiteSword, OffHand=items.TowerShield, Armor=items.HalfPlate),
                         restrictions={'Weapon': ['Dagger', 'Sword'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Light', 'Medium']})


class Assassin(Job):
    """
    Promotion: Footpad -> Assassin -> Ninja
    Pros: Higher dexterity and wisdom (magic defense); earlier access to skills and more powerful skills
    Cons: Lower strength and constitution; can only equip daggers
    """

    def __init__(self):
        super().__init__(name="THIEF", description="",
                         min_str=9, min_int=13, min_wis=15, min_con=8, min_cha=6, min_dex=18,
                         equipment=dict(Weapon=items.SteelDagger, OffHand=items.SteelDagger, Armor=items.Cuirboulli),
                         restrictions={'Weapon': ['Dagger'],
                                       'OffHand': ['Dagger'],
                                       'Armor': ['Light']})


class Ninja(Job):
    """
    Promotion: Footpad -> Assassin -> Ninja
    """

    def __init__(self):
        super().__init__(name="ROGUE", description="",
                         min_str=11, min_int=15, min_wis=17, min_con=10, min_cha=7, min_dex=22,
                         equipment=dict(Weapon=items.AdamantiteDagger, OffHand=items.AdamantiteDagger,
                                        Armor=items.Studded),
                         restrictions={'Weapon': ['Dagger'],
                                       'OffHand': ['Dagger'],
                                       'Armor': ['Light']})
