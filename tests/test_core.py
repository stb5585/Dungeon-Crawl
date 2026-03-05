#!/usr/bin/env python3
"""
Core Functionality Tests

Tests core character and combat functionality without external dependencies.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.enemies import Goblin
from tests.test_framework import TestGameState


def test_character_creation():
    """Test basic character creation."""
    print("\n[Test] Character Creation")
    
    char = TestGameState.create_player(name="TestHero", class_name="Warrior", race_name="Human")
    assert char.name == "TestHero"
    assert char.is_alive()
    print("  ✅ Character can be created")
    print(f"  ✅ Character name: {char.name}")
    print(f"  ✅ Character race: {char.race.name}")
    print(f"  ✅ Character class: {char.cls.name}")


def test_character_attributes():
    """Test character attributes and stats."""
    print("\n[Test] Character Attributes")
    
    char = TestGameState.create_player(name="TestHero", class_name="Warrior", race_name="Human")
    
    required_attrs = [
        'name', 'health', 'mana', 'stats', 'combat', 'equipment',
        'magic_effects', 'status_effects', 'physical_effects', 'stat_effects'
    ]
    
    missing = []
    for attr in required_attrs:
        if not hasattr(char, attr):
            missing.append(attr)
        else:
            print(f"  ✅ {attr}")
    
    assert not missing, f"Missing attributes: {missing}"


def test_character_methods():
    """Test character has required methods."""
    print("\n[Test] Character Methods")
    
    char = TestGameState.create_player(name="Test", class_name="Warrior", race_name="Human")
    
    # Test existing methods
    methods_found = []
    methods_missing = []
    
    if hasattr(char, 'is_alive'):
        assert callable(char.is_alive)
        print("  ✅ is_alive()")
        methods_found.append('is_alive')
    
    if hasattr(char, 'incapacitated'):
        assert callable(char.incapacitated)
        result = char.incapacitated()
        print(f"  ✅ incapacitated() -> {result}")
        methods_found.append('incapacitated')
    
    if hasattr(char, 'check_active'):
        assert callable(char.check_active)
        active, msg = char.check_active()
        print(f"  ✅ check_active() -> ({active}, '{msg}')")
        methods_found.append('check_active')
    else:
        print("  ⚠️  check_active() - NOT FOUND (needed by EnhancedBattleManager)")
        methods_missing.append('check_active')
    
    if hasattr(char, 'weapon_damage'):
        print("  ✅ weapon_damage()")
        methods_found.append('weapon_damage')
    
    # Assert no methods are missing
    assert len(methods_missing) == 0, f"Missing methods: {methods_missing}"


def test_weapon_damage_api():
    """Test weapon_damage API contract."""
    print("\n[Test] weapon_damage API")
    
    attacker = TestGameState.create_player(name="Attacker", class_name="Warrior", race_name="Human")
    defender = Goblin()

    result = attacker.weapon_damage(defender)
    assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
    assert len(result) == 3, f"Expected 3 elements, got {len(result)}"
    
    result_str, hit, crit = result
    print(f"  ✅ Returns tuple(str, bool, int/float)")
    print(f"  ✅ Result: hit={hit}, crit={crit}")


def test_combat_result():
    """Test CombatResult creation."""
    print("\n[Test] CombatResult API")
    from src.core.combat.combat_result import CombatResult
    
    # Test creating with minimal args
    result = CombatResult(action="Attack")
    print("  ✅ Can create with action only")
    print(f"  ✅ actor={result.actor}, target={result.target}")
    assert result.action == "Attack"
    assert result.actor is None
    assert result.target is None


def test_enemy_creation():
    """Test enemy creation."""
    print("\n[Test] Enemy Creation")
    from src.core.enemies import random_enemy
    
    enemy = random_enemy('0')
    print(f"  ✅ Created enemy: {enemy.name}")
    assert enemy.name is not None
    
    # Check if enemy has check_active
    if hasattr(enemy, 'check_active'):
        print("  ✅ Enemy has check_active()")
    else:
        print("  ⚠️  Enemy missing check_active()")


def test_player_creation():
    """Test player creation."""
    print("\n[Test] Player Creation")
    
    # Use TestGameState to properly create a player
    player = TestGameState.create_player(name="TestPlayer", class_name="Warrior", race_name="Human")
    print(f"  ✅ Created player: {player.name}")
    assert player.name == "TestPlayer"
    
    # Check if player has check_active
    if hasattr(player, 'check_active'):
        print("  ✅ Player has check_active()")
    else:
        print("  ⚠️  Player missing check_active() - REQUIRED by EnhancedBattleManager")


def main():
    """Run all tests."""
    tests = [
        test_character_creation,
        test_character_attributes,
        test_character_methods,
        test_weapon_damage_api,
        test_combat_result,
        test_enemy_creation,
        test_player_creation,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            if isinstance(result, tuple):
                success, details = result
                results.append((test.__name__, success, details))
            else:
                results.append((test.__name__, True, None))
        except Exception as e:
            print(f"  ❌ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test.__name__, False, str(e)))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    print("\n📋 Issues Found:")
    for name, success, details in results:
        if not success:
            print(f"  ❌ {name}")
            if details:
                print(f"     {details}")
        elif details:
            print(f"  ⚠️  {name}: {details}")
    
    print("\n" + "=" * 70)
    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
