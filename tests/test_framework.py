"""
Test Framework for Dungeon Crawl - Quick Testing Utilities

This module provides utilities to quickly set up game states for testing
without needing to play through the entire game.

Usage:
    from tests.test_framework import TestGameState
    
    # Create a Knight Enchanter ready for final boss
    player = TestGameState.create_player_for_final_boss()
    
    # Create a player with specific equipment/spells
    player = TestGameState.create_player(
        class_name="Knight Enchanter",
        level=50,
        health=(500, 500),
        mana=(200, 200),
        spells=["Fireball", "Heal"],
        skills=["Arcane Blast"],
        equipment={"Weapon": "Mithril Sword", "Armor": "Mithril Plate"}
    )
"""

import copy

from src.core.character import Resource, Stats, Combat, Level
from src.core.player import Player
from src.core.save_system import SaveManager
from src.core import classes
from src.core import items
from src.core import abilities
from src.core import races

# Import specific ability classes for better reliability
from src.core.abilities import (
    ArcaneBlast, Fireball, Heal, Heal2, Heal3,
    Regen, Regen2, Regen3, ManaShield
)

# Import specific item classes
from src.core.items import (
    MithrilshodStaff, PlateMail, PowerRing,
    GarfunkelPendant, NoWeapon, NoArmor, NoOffHand, NoPendant, NoRing
)


class TestGameState:
    """Factory for creating test player states."""
    
    @staticmethod
    def create_player(
        name: str = "TestPlayer",
        class_name: str = "Knight Enchanter",
        race_name: str = "Human",
        level: int = 50,
        pro_level: int = None,
        health: tuple = (500, 500),
        mana: tuple = (200, 200),
        stats: dict = None,
        gold: int = 10000,
        spells: list = None,
        skills: list = None,
        equipment: dict = None,
        save_as: str = None,
    ) -> Player:
        """
        Create a custom test player.
        
        Args:
            name: Player name
            class_name: Character class (e.g., "Knight Enchanter")
            race_name: Character race (e.g., "Human")
            level: Player level
            pro_level: Promotion level (auto-determined from class if None)
                Mage line: Mage=1, Sorcerer/Warlock/Spellblade/Summoner=2, Wizard/Shadowcaster/Knight Enchanter/Grand Summoner=3
            health: (max, current) tuple
            mana: (max, current) tuple
            stats: Dict of stats (str, int, wis, con, cha, dex)
            gold: Starting gold
            spells: List of spell names to add
            skills: List of skill names to add
            equipment: Dict of slot -> item name mappings
        
        Returns:
            Player: Configured player instance
        """
        # Set up stats
        if stats is None:
            stats = {
                'strength': 20, 'intel': 25, 'wisdom': 20,
                'con': 18, 'charisma': 15, 'dex': 18
            }
        
        stats_obj = Stats(
            strength=stats.get('strength', 20),
            intel=stats.get('intel', 25),
            wisdom=stats.get('wisdom', 20),
            con=stats.get('con', 18),
            charisma=stats.get('charisma', 15),
            dex=stats.get('dex', 18),
        )
        
        # Set up combat
        combat_obj = Combat(attack=10, defense=10, magic=15, magic_def=10)
        
        # Auto-determine pro_level from class if not explicitly provided
        # This ensures the pro_level matches the class (e.g., Mage=1, Warlock=2, Shadowcaster=3)
        if pro_level is None:
            pro_level = TestGameState._get_class_pro_level(class_name)
        
        # Create level
        level_obj = Level(level=level, pro_level=pro_level, exp=0, exp_to_gain=50)
        
        # Create resources
        health_obj = Resource(max=health[0], current=health[1])
        mana_obj = Resource(max=mana[0], current=mana[1])
        
        # Create player
        player = Player(
            location_x=5, location_y=10, location_z=0,
            level=level_obj,
            health=health_obj,
            mana=mana_obj,
            stats=stats_obj,
            combat=combat_obj,
            gold=gold,
            resistance={'Fire': 0., 'Ice': 0., 'Electric': 0., 'Water': 0., 
                       'Earth': 0., 'Wind': 0., 'Shadow': 0., 'Holy': 0., 
                       'Poison': 0., 'Physical': 0.}
        )
        
        player.name = name
        
        # Set class
        for cls_attr in dir(classes):
            cls_obj = getattr(classes, cls_attr)
            if hasattr(cls_obj, '__call__'):
                try:
                    instance = cls_obj()
                    if hasattr(instance, 'name') and instance.name == class_name:
                        player.cls = instance
                        break
                except Exception:
                    pass
        
        # Set race
        for race_attr in dir(races):
            race_obj = getattr(races, race_attr)
            if hasattr(race_obj, '__call__'):
                try:
                    instance = race_obj()
                    if hasattr(instance, 'name') and instance.name == race_name:
                        player.race = instance
                        break
                except Exception:
                    pass
        
        # Add spells
        if spells:
            for spell_name in spells:
                spell = TestGameState._get_ability_by_name(spell_name)
                if spell:
                    player.spellbook['Spells'][spell_name] = spell
        
        # Add skills/power-ups
        if skills:
            for skill_name in skills:
                skill = TestGameState._get_ability_by_name(skill_name)
                if skill:
                    player.spellbook['Skills'][skill_name] = skill
                    # If it's a power-up ability, set the flag
                    if hasattr(skill, 'subtyp') and skill.subtyp == 'Power Up':
                        player.power_up = True
        
        # Set equipment
        if equipment:
            for slot, item_name in equipment.items():
                item = TestGameState._get_item_by_name(item_name)
                if item:
                    player.equipment[slot] = item
        else:
            # If no custom equipment provided, use class default equipment
            if hasattr(player.cls, 'equipment') and player.cls.equipment:
                # Deep copy equipment so tests cannot leak mutable item state
                # (for example weapon disarm flags or other per-item mutations)
                # into later synthetic players created from the same class defaults.
                player.equipment = copy.deepcopy(player.cls.equipment)
        
        # Save character if requested
        if save_as:
            SaveManager.save_player(player, save_as)
        
        return player
    
    @staticmethod
    def create_player_for_final_boss(save_as: str = None) -> Player:
        """
        Create a Knight Enchanter fully prepared for the final Devil boss.
        
        Args:
            save_as: Optional filename to save the character (e.g., 'final_boss_ready.save')
        
        Returns:
            Player: High-level Knight Enchanter with Arcane Blast
        """
        return TestGameState.create_player(
            name="FinalBossReady",
            class_name="Knight Enchanter",
            level=50,
            health=(999, 999),
            mana=(999, 999),
            stats={
                'strength': 18, 'intel': 30, 'wisdom': 22,
                'con': 20, 'charisma': 16, 'dex': 19
            },
            gold=500000,
            spells=["Fireball", "Heal", "Heal3", "Regen3"],
            skills=["Arcane Blast", "ManaSlice2"],
            equipment={
                "Weapon": "Falchion",
                "Armor": "Tarnkappe",
                "OffHand": "Compendium of the Ancients",
                "Ring": "Force Ring",
                "Pendant": "Diamond Locket"
            },
            save_as=save_as
        )
    
    @staticmethod
    def create_player_with_class(class_name: str, level: int = 30) -> Player:
        """
        Create a player of a specific class at a given level.
        
        Args:
            class_name: Name of the class
            level: Player level
        
        Returns:
            Player: Player of the specified class
        """
        return TestGameState.create_player(
            name=f"Test{class_name}",
            class_name=class_name,
            level=level,
            health=(300, 300),
            mana=(150, 150),
        )
    
    @staticmethod
    def _get_class_pro_level(class_name: str) -> int:
        """Get the promotion level for a given class name.
        
        Returns:
            int: The pro_level (1-3) for the class, or 1 if not found
        """
        # Try to find the class and get its pro_level
        for cls_attr in dir(classes):
            cls_obj = getattr(classes, cls_attr)
            if hasattr(cls_obj, '__call__'):
                try:
                    instance = cls_obj()
                    if hasattr(instance, 'name') and instance.name == class_name:
                        return getattr(instance, 'pro_level', 1)
                except Exception:
                    pass
        # Default to 1 if not found
        return 1
    
    @staticmethod
    def _get_ability_by_name(name: str):
        """Find and instantiate an ability by name.
        
        Supports:
        - Class names: 'Fireball', 'Heal', 'Heal2', 'Heal3'
        - Display names with variants: 'Heal (upgraded)', 'Heal3 (best)'
        - Aliases: maps common names to specific versions
        """
        # Direct class name mappings - use class names as primary key
        # This avoids ambiguity with abilities that share display names
        ability_classes = {
            # Most common/base versions
            'ArcaneBlast': abilities.ArcaneBlast,
            'ManaShield': abilities.ManaShield,
            'Fireball': abilities.Fireball,
            'Heal': abilities.Heal,
            'Regen': abilities.Regen,
            
            # Explicit variants - use for disambiguation
            'Heal2': abilities.Heal2,      # Upgraded Heal
            'Heal3': abilities.Heal3,      # Best Heal
            'Regen2': abilities.Regen2,    # Upgraded Regen
            'Regen3': abilities.Regen3,    # Best Regen
            'ManaShield2': abilities.ManaShield2,
            'ManaSlice': abilities.ManaSlice,
            'ManaSlice2': abilities.ManaSlice2,
            
            # Aliases for convenience
            'Greater Heal': abilities.Heal2,
            'Best Heal': abilities.Heal3,
            'Health Regeneration': abilities.Regen,  # Regen actually heals health
            'Health Regeneration (upgraded)': abilities.Regen2,
            'Health Regeneration (best)': abilities.Regen3,
        }
        
        # Try direct class name/alias map first
        if name in ability_classes:
            try:
                return ability_classes[name]()
            except Exception:
                pass
        
        # Fallback to search by display name (returns first match - may be ambiguous!)
        for attr_name in dir(abilities):
            attr = getattr(abilities, attr_name)
            if hasattr(attr, '__call__'):
                try:
                    instance = attr()
                    if hasattr(instance, 'name') and instance.name == name:
                        return instance
                except Exception:
                    pass
        return None
    
    @staticmethod
    def _get_item_by_name(name: str):
        """Find and instantiate an item by name."""
        # Direct class mappings for common items
        item_classes = {
            'Mithrilshod Staff': items.MithrilshodStaff,  # Best 2-handed sword available
            'Plate Mail': items.PlateMail,  # Heavy plate armor
            'Power Ring': items.PowerRing,  # Best ring
            'Garfunkel Pendant': items.GarfunkelPendant,  # Good pendant
            'Leather Armor': items.LeatherArmor,
            'Jian': items.Jian if hasattr(items, 'Jian') else None,
        }
        
        # Try direct class map first
        if name in item_classes and item_classes[name]:
            try:
                return item_classes[name]()
            except Exception:
                pass
        
        # Fallback to search if not in map
        for attr_name in dir(items):
            attr = getattr(items, attr_name)
            if hasattr(attr, '__call__'):
                try:
                    instance = attr()
                    if hasattr(instance, 'name') and instance.name == name:
                        return instance
                except Exception:
                    pass
        
        # Fallback: return None equipment
        try:
            return items.remove_equipment('Weapon')
        except Exception:
            return None


# Debug helper to quickly test specific scenarios
if __name__ == "__main__":
    # Example: Create and inspect a test player
    player = TestGameState.create_player_for_final_boss(save_as="final_boss_ready.save")
    print(f"Created test player: {player.name}")
    print(f"  Class: {player.cls.name}")
    print(f"  Level: {player.level.level}")
    print(f"  Health: {player.health.current}/{player.health.max}")
    print(f"  Mana: {player.mana.current}/{player.mana.max}")
    print(f"  Spells: {list(player.spellbook['Spells'].keys())}")
    print(f"  Skills: {list(player.spellbook['Skills'].keys())}")
    print(f"  Power Up: {player.power_up}")
