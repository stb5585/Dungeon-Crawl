# Curses UI Retirement

Status: `Retired`

## Decision

The terminal/curses game frontend is retired from the active codebase. Pygame
is the only supported player-facing frontend.

The final committed curses implementation is preserved by the annotated Git
tag `curses-ui-final`, which points to commit `a980649`. Historical changelog
and shipped-regression entries remain accurate records of the period when both
frontends were supported.

## Removed Surface

- `game_curses.py`;
- `src/ui_curses/`;
- `tests/ui_curses/`;
- curses package entry points;
- curses launch behavior in `launch.sh` and `launch_debug.sh`;
- active documentation and acceptance requirements that mandated curses
  parity.

The standard launch scripts now start Pygame. Existing JSON saves remain
compatible because both frontends used the shared
`src/core/save_system/SaveManager`.

## Terminal Development Contract

Terminal usage remains an important development workflow, but it targets the
shared engine rather than a second interactive frontend:

```bash
./.venv/bin/python -m pytest tests/core -q
./.venv/bin/python -m pytest tests/integration -q
./.venv/bin/python tools/dev_tools.py effects
./.venv/bin/python tools/dev_tools.py queue
./.venv/bin/python tools/dev_tools.py events
./.venv/bin/python tools/dev_tools.py abilities --directory src/core/data/abilities
```

New diagnostic needs should extend headless tests, simulator policies, compact
reports, debug encounter overrides, or development tools. They should not
reintroduce a second player-facing terminal UI.

## Core Boundary

The deeper compatibility cleanup also removed:

- terminal menu and screen methods from `Player`;
- the old `Player.end_combat()` outcome path superseded by `BattleEngine`;
- the terminal chest/door `Player.open_up()` path;
- presentation parameters such as `textbox`, `confirm_popup`,
  `battle_manager`, and `save_popup` from shared core methods;
- the `game.stdscr` Pygame compatibility shim;
- the bound-method `actions_dict` terminal command catalog; and
- non-combat action metadata formerly returned by map tiles.

Active core methods now mutate gameplay state and return values or messages.
Pygame owns confirmation, rendering, modal flow, and encounter presentation.
Tile `available_actions()` methods remain only as the combat engine's action
query contract; outside combat they no longer publish terminal navigation or
menu commands.

The slot-machine animation callback and map-tile `popup_class` injection remain
because Pygame actively uses them. They are frontend extension points, not
curses compatibility.

## Future Compatibility

The archive tag is a recovery point, not a maintained release branch. Future
core, save, content, or Python changes do not need to preserve compatibility
with the archived frontend.

If a maintainer later revives it, the work should happen as a separate package
or project consuming public core APIs. Active development must not restore
curses parity as a requirement for Pygame features.
