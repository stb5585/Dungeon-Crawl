# The Forsaken Tenet

The Forsaken Tenet is a Python 3.12+ dungeon-crawl RPG with terminal and
Pygame frontends. Code and some legacy docs may still refer to the project as
Dungeon Crawl until the rename cleanup is finished.

## Current Status

The current source of truth is
[docs/DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md). As of the latest
roadmap pass:

- Core gameplay lives under `src/core/` and is shared by both UIs.
- Terminal/curses UI lives under `src/ui_curses/`.
- Pygame UI lives under `src/ui_pygame/`.
- Ability data is substantially migrated to YAML under
  `src/core/data/abilities/`.
- P4 content and systems expansion is active; completed P4e class-kit scope and
  deferred deep-kit gates are tracked in
  [docs/P4E_CLASS_KIT_SPECS.md](docs/P4E_CLASS_KIT_SPECS.md).
- Older phase/migration docs are retained for historical context, not as the
  current backlog.

## Requirements

- Python 3.12+
- Project virtual environment at `./.venv/`
- Runtime packages include `numpy`, `PyYAML`, `pygame`, and `Pillow`

Always prefer the project virtual environment for Python commands:

```bash
./.venv/bin/python -m pytest tests/core -q
./.venv/bin/python tools/dev_tools.py --help
```

## Running The Game

```bash
# Terminal/curses version
./launch.sh

# Pygame version
./launch_gui.sh

# Direct Pygame entry point
./.venv/bin/python game_pygame.py

# Character Menu preview
./launch_gui_character_menu.sh
./.venv/bin/python game_pygame.py --character-menu
```

## Testing

Run focused tests for the area you changed:

```bash
./.venv/bin/python -m pytest tests/core -q
./.venv/bin/python -m pytest tests/ui_pygame -q
./.venv/bin/python -m pytest tests/integration -q
```

Run the full suite when broader validation is needed:

```bash
./.venv/bin/python -m pytest tests/ -q
```

See [tests/README.md](tests/README.md) for current coverage notes and test
layout.

## Repository Layout

```text
src/
  core/          Shared game logic, combat, data, classes, items, saves
  ui_curses/     Terminal UI
  ui_pygame/     Pygame UI, assets, renderer, menus, combat view

docs/            Roadmap, active specs, implementation notes, archive
map_files/       Dungeon maps
tools/           Development, asset, audio, and balance utilities
tests/           Regression suite

game_curses.py   Terminal entry point
game_pygame.py   Pygame entry point
```

## Documentation

Start with [docs/README.md](docs/README.md). The most useful current docs are:

- [docs/DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md)
- [docs/P4E_CLASS_KIT_SPECS.md](docs/P4E_CLASS_KIT_SPECS.md)
- [docs/CLASS_RING_ACTIVATION_SPEC.md](docs/CLASS_RING_ACTIVATION_SPEC.md)
- [docs/MAIN_STORYLINE_PLOT_SPEC.md](docs/MAIN_STORYLINE_PLOT_SPEC.md)
- [docs/PLAYTEST_CHECKLIST.md](docs/PLAYTEST_CHECKLIST.md)
- [docs/ENEMY_VISUAL_SYSTEM.md](docs/ENEMY_VISUAL_SYSTEM.md)
- [docs/DUNGEON_TILE_ART.md](docs/DUNGEON_TILE_ART.md)

## Development Tools

```bash
./.venv/bin/python tools/dev_tools.py effects
./.venv/bin/python tools/dev_tools.py queue
./.venv/bin/python tools/dev_tools.py events
./.venv/bin/python tools/dev_tools.py abilities --directory src/core/data/abilities
./.venv/bin/python tools/run_balance_suite.py --help
```

See [tools/README.md](tools/README.md) for more.
