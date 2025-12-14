# Phase 2 Integration Guide

## Action Queue Integration

The action queue system has been integrated into combat through the `EnhancedBattleManager` class.

### Key Design Decisions

1. **Still Turn-Based**: Combat remains turn-based, just with smarter ordering
2. **Telegraph System**: 
   - Default: "Enemy is preparing something..."
   - Seeker/Inquisitor: "Enemy is preparing Dragon Breath!"
3. **Backward Compatible**: Can toggle between traditional and enhanced modes

### Integration Status

✅ **Complete**:
- `EnhancedBattleManager` class created
- Action queue integration
- Telegraph system for charging abilities
- Priority and speed-based turn order
- Seeker/Inquisitor-specific information reveal

⏳ **Next Steps**:
1. Test with actual combat
2. Add event emissions
3. Define charging abilities
4. Implement enemy action stacks

### How to Use

#### Option 1: Drop-in Replacement (Recommended for Testing)

```python
# In map_tiles.py or wherever combat is initiated
from combat.enhanced_manager import EnhancedBattleManager

# Instead of:
# battle_manager = BattleManager(game, enemy)

# Use:
battle_manager = EnhancedBattleManager(game, enemy, use_queue=True)
```

#### Option 2: Feature Flag

```python
# In game.py or config
USE_ACTION_QUEUE = True  # Set to False to use traditional combat

# Then in combat initiation:
if USE_ACTION_QUEUE:
    battle_manager = EnhancedBattleManager(game, enemy)
else:
    battle_manager = BattleManager(game, enemy)
```

#### Option 3: Gradual Migration

Keep both systems, let player choose:
```python
# In settings menu
if player_settings['advanced_combat']:
    battle_manager = EnhancedBattleManager(game, enemy)
else:
    battle_manager = BattleManager(game, enemy)
```

### Action Properties

The system automatically determines action properties:

| Action Type | Priority | Delay | Notes |
|------------|----------|-------|-------|
| Attack | NORMAL | 0 | Standard attack |
| Quick Skill | HIGH | 0 | Skills with "Quick" in name |
| Normal Skill | NORMAL | 0 | Most skills |
| Low-cost Spell | NORMAL | 0 | Cost ≤ 20 mana |
| High-cost Spell | NORMAL | 1 | Cost > 20 mana (charges) |
| Item Use | NORMAL | 0 | Items execute normally |
| Flee | HIGH | 0 | Fast escape attempt |
| Defend | HIGH | 0 | Reactive defense |

### Charging Actions

When an action has `delay > 0`:

**Turn 1**: 
```
Player casts Meteor (cost 25)
"You begin charging Meteor..."
Enemy attacks
```

**Turn 2**:
```
"Continuing to charge Meteor... (1 turn remaining)"
Enemy attacks
```

**Turn 3**:
```
Meteor executes!
Enemy's turn
```

### Telegraph Messages

#### Default (Most Classes)
```
"Goblin is preparing something..."
```

#### Seeker/Inquisitor Classes
```
"Dragon is preparing Fire Breath!"
```

This creates strategic value for information-gathering classes.

### Enemy Action Stacks

Enemies can now have complex AI:

```python
# Example: Boss with multi-phase strategy
enemy.action_stack = [
    ("Use Skill", "Power Up"),      # Phase 1: Buff
    ("Attack", None),                # Phase 2: Attack
    ("Attack", None),                # Phase 3: Attack again
    ("Cast Spell", "Fireball"),      # Phase 4: Nuke
    ("Use Item", "Health Potion"),   # Phase 5: Heal if needed
]
```

The queue system will execute these in order, factoring in priority/speed.

### Testing

Test the enhanced manager:

```bash
# Run basic combat flow test
python3 -c "
from combat.enhanced_manager import EnhancedBattleManager
print('EnhancedBattleManager imported successfully!')
print('Action queue integration ready for testing.')
"
```

### Configuration

Add to `game.py` or create `config.py`:

```python
# Combat Configuration
COMBAT_CONFIG = {
    'use_action_queue': True,         # Enable enhanced combat
    'telegraph_all': False,           # False = only Seeker/Inquisitor see details
    'charge_threshold': 20,           # Spells > 20 mana charge for 1 turn
    'quick_skill_priority': True,     # Skills with "Quick" get HIGH priority
}
```

### Known Considerations

1. **Charging System**: Currently only high-cost spells charge. Need to define which abilities should charge explicitly.

2. **Enemy AI**: The `enemy.action_stack` mentioned in notes.txt is now supported but needs to be populated for each enemy type.

3. **Speed Scaling**: Very high/low DEX differences might lead to one-sided battles. May need balance tuning.

4. **Summon Coordination**: Summons currently use simple AI (always attack). Could be enhanced.

### Event Integration (Next Phase)

Once action queue is tested, add event emissions:

```python
from events import get_event_bus, EventType, create_combat_event

# In _execute_scheduled_action:
event_bus = get_event_bus()
event_bus.emit(create_combat_event(
    EventType.ACTION_EXECUTED,
    actor=scheduled_action.actor,
    target=self.defender,
    action_type=scheduled_action.action_type.value
))
```

This will enable:
- GUI to animate actions
- Analytics to track action patterns
- Logging for debugging

### Migration Checklist

- [x] Create EnhancedBattleManager
- [x] Implement action queue integration
- [x] Add telegraph system
- [x] Seeker/Inquisitor information reveal
- [ ] Test with actual combat
- [ ] Define charging abilities data
- [ ] Populate enemy action stacks
- [ ] Add event emissions
- [ ] Performance testing
- [ ] Balance tuning

### Performance Notes

The action queue adds minimal overhead:
- Sorting is O(n log n) where n = number of actions per round (typically 2-4)
- Memory: One ActionQueue instance per battle
- No impact on save file size

### Rollback Plan

If issues arise:
1. Set `use_queue=False` in EnhancedBattleManager
2. Falls back to traditional turn-based combat
3. No save file corruption
4. Players can toggle in settings

## Next: Defining Charging Abilities

Create `data/charging_abilities.yaml`:

```yaml
# Abilities that require charging
charging_abilities:
  # Spells
  Meteor:
    charge_time: 2
    telegraph_message: "summoning a meteor from the sky"
  
  Dragon Breath:
    charge_time: 1
    telegraph_message: "inhaling deeply"
  
  Ultimate Blast:
    charge_time: 3
    telegraph_message: "gathering immense power"
  
  # Skills
  Limit Break:
    charge_time: 2
    telegraph_message: "channeling inner strength"
  
  Snipe:
    charge_time: 1
    telegraph_message: "taking careful aim"
```

This data can be loaded by EnhancedBattleManager to determine charge times.
