"""Foundation behavior for the menus package."""

import curses
from textwrap import wrap


class PopupMenu:

    def __init__(self, game, header_message=None, box_height=20, box_width=30):
        self.game = game
        self.screen_height, self.screen_width = game.stdscr.getmaxyx()
        self.header_message = wrap(header_message, box_width - 2, break_on_hyphens=False) if header_message else header_message
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
        if self.header_message:
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


class ConfirmPopupMenu(PopupMenu):
    def __init__(self, game, header_message, box_height=None):
        if not box_height:
            wrapped = wrap(header_message, 28, break_on_hyphens=False) if header_message else []
            box_height = max(7, len(wrapped) + 6)
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


class TextBox:
    def __init__(self, game):
        """Cross-backend text box."""
        self.game = game
        self.win = None
        self.height, self.width = game.stdscr.getmaxyx()

    def print_text_in_rectangle(self, text):
        if "\n" in text:
            lines = text.splitlines()
        else:
            lines = wrap(text, 48, break_on_hyphens=False)
        rect_width = max(50, len(max(lines, key=len)) + 2)
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
        self.game.stdscr.getch()

    def clear_rectangle(self):
        if self.win:
            self.win.erase()
            self.win.refresh()
