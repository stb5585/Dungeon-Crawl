"""Quests behavior for the menus package."""

import curses
import time

import src.ui_curses.menus as menus
from .foundation import PopupMenu


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
        self.display_to_quest = {}

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
                self.popup_win.addstr(h_adjust, 16, f"{quest}: Complete")
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
                    continue  # Section header, not selectable
                if self.options_list[self.current_option] == "Turned In":
                    self.show_turned_in()
                else:
                    self.inspect_quests()

    def update_options(self):
        self.options_list = []
        active = []
        self.completed = []   # completed but not turned in
        self.turned_in = []
        self.display_to_quest = {}
        for typ in ["Main", "Side"]:
            for quest, info in self.game.player_char.quest_dict[typ].items():
                if info["Turned In"]:
                    self.turned_in.append(quest)
                elif info["Completed"]:
                    self.completed.append(quest)
                    self.display_to_quest[quest] = quest
                else:
                    active.append(quest)
                    self.display_to_quest[quest] = quest
        self.options_list.extend(active)
        if self.completed:
            self.options_list.append("Completed Quests")
            self.options_list.extend(self.completed)
        if self.turned_in:
            self.options_list.append("Turned In")
        self.options_list.append("Go Back")

    def inspect_quests(self):
        option = self.options_list[self.current_option]
        quest_name = self.display_to_quest.get(option, option)
        if quest_name in self.game.player_char.quest_dict["Main"]:
            quest = self.game.player_char.quest_dict["Main"][quest_name]
        else:
            quest = self.game.player_char.quest_dict["Side"][quest_name]
        questbox = menus.TextBox(self.game)
        questbox.print_text_in_rectangle(self.quest_str_config(quest))
        questbox.clear_rectangle()

    def quest_str_config(self, quest):
        completed = "Yes" if quest["Completed"] else "No"
        turned_in = "Yes" if quest["Turned In"] else "No"
        what_str = quest["What"] if isinstance(quest["What"], str) else quest["What"].name
        quest_str =  (f"{self.options_list[self.current_option]}\n\n"
                      f"{quest['Type']} {what_str}\n"
                      f"Questgiver: {quest['Who']}\n")
        if quest['Type'] == 'Collect':
            if quest['What'] == 'Relics':
                relics = ["Triangulus", "Quadrata", "Hexagonum", "Luna", "Polaris", "Infinitas"]
                current = sum([item in self.game.player_char.special_inventory for item in relics])
            else:
                try:
                    current = len(self.game.player_char.special_inventory[quest['What'].name])
                except KeyError:
                    current = 0
            quest_str += f"Collected: {current}/{quest['Total']}\n"
        quest_str += f"Completed: {completed}\n"
        quest_str += f"Turned In: {turned_in}\n"
        return quest_str

    def completed_quests(self):
        questbox = menus.TextBox(self.game)
        questbox.print_text_in_rectangle("\n".join(self.completed))
        questbox.clear_rectangle()

    def show_turned_in(self):
        questbox = menus.TextBox(self.game)
        if self.turned_in:
            questbox.print_text_in_rectangle("\n".join(self.turned_in))
        else:
            questbox.print_text_in_rectangle("No turned in quests.")
        questbox.clear_rectangle()
