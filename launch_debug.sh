#!/bin/bash

(
    set -e
    cd "$(dirname "${BASH_SOURCE[0]}")"

    printf '\e[8;37;120t'
    exec ./.venv/bin/python game_curses.py --debug "$@"
)
