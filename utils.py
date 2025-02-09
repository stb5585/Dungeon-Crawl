###########################################
""" utils manager """

import curses
import curses.textpad
import random
import time
from textwrap import wrap

import dill


# functions
def player_input(game, prompt):
    """
    Function that handles player input, i.e. name selection

    Args:
        game(object): the game object that contains necessary parameters, specifically the screen
        prompt(str): text prompt informing player of what they are inputting

    Returns:
        string containing the player input requested
    """

    curses.curs_set(1)  # Show the cursor
    game.stdscr.erase()
    game.stdscr.refresh()
    height, width = game.stdscr.getmaxyx()
    
    input_str = ""
    game.stdscr.addstr(height // 2, width // 2 - len(prompt) + 5, prompt)
    while True:
        key = game.stdscr.getch()

        # Handle Enter
        if key == curses.KEY_ENTER or key in [10, 13]:
            break

        # Handle Backspace
        elif key == curses.KEY_BACKSPACE or key == 127:
            if len(input_str) > 0:
                input_str = input_str[:-1]  # Remove the last character
                game.stdscr.delch(height // 2, width // 2 + len(input_str) + 6)  # Remove character from screen

        # Handle regular character input
        elif key != curses.KEY_RESIZE:  # Ignore resize key
            input_str += chr(key)
            game.stdscr.addch(height // 2, width // 2 + len(input_str) + 5, chr(key))  # Display the character

        game.stdscr.refresh()
    curses.curs_set(0)  # Hide the cursor
    return input_str


def ascii_art(filename):
    """
    Function that loads a text file containing an ascii enemy image

    Args:
        filename(str): the name of the ascii file to load

    Returns:
        a list of strings containing the characters that resemble the character picture
    """

    with open("ascii_files/" + filename, "r") as f:
        ascii_str = f.readlines()
    return [x for x in ascii_str if x.strip()]


def scaled_decay_function(x, rate=0.1):
    """
    Returns a value between 0 and 1 that decreases as x increases.
    
    Args:
        x (float): The input value, must be >= 0.
        rate (float): The rate of decay; higher values make it decrease faster.

    Returns:
        float: A value between 0 and 1.
    """

    if x < 0:
        raise ValueError("x must be non-negative.")
    decay_value = 1 / (1 + rate * x)  # Exponential decay
    return 0.5 + decay_value * 0.75  # Scale and shift to fit [0.5, 1.25]


def save_file_popup(game, load=False):
    header = "Save Game"
    message = "Saving your progress, please wait..."
    if load:
        header = "Load Game"
        message = "Loading game file..."
    curses.curs_set(0)  # Hide cursor
    height, width = game.stdscr.getmaxyx()
    popup_height, popup_width = 9, 50
    popup_y, popup_x = (height - popup_height) // 2, (width - popup_width) // 2

    # Create popup window
    popup = curses.newwin(popup_height, popup_width, popup_y, popup_x)
    popup.box()
    popup.addstr(1, (popup_width - len(header)) // 2, header, curses.A_BOLD)
    popup.addstr(3, (popup_width - len(message)) // 2, message)

    # Progress bar variables
    bar_width = popup_width - 4
    progress = 0
    steps = 20
    delay = 3 / steps  # Total delay split across steps

    # Draw initial progress bar
    popup.addstr(5, 2, "[" + " " * (bar_width - 2) + "]")
    popup.refresh()

    # Simulate progress
    for i in range(steps + 1):
        progress = int(i * (bar_width - 2) / steps)
        popup.addstr(5, 3, "#" * progress)
        popup.refresh()
        if not game.debug_mode:
            time.sleep(delay)

    # Completion message
    if not load:
        popup.addstr(7, (popup_width - 24) // 2, "Game saved successfully!", curses.A_BOLD)
        popup.refresh()
        if not game.debug_mode:
            time.sleep(2)

    # Cleanup
    popup.erase()
    game.stdscr.refresh()


# objects
class MainMenu:
    """
    
    """

    def __init__(self, game):
        self.game = game
        self.height, self.width = game.stdscr.getmaxyx()
        self.options_list = None
        self.current_option = 0
        self.create_windows()

    def create_windows(self):
        self.title_win = curses.newwin(self.height // 4, self.width, 0, 0)
        self.options_win = curses.newwin(3 * self.height // 4, self.width, self.height // 4, 0)

    def refresh_all(self):
        self.title_win.refresh()
        self.options_win.refresh()

    def draw_title(self):
        self.title_win.erase()
        title = ["     ____  __  ___   __________________  _   __   __________  ___ _       ____ \n",
                "   / __ \\/ / / / | / / ____/ ____/ __ \\/ | / /  / ____/ __ \\/   | |     / / / \n",
                "  / / / / / / /  |/ / / __/ __/ / / / /  |/ /  / /   / /_/ / /| | | /| / / /  \n",
                " / /_/ / /_/ / /|  / /_/ / /___/ /_/ / /|  /  / /___/ _, _/ ___ | |/ |/ / /___\n",
                "/_____/\\____/_/ |_/\\____/_____/\\____/_/ |_/   \\____/_/ |_/_/  |_|__/|__/_____/\n"]
        for i, line in enumerate(title):
            self.title_win.addstr(i + 1, self.width//2 - len(line)//2, line, curses.A_BOLD)
        self.title_win.box()

    def draw_options(self):
        self.options_win.erase()
        for idx, option in enumerate(self.options_list):
            if idx == self.current_option:
                self.options_win.attron(curses.A_REVERSE)
            self.options_win.addstr(self.height // 3 + idx, (self.width // 2) - (len(option) // 2), option)
            if idx == self.current_option:
                self.options_win.attroff(curses.A_REVERSE)
        self.options_win.box()

    def draw_all(self):
        self.draw_title()
        self.draw_options()

    def erase(self):
        self.game.stdscr.erase()
        self.game.stdscr.refresh()

    def update_options(self, options):
        self.current_option = 0
        self.options_list = options
        self.draw_all()
        self.refresh_all()

    def navigate_menu(self):
        while True:
            self.draw_all()
            self.refresh_all()
            key = self.game.stdscr.getch()
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return self.current_option


class NewGameMenu:
    """
    
    """

    def __init__(self, game):
        self.game = game
        self.height, self.width = game.stdscr.getmaxyx()
        self.options_list = None
        self.current_option = 0
        self.page = 1
        self.top_text = ""
        self.race = None
        self.cls = None
        self.create_windows()

    def create_windows(self):
        self.top_win = curses.newwin(self.height // 12, self.width, 0, 0)
        self.options_win = curses.newwin(11 * self.height // 12, self.width // 3, self.height // 12, 2 * self.width // 3)
        self.desc_win = curses.newwin(11 * self.height // 12, 2 * self.width // 3, self.height // 12, 0)

    def refresh_all(self):
        self.top_win.refresh()
        self.options_win.refresh()
        self.desc_win.refresh()

    def draw_top(self):
        self.top_win.erase()
        self.top_win.addstr(1, self.width // 2 - 17, self.top_text, curses.A_BOLD)
        self.top_win.box()

    def draw_options(self):
        self.options_win.erase()
        for idx, line in enumerate(self.options_list):
            if idx == self.current_option:
                self.options_win.attron(curses.A_REVERSE)
            self.options_win.addstr(
                (3 * self.height // 8) - (len(self.options_list) // 2) + idx, (self.width // 6) - (len(line) // 2), line)
            if idx == self.current_option:
                self.options_win.attroff(curses.A_REVERSE)
        self.options_win.box()

    def draw_desc(self):
        self.desc_win.erase()
        if self.options_list[self.current_option] != "Go Back":
            if self.page == 1:
                self.race = self.game.races_dict[self.options_list[self.current_option]]()
                self.desc_win.addstr(1, self.width // 3 - (len(self.race.name) // 2), self.race.name, curses.A_BOLD)
                lines = self.race.description.splitlines()
                for i, line in enumerate(lines):
                    self.desc_win.addstr(i + 3, 3, line)
                self.desc_win.addstr(9, self.width // 3 - 5, "Base Stats", curses.A_BOLD)
                stats_str = ["{:14}{:>4}    {:14}{:>4}".format(
                                "Strength:", f"{self.race.strength}", "Health:", f"{self.race.con * 2}"),
                            "{:14}{:>4}    {:14}{:>4}".format(
                                "Intelligence:", f"{self.race.intel}", "Mana:", f"{self.race.intel + self.race.wisdom // 2}"),
                            "{:14}{:>4}    {:14}{:>4}".format(
                                "Wisdom:", f"{self.race.wisdom}", "Attack:", f"{self.race.base_attack}"),
                            "{:14}{:>4}    {:14}{:>4}".format(
                                "Constitution:", f"{self.race.con}", "Defense:", f"{self.race.base_defense}"),
                            "{:14}{:>4}    {:14}{:>4}".format(
                                "Charisma:", f"{self.race.charisma}", "Magic:", f"{self.race.base_magic}"),
                            "{:14}{:>4}    {:14}{:>4}".format(
                                "Dexterity:", f"{self.race.dex}", "Magic Defense:", f"{self.race.base_magic_def}")]
                for j, line in enumerate(stats_str):
                    self.desc_win.addstr(j + 11, (self.width // 3) - (len(line) // 2), line)
                self.desc_win.addstr(j + 13, self.width // 3 - 6, "Resistances", curses.A_BOLD)
                resist_str = ["{:12}{:>6}    {:12}{:>6}".format(
                                  "Fire:", f"{self.race.resistance['Fire']}", "Ice:", f"{self.race.resistance['Ice']}"),
                              "{:12}{:>6}    {:12}{:>6}".format(
                                  "Electric:", f"{self.race.resistance['Electric']}", "Water:", f"{self.race.resistance['Water']}"),
                              "{:12}{:>6}    {:12}{:>6}".format(
                                  "Earth:", f"{self.race.resistance['Earth']}", "Wind:", f"{self.race.resistance['Wind']}"),
                              "{:12}{:>6}    {:12}{:>6}".format(
                                  "Shadow:", f"{self.race.resistance['Shadow']}", "Holy:", f"{self.race.resistance['Holy']}"),
                              "{:12}{:>6}    {:12}{:>6}".format(
                                  "Poison:", f"{self.race.resistance['Poison']}", "Physical:", f"{self.race.resistance['Physical']}")]
                for k, line in enumerate(resist_str):
                    self.desc_win.addstr(j + k + 15, (self.width // 3) - (len(line) // 2), line)
                self.desc_win.addstr(j + k + 17, self.width // 3 - 9, "Available Classes", curses.A_BOLD)
                cls_res_str = ", ".join(self.race.cls_res['Base'])
                self.desc_win.addstr(j + k + 19, (self.width // 3) - (len(cls_res_str) // 2), cls_res_str)
            elif self.page == 2:
                self.cls = self.game.classes_dict[self.options_list[self.current_option]]['class']()
                self.desc_win.addstr(1, self.width // 3 - (len(self.cls.name) // 2), self.cls.name, curses.A_BOLD)
                lines = self.cls.description.splitlines()
                for i, line in enumerate(lines):
                    self.desc_win.addstr(i + 3, 3, line)
                self.desc_win.addstr(9, self.width // 3 - 7, "Starting Stats", curses.A_BOLD)
                stat_plus_str = ["{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Strength:", f"{self.race.strength+self.cls.str_plus}", f"+{self.cls.str_plus}",
                                    "Health:", f"{(self.race.con+self.cls.con_plus)*2}", f"+{(self.cls.con_plus*2)}"),
                                 "{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Intelligence:", f"{self.race.intel+self.cls.int_plus}", f"+{self.cls.int_plus}",
                                    "Mana:", f"{(self.race.intel+self.cls.int_plus)*2}", f"+{self.cls.int_plus*2}"),
                                 "{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Wisdom:", f"{self.race.wisdom+self.cls.wis_plus}", f"+{self.cls.wis_plus}",
                                    "Attack:", f"{self.race.base_attack+self.cls.att_plus}", f"+{self.cls.att_plus}"),
                                 "{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Constitution:",  f"{self.race.con+self.cls.con_plus}", f"+{self.cls.con_plus}",
                                    "Defense:", f"{self.race.base_defense+self.cls.def_plus}", f"+{self.cls.def_plus}"),
                                 "{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Charisma:", f"{self.race.charisma+self.cls.cha_plus}", f"+{self.cls.cha_plus}",
                                    "Magic:", f"{self.race.base_magic+self.cls.magic_plus}", f"+{self.cls.magic_plus}"),
                                 "{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Dexterity:", f"{self.race.dex+self.cls.dex_plus}", f"+{self.cls.dex_plus}",
                                    "Magic Defense:", f"{self.race.base_magic_def+self.cls.magic_def_plus}", 
                                    f"+{self.cls.magic_def_plus}")]
                for j, line in enumerate(stat_plus_str):
                    self.desc_win.addstr(j + 11, (self.width // 3) - (len(line) // 2), line)
                self.desc_win.addstr(j + 14, self.width // 3 - 11, "Equipment Restrictions", curses.A_BOLD)
                for k, (typ, lst) in enumerate(self.cls.restrictions.items()):
                    line = f"{typ}: " + ", ".join(lst)
                    self.desc_win.addstr(j + k + 16, (self.width // 3) - (len(line) // 2), line)
                self.desc_win.addstr(j + k + 19, self.width // 3 - 10, "Available Promotions", curses.A_BOLD)
                promo_str = ", ".join([x for x in self.game.classes_dict[self.cls.name]['pro'] if x in self.race.cls_res['First']])
                self.desc_win.addstr(j + k + 21, (self.width // 3) - (len(promo_str) // 2), promo_str)
            else:
                pass
        self.desc_win.box()

    def draw_all(self):
        self.draw_top()
        self.draw_options()
        self.draw_desc()

    def erase(self):
        self.game.stdscr.erase()
        self.game.stdscr.refresh()

    def update_options(self):
        self.current_option = 0
        if self.page == 1:
            self.top_text = "Select the race for your character"
            self.options_list = list(self.game.races_dict.keys())
            self.options_list.append("Go Back")
        elif self.page == 2:
            self.top_text = f"Select the class for your {self.race.name} character"
            self.options_list = self.race.cls_res['Base'].copy()
            self.options_list.append("Go Back")

    def navigate_menu(self):
        while True:
            self.draw_all()
            self.refresh_all()
            key = self.game.stdscr.getch()
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if self.page == 1:
                    if self.options_list[self.current_option] == "Go Back":
                        return
                    self.page += 1
                    return self.race
                if self.page == 2:
                    if self.options_list[self.current_option] == "Go Back":
                        self.race = None
                        self.cls = None
                        self.page = 1
                        self.current_option = 0
                        return
                    else:
                        return self.cls


class LoadGameMenu:
    def __init__(self, game, load_options):
        self.game = game
        self.options_list = load_options
        self.height, self.width = game.stdscr.getmaxyx()
        self.top_text = "Choose the character to load"
        self.current_option = 0
        self.create_windows()

    def create_windows(self):
        self.top_win = curses.newwin(self.height // 12, self.width, 0, 0)
        self.options_win = curses.newwin(11 * self.height // 12, self.width // 3, self.height // 12, 2 * self.width // 3)
        self.desc_win = curses.newwin(11 * self.height // 12, 2 * self.width // 3, self.height // 12, 0)

    def refresh_all(self):
        self.top_win.refresh()
        self.options_win.refresh()
        self.desc_win.refresh()

    def draw_top(self):
        self.top_win.erase()
        self.top_win.addstr(1, self.width // 2 - 17, self.top_text, curses.A_BOLD)
        self.top_win.box()

    def draw_options(self):
        self.options_win.erase()
        for idx, line in enumerate(self.options_list):
            if idx == self.current_option:
                self.options_win.attron(curses.A_REVERSE)
            self.options_win.addstr(
                (3 * self.height // 8) - (len(self.options_list) // 2) + idx, (self.width // 6) - (len(line) // 2), line)
            if idx == self.current_option:
                self.options_win.attroff(curses.A_REVERSE)
        self.options_win.box()

    def draw_desc(self):
        self.desc_win.erase()
        if self.options_list[self.current_option] != "Go Back":
            loadfile = f"save_files/{self.options_list[self.current_option].lower()}.save"
            with open(loadfile, "rb") as save_file:
                player_dict = dill.load(save_file)
            desc_lines = self.config_desc_str(player_dict).splitlines()
            for i, line in enumerate(desc_lines):
                self.desc_win.addstr(5 + (2 * i), self.width // 3 - (len(line) // 2), line)
        self.desc_win.box()

    def draw_all(self):
        self.draw_top()
        self.draw_options()
        self.draw_desc()

    def erase(self):
        self.game.stdscr.erase()
        self.game.stdscr.refresh()

    def config_desc_str(self, player_dict):
        desc_str = f"{player_dict['name']}\n"
        desc_str += (f"Level {player_dict['level'].level} "
                     f"{player_dict['race'].name} "
                     f"{player_dict['cls'].name}\n")
        desc_str += (f"{'Hit Points:':13}{' ':1}{player_dict['health'].current:3}/{player_dict['health'].max:>3}\n"
                     f"{'Mana Points:':13}{' ':1}{player_dict['mana'].current:3}/{player_dict['mana'].max:>3}\n"
                     f"{'Strength:':13}{' ':1}{player_dict['stats'].strength:>7}\n"
                     f"{'Intelligence:':13}{' ':1}{player_dict['stats'].intel:>7}\n"
                     f"{'Wisdom:':13}{' ':1}{player_dict['stats'].wisdom:>7}\n"
                     f"{'Constitution:':13}{' ':1}{player_dict['stats'].con:>7}\n"
                     f"{'Charisma:':13}{' ':1}{player_dict['stats'].charisma:>7}\n"
                     f"{'Dexterity:':13}{' ':1}{player_dict['stats'].dex:>7}\n")
        return desc_str

    def navigate_menu(self):
        while True:
            self.draw_all()
            self.refresh_all()
            key = self.game.stdscr.getch()
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return self.current_option


class DungeonMenu:
    def __init__(self, game):
        self.game = game
        self.height, self.width = game.stdscr.getmaxyx()
        self.room = self.game.player_char.world_dict[
            (self.game.player_char.location_x, self.game.player_char.location_y, self.game.player_char.location_z)
            ]
        self.create_windows()

    def create_windows(self):
        self.top_win = curses.newwin(3 * self.height // 4, self.width, 0, 0)
        self.bottomleft_win = curses.newwin(self.height // 4, 2 * self.width // 3, 3 * self.height // 4, 0)
        self.bottomright_win = curses.newwin(self.height // 4, self.width // 3, 3 * self.height // 4, 2 * self.width // 3)

    def refresh_all(self):
        self.top_win.refresh()
        self.bottomleft_win.refresh()
        self.bottomright_win.refresh()

    def draw_top(self):
        level = self.game.player_char.location_z
        map_str = self.game.player_char.minimap()
        if self.game.player_char.state == 'fight':
            map_str += f"\n\n{self.game.player_char.name} is attacked by a {self.room.enemy.name}."
        self.top_win.erase()
        dungeon_message = f"Dungeon Level {level}\n"
        self.top_win.addstr(1, (self.width // 2) - (len(dungeon_message) // 2), dungeon_message)
        rows = map_str.splitlines()
        for y, row in enumerate(rows):
            self.top_win.addstr(y+2, (self.width // 2) - (len(row) // 2), row)
        self.top_win.box()

    def draw_bottomleft(self):
        room_str = self.room.intro_text(self.game)
        player_str = f"{str(self.game.player_char)}\n\n"
        self.bottomleft_win.erase()
        self.bottomleft_win.addstr(1, (self.width // 3) - (len(player_str) // 2), player_str)
        detail_text = room_str.splitlines()
        for i, line in enumerate(detail_text):
            self.bottomleft_win.addstr(
                (self.height // 6) - (len(detail_text) // 2) + i, (self.width // 3) - (len(line) // 2), line)
        self.bottomleft_win.box()

    def draw_bottomright(self):
        options = f"Move North (w)\n\nMove West (a)\tMove East (d)\n\nMove South (s)"
        self.bottomright_win.erase()
        options = options.splitlines()
        for i, line in enumerate(options):
            self.bottomright_win.addstr(
                (self.height // 5) - len(options) + i, (self.width // 6) - (len(line) // 2), line)
        self.bottomright_win.box()

    def draw_all(self):
        self.draw_top()
        self.draw_bottomleft()
        self.draw_bottomright()


class CombatMenu:
    def __init__(self, game):
        self.game = game
        self.height, self.width = game.stdscr.getmaxyx()
        self.options_list = None
        self.current_option = 0
        self.create_windows()

    def create_windows(self):
        self.enemy_win = curses.newwin(3 * self.height // 4, self.width, 0, 0)
        self.char_win = curses.newwin(self.height // 4, self.width // 2, 3 * self.height // 4, 0)
        self.options_win = curses.newwin(self.height // 4, self.width // 2, 3 * self.height // 4, self.width // 2)

    def refresh_all(self):
        self.enemy_win.refresh()
        self.char_win.refresh()
        self.options_win.refresh()

    def draw_enemy(self, enemy, vision=False):
        self.enemy_win.erase()
        enemy_text = str(enemy)
        if not vision:
            enemy_text = enemy_text.split("|")[0].strip()
        self.enemy_win.addstr((3 * self.height // 4) - 2, (self.width // 2) - (len(enemy_text) // 2), enemy_text)
        enemy_picture = ascii_art(enemy.cls.picture)
        for i, line in enumerate(enemy_picture):  # 21 spaces from top to bottom text
            self.enemy_win.addstr(
                (self.height // 3) - (len(enemy_picture) // 2) + i, (self.width // 2) - len(line) // 2, line)
        self.enemy_win.box()

    def draw_char(self, char=None):
        if not char:
            char = self.game.player_char
        self.char_win.erase()
        self.char_win.addstr(1, (self.width // 4) - (len(char.name) // 2), char.name)

        # Health bar calculation
        hp_percentage = char.health.current / char.health.max
        hp_bar_width = self.width // 4  # Bar takes up 50% of the screen width
        filled_hp = int(hp_bar_width * hp_percentage)
        hp_bar = "[" + "#" * filled_hp + " " * (hp_bar_width - filled_hp) + "]"
        hp_text = f"HP: {char.health.current}/{char.health.max}"

        # Mana bar calculation
        mana_percentage = char.mana.current / char.mana.max
        mana_bar_width = self.width // 4  # Bar takes up 50% of the screen width
        filled_mana = int(mana_bar_width * mana_percentage)
        mana_bar = "[" + "#" * filled_mana + " " * (mana_bar_width - filled_mana) + "]"
        mana_text = f"MP: {char.mana.current}/{char.mana.max}"

        # Display HP bar at the top
        self.char_win.addstr(2, (self.width // 4) - (len(hp_bar) // 2), hp_bar)
        self.char_win.addstr(3, (self.width // 4) - (len(hp_text) // 2), hp_text)

        # Display Mana bar below HP bar
        self.char_win.addstr(5, (self.width // 4) - (len(mana_bar) // 2), mana_bar)
        self.char_win.addstr(6, (self.width // 4) - (len(mana_text) // 2), mana_text)
        self.char_win.box()

    def draw_options(self, options):
        self.options_win.erase()
        self.options_list = options
        for idx, option in enumerate(self.options_list):
            if idx == self.current_option:
                self.options_win.attron(curses.A_REVERSE)
            self.options_win.addstr((4 - (len(self.options_list) // 2)) + idx, (self.width // 4) - (len(option) // 2), option)
            if idx == self.current_option:
                self.options_win.attroff(curses.A_REVERSE)
        self.options_win.box()

    def update_options(self, options):
        self.current_option = 0
        self.options_list = options

    def navigate_menu(self):
        while True:
            self.draw_options(self.options_list)
            self.refresh_all()
            key = self.game.stdscr.getch()
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return self.current_option


class TownMenu:
    def __init__(self, game, options_list):
        self.game = game
        self.height, self.width = game.stdscr.getmaxyx()
        self.options_list = options_list
        self.current_option = 0
        self.rows, self.cols = (3, 3)
        self.create_windows()

    def create_windows(self):
        self.title_win = curses.newwin(self.height // 12, self.width, 0, 0)
        self.options_win = curses.newwin(11 * self.height // 12, self.width, self.height // 12, 0)

    def draw_title(self):
        title_message = "Welcome to the town of Silvana!"
        self.title_win.erase()
        self.title_win.addstr(1, (self.width // 2) - (len(title_message) // 2), title_message, curses.A_BOLD)
        self.title_win.box()

    def draw_options(self):
        self.options_win.erase()
        grid_width = self.width // self.cols
        grid_height = (11 * self.height // 12) // self.rows
        self.options_win.addstr(self.height // 4, 0, "-" * self.width)
        self.options_win.addstr(7 * self.height // 12, 0, "-" * self.width)
        for i in range(11 * self.height // 12):
            self.options_win.addstr(i, self.width // 3, "|")
            self.options_win.addstr(i, 2 * self.width // 3, "|")
        for idx, option in enumerate(self.options_list):
            row = idx // self.cols
            col = idx % self.cols
            x = col * grid_width + (grid_width // 3) + (7 - len(option) // 2)
            y = row * grid_height + 5
            if idx == self.current_option:
                self.options_win.attron(curses.A_REVERSE)
            self.options_win.addstr(y, x, option)
            if idx == self.current_option:
                self.options_win.attroff(curses.A_REVERSE)
        self.options_win.box()

    def draw_all(self):
        self.draw_title()
        self.draw_options()
        
    def refresh_all(self):
        self.title_win.refresh()
        self.options_win.refresh()

    def navigate_menu(self):
        while True:
            self.draw_all()
            self.refresh_all()
            key = self.game.stdscr.getch()
            if key == curses.KEY_UP:
                self.current_option = (self.current_option - self.cols) % len(self.options_list)
            elif key == curses.KEY_DOWN:
                self.current_option = (self.current_option + self.cols) % len(self.options_list)
            elif key == curses.KEY_LEFT:
                self.current_option = (self.current_option - 1) % len(self.options_list)
            elif key == curses.KEY_RIGHT:
                self.current_option = (self.current_option + 1) % len(self.options_list)
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return self.current_option


class LocationMenu:
    def __init__(self, game, message, options_list, options_message=None):
        self.game = game
        self.height, self.width = game.stdscr.getmaxyx()
        self.message = message
        self.options_list = options_list
        self.options_message = options_message
        self.content = None
        self.current_option = 0
        self.create_windows()

    def create_windows(self):
        self.top_win = curses.newwin(self.height // 12, self.width, 0, 0)
        self.options_win = curses.newwin(11 * self.height // 12, self.width, self.height // 12, 0)

    def draw_top(self):
        self.top_win.erase()
        self.top_win.addstr(1, (self.width // 2) - (len(self.message) // 2), self.message, curses.A_BOLD)
        self.top_win.box()

    def draw_options(self):
        self.options_win.erase()
        if self.options_message:
            self.options_win.addstr((3 * self.height // 8) - (len(self.options_list) // 2) - 2,
                                    (self.width // 2) - (len(self.options_message) // 2), self.options_message, curses.A_BOLD)
        for idx, line in enumerate(self.options_list):
            if idx == self.current_option:
                self.options_win.attron(curses.A_REVERSE)
            self.options_win.addstr(
                (3 * self.height // 8) - (len(self.options_list) // 2) + idx, (self.width // 2) - (len(line) // 2), line)
            if idx == self.current_option:
                self.options_win.attroff(curses.A_REVERSE)
        self.options_win.box()

    def draw_all(self):
        self.draw_top()
        self.draw_options()

    def refresh_all(self):
        self.top_win.refresh()
        self.options_win.refresh()

    def update_options(self, options, options_message=None, reset_current=True):
        if reset_current:
            self.current_option = 0
        self.options_list = options
        self.options_message = options_message

    def navigate_menu(self):
        while True:
            self.draw_all()
            self.refresh_all()
            key = self.game.stdscr.getch()
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return self.current_option


class ShopMenu:

    def __init__(self, game, shop_message):
        self.game = game
        self.height, self.width = game.stdscr.getmaxyx()
        self.shop_message = shop_message
        self.options_list = ["Buy", "Sell", "Quests", "Leave"]
        self.buy_or_sell = None
        self.current_option = 0
        self.itemdict = None
        self.item_str_list = []
        self.current_item = 0
        self.pages = [0]
        self.page = 0
        self.create_windows()

    def create_windows(self):
        self.top_win = curses.newwin(self.height // 12, self.width, 0, 0)
        self.options_win = curses.newwin(self.height // 4, self.width // 3, self.height // 12, 0)
        self.item_desc_win = curses.newwin(self.height // 4, 2 * self.width // 3, self.height // 12, self.width // 3)
        self.shop_list_win = curses.newwin(2 * self.height // 3, 2 * self.width // 3, self.height // 3, 0)
        self.mod_win = curses.newwin(7 * self.height // 12, self.width // 3, self.height // 3, 2 * self.width // 3)
        self.gold_win = curses.newwin(self.height // 12, self.width // 3, 11 * self.height // 12, 2 * self.width // 3)

    def draw_top(self):
        self.top_win.erase()
        self.top_win.addstr(1, (self.width // 2) - (len(self.shop_message) // 2), self.shop_message, curses.A_BOLD)
        self.top_win.box()

    def draw_options(self):
        self.options_win.erase()
        for idx, option in enumerate(self.options_list):
            if idx == self.current_option:
                self.options_win.attron(curses.A_REVERSE)
            self.options_win.addstr(
                (3 * self.height // 24) - (len(self.options_list) // 2) + idx + 1, self.width // 6 - (len(option) // 2), option)
            if idx == self.current_option:
                self.options_win.attroff(curses.A_REVERSE)
        self.options_win.box()

    def draw_item_desc(self):
        self.item_desc_win.erase()
        if self.itemdict:
            item_str = self.item_str_list[self.current_item]
            if item_str not in ["Go Back", "Next Page"]:
                if self.buy_or_sell == "Buy":
                    typ, name, _, _ = [x.strip() for x in list(filter(None, item_str.split('  ')))]
                    item = [x for x in self.itemdict[typ] if x().name == name][0]()
                    lines = wrap(item.description, 75, break_on_hyphens=False)
                elif self.buy_or_sell == "Sell":
                    typ, name, _ = [x.strip() for x in list(filter(None, item_str.split('  ')))]
                    item = self.itemdict[name][0]
                    lines = wrap(item.description, 75, break_on_hyphens=False)
                for i, line in enumerate(lines):
                    self.item_desc_win.addstr(self.height // 8 + i - (len(lines) // 2),
                                            (self.width // 3) - (len(line) // 2), line)
                if item.typ == "Weapon" and item.element:  # TODO change to include armor
                    pass
        self.item_desc_win.box()

    def draw_shop_list(self):
        self.shop_list_win.erase()
        if self.itemdict:
            if self.buy_or_sell == "Buy":
                shop_str = f"{'Type':16}{' ':2}{'Item':33}{'Cost':5}{' ':9}{'Owned':>13}"
            else:
                shop_str = f"{'Type':16}{' ':2}{'Item':33}{' ':14}{'Owned':>13}"
            self.shop_list_win.addstr(1, 1, shop_str, curses.A_BOLD)
            for idx, item in enumerate(self.item_str_list):
                if idx == self.current_item:
                    self.shop_list_win.attron(curses.A_REVERSE)
                self.shop_list_win.addstr(2 + idx, 1, item)
                if idx == self.current_item:
                    self.shop_list_win.attroff(curses.A_REVERSE)
        self.shop_list_win.box()

    def draw_mod(self):
        self.mod_win.erase()
        if self.itemdict:
            combat_str_dict = self.config_mod_str()
            if combat_str_dict:
                self.mod_win.addstr(1, (self.width // 6) - 11, "Equipment Modifications", curses.A_BOLD)
            for idx, (mod, value) in enumerate(combat_str_dict.items()):
                self.mod_win.addstr((7 * self.height // 24) - len(combat_str_dict) + (idx * 2) + 1, 1, mod)
                self.mod_win.addstr((7 * self.height // 24) - len(combat_str_dict) + (idx * 2) + 1,
                                    (self.width // 3) - len(value) - 1, value)
        self.mod_win.box()

    def draw_gold(self):
        gold = str(self.game.player_char.gold) + "G"
        self.gold_win.erase()
        self.gold_win.addstr(1, self.width // 3 - (len(gold) + 1), gold, curses.A_BOLD)
        self.gold_win.box()

    def draw_all(self):
        self.draw_top()
        self.draw_options()
        self.draw_mod()
        self.draw_item_desc()
        self.draw_shop_list()
        self.draw_gold()

    def refresh_all(self):
        self.top_win.refresh()
        self.options_win.refresh()
        self.mod_win.refresh()
        self.item_desc_win.refresh()
        self.shop_list_win.refresh()
        self.gold_win.refresh()

    def update_options(self, options):
        self.current_option = 0
        self.options_list = options

    def reset_options(self, quests=False):
        self.current_option = 0
        self.options_list = ["Buy", "Sell", "Leave"]
        if quests:
            self.options_list.insert(2, "Quests")

    def update_itemdict(self, itemdict, reset_current=True):
        if reset_current:
            self.current_item = 0
        self.itemdict = itemdict
        if itemdict:
            self.config_item_str()

    def config_item_str(self):
        self.item_str_list = []
        start_item_idx = self.pages[self.page] * 19
        if self.options_list[self.current_option] == "Sell":
            for name, itemlist in self.itemdict.items():
                typ = itemlist[0].typ
                self.item_str_list.append(f"{typ:16}{' ':2}{name:31}{'':26}x{len(itemlist):2}")
        else:
            for typ, lst in self.itemdict.items():
                for item in lst:
                    adj_scale = scaled_decay_function(self.game.player_char.stats.charisma // 2)
                    if self.game.player_char.in_town():
                        if item().rarity >= max(0.4, (1.0 - (0.02 * self.game.player_char.player_level()))):
                            adj_cost = max(1, int(item().value * adj_scale))
                            num = 0
                            if item().name in self.game.player_char.inventory:
                                num = len(self.game.player_char.inventory[item().name])
                            self.item_str_list.append(f"{typ:16}{' ':2}{item().name:31}{adj_cost:6}{' ':20}x{num:>2}")
                    else:
                        exception_list = ["Old Key"]
                        if 0.1 <= item().rarity < 0.4 or item().name in exception_list:
                            adj_cost = max(1, int(item().value * adj_scale))
                            num = 0
                            if item().name in self.game.player_char.inventory:
                                num = len(self.game.player_char.inventory[item().name])
                            self.item_str_list.append(f"{typ:16}{' ':2}{item().name:31}{adj_cost:6}{' ':20}x{num:>2}")             
        istr_len = len(self.item_str_list)
        if istr_len > 19:
            self.item_str_list = self.item_str_list[start_item_idx:start_item_idx+19]
            self.item_str_list.append("Next Page")
            for i in range(istr_len // 19):
                self.pages.append(i+1)
        self.item_str_list.append("Go Back")

    def config_mod_str(self):
        mod_dict = {}
        item_str = self.item_str_list[self.current_item]
        if item_str not in ["Go Back", "Next Page"]:
            if self.buy_or_sell == "Buy":
                try:
                    typ, name, _, _ = [x.strip() for x in list(filter(None, item_str.split('  ')))]
                    item = [x for x in self.itemdict[typ] if x().name == name][0]
                    for line in self.game.player_char.equip_diff(item(), item().typ, buy=True).splitlines():
                        mod, value = list(filter(None, line.split('  ')))
                        mod_dict[mod] = value
                except KeyError:
                    pass
            elif self.buy_or_sell == "Sell":
                try:
                    typ, name, _ = [x.strip() for x in list(filter(None, item_str.split('  ')))]
                    item = self.itemdict[name][0]
                    for line in self.game.player_char.equip_diff(item, item.typ, buy=True).splitlines():
                        mod, value = list(filter(None, line.split('  ')))
                        mod_dict[mod] = value
                except KeyError:
                    pass
        return mod_dict

    def navigate_options(self):
        while True:
            self.draw_all()
            self.refresh_all()
            key = self.game.stdscr.getch()
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if self.options_list[self.current_option] == "Buy":
                    self.buy_or_sell = "Buy"
                elif self.options_list[self.current_option] == "Sell":
                    self.buy_or_sell = "Sell"
                return self.options_list[self.current_option]

    def navigate_items(self):
        while True:
            self.draw_all()
            self.refresh_all()
            key = self.game.stdscr.getch()
            if key == curses.KEY_UP:
                self.current_item -= 1
                if self.current_item < 0:
                    self.current_item = len(self.item_str_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_item += 1
                if self.current_item > len(self.item_str_list) - 1:
                    self.current_item = 0
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if self.item_str_list[self.current_item] != "Next Page":
                    if self.item_str_list[self.current_item] == "Go Back":
                        self.page = 0
                    return self.item_str_list[self.current_item]
                self.page += 1
                if self.page > self.pages[-1]:
                    self.page = 0
                self.update_itemdict(self.itemdict, reset_current=True)


class CharacterMenu:
    """
    
    """

    def __init__(self, game, options_list):
        self.game = game
        self.height, self.width = game.stdscr.getmaxyx()
        self.options_list = options_list
        self.current_option = 0
        self.rows, self.cols = (3, 2)
        self.create_windows()

    def create_windows(self):
        self.options_win = curses.newwin(self.height // 4, 3 * self.width // 5, 0, 0)  # top left
        self.player_loc_win = curses.newwin(self.height // 7, 2 * self.width // 5, 0, 3 * self.width // 5)  # top right top
        self.info_win = curses.newwin(self.height // 7 - 1, 2 * self.width // 5, self.height // 8 + 1, 3 * self.width // 5)  # top right bottom
        self.status_win = curses.newwin(3 * self.height // 4, self.width, self.height // 4, 0)  # bottom

    def refresh_all(self):
        self.options_win.refresh()
        self.player_loc_win.refresh()
        self.info_win.refresh()
        self.status_win.refresh()

    def draw_all(self):
        self.draw_options()
        self.draw_player_loc()
        self.draw_info()
        self.draw_status()

    def draw_options(self):
        self.options_win.erase()
        grid_width = (self.width // 3) // self.cols
        grid_height = (self.height // 8) // self.rows
        for idx, option in enumerate(self.options_list):
            row = idx // self.cols
            col = idx % self.cols
            x = col * grid_width + grid_width + 3
            y = row * grid_height + 3
            if idx == self.current_option:
                self.options_win.attron(curses.A_REVERSE)
            self.options_win.addstr(y, x, option)
            if idx == self.current_option:
                self.options_win.attroff(curses.A_REVERSE)
        self.options_win.box()

    def draw_player_loc(self):
        gold_str = f"{self.game.player_char.gold}G"
        weight_str = f"{self.game.player_char.current_weight()}/{self.game.player_char.max_weight()}"
        self.player_loc_win.erase()
        self.player_loc_win.addstr(1, 1, f"{self.game.player_char.name}", curses.A_BOLD)
        self.player_loc_win.addstr(3, 1,
                                   (f"Level {self.game.player_char.level.level} "
                                    f"{self.game.player_char.race.name} "
                                    f"{self.game.player_char.cls.name}"))
        if self.game.player_char.in_town():
            loc_str = "Town"
        else:
            loc_str = f"Dungeon Level {self.game.player_char.location_z}"
        self.player_loc_win.addstr(2, 1, loc_str)
        self.player_loc_win.addstr(1, 2 * self.width // 5 - len(weight_str) - 13, "Weight/Max:", curses.A_BOLD)
        self.player_loc_win.addstr(1, 2 * self.width // 5 - len(weight_str) - 1, weight_str)
        if self.game.player_char.encumbered:
            self.player_loc_win.addstr(2, 2 * self.width // 5 - 11, "ENCUMBERED", curses.A_BOLD)
        self.player_loc_win.addstr(3, 2 * self.width // 5 - len(gold_str) - 1, gold_str, curses.A_BOLD)
        self.player_loc_win.box()

    def draw_info(self):
        exp = f"{self.game.player_char.level.exp}"
        to_level = f"{self.game.player_char.level.exp_to_gain}"
        self.info_win.erase()
        self.info_win.addstr(1, 1, "Experience:", curses.A_BOLD)
        self.info_win.addstr(1, 2 * self.width // 5 - len(exp) - 1, exp)
        self.info_win.addstr(2, 1, "To Next Level:", curses.A_BOLD)
        self.info_win.addstr(2, 2 * self.width // 5 - len(to_level) - 1, to_level)
        self.info_win.box()

    def draw_status(self):
        self.status_win.erase()
        status_lines = self.game.player_char.status_str().splitlines()
        for i, line in enumerate(status_lines):
            self.status_win.addstr((2 * i) + 2, self.width // 12, line)
        combat_lines = self.game.player_char.combat_str().splitlines()
        for i, line in enumerate(combat_lines):
            self.status_win.addstr((2 * i) + 2, self.width // 3, line)
        equip_lines = self.game.player_char.equipment_str().splitlines()
        self.status_win.addstr(2, 84, "Equipped Gear", curses.A_BOLD)
        for i, line in enumerate(equip_lines):
            self.status_win.addstr((2 * i) + 4, 3 * self.width // 5, line)
        resist_lines = self.game.player_char.resist_str().splitlines()
        self.status_win.addstr((5 * self.height // 8) - 2, (self.width // 2) - 6, "Resistances", curses.A_BOLD)
        for i, line in enumerate(resist_lines):
            row = i // 2
            col = i % 2
            self.status_win.addstr((5 * self.height // 8) + (2 * col), 10 + row * self.width // 4, line)
        self.status_win.box()

    def navigate_menu(self):
        while True:
            self.draw_options()
            self.refresh_all()
            key = self.game.stdscr.getch()
            if key == curses.KEY_UP:
                self.current_option = (self.current_option - self.cols) % len(self.options_list)
            elif key == curses.KEY_DOWN:
                self.current_option = (self.current_option + self.cols) % len(self.options_list)
            elif key == curses.KEY_LEFT:
                self.current_option = (self.current_option - 1) % len(self.options_list)
            elif key == curses.KEY_RIGHT:
                self.current_option = (self.current_option + 1) % len(self.options_list)
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return self.current_option


class PopupMenu:

    def __init__(self, game, header_message, box_height=20, box_width=30):
        self.game = game
        self.screen_height, self.screen_width = game.stdscr.getmaxyx()
        self.header_message = wrap(header_message, box_width - 2, break_on_hyphens=False)
        self.box_height, self.box_width = (box_height, box_width)
        self.options_list = []
        self.current_option = 0
        self.create_popup()

    def create_popup(self):
        # Create popup window dimensions
        start_y, start_x = (self.screen_height // 2) - (self.box_height // 2), (self.screen_width // 2) - (self.box_width // 2)
        # Create a new window for the popup
        self.popup_win = curses.newwin(self.box_height, self.box_width, start_y, start_x)

    def draw_popup(self):
        self.popup_win.erase()
        if not isinstance(self.header_message, list):
            self.header_message = [self.header_message]
        for i, line in enumerate(self.header_message):
            self.popup_win.addstr(1 + i, (self.box_width // 2) - (len(line) // 2), line, curses.A_BOLD)
        for idx, option in enumerate(self.options_list):
            if idx == self.current_option:
                self.popup_win.attron(curses.A_REVERSE)
            self.popup_win.addstr(3 + idx + i, self.box_width // 2 - (len(option) // 2), option)
            if idx == self.current_option:
                self.popup_win.attroff(curses.A_REVERSE)
        self.popup_win.box()

    def clear_popup(self):
        self.popup_win.erase()
        self.popup_win.refresh()

    def navigate_popup(self):
        self.draw_popup()
        while True:
            self.draw_popup()
            self.popup_win.refresh()
            key = self.game.stdscr.getch()

            # Navigate the item list
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return self.current_option


class PromotionPopupMenu(PopupMenu):

    def __init__(self, game, header_message, current_class, familiar=False, box_height=30, box_width=120):
        super().__init__(game, header_message, box_height, box_width)
        self.current_class = current_class
        self.options_list = []
        self.cls_dict = {}
        self.familiar = familiar

    def draw_popup(self):
        self.popup_win.erase()
        if self.options_list[self.current_option] != "Go Back":
            if self.familiar:
                # self.popup_win.addstr(1, (self.box_width // 2) - 5, "Promotion", curses.A_BOLD)
                fam = self.cls_dict[self.options_list[self.current_option]]()
                self.popup_win.addstr(7, (2 * self.box_width // 5) - (len(fam.race) // 2), fam.race, curses.A_BOLD)
                lines = wrap(fam.inspect(), 75, break_on_hyphens=False)
                for i, line in enumerate(lines):
                    self.popup_win.addstr(i + 9, 14, line)
                self.popup_win.addstr(16, (2 * self.box_width // 5) - 5, "Abilities", curses.A_BOLD)
                spells = list(fam.spellbook["Spells"].keys())
                if not spells:
                    spells = ["None"]
                spell_str = "Spells: " + ", ".join(spells)
                self.popup_win.addstr(18, (2 * self.box_width // 5) - (len(spell_str) // 2), spell_str)
                skills = list(fam.spellbook["Skills"].keys())
                if not skills:
                    skills = ["None"]
                skill_str = "Skills: " + ", ".join(skills)
                self.popup_win.addstr(19, (2 * self.box_width // 5) - (len(skill_str) // 2), skill_str)
            else:
                self.popup_win.addstr(1, (self.box_width // 2) - 5, "Promotion", curses.A_BOLD)
                cls = self.cls_dict[self.current_class][self.current_option]
                self.popup_win.addstr(3, (2 * self.box_width // 5) - (len(cls.name) // 2), cls.name, curses.A_BOLD)
                # class description
                lines = cls.description.splitlines()
                for i, line in enumerate(lines):
                    self.popup_win.addstr(i + 5, 14, line)
                # promo stats
                self.popup_win.addstr(13, (self.box_width // 5) - 7, "Promotion Stats", curses.A_BOLD)
                stat_plus_str = ["{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Strength:", f"{self.game.player_char.stats.strength+cls.str_plus}", f"+{cls.str_plus}",
                                    "Health:", f"{self.game.player_char.health.max+(cls.con_plus*2)}", f"+{cls.con_plus*2}"),
                                 "{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Intelligence:", f"{self.game.player_char.stats.intel+cls.int_plus}", f"+{cls.int_plus}",
                                    "Mana:", f"{self.game.player_char.mana.max+(cls.int_plus*2)}", f"+{cls.int_plus*2}"),
                                 "{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Wisdom:", f"{self.game.player_char.stats.wisdom+cls.wis_plus}", f"+{cls.wis_plus}",
                                    "Attack:", f"{self.game.player_char.combat.attack+cls.att_plus}", f"+{cls.att_plus}"),
                                 "{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Constitution:",  f"{self.game.player_char.stats.con+cls.con_plus}", f"+{cls.con_plus}",
                                    "Defense:", f"{self.game.player_char.combat.defense+cls.def_plus}", f"+{cls.def_plus}"),
                                 "{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Charisma:", f"{self.game.player_char.stats.charisma+cls.cha_plus}", f"+{cls.cha_plus}",
                                    "Magic:", f"{self.game.player_char.combat.magic+cls.magic_plus}", f"+{cls.magic_plus}"),
                                 "{:14}{:>3}({:>2})  {:14}{:>4}({:>2})".format(
                                    "Dexterity:", f"{self.game.player_char.stats.dex+cls.dex_plus}", f"+{cls.dex_plus}",
                                    "Magic Defense:", f"{self.game.player_char.combat.magic_def+cls.magic_def_plus}", 
                                    f"+{cls.magic_def_plus}")]
                for j, line in enumerate(stat_plus_str):
                    self.popup_win.addstr(j + 14, (self.box_width // 5) - (len(line) // 2), line)
                # new equipment
                self.popup_win.addstr(13, (3 * self.box_width // 5) - 6, "New Equipment", curses.A_BOLD)
                self.popup_win.addstr(14, (3 * self.box_width // 5) - 15, f"{'Weapon:':8} {cls.equipment['Weapon'].name:>20}")
                self.popup_win.addstr(16, (3 * self.box_width // 5) - 15, f"{'OffHand:':8} {cls.equipment['OffHand'].name:>20}")
                self.popup_win.addstr(18, (3 * self.box_width // 5) - 15, f"{'Armor:':8} {cls.equipment['Armor'].name:>20}")
                # equipment restrictions
                self.popup_win.addstr(j + 17, (2 * self.box_width // 5) - 11, "Equipment Restrictions", curses.A_BOLD)
                for k, (typ, lst) in enumerate(cls.restrictions.items()):
                    line = f"{typ}: " + ", ".join(lst)
                    self.popup_win.addstr(j + k + 19, (2 * self.box_width // 5) - (len(line) // 2), line)
        # header message and options
        if not isinstance(self.header_message, list):
            self.header_message = [self.header_message]
        for i, line in enumerate(self.header_message):
            self.popup_win.addstr((self.box_height // 2) - (len(self.options_list) // 2) + i - 3,
                                  (7 * self.box_width // 8) - (len(line) // 2), line, curses.A_BOLD)
        for idx, option in enumerate(self.options_list):
            if idx == self.current_option:
                self.popup_win.attron(curses.A_REVERSE)
            self.popup_win.addstr((self.box_height // 2) - (len(self.options_list) // 2) + idx + i,
                                  (7 * self.box_width // 8) - (len(option) // 2), option)
            if idx == self.current_option:
                self.popup_win.attroff(curses.A_REVERSE)
        self.popup_win.box()

    def update_options(self, options_list, cls_dict):
        self.current_option = 0
        self.options_list = options_list
        self.cls_dict = cls_dict


class CombatPopupMenu(PopupMenu):
    def __init__(self, game, header_message):
        super().__init__(game, header_message)

    def update_options(self, options_list, header_message):
        self.current_option = 0
        self.options_list = options_list
        self.header_message = header_message


class SlotMachinePopupMenu(PopupMenu):
    def __init__(self, game, header_message, box_height=5, box_width=7):
        super().__init__(game, header_message, box_height, box_width)
        self.result = ['*', '*', '*']

    def draw_popup(self):
        self.popup_win.erase()
        self.popup_win.box()
        self.popup_win.addstr(2, 2, "".join(self.result))
        for i, _ in enumerate(self.result):
            for _ in range(50):
                self.result[i] = str(random.randint(0, 9))
                self.popup_win.addstr(2, 2, "".join(self.result))
                self.popup_win.refresh()
                time.sleep(0.01)
        self.game.stdscr.getch()
    
    def results(self):
        self.draw_popup()
        return "".join(self.result)

    def navigate_popup(self):
        raise NotImplementedError


class BlackjackPopupMenu(PopupMenu):

    def __init__(self, game, header_message, box_height=10, box_width=30):
        super().__init__(game, header_message, box_height, box_width)
        self.numbers = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.suits = ["♠️", "♥️", "♣️", "♦️"]
        self.deck = [f"{suit} {number}" for suit in self.suits for number in self.numbers]
        self.user_hand = []
        self.user_stay = False
        self.target_hand = []
        self.target_stay = False

    def draw_popup(self):
        user_name, target_name = self.header_message[0].split('  ')
        self.popup_win.erase()
        self.popup_win.addstr(1, 2, user_name)
        self.popup_win.addstr(1, 27 - len(target_name), target_name)
        for i, card in enumerate(self.user_hand):
            self.popup_win.addstr(3 + i, 5, card)
        for i, card in enumerate(self.target_hand):
            self.popup_win.addstr(3 + i, 18, card)
        self.popup_win.box()

    def deal(self):
        def draw_card(cards):
            card = random.choice(cards)
            return cards.pop(cards.index(card))

        def score(hand):
            total = 0
            for card in hand:
                try:
                    total += int(card.split()[1])
                except ValueError:
                    if card.split()[1] in ['J', 'Q', 'K']:
                        total += 10
                    else:
                        total += 11
                        if total > 21:
                            total -= 10
            return total

        if not self.target_stay:
            self.target_hand.append(draw_card(self.deck))
            target_score = score(self.target_hand)
            if target_score > 21:
                return "Target Break"
            if target_score >= 17:
                self.target_stay = True
        if not self.user_stay:
            self.user_hand.append(draw_card(self.deck))
            user_score = score(self.user_hand)
            if user_score > 21:
                return "User Break"
            if user_score >= 17:
                self.user_stay = True
        if all([self.target_stay, self.user_stay]):
            target_score = score(self.target_hand)
            user_score = score(self.user_hand)
            if target_score > user_score:
                return "Target Win"
            if user_score > target_score:
                return "User Win"
            return "Push"

    def navigate_popup(self):
        self.draw_popup()
        result = None
        while True:
            if result:
                self.draw_popup()
                self.popup_win.refresh()
                self.game.stdscr.getch()
                return result
            self.draw_popup()
            self.popup_win.refresh()
            result = self.deal()
            self.game.stdscr.getch()


class SelectionPopupMenu(PopupMenu):

    def __init__(self, game, header_message, stat_options, box_height=10, rewards=None, confirm=True):
        super().__init__(game, header_message, box_height=box_height)
        self.options_list = stat_options
        self.rewards = rewards
        self.confirm = confirm

    def navigate_popup(self):
        self.draw_popup()
        while True:
            self.draw_popup()
            self.popup_win.refresh()
            key = self.game.stdscr.getch()

            # Navigate the item list
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0
            elif key == ord("i") or key == ord("I") and self.rewards:
                try:
                    self.inspect_item(self.rewards[self.current_option])
                except TypeError:
                    pass
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if self.confirm:
                    choice_str = self.options_list[self.current_option]
                    confirm_str = f"Are you sure you want to choose: {choice_str}?"
                    confirm_popup = ConfirmPopupMenu(self.game, confirm_str, box_height=7)
                    if confirm_popup.navigate_popup():
                        return self.current_option
                else:
                    return self.current_option

    def inspect_item(self, item):
        itembox = TextBox(self.game)
        itembox.print_text_in_rectangle(str(item()))
        self.game.stdscr.getch()
        itembox.clear_rectangle()


class ShopPopup(PopupMenu):

    def __init__(self, game, header_message, max="01", box_height=20, box_width=30):
        super().__init__(game, header_message, box_height, box_width)
        self.current_option = 1
        self.max = max.zfill(2)
        self.tens = self.max[0]
        self.ones = self.max[1]

    def draw_popup(self):
        self.popup_win.erase()
        for i, line in enumerate(self.header_message):
            self.popup_win.addstr(1 + i, (self.box_width // 2) - (len(line) // 2), line, curses.A_BOLD)
        for idx, option in enumerate([self.tens, self.ones]):
            if idx == self.current_option:
                self.popup_win.attron(curses.A_REVERSE)
            self.popup_win.addstr(3 + i, self.box_width // 2 + idx - 1, option)
            if idx == self.current_option:
                self.popup_win.attroff(curses.A_REVERSE)
        self.popup_win.box()

    def navigate_popup(self):
        self.draw_popup()
        while True:
            self.draw_popup()
            self.popup_win.refresh()
            key = self.game.stdscr.getch()

            # Navigate the item list
            if key == curses.KEY_LEFT:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = 1
            elif key == curses.KEY_RIGHT:
                self.current_option += 1
                if self.current_option > 1:
                    self.current_option = 0
            elif key == curses.KEY_UP:
                if self.current_option == 1:
                    self.ones = str(int(self.ones) + 1)
                    if int(self.ones) > 9:
                        self.ones = "0"
                else:
                    self.tens = str(int(self.tens) + 1)
                    if int(self.tens) > 9:
                        self.tens = "0"
            elif key == curses.KEY_DOWN:
                if self.current_option == 1:
                    self.ones = str(int(self.ones) - 1)
                    if int(self.ones) < 0:
                        self.ones = "9"
                else:
                    self.tens = str(int(self.tens) - 1)
                    if int(self.tens) < 0:
                        self.tens = "9"
            elif key == curses.KEY_ENTER or key in [10, 13]:
                return int(self.tens+self.ones)


class ConfirmPopupMenu(PopupMenu):
    def __init__(self, game, header_message, box_height=0):
        super().__init__(game, header_message, box_height=box_height)
        self.options_list = ["Yes", "No"]

    def create_popup(self):
        # Create popup window dimensions
        start_y, start_x = (self.screen_height // 2) - (self.box_height // 2), (self.screen_width // 2) - (self.box_width // 2)
        # Create a new window for the popup
        self.popup_win = curses.newwin(self.box_height, self.box_width, start_y, start_x)

    def navigate_popup(self):
        self.draw_popup()
        while True:
            self.draw_popup()
            self.popup_win.refresh()
            key = self.game.stdscr.getch()

            # Navigate the item list
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0

            # Confirm selection
            if key == ord('\n'):  # Enter key
                if self.options_list[self.current_option] == "Yes":
                    return True
                return False


class InventoryPopupMenu(PopupMenu):
    def __init__(self, game, header_message):
        super().__init__(game, header_message)
        self.pages = [0]
        self.page = 0

    def draw_popup(self):
        self.update_itemlist()
        self.popup_win.erase()
        for i, line in enumerate(self.header_message):
            self.popup_win.addstr(1 + i, (self.box_width // 2) - (len(line) // 2), line, curses.A_BOLD)
        # Display item list
        for idx, item in enumerate(self.options_list):
            if idx == self.current_option:
                self.popup_win.attron(curses.A_REVERSE)
            length = '' if not len(item[1]) else len(item[1])
            item_str = f"{item[0]:24}{length:2}"
            self.popup_win.addstr(3 + idx, 2, item_str)
            if idx == self.current_option:
                self.popup_win.attroff(curses.A_REVERSE)
        self.popup_win.box()   

    def update_itemlist(self):
        self.options_list = []
        start_item_idx = self.pages[self.page] * 14
        if self.header_message[0] == "Inventory":
            inv_len = len(self.game.player_char.inventory)
            if inv_len > 0:
                inventory_keys = list(self.game.player_char.inventory.keys())[start_item_idx:start_item_idx+14]
                for key in inventory_keys:
                    self.options_list.append((key, self.game.player_char.inventory[key]))
        elif self.header_message[0] == "Key Items":
            inv_len = len(self.game.player_char.special_inventory)
            if inv_len > 0:
                inventory_keys = list(self.game.player_char.special_inventory.keys())[start_item_idx:start_item_idx+14]
                for key in inventory_keys:
                    self.options_list.append((key, self.game.player_char.special_inventory[key]))
        else:
            raise NotImplementedError
        if inv_len > 14:
            self.options_list.append(("Next Page", []))
            for i in range(inv_len // 14):
                self.pages.append(i+1)
        self.options_list.append(("Go Back", []))

    def navigate_popup(self):
        self.draw_popup()
        if not self.options_list:
            box = TextBox(self.game)
            box.print_text_in_rectangle("You do not have any items in your inventory.")
            self.game.stdscr.getch()
            box.clear_rectangle()
            return
        while True:
            self.draw_popup()
            self.popup_win.refresh()
            key = self.game.stdscr.getch()

            # Navigate the item list
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0

            # Confirm selection
            if key == ord('\n'):  # Enter key
                name = self.options_list[self.current_option][0]
                if name == "Go Back":
                    return name
                if name == "Next Page":
                    self.current_option = 0
                    self.page += 1
                    if self.page > self.pages[-1]:
                        self.page = 0
                else:
                    item = self.options_list[self.current_option][1][0]
                    self.inspect_item(item)
                    return item

    def inspect_item(self, item):
        itembox = TextBox(self.game)
        itembox.print_text_in_rectangle(str(item))
        self.game.stdscr.getch()
        itembox.clear_rectangle()


class EquipPopupMenu(PopupMenu):

    def __init__(self, game, header_message, box_height):
        super().__init__(game, header_message, box_height=box_height)
        self.options_list = ["Weapon", "OffHand", "Armor", "Ring", "Pendant", "Go Back"]
        self.equip_type = None
        self.page = 1

    def navigate_popup(self):
        self.draw_popup()
        while True:
            self.draw_popup()
            self.popup_win.refresh()
            key = self.game.stdscr.getch()

            # Navigate the option list
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0

            # Confirm selection
            if key == ord('\n'):  # Enter key
                if self.options_list[self.current_option] == "Go Back":
                    if self.page > 1:
                        self.page -= 1
                        self.update_options()
                    else:
                        return
                else:
                    if self.page < 3:
                        self.page += 1
                    if self.page == 3:
                        equip = self.diffbox()
                        if equip:
                            return
                    self.update_options()

    def update_options(self):
        if self.page == 1:
            self.options_list = ["Weapon", "OffHand", "Armor", "Ring", "Pendant", "Go Back"]
        elif self.page == 2:
            self.equip_type = self.options_list[self.current_option]
            if self.equip_type == "Go Back":
                self.page = 1
                self.update_options()
                return
            self.options_list = []
            for item in self.game.player_char.inventory.values():
                if self.game.player_char.cls.equip_check(item[0], self.equip_type):
                    self.options_list.append(item[0].name)
            if self.game.player_char.equipment[self.equip_type] != self.game.player_char.unequip(self.equip_type):
                self.options_list.append("Unequip")
            self.options_list.append("Go Back")
        else:
            pass
        self.current_option = 0

    def diffbox(self):
        if self.options_list[self.current_option] == "Unequip":
            item = self.game.player_char.unequip(typ=self.equip_type)
            confirm_str = f"Are you sure you want to unequip your {self.equip_type.lower()}?"
        else:
            item = self.game.player_char.inventory[self.options_list[self.current_option]][0]
            confirm_str = f"Are you sure you want to equip {item.name}?"
        diff_str = ""
        for line in self.game.player_char.equip_diff(item, self.equip_type).splitlines():
            mod, value = list(filter(None, line.split('  ')))
            diff_str += f"{mod:<16}{value:>29}\n"
        itembox = TextBox(self.game)
        itembox.print_text_in_rectangle(diff_str)
        self.game.stdscr.getch()
        confirm = ConfirmPopupMenu(self.game, confirm_str, box_height=7)
        if confirm.navigate_popup():
            self.game.player_char.equip(self.equip_type, item)
            return True
        return False


class AbilitiesPopupMenu(PopupMenu):
    def __init__(self, game, header_message):
        super().__init__(game, header_message)
        self.options_list = ["Spells", "Skills", "Go Back"]
        self.ability_type = None
        self.page = 1

    def navigate_popup(self):
        self.draw_popup()
        while True:
            self.draw_popup()
            self.popup_win.refresh()
            key = self.game.stdscr.getch()

            # Navigate the option list
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option > len(self.options_list) - 1:
                    self.current_option = 0

            # Confirm selection
            if key == ord('\n'):  # Enter key
                if self.options_list[self.current_option] == "Go Back":
                    self.page -= 1
                    if not self.page:
                        return
                else:
                    self.page += 1
                if self.page == 3:
                    self.inspect_ability()
                    return
                self.update_options()

    def update_options(self):
        if self.page == 1:
            self.ability_type = None
            self.options_list = ["Spells", "Skills", "Go Back"]
        else:
            self.ability_type = self.options_list[self.current_option]
            self.usable_abilities = self.game.player_char.usable_abilities(self.ability_type)
            if len(self.game.player_char.spellbook[self.ability_type]) == 0:
                specialsbox = TextBox(self.game)
                specialsbox.print_text_in_rectangle("You do not have any abilities.")
                self.game.stdscr.getch()
                specialsbox.clear_rectangle()
                self.page -= 1
                return
            self.options_list = []
            for name in self.game.player_char.spellbook[self.ability_type]:
                self.options_list.append(name)
            self.options_list.append("Go Back")
        self.current_option = 0

    def inspect_ability(self):
        ability = self.game.player_char.spellbook[self.ability_type][self.options_list[self.current_option]]
        abilitybox = TextBox(self.game)
        abilitybox.print_text_in_rectangle(str(ability))
        self.game.stdscr.getch()
        abilitybox.clear_rectangle()
        if (hasattr(ability, "cast_out") or hasattr(ability, "use_out")) and \
            ability.cost <= self.game.player_char.mana.current and not self.game.player_char.in_town():
            use_or_cast = "cast" if self.ability_type == "Spells" else "use"
            confirm_str = f"Do you want to {use_or_cast} {ability.name}?"
            confirm = ConfirmPopupMenu(self.game, confirm_str, box_height=6)
            if confirm.navigate_popup():
                if hasattr(ability, "cast_out"):
                    message = ability.cast_out(self.game)
                else:
                    message = ability.use_out(self.game)
                abilitybox.print_text_in_rectangle(message)
                self.game.stdscr.getch()
                abilitybox.clear_rectangle()


class QuestPopupMenu(PopupMenu):
    def __init__(self, game, box_height=20, box_width=30):
        super().__init__(game, "", box_height=box_height, box_width=box_width)

    def draw_popup(self, content):
        self.popup_win.erase()
        self.popup_win.box()
        delay = 0 if self.game.debug_mode else 0.075
        for i, line in enumerate(content):
            for j, char in enumerate(line):
                self.popup_win.addch(i + 1, j + 2, char)
                self.popup_win.refresh()
                time.sleep(delay)
        self.game.stdscr.getch()

    def navigate_popup(self):
        raise NotImplementedError


class QuestListPopupMenu(PopupMenu):

    def __init__(self, game, header_message):
        super().__init__(game, header_message, box_height=20, box_width=50)
        self.scroll_offset = 0  # Tracks the starting index of visible quests
        self.max_visible_options = self.box_height - 10  # Adjusted for header, bounties, and gap

    def draw_popup(self):
        self.update_options()
        h_adjust = 1
        self.popup_win.erase()

        # Draw header
        for i, line in enumerate(self.header_message):
            self.popup_win.addstr(1 + i, (self.box_width // 2) - (len(line) // 2), line, curses.A_BOLD)
        h_adjust += 2

        # Display up to 4 bounty quests
        self.popup_win.addstr(h_adjust, 13, "Bounties: Remaining/Total")
        h_adjust += 1
        for quest, info in self.game.player_char.quest_dict["Bounty"].items():
            if info[2]:
                self.popup_win.addstr(h_adjust, 16, f"{quest}: Completed")
            else:
                self.popup_win.addstr(h_adjust, 16, f"{quest}: {info[1]}/{info[0]['num']}")
            h_adjust += 1

        # Add a gap
        h_adjust += 1

        # Remaining space for quest list
        remaining_space = self.box_height - h_adjust - 2
        visible_options = self.options_list[self.scroll_offset:self.scroll_offset + remaining_space]
        for idx, option in enumerate(visible_options):
            display_idx = idx + h_adjust
            if display_idx >= self.box_height - 1:
                break  # Prevent drawing outside the box
            if idx + self.scroll_offset == self.current_option:
                self.popup_win.attron(curses.A_REVERSE)
            self.popup_win.addstr(display_idx, 2, option)
            if idx + self.scroll_offset == self.current_option:
                self.popup_win.attroff(curses.A_REVERSE)

        # Draw scroll indicators
        if self.scroll_offset > 0:
            self.popup_win.addstr(h_adjust - 1, self.box_width // 2 - 3, "↑", curses.A_BOLD)
        if self.scroll_offset + remaining_space < len(self.options_list):
            self.popup_win.addstr(self.box_height - 2, self.box_width // 2 - 3, "↓", curses.A_BOLD)

        self.popup_win.box()

    def navigate_popup(self):
        self.draw_popup()
        while True:
            self.draw_popup()
            self.popup_win.refresh()
            key = self.game.stdscr.getch()

            # Navigate the item list
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:  # Wrap around to the bottom
                    self.current_option = len(self.options_list) - 1
                    self.scroll_offset = max(0, self.current_option - self.max_visible_options + 1)
                elif self.current_option < self.scroll_offset:
                    self.scroll_offset -= 1

            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option >= len(self.options_list):  # Wrap around to the top
                    self.current_option = 0
                    self.scroll_offset = 0
                elif self.current_option >= self.scroll_offset + self.max_visible_options:
                    self.scroll_offset += 1

            # Confirm selection
            if key == ord('\n'):  # Enter key
                if self.options_list[self.current_option] == "Go Back":
                    return
                if self.options_list[self.current_option] == "Completed Quests":
                    self.completed_quests()
                else:
                    self.inspect_quests()

    def update_options(self):
        self.options_list = []
        self.completed = []
        for typ in ["Main", "Side"]:
            for quest, info in self.game.player_char.quest_dict[typ].items():
                if info["Turned In"]:
                    self.completed.append(quest)
                else:
                    self.options_list.append(quest)
        if self.completed:
            self.options_list.append("Completed Quests")
        self.options_list.append("Go Back")

    def inspect_quests(self):
        if self.options_list[self.current_option] in self.game.player_char.quest_dict["Main"]:
            quest = self.game.player_char.quest_dict["Main"][self.options_list[self.current_option]]
        else:
            quest = self.game.player_char.quest_dict["Side"][self.options_list[self.current_option]]
        questbox = TextBox(self.game)
        questbox.print_text_in_rectangle(self.quest_str_config(quest))
        self.game.stdscr.getch()
        questbox.clear_rectangle()

    def quest_str_config(self, quest):
        completed = "Yes" if quest["Completed"] else "No"
        what_str = quest["What"] if isinstance(quest["What"], str) else quest["What"]().name
        quest_str =  (f"{self.options_list[self.current_option]}\n\n"
                      f"{quest['Type']} {what_str}\n"
                      f"Questgiver: {quest['Who']}\n")
        if quest['Type'] == 'Collect':
            if quest['What'] == 'Relics':
                relics = ["Triangulus", "Quadrata", "Hexagonum", "Luna", "Polaris", "Infinitas"]
                current = sum([item in self.game.player_char.special_inventory for item in relics])
            else:
                try:
                    current = len(self.game.player_char.special_inventory[quest['What']().name])
                except KeyError:
                    current = 0
            quest_str += f"Collected: {current}/{quest['Total']}\n"
        quest_str += f"Completed: {completed}\n"
        return quest_str

    def completed_quests(self):
        questbox = TextBox(self.game)
        questbox.print_text_in_rectangle("\n".join(self.completed))
        self.game.stdscr.getch()
        questbox.clear_rectangle()


class TextBox:
    def __init__(self, game):
        self.game = game
        self.height, self.width = game.stdscr.getmaxyx()
        self.win = None
    
    def print_text_in_rectangle(self, text):
        # Calculate the position
        if "\n" in text:
            lines = text.splitlines()
        else:
            lines = wrap(text, 48, break_on_hyphens=False)
        rect_width = max(50, len(max(lines, key=len))+2)
        rect_height = len(lines) + 2
        start_y = (self.height - rect_height) // 2
        start_x = (self.width - rect_width) // 2

        # Create the window for the rectangle
        self.win = curses.newwin(rect_height, rect_width, start_y, start_x)
        self.win.box()

        # Center the text inside the rectangle
        for i, line in enumerate(lines):
            self.win.addstr(i + 1, (rect_width // 2) - (len(line) // 2), line)

        # Refresh to show the changes
        self.win.refresh()

    def clear_rectangle(self):
        self.win.erase()
        self.win.refresh()
