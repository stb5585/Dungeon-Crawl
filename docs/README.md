# Documentation Index

## Architecture & Planning
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - 6-phase migration plan from terminal to GUI, monetization strategy
- **[FORESIGHT_ENHANCEMENT.md](FORESIGHT_ENHANCEMENT.md)** - Future enhancement plan for making foresight accessible to all classes

## Implementation Guides
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Phase 2 integration instructions for EnhancedBattleManager
- **[NEW_SYSTEMS.md](NEW_SYSTEMS.md)** - User guide for new systems (action queue, effects, events, etc.)
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Summary of work completed

## Testing & Quick Start
- **[TEST_SUMMARY.md](TEST_SUMMARY.md)** - Detailed test results and integration status
- **[QUICK_TEST_GUIDE.md](QUICK_TEST_GUIDE.md)** - Quick reference for testing enhanced combat

## Development Notes
- **[notes.txt](notes.txt)** - TODO list, design questions, bug fixes, scaling notes

## Tools & Tests
- **[../tools/](../tools/)** - Development utilities (dev_tools.py, modify_save.py)
- **[../tests/](../tests/)** - Test files (test_integration.py, basic_tests.py)

## Project Structure

### New Modules
```
combat/          - Enhanced combat system (action queue, enhanced manager)
effects/         - Expanded effect system (20+ composable effect types)
events/          - Event-driven architecture (event bus, 40+ event types)
presentation/    - UI abstraction layer (presenter interfaces)
analytics/       - Combat simulation and balance testing
data/            - YAML-based ability definitions
```

### Core Game Files
```
game.py          - Main game loop
player.py        - Player character
combat.py        - Original combat system (still used as base)
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
The enhanced combat system is controlled by `USE_ENHANCED_COMBAT` flag in:
- `map_tiles.py` (line 14)
- `player.py` (line 19)
- `game.py` (line 18)

Set to `False` to use original combat system.

## Recent Changes

### Enhanced Combat Integration (Current)
- Integrated EnhancedBattleManager into all combat scenarios
- Telegraph system for Seeker/Inquisitor (shows specific enemy actions)
- Priority-based turn ordering (speed + action priority)
- Support for charging/multi-turn abilities
- Backward compatible with feature flags

### Phase 1: Foundation Systems
- Action queue with 5 priority levels
- 20+ composable effect types
- Event bus with 40+ event types
- Presentation layer abstractions (4 implementations)
- Combat analytics framework
- YAML ability loader
