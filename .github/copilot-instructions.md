# Copilot instructions for Dungeon Crawl

You are an export Python developer familiar with the Dungeon Crawl codebase. Provide code completions and suggestions that align with the project's architecture, coding conventions, and design patterns as outlined below.

## Big-picture architecture
- `src/core/` is the UI-agnostic game engine (combat, characters, items, data, events). Keep core logic here.
- `src/ui_curses/` and `src/ui_pygame/` are the two UI layers; they own battle managers and presentation logic.
- Combat is event-driven: `src/core/events/event_bus.py` defines `EventBus` + `EventType`. Combat flow emits events in `src/core/combat/enhanced_manager.py`, `src/core/battle.py`, `src/core/character.py`, and `src/core/abilities.py`.
- Event emissions are non-breaking and wrapped in try/except, so logic must still work if no subscribers exist.
- The presentation layer is abstracted via `presentation/interface.py` with multiple presenters (Null/Console/EventDriven); UIs subscribe to events for animations.

## Data-driven systems
- Abilities are migrating to YAML: charging abilities live in `src/core/data/abilities/` and load via `data/ability_loader.py`.
- Effects are composable in `effects/` (Composite/Chance/Conditional effects); prefer these over ad-hoc status logic.
- Content data (quests/dialogues/special events) is JSON in `src/core/data/content/` and loaded via `data/data_loader.py`.

## Combat specifics
- Enhanced combat uses a priority-based action queue in `src/core/combat/action_queue.py`; `EnhancedBattleManager` integrates it.
- Battle analytics are centralized in `src/core/combat/battle_logger.py` and used by both UIs.
- Charging abilities use `delay`/`charge_time` + telegraph messages; the Seeker/Inquisitor sees detailed telegraphs.

## Workflow & commands
- Run terminal game: `./launch.sh` or `python game_curses.py`.
- Run pygame game: `python game_pygame.py`.
- Dev tools (from repo root): `python3 tools/dev_tools.py [effects|queue|events|abilities|balance]`.
- Tests: `.venv/bin/python -m pytest tests/ -v` (see `tests/README.md` for patterns).

## Project conventions
- Absolute imports (`src.core.*`) are expected for cross-context execution.
- Paths are resolved with `Path(__file__).parent` for test compatibility.
- Keep UI-free logic in `src/core/`; UI layers should adapt core APIs instead of modifying them.
- Sprite generation is script-based: `src/ui_pygame/assets/ascii_to_sprite_colored.py` converts `ascii_files/` to colored PNGs.
