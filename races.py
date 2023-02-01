###########################################
""" race manager """

# Imports
import os

import storyline


# Functions
def define_race():
    """
    Allows the player to choose which race they wish to play
    """
    race_list = [Human, Elf, HalfElf, Giant, Gnome, Dwarf, HalfOrc]
    while True:
        create_race = {1: {"Options": [('Human', 0), ('Elf', 1), ('Half Elf', 2), ('Giant', 3), ('Gnome', 4),
                                       ('Dwarf', 5), ('Half Orc', 6)],
                           "Text": ["Choose a race for your character.\n"]}}
        race_index = storyline.story_flow(create_race, response=True)
        race = race_list[race_index]()
        print(race)
        choose = input("Are you sure you want to play as a {}? ".format(race_list[race_index]().name.lower()))
        if choose in ['y', 'yes']:
            break
    os.system('cls' if os.name == 'nt' else 'clear')
    return race_list[race_index]()


class Race:
    """
    Base definition for the Race class
    *_rng parameters set the range for which the random stats are chosen from
    """

    def __init__(self, name, description, str_rng, int_rng, wis_rng, con_rng, cha_rng, dex_rng, cls_res, resistance):
        self.name = name
        self.description = description
        self.str_rng = str_rng
        self.int_rng = int_rng
        self.wis_rng = wis_rng
        self.con_rng = con_rng
        self.cha_rng = cha_rng
        self.dex_rng = dex_rng
        self.cls_res = cls_res
        self.resistance = resistance

    def __str__(self):
        return "Race: {}\n" \
               "Description: {}\n" \
               "Stats (min/max):\n" \
               "Strength: {}/{}\n" \
               "Intelligence: {}/{}\n" \
               "Wisdom: {}/{}\n" \
               "Constitution: {}/{}\n" \
               "Charisma: {}/{}\n" \
               "Dexterity: {}/{}\n" \
               "Resistances:\n" \
               "Fire: {}\n" \
               "Ice: {}\n" \
               "Electric: {}\n" \
               "Water: {}\n" \
               "Earth: {}\n" \
               "Wind: {}\n" \
               "Shadow: {}\n" \
               "Death: {}\n" \
               "Holy: {}\n" \
               "Poison: {}\n".format(self.name, self.description,
                                     self.str_rng[0], self.str_rng[1],
                                     self.int_rng[0], self.int_rng[1],
                                     self.wis_rng[0], self.wis_rng[1],
                                     self.con_rng[0], self.con_rng[1],
                                     self.cha_rng[0], self.cha_rng[1],
                                     self.dex_rng[0], self.dex_rng[1],
                                     self.resistance['Fire'],
                                     self.resistance['Ice'],
                                     self.resistance['Electric'],
                                     self.resistance['Water'],
                                     self.resistance['Earth'],
                                     self.resistance['Wind'],
                                     self.resistance['Shadow'],
                                     self.resistance['Death'],
                                     self.resistance['Holy'],
                                     self.resistance['Poison'])


class Human(Race):

    def __init__(self):
        super().__init__(name="Human", description="Humans are something you, as a player, can relate to. They are "
                                                   "the most versatile of all races, making a viable option for all "
                                                   "classes. While they have no magical resistances, they also have no"
                                                   " weaknesses.",
                         str_rng=(5, 14), int_rng=(5, 14), wis_rng=(5, 14),
                         con_rng=(5, 14), cha_rng=(5, 14), dex_rng=(5, 14),
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
                         resistance={'Fire': 0,
                                     'Ice': 0,
                                     'Electric': 0,
                                     'Water': 0,
                                     'Earth': 0,
                                     'Wind': 0,
                                     'Shadow': 0,
                                     'Death': 0,
                                     'Holy': 0,
                                     'Poison': 0}
                         )


class Elf(Race):

    def __init__(self):
        super().__init__(name="Elf", description="Elves are the magic users of the game. They are excellent spell "
                                                 "casters and have decent resistance to elemental magic. They are not,"
                                                 " however, very good at fighting with weapons and have a low "
                                                 "constitution, making them more susceptible to death magic.",
                         str_rng=(3, 11), int_rng=(7, 17), wis_rng=(7, 16),
                         con_rng=(3, 11), cha_rng=(5, 15), dex_rng=(6, 15),
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
                                     'Holy': 0,
                                     'Poison': 0}
                         )


class HalfElf(Race):

    def __init__(self):
        super().__init__(name="Half Elf", description="Half elves are the result of interbreeding between humans and "
                                                      "elves. They are just as versatile as humans and possess an "
                                                      "improved magical prowess, as well as mild elemental resistance. "
                                                      "Like their elf cousins, they do have a slight susceptibility to "
                                                      "death magic.",
                         str_rng=(5, 13), int_rng=(6, 16), wis_rng=(6, 15),
                         con_rng=(4, 12), cha_rng=(5, 15), dex_rng=(5, 15),
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
                                     'Holy': 0,
                                     'Poison': 0}
                         )


class Giant(Race):

    def __init__(self):
        super().__init__(name="Giant", description="Giants live for one thing - slicing a monster in two with one"
                                                   " blow. Known for their brutal ways and having the advantage of"
                                                   " being over eight feet tall, they make the best Warriors one can"
                                                   " find. Giants are a sturdy race and have great resistance against "
                                                   "death spells, as well as a mild resistance to poisons. However, "
                                                   "they are not the most pious beings and are weak against holy "
                                                   "spells.",
                         str_rng=(10, 18), int_rng=(3, 11), wis_rng=(5, 14),
                         con_rng=(6, 15), cha_rng=(3, 10), dex_rng=(3, 11),
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
                                     'Death': 0.75,
                                     'Holy': -0.3,
                                     'Poison': 0.33}
                         )


class Gnome(Race):

    def __init__(self):
        super().__init__(name="Gnome", description="Gnomes are very charismatic, giving them a distinct advantage in "
                                                   "money making and vendor relation. They are also above average "
                                                   "spell caster with a slight affinity toward the divine, giving them "
                                                   "a slight resistance against holy spells but are weak against "
                                                   "shadow. Gnomes prefer the civilized world and thus are not found "
                                                   "among the ranks of Pathfinders.",
                         str_rng=(4, 13), int_rng=(7, 15), wis_rng=(5, 15),
                         con_rng=(3, 13), cha_rng=(8, 18), dex_rng=(6, 15),
                         cls_res={'Base': ['Warrior', 'Mage', 'Footpad', 'Healer'],
                                  'First': ['Weapon Master', 'Paladin', 'Lancer',
                                            'Sorcerer', 'Spellblade',
                                            'Thief', 'Inquisitor', 'Assassin',
                                            'Cleric', 'Priest', 'Monk'],
                                  'Second': ['Berserker', 'Crusader', 'Dragoon',
                                             'Wizard', 'Knight Enchanter',
                                             'Rogue', 'Seeker', 'Ninja',
                                             'Templar', 'Archbishop', 'Master Monk']},
                         resistance={'Fire': 0,
                                     'Ice': 0,
                                     'Electric': 0,
                                     'Water': 0,
                                     'Earth': 0,
                                     'Wind': 0,
                                     'Shadow': -0.2,
                                     'Death': 0,
                                     'Holy': 0.2,
                                     'Poison': 0}
                         )


class Dwarf(Race):

    def __init__(self):
        super().__init__(name="Dwarf", description="Dwarves are very curious, always up for an adventure. They are "
                                                   "also fairly versatile, although not as much as humans. They are"
                                                   " more robust but lack the dexterity to be an elite Footpad and "
                                                   "also have a healthy mistrust of the arcane. As beings of the Earth,"
                                                   " dwarves have high resistance against earth and poison spells but"
                                                   " are weak against shadow magic.",
                         str_rng=(5, 14), int_rng=(5, 13), wis_rng=(5, 15),
                         con_rng=(6, 14), cha_rng=(6, 14), dex_rng=(4, 12),
                         cls_res={'Base': ['Warrior', 'Healer', 'Pathfinder'],
                                  'First': ['Weapon Master', 'Paladin', 'Lancer',
                                            'Cleric', 'Priest', 'Monk',
                                            'Diviner', 'Shaman'],
                                  'Second': ['Berserker', 'Crusader', 'Dragoon',
                                             'Templar', 'Archbishop', 'Master Monk',
                                             'Geomancer', 'Soulcatcher']},
                         resistance={'Fire': 0,
                                     'Ice': 0,
                                     'Electric': 0,
                                     'Water': 0,
                                     'Earth': 0.75,
                                     'Wind': 0,
                                     'Shadow': -0.3,
                                     'Death': 0,
                                     'Holy': 0,
                                     'Poison': 0.5}
                         )


class HalfOrc(Race):

    def __init__(self):
        super().__init__(name="Half Orc", description="Half orcs are the result of interbreeding between humans and "
                                                      "orcs, which while rare does occur. While not a strong as their "
                                                      "full-blood brethren, half orcs are much stronger on average "
                                                      "than humans. However the stigma related to half orcs makes "
                                                      "them far less charismatic. There inherit bloodlust makes the "
                                                      "pursuit of the divine unappealing. Because of this, half orcs "
                                                      "are weak against holy magic but have mild resistances against "
                                                      "shadow, death, and poison.",
                         str_rng=(6, 15), int_rng=(4, 13), wis_rng=(6, 15),
                         con_rng=(5, 14), cha_rng=(3, 11), dex_rng=(6, 14),
                         cls_res={'Base': ['Warrior', 'Mage', 'Footpad', 'Pathfinder'],
                                  'First': ['Weapon Master', 'Lancer',
                                            'Sorcerer', 'Warlock', 'Spellblade',
                                            'Thief', 'Inquisitor', 'Assassin',
                                            'Druid', 'Diviner', 'Shaman'],
                                  'Second': ['Berserker', 'Dragoon',
                                             'Wizard', 'Necromancer', 'Knight Enchanter',
                                             'Rogue', 'Seeker', 'Ninja',
                                             'Lycan', 'Geomancer', 'Soulcatcher']},
                         resistance={'Fire': 0,
                                     'Ice': 0,
                                     'Electric': 0,
                                     'Water': 0,
                                     'Earth': 0,
                                     'Wind': 0,
                                     'Shadow': 0.2,
                                     'Death': 0.1,
                                     'Holy': -0.2,
                                     'Poison': 0.1}
                         )


races_dict = {'Human': Human,
              'Elf': Elf,
              'Half Elf': HalfElf,
              "Giant": Giant,
              'Gnome': Gnome,
              'Dwarf': Dwarf,
              'Half Orc': HalfOrc}
