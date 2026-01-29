"""
Sprite Manager - Loads and manages sprite assets for Dungeon Crawl.

This module provides a centralized sprite management system with caching,
enemy-to-sprite mapping, and easy sprite retrieval.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import pygame
import os

if TYPE_CHECKING:
    from src.core.character import Character

# Enemy name to sprite mapping
ENEMY_SPRITE_MAP = {
    # Goblins and small humanoids
    'Goblin': 'goblin',
    'Hobgoblin': 'goblin',
    'Kobold': 'goblin',
    'Gnoll': 'goblin',
    'Imp': 'goblin',
    
    # Orcs and larger humanoids
    'Orc': 'orc',
    'Ogre': 'orc',
    'Minotaur': 'orc',
    'Troll': 'orc',
    
    # Undead
    'Skeleton': 'skeleton',
    'Zombie': 'zombie',
    'Ghoul': 'zombie',
    'Wraith': 'skeleton',
    'Lich': 'skeleton',
    'Vampire': 'zombie',
    'Wight': 'skeleton',
    
    # Beasts
    'Wolf': 'wolf',
    'Dire Wolf': 'wolf',
    'Bear': 'wolf',
    'Dire Bear': 'wolf',
    'Panther': 'wolf',
    'Werewolf': 'wolf',
    
    # Spiders and insects
    'Spider': 'spider',
    'Giant Spider': 'spider',
    'Scorpion': 'spider',
    'Giant Scorpion': 'spider',
    'Centipede': 'spider',
    'Hornet': 'spider',
    
    # Slimes
    'Slime': 'slime',
    'Ooze': 'slime',
    'Jelly': 'slime',
    
    # Dragons
    'Dragon': 'dragon',
    'Red Dragon': 'dragon',
    'Wyvern': 'dragon',
    'Wyrm': 'dragon',
    'Pseudodragon': 'dragon',
    
    # Demons and fiends
    'Demon': 'demon',
    'Devil': 'demon',
    'Archvile': 'demon',
    'Quasit': 'demon',
    
    # Default for unknown enemies
    'default': 'goblin',
}

# Player class to sprite mapping
PLAYER_SPRITE_MAP = {
    'Warrior': 'player_warrior',
    'Paladin': 'player_warrior',
    'Crusader': 'player_warrior',
    'Berserker': 'player_warrior',
    
    'Mage': 'player_mage',
    'Wizard': 'player_mage',
    'Sorcerer': 'player_mage',
    'Warlock': 'player_mage',
    'Summoner': 'player_mage',
    
    'Rogue': 'player_rogue',
    'Thief': 'player_rogue',
    'Assassin': 'player_rogue',
    'Ninja': 'player_rogue',
    'Ranger': 'player_rogue',
    'Hunter': 'player_rogue',
    
    'Cleric': 'player_cleric',
    'Priest': 'player_cleric',
    'Monk': 'player_cleric',
    'Druid': 'player_cleric',
    
    'default': 'player_default',
}


class SpriteManager:
    """Manages sprite loading, caching, and retrieval."""
    
    def __init__(self, assets_dir: str = "src/ui_pygame/assets"):
        """Initialize sprite manager."""
        self.assets_dir = assets_dir
        self.sprite_cache: dict[str, pygame.Surface] = {}
        self.effect_cache: dict[str, pygame.Surface] = {}
        self.icon_cache: dict[str, pygame.Surface] = {}
        
    def load_sprite(self, name: str, category: str = "sprites") -> pygame.Surface | None:
        """Load a sprite from file with caching."""
        cache_key = f"{category}:{name}"
        
        # Check cache first
        if cache_key in self.sprite_cache:
            return self.sprite_cache[cache_key]
        
        # Build file path
        filepath = os.path.join(self.assets_dir, category, f"{name}.png")
        
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"Warning: Sprite not found: {filepath}")
            return None
        
        # Load and cache
        try:
            # Load without convert_alpha for headless compatibility
            surface = pygame.image.load(filepath)
            # Try to convert if display is available
            try:
                surface = surface.convert_alpha()
            except pygame.error:
                pass  # No display available, use unconverted surface
            self.sprite_cache[cache_key] = surface
            return surface
        except Exception as e:
            print(f"Error loading sprite {filepath}: {e}")
            return None
            
    def get_character_sprite(self, character: Character) -> pygame.Surface | None:
        """Get appropriate sprite for a character (player or enemy)."""
        # Determine if this is a player or enemy
        is_player = hasattr(character, 'cls') and hasattr(character.cls, 'name')
        
        if is_player:
            # Player character - use class name
            class_name = character.cls.name if hasattr(character.cls, 'name') else 'default'
            sprite_name = PLAYER_SPRITE_MAP.get(class_name, PLAYER_SPRITE_MAP['default'])
        else:
            # Enemy - use name
            enemy_name = character.name
            
            # Try exact match first
            sprite_name = ENEMY_SPRITE_MAP.get(enemy_name)
            
            # If no exact match, try partial matches
            if sprite_name is None:
                for key in ENEMY_SPRITE_MAP.keys():
                    if key in enemy_name or enemy_name in key:
                        sprite_name = ENEMY_SPRITE_MAP[key]
                        break
            
            # Fall back to default
            if sprite_name is None:
                sprite_name = ENEMY_SPRITE_MAP['default']
        
        return self.load_sprite(sprite_name, "sprites")
        
    def get_effect_sprite(self, effect_name: str) -> pygame.Surface | None:
        """Get spell/effect sprite."""
        # Map effect names to sprite files
        effect_map = {
            'fire': 'fireball',
            'fireball': 'fireball',
            'ice': 'ice_shard',
            'frost': 'ice_shard',
            'lightning': 'lightning',
            'thunder': 'lightning',
            'heal': 'heal',
            'cure': 'heal',
            'poison': 'poison',
            'magic': 'magic',
            'arcane': 'magic',
        }
        
        # Normalize effect name
        effect_lower = effect_name.lower()
        sprite_name = None
        
        # Try exact match
        sprite_name = effect_map.get(effect_lower)
        
        # Try partial match
        if sprite_name is None:
            for key in effect_map.keys():
                if key in effect_lower:
                    sprite_name = effect_map[key]
                    break
        
        # Default to magic
        if sprite_name is None:
            sprite_name = 'magic'
            
        return self.load_sprite(sprite_name, "effects")
        
    def get_status_icon(self, status_name: str) -> pygame.Surface | None:
        """Get status effect icon."""
        # Map status names to icon files
        icon_map = {
            'stun': 'icon_stun',
            'stunned': 'icon_stun',
            'poison': 'icon_poison',
            'poisoned': 'icon_poison',
            'sleep': 'icon_sleep',
            'sleeping': 'icon_sleep',
            'asleep': 'icon_sleep',
            'burn': 'icon_burn',
            'burning': 'icon_burn',
            'frozen': 'icon_frozen',
            'freeze': 'icon_frozen',
            'blind': 'icon_blind',
            'blinded': 'icon_blind',
        }
        
        # Normalize status name
        status_lower = status_name.lower()
        icon_name = icon_map.get(status_lower, 'icon_blind')  # Default icon
        
        return self.load_sprite(icon_name, "ui")
        
    def scale_sprite(self, sprite: pygame.Surface, scale: float) -> pygame.Surface:
        """Scale a sprite by a factor."""
        if sprite is None:
            return None
        new_size = (int(sprite.get_width() * scale), int(sprite.get_height() * scale))
        return pygame.transform.scale(sprite, new_size)
        
    def flip_sprite(self, sprite: pygame.Surface, horizontal: bool = True, 
                   vertical: bool = False) -> pygame.Surface:
        """Flip a sprite horizontally or vertically."""
        if sprite is None:
            return None
        return pygame.transform.flip(sprite, horizontal, vertical)
        
    def preload_common_sprites(self):
        """Preload commonly used sprites into cache."""
        print("Preloading sprites...")
        
        # Load all player sprites
        for sprite_name in set(PLAYER_SPRITE_MAP.values()):
            self.load_sprite(sprite_name, "sprites")
            
        # Load common enemy sprites
        common_enemies = ['goblin', 'orc', 'skeleton', 'zombie', 'spider', 'wolf', 'slime']
        for sprite_name in common_enemies:
            self.load_sprite(sprite_name, "sprites")
            
        # Load all effects
        effects = ['fireball', 'ice_shard', 'lightning', 'heal', 'poison', 'magic']
        for effect_name in effects:
            self.load_sprite(effect_name, "effects")
            
        # Load all icons
        icons = ['icon_stun', 'icon_poison', 'icon_sleep', 'icon_burn', 'icon_frozen', 'icon_blind']
        for icon_name in icons:
            self.load_sprite(icon_name, "ui")
            
        print(f"  ✓ Preloaded {len(self.sprite_cache)} sprites")
        
    def clear_cache(self):
        """Clear sprite cache to free memory."""
        self.sprite_cache.clear()
        self.effect_cache.clear()
        self.icon_cache.clear()


# Global sprite manager instance
_sprite_manager: SpriteManager | None = None


def get_sprite_manager() -> SpriteManager:
    """Get or create the global sprite manager."""
    global _sprite_manager
    if _sprite_manager is None:
        _sprite_manager = SpriteManager()
        # Preload common sprites
        try:
            _sprite_manager.preload_common_sprites()
        except Exception as e:
            print(f"Warning: Could not preload sprites: {e}")
    return _sprite_manager


if __name__ == "__main__":
    # Test sprite loading
    pygame.init()
    
    print("Testing sprite manager...")
    manager = get_sprite_manager()
    
    # Test loading sprites
    warrior = manager.load_sprite("player_warrior", "sprites")
    print(f"✓ Loaded player_warrior: {warrior.get_size() if warrior else 'FAILED'}")
    
    goblin = manager.load_sprite("goblin", "sprites")
    print(f"✓ Loaded goblin: {goblin.get_size() if goblin else 'FAILED'}")
    
    fireball = manager.load_sprite("fireball", "effects")
    print(f"✓ Loaded fireball effect: {fireball.get_size() if fireball else 'FAILED'}")
    
    stun_icon = manager.load_sprite("icon_stun", "ui")
    print(f"✓ Loaded stun icon: {stun_icon.get_size() if stun_icon else 'FAILED'}")
    
    print(f"\n✓ Sprite manager test complete!")
    print(f"  Cache contains {len(manager.sprite_cache)} sprites")
