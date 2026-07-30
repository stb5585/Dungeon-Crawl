"""Navigation behavior for the menus package."""

import curses
from textwrap import wrap

from src.core import items as items_module
from src.core.classes import astromancer
from .helpers import ascii_art


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
        if self.game.player_char.state == 'fight' and self.room.enemy:
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
        options = f"Move Forward (w)\n\nTurn Left (a)\tTurn Right (d)\n\nMove Backward (s)"
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

    def _effect_label(self, effect_name):
        labels = {
            "Berserk": "BRK",
            "Blind": "BLD",
            "Doom": "DOM",
            "Poison": "PSN",
            "Silence": "SIL",
            "Sleep": "SLP",
            "Stun": "STN",
            "Defend": "DEF",
            "Steal Success": "STE",
            "Bleed": "RND",
            "Disarm": "DSA",
            "Prone": "PRN",
            "Attack": "ATK",
            "Defense": "DEF",
            "Magic": "MAG",
            "Magic Defense": "MDF",
            "Speed": "SPD",
            "DOT": "DOT",
            "Duplicates": "DUP",
            "Ice Block": "ICE",
            "Mana Shield": "MSH",
            "Reflect": "RFL",
            "Regen": "REG",
            "Resist Fire": "RF",
            "Resist Ice": "RI",
            "Resist Electric": "RE",
            "Resist Water": "RW",
            "Resist Earth": "RTH",
            "Resist Wind": "RWI",
            "Jump": "JMP",
            "Power Up": "PWR",
        }
        return labels.get(effect_name, effect_name[:3].upper())

    def _collect_status_icons(self, character):
        icons = []
        skip_effects = {
            "DOT",
            "Duplicates",
            "Jump",
            "Power Up",
            "Shapeshifted",
            "Steal Success",
        }
        positive_status = {"Defend", "Steal Success"}
        positive_magic = {
            "Duplicates",
            "Ice Block",
            "Mana Shield",
            "Reflect",
            "Regen",
            "Resist Fire",
            "Resist Ice",
            "Resist Electric",
            "Resist Water",
            "Resist Earth",
            "Resist Wind",
        }

        for name, effect in character.status_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), name in positive_status))
        for name, effect in character.physical_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), False))
        for name, effect in character.stat_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), effect.extra >= 0))
        for name, effect in character.magic_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), name in positive_magic))
        for name, effect in character.class_effects.items():
            if effect.active and name not in skip_effects:
                icons.append((self._effect_label(name), True))

        # Maelstrom Weapon passive stack indicator (Soulcatcher/Shaman)
        try:
            maelstrom_hits = int(getattr(character, "maelstrom_hits", 0))
            skills = getattr(character, "spellbook", {}).get("Skills", {})
            has_maelstrom = "Maelstrom Weapon" in skills
            if has_maelstrom and maelstrom_hits > 0:
                icons.append((f"MW{maelstrom_hits}", True))
        except (AttributeError, TypeError, ValueError):
            pass

        return icons

    def _format_status_icons(self, character):
        icons = self._collect_status_icons(character)
        if not icons:
            return ""
        parts = []
        for label, is_positive in icons:
            prefix = "+" if is_positive else "-"
            parts.append(f"{prefix}{label}")
        return " ".join(parts)

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

        status_text = self._format_status_icons(enemy)
        if status_text:
            max_width = self.width - 4
            if len(status_text) > max_width:
                status_text = status_text[:max_width - 3] + "..."
            self.enemy_win.addstr((3 * self.height // 4) - 1, (self.width // 2) - (len(status_text) // 2), status_text)

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

        status_row = 8
        if astromancer.has_rune_system(char):
            max_width = (self.width // 2) - 4
            rune_parts = []
            if astromancer.is_astromancer(char):
                rune_parts.append(f"Sign {astromancer.active_constellation(char)}")
            rune_parts.extend(astromancer.rune_grid_lines(char))
            rune_text = " | ".join(rune_parts)
            if len(rune_text) > max_width:
                rune_text = rune_text[:max_width - 3] + "..."
            self.char_win.addstr(8, (self.width // 4) - (len(rune_text) // 2), rune_text)
            status_row = 9

        status_text = self._format_status_icons(char)
        if status_text:
            max_width = (self.width // 2) - 4
            if len(status_text) > max_width:
                status_text = status_text[:max_width - 3] + "..."
            self.char_win.addstr(status_row, (self.width // 4) - (len(status_text) // 2), status_text)
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
                return self.options_list[self.current_option]


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
        self.scroll_offset = 0
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

        # Calculate available space for displaying options
        # Reserve space for: optional message (3 lines), box border, scroll indicators
        base_y = (3 * self.height // 8) - (len(self.options_list) // 2) - 2
        if self.options_message:
            self.options_win.addstr(base_y, (self.width // 2) - (len(self.options_message) // 2),
                                    self.options_message, curses.A_BOLD)
            start_y = base_y + 2
        else:
            start_y = base_y

        # Calculate max visible options based on window height
        max_visible = (11 * self.height // 12) - start_y - 4  # Reserve space for borders and indicators

        # Determine which options to display (windowed view)
        visible_options = self.options_list[self.scroll_offset:self.scroll_offset + max_visible]

        # Draw visible options
        for idx, line in enumerate(visible_options):
            display_y = start_y + idx
            actual_idx = idx + self.scroll_offset

            if actual_idx == self.current_option:
                self.options_win.attron(curses.A_REVERSE)
            self.options_win.addstr(display_y, (self.width // 2) - (len(line) // 2), line)
            if actual_idx == self.current_option:
                self.options_win.attroff(curses.A_REVERSE)

        # Draw scroll indicators
        if self.scroll_offset > 0:
            # Up arrow indicator
            self.options_win.addstr(start_y - 1, (self.width // 2) - 3, "↑ More", curses.A_BOLD)
        if self.scroll_offset + max_visible < len(self.options_list):
            # Down arrow indicator
            indicator_y = min(start_y + len(visible_options), (11 * self.height // 12) - 2)
            self.options_win.addstr(indicator_y, (self.width // 2) - 3, "↓ More", curses.A_BOLD)

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
            self.scroll_offset = 0
        else:
            # Clamp current_option and scroll_offset to valid ranges when list size changes
            self.current_option = min(self.current_option, max(0, len(options) - 1))
            self.scroll_offset = min(self.scroll_offset, max(0, len(options) - 1))
        self.options_list = options
        self.options_message = options_message

    def navigate_menu(self):
        # Calculate max visible items (same as in draw_options)
        base_y = (3 * self.height // 8) - (len(self.options_list) // 2) - 2
        start_y = base_y + 2 if self.options_message else base_y
        max_visible = (11 * self.height // 12) - start_y - 4

        while True:
            self.draw_all()
            self.refresh_all()
            key = self.game.stdscr.getch()
            if key == curses.KEY_UP:
                self.current_option -= 1
                if self.current_option < 0:
                    self.current_option = len(self.options_list) - 1
                    # Jump to bottom, adjust scroll
                    self.scroll_offset = max(0, len(self.options_list) - max_visible)
                elif self.current_option < self.scroll_offset:
                    # Scroll up
                    self.scroll_offset = self.current_option
            elif key == curses.KEY_DOWN:
                self.current_option += 1
                if self.current_option >= len(self.options_list):
                    # Wrap to top
                    self.current_option = 0
                    self.scroll_offset = 0
                elif self.current_option >= self.scroll_offset + max_visible:
                    # Scroll down
                    self.scroll_offset = self.current_option - max_visible + 1
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
                for idx, metadata_line in enumerate(items_module.item_metadata_lines(item)):
                    self.item_desc_win.addstr(
                        self.height // 8 + len(lines) + idx + 1 - (len(lines) // 2),
                        (self.width // 3) - (len(metadata_line) // 2),
                        metadata_line,
                    )
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
            adj_scale = self.game.player_char.shop_price_scale()
            for typ, lst in self.itemdict.items():
                for item in lst:
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

    def __init__(self, game, options_list=None):
        self.game = game
        self.height, self.width = game.stdscr.getmaxyx()
        self.options_list = options_list if options_list is not None else []
        self.current_option = 0
        self.rows, self.cols = (3, 2)
        self.create_windows()

    def create_windows(self):
        self.options_win = curses.newwin(self.height // 4, 3 * self.width // 5, 0, 0)  # top left
        self.player_loc_win = curses.newwin(self.height // 7, 2 * self.width // 5, 0, 3 * self.width // 5)  # top right top
        self.info_win = curses.newwin(self.height // 7 - 1, 2 * self.width // 5, self.height // 8 + 1, 3 * self.width // 5)  # top right bottom
        self.status_win = curses.newwin(3 * self.height // 4, self.width, self.height // 4, 0)  # bottom

    def set_options(self, options_list):
        """Set the options list for the menu."""
        self.options_list = options_list
        self.current_option = 0

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
