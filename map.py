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

    def modify_player(self, player, wmap):
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
            wmap['World'][(self.x + 1, self.y, self.z)].visited = True
        if world.tile_exists(self.x - 1, self.y, self.z):
            wmap['World'][(self.x - 1, self.y, self.z)].visited = True
        if world.tile_exists(self.x, self.y - 1, self.z):
            wmap['World'][(self.x, self.y - 1, self.z)].visited = True
        if world.tile_exists(self.x, self.y + 1, self.z):
            wmap['World'][(self.x, self.y + 1, self.z)].visited = True

    def minimap(self, player, world_dict):
        """
        Function that allows the player to view the current dungeon level in terminal
        15 x 10 grid
        """
        level = player.location_z
        map_size = (20, 20)
        map_array = numpy.zeros(map_size).astype(str)
        for tile in world_dict['World']:
            if level == tile[2]:
                tile_x, tile_y = tile[1], tile[0]
                if world_dict['World'][tile].visited:
                    if world_dict['World'][tile] is None:
                        continue
                    elif 'stairs' in world_dict['World'][tile].intro_text(player):
                        map_array[tile_x][tile_y] = "x"  # 75
                    elif world_dict['World'][tile].enter:
                        map_array[tile_x][tile_y] = "."  # 255
                    else:
                        if world_dict['World'][tile].visited:
                            map_array[tile_x][tile_y] = "#"
        map_array[player.location_y][player.location_x] = "+"  # 125
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

    def modify_player(self, player, wmap):
        player.state = 'normal'
        player.health = player.health_max
        player.mana = player.mana_max
        town.town(player, wmap)


class EnemyRoom(MapTile):
    def __init__(self, x, y, z, enemy):
        super().__init__(x, y, z)
        self.enemy = enemy

    def intro_text(self, player):
        return ""

    def modify_player(self, player, wmap):
        self.visited = True
        self.adjacent_visited(wmap)
        if self.enemy.is_alive():
            player.state = 'fight'
            combat.battle(player, self.enemy, wmap)

    def available_actions(self, player):
        if self.enemy.is_alive():
            if len(player.spellbook['Spells']) > 0 and len(player.spellbook['Skills']) > 0:
                return [actions.Attack(), actions.UseSkill(), actions.CastSpell(), actions.UseItem()]
            elif len(player.spellbook['Spells']) > 0:
                return [actions.Attack(), actions.CastSpell(), actions.UseItem()]
            elif len(player.spellbook['Skills']) > 0:
                return [actions.Attack(), actions.UseSkill(), actions.UseItem()]
            else:
                return [actions.Attack(), actions.UseItem()]
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class SpecialTile(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.special = True

    def intro_text(self, player):
        raise NotImplementedError

    def modify_player(self, player, wmap):
        self.adjacent_visited(wmap)

    def special_text(self, player):
        raise NotImplementedError


class Wall(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enter = False

    def intro_text(self, player):
        return ""

    def modify_player(self, player, wmap):
        self.adjacent_visited(wmap)


class RandomTile(MapTile):
    """
    Dummy tile; world.py will see this and randomly pick between empty or random enemy
    """
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        raise NotImplementedError()

    def modify_player(self, player, wmap):
        raise NotImplementedError()


class RandomTile2(MapTile):
    """
    Dummy tile; world.py will see this and randomly pick between empty or random enemy from 1 level lower
    """
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        raise NotImplementedError()

    def modify_player(self, player, wmap):
        raise NotImplementedError()


class EmptyCavePath(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        return ""

    def modify_player(self, player, wmap):
        self.adjacent_visited(wmap)

    def available_actions(self, player):
        return self.adjacent_moves([actions.CharacterMenu()])


class LockedDoor(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.LockedDoor())

    def intro_text(self, player):
        if self.enemy.is_alive():
            if self.enemy.lock:
                return """
                {} finds a locked door. If only you could find the key...
                """.format(player.name.capitalize())
            else:
                return """
                There is an unlocked door.
                """
        else:
            return """
            There is an open door.
            """


class LockedDoorEast(LockedDoor):
    def __init__(self, x, y, z):
        super(LockedDoorEast, self).__init__(x, y, z)
        self.blocked = "East"

    def available_actions(self, player):
        if self.enemy.is_alive():
            if self.enemy.lock:
                return self.adjacent_moves([actions.UseItem(), actions.CharacterMenu()], blocked=self.blocked)
            else:
                return self.adjacent_moves([actions.Open(enemy=self.enemy), actions.CharacterMenu()], blocked=self.blocked)
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class LockedDoorWest(LockedDoor):
    def __init__(self, x, y, z):
        super(LockedDoorWest, self).__init__(x, y, z)
        self.blocked = "West"

    def available_actions(self, player):
        if self.enemy.is_alive():
            if self.enemy.lock:
                return self.adjacent_moves([actions.UseItem(), actions.CharacterMenu()], blocked=self.blocked)
            else:
                return self.adjacent_moves([actions.Open(enemy=self.enemy), actions.CharacterMenu()], blocked=self.blocked)
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class LockedDoorNorth(LockedDoor):
    def __init__(self, x, y, z):
        super(LockedDoorNorth, self).__init__(x, y, z)
        self.blocked = "North"

    def available_actions(self, player):
        if self.enemy.is_alive():
            if self.enemy.lock:
                return self.adjacent_moves([actions.UseItem(), actions.CharacterMenu()], blocked=self.blocked)
            else:
                return self.adjacent_moves([actions.Open(enemy=self.enemy), actions.CharacterMenu()], blocked=self.blocked)
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class LockedDoorSouth(LockedDoor):
    def __init__(self, x, y, z):
        super(LockedDoorSouth, self).__init__(x, y, z)
        self.blocked = "South"

    def available_actions(self, player):
        if self.enemy.is_alive():
            if self.enemy.lock:
                return self.adjacent_moves([actions.UseItem(), actions.CharacterMenu()], blocked=self.blocked)
            else:
                return self.adjacent_moves([actions.Open(enemy=self.enemy), actions.CharacterMenu()], blocked=self.blocked)
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class RandomEnemyRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.random_enemy(str(z)))

    def intro_text(self, player):
        if 'Chest' in self.enemy.name:
            if self.enemy.is_alive():
                if self.enemy.lock:
                    return """
                    {} finds a chest!!... but it is locked.
                    """.format(player.name.capitalize())
                else:
                    return """
                    {} finds a chest!!
                    """.format(player.name.capitalize())
            else:
                return """
                This room has an open chest.
                """
        else:
            if self.enemy.is_alive():
                return """
                An enemy {} attacks {}!
                """.format(self.enemy.name, player.name.capitalize())
            else:
                return """
                A dead {} lies on the ground.
                """.format(self.enemy.name)

    def available_actions(self, player):
        if 'Chest' in self.enemy.name:
            if self.enemy.is_alive():
                if self.enemy.lock:
                    return self.adjacent_moves([actions.UseSkill(), actions.UseItem(), actions.CharacterMenu()])
                else:
                    return self.adjacent_moves([actions.Open(enemy=self.enemy), actions.CharacterMenu()])
            else:
                return self.adjacent_moves([actions.CharacterMenu()])
        else:
            if self.enemy.is_alive():
                if len(player.spellbook['Spells']) > 0 and len(player.spellbook['Skills']) > 0:
                    return [actions.Attack(), actions.UseSkill(), actions.CastSpell(),
                            actions.UseItem()]
                elif len(player.spellbook['Spells']) > 0:
                    return [actions.Attack(), actions.CastSpell(), actions.UseItem()]
                elif len(player.spellbook['Skills']) > 0:
                    return [actions.Attack(), actions.UseSkill(), actions.UseItem()]
                else:
                    return [actions.Attack(), actions.UseItem()]
            else:
                return self.adjacent_moves([actions.CharacterMenu()])


class RandomEnemyRoom2(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.random_enemy(str(z + 1)))

    def intro_text(self, player):
        if 'Chest' in self.enemy.name:
            if self.enemy.is_alive():
                if self.enemy.lock:
                    return """
                    {} finds a chest!!... but it is locked.
                    """.format(player.name.capitalize())
                else:
                    return """
                    {} finds a chest!!
                    """.format(player.name.capitalize())
            else:
                return """
                This room has an open chest.
                """
        else:
            if self.enemy.is_alive():
                return """
                An enemy {} attacks {}!
                """.format(self.enemy.name, player.name.capitalize())
            else:
                return """
                A dead {} lies on the ground.
                """.format(self.enemy.name)

    def available_actions(self, player):
        if 'Chest' in self.enemy.name:
            if self.enemy.is_alive():
                if self.enemy.lock:
                    return self.adjacent_moves([actions.UseSkill(), actions.UseItem(), actions.CharacterMenu()])
                else:
                    return self.adjacent_moves([actions.Open(enemy=self.enemy), actions.CharacterMenu()])
            else:
                return self.adjacent_moves([actions.CharacterMenu()])
        else:
            if self.enemy.is_alive():
                if len(player.spellbook['Spells']) > 0 and len(player.spellbook['Skills']) > 0:
                    return [actions.Attack(), actions.UseSkill(), actions.CastSpell(),
                            actions.UseItem()]
                elif len(player.spellbook['Spells']) > 0:
                    return [actions.Attack(), actions.CastSpell(), actions.UseItem()]
                elif len(player.spellbook['Skills']) > 0:
                    return [actions.Attack(), actions.UseSkill(), actions.UseItem()]
                else:
                    return [actions.Attack(), actions.UseItem()]
            else:
                return self.adjacent_moves([actions.CharacterMenu()])


class MinotaurRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.Minotaur())

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


class PseudodragonRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.Pseudodragon())

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


class CockatriceRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.Cockatrice())

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


class GolemRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.Golem())

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


class DomingoRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.Domingo())

    def intro_text(self, player):
        if self.enemy.is_alive():
            return """
            {} stumbles across a floating, tentacled creature wearing a white hat. 
            """.format(player.name)
        else:
            return """
            A dead {} lies on the ground.
            """.format(self.enemy.name)


class RedDragonRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.RedDragon())

    def intro_text(self, player):
        if self.enemy.is_alive():
            return """
            Boss fight!
            An enemy {} attacks {}!
            """.format(self.enemy.name, player.name.capitalize())
        else:
            return """
            The smoking ruins of the once great beast lie in a heap.
            """


class LootRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.Chest(z))

    def intro_text(self, player):
        if self.enemy.is_alive():
            return """
            {} finds a chest!!
            """.format(player.name.capitalize())
        else:
            return """
            This room has an open chest.
            """

    def available_actions(self, player):
        if self.enemy.is_alive():
            return self.adjacent_moves([actions.Open(enemy=self.enemy), actions.CharacterMenu()])
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class LootRoom2(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.Chest(z + 1))

    def intro_text(self, player):
        if self.enemy.is_alive():
            return """
            {} finds a chest!!
            """.format(player.name.capitalize())
        else:
            return """
            This room has an open chest.
            """

    def available_actions(self, player):
        if self.enemy.is_alive():
            return self.adjacent_moves([actions.Open(enemy=self.enemy), actions.CharacterMenu()])
        else:
            return self.adjacent_moves([actions.CharacterMenu()])


class UnobtainiumRoom(SpecialTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.visited = False

    def intro_text(self, player):
        return """
        An empty pedestal stands in the center of the room.
        """

    def modify_player(self, player, wmap):
        self.adjacent_visited(wmap)
        if not self.visited:
            player.modify_inventory(items.Unobtainium, num=1)
            self.visited = True

    def available_actions(self, player):
        return self.adjacent_moves([actions.CharacterMenu()])

    def special_text(self, player):
        game.unobtainium_room()


class FinalBossRoom(SpecialTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.visited = False

    def intro_text(self, player):
        return """
        Step forward to face your destiny.
        """

    def modify_player(self, player, wmap):
        self.adjacent_visited(wmap)
        self.visited = True

    def available_actions(self, player):
        return self.adjacent_moves([actions.CharacterMenu()])

    def special_text(self, player):
        if not self.visited:
            game.final_boss(player)


class StairsUp(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        return """
        {} sees a flight of stairs going up.
        """.format(player.name.capitalize())

    def modify_player(self, player, wmap):
        self.adjacent_visited(wmap)

    def available_actions(self, player):
        return self.adjacent_moves([actions.StairsUp(), actions.CharacterMenu()])


class StairsDown(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        return """
        {} sees a flight of stairs going down.
        """.format(player.name.capitalize())

    def modify_player(self, player, wmap):
        self.adjacent_visited(wmap)

    def available_actions(self, player):
        return self.adjacent_moves([actions.StairsDown(), actions.CharacterMenu()])


class SecretShop(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        return """
        {} finds a secret shop in the depths of the dungeon.
        """.format(player.name.capitalize())

    def modify_player(self, player, wmap):
        self.adjacent_visited(wmap)
        player.state = 'normal'
        town.secret_shop(player)

    def available_actions(self, player):
        pass


class EndTile(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player):
        return """"""

    def modify_player(self, player, wmap):
        raise NotImplementedError  # TODO create function for ending the game

    def available_actions(self, player):
        pass

