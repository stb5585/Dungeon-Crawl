# Quick Reference: Testing Enhanced Combat

## What Changed
Enhanced combat system is now **ACTIVE** in the game with a feature flag for easy toggling.

## Test Checklist

### 1. Basic Combat Flow ✅
- [x] Integration tests pass (`python3 test_integration.py`)
- [x] EnhancedBattleManager imports successfully
- [ ] **YOU TEST**: Start game and enter combat

### 2. Foresight System ✅
- [x] Seeker/Inquisitor see specific enemy actions
- [x] Other classes see "preparing something..."
- [ ] **YOU TEST**: Try with Seeker vs Warrior class

### 3. Turn Priority ✅
- [x] Fast characters act before slow characters
- [x] Quick skills get HIGH priority
- [x] Spells/attacks get NORMAL priority
- [ ] **YOU TEST**: Verify turn order makes sense

### 4. Charging Actions ⏳
- [x] Framework implemented
- [ ] Need to define charging abilities in YAML
- [ ] Need to populate enemy action stacks

## How to Test

### Quick Test (Recommended)
```bash
# Launch the game
./launch.sh

# Or with virtual environment
/home/tom/Projects/Dungeon-Crawl/.venv/bin/python game.py
```

1. Create a **Seeker** or **Inquisitor** character
2. Enter combat (find an enemy room)
3. Observe if you see specific enemy actions in telegraphs
4. Create a **Warrior** or **Mage** character
5. Enter combat again
6. Observe if you see generic "preparing something..." messages

### If Combat Breaks

**Option 1: Disable Enhanced Combat**
Edit these files and change:
```python
USE_ENHANCED_COMBAT = False
```
In:
- `map_tiles.py` (line 14)
- `player.py` (line 19)  
- `game.py` (line 18)

**Option 2: Check for Errors**
Look at the terminal output - if there's an error, it will show which file/line failed.

## Expected Behavior

### With Seeker/Inquisitor
```
Enemy Turn:
The Goblin is preparing a Power Attack!
[Enemy attacks with Power Attack]
```

### With Other Classes
```
Enemy Turn:
The Goblin is preparing something...
[Enemy attacks]
```

### Turn Order Example
```
Round 1:
1. You (DEX 16) - Quick Strike [HIGH priority]
2. Fast Goblin (DEX 14) - Attack [NORMAL priority]
3. Slow Orc (DEX 8) - Attack [NORMAL priority]
```

## Current Limitations

1. **Enemy Action Stacks**: Not yet populated
   - Enemies use existing AI for now
   - Telegraph system works but shows generic abilities
   
2. **Charging Abilities**: Not yet defined
   - No multi-turn spells in YAML yet
   - System is ready, just needs data
   
3. **Foresight Items**: Not yet implemented
   - Only Seeker/Inquisitor have foresight
   - Enhancement plan in `FORESIGHT_ENHANCEMENT.md`

## Files Changed

### Core Integration
- ✅ `combat/enhanced_manager.py` - Enhanced combat manager
- ✅ `map_tiles.py` - Spring encounters
- ✅ `player.py` - Mimic encounters  
- ✅ `game.py` - Room encounters

### Testing & Documentation
- ✅ `test_integration.py` - Integration test suite
- ✅ `TEST_SUMMARY.md` - Detailed test results
- ✅ `FORESIGHT_ENHANCEMENT.md` - Future enhancement plan
- ✅ `QUICK_TEST_GUIDE.md` - This file

### Existing Systems (No Changes)
- ✅ `combat/action_queue.py` - Action queue (tested ✅)
- ✅ `effects/` - Enhanced effects (tested ✅)
- ✅ `events/` - Event system (tested ✅)
- ✅ `presentation/` - UI abstraction (tested ✅)
- ✅ `analytics/` - Combat simulator (tested ✅)
- ✅ `data/` - YAML ability loader (tested ✅)

## Troubleshooting

### "ImportError" when launching
**Solution**: Make sure you're using the virtual environment:
```bash
/home/tom/Projects/Dungeon-Crawl/.venv/bin/python game.py
```

### "AttributeError" in combat
**Solution**: Disable enhanced combat temporarily, report the error:
```python
USE_ENHANCED_COMBAT = False
```

### Combat feels the same
**Expected**: Turn order might be more logical, but otherwise similar
- The queue system is active but enemies don't have complex action stacks yet
- Foresight only shows for Seeker/Inquisitor
- Multi-turn abilities not yet defined

### Want to see the queue in action?
Run the dev tools:
```bash
/home/tom/Projects/Dungeon-Crawl/.venv/bin/python dev_tools.py queue
```

## Next Development Steps

1. **Test in gameplay** ← YOU ARE HERE
2. **Define charging abilities** (YAML files)
3. **Populate enemy AI stacks** (enemy definitions)
4. **Add event emissions** (for GUI/analytics)
5. **Implement foresight items** (spells/abilities/equipment)

---

**Ready to test!** Launch the game and report any issues.
