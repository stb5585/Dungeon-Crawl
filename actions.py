###########################################
""" action manager """

# Imports
import character


class Action:
    def __init__(self, method, name, hotkey, **kwargs):
        self.method = method
        self.hotkey = hotkey
        self.name = name
        self.kwargs = kwargs

    def __str__(self):
        return "{}: {}".format(self.hotkey, self.name)


class MoveNorth(Action):
    def __init__(self):
        super().__init__(method=character.Player.move_north, name='Move north', hotkey='3')


class MoveSouth(Action):
    def __init__(self):
        super().__init__(method=character.Player.move_south, name='Move south', hotkey='4')


class MoveEast(Action):
    def __init__(self):
        super().__init__(method=character.Player.move_east, name='Move east', hotkey='1')


class MoveWest(Action):
    def __init__(self):
        super().__init__(method=character.Player.move_west, name='Move west', hotkey='2')


class StairsUp(Action):
    def __init__(self):
        super().__init__(method=character.Player.stairs_up, name='Take stairs up', hotkey='u')


class StairsDown(Action):
    def __init__(self):
        super().__init__(method=character.Player.stairs_down, name='Take stairs down', hotkey='d')


class ViewInventory(Action):
    """Prints the player's inventory"""

    def __init__(self):
        super().__init__(method=character.Player.print_inventory, name='Inventory', hotkey='i')


class Attack(Action):
    def __init__(self, enemy):
        super().__init__(method=character.Player.do_damage, name="Attack", hotkey='a', enemy=enemy)


class Flee(Action):
    def __init__(self):
        super().__init__(method=character.Player.flee, name="Flee", hotkey='f')


class Status(Action):
    def __init__(self):
        super().__init__(method=character.Player.status, name="Status", hotkey='c')


class Minimap(Action):
    def __init__(self, world_dict):
        super().__init__(method=character.Player.minimap, name="Minimap", hotkey='m', world_dict=world_dict)


class Equip(Action):
    def __init__(self):
        super().__init__(method=character.Player.equip, name="Equip", hotkey='e')


class Potion(Action):
    def __init__(self):
        super().__init__(method=character.Player.use_potion, name="Potion", hotkey='p')


class OpenChest(Action):
    def __init__(self, enemy):
        super().__init__(method=character.Player.chest, name="Open", hotkey='o', enemy=enemy)


class Spellbook(Action):
    def __init__(self):
        super().__init__(method=character.Player.spellbook, name="Spellbook", hotkey='b')


class Save(Action):
    def __init__(self):
        super().__init__(method=character.Player.save, name="Save", hotkey='s')


class Quit(Action):
    def __init__(self):
        super().__init__(method=character.Player.game_quit, name="Quit", hotkey='q')
