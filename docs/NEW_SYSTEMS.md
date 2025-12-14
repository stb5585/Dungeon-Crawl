# Dungeon Crawl - New Systems Guide

## Overview of Improvements

This document describes the new systems added to Dungeon Crawl to improve architecture, enable GUI migration, and support balance testing/analytics.

## New Modules

### 1. Combat Action Queue (`combat/action_queue.py`)

A priority-based action queue system for more sophisticated turn-based combat.

**Key Features:**
- Priority-based action execution (IMMEDIATE → HIGH → NORMAL → LOW → DELAYED)
- Speed-based turn order (within same priority)
- Delayed actions (charge-up abilities, status ticks)
- Support for enemy AI action stacks

**Usage Example:**
```python
from combat import ActionQueue, ActionType, ActionPriority

queue = ActionQueue()

# Schedule a fast attack
queue.schedule(
    actor=player,
    action_type=ActionType.ATTACK,
    callback=attack_function,
    target=enemy,
    priority=ActionPriority.HIGH,
    speed_modifier=1.5  # 50% faster
)

# Resolve actions in priority order
while queue.has_ready_actions():
    queue.resolve_next()
```

**Benefits:**
- Enables complex enemy AI behaviors
- Supports simultaneous/multi-actor combat
- Clean separation of action scheduling from execution

### 2. Enhanced Effect System (`effects/`)

Expanded effect types with composition and conditional logic.

**New Effect Types:**
- **Buffs/Debuffs** (`buffs.py`): StatModifierEffect, AttackBuffEffect, DefenseBuffEffect, etc.
- **Composite Effects** (`composite.py`): CompositeEffect, ConditionalEffect, ChanceEffect, ScalingEffect
- **Advanced Effects**: LifestealEffect, ReflectDamageEffect, DamageOverTimeEffect, DispelEffect, ShieldEffect

**Usage Example:**
```python
from effects import CompositeEffect, DamageEffect, ChanceEffect, StatusEffect

# Fireball: Damage + 30% chance to burn
damage = DamageEffect(base_damage=25, scaling=1.5)
burn = StatusEffect(name="Burn", duration=3)
chance_burn = ChanceEffect(burn, chance=0.3)

fireball_effect = CompositeEffect([damage, chance_burn])
```

**Benefits:**
- Abilities can combine multiple effects
- Easy to create complex interactions
- Testable in isolation

### 3. Event System (`events/event_bus.py`)

Event-driven architecture to decouple game logic from UI.

**Key Features:**
- Observer pattern implementation
- 40+ event types (combat, status, UI, world)
- Event history for analytics
- Multiple subscribers per event

**Usage Example:**
```python
from events import get_event_bus, EventType, create_combat_event

bus = get_event_bus()

# Subscribe to damage events
def on_damage(event):
    print(f"{event.actor.name} dealt {event.data['damage']} damage!")

bus.subscribe(EventType.DAMAGE_DEALT, on_damage)

# Emit events from game logic
bus.emit(create_combat_event(
    EventType.DAMAGE_DEALT,
    actor=player,
    target=enemy,
    damage=25
))
```

**Benefits:**
- UI can react to game events without tight coupling
- Easy to add new UI implementations (GUI, web)
- Event history enables analytics

### 4. Presentation Layer (`presentation/interface.py`)

Abstract interface for UI implementations.

**Implementations:**
- `GamePresenter` - Abstract base class
- `NullPresenter` - Headless mode (testing, simulation)
- `ConsolePresenter` - Simple text-based UI
- `EventDrivenPresenter` - Base for event-reactive UIs
- (Future) `CursesPresenter` - Wrap existing curses code
- (Future) `PygamePresenter` - GUI implementation

**Usage Example:**
```python
from presentation import ConsolePresenter

# Use console presenter instead of curses
presenter = ConsolePresenter()
presenter.initialize()

presenter.render_combat(player, enemy, actions=["Attack", "Defend"])
action = presenter.get_player_action(["Attack", "Defend", "Flee"])

presenter.cleanup()
```

**Benefits:**
- Game logic independent of UI technology
- Easy to test without UI
- Swap UIs without changing game code

### 5. Data-Driven Abilities (`data/ability_loader.py`)

Load abilities from YAML files instead of hardcoding.

**Key Features:**
- AbilityFactory - Create abilities from data
- EffectFactory - Create effects from data
- YAML-based ability definitions
- Automatic effect composition

**Example Ability File** (`data/abilities/fireball.yaml`):
```yaml
name: Fireball
type: Spell
subtype: Offensive
description: Launches a ball of fire at the enemy
cost: 15
damage_mod: 1.5
effects:
  - type: damage
    base: 25
    scaling:
      stat: intelligence
      ratio: 1.5
    element: Fire
  - type: chance
    chance: 0.3
    effect:
      type: dot
      dot_type: Burn
      damage_per_tick: 5
      duration: 3
```

**Usage Example:**
```python
from data.ability_loader import AbilityFactory

# Load single ability
fireball = AbilityFactory.create_from_yaml('data/abilities/fireball.yaml')

# Load all abilities from directory
abilities = AbilityFactory.load_abilities_from_directory('data/abilities')
```

**Benefits:**
- Balance changes without code edits
- Moddable by non-programmers
- Easy to test all abilities programmatically

### 6. Combat Analytics (`analytics/combat_simulator.py`)

Tools for balance testing and analysis.

**Key Features:**
- CombatSimulator - Run automated battles
- BalanceReport - Statistical analysis
- Win rate calculation
- Outlier detection (overpowered/underpowered)
- Ability usage tracking

**Usage Example:**
```python
from analytics import CombatSimulator

simulator = CombatSimulator()

# Run 1000 simulations
report = simulator.run_simulations(
    char1=warrior_level_10,
    char2=mage_level_10,
    iterations=1000
)

print(report.generate_summary())
# Win Rates by Class:
# Warrior: 55.3%
# Mage: 44.7%
# Average Turns: 12.4

# Identify balance issues
outliers = report.identify_outliers()
print(outliers['overpowered'])  # Classes with >2 std dev win rate
```

**Benefits:**
- Automated balance testing
- Data-driven balancing decisions
- Foundation for monetizable tools

## Development Tools

### CLI Tool (`dev_tools.py`)

Command-line interface for testing new systems.

**Available Commands:**

```bash
# Test ability loader
python dev_tools.py abilities --directory data/abilities
python dev_tools.py abilities --file data/abilities/fireball.yaml

# Test event system
python dev_tools.py events --verbose

# Test action queue
python dev_tools.py queue

# Test effect system
python dev_tools.py effects

# Run balance simulations (placeholder)
python dev_tools.py balance --iterations 1000

# Generate sample ability YAML files
python dev_tools.py generate --output data/abilities
```

## Migration Path

### Phase 1: Parallel Systems ✅ COMPLETE
- New modules coexist with existing code
- No breaking changes to current game
- All new systems can be tested independently

### Phase 2: Integration (Next Steps)
1. **Modify BattleManager** to use ActionQueue
   - Replace current turn logic with queue-based system
   - Implement enemy action stacks
   
2. **Add Event Emissions** to existing combat flow
   - Emit events on damage, status changes, etc.
   - Keep existing string returns for compatibility
   
3. **Create CursesPresenter** wrapper
   - Wrap existing curses code in GamePresenter interface
   - Test with existing game flow

4. **Start Ability Migration**
   - Convert 5-10 abilities to YAML format
   - Test with new effect system
   - Gradually migrate more abilities

### Phase 3: GUI Development
1. Implement PygamePresenter
2. Subscribe to events for animations
3. Build sprite system
4. Create GUI-specific battle UI

### Phase 4: Analytics Integration
1. Run automated balance tests
2. Identify problematic abilities/classes
3. Use data to drive balance changes
4. Generate reports for monetization demo

## Testing the New Systems

### Test Event System
```bash
python dev_tools.py events --verbose
```

Output shows events being emitted and logged.

### Test Action Queue
```bash
python dev_tools.py queue
```

Shows action scheduling and priority-based execution.

### Test Ability Loading
```bash
python dev_tools.py abilities --directory data/abilities
```

Loads all YAML abilities and displays their properties.

### Test Effects
```bash
python dev_tools.py effects
```

Lists all available effect types.

## File Structure

```
dungeon-crawl/
├── combat/                      # NEW: Combat systems
│   ├── __init__.py
│   └── action_queue.py         # Action queue and turn manager
├── effects/                     # ENHANCED: Effect system
│   ├── __init__.py
│   ├── base.py
│   ├── damage.py
│   ├── healing.py
│   ├── status.py
│   ├── buffs.py                # NEW: Buff/debuff effects
│   └── composite.py            # NEW: Advanced effects
├── events/                      # NEW: Event system
│   ├── __init__.py
│   └── event_bus.py
├── presentation/                # NEW: UI abstraction
│   ├── __init__.py
│   └── interface.py            # GamePresenter and implementations
├── analytics/                   # NEW: Balance testing
│   ├── __init__.py
│   └── combat_simulator.py
├── data/                        # NEW: Data-driven definitions
│   ├── ability_loader.py
│   └── abilities/
│       ├── fireball.yaml
│       ├── power_strike.yaml
│       └── blessing.yaml
├── ARCHITECTURE.md              # NEW: Architecture documentation
├── NEW_SYSTEMS.md              # This file
└── dev_tools.py                # NEW: CLI development tools
```

## Backward Compatibility

All new systems are:
- **Opt-in**: Existing code continues to work
- **Non-breaking**: No changes to current game logic
- **Testable**: Can be used independently

The existing game can run unchanged while new systems are developed and tested in parallel.

## Next Steps for Integration

1. **Choose an integration point** (e.g., start with BattleManager)
2. **Add event emissions** to existing combat without removing strings
3. **Create a feature flag** to toggle new systems on/off
4. **Test thoroughly** with existing save files
5. **Gradually migrate** abilities to data-driven format

## Monetization Considerations

The new systems position Dungeon Crawl for:

1. **Developer Tools** - Combat simulator as a service
2. **Balance Analytics** - Automated balance testing API
3. **Modding Platform** - YAML-based ability/enemy creation
4. **Engine Licensing** - Reusable turn-based combat engine

See `ARCHITECTURE.md` for full monetization strategy.

## Questions or Issues?

The new systems are designed to be:
- **Self-documenting** (see docstrings)
- **Testable** (use `dev_tools.py`)
- **Modular** (can be used independently)

For integration questions, refer to `ARCHITECTURE.md` Phase 2 details.
