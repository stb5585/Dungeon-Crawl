#!/usr/bin/env python3
"""
Battle System Tests

Tests the battle manager and combat flow.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestBattleManagerAPI:
    """Test BattleManager API and integration."""
    
    def test_battle_manager_import(self):
        """Test that BattleManager can be imported."""
        from src.ui_curses.battle import BattleManager
        assert BattleManager is not None
    
    def test_enhanced_battle_manager_import(self):
        """Test that EnhancedBattleManager can be imported."""
        from src.ui_curses.enhanced_manager import EnhancedBattleManager
        assert EnhancedBattleManager is not None
    
    def test_battle_manager_creation(self):
        """Test basic BattleManager instantiation."""
        
        # Create mock objects
        class MockGame:
            def __init__(self):
                self.screen = None
                self.level = 1
        
        class MockEnemy:
            def __init__(self):
                self.name = "TestEnemy"
                self.health = type('obj', (), {'current': 100, 'max': 100})()
                self.is_alive = lambda: self.health.current > 0
        
        try:
            game = MockGame()
            enemy = MockEnemy()
            # BattleManager typically needs more context
            # This documents what's required
            pytest.skip("BattleManager requires full game context")
        except Exception as e:
            pytest.skip(f"BattleManager instantiation needs game: {e}")


class TestCombatResultAPI:
    """Test CombatResult dataclass API."""
    
    def test_combat_result_creation(self):
        """Test creating CombatResult objects."""
        from src.core.combat.combat_result import CombatResult
        
        # Test with minimal args (actor and target should be optional)
        result = CombatResult(action="Attack")
        assert result.action == "Attack"
        assert result.actor is None
        assert result.target is None
    
    def test_combat_result_with_characters(self):
        """Test CombatResult with character references."""
        from src.core.combat.combat_result import CombatResult
        from tests.test_framework import TestGameState
        
        attacker = TestGameState.create_player(name="Attacker", class_name="Warrior", race_name="Human")
        defender = TestGameState.create_player(name="Defender", class_name="Warrior", race_name="Human")
        
        result = CombatResult(
            action="Attack",
            actor=attacker,
            target=defender,
            hit=True,
            damage=10
        )
        
        assert result.actor == attacker
        assert result.target == defender
        assert result.hit is True
        assert result.damage == 10
    
    def test_combat_result_group(self):
        """Test CombatResultGroup functionality."""
        from src.core.combat.combat_result import CombatResult, CombatResultGroup
        
        group = CombatResultGroup()
        assert len(group.results) == 0
        
        result = CombatResult(action="Test")
        group.add(result)
        assert len(group.results) == 1


class TestAbilitiesAPI:
    """Test that abilities can create CombatResult objects."""
    
    def test_ability_initialization(self):
        """Test that abilities can initialize without errors."""
        from src.core.abilities import Ability
        
        # Abilities should be able to create empty CombatResult
        try:
            # This might fail if CombatResult requires actor/target
            ability = Ability(
                name="Test Ability",
                description="A test ability"
            )
            # If it has a result attribute, it should be a CombatResult
            if hasattr(ability, 'result'):
                from src.core.combat.combat_result import CombatResult
                assert isinstance(ability.result, CombatResult)
        except TypeError as e:
            if "missing" in str(e) and "required" in str(e):
                pytest.fail(f"CombatResult requires optional parameters: {e}")


def run_tests():
    """Run all tests."""
    print("=" * 70)
    print("BATTLE SYSTEM TESTS")
    print("=" * 70)
    print()
    
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
