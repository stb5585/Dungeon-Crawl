# Architecture

This document describes the supported runtime boundaries after the
`improvements` stabilization pass. Design-gate documents own future gameplay
decisions; this document owns the shape of the application.

## Runtime Boundaries

`src/core/` is the UI-independent game engine. It owns characters, progression,
combat, encounters, items, quests, maps, persistence, events, and content
loading. Core code must not render, poll Pygame input, or require a display.

`src/ui_pygame/` is the supported player-facing frontend. It translates input
into core operations and renders core state and results. The retired curses UI
is preserved at the `curses-ui-final` Git tag and is not a second supported
runtime.

## Public Package APIs

Callers should import package-owned types from stable package entry points when
one exists, including `src.core.character`, `src.core.abilities`,
`src.core.combat.battle_engine`, `src.core.events`, and
`src.core.save_system`. Their `__init__.py` imports are intentional public or
compatibility re-exports, so lint configuration exempts only package
initializers from unused-import reporting.

Compatibility re-exports are transitional, but they must not be removed just
because an implementation was split into modules. A later cleanup should first
inventory external and internal callers, document a replacement import for
each symbol, add a deprecation period where practical, and remove the alias in
a separately announced breaking release.

## Combat Actions And Targets

The Pygame combat manager drives `BattleEngine`; the engine owns the combat
state and never reads input. A requested action is represented by an immutable
`ActionIntent` containing the action, optional choice, and stable encounter
target IDs. `TargetScope` defines no-target, self, single-enemy, and all-enemy
shapes. `TargetLossPolicy` determines whether a committed action stays locked,
retargets to focus, or uses a roster snapshot.

The engine validates the intent, expands and resolves targets against the live
`CombatEncounter`, executes the action, and returns an `ActionResult` with a
machine-readable validation code when rejected. The actor cycle owns fixed
turn order; pre-turn and post-turn results carry status and resolution effects,
and `BattleOutcome` carries final settlement. Events and the battle logger
observe this flow without becoming the source of combat truth.

The next combat architecture phase is intentionally deferred. Large mutation
methods such as weapon damage and status-effect resolution should be replaced
incrementally by typed, ordered modifier pipelines operating on explicit
combat context and result models. That work needs compatibility tests and
design approval; it is not part of stabilization.

## Saves And Migration

Save payloads have an explicit integer version. Version 5 is current. Repository
history proves that `master` produced version 3 and that the intermediate
`improvements` serializer continued to produce version 3 before changing
directly to version 5. No committed version 4 writer was found.

`SaveManager` reads and validates a payload before deserialization. Supported
legacy payloads migrate in memory, deserialize, receive an exact
`.v<version>.bak` copy of their original text, and are then replaced atomically.
If replacement fails, the loaded player and original/backup remain recoverable
and the caller receives a structured warning. Unknown versions and version 4
fail with a specific unsupported-version result rather than guessed data.

Version 3 staged class levels map to global levels by adding 0, 30, or 60 for
base, first-promotion, and second-promotion classes. Promotion lineage and
points earned through the resulting global level are reconstructed. Serialized
statistics already include legacy attribute choices, so attribute points are
not granted again. Version 3 did not preserve enough information to translate
partial progress within the current level; migrated total experience is set to
the threshold for the reconstructed level.

## Resources And Writable Data

`src.paths` is the path authority. In a checkout, resources resolve from the
repository root; in a PyInstaller process they resolve from `sys._MEIPASS`.
Packaged maps live under `src/core/data/maps/`, and Pygame assets live under
`src/ui_pygame/assets/`. Runtime code must not use the current working directory
to find either category.

Saves, temporary files, configuration, and debug logs use the platform user-data
directory: `%LOCALAPPDATA%` on Windows, `~/Library/Application Support` on
macOS, and `$XDG_DATA_HOME` or `~/.local/share` on Linux. The
`FORSAKEN_TENET_DATA_DIR` environment variable provides an explicit test and
development override.

## Distribution

The supported portable model is a PyInstaller onedir application built from
`packaging/forsaken_tenet.spec` with
`./.venv/bin/python tools/build_distribution.py --clean`. The bundle includes
runtime maps and assets but excludes documentation review sheets. Its
`--smoke-test` mode initializes headless Pygame, checks representative images
and maps, and verifies writable user-data directories without entering an
interactive loop.

Ordinary CI pushes validate source only. Artifact construction, headless frozen
startup, and artifact upload run only for a manual workflow dispatch or a
published release.
