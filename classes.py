###########################################
""" class manager """

# Imports
import os
import time

import storyline
import items
import spells
from races import races_dict


# Functions
def define_class(race):
    """
    Allows user to select desired class and returns the object
    """
    class_dict = {'Warrior': Warrior,
                  'Mage': Mage,
                  'Footpad': Footpad,
                  'Healer': Healer,
                  'Pathfinder': Pathfinder}
    while True:
        char_class = list()
        for i, cls in enumerate(race.cls_res['Base']):
            char_class.append((cls, i))
        create_class = {1: {"Options": char_class,
                            "Text": ["Choose your character's class.\n"]}}
        class_index = storyline.story_flow(create_class, response=True)
        print(class_dict[char_class[class_index][0]]().__str__() + "\n")
        choose = input("Are you sure you want to play as a {}? ".format(
            class_dict[char_class[class_index][0]]().name.lower()))
        if choose in ['y', 'yes']:
            break
    os.system('cls' if os.name == 'nt' else 'clear')
    return class_dict[char_class[class_index][0]]()


def equip_check(item, item_typ, class_name):
    """
    Checks if the class allows the item type to be equipped
    """
    class_list = [('Warrior', Warrior), ('Mage', Mage), ('Footpad', Footpad),
                  ('Healer', Healer), ('Pathfinder', Pathfinder),
                  ('Weapon Master', WeaponMaster), ('Berserker', Berserker),
                  ('Paladin', Paladin), ('Crusader', Crusader),
                  ('Lancer', Lancer), ('Dragoon', Dragoon),
                  ('Sorcerer', Sorcerer), ('Wizard', Wizard),
                  ('Warlock', Warlock), ('Necromancer', Necromancer),
                  ('Spellblade', Spellblade), ('Knight Enchanter', KnightEnchanter),
                  ('Thief', Thief), ('Rogue', Rogue),
                  ('Inquisitor', Inquisitor), ('Seeker', Seeker),
                  ('Assassin', Assassin), ("Ninja", Ninja),
                  ('Cleric', Cleric), ('Templar', Templar),
                  ('Monk', Monk), ('Master Monk', MasterMonk),
                  ('Priest', Priest), ('Archbishop', Archbishop),
                  ('Druid', Druid), ('Lycan', Lycan),
                  ('Diviner', Diviner), ('Geomancer', Geomancer),
                  ('Shaman', Shaman), ('Soulcatcher', Soulcatcher)]
    if type(item) == list:
        item = item[0]
    for cls in class_list:
        if class_name == cls[0]:
            try:
                if cls[0] in item().restriction:
                    return True
            except AttributeError:
                pass
            if item_typ == 'Accessory':
                return True
            elif item().subtyp in cls[1]().restrictions[item_typ]:
                return True
            else:
                return False


def promotion(player):
    exp_scale = 50  # TODO
    pro1_dict = {Warrior().name: [WeaponMaster(), Paladin(), Lancer()],
                 Mage().name: [Sorcerer(), Warlock(), Spellblade()],
                 Footpad().name: [Thief(), Inquisitor(), Assassin()],
                 Healer().name: [Cleric(), Priest(), Monk()],
                 Pathfinder().name: [Druid(), Diviner(), Shaman()]}
    pro2_dict = {WeaponMaster().name: [Berserker()],
                 Paladin().name: [Crusader()],
                 Lancer().name: [Dragoon()],
                 Sorcerer().name: [Wizard()],
                 Warlock().name: [Necromancer()],
                 Spellblade().name: [KnightEnchanter()],
                 Thief().name: [Rogue()],
                 Inquisitor().name: [Seeker()],
                 Assassin().name: [Ninja()],
                 Cleric().name: [Templar()],
                 Priest().name: [Archbishop()],
                 Monk().name: [MasterMonk()],
                 Druid().name: [Lycan()],
                 Diviner().name: [Geomancer()],
                 Shaman().name: [Soulcatcher()]}
    current_class = player.cls
    class_options = []
    i = 0
    if player.pro_level == 1:
        for cls in pro1_dict[current_class]:
            if cls.name in races_dict[player.race]().cls_res['First']:
                class_options.append((cls.name, i))
                i += 1
    else:
        for cls in pro2_dict[current_class]:
            if cls.name in races_dict[player.race]().cls_res['Second']:
                class_options.append((cls.name, i))
                i += 1
    if len(class_options) > 1:
        print("Choose your path.")
        class_index = storyline.get_response(class_options)
    else:
        class_index = 0
    if player.pro_level == 1:
        new_class = pro1_dict[current_class][class_index]
    else:
        new_class = pro2_dict[current_class][class_index]
    print(new_class)
    print("You have chosen to promote from {} to {}.".format(current_class, new_class.name))
    promote = input("Do you wish to continue? (Y or N) ").lower()
    if promote == 'y':
        print("Congratulations! {} has been promoted from a {} to a {}!".format(player.name, current_class,
                                                                                new_class.name))
        player.equip(unequip=True)
        promoted_player = player
        promoted_player.pro_level = new_class.pro_level
        promoted_player.level = 1
        promoted_player.experience = 0
        promoted_player.exp_to_gain = (exp_scale ** player.pro_level) * player.level
        promoted_player.cls = new_class.name
        promoted_player.equipment = new_class.equipment
        if new_class.name == 'Warlock':
            promoted_player.spellbook['Spells'] = dict()
            print("You unlearn all of your arcane spells.")
            time.sleep(0.5)
        elif new_class.name == 'Weapon Master':
            del promoted_player.spellbook['Skills']['Shield Slam']
            print("You unlearn Shield Slam.")
            time.sleep(0.5)
        elif new_class.name == 'Inquisitor':
            del promoted_player.spellbook['Skills']['Kidney Punch']
            print("You unlearn Kidney Punch.")
            time.sleep(0.5)
        if str(promoted_player.level) in spells.spell_dict[promoted_player.cls]:
            spell_gain = spells.spell_dict[promoted_player.cls][str(promoted_player.level)]
            promoted_player.spellbook['Spells'][spell_gain().name] = spell_gain
            print(spell_gain())
            print("You have gained the ability to cast {}.".format(spell_gain().name))
            time.sleep(0.5)
        if str(promoted_player.level) in spells.skill_dict[promoted_player.cls]:
            skill_gain = spells.skill_dict[promoted_player.cls][str(promoted_player.level)]
            promoted_player.spellbook['Skills'][skill_gain().name] = skill_gain
            print(skill_gain())
            print("You have gained the ability to use {}.".format(skill_gain().name))
            time.sleep(0.5)
        time.sleep(0.5)
        print("Stat Gains")
        print("Strength: {} -> {}".format(promoted_player.strength, promoted_player.strength + new_class.str_plus))
        promoted_player.strength += new_class.str_plus
        print("Intelligence: {} -> {}".format(promoted_player.intel, promoted_player.intel + new_class.int_plus))
        promoted_player.intel += new_class.int_plus
        print("Wisdom: {} -> {}".format(promoted_player.wisdom, promoted_player.wisdom + new_class.wis_plus))
        promoted_player.wisdom += new_class.wis_plus
        print("Constitution: {} -> {}".format(promoted_player.con, promoted_player.con + new_class.con_plus))
        promoted_player.con += new_class.con_plus
        print("Charisma: {} -> {}".format(promoted_player.charisma, promoted_player.charisma + new_class.cha_plus))
        promoted_player.charisma += new_class.cha_plus
        print("Dexterity: {} -> {}".format(promoted_player.dex, promoted_player.dex + new_class.dex_plus))
        promoted_player.dex += new_class.dex_plus
        print("New Equipment")
        print("Weapon: {}".format(player.equipment['Weapon']().name))
        print("OffHand: {}".format(player.equipment['OffHand']().name))
        print("Armor: {}".format(player.equipment['Armor']().name))
        input("Press enter to continue")
    else:
        print("If you change your mind, you know where to find us.")
        time.sleep(1)


class Job:
    """
    Base definition for the class
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
                       -> Paladin       -> Crusader
                       |
                       -> Lancer        -> Dragoon
    """

    def __init__(self):
        super().__init__(name="Warrior", description="A Warrior is a weapon specialist that relies on strength and "
                                                     "defense. While unable to cast spells, they have access to a wide"
                                                     " variety of combat skills that make them deadly in combat. The "
                                                     "most stout of the bass classes, this character is best for "
                                                     "someone who wants to hack and slash their way through the game.",
                         str_plus=1, int_plus=0, wis_plus=0, con_plus=1, cha_plus=0, dex_plus=0,
                         equipment=dict(Weapon=items.BronzeSword, OffHand=items.WoodShield, Armor=items.HideArmor,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Sword', 'Mace', 'Axe', 'Hammer', 'Polearm'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Light', 'Medium', 'Heavy']},
                         pro_level=1)


class WeaponMaster(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
    Pros: Can dual wield and can equip light armor
    Cons: Cannot use shields or heavy armor; does not get DEX bonus to attack when equipping fist weapons
    """

    def __init__(self):
        super().__init__(name="Weapon Master", description="Weapon Masters focus on the mastery of weapons and their"
                                                           " skill with them. They can equip all weapons and learn the"
                                                           " ability to dual wield one-handed weapons. Since Weapon "
                                                           "Masters really on dexterity, they lose the ability to wear"
                                                           " heavy armor and shields.",
                         str_plus=2, int_plus=0, wis_plus=0, con_plus=1, cha_plus=0, dex_plus=1,
                         equipment=dict(Weapon=items.GreatAxe, OffHand=items.NoOffHand, Armor=items.ScaleMail,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Sword', 'Mace', 'Axe', 'Hammer', 'Polearm',
                                                  'Staff'],
                                       'OffHand': ['Fist', 'Dagger', 'Sword', 'Mace'],
                                       'Armor': ['Light', 'Medium']},
                         pro_level=2)


class Berserker(Job):
    """
    Promotion: Warrior -> Weapon Master -> Berserker
    Pros: Can dual wield 2-handed weapons
    Cons: Cannot use shields and can only equip light armor; does not get DEX bonus to attack when equipping fist
    weapons
    """

    def __init__(self):
        super().__init__(name="Berserker", description="Berserkers are combat masters, driven by pure rage and "
                                                       "vengeance. They are so adept at using weapons, they gain the "
                                                       "ability to dual wield two-handed weapons. Their further "
                                                       "reliance on maneuverability limits the type of armor to light "
                                                       "armor.",
                         str_plus=3, int_plus=0, wis_plus=0, con_plus=1, cha_plus=0, dex_plus=2,
                         equipment=dict(Weapon=items.AdamantiteAxe, OffHand=items.WarHammer,
                                        Armor=items.StuddedLeather, Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Sword', 'Axe', 'Hammer', 'Polearm', 'Staff'],
                                       'OffHand': ['Fist', 'Dagger', 'Sword', 'Axe', 'Hammer', 'Polearm', 'Staff'],
                                       'Armor': ['Light']},
                         pro_level=3)


class Paladin(Job):
    """
    Promotion: Warrior -> Paladin -> Crusader
    Pros: Can use shields and heavy armor; can cast healing spells
    Cons: Cannot equip 2-handed weapons except hammers; lower strength gain
    """

    def __init__(self):
        super().__init__(name="Paladin", description="The Paladin is a holy knight, crusading in the name of good and "
                                                     "order, and is a divine spell caster. Gaining some healing and "
                                                     "damage spells, paladins become a more balanced class and are "
                                                     "ideal for players who always forget to restock health potions. "
                                                     "Paladins hold to the adage that \"the best offense is a good "
                                                     "defense\", and thus lose the ability to equip two-handed "
                                                     "weapons (except hammers).",
                         str_plus=1, int_plus=0, wis_plus=1, con_plus=2, cha_plus=0, dex_plus=0,
                         equipment=dict(Weapon=items.SteelMace, OffHand=items.IronShield, Armor=items.Splint,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Sword', 'Mace', 'Hammer'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']},
                         pro_level=2)


class Crusader(Job):
    """
    Promotion: Warrior -> Paladin -> Crusader
    Pros: Can use shields and heavy armor; can cast healing spells
    Cons: Cannot equip 2-handed weapons except hammers; lower strength gain
    """

    def __init__(self):
        super().__init__(name="Crusader", description="The Crusader is a holy warrior, who values order and justice "
                                                      "above all else. Crusaders continue the path of the paladin, "
                                                      "fully embracing all aspects that carry over.",
                         str_plus=1, int_plus=0, wis_plus=2, con_plus=2, cha_plus=1, dex_plus=0,
                         equipment=dict(Weapon=items.AdamantiteMace, OffHand=items.TowerShield,
                                        Armor=items.PlateMail, Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Sword', 'Mace', 'Hammer'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']},
                         pro_level=3)


class Lancer(Job):
    """
    Promotion: Warrior -> Lancer -> Dragoon
    Pros: Can use polearms as 1-handed weapons; can equip shields and heavy armor
    Cons: Cannot equip other 2-handed weapons or dual wield
    """

    def __init__(self):
        super().__init__(name="Lancer", description="Lancers are typically more at home on the back of a horse but one "
                                                    "benefit this affords is the skill to wield a two-handed polearm "
                                                    "while also using a shield. They are also adept at leaping high "
                                                    "into the air and driving that polearm into their enemies.",
                         str_plus=2, int_plus=0, wis_plus=0, con_plus=1, cha_plus=0, dex_plus=1,
                         equipment=dict(Weapon=items.Pike, OffHand=items.IronShield, Armor=items.Splint,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Sword', 'Polearm'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']},
                         pro_level=2)


class Dragoon(Job):
    """
    Promotion: Warrior -> Lancer -> Dragoon
    Pros: Can use polearms as 1-handed weapons; can equip swords, shields and heavy armor
    Cons: Cannot equip other 2-handed weapons or dual wield
    """

    def __init__(self):
        super().__init__(name="Dragoon", description="Masters of spears, lances, and polearms and gifted with "
                                                     "supernatural abilities, Dragoons have become legendary for their"
                                                     " grace and power. Their intense training, said to have been "
                                                     "passed down by the dragon riders of old, allows these warriors to"
                                                     " leap unnaturally high into the air and strike their foes with "
                                                     "deadly force from above.",
                         str_plus=2, int_plus=0, wis_plus=0, con_plus=2, cha_plus=0, dex_plus=2,
                         equipment=dict(Weapon=items.Halberd, OffHand=items.TowerShield, Armor=items.PlateMail,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Sword', 'Polearm'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']},
                         pro_level=3)


class Mage(Job):
    """
    Promotion: Mage -> Sorcerer   -> Wizard
                    |
                    -> Warlock    -> Necromancer
                    |
                    -> Spellblade -> Knight Enchanter
    """

    def __init__(self):
        super().__init__(name="Mage", description="Mages possess exceptional aptitude for spell casting, able to "
                                                  "destroy an enemy with the wave of a finger. Weaker and more "
                                                  "vulnerable than any other class, they more than make up for it "
                                                  "with powerful magics.",
                         str_plus=0, int_plus=1, wis_plus=1, con_plus=0, cha_plus=0, dex_plus=0,
                         equipment=dict(Weapon=items.PineStaff, OffHand=items.NoOffHand, Armor=items.Tunic,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=1)


class Sorcerer(Job):
    """
    Promotion: Mage -> Sorcerer -> Wizard
    Pros: Higher intelligence gain; earlier access to spells and access to higher level spells
    Cons: None
    """

    def __init__(self):
        super().__init__(name="Sorcerer", description="A Sorcerer is someone who practices magic derived from "
                                                      "supernatural, occult, or arcane sources. They spend most of "
                                                      "their life reading massive tomes to expand their "
                                                      "knowledge and the rest of the time applying that knowledge at "
                                                      "the expense of anything in their path.",
                         str_plus=0, int_plus=2, wis_plus=2, con_plus=0, cha_plus=0, dex_plus=0,
                         equipment=dict(Weapon=items.IronshodStaff, OffHand=items.NoOffHand, Armor=items.SilverCloak,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=2)


class Wizard(Job):
    """
    Promotion: Mage -> Sorcerer -> Wizard
    Pros: Higher intelligence gain; earlier access to spells and access to higher level spells
    Cons: None
    """

    def __init__(self):
        super().__init__(name="Wizard", description="The Wizard is a master of arcane magic, unparalleled in their "
                                                    "magical ability. Being able to cast the most powerful spells makes"
                                                    " the wizard an ideal class for anyone who prefers to live fast "
                                                    "and die hard if not properly prepared.",
                         str_plus=0, int_plus=3, wis_plus=2, con_plus=0, cha_plus=1, dex_plus=0,
                         equipment=dict(Weapon=items.SerpentStaff, OffHand=items.NoOffHand,
                                        Armor=items.CloakEnchantment, Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=3)


class Warlock(Job):
    """
    Promotion: Mage -> Warlock -> Necromancer
    Pros: Higher strength and constitution gain; access to additional skills; gains access to shadow spells and familiar
    Cons: Lower intelligence gain and limited access to higher level spells; lose access to learned arcane Mage spells
    """

    def __init__(self):
        super().__init__(name="Warlock", description="The Warlock specializes in the dark arts, forsaking the arcane "
                                                     "training learned as a Mage. However this focus unlocks powerful "
                                                     "abilities, including the ability to summon a familiar to aid "
                                                     "them.",
                         str_plus=1, int_plus=1, wis_plus=1, con_plus=1, cha_plus=0, dex_plus=0,
                         equipment=dict(Weapon=items.SteelDagger, OffHand=items.TomeKnowledge, Armor=items.SilverCloak,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=2)


class Necromancer(Job):
    """
    Promotion: Mage -> Warlock -> Necromancer
    Pros: Higher strength and constitution gain; access to additional skills; more powerful familiars
    Cons: Lower intelligence gain and limited access to higher level spells
    """

    def __init__(self):
        super().__init__(name="Necromancer", description="The Necromancer is highly attuned to the dark arts and can "
                                                         "conjure the most demonic of powers, including the practicing"
                                                         " of forbidden blood magic.",
                         str_plus=1, int_plus=1, wis_plus=2, con_plus=2, cha_plus=0, dex_plus=0,
                         equipment=dict(Weapon=items.AdamantiteDagger, OffHand=items.Necronomicon,
                                        Armor=items.CloakEnchantment, Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=3)


class Spellblade(Job):
    """
    Promotion: Mage -> Spellblade -> Knight Enchanter
    Pros: Adds melee damage based on mana percentage and level; higher strength and constitution gain; can equip swords
    and light armor
    Cons: Lower intelligence and wisdom gain; cannot equip staves; gains spells at a much slower pace
    """

    def __init__(self):
        super().__init__(name="Spellblade", description="The Spellblade combines a magical affinity with a higher level"
                                                        " of martial prowess from the other magical classes. While they"
                                                        " no longer gain many of the same arcane spells, the spellblade"
                                                        " has unlocked the ability to channel the learned magical power"
                                                        " through their blade to devastate enemies.",
                         str_plus=2, int_plus=0, wis_plus=0, con_plus=2, cha_plus=0, dex_plus=0,
                         equipment=dict(Weapon=items.SteelSword, OffHand=items.TomeKnowledge, Armor=items.Cuirboulli,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Sword'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth', 'Light']},
                         pro_level=2)


class KnightEnchanter(Job):
    """
    Promotion: Mage -> Spellblade -> Knight Enchanter
    Pros: Adds melee damage based on mana percentage and level; higher strength and constitution gain; can equip swords
    and light armor
    Cons: Lower intelligence and wisdom; cannot equip staves; gains spells at a much slower pace
    """

    def __init__(self):
        super().__init__(name="Knight Enchanter", description="The Knight Enchanter uses their arcane powers to imbue"
                                                              " weapons with magical enchantments that can rival the "
                                                              "most powerful fighter.",
                         str_plus=2, int_plus=1, wis_plus=1, con_plus=2, cha_plus=0, dex_plus=0,
                         equipment=dict(Weapon=items.AdamantiteSword, OffHand=items.BookShadows,
                                        Armor=items.StuddedLeather, Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Sword'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth', 'Light']},
                         pro_level=3)


class Footpad(Job):
    """
    Promotion: Footpad -> Thief      -> Rogue
                       |
                       -> Inquisitor -> Seeker
                       |
                       -> Assassin   -> Ninja
    """

    def __init__(self):
        super().__init__(name="Footpad", description="Footpads are agile and perceptive, with an natural ability of "
                                                     "deftness. While more than capable of holding their own in hand-"
                                                     "to-hand combat, they truly excel at subterfuge. Footpads are the"
                                                     " only base class that can dual wield, albeit the offhand weapon "
                                                     "must be a dagger.",
                         str_plus=0, int_plus=0, wis_plus=0, con_plus=0, cha_plus=0, dex_plus=2,
                         equipment=dict(Weapon=items.BronzeSword, OffHand=items.BronzeDagger, Armor=items.PaddedArmor,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Sword', 'Mace'],
                                       'OffHand': ['Dagger'],
                                       'Armor': ['Light']},
                         pro_level=1)


class Thief(Job):
    """
    Promotion: Footpad -> Thief-> Rogue
    Pros: Access to stealth abilities earlier than other classes; uses dex instead of strength for damage; more balanced
     stat gain
    Cons: Lower dex gain
    """

    def __init__(self):
        super().__init__(name="Thief", description="Thieves prefer stealth over brute force, although a well-placed "
                                                   "backstab is still highly effective. They gain stealth abilities "
                                                   "more quickly than other classes and are typically more well-"
                                                   "balanced.",
                         str_plus=1, int_plus=1, wis_plus=0, con_plus=1, cha_plus=0, dex_plus=1,
                         equipment=dict(Weapon=items.SteelSword, OffHand=items.SteelDagger, Armor=items.Cuirboulli,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Sword', 'Mace'],
                                       'OffHand': ['Dagger'],
                                       'Armor': ['Light']},
                         pro_level=2)


class Rogue(Job):
    """
    Promotion: Footpad -> Thief -> Rogue
    Pros: Ability to dual wield (can use swords, maces, and fists in offhand); Access to stealth abilities earlier than
     other classes; uses dex instead of strength for damage; more balanced stat gain
    Cons: Lower dex gain
    """

    def __init__(self):
        super().__init__(name="Rogue", description="Rogues rely on skill, stealth, and their foes' vulnerabilities to "
                                                   "get the upper hand in any situation. They have a knack for finding "
                                                   "the solution to just about any problem, demonstrating a "
                                                   "resourcefulness and versatility that has no rival. They gain the "
                                                   "ability to dual wield swords, maces, and fist weapons.",
                         str_plus=1, int_plus=1, wis_plus=1, con_plus=1, cha_plus=1, dex_plus=1,
                         equipment=dict(Weapon=items.AdamantiteSword, OffHand=items.AdamantiteDagger,
                                        Armor=items.StuddedLeather, Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Sword', 'Mace'],
                                       'OffHand': ['Fist', 'Dagger', 'Sword', 'Mace'],
                                       'Armor': ['Light']},
                         pro_level=3)


class Inquisitor(Job):
    """
    Promotion: Footpad -> Inquisitor -> Seeker
    Pros: Increased strength and constitution; ability to perceive enemy status and weaknesses; access to medium armor,
          shields, and some spells
    Cons: Lower dexterity; lose ability to dual wield
    """

    def __init__(self):
        super().__init__(name="Inquisitor", description="Inquisitors excel at rooting out hidden secrets and "
                                                        "unraveling mysteries. They rely on a sharp eye for detail, "
                                                        "but also on a finely honed ability to read the words and "
                                                        "deeds of other creatures to determine their true intent. "
                                                        "They excel at defeating creatures that hide among and prey "
                                                        "upon ordinary folk, and their mastery of lore and sharp eye "
                                                        "make them well-equipped to expose and end hidden evils.",
                         str_plus=1, int_plus=0, wis_plus=0, con_plus=2, cha_plus=1, dex_plus=0,
                         equipment=dict(Weapon=items.SteelSword, OffHand=items.IronShield, Armor=items.ScaleMail,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Sword', 'Mace'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Light', 'Medium']},
                         pro_level=2)


class Seeker(Job):
    """
    Promotion: Footpad -> Inquisitor -> Seeker
    Pros: Increased strength and constitution; ability to perceive enemy status and weaknesses; access to medium armor,
          shields, and some spells
    Cons: Lower dexterity; lose ability to dual wield
    """

    def __init__(self):
        super().__init__(name="Seeker", description="Seekers are very good at moving through the dungeon, being able to"
                                                    " levitate, locate other characters, and teleport. They can’t "
                                                    "directly kill monsters with their magical abilities, but a Seeker "
                                                    "does well with a weapon in hand. They are also the best at "
                                                    "mapping the dungeon and detecting any types of ‘anomalies’ they "
                                                    "may encounter in the depths.",
                         str_plus=1, int_plus=1, wis_plus=1, con_plus=2, cha_plus=1, dex_plus=0,
                         equipment=dict(Weapon=items.AdamantiteSword, OffHand=items.TowerShield,
                                        Armor=items.Breastplate, Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Sword', 'Mace'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Light', 'Medium']},
                         pro_level=3)


class Assassin(Job):
    """
    Promotion: Footpad -> Assassin -> Ninja
    Pros: Higher dexterity and wisdom (magic defense); earlier access to skills and more powerful skills; can use fist
      weapons in the offhand slot; uses dex instead of strength for damage
    Cons: Lower strength and constitution; can only equip daggers or fist weapons; do not gain DEX bonus with fist
      weapons
    """

    def __init__(self):
        super().__init__(name="Assassin", description="You focus your training on the grim art of death. Those who "
                                                      "adhere to this archetype are diverse: hired killers, spies, "
                                                      "bounty hunters, and even specially anointed priests trained to "
                                                      "exterminate  the enemies of their deity. Stealth, poison, and "
                                                      "disguise help you eliminate your foes with deadly efficiency.",
                         str_plus=0, int_plus=0, wis_plus=2, con_plus=0, cha_plus=0, dex_plus=2,
                         equipment=dict(Weapon=items.SteelDagger, OffHand=items.SteelDagger, Armor=items.Cuirboulli,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger'],
                                       'OffHand': ['Fist', 'Dagger'],
                                       'Armor': ['Light']},
                         pro_level=2)


class Ninja(Job):
    """
    Promotion: Footpad -> Assassin -> Ninja
    Pros: Higher dexterity and wisdom (magic defense); earlier access to skills and more powerful skills; the only class
      that can equip Ninja swords; uses dex instead of strength for damage
    Cons: Lower strength and constitution; can only equip daggers
    """

    def __init__(self):
        super().__init__(name="Ninja", description="Since a Ninja desires quickness, they are very specific about the "
                                                   "items they use. Ninjas are not allowed to wear most types of armor "
                                                   "and other items. However, having access to special weapons that "
                                                   "only they can use, Ninjas possess the skills of Critically hitting "
                                                   "and Backstabbing their opponents, along with moderate thieving "
                                                   "skills.",
                         str_plus=0, int_plus=1, wis_plus=2, con_plus=0, cha_plus=0, dex_plus=3,
                         equipment=dict(Weapon=items.Tanto, OffHand=items.AdamantiteDagger,
                                        Armor=items.StuddedLeather, Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Ninja Blades'],
                                       'OffHand': ['Fist', 'Dagger', 'Ninja Blades'],
                                       'Armor': ['Light']},
                         pro_level=3)


class Healer(Job):
    """
    Promotion: Healer -> Cleric -> Templar
                      |
                      -> Priest -> Archbishop
                      |
                      -> Monk   -> Master Monk

    """

    def __init__(self):
        super().__init__(name="Healer", description="Healers primary role in battle is to preserve the party with "
                                                    "healing and protective spells. Well, how does that work when "
                                                    "they are alone? Pretty much the same way!",
                         str_plus=0, int_plus=1, wis_plus=1, con_plus=0, cha_plus=0, dex_plus=0,
                         equipment=dict(Weapon=items.PineStaff, OffHand=items.NoOffHand, Armor=items.Tunic,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Mace', 'Staff'],
                                       'OffHand': ['Shield', 'Tome'],
                                       'Armor': ['Cloth', 'Light']},
                         pro_level=1)


class Cleric(Job):
    """
    Promotion: Healer -> Cleric -> Templar
    Pros: Can equip medium armor; gains additional protective abilities including turn undead; increased strength and
    constitution
    Cons: gains fewer healing spells compared to Priest class; no longer gains holy damage spells; lose access to tomes
    """

    def __init__(self):
        super().__init__(name="Cleric", description="Where the paladin is a warrior that can heal, a cleric is a "
                                                    "healer that can hold their own in combat. The biggest difference"
                                                    "is that the cleric cannot equip heavy armor (that will come...)"
                                                    " but gain additional protective abilities that paladins do not.",
                         str_plus=1, int_plus=0, wis_plus=2, con_plus=1, cha_plus=0, dex_plus=0,
                         equipment=dict(Weapon=items.SteelMace, OffHand=items.IronShield, Armor=items.ScaleMail,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Mace', 'Staff'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Light', 'Medium']},
                         pro_level=2)


class Templar(Job):
    """
    Promotion: Healer -> Cleric -> Templar
    Pros: Can equip heavy armor and hammers; gains additional protective abilities including turn undead; increased
    strength and constitution
    Cons: gains fewer healing spells compared to Archbishop class; no longer gains holy damage spells; lose access to
    tomes and staves
    """

    def __init__(self):
        super().__init__(name="Templar", description="A templar exemplifies the best of both worlds, able to heal and"
                                                     " protect while also being able to dish out quite a bit of damage"
                                                     " along the way. While a templar is right at home with a mace and"
                                                     " a shield, they have also trained in the art of the 2-handed "
                                                     "hammer.",
                         str_plus=1, int_plus=0, wis_plus=2, con_plus=2, cha_plus=0, dex_plus=1,
                         equipment=dict(Weapon=items.AdamantiteMace, OffHand=items.TowerShield, Armor=items.PlateMail,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Mace', 'Hammer'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Light', 'Medium', 'Heavy']},
                         pro_level=3)


class Priest(Job):
    """
    Promotion: Healer -> Priest -> Archbishop
    Pros: Access to the best healing and holy spells; only class that can equip the holy staff and Princess Guard
    Cons: Can only equip cloth armor; lose access to shields
    """

    def __init__(self):
        super().__init__(name="Priest", description="A priest channels the holy light through prayer, accessing "
                                                    "powerful regenerative and cleansing spells. While they can only "
                                                    "equip cloth armor, they gain the ability to increase their "
                                                    "defense at the expense of mana.",
                         str_plus=0, int_plus=1, wis_plus=3, con_plus=0, cha_plus=0, dex_plus=0,
                         equipment=dict(Weapon=items.IronshodStaff, OffHand=items.NoOffHand, Armor=items.SilverCloak,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Mace', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=2)


class Archbishop(Job):
    """
    Promotion: Healer -> Priest -> Archbishop
    Pros: Access to the best healing and holy spells; only class that can equip the holy staff and Princess Guard
    Cons: Can only equip cloth armor; lose access to shields
    """

    def __init__(self):
        super().__init__(name="Archbishop", description="An archbishop attunes with the holy light for the most "
                                                        "powerful healing, protective, and holy magics available.",
                         str_plus=0, int_plus=1, wis_plus=4, con_plus=0, cha_plus=1, dex_plus=0,
                         equipment=dict(Weapon=items.HolyStaff, OffHand=items.NoOffHand, Armor=items.CloakEnchantment,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Mace', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=3)


class Monk(Job):
    """
    Promotion: Healer -> Monk -> Master Monk
    Pros: Adds strength AND dexterity to hit and damage rolls when equipped with fist(s)
    Cons: Can only wear light armor; stops gaining healing spells and wisdom gains; can only equip fist weapons in
    offhand
    """

    def __init__(self):
        super().__init__(name="Monk", description="Monks abandon the cloth to focus the mind into the body, harnessing "
                                                  "the inner power of the chi. While an adept fighter with a staff, "
                                                  "monks specialize in hand-to-hand combat, adding both strength and "
                                                  "dexterity to their damage when equipped with Fist weapons.",
                         str_plus=1, int_plus=0, wis_plus=0, con_plus=1, cha_plus=0, dex_plus=2,
                         equipment=dict(Weapon=items.SteelFist, OffHand=items.SteelFist, Armor=items.Cuirboulli,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Staff'],
                                       'OffHand': ['Fist'],
                                       'Armor': ['Light']},
                         pro_level=2)


class MasterMonk(Job):
    """
    Promotion: Healer -> Monk -> Master Monk
    Pros: Adds strength AND dexterity to hit and damage rolls when equipped with fist(s)
    Cons: Can only wear light armor; stops gaining healing spells and wisdom gains; can only equip fist weapons in
    offhand
    """

    def __init__(self):
        super().__init__(name="Master Monk", description="A master monk has fully attuned to the power of the chi, "
                                                         "becoming unparalleled at dealing damage with its fists.",
                         str_plus=2, int_plus=0, wis_plus=0, con_plus=2, cha_plus=0, dex_plus=1,
                         equipment=dict(Weapon=items.AdamantiteFist, OffHand=items.AdamantiteFist,
                                        Armor=items.StuddedLeather, Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Staff'],
                                       'OffHand': ['Fist'],
                                       'Armor': ['Light']},
                         pro_level=3)


class Pathfinder(Job):
    """
    Promotion: Pathfinder -> Druid   -> Lycan
                          |
                          -> Diviner -> Geomancer
                          |
                          -> Shaman  -> Soulcatcher
    """

    def __init__(self):
        super().__init__(name="Pathfinder", description="In philosophy, naturalism is the belief that only natural laws"
                                                        " and forces operate in the universe. A pathfinder embraces "
                                                        "this idea by being attuned to one or more of the various "
                                                        "aspects of nature, including the 4 classical elements: Earth, "
                                                        "Wind, Water, and Fire.",
                         str_plus=0, int_plus=0, wis_plus=1, con_plus=1, cha_plus=0, dex_plus=0,
                         equipment=dict(Weapon=items.BronzeDagger, OffHand=items.WoodShield, Armor=items.HideArmor,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Mace', 'Polearm', 'Hammer', 'Staff'],
                                       'OffHand': ['Shield', 'Tome'],
                                       'Armor': ['Cloth', 'Light', 'Medium']},
                         pro_level=1)


class Druid(Job):
    """
    Promotion: Pathfinder -> Druid -> Lycan
    Pros: gains animal abilities and statistics when shifted
    Cons: loses ability to wear medium armor and shields
    """

    def __init__(self):
        super().__init__(name="Druid", description="Druids act as an extension of nature to call upon the elemental"
                                                   " forces, embodying nature's wrath and mystique. This attunement "
                                                   "with nature allows druids to emulate creatures of the animal world,"
                                                   " transforming into them and gaining there specs and abilities. They"
                                                   " lose the ability to wear medium armor and shields but gain "
                                                   "natural weapons and armor when transformed.",
                         str_plus=1, int_plus=0, wis_plus=1, con_plus=1, cha_plus=0, dex_plus=1,
                         equipment=dict(Weapon=items.IronshodStaff, OffHand=items.NoOffHand, Armor=items.Cuirboulli,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Mace', 'Polearm', 'Hammer', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth', 'Light']},
                         pro_level=2)


class Lycan(Job):
    """
    Promotion: Pathfinder -> Druid -> Lycan
    Pros: mastered the art of shapeshifting
    Cons: loses ability to wear medium armor and shields; lose certain spells and abilities
    """

    def __init__(self):
        super().__init__(name="Lycan", description="Unlike the lycans of mythology who have little choice in morphing "
                                                   "into their animal form, these lycans have gained mastery over their"
                                                   " powers to become something truly terrifying.",
                         str_plus=1, int_plus=0, wis_plus=1, con_plus=2, cha_plus=0, dex_plus=2,
                         equipment=dict(Weapon=items.WarHammer, OffHand=items.NoOffHand, Armor=items.StuddedLeather,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Mace', 'Polearm', 'Hammer', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth', 'Light']},
                         pro_level=3)


class Diviner(Job):
    """
    Promotion: Pathfinder -> Diviner -> Geomancer
    Pros: added benefits/reduced effect of special tiles (once implemented); can learn enemy spells when cast against
    Cons: loses access to shields and some weapon choices
    """

    def __init__(self):
        super().__init__(name="Diviner", description="A diviner works with nature to balance the four classical "
                                                     "elements of Earth, Wind, Water, and Fire, and can learn certain "
                                                     "spells cast against them within these domains. Diviners are also "
                                                     "hyper aware of their surroundings, limiting the effect of traps "
                                                     "and magic effects.",
                         str_plus=0, int_plus=1, wis_plus=2, con_plus=1, cha_plus=0, dex_plus=0,
                         equipment=dict(Weapon=items.SteelDagger, OffHand=items.TomeKnowledge, Armor=items.SilverCloak,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=2)


class Geomancer(Job):
    """
    Promotion: Pathfinder -> Diviner -> Geomancer
    Pros: added benefits/reduced effect of special tiles (once implemented); can learn enemy spells when cast against
    Cons: loses access to shields and some weapon choices
    """

    def __init__(self):
        super().__init__(name="Geomancer", description="Classified as one of the 7 forbidden arts, geomancers have "
                                                       "mastered natural phenomena, granting them access to some of the"
                                                       " most devastating elemental spells. Their adeptness with "
                                                       "magical effects allow geomancers to manipulate special tiles to"
                                                       " their advantage.",
                         str_plus=0, int_plus=2, wis_plus=2, con_plus=2, cha_plus=0, dex_plus=0,
                         equipment=dict(Weapon=items.AdamantiteDagger, OffHand=items.DragonRouge,
                                        Armor=items.CloakEnchantment, Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Staff'],
                                       'OffHand': ['Tome'],
                                       'Armor': ['Cloth']},
                         pro_level=3)


class Shaman(Job):
    """
    Promotion: Pathfinder -> Shaman -> Soulcatcher
    Pros: chance to gain essence from enemies; can dual wield fist weapons; can imbue weapons with elemental fury
    Cons: does not gain DEX bonus from fist weapons; loses access to tomes and some weapons
    """

    def __init__(self):
        super().__init__(name="Shaman", description="Shamans are spiritual guides that seek to help the dead to pass on"
                                                    " to the afterlife. In doing so, they can sometimes absorb some "
                                                    "essence of the departed. They also commune with the chaotic "
                                                    "elements, gaining the ability to imbue their weapons.",
                         str_plus=1, int_plus=0, wis_plus=1, con_plus=1, cha_plus=0, dex_plus=1,
                         equipment=dict(Weapon=items.SteelFist, OffHand=items.SteelFist, Armor=items.ScaleMail,
                                        Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Mace', 'Staff'],
                                       'OffHand': ['Fist', 'Shield'],
                                       'Armor': ['Cloth', 'Light', 'Medium']},
                         pro_level=2)


class Soulcatcher(Job):
    """
    Promotion: Pathfinder -> Shaman -> Soulcatcher
    Pros: increased chance to gain essence from enemies; can dual wield fist weapons; can imbue weapons with elemental
      fury
    Cons: does not gain DEX bonus from fist weapons; loses access to tomes and some weapons
    """

    def __init__(self):
        super().__init__(name="Soulcatcher", description="Soulcatchers do everything that a shaman can do, only better."
                                                         " They are much more adept at absorbing the essence of the "
                                                         "dead, while mastering elemental fury.",
                         str_plus=2, int_plus=1, wis_plus=1, con_plus=1, cha_plus=0, dex_plus=1,
                         equipment=dict(Weapon=items.AdamantiteFist, OffHand=items.AdamantiteFist,
                                        Armor=items.Breastplate, Pendant=items.NoPendant, Ring=items.NoRing),
                         restrictions={'Weapon': ['Fist', 'Dagger', 'Mace', 'Staff'],
                                       'OffHand': ['Fist', 'Shields'],
                                       'Armor': ['Cloth', 'Light', 'Medium']},
                         pro_level=3)
