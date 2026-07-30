#!/usr/bin/env python3
"""
Entry point for The Forsaken Tenet - Curses (Terminal) Version
Run the game with: python game_curses.py
"""

from src.ui_curses.game import main as curses_main


def main():
    """Main entry point for curses version."""
    return curses_main()


if __name__ == "__main__":
    main()
