"""Interactive and Realm of Cambion map tiles."""

import random

from .. import companions, enemies, items
from ..classes import dragoon
from ..player import actions_dict
from .paths import EmptyCavePath, SpecialTile
from .rules import (
    CAMBION_ALARM_ENEMY,
    CAMBION_PORTAL_FLAVOR,
    CAMBION_PORTAL_MAP,
    CAMBION_ROTATOR_FLAVOR,
    CAMBION_SWITCH_CODE,
    CHALICE_QUEST_NAME,
    _apply_cambion_antimagic,
    _ensure_cambion_state,
    _ensure_chalice_progress,
    _enterable_adjacent_positions,
    _queue_cambion_message,
    cambion_anti_magic_active,
    disable_cambion_anti_magic,
    nature_communion_text,
    return_to_underground_spring,
    reveal_cambion_code_clue,
    sync_chalice_map_description,
)


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
        water_message = nature_communion_text(player_char, "Water")
        if water_message and textbox:
            textbox.print_text_in_rectangle(water_message)
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
        earth_message = nature_communion_text(game.player_char, "Earth")
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
        return earth_message


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
            _queue_cambion_message(
                player_char,
                CAMBION_PORTAL_FLAVOR.get(
                    pos,
                    "Space folds in on itself and spits you out elsewhere in the realm.",
                ),
            )
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
        _queue_cambion_message(player_char, CAMBION_ROTATOR_FLAVOR[cambion_anti_magic_active(player_char)])


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

    def has_kaelenon_branch(self, game):
        return dragoon.has_pending_terminal_branch(game.player_char)

    def resolve_kaelenon_branch(self, game):
        message = dragoon.resolve_terminal_branch(game.player_char)
        if message:
            _queue_cambion_message(game.player_char, message)
            return True
        return False

    def attempt_disable(self, game, code: str | None):
        player_char = game.player_char
        if self.resolve_kaelenon_branch(game):
            return True
        state = _ensure_cambion_state(player_char)
        if not state["anti_magic_active"]:
            _queue_cambion_message(player_char, "The terminal displays: SHIELD OFFLINE. The realm feels less certain without its hum.")
            return True

        if str(code).strip() == CAMBION_SWITCH_CODE:
            disable_cambion_anti_magic(player_char)
            _queue_cambion_message(
                player_char,
                "The terminal accepts the code. The anti-magic field collapses, and distant portals flare in reply.",
            )
            return True

        state["alarm_count"] += 1
        self.enemy = CAMBION_ALARM_ENEMY()
        _apply_cambion_antimagic(self, player_char, self.enemy)
        player_char.state = "fight"
        _queue_cambion_message(player_char, "The terminal flashes red. An alarm sounds and a guardian attacks!")
        return False
