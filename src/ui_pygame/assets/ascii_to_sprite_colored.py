"""
ASCII Art to Colored Sprite Converter

Converts ASCII art files to colored PNG sprites with proper color palettes
instead of grayscale, preserving detail and allowing for complex coloring.

This system maps ASCII characters to brightness levels, then applies
color palettes based on enemy type to create detailed colored sprites.
"""

import os
from pathlib import Path

import pygame

# ASCII character to brightness mapping
# Space is transparent (None), others map 0-255
ASCII_BRIGHTNESS_MAP = {
    ' ': None,  # Transparent
    '.': 30,
    ':': 60,
    '-': 90,
    '=': 120,
    '+': 150,
    '*': 180,
    '#': 210,
    '%': 230,
    '@': 255,
}

# Enemy type to color palette mapping
# Each palette is (base_color, shadow_color, highlight_color, accent_color)
ENEMY_COLOR_PALETTES = {
    'goblin': {
        'base': (100, 150, 50),        # Greenish
        'shadow': (50, 80, 25),
        'highlight': (150, 200, 80),
        'accent': (200, 100, 50),      # Reddish skin
    },
    'orc': {
        'base': (120, 120, 120),       # Gray
        'shadow': (60, 60, 60),
        'highlight': (180, 180, 180),
        'accent': (150, 100, 80),      # Brown accents
    },
    'skeleton': {
        'base': (200, 200, 200),       # Pale
        'shadow': (100, 100, 100),
        'highlight': (240, 240, 240),
        'accent': (50, 50, 50),        # Dark gaps
    },
    'zombie': {
        'base': (100, 150, 100),       # Sickly green
        'shadow': (50, 80, 50),
        'highlight': (150, 200, 150),
        'accent': (150, 50, 50),       # Reddish wounds
    },
    'spider': {
        'base': (40, 40, 60),          # Dark purplish
        'shadow': (20, 20, 30),
        'highlight': (80, 80, 120),
        'accent': (100, 50, 100),      # Purple accents
    },
    'wolf': {
        'base': (139, 90, 60),         # Brown
        'shadow': (70, 45, 30),
        'highlight': (189, 140, 110),
        'accent': (200, 150, 100),     # Lighter fur
    },
    'dragon': {
        'base': (200, 50, 50),         # Red
        'shadow': (100, 25, 25),
        'highlight': (255, 100, 100),
        'accent': (255, 200, 0),       # Gold accents
    },
    'undead': {
        'base': (120, 120, 150),       # Blue-gray
        'shadow': (60, 60, 80),
        'highlight': (180, 180, 220),
        'accent': (255, 200, 100),     # Glowing eyes
    },
    'demon': {
        'base': (150, 50, 150),        # Purple
        'shadow': (80, 25, 80),
        'highlight': (200, 100, 200),
        'accent': (255, 100, 0),       # Orange fire accents
    },
    'slime': {
        'base': (100, 200, 100),       # Bright green
        'shadow': (50, 100, 50),
        'highlight': (150, 255, 150),
        'accent': (200, 255, 200),     # Translucent highlights
    },
    'humanoid': {
        'base': (160, 130, 110),       # Skin tone
        'shadow': (100, 80, 60),
        'highlight': (210, 170, 140),
        'accent': (200, 100, 100),     # Armor/clothing
    },
}

# Default palette for unknown types
DEFAULT_PALETTE = {
    'base': (150, 150, 150),
    'shadow': (75, 75, 75),
    'highlight': (200, 200, 200),
    'accent': (100, 100, 150),
}


def get_palette_for_enemy(enemy_name):
    """
    Determine the color palette for an enemy based on its name.
    
    Args:
        enemy_name: Name of the enemy (e.g., 'goblin', 'skeleton')
    
    Returns:
        Color palette dict with 'base', 'shadow', 'highlight', 'accent'
    """
    enemy_name_lower = enemy_name.lower()
    
    # Direct matches
    if enemy_name_lower in ENEMY_COLOR_PALETTES:
        return ENEMY_COLOR_PALETTES[enemy_name_lower]
    
    # Substring matches
    for enemy_type, palette in ENEMY_COLOR_PALETTES.items():
        if enemy_type in enemy_name_lower:
            return palette
    
    # Special cases
    if any(word in enemy_name_lower for word in ['bat', 'bird', 'eagle', 'owl']):
        return ENEMY_COLOR_PALETTES['wolf']
    elif any(word in enemy_name_lower for word in ['imp', 'demon', 'devil', 'fiend']):
        return ENEMY_COLOR_PALETTES['demon']
    elif any(word in enemy_name_lower for word in ['slime', 'ooze', 'blob']):
        return ENEMY_COLOR_PALETTES['slime']
    elif any(word in enemy_name_lower for word in ['dragon', 'wyrm', 'drake']):
        return ENEMY_COLOR_PALETTES['dragon']
    elif any(word in enemy_name_lower for word in ['rat', 'rodent', 'were']):
        return ENEMY_COLOR_PALETTES['wolf']
    elif any(word in enemy_name_lower for word in ['spider', 'insect', 'centipede', 'scorpion']):
        return ENEMY_COLOR_PALETTES['spider']
    
    return DEFAULT_PALETTE


def brightness_to_color(brightness, palette):
    """
    Map a brightness value (0-255) to a color using the palette.
    
    Uses the brightness to interpolate between shadow, base, highlight, and accent colors.
    """
    if brightness is None:
        return None  # Transparent
    
    # Normalize brightness to 0-1
    norm = brightness / 255.0
    
    if norm < 0.25:
        # Very dark: shadow to base
        t = norm / 0.25
        shadow = palette['shadow']
        base = palette['base']
        return tuple(int(shadow[i] * (1 - t) + base[i] * t) for i in range(3))
    elif norm < 0.5:
        # Dark: base
        t = (norm - 0.25) / 0.25
        base = palette['base']
        highlight = palette['highlight']
        return tuple(int(base[i] * (1 - t) + highlight[i] * t) for i in range(3))
    elif norm < 0.75:
        # Light: highlight
        t = (norm - 0.5) / 0.25
        highlight = palette['highlight']
        accent = palette['accent']
        return tuple(int(highlight[i] * (1 - t) + accent[i] * t) for i in range(3))
    else:
        # Very bright: accent
        return palette['accent']


def ascii_to_sprite(ascii_content, enemy_name, output_size=128):
    """
    Convert ASCII art string to a colored pygame Surface.
    
    Args:
        ascii_content: String containing ASCII art (lines separated by newlines)
        enemy_name: Name of enemy for palette selection
        output_size: Size of output sprite (square)
    
    Returns:
        pygame.Surface with the colored sprite
    """
    pygame.init()
    
    # Get color palette for this enemy
    palette = get_palette_for_enemy(enemy_name)
    
    # Parse ASCII art
    lines = ascii_content.strip().split('\n')
    
    # Find dimensions
    max_width = max((len(line) for line in lines), default=1)
    height = len(lines)
    
    # Create surface
    surface = pygame.Surface((output_size, output_size), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))  # Transparent background
    
    # Calculate scaling
    char_width = output_size / max_width if max_width > 0 else output_size
    char_height = output_size / height if height > 0 else output_size
    
    # For colored sprites, use slightly larger character size to avoid gaps
    char_width = max(char_width, 1)
    char_height = max(char_height, 1)
    
    # Draw each character
    for y, line in enumerate(lines):
        for x, char in enumerate(line):
            brightness = ASCII_BRIGHTNESS_MAP.get(char)
            
            if brightness is None:
                continue  # Transparent
            
            color = brightness_to_color(brightness, palette)
            if color is None:
                continue
            
            # Add alpha channel (full opacity)
            color_with_alpha = (*color, 255)
            
            # Draw pixel/block for this character
            rect = pygame.Rect(
                int(x * char_width),
                int(y * char_height),
                int(char_width) + 1,  # +1 to avoid gaps
                int(char_height) + 1
            )
            pygame.draw.rect(surface, color_with_alpha, rect)
    
    return surface


def convert_ascii_files_to_sprites(ascii_dir, output_dir, size=128):
    """
    Batch convert all ASCII files in a directory to colored sprites.
    
    Args:
        ascii_dir: Directory containing ASCII art files
        output_dir: Directory to save PNG sprites
        size: Output sprite size (default 128x128)
    """
    pygame.init()
    
    os.makedirs(output_dir, exist_ok=True)
    
    ascii_path = Path(ascii_dir)
    converted = 0
    failed = 0
    
    for ascii_file in sorted(ascii_path.glob('*.txt')):
        try:
            enemy_name = ascii_file.stem  # Filename without .txt
            
            # Read ASCII content
            with open(ascii_file, 'r', encoding='utf-8') as f:
                ascii_content = f.read()
            
            # Convert to sprite
            sprite_surface = ascii_to_sprite(ascii_content, enemy_name, size)
            
            # Save PNG
            output_file = Path(output_dir) / f"{enemy_name}.png"
            pygame.image.save(sprite_surface, str(output_file))
            
            print(f"✓ Converted {enemy_name}")
            converted += 1
            
        except Exception as e:
            print(f"✗ Failed to convert {ascii_file.name}: {e}")
            failed += 1
    
    print(f"\n✓ Successfully converted {converted} sprites")
    if failed > 0:
        print(f"✗ Failed to convert {failed} sprites")
    
    return converted, failed


if __name__ == "__main__":
    # Convert all ASCII files
    ascii_directory = "ascii_files"
    sprite_output = "src/ui_pygame/assets/sprites/enemies"
    
    if os.path.exists(ascii_directory):
        converted, failed = convert_ascii_files_to_sprites(ascii_directory, sprite_output)
    else:
        print(f"ASCII directory not found: {ascii_directory}")
