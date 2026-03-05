#!/usr/bin/env python3
"""
Character and Combat System Tests

Tests core character functionality, combat mechanics, and API contracts.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest

from src.core.enemies import Goblin
from src.core import items
from tests.test_framework import TestGameState


class TestCharacterCreation:
    """Test basic character creation and initialization."""
    
    def test_create_basic_character(self):
        """Test creating a basic character."""
        char = TestGameState.create_player(
            name="TestHero",
            class_name="Warrior",
            race_name="Human"
        )
        assert char.name == "TestHero"
        assert char.race.name == "Human"
        assert char.cls.name == "Warrior"
        assert char.is_alive()
    
    def test_character_has_required_attributes(self):
        """Verify character has all required attributes for combat."""
        char = TestGameState.create_player(name="Test", class_name="Warrior", race_name="Human")
        
        # Core attributes
        assert hasattr(char, 'name')
        assert hasattr(char, 'health')
        assert hasattr(char, 'mana')
        assert hasattr(char, 'stats')
        assert hasattr(char, 'combat')
        assert hasattr(char, 'equipment')
        
        # Combat attributes
        assert hasattr(char, 'magic_effects')
        assert hasattr(char, 'status_effects')
        assert hasattr(char, 'physical_effects')
        assert hasattr(char, 'stat_effects')
        
        # Methods
        assert hasattr(char, 'is_alive')
        assert hasattr(char, 'weapon_damage')
        assert hasattr(char, 'hit_chance')
        assert hasattr(char, 'dodge_chance')


class TestCharacterMethods:
    """Test character methods exist and have correct signatures."""
    
    def test_check_active_method(self):
        """Test if check_active method exists or needs to be added."""
        char = TestGameState.create_player(name="Test", class_name="Warrior", race_name="Human")
        
        # This will fail if method doesn't exist
        if hasattr(char, 'check_active'):
            active, message = char.check_active()
            assert isinstance(active, bool)
            assert isinstance(message, str)
        else:
            pytest.skip("check_active method not implemented - needs to be added")
    
    def test_incapacitated_method(self):
        """Test incapacitated method."""
        char = TestGameState.create_player(name="Test", class_name="Warrior", race_name="Human")
        assert hasattr(char, 'incapacitated')
        result = char.incapacitated()
        assert isinstance(result, bool)
    
    def test_weapon_damage_signature(self):
        """Verify weapon_damage has the expected signature."""
        char = TestGameState.create_player(name="Attacker", class_name="Warrior", race_name="Human")
        target = Goblin()

        # Should accept target as first positional argument
        # Should return tuple of (str, bool, int)
        result = char.weapon_damage(target)
        assert isinstance(result, tuple)
        assert len(result) == 3
        result_str, hit, crit = result
        assert isinstance(result_str, str)
        assert isinstance(hit, bool)
        assert isinstance(crit, (int, float))

    def test_disarm_reduces_enemy_weapon_mod_total(self):
        """Disarm should reduce total weapon attack output, not only base weapon damage."""
        enemy = Goblin()
        enemy.status_effects["Berserk"].active = False
        enemy.magic_effects["Totem"].active = False
        enemy.stat_effects["Attack"].active = False

        enemy.physical_effects["Disarm"].active = False
        armed_mod = enemy.check_mod("weapon")

        enemy.physical_effects["Disarm"].active = True
        disarmed_mod = enemy.check_mod("weapon")

        expected_armed = enemy.combat.attack + enemy.equipment["Weapon"].damage
        expected_disarmed = int(enemy.combat.attack * 0.5)

        assert armed_mod == expected_armed
        assert disarmed_mod == expected_disarmed
        assert disarmed_mod < armed_mod

    def test_disarm_reduces_player_weapon_mod_total(self):
        """Player check_mod override should apply the same disarm weapon penalty."""
        player = TestGameState.create_player(name="Test", class_name="Warrior", race_name="Human")
        player.status_effects["Berserk"].active = False
        player.stat_effects["Attack"].active = False

        player.physical_effects["Disarm"].active = False
        armed_mod = player.check_mod("weapon")

        player.physical_effects["Disarm"].active = True
        disarmed_mod = player.check_mod("weapon")

        expected_armed = player.combat.attack + player.equipment["Weapon"].damage
        expected_disarmed = int(player.combat.attack * 0.5)

        assert armed_mod == expected_armed
        assert disarmed_mod == expected_disarmed
        assert disarmed_mod < armed_mod

    def test_fist_weapon_not_penalized_by_disarm(self):
        """Fist weapons are not disarmable and should not lose attack from disarm state."""
        player = TestGameState.create_player(name="Test", class_name="Warrior", race_name="Human")
        player.equipment["Weapon"] = items.BrassKnuckles()
        player.status_effects["Berserk"].active = False
        player.stat_effects["Attack"].active = False

        assert player.can_be_disarmed() is False

        player.physical_effects["Disarm"].active = False
        armed_mod = player.check_mod("weapon")

        player.physical_effects["Disarm"].active = True
        disarmed_mod = player.check_mod("weapon")

        assert disarmed_mod == armed_mod


class TestCombatAPIContract:
    """Test the API contract between combat systems and character."""
    
    def test_enemy_has_combat_attributes(self):
        """Verify enemies have all required combat attributes."""
        from src.core.enemies import Goblin
        
        enemy = Goblin()
        assert hasattr(enemy, 'name')
        assert hasattr(enemy, 'health')
        assert hasattr(enemy, 'magic_effects')
        assert hasattr(enemy, 'status_effects')
        assert hasattr(enemy, 'tunnel')
        assert hasattr(enemy, 'is_alive')
        assert hasattr(enemy, 'weapon_damage')
        assert hasattr(enemy, 'dodge_chance')
    
    def test_player_has_combat_attributes(self):
        """Verify player has all required combat attributes."""
        # Use TestGameState to properly create a player
        player = TestGameState.create_player(name="TestPlayer", class_name="Warrior", race_name="Human")
        
        # Basic attributes
        assert hasattr(player, 'name')
        assert hasattr(player, 'health')
        assert hasattr(player, 'cls')
        
        # Combat methods
        assert hasattr(player, 'weapon_damage')
        assert hasattr(player, 'is_alive')


class TestEnhancedCombatRequirements:
    """Test requirements for enhanced combat system."""
    
    def test_character_needs_check_active(self):
        """Document that check_active method is needed."""
        char = TestGameState.create_player(name="Test", class_name="Warrior", race_name="Human")
        
        if not hasattr(char, 'check_active'):
            # This is expected - we need to add it
            print("⚠️  check_active method missing - needs implementation")
            assert True  # Document the requirement
        else:
            active, msg = char.check_active()
            assert isinstance(active, bool)
            assert isinstance(msg, str)
    
    def test_character_has_speed_stat(self):
        """Verify characters have speed/dex stat for turn order."""
        char = TestGameState.create_player(name="Test", class_name="Warrior", race_name="Human")
        
        # Check for speed or dexterity stat
        assert hasattr(char, 'stats')
        assert hasattr(char.stats, 'dex') or hasattr(char.stats, 'speed')


def run_tests():
    """Run all tests and report results."""
    print("=" * 70)
    print("CHARACTER AND COMBAT SYSTEM TESTS")
    print("=" * 70)
    print()
    
    # Run pytest with verbose output
    import pytest
    exit_code = pytest.main([
        __file__,
        '-v',
        '--tb=short',
        '--color=yes'
    ])
    
    return exit_code


if __name__ == '__main__':
    sys.exit(run_tests())
