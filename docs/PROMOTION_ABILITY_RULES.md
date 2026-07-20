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

All rules are defined in `src/core/classes/rules.py` using the
`PROMOTION_ABILITY_RULES` dictionary.

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

## Promotion Decision Matrix

This matrix is the complete documentation baseline for current first- and
second-promotion ability transitions. `Keep` means no pruning rule is planned.
`Identity Trade` means an implemented rule removes abilities that no longer
match the promotion. The matrix itself is documentation rather than a runtime
pruning change unless an implemented rule is called out.

### Warrior Branch

| Promotion Path | Classification | Intended Ability Transition |
| --- | --- | --- |
| Warrior -> Weapon Master | Identity Trade | Remove shield-centered skills that conflict with dual-wield discipline. Current rule removes `Shield Slam`. |
| Weapon Master -> Berserker | Keep | Retain Weapon Master weapon discipline and weapon arts; Berserker adds Bloodied Momentum and heavy-weapon mutation. |
| Weapon Master -> Grandmaster of Arms | Keep | Retain and deepen Weapon Discipline; Grandmaster Class Ring expands the chosen bound art. |
| Warrior -> Paladin | Keep | Retain Warrior basics while adding permanent vow, holy identity, and Oath Conviction. |
| Paladin -> Crusader | Keep | Retain Paladin vow identity and deepen Oath Conviction through Vow Affirmation. |
| Warrior -> Lancer | Keep | Retain core martial skills while adding Jump, polearm identity, and Aerial Tempo. |
| Lancer -> Dragoon | Keep | Retain Jump/polearm progression and deepen Aerial Tempo through Aerial Supremacy follow-through. |
| Warrior -> Sentinel | Keep | Retain core martial skills while adding shield/guard identity. |
| Sentinel -> Stalwart Defender | Keep | Retain shield/guard identity and deepen Resolve with full-bar Resolve Surges. |

### Mage Branch

| Promotion Path | Classification | Intended Ability Transition |
| --- | --- | --- |
| Mage -> Sorcerer | Keep | Retain elemental Mage spells; Sorcerer starts the 0-50 School Affinity wheel and tier-2 upgrade path. |
| Sorcerer -> Wizard | Keep | Retain Sorcerer affinity progress and expand the cap to 100 for tier-3/final mastery. |
| Mage -> Warlock | Identity Trade | Trade elemental attack magic for shadow magic while preserving `Enfeeble`. Current rule keeps only `Enfeeble`. |
| Warlock -> Shadowcaster | Keep | Retain Warlock shadow spellbook and familiar identity. |
| Warlock -> Demonologist | Keep | Retain Warlock/familiar identity; Demonologist contracts, corruption, patron mood, and ring echo deepen that identity. |
| Mage -> Spellblade | Keep | Retain arcane training while adding weapon-channeling identity. |
| Spellblade -> Knight Enchanter | Keep | Retain Spellblade hybrid kit and deepen enchantment/mana-tap identity. |
| Mage -> Summoner | Keep | Retain Mage spell context and add summon identity; the V1 bond spec does not require spell pruning. |
| Summoner -> Grand Summoner | Keep | Retain summon kit and add sacrifice/conduit scaling. |

### Footpad Branch

| Promotion Path | Classification | Intended Ability Transition |
| --- | --- | --- |
| Footpad -> Thief | Keep | Retain stealth/toolkit skills and add loot economy identity, including Scavenger's Eye and Fortune/Misfortune. |
| Thief -> Rogue | Keep | Retain thief utility, Fortune/Misfortune, and loot identity while adding Finders Keepers, Cheat Death, and Loaded Dice payoff. |
| Footpad -> Inquisitor | Identity Trade | Remove stealth skills that conflict with open investigation, then add Case Journal and Revelation counterplay. Current rule removes the stealth suite. |
| Inquisitor -> Seeker | Keep | Retain reveal/inspection identity, Case Journal progress, and Revelation while adding Wayfinding and cartography/cache identity. |
| Footpad -> Assassin | Keep | Retain stealth skills and add poison/lethal pressure, including Death Mark setup. |
| Assassin -> Ninja | Keep | Retain assassin kit and Death Mark setup while adding Ninja Blade execution pressure and No-Trace Opener payoff. |
| Footpad -> Spell Stealer | Keep | Retain dexterous theft identity while adding spell theft and the combat-only Stolen Charge loop; stolen-spell scrolls are selected from the combat `Spells` picker rather than a Character Menu tab. |
| Spell Stealer -> Arcane Trickster | Keep | Retain spell theft, Stolen Charge, and permanent stolen-spell learning while adding Arcane Larceny payoff; no dedicated Character Menu mechanic tab is added for this path. |

### Healer Branch

| Promotion Path | Classification | Intended Ability Transition |
| --- | --- | --- |
| Healer -> Cleric | Keep | Retain healing foundation and add shield/holy utility. |
| Cleric -> Templar | Keep | Retain cleric defense/holy identity and add ordered blessings. |
| Cleric -> Hierophant | Keep | Retain cleric defense/holy identity and add staff-shield battle-casting through Devotion. |
| Healer -> Monk | Identity Trade | Trade spellcasting for martial chi. Current rule clears learned spells. |
| Monk -> Master Monk | Keep | Retain chi/martial kit and deepen Ki mastery, `Dim Mak`, and late-game martial weapon identity. |
| Healer -> Priest | Keep | Retain and deepen spellcasting support through the Prayer support loop. |
| Priest -> Archbishop | Keep | Retain priest spell identity and add Prayer-powered Benediction plus intervention smoothing. |
| Healer -> Bard | Identity Trade | Trade full divine spellcasting for light support and music. Bard keeps only known `Heal`, `Regen`, and `Cleanse`; divine offense and higher divine progression should be removed. |
| Bard -> Troubadour | Keep | Retain song identity and add Encore/music mastery. |

### Pathfinder Branch

| Promotion Path | Classification | Intended Ability Transition |
| --- | --- | --- |
| Pathfinder -> Druid | Keep | Retain nature magic and add transformation/nature rites. |
| Druid -> Lycan | Keep | Retain form/nature identity and add moon/frenzy behavior. |
| Druid -> Archdruid | Keep | Retain nature magic, deepen Fourfold Balance, and add combat Aspect Harmony. |
| Pathfinder -> Diviner | Keep | Retain exploration/nature context while adding learned-spell/rune identity; Diviner does not gain Foresight Threads in V1. |
| Diviner -> Astromancer | Keep | Retain runes and expand constellation/time identity through combat-only Foresight Threads and `Threaded Cast`. |
| Pathfinder -> Shaman | Keep | Retain nature spell context and add Totem communion. |
| Shaman -> Soulcatcher | Keep | Retain Totem identity and add Soul Aspect/Soul Drain. |
| Pathfinder -> Ranger | Identity Trade | Trade spellcasting for physical beastcraft. Current rule clears learned spells. |
| Ranger -> Beast Master | Keep | Retain taming/favored-enemy identity and add shared recovery. |

## Adding New Promotion Rules

To add a promotion rule for a class that's missing one:

1. **Identify the transition**: What abilities should be lost? Why?
2. **Add to `PROMOTION_ABILITY_RULES`** in `src/core/classes/rules.py`:

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
The text promotion flow calls:
```python
ability_change_msg = apply_promotion_ability_rules(promoted_player, new_class.name)
promo_str += ability_change_msg
```

### Pygame Version (gui/church.py)
The `ChurchManager.handle_promotion()` method calls:
```python
apply_promotion_ability_rules(self.player_char, chosen_name)
```

The pygame promotion preview now carries the class-change, stat-delta, and
class-mechanic education. After confirmation, pygame applies the promotion,
adds class stat/resource/combat bonuses, increases current HP/MP by the same
amount as max HP/MP bonuses, and shows one concise congratulations popup. It no
longer emits separate ability-change/tutorial popups for the normal success
path.

Both versions use the same underlying `apply_promotion_ability_rules()` function
for consistency.

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

## Expansion Gate

The current transition matrix is the compatibility baseline. Future promotion
ability changes must define spell and skill gain rules, class-specific
retention variants, ability-history restoration behavior, UI messages for text
and pygame flows, save compatibility, and focused tests before implementation.

Do not add broad ability-history restoration, alternate retention policies, or
new promotion spell/skill grants as roadmap cleanup. Promote them through this
doc first so `town.py`, `ChurchManager`, save/load, and regression tests stay
aligned.
