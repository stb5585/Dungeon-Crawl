#!/bin/bash

(
    set -e
    cd "$(dirname "${BASH_SOURCE[0]}")"

    # export DUNGEON_RENDERER_DEBUG_GEOMETRY=1
    # export DUNGEON_RENDERER_DISABLE_DARKNESS=1
    # export DUNGEON_RENDERER_DEBUG_SCENE=1
    # export DUNGEON_RENDERER_DEBUG_COMMANDS=1
    # export DUNGEON_RENDERER_DEBUG_SURFACE_SLOTS=1

    # Force a specific encounter for debugging purposes.
    # export DUNGEON_FORCE_ENEMY=InvisibleStalker
    # export DUNGEON_FORCE_ENCOUNTER=burrow_and_bone

    # Set DUNGEON_FORCE_ENEMY before launch when a deterministic encounter is useful.
    exec ./.venv/bin/python game_pygame.py --debug "$@"
)
