# Retired Generated Enemy Sprites

The old generated enemy sprite PNGs have been retired from runtime use and moved to `old_assets/retired_enemy_sprites/`.

Current enemy presentation uses transparent full-body combat sprites in `src/ui_pygame/assets/enemy_combat_sprites/`, loaded through `EnemyCombatSpriteManager`.

Do not add new runtime enemy assets under `src/ui_pygame/assets/sprites/enemies/`. Missing enemy visuals should be fixed by adding or mapping a combat sprite, or by tuning `enemy_combat_sprite_map.json`, `enemy_combat_sprite_scale.json`, and token crop data.

## Generation

The legacy converter can still be used for historical/reference output, but it does not feed combat rendering:

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

Generated enemy sprites are no longer loaded during combat rendering. `CombatView`, dungeon boss navigation, target panels, and enemy tokens all use `EnemyCombatSpriteManager` and `enemy_combat_sprites/`.

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
