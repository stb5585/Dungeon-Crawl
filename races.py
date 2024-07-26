###########################################
""" race manager """

# Imports
import os
from dataclasses import dataclass
from typing import Dict, List

import storyline


# Functions
def define_race():
    """
    Allows the player_char to choose which race they wish to play
    """
    while True:
        print("Choose a race for your character.")
        race_index = storyline.get_response(list(races_dict))
        race = list(races_dict.values())[race_index]()
        print(race)
        print(f"Are you sure you want to play as a {list(races_dict.values())[race_index]().name.lower()}? ")
        choose = storyline.get_response(["Yes", "No"])
        if not choose:
            break
        os.system('cls' if os.name == 'nt' else 'clear')
    return list(races_dict.values())[race_index]()


@dataclass
class Race:
    """
    Base definition for the Race class
    Stat parameters define the starting stats for each race
    Class restriction lists the available classes for each race
    Resistance describes each race's resistances to magic
    """

    name: str
    description: str
    strength: int
    intel: int
    wisdom: int
    con: int
    charisma: int
    dex: int
    cls_res: Dict[str, List[str]]
    resistance: Dict[str, float]

    def __str__(self):
        return (f"\n===========Description=============\n"
                f"{self.description}\n"
                f"==============Stats================\n"
                f"          Strength: {self.strength}\n"
                f"      Intelligence: {self.intel}\n"
                f"            Wisdom: {self.wisdom}\n"
                f"      Constitution: {self.con}\n"
                f"          Charisma: {self.charisma}\n"
                f"         Dexterity: {self.dex}\n"
                f"===========Resistances=============\n"
                f"            Fire: {self.resistance['Fire']}\n"
                f"             Ice: {self.resistance['Ice']}\n"
                f"        Electric: {self.resistance['Electric']}\n"
                f"           Water: {self.resistance['Water']}\n"
                f"           Earth: {self.resistance['Earth']}\n"
                f"            Wind: {self.resistance['Wind']}\n"
                f"          Shadow: {self.resistance['Shadow']}\n"
                f"           Death: {self.resistance['Death']}\n"
                f"           Stone: {self.resistance['Stone']}\n"
                f"            Holy: {self.resistance['Holy']}\n"
                f"          Poison: {self.resistance['Poison']}\n"
                f"        Physical: {self.resistance['Physical']}\n"
                f"===================================\n")


@dataclass
class Human(Race):
    """

    """

    def __init__(self):
        super().__init__(name="Human", description="Humans are something you, can relate \nto. They are the most "
                                                   "versatile of \nall races, making a viable option \nfor all classes. "
                                                   "While they have no \nmagical resistances, they also have \nno "
                                                   "weaknesses.",
                         strength=10, intel=10, wisdom=10, con=10, charisma=10, dex=10,
                         cls_res={'Base': ['Warrior', 'Mage', 'Footpad', 'Healer', 'Pathfinder'],
                                  'First': ['Weapon Master', 'Paladin', 'Lancer',
                                            'Sorcerer', 'Warlock', 'Spellblade',
                                            'Thief', 'Inquisitor', 'Assassin',
                                            'Cleric', 'Priest', 'Monk',
                                            'Druid', 'Diviner', 'Shaman'],
                                  'Second': ['Berserker', 'Crusader', 'Dragoon',
                                             'Wizard', 'Necromancer', 'Knight Enchanter',
                                             'Rogue', 'Seeker', 'Ninja',
                                             'Templar', 'Archbishop', 'Master Monk',
                                             'Lycan', 'Geomancer', 'Soulcatcher']},
                         resistance={'Fire': 0.,
                                     'Ice': 0.,
                                     'Electric': 0.,
                                     'Water': 0.,
                                     'Earth': 0.,
                                     'Wind': 0.,
                                     'Shadow': 0.,
                                     'Death': 0.,
                                     'Stone': 0.,
                                     'Holy': 0.,
                                     'Poison': 0.,
                                     'Physical': 0.}
                         )


@dataclass
class Elf(Race):
    """

    """

    def __init__(self):
        super().__init__(name="Elf", description="Elves are the magic users of the \ngame. They are excellent spell \n"
                                                 "casters and have decent resistance \nto elemental magic. They are not,"
                                                 " \nhowever, very good at fighting with \nweapons and have a low "
                                                 "constitution, \nmaking them more susceptible to death \nmagic.",
                         strength=6, intel=12, wisdom=11, con=8, charisma=11, dex=12,
                         cls_res={'Base': ['Mage', 'Footpad', 'Healer', 'Pathfinder'],
                                  'First': ['Sorcerer', 'Warlock', 'Spellblade',
                                            'Thief', 'Inquisitor', 'Assassin',
                                            'Priest',
                                            'Druid', 'Diviner'],
                                  'Second': ['Wizard', 'Necromancer', 'Knight Enchanter',
                                             'Rogue', 'Seeker', 'Ninja',
                                             'Archbishop',
                                             'Lycan', 'Geomancer']},
                         resistance={'Fire': 0.25,
                                     'Ice': 0.25,
                                     'Electric': 0.25,
                                     'Water': 0.25,
                                     'Earth': 0.25,
                                     'Wind': 0.25,
                                     'Shadow': 0,
                                     'Death': -0.2,
                                     'Stone': 0.,
                                     'Holy': 0.,
                                     'Poison': 0.,
                                     'Physical': -0.1}
                         )


@dataclass
class HalfElf(Race):
    """

    """

    def __init__(self):
        super().__init__(name="Half Elf", description="Half elves are the result of inter-\nbreeding between humans and "
                                                      "elves. \nThey are just as versatile as humans \nand possess an "
                                                      "improved magical prowess, \nas well as mild elemental resistance. \n"
                                                      "Like their elf cousins, they do have \na slight susceptibility to "
                                                      "death magic.",
                         strength=8, intel=12, wisdom=10, con=8, charisma=10, dex=12,
                         cls_res={'Base': ['Warrior', 'Mage', 'Footpad', 'Healer', 'Pathfinder'],
                                  'First': ['Paladin', 'Lancer',
                                            'Sorcerer', 'Warlock', 'Spellblade',
                                            'Thief', 'Inquisitor', 'Assassin',
                                            'Cleric', 'Priest', 'Monk',
                                            'Druid', 'Diviner', 'Shaman'],
                                  'Second': ['Crusader', 'Dragoon',
                                             'Wizard', 'Necromancer', 'Knight Enchanter',
                                             'Rogue', 'Seeker', 'Ninja',
                                             'Templar', 'Archbishop', 'Master Monk',
                                             'Lycan', 'Geomancer', 'Soulcatcher']},
                         resistance={'Fire': 0.1,
                                     'Ice': 0.1,
                                     'Electric': 0.1,
                                     'Water': 0.1,
                                     'Earth': 0.1,
                                     'Wind': 0.1,
                                     'Shadow': 0,
                                     'Death': -0.1,
                                     'Stone': 0.,
                                     'Holy': 0.,
                                     'Poison': 0.,
                                     'Physical': -0.1}
                         )


@dataclass
class Giant(Race):
    """

    """

    def __init__(self):
        super().__init__(name="Giant", description="Known for their brutal ways and having \nthe advantage of"
                                                   " being over eight feet \ntall, Giants make the best Warriors \none can"
                                                   " find. Giants are a sturdy race \nand have great resistance against "
                                                   "\ndeath spells, as well as a mild resistance \nto poisons and physical "
                                                   "damage. However, \nthey are not the most pious beings \nand are weak "
                                                   "against holy spells \nand have the lowest charisma of any class.",
                         strength=15, intel=7, wisdom=8, con=14, charisma=6, dex=10,
                         cls_res={'Base': ['Warrior'],
                                  'First': ['Weapon Master'],
                                  'Second': ['Berserker']},
                         resistance={'Fire': 0,
                                     'Ice': 0,
                                     'Electric': 0,
                                     'Water': 0,
                                     'Earth': 0,
                                     'Wind': 0,
                                     'Shadow': 0,
                                     'Death': 0.5,
                                     'Stone': 0.,
                                     'Holy': -0.3,
                                     'Poison': 0.33,
                                     'Physical': 0.2}
                         )


@dataclass
class Gnome(Race):
    """

    """

    def __init__(self):
        super().__init__(name="Gnome", description="Gnomes are very charismatic, giving \nthem a distinct advantage in "
                                                   "money \nmaking, vendor relations, and are \nespecially lucky. They are "
                                                   "also \nabove average spell caster with a \nslight affinity toward the "
                                                   "divine, \ngiving them a slight resistance to \nholy spells. Gnomes "
                                                   "prefer the civilized \nworld and thus are not found among the \nranks"
                                                   " of Pathfinders.",
                         strength=8, intel=10, wisdom=12, con=8, charisma=12, dex=10,
                         cls_res={'Base': ['Warrior', 'Mage', 'Footpad', 'Healer'],
                                  'First': ['Weapon Master', 'Paladin', 'Lancer',
                                            'Sorcerer', 'Spellblade',
                                            'Thief', 'Inquisitor', 'Assassin',
                                            'Cleric', 'Priest', 'Monk'],
                                  'Second': ['Berserker', 'Crusader', 'Dragoon',
                                             'Wizard', 'Knight Enchanter',
                                             'Rogue', 'Seeker', 'Ninja',
                                             'Templar', 'Archbishop', 'Master Monk']},
                         resistance={'Fire': 0.,
                                     'Ice': 0.,
                                     'Electric': 0.,
                                     'Water': 0.,
                                     'Earth': 0.,
                                     'Wind': 0.,
                                     'Shadow': -0.2,
                                     'Death': 0.,
                                     'Stone': 0.,
                                     'Holy': 0.2,
                                     'Poison': 0.,
                                     'Physical': 0.}
                         )


@dataclass
class Dwarf(Race):
    """

    """

    def __init__(self):
        super().__init__(name="Dwarf", description="Dwarves are a versatile race, rivaled \nonly by the human races. They are"
                                                   " \nrobust but are not very nimble and \nhave a healthy mistrust of the "
                                                   "\narcane. As beings of the Earth, \ndwarves have resistance against "
                                                   "earth, \npoison, and physical damage but are \nweak against shadow magic.",
                         strength=12, intel=10, wisdom=10, con=12, charisma=8, dex=8,
                         cls_res={'Base': ['Warrior', 'Healer', 'Pathfinder'],
                                  'First': ['Weapon Master', 'Paladin', 'Lancer',
                                            'Cleric', 'Priest', 'Monk',
                                            'Diviner', 'Shaman'],
                                  'Second': ['Berserker', 'Crusader', 'Dragoon',
                                             'Templar', 'Archbishop', 'Master Monk',
                                             'Geomancer', 'Soulcatcher']},
                         resistance={'Fire': 0.,
                                     'Ice': 0.,
                                     'Electric': 0.,
                                     'Water': 0.,
                                     'Earth': 0.25,
                                     'Wind': 0.,
                                     'Shadow': -0.3,
                                     'Death': 0.,
                                     'Stone': 0.,
                                     'Holy': 0.,
                                     'Poison': 0.25,
                                     'Physical': 0.1}
                         )


@dataclass
class HalfOrc(Race):
    """

    """

    def __init__(self):
        super().__init__(name="Half Orc", description="Half orcs are the result of inter-\nbreeding between humans and "
                                                      "orcs, \nwhich while rare does occur. While not \na strong as their "
                                                      "full-blood brethren, \nhalf orcs are much stronger on average \n"
                                                      "than humans. However the stigma related \nto half orcs makes "
                                                      "them far less \ncharismatic. There inherit bloodlust \nmakes the "
                                                      "pursuit of the divine \nunappealing.",
                         strength=13, intel=10, wisdom=8, con=11, charisma=8, dex=10,
                         cls_res={'Base': ['Warrior', 'Mage', 'Footpad', 'Pathfinder'],
                                  'First': ['Weapon Master', 'Lancer',
                                            'Sorcerer', 'Warlock', 'Spellblade',
                                            'Thief', 'Inquisitor', 'Assassin',
                                            'Druid', 'Diviner', 'Shaman'],
                                  'Second': ['Berserker', 'Dragoon',
                                             'Wizard', 'Necromancer', 'Knight Enchanter',
                                             'Rogue', 'Seeker', 'Ninja',
                                             'Lycan', 'Geomancer', 'Soulcatcher']},
                         resistance={'Fire': 0.,
                                     'Ice': 0.,
                                     'Electric': 0.,
                                     'Water': 0.,
                                     'Earth': 0.,
                                     'Wind': 0.,
                                     'Shadow': 0.2,
                                     'Death': 0.1,
                                     'Stone': 0.,
                                     'Holy': -0.2,
                                     'Poison': 0.1,
                                     'Physical': 0.}
                         )


races_dict = {'Human': Human,
              'Elf': Elf,
              'Half Elf': HalfElf,
              "Giant": Giant,
              'Gnome': Gnome,
              'Dwarf': Dwarf,
              'Half Orc': HalfOrc}
