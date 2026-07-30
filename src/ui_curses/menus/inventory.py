"""Inventory behavior for the menus package."""

import curses

from src.core import map_tiles
import src.ui_curses.menus as menus
from .foundation import PopupMenu


class InventoryPopupMenu(PopupMenu):
    def __init__(self, game, header_message):
        super().__init__(game, header_message)
        self.pages = [0]
        self.page = 0
        self.sort_modes = ["Name", "Type", "Quantity", "Combat"]
        self.sort_mode_idx = 0

    def _is_combat_usable(self, item) -> bool:
        subtyp = getattr(item, "subtyp", None)
        return (
            subtyp in ("Health", "Mana", "Elixir", "Status")
            or (subtyp == "Scroll" and getattr(item, "name", "") != "Sanctuary Scroll")
        )

    def _sorted_inventory_keys(self, inventory_dict):
        keys = list(inventory_dict.keys())
        mode = self.sort_modes[self.sort_mode_idx]
        if mode == "Combat":
            combat_keys = [
                key for key in keys
                if inventory_dict.get(key) and self._is_combat_usable(inventory_dict[key][0])
            ]
            non_combat_keys = [
                key for key in keys
                if not (inventory_dict.get(key) and self._is_combat_usable(inventory_dict[key][0]))
            ]
            return sorted(combat_keys, key=lambda key: str(key).lower()) + non_combat_keys
        if mode == "Type":
            return sorted(keys, key=lambda key: (
                str(getattr(inventory_dict[key][0], "subtyp", "")),
                str(key).lower(),
            ))
        if mode == "Quantity":
            return sorted(keys, key=lambda key: (-len(inventory_dict[key]), str(key).lower()))
        return sorted(keys, key=lambda key: str(key).lower())

    def cycle_sort_mode(self):
        self.sort_mode_idx = (self.sort_mode_idx + 1) % len(self.sort_modes)
        self.page = 0
        self.current_option = 0

    def draw_popup(self):
        self.update_itemlist()
        self.popup_win.erase()
        line_offset = 0
        for i, line in enumerate(self.header_message):
            self.popup_win.addstr(1 + i, (self.box_width // 2) - (len(line) // 2), line, curses.A_BOLD)
            line_offset = i + 1
        list_start = 3 + line_offset
        if self.header_message and self.header_message[0] == "Inventory":
            sort_line = f"Sort: {self.sort_modes[self.sort_mode_idx]} (press S)"
            self.popup_win.addstr(2 + line_offset, max(2, (self.box_width // 2) - (len(sort_line) // 2)), sort_line)
            list_start += 1
        # Display item list
        for idx, item in enumerate(self.options_list):
            if idx == self.current_option:
                self.popup_win.attron(curses.A_REVERSE)
            length = '' if not len(item[1]) else len(item[1])
            item_str = f"{item[0]:24}{length:2}"
            self.popup_win.addstr(list_start + idx, 2, item_str)
            if idx == self.current_option:
                self.popup_win.attroff(curses.A_REVERSE)
        self.popup_win.box()

    def update_itemlist(self):
        self.options_list = []
        if self.header_message[0] == "Inventory":
            sorted_keys = self._sorted_inventory_keys(self.game.player_char.inventory)
            inv_len = len(sorted_keys)
            total_pages = max(1, (inv_len + 13) // 14)
            self.pages = list(range(total_pages))
            self.page = min(self.page, total_pages - 1)
            start_item_idx = self.page * 14
            if inv_len > 0:
                inventory_keys = sorted_keys[start_item_idx:start_item_idx+14]
                for key in inventory_keys:
                    self.options_list.append((key, self.game.player_char.inventory[key]))
        elif self.header_message[0] == "Key Items":
            inv_len = len(self.game.player_char.special_inventory)
            total_pages = max(1, (inv_len + 13) // 14)
            self.pages = list(range(total_pages))
            self.page = min(self.page, total_pages - 1)
            start_item_idx = self.page * 14
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
            box = menus.TextBox(self.game)
            box.print_text_in_rectangle("You do not have any items in your inventory.")
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
            elif key in (ord('s'), ord('S')) and self.header_message and self.header_message[0] == "Inventory":
                self.cycle_sort_mode()

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
        try:
            map_tiles.reveal_chalice_map_on_inspect(self.game.player_char, item)
        except Exception:
            pass
        itembox = menus.TextBox(self.game)
        if getattr(item, "name", "") == "Chalice Map":
            preview = map_tiles.chalice_map_preview_text(self.game.player_char)
            if preview:
                itembox.print_text_in_rectangle(preview)
                itembox.clear_rectangle()
                return
        itembox.print_text_in_rectangle(str(item))
        itembox.clear_rectangle()


class EquipPopupMenu(PopupMenu):

    def __init__(self, game, header_message, box_height):
        super().__init__(game, header_message, box_height=box_height)
        self.options_list = ["Weapon", "OffHand", "Armor", "Helmet", "Ring", "Pendant", "Go Back"]
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
            self.options_list = ["Weapon", "OffHand", "Armor", "Helmet", "Ring", "Pendant", "Go Back"]
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
        itembox = menus.TextBox(self.game)
        itembox.print_text_in_rectangle(diff_str)
        confirm = menus.ConfirmPopupMenu(self.game, confirm_str, box_height=7)
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
                specialsbox = menus.TextBox(self.game)
                specialsbox.print_text_in_rectangle("You do not have any abilities.")
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
        abilitybox = menus.TextBox(self.game)
        abilitybox.print_text_in_rectangle(str(ability))
        abilitybox.clear_rectangle()
        if (hasattr(ability, "cast_out") or hasattr(ability, "use_out")) and \
            ability.cost <= self.game.player_char.mana.current and not self.game.player_char.in_town():
            use_or_cast = "cast" if self.ability_type == "Spells" else "use"
            confirm_str = f"Do you want to {use_or_cast} {ability.name}?"
            confirm = menus.ConfirmPopupMenu(self.game, confirm_str, box_height=6)
            if confirm.navigate_popup():
                if hasattr(ability, "cast_out"):
                    message = ability.cast_out(self.game)
                else:
                    message = ability.use_out(self.game)
                abilitybox.print_text_in_rectangle(message)
                abilitybox.clear_rectangle()
