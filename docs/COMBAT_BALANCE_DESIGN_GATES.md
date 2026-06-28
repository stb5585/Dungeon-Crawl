# Combat Balance Design Gates

This is the durable combat architecture and balance decision reference. It
documents current behavior, locks current defaults, records report questions,
and gates future combat or balance changes behind explicit one-page specs.

## Review Baseline

### Combat Architecture

- `src/core/combat/battle_engine.py` owns UI-agnostic combat flow:
  initiative setup, pre-turn checks, forced actions, action execution,
  companion/Totem/post-turn handling, turn swapping, and battle-end rewards.
- `src/core/character.py` owns status and effect ticking through
  `Character.effects()`.
  - Status ticks happen at the active actor's start of turn.
  - Poison, DOT, Bleed, Doom, Ice Block, Prone, Silence, Stun, Sleep, Defend,
    Reflect, Totem, and related effects are resolved there.
  - A status tick can defeat the active actor before they act.
- Enemies use `action_stack` priority rules in `src/core/enemies.py` when
  configured, falling back to legacy random action selection otherwise.
  - `ActionPriority` currently supports `HIGH`, `NORMAL`, `LOW`,
    `LOW_HP_ONLY`, and `SKIP` style AI decisions.
  - Enemy combat items are surfaced through `_combat_item_choices()` and used
    through the same BattleEngine item action path as player item use.
- `src/core/combat/action_queue.py` exists as a priority/delay scheduling
  helper, but the main one-on-one BattleEngine loop remains the active combat
  runtime.

### Analytics And Tooling

- `src/core/analytics/combat_simulator.py` runs simulated fights through the
  real `BattleEngine`.
- `CombatStats` stores per-fight results including winner, turns, HP remaining,
  damage totals, ability usage, status applications, critical hits, and misses.
- `BalanceReport` exports aggregate win rates, average and median turn counts,
  close-fight and stomp rates, ability usage, status frequency, outliers,
  compact summaries, and JSON payloads.
- `tools/run_balance_suite.py` builds representative class/race/enemy matchups
  and supports tier, level, race, gear, meta-loadout, progression, and race
  delta options.
- Known tooling issue: `./.venv/bin/python tools/run_balance_suite.py --help`
  currently fails because one argparse help string contains an unescaped `%`.
  Do not treat that failure as a combat gameplay issue; fix it only in a
  tooling cleanup slice.

## Current-Slice Decisions

- Keep existing random-roll mechanics. Do not convert rolls to DnD-style dice
  notation without a promoted combat-balance decision.
- Keep current Silence behavior: `abilities_suppressed()` blocks spells,
  skills, summons, and other ability-like actions while Silence or anti-magic
  is active.
- Keep current status-tick timing: start-of-turn effect ticks resolve before
  the actor's action, and those ticks may defeat the active actor.
- Keep current shield, Reflect, ignore-defense, resistance, dodge, block, and
  damage-resolution order unchanged until a dedicated combat-resolution spec
  defines a replacement order.
- Keep current single-enemy combat and one-action turn flow. Multi-enemy combat
  and speed-based combat stacks are deferred.
- Keep current experience rules. Class/race-specific level scaling,
  charisma-driven experience, unlockable race/class/level strategy, and
  difficulty-level strategy are deferred.
- Keep numeric balance constants unchanged until simulator reports are generated
  and reviewed.

## Balance Report Plan

Canonical report commands for later validation:

```bash
./.venv/bin/python tools/run_balance_suite.py --tier base --level 10 --iters 30 --seed 1337
./.venv/bin/python tools/run_balance_suite.py --tier first --level 20 --iters 30 --seed 1337
./.venv/bin/python tools/run_balance_suite.py --tier second --level 30 --iters 30 --seed 1337
./.venv/bin/python tools/run_balance_suite.py --tier all --level 20 --iters 30 --seed 1337 --races Human Elf "Half Elf" "Half Giant" Gnome Dwarf "Half Orc" --delta --baseline-race Human
```

Report questions to answer before changing balance values:

- Stat-dump tradeoffs: do high single-stat builds win too reliably, lose too
  sharply, or create obvious dead stats in the representative suite?
- Poison, stun, and crit scaling: do status/control builds create runaway
  outcomes, excessive no-action turns, or too many low-interaction wins?
- PvE outliers: which class/enemy pairs produce extreme win rates, very short
  stomps, long stalls, or repeated draws?
- Enemy item usage after stealing consumables: once a player removes an enemy's
  potion or elixir, does the enemy AI stop selecting that missing item and fall
  back cleanly?
- Race baselines: after class kits stabilize, do race/class restrictions and
  racial stat/resistance packages create acceptable deltas against Human?
- Progression modeling: do `--progression on`, tiered gear, and meta-loadouts
  produce believable late-game approximations before they are used for tuning?

Numeric tuning remains out of scope until the reports above are generated,
saved, and reviewed against actual playtest findings.

## Class-Kit Threshold Use

`docs/CLASS_KIT_DESIGN_GATES.md` owns the class-kit balance thresholds for
promotion meters, ring preservation, and action-economy loops. Those thresholds
are watch-first evidence gates. A `Watch` or `Tuning Gate` finding should record
manual observations, simulator payloads, class/race/enemy matchup, level,
gear/loadout, ring state, and relevant `class_kit_events` or
`action_economy_events` counts before any tuning is proposed.

Threshold findings do not authorize immediate numeric changes. Numeric tuning
still requires a promoted one-page balance spec that states the observed
problem, affected class tracks, target behavior, exact constants or trigger
rules to change, regression coverage, simulator commands, and manual playtest
checks.

## Deferred One-Page Spec Gates

Each item below needs a one-page spec before implementation. Each spec must
define current behavior, target behavior, UI text/surfaces, save compatibility,
tests, and balance assumptions.

### Ability And Menu Ergonomics

- Spell and skill sorting, including mana-cost ordering and broader action menu
  ordering beyond current `Runic Boost` insertion.
- Status-gated skill visibility and messaging.
- Out-of-combat timed buffs/debuffs.
- Monk/Master Monk bare-handed skill support and attack bonuses.
- Polearm Mastery as a future quest/item-unlock hook. Do not wire it without a
  trigger, reward source, UI text, and balance decision.

### Ability Reworks

- Wind eject effects and reward handling.
- Absorb Essence rework.
- Mana-percentage damage abilities.
- Prismatic Rays.
- Throw inventory-item ability.
- Magic-stat success scaling.
- Always-hit spell flags. A promoted spec must define resistance behavior,
  boss-immunity boundaries, UI text, combat log text, and regression tests.

### Combat Semantics

- DnD-style dice roll conversion.
- Charisma or alternate-stat experience modifiers.
- Silence edge cases beyond current `abilities_suppressed()` behavior.
- Nightmare and flying creature land/takeoff behavior.
- Whether status ticks should continue after enemy defeat in any future
  multi-actor flow.
- Ignore-defense semantics and shield/Reflect/damage-resolution order.
- Unlockable races, unlockable classes, level caps, and difficulty tiers.

### Architecture Expansions

- Multi-enemy combat, including targeting, encounter generation, UI layout,
  loot/XP allocation, AI, simulator support, and balance expectations.
- Speed-based combat stacks, including initiative/action-queue rules,
  multiple-turn caps, UI messaging, simulator impact, and save compatibility.

## Validation

Docs-only spec changes should run:

```bash
rg -n "COMBAT_BALANCE_DESIGN_GATES|Combat Balance Design Gates|Needs Exploration|Needs Design Decision" docs README.md
git diff --check
```

Focused exploratory tests are optional unless executable examples or simulator
behavior are changed:

```bash
./.venv/bin/python -m pytest tests/core/test_combat_simulator.py tests/core/test_combat_simulator_advanced.py
```
