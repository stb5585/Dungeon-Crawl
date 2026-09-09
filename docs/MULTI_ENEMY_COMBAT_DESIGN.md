# Multi-Enemy Combat Design

## Status

Status: `Implemented One-or-Two-Enemy Support; Ordinary Rollout Deferred`

This document owns the current runtime contract for explicit one- or two-enemy
encounters. The foundational baseline supplies virtual readiness, concealment
legality, actor-relative target scopes, symmetric area resolution, and the
two-hostile cap. Ordinary random generation remains singleton: no pair has
qualified for rollout, and the rollout switch has no catalog entry.

The engine and Pygame support explicit development encounters and overrides.
A proposal to add ordinary pairs, floor-5 content, or larger rosters must meet
the promotion requirements in
[`MULTI_ENEMY_FUTURE_GATE.md`](MULTI_ENEMY_FUTURE_GATE.md). The completed
Pilot 1-3 narrative, evidence matrices, and manual runs remain browsable in
[`history/MULTI_ENEMY_PILOT_3_PLAN.md`](history/MULTI_ENEMY_PILOT_3_PLAN.md).

## Motivation

The singleton encounter baseline makes ordinary combat read as a one-on-one
contest even when an ability's fiction describes an area, formation, pack,
field, or group.
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
- Extend encounter generation, current-save persistence, analytics, and balance
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

## Current Runtime Contract

- `BattleEngine` normalizes legacy singleton construction into an `Encounter`
  and schedules living combatants through virtual readiness with stable IDs.
- Explicit actor-relative `ActionIntent` targets, `TargetScope`,
  `TargetLossPolicy`, and `CombatResultGroup` own validation and area results.
- Invalid intents return a machine-readable validation result; committed
  actions own their scheduling and resource effects, and defeated actors are
  skipped.
- Pygame supports lane selection, keyboard and mouse targeting, focus state,
  target cancellation, and target-loss feedback for one or two enemies.
- Outcomes, rewards, logs, events, and simulator records are roster-aware.
- Ordinary generation remains singleton because no pair qualified. Curated
  pairs require explicit development override keys. The default-on
  `DUNGEON_PILOT3_ROLLOUT` kill switch remains available for an approved
  rollout; saves do not preserve mid-combat snapshots.

## Current V1 Player Experience

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

`BattleEngine(player, enemy, tile, ...)` remains a singleton compatibility
entry point and creates an encounter. The `encounter=` entry point accepts the
roster model; supplying both is an error.

The old contextual `engine.enemy` bridge is removed. Callers use the encounter
primary member, current actor, focus, or an explicit action target according to
their need.

`attacker` and `defender` remain action-resolution aliases. They do not
represent the encounter as a whole and do not own scheduling.

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

Implemented default rules:

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

Counterspell remains retaliation and resolves independently for each affected
target. It does not cancel the cast or another target's portion.

### Defeat And Removal

Zero HP removes an enemy from future turns, but the engine records a semantic
resolution before rewards:

| Resolution | Hostile afterward | Kill credit | Normal loot/XP |
| --- | --- | --- | --- |
| `defeated` | No | Yes | Candidate |
| `mercy` | No | No | Redemption rules |
| `tamed` | No | No | No |
| `ejected` | No | Half | No loot |
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

Implemented separation:

- **per defeated enemy:** kill dictionary, Bestiary defeat, bounty/quest
  progress, soul harvest, eligible loot, enemy-specific class triggers;
- **per resolved non-kill enemy:** mercy, taming, ejection, or escape handling;
- **per encounter:** player effect cleanup, transformation reset, battle scar,
  victory count, encounter-survived count, contract cooling, class-kit
  `end_combat`, total XP award, summon XP award, level-up calculation, boss/tile
  completion.

Total encounter XP is the sum of eligible enemy XP, awarded once after
multipliers. Loot is processed in authored slot order so inventory-full and
floor-drop behavior is deterministic. Flee or player defeat discards partial
ledger progress and rewards; per-kill and per-encounter hooks follow the cadence
defined in the approved decisions below.

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
- Give each slot its own name, Sight-gated HP/MP and status icons, animator,
  target rectangle, recoil/death state, floating text anchor, and telegraph.
- Use a single bright arrow above the focused enemy; omit focus borders and
  selection plates so paired and singleton combat share the same composition.
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

## Current-Save Persistence

The current serializer may contain one tile `enemy_state`; it loads as a
singleton encounter.

If encounters need to persist outside active combat, add a versioned
`encounter_state` with:

- encounter key and source;
- member states in authored slot order;
- canonical enemy serializer payload per member;
- combatant/display identity sufficient to restore duplicates;
- resolution state for members already removed, if partial encounters persist.

During a transition, singleton writers may continue writing `enemy_state`, or
write both forms if the current-save contract requires it. Load precedence must
be explicit when both keys exist. Because saves are pre-release development
artifacts, an approved implementation may instead require a local-save reset.

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

## Ability And Progression Integration

Targeting belongs to the canonical ability definition, not to a progression
node. Tree nodes should continue to reference ability classes/IDs and should
not duplicate `TargetScope`, coefficients, or encounter rules in the
progression manifest.

The target-scope enum, structured-result contract, and ability inventory are
implemented. New abilities must declare scope through the canonical ability
definition and must cover resource, reaction, per-kill, and singleton behavior.
The foundational ability-taxonomy refactor may relocate metadata, but it must
preserve this ownership rule.

Changing only an ability's target scope should not require a progression node
ID change. Renaming or replacing a node/ability identity remains subject to
the current-save and reset rules in `ABILITY_TREE_DESIGN.md`.
