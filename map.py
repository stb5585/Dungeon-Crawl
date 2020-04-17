###########################################
""" map manager """

# Imports
import character
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

    def adjacent_moves(self, append_list: list = None):
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

    def available_actions(self, player):
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

    def available_actions(self, player):
        if self.enemy.is_alive():
            if len(player.spellbook['Spells']) > 0 and len(player.spellbook['Skills']) > 0:
                return [actions.Attack(enemy=self.enemy), actions.UseSkill(), actions.CastSpell(), actions.UseItem()]
            elif len(player.spellbook['Spells']) > 0:
                return [actions.Attack(enemy=self.enemy), actions.CastSpell(), actions.UseItem()]
            elif len(player.spellbook['Skills']) > 0:
                return [actions.Attack(enemy=self.enemy), actions.UseSkill(), actions.UseItem()]
            else:
                return [actions.Attack(enemy=self.enemy), actions.UseItem()]
        else:
            return self.adjacent_moves([actions.Status()])


class EmptyCavePath(MapTile):
    def intro_text(self):
        pass

    def modify_player(self, player):
        # Room has no action on player
        pass

    def available_actions(self, player):
        return self.adjacent_moves([actions.Status()])


class RandomEnemyRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.random_enemy(str(z)))

    def intro_text(self):
        if 'Chest' in self.enemy.name:
            if self.enemy.is_alive():
                if self.enemy.lock:
                    return """
                    You find a chest!!... but it is locked.
                    """
                else:
                    return """
                    You find a chest!!
                    """
            else:
                return """
                This room has an open chest.
                """
        else:
            if self.enemy.is_alive():
                return """
                An enemy {} attacks you!
                """.format(self.enemy.name)
            else:
                return """
                A dead {} lies on the ground.
                """.format(self.enemy.name)

    def available_actions(self, player):
        if 'Chest' in self.enemy.name:
            if self.enemy.is_alive():
                if self.enemy.lock:
                    return self.adjacent_moves([actions.UseSkill(), actions.UseItem()])
                else:
                    return self.adjacent_moves([actions.OpenChest(enemy=self.enemy)])
            else:
                return self.adjacent_moves([actions.Status()])
        else:
            if self.enemy.is_alive():
                if len(player.spellbook['Spells']) > 0 and len(player.spellbook['Skills']) > 0:
                    return [actions.Attack(enemy=self.enemy), actions.UseSkill(), actions.CastSpell(),
                            actions.UseItem()]
                elif len(player.spellbook['Spells']) > 0:
                    return [actions.Attack(enemy=self.enemy), actions.CastSpell(), actions.UseItem()]
                elif len(player.spellbook['Skills']) > 0:
                    return [actions.Attack(enemy=self.enemy), actions.UseSkill(), actions.UseItem()]
                else:
                    return [actions.Attack(enemy=self.enemy), actions.UseItem()]
            else:
                return self.adjacent_moves([actions.Status()])


class MinotaurRoom(EnemyRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, enemies.Minotaur())

    def intro_text(self):
        if self.enemy.is_alive():
            return """
            Boss fight!
            An enemy {} attacks you!
            """.format(self.enemy.name)
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
            Boss fight!
            An enemy {} attacks you!
            """.format(self.enemy.name)
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
            Boss fight!
            An enemy {} attacks you!
            """.format(self.enemy.name)
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
            Boss fight!
            An enemy {} attacks you!
            """.format(self.enemy.name)
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
            Boss fight!
            An enemy {} attacks you!
            """.format(self.enemy.name)
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

    def available_actions(self, player):
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

    def available_actions(self, player):
        return self.adjacent_moves([actions.StairsUp(), actions.Status()])


class StairsDown(MapTile):
    def intro_text(self):
        return """
        You see a flight of stairs going down.
        """

    def modify_player(self, player):
        pass

    def available_actions(self, player):
        return self.adjacent_moves([actions.StairsDown(), actions.Status()])
