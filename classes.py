###########################################
""" class manager """

# Imports
import time

import storyline
import items
import character
import spells


# Functions
def define_class():
    """
    Allows user to select desired class and returns the object
    """
    class_list = [Warrior, Mage, Footpad]
    print("Now, choose your class.")
    option_list = [('Warrior', 0), ('Mage', 1), ('Footpad', 2)]
    while True:
        class_index = storyline.get_response(option_list)
        print(class_list[class_index]())
        choose = input("Are you sure you want to play as a %s? " % class_list[class_index]().name).lower()
        if choose == 'y':
            break
    return class_list[class_index]()


def equip_check(item, item_typ, class_name):
    """
    Checks if the class allows the item type to be equipped
    """
    class_list = [('WARRIOR', Warrior), ('MAGE', Mage), ('FOOTPAD', Footpad),
                  ('WEAPON MASTER', WeaponMaster), ('BERSERKER', Berserker),
                  ('PALADIN', Paladin), ('CRUSADER', Crusader),
                  ('LANCER', Lancer), ('DRAGOON', Dragoon),
                  ('SORCERER', Sorcerer), ('WIZARD', Wizard),
                  ('WARLOCK', Warlock), ('NECROMANCER', Necromancer),
                  ('SPELLBLADE', Spellblade), ('KNIGHT ENCHANTER', KnightEnchanter),
                  ('THIEF', Thief), ('ROGUE', Rogue),
                  ('INQUISITIVE', Inquisitive), ('SEEKER', Seeker),
                  ('ASSASSIN', Assassin), ("NINJA", Ninja)]
    for cls in class_list:
        if class_name == cls[0]:
            if item[0]().subtyp in cls[1]().restrictions[item_typ]:
                return True
            else:
                return False


def promotion(player: object):
    class_dict = {Warrior().name: [WeaponMaster(), Paladin(), Lancer()],
                  WeaponMaster().name: [Berserker()],
                  Paladin().name: [Crusader()],
                  Lancer().name: [Dragoon()],
                  Mage().name: [Sorcerer(), Warlock(), Spellblade()],
                  Sorcerer().name: [Wizard()],
                  Warlock().name: [Necromancer()],
                  Spellblade().name: [KnightEnchanter()],
                  Footpad().name: [Thief(), Inquisitive(), Assassin()],
                  Thief().name: [Rogue()],
                  Inquisitive().name: [Seeker()],
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
            print("Congratulations! %s has been promoted from a %s to a %s!" % (player.name, current_class,
                                                                                new_class.name))
            player.equip(unequip=True)
            promoted_player = player
            promoted_player.pro_level = new_class.pro_level
            promoted_player.level = 1
            promoted_player.experience = 0
            promoted_player.cls = new_class.name
            promoted_player.equipment = new_class.equipment
            if new_class.name == 'WARLOCK':
                promoted_player.spellbook['Spells'] = {'Shadow Bolt': spells.ShadowBolt}
                print("You unlearn all of your spells but gain Shadow Bolt!")
                time.sleep(0.5)
                print(spells.ShadowBolt())
            elif new_class.name == 'WEAPON MASTER':
                del promoted_player.spellbook['Skills']['Shield Slam']
                promoted_player.spellbook['Skills']['Mortal Strike'] = spells.MortalStrike
                print("You unlearn Shield Slam but gain Mortal Strike!")
                time.sleep(0.5)
                print(spells.MortalStrike())
            print("Stat Gains")
            if new_class.str_plus > 0:
                print("Strength: %s -> %s" % (promoted_player.strength, promoted_player.strength + new_class.str_plus))
                promoted_player.strength += new_class.str_plus
                time.sleep(0.5)
            if new_class.int_plus > 0:
                print("Intelligence: %s -> %s" % (promoted_player.intel, promoted_player.intel + new_class.int_plus))
                promoted_player.intel += new_class.int_plus
                time.sleep(0.5)
            if new_class.wis_plus > 0:
                print("Wisdom: %s -> %s" % (promoted_player.wisdom, promoted_player.wisdom + new_class.wis_plus))
                promoted_player.wisdom += new_class.wis_plus
                time.sleep(0.5)
            if new_class.con_plus > 0:
                print("Constitution: %s -> %s" % (promoted_player.con, promoted_player.con + new_class.con_plus))
                promoted_player.con += new_class.con_plus
                time.sleep(0.5)
            if new_class.cha_plus > 0:
                print("Charisma: %s -> %s" % (promoted_player.charisma, promoted_player.charisma + new_class.cha_plus))
                promoted_player.charisma += new_class.cha_plus
                time.sleep(0.5)
            if new_class.dex_plus > 0:
                print("Dexterity: %s -> %s" % (promoted_player.dex, promoted_player.dex + new_class.dex_plus))
                promoted_player.dex += new_class.dex_plus
            time.sleep(2)
        else:
            print("If you change your mind, you know where to find us.")


class Job:
    """
    Base definition for the Class class
    min_* parameters set the minimum value the player will start out with, regardless of roll
    equipment lists the items the player starts out with for the selected class
    restrictions list the allowable item types the class can equip
    """

    def __init__(self, name, description, str_plus, int_plus, wis_plus, con_plus, cha_plus, dex_plus, equipment,
                 restrictions, pro_level):
        self.name = name
        self.description = description
        self.str_plus = str_plus
        self.int_plus = int_plus
        self.wis_plus = wis_plus
        self.con_plus = con_plus
        self.cha_plus = cha_plus
        self.dex_plus = dex_plus
        self.equipment = equipment
        self.restrictions = restrictions
        self.pro_level = pro_level

    def __str__(self):
        return "Name: {}\n" \
               "Description: {}\n" \
               "\n" \
               "Stats Boosts\n" \
               "Strength: {}\n" \
               "Intelligence: {}\n" \
               "Wisdom: {}\n" \
               "Constitution: {}\n" \
               "Charisma: {}\n" \
               "Dexterity: {}".format(self.name, self.description, self.str_plus, self.int_plus, self.wis_plus,
                                      self.con_plus, self.cha_plus, self.dex_plus)


class Warrior(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
                       |
                       -> Paladin -> Crusader
                       |
                       -> Lancer  -> Dragoon
    """

    def __init__(self):
        super().__init__(name="WARRIOR", description="A Warrior is a weapon specialist that relies on strength and \n"
                                                     "defense.",
                         str_plus=3, int_plus=0, wis_plus=1, con_plus=3, cha_plus=0, dex_plus=1,
                         equipment=dict(Weapon=items.BronzeSword, OffHand=items.WoodShield, Armor=items.HideArmor),
                         restrictions={'Weapon': ['Dagger', 'Sword', 'Mace', 'Axe', 'Hammer', 'Polearm'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Light', 'Medium', 'Heavy']},
                         pro_level=1)


class WeaponMaster(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
    Pros: Can dual wield and can equip light armor
    Cons: Cannot use shields or heavy armor
    """

    def __init__(self):
        super().__init__(name="WEAPON MASTER", description="Weapon Masters focus on the mastery of weapons and their"
                                                           " skill with them.",
                         str_plus=3, int_plus=1, wis_plus=1, con_plus=2, cha_plus=1, dex_plus=2,
                         equipment=dict(Weapon=items.GreatAxe, OffHand=items.NoOffHand, Armor=items.ScaleMail),
                         restrictions={'Weapon': ['Dagger', 'Sword', 'Mace', 'Axe', 'Hammer', 'Polearm', 'Staff'],
                                       'OffHand': ['Dagger', 'Sword', 'Mace'],
                                       'Armor': ['Light', 'Medium']},
                         pro_level=2)


class Berserker(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
    Pros: Can dual wield 2-handed weapons
    Cons: Cannot use shields and can only equip light armor
    """

    def __init__(self):
        super().__init__(name="BERSERKER", description="Berserkers are combat masters, driven by pure rage and "
                                                       "vengeance.",
                         str_plus=4, int_plus=1, wis_plus=1, con_plus=2, cha_plus=1, dex_plus=3,
                         equipment=dict(Weapon=items.AdamantiteAxe, OffHand=items.WarHammer,
                                        Armor=items.StuddedCuirboulli),
                         restrictions={'Weapon': ['Dagger', 'Sword', 'Axe', 'Hammer', 'Polearm', 'Staff'],
                                       'OffHand': ['Dagger', 'Sword', 'Axe', 'Hammer', 'Polearm', 'Staff'],
                                       'Armor': ['Light']},
                         pro_level=3)


class Paladin(Job):
    """
    Promotion: Warrior -> Paladin -> Crusader
    Pros: Can use shields and heavy armor; can cast healing spells
    Cons: Cannot equip 2-handed weapons or dual wield
    """

    def __init__(self):
        super().__init__(name="PALADIN", description="The Paladin is a holy knight, crusading in the name of good and "
                                                     "order, and is a divine spell caster.",
                         str_plus=1, int_plus=2, wis_plus=2, con_plus=3, cha_plus=1, dex_plus=1,
                         equipment=dict(Weapon=items.SteelMace, OffHand=items.IronShield, Armor=items.Splint),
                         restrictions={'Weapon': ['Sword', 'Mace'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']},
                         pro_level=2)


class Crusader(Job):
    """
    Promotion: Warrior -> Paladin -> Crusader
    Pros: Can use shields and heavy armor; can cast healing spells
    Cons: Cannot equip 2-handed weapons or dual wield
    """

    def __init__(self):
        super().__init__(name="CRUSADER", description="The Crusader is a holy warrior, who values order and justice "
                                                      "above all else.",
                         str_plus=2, int_plus=2, wis_plus=2, con_plus=3, cha_plus=2, dex_plus=1,
                         equipment=dict(Weapon=items.AdamantiteMace, OffHand=items.TowerShield,
                                        Armor=items.FullPlate),
                         restrictions={'Weapon': ['Sword', 'Mace'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']},
                         pro_level=3)


class Lancer(Job):
    """
    Promotion: Warrior -> Lancer -> Dragoon
    Pros: Can use polearms as 1-handed weapons; can equip shields and heavy armor
    Cons: Cannot equip 2-handed weapons or dual wield
    """

    def __init__(self):
        super().__init__(name="LANCER", description="The Lancer spend their time specializing in the art of wielding "
                                                    "polearms and shields.",
                         str_plus=3, int_plus=1, wis_plus=2, con_plus=2, cha_plus=1, dex_plus=1,
                         equipment=dict(Weapon=items.Pike, OffHand=items.IronShield, Armor=items.Splint),
                         restrictions={'Weapon': ['Polearm'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']},
                         pro_level=2)


class Dragoon(Job):
    """
    Promotion: Warrior -> Lancer -> Dragoon
    Pros: Can use polearms as 1-handed weapons; can equip swords, shields and heavy armor
    Cons: Cannot equip 2-handed weapons or dual wield
    """

    def __init__(self):
        super().__init__(name="DRAGOON", description="Masters of spears, lances and polearms and gifted with "
                                                     "supernatural abilities, Dragoons have become legendary for their"
                                                     " grace and power. Their intense training, said to have been "
                                                     "passed down by the dragon riders of old, allows these warriors to"
                                                     " leap unnaturally high into the air and strike their foes with "
                                                     "deadly force from above. ",
                         str_plus=3, int_plus=1, wis_plus=2, con_plus=3, cha_plus=1, dex_plus=2,
                         equipment=dict(Weapon=items.Halberd, OffHand=items.TowerShield, Armor=items.FullPlate),
                         restrictions={'Weapon': ['Sword', 'Polearm'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']},
                         pro_level=3)


class Mage(Job):
    """
    Promotion: Mage ->  Sorcerer  -> Wizard
                    |
                    ->   Warlock  -> Necromancer
                    |
                    -> Spellblade -> Knight Enchanter
    """

    def __init__(self):
        super().__init__(name="MAGE", description="Mages possess exceptional aptitude for spell casting, able to \n"
                                                  "destroy an enemy with the wave of a finger. Weaker and more \n"
                                                  "vulnerable than any other class, they more than make up for it \n"
                                                  "with powerful magics.",
                         str_plus=0, int_plus=4, wis_plus=3, con_plus=0, cha_plus=2, dex_plus=1,
                         equipment=dict(Weapon=items.PineStaff, OffHand=items.NoOffHand, Armor=items.Tunic),
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Grimoire'],
                                       'Armor': ['Cloth']},
                         pro_level=1)


class Sorcerer(Job):
    """
    Promotion: Mage -> Sorcerer -> Wizard
    Pros: Higher intelligence; earlier access to spells and access to higher level spells
    Cons: Lower strength and constitution
    """

    def __init__(self):
        super().__init__(name="SORCERER", description="A Sorcerer is someone who uses or practices magic derived from "
                                                      "supernatural, occult, or arcane sources.",
                         str_plus=0, int_plus=4, wis_plus=2, con_plus=1, cha_plus=1, dex_plus=2,
                         equipment=dict(Weapon=items.IronshodStaff, OffHand=items.NoOffHand, Armor=items.SilverCloak),
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Grimoire'],
                                       'Armor': ['Cloth']},
                         pro_level=2)


class Wizard(Job):
    """
    Promotion: Mage -> Sorcerer -> Wizard
    Pros: Higher intelligence; earlier access to spells and access to higher level spells
    Cons: Lower strength and constitution
    """

    def __init__(self):
        super().__init__(name="WIZARD", description="The Wizard is a master of arcane magic, who has studied the "
                                                    "subject for years. He practices until he is able to command magic "
                                                    "with ease.",
                         str_plus=0, int_plus=5, wis_plus=3, con_plus=1, cha_plus=1, dex_plus=2,
                         equipment=dict(Weapon=items.SerpentStaff, OffHand=items.NoOffHand, Armor=items.WizardRobe),
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Grimoire'],
                                       'Armor': ['Cloth']},
                         pro_level=3)


class Warlock(Job):
    """
    Promotion: Mage -> Warlock -> Necromancer
    Pros: Higher strength and constitution; access to additional skills
    Cons: Lower intelligence and limited access to higher level spells
    """

    def __init__(self):
        super().__init__(name="WARLOCK", description="The Warlock is a arcanist, who conjures the dark arts to harness "
                                                     "their innate magical gift, and perform spell-like feats and "
                                                     "abilities.",
                         str_plus=1, int_plus=3, wis_plus=3, con_plus=2, cha_plus=0, dex_plus=1,
                         equipment=dict(Weapon=items.SteelDagger, OffHand=items.TomeKnowledge, Armor=items.SilverCloak),
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Grimoire'],
                                       'Armor': ['Cloth']},
                         pro_level=2)


class Necromancer(Job):
    """
    Promotion: Mage -> Warlock -> Necromancer
    Pros: Higher strength and constitution; access to additional skills
    Cons: Lower intelligence and limited access to higher level spells
    """

    def __init__(self):
        super().__init__(name="NECROMANCER", description="The Necromancer is highly attune to the dark arts and can "
                                                         "conjure the most demonic of powers, including the practicing"
                                                         " of forbidden blood magic.",
                         str_plus=2, int_plus=3, wis_plus=3, con_plus=3, cha_plus=0, dex_plus=1,
                         equipment=dict(Weapon=items.AdamantiteDagger, OffHand=items.Necronomicon,
                                        Armor=items.CloakEnchantment),
                         restrictions={'Weapon': ['Dagger', 'Staff'],
                                       'OffHand': ['Grimoire'],
                                       'Armor': ['Cloth']},
                         pro_level=3)


class Spellblade(Job):
    """
    Promotion: Mage -> Spellblade -> Knight Enchanter
    Pros: Adds a portion of intelligence to melee damage; higher strength and constitution; can equip swords and light
    armor
    Cons: Lower intelligence and wisdom; cannot equip staves
    """

    def __init__(self):
        super().__init__(name="SPELLBLADE", description="The Spellblade combines a magical affinity with a higher level"
                                                        "of martial prowess from the other magical classes.",
                         str_plus=2, int_plus=2, wis_plus=2, con_plus=2, cha_plus=1, dex_plus=1,
                         equipment=dict(Weapon=items.SteelSword, OffHand=items.TomeKnowledge, Armor=items.Cuirboulli),
                         restrictions={'Weapon': ['Dagger', 'Sword'],
                                       'OffHand': ['Grimoire'],
                                       'Armor': ['Cloth', 'Light']},
                         pro_level=2)


class KnightEnchanter(Job):
    """
    Promotion: Mage -> Spellblade -> Knight Enchanter
    Pros: Adds a portion of intelligence to melee damage; higher strength and constitution; can equip swords and light
    armor
    Cons: Lower intelligence and wisdom; cannot equip staves
    """

    def __init__(self):
        super().__init__(name="KNIGHT ENCHANTER", description="The Knight Enchanter uses their arcane powers to imbue"
                                                              " weapons with magical enchantments that can rival the "
                                                              "most powerful fighter.",
                         str_plus=3, int_plus=2, wis_plus=2, con_plus=3, cha_plus=1, dex_plus=1,
                         equipment=dict(Weapon=items.AdamantiteSword, OffHand=items.BookShadows,
                                        Armor=items.StuddedCuirboulli),
                         restrictions={'Weapon': ['Dagger', 'Sword'],
                                       'OffHand': ['Grimoire'],
                                       'Armor': ['Cloth', 'Light']},
                         pro_level=3)


class Footpad(Job):
    """
    Promotion: Footpad ->  Thief   -> Rogue
                       |
                       ->  Inquisitive  -> Seeker
                       |
                       -> Assassin -> Ninja
    """

    def __init__(self):
        super().__init__(name="FOOTPAD", description="Footpads are agile and perceptive, with an natural ability of \n"
                                                     "deftness. While more than capable of holding their own in hand-\n"
                                                     "to-hand combat, they truly excel at subterfuge.",
                         str_plus=0, int_plus=1, wis_plus=2, con_plus=1, cha_plus=1, dex_plus=3,
                         equipment=dict(Weapon=items.BronzeSword, OffHand=items.BronzeDagger, Armor=items.PaddedArmor),
                         restrictions={'Weapon': ['Dagger', 'Sword', 'Mace'],
                                       'OffHand': ['Dagger'],
                                       'Armor': ['Light']},
                         pro_level=1)


class Thief(Job):
    """
    Promotion: Footpad -> Thief-> Rogue
    Pros: Ability to dual wield (only daggers in offhand) and access to certain abilities (including stealing)
    Cons: Average stats
    """

    def __init__(self):
        super().__init__(name="THIEF", description="Thieves are the best at collecting treasure, although the guild "
                                                   "makes sure to get a fair share. Very devoted to stealing, Thieves "
                                                   "often lack fighting skill, but make up for it with their "
                                                   "treacherous backstabbing.",
                         str_plus=1, int_plus=1, wis_plus=2, con_plus=2, cha_plus=2, dex_plus=2,
                         equipment=dict(Weapon=items.SteelSword, OffHand=items.SteelDagger, Armor=items.Cuirboulli),
                         restrictions={'Weapon': ['Dagger', 'Sword', 'Mace'],
                                       'OffHand': ['Dagger'],
                                       'Armor': ['Light']},
                         pro_level=2)


class Rogue(Job):
    """
    Promotion: Footpad -> Thief -> Rogue
    Pros: Ability to dual wield (can use swords and maces in offhand) and access to certain abilities (including
    stealing)
    Cons: Lower average stats
    """

    def __init__(self):
        super().__init__(name="ROGUE", description="Rogues rely on skill, stealth, and their foes' vulnerabilities to "
                                                   "get the upper hand in any situation. They have a knack for finding "
                                                   "the solution to just about any problem, demonstrating a "
                                                   "resourcefulness and versatility that has no rival.",
                         str_plus=1, int_plus=2, wis_plus=2, con_plus=2, cha_plus=2, dex_plus=3,
                         equipment=dict(Weapon=items.AdamantiteSword, OffHand=items.AdamantiteDagger,
                                        Armor=items.StuddedCuirboulli),
                         restrictions={'Weapon': ['Dagger', 'Sword', 'Mace'],
                                       'OffHand': ['Dagger', 'Sword', 'Mace'],
                                       'Armor': ['Light']},
                         pro_level=3)


class Inquisitive(Job):
    """
    Promotion: Footpad -> Inquisitive -> Seeker
    Pros: Increased strength and constitution; ability to perceive enemy status and weaknesses; access to medium armor,
          shields, and some spells as well as dual wielding
    Cons: Much lower dexterity
    """

    def __init__(self):
        super().__init__(name="INQUISITIVE", description="Inquisitives excel at rooting out hidden secrets and "
                                                         "unraveling mysteries. They rely on a sharp eye for detail, "
                                                         "but also on a finely honed ability to read the words and "
                                                         "deeds of other creatures to determine their true intent. "
                                                         "They excel at defeating creatures that hide among and prey "
                                                         "upon ordinary folk, and their mastery of lore and sharp eye "
                                                         "make them well-equipped to expose and end hidden evils.",
                         str_plus=2, int_plus=1, wis_plus=2, con_plus=3, cha_plus=1, dex_plus=1,
                         equipment=dict(Weapon=items.SteelSword, OffHand=items.IronShield, Armor=items.ScaleMail),
                         restrictions={'Weapon': ['Dagger', 'Sword', 'Mace'],
                                       'OffHand': ['Shield', 'Dagger', 'Sword', 'Mace'],
                                       'Armor': ['Light', 'Medium']},
                         pro_level=2)


class Seeker(Job):
    """
    Promotion: Footpad -> Inquisitive -> Seeker
    Pros: Increased strength and constitution; ability to perceive enemy status and weaknesses; access to medium armor,
          shields, and some spells as well as dual wielding
    Cons: Much lower dexterity
    """

    def __init__(self):
        super().__init__(name="SEEKER", description="Seekers are very good at moving through the dungeon, being able to"
                                                    " levitate, locate other characters, and teleport. They can’t "
                                                    "directly kill monsters with their magical abilities, but a Seeker "
                                                    "does well with a weapon in hand.  They are also the best at "
                                                    "mapping the dungeon and detecting any types of ‘anomalies’ they "
                                                    "may encounter in the depths.",
                         str_plus=3, int_plus=1, wis_plus=2, con_plus=3, cha_plus=1, dex_plus=2,
                         equipment=dict(Weapon=items.AdamantiteSword, OffHand=items.TowerShield, Armor=items.HalfPlate),
                         restrictions={'Weapon': ['Dagger', 'Sword', 'Mace'],
                                       'OffHand': ['Shield', 'Dagger', 'Sword', 'Mace'],
                                       'Armor': ['Light', 'Medium']},
                         pro_level=3)


class Assassin(Job):
    """
    Promotion: Footpad -> Assassin -> Ninja
    Pros: Higher dexterity and wisdom (magic defense); earlier access to skills and more powerful skills
    Cons: Lower strength and constitution; can only equip daggers
    """

    def __init__(self):
        super().__init__(name="ASSASSIN", description="You focus your training on the grim art of death. Those who "
                                                      "adhere to this archetype are diverse: hired killers, spies, "
                                                      "bounty hunters, and even specially anointed priests trained to "
                                                      "exterminate  the enemies of their deity. Stealth, poison, and "
                                                      "disguise help you eliminate your foes with deadly efficiency.",
                         str_plus=0, int_plus=1, wis_plus=3, con_plus=1, cha_plus=1, dex_plus=4,
                         equipment=dict(Weapon=items.SteelDagger, OffHand=items.SteelDagger, Armor=items.Cuirboulli),
                         restrictions={'Weapon': ['Dagger'],
                                       'OffHand': ['Dagger'],
                                       'Armor': ['Light']},
                         pro_level=2)


class Ninja(Job):
    """
    Promotion: Footpad -> Assassin -> Ninja
    Pros: Higher dexterity and wisdom (magic defense); earlier access to skills and more powerful skills
    Cons: Lower strength and constitution; can only equip daggers
    """

    def __init__(self):
        super().__init__(name="NINJA", description="Ninjas are weapons masters and can use almost all weapons including"
                                                   " their hands. Since a Ninja desires quickness, they are very "
                                                   "specific about the items they use. Ninjas are not allowed to wear"
                                                   " most types of armor and other items. However, having access to "
                                                   "special weapons that only they can use, Ninjas possess the skills "
                                                   "of Critically hitting and Backstabbing their opponents, along with "
                                                   "moderate thieving skills.",
                         str_plus=0, int_plus=2, wis_plus=3, con_plus=1, cha_plus=2, dex_plus=4,
                         equipment=dict(Weapon=items.AdamantiteDagger, OffHand=items.AdamantiteDagger,
                                        Armor=items.StuddedCuirboulli),
                         restrictions={'Weapon': ['Dagger'],
                                       'OffHand': ['Dagger'],
                                       'Armor': ['Light']},
                         pro_level=3)
