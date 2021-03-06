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
    while True:
        race_index = storyline.get_response(option_list)
        race = race_list[race_index]()
        print(race)
        print("Stats (min/max):\n"
              "Strength: %d/%d\n"
              "Intelligence: %d/%d\n"
              "Wisdom: %d/%d\n"
              "Constitution: %d/%d\n"
              "Charisma: %d/%d\n"
              "Dexterity: %d/%d" % (race.str_rng[0], race.str_rng[1],
                                    race.int_rng[0], race.int_rng[1],
                                    race.wis_rng[0], race.wis_rng[1],
                                    race.con_rng[0], race.con_rng[1],
                                    race.cha_rng[0], race.cha_rng[1],
                                    race.dex_rng[0], race.dex_rng[1]))
        choose = input("Are you sure you want to play as a %s? " % race_list[race_index]().name).lower()
        if choose == 'y':
            break
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
                         str_rng=(5, 14), int_rng=(5, 14), wis_rng=(5, 14), con_rng=(5, 14), cha_rng=(5, 14),
                         dex_rng=(5, 14))


class Elf(Race):

    def __init__(self):
        super().__init__(name="ELF", description="Elves are the magic users of the game. They are excellent spell \n"
                                                 "casters. They are not, however, very good at fighting with weapons\n"
                                                 " and have a low constitution, although their respectable dexterity\n"
                                                 "make them decent Footpads.",
                         str_rng=(3, 11), int_rng=(7, 17), wis_rng=(7, 16), con_rng=(3, 11), cha_rng=(5, 15),
                         dex_rng=(6, 15))


class Giant(Race):

    def __init__(self):
        super().__init__(name="GIANT", description="Giants live for one thing - slicing a monster in two with one\n"
                                                   " blow. Known for their brutal ways and having the advantage of\n"
                                                   " being over eight feet tall, they make the best Warriors one can\n"
                                                   " find. While they are not restricted from spell casting, their\n"
                                                   " low intelligence limit their effectiveness.",
                         str_rng=(10, 18), int_rng=(3, 11), wis_rng=(5, 14), con_rng=(6, 15), cha_rng=(3, 10),
                         dex_rng=(3, 11))


class Gnome(Race):

    def __init__(self):
        super().__init__(name="GNOME", description="Gnomes are very charismatic, giving them a distinct advantage in \n"
                                                   "money making and vendor relation. They are also above average \n"
                                                   "spell caster.",
                         str_rng=(4, 13), int_rng=(7, 15), wis_rng=(5, 15), con_rng=(3, 13), cha_rng=(8, 18),
                         dex_rng=(6, 15))


class Dwarf(Race):

    def __init__(self):
        super().__init__(name="DWARF", description="Dwarves are very curious, always up for an adventure. They are \n"
                                                   "also fairly versatile, although not as much as humans. They are\n"
                                                   " more robust but lack the dexterity to be an elite Footpad.",
                         str_rng=(5, 14), int_rng=(5, 13), wis_rng=(5, 15), con_rng=(6, 14), cha_rng=(6, 14),
                         dex_rng=(4, 12))
