# Dungeon Crawl - Changelog

## [Unreleased] - 2025-12-14

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
  - Dependencies: dill, numpy, pyyaml
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
- shadow_strike.yaml, summon_allies.yaml, crushing_blow.yaml
- holy_smite.yaml, power_strike.yaml, blessing.yaml, fireball.yaml

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
