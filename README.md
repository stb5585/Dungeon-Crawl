# The Forsaken Tenet

The Forsaken Tenet is a Python 3.12+ visual dungeon-crawl RPG built with
Pygame. Some legacy module names and archived documents still refer to the
earlier Dungeon Crawl working title.

## Current Status

The current source of truth is
[docs/DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md). As of the latest
roadmap pass:

- Core gameplay lives under `src/core/`.
- The supported visual frontend lives under `src/ui_pygame/`.
- Terminal development remains available through tests, simulators, reports,
  and diagnostic tools rather than a second playable frontend.
- Ability data is substantially migrated to YAML under
  `src/core/data/abilities/`.
- Current P4-P7 content slices are completed; P8 playtest readiness and
  evidence collection are the active roadmap lane.
- Completed class-kit scope and deferred deep-kit gates are tracked in
  [docs/CLASS_KIT_DESIGN_GATES.md](docs/CLASS_KIT_DESIGN_GATES.md).
- Combat architecture and balance decisions are specified in
  [docs/COMBAT_BALANCE_DESIGN_GATES.md](docs/COMBAT_BALANCE_DESIGN_GATES.md)
  before gameplay or balance rules change.
- Presentation, dungeon/world/encounter, and equipment/economy work now have
  dedicated design-gate docs linked from the roadmap and docs index.
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
# Standard Pygame launch
./launch.sh

# Explicit Pygame alias
./launch_gui.sh

# Direct Pygame entry point
./.venv/bin/python game_pygame.py

# Character Menu preview
./launch_gui_character_menu.sh
./.venv/bin/python game_pygame.py --character-menu
```

## Terminal Development

The retired curses frontend remains recoverable from the Git tag
`curses-ui-final`. Current terminal workflows exercise the shared engine
without maintaining a second player-facing UI:

```bash
./.venv/bin/python -m pytest tests/core -q
./.venv/bin/python -m pytest tests/integration -q
./.venv/bin/python tools/dev_tools.py effects
./.venv/bin/python tools/dev_tools.py events
./.venv/bin/python tools/run_balance_suite.py --tier base --level 10 --iters 30 --seed 1337
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
  ui_pygame/     Pygame UI, assets, renderer, menus, combat view

docs/            Roadmap, durable design references, implementation notes, archive
map_files/       Dungeon maps
tools/           Development, asset, audio, and balance utilities
tests/           Regression suite

game_pygame.py   Pygame entry point
```

## Documentation

Start with [docs/README.md](docs/README.md). The most useful current docs are:

- [docs/DEVELOPMENT_ROADMAP.md](docs/DEVELOPMENT_ROADMAP.md)
- [docs/CLASS_KIT_DESIGN_GATES.md](docs/CLASS_KIT_DESIGN_GATES.md)
- [docs/COMBAT_BALANCE_DESIGN_GATES.md](docs/COMBAT_BALANCE_DESIGN_GATES.md)
- [docs/CLASS_RING_SYSTEM.md](docs/CLASS_RING_SYSTEM.md)
- [docs/PRESENTATION_ASSET_DESIGN_GATES.md](docs/PRESENTATION_ASSET_DESIGN_GATES.md)
- [docs/DUNGEON_WORLD_ENCOUNTER_DESIGN_GATES.md](docs/DUNGEON_WORLD_ENCOUNTER_DESIGN_GATES.md)
- [docs/EQUIPMENT_ITEMS_ECONOMY_DESIGN_GATES.md](docs/EQUIPMENT_ITEMS_ECONOMY_DESIGN_GATES.md)
- [docs/STORY_AND_ENDGAME_DESIGN.md](docs/STORY_AND_ENDGAME_DESIGN.md)
- [docs/PLAYTEST_CHECKLIST.md](docs/PLAYTEST_CHECKLIST.md)
- [docs/ENEMY_VISUAL_SYSTEM.md](docs/ENEMY_VISUAL_SYSTEM.md)
- [docs/DUNGEON_TILE_ART.md](docs/DUNGEON_TILE_ART.md)

## Development Tools

```bash
./.venv/bin/python tools/dev_tools.py effects
./.venv/bin/python tools/dev_tools.py queue
./.venv/bin/python tools/dev_tools.py events
./.venv/bin/python tools/dev_tools.py abilities --directory src/core/data/abilities
./.venv/bin/python tools/run_balance_suite.py --tier base --level 10 --iters 30 --seed 1337
```

See [tools/README.md](tools/README.md) for more.
