# Sound System Documentation

## Overview

The Dungeon Crawl sound system provides immersive audio feedback through sound effects and background music. It integrates seamlessly with the game's event-driven architecture.

## Architecture

### Sound Manager

The `SoundManager` class (`src/ui_pygame/assets/sound_manager.py`) handles:
- Sound effect loading and caching
- Background music playback
- Volume control (master, SFX, and music separately)
- Event-driven sound playback

### Event Integration

The sound manager subscribes to combat and game events:
- `COMBAT_START` - Combat begins sound
- `COMBAT_END` - Victory/defeat/flee sounds
- `DAMAGE_DEALT` - Hit sounds (normal/heavy/critical)
- `HEALING_DONE` - Healing sound
- `SPELL_CAST` - Spell casting sounds (fire/ice/lightning/etc.)
- `SKILL_USE` - Skill usage sounds
- `STATUS_APPLIED` - Status effect sounds (poison/stun/burn)
- `CHARACTER_DEATH` - Death sounds (player/enemy)
- `LEVEL_UP` - Level up fanfare

### Menu Sounds

UI navigation triggers sounds automatically:
- Arrow keys - `menu_select.wav`
- Enter/Space - `menu_confirm.wav`
- Escape - `menu_cancel.wav`

## File Structure

```
src/ui_pygame/assets/
├── sounds/          # Sound effects (.wav or .ogg)
│   ├── combat_start.wav
│   ├── hit.wav
│   ├── critical_hit.wav
│   ├── spell_fire.wav
│   ├── menu_select.wav
│   └── ... (see sounds/README.md)
└── music/           # Background music (.ogg or .mp3)
    ├── town.ogg
    ├── dungeon_floor1.ogg
    ├── combat_boss.ogg
    └── ... (see music/README.md)
```

## Usage

### Basic Usage

The sound manager is automatically initialized when the PygamePresenter starts:

```python
from src.ui_pygame.assets.sound_manager import get_sound_manager

# Get the singleton instance
sound_manager = get_sound_manager()

# Play a sound effect
sound_manager.play_sfx("hit")

# Play background music (loops by default)
sound_manager.play_music("dungeon_floor1")

# Stop music
sound_manager.stop_music()
```

### Volume Control

```python
# Set master volume (0.0 to 1.0)
sound_manager.set_master_volume(0.8)

# Set SFX volume
sound_manager.set_sfx_volume(0.7)

# Set music volume
sound_manager.set_music_volume(0.5)

# Disable all sound
sound_manager.disable()

# Re-enable sound
sound_manager.enable()
```

### Playing Custom Sounds

```python
# Play with custom volume
sound_manager.play_sfx("explosion", volume=1.0)

# Loop a sound effect
sound_manager.play_sfx("ambient_wind", loops=-1)  # -1 = infinite

# Play music with fade-in
sound_manager.play_music("boss_battle", fade_ms=2000)
```

## Adding New Sounds

1. **Create or find sound files** (WAV or OGG format recommended)
2. **Place files in appropriate directory**:
   - Sound effects → `src/ui_pygame/assets/sounds/`
   - Music → `src/ui_pygame/assets/music/`
3. **Use descriptive names** (lowercase, underscores)
4. **Play the sound** using the sound manager

### Example: Adding a New Spell Sound

1. Add `spell_explosion.wav` to `assets/sounds/`
2. Update the `_on_spell_cast` or `_on_skill_use` event handler in `sound_manager.py`:

```python
elif 'explosion' in spell_name.lower():
    self.play_sfx("spell_explosion")
```

## Development Without Sound Files

The sound system gracefully handles missing audio files:
- Missing sounds are logged but don't cause errors
- Game continues to function normally
- Use `tools/generate_placeholder_sounds.py` to create simple beeps for testing

## Generating Placeholder Sounds

For development without proper sound assets:

```bash
# Generate all placeholder sound effects
python3 tools/generate_placeholder_sounds.py

# Specify custom output directory
python3 tools/generate_placeholder_sounds.py --output path/to/sounds
```

**Note**: Placeholder sounds are simple sine wave tones. Replace with professional sound effects for production.

## Configuration

### Pygame Mixer Settings

Default settings (configured in `SoundManager.__init__`):
- **Frequency**: 44100 Hz
- **Size**: 16-bit
- **Channels**: 2 (stereo)
- **Buffer**: 512 samples
- **Simultaneous sounds**: 16 channels

### Default Volumes

- **Master**: 1.0 (100%)
- **SFX**: 0.7 (70%)
- **Music**: 0.5 (50%)

## Performance Notes

- **Sound caching**: SFX are loaded once and reused
- **Music streaming**: Music files are streamed, not cached
- **Channel limit**: Up to 16 sounds can play simultaneously
- **Small file sizes**: Keep SFX under 100KB when possible

## Troubleshooting

### No Sound Playing

1. Check if pygame.mixer initialized:
   ```python
   import pygame
   print(pygame.mixer.get_init())  # Should return settings tuple
   ```

2. Check sound files exist:
   ```bash
   ls -la src/ui_pygame/assets/sounds/
   ```

3. Check volume levels:
   ```python
   print(sound_manager.enabled)
   print(sound_manager.master_volume)
   ```

### Sound Cutting Out

- Increase buffer size in `SoundManager.__init__`
- Reduce number of simultaneous channels
- Use compressed audio formats (OGG) instead of WAV

### Music Not Looping

- Ensure music file has seamless loop points
- Use OGG format which supports better looping
- Check `loops` parameter is set to -1

## Future Enhancements

- [ ] Spatial audio (positional sound based on enemy position)
- [ ] Dynamic music transitions (combat intensity)
- [ ] Sound effect randomization (multiple variants)
- [ ] Audio ducking (auto-lower music during combat)
- [ ] Sound profiles (presets for different preferences)
- [ ] Per-entity sound customization
