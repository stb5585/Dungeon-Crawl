###########################################
""" action manager """

# Imports
import player


class Action:
    def __init__(self, method, name, hotkey, **kwargs):
        self.method = method
        self.name = name
        self.hotkey = hotkey
        self.kwargs = kwargs

    def __str__(self):
        return "{}".format(self.name)


class MoveNorth(Action):
    def __init__(self):
        super().__init__(method=player.Player.move_north, name='Move north (w)', hotkey='w')


class MoveSouth(Action):
    def __init__(self):
        super().__init__(method=player.Player.move_south, name='Move south (s)', hotkey='s')


class MoveEast(Action):
    def __init__(self):
        super().__init__(method=player.Player.move_east, name='Move east (d)', hotkey='d')


class MoveWest(Action):
    def __init__(self):
        super().__init__(method=player.Player.move_west, name='Move west (a)', hotkey='a')


class StairsUp(Action):
    def __init__(self):
        super().__init__(method=player.Player.stairs_up, name='Take stairs up', hotkey="u")


class StairsDown(Action):
    def __init__(self):
        super().__init__(method=player.Player.stairs_down, name='Take stairs down', hotkey="j")


class ViewInventory(Action):
    """
    Prints the player's inventory
    """
    def __init__(self):
        super().__init__(method=player.Player.print_inventory, name='Inventory', hotkey=None)


class ViewQuests(Action):
    """

    """
    def __init__(self):
        super().__init__(method=player.Player.view_quests, name="Quests", hotkey=None)


class Flee(Action):
    def __init__(self):
        super().__init__(method=player.Player.flee, name="Flee", hotkey=None)


class Status(Action):
    def __init__(self):
        super().__init__(method=player.Player.status, name="Status", hotkey=None)


class Equip(Action):
    def __init__(self):
        super().__init__(method=player.Player.equip, name="Equip", hotkey=None)


class UseItem(Action):
    def __init__(self, tile=None):
        super().__init__(method=player.Player.use_item, name="Item", hotkey=None, tile=tile)


class Open(Action):
    def __init__(self, tile=None):
        super().__init__(method=player.Player.open_up, name="Open", hotkey="o", tile=tile)


class ListSpecials(Action):
    def __init__(self):
        super().__init__(method=player.Player.specials, name="Specials", hotkey=None)


class Save(Action):
    def __init__(self, wmap):
        super().__init__(method=player.Player.save, name="Save", hotkey=None, wmap=wmap)


class Quit(Action):
    def __init__(self):
        super().__init__(method=player.Player.game_quit, name="Quit", hotkey=None)


class CharacterMenu(Action):
    def __init__(self, tile=None):
        super().__init__(method=player.Player.character_menu, name="Character Menu", hotkey="c", tile=tile)


class Attack(Action):
    def __init__(self):
        super().__init__(method=None, name="Attack", hotkey=None)


class CastSpell(Action):
    def __init__(self):
        super().__init__(method=None, name="Cast Spell", hotkey=None)


class UseSkill(Action):
    def __init__(self):
        super().__init__(method=None, name="Use Skill", hotkey=None)
