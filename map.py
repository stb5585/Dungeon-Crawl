###########################################
""" map manager """

# Imports
import random

import enemies
import actions
import game
import items
import combat
import town


class MapTile:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.visited = False  # tells whether the tile has been visited by player_char
        self.enter = True  # keeps player_char from entering walls
        self.special = False

    def intro_text(self, player_char):
        raise NotImplementedError()

    def modify_player(self, player_char):
        raise NotImplementedError()

    def adjacent_moves(self, player_char, append_list: list = None, blocked=None):
        """Returns all move actions for adjacent tiles."""
        if append_list is None:
            append_list = []
        moves = []
        try:
            if player_char.world_dict[(self.x + 1, self.y, self.z)].enter and blocked != "East":
                moves.append(actions.MoveEast())
        except KeyError:
            pass
        try:
            if player_char.world_dict[(self.x - 1, self.y, self.z)].enter and blocked != "West":
                moves.append(actions.MoveWest())
        except KeyError:
            pass
        try:
            if player_char.world_dict[(self.x, self.y - 1, self.z)].enter and blocked != "North":
                moves.append(actions.MoveNorth())
        except KeyError:
            pass
        try:
            if player_char.world_dict[(self.x, self.y + 1, self.z)].enter and blocked != "South":
                moves.append(actions.MoveSouth())
        except KeyError:
            pass
        for item in append_list:
            moves.append(item)
        return moves

    def available_actions(self, player_char):
        """Returns all the available actions in this room."""
        pass

    def adjacent_visited(self, player_char):
        """Changes visited parameter for 8 adjacent tiles"""
        # reveals 4 spaces in cardinal directions
        try:
            player_char.world_dict[(self.x + 1, self.y, self.z)].visited = True
        except KeyError:
            pass
        try:
            player_char.world_dict[(self.x - 1, self.y, self.z)].visited = True
        except KeyError:
            pass
        try:
            player_char.world_dict[(self.x, self.y - 1, self.z)].visited = True
        except KeyError:
            pass
        try:
            player_char.world_dict[(self.x, self.y + 1, self.z)].visited = True
        except KeyError:
            pass


class Town(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player_char):
        return ""

    def modify_player(self, player_char):
        player_char.state = 'normal'
        player_char.health = player_char.health_max
        player_char.mana = player_char.mana_max
        town.town(player_char)


class EnemyRoom(MapTile):
    def __init__(self, x, y, z, enemy):
        super().__init__(x, y, z)
        self.enemy = enemy

    def intro_text(self, player_char):
        if self.enemy.is_alive():
            return """
            An enemy {} attacks {}!
            """.format(self.enemy.name, player_char.name)
        else:
            return """
            A dead {} lies on the ground.
            """.format(self.enemy.name)

    def modify_player(self, player_char):
        self.visited = True
        self.adjacent_visited(player_char)
        if self.enemy.is_alive():
            player_char.state = 'fight'
            combat.battle(player_char, self.enemy)

    def available_actions(self, player_char):
        if self.enemy.is_alive():
            action_list = [actions.Attack(), actions.UseItem(), actions.Flee()]
            if len(player_char.spellbook['Spells']) > 0:
                action_list.insert(1, actions.CastSpell())
            if len(player_char.spellbook['Skills']) > 0:
                action_list.insert(1, actions.UseSkill())
            return action_list
        else:
            return self.adjacent_moves(player_char, [actions.CharacterMenu()])


class StairsUp(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player_char):
        return """
        {} sees a flight of stairs going up. (Enter 'u' to use)
        """.format(player_char.name.capitalize())

    def modify_player(self, player_char):
        self.visited = True
        self.adjacent_visited(player_char)

    def available_actions(self, player_char):
        return self.adjacent_moves(player_char, [actions.StairsUp(), actions.CharacterMenu()])


class StairsDown(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player_char):
        return """
        {} sees a flight of stairs going down. (Enter 'j' to use)
        """.format(player_char.name.capitalize())

    def modify_player(self, player_char):
        self.visited = True
        self.adjacent_visited(player_char)

    def available_actions(self, player_char):
        return self.adjacent_moves(player_char, [actions.StairsDown(), actions.CharacterMenu()])


class SpecialTile(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.special = True
        self.read = False

    def intro_text(self, player_char):
        raise NotImplementedError

    def modify_player(self, player_char):
        self.adjacent_visited(player_char)

    def special_text(self, player_char):
        raise NotImplementedError

    def available_actions(self, player_char):
        return self.adjacent_moves(player_char, [actions.CharacterMenu()])


class Wall(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enter = False

    def intro_text(self, player_char):
        return ""

    def modify_player(self, player_char):
        self.visited = True
        self.adjacent_visited(player_char)


class FakeWall(Wall):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enter = True

    def available_actions(self, player_char):
        return self.adjacent_moves(player_char, [actions.CharacterMenu()])


class RandomTile(MapTile):
    """
    Dummy tile; randomly picks between empty or random enemy
    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player_char):
        raise NotImplementedError()

    def modify_player(self, player_char):
        raise NotImplementedError()


class RandomTile2(MapTile):
    """
    Dummy tile; randomly picks between empty or random enemy from 1 level lower
    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player_char):
        raise NotImplementedError()

    def modify_player(self, player_char):
        raise NotImplementedError()


class EmptyCavePath(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player_char):
        return """
        
        """

    def modify_player(self, player_char):
        self.visited = True
        self.adjacent_visited(player_char)
        if player_char.cls in ['Warlock', 'Shadowcaster']:
            if player_char.familiar.typ == 'Jinkin' and player_char.familiar.pro_level == 3:
                if not random.randint(0, int(20 - player_char.check_mod('luck', luck_factor=10))):
                    rand_item = items.random_item(self.z)
                    player_char.modify_inventory(rand_item, 1)
                    print("{} finds {} and gives it to {}.".format(
                        player_char.familiar.name, rand_item().name, player_char.name))

    def available_actions(self, player_char):
        return self.adjacent_moves(player_char, [actions.CharacterMenu()])


class WarningTile(EmptyCavePath):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player_char):
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

    def intro_text(self, player_char):
        if self.enemy.is_alive():
            return """
            Boss fight!
            An enemy {} attacks {}!
            """.format(self.enemy.name, player_char.name.capitalize())
        else:
            return """
            A dead {} lies on the ground.
            """.format(self.enemy.name)

    def available_actions(self, player_char):
        if self.enemy.is_alive():
            action_list = [actions.Attack(), actions.UseItem()]
            if len(player_char.spellbook['Spells']) > 0:
                action_list.insert(1, actions.CastSpell())
            if len(player_char.spellbook['Skills']) > 0:
                action_list.insert(1, actions.UseSkill())
            return action_list
        else:
            return self.adjacent_moves(player_char, [actions.CharacterMenu()])


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


class CerberusBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Cerberus()


class FinalBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Devil()


class ChestRoom(MapTile):
    def __init__(self, x, y, z, loot):
        super().__init__(x, y, z)
        self.loot = loot

    def intro_text(self, player_char):
        raise NotImplementedError

    def available_actions(self, player_char):
        raise NotImplementedError

    def modify_player(self, player_char):
        self.visited = True
        self.adjacent_visited(player_char)


class UnlockedChestRoom(ChestRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, items.random_item(z))
        self.open = False
        self.locked = False

    def intro_text(self, player_char):
        if not self.open:
            return """
            {} finds a chest. (Enter 'o' to open)
            """.format(player_char.name.capitalize())
        else:
            return """
            This room has an open chest.
            """

    def available_actions(self, player_char):
        if not self.open:
            return self.adjacent_moves(player_char, [actions.Open(self), actions.CharacterMenu()])
        else:
            return self.adjacent_moves(player_char, [actions.CharacterMenu()])


class UnlockedChestRoom2(UnlockedChestRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.loot = items.random_item(z + 1)
        self.open = False
        self.locked = False


class LockedChestRoom(ChestRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z, items.random_item(z + 1))
        self.open = False
        self.locked = True

    def intro_text(self, player_char):
        if not self.open:
            if self.locked:
                return """
                {} finds a chest!!... but it is locked.
                """.format(player_char.name.capitalize())
            else:
                return """
                {} finds a chest. (Enter 'o' to open)
                """.format(player_char.name.capitalize())
        else:
            return """
            This room has an open chest.
            """

    def available_actions(self, player_char):
        if not self.open:
            if self.locked:
                return self.adjacent_moves(player_char, [actions.UseSkill(), actions.UseItem(),
                                                         actions.CharacterMenu(tile=self)])
            else:
                return self.adjacent_moves(player_char, [actions.Open(self), actions.CharacterMenu()])
        else:
            return self.adjacent_moves(player_char, [actions.CharacterMenu()])


class LockedChestRoom2(LockedChestRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.loot = items.random_item(z + 2)
        self.open = False
        self.locked = True


class LockedDoor(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.open = False
        self.locked = True
        self.blocked = None

    def intro_text(self, player_char):
        if not self.open:
            if self.locked:
                return """
                {} finds a locked door. If only you could find the key...
                """.format(player_char.name.capitalize())
            else:
                return """
                There is an unlocked door. (Enter 'o' to open)
                """
        else:
            return """
            There is an open door.
            """

    def modify_player(self, player_char):
        self.visited = True
        self.adjacent_visited(player_char)

    def available_actions(self, player_char):
        if not self.open:
            if self.locked:
                return self.adjacent_moves(player_char, [actions.UseItem(tile=self), actions.CharacterMenu(tile=self)],
                                           blocked=self.blocked)
            else:
                return self.adjacent_moves(player_char, [actions.Open(self), actions.CharacterMenu()],
                                           blocked=self.blocked)
        else:
            return self.adjacent_moves(player_char, [actions.CharacterMenu()])


class LockedDoorEast(LockedDoor):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.blocked = "East"


class LockedDoorWest(LockedDoor):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.blocked = "West"


class LockedDoorNorth(LockedDoor):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.blocked = "North"


class LockedDoorSouth(LockedDoor):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.blocked = "South"


class UnobtainiumRoom(SpecialTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player_char):
        return """
        An empty pedestal stands in the center of the room.
        """

    def modify_player(self, player_char):
        self.adjacent_visited(player_char)
        if not self.visited:
            player_char.modify_inventory(items.Unobtainium, rare=True)
            self.visited = True

    def special_text(self, player_char):
        if not self.read:
            game.unobtainium_room()
            self.read = True


class RelicRoom(SpecialTile):
    """

    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player_char):
        return """
        An empty pedestal stands in the center of the room.
        """

    def modify_player(self, player_char):
        self.adjacent_visited(player_char)
        if not self.visited:
            player_char.health = player_char.health_max
            player_char.mana = player_char.mana_max
            relics = [items.Relic1, items.Relic2, items.Relic3, items.Relic4, items.Relic5, items.Relic6]
            player_char.modify_inventory(relics[player_char.location_z - 1], rare=True)
            self.visited = True

    def special_text(self, player_char):
        if not self.read:
            game.relic_room(player_char.location_z)
            self.read = True


class FinalBlocker(SpecialTile):
    """

    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.blocked = "North"

    def intro_text(self, player_char):
        if not player_char.has_relics:
            return """
            You must collect all 6 relics before you can pass.
            """
        return """
        The way has opened. Destiny awaits! 
        """

    def available_actions(self, player_char):
        if not player_char.has_relics:
            return self.adjacent_moves(player_char, [actions.CharacterMenu()], blocked=self.blocked)
        return self.adjacent_moves(player_char, [actions.CharacterMenu()])

    def special_text(self, player_char):
        if player_char.has_relics and not self.read:
            game.final_blocker(player_char)
            self.read = True


class SecretShop(MapTile):
    """

    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player_char):
        return """
        {} finds a secret shop in the depths of the dungeon.
        """.format(player_char.name.capitalize())

    def modify_player(self, player_char):
        self.visited = True
        self.adjacent_visited(player_char)
        player_char.state = 'normal'
        town.secret_shop(player_char)

    def available_actions(self, player_char):
        pass


class UltimateArmorShop(MapTile):
    """

    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.looted = False

    def intro_text(self, player_char):
        if not self.looted:
            return """
            {} finds a forge in the depths of the dungeon. A large man stands in front of you.
            """.format(player_char.name.capitalize())
        else:
            return """
            A large empty room.
            """

    def modify_player(self, player_char):
        self.visited = True
        self.adjacent_visited(player_char)
        player_char.state = 'normal'
        if not self.looted:
            self.looted = town.ultimate_armor_repo(player_char)

    def available_actions(self, player_char):
        pass
