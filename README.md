TITLE: Dungeon Crawl (working title)

AUTHOR: Shawn Thomas Booth

CREATION DATE: March 2020

LANGUAGE: Python 3.11.11

DEPENDENCIES:
Standard Library
- curses
- dataclasses
- glob
- math
- os
- dill
- random
- re
- sys
- time
- typing

3rd Party
- dill 0.3.9
- numpy 2.2.3
- PyYAML 6.x (for data-driven abilities)

EXECUTION:
- source launch.sh (play the game)
- python3 tools/dev_tools.py --help (test new systems)
 
DESCRIPTION:
- A dungeon crawl, text-based RPG that takes inspiration from many games. The current iteration allows for character 
  creation options from race and class selection, random statistical rolls, interactive town format, and 5-level dungeon
  crawl.  
  - Charisma is essentially a luck statistic, lowering cost and improving chance of success

## Recent Improvements (December 2024)

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

DIRECTORY STRUCTURE:
```
combat/          - Enhanced combat system (action queue, enhanced manager)
effects/         - Expanded effect system (20+ composable types)
events/          - Event-driven architecture (event bus)
presentation/    - UI abstraction layer
analytics/       - Combat simulation and balance testing
data/            - YAML-based ability/item definitions
docs/            - All documentation and design notes
tools/           - Development utilities (dev_tools.py, modify_save.py)
tests/           - Test files
```

CORE GAME FILES:
- abilities.py
- battle.py (BattleManager, BattleLogger)
- character.py
- classes.py
- combat_result.py
- companions.py
- enemies.py
- game.py
- items.py
- map_tiles.py
- races.py
- README.md
- town.py
- tutorial.py
- utils.py

FILE DESCRIPTIONS:
- abilities.py
    - Main file for controlling spells and skills of the character classes
- battle.py
    - Main file for handling combat between the player and enemies; includes BattleManager for combat flow and 
      BattleLogger for recording battle events for later analysis
- character.py
    - Main file for controlling the all characters, players, enemies, and companions
- classes.py
    - File that controls the classes available for new characters to choose from; includes function that checks whether 
      an item can be equipped by a player's class
- companions.py
    - File that defines class companions, Warlock familiars and Summon creatures 
- enemies.py
    - Main file for controlling enemies, including the statistics and unique aspects of each enemy
- game.py
    - The primary file for the game; controls how and when the game functions
- items.py
    - Main file for controlling items, including randomly generating for chests and drops
- launch.sh
    - source file used to set the terminal size and launch the game
- map_tiles.py
    - Defines the room tiles of the world and available movement per each tile
- player.py
    - File for controlling the playable character, including all actions/interactions with the world
- races.py
    - File that outlines the various racial options when creating a new character
- README.md
    - General description of program
- town.py
    - Controls the interactions of the character while in town
- tutorial.py
    - File that controls the tutorial; not yet implemented
- utils.py
    - FIle that contains utility functions and classes, including the TUI instances
