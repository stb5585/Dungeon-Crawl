# Multi-Enemy Combat Design

## Status

Status: `Implemented - Slices 0 and 1 (singleton roster only)`

This document promotes the multi-enemy combat item from
`COMBAT_BALANCE_DESIGN_GATES.md` into a concrete architecture proposal.
Architecture decisions 1-12 are approved for Slices 0 and 1. Content,
frontend, and balance decisions 13-21 remain deferred until their rollout
slices. Slice 1 introduces only a runtime roster with singleton parity; it
does not authorize two-enemy battle execution or generation.

The first stable release is intentionally limited to one player-facing combat
slot against one or two enemies. The architecture should not impose a permanent
two-enemy ceiling, but content generation and UI acceptance must enforce that
ceiling until playtest and simulator evidence support expanding it.

## Motivation

The current duel loop makes every encounter read as a one-on-one contest even
when an ability's fiction describes an area, formation, pack, field, or group.
That limits:

- abilities that attack or control multiple enemies;
- encounter composition and enemy-role identity;
- target-priority decisions;
- the value of fields, counters, summons, companions, and defensive tools;
- the sense that dungeon creatures inhabit the world together.

The goal is not simply to double incoming attacks. Multi-enemy combat should
add target choice and encounter texture while keeping turns legible and the
existing one-enemy game reliable.

## Goals

- Support encounters containing exactly one or two living enemy instances.
- Preserve current one-enemy mechanics and frontend behavior through a
  compatibility path.
- Give basic attacks and single-target abilities an explicit enemy target.
- Give abilities a declared target scope that can represent all-enemy effects.
- Resolve multi-target effects independently per target while paying the
  action's resource cost once.
- Give each living enemy its own turn, statuses, AI decision, telegraph,
  rewards, logs, and presentation state.
- Keep gameplay authority in the UI-agnostic `BattleEngine`.
- Keep targeting rules in the engine rather than the Pygame frontend.
- Extend encounter generation, save compatibility, analytics, and balance
  tooling before multi-enemy encounters become common.
- Provide a safe rollout that begins with curated, opt-in two-enemy encounters.

## Non-Goals For The Initial Release

- More than two enemies.
- Multiple controllable party members or multiple simultaneous player slots.
- Formation, rows, distance, adjacency, cones, lines, or positional movement.
- Reinforcements, waves, enemy summoning, or enemies joining mid-encounter.
- Speed gauges, action points, simultaneous actions, or adoption of the
  existing experimental `ActionQueue`.
- A global numeric rebalance of every ability and enemy.
- Boss-plus-add encounters, story duos, Class Ring trials, Thieves Guild
  trials, Funhouse encounters, or scripted final encounters.
- Area effects that select an arbitrary subset of enemies.
- Saving and resuming in the middle of a combat loop unless that capability is
  separately approved.

## Current Runtime Constraints

The current combat path is structurally one-on-one:

- `BattleEngine` accepts one `enemy` and alternates
  `attacker`/`defender` between two sides.
- `determine_initiative()` returns a pair rather than an actor cycle.
- actions implicitly use `self.defender`; neither frontend asks for a target;
- `battle_continues()` ends when `self.enemy` dies;
- status ticks, passive retaliation, delayed spells, familiar output, Totems,
  charging abilities, and forced actions all assume one opposing object;
- `BattleOutcomeMixin` awards XP, loot, quests, kill credit, vows, class-kit
  triggers, and cleanup for one enemy;
- pygame rendering, animations, floating text, enemy details, telegraphs, and
  presenter state use one enemy or the literal target key `"enemy"`;
- `CombatResult` and most event payloads carry one target, although
  `CombatResultGroup` already provides a useful per-target result container;
- the simulator models `char1` against `char2`, and `BattleLogger` stores one
  enemy metadata record;
- encounter catalogs return one enemy and map tiles/save payloads store one
  `enemy`/`enemy_state`;
- mechanics such as Rewind, Foretell, Bard songs, Paladin marks, delayed
  spells, Hallowed Ground, and summon support directly inspect
  `battle_engine.enemy` or the current defender.

These are migration points, not reasons to implement a second parallel combat
engine.

## Proposed V1 Player Experience

### Encounter Start

The combat intro names both enemies and presents them in stable left-to-right
slots. Duplicate names receive encounter-only labels such as `Goblin A` and
`Goblin B`; their canonical bestiary and quest identity remains `Goblin`.

For one enemy, combat looks and behaves as it does now. For two enemies, the
player can inspect both HP/status panels subject to the existing Sight and
invisibility rules.

### Choosing An Action And Target

The input sequence is:

1. Choose the action.
2. Choose the spell, skill, item, or command when the action requires one.
3. If the resolved target scope is `SINGLE_ENEMY` and more than one valid enemy
   remains, choose an enemy.
4. Confirm and execute.

There is no target prompt when only one valid target exists. `SELF` and
`ALL_ENEMIES` abilities execute without a target prompt. Cancelling target
selection returns to the ability selection without consuming the turn or
resource.

Basic Attack is `SINGLE_ENEMY`. The UI remembers the last valid focused enemy
as a convenience, but it must still make the impending target visually clear.
If that enemy dies, focus moves to the first living enemy in authored slot
order.

### Turn Readability

Only one actor is active at a time. The active enemy's slot, name, and
telegraph are highlighted. The combat log always uses encounter display labels
when duplicate enemies exist.

An enemy that dies or otherwise leaves the encounter cannot act later in the
cycle. Combat continues until the player side is defeated, the player flees,
or no hostile enemy remains.

## Core Domain Model

### Encounter

Introduce a UI-agnostic runtime model, provisionally named
`CombatEncounter`:

```python
@dataclass
class CombatEncounter:
    encounter_id: str
    enemies: list[EncounterEnemy]
    tags: frozenset[str] = frozenset()
    source: str = "legacy"
```

Each `EncounterEnemy` wraps one `Character` and encounter-only identity:

```python
@dataclass
class EncounterEnemy:
    combatant_id: str
    character: Character
    slot: int
    display_label: str
    resolution: str | None = None
```

`resolution` records why the combatant left the hostile roster, for example
`defeated`, `mercy`, `tamed`, or `ejected`. It must not be inferred only from
zero HP because those outcomes have different reward rules.

The encounter exposes:

- `living_enemies`;
- `hostile_enemies`;
- `resolved_enemies`;
- `primary_enemy`, a stable authored leader used only for encounter identity;
- lookup by `combatant_id`;
- encounter completion state.

Enemy `Character` objects remain the owners of HP, MP, statuses, spellbooks,
AI, and combat ratings. The wrapper should not duplicate character state.

### BattleEngine Compatibility

The canonical engine state becomes:

```text
encounter
├── enemies[1..2]
├── active_actor
├── selected_target
├── actor_cycle
└── resolution_ledger
```

During migration, `BattleEngine(player, enemy, tile, ...)` remains supported
and creates a singleton encounter. A new `encounter=` entry point accepts the
roster model. Supplying both is an error.

The legacy `engine.enemy` property may temporarily return
`selected_target.character` so old singleton callers continue to work, but new
engine code must use `encounter`, `primary_enemy`, or `selected_target`
explicitly. It must never use the compatibility property for reward iteration,
encounter completion, or story identity.

`attacker` and `defender` may remain as action-resolution aliases during the
migration. They are not sufficient to represent the encounter and should not
own turn scheduling.

### Action Intent And Target Scope

Extend action execution to receive a structured intent:

```python
class TargetScope(Enum):
    SELF = "self"
    SINGLE_ENEMY = "single_enemy"
    ALL_ENEMIES = "all_enemies"


@dataclass(frozen=True)
class ActionIntent:
    action: str
    choice: str | None = None
    target_ids: tuple[str, ...] = ()
```

Future scopes such as `SINGLE_ALLY`, `ALL_ALLIES`, `ANY_COMBATANT`, or
`RANDOM_ENEMY` may be added when the game actually has abilities that require
them. V1 should not pre-build party targeting.

Every active ability ultimately exposes a target scope. Existing abilities
receive compatibility defaults:

- weapon attacks and offensive spells/skills: `SINGLE_ENEMY`;
- healing and defensive abilities that currently force the caster:
  `SELF`;
- non-target actions such as Defend, Recall, Transform, and Pickup Weapon:
  `SELF` or no target;
- Hallowed Ground and newly approved area abilities: `ALL_ENEMIES`.

The defaults are a migration aid, not an authoring contract. New abilities
must declare their scope, and existing exceptional abilities must be audited
rather than classified only from subtype strings.

The engine, not the UI, validates that:

- every requested target belongs to the encounter;
- every target is alive and hostile when required;
- target count matches the ability scope;
- hidden enemies remain mechanically targetable or untargetable according to
  the approved Sight decision;
- no resource is spent when intent validation fails.

### Multi-Target Resolution

An `ALL_ENEMIES` action snapshots the valid living enemy targets when execution
begins. It then resolves the same effect separately against each target in
stable slot order.

Proposed default rules:

- mana, item, class-resource, and action costs are paid once;
- hit, dodge, block, critical, resistance, immunity, damage, and secondary
  effects roll independently for each target;
- one target's death does not stop resolution against later snapshotted
  targets;
- per-target damage/status events are emitted with their actual target;
- action-level events are emitted once and identify the selected scope;
- the return value is a `CombatResultGroup` when the underlying ability uses
  structured results;
- player-facing text groups the cast announcement once, followed by concise
  per-target outcomes;
- on-kill triggers declare whether they trigger per defeated enemy or once per
  action. Existing triggers must be audited before conversion.

An ability should not accept a raw `targets` keyword as its public targeting
contract. The engine resolves an `ActionIntent` into valid characters and
passes an explicit action context so UI, AI, and direct tests share one path.

### Turn Cycle

V1 keeps one action per living combatant per round and does not adopt
speed-based action stacks.

The provisional cycle is side initiative:

- if the player side wins initiative:
  `player slot -> enemy slot 0 -> enemy slot 1`;
- if the enemy side wins initiative:
  `enemy slot 0 -> enemy slot 1 -> player slot`;
- an active summon continues to occupy the player slot as it does today;
- authored enemy slot order remains stable for the encounter;
- defeated/resolved actors are skipped;
- a round ends after every actor who was eligible at its start has either
  acted or been skipped.

Start-of-turn status effects remain tied to the active character's own turn.
Durations continue to decrement through existing character effect processing.
This avoids silently accelerating an enemy's statuses merely because another
enemy was added.

Round events may be emitted for diagnostics, but no mechanic should change
from turns to rounds without an ability-specific decision and regression test.

The exact initiative comparison is still a blocking decision. Reusing
`determine_initiative(player, encounter.primary_enemy)` is compatible but may
underrepresent a faster secondary enemy. Comparing against the fastest living
enemy is safer but changes encounter balance.

### Enemy AI

Each enemy independently calls its existing `options()` logic on its turn.
During V1, the only opposing active combatant is the player or the summon that
currently occupies the player slot, so legacy enemy actions retain a valid
single target.

The AI context should nevertheless expose:

- all living allies and opponents;
- the active opposing combatant;
- prior actions in the current round;
- encounter tags and slot identity.

V1 does not require coordinated combo planning. It does require AI to avoid:

- choosing a dead or resolved target;
- repeating a unique encounter-wide effect that cannot stack;
- selecting an action made invalid by another enemy earlier in the round;
- treating an ally's low HP or status as its own.

Enemy target selection against multiple player-side actors is deferred until
the game gives summons, companions, or party members independent targetable
slots.

### Charging, Delayed, And Forced Actions

Charging state must store `combatant_id`, not only a mutable defender object.
Before a charged or delayed action resolves, the engine validates the original
target.

The recommended V1 fallback is:

- single-target charged action whose target left combat: cancel, log the lost
  target, and do not charge the cost a second time;
- all-enemy charged action: resolve against the living roster at release time;
- Berserk basic attack: choose the current focus if valid, otherwise the first
  living enemy;
- delayed single-target spell: remain bound to its original target rather than
  silently moving to another enemy.

Whether a cancelled charge refunds its original cost is a required decision.

### Passive Reactions And Global Effects

Reactions must be bound to the actual source and target of the triggering
result:

- thorns and counterattacks belong only to the enemy that was hit;
- Riposte targets the enemy whose action triggered it;
- Reflect applies to the reflecting target's portion of a multi-target spell;
- resurrection checks only the combatant that died;
- on-death effects execute once for that combatant;
- familiar, companion, and Totem attacks require an explicit target policy;
- fields such as Hallowed Ground keep per-character effect state but derive
  their initial target list from the encounter;
- Battle Hymn and other encounter-wide effects enumerate participants through
  the encounter API rather than named `player`/`enemy`/`summon` attributes.

Counterspell behavior for an all-enemy spell is not yet specified. It could
cancel the entire cast, cancel only that enemy's portion, or roll once before
target resolution. This must be decided before the first reflectable or
counterable all-enemy damage spell ships.

### Defeat And Removal

Zero HP removes an enemy from future turns, but the engine records a semantic
resolution before rewards:

| Resolution | Hostile afterward | Kill credit | Normal loot/XP |
| --- | --- | --- | --- |
| `defeated` | No | Yes | Candidate |
| `mercy` | No | No | Redemption rules |
| `tamed` | No | No | No |
| `ejected` | No | No | No loot; XP decision open |
| `escaped` | No | No | No |

The encounter ends in victory when no hostile enemy remains, including a mixed
result such as one defeated enemy and one redeemed enemy. Death animations and
cleanup occur per enemy rather than at encounter end.

## Rewards And Progression

The engine should build a resolution ledger during combat and settle it once
through an encounter-level outcome service. It must not call the current
single-enemy `_process_victory()` once per enemy because that would duplicate
end-of-combat cleanup, class-kit triggers, transformation resets, and encounter
statistics.

Proposed separation:

- **per defeated enemy:** kill dictionary, Bestiary defeat, bounty/quest
  progress, soul harvest, eligible loot, enemy-specific class triggers;
- **per resolved non-kill enemy:** mercy, taming, ejection, or escape handling;
- **per encounter:** player effect cleanup, transformation reset, battle scar,
  victory count, encounter-survived count, contract cooling, class-kit
  `end_combat`, total XP award, summon XP award, level-up calculation, boss/tile
  completion.

Total encounter XP is provisionally the sum of eligible enemy XP, awarded once
after multipliers. Loot is processed in authored slot order so inventory-full
and floor-drop behavior is deterministic.

This section requires explicit decisions for partial victories, flee/death
after defeating one enemy, bounty encounters, and per-kill class resources.

## Encounter Authoring And Generation

Do not create two-enemy encounters by independently rolling the existing
catalog twice. That can produce incoherent identities, duplicate bosses,
extreme control combinations, and accidental difficulty spikes.

Add authored `EncounterSpec` data:

```python
@dataclass(frozen=True)
class EncounterSpec:
    encounter_key: str
    enemy_factories: tuple[EnemyFactory, ...]
    floors: tuple[str, ...]
    weight: int = 1
    tags: frozenset[str] = frozenset()
    enabled: bool = False
```

The existing `random_enemy()` remains as a singleton compatibility API.
`random_encounter()` selects from eligible singleton and explicitly enabled
pair specs. Debug overrides should support both one forced enemy and one forced
encounter key.

Initial content rollout should use a small matrix of reviewed pairs:

- no boss or trial classes;
- no pair containing two hard-control specialists;
- no pair containing two high-burst enemies until measured;
- no pair whose combined expected actions or HP exceeds its floor budget;
- duplicate and mixed-species pairs both tested;
- at least one early, middle, and late floor pair only after the preceding
  floor is stable.

Encounter chance, composition budget, and pair eligibility are balance
decisions, not architecture constants.

## Frontend Design

### Pygame

- Render two enemy slots horizontally in the current combat area, with smaller
  maximum sprite bounds than the singleton layout.
- Give each slot its own name, HP/MP, status icons, Sight state, animator,
  target rectangle, recoil/death state, floating text anchor, and telegraph.
- Use a bright focus border and target arrow; do not communicate selection by
  color alone.
- Keyboard target navigation uses left/right or A/D; confirm uses the existing
  confirm inputs; Escape/Backspace cancels.
- Mouse selection uses the enemy slot/card target rectangle.
- The detailed enemy panel follows focus. The player can change focus while
  browsing actions without committing a target.
- For a singleton encounter, retain the current centered sprite scale and omit
  target-selection chrome.
- Replace literal visual target strings such as `"enemy"` with combatant IDs
  mapped to target rectangles.
- Presenter state stores an encounter roster and resolves event targets by
  object/ID; it must not position every non-player event at one fixed x value.

### Headless Development Surfaces

- Engine tests build singleton and two-enemy encounters without initializing
  Pygame.
- Simulator policies select explicit targets and record per-combatant results.
- Debug encounter overrides can force a pair from terminal commands before it
  is enabled in random generation.
- Text logs and reports use duplicate-safe display labels and combatant IDs.

## Events, Logging, And Analytics

### Events

- Keep `CombatEvent.target` as the one actual target for per-target events.
- Emit one damage/status/death event per affected combatant.
- Add encounter metadata only when a consumer is updated to use it:
  `encounter_id`, `combatant_id`, `target_scope`, and `target_ids`.
- `COMBAT_START` and `COMBAT_END` need a roster summary in `data`; their legacy
  `target` remains the primary enemy during compatibility.
- Core resolution must remain independent of subscribers.

### Battle Logger

- Replace singleton `enemy` metadata with an `enemies` list while retaining a
  legacy singleton view in exported payloads for a compatibility period.
- Log canonical identity, display label, combatant ID, slot, and resolution.
- Count actions and damage per combatant ID so duplicate enemy names do not
  collapse into one analytics bucket.
- Track rounds separately from actor turns.

### Simulator

The simulator needs an encounter policy and multi-enemy result model before
numeric tuning:

- player win rate by encounter key and composition;
- turns and rounds;
- player actions versus total enemy actions;
- damage dealt/taken per enemy and per round;
- target selection share and time-to-first-enemy defeat;
- no-action/control-loss turns by actor;
- all-enemy versus single-target ability usage and efficiency;
- partial-resolution outcome counts;
- focus-fire and duplicate-enemy cases;
- class/race/gear/progression deltas against the equivalent singleton fights.

A two-enemy fight must not be represented as an ordinary PvP-style
`winner`/`loser` pair in `CombatStats`.

## Save Compatibility

Current saves may contain one tile `enemy_state`. They must continue to load as
a singleton encounter.

If encounters need to persist outside active combat, add a versioned
`encounter_state` with:

- encounter key and source;
- member states in authored slot order;
- canonical enemy serializer payload per member;
- combatant/display identity sufficient to restore duplicates;
- resolution state for members already removed, if partial encounters persist.

For one release, singleton writers may continue writing `enemy_state`, or write
both forms if the save-size and migration policy permits it. Load precedence
must be explicit when both keys exist.

V1 should avoid persisting active turn order, selected target, temporary
combat-only IDs, or charged actions unless mid-combat save/resume is approved.
If saving is impossible during combat today, that boundary should be retained
rather than accidentally creating an incomplete combat snapshot format.

## Special-Mechanic Audit

The following mechanics must have focused decisions or regression coverage
before broad rollout:

- Rewind/Foretell snapshots and target identity;
- Wormhole and other delayed spells;
- Jump, Charge, Crushing Blow, and other charge-target retention;
- Hallowed Ground and future all-enemy fields;
- Reflect, Counterspell, thorns, retaliation, Riposte, and on-death attacks;
- Berserk forced targeting and Chorus Time;
- Battle Hymn participant enumeration and enemy-opening Bard debuffs;
- Paladin Challenge, Condemnation, Redeem, Repel the Wicked, and bounty logic;
- Windswept, taming, no-reward removals, and mixed resolution encounters;
- Totem pulses, familiar turns, Beast Master commands, and summon support;
- natural-spell kill runes, death marks, soul harvest, frenzy-on-kill, battle
  scars, contracts, and other per-kill/per-encounter class-kit triggers;
- resurrection and enemies that change form instead of dying;
- Vesperion, Mad Waitress, Behemoth, Red Dragon, and every scripted/trial
  combat, even though they remain singleton in V1;
- duplicate enemy inventory, item stealing, quest identity, Bestiary identity,
  and loot drops.

## Ability-Tree Refactor Integration

Targeting belongs to the canonical ability definition, not to a progression
node. Tree nodes should continue to reference ability classes/IDs and should
not duplicate `TargetScope`, coefficients, or encounter rules in the
progression manifest.

The paused ability-tree work can resume in two stages:

1. After the target-scope enum, metadata location, and structured-result
   contract are approved, abilities and future nodes may be designed with an
   explicit scope even while two-enemy generation remains disabled.
2. Abilities declared `ALL_ENEMIES` should not become purchasable in normal
   play until Slice 3 proves their resource, reaction, kill-trigger, and
   singleton behavior. A development-only tree/node is acceptable for
   headless and UI validation.

Before resuming broad tree authoring, build an ability inventory containing
canonical ID/class, current description, inferred scope, approved scope,
resource cost, charge behavior, reaction exposure, and per-kill triggers.
That inventory will distinguish simple metadata work from abilities that need
bespoke multi-target mechanics.

Changing only an ability's target scope should not require a progression node
ID migration. Renaming or replacing a version-5 node/ability identity remains
subject to the existing save and ownership rules in
`ABILITY_TREE_DESIGN.md`.

## Rollout Plan

### Slice 0 - Decision And Characterization Gate

- Answer Required Decisions 1-12.
- Inventory abilities and mechanics by target scope and trigger cadence.
- Add singleton characterization tests around current turn order, rewards,
  statuses, summons, Rewind, events, logger output, and Pygame presentation.
- Record a simulator singleton baseline before architecture changes.

Exit condition: approved target/turn/reward contracts and a parity test set.

#### Slice 0 Singleton Simulator Baseline

The pre-refactor singleton baseline completed successfully on 2026-08-03 with:

```bash
./.venv/bin/python tools/run_balance_suite.py --tier base --level 10 --iters 30 --seed 1337
```

The retained local report is
`reports/balance_baselines/multi_enemy_slice0_pre_refactor.txt` (117 lines,
SHA-256 `edccb0d62fecdf1d350189421aa9d5d9a2004a388c9bde2664df3896b7993fbe`).
Balance-baseline reports are intentionally gitignored; the command, seed,
status, location, and checksum here are the durable record. This run is a
parity reference, not authorization for numeric tuning.

The same command completed after Slice 1 and wrote
`reports/balance_baselines/multi_enemy_slice1_post_refactor.txt`. The report
was byte-for-byte identical (`cmp` exit 0) and had the same SHA-256 checksum,
confirming no measured singleton simulator drift.

### Slice 1 - Encounter Roster With Singleton Parity

- Add `CombatEncounter`, member identity, and resolution ledger.
- Allow the engine to consume singleton encounters through the legacy
  constructor.
- Replace internal completion and stable-identity reads without exposing
  two-enemy content.
- Extend logger/event lifecycle payloads with compatible roster data.

Exit condition: existing singleton tests and focused parity tests pass with
multi-enemy generation disabled.

### Slice 2 - Actor Cycle And Explicit Single Targeting

- Add the actor cycle, living-actor skipping, rounds, and explicit
  `ActionIntent`.
- Add target-scope declarations and compatibility defaults.
- Refactor forced, charged, delayed, passive, familiar, summon, and Totem paths
  to use explicit targets.
- Add headless two-enemy engine tests; keep gameplay generation disabled.

Exit condition: two enemies can complete a headless battle with correct status
ticks, turns, target validation, and mixed death order.

### Slice 3 - Multi-Target Ability Contract

- Use `CombatResultGroup` and per-target event emission.
- Convert Hallowed Ground as the first all-enemy reference ability.
- Add one simple direct-damage all-enemy test ability or approved real ability.
- Resolve reaction, cost, death-during-action, and per-kill trigger semantics.

Exit condition: single-target and all-enemy actions share one validated engine
path and are deterministic under seeded tests.

### Slice 4 - Frontend Targeting

- Implement pygame dual-slot layout, focus, target selection, effects, and
  duplicate labels.
- Add automated layout/input tests and manual 1v1/1v2 acceptance checks.

Exit condition: singleton presentation remains readable, Pygame can finish a
curated two-enemy debug encounter, and the same encounter completes through
the headless engine harness.

### Slice 5 - Outcomes, Save State, And Simulation

- Settle ledger-based XP, loot, quest, bounty, class-kit, and removal results.
- Add the approved encounter serializer/migration if persistent pairs require
  it.
- Extend simulator, battle reports, debug override, and balance suite.
- Run singleton regression and paired encounter baselines.

Exit condition: no duplicate encounter rewards/cleanup and old saves load.

### Slice 6 - Curated Content Pilot

- Author a very small opt-in pair catalog.
- Enable pairs behind a development flag or debug encounter key.
- Playtest action economy, readability, control chains, and resource pressure.
- Promote one bounded floor band only after its evidence is reviewed.

Exit condition: stable crash-free playtests, acceptable balance evidence, and
no unresolved blocker from the special-mechanic audit.

## Approved Architecture Decisions

The following contracts are approved for Slices 0 and 1. Runtime behavior
belonging to later slices remains deferred even though its contract is fixed.

### Blocking The Architecture Slices

1. **Turn order:** Roll an individual weighted actor permutation once at
   combat start and reuse it each round. Existing hangover, encumbrance,
   invisibility, speed, and luck rules inform that initial ordering. Resolved
   or dead actors are skipped. Implementation begins in Slice 2.

2. **Durations:** Effects tick only on their owner's turns. A one-turn effect
   therefore expires at that combatant's next owner-turn tick; fields that
   pulse per round must declare that cadence separately.

3. **Target scopes:** V1 uses `NONE`, `SELF`, `SINGLE_ENEMY`, and
   `ALL_ENEMIES`. Invisible unrevealed enemies remain directly targetable with
   existing information and accuracy penalties and remain included in
   `ALL_ENEMIES`.

4. **Reflect and Counterspell:** Resolve reactions independently per target
   portion. Reflect changes only the reflecting target's result. Counterspell
   remains retaliation and may trigger independently for each target; it does
   not cancel the cast or other target portions.

5. **Lost charged or delayed targets:** Each affected ability declares
   `LOCKED`, `RETARGET_FOCUS`, or `SNAPSHOT_ROSTER`. Costs are paid once when
   charging begins and are neither refunded nor charged again. Initial locked
   abilities are Jump, Charge, Crushing Blow, and Wormhole-delayed spells.
   Shadow Strike and Arcane Blast use `RETARGET_FOCUS`. Future charged
   `ALL_ENEMIES` actions use `SNAPSHOT_ROSTER`.

6. **Trigger cadence:** Resource spend, runes, and cast-level hooks run once
   per action. Kill records, Bestiary defeats, bounties, quests, soul harvest,
   death marks, enemy-specific Paladin hooks, loot, and explicit on-kill
   resources run once per eligible enemy. Total XP settlement, summon XP,
   level-up, Battle Scar, Demonologist settlement, Grandmaster settlement,
   cleanup, encounter statistics, and `promotion_kits.end_combat` run once per
   encounter. Lycan frenzy checks per kill without extending an active frenzy.

7. **Resolution ledger:** Terminal values are `defeated`, `mercy`, `tamed`,
   `ejected`, and `escaped`, with an optional cause. An encounter is won when
   no unresolved living hostile remains. Ejection awards half XP only and no
   kill, loot, bounty, quest, or on-kill credit. Reward settlement is deferred
   to Slice 5.

8. **Partial progress:** Flee or player defeat discards partial ledger
   progress and all corresponding rewards. A later encounter restores the
   full authored roster; V1 has no persistent attrition.

9. **Flee:** Make one attempt against the fastest living hostile. Smoke Screen
   automatically succeeds only when no living hostile can perceive the user;
   otherwise it contests the fastest perceiving hostile. Windswept is
   target-only ejection, not player flee.

10. **Allies:** Maintain one active player-side slot. An active summon replaces
    the player in that slot. Familiars, companions, and Totems are automatic
    output and cannot be targeted independently. Their actions use the current
    valid focus or the first living authored slot.

11. **Compatibility API:** During Slice 1, `engine.enemy` returns the singleton
    primary enemy. In multi-enemy migration it may return the selected target
    only during an active action context and must raise on ambiguous access.
    Production core uses are removed by the end of Slice 3 and the bridge is
    deleted before curated-pair enablement in Slice 6.

12. **Persistence:** Encounters and their IDs, order, focus, ledger, and
    charges remain runtime-only. Continue reading and writing legacy
    `enemy_state`; do not add `encounter_state` or mid-combat save/resume.

## Deferred Content And Balance Decisions

The following questions remain required before the affected later slice.

13. **What is the intended difficulty budget for a pair?**
    Is a pair expected to be harder than a same-floor singleton, equivalent
    through weaker members, or a rare elite encounter? Define target win rate,
    action count, and resource-pressure bands before tuning.

14. **How often do pairs appear and where?**
    Decide eligible floors, encounter chance, safe/tutorial exclusions, and
    whether pairs can guard chests or quest objectives.

15. **Which compositions are legal?**
    Decide duplicate species, mixed species, hard-control caps, healer/support
    roles, high-burst pairings, and whether authored synergy is desirable in
    the pilot.

16. **How is total XP and loot budgeted?**
    Recommendation: sum eligible member XP and process member loot in slot
    order, then tune individual pair specs. Confirm inventory-full floor drops,
    gold, bounty rewards, and whether a pair receives an encounter-level reward
    multiplier.

17. **How should single-target and all-enemy ability power compare?**
    Define whether area damage uses reduced per-target coefficients, higher
    cost/cooldown, target-count scaling, or full damage. Do not retrofit
    coefficients without simulator and playtest evidence.

18. **Which existing abilities become multi-target first?**
    Hallowed Ground is the reference field but not necessarily the first
    direct-damage ability. Approve a small ability list before resuming broad
    ability-tree authoring.

19. **Are enemy all-target abilities part of V1?**
    With one active player slot they add little targeting value, but they affect
    summons/companions if those become independent targets. Keep them deferred
    unless the ally-side decision requires them.

20. **What is the frontend minimum resolution and information density?**
    Approve Pygame slot/card sizes, detailed-panel behavior, and whether exact
    HP remains hidden without Sight for each enemy independently.

21. **What metrics authorize expansion beyond two enemies or curated pairs?**
    Define crash-free playtest volume, simulator bands, UI readability checks,
    and regression thresholds. More than two enemies requires a separate
    promoted scope decision even if the roster model technically supports it.

## Acceptance Criteria

The initial multi-enemy release is complete only when:

- all approved one-enemy characterization tests still pass;
- the engine supports one or two enemies without a second combat code path;
- every action is validated against an explicit target scope;
- each living combatant gets no more than one ordinary action per round;
- statuses tick at the approved cadence and dead actors never act;
- an all-enemy action pays once and records independent target results;
- rewards and cleanup occur exactly once at their declared enemy/encounter
  cadence;
- mixed kill/removal encounters resolve correctly;
- Pygame makes focus, active actor, HP/status, and duplicate identity legible;
- old singleton saves load without data loss;
- debug selection can force a specific pair;
- simulator and logger output distinguish duplicate combatants;
- scripted bosses and trials remain singleton and retain their existing
  behavior;
- curated pair generation is capped at two and can be disabled independently
  of singleton encounters.

## Validation Plan

Focused implementation validation should grow by slice, beginning with:

```bash
./.venv/bin/python -m pytest \
  tests/core/test_battle_engine.py \
  tests/core/test_combat_result.py \
  tests/core/test_status_effect_interactions.py

./.venv/bin/python -m pytest \
  tests/ui_pygame/test_combat_manager.py \
  tests/ui_pygame/test_combat_view.py

./.venv/bin/python -m pytest \
  tests/core/test_combat_simulator.py \
  tests/core/test_combat_simulator_advanced.py \
  tests/integration/test_battle.py
```

Every implementation slice should also run `git diff --check`. A full core,
integration, and frontend regression run is required before curated pairs are
enabled outside debug mode.
