###########################################
""" map manager """

import random
import time

import companions
import enemies
import items
import town
import utils
from player import actions_dict


# functions
def check_fake_wall(tile, game):
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        try:
            if "FakeWall" in str(game.player_char.world_dict[(tile.x + dx, tile.y + dy, tile.z)]) and \
                not game.player_char.world_dict[(tile.x + dx, tile.y + dy, tile.z)].visited:
                return "Something seems off but you aren't quite sure what...\n"
        except KeyError:
            continue
    return ""


# objects
class MapTile:

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.near = False
        self.visited = False  # tells whether the tile has been visited by player_char
        self.enter = True  # keeps player_char from entering walls
        self.special = False
        self.open = False

    def intro_text(self, game):
        intro_str = ""
        if 'Keen Eye' in game.player_char.spellbook['Skills']:
            intro_str += check_fake_wall(self, game)
        return intro_str

    def modify_player(self, game):
        raise NotImplementedError()

    def adjacent_moves(self, player_char, append_list: list = None, blocked=None):
        """Returns all move actions for adjacent tiles."""
        if append_list is None:
            append_list = []
        moves = []
        for dx, dy, direction in [(1, 0, "East"), (-1, 0, "West"), (0, 1, "South"), (0, -1, "North")]:
            try:
                if player_char.world_dict[(self.x + dx, self.y + dy, self.z)].enter and blocked != direction:
                    moves.append(actions_dict[f'Move{direction}'])
            except KeyError:
                continue
        for item in append_list:
            moves.append(item)
        return moves

    def available_actions(self, player_char):
        """Returns all the available actions in this room."""
        raise NotImplementedError()

    def adjacent_visited(self, player_char):
        """Changes visited parameter for 4 adjacent tiles"""
        # reveals 4 spaces in cardinal directions
        see = [True] * 4
        try:
            if 'LockedDoor' in str(self):
                if not self.open and self.blocked == "East" and \
                    not player_char.world_dict[(self.x + 1, self.y, self.z)].near:
                    see[0] = False
            player_char.world_dict[(self.x + 1, self.y, self.z)].near = see[0]
        except KeyError:
            pass
        try:
            if 'LockedDoor' in str(self):
                if not self.open and self.blocked == "West" and \
                    not player_char.world_dict[(self.x - 1, self.y, self.z)].near:
                    see[1] = False
            player_char.world_dict[(self.x - 1, self.y, self.z)].near = see[1]
        except KeyError:
            pass
        try:
            if 'LockedDoor' in str(self) or "FinalBlocker" in str(self):
                if not self.open and self.blocked == "North" and \
                    not player_char.world_dict[(self.x, self.y - 1, self.z)].near:
                    see[2] = False
            player_char.world_dict[(self.x, self.y - 1, self.z)].near = see[2]
        except KeyError:
            pass
        try:
            if 'LockedDoor' in str(self):
                if not self.open and self.blocked == "South" and \
                    not player_char.world_dict[(self.x, self.y + 1, self.z)].near:
                    see[3] = False
            player_char.world_dict[(self.x, self.y + 1, self.z)].near = see[3]
        except KeyError:
            pass


class StairsUp(MapTile):

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += (f"{game.player_char.name} sees a flight of stairs going up.\n"
                      f"(Enter 'u' to use)\n")
        return intro_str

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)

    def available_actions(self, player_char):
        return self.adjacent_moves(player_char, [actions_dict['StairsUp'], actions_dict['CharacterMenu']])


class StairsDown(MapTile):

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += (f"{game.player_char.name} sees a flight of stairs going down.\n"
                      f"(Enter 'j' to use)\n")
        return intro_str

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)

    def available_actions(self, player_char):
        return self.adjacent_moves(player_char, [actions_dict['StairsDown'], actions_dict['CharacterMenu']])


class SpecialTile(MapTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.special = True
        self.read = False

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)

    def special_text(self, game):
        raise NotImplementedError

    def available_actions(self, player_char):
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])


class Wall(MapTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enter = False

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)

    def available_actions(self, player_char):
        """Returns all the available actions in this room."""
        return player_char


class FakeWall(Wall):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enter = True

    def available_actions(self, player_char):
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])


class CavePath(MapTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = None

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)
        if game.player_char.cls in ['Warlock', 'Shadowcaster']:
            if game.player_char.familiar.race == 'Jinkin' and game.player_char.familiar.pro_level == 3:
                if not random.randint(0, int(20 - game.player_char.check_mod('luck', luck_factor=10))):
                    rand_item = items.random_item(self.z)
                    game.player_char.modify_inventory(rand_item, 1)
                    find_message = f"{game.player_char.familiar.name} finds {rand_item.name} and gives it to {game.player_char.name}.\n"
                    findbox = utils.TextBox(game)
                    findbox.print_text_in_rectangle(find_message)
                    time.sleep(0.5)
                    game.stdscr.getch()
                    findbox.clear_rectangle()
        if all([not random.randint(0, 4),
                self.enemy is None,
                game.random_combat]):
            self.enter_combat(game.player_char)

    def available_actions(self, player_char):
        if player_char.state == 'fight':
            action_list = ["Attack", "Use Item", "Flee"]
            if not player_char.status_effects["Silence"].active:
                if player_char.usable_abilities("Spells"):
                    action_list.insert(1, "Cast Spell")
                if player_char.usable_abilities("Skills"):
                    action_list.insert(1, "Use Skill")
            action_list = player_char.additional_actions(action_list)
            return action_list
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])

    def enter_combat(self, player_char):
        raise NotImplementedError


class EmptyCavePath(CavePath):
    """
    Cave Path with no random enemies
    """

    def enter_combat(self, player_char):
        pass


class CavePath0(CavePath):

    def modify_player(self, game):
        super().modify_player(game)
        if 'Bring Him Home' in game.player_char.quest_dict['Side']:
            if not game.player_char.quest_dict['Side']['Bring Him Home']['Completed']:
                if not random.randint(0, 20 - game.player_char.check_mod('luck', luck_factor=10)):
                    game.special_event("Timmy")
                    game.player_char.quest_dict['Side']['Bring Him Home']['Completed'] = True
                    game.player_char.to_town()
        if "Ticket to Ride" in game.player_char.quest_dict['Side']:
            if not game.player_char.quest_dict['Side']['Ticket to Ride']['Completed']:
                if not random.randint(0, 20 - game.player_char.check_mod('luck', luck_factor=5)):
                    quest_message = f"You find a piece of the raffle ticket.\n"
                    game.player_char.modify_inventory(items.TicketPiece(), rare=True)
                    quest_message += game.player_char.quests(item=items.TicketPiece())
                    questbox = utils.TextBox(game)
                    questbox.print_text_in_rectangle(quest_message)
                    time.sleep(0.5)
                    game.stdscr.getch()
                    questbox.clear_rectangle()

    def enter_combat(self, player_char):
        self.enemy = enemies.random_enemy('0')
        player_char.state = 'fight'


class CavePath1(CavePath):

    def modify_player(self, game):
        super().modify_player(game)
        if (self.x, self.y, self.z) == (8, 8, 1) and \
            "Rookie Mistake" in game.player_char.quest_dict['Side']:
            if not game.player_char.quest_dict['Side']['Rookie Mistake']['Completed']:
                game.special_event("Rookie")
                game.player_char.modify_inventory(items.DeadBody(), rare=True)
                self.enter_combat(game.player_char)

    def enter_combat(self, player_char):
        self.enemy = enemies.random_enemy(str(self.z))
        player_char.state = 'fight'


class CavePath2(CavePath):

    def enter_combat(self, player_char):
        self.enemy = enemies.random_enemy(str(self.z + 1))
        player_char.state = 'fight'


class BossPath(CavePath):

    def enter_combat(self, player_char):
        self.enemy = random.choice([enemies.Minotaur(),
                                    enemies.Barghest(),
                                    enemies.Pseudodragon(),
                                    enemies.Nightmare()])
        player_char.state = "fight"


class SandwormLair(EmptyCavePath):

    def modify_player(self, game):
        super().modify_player(game)
        if all(["Summoner" in game.player_char.cls.name,
                "Chiryu Koma" in game.player_char.special_inventory,
                "Dilong" not in game.player_char.summons]):
            game.special_event("Dilong")
            summon = companions.Dilong()
            summon.initialize_stats(game.player_char)
            game.player_char.modify_inventory(items.ChiryuKoma(), subtract=True, rare=True)
            game.player_char.summons[summon.name] = summon


class FirePath(EmptyCavePath):

    def modify_player(self, game):
        super().modify_player(game)
        if not game.player_char.flying:
            resist = game.player_char.check_mod("resist", "Fire")
            health_10per = max(0, int(game.player_char.health.max * 0.1 * (1 - resist)))
            damage = random.randint(health_10per // 2, health_10per)
            game.player_char.health.current -= damage
            if damage > 0:
                lava_message = f"{game.player_char.name} takes {damage} damage from the fire."
                lavabox = utils.TextBox(game)
                lavabox.print_text_in_rectangle(lava_message)
                time.sleep(0.5)
                game.stdscr.getch()
                lavabox.clear_rectangle()


class FirePathSpecial(FirePath):
    """
    Cacus summon can be obtained by Summoner class once Vulcan's Hammer is obtained
    """

    def modify_player(self, game):
        if "Vulcan's Hammer" in game.player_char.special_inventory:
            game.special_event("Cacus")
            summon = companions.Cacus()
            summon.initialize_stats(game.player_char)
            game.player_char.modify_inventory(items.BlacksmithsHammer(), subtract=True, rare=True)
            game.player_char.summons[summon.name] = summon
        else:
            super().modify_player(game)


class UndergroundSpring(SpecialTile):
    """
    Drinking from the spring unlocks the sword Excaliper 2:B19
    Fuath summon can be obtained by Summoner class after defeating enemy
    Retrieve Excaliper item to summon Maid of the Spring, Nimue (quest giver)
    Special interaction (maybe reward?) if you craft Excalibur and return
    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.drink = False
        self.nimue = False
        self.enemy = None
        self.defeated = False

    def modify_player(self, game):
        self.visited = True
        player_char = game.player_char
        confirm_message = "The water looks refreshing. Do you want to drink from the spring?"
        confirm = utils.ConfirmPopupMenu(game, header_message=confirm_message, box_height=8)
        springbox = utils.TextBox(game)
        if "Naivete" in player_char.quest_dict["Side"] and \
            not player_char.quest_dict["Side"]["Naivete"]["Completed"]:
            player_char.modify_inventory(items.EmptyVial(), subtract=True, rare=True)
            player_char.modify_inventory(items.SpringWater(), rare=True)
            player_char.quest_dict["Side"]["Naivete"]["Completed"] = True
            message = ("You fill the empty vial with some of the spring water.\n"
                       "You have completed the quest Naivete.\n")
            springbox.print_text_in_rectangle(message)
            game.stdscr.getch()
            springbox.clear_rectangle()
        if confirm.navigate_popup():
            if player_char.level.pro_level > 1 and not random.randint(0, 1):
                if not self.defeated:
                    self.generate_enemy()
                    if self.enemy.is_alive():
                        game.special_event("Fuath1")
                        self.enter_combat(player_char)
                        game.battle(self.enemy, pause=False)
                    if all(["Summoner" in player_char.cls.name,
                            "Fuath" not in player_char.summons,
                            player_char.is_alive()]):
                        game.special_event("Fuath2")
                        summon = companions.Fuath()
                        summon.initialize_stats(player_char)
                        player_char.summons[summon.name] = summon
                if not player_char.is_alive():
                    return
                self.defeated = True
            if not self.drink:
                message = "You drank water from the underground spring...nothing seems to have changed."
                springbox.print_text_in_rectangle(message)
                game.stdscr.getch()
                springbox.clear_rectangle()
                self.drink = True
            if not self.nimue and "Excaliper" in player_char.special_inventory:
                game.special_event("Nimue")
                player_char.modify_inventory(items.Excaliper(), subtract=True, rare=True)
                self.nimue = True
            if self.nimue:
                if "Excalibur" in player_char.inventory or \
                    "Excalibur" == player_char.equipment['Weapon'].name:
                    game.special_event("Excalibur")
                    if "Excalibur" in player_char.inventory:
                        player_char.modify_inventory(items.Excalibur2())
                        player_char.modify_inventory(items.Excalibur(), subtract=True)
                    else:
                        player_char.equipment['Weapon'] = items.Excalibur2()
                """ TODO
                quest, responses = town.check_quests(game, "Nimue")
                if not quest:
                    response = random.choice(random.choice(responses))
                    springbox.print_text_in_rectangle(response)
                    game.stdscr.getch()
                    springbox.clear_rectangle()
                confirm.header_message = "Do you wish to enter the Realm of Cambion?\n"
                if confirm.navigate_popup():
                    player_char.location_x, player_char.location_y, player_char.location_z = (4, 9, 7)
                """

    def enter_combat(self, player_char):
        player_char.state = "fight"

    def special_text(self, game):
        pass

    def generate_enemy(self):
        if self.visited:
            self.enemy = enemies.Fuath()

    def available_actions(self, player_char):
        if player_char.state == 'fight':
            action_list = ["Attack", "Use Item"]
            if not player_char.status_effects["Silence"].active:
                if player_char.usable_abilities("Spells"):
                    action_list.insert(1, "Cast Spell")
                if player_char.usable_abilities("Skills"):
                    action_list.insert(1, "Use Skill")
            action_list = player_char.additional_actions(action_list)
            return action_list
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])


class Boulder(SpecialTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        if not self.read:
            intro_str += "You see a boulder that seems very out of place.\n"
        else:
            intro_str += "There's that boulder where you found that sword...and broke it.\n"
        return intro_str

    def modify_player(self, game):
        pass

    def special_text(self, game):
        if game.player_char.world_dict[(4, 9, 3)].drink and not self.read:
            game.special_event("Boulder")
            game.player_char.modify_inventory(items.Excaliper(), rare=True)
            self.read = True


class Portal(EmptyCavePath):
    """
    Returns player from the Realm of Cambion to the Underground Spring
    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)


class Rotator(EmptyCavePath):
    """
    Spins the player around and pushes them into one of the adjacent enterable spaces
    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)


class BossRoom(SpecialTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = None
        self.defeated = False

    def available_actions(self, player_char):
        if player_char.state == 'fight':
            action_list = ["Attack", "Use Item"]
            if not player_char.status_effects["Silence"].active:
                if player_char.usable_abilities("Spells"):
                    action_list.insert(1, "Cast Spell")
                if player_char.usable_abilities("Skills"):
                    action_list.insert(1, "Use Skill")
            action_list = player_char.additional_actions(action_list)
            return action_list
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)
        if not self.defeated:
            self.generate_enemy()
            if self.enemy.is_alive():
                self.enter_combat(game.player_char)

    def enter_combat(self, player_char):
        player_char.state = 'fight'

    def special_text(self, game):
        if not self.read:
            game.special_event(self.enemy().name)
            self.read = True

    def generate_enemy(self):
        if self.visited:
            try:
                self.enemy = self.enemy()
            except TypeError:
                pass


class MinotaurBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Minotaur

    def intro_text(self, game):
        if not self.enemy:
            return "The remains of the Minotaur lay at your feet.\n"
        return super().intro_text(game)


class BarghestBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Barghest

    def intro_text(self, game):
        if not self.enemy:
            return "A slumped mass of fur and blood mark where the Barghest was slain.\n"
        return super().intro_text(game)


class PseudodragonBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Pseudodragon

    def intro_text(self, game):
        if not self.enemy:
            return "A lavish lair bespeckled with the dust of the smote Pseudodragon.\n"
        return super().intro_text(game)


class NightmareBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Nightmare

    def intro_text(self, game):
        if not self.enemy:
            return ("A heap of bone and sinew is all that is left of the horror that \n"
                    "once befell this hall.\n")
        return super().intro_text(game)


class CockatriceBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Cockatrice

    def intro_text(self, game):
        if not self.enemy:
            return ("Nothing but bones and feathers are left to mark the spot where \n"
                    "the Cockatrice was defeated.")
        return super().intro_text(game)


class WendigoBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Wendigo

    def intro_text(self, game):
        if not self.enemy:
            return "The air feels cold here...but no sign of the slain Wendigo."
        return super().intro_text(game)

    def special_text(self, game):
        super().special_text(game)
        if not self.enemy and "Summoner" in game.player_char.cls.name and \
            "Agloolik" not in game.player_char.summons:
            game.special_event("Agloolik")
            summons = companions.Agloolik()
            summons.initialize_stats(game.player_char)
            game.player_char.summons["Agloolik"] = summons


class IronGolemBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.IronGolem

    def intro_text(self, game):
        if not self.enemy:
            return ("")
        return super().intro_text(game)


class GolemBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Golem

    def intro_text(self, game):
        if not self.enemy:
            return ("")
        return super().intro_text(game)


class JesterBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Jester

    def intro_text(self, game):
        if not self.enemy:
            return ("")
        return super().intro_text(game)


class DomingoBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Domingo

    def intro_text(self, game):
        if not self.enemy:
            return ("")
        return super().intro_text(game)


class RedDragonBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.RedDragon

    def intro_text(self, game):
        if not self.enemy:
            return ("")
        return super().intro_text(game)


class CerberusBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Cerberus

    def intro_text(self, game):
        if not self.enemy:
            return ("")
        return super().intro_text(game)


class FinalBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Devil

    def intro_text(self, game):
        if not self.enemy:
            return ("")
        return super().intro_text(game)


class ChestRoom(MapTile):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.open = False
        self.locked = False
        self.loot = None

    def available_actions(self, player_char):
        raise NotImplementedError

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)
        self.generate_loot()

    def generate_loot(self):
        if self.visited:
            bonus = int('Locked' in str(self)) + int('Room2' in str(self))
            self.loot = items.random_item(self.z + bonus)


class UnlockedChestRoom(ChestRoom):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.locked = False

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        if not self.open:
            intro_str += f"{game.player_char.name} finds a chest. (Enter 'o' to open)\n"
        else:
            intro_str += "This room has an open chest.\n"
        return intro_str

    def available_actions(self, player_char):
        if not self.open:
            if player_char.state == 'fight':
                action_list = ["Attack", "Use Item", "Flee"]
                if not player_char.status_effects["Silence"].active:
                    if player_char.usable_abilities("Spells"):
                        action_list.insert(1, "Cast Spell")
                    if player_char.usable_abilities("Skills"):
                        action_list.insert(1, "Use Skill")
                action_list = player_char.additional_actions(action_list)
                return action_list
            return self.adjacent_moves(player_char, [actions_dict['Open'], actions_dict['CharacterMenu']])
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])


class UnlockedChestRoom2(UnlockedChestRoom):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)


class LockedChestRoom(ChestRoom):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.locked = True

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        if not self.open:
            if self.locked:
                intro_str += f"{game.player_char.name} finds a chest!!... but it is locked.\n"
            else:
                intro_str += f"{game.player_char.name} finds a chest. (Enter 'o' to open)\n"
        else:
            intro_str += "This room has an open chest.\n"
        return intro_str

    def available_actions(self, player_char):
        if not self.open:
            if self.locked:
                return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])
            if player_char.state == 'fight':
                action_list = ["Attack", "Use Item", "Flee"]
                if not player_char.status_effects["Silence"].active:
                    if player_char.usable_abilities("Spells"):
                        action_list.insert(1, "Cast Spell")
                    if player_char.usable_abilities("Skills"):
                        action_list.insert(1, "Use Skill")
                action_list = player_char.additional_actions(action_list)
                return action_list
            return self.adjacent_moves(player_char, [actions_dict['Open'], actions_dict['CharacterMenu']])
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)
        self.generate_loot()
        if self.locked:
            unlockbox = utils.TextBox(game)
            if "Master Key" in game.player_char.special_inventory:
                self.locked = False
                unlockbox.print_text_in_rectangle("You open the chest with the Master key.\n")
                game.stdscr.getch()
                unlockbox.clear_rectangle()
            elif any(["Lockpick" in game.player_char.spellbook["Skills"],
                      "Master Lockpick" in game.player_char.spellbook["Skills"]]):
                unlockbox.print_text_in_rectangle(f"{game.player_char.name} skillfully unlocks the chest.\n")
                self.locked = False
                game.stdscr.getch()
                unlockbox.clear_rectangle()
            elif "Key" in game.player_char.inventory:
                popup = utils.ConfirmPopupMenu(game, "Do you want to unlock the chest with a Key?", box_height=8)
                if popup.navigate_popup():
                    self.locked = False
                    game.player_char.modify_inventory(game.player_char.inventory["Key"][0], subtract=True)


class LockedChestRoom2(LockedChestRoom):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.locked = True


class LockedDoor(MapTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.open = False
        self.locked = True
        self.blocked = None

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        if not self.open:
            if self.locked:
                intro_str += (f"{game.player_char.name} finds a locked door.\n"
                        f"If only you could find the key...\n")
            else:
                intro_str += (f"There is an unlocked door.\n"
                    f"(Enter 'o' to open)\n")
        else:
            intro_str += "There is an open door.\n"
        return intro_str

    def modify_player(self, game):
        self.visited = True
        self.which_blocked(game)
        self.adjacent_visited(game.player_char)
        if self.locked:
            if "Master Key" in game.player_char.special_inventory:
                self.locked = False
                unlockbox = utils.TextBox(game)
                unlockbox.print_text_in_rectangle("You open the door with the Master key.\n")
                game.stdscr.getch()
                unlockbox.clear_rectangle()
            elif 'Master Lockpick' in game.player_char.spellbook['Skills']:
                unlockbox.print_text_in_rectangle(f"{game.player_char.name} skillfully unlocks the chest.\n")
                self.locked = False
                game.stdscr.getch()
                unlockbox.clear_rectangle()
            elif "Old Key" in game.player_char.inventory:
                popup = utils.ConfirmPopupMenu(game, "Do you want to unlock the door with an Old Key?", box_height=8)
                if popup.navigate_popup():
                    self.locked = False
                    game.player_char.modify_inventory(game.player_char.inventory['Old Key'][0], subtract=True)

    def available_actions(self, player_char):
        if not self.open:
            if self.locked:
                return self.adjacent_moves(
                    player_char,
                    [actions_dict['CharacterMenu']],
                    blocked=self.blocked)
            return self.adjacent_moves(
                player_char,
                [actions_dict['Open'], actions_dict['CharacterMenu']],
                blocked=self.blocked)
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])

    def which_blocked(self, game):
        if self.x == game.player_char.previous_location[0] + 1:
            self.blocked = "East"
        if self.x == game.player_char.previous_location[0] - 1:
            self.blocked = "West"
        if self.y == game.player_char.previous_location[1] - 1:
            self.blocked = "North"
        if self.y == game.player_char.previous_location[1] + 1:
            self.blocked = "South"


class WarningTile(CavePath):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.warning = False

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        if not self.warning:
            intro_str += (f"Enemies beyond this point increase in difficulty.\n"
                          f"Plan accordingly.\n")
        return intro_str

    def enter_combat(self, player_char):
        pass


class UnobtainiumRoom(SpecialTile):

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += "An empty pedestal stands in the center of the room.\n"
        return intro_str

    def modify_player(self, game):
        self.adjacent_visited(game.player_char)
        if not self.visited:
            game.player_char.modify_inventory(items.Unobtainium(), rare=True, quest=True)
            self.visited = True

    def special_text(self, game):
        if not self.read:
            game.special_event("Unobtainium")
            self.read = True
            

class RelicRoom(SpecialTile):

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += "An empty pedestal stands in the center of the room.\n"
        return intro_str

    def modify_player(self, game):
        self.adjacent_visited(game.player_char)
        self.visited = True

    def special_text(self, game):
        if not self.read:
            game.special_event("Relic Room")
            relics = [items.Relic1(), items.Relic2(), items.Relic3(), items.Relic4(), items.Relic5(), items.Relic6()]
            game.player_char.modify_inventory(relics[game.player_char.location_z - 1], rare=True, quest=True)
            self.read = True
            specialbox = utils.TextBox(game)
            specialbox.print_text_in_rectangle("Your health and mana have been restored to full!\n")
            game.stdscr.getch()
            game.player_char.health.current = game.player_char.health.max
            game.player_char.mana.current = game.player_char.mana.max
            game.player_char.quests()
            specialbox.clear_rectangle()
            


class DeadBody(SpecialTile):

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        if not self.read:
            intro_str += "The body of a soldier lies in a heap on the floor.\n"
        else:
            if 'Something to Cry About' in game.player_char.quest_dict['Side']:
                if game.player_char.quest_dict['Side']['Something to Cry About']['Completed']:
                    intro_str += f"The two lovers have been reunited. May they rest in peace.\n"
            else:
                intro_str += (f"'Here lies Joffrey, survived by his one true love.\n"
                              f"May he be a reminder of the horrors of combat.\n")
        return intro_str

    def modify_player(self, game):
        self.adjacent_visited(game.player_char)
        self.visited = True
        if 'Something to Cry About' in game.player_char.quest_dict['Side']:
            if not game.player_char.quest_dict['Side']['Something to Cry About']['Completed']:
                game.special_event("Waitress")
                self.enter_combat(game.player_char)

    def special_text(self, game):
        if 'A Bad Dream' in game.player_char.quest_dict['Main']:
            if not self.read:
                game.special_event("Dead Body")
                game.player_char.modify_inventory(items.LuckyLocket(), rare=True, quest=True)
                game.player_char.quest_dict['Main']['A Bad Dream']['Completed'] = True
                self.read = True
                
    def enter_combat(self, player_char):
        self.enemy = enemies.NightHag2()
        player_char.state = 'fight'

    def available_actions(self, player_char):
        if player_char.state == 'fight':
            action_list = ["Attack", "Use Item", "Flee"]
            if not player_char.status_effects["Silence"].active:
                if player_char.usable_abilities("Spells"):
                    action_list.insert(1, "Cast Spell")
                if player_char.usable_abilities("Skills"):
                    action_list.insert(1, "Use Skill")
            action_list = player_char.additional_actions(action_list)
            return action_list
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])


class FinalBlocker(SpecialTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.blocked = "North"

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        if not game.player_char.has_relics():
            intro_str += "An invisible force blocks your path.\n"
        else:
            intro_str += "The way has opened. Destiny awaits!\n"
        return intro_str

    def available_actions(self, player_char):
        if not player_char.has_relics():
            return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']], blocked=self.blocked)
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])

    def special_text(self, game):
        if game.player_char.has_relics() and not self.read:
            game.special_event("Final Blocker")
            self.read = True
            


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

    def adjacent_visited(self, player_char):
        """"
        Changes visited parameter for area around final boss
        """

        for x in [13, 14, 15, 16, 17]:
            for y in [8, 9, 10, 11]:
                player_char.world_dict[(x, y, 6)].near = True

    def special_text(self, game):
        fight = game.special_event("Final Boss")
        if fight:
            game.player_char.move_north()
            game.player_char.move_north()
        else:
            game.player_char.move_south()


class SecretShop(SpecialTile):

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)
        game.player_char.state = 'normal'
        town.secret_shop(game)

    def special_text(self, game):
        if not self.read:
            game.special_event("Secret Shop")
            self.read = True

    def available_actions(self, player_char):
        pass


class UltimateArmorShop(SpecialTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.looted = False

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += (f"{game.player_char.name} finds a forge in the depths of the dungeon.\n"
                        f"A large man stands in front of you.\n")
        return intro_str

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)
        game.player_char.state = 'normal'
        town.ultimate_armor_repo(game)

    def available_actions(self, player_char):
        pass

    def special_text(self, game):
        if not self.read:
            game.special_text("Ultimate Armor")
            self.read = True


class WarpPoint(MapTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.warped = False

    def modify_player(self, game):
        if not self.warped:
            popup = utils.ConfirmPopupMenu(game, "Do you want to return to town?", box_height=7)
            if popup.navigate_popup():
                game.player_char.to_town()
                town.town(game)
                return
        self.warped = False
        self.visited = True
        self.adjacent_visited(game.player_char)

    def available_actions(self, player_char):
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])
