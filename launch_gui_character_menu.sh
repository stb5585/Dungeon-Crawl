#!/bin/bash

(
    set -e
    cd "$(dirname "${BASH_SOURCE[0]}")"

    export DUNGEON_CRAWL_MODERN_CHARACTER_MENU=1

    exec ./.venv/bin/python game_pygame.py --character-menu "$@"
)
