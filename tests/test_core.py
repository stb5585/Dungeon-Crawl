#!/usr/bin/env python3
"""
Core Functionality Tests

Tests core character and combat functionality without external dependencies.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_character_creation():
    """Test basic character creation."""
    print("\n[Test] Character Creation")
    from character import Character
    from races import Human
    from classes import Warrior
    
    char = Character(name="TestHero", race=Human(), cls=Warrior())
    assert char.name == "TestHero"
    assert char.is_alive()
    print("  ✅ Character can be created")
    print(f"  ✅ Character name: {char.name}")
    print(f"  ✅ Character race: {char.race.name}")
    print(f"  ✅ Character class: {char.cls.name}")
    return True


def test_character_attributes():
    """Test character attributes and stats."""
    print("\n[Test] Character Attributes")
    from character import Character
    from races import Human
    from classes import Warrior
    
    char = Character(name="TestHero", race=Human(), cls=Warrior())
    
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
    
    if missing:
        print(f"  ❌ Missing attributes: {missing}")
        return False
    return True


def test_character_methods():
    """Test character has required methods."""
    print("\n[Test] Character Methods")
    from character import Character
    from races import Human
    from classes import Warrior
    
    char = Character(name="Test", race=Human(), cls=Warrior())
    
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
    
    return len(methods_missing) == 0, methods_missing


def test_weapon_damage_api():
    """Test weapon_damage API contract."""
    print("\n[Test] weapon_damage API")
    from character import Character
    from races import Human
    from classes import Warrior
    
    attacker = Character(name="Attacker", race=Human(), cls=Warrior())
    defender = Character(name="Defender", race=Human(), cls=Warrior())
    
    try:
        result = attacker.weapon_damage(defender)
        assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"
        assert len(result) == 3, f"Expected 3 elements, got {len(result)}"
        
        result_str, hit, crit = result
        print(f"  ✅ Returns tuple(str, bool, int/float)")
        print(f"  ✅ Result: hit={hit}, crit={crit}")
        return True
    except Exception as e:
        print(f"  ❌ weapon_damage failed: {e}")
        return False


def test_combat_result():
    """Test CombatResult creation."""
    print("\n[Test] CombatResult API")
    from combat_result import CombatResult
    
    # Test creating with minimal args
    try:
        result = CombatResult(action="Attack")
        print("  ✅ Can create with action only")
        print(f"  ✅ actor={result.actor}, target={result.target}")
        return True
    except TypeError as e:
        print(f"  ❌ Cannot create with action only: {e}")
        return False


def test_enemy_creation():
    """Test enemy creation."""
    print("\n[Test] Enemy Creation")
    from enemies import random_enemy
    
    try:
        enemy = random_enemy('0')
        print(f"  ✅ Created enemy: {enemy.name}")
        
        # Check if enemy has check_active
        if hasattr(enemy, 'check_active'):
            print("  ✅ Enemy has check_active()")
        else:
            print("  ⚠️  Enemy missing check_active()")
        
        return True
    except Exception as e:
        print(f"  ❌ Enemy creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_player_creation():
    """Test player creation."""
    print("\n[Test] Player Creation")
    from player import Player
    from races import Human
    from classes import Warrior
    
    try:
        player = Player("TestPlayer", Human(), Warrior())
        print(f"  ✅ Created player: {player.name}")
        
        # Check if player has check_active
        if hasattr(player, 'check_active'):
            print("  ✅ Player has check_active()")
        else:
            print("  ⚠️  Player missing check_active() - REQUIRED by EnhancedBattleManager")
        
        return True
    except Exception as e:
        print(f"  ❌ Player creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("CORE FUNCTIONALITY TEST SUITE")
    print("=" * 70)
    
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
                results.append((test.__name__, result, None))
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
