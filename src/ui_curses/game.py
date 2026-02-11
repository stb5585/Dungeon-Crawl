"""
The main module to run the Dungeon Crawl game (Curses version).
"""

import sys
import time

import curses

from src.core import abilities, items, player
from src.core.character import Combat, Level, Resource, Stats
from src.core.classes import classes_dict
from src.core.data.data_loader import get_special_events
from src.core.races import races_dict
from src.core.save_system import SaveManager
from src.core.town import BountyBoard
from . import menus, town
from .battle import BattleManager
from .enhanced_manager import EnhancedBattleManager

# Feature flag: Set to True to use enhanced combat with action queue
USE_ENHANCED_COMBAT = True


# objects
class Game:
    """Game object that contains all of the necessary details

    Args:
        stdscr
        debug_mode (optional, bool)
        load_files
        races_dict
        classes_dict
        player_char
        bounties
        _random_combat
        _time
        _difficulty_rating
    """

    def __init__(self, stdscr, debug_mode=False):
        self.stdscr = stdscr
        self.debug_mode = debug_mode
        self.load_files = SaveManager.list_saves()
        self.races_dict = races_dict
        self.classes_dict = classes_dict
        self.player_char = None
        self.bounties = {}
        self._random_combat = True
        self._time = time.time()
        self._difficulty_rating = None
        curses.curs_set(0)  # Hide cursor
        self.main_menu()

    def main_menu(self):
        menu = menus.MainMenu(self)
        menu.erase()
        if self.debug_mode:
            confirm_str = "You are in debug mode. Do you want to turn off random encounters?"
            confirm = menus.ConfirmPopupMenu(self, confirm_str, box_height=8)
            if confirm.navigate_popup():
                self._random_combat = False
        menu_options = ['New Game', 'Settings', 'Exit']
        if self.load_files:
            menu_options.insert(1, "Load Game")
        menu.update_options(menu_options)
        while True:
            while True:
                selected_idx = menu.navigate_menu()
                menu.erase()
                if menu_options[selected_idx] == 'New Game':
                    self.player_char = self.new_game()
                elif menu_options[selected_idx] == 'Load Game':
                    self.player_char = self.load_game(menu)
                elif menu_options[selected_idx] == 'Settings':
                    """
                    Settings to include
                    - special text print speed
                    - difficulty level
                        - _difficulty_rating
                    - hardcore mode (perma-death)
                    - 
                    """
                    pass
                else:
                    sys.exit(0)  # Exit the game
                if self.player_char:
                    break
            self.run()
            self.update_loadfiles()
            if self.load_files and "Load Game" not in menu_options:
                menu_options.insert(1, "Load Game")
            menu.update_options(menu_options)

    def update_loadfiles(self):
        self.load_files = SaveManager.list_saves()

    def debug_level_up(self):
        """Debug-only shortcut to trigger a single level-up."""
        if not self.debug_mode or not self.player_char:
            return
        if self.player_char.max_level():
            textbox = menus.TextBox(self)
            textbox.print_text_in_rectangle("Already at max level.")
            self.stdscr.getch()
            textbox.clear_rectangle()
            return
        textbox = menus.TextBox(self)
        stat_menu = menus.SelectionPopupMenu(
            self,
            "Pick the stat you would like to increase.",
            [f'Strength - {self.player_char.stats.strength}',
             f'Intelligence - {self.player_char.stats.intel}',
             f'Wisdom - {self.player_char.stats.wisdom}',
             f'Constitution - {self.player_char.stats.con}',
             f'Charisma - {self.player_char.stats.charisma}',
             f'Dexterity - {self.player_char.stats.dex}'],
            box_height=12,
            confirm=False
        )
        self.player_char.level_up(self, textbox=textbox, menu=stat_menu)

    def run(self):
        self.update_bounties()
        while not self.player_char.quit:
            self.player_char.encumbered = self.player_char.current_weight() > self.player_char.max_weight()
            if time.time() - self._time > (900 * self.player_char.level.pro_level):
                self.update_bounties()
            if self.player_char.in_town():
                self.player_char.town_heal()
                town.town(self)
            else:
                self.navigate()

    def new_game(self):
        time.sleep(0.5)
        texts = [
            "A great evil has taken hold in the unlikeliest of places, a small town on the edge of the kingdom.",
            "The town of Silvana has sent out a plea for help, with many coming from far and wide to test their mettle.",
            "You, bright-eyed and bushy-tailed, decided that fame and glory were within reach.",
            "What you didn't know was that all who had attempted this feat have never been heard from again.",
            "Will you be different or just another lost soul?",
        ]
        if not self.debug_mode:
            texts_pad = menus.QuestPopupMenu(self, box_height=len(texts)+2, box_width=len(max(texts, key=len))+4)
            texts_pad.draw_popup(texts)
            self.stdscr.getch()

        # Select the race of the character
        menu = menus.NewGameMenu(self)
        while True:
            menu.update_options()
            while True:
                race = menu.navigate_menu()
                if not race:
                    return
                else:
                    confirm_str = f"Are you sure you want to play as a {race.name.lower()}?"
                    confirm = menus.ConfirmPopupMenu(self, confirm_str, box_height=7)
                    if confirm.navigate_popup():
                        break
                    menu.page = 1
            
            # Select the class of the character
            menu.update_options()
            while True:
                cls = menu.navigate_menu()
                if not cls:
                    break
                confirm_str = f"Are you sure you want to play as a {cls.name.lower()}?"
                confirm = menus.ConfirmPopupMenu(self, confirm_str, box_height=7)
                if confirm.navigate_popup():
                    break
            if cls:
                break
            if menu.options_list[menu.current_option] == "Go Back":
                return

        enternamebox = menus.TextBox(self)
        while True:
            name_message = "What is your character's name?"
            name = menus.player_input(self, name_message).capitalize()
            if not name:
                if not self.debug_mode:
                    enternamebox.print_text_in_rectangle("Name cannot be empty.")
                    self.stdscr.getch()
                    enternamebox.clear_rectangle()
                else:
                    name = "Test"
                    break
            else:
                menu.erase()
                confirm_str = f"Are you sure you want to name your character {name}?"
                confirm = menus.ConfirmPopupMenu(self, confirm_str, box_height=7)
                if confirm.navigate_popup():
                    break
        menu.erase()

        created = f"Welcome {name}, the {race.name} {cls.name}.\nReport to the barracks for your orders."
        enternamebox.print_text_in_rectangle(created)
        enternamebox.clear_rectangle()

        # Define the player character
        location_x, location_y, location_z = (5, 10, 0)
        stats = tuple(map(lambda x, y: x + y, (race.strength, race.intel, race.wisdom, race.con, race.charisma, race.dex),
                        (cls.str_plus, cls.int_plus, cls.wis_plus, cls.con_plus, cls.cha_plus, cls.dex_plus)))
        hp = stats[3] * 2  # starting HP equal to constitution x 2
        mp = stats[1] * 2  # starting MP equal to intel x 2
        attack = race.base_attack + cls.att_plus
        defense = race.base_defense + cls.def_plus
        magic = race.base_magic + cls.magic_plus
        magic_def = race.base_magic_def + cls.magic_def_plus
        gold = stats[4] * 25  # starting gold equal to charisma x 25
        player_char = player.Player(location_x, location_y, location_z, level=Level(),
                            health=Resource(hp, hp), mana=Resource(mp, mp),
                            stats=Stats(stats[0], stats[1], stats[2], stats[3], stats[4], stats[5]),
                            combat=Combat(attack=attack, defense=defense, magic=magic, magic_def=magic_def),
                            gold=gold, resistance=race.resistance)
        player_char.name = name
        player_char.race = race
        player_char.cls = cls
        player_char.equipment = cls.equipment
        if "1" in abilities.spell_dict[cls.name]:
            spell_gain = abilities.spell_dict[cls.name]["1"]()
            player_char.spellbook['Spells'][spell_gain.name] = spell_gain
        player_char.storage["Health Potion"] = [items.HealthPotion() for _ in range(5)]  # care package
        player_char.load_tiles()

        return player_char

    def load_game(self, menu):
        player_char = None
        load_options = []
        for f in self.load_files:
            load_options.append(f.split(".")[0].capitalize())
        load_options.append("Go Back")
        menu = menus.LoadGameMenu(self, load_options)
        selected_idx = menu.navigate_menu()
        if load_options[selected_idx] == "Go Back":
            return
        menus.save_file_popup(self, load=True)
        filename = self.load_files[selected_idx]
        player_char = SaveManager.load_player(filename)
        if player_char is None:
            return
        
        # Reset state to normal when loading to prevent immediate combat
        player_char.state = 'normal'
        # Clear enemy from current room if any
        current_room = player_char.world_dict.get(
            (player_char.location_x, player_char.location_y, player_char.location_z)
        )
        if current_room and hasattr(current_room, 'enemy'):
            current_room.enemy = None
        
        # Clear screen after loading to ensure clean state
        self.stdscr.clear()
        self.stdscr.refresh()

        return player_char

    def navigate(self):
        room = self.player_char.world_dict[
            (self.player_char.location_x, self.player_char.location_y, self.player_char.location_z)
            ]
        try:
            room.special_text(self)
        except AttributeError:
            pass
        room.modify_player(self)
        if self.player_char.in_town() or "Shop" in str(room):
            return
        dmenu = menus.DungeonMenu(self)
        dmenu.draw_all()
        dmenu.refresh_all()
        while True:
            # Update room reference in case player moved
            room = self.player_char.world_dict[
                (self.player_char.location_x, self.player_char.location_y, self.player_char.location_z)
                ]
            if self.player_char.in_town() or self.player_char.quit:
                return
            available_actions = room.available_actions(self.player_char)
            if self.player_char.state == "normal":
                room.enemy = None
                action_input = self.stdscr.getch()
                if self.debug_mode and action_input in [ord('l'), ord('L')]:
                    self.debug_level_up()
                    dmenu.draw_all()
                    dmenu.refresh_all()
                    continue
                for action in available_actions:
                    available_hotkeys = [x['hotkey'] for x in available_actions]
                    try:
                        if chr(action_input).lower() == action['hotkey']:
                            # Special handling for Character Menu
                            if action['name'] == 'Character Menu':
                                from src.core.player import actions_dict
                                char_menu = menus.CharacterMenu(self)
                                ui_factory = {
                                    'InventoryPopup': menus.InventoryPopupMenu,
                                    'ConfirmPopup': menus.ConfirmPopupMenu,
                                    'TextBox': menus.TextBox,
                                    'Popup': menus.PopupMenu,
                                    'EquipmentPopup': menus.EquipPopupMenu,
                                    'SpecialsPopup': menus.AbilitiesPopupMenu,
                                    'QuestsPopup': menus.QuestListPopupMenu,
                                    'JumpModsPopup': menus.JumpModsPopupMenu
                                }
                                action['method'](self.player_char, self, menu=char_menu, textbox=menus.TextBox(self), actions_dict=actions_dict, ui_factory=ui_factory)
                            else:
                                # Try calling with game parameter first, fall back to without
                                try:
                                    action['method'](self.player_char, self)
                                except TypeError:
                                    action['method'](self.player_char)
                            if chr(action_input).lower() in available_hotkeys and \
                                ("Move" in action['name'] or "Open" in action['name'] or "stairs" in action['name']):
                                return
                    except TypeError:
                        pass
            else:
                while True:
                    key = self.stdscr.getch()
                    if key == curses.KEY_ENTER or key in [10, 13]:
                        break
                # Create UI components for battle
                battle_ui = menus.CombatMenu(self)
                battle_popup = menus.CombatPopupMenu(self)
                textbox = menus.TextBox(self)
                
                if USE_ENHANCED_COMBAT:
                    battle = EnhancedBattleManager(self, room.enemy, use_queue=True,
                                                   battle_ui=battle_ui, battle_popup=battle_popup, textbox=textbox)
                else:
                    battle = BattleManager(self, room.enemy,
                                          battle_ui=battle_ui, battle_popup=battle_popup, textbox=textbox)
                flee = battle.execute_battle()
                if flee:
                    return
            dmenu.draw_all()
            dmenu.refresh_all()

    def update_bounties(self):
        self.bounties = {}
        bounties = BountyBoard()
        bounties.generate_bounties(self)
        for bounty in bounties.bounties:
            self.bounties[bounty["enemy"].name] = bounty

    def delete_bounty(self, bounty):
        del self.bounties[bounty["enemy"].name]

    def special_event(self, name):
        special_event_dict = get_special_events()
        text = special_event_dict[name]["Text"]
        pad = menus.QuestPopupMenu(self, box_height=len(text)+2, box_width=len(max(text, key=len))+4)
        pad.draw_popup(text)
        pad.clear_popup()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "debug":
            curses.wrapper(Game, **{'debug_mode': True})
    curses.wrapper(Game)
