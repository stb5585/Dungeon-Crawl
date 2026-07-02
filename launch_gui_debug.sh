#!/bin/bash
# Launch The Forsaken Tenet with Pygame GUI

cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Set PYTHONPATH to include project root
export PYTHONPATH="$(pwd):$PYTHONPATH"
export DUNGEON_RENDERER_DEBUG_GEOMETRY=1
export DUNGEON_RENDERER_DISABLE_DARKNESS=1

# Optional ability-testing override:
# DUNGEON_FORCE_ENEMY=Test ./launch_gui_debug.sh
# export DUNGEON_FORCE_ENEMY=Test

# Optional noisy logging when chasing rendering bugs:
export DUNGEON_RENDERER_DEBUG_SCENE=1
export DUNGEON_RENDERER_DEBUG_COMMANDS=1
export DUNGEON_RENDERER_DEBUG_SURFACE_SLOTS=1

# Optional ability-testing override:
# export DUNGEON_FORCE_ENEMY=Bandit
unset DUNGEON_FORCE_ENEMY

# Run the GUI game
python game_pygame.py --debug
