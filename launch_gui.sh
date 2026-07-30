#!/bin/bash

(
    set -e
    cd "$(dirname "${BASH_SOURCE[0]}")"

    unset DUNGEON_RENDERER_DEBUG_GEOMETRY
    unset DUNGEON_RENDERER_DISABLE_DARKNESS
    unset DUNGEON_RENDERER_DEBUG_SCENE
    unset DUNGEON_RENDERER_DEBUG_COMMANDS
    unset DUNGEON_RENDERER_DEBUG_SURFACE_SLOTS

    exec ./.venv/bin/python game_pygame.py "$@"
)
