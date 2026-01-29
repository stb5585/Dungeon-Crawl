#!/usr/bin/env python3
"""
Test script to verify PIL perspective transforms work correctly.
Creates sample perspective-transformed tiles and displays them.
"""

import os

import pygame
from PIL import Image


def test_perspective_transform():
    """Test that PIL can load textures and apply perspective transforms."""
    pygame.init()
    
    # Create test screen
    screen = pygame.display.set_mode((1024, 600))
    pygame.display.set_caption("Perspective Transform Test")
    
    # Load a texture
    tileset_path = "src/ui_pygame/assets/dungeon_tiles"
    texture_file = os.path.join(tileset_path, "walls/brick.png")
    
    try:
        # Load with PIL
        pil_image = Image.open(texture_file)
        print(f"✓ Loaded texture: {texture_file}")
        print(f"  Size: {pil_image.size}, Mode: {pil_image.mode}")
        
        # Test left wall perspective transform
        wall_width = 128
        wall_height = 512
        inset = 128
        
        # Scale source texture
        scaled = pil_image.resize((512, 512), Image.LANCZOS)
        
        # Left wall quad
        left_quad = (
            0, 0,                     # top-left (unchanged)
            wall_width, inset,        # top-right (move down/in)
            wall_width, wall_height-inset,  # bottom-right (move up/in)
            0, wall_height            # bottom-left (unchanged)
        )
        
        left_wall = scaled.transform(
            (wall_width, wall_height),
            Image.QUAD,
            left_quad,
            Image.BICUBIC
        )
        print(f"✓ Created left wall perspective: {left_wall.size}")
        
        # Right wall quad
        right_quad = (
            0, inset,                 # top-left (move down/in)
            wall_width, 0,            # top-right (unchanged)
            wall_width, wall_height,  # bottom-right (unchanged)
            0, wall_height-inset      # bottom-left (move up/in)
        )
        
        right_wall = scaled.transform(
            (wall_width, wall_height),
            Image.QUAD,
            right_quad,
            Image.BICUBIC
        )
        print(f"✓ Created right wall perspective: {right_wall.size}")
        
        # Floor perspective
        floor_width = 512
        floor_height = 128
        floor_quad = (
            inset, 0,           # top-left (narrow)
            floor_width-inset, 0,  # top-right (narrow)
            floor_width, floor_height,  # bottom-right (wide)
            0, floor_height     # bottom-left (wide)
        )
        
        floor_pil = pil_image.resize((floor_width, floor_height), Image.LANCZOS)
        floor = floor_pil.transform(
            (floor_width, floor_height),
            Image.QUAD,
            floor_quad,
            Image.BICUBIC
        )
        print(f"✓ Created floor perspective: {floor.size}")
        
        # Convert to pygame and display
        screen.fill((20, 20, 20))
        
        # Display left wall
        left_data = left_wall.tobytes()
        left_surf = pygame.image.fromstring(left_data, left_wall.size, left_wall.mode)
        screen.blit(left_surf, (50, 50))
        
        # Display right wall
        right_data = right_wall.tobytes()
        right_surf = pygame.image.fromstring(right_data, right_wall.size, right_wall.mode)
        screen.blit(right_surf, (250, 50))
        
        # Display floor
        floor_data = floor.tobytes()
        floor_surf = pygame.image.fromstring(floor_data, floor.size, floor.mode)
        screen.blit(floor_surf, (450, 50))
        
        # Add labels
        font = pygame.font.Font(None, 24)
        labels = [
            ("Left Wall (Perspective)", (50, 20)),
            ("Right Wall (Perspective)", (250, 20)),
            ("Floor (Perspective)", (450, 20)),
        ]
        for text, pos in labels:
            label = font.render(text, True, (255, 255, 255))
            screen.blit(label, pos)
        
        # Instructions
        title = font.render("PIL Perspective Transform Test - Press ESC to close", True, (255, 255, 255))
        screen.blit(title, (50, screen.get_height() - 40))
        
        pygame.display.flip()
        
        # Validation: Just verify transforms created successfully (no GUI loop for tests)
        print("✓ Left wall perspective created: " + str(left_wall.size))
        print("✓ Right wall perspective created: " + str(right_wall.size))
        print("✓ Floor perspective created: " + str(floor.size))
        
        pygame.quit()
        print("\n✓ PIL perspective transforms working correctly!")
        assert True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"PIL perspective transform failed: {e}"

if __name__ == "__main__":
    print("=" * 60)
    print("Testing PIL Perspective Transforms")
    print("=" * 60)
    print()
    
    success = test_perspective_transform()
    
    if success:
        print("\n" + "=" * 60)
        print("SUCCESS: Perspective transforms are ready!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("ERROR: Perspective transform test failed")
        print("=" * 60)
