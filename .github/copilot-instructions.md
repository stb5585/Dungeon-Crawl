# Copilot instructions for Dungeon Crawl

You are an expert Python developer familiar with The Forsaken Tenet / Dungeon Crawl codebase. Provide code completions and suggestions that align with the project's architecture, coding conventions, and design patterns as outlined below.

## Big-picture architecture
- `src/core/` is the UI-agnostic game engine (combat, characters, items, data, events). Keep core logic here.
- `src/ui_curses/` and `src/ui_pygame/` are the two UI layers; they own battle managers and presentation logic.
- Combat is event-driven: `src/core/events/event_bus.py` defines `EventBus` + `EventType`. Shared combat flow lives in `src/core/combat/battle_engine.py`; character and ability code emit supporting events from `src/core/character.py`, `src/core/abilities.py`, and data-driven effect helpers.
- Event emissions are non-breaking and wrapped in try/except, so logic must still work if no subscribers exist.
- UI-specific presentation lives in `src/ui_curses/` and `src/ui_pygame/`; UIs should adapt core APIs instead of moving mechanics out of `src/core/`.

## Data-driven systems
- Ability definitions live in `src/core/data/abilities/` and load via `src/core/data/ability_loader.py`.
- Effects are composable in `src/core/effects/` (Composite/Chance/Conditional effects); prefer these over ad-hoc status logic when practical.
- Content data (quests/dialogues/special events) is JSON in `src/core/data/content/` and loaded via `src/core/data/data_loader.py`.

## Combat specifics
- Shared combat uses `src/core/combat/battle_engine.py`, with priority/action-queue helpers in `src/core/combat/action_queue.py` and `src/core/combat/initiative.py`.
- Battle analytics are centralized in `src/core/combat/battle_logger.py` and used by both UIs.
- Charging abilities use `delay`/`charge_time` + telegraph messages; the Seeker/Inquisitor sees detailed telegraphs.

## Workflow & commands
- Run terminal game: `./launch.sh` or `./.venv/bin/python game_curses.py`.
- Run pygame game: `./launch_gui.sh` or `./.venv/bin/python game_pygame.py`.
- Dev tools: `./.venv/bin/python tools/dev_tools.py [effects|queue|events|abilities|balance]`.
- Tests: `./.venv/bin/python -m pytest tests/ -q` (see `tests/README.md` for patterns).

## Project conventions
- Absolute imports (`src.core.*`) are expected for cross-context execution.
- Paths are resolved with `Path(__file__).parent` for test compatibility.
- Keep UI-free logic in `src/core/`; UI layers should adapt core APIs instead of modifying them.
- Enemy combat sprite review sheets are script-based: use `./.venv/bin/python tools/build_enemy_combat_sprites.py` for approved transparent PNG assets.
