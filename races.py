###########################################
""" race manager """

# Imports
from textwrap import wrap


# Race objects
class Race:
    """
    Base definition for the Race class
    Stat parameters define the starting stats for each race
    Class restriction lists the available classes for each race
    Resistance describes each race's resistances to magic
    """
    def __init__(self, name, description, strength, intel, wisdom, con, charisma, dex, cls_res, resistance):
        self.name = name
        self.description = "\n".join(wrap(description, 75))
        self.strength = strength
        self.intel = intel
        self.wisdom = wisdom
        self.con = con
        self.charisma = charisma
        self.dex = dex
        self.cls_res = cls_res
        self.resistance = resistance


class Human(Race):

    def __init__(self):
        super().__init__(name="Human", description="Humans are something you can relate to. They are the most "
                                                   "versatile of all races, making a viable option for all classes. "
                                                   "While they have no magical resistances, they also have no "
                                                   "weaknesses.",
                         strength=10, intel=10, wisdom=10, con=10, charisma=10, dex=10,
                         cls_res={'Base': ['Warrior', 'Mage', 'Footpad', 'Healer', 'Pathfinder'],
                                  'First': ['Weapon Master', 'Paladin', 'Lancer', 'Sentinel',
                                            'Sorcerer', 'Warlock', 'Spellblade',
                                            'Thief', 'Inquisitor', 'Assassin',
                                            'Cleric', 'Priest', 'Monk',
                                            'Druid', 'Diviner', 'Shaman'],
                                  'Second': ['Berserker', 'Crusader', 'Dragoon', 'Stalwart Defender',
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


class Elf(Race):

    def __init__(self):
        super().__init__(name="Elf", description="Elves are the magic users of the game. They are excellent spell "
                                                 "casters and have decent resistance to elemental magic. They are not,"
                                                 " however, very good at fighting with weapons and have low "
                                                 "constitution, making them more susceptible to death magic.",
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
                                     'Shadow': 0.,
                                     'Death': -0.2,
                                     'Stone': 0.,
                                     'Holy': 0.,
                                     'Poison': 0.,
                                     'Physical': -0.1}
                         )


class HalfElf(Race):

    def __init__(self):
        super().__init__(name="Half Elf", description="Half elves are the result of the interbreeding between humans and "
                                                      "elves. They are just as versatile as humans and possess an "
                                                      "improved magical prowess, as well as mild elemental resistance. "
                                                      "Like their elf cousins, they do have a slight susceptibility to "
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
                                     'Shadow': 0.,
                                     'Death': -0.1,
                                     'Stone': 0.,
                                     'Holy': 0.,
                                     'Poison': 0.,
                                     'Physical': -0.1}
                         )


class Giant(Race):

    def __init__(self):
        super().__init__(name="Giant", description="A brutal race standing over eight feet tall, Giants make the best"
                                                   " Warriors one can find. Giants are a sturdy race and have great"
                                                   " resistance against death spells, as well as a mild resistance" 
                                                   " to poisons an physical damage. However, they are not the most"
                                                   " pious beings and are weak against holy spells.",
                         strength=15, intel=7, wisdom=8, con=14, charisma=6, dex=10,
                         cls_res={'Base': ['Warrior'],
                                  'First': ['Weapon Master'],
                                  'Second': ['Berserker']},
                         resistance={'Fire': 0.,
                                     'Ice': 0.,
                                     'Electric': 0.,
                                     'Water': 0.,
                                     'Earth': 0.,
                                     'Wind': 0.,
                                     'Shadow': 0.,
                                     'Death': 0.5,
                                     'Stone': 0.,
                                     'Holy': -0.3,
                                     'Poison': 0.33,
                                     'Physical': 0.2}
                         )


class Gnome(Race):

    def __init__(self):
        super().__init__(name="Gnome", description="Gnomes are very charismatic, giving them a distinct advantage in "
                                                   "money making, vendor relations, and are especially lucky. They are "
                                                   "also above average spell caster with a slight affinity toward the "
                                                   "divine, giving them a slight resistance to holy spells. Gnomes "
                                                   "prefer the civilized world and thus are not found among the ranks"
                                                   " of Pathfinders.",
                         strength=8, intel=10, wisdom=12, con=8, charisma=12, dex=10,
                         cls_res={'Base': ['Warrior', 'Mage', 'Footpad', 'Healer'],
                                  'First': ['Weapon Master', 'Paladin',
                                            'Sorcerer', 'Spellblade',
                                            'Thief', 'Inquisitor', 'Assassin',
                                            'Cleric', 'Priest'],
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


class Dwarf(Race):

    def __init__(self):
        super().__init__(name="Dwarf", description="Dwarves are a versatile race, rivaled only by the human races. They are"
                                                   " robust but are not very nimble and have a healthy mistrust of the "
                                                   "arcane. As beings of the Earth, dwarves have resistance against"
                                                   " earth, poison, and physical damage but are weak against shadow magic.",
                         strength=12, intel=10, wisdom=10, con=12, charisma=8, dex=8,
                         cls_res={'Base': ['Warrior', 'Healer', 'Pathfinder'],
                                  'First': ['Weapon Master', 'Paladin',
                                            'Cleric', 'Priest',
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


class HalfOrc(Race):

    def __init__(self):
        super().__init__(name="Half Orc", description="Half orcs are the result of interbreeding between humans and "
                                                      "orcs, which while rare does occur. While not a strong as their "
                                                      "fullblood brethren, half orcs are much stronger on average "
                                                      "than humans. However the stigma related to half orcs makes "
                                                      "them far less charismatic, while there inherit bloodlust "
                                                      "makes any pursuit of the divine unappealing.",
                         strength=12, intel=10, wisdom=8, con=11, charisma=8, dex=11,
                         cls_res={'Base': ['Warrior', 'Mage', 'Footpad', 'Pathfinder'],
                                  'First': ['Weapon Master', 'Lancer',
                                            'Sorcerer', 'Warlock', 'Spellblade',
                                            'Thief', 'Inquisitor', 'Assassin',
                                            'Diviner', 'Shaman'],
                                  'Second': ['Berserker', 'Dragoon',
                                             'Wizard', 'Necromancer', 'Knight Enchanter',
                                             'Rogue', 'Seeker', 'Ninja',
                                             'Geomancer', 'Soulcatcher']},
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
