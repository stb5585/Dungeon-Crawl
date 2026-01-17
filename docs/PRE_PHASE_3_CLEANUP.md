# Pre-Phase 3 Cleanup Analysis

This document addresses three key questions before moving to Phase 3 (GUI Development):

1. Project configuration migration to pyproject.toml
2. Architecture restructuring needs
3. Incomplete features requiring implementation

## 1. Project Configuration Migration ✅

### Changes Made

**Created: `pyproject.toml`**
- Modern Python packaging standard (PEP 621)
- Replaces `requirements.txt` for dependency management
- Includes project metadata, dependencies, and tool configurations
- Sets up optional dependencies for `dev` and `gui` (Phase 3)

**Key Sections:**
```toml
[project]
name = "dungeon-crawl"
version = "2.0.0"
dependencies = ["numpy>=2.2.0", "pyyaml>=6.0.2"]

[project.optional-dependencies]
dev = ["pytest>=7.4.2", "pytest-cov>=4.1.0"]
gui = ["pygame>=2.5.0"]  # For Phase 3

[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.black]
line-length = 100

[tool.mypy]
python_version = "3.10"
```

**Migration Steps:**
1. ✅ Created `pyproject.toml` with all project metadata
2. ⏸️ Keep `requirements.txt` for now (backward compatibility)
3. 📋 Future: Remove `requirements.txt` after confirming pyproject.toml works

**Installation Commands:**
```bash
# Install base dependencies
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Install with GUI dependencies (Phase 3)
pip install -e ".[gui]"
```

---

## 2. Architecture Restructuring Analysis

### Current Structure
```
/home/tom/Projects/Dungeon-Crawl/
├── abilities.py          # 6462 lines
├── battle.py             # Combat manager
├── character.py          # Character class
├── classes.py            # Character classes
├── combat_result.py      # Combat results
├── companions.py         # Companion system
├── enemies.py            # 3107 lines
├── game.py               # Main game loop
├── items.py              # 4229 lines
├── map_tiles.py          # Map/dungeon logic
├── player.py             # Player character
├── races.py              # Character races
├── town.py               # Town systems
├── tutorial.py           # Tutorial system
├── utils.py              # Utilities
├── combat/               # Combat subsystems
│   ├── action_queue.py
│   └── enhanced_manager.py
├── effects/              # Effect system
│   ├── base.py
│   ├── damage.py
│   ├── healing.py
│   ├── status.py
│   ├── buffs.py
│   └── composite.py
├── events/               # Event system
│   ├── event_bus.py
│   └── event_types.py
├── presentation/         # UI abstraction
│   └── interface.py
├── data/                 # Data files
│   └── abilities/        # YAML ability definitions
├── analytics/            # Analytics tools
├── tools/                # Dev tools
└── tests/                # Test suite
```

### Recommendation: **DO NOT RESTRUCTURE YET**

**Reasoning:**

1. **Phase 2 Just Completed** ✅
   - Enhanced combat system fully integrated
   - Event emissions working
   - All bugs fixed
   - System is stable

2. **New Modules Already Organized** ✅
   - `combat/` - Combat subsystems
   - `effects/` - Effect system
   - `events/` - Event bus
   - `presentation/` - UI abstraction
   - Modern architecture already in place

3. **Big Files Are Not Problematic**
   - `abilities.py` (6462 lines) - Large but organized by ability type
   - `items.py` (4229 lines) - Item catalog, naturally large
   - `enemies.py` (3107 lines) - Enemy catalog, naturally large
   - These are **data-heavy** files, not logic-heavy

4. **Phase 3 Priorities**
   - GUI implementation is the next major milestone
   - Restructuring would delay GUI work
   - Event system already provides clean separation

5. **Future Refactor Opportunity**
   - After Phase 3 GUI is stable
   - Move to data-driven abilities (Phase 4)
   - `abilities.py` → `data/abilities/*.yaml` migration
   - Then core files become much smaller

### Proposed Module Structure (Phase 4+)

*For future consideration after Phase 3:*

```
dungeon_crawl/
├── __init__.py
├── __main__.py           # Entry point
├── core/
│   ├── __init__.py
│   ├── character.py
│   ├── stats.py
│   ├── resources.py
│   └── status.py
├── game/
│   ├── __init__.py
│   ├── game_loop.py
│   ├── world.py
│   ├── dungeon.py
│   └── town.py
├── combat/
│   ├── __init__.py
│   ├── battle.py
│   ├── action_queue.py
│   ├── enhanced_manager.py
│   └── combat_result.py
├── content/
│   ├── __init__.py
│   ├── abilities.py      # Or migrate to YAML
│   ├── items.py          # Or migrate to YAML
│   ├── enemies.py        # Or migrate to YAML
│   ├── classes.py
│   ├── races.py
│   └── companions.py
├── systems/
│   ├── __init__.py
│   ├── effects/
│   ├── events/
│   └── presentation/
├── data/                 # YAML/JSON data
├── analytics/
├── tools/
└── tests/
```

**Decision: Defer to Phase 4+**
- Focus on Phase 3 GUI first
- Revisit after GUI is stable and working

---

## 3. Incomplete Features Analysis

### ~~Critical Issues~~ ✅ ALL CRITICAL ISSUES RESOLVED

#### ~~A. weapon_damage() special_effect Calls~~ ✅ **FIXED**

**Status:** ✅ **COMPLETE** - All weapon and armor special effects now operational

**Location:** `character.py` lines 325-335, 508-540

**What was Fixed:**
1. **Leer Attack Re-enabled** (lines 325-335):
   - Creates CombatResult object for Leer/Gaze attacks
   - Calls special_effect with CombatResultGroup
   - Petrification effects now work properly

2. **Weapon/Armor Special Effects Re-enabled** (lines 508-540):
   - Creates CombatResult for each successful hit
   - Calls armor special_effect (thorns, reflection)
   - Calls weapon special_effect (life steal, instant death, stun, elemental)
   - Processes Drain and Instant Death flags from results

3. **CombatResultGroup Enhanced** (`combat_result.py`):
   - Added `__getitem__` for subscripting: `results[-1]`
   - Added `__len__` for length checks
   - Maintains backward compatibility with 43 special_effect methods in items.py

4. **items.py Gaze Fix** (line 1657):
   - Fixed missing `result = results.results[-1]` line

**Testing:**
- Created `tests/test_weapon_special_effects.py` - 5/5 tests passing ✅
- Tested: VampireBite life steal, Ninjato instant death, Mjolnir stun, Gaze petrification, armor effects
- All modules import successfully ✅

**Impact:**
- ✅ Life steal weapons restore health on critical hits
- ✅ Elemental damage weapons apply bonus damage
- ✅ Armor thorns/reflection effects work
- ✅ Instant death effects trigger on critical hits
- ✅ Leer/Gaze petrification attacks functional
- ✅ Stun/status effects from weapons apply correctly

**Phase 3 Status:** 🟢 **READY TO PROCEED** - No blocking issues remaining

---

#### B. Companion Ultimate Attacks - NOT IMPLEMENTED 📋

**Location:** `companions.py` - 9 companions missing ultimate attacks

**Missing Ultimates:**
1. **Carbuncle** (line 285) - Ruby Light ultimate
2. **Cait Sith** (line 357) - Slot Machine ultimate  
3. **Chocobo** (line 394) - Chocobo Kick ultimate
4. **Imp** (line 430) - Burning Wheel ultimate
5. **Moogle** (line 467) - Moogle Dance ultimate
6. **Shiva** (line 506) - Wind Shrapnel/Bullets ultimate
7. **Sprite** (line 545) - Life Stream ultimate
8. **Sylph** (line 626) - Whispering Wind ultimate
9. **Tonberry** (line 677) - Everyone's Grudge ultimate

**Current State:**
```python
class Carbuncle(Companion):
    """
    Summon: Carbuncle
    - Carbuncle Beam: Reflect spell
    - Ruby Light: Full party heal
    - Ultimate attack TODO
    """
```

**Impact:**
- Companions less powerful than intended
- Missing endgame companion mechanics
- Incomplete companion progression system

**Priority:** MEDIUM - Feature gap but not blocking Phase 3

---

### Minor Issues (Can Defer to Phase 4+)

#### C. Quest System - Basic Implementation

**Location:** `town.py` line 169
```python
# Quest givers and information; additional quests to be added and rewards need to be optimized TODO
```

**Status:** Basic quest system works, but limited content

**Priority:** LOW - Can expand in content updates

---

#### D. Player Limiter - Unclear Purpose

**Location:** `player.py` line 906
```python
limiter = 1  # TODO
```

**Status:** Unclear what this was intended to limit

**Priority:** LOW - Investigate later

---

#### E. Elemental Armor - Partial Implementation

**Location:** `utils.py` line 803
```python
if item.typ == "Weapon" and item.element:  # TODO change to include armor
```

**Status:** Only weapons have elemental properties, armor doesn't

**Priority:** LOW - Design decision needed

---

#### F. Sheet Music Items - Placeholder

**Location:** `items.py` line 3889
```python
class SheetMusic(Miscellaneous):
    """
    Base sheet music item  TODO
    """
```

**Status:** Class exists but no items or functionality

**Priority:** LOW - Future feature

---

## Summary & Recommendations

### Before Phase 3

**MUST FIX:**
1. ✅ **pyproject.toml** - COMPLETE
2. ⚠️ **weapon_damage special_effect calls** - CRITICAL, must fix
   - Re-enable item/weapon special effects
   - Update to CombatResultGroup API
   - Test all special effect items

**CAN DEFER:**
3. ✅ **Architecture restructuring** - Defer to Phase 4+
   - Current structure is fine for Phase 3
   - New modules already well-organized
   - Restructure after GUI is stable

4. 📋 **Companion ultimates** - Defer to Phase 4
   - Not blocking GUI development
   - Can implement during content expansion

5. 📋 **Minor TODOs** - Defer to Phase 4+
   - Quest expansion, sheet music, elemental armor
   - Address during content/polish phase

### Action Plan

**Immediate (Pre-Phase 3):**
1. ✅ Create pyproject.toml
2. ⚠️ Fix weapon_damage special_effect calls
3. ✅ Document incomplete features (this file)
4. Test special effect items work correctly

**Phase 3 (GUI Development):**
- Proceed with Pygame presenter
- Use event system for animations
- Keep core game logic unchanged

**Phase 4 (Data-Driven & Polish):**
- Migrate abilities to YAML (already 18 charging abilities done)
- Implement companion ultimates
- Consider module restructuring
- Expand quest content
- Complete minor TODOs

---

## Testing Checklist Before Phase 3

- [ ] Fix weapon_damage special_effect calls
- [ ] Test life steal weapons work
- [ ] Test elemental damage weapons work
- [ ] Test armor reflection/thorns work
- [ ] Test Leer natural weapon
- [ ] Verify pyproject.toml installation works
- [ ] All Phase 2 tests still passing
- [ ] Enhanced combat system works
- [ ] Event emissions work
- [ ] No regressions from changes

Once these are complete, Phase 3 GUI development can begin with confidence.
