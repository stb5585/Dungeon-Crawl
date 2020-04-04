###########################################
""" class manager """

# Imports
import storyline
import items


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
    Promotion: Warrior -> Knight  -> Lord
                       |
                       -> Paladin -> Crusader
                       |
                       -> Lancer  -> Dragoon
    """

    def __init__(self):
        super().__init__(name="WARRIOR", description="A warrior is a weapon specialist that relies on strength and \n"
                                                     "defense.",
                         min_str=12, min_int=7, min_wis=5, min_con=10, min_cha=6, min_dex=8,
                         equipment=dict(Weapon=items.BronzeSword, OffHand=items.WoodShield, Armor=items.HideArmor),
                         restrictions={'Weapon': ['Sword', 'Axe', 'Polearm'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Medium', 'Heavy']})


class Mage(Job):
    """
    Promotion: Mage -> Sorcerer -> Wizard
                    |
                    -> Warlock  -> Necromancer
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


class Footpad(Job):
    """
    Promotion: Footpad -> Thief    -> Rogue
                       |
                       -> Ranger   -> Seeker
                       |
                       -> Assassin -> Ninja
    """

    def __init__(self):
        super().__init__(name="FOOTPAD", description="Footpads are agile and perceptive, with an natural ability of \n"
                                                     "deftness. While more than capable of holding their own in hand-\n"
                                                     "to-hand combat, they truly excel at subterfuge.",
                         min_str=8, min_int=10, min_wis=8, min_con=7, min_cha=5, min_dex=12,
                         equipment=dict(Weapon=items.BronzeDagger, OffHand=items.Buckler, Armor=items.PaddedArmor),
                         restrictions={'Weapon': ['Dagger', 'Sword'],
                                       'OffHand': ['Shield'],
                                       'Armor': ['Light', 'Medium']})
