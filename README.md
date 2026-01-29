TITLE: Dungeon Crawl (working title)

AUTHOR: Shawn Thomas Booth

CREATION DATE: March 2020

LANGUAGE: Python 3.10+

DEPENDENCIES:
Standard Library
- curses
- dataclasses
- glob
- math
- os
- random
- re
- sys
- time
- typing

3rd Party
- numpy 2.2.3
- PyYAML 6.x (for data-driven abilities)
- pygame 2.5.0+ (for GUI and sprite rendering)
- Pillow 10.0.0+ (for image processing and perspective transforms)

EXECUTION:
- source launch.sh (play the game)
- python3 tools/dev_tools.py --help (test new systems)
 
DESCRIPTION:
- A dungeon crawl, text-based RPG that takes inspiration from many games. The current iteration allows for character 
  creation options from race and class selection, random statistical rolls, interactive town format, and 5-level dungeon
  crawl.  
  - Charisma is essentially a luck statistic, lowering cost and improving chance of success

## Recent Improvements (December 2025)

Dungeon Crawl has been significantly enhanced with modern architecture and forward-thinking systems:

### New Systems
- **Combat Action Queue** - Priority-based turn system with delayed actions
- **Enhanced Effect System** - 20+ composable effect types (buffs, debuffs, composite effects)
- **Event System** - Event-driven architecture for UI decoupling
- **Presentation Layer** - Abstract UI interface (enables GUI migration)
- **Data-Driven Abilities** - YAML-based ability definitions
- **Combat Analytics** - Automated balance testing and simulation framework

### Developer Tools
```bash
python3 tools/dev_tools.py effects       # Test effect system
python3 tools/dev_tools.py queue         # Test action queue
python3 tools/dev_tools.py events        # Test event bus
python3 tools/dev_tools.py abilities -d data/abilities  # Load abilities
```

### Documentation
All documentation is now in the **[docs/](docs/)** directory:
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Complete GUI migration roadmap
- **[docs/NEW_SYSTEMS.md](docs/NEW_SYSTEMS.md)** - User guide for new systems
- **[docs/TEST_SUMMARY.md](docs/TEST_SUMMARY.md)** - Integration test results
- **[docs/QUICK_TEST_GUIDE.md](docs/QUICK_TEST_GUIDE.md)** - Quick testing reference
- **[docs/notes.txt](docs/notes.txt)** - TODO list and development notes

See **[docs/README.md](docs/README.md)** for complete documentation index.

### Strategic Direction
Dungeon Crawl is now positioned as:
1. **A playable game** (terminal now, GUI later)
2. **A technical showcase** (clean architecture, testable systems)
3. **A reusable platform** (extractable combat engine + tools)
4. **A monetizable product** (developer-facing balance/simulation tools)

See **[docs/README.md](docs/README.md)** for complete documentation index.

FUTURE DEVELOPMENT:
- Immediate: Populate enemy action stacks, define charging abilities
- Short-term: GUI implementation (Pygame or web-based)
- Medium-term: Complete ability migration to data-driven format
- Long-term: Extract reusable engine, launch developer tools as SaaS

DIRECTORY STRUCTURE (Updated January 2026):
```
src/
  core/          - Game engine (UI-agnostic logic)
                   ├── abilities.py, battle.py, character.py, classes.py
                   ├── enemies.py, items.py, player.py, town.py, etc.
                   ├── combat/ (action queue, enhanced manager)
                   └── events/ (event bus)
  ui_curses/     - Terminal UI implementation (curses-based)
                   ├── game.py, menus.py, town.py, map_tiles.py
  ui_pygame/     - GUI implementation (Pygame-based, in development)
                   ├── game.py
                   ├── gui/ (combat manager, shops, character screen, etc.)
                   └── presentation/ (pygame presenter)

effects/         - Expanded effect system (20+ composable types)
presentation/    - UI abstraction layer (interface + implementations)
analytics/       - Combat simulation and balance testing
data/            - YAML-based ability/item definitions
assets/          - Sprites, backgrounds, tiles, UI graphics
docs/            - All documentation and design notes
tools/           - Development utilities (dev_tools.py, modify_save.py)
tests/           - Comprehensive test suite
_old_code_archive/ - Archived original files (git-ignored)

game_curses.py   - Terminal game entry point
game_pygame.py   - GUI game entry point
```

CORE GAME FILES (now in src/core/):
- abilities.py
- battle.py (BattleManager, BattleLogger)
- character.py
- combat_result.py
- companions.py
- enemies.py
- items.py
- player.py
- races.py
- save_system.py
- town.py
- tutorial.py

FILE DESCRIPTIONS (Core Game Logic - src/core/):
- **abilities.py** - Spells and skills for all character classes
- **battle.py** - Combat management (BattleManager, BattleLogger, action queue integration)
- **character.py** - All characters (players, enemies, companions) with stats and combat logic
- **classes.py** - Class definitions, promotions, and equipment restrictions
- **companions.py** - Warlock familiars, summon creatures, and class companions
- **enemies.py** - Enemy definitions, AI action stacks, and special abilities
- **items.py** - Item system with random generation, special effects, and equipment
- **player.py** - Player character with world interactions, dungeon exploration, treasure
- **races.py** - Racial options for character creation with stat bonuses
- **save_system.py** - Data-driven save/load system (JSON-based)
- **town.py** - Town interactions, shops, quests, promotions
- **combat/action_queue.py** - Priority-based turn system with charging abilities
- **combat/enhanced_manager.py** - Enhanced battle manager with action queue integration
- **events/event_bus.py** - Event system for UI decoupling and animations

UI IMPLEMENTATIONS:
- **src/ui_curses/** - Terminal UI (curses-based, fully functional)
  - game.py - Main game loop and UI orchestration
  - menus.py - Menu system and popup dialogs
  - town.py - Town UI
  - map_tiles.py - Dungeon rendering
  
- **src/ui_pygame/** - GUI (Pygame-based, in development)
  - game.py - Pygame game loop
  - gui/ - All GUI components (combat, shops, character screen, dungeon renderer, etc.)
  - presentation/pygame_presenter.py - Event-driven presenter with animations

ENTRY POINTS:
- **game_curses.py** - Launch terminal version: `python game_curses.py`
- **game_pygame.py** - Launch GUI version: `python game_pygame.py`
- **launch.sh** - Shell script for terminal version with proper window sizing
