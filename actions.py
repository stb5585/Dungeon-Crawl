###########################################
""" action manager """

# Imports
import character


class Action:
    def __init__(self, method, name, **kwargs):
        self.method = method
        self.name = name
        self.kwargs = kwargs

    def __str__(self):
        return "{}".format(self.name)


class MoveNorth(Action):
    def __init__(self):
        super().__init__(method=character.Player.move_north, name='Move north')


class MoveSouth(Action):
    def __init__(self):
        super().__init__(method=character.Player.move_south, name='Move south')


class MoveEast(Action):
    def __init__(self):
        super().__init__(method=character.Player.move_east, name='Move east')


class MoveWest(Action):
    def __init__(self):
        super().__init__(method=character.Player.move_west, name='Move west')


class StairsUp(Action):
    def __init__(self):
        super().__init__(method=character.Player.stairs_up, name='Take stairs up')


class StairsDown(Action):
    def __init__(self):
        super().__init__(method=character.Player.stairs_down, name='Take stairs down')


class ViewInventory(Action):
    """
    Prints the player's inventory
    """
    def __init__(self):
        super().__init__(method=character.Player.print_inventory, name='Inventory')


class Attack(Action):
    def __init__(self):
        super().__init__(method=None, name="Attack")


class CastSpell(Action):
    def __init__(self):
        super().__init__(method=None, name="Cast Spell")


class UseSkill(Action):
    def __init__(self):
        super().__init__(method=None, name="Use Skill")


class Flee(Action):
    def __init__(self):
        super().__init__(method=character.Player.flee, name="Flee")


class Status(Action):
    def __init__(self):
        super().__init__(method=character.Player.status, name="Status")


class Minimap(Action):
    def __init__(self, world_dict):
        super().__init__(method=character.Player.minimap, name="Minimap", world_dict=world_dict)


class Equip(Action):
    def __init__(self):
        super().__init__(method=character.Player.equip, name="Equip")


class UseItem(Action):
    def __init__(self):
        super().__init__(method=character.Player.use_item, name="Item", enemy=None)


class Open(Action):
    def __init__(self, enemy):
        super().__init__(method=character.Player.open_up, name="Open", enemy=enemy)


class ListSpecials(Action):
    def __init__(self):
        super().__init__(method=character.Player.specials, name="Specials")


class Save(Action):
    def __init__(self, wmap):
        super().__init__(method=character.Player.save, name="Save", wmap=wmap)


class Quit(Action):
    def __init__(self):
        super().__init__(method=character.Player.game_quit, name="Quit")


class CharacterMenu(Action):
    def __init__(self):
        super().__init__(method=character.Player.character_menu, name="Character Menu")
