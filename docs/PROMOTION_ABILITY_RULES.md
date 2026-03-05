# Promotion Ability Transition Rules

## Overview

When characters promote to new classes, some abilities are lost while others may be retained or gained. This system provides clear, maintainable rules for these transitions.

## Why Ability Transitions?

Certain promotions represent a fundamental shift in how a character operates:

- **Mage → Warlock**: Shifts from Arcane magic to Shadow magic. Loses access to elemental spells but retains Enfeeble as it applies to both magic disciplines.
- **Healer → Monk**: Abandons magical training to focus on physical chi. Loses all spells entirely.
- **Footpad → Inquisitor**: Abandons stealth in favor of investigation. Loses all stealth-based skills.
- **Warrior → Weapon Master**: Specializes in dual-wielding weapons. Loses the Shield Slam ability since shields are no longer used.

## Implementation

All rules are defined in `classes.py` using the `PROMOTION_ABILITY_RULES` dictionary.

### Rule Structure

```python
"TargetClassName": {
    "clear_spells": bool,           # Clear all spells? True/False
    "keep_spells": ["Spell1", ...], # Which spells to preserve (if clear_spells=True)
    "remove_spells": ["Spell1", ...], # Which spells to remove (if clear_spells=False)
    "remove_skills": ["Skill1", ...], # Which skills to remove
    "description": "Message..."      # What to tell the player
}
```

### Parameters

| Parameter | Type | Purpose |
|-----------|------|---------|
| `clear_spells` | bool | If `True`, wipes all spells and only keeps those in `keep_spells`. If `False`, retains all spells but can remove specific ones. |
| `keep_spells` | list | Spells to preserve/restore after promotion. If a spell isn't in the current spellbook, it will be created from the abilities module. |
| `remove_spells` | list | Specific spells to remove (only applies if `clear_spells=False`). |
| `remove_skills` | list | Skills to remove from the character's skill list. |
| `description` | str | Message displayed to the player describing what abilities were lost. |

## Current Promotion Rules

### Warlock (from Mage)
- **Action**: Keep only Enfeeble spell
- **Reason**: Enfeeble works with both Arcane and Shadow magic disciplines
- **Message**: "You lose all previously learned attack spells."

### Shadowcaster (from Warlock)
- **Action**: No changes to spells
- **Reason**: Shadowcaster inherits Warlock's spellbook

### Monk (from Healer)
- **Action**: Clear all spells
- **Reason**: Monks channel chi, not magic
- **Message**: "You lose all previously learned spells."

### Ranger (from Pathfinder)
- **Action**: Clear all spells
- **Reason**: Rangers use physical abilities, not magic
- **Message**: "You lose all previously learned spells."

### Weapon Master (from Warrior)
- **Action**: Remove Shield Slam skill
- **Reason**: Weapon Masters dual-wield without shields
- **Message**: "You lose the skill Shield Slam."

### Inquisitor (from Footpad)
- **Action**: Remove all stealth skills (Backstab, Smoke Screen, Pocket Sand, Kidney Punch, Steal, Sleeping Powder)
- **Reason**: Inquisitors investigate openly, not through stealth
- **Message**: "You lose all stealth skills."

## Adding New Promotion Rules

To add a promotion rule for a class that's missing one:

1. **Identify the transition**: What abilities should be lost? Why?
2. **Add to `PROMOTION_ABILITY_RULES`** in `classes.py`:

```python
"NewClassName": {
    "clear_spells": True,  # or False
    "keep_spells": ["SpellName"],  # if clear_spells=True
    "remove_spells": [],
    "remove_skills": ["SkillName"],
    "description": "You lose [description of loss]."
}
```

3. **Test promotion** in both:
   - Text-based version: `town.py` promotion system
   - Pygame version: `gui/church.py` ChurchManager

## Implementation Details

### Text Version (town.py)
The `promotion()` function in `classes.py` calls:
```python
ability_change_msg = apply_promotion_ability_rules(promoted_player, new_class.name)
promo_str += ability_change_msg
```

### Pygame Version (gui/church.py)
The `ChurchManager.handle_promotion()` method calls:
```python
ability_change_msg = apply_promotion_ability_rules(self.player_char, chosen_name)
if ability_change_msg:
    self.presenter.show_message(ability_change_msg.strip())
```

Both versions use the same underlying `apply_promotion_ability_rules()` function for consistency.

## Function Reference

### `apply_promotion_ability_rules(promoted_player, new_class_name)`

**Purpose**: Apply ability transition rules when a character is promoted.

**Parameters**:
- `promoted_player` (Character): The character being promoted
- `new_class_name` (str): Name of the new class being promoted to

**Returns**: 
- `str`: Message describing changes, empty string if none

**Behavior**:
1. Looks up rules in `PROMOTION_ABILITY_RULES`
2. If `clear_spells=True`: Removes all spells, then adds only those in `keep_spells`
3. If `clear_spells=False`: Keeps existing spells but removes those in `remove_spells` and/or `keep_spells` (overwrite)
4. Removes all skills listed in `remove_skills`
5. Returns the description message

**Note**: Spells are created on-demand from the abilities module if not currently in the spellbook.

## Future Enhancements

- [ ] Add rules for remaining promotion transitions (Bard, Troubadour, etc.)
- [ ] Add spell/skill *gain* rules in addition to loss
- [ ] Allow class-specific variants (e.g., "keep half your spells" logic)
- [ ] Track ability history for potential future mechanic (restore if reverting)
