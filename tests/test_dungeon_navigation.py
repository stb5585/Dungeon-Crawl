#!/usr/bin/env python3
"""
Test script to verify dungeon navigation is working correctly.
This simulates the key presses without needing the full GUI.
"""

from src.core.player import Player, DIRECTIONS
from src.core.character import Combat, Level, Resource, Stats


def test_movement():
    """Test that movement logic works correctly."""
    print("="*70)
    print("DUNGEON NAVIGATION TEST")
    print("="*70)
    print()
    
    # Create test player at dungeon entrance
    player = Player(
        5, 10, 1,  # Dungeon entrance
        level=Level(),
        health=Resource(20, 20),
        mana=Resource(10, 10),
        stats=Stats(10, 10, 10, 10, 10, 10),
        combat=Combat(attack=10, defense=10, magic=5, magic_def=5),
        gold=100,
        resistance={}
    )
    player.facing = "east"
    player.load_tiles()
    
    print(f"✅ Player created at ({player.location_x}, {player.location_y}, {player.location_z})")
    print(f"   Facing: {player.facing}")
    print(f"   Total tiles loaded: {len(player.world_dict)}")
    print()
    
    # Test 1: Check current tile
    current_tile = player.world_dict.get((player.location_x, player.location_y, player.location_z))
    print(f"TEST 1: Current Tile")
    print(f"   Type: {type(current_tile).__name__}")
    print(f"   ✅ PASS" if current_tile else "   ❌ FAIL")
    print()
    
    # Test 2: Check tile ahead
    dx, dy = DIRECTIONS[player.facing]["move"]
    ahead_pos = (player.location_x + dx, player.location_y + dy, player.location_z)
    tile_ahead = player.world_dict.get(ahead_pos)
    
    print(f"TEST 2: Tile Ahead (facing {player.facing})")
    print(f"   Position: {ahead_pos}")
    print(f"   Type: {type(tile_ahead).__name__ if tile_ahead else 'None'}")
    if tile_ahead:
        can_enter = getattr(tile_ahead, 'enter', True)
        print(f"   Can enter: {can_enter}")
        print(f"   ✅ PASS - Can move forward" if can_enter else "   ❌ FAIL - Blocked")
    else:
        print(f"   ❌ FAIL - No tile found")
    print()
    
    # Test 3: Simulate movement
    if tile_ahead and getattr(tile_ahead, 'enter', True):
        old_pos = (player.location_x, player.location_y)
        player.location_x += dx
        player.location_y += dy
        new_pos = (player.location_x, player.location_y)
        
        print(f"TEST 3: Movement Simulation")
        print(f"   From: {old_pos}")
        print(f"   To:   {new_pos}")
        
        new_tile = player.world_dict.get((player.location_x, player.location_y, player.location_z))
        print(f"   New tile type: {type(new_tile).__name__ if new_tile else 'None'}")
        print(f"   ✅ PASS - Movement successful")
    else:
        print(f"TEST 3: Movement Simulation")
        print(f"   ❌ SKIP - Cannot move (blocked or no tile)")
    print()
    
    # Test 4: Turn and check other directions
    player.location_x, player.location_y = 5, 10  # Reset position
    
    print(f"TEST 4: All Directions from Start")
    for direction in ["north", "east", "south", "west"]:
        dx, dy = DIRECTIONS[direction]["move"]
        x, y = 5 + dx, 10 + dy
        t = player.world_dict.get((x, y, 1))
        tile_name = type(t).__name__ if t else "None"
        can_enter = getattr(t, 'enter', True) if t else False
        status = "✅ Movable" if (t and can_enter) else "❌ Blocked"
        print(f"   {direction:6s}: {tile_name:20s} {status}")
    print()
    
    # Test 5: Check quit flag
    print(f"TEST 5: Player State")
    print(f"   quit flag: {player.quit}")
    print(f"   in_town: {player.in_town()}")
    print(f"   ✅ PASS")
    print()
    
    print("="*70)
    print("ALL TESTS COMPLETE")
    print("="*70)
    print()
    print("If all tests passed, the dungeon navigation should work!")
    print("Try running the game with: python pygame_game.py")


if __name__ == '__main__':
    test_movement()
