###########################################
""" map manager """

# Imports
import numpy

import enemies
import actions
import game
import items
import world
import combat
import town


class MapTile:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.visited = False  # tells whether the tile has been visited by player
        self.enter = True  # keeps player from entering walls
        self.special = False

    def intro_text(self, player):
        raise NotImplementedError()

    def modify_player(self, player):
        raise NotImplementedError()

    def adjacent_moves(self, append_list: list = None, blocked=None):
        """Returns all move actions for adjacent tiles."""
        if append_list is None:
            append_list = []
        moves = []
        try:
            if world.tile_exists(self.x + 1, self.y, self.z).enter and blocked != "East":
                moves.append(actions.MoveEast())
        except AttributeError:
            pass
        try:
            if world.tile_exists(self.x - 1, self.y, self.z).enter and blocked != "West":
                moves.append(actions.MoveWest())
        except AttributeError:
            pass
        try:
            if world.tile_exists(self.x, self.y - 1, self.z).enter and blocked != "North":
                moves.append(actions.MoveNorth())
        except AttributeError:
            pass
        try:
            if world.tile_exists(self.x, self.y + 1, self.z).enter and blocked != "South":
                moves.append(actions.MoveSouth())
        except AttributeError:
            pass
        for item in append_list:
            moves.append(item)
        return moves

    def available_actions(self, player):
        """Returns all the available actions in this room."""
        pass

    def adjacent_visited(self, wmap):
        """Changes visited parameter for 8 adjacent tiles"""
        # reveals 4 spaces in cardinal directions
        if world.tile_exists(self.x + 1, self.y, self.z):
            wmap[(self.x + 1, self.y, self.z)].visited = True
        if world.tile_exists(self.x - 1, self.y, self.z):
            wmap[(self.x - 1, self.y, self.z)].visited = True
        if world.tile_exists(self.x, self.y - 1, self.z):
            wmap[(self.x, self.y - 1, self.z)].visited = True
        if world.tile_exists(self.x, self.y + 1, self.z):
            wmap[(self.x, self.y + 1, self.z)].visited = True

    def minimap(self, player):
        """
        Function that allows the player to view the current dungeon level in terminal
        20 x 20 grid
        """
        world_dict = player.world_dict['World']
        level = player.location_z
        map_size = (20, 20)
        map_array = numpy.zeros(map_size).astype(str)
        for tile in world_dict:
            if level == tile[2]:
                tile_x, tile_y = tile[1], tile[0]
                if world_dict[tile].visited:
                    if world_dict[tile] is None:
                        continue
                    elif 'Stairs' in world_dict[tile].__str__():
                        map_array[tile_x][tile_y] = "x"
                    elif 'DoorEast' in world_dict[tile].__str__() or \
                            'DoorWest' in world_dict[tile].__str__():
                        if not world_dict[tile].open:
                            map_array[tile_x][tile_y] = "|"
                        else:
                            map_array[tile_x][tile_y] = "."
                    elif 'DoorNorth' in world_dict[tile].__str__() or \
                            'DoorSouth' in world_dict[tile].__str__():
                        if not world_dict[tile].open:
                            map_array[tile_x][tile_y] = "_"
                        else:
                            map_array[tile_x][tile_y] = "."
                    elif 'Wall' in world_dict[tile].__str__():
                        map_array[tile_x][tile_y] = "#"
                    else:
                        map_array[tile_x][tile_y] = "."
        map_array[player.location_y][player.location_x] = "+"
        map_array[map_array == "0.0"] = " "
        map_array = numpy.insert(map_array, 0, numpy.zeros(map_array.shape[1]), 0)
        map_array[map_array == "0.0"] = "\u203E"  # overline character
        map_array = numpy.vstack([map_array, numpy.zeros(map_array.shape[1])])
        map_array[map_array == "0.0"] = "_"
        map_array = numpy.insert(map_array, 0, numpy.zeros(map_array.shape[0]), 1)
        map_array[map_array == "0.0"] = "|"
        map_array = numpy.append(map_array, numpy.zeros(map_array.shape[0]).reshape(-1, 1), 1)
        map_array[map_array == "0.0"] = "|"
        for i, l in enumerate(map_array):
            print(" ".join(l))


class Town(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        return ""

    def modify_player(self, player):
        player.state = 'normal'
        player.health = player.health_max
        player.mana = player.mana_max
        town.town(player)


class EnemyRoom(MapTile):
    def __init__(self, x, y, z, enemy):
        super().__init__(x, y, z)
        self.enemy = enemy

    def intro_text(self, player):
        if self.enemy.is_alive():
            return """
            An enemy {} attacks {}!
            """.format(self.enemy.name, player.name)
        else:
            return """
            A dead {} lies on the ground.
            """.format(self.enemy.name)

    def modify_player(self, player):
        self.visited = True
        self.adjacent_visited(player.world_dict['World'])
        if self.enemy.is_alive():
            player.state = 'fight'
            combat.battle(player, self.enemy)

    def available_actions(self, player):
        if self.enemy.is_alive():
            action_list = [actions.Attack(), actions.UseItem(), actions.Flee()]
            if len(player.spellbook['Spells']) > 0:
                action_list.insert(1, actions.CastSpell())
            if len(player.spellbook['Skills']) > 0:
                action_list.insert(1, actions.UseSkill())
            return action_list
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class StairsUp(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        return """
        {} sees a flight of stairs going up. (Enter 'u' to use)
        """.format(player.name.capitalize())

    def modify_player(self, player):
        self.visited = True
        self.adjacent_visited(player.world_dict['World'])

    def available_actions(self, player):
        return self.adjacent_moves([actions.StairsUp(), actions.CharacterMenu()])


class StairsDown(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        return """
        {} sees a flight of stairs going down. (Enter 'j' to use)
        """.format(player.name.capitalize())

    def modify_player(self, player):
        self.visited = True
        self.adjacent_visited(player.world_dict['World'])

    def available_actions(self, player):
        return self.adjacent_moves([actions.StairsDown(), actions.CharacterMenu()])


class SpecialTile(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.special = True

    def intro_text(self, player):
        raise NotImplementedError

    def modify_player(self, player):
        self.adjacent_visited(player.world_dict['World'])

    def special_text(self, player):
        raise NotImplementedError


class Wall(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enter = False

    def intro_text(self, player):
        return ""

    def modify_player(self, player):
        self.visited = True
        self.adjacent_visited(player.world_dict['World'])


class FakeWall(Wall):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enter = True

    def available_actions(self, player):
        return self.adjacent_moves([actions.CharacterMenu()])


class RandomTile(MapTile):
    """
    Dummy tile; world.py will see this and randomly pick between empty or random enemy
    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        raise NotImplementedError()

    def modify_player(self, player):
        raise NotImplementedError()


class RandomTile2(MapTile):
    """
    Dummy tile; world.py will see this and randomly pick between empty or random enemy from 1 level lower
    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        raise NotImplementedError()

    def modify_player(self, player):
        raise NotImplementedError()


class EmptyCavePath(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        return """
        
        """

    def modify_player(self, player):
        self.visited = True
        self.adjacent_visited(player.world_dict['World'])

    def available_actions(self, player):
        return self.adjacent_moves([actions.CharacterMenu()])


class WarningTile(EmptyCavePath):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        return """
        Enemies beyond this point increase in difficulty. Plan accordingly.
        """


class RandomEnemyRoom0(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.random_enemy('0'))


class RandomEnemyRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.random_enemy(str(z)))


class RandomEnemyRoom2(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.random_enemy(str(z + 1)))


class BossRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, None)

    def intro_text(self, player):
        if self.enemy.is_alive():
            return """
            Boss fight!
            An enemy {} attacks {}!
            """.format(self.enemy.name, player.name.capitalize())
        else:
            return """
            A dead {} lies on the ground.
            """.format(self.enemy.name)

    def available_actions(self, player):
        if self.enemy.is_alive():
            action_list = [actions.Attack(), actions.UseItem()]
            if len(player.spellbook['Spells']) > 0:
                action_list.insert(1, actions.CastSpell())
            if len(player.spellbook['Skills']) > 0:
                action_list.insert(1, actions.UseSkill())
            return action_list
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class MinotaurBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Minotaur()


class BarghestBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Barghest()


class PseudodragonBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Pseudodragon()


class NightmareBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Nightmare()


class CockatriceBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Cockatrice()


class WendigoBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Wendigo()


class GolemBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Golem()


class JesterBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Jester()


class DomingoBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Domingo()


class RedDragonBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.RedDragon()


class FinalBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Cthulhu()


class ChestRoom(MapTile):
    def __init__(self, x, y, z, loot):
        super().__init__(x, y, z)
        self.loot = loot

    def intro_text(self, player):
        raise NotImplementedError

    def available_actions(self, player):
        raise NotImplementedError

    def modify_player(self, player):
        self.visited = True
        self.adjacent_visited(player.world_dict['World'])


class UnlockedChestRoom(ChestRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, items.random_item(z))
        self.open = False
        self.locked = False

    def intro_text(self, player):
        if not self.open:
            return """
            {} finds a chest. (Enter 'o' to open)
            """.format(player.name.capitalize())
        else:
            return """
            This room has an open chest.
            """

    def available_actions(self, player):
        if not self.open:
            return self.adjacent_moves([actions.Open(self), actions.CharacterMenu()])
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class UnlockedChestRoom2(ChestRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, items.random_item(z + 1))
        self.open = False
        self.locked = False

    def intro_text(self, player):
        if not self.open:
            return """
            {} finds a chest. (Enter 'o' to open)
            """.format(player.name.capitalize())
        else:
            return """
            This room has an open chest.
            """

    def available_actions(self, player):
        if not self.open:
            return self.adjacent_moves([actions.Open(self), actions.CharacterMenu()])
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class LockedChestRoom(ChestRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, items.random_item(z + 1))
        self.open = False
        self.locked = True

    def intro_text(self, player):
        if not self.open:
            if self.locked:
                return """
                {} finds a chest!!... but it is locked.
                """.format(player.name.capitalize())
            else:
                return """
                {} finds a chest. (Enter 'o' to open)
                """.format(player.name.capitalize())
        else:
            return """
            This room has an open chest.
            """

    def available_actions(self, player):
        if not self.open:
            if self.locked:
                return self.adjacent_moves([actions.UseSkill(), actions.UseItem(), actions.CharacterMenu(tile=self)])
            else:
                return self.adjacent_moves([actions.Open(self), actions.CharacterMenu()])
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class LockedChestRoom2(ChestRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, items.random_item(z + 2))
        self.open = False
        self.locked = True

    def intro_text(self, player):
        if not self.open:
            if self.locked:
                return """
                {} finds a chest!!... but it is locked.
                """.format(player.name.capitalize())
            else:
                return """
                {} finds a chest. (Enter 'o' to open)
                """.format(player.name.capitalize())
        else:
            return """
            This room has an open chest.
            """

    def available_actions(self, player):
        if not self.open:
            if self.locked:
                return self.adjacent_moves([actions.UseSkill(), actions.UseItem(), actions.CharacterMenu(tile=self)])
            else:
                return self.adjacent_moves([actions.Open(self), actions.CharacterMenu()])
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class LockedDoor(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.open = False
        self.locked = True

    def intro_text(self, player):
        if not self.open:
            if self.locked:
                return """
                {} finds a locked door. If only you could find the key...
                """.format(player.name.capitalize())
            else:
                return """
                There is an unlocked door. (Enter 'o' to open)
                """
        else:
            return """
            There is an open door.
            """

    def modify_player(self, player):
        self.visited = True
        self.adjacent_visited(player.world_dict['World'])


class LockedDoorEast(LockedDoor):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.blocked = "East"

    def available_actions(self, player):
        if not self.open:
            if self.locked:
                return self.adjacent_moves([actions.UseItem(tile=self), actions.CharacterMenu(tile=self)],
                                           blocked=self.blocked)
            else:
                return self.adjacent_moves([actions.Open(self), actions.CharacterMenu()], blocked=self.blocked)
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class LockedDoorWest(LockedDoor):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.blocked = "West"

    def available_actions(self, player):
        if self.open:
            if self.locked:
                return self.adjacent_moves([actions.UseItem(tile=self), actions.CharacterMenu(tile=self)],
                                           blocked=self.blocked)
            else:
                return self.adjacent_moves([actions.Open(self), actions.CharacterMenu()], blocked=self.blocked)
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class LockedDoorNorth(LockedDoor):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.blocked = "North"

    def available_actions(self, player):
        if self.open:
            if self.locked:
                return self.adjacent_moves([actions.UseItem(tile=self), actions.CharacterMenu(tile=self)],
                                           blocked=self.blocked)
            else:
                return self.adjacent_moves([actions.Open(self), actions.CharacterMenu()], blocked=self.blocked)
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class LockedDoorSouth(LockedDoor):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.blocked = "South"

    def available_actions(self, player):
        if self.open:
            if self.locked:
                return self.adjacent_moves([actions.UseItem(tile=self), actions.CharacterMenu(tile=self)],
                                           blocked=self.blocked)
            else:
                return self.adjacent_moves([actions.Open(self), actions.CharacterMenu()], blocked=self.blocked)
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class UnobtainiumRoom(SpecialTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        return """
        An empty pedestal stands in the center of the room.
        """

    def modify_player(self, player):
        self.adjacent_visited(player.world_dict['World'])
        if not self.visited:
            player.modify_inventory(items.Unobtainium, rare=True)
            self.visited = True

    def available_actions(self, player):
        return self.adjacent_moves([actions.CharacterMenu()])

    def special_text(self, player):
        game.unobtainium_room()


class RelicRoom(SpecialTile):
    """

    """
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        return """
        An empty pedestal stands in the center of the room.
        """

    def modify_player(self, player):
        self.adjacent_visited(player.world_dict['World'])
        if not self.visited:
            player.health = player.health_max
            player.mana = player.mana_max
            relics = [items.Relic1, items.Relic2, items.Relic3, items.Relic4, items.Relic5, items.Relic6]
            player.modify_inventory(relics[player.location_z - 1], rare=True)
            self.visited = True

    def available_actions(self, player):
        return self.adjacent_moves([actions.CharacterMenu()])

    def special_text(self, player):
        game.relic_room(player.location_z)


class FinalBlocker(MapTile):
    """
    TODO tile will block player from reaching final boss without all 6 relics
    """
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        pass

    def modify_player(self, player):
        pass


class SecretShop(MapTile):
    """

    """
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        return """
        {} finds a secret shop in the depths of the dungeon.
        """.format(player.name.capitalize())

    def modify_player(self, player):
        self.visited = True
        self.adjacent_visited(player.world_dict['World'])
        player.state = 'normal'
        town.secret_shop(player)

    def available_actions(self, player):
        pass


class UltimateArmorShop(MapTile):
    """

    """
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.looted = False

    def intro_text(self, player):
        if not self.looted:
            return """
            {} finds a forge in the depths of the dungeon. A large man stands in front of you.
            """.format(player.name.capitalize())
        else:
            return """
            A large empty room.
            """

    def modify_player(self, player):
        self.visited = True
        self.adjacent_visited(player.world_dict['World'])
        player.state = 'normal'
        if not self.looted:
            self.looted = town.ultimate_armor_repo(player)

    def available_actions(self, player):
        pass
