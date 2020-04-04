###########################################
""" race manager """

# Imports
import storyline


# Functions
def define_race():
    """
    Allows the player to choose which race they wish to play
    """
    print("Choose a race for your character.")
    race_list = [Human, Elf, Giant, Gnome, Dwarf]
    option_list = [('Human', 0), ('Elf', 1), ('Giant', 2), ('Gnome', 3), ('Dwarf', 4)]
    race_index = storyline.get_response(option_list)
    print(race_list[race_index]())
    return race_list[race_index]()


class Race:
    """
    Base definition for the Race class
    *_rng parameters set the range for which the random stats are chosen from
    """
    def __init__(self, name, description, str_rng, int_rng, wis_rng, con_rng, cha_rng, dex_rng):
        self.name = name
        self.description = description
        self.str_rng = str_rng
        self.int_rng = int_rng
        self.wis_rng = wis_rng
        self.con_rng = con_rng
        self.cha_rng = cha_rng
        self.dex_rng = dex_rng

    def __str__(self):
        return "Race: {}\n" \
               "Description: {}\n".format(self.name, self.description)


class Human(Race):

    def __init__(self):
        super().__init__(name="HUMAN", description="Humans are something you, as a player, can relate to. They are \n"
                                                   "the most versatile of all races, making a viable option for all \n"
                                                   "classes.",
                         str_rng=(5, 18), int_rng=(5, 18), wis_rng=(5, 18), con_rng=(5, 18), cha_rng=(5, 18),
                         dex_rng=(5, 18))


class Elf(Race):

    def __init__(self):
        super().__init__(name="ELF", description="Elves are the magic users of the game. They are excellent spell \n"
                                                 "casters. They are not, however, very good at fighting with weapons\n"
                                                 " and have a low constitution, although their respectable dexterity\n"
                                                 "make them decent Footpads.",
                         str_rng=(3, 14), int_rng=(7, 20), wis_rng=(7, 20), con_rng=(3, 14), cha_rng=(5, 18),
                         dex_rng=(6, 18))


class Giant(Race):

    def __init__(self):
        super().__init__(name="GIANT", description="Giants live for one thing - slicing a monster in two with one\n"
                                                   " blow. Known for their brutal ways and having the advantage of\n"
                                                   " being over eight feet tall, they make the best Warriors one can\n"
                                                   " find. While they are not restricted from spell casting, their\n"
                                                   " low intelligence limit their effectiveness.",
                         str_rng=(12, 25), int_rng=(3, 14), wis_rng=(5, 18), con_rng=(9, 19), cha_rng=(3, 14),
                         dex_rng=(3, 14))


class Gnome(Race):

    def __init__(self):
        super().__init__(name="GNOME", description="Gnomes are very charismatic, giving them a distinct advantage in \n"
                                                   "money making and vendor relation. They are also above average \n"
                                                   "spell caster.",
                         str_rng=(4, 17), int_rng=(7, 19), wis_rng=(5, 19), con_rng=(3, 17), cha_rng=(9, 22),
                         dex_rng=(6, 18))


class Dwarf(Race):

    def __init__(self):
        super().__init__(name="DWARF", description="Dwarves are very curious, always up for an adventure. They are \n"
                                                   "also fairly versatile, although not as much as humans. They are\n"
                                                   " more robust but lack the dexterity to be an elite Footpad.",
                         str_rng=(5, 18), int_rng=(5, 17), wis_rng=(5, 19), con_rng=(6, 19), cha_rng=(6, 18),
                         dex_rng=(4, 16))
