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

    def __init__(self, name, description, str_rng, int_rng, wis_rng, con_rng, cha_rng, dex_rng, cls_res):
        self.name = name
        self.description = description
        self.str_rng = str_rng
        self.int_rng = int_rng
        self.wis_rng = wis_rng
        self.con_rng = con_rng
        self.cha_rng = cha_rng
        self.dex_rng = dex_rng
        self.cls_res = cls_res

    def __str__(self):
        return "Race: {}\n" \
               "Description: {}\n" \
               "Stats (min/max):\n" \
               "Strength: {}/{}\n" \
               "Intelligence: {}/{}\n" \
               "Wisdom: {}/{}\n" \
               "Constitution: {}/{}\n" \
               "Charisma: {}/{}\n" \
               "Dexterity: {}/{}\n".format(self.name, self.description,
                                           self.str_rng[0], self.str_rng[1],
                                           self.int_rng[0], self.int_rng[1],
                                           self.wis_rng[0], self.wis_rng[1],
                                           self.con_rng[0], self.con_rng[1],
                                           self.cha_rng[0], self.cha_rng[1],
                                           self.dex_rng[0], self.dex_rng[1])


class Human(Race):

    def __init__(self):
        super().__init__(name="HUMAN", description="Humans are something you, as a player, can relate to. They are "
                                                   "the most versatile of all races, making a viable option for all "
                                                   "classes.",
                         str_rng=(5, 14), int_rng=(5, 14), wis_rng=(5, 14), con_rng=(5, 14), cha_rng=(5, 14),
                         dex_rng=(5, 14),
                         cls_res=['Warrior', 'Mage', 'Footpad', 'Healer', 'Naturalist'])


class Elf(Race):

    def __init__(self):
        super().__init__(name="ELF", description="Elves are the magic users of the game. They are excellent spell "
                                                 "casters. They are not, however, very good at fighting with weapons"
                                                 " and have a low constitution, although their respectable dexterity "
                                                 "make them decent Footpads.",
                         str_rng=(3, 11), int_rng=(7, 17), wis_rng=(7, 16), con_rng=(3, 11), cha_rng=(5, 15),
                         dex_rng=(6, 15),
                         cls_res=['Mage', 'Footpad', 'Healer', 'Naturalist'])


class HalfElf(Race):

    def __init__(self):
        super().__init__(name="HALFELF", description="Half elves are the result of interbreeding between humans and "
                                                     "elves. They are just as versatile as humans and possess an "
                                                     "improved magical prowess.",
                         str_rng=(5, 13), int_rng=(6, 16), wis_rng=(6, 15), con_rng=(4, 12), cha_rng=(5, 15),
                         dex_rng=(5, 15),
                         cls_res=['Warrior', 'Mage', 'Footpad', 'Healer', 'Naturalist'])


class Giant(Race):

    def __init__(self):
        super().__init__(name="GIANT", description="Giants live for one thing - slicing a monster in two with one"
                                                   " blow. Known for their brutal ways and having the advantage of"
                                                   " being over eight feet tall, they make the best Warriors one can"
                                                   " find.",
                         str_rng=(10, 18), int_rng=(3, 11), wis_rng=(5, 14), con_rng=(6, 15), cha_rng=(3, 10),
                         dex_rng=(3, 11),
                         cls_res=['Warrior'])


class Gnome(Race):

    def __init__(self):
        super().__init__(name="GNOME", description="Gnomes are very charismatic, giving them a distinct advantage in "
                                                   "money making and vendor relation. They are also above average "
                                                   "spell caster. Gnomes prefer the civilized world and thus are not "
                                                   "found among the ranks of Naturalists.",
                         str_rng=(4, 13), int_rng=(7, 15), wis_rng=(5, 15), con_rng=(3, 13), cha_rng=(8, 18),
                         dex_rng=(6, 15),
                         cls_res=['Warrior', 'Mage', 'Footpad', 'Healer'])


class Dwarf(Race):

    def __init__(self):
        super().__init__(name="DWARF", description="Dwarves are very curious, always up for an adventure. They are "
                                                   "also fairly versatile, although not as much as humans. They are"
                                                   " more robust but lack the dexterity to be an elite Footpad and "
                                                   "also have a healthy mistrust of the arcane.",
                         str_rng=(5, 14), int_rng=(5, 13), wis_rng=(5, 15), con_rng=(6, 14), cha_rng=(6, 14),
                         dex_rng=(4, 12),
                         cls_res=['Warrior', 'Healer', 'Naturalist'])


class HalfOrc(Race):

    def __init__(self):
        super().__init__(name="HALFORC", description="Half orcs are the result of interbreeding between humans and orcs"
                                                     ", which while rare does occur. While not a strong as their full-"
                                                     "blood brethren, half orcs are much stronger on average than "
                                                     "humans. However the stigma related to half orcs makes them far"
                                                     " less charismatic. There inherit bloodlust makes the pursuit of "
                                                     "the divine unappealing.",
                         str_rng=(6, 15), int_rng=(4, 13), wis_rng=(6, 15), con_rng=(5, 14), cha_rng=(3, 11),
                         dex_rng=(6, 14),
                         cls_res=['Warrior', 'Mage', 'Footpad', 'Naturalist'])
