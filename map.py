###########################################
""" map manager """

# Imports
import enemies
import actions
import world
import combat


class MapTile:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def intro_text(self):
        raise NotImplementedError()

    def modify_player(self, player):
        raise NotImplementedError()

    def adjacent_moves(self, append_list=None):
        """Returns all move actions for adjacent tiles."""
        if append_list is None:
            append_list = []
        moves = []
        if world.tile_exists(self.x + 1, self.y, self.z):
            moves.append(actions.MoveEast())
        if world.tile_exists(self.x - 1, self.y, self.z):
            moves.append(actions.MoveWest())
        if world.tile_exists(self.x, self.y - 1, self.z):
            moves.append(actions.MoveNorth())
        if world.tile_exists(self.x, self.y + 1, self.z):
            moves.append(actions.MoveSouth())
        for item in append_list:
            moves.append(item)
        return moves

    def available_actions(self):
        """Returns all of the available actions in this room."""
        pass


class EnemyRoom(MapTile):
    def __init__(self, x, y, z, enemy):
        self.enemy = enemy
        super().__init__(x, y, z)

    def modify_player(self, player):
        if self.enemy.is_alive():
            player.state = 'fight'
            combat.battle(player, self.enemy)

    def available_actions(self):
        if self.enemy.is_alive():
            return [actions.Attack(enemy=self.enemy), actions.Special(), actions.UseItem()]
        else:
            return self.adjacent_moves([actions.Status()])


class EmptyCavePath(MapTile):
    def intro_text(self):
        pass

    def modify_player(self, player):
        # Room has no action on player
        pass

    def available_actions(self):
        return self.adjacent_moves([actions.Status()])


class RandomEnemyRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.random_enemy(str(z)))

    def intro_text(self):
        if self.enemy.is_alive():
            return """
            An enemy {} attacks you!\n
            {}
            """.format(self.enemy.name, self.enemy.health)
        else:
            return """
            A dead {} lies on the ground.
            """.format(self.enemy.name)


class MinotaurRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.Minotaur())

    def intro_text(self):
        if self.enemy.is_alive():
            return """
            An enemy {} attacks you!\n
            {}
            """.format(self.enemy.name, self.enemy.health)
        else:
            return """
            A dead {} lies on the ground.
            """.format(self.enemy.name)


class PseudodragonRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.Pseudodragon())

    def intro_text(self):
        if self.enemy.is_alive():
            return """
            An enemy {} attacks you!\n
            {}
            """.format(self.enemy.name, self.enemy.health)
        else:
            return """
            A dead {} lies on the ground.
            """.format(self.enemy.name)


class CockatriceRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.Cockatrice())

    def intro_text(self):
        if self.enemy.is_alive():
            return """
            An enemy {} attacks you!\n
            {}
            """.format(self.enemy.name, self.enemy.health)
        else:
            return """
            A dead {} lies on the ground.
            """.format(self.enemy.name)


class GolemRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.Golem())

    def intro_text(self):
        if self.enemy.is_alive():
            return """
            An enemy {} attacks you!\n
            {}
            """.format(self.enemy.name, self.enemy.health)
        else:
            return """
            A dead {} lies on the ground.
            """.format(self.enemy.name)


class RedDragonRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.RedDragon())

    def intro_text(self):
        if self.enemy.is_alive():
            return """
            An enemy {} attacks you!\n
            {}
            """.format(self.enemy.name, self.enemy.health)
        else:
            return """
            A dead {} lies on the ground.
            """.format(self.enemy.name)


class LootRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.Chest())

    def intro_text(self):
        if self.enemy.is_alive():
            return """
            You find a chest!!
            """
        else:
            return """
            This room has an open chest.
            """

    def available_actions(self):
        if self.enemy.is_alive():
            return self.adjacent_moves([actions.OpenChest(enemy=self.enemy)])
        else:
            return self.adjacent_moves([actions.Status()])


class StairsUp(MapTile):
    def intro_text(self):
        return """
        You see a flight of stairs going up.
        """

    def modify_player(self, player):
        pass

    def available_actions(self):
        return self.adjacent_moves([actions.StairsUp(), actions.Status()])


class StairsDown(MapTile):
    def intro_text(self):
        return """
        You see a flight of stairs going down.
        """

    def modify_player(self, player):
        pass

    def available_actions(self):
        return self.adjacent_moves([actions.StairsDown(), actions.Status()])
