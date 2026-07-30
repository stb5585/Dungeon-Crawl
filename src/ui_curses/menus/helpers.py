"""Helpers behavior for the menus package."""

import curses
import time


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
