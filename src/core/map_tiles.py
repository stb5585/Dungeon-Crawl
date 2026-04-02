###########################################
""" map manager """

import random
from textwrap import wrap

from . import companions, enemies, items, town
from .player import DIRECTIONS, REALM_OF_CAMBION_LEVEL, actions_dict

# Feature flag: Set to True to use enhanced combat with action queue
USE_ENHANCED_COMBAT = True


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


CHALICE_QUEST_NAME = "The Holy Grail of Quests"
CHALICE_PROGRESS_KEY = "Chalice Progress"
CHALICE_ADVENTURER_POS = (12, 14, 3)
CHALICE_LOCATION_POS = (2, 17, 6)
UNDERGROUND_SPRING_POS = (4, 9, 3)
REALM_OF_CAMBION_ENTRY_POS = (1, 28, REALM_OF_CAMBION_LEVEL)
CAMBION_SWITCH_CODE = "2749"
CAMBION_SWITCH_POS = (12, 28, REALM_OF_CAMBION_LEVEL)
CAMBION_ALARM_ENEMY = enemies.Warforged
CAMBION_CODE_CLUES = {
    (1, 1, REALM_OF_CAMBION_LEVEL): "A sigil burned into the stone shows the first digit: 2.",
    (23, 9, REALM_OF_CAMBION_LEVEL): "A charred warning plate hisses. The second digit is 7.",
    (20, 20, REALM_OF_CAMBION_LEVEL): "A rotating ring clicks into place and reveals the third digit: 4.",
    (25, 28, REALM_OF_CAMBION_LEVEL): "An etched rune near the terminal reveals the last digit: 9.",
}
CAMBION_PORTAL_PAIRS = [
    ((1, 1, REALM_OF_CAMBION_LEVEL), (28, 28, REALM_OF_CAMBION_LEVEL)),
    ((9, 1, REALM_OF_CAMBION_LEVEL), (28, 20, REALM_OF_CAMBION_LEVEL)),
    ((11, 1, REALM_OF_CAMBION_LEVEL), (1, 22, REALM_OF_CAMBION_LEVEL)),
    ((17, 1, REALM_OF_CAMBION_LEVEL), (5, 28, REALM_OF_CAMBION_LEVEL)),
    ((28, 1, REALM_OF_CAMBION_LEVEL), (8, 3, REALM_OF_CAMBION_LEVEL)),
    ((1, 4, REALM_OF_CAMBION_LEVEL), (16, 4, REALM_OF_CAMBION_LEVEL)),
    ((24, 6, REALM_OF_CAMBION_LEVEL), (22, 10, REALM_OF_CAMBION_LEVEL)),
    ((4, 11, REALM_OF_CAMBION_LEVEL), (17, 13, REALM_OF_CAMBION_LEVEL)),
    ((20, 13, REALM_OF_CAMBION_LEVEL), (23, 13, REALM_OF_CAMBION_LEVEL)),
    ((28, 15, REALM_OF_CAMBION_LEVEL), (22, 17, REALM_OF_CAMBION_LEVEL)),
    ((6, 18, REALM_OF_CAMBION_LEVEL), (12, 24, REALM_OF_CAMBION_LEVEL)),
]
CHALICE_ALTAR_IMAGE_PATH = "src/ui_pygame/assets/sprites/key_items/chalice_map.png"
CHALICE_MAP_BLANK_DESC = "A weathered map whose ink appears almost completely faded."
CHALICE_MAP_METHOD_DESC = (
    "A weathered map with barely visible marks. The hidden adventurer showed you a trick to reveal it—"
    "inspect it closely."
)
CHALICE_MAP_REVEALED_DESC = (
    "The hidden ink has surfaced. The map marks a sealed altar on the sixth floor."
)
CHALICE_MAP_REVEALED_ASCII = (
    "Map Fragment\n"
    "+------------------+\n"
    "| Floor 6          |\n"
    "|                  |\n"
    "|  x=2, y=17   X   |\n"
    "|              altar|\n"
    "+------------------+"
)


def _ensure_chalice_progress(quest_data: dict | None) -> dict | None:
    if not quest_data:
        return None
    progress = quest_data.setdefault(CHALICE_PROGRESS_KEY, {})
    for key in ("Hooded", "Map", "Sergeant", "Adventurer", "Revealed", "Spawned"):
        progress.setdefault(key, False)
    return progress


def get_chalice_progress(player_char):
    quest_dict = getattr(player_char, "quest_dict", {})
    quest_data = quest_dict.get("Side", {}).get(CHALICE_QUEST_NAME)
    return _ensure_chalice_progress(quest_data)


def chalice_altar_visible(player_char) -> bool:
    """Return whether the Golden Chalice altar should be visible to the player."""
    quest_dict = getattr(player_char, "quest_dict", {})
    quest_data = quest_dict.get("Side", {}).get(CHALICE_QUEST_NAME)
    progress = _ensure_chalice_progress(quest_data)
    return bool(progress and (progress.get("Revealed") or quest_data.get("Completed")))


def _set_chalice_map_description(player_char, text: str):
    map_items = player_char.special_inventory.get("Chalice Map", [])
    if not map_items:
        return
    wrapped = "\n".join(wrap(text, 35, break_on_hyphens=False))
    for map_item in map_items:
        map_item.description = wrapped


def sync_chalice_map_description(player_char):
    """Keep Chalice Map description aligned with quest progression."""
    quest_data = player_char.quest_dict.get("Side", {}).get(CHALICE_QUEST_NAME)
    progress = _ensure_chalice_progress(quest_data)
    if not progress or "Chalice Map" not in player_char.special_inventory:
        return

    if progress.get("Revealed") or (quest_data and quest_data.get("Completed")):
        _set_chalice_map_description(player_char, CHALICE_MAP_REVEALED_DESC)
    elif progress.get("Adventurer"):
        _set_chalice_map_description(player_char, CHALICE_MAP_METHOD_DESC)
    else:
        _set_chalice_map_description(player_char, CHALICE_MAP_BLANK_DESC)


def reveal_chalice_map_on_inspect(player_char, item) -> bool:
    """Reveal Chalice location when an instructed player inspects the map."""
    if not item or getattr(item, "name", "") != "Chalice Map":
        return False

    quest_data = player_char.quest_dict.get("Side", {}).get(CHALICE_QUEST_NAME)
    progress = _ensure_chalice_progress(quest_data)
    if not progress:
        return False

    revealed_now = False
    if progress.get("Adventurer") and not progress.get("Revealed"):
        progress["Revealed"] = True
        if quest_data is not None:
            quest_data["Help Text"] = "The map reveals the altar at 6:2,17. Seek the Golden Chalice there."
        revealed_now = True

    sync_chalice_map_description(player_char)
    return revealed_now


def chalice_map_preview_text(player_char) -> str:
    quest_data = player_char.quest_dict.get("Side", {}).get(CHALICE_QUEST_NAME)
    progress = _ensure_chalice_progress(quest_data)
    if not progress:
        return ""
    if not progress.get("Adventurer"):
        return "The map is too faded to decipher."
    if not progress.get("Revealed"):
        return "Most of the ink is still hidden. Inspect the map carefully to reveal the altar location."
    return CHALICE_MAP_REVEALED_ASCII


def _replace_tile(world_dict, pos, new_tile):
    old_tile = world_dict.get(pos)
    if old_tile:
        for attr in ("visited", "near", "open", "read", "blocked", "enter", "defeated"):
            if hasattr(old_tile, attr) and hasattr(new_tile, attr):
                setattr(new_tile, attr, getattr(old_tile, attr))
    world_dict[pos] = new_tile


CAMBION_PORTAL_MAP = {}
for left, right in CAMBION_PORTAL_PAIRS:
    CAMBION_PORTAL_MAP[left] = right
    CAMBION_PORTAL_MAP[right] = left


def _enterable_adjacent_positions(world_dict, x: int, y: int, z: int) -> list[tuple[str, tuple[int, int, int]]]:
    positions = []
    for direction, data in DIRECTIONS.items():
        dx, dy = data["move"]
        pos = (x + dx, y + dy, z)
        tile = world_dict.get(pos)
        if tile and getattr(tile, "enter", False):
            positions.append((direction, pos))
    return positions


def _ensure_cambion_state(player_char) -> dict:
    state = getattr(player_char, "cambion_state", None)
    if not isinstance(state, dict):
        state = {}
        player_char.cambion_state = state
    state.setdefault("anti_magic_active", True)
    state.setdefault("alarm_count", 0)
    state.setdefault("clues_found", {})
    state.setdefault("messages", [])
    player_char.anti_magic_active = bool(state["anti_magic_active"])
    return state


def _queue_cambion_message(player_char, message: str):
    state = _ensure_cambion_state(player_char)
    state["messages"].append(message)


def pop_cambion_messages(player_char) -> list[str]:
    if getattr(player_char, "location_z", None) != REALM_OF_CAMBION_LEVEL and not hasattr(player_char, "cambion_state"):
        return []
    state = _ensure_cambion_state(player_char)
    messages = list(state.get("messages", []))
    state["messages"] = []
    return messages


def cambion_anti_magic_active(player_char) -> bool:
    return bool(_ensure_cambion_state(player_char).get("anti_magic_active", True))


def disable_cambion_anti_magic(player_char):
    state = _ensure_cambion_state(player_char)
    state["anti_magic_active"] = False
    player_char.anti_magic_active = False


def reveal_cambion_code_clue(player_char, pos):
    if pos not in CAMBION_CODE_CLUES:
        return
    state = _ensure_cambion_state(player_char)
    key = f"{pos[0]},{pos[1]},{pos[2]}"
    if state["clues_found"].get(key):
        return
    state["clues_found"][key] = True
    _queue_cambion_message(player_char, CAMBION_CODE_CLUES[pos])


def _apply_cambion_antimagic(tile, player_char, enemy=None):
    if tile.z != REALM_OF_CAMBION_LEVEL:
        return
    active = cambion_anti_magic_active(player_char)
    player_char.anti_magic_active = active
    if enemy is not None:
        enemy.anti_magic_active = active


def enter_realm_of_cambion(player_char):
    player_char.enter_realm_of_cambion(*REALM_OF_CAMBION_ENTRY_POS, facing="east")
    player_char.cambion_state = {
        "anti_magic_active": True,
        "alarm_count": 0,
        "clues_found": {},
        "messages": [],
    }
    player_char.anti_magic_active = True


def return_to_underground_spring(player_char):
    if hasattr(player_char, "cambion_return") and player_char.cambion_return:
        player_char.exit_realm_of_cambion()
        return
    player_char.location_x, player_char.location_y, player_char.location_z = UNDERGROUND_SPRING_POS
    player_char.facing = "east"


def update_chalice_location(game):
    """Hide or reveal the Golden Chalice altar based on quest progression."""
    player_char = game.player_char
    quest_data = player_char.quest_dict.get("Side", {}).get(CHALICE_QUEST_NAME)
    progress = _ensure_chalice_progress(quest_data)
    sync_chalice_map_description(player_char)
    pos = CHALICE_LOCATION_POS
    tile = player_char.world_dict.get(pos)
    if tile is None:
        return

    should_reveal = chalice_altar_visible(player_char)
    if should_reveal:
        if not isinstance(tile, GoldenChaliceRoom):
            new_tile = GoldenChaliceRoom(*pos)
            new_tile.enter = False
            _replace_tile(player_char.world_dict, pos, new_tile)
            if progress is not None:
                progress["Spawned"] = True
            if (player_char.location_x, player_char.location_y, player_char.location_z) == pos:
                game.special_event("Chalice Revealed")
        else:
            tile.enter = False
    else:
        if isinstance(tile, GoldenChaliceRoom):
            tile.enter = True
            _replace_tile(player_char.world_dict, pos, CavePath(*pos))


def handle_chalice_adventurer(game):
    """Trigger the hidden adventurer clue for the Golden Chalice quest."""
    player_char = game.player_char
    quest_data = player_char.quest_dict.get("Side", {}).get(CHALICE_QUEST_NAME)
    progress = _ensure_chalice_progress(quest_data)
    if not progress:
        return
    if progress.get("Adventurer"):
        return
    if (player_char.location_x, player_char.location_y, player_char.location_z) != CHALICE_ADVENTURER_POS:
        return
    if not progress.get("Sergeant"):
        return
    progress["Adventurer"] = True
    quest_data["Help Text"] = "Inspect the Chalice Map to reveal where the hidden altar lies."
    sync_chalice_map_description(player_char)
    game.special_event("Chalice Adventurer")


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
        """Returns available move actions: moving forward and turning around."""
        if append_list is None:
            append_list = []

        moves = [actions_dict["TurnLeft"], actions_dict["TurnRight"], actions_dict["TurnAround"]]

        # Forward movement based on player's facing direction
        facing = player_char.facing
        dx, dy = DIRECTIONS[facing]["move"]
        new_pos = (self.x + dx, self.y + dy, self.z)

        # If moving forward is possible, add it
        tile = player_char.world_dict.get(new_pos)
        if tile and getattr(tile, "enter", False) and blocked != facing:
            moves.append(actions_dict["MoveForward"])

        moves.extend(append_list)
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


class LadderUp(MapTile):

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += (f"{game.player_char.name} sees a sturdy ladder leading up.\n"
                      f"(Enter 'u' to use)\n")
        return intro_str

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)

    def available_actions(self, player_char):
        return self.adjacent_moves(player_char, [actions_dict['StairsUp'], actions_dict['CharacterMenu']])


class LadderDown(MapTile):

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += (f"{game.player_char.name} sees a sturdy ladder leading down.\n"
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
        return []


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

    def modify_player(self, game, textbox=None):
        self.visited = True
        self.adjacent_visited(game.player_char)
        if self.z == REALM_OF_CAMBION_LEVEL:
            reveal_cambion_code_clue(game.player_char, (self.x, self.y, self.z))
        if game.player_char.cls in ['Warlock', 'Shadowcaster']:
            if game.player_char.familiar.race == 'Jinkin' and game.player_char.familiar.pro_level == 3:
                if not random.randint(0, int(20 - game.player_char.check_mod('luck', luck_factor=10))):
                    rand_item = items.random_item(self.z)
                    game.player_char.modify_inventory(rand_item, 1)
                    if textbox:
                        textbox.print_text_in_rectangle(f"{game.player_char.familiar.name} finds {rand_item.name} and gives it to {game.player_char.name}.")
        # Scale random encounter rate down if player greatly outlevels the area
        try:
            if hasattr(game.player_char, "player_level") and callable(game.player_char.player_level):
                player_level = game.player_char.player_level()
            else:
                player_level = game.player_char.level.level
        except Exception:
            player_level = 1

        expected_level = max(1, (self.z + 1) * 10)
        level_diff = max(0, player_level - expected_level)

        extra_roll = min(10, level_diff // 5)

        if all([not random.randint(0, 4 + extra_roll),
                self.enemy is None,
                game._random_combat]):
            self.enter_combat(game.player_char)

    def available_actions(self, player_char):
        if player_char.state == 'fight':
            action_list = ["Attack", "Use Item", "Flee"]
            if not player_char.abilities_suppressed():
                if player_char.usable_abilities("Spells"):
                    action_list.insert(1, "Cast Spell")
                if player_char.usable_abilities("Skills"):
                    action_list.insert(1, "Use Skill")
            action_list.insert(1, "Defend")
            if player_char.is_disarmed():
                action_list.insert(2, "Pickup Weapon")
            action_list = player_char.additional_actions(action_list)
            return action_list
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])

    def enter_combat(self, player_char):
        raise NotImplementedError


class EmptyCavePath(CavePath):
    """
    Cave Path with no random enemies
    """

    def modify_player(self, game, textbox=None):
        return super().modify_player(game, textbox)

    def enter_combat(self, player_char):
        pass


class CavePath0(CavePath):

    def modify_player(self, game, textbox=None, popup_class=None):
        super().modify_player(game, textbox=textbox)
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
                    if textbox:
                        textbox.print_text_in_rectangle(quest_message)
                    elif popup_class and game.presenter is not None:
                        # Pygame version - show quest notification as a popup
                        dungeon_bg = game.presenter.screen.copy()
                        popup = popup_class(game.presenter, quest_message, show_buttons=False)
                        popup.show(
                            background_draw_func=lambda: game.presenter.screen.blit(dungeon_bg, (0, 0)),
                            flush_events=True,
                            require_key_release=True,
                            min_display_ms=300
                        )
    def enter_combat(self, player_char):
        self.enemy = enemies.random_enemy('0')
        _apply_cambion_antimagic(self, player_char, self.enemy)
        player_char.state = 'fight'


class CavePath1(CavePath):

    def modify_player(self, game, textbox=None, popup_class=None):
        super().modify_player(game, textbox=textbox)
        if (self.x, self.y, self.z) == (8, 8, 1) and \
            "Rookie Mistake" in game.player_char.quest_dict['Side']:
            if not game.player_char.quest_dict['Side']['Rookie Mistake']['Completed']:
                game.special_event("Rookie")
                game.player_char.modify_inventory(items.DeadSoldier(), rare=True)
                quest_message = "You found the rookie! He's dead...\n"
                if textbox:
                    textbox.print_text_in_rectangle(quest_message)
                elif popup_class and game.presenter is not None:
                    # Pygame version - show quest notification as a popup
                    dungeon_bg = game.presenter.screen.copy()
                    popup = popup_class(game.presenter, quest_message, show_buttons=False)
                    popup.show(background_draw_func=lambda: game.presenter.screen.blit(dungeon_bg, (0, 0)))
                self.enter_combat(game.player_char)

    def enter_combat(self, player_char):
        self.enemy = enemies.random_enemy(str(self.z))
        _apply_cambion_antimagic(self, player_char, self.enemy)
        player_char.state = 'fight'


class CavePath2(CavePath):

    def enter_combat(self, player_char):
        self.enemy = enemies.random_enemy(str(self.z + 1))
        _apply_cambion_antimagic(self, player_char, self.enemy)
        player_char.state = 'fight'


class FunhouseEmptyPath(EmptyCavePath):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)


class FunhousePath(CavePath):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def enter_combat(self, player_char):
        self.enemy = enemies.funhouse_enemy()
        player_char.state = 'fight'


class FunhouseWall(FakeWall):
    """A deceptive wall tile that disorients the player when entered."""

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.blocked = None

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += f"{game.player_char.name} sees only endless reflections and twisted corridors.\n"
        intro_str += "Which way is forward?\n"
        return intro_str

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)
        # Disorient the player: reverse their facing direction
        reverse_map = {"north": "south", "south": "north", "east": "west", "west": "east"}
        original_facing = game.player_char.facing
        game.player_char.facing = reverse_map.get(original_facing, original_facing)

    def available_actions(self, player_char):
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])


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

    def modify_player(self, game, textbox=None):
        super().modify_player(game, textbox=textbox)
        if not game.player_char.flying:
            resist = game.player_char.check_mod("resist", typ="Fire")
            health_10per = max(0, int(game.player_char.health.max * 0.1 * (1 - resist)))
            damage = random.randint(health_10per // 2, health_10per)
            game.player_char.health.current -= damage
            if damage > 0:
                if textbox:
                    textbox.print_text_in_rectangle(
                        f"The heat sears {game.player_char.name}, dealing {damage} damage!"
                    )


class FirePathSpecial(FirePath):
    """
    Cacus summon can be obtained by Summoner class once Vulcan's Hammer is obtained
    """

    def modify_player(self, game, textbox=None):
        if "Vulcan's Hammer" in game.player_char.special_inventory:
            game.special_event("Cacus")
            summon = companions.Cacus()
            summon.initialize_stats(game.player_char)
            game.player_char.modify_inventory(items.BlacksmithsHammer(), subtract=True, rare=True)
            game.player_char.summons[summon.name] = summon
        else:
            super().modify_player(game, textbox=textbox)


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

    def modify_player(self, game, confirm_popup=None, textbox=None, battle_manager=None):
        """
        Handles player interaction with the underground spring. UI and combat logic must be provided by the frontend.
        Args:
            game: Game instance (for context)
            confirm_popup: Optional ConfirmPopupMenu UI component
            textbox: Optional TextBox UI component
            battle_manager: Optional callable/class for handling battles
        """
        self.visited = True
        player_char = game.player_char
        # UI hook: confirm with player about drinking from spring
        # UI hook: show quest completion message for Naivete
        if "Naivete" in player_char.quest_dict["Side"] and \
            not player_char.quest_dict["Side"]["Naivete"]["Completed"]:
            player_char.modify_inventory(items.EmptyVial(), subtract=True, rare=True)
            player_char.modify_inventory(items.SpringWater(), rare=True)
            player_char.quest_dict["Side"]["Naivete"]["Completed"] = True
            if textbox:
                textbox.print_text_in_rectangle(
                    "You fill the empty vial with water from the spring. "
                    "You feel a strange sense of clarity as you do so."
                )
        if confirm_popup and confirm_popup.navigate_popup():
            if player_char.level.pro_level > 1 and not random.randint(0, 1):
                if not self.defeated:
                    self.generate_enemy()
                    if self.enemy.is_alive():
                        game.special_event("Fuath1")
                        self.enter_combat(player_char)
                        if battle_manager:
                            battle_manager(game, self.enemy)
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
                if textbox:
                    textbox.print_text_in_rectangle(message)
                self.drink = True
            if not self.nimue and "Excaliper" in player_char.special_inventory:
                game.special_event("Nimue")
                player_char.modify_inventory(items.Excaliper(), subtract=True, rare=True)
                self.nimue = True
                # Track this as first meeting - don't offer quests yet
                if not hasattr(self, 'nimue_met_before'):
                    self.nimue_met_before = False
            
            if self.nimue:
                if "Excalibur" in player_char.inventory or \
                    "Excalibur" == player_char.equipment['Weapon'].name:
                    game.special_event("Excalibur")
                    if "Excalibur" in player_char.inventory:
                        player_char.modify_inventory(items.Excalibur2())
                        player_char.modify_inventory(items.Excalibur(), subtract=True)
                    else:
                        player_char.equipment['Weapon'] = items.Excalibur2()
                
                # Offer Nimue quests only on subsequent visits (curses UI)
                if textbox:
                    # Check if this is a return visit (not the first meeting)
                    if hasattr(self, 'nimue_met_before') and self.nimue_met_before:
                        # Import here to avoid circular dependency
                        from src.ui_curses import town as curses_town
                        quest, responses = curses_town.check_quests(game, "Nimue")
                        if not quest:
                            import random
                            response = random.choice(random.choice(responses))
                            textbox.print_text_in_rectangle(response)
                            textbox.clear_rectangle()
                    
                    # Mark that we've met Nimue before for next visit
                    self.nimue_met_before = True

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
            if not player_char.abilities_suppressed():
                if player_char.usable_abilities("Spells"):
                    action_list.insert(1, "Cast Spell")
                if player_char.usable_abilities("Skills"):
                    action_list.insert(1, "Use Skill")
            action_list.insert(1, "Defend")
            if player_char.is_disarmed():
                action_list.insert(2, "Pickup Weapon")
            action_list = player_char.additional_actions(action_list)
            return action_list
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])


class Boulder(SpecialTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enter = False

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

        quest_data = game.player_char.quest_dict.get("Side", {}).get(CHALICE_QUEST_NAME)
        progress = _ensure_chalice_progress(quest_data)
        if progress and progress.get("Hooded") and not progress.get("Map"):
            if self.read:
                game.special_event("Chalice Map")
                game.player_char.modify_inventory(items.ChaliceMap(), rare=True, quest=True)
                progress["Map"] = True
                sync_chalice_map_description(game.player_char)
                quest_data["Help Text"] = "Bring the map to the Sergeant at the barracks for help deciphering it."


class Portal(EmptyCavePath):
    """
    Returns player from the Realm of Cambion to the Underground Spring
    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += "A shimmering portal flickers here, reflecting impossible corridors in its surface.\n"
        return intro_str

    def modify_player(self, game):
        self.visited = True
        player_char = game.player_char
        self.adjacent_visited(player_char)
        reveal_cambion_code_clue(player_char, (self.x, self.y, self.z))
        pos = (self.x, self.y, self.z)
        if pos in CAMBION_PORTAL_MAP:
            destination = CAMBION_PORTAL_MAP[pos]
            player_char.previous_location = pos
            player_char.location_x, player_char.location_y, player_char.location_z = destination
            destination_tile = player_char.world_dict.get(destination)
            if destination_tile:
                destination_tile.visited = True
                destination_tile.adjacent_visited(player_char)
            _queue_cambion_message(player_char, "Space folds in on itself and spits you out elsewhere in the realm.")
            return
        return_to_underground_spring(player_char)


class Rotator(EmptyCavePath):
    """
    Spins the player around and pushes them into one of the adjacent enterable spaces
    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += "The floor hums beneath your feet, as if some hidden mechanism is waiting to trigger.\n"
        return intro_str

    def modify_player(self, game):
        self.visited = True
        player_char = game.player_char
        previous = getattr(player_char, "previous_location", None)
        reveal_cambion_code_clue(player_char, (self.x, self.y, self.z))

        options = _enterable_adjacent_positions(player_char.world_dict, self.x, self.y, self.z)
        if not options:
            self.adjacent_visited(player_char)
            return

        filtered = [entry for entry in options if entry[1] != previous]
        if filtered:
            options = filtered

        direction, destination = random.choice(options)
        player_char.previous_location = (self.x, self.y, self.z)
        player_char.facing = direction
        player_char.location_x, player_char.location_y, player_char.location_z = destination

        destination_tile = player_char.world_dict.get(destination)
        if destination_tile:
            destination_tile.visited = True
            destination_tile.adjacent_visited(player_char)
        _queue_cambion_message(player_char, "The room spins violently and throws you down a different passage.")


class Trap(EmptyCavePath):
    """
    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)

    def intro_text(self, game):
        return super().intro_text(game)

    def modify_player(self, game):
        super().modify_player(game)
        player_char = game.player_char
        reveal_cambion_code_clue(player_char, (self.x, self.y, self.z))
        damage = min(player_char.health.current - 1, random.randint(10, 28))
        if damage > 0:
            player_char.health.current -= damage
            _queue_cambion_message(player_char, f"A hidden trap snaps shut, dealing {damage} damage!")


class AntiMagicSwitch(EmptyCavePath):
    """
    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = None

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        if cambion_anti_magic_active(game.player_char):
            intro_str += "A humming terminal pulses here, bound to the realm's anti-magic field.\n"
        else:
            intro_str += "The terminal sits dark and silent. The anti-magic field is down.\n"
        return intro_str

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)

    def attempt_disable(self, game, code: str | None):
        player_char = game.player_char
        state = _ensure_cambion_state(player_char)
        if not state["anti_magic_active"]:
            _queue_cambion_message(player_char, "The terminal displays: SHIELD OFFLINE.")
            return True

        if str(code).strip() == CAMBION_SWITCH_CODE:
            disable_cambion_anti_magic(player_char)
            _queue_cambion_message(player_char, "The terminal accepts the code. The anti-magic field collapses.")
            return True

        state["alarm_count"] += 1
        self.enemy = CAMBION_ALARM_ENEMY()
        _apply_cambion_antimagic(self, player_char, self.enemy)
        player_char.state = "fight"
        _queue_cambion_message(player_char, "The terminal flashes red. An alarm sounds and a guardian attacks!")
        return False


class BossRoom(SpecialTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = None
        self.defeated = False

    def available_actions(self, player_char):
        if player_char.state == 'fight':
            action_list = ["Attack", "Use Item"]
            if not player_char.abilities_suppressed():
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
        if self.z == REALM_OF_CAMBION_LEVEL:
            reveal_cambion_code_clue(game.player_char, (self.x, self.y, self.z))
        if not self.defeated:
            self.generate_enemy()
            if self.enemy.is_alive():
                self.enter_combat(game.player_char)

    def enter_combat(self, player_char):
        _apply_cambion_antimagic(self, player_char, self.enemy)
        player_char.state = 'fight'

    def special_text(self, game):
        if not self.read:
            enemy_instance = self.enemy if isinstance(self.enemy, str) else (self.enemy() if callable(self.enemy) else self.enemy)
            enemy_name = enemy_instance.name if hasattr(enemy_instance, 'name') else str(enemy_instance)
            game.special_event(enemy_name)
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
        self.tokens_required = 4

    def intro_text(self, game):
        if not self.enemy:
            return "The twisted carnival around you suddenly snaps back to reality. You have vanquished the Jester.\n"
        return super().intro_text(game)
    
    def modify_player(self, game):
        """Check for tokens before allowing combat with Jester."""
        self.visited = True
        self.adjacent_visited(game.player_char)
        
        # Count Jester Tokens in inventory
        token_count = len([item for items in game.player_char.inventory.values() for item in items 
                          if hasattr(item, 'name') and item.name == "Jester Token"])
        
        if token_count < self.tokens_required:
            # Not enough tokens - turn player away
            msg = f"The Jester emerges from the shadows, blocking your path.\n"
            msg += f"'Not ready yet, carnival wanderer! Return when you've collected more of my tokens.'\n"
            msg += f"Tokens collected: {token_count}/{self.tokens_required}\n"
            if hasattr(game, 'add_message'):
                game.add_message(msg)
            return
        
        # Enough tokens - proceed with normal combat startup
        if not self.defeated:
            self.generate_enemy()
            if self.enemy.is_alive():
                self.enter_combat(game.player_char)
    
    def special_text(self, game):
        """Handle victory condition and exit the funhouse."""
        if not self.enemy and game.player_char.location_z == 7:
            # Jester defeated - exit the funhouse
            game.player_char.exit_funhouse()
            if hasattr(game, 'special_event'):
                game.special_event("Jester Defeated")
        else:
            super().special_text(game)


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


class CirceBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Circe

    def intro_text(self, game):
        if not self.enemy:
            return ("")
        return super().intro_text(game)


class MerzhinBossRoom(BossRoom):
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Merzhin

    def intro_text(self, game):
        if not self.enemy:
            return ("Merzhin's illusions have collapsed, leaving only the fading hush of the realm.\n")
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
        self.enter = False
        self.generate_loot()  # Generate loot when chest is created

    def available_actions(self, player_char):
        raise NotImplementedError

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)
        self.generate_loot()

    def generate_loot(self):
        """Generate random loot for the chest if not already generated."""
        if self.loot is None:
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
                if not player_char.abilities_suppressed():
                    if player_char.usable_abilities("Spells"):
                        action_list.insert(1, "Cast Spell")
                    if player_char.usable_abilities("Skills"):
                        action_list.insert(1, "Use Skill")
                action_list.insert(1, "Defend")
                if player_char.is_disarmed():
                    action_list.insert(2, "Pickup Weapon")
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
                if not player_char.abilities_suppressed():
                    if player_char.usable_abilities("Spells"):
                        action_list.insert(1, "Cast Spell")
                    if player_char.usable_abilities("Skills"):
                        action_list.insert(1, "Use Skill")
                action_list.insert(1, "Defend")
                if player_char.is_disarmed():
                    action_list.insert(2, "Pickup Weapon")
                action_list = player_char.additional_actions(action_list)
                return action_list
            return self.adjacent_moves(player_char, [actions_dict['Open'], actions_dict['CharacterMenu']])
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])

    def modify_player(self, game, confirm_popup=None, textbox=None):
        """
        Handles player interaction with a locked chest. UI logic must be provided by the frontend.
        Args:
            game: Game instance (for context)
            confirm_popup: Optional ConfirmPopupMenu UI component
            textbox: Optional TextBox UI component
        """
        self.visited = True
        self.adjacent_visited(game.player_char)
        self.generate_loot()
        if self.locked:
            # UI hook: prompt player to unlock chest (Master Key, lockpick, or Key)
            # UI hook: show unlock success/failure messages
            if "Master Key" in game.player_char.special_inventory:
                self.locked = False
                if textbox:
                    textbox.print_text_in_rectangle("You open the chest with the Master key.\n")
            elif any(["Lockpick" in game.player_char.spellbook["Skills"],
                      "Master Lockpick" in game.player_char.spellbook["Skills"]]):
                self.locked = False
                if textbox:
                    textbox.print_text_in_rectangle(f"{game.player_char.name} skillfully unlocks the chest.\n")
            elif "Key" in game.player_char.inventory and confirm_popup and confirm_popup.navigate_popup():
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

    def modify_player(self, game, confirm_popup=None, textbox=None):
        """
        Handles player interaction with a locked door. UI logic must be provided by the frontend.
        Args:
            game: Game instance (for context)
            confirm_popup: Optional ConfirmPopupMenu UI component
            textbox: Optional TextBox UI component
        """
        self.visited = True
        self.which_blocked(game)
        self.adjacent_visited(game.player_char)
        # If door is already open, no need to unlock it
        if self.open:
            return
        if self.locked:
            # UI hook: prompt player to unlock door (Master Key, lockpick, or Old Key)
            # UI hook: show unlock success/failure messages
            if "Master Key" in game.player_char.special_inventory:
                self.locked = False
                if textbox:
                    textbox.print_text_in_rectangle("You open the door with the Master key.\n")
            elif 'Master Lockpick' in game.player_char.spellbook['Skills']:
                self.locked = False
                if textbox:
                    textbox.print_text_in_rectangle(f"{game.player_char.name} skillfully unlocks the chest.\n")
            elif "Old Key" in game.player_char.inventory and confirm_popup and confirm_popup.navigate_popup():
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


class OreVaultDoor(Wall):
    """
    Hidden door that blocks access to the Unobtainium vault.
    Appears as a regular wall unless the player has Keen Eye skill or the Cryptic Key.
    Can only be unlocked with the Cryptic Key, Master Key, or Master Lockpick.
    """

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.open = False
        self.locked = True
        self.blocked = None
        self.enter = False  # Starts as impassable wall
        self.detected = False  # Track if player has detected the hidden door

    def intro_text(self, game):
        intro_str = ""
        # Call grandparent MapTile intro_text for Keen Eye check
        intro_str += MapTile.intro_text(self, game)
        
        # Door is open - can pass through
        if self.open:
            intro_str += "The secret vault door stands open.\n"
            return intro_str
        
        # Check if player can perceive the hidden door
        has_keen_eye = 'Keen Eye' in game.player_char.spellbook['Skills']
        has_cryptic_key = "Cryptic Key" in game.player_char.inventory
        
        # Only reveal and mark as detected if player has the means to see it
        if has_cryptic_key:
            # Key glows in presence of the door
            self.detected = True
            intro_str += "The Cryptic Key in your possession begins to glow warmly.\n"
            intro_str += "You notice faint seams in the wall... a hidden door!\n"
        elif has_keen_eye:
            # Keen perception reveals the door
            self.detected = True
            intro_str += f"{game.player_char.name}'s keen eye spots something unusual in the wall.\n"
            intro_str += "The stone here doesn't quite match... it's a hidden door!\n"
        else:
            # Reset detected status if player no longer has the means to see it
            self.detected = False
        # Otherwise appears as a normal wall (no text)
        
        return intro_str

    def modify_player(self, game, confirm_popup=None, textbox=None):
        """
        Handles player interaction with the Ore Vault hidden door. UI logic must be provided by the frontend.
        Args:
            game: Game instance (for context)
            confirm_popup: Optional ConfirmPopupMenu UI component
            textbox: Optional TextBox UI component
        """
        self.visited = True
        self.which_blocked(game)
        self.adjacent_visited(game.player_char)
        
        # If door hasn't been detected, treat it like a wall - no interaction
        has_cryptic_key = "Cryptic Key" in game.player_char.inventory
        has_keen_eye = 'Keen Eye' in game.player_char.spellbook['Skills']
        
        if not (has_cryptic_key or has_keen_eye or self.open):
            # Door is not detected and not open - act like a wall, do nothing
            return
        
        # If door is already open, allow passage
        if self.open:
            self.enter = True
            return
        
        # If locked, check for ways to unlock
        if self.locked:
            # UI hook: prompt player to unlock hidden door (Cryptic Key, Master Key, or Master Lockpick)
            # UI hook: show unlock success/failure messages
            if "Cryptic Key" in game.player_char.inventory and confirm_popup and confirm_popup.navigate_popup():
                self.locked = False
                self.open = True
                self.enter = True
                if textbox:
                    textbox.print_text_in_rectangle("The Cryptic Key turns smoothly in the hidden lock.\nThe door swings open, revealing the vault beyond!\n")
                game.player_char.modify_inventory(game.player_char.inventory['Cryptic Key'][0], subtract=True)
            elif "Master Key" in game.player_char.special_inventory and 'Keen Eye' in game.player_char.spellbook['Skills'] and confirm_popup and confirm_popup.navigate_popup():
                self.locked = False
                self.open = True
                self.enter = True
                if textbox:
                    textbox.print_text_in_rectangle("You open the hidden door with the Master Key.\n")
            elif 'Master Lockpick' in game.player_char.spellbook['Skills'] and 'Keen Eye' in game.player_char.spellbook['Skills'] and confirm_popup and confirm_popup.navigate_popup():
                self.locked = False
                self.open = True
                self.enter = True
                if textbox:
                    textbox.print_text_in_rectangle(f"{game.player_char.name} skillfully unlocks the hidden door.\n")

    def available_actions(self, player_char):
        # If open, allow normal movement
        if self.open:
            return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])
        # If closed, acts like a wall (blocks movement)
        return []

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

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)
        self.warning = True

    def enter_combat(self, player_char):
        # If locked, check for ways to unlock
        if self.locked:
            # UI hook: prompt player to unlock chest (Master Key, lockpick, or Key)
            # UI hook: show unlock success/failure messages
            pass
            

class UnobtainiumRoom(SpecialTile):

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        return intro_str

    def modify_player(self, game):
        # Reveal nearby tiles but leave the ore to be looted manually
        self.adjacent_visited(game.player_char)

    def special_text(self, game):
        if not self.read:
            game.special_event("Unobtainium")
            self.read = True
            

class RelicRoom(SpecialTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enter = False

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        intro_str += "An empty altar stands in the center of the room.\n"
        return intro_str

    def modify_player(self, game):
        self.adjacent_visited(game.player_char)
        self.visited = True

    def special_text(self, game, textbox=None):
        if not self.read:
            game.special_event("Relic Room")
            relics = [items.Relic1(), items.Relic2(), items.Relic3(), items.Relic4(), items.Relic5(), items.Relic6()]
            game.player_char.modify_inventory(relics[game.player_char.location_z - 1], rare=True, quest=True)
            self.read = True
            if textbox:
                textbox.print_text_in_rectangle("Your health and mana have been restored to full!\n")
            game.player_char.health.current = game.player_char.health.max
            game.player_char.mana.current = game.player_char.mana.max
            game.player_char.quests()
            if textbox:
                textbox.clear_rectangle()


class IncubusLair(BossRoom):
    """Encounter with the Incubus (father of Merzhin) - required for Oedipal Complex quest."""
    
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = enemies.Incubus
        self.defeated = False

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        # Check if quest is active
        if "Oedipal Complex" in game.player_char.quest_dict.get("Side", {}):
            if not game.player_char.quest_dict["Side"]["Oedipal Complex"]["Completed"]:
                intro_str += "A deep, primal presence emanates from the shadows. Eyes glow red in the darkness.\n"
            else:
                intro_str += "The faint charred remains of a demonic entity scatter the floor.\n"
        else:
            intro_str += "The air here feels heavy and oppressive.\n"
        return intro_str

    def modify_player(self, game):
        self.adjacent_visited(game.player_char)
        self.visited = True
        quest_data = game.player_char.quest_dict.get("Side", {}).get("Oedipal Complex")
        if not quest_data:
            return
        if quest_data.get("Completed") or self.defeated:
            return
        if game.player_char.state == "fight":
            return

        # Spawn and enter combat only when the quest is active/incomplete.
        self.generate_enemy()
        if self.enemy and self.enemy.is_alive():
            self.enter_combat(game.player_char)

    def special_text(self, game):
        # Only trigger if quest is active and not yet completed
        if "Oedipal Complex" in game.player_char.quest_dict.get("Side", {}):
            if not game.player_char.quest_dict["Side"]["Oedipal Complex"]["Completed"]:
                if not self.defeated:
                    return "The Incubus emerges from the shadows to challenge you!"
        return ""

    def enter_combat(self, player_char):
        player_char.state = "fight"

    def defeat_incubus(self, game):
        """Complete the Oedipal Complex quest when Incubus is defeated."""
        if "Oedipal Complex" in game.player_char.quest_dict.get("Side", {}):
            if not game.player_char.quest_dict["Side"]["Oedipal Complex"]["Completed"]:
                game.player_char.quest_dict["Side"]["Oedipal Complex"]["Completed"] = True
                game.special_event("Incubus Defeated")
                self.defeated = True
                self.enter = False
                return True
        return False

    def available_actions(self, player_char):
        if player_char.state == 'fight':
            action_list = ["Attack", "Use Item"]
            if not player_char.abilities_suppressed():
                if player_char.usable_abilities("Spells"):
                    action_list.insert(1, "Cast Spell")
                if player_char.usable_abilities("Skills"):
                    action_list.insert(1, "Use Skill")
            action_list = player_char.additional_actions(action_list)
            return action_list
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])


class GoldenChaliceRoom(SpecialTile):
    """Location of the Golden Chalice - required for The Holy Grail of Quests."""
    
    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        # Hidden altar locations behave like an ordinary floor tile until revealed.
        self.enter = True

    @staticmethod
    def _altar_visible_for(player_char) -> bool:
        return chalice_altar_visible(player_char)

    def intro_text(self, game):
        self.enter = not self._altar_visible_for(game.player_char)
        intro_str = super().intro_text(game)
        if "The Holy Grail of Quests" in game.player_char.quest_dict.get("Side", {}):
            if not game.player_char.quest_dict["Side"]["The Holy Grail of Quests"]["Completed"]:
                intro_str += "A golden chalice filled with a mysterious liquid sits on a pedestal, glowing faintly.\n"
            else:
                intro_str += "An empty pedestal stands where the chalice once rested.\n"
        else:
            intro_str += "A golden chalice sits on a pedestal, but something feels... forbidden about disturbing it.\n"
        return intro_str

    def modify_player(self, game):
        self.enter = not self._altar_visible_for(game.player_char)
        self.adjacent_visited(game.player_char)
        self.visited = True

    def special_text(self, game):
        self.enter = not self._altar_visible_for(game.player_char)
        # Only allow pickup if quest is active
        if "The Holy Grail of Quests" in game.player_char.quest_dict.get("Side", {}):
            if not game.player_char.quest_dict["Side"]["The Holy Grail of Quests"]["Completed"]:
                return "The chalice is yours to take!"
            return ""
        return "An invisible force prevents you from taking the chalice."

    def pickup_chalice_action(self, game):
        """Actually pick up the chalice when player confirms."""
        self.enter = not self._altar_visible_for(game.player_char)
        if "The Holy Grail of Quests" in game.player_char.quest_dict.get("Side", {}):
            if not game.player_char.quest_dict["Side"]["The Holy Grail of Quests"]["Completed"]:
                game.special_event("Golden Chalice")
                game.player_char.modify_inventory(items.GoldenChalice(), rare=True, quest=True)
                game.player_char.quest_dict["Side"]["The Holy Grail of Quests"]["Completed"] = True
                self.read = True
                self.enter = False
                return True
        return False


class DeadBody(SpecialTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enemy = None
        self.defeated = False

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
        if 'Something to Cry About' in game.player_char.quest_dict['Side'] and not self.defeated:
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
            if not player_char.abilities_suppressed():
                if player_char.usable_abilities("Spells"):
                    action_list.insert(1, "Cast Spell")
                if player_char.usable_abilities("Skills"):
                    action_list.insert(1, "Use Skill")
            action_list.insert(1, "Defend")
            if player_char.is_disarmed():
                action_list.insert(2, "Pickup Weapon")
            action_list.insert(1, "Defend")
            if player_char.is_disarmed():
                action_list.insert(2, "Pickup Weapon")
            action_list.insert(1, "Defend")
            if player_char.is_disarmed():
                action_list.insert(2, "Pickup Weapon")
            action_list.insert(1, "Defend")
            if player_char.is_disarmed():
                action_list.insert(2, "Pickup Weapon")
            action_list.insert(1, "Defend")
            if player_char.is_disarmed():
                action_list.insert(2, "Pickup Weapon")
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

    def available_actions(self, player_char):
        """Return combat actions for the final boss."""
        action_list = ["Attack", "Use Item", "Flee"]
        if not player_char.abilities_suppressed():
            if player_char.usable_abilities("Spells"):
                action_list.insert(1, "Cast Spell")
            if player_char.usable_abilities("Skills"):
                action_list.insert(1, "Use Skill")
        return action_list

    def special_text(self, game):
        fight = game.special_event("Final Boss")
        if fight:
            game.player_char.move_north()
            game.player_char.move_north()
        else:
            game.player_char.move_south()


class SecretShop(SpecialTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.enter = False  # Cannot enter - interact from adjacent space

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
        return []


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
        return []

    def special_text(self, game):
        if not self.read:
            game.special_text("Ultimate Armor")
            self.read = True


class WarpPoint(MapTile):

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.warped = False

    def modify_player(self, game, confirm_popup=None):
        """
        Handles player interaction with the warp point. UI logic must be provided by the frontend.
        Args:
            game: Game instance (for context)
            confirm_popup: Optional ConfirmPopupMenu UI component
        """
        if not game.player_char.warp_point:
            self.visited = True
            self.adjacent_visited(game.player_char)
            return
        if not self.warped:
            if confirm_popup and confirm_popup.navigate_popup():
                game.player_char.to_town()
                town.town(game)
                return
        self.warped = False
        self.visited = True
        self.adjacent_visited(game.player_char)

    def available_actions(self, player_char):
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])


class FunhouseTeleporter(SpecialTile):

    def modify_player(self, game):
        self.visited = True
        self.adjacent_visited(game.player_char)

        # Already in the funhouse; no further teleporting needed.
        if game.player_char.location_z == 7:
            return

        # Save return point for potential future exit logic.
        game.player_char.funhouse_return = (
            game.player_char.location_x,
            game.player_char.location_y,
            game.player_char.location_z,
            game.player_char.facing,
        )

        # Move player into the dedicated funhouse challenge level (level 4 boss area).
        game.player_char.location_x = 0
        game.player_char.location_y = 9
        game.player_char.location_z = 7
        game.player_char.facing = "north"
        
        # Trigger funhouse entry special event
        game.special_event("Funhouse Entry")

class FunhouseMimicChest(ChestRoom):
    """A special chest for the funhouse that guarantees a Mimic encounter and drops a Jester Token."""

    def __init__(self, x, y, z):
        super().__init__(x, y, z)
        self.locked = False
        self.enemy = None

    def intro_text(self, game):
        intro_str = super().intro_text(game)
        if not self.open:
            intro_str += f"{game.player_char.name} finds a peculiar chest adorned with strange patterns. (Enter 'o' to open)\n"
        else:
            intro_str += "This chest has already been opened.\n"
        return intro_str

    def available_actions(self, player_char):
        if not self.open:
            if player_char.state == 'fight':
                action_list = ["Attack", "Use Item", "Flee"]
                if not player_char.abilities_suppressed():
                    if player_char.usable_abilities("Spells"):
                        action_list.insert(1, "Cast Spell")
                    if player_char.usable_abilities("Skills"):
                        action_list.insert(1, "Use Skill")
                action_list.insert(1, "Defend")
                if player_char.is_disarmed():
                    action_list.insert(2, "Pickup Weapon")
                action_list = player_char.additional_actions(action_list)
                return action_list
            return self.adjacent_moves(player_char, [actions_dict['Open'], actions_dict['CharacterMenu']])
        return self.adjacent_moves(player_char, [actions_dict['CharacterMenu']])

    def generate_loot(self):
        """Generate level 4 loot for the funhouse chest (not scaled to z=7)."""
        if self.loot is None:
            # Generate loot at level 4 difficulty (not at zone level)
            self.loot = items.random_item(4)
