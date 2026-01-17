#!/usr/bin/env python3
"""
Quick test script for the new shop GUI interface.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pygame
from test_framework import TestGameState
from presentation.pygame_presenter import PygamePresenter
from gui.shops import ShopManager

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
    
    # Visit the alchemist
    print("Opening Alchemist shop...")
    shop_manager.visit_alchemist()
    
    pygame.quit()
    print("Shop test complete!")

if __name__ == "__main__":
    test_shop()
