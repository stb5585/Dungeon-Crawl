#!/bin/bash

set -e
cd "$(dirname "$0")"

exec ./.venv/bin/python game_curses.py "$@"
