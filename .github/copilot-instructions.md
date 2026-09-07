# Copilot instructions for Dungeon Crawl

You are an expert Python developer familiar with The Forsaken Tenet / Dungeon Crawl codebase. Provide code completions and suggestions that align with the project's architecture, coding conventions, and design patterns as outlined below.

## Big-picture architecture
- `src/core/` is the UI-agnostic game engine (combat, characters, items, data, events). Keep core logic here.
- `src/ui_pygame/` is the supported player-facing UI and owns presentation
  logic. The retired curses frontend is archived at Git tag
  `curses-ui-final`.
- Combat is event-driven: `src/core/events/event_bus.py` defines `EventBus` and
  `EventType`. Shared combat flow lives in the
  `src/core/combat/battle_engine/` package; character and ability code emit
  supporting events from the `src/core/character/` and
  `src/core/abilities/` packages and data-driven effect helpers.
- Event emissions are non-breaking and wrapped in try/except, so logic must still work if no subscribers exist.
- UI-specific presentation lives in `src/ui_pygame/`; it should adapt core
  APIs instead of moving mechanics out of `src/core/`.

## Data-driven systems
- Ability definitions live in `src/core/data/abilities/` and load through the
  `src/core/data/ability_loader/` package.
- Effects are composable in `src/core/effects/` (Composite/Chance/Conditional effects); prefer these over ad-hoc status logic when practical.
- Content data (quests/dialogues/special events) is JSON in `src/core/data/content/` and loaded via `src/core/data/data_loader.py`.

## Combat specifics
- Shared combat uses the `src/core/combat/battle_engine/` package, with
  priority/action-queue helpers in `src/core/combat/action_queue.py` and actor
  ordering in `src/core/combat/actor_cycle.py`.
- Battle analytics are centralized in `src/core/combat/battle_logger.py`.
- Charging abilities use `delay`/`charge_time` + telegraph messages; the Seeker/Inquisitor sees detailed telegraphs.

## Workflow & commands
- Run the game with `./launch.sh` or `./.venv/bin/python game_pygame.py`.
  Use `./launch_character_menu.sh` for the character preview and
  `./launch_debug.sh` for the debug launcher.
- Terminal-only development uses pytest, `tools/dev_tools.py`, combat
  simulators, and balance reports.
- Dev tools: `./.venv/bin/python tools/dev_tools.py [effects|queue|events|abilities|balance]`.
- Tests: `./.venv/bin/python -m pytest tests/ -q` (see `tests/README.md` for patterns).

## Project conventions
- Absolute imports (`src.core.*`) are expected for cross-context execution.
- Read-only resources resolve through `src.paths`; saves, temporary files,
  configuration, and logs use its platform user-data paths.
- Keep UI-free logic in `src/core/`; UI layers should adapt core APIs instead of modifying them.
- Enemy combat sprite review sheets are script-based: use `./.venv/bin/python tools/build_enemy_combat_sprites.py` for approved transparent PNG assets.
