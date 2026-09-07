# Foundational Gameplay Refactor Plan

Status: `Active — Decisions Required Before Implementation`

This document organizes the gameplay-changing work that should be resolved
before broad manual playtesting. It does not approve new mechanics by itself.
Each phase must first replace its open questions with an explicit decision
block covering runtime behavior, UI behavior, compatibility, and validation.

## Why This Precedes Broad Playtesting

Combat timing, targetability, ability classification, encounter size, and the
combat action interface shape nearly every playtest observation. Testing class
balance, pacing, and readability extensively before those foundations settle
would produce short-lived evidence. Focused manual checks remain appropriate
inside each implementation slice; the comprehensive playtest queue resumes
after the refactor baseline is stable.

## Dependency Order

### 1. Ability Taxonomy And Ownership

State: `Spec Gate`

Define canonical metadata for each spell and skill without changing stable
ability IDs merely to improve organization.

The taxonomy should decide:

- origin: arcane, divine, natural, spiritual, extraplanar, innate, or another
  approved set;
- method: manifestation, binding, transformation, channeling, projection, or
  another approved set;
- intent: damage, protection, restoration, control, mobility, information,
  summoning, or another approved set;
- active, passive, reaction, field, summon, and item-action boundaries;
- target scope and target-loss behavior;
- which module owns behavior versus declarative data; and
- how hidden interactions such as Wizard cross-element effects are represented
  without disclosing them in player-facing descriptions.

Implementation should migrate metadata and ownership in small batches with
loader validation and stable-ID regression coverage. File reorganization is a
consequence of the contract, not the first step.

Owner references:

- [`src/core/data/abilities/README.md`](../src/core/data/abilities/README.md)
- [`PROMOTION_ABILITY_RULES.md`](PROMOTION_ABILITY_RULES.md)
- [`MULTI_ENEMY_ABILITY_INVENTORY.md`](MULTI_ENEMY_ABILITY_INVENTORY.md)
- [`WIZARD_CROSS_ELEMENT_INTERACTIONS.md`](WIZARD_CROSS_ELEMENT_INTERACTIONS.md)

### 2. Combat Timing, Speed, And Accuracy

State: `Spec Gate`

Define one combat timing model before extending the existing action-queue helper
or replacing the actor-cycle UI.

The decision must cover:

- initiative and turn ordering;
- whether Speed changes order, action frequency, accuracy, dodge, or a bounded
  subset of those effects;
- elimination of unintended Dexterity or Speed double counting;
- minimum and maximum turn frequency;
- delayed, charged, forced, companion, summon, Totem, and reaction actions;
- status-tick timing and defeat during pre-turn processing;
- deterministic simulator behavior and diagnostics; and
- whether current saves or in-progress combat snapshots are affected and
  whether local saves must be reset.

Numeric balance changes should follow the structural implementation and a new
simulator baseline rather than being bundled into the architecture change.

Owner reference: [`COMBAT_BALANCE_DESIGN_GATES.md`](COMBAT_BALANCE_DESIGN_GATES.md).

### 3. Visibility, Reveal, And Targetability

State: `Spec Gate`

Define invisibility as a targeting rule shared by combat logic, AI, ability
metadata, and presentation.

The decision must cover:

- whether an invisible enemy can be selected by single-target actions;
- whether area actions can affect an unrevealed enemy;
- Sight, detection, Wisdom, class-feature, and scripted reveal sources;
- sprite, token, HP/MP, status, and target-card visibility;
- target loss after an action is chosen;
- AI behavior when no legal visible target exists; and
- boss, trial, transformation, and multi-enemy exceptions.

Do not implement a Pygame-only concealment rule. Core target validation must be
authoritative.

Owner references:

- [`COMBAT_BALANCE_DESIGN_GATES.md`](COMBAT_BALANCE_DESIGN_GATES.md)
- [`MULTI_ENEMY_COMBAT_DESIGN.md`](MULTI_ENEMY_COMBAT_DESIGN.md)
- [`ENEMY_VISUAL_SYSTEM.md`](ENEMY_VISUAL_SYSTEM.md)

### 4. Multi-Enemy Scope And Combat View

State: `Evidence Gate`, then `Spec Gate`

First rerun the Pilot 3 promoted-class matrices now that all authored trees are
complete. Then decide:

- whether curated pairs enter ordinary encounter generation;
- eligible floors, probability, exclusions, telemetry, and a runtime kill
  switch;
- the representative floor-5 second-promotion matrix;
- enemy-authored area-action behavior;
- whether the supported roster remains capped at two;
- battlefield slots, sprite scale, flying offsets, turn-order display, target
  cards, and status readability; and
- reward, quest, Bestiary, loot, and kill-credit behavior for every member.

Do not use local encounter multipliers to hide a class-matrix or action-contract
problem. Do not expand beyond two enemies until the UI and action model have an
approved larger-roster contract.

Owner references:

- [`MULTI_ENEMY_COMBAT_DESIGN.md`](MULTI_ENEMY_COMBAT_DESIGN.md)
- [`MULTI_ENEMY_PILOT_3_PLAN.md`](MULTI_ENEMY_PILOT_3_PLAN.md)

### 5. Combat Actions And Resource Presentation

State: `Spec Gate`

Replace or extend the combat ability menus only after ability categories and
combat timing are stable.

The decision must cover:

- a bounded or unbounded action shortcut bar;
- assignment, rearrangement, defaults, empty slots, and controller/keyboard/
  mouse behavior;
- current-save ownership of player layouts and any required local reset;
- access to actions not placed on the shortcut bar;
- separation of active, passive, reaction, and unavailable abilities;
- spellbook and Character Menu responsibilities;
- charged-action preparation and cancellation;
- class-resource meters below HP/MP, including overflow and color/accessibility;
  and
- multi-target selection and action preview.

The first implementation slice should preserve keyboard behavior and expose the
new model behind a compatibility adapter before removing the current picker.

Owner references:

- [`PRESENTATION_ASSET_DESIGN_GATES.md`](PRESENTATION_ASSET_DESIGN_GATES.md)
- [`CLASS_KIT_DESIGN_GATES.md`](CLASS_KIT_DESIGN_GATES.md)
- [`CLASS_RING_SYSTEM.md`](CLASS_RING_SYSTEM.md)

### 6. Dungeon Rest And Recovery

State: `Decision Gate`

Decide whether resting is part of this foundational milestone or a later
exploration feature. A promoted spec must define recovery amounts, resource
reset behavior, interruption odds, initiative loss, usable tools/items,
location restrictions, save behavior, and the relationship to Inns and other
recovery services.

Owner reference:
[`DUNGEON_WORLD_ENCOUNTER_DESIGN_GATES.md`](DUNGEON_WORLD_ENCOUNTER_DESIGN_GATES.md).

## Progression Boundary

The flat-level, separate-currency, point-purchased tree system is the current
shipped baseline. All 49 trees were completed after the earlier
progression checkpoint, so that checkpoint is no longer an active plan.

Do not reopen progression as incidental cleanup. A replacement progression
proposal must explicitly decide:

1. whether global levels and separate progression/attribute currencies remain;
2. whether abilities, passives, and promotions share one tree;
3. how learned abilities participate in later class development;
4. how promotions close or carry options forward;
5. which class resources are inherent versus purchased; and
6. how node ownership is serialized and whether local saves must be reset.

State: `Hold Unless Explicitly Promoted`.

## Decision Block Template

Every phase must answer:

```text
Problem:
Current behavior:
Target behavior:
In scope:
Out of scope:
Core owner:
UI surfaces:
Stable IDs and current-save/reset policy:
Failure and fallback behavior:
Automated regression targets:
Focused manual validation:
New simulator or diagnostic evidence:
```

## Milestone Exit Criteria

The foundational refactor milestone is complete when:

- approved core contracts are implemented without unresolved compatibility
  adapters that change gameplay;
- stable identifiers and current-save behavior are validated;
- combat simulator baselines have been regenerated for the new rules;
- the supported combat UI represents every legal action and target state;
- focused automated and manual checks pass for each changed slice; and
- [`playtest/CURRENT.md`](playtest/CURRENT.md) has been rebased onto the new
  gameplay baseline.
