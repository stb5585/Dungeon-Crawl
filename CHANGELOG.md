# Dungeon Crawl - Changelog

## [Unreleased] - 2026-05-06

### Changed

#### Pygame Renderer and Combat UI Polish
- Improved combat status icon readability with urgent-effect prioritization, duplicate compaction, counted labels, Maelstrom Weapon stack visibility, stronger alert coloring, and shared helper behavior across the main combat view and dungeon-combat HUD.
- Tightened combat telegraph presentation with warning-colored wrapped log lines, a dedicated banner that tracks the full latest telegraph message, and clearing behavior after non-telegraph follow-up messages.
- Fit long combat selection labels and turn-indicator subtitles by rendered width so dense item/spell/skill names and long player/enemy names stay inside their UI surfaces.
- Hardened stale-input handling across Pygame popups and navigation loops, including town menus, class/race/load/shop selection, shared popup menus, dungeon escape/loot/key-use prompts, combat action/submenu selectors, shop screens, and the character screen.
- Expanded dungeon renderer smoke coverage around side-corridor walls, open/closed and hidden Ore Vault doors, side-door state preservation, depth-3 outer floor/ceiling slot routing, and left/right floor-special placement parity.

### Documentation
- Updated `docs/DEVELOPMENT_ROADMAP.md` with the completed Pygame polish items and current follow-up notes.

## [Unreleased] - 2026-02-22

### Added

#### Sound System (2026-02-22) 🔊
- **Complete sound manager with event-driven audio**
  - SoundManager class with pygame.mixer integration
  - Automatic pygame.mixer initialization (44.1kHz, 16-bit, stereo)
  - 16 simultaneous sound channels
  - Sound effect caching for performance
  - Graceful handling of missing audio files
  
- **Event-driven sound effects**
  - Combat sounds: hit, heavy_hit, critical_hit, victory, defeat, flee
  - Spell sounds: cast, fire, ice, lightning, heal, buff, debuff
  - Status effects: poison, stun, burn
  - Character events: heal, level_up, player_death, enemy_death
  - UI sounds: menu_select, menu_confirm, menu_cancel
  
- **Background music support**
  - Looping music with fade in/out transitions
  - Separate music directory structure
  - Designed for location-based and combat music
  
- **Volume controls**
  - Independent master, SFX, and music volume
  - Enable/disable sound system
  - Volume ranges from 0.0 to 1.0
  
- **Development tools**
  - `tools/generate_placeholder_sounds.py` - Creates simple beep sounds for testing
  - Generates 30+ sound effects as sine wave tones
  - Requires numpy and scipy for tone generation
  
- **Documentation**
  - `docs/SOUND_SYSTEM.md` - Comprehensive sound system guide
  - `assets/sounds/README.md` - Sound effects catalog
  - `assets/music/README.md` - Music tracks guide

#### Map and Sprite Tooling (2026-02-22)
- **Enemy sprites**: 42 new 32x32 enemy sprites for pygame UI
- **Tiled integration tools**
  - `tools/generate_tiled_tileset.py` - Creates Tiled .tsx tilesets
  - `tools/convert_maps_to_tiled_json.py` - Converts text maps to Tiled JSON
  - `tools/sprite_sheet_extractor.py` - Extracts sprites from sheets
  - `tools/sprite_merger.py` - Combines sprites into composite images

## [Unreleased] - 2026-01-28

### Major Reorganization - Code Structure Overhaul ✅

#### Codebase Reorganization
**Complete restructuring into modular architecture**:
- **src/core/** - All game logic modules (UI-agnostic)
  - Moved: abilities.py, battle.py, character.py, classes.py, combat_result.py
  - Moved: companions.py, enemies.py, items.py, map_tiles.py, player.py
  - Moved: races.py, save_system.py, town.py, tutorial.py
  - Kept: combat/ and events/ subdirectories
  
- **src/ui_curses/** - Terminal UI implementation
  - Moved: game.py, menus.py, town.py from root
  - Clean separation from game logic
  
- **src/ui_pygame/** - GUI implementation (Pygame)
  - Organized: gui/ directory with all pygame components
  - Created: presentation/pygame_presenter.py for event-driven UI
  
- **_old_code_archive/** - Archived original files
  - Git-ignored for safety during reorganization
  - Original file structure preserved

#### Import System Overhaul
**Fixed 20+ import errors across reorganized codebase**:
- **Core Modules**: Updated all imports to use relative imports (`from . import`, `from .. import`)
- **UI Modules**: Fixed cross-boundary imports (`from ..core import`, `from ...core import`)
- **Pygame GUI**: Corrected all relative import paths in gui/ subdirectories
- **Module-Level Imports**: Moved all local function imports to module level
- **Circular Dependencies**: Resolved with proper import structure

**Files Fixed** (20+ files):
- src/core/abilities.py (8 import fixes + 3 bugfixes for missing code)
- src/core/town.py (added enemies import)
- src/core/player.py (removed invalid utils import, fixed Mimic instantiation)
- src/core/classes.py (removed try/except fallbacks, added module imports)
- src/core/save_system.py (added enemies import, fixed indentation)
- src/ui_curses/town.py (added enemies import)
- src/ui_pygame/gui/combat_manager.py (fixed TYPE_CHECKING imports)
- src/ui_pygame/gui/enhanced_dungeon_renderer.py (added DIRECTIONS import)
- src/ui_pygame/gui/popup_menus.py (added module-level items import)
- And 10+ more files with import corrections

#### Code Quality Improvements
- **Syntax Errors Fixed**: 3 syntax errors from incomplete edits (abilities.py, save_system.py)
- **Indentation Fixed**: Corrected indentation errors in save_system.py
- **Missing Code Restored**: Added missing popup/result assignments in abilities.py
- **Dead Code Removed**: Eliminated unreachable pygame code in curses menus.py

#### Verification
- ✅ **Both UIs Working**: Terminal (curses) and GUI (pygame) both import successfully
- ✅ **Zero Import Errors**: Comprehensive grep search confirms no bad imports remain
- ✅ **All Tests Passing**: Import verification test passes for all critical modules
- ✅ **Entry Points Functional**: Both game_curses.py and game_pygame.py launch correctly

#### Developer Experience
- **Clearer Structure**: Logical separation of concerns (core vs UI)
- **Easier Navigation**: Files organized by purpose
- **Better Imports**: Consistent relative import patterns
- **Future-Proof**: Ready for additional UI implementations (web, mobile)

---

## [Phase 3 Started] - 2025-12-14

### Phase 3 Started - GUI Development with Pygame 🎮

#### Pygame Integration
- **Pygame 2.6.1 Installed**: Modern 2D graphics library for Python
- **PygamePresenter**: Complete presenter implementation with event subscriptions
- **Combat UI**: Character sprites, health/mana bars, status effects, turn display

#### Visual Features
- **Floating Damage Numbers**: Animated text showing damage/healing with color-coded types
- **Screen Shake**: Dynamic camera shake for critical hits and big damage
- **Combat Log**: Scrolling text log at bottom of screen
- **Telegraph Display**: Warning messages for charging abilities (Seeker/Inquisitor)
- **Status Icons**: Visual indicators for active status effects

#### Event Integration
- **COMBAT_START/END**: Initialize combat UI, display victory/defeat
- **DAMAGE_DEALT**: Create floating damage text with type-specific colors
- **HEALING_DONE**: Green floating text for healing
- **CRITICAL_HIT**: Enhanced visual feedback with extra screen shake
- **STATUS_APPLIED**: Add status to character display
- **TURN_START**: Update turn counter

#### Damage Type Colors
- Physical (White), Fire (Red), Ice (Light Blue), Lightning (Yellow)
- Poison (Green), Holy (Gold), Shadow/Arcane (Purple), Drain (Dark Red)

#### Next Steps
- Create sprite assets for characters and enemies
- Add spell effect animations
- Implement particle systems
- Create main menu and game over screens
- Add sound effects and music

---

### Phase 2 Complete - Enhanced Combat System ✅

#### Major Features Added
- **Action Queue System**: Turn-based combat with priority system (IMMEDIATE, HIGH, NORMAL, LOW, DELAYED)
- **Charging Abilities**: 18 abilities with charge times and telegraph messages for tactical gameplay
- **Event System**: 38 status effect events + combat events (damage, healing, dodge, block, critical hit)
- **YAML Ability System**: Externalized ability definitions for easier balance and modding

#### Combat Enhancements
- **Telegraph Messages**: Seeker/Inquisitor classes get foresight warnings about charging enemy abilities
- **Enhanced Battle Manager**: Full action queue integration with 117 enemy ability stacks
- **Status Effect Events**: All 38 status effects emit events with proper duration/source tracking
- **Damage/Healing Events**: Combat actions emit events for future GUI animations

#### Critical Fixes

##### Weapon Special Effects Re-enabled (Dec 14, 2025)
**Issue**: All weapon and armor special effects were disabled during CombatResultGroup API refactor
- 43 special effect methods completely non-functional
- Life steal, instant death, elemental damage, stun effects broken
- Leer/Gaze petrification attacks not working
- Armor thorns/reflection inactive

**Resolution**:
- **character.py** (lines 325-335, 508-540): Re-enabled special_effect calls with CombatResultGroup integration
- **combat_result.py** (lines 50-62): Made CombatResultGroup subscriptable (added `__getitem__`, `__len__`)
- **items.py** (line 1657): Fixed Gaze weapon missing result assignment
- **tests/test_weapon_special_effects.py**: Created comprehensive test suite (5/5 passing)

**Impact**: All weapon/armor special effects now operational - life steal, instant death, stun, elemental damage, petrification, thorns/reflection all working.

#### Project Configuration
- **pyproject.toml**: Modern Python packaging with PEP 621 standard
  - Dependencies: numpy, pyyaml
  - Dev dependencies: pytest, pytest-cov
  - GUI dependencies: pygame (for Phase 3)
  - Tool configs: pytest, black, mypy, isort, coverage
  - Entry point: `dungeon-crawl` command

#### YAML Ability Files Created (18 total)
**2-turn charge abilities**:
- meteor.yaml, dragon_breath.yaml, detonate.yaml

**1-turn charge abilities**:
- jump.yaml, charge.yaml, true_strike.yaml, true_piercing_strike.yaml
- ultima.yaml, disintegrate.yaml, dim_mak.yaml, arcane_blast.yaml
- shadow_strike.yaml, crushing_blow.yaml
- blessing.yaml, fireball.yaml

**Features**:
- Telegraph messages for foresight mechanics
- Special mechanics: prone_while_charging, unblockable, guaranteed_hit, ignore_defense
- Future: Cooldown system documented for Phase 3 implementation

#### Code Quality
- Removed unused imports (abilities.py - 4 effect imports)
- Fixed module conflicts (combat.py → battle.py)
- Added type hints with `from __future__ import annotations`
- Fixed mutable default arguments in dataclasses

#### Documentation
- **docs/PHASE_2.md**: Complete Phase 2 status and features
- **docs/ARCHITECTURE.md**: System architecture and design decisions
- **docs/PRE_PHASE_3_CLEANUP.md**: Pre-Phase 3 analysis and recommendations
- **data/abilities/README.md**: YAML ability system documentation
- **tests/**: Integration tests (6/6 passing), weapon special effects tests (5/5 passing)

#### Testing
- ✅ All modules import cleanly
- ✅ Enhanced combat manager integration (117/117 enemy stacks)
- ✅ Event system (38/38 status events + combat events)
- ✅ Weapon special effects (5/5 test suite passing)
- ✅ Action queue system functional
- ✅ YAML ability loader working

### Phase 3 Readiness 🟢

**Status**: Ready to proceed with GUI development

**What's Complete**:
- ✅ Event system for animations (38 status + 6 combat event types)
- ✅ Action queue for turn order display
- ✅ Combat mechanics fully functional
- ✅ Presentation interface ready for Pygame implementation
- ✅ Telegraph messages for UI display
- ✅ All special effects working

**Next Steps**:
1. Install Pygame: `pip install -e '.[gui]'`
2. Implement Pygame presenter in `presentation/pygame_presenter.py`
3. Create combat UI: sprites, health/mana bars, status icons
4. Add animations using event system
5. Implement telegraph message UI for Seeker/Inquisitor foresight

### Deferred to Phase 4+
- **Architecture Restructuring**: Current structure is functional, defer until after GUI stable
- **Companion Ultimate Attacks**: 9 missing (Carbuncle, Cait Sith, Chocobo, Imp, Moogle, Shiva, Sprite, Sylph, Tonberry)
- **Full YAML Migration**: 18/215 abilities done, complete remaining 197 in Phase 4
- **Quest System Expansion**: Basic system works, add more content later

---

## Format
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### Types of changes
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities
