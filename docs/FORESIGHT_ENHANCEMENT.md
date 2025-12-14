# Foresight System Enhancement Plan

## Current Implementation
- **Location**: `combat/enhanced_manager.py` in `_get_telegraph_message()` method
- **Current Logic**: 
  ```python
  has_foresight = self.player_char.cls.name in ["Seeker", "Inquisitor"]
  ```
- **Effect**: Seeker and Inquisitor classes see specific enemy actions (telegraphs), other classes see "preparing something..."

## Enhancement Goals
Make foresight accessible to all classes through multiple channels:

### 1. Items
- **Foresight Amulet** (Rare): Grants permanent foresight while equipped
- **Crystal Ball** (Consumable): Grants 3 turns of foresight
- **Third Eye Helm** (Legendary): Grants foresight + reveals enemy health percentages

### 2. Spells
- **Divine Sight** (Cleric, Level 3): Grants foresight for 5 turns, costs 15 MP
- **Precognition** (Mage, Level 4): Grants foresight for current battle, costs 25 MP
- **Battle Insight** (Bard, Level 2): Grants foresight for 3 turns, costs 10 MP

### 3. Abilities
- **Tactical Assessment** (Warrior skill): Passive, grants foresight after observing enemy for 2 turns
- **Hunter's Instinct** (Ranger skill): Passive, grants foresight against beasts and natural creatures
- **Study Opponent** (Monk ability): Active, consumes 1 turn to gain foresight for 4 turns

### 4. Racial Traits
- **Elf Variant** (High Elf): Natural foresight as racial trait
- **Tiefling Variant** (Arcane bloodline): Foresight against spellcasters

### 5. Temporary Buffs
- **Battle Trance**: Consumable potion, 5 turns foresight
- **Sage's Blessing**: Town temple buff, lasts entire dungeon level

## Implementation Plan

### Phase 1: Character Attribute
Add `foresight` tracking to Character class:
```python
# In character.py
@dataclass
class CombatStats:
    # ... existing fields ...
    foresight_turns: int = 0  # 0 = no foresight, -1 = permanent
```

### Phase 2: Update Telegraph Check
Modify `_get_telegraph_message()` to check multiple sources:
```python
def _has_foresight(self) -> bool:
    """Check if player has foresight from any source."""
    # Natural class ability
    if self.player_char.cls.name in ["Seeker", "Inquisitor"]:
        return True
    
    # Temporary buff
    if self.player_char.combat.foresight_turns != 0:
        return True
    
    # Equipped items
    if hasattr(self.player_char, 'inventory'):
        for item in self.player_char.inventory.equipped:
            if item and getattr(item, 'grants_foresight', False):
                return True
    
    # Racial trait
    if hasattr(self.player_char, 'race'):
        if getattr(self.player_char.race, 'has_foresight', False):
            return True
    
    return False
```

### Phase 3: Foresight Tracking
Add turn-based decrement:
```python
# In BattleManager.after_turn() or similar
if self.player_char.combat.foresight_turns > 0:
    self.player_char.combat.foresight_turns -= 1
```

### Phase 4: Item/Spell/Ability Integration
- Add `grants_foresight` attribute to items
- Create foresight-granting spells in `abilities.py`
- Add foresight effects to `effects/buffs.py`

### Phase 5: UI Feedback
Show foresight source to player:
```
"Your Foresight Amulet reveals the enemy's next move..."
"Your Precognition spell shows the enemy preparing..."
"Your Seeker training lets you anticipate the enemy's action..."
```

## Benefits
1. **Build Diversity**: Other classes can access Seeker's signature feature
2. **Strategic Depth**: Players must decide when to use limited foresight resources
3. **Item Value**: Foresight items become highly sought after
4. **Class Identity**: Seeker/Inquisitor still unique (permanent, no cost)
5. **Monetization**: Foresight items can be rare/legendary loot for player retention

## Notes
- Seeker/Inquisitor should keep permanent foresight (class identity)
- Temporary foresight should feel powerful but limited (resource management)
- Multiple sources can stack duration but not quality (no "super foresight")
- Telegraph messages should indicate the source of foresight
