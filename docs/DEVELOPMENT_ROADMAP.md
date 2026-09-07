# The Forsaken Tenet Development Roadmap

*Updated: September 5, 2026*

This roadmap contains only active priorities, ordered candidates, and deferred
decision gates. Shipped history belongs in [`CHANGELOG.md`](../CHANGELOG.md),
and detailed runtime contracts belong in their owner documents.

## Current Baseline

- Pygame is the supported player-facing frontend. Core logic lives under
  `src/core/`; headless tests, simulators, and reports provide non-graphical
  development coverage.
- Flat global progression and all 49 authored class ability trees are shipped.
  [`ABILITY_TREE_DESIGN.md`](ABILITY_TREE_DESIGN.md),
  [`PROMOTION_ABILITY_RULES.md`](PROMOTION_ABILITY_RULES.md), and the
  [`ability_trees/`](ability_trees/) references define the current contract.
- Critical promotion class-kit closure is shipped. Remaining class-kit work is
  evidence-driven tuning, presentation, or separately approved expansion.
- Multi-enemy combat supports one or two enemies through direct APIs and
  development encounter overrides. Ordinary random encounters remain
  singleton.
- The Vesperion/Voluntas endgame route, Class Ring awakening paths, Pygame
  dungeon/town/combat flows, and the current save contract are implemented.

## Planning States

- `Active`: the next planning or implementation program.
- `Ready`: sufficiently bounded to begin after higher-priority work.
- `Spec Gate`: requires an approved behavior and compatibility contract before
  implementation.
- `Evidence Gate`: requires focused automated or manual evidence before a
  decision.
- `Deferred`: intentionally postponed until its dependency is complete.
- `Watch`: preserve current behavior and record issues encountered nearby.

## Active Priority — Foundational Gameplay Refactors

Status: `Active — Specification And Sequencing`

The next development milestone is to settle the gameplay-changing refactors
listed in [`FOUNDATIONAL_REFACTOR_PLAN.md`](FOUNDATIONAL_REFACTOR_PLAN.md).
Broad manual playtesting is deferred because its balance, pacing, and interface
findings would be invalidated by changes to combat timing, targeting, ability
organization, or the combat action interface.

The ordered planning sequence is:

1. Define the canonical ability taxonomy and ownership boundary.
2. Define combat timing, initiative, Speed, dodge, and action scheduling.
3. Define invisibility, reveal, targetability, and area-target interaction.
4. Decide the supported multi-enemy encounter scope and combat-view layout.
5. Define the combat action bar, active/passive organization, and class-resource
   presentation.
6. Decide whether dungeon resting belongs in the same gameplay revision.

This order records dependencies, not pre-approval. Each phase must preserve
stable IDs and the current save shape or explicitly require local development
saves to be reset.

### First Implementation Target

No broad refactor should begin until the first three decision blocks are
approved together: ability metadata, combat timing/accuracy, and targeting.
They share enough runtime and UI assumptions that implementing one against the
old behavior risks immediate rework.

After those decisions, the first implementation slice should establish the
shared core contracts and characterization tests without changing content
balance. UI replacement, encounter expansion, and numeric tuning follow only
after the core rules are stable.

## Evidence Task — Multi-Enemy Pilot 3 Rebenchmark

Status: `Ready — Tree Dependency Complete`

The authored-tree dependency is complete, so the existing floor-3/floor-4
promoted-class matrices may be rerun against the current progression baseline.
This is evidence collection, not authorization to enable random pairs or tune
global combat values.

Use [`MULTI_ENEMY_PILOT_3_PLAN.md`](MULTI_ENEMY_PILOT_3_PLAN.md) for the exact
matrix and retained pre-tree results. The result informs the multi-enemy scope
decision in the foundational refactor:

- whether curated pairs should enter ordinary generation;
- whether floor 5 should be added;
- how enemy-authored area actions resolve; and
- whether the redesigned combat view should support two enemies or a larger
  bounded roster.

Until that decision is approved, keep ordinary generation singleton and keep
rosters larger than two out of scope.

## Deferred Milestone — Broad Manual Playtest

Status: `Deferred Until Foundational Refactors Stabilize`

Manual playtesting remains important, but the comprehensive class-kit,
progression, balance, and endgame pass should begin after the foundational
refactor milestone. Preserve the queue in
[`playtest/CURRENT.md`](playtest/CURRENT.md) and the evidence format in
[`CLASS_KIT_EVIDENCE_NOTES.md`](CLASS_KIT_EVIDENCE_NOTES.md).

During refactor implementation, use only focused manual checks needed to verify
the changed slice. Automated regressions remain mandatory. A reproducible bug
encountered during focused validation may be fixed immediately when the fix is
small and does not settle an open design question by accident.

The broad playtest milestone resumes when:

1. combat timing, targeting, and multi-enemy scope are stable;
2. the combat action interface and resource presentation are stable;
3. current save serialization and any required local-save reset are complete;
4. focused regression suites pass; and
5. the roadmap records the new baseline to test.

## Ready After The Foundational Refactors

These are bounded follow-ups, not current priorities:

| Area | State | First safe slice | Owner |
| --- | --- | --- | --- |
| Final-room and ending continuity | `Ready` | Story-card and dialogue continuity only; no boss or route-rule changes. | [`STORY_AND_ENDGAME_DESIGN.md`](STORY_AND_ENDGAME_DESIGN.md) |
| Postgame town fallout | `Ready` | Local acknowledgement dialogue without changing services, quests, or rewards. | [`QUEST_STORY_INTEGRATION_DESIGN.md`](QUEST_STORY_INTEGRATION_DESIGN.md) |
| Red Dragon continuity | `Ready` | Copy-only distinction between defeat, restoration, and binding outcomes. | [`STORY_AND_ENDGAME_DESIGN.md`](STORY_AND_ENDGAME_DESIGN.md) |
| Presentation readability | `Evidence Gate` | One UI/log or asset fix supported by a concrete readability finding. | [`PRESENTATION_ASSET_DESIGN_GATES.md`](PRESENTATION_ASSET_DESIGN_GATES.md) |
| Class-kit tuning | `Evidence Gate` | One mechanic and one explicit tuning contract. | [`CLASS_KIT_DESIGN_GATES.md`](CLASS_KIT_DESIGN_GATES.md) |

## Deferred Design Gates

| Area | Required before promotion | Owner |
| --- | --- | --- |
| Durability, identification, item modification, equipment actives, and rarity | State model, current serializer, local-save reset policy, UI, economy, and balance contract. | [`EQUIPMENT_ITEMS_ECONOMY_DESIGN_GATES.md`](EQUIPMENT_ITEMS_ECONOMY_DESIGN_GATES.md) |
| Harvesting, salvage, destructible dungeon features, and deeper Cambion rooms | Content beat, tile state, reward, current persistence, and local-save reset policy. | [`DUNGEON_WORLD_ENCOUNTER_DESIGN_GATES.md`](DUNGEON_WORLD_ENCOUNTER_DESIGN_GATES.md) |
| Broader class-kit systems | One track-specific trigger, state, UI, save, action-economy, and tuning spec. | [`CLASS_KIT_DESIGN_GATES.md`](CLASS_KIT_DESIGN_GATES.md) |
| Guardian rooms, mini-bosses, deeper Reflection, and Vesperion tuning | Story trigger, failure/retry behavior, route compatibility, and balance target. | [`STORY_AND_ENDGAME_DESIGN.md`](STORY_AND_ENDGAME_DESIGN.md) |
| Dynamic/spatial audio and final asset replacement | Concrete asset list, runtime routing, fallback, and settings behavior. | [`SOUND_SYSTEM.md`](SOUND_SYSTEM.md) |
| Profiles, achievements, run summaries, and account-wide Bestiary data | Ownership, privacy, storage, migration, and reset contract. | This roadmap plus a future dedicated spec. |
| Broad UI/core cleanup | A concrete duplicated rule or save/testability defect with a bounded extraction plan. | The affected domain owner document. |

## Watch Items

Do not promote these observations directly into numeric or architectural
changes:

- Footpad early damage and survivability.
- Poison duration, application, and immunity consistency.
- Multi-strike accuracy and single-action accounting.
- Ironwall Revenge reliability and Repercussion area tuning.
- Resolve generation and Burst cost.
- Race/class balance deltas.
- Bounty restock pacing.
- Class Ring preservation effects and high-action-economy class kits.

Record combat findings using
[`COMBAT_BALANCE_DESIGN_GATES.md`](COMBAT_BALANCE_DESIGN_GATES.md) and class-kit
findings using [`CLASS_KIT_EVIDENCE_NOTES.md`](CLASS_KIT_EVIDENCE_NOTES.md).

## Working Rules

1. The roadmap owns priority; domain documents own behavior.
2. `CHANGELOG.md` owns shipped history. Do not leave completed phase narratives
   in the active roadmap.
3. Do not implement a `Spec Gate` by inference from a loose idea.
4. Preserve stable ability, node, event, item, quest, and current-save identifiers
   unless the approved slice explicitly requires a local-save reset.
5. Run focused tests for every changed system before broad validation.
6. Update the owner document and roadmap in the same change when a gate is
   promoted, completed, or deferred.
