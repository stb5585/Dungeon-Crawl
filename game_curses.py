#!/usr/bin/env python3
"""
Entry point for Dungeon Crawl - Curses (Terminal) Version
Run the game with: python game_curses.py
"""

import curses
import sys

from src.ui_curses.game import Game


def main():
    """Main entry point for curses version."""
    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        curses.wrapper(Game, **{'debug_mode': True})
    else:
        curses.wrapper(Game)


if __name__ == "__main__":
    main()
