# Sound Effects Directory

This directory contains sound effects for Dungeon Crawl.

## Supported Formats

- `.wav` - Uncompressed audio (best for short sound effects)
- `.ogg` - Compressed audio (good for longer sounds)

## Sound Effect Categories

### Combat Sounds
- `combat_start.wav` - Combat begins
- `hit.wav` - Normal attack hit
- `heavy_hit.wav` - Heavy damage hit (>50 damage)
- `critical_hit.wav` - Critical hit
- `miss.wav` - Attack missed
- `block.wav` - Attack blocked/parried
- `victory.wav` - Combat won
- `defeat.wav` - Combat lost
- `flee.wav` - Fled from combat

### Spell/Ability Sounds
- `spell_cast.wav` - Generic spell casting
- `spell_fire.wav` - Fire spell
- `spell_ice.wav` - Ice/frost spell  
- `spell_lightning.wav` - Lightning/shock spell
- `spell_heal.wav` - Healing spell
- `spell_buff.wav` - Buff spell
- `spell_debuff.wav` - Debuff spell

### Status Effect Sounds
- `poison.wav` - Poison/bleed applied
- `stun.wav` - Stun/freeze applied
- `burn.wav` - Burn applied

### Character Sounds
- `heal.wav` - Healing received
- `level_up.wav` - Character leveled up
- `player_death.wav` - Player died
- `enemy_death.wav` - Enemy died

### UI Sounds
- `menu_select.wav` - Menu option selected
- `menu_confirm.wav` - Menu confirmed
- `menu_cancel.wav` - Menu cancelled
- `item_pickup.wav` - Item picked up
- `item_equip.wav` - Item equipped
- `coin.wav` - Gold obtained
- `door_open.wav` - Door opened
- `chest_open.wav` - Chest opened

## Adding New Sounds

1. Place sound files in this directory
2. Use descriptive names (lowercase, underscores)
3. Keep files small (<100KB for SFX recommended)
4. Use 44100Hz sample rate for compatibility

## Creating Placeholder Sounds

For development, you can use the `tools/generate_placeholder_sounds.py` script to create simple beep sounds as placeholders.
