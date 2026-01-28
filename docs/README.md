# Documentation Index

## Architecture & Planning
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Long-term 6-phase migration plan from terminal to GUI, monetization strategy
- **[PHASE_2.md](PHASE_2.md)** - Phase 2 complete reference: Enhanced combat, event emissions, bug fixes ✅
- **[PRE_PHASE_3_CLEANUP.md](PRE_PHASE_3_CLEANUP.md)** - Project configuration and Phase 3 planning

## Implementation Guides
- **[NEW_SYSTEMS.md](NEW_SYSTEMS.md)** - User guide for new systems (action queue, effects, events, etc.)
- **[EVENT_EMISSIONS.md](EVENT_EMISSIONS.md)** - Event system implementation details and usage
- **[PROMOTION_ABILITY_RULES.md](PROMOTION_ABILITY_RULES.md)** - Character promotion ability transition rules with extensibility examples

## Development Notes
- **[notes.txt](notes.txt)** - Personal TODO list, design questions, and feature ideas (not tracked in git)
- **[archive/](archive/)** - Archived documentation and past enhancement plans

## Related Documentation
- **[../tests/README.md](../tests/README.md)** - Test suite documentation (47 passing tests, recent improvements)
- **[../tools/](../tools/)** - Development utilities (dev_tools.py, modify_save.py)

## Project Structure

### Core Modules
```
combat/          - Enhanced combat system (action queue, enhanced manager)
effects/         - Expanded effect system (20+ composable effect types)
events/          - Event-driven architecture (event bus, 40+ event types)
presentation/    - UI abstraction layer (presenter interfaces)
analytics/       - Combat simulation and balance testing
data/            - YAML-based ability definitions
```

## Recent Changes

### Phase 3 Status
- Pygame GUI implementation in progress
- Event system fully integrated with combat
- Character sprite generation system operational
- Test suite expanded to 47 tests with equipment validation

### Latest Fixes (This Session)
- ✅ Two-handed weapon equipment logic (Lancer/Dragoon exception validated)
- ✅ Key Items menu display from special_inventory
- ✅ GitHub Actions CI/CD (upload-artifact v3 → v4)
- ✅ Test suite health (47 passing, 1 skipped, 0 failures)
- ✅ Equipment system tests added (16 new tests)

### Core Game Files
```
game.py          - Main game loop
player.py        - Player character
battle.py        - Combat system (formerly combat.py)
enemies.py       - Enemy definitions
abilities.py     - Ability/spell/skill definitions
items.py         - Item definitions
classes.py       - Character classes
races.py         - Character races
```

## Getting Started

### Run the Game
```bash
./launch.sh
# or with virtual environment
.venv/bin/python game.py
```

### Run Tests
```bash
.venv/bin/python tests/test_integration.py
.venv/bin/python tests/basic_tests.py
```

### Use Development Tools
```bash
.venv/bin/python tools/dev_tools.py --help
.venv/bin/python tools/dev_tools.py effects    # Test effect system
.venv/bin/python tools/dev_tools.py queue      # Test action queue
.venv/bin/python tools/dev_tools.py events     # Test event system
.venv/bin/python tools/dev_tools.py abilities  # Test YAML loader
```

## Configuration

### Enable/Disable Enhanced Combat
The enhanced combat system is controlled by `USE_ENHANCED_COMBAT` flag (default: `True`) in:
- `game.py` (line 18)
- `player.py` (line 19)
- `map_tiles.py` (line 14)

Set to `False` to use traditional combat system. See `PHASE_2.md` for details.

## Project Status

### ✅ Phase 2 Complete: Enhanced Combat System
- **EnhancedBattleManager**: Priority-based turn ordering, action queue integration
- **Event System**: 38 event types with complete coverage (combat, damage, healing, status effects)
- **Telegraph System**: Seeker/Inquisitor foresight shows specific enemy actions
- **YAML Abilities**: 8 charging abilities defined with telegraph messages
- **Enemy Action Stacks**: 9 key enemies populated with ability lists
- **Bug Fixes**: ManaShield, Sandstorm, Meteor, BreatheFire, potions, mid-turn incapacitation
- **Backward Compatible**: Feature flags allow toggling enhanced features

**Phase 2 Deliverables**:
- Status effect event emissions (10+ abilities)
- Granular damage/healing events (critical hits, dodges, blocks, damage types)
- Charging abilities YAML (Meteor, Dragon Breath, Dim Mak, Arcane Blast, etc.)
- Enemy action stacks (Dragons, Behemoth, Assassins, Knights, Disciples, basic enemies)

### Phase 1: Foundation Systems
- Action queue with 5 priority levels
- 20+ composable effect types
- Event bus with 38+ event types
- Presentation layer abstractions (4 implementations)
- Combat analytics framework
- YAML ability loader

### Next: Phase 3 GUI Development
Use Pygame presenter to visualize combat with event-driven animations.

See `ARCHITECTURE.md` for full roadmap, `PHASE_2.md` for Phase 2 details.
