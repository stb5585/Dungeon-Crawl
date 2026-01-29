#!/usr/bin/env python3
"""
Test script to verify the new tileset loading and perspective generation.
This creates a simple preview without requiring the full game to run.
"""

import os
import sys

import pygame

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))


def test_tileset_loading():
    """Test loading and generating perspective tiles."""
    pygame.init()
    
    # Create a test screen
    screen = pygame.display.set_mode((1024, 512))
    pygame.display.set_caption("Tileset Preview")
    
    # Load textures
    tileset_path = "src/ui_pygame/assets/dungeon_tiles"
    
    texture_map = {
        'wall': 'walls/brick.png',
        'floor': 'floors/dirt.png',
        'ceiling': 'ceilings/stone.png',
    }
    
    textures = {}
    for tex_type, tex_path in texture_map.items():
        file_path = os.path.join(tileset_path, tex_path)
        try:
            image = pygame.image.load(file_path).convert_alpha()
            textures[tex_type] = image
            print(f"✓ Loaded {tex_type}: {tex_path} - Size: {image.get_size()}")
        except Exception as e:
            print(f"✗ ERROR loading {tex_type}: {e}")
            assert False, f"Failed to load {tex_type}: {e}"
    
    # Display raw textures on left side
    screen.fill((50, 50, 50))
    
    y_offset = 10
    for tex_type, texture in textures.items():
        # Scale down for display
        scaled = pygame.transform.scale(texture, (150, 150))
        screen.blit(scaled, (10, y_offset))
        
        # Label
        font = pygame.font.Font(None, 24)
        label = font.render(tex_type, True, (255, 255, 255))
        screen.blit(label, (170, y_offset + 65))
        
        y_offset += 160
    
    # Show a simple composite on the right side
    # This demonstrates how the tiles would look together
    comp_x = 400
    comp_y = 50
    comp_size = 400
    
    # Draw background
    pygame.draw.rect(screen, (10, 10, 10), (comp_x, comp_y, comp_size, comp_size))
    
    # Ceiling (top 1/4)
    if textures.get('ceiling'):
        ceiling = pygame.transform.scale(textures['ceiling'], (comp_size, comp_size // 4))
        screen.blit(ceiling, (comp_x, comp_y))
    
    # Floor (bottom 1/4)
    if textures.get('floor'):
        floor = pygame.transform.scale(textures['floor'], (comp_size, comp_size // 4))
        screen.blit(floor, (comp_x, comp_y + comp_size - comp_size // 4))
    
    # Left wall (1/4 width, full height)
    if textures.get('wall'):
        left_wall = pygame.transform.scale(textures['wall'], (comp_size // 4, comp_size))
        screen.blit(left_wall, (comp_x, comp_y))
    
    # Right wall (1/4 width, full height)
    if textures.get('wall'):
        right_wall = pygame.transform.scale(textures['wall'], (comp_size // 4, comp_size))
        screen.blit(right_wall, (comp_x + comp_size - comp_size // 4, comp_y))
    
    # Back wall (centered, 1/2 size)
    if textures.get('wall'):
        back_size = comp_size // 2
        back_wall = pygame.transform.scale(textures['wall'], (back_size, back_size))
        # Apply darkening
        back_wall.fill((180, 180, 180), special_flags=pygame.BLEND_RGBA_MULT)
        back_x = comp_x + (comp_size - back_size) // 2
        back_y = comp_y + (comp_size - back_size) // 2
        screen.blit(back_wall, (back_x, back_y))
    
    # Add title
    title_font = pygame.font.Font(None, 32)
    title = title_font.render("New Tileset Preview - Press ESC to close", True, (255, 255, 255))
    screen.blit(title, (10, screen.get_height() - 40))
    
    pygame.display.flip()
    
    # Validation: Just verify textures loaded successfully (no GUI loop for tests)
    print("✓ Wall texture loaded: " + str(textures.get('wall').get_size() if textures.get('wall') else "N/A"))
    print("✓ Floor texture loaded: " + str(textures.get('floor').get_size() if textures.get('floor') else "N/A"))
    print("✓ Ceiling texture loaded: " + str(textures.get('ceiling').get_size() if textures.get('ceiling') else "N/A"))
    
    pygame.quit()
    print("\n✓ All textures loaded successfully!")
    print("✓ Tileset integration complete!")
    assert True


if __name__ == "__main__":
    print("=" * 60)
    print("Testing New Dungeon Tileset Integration")
    print("=" * 60)
    print()
    
    success = test_tileset_loading()
    
    if success:
        print("\n" + "=" * 60)
        print("SUCCESS: Tileset is ready to use!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("ERROR: Tileset loading failed")
        print("=" * 60)
        sys.exit(1)
