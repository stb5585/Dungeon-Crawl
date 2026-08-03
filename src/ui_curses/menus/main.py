"""Main behavior for the menus package."""

import curses

from src.core.save_system import SaveManager


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
            if self.game.debug_mode and key in [ord('l'), ord('L')]:
                if hasattr(self.game, "debug_level_up"):
                    self.game.debug_level_up()
                continue
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
                # Racial traits (virtue/sin)
                try:
                    virtue = getattr(self.race, "virtue", None)
                    sin = getattr(self.race, "sin", None)
                    if virtue and getattr(virtue, "name", ""):
                        self.desc_win.addstr(j + k + 21, self.width // 3 - 6, "Virtue / Sin", curses.A_BOLD)
                        self.desc_win.addstr(j + k + 23, 3, f"Virtue: {virtue.name}")
                        if getattr(virtue, "description", ""):
                            self.desc_win.addstr(j + k + 24, 5, str(virtue.description)[: self.width // 3 - 8])
                    if sin and getattr(sin, "name", ""):
                        row = j + k + 26
                        self.desc_win.addstr(row, 3, f"Sin: {sin.name}")
                        if getattr(sin, "description", ""):
                            self.desc_win.addstr(row + 1, 5, str(sin.description)[: self.width // 3 - 8])
                except Exception:
                    pass
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
            loadfile = f"{self.options_list[self.current_option].lower()}.save"
            player_obj = SaveManager.load_player(loadfile)
            desc_lines = self.config_desc_str(player_obj).splitlines()
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

    def config_desc_str(self, player_obj):
        if player_obj is None:
            return getattr(
                SaveManager.last_load_result,
                "error",
                None,
            ) or "Corrupted save"
        desc_str = f"{getattr(player_obj, 'name', 'Unknown')}\n"
        level = getattr(getattr(player_obj, 'level', None), 'level', '?')
        race_name = getattr(getattr(player_obj, 'race', None), 'name', 'Unknown')
        cls_name = getattr(getattr(player_obj, 'cls', None), 'name', 'Unknown')
        desc_str += (f"Level {level} {race_name} {cls_name}\n")

        health = getattr(player_obj, 'health', None)
        mana = getattr(player_obj, 'mana', None)
        stats = getattr(player_obj, 'stats', None)

        if health and mana and stats:
            desc_str += (f"{'Hit Points:':13} {' ':1}{health.current:3}/{health.max:>3}\n"
                         f"{'Mana Points:':13} {' ':1}{mana.current:3}/{mana.max:>3}\n"
                         f"{'Strength:':13} {' ':1}{stats.strength:>7}\n"
                         f"{'Intelligence:':13} {' ':1}{stats.intel:>7}\n"
                         f"{'Wisdom:':13} {' ':1}{stats.wisdom:>7}\n"
                         f"{'Constitution:':13} {' ':1}{stats.con:>7}\n"
                         f"{'Charisma:':13} {' ':1}{stats.charisma:>7}\n"
                         f"{'Dexterity:':13} {' ':1}{stats.dex:>7}\n")
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
