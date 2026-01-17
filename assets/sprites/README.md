# Enemy Sprites

This directory contains automatically generated sprite images converted from ASCII art.

## Generation

Sprites are generated from the ASCII art files in `../ascii_files/` using the converter script:

```bash
python3 utils/ascii_to_sprite.py
```

## Sprite Sizes

Each enemy has three sprite sizes:
- **32x32 pixels** - Small icons for minimap or compact views
- **64x64 pixels** - Medium size for general use
- **128x128 pixels** - Large detailed sprites for combat or close-up views

## Naming Convention

Files are named: `{enemy_name}_{size}.png`

Examples:
- `goblin_32.png` - 32x32 goblin sprite
- `skeleton_64.png` - 64x64 skeleton sprite
- `reddragon_128.png` - 128x128 red dragon sprite

## Character Mapping

The ASCII art uses characters to represent different brightness levels:

| Character | Brightness | Usage |
|-----------|------------|-------|
| ` ` (space) | Transparent | Background |
| `.` | 30 | Very dark details |
| `:` | 60 | Dark details |
| `-` | 90 | Medium-dark |
| `=` | 120 | Medium |
| `+` | 150 | Medium-light |
| `*` | 180 | Light |
| `#` | 210 | Very light |
| `%` | 230 | Bright |
| `@` | 255 | Brightest highlights |

## Usage in Game

Sprites can be loaded in the Pygame GUI using:

```python
import pygame

# Load a sprite
sprite = pygame.image.load('sprites/goblin_64.png')

# Blit to screen
screen.blit(sprite, (x, y))
```

## Customization

To regenerate sprites with different settings, edit `utils/ascii_to_sprite.py`:

- `pixel_size`: Base pixel size for each character
- `color_scheme`: Color palette ('monochrome', 'green', 'red', 'blue', 'orange', 'purple')
- `sizes`: List of output sizes in pixels

Then run the script again to regenerate all sprites.
