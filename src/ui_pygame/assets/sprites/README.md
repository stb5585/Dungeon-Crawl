# Enemy Sprites

Enemy sprites live in the `enemies/` subdirectory and are generated from ASCII art with full color support.

## Generation

Sprites are generated from the ASCII art files in `../../ascii_files/` using the colored converter script:

```bash
python3 src/ui_pygame/assets/ascii_to_sprite_colored.py
```

## Sprite Sizes

All enemy sprite files are sized 128x128 pixels.

## Colored Sprite System (Improved)

The new sprite generation system creates **fully colored sprites** instead of grayscale ones. This solves the previous limitation where blanket colorization would destroy sprite detail and outlines.

### How It Works

ASCII characters are mapped to brightness levels, which are then converted to actual colors using enemy-type-specific color palettes:

| Character | Brightness | Typical Usage |
|-----------|------------|-------|
| ` ` (space) | Transparent | Background |
| `.` | 30 | Very dark shadows |
| `:` | 60 | Dark details |
| `-` | 90 | Medium-dark shading |
| `=` | 120 | Base medium tones |
| `+` | 150 | Medium-light tones |
| `*` | 180 | Light highlights |
| `#` | 210 | Bright highlights |
| `%` | 230 | Very bright details |
| `@` | 255 | Brightest accents |

### Color Palettes

Each enemy type has a unique color palette with 4 color layers:

1. **Shadow Color** - Used for darkest ASCII characters (., :)
2. **Base Color** - Primary color for the enemy (=, +)
3. **Highlight Color** - Used for lighter tones (*, #)
4. **Accent Color** - Used for very bright details (@, %), often representing equipment/eyes

Palettes are defined in `ascii_to_sprite_colored.py` for types:
- `goblin`: Greenish with brown accents
- `orc`: Gray with brown accents
- `skeleton`: Pale white with dark gaps
- `zombie`: Sickly green with red wounds
- `spider`: Dark purple with purple accents
- `wolf`: Brown with lighter fur
- `dragon`: Red with gold accents
- `demon`: Purple with orange fire
- `slime`: Bright green with translucent highlights
- And more...

### Benefits Over Old System

**Before:** Sprites were grayscale, then a single blanket color was applied via multiplicative blending. This made dark colors (like black) appear as a void, losing all detail.

**Now:** Sprites are generated with full color information baked in:
- ✓ Complex outlines and details remain visible
- ✓ Clothing, armor, and equipment details show through
- ✓ Natural color variety for realism
- ✓ Eyes and highlights properly distinct
- ✓ No more "void" appearance for dark enemies

## Usage in Game

Sprites are automatically loaded during combat rendering in `src/ui_pygame/gui/combat_view.py`. The `_get_enemy_sprite()` method loads the PNG based on the enemy's `picture` attribute.

```python
# Sprites are loaded automatically
# No manual colorization needed - sprites are pre-colored
sprite = self._get_enemy_sprite(enemy)  # Already colored!
self.screen.blit(sprite, position)
```

## Customization

To modify sprite colors or add new palettes, edit `ascii_to_sprite_colored.py`:

1. **Add new color palette** in `ENEMY_COLOR_PALETTES`:
```python
'custom_type': {
    'base': (R, G, B),
    'shadow': (R, G, B),
    'highlight': (R, G, B),
    'accent': (R, G, B),
}
```

2. **Update color-to-enemy mapping** in `get_palette_for_enemy()` to apply your palette

3. **Regenerate sprites**:
```bash
cd /home/tom/Projects/Dungeon-Crawl
.venv/bin/python src/ui_pygame/assets/ascii_to_sprite_colored.py
```

## Technical Details

- Input: ASCII art files from `ascii_files/` directory
- Process: ASCII → Brightness levels → Color palette interpolation → PNG
- Output: 128x128 RGBA PNG with transparency
- Brightness interpolation: Pixels between brightness values smoothly interpolate between colors
