#!/usr/bin/env python3
"""
Quick test script for the new shop GUI interface.
"""

import os
import sys
from pathlib import Path

import pygame

sys.path.insert(0, str(Path(__file__).parents[2]))

from src.ui_pygame.gui.shops import ShopManager
from src.ui_pygame.presentation.pygame_presenter import PygamePresenter
from tests.test_framework import TestGameState


def test_shop():
    """Test the shop interface."""
    # Create a test player
    player = TestGameState.create_player(
        name="TestShopPlayer",
        class_name="Mage",
        level=15,
        gold=5000
    )
    
    # Initialize pygame
    pygame.init()
    presenter = PygamePresenter()
    
    # Create shop manager
    shop_manager = ShopManager(presenter, player)
    
    # Just test that the shop manager can be created successfully
    # Note: visit_alchemist() etc. are interactive and require GUI interaction
    print("Shop manager created successfully!")
    print(f"Player gold: {player.gold}")
    print(f"Player level: {player.level.level}")
    
    # Test that shop manager has the expected methods
    assert hasattr(shop_manager, 'visit_alchemist'), "Missing visit_alchemist method"
    assert hasattr(shop_manager, 'visit_blacksmith'), "Missing visit_blacksmith method"
    assert hasattr(shop_manager, 'visit_jeweler'), "Missing visit_jeweler method"
    
    pygame.quit()
    print("Shop test complete!")
    print("Note: To test shop interactively, run the game and visit shops in-game.")


if __name__ == "__main__":
    test_shop()
