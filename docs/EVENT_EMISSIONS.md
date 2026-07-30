# Event Emissions Reference

This document is the current reference for the game's event bus and combat
event-emission contract. It owns event payload enrichment rules for the Systems,
Audio, and Meta gates.

## Contract

- Event emission is non-breaking: gameplay must continue if no subscribers are
  registered or a subscriber fails.
- Core mechanics must not depend on presentation subscribers.
- Events should carry structured payloads only when a consumer needs them.
- New event payload fields should be added deliberately and covered when they
  affect UI, audio, diagnostics, analytics, or save-sensitive behavior.

## Core Types

- `src/core/events/event_bus.py`
  - `EventType`
  - `GameEvent`
  - `CombatEvent`
  - `EventBus`
  - `get_event_bus()`
  - `create_combat_event()`
- `src/core/combat/combat_result.py`
  - `CombatResult`
  - `CombatResultGroup`

## Current Emitters

- the focused modules under `src/core/combat/battle_engine/`
  - combat start/end;
  - attack, spell, skill, item, defend, and flee action events.
- the focused modules under `src/core/character/`
  - damage, healing, status application/removal/tick, dodge, block, and critical
    hit helpers.
- the focused modules under `src/core/abilities/`,
  `src/core/data/data_driven_abilities/`, and the
  focused modules under `src/core/effects/`
  - ability/effect-specific damage, healing, and status event helpers.
- `src/ui_curses/enhanced_manager.py`
  - curses enhanced turn start/end events.

## Current Consumers

- `src/ui_pygame/presentation/pygame_presenter.py`
  - combat lifecycle, turn, damage, healing, critical, and status presentation.
- `src/ui_pygame/assets/sound_manager.py`
  - combat, damage, block, healing, spell, skill, item, status, death, and
    level-up audio routing.
- `src/core/analytics/combat_simulator.py`
  - combat-stat summaries and simulator reporting.
- `src/core/combat/battle_logger.py`
  - structured combat diagnostics and JSON export support.

## Event Groups

Combat lifecycle:

- `COMBAT_START`
- `COMBAT_END`
- `TURN_START`
- `TURN_END`
- `ROUND_START`
- `ROUND_END`

Actions:

- `ATTACK`
- `SPELL_CAST`
- `SKILL_USE`
- `ITEM_USE`
- `DEFEND`
- `FLEE_ATTEMPT`

Damage and recovery:

- `DAMAGE_DEALT`
- `DAMAGE_TAKEN`
- `HEALING_DONE`
- `CRITICAL_HIT`
- `MISS`
- `DODGE`
- `BLOCK`

Status and stats:

- `STATUS_APPLIED`
- `STATUS_REMOVED`
- `STATUS_TICK`
- `BUFF_APPLIED`
- `DEBUFF_APPLIED`
- `STAT_CHANGE`
- `HP_CHANGE`
- `MP_CHANGE`

Character, UI, and world:

- `CHARACTER_DEATH`
- `LEVEL_UP`
- `MENU_OPEN`
- `MENU_CLOSE`
- `MESSAGE_DISPLAY`
- `CHOICE_REQUIRED`
- `MOVE`
- `INTERACT`
- `ITEM_PICKUP`
- `ITEM_DROP`
- `QUEST_UPDATE`

## Usage

Subscribe to an event:

```python
from src.core.events.event_bus import EventType, get_event_bus


def on_damage(event):
    print(f"{event.actor.name} dealt {event.data['damage']} damage")


get_event_bus().subscribe(EventType.DAMAGE_DEALT, on_damage)
```

Emit a combat event:

```python
from src.core.events.event_bus import EventType, create_combat_event, get_event_bus


get_event_bus().emit(
    create_combat_event(
        EventType.SPELL_CAST,
        actor=caster,
        target=target,
        spell_name=spell.name,
    )
)
```

Inspect history:

```python
from src.core.events.event_bus import EventType, get_event_bus


bus = get_event_bus()
all_events = bus.get_history()
damage_events = bus.get_history(EventType.DAMAGE_DEALT)
```

## Current Follow-Up Areas

- Current audio routing has weapon identity and attack-source metadata for
  source-specific weapon sounds such as `laser_beam.wav`.
- Item-use events expose item type/subtype metadata for scroll and recovery-item
  audio routing.
- Future source-specific audio should add payload fields only when the emitting
  gameplay layer has a stable source to expose.
- New diagnostics should prefer existing event history and compact summaries
  before adding parallel reporting state.
- Keep event-history retention bounded and avoid emitting presentation-only
  events from core gameplay unless a real consumer needs them.

## Payload Enrichment Gate

Add payload fields only when a concrete UI, audio, diagnostics, analytics, or
tooling consumer needs them. Event emissions must remain non-breaking if no
subscriber exists or if a subscriber fails, and core mechanics must not depend
on presentation subscribers.

Before adding a new field, identify the consumer, the emitting layer with stable
access to the source data, fallback behavior when the field is absent, and the
focused tests that prove old callers still work. Prefer existing event history
and compact diagnostics before adding parallel reporting state.

## Validation

Use focused tests around the systems being changed. For broad event-regression
confidence, run:

```bash
./.venv/bin/python -m pytest tests/core tests/integration -q
```
