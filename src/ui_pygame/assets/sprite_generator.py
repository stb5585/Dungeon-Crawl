"""
Sprite Generator - Creates placeholder sprites for Dungeon Crawl.

This module generates simple, recognizable sprites programmatically using Pygame.
These can be replaced with actual artwork later.
"""
import pygame
import os

# Color palette
COLORS = {
    'player_blue': (50, 100, 200),
    'player_light_blue': (100, 150, 255),
    'goblin_green': (100, 150, 50),
    'orc_gray': (120, 120, 120),
    'dragon_red': (200, 50, 50),
    'skeleton_white': (230, 230, 230),
    'spider_black': (40, 40, 60),
    'slime_green': (100, 200, 100),
    'demon_purple': (150, 50, 150),
    'undead_gray': (100, 100, 130),
    'beast_brown': (139, 90, 60),
    'gold': (255, 215, 0),
    'silver': (192, 192, 192),
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'transparent': (255, 0, 255),  # Magenta for transparency
}


class SpriteGenerator:
    """Generate placeholder sprites for characters and enemies."""
    
    def __init__(self, output_dir: str = "sprites"):
        """Initialize sprite generator."""
        pygame.init()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def create_humanoid_sprite(self, name: str, body_color: tuple[int, int, int], 
                               size: tuple[int, int] = (64, 64),
                               has_weapon: bool = False,
                               has_shield: bool = False) -> str:
        """Create a humanoid sprite (player, warrior, etc.)."""
        surface = pygame.Surface(size)
        surface.fill(COLORS['transparent'])
        surface.set_colorkey(COLORS['transparent'])
        
        center_x = size[0] // 2
        center_y = size[1] // 2
        
        # Head
        pygame.draw.circle(surface, body_color, (center_x, center_y - 10), 8)
        pygame.draw.circle(surface, COLORS['black'], (center_x, center_y - 10), 8, 2)
        
        # Eyes
        pygame.draw.circle(surface, COLORS['black'], (center_x - 3, center_y - 12), 2)
        pygame.draw.circle(surface, COLORS['black'], (center_x + 3, center_y - 12), 2)
        
        # Body
        pygame.draw.rect(surface, body_color, (center_x - 8, center_y, 16, 20))
        pygame.draw.rect(surface, COLORS['black'], (center_x - 8, center_y, 16, 20), 2)
        
        # Arms
        pygame.draw.rect(surface, body_color, (center_x - 14, center_y + 2, 6, 15))
        pygame.draw.rect(surface, body_color, (center_x + 8, center_y + 2, 6, 15))
        
        # Legs
        pygame.draw.rect(surface, body_color, (center_x - 6, center_y + 20, 5, 12))
        pygame.draw.rect(surface, body_color, (center_x + 1, center_y + 20, 5, 12))
        
        # Weapon (sword on right side)
        if has_weapon:
            weapon_color = COLORS['silver']
            # Sword blade
            pygame.draw.line(surface, weapon_color, 
                           (center_x + 12, center_y + 5), 
                           (center_x + 16, center_y - 5), 3)
            # Sword hilt
            pygame.draw.line(surface, COLORS['gold'], 
                           (center_x + 10, center_y + 7), 
                           (center_x + 14, center_y + 7), 4)
        
        # Shield (on left side)
        if has_shield:
            shield_points = [
                (center_x - 16, center_y + 5),
                (center_x - 12, center_y + 3),
                (center_x - 12, center_y + 12),
                (center_x - 16, center_y + 10),
            ]
            pygame.draw.polygon(surface, COLORS['silver'], shield_points)
            pygame.draw.polygon(surface, COLORS['black'], shield_points, 2)
        
        filepath = os.path.join(self.output_dir, f"{name}.png")
        pygame.image.save(surface, filepath)
        return filepath
        
    def create_monster_sprite(self, name: str, sprite_type: str, 
                             color: tuple[int, int, int],
                             size: tuple[int, int] = (64, 64)) -> str:
        """Create a monster sprite with various types."""
        surface = pygame.Surface(size)
        surface.fill(COLORS['transparent'])
        surface.set_colorkey(COLORS['transparent'])
        
        center_x = size[0] // 2
        center_y = size[1] // 2
        
        if sprite_type == 'blob':  # Slimes, oozes
            # Blob body
            pygame.draw.ellipse(surface, color, (center_x - 20, center_y - 5, 40, 30))
            pygame.draw.ellipse(surface, COLORS['black'], (center_x - 20, center_y - 5, 40, 30), 2)
            # Eyes
            pygame.draw.circle(surface, COLORS['black'], (center_x - 8, center_y + 5), 3)
            pygame.draw.circle(surface, COLORS['black'], (center_x + 8, center_y + 5), 3)
            pygame.draw.circle(surface, COLORS['white'], (center_x - 7, center_y + 4), 1)
            pygame.draw.circle(surface, COLORS['white'], (center_x + 9, center_y + 4), 1)
            
        elif sprite_type == 'quadruped':  # Beasts, wolves
            # Body
            pygame.draw.ellipse(surface, color, (center_x - 15, center_y - 5, 30, 20))
            pygame.draw.ellipse(surface, COLORS['black'], (center_x - 15, center_y - 5, 30, 20), 2)
            # Head
            pygame.draw.circle(surface, color, (center_x + 12, center_y - 8), 10)
            pygame.draw.circle(surface, COLORS['black'], (center_x + 12, center_y - 8), 10, 2)
            # Eyes
            pygame.draw.circle(surface, COLORS['black'], (center_x + 15, center_y - 10), 2)
            # Legs
            for x_off in [-12, -6, 6, 12]:
                pygame.draw.rect(surface, color, (center_x + x_off - 2, center_y + 15, 4, 12))
            # Tail
            pygame.draw.line(surface, color, (center_x - 15, center_y), 
                           (center_x - 22, center_y - 8), 3)
            
        elif sprite_type == 'spider':  # Spiders, insects
            # Body
            pygame.draw.ellipse(surface, color, (center_x - 12, center_y - 8, 24, 16))
            pygame.draw.ellipse(surface, COLORS['black'], (center_x - 12, center_y - 8, 24, 16), 2)
            # Head
            pygame.draw.circle(surface, color, (center_x, center_y - 12), 8)
            pygame.draw.circle(surface, COLORS['black'], (center_x, center_y - 12), 8, 2)
            # Eyes
            for x_off in [-3, 3]:
                pygame.draw.circle(surface, COLORS['black'], (center_x + x_off, center_y - 13), 2)
            # Legs (8 legs)
            for i, angle in enumerate(range(-60, 240, 40)):
                import math
                rad = math.radians(angle)
                x1 = center_x + int(12 * math.cos(rad))
                y1 = center_y + int(8 * math.sin(rad))
                x2 = center_x + int(20 * math.cos(rad))
                y2 = center_y + int(15 * math.sin(rad))
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 2)
                
        elif sprite_type == 'dragon':  # Dragons, large beasts
            # Body
            pygame.draw.ellipse(surface, color, (center_x - 18, center_y - 10, 36, 25))
            pygame.draw.ellipse(surface, COLORS['black'], (center_x - 18, center_y - 10, 36, 25), 2)
            # Head
            pygame.draw.circle(surface, color, (center_x + 15, center_y - 15), 12)
            pygame.draw.circle(surface, COLORS['black'], (center_x + 15, center_y - 15), 12, 2)
            # Eye
            pygame.draw.circle(surface, COLORS['black'], (center_x + 18, center_y - 17), 3)
            pygame.draw.circle(surface, COLORS['gold'], (center_x + 19, center_y - 18), 1)
            # Horns
            pygame.draw.polygon(surface, color, [
                (center_x + 10, center_y - 22),
                (center_x + 8, center_y - 28),
                (center_x + 12, center_y - 24)
            ])
            pygame.draw.polygon(surface, color, [
                (center_x + 18, center_y - 22),
                (center_x + 20, center_y - 28),
                (center_x + 16, center_y - 24)
            ])
            # Wings
            wing_points_left = [
                (center_x - 18, center_y - 5),
                (center_x - 28, center_y - 15),
                (center_x - 20, center_y + 5)
            ]
            wing_points_right = [
                (center_x + 18, center_y - 5),
                (center_x + 28, center_y - 15),
                (center_x + 20, center_y + 5)
            ]
            pygame.draw.polygon(surface, color, wing_points_left)
            pygame.draw.polygon(surface, COLORS['black'], wing_points_left, 2)
            pygame.draw.polygon(surface, color, wing_points_right)
            pygame.draw.polygon(surface, COLORS['black'], wing_points_right, 2)
            # Tail
            pygame.draw.line(surface, color, (center_x - 18, center_y + 5), 
                           (center_x - 28, center_y + 15), 4)
            
        elif sprite_type == 'skeleton':  # Undead
            # Skull
            pygame.draw.circle(surface, color, (center_x, center_y - 10), 10)
            pygame.draw.circle(surface, COLORS['black'], (center_x, center_y - 10), 10, 2)
            # Eye sockets
            pygame.draw.circle(surface, COLORS['black'], (center_x - 4, center_y - 12), 3)
            pygame.draw.circle(surface, COLORS['black'], (center_x + 4, center_y - 12), 3)
            # Ribcage
            for i in range(4):
                y = center_y + 2 + i * 4
                pygame.draw.line(surface, color, (center_x - 8, y), (center_x + 8, y), 2)
            # Spine
            pygame.draw.line(surface, color, (center_x, center_y), (center_x, center_y + 18), 3)
            # Arms (bones)
            pygame.draw.line(surface, color, (center_x - 10, center_y + 2), (center_x - 16, center_y + 12), 3)
            pygame.draw.line(surface, color, (center_x + 10, center_y + 2), (center_x + 16, center_y + 12), 3)
            # Legs (bones)
            pygame.draw.line(surface, color, (center_x - 4, center_y + 18), (center_x - 6, center_y + 30), 3)
            pygame.draw.line(surface, color, (center_x + 4, center_y + 18), (center_x + 6, center_y + 30), 3)
            
        else:  # Default: goblin-like
            # Head
            pygame.draw.circle(surface, color, (center_x, center_y - 8), 10)
            pygame.draw.circle(surface, COLORS['black'], (center_x, center_y - 8), 10, 2)
            # Large eyes
            pygame.draw.circle(surface, COLORS['white'], (center_x - 4, center_y - 10), 4)
            pygame.draw.circle(surface, COLORS['white'], (center_x + 4, center_y - 10), 4)
            pygame.draw.circle(surface, COLORS['black'], (center_x - 3, center_y - 9), 2)
            pygame.draw.circle(surface, COLORS['black'], (center_x + 5, center_y - 9), 2)
            # Pointy ears
            pygame.draw.polygon(surface, color, [
                (center_x - 10, center_y - 10),
                (center_x - 14, center_y - 14),
                (center_x - 8, center_y - 8)
            ])
            pygame.draw.polygon(surface, color, [
                (center_x + 10, center_y - 10),
                (center_x + 14, center_y - 14),
                (center_x + 8, center_y - 8)
            ])
            # Body
            pygame.draw.rect(surface, color, (center_x - 8, center_y + 2, 16, 18))
            pygame.draw.rect(surface, COLORS['black'], (center_x - 8, center_y + 2, 16, 18), 2)
            # Arms
            pygame.draw.rect(surface, color, (center_x - 12, center_y + 4, 4, 12))
            pygame.draw.rect(surface, color, (center_x + 8, center_y + 4, 4, 12))
            # Legs
            pygame.draw.rect(surface, color, (center_x - 6, center_y + 20, 5, 10))
            pygame.draw.rect(surface, color, (center_x + 1, center_y + 20, 5, 10))
        
        filepath = os.path.join(self.output_dir, f"{name}.png")
        pygame.image.save(surface, filepath)
        return filepath
        
    def create_effect_sprite(self, name: str, effect_type: str,
                            color: tuple[int, int, int],
                            size: tuple[int, int] = (64, 64)) -> str:
        """Create spell effect sprites."""
        surface = pygame.Surface(size)
        surface.fill(COLORS['transparent'])
        surface.set_colorkey(COLORS['transparent'])
        
        center_x = size[0] // 2
        center_y = size[1] // 2
        
        if effect_type == 'fireball':
            # Fire core
            pygame.draw.circle(surface, (255, 200, 0), (center_x, center_y), 18)
            pygame.draw.circle(surface, (255, 100, 0), (center_x, center_y), 14)
            pygame.draw.circle(surface, (200, 50, 0), (center_x, center_y), 10)
            
        elif effect_type == 'ice':
            # Ice crystal
            points = []
            import math
            for i in range(6):
                angle = math.radians(i * 60)
                x = center_x + int(20 * math.cos(angle))
                y = center_y + int(20 * math.sin(angle))
                points.append((x, y))
            pygame.draw.polygon(surface, color, points)
            pygame.draw.circle(surface, COLORS['white'], (center_x, center_y), 8)
            
        elif effect_type == 'lightning':
            # Lightning bolt
            bolt_points = [
                (center_x, 5),
                (center_x + 5, 20),
                (center_x, 25),
                (center_x + 8, 40),
                (center_x + 3, 50),
                (center_x, 35),
                (center_x - 3, 45),
            ]
            pygame.draw.lines(surface, color, False, bolt_points, 4)
            pygame.draw.lines(surface, COLORS['white'], False, bolt_points, 2)
            
        elif effect_type == 'heal':
            # Green cross
            pygame.draw.rect(surface, color, (center_x - 4, center_y - 16, 8, 32))
            pygame.draw.rect(surface, color, (center_x - 16, center_y - 4, 32, 8))
            # Glow
            pygame.draw.circle(surface, (*color[:3], 128), (center_x, center_y), 20, 3)
            
        elif effect_type == 'poison':
            # Poison bubbles
            pygame.draw.circle(surface, color, (center_x - 8, center_y - 8), 8)
            pygame.draw.circle(surface, color, (center_x + 6, center_y - 4), 6)
            pygame.draw.circle(surface, color, (center_x - 4, center_y + 8), 7)
            pygame.draw.circle(surface, color, (center_x + 8, center_y + 6), 5)
            
        else:  # Generic magic sparkle
            # Star pattern
            import math
            for i in range(8):
                angle = math.radians(i * 45)
                x = center_x + int(16 * math.cos(angle))
                y = center_y + int(16 * math.sin(angle))
                pygame.draw.circle(surface, color, (x, y), 3)
            pygame.draw.circle(surface, COLORS['white'], (center_x, center_y), 6)
        
        filepath = os.path.join(self.output_dir, f"{name}.png")
        pygame.image.save(surface, filepath)
        return filepath
        
    def create_icon(self, name: str, icon_type: str, 
                   color: tuple[int, int, int],
                   size: tuple[int, int] = (32, 32)) -> str:
        """Create UI icons for status effects, etc."""
        surface = pygame.Surface(size)
        surface.fill(COLORS['transparent'])
        surface.set_colorkey(COLORS['transparent'])
        
        center_x = size[0] // 2
        center_y = size[1] // 2
        
        # Draw border
        pygame.draw.rect(surface, COLORS['black'], (0, 0, size[0], size[1]), 2)
        
        if icon_type == 'stun':
            # Stars around head
            import math
            for i in range(3):
                angle = math.radians(i * 120)
                x = center_x + int(10 * math.cos(angle))
                y = center_y + int(10 * math.sin(angle)) - 5
                # Draw star
                points = []
                for j in range(5):
                    a = math.radians(j * 72 - 90)
                    radius = 4 if j % 2 == 0 else 2
                    points.append((x + int(radius * math.cos(a)), 
                                 y + int(radius * math.sin(a))))
                pygame.draw.polygon(surface, color, points)
                
        elif icon_type == 'poison':
            # Skull
            pygame.draw.circle(surface, color, (center_x, center_y - 4), 8)
            pygame.draw.circle(surface, COLORS['black'], (center_x - 3, center_y - 6), 2)
            pygame.draw.circle(surface, COLORS['black'], (center_x + 3, center_y - 6), 2)
            # Crossbones
            pygame.draw.line(surface, color, (center_x - 8, center_y + 8), 
                           (center_x + 8, center_y + 8), 3)
            
        elif icon_type == 'sleep':
            # Z's
            for i, (x, y) in enumerate([(8, 8), (14, 4), (20, 0)]):
                size_z = 6 - i
                pygame.draw.line(surface, color, (x, y), (x + size_z, y), 2)
                pygame.draw.line(surface, color, (x, y + size_z), (x + size_z, y), 2)
                pygame.draw.line(surface, color, (x, y + size_z), (x + size_z, y + size_z), 2)
                
        elif icon_type == 'fire':
            # Flame
            points = [
                (center_x, center_y - 10),
                (center_x + 6, center_y),
                (center_x + 4, center_y + 8),
                (center_x - 4, center_y + 8),
                (center_x - 6, center_y),
            ]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, (255, 200, 0), 
                              [(p[0], p[1] + 2) for p in points[:3]] + [(center_x, center_y + 6)])
            
        else:  # Generic effect
            pygame.draw.circle(surface, color, (center_x, center_y), 12)
            pygame.draw.circle(surface, COLORS['white'], (center_x, center_y), 8)
        
        filepath = os.path.join(self.output_dir, f"{name}.png")
        pygame.image.save(surface, filepath)
        return filepath


def generate_all_sprites():
    """Generate all sprites needed for the game."""
    print("Generating sprites...")
    
    # Player characters
    sprite_gen = SpriteGenerator("src/ui_pygame/assets/sprites")
    
    # Player classes
    sprite_gen.create_humanoid_sprite("player_warrior", COLORS['player_blue'], 
                                     has_weapon=True, has_shield=True)
    sprite_gen.create_humanoid_sprite("player_mage", COLORS['player_light_blue'], 
                                     has_weapon=False)
    sprite_gen.create_humanoid_sprite("player_rogue", (80, 80, 120), 
                                     has_weapon=True)
    sprite_gen.create_humanoid_sprite("player_cleric", (200, 200, 100), 
                                     has_shield=True)
    sprite_gen.create_humanoid_sprite("player_default", COLORS['player_blue'])
    
    # Common enemies
    sprite_gen.create_monster_sprite("goblin", "goblin", COLORS['goblin_green'])
    sprite_gen.create_monster_sprite("orc", "goblin", COLORS['orc_gray'])
    sprite_gen.create_monster_sprite("skeleton", "skeleton", COLORS['skeleton_white'])
    sprite_gen.create_monster_sprite("zombie", "goblin", COLORS['undead_gray'])
    sprite_gen.create_monster_sprite("spider", "spider", COLORS['spider_black'])
    sprite_gen.create_monster_sprite("wolf", "quadruped", COLORS['beast_brown'])
    sprite_gen.create_monster_sprite("slime", "blob", COLORS['slime_green'])
    sprite_gen.create_monster_sprite("dragon", "dragon", COLORS['dragon_red'])
    sprite_gen.create_monster_sprite("demon", "goblin", COLORS['demon_purple'])
    
    print(f"  ✓ Created {9} character sprites")
    
    # Effects
    effect_gen = SpriteGenerator("src/ui_pygame/assets/effects")
    effect_gen.create_effect_sprite("fireball", "fireball", (255, 100, 0))
    effect_gen.create_effect_sprite("ice_shard", "ice", (100, 200, 255))
    effect_gen.create_effect_sprite("lightning", "lightning", (255, 255, 100))
    effect_gen.create_effect_sprite("heal", "heal", (100, 255, 100))
    effect_gen.create_effect_sprite("poison", "poison", (100, 200, 100))
    effect_gen.create_effect_sprite("magic", "sparkle", (200, 100, 255))
    
    print(f"  ✓ Created {6} effect sprites")
    
    # Status icons
    icon_gen = SpriteGenerator("src/ui_pygame/assets/ui")
    icon_gen.create_icon("icon_stun", "stun", (255, 255, 100))
    icon_gen.create_icon("icon_poison", "poison", (100, 200, 100))
    icon_gen.create_icon("icon_sleep", "sleep", (150, 150, 255))
    icon_gen.create_icon("icon_burn", "fire", (255, 100, 50))
    icon_gen.create_icon("icon_frozen", "ice", (100, 200, 255))
    icon_gen.create_icon("icon_blind", "generic", (80, 80, 80))
    
    print(f"  ✓ Created {6} UI icons")
    print(f"\n✓ Total: {21} sprites generated!")


if __name__ == "__main__":
    generate_all_sprites()
