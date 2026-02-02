TITLE: Dungeon Crawl (working title)

AUTHOR: Shawn Thomas Booth

CREATION DATE: March 2020

LANGUAGE: Python 3.12+

DEPENDENCIES:
Standard Library
- curses (ui_curses only)
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


## Recent Improvements (February 2026)

Dungeon Crawl has completed a major code restructuring focused on architecture, maintainability, and feature parity:

### Completed Refactoring
- **Data Externalization** - Quest system, dialogues, and special events now in JSON files (src/core/data/content/)
- **Combat Analytics** - BattleLogger integrated in BOTH curses and Pygame UIs for consistent event tracking
- **Import Standardization** - Absolute imports (`src.core.*`) for reliable cross-context execution
- **UI Separation** - Battle managers moved to UI layers (ui_curses/, ui_pygame/), keeping core/ UI-agnostic
- **Path Resolution** - Absolute path handling using `Path(__file__).parent` for test compatibility

### Systems (December 2025)
- **Combat Action Queue** - Priority-based turn system with delayed actions
- **Enhanced Effect System** - 20+ composable effect types (buffs, debuffs, composite effects)
- **Event System** - Event-driven architecture for UI decoupling
- **Presentation Layer** - Abstract UI interface supporting multiple UIs
- **Data-Driven Content** - JSON-based quest/dialogue system (complete), YAML abilities (in progress)
- **Combat Analytics** - BattleLogger with detailed event tracking for balance testing

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
- **[docs/EVENT_EMISSIONS.md](docs/EVENT_EMISSIONS.md)** - describes combat event flow output
- **[docs/NEW_SYSTEMS.md](docs/NEW_SYSTEMS.md)** - User guide for new systems
- **[docs/PROMOTION_ABILITY_RULES.md](docs/PROMOTION_ABILITY_RULES.md)** - outlines ability acquisition at promotion
- **[docs/notes.txt](docs/notes.txt)** - TODO list and development notes

See **[docs/README.md](docs/README.md)** for complete documentation index.

FUTURE DEVELOPMENT:
- Immediate: Populate enemy action stacks, define charging abilities
- Short-term: GUI implementation (Pygame or web-based)
- Medium-term: Complete ability migration to data-driven format
- Long-term: Extract reusable engine, launch developer tools as SaaS

DIRECTORY STRUCTURE (Updated February 2026):
```
src/
  core/          - Game engine (UI-agnostic logic)
                   ├── abilities.py, character.py, classes.py
                   ├── enemies.py, items.py, player.py, town.py, etc.
                   ├── combat/ (action queue, combat_result, battle_logger)
                   ├── data/ (data_loader, content/*.json)
                   └── events/ (event bus)
  ui_curses/     - Terminal UI implementation (curses-based)
                   ├── game.py, menus.py, town.py, map_tiles.py
                   ├── battle.py, enhanced_manager.py (combat UI logic)
                   └── classes.py (promotion UI)
  ui_pygame/     - GUI implementation (Pygame-based)
                   ├── game.py
                   ├── gui/ (combat_manager, shops, character screen, etc.)
                   └── presentation/ (pygame presenter)

ascii_files/     - ASCII art for enemies
map_files/       - Dungeon floor layouts
save_files/      - Player save data
effects/         - Expanded effect system (20+ composable types)
presentation/    - UI abstraction layer (interface + implementations)
data/            - YAML-based ability definitions (in progress)
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
- character.py
- companions.py
- enemies.py
- items.py
- player.py
- races.py
- save_system.py
- town.py
- tutorial.py
- combat/ (battle_logger, combat_result, action_queue)
- data/ (data_loader, content/dialogues.json, quests.json, special_events.json)

FILE DESCRIPTIONS (Core Game Logic - src/core/):
- **abilities.py** - Spells and skills for all character classes
- **character.py** - All characters (players, enemies, companions) with stats and combat logic
- **classes.py** - Class definitions, promotions, and equipment restrictions
- **companions.py** - Warlock familiars, summon creatures, and class companions
- **enemies.py** - Enemy definitions, AI action stacks, and special abilities
- **items.py** - Item system with random generation, special effects, and equipment
- **player.py** - Player character with world interactions, dungeon exploration, treasure
- **races.py** - Racial options for character creation with stat bonuses
- **save_system.py** - Data-driven save/load system (JSON-based)
- **town.py** - Town core logic (quest validation, shop inventory)
- **combat/battle_logger.py** - Combat event logging for analytics (used by both UIs)
- **combat/combat_result.py** - Combat result dataclasses for action outcomes
- **combat/action_queue.py** - Priority-based turn system with charging abilities
- **data/data_loader.py** - JSON data loader with caching for game content
- **data/content/** - JSON files for quests, dialogues, special events
- **events/event_bus.py** - Event system for UI decoupling and animations

UI IMPLEMENTATIONS:
- **src/ui_curses/** - Terminal UI (curses-based, fully functional)
  - game.py - Main ga with quest/shop interactions
  - battle.py - BattleManager with BattleLogger integration
  - enhanced_manager.py - Action queue-based combat manager
  - classes.py - Promotion and familiar selection UI
  
- **src/ui_pygame/** - GUI (Pygame-based, fully functional)
  - game.py - Pygame game loop
  - gui/combat_manager.py - GUI combat with BattleLogger integration (13 logging points)
  - gui/shops.py - Blacksmith, alchemist, jeweler with quest integration
  - gui/inn.py - Tavern interactions with patron dialogues and bounties
  - gui/dungeon_manager.py - First-person dungeon exploration
  - gui/enhanced_dungeon_renderer.py - Perspective tileset rendering
  - game.py - Pygame game loop
  - gui/ - All GUI components (combat, shops, character screen, dungeon renderer, etc.)
  - presentation/pygame_presenter.py - Event-driven presenter with animations

ENTRY POINTS:
- **game_curses.py** - Launch terminal version: `python game_curses.py`
- **game_pygame.py** - Launch GUI version: `python game_pygame.py`
- **launch.sh** - Shell script for terminal version with proper window sizing
