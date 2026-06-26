#!/bin/bash
# Launch directly into the Pygame first-person town navigation prototype.

set -e

cd "$(dirname "$0")"

source .venv/bin/activate
export PYTHONPATH="$(pwd):$PYTHONPATH"

unset DUNGEON_RENDERER_DEBUG_GEOMETRY
unset DUNGEON_RENDERER_DISABLE_DARKNESS
unset DUNGEON_RENDERER_DEBUG_SCENE
unset DUNGEON_RENDERER_DEBUG_COMMANDS
unset DUNGEON_RENDERER_DEBUG_SURFACE_SLOTS

python game_pygame.py --town-navigation --preview-name "Town Preview" "$@"
