###########################################
""" map manager """

# Imports
import os
import random
import sys
import time

import pyfiglet

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
        self.near = False
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
        """Changes visited parameter for 4 adjacent tiles"""
        # reveals 4 spaces in cardinal directions
        see = [True] * 4
        try:
            if 'LockedDoorEast' in self.__str__():
                if not self.open:
                    see[0] = False
            player_char.world_dict[(self.x + 1, self.y, self.z)].near = see[0]
        except KeyError:
            pass
        try:
            if 'LockedDoorWest' in self.__str__():
                if not self.open:
                    see[1] = False
            player_char.world_dict[(self.x - 1, self.y, self.z)].near = see[1]
        except KeyError:
            pass
        try:
            if 'LockedDoorNorth' in self.__str__():
                if not self.open:
                    see[2] = False
            player_char.world_dict[(self.x, self.y - 1, self.z)].near = see[2]
        except KeyError:
            pass
        try:
            if 'LockedDoorSouth' in self.__str__():
                if not self.open:
                    see[3] = False
            player_char.world_dict[(self.x, self.y + 1, self.z)].near = see[3]
        except KeyError:
            pass


class Town(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player_char):
        return ""

    def modify_player(self, player_char):
        self.visited = True
        self.adjacent_visited(player_char)
        player_char.state = 'normal'
        player_char.health = player_char.health_max
        player_char.mana = player_char.mana_max
        town.town(player_char)

    def adjacent_visited(self, player_char):
        """Changes visited parameter for 4 adjacent tiles"""
        # reveals 4 spaces in cardinal directions
        try:
            player_char.world_dict[(self.x + 1, self.y, 1)].near = True
        except KeyError:
            pass
        try:
            player_char.world_dict[(self.x - 1, self.y, 1)].near = True
        except KeyError:
            pass
        try:
            player_char.world_dict[(self.x, self.y - 1, 1)].near = True
        except KeyError:
            pass
        try:
            player_char.world_dict[(self.x, self.y + 1, 1)].near = True
        except KeyError:
            pass


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
        return """
        
        """

    def modify_player(self, player_char):
        self.visited = True
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


class CavePath(MapTile):
    """

    """
    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player_char):
        if 'Keen Eye' in list(player_char.spellbook['Skills'].keys()):
            if 'FakeWall' in [player_char.world_dict[(self.x + 1, self.y, 1)].__str__(),
                              player_char.world_dict[(self.x - 1, self.y, 1)].__str__(),
                              player_char.world_dict[(self.x, self.y + 1, 1)].__str__(),
                              player_char.world_dict[(self.x, self.y - 1, 1)].__str__()]:
                return """
                Something seems off but you aren't quite sure what...
                """
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
                    input("Press enter to continue")
        if not random.randint(0, 4):
            self.enter_combat(player_char)

    def available_actions(self, player_char):
        if player_char.state == 'fight':
            action_list = [actions.Attack(), actions.UseItem(), actions.Flee()]
            if len(player_char.spellbook['Spells']) > 0 and not player_char.status_effects['Silence'][0]:
                action_list.insert(1, actions.CastSpell())
            if len(player_char.spellbook['Skills']) > 0:
                action_list.insert(1, actions.UseSkill())
            return action_list
        return self.adjacent_moves(player_char, [actions.CharacterMenu()])

    def enter_combat(self, player_char):
        raise NotImplementedError


class EmptyCavePath(CavePath):
    """
    Cave Path with no random enemies
    """

    def enter_combat(self, player_char):
        pass


class CavePath0(CavePath):
    """

    """

    def enter_combat(self, player_char):
        enemy = enemies.random_enemy('0')
        player_char.state = 'fight'
        combat.battle(player_char, enemy)
        if 'Bring Him Home' in player_char.quest_dict['Side'].keys():
            if not player_char.quest_dict['Side']['Bring Him Home']['Completed']:
                if not random.randint(0, 20 - player_char.check_mod('luck', luck_factor=10)):
                    game.timmy()
                    player_char.quest_dict['Side']['Bring Him Home']['Completed'] = True
                    print("You have completed the quest Bring Him Home.")
                    time.sleep(2)
                    player_char.location_x, player_char.location_y, player_char.location_z = (5, 10, 0)
                    town.town(player_char)


class CavePath1(CavePath):
    """

    """

    def enter_combat(self, player_char):
        enemy = enemies.random_enemy(str(self.z))
        player_char.state = 'fight'
        combat.battle(player_char, enemy)


class CavePath2(CavePath):
    """

    """

    def enter_combat(self, player_char):
        enemy = enemies.random_enemy(str(self.z + 1))
        player_char.state = 'fight'
        combat.battle(player_char, enemy)


class BossRoom(CavePath):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = None

    def available_actions(self, player_char):
        if player_char.state == 'fight':
            action_list = [actions.Attack(), actions.UseItem(), actions.Flee()]
            if len(player_char.spellbook['Spells']) > 0 and not player_char.status_effects['Silence'][0]:
                action_list.insert(1, actions.CastSpell())
            if len(player_char.spellbook['Skills']) > 0:
                action_list.insert(1, actions.UseSkill())
            return action_list
        return self.adjacent_moves(player_char, [actions.CharacterMenu()])

    def modify_player(self, player_char):
        self.visited = True
        self.adjacent_visited(player_char)
        if self.enemy.is_alive():
            self.enter_combat(player_char)

    def enter_combat(self, player_char):
        player_char.state = 'fight'
        combat.battle(player_char, self.enemy)


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


class IronGolemBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.IronGolem()


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

    def enter_combat(self, player_char):
        player_char.state = 'fight'
        combat.battle(player_char, self.enemy)
        if not player_char.is_alive():
            os.system('cls' if os.name == 'nt' else 'clear')
            f = pyfiglet.Figlet(font='slant')
            print(f.renderText("GAME OVER"))
            time.sleep(2)
            sys.exit(0)
        else:
            pass


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
            if player_char.state == 'fight':
                action_list = [actions.Attack(), actions.UseItem(), actions.Flee()]
                if len(player_char.spellbook['Spells']) > 0 and not player_char.status_effects['Silence'][0]:
                    action_list.insert(1, actions.CastSpell())
                if len(player_char.spellbook['Skills']) > 0:
                    action_list.insert(1, actions.UseSkill())
                return action_list
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
                return self.adjacent_moves(player_char, [actions.CharacterMenu(tile=self)])
            else:
                if player_char.state == 'fight':
                    action_list = [actions.Attack(), actions.UseItem(), actions.Flee()]
                    if len(player_char.spellbook['Spells']) > 0 and not player_char.status_effects['Silence'][0]:
                        action_list.insert(1, actions.CastSpell())
                    if len(player_char.spellbook['Skills']) > 0:
                        action_list.insert(1, actions.UseSkill())
                    return action_list
                return self.adjacent_moves(player_char, [actions.Open(self), actions.CharacterMenu()])
        else:
            return self.adjacent_moves(player_char, [actions.CharacterMenu()])

    def modify_player(self, player_char):
        self.visited = True
        self.adjacent_visited(player_char)
        if self.locked:
            if 'Lockpick' in list(player_char.spellbook['Skills'].keys()):
                print("{} unlocks the chest.".format(player_char.name))
                self.locked = False
                time.sleep(1)


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


class WarningTile(CavePath):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.warning = False

    def intro_text(self, player_char):
        if not self.warning:
            return """
            Enemies beyond this point increase in difficulty. Plan accordingly.
            """
        return """
        
        """

    def enter_combat(self, player_char):
        pass


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
            os.system('cls' if os.name == 'nt' else 'clear')


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
        self.visited = True

    def special_text(self, player_char):
        if not self.read:
            game.relic_room(player_char.location_z)
            relics = [items.Relic1, items.Relic2, items.Relic3, items.Relic4, items.Relic5, items.Relic6]
            player_char.modify_inventory(relics[player_char.location_z - 1], rare=True)
            self.read = True
            print("Your health and mana have been restored to full!")
            player_char.health = player_char.health_max
            player_char.mana = player_char.mana_max
            player_char.quests()
            input("Press enter to continue")


class DeadBody(SpecialTile):
    """

    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player_char):
        if not self.read:
            return """
            The body of a soldier lies in a heap on the floor.
            """
        return """
        You see a burial mound with an inscription carved in the floor reading "Here lies Joffrey, survived by his one
          true love. May he be a reminder of the horrors of combat."
        """

    def modify_player(self, player_char):
        self.adjacent_visited(player_char)
        self.visited = True

    def special_text(self, player_char):
        if 'A Bad Dream' in player_char.quest_dict.keys():
            if not self.read:
                game.dead_body()
                player_char.modify_inventory(items.LuckyLocket, rare=True)
                self.read = True
                input("Press enter to continue")


class FinalBlocker(SpecialTile):
    """

    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.blocked = "North"

    def intro_text(self, player_char):
        if not player_char.has_relics:
            return """
            An invisible force blocks your path.
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
            game.final_blocker()
            self.read = True
            os.system('cls' if os.name == 'nt' else 'clear')


class FinalRoom(SpecialTile):
    """
    Player will be given an option to fight or turn around; fight will move them to FinalBossRoom and turn around will
      move them back to FinalBlocker
    Tiles to show -
    (13,  8, 6), (14,  8, 6), (15,  8, 6), (16,  8, 6), (17,  8, 6)
    (13,  9, 6), (14,  9, 6), (15,  9, 6), (16,  9, 6), (17,  9, 6)
    (13, 10, 6), (14, 10, 6), (15, 10, 6), (16, 10, 6), (17, 10, 6)
    (13, 11, 6), (14, 11, 6), (15, 11, 6), (16, 11, 6), (17, 11, 6)
    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def adjacent_visited(self, player_char):
        """"
        Changes visited parameter for area around final boss
        """

        for x in [13, 14, 15, 16, 17]:
            for y in [8, 9, 10, 11]:
                player_char.world_dict[(x, y, 6)].near = True

    def special_text(self, player_char):
        fight = game.final_boss(player_char)
        if fight:
            player_char.move_north()
            player_char.move_north()
        else:
            player_char.move_south()


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


class WarpPoint(MapTile):
    """

    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, player_char):
        pass

    def modify_player(self, player_char):
        self.visited = True
        self.adjacent_visited(player_char)
