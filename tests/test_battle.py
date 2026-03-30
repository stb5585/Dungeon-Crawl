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


class TestBattleEngineBasics:
    """Core BattleEngine behavior for basic combat flow."""

    class MockTile:
        def __init__(self, enemy=None):
            self.enemy = enemy
            self.defeated = False

        def available_actions(self, _player):
            return ["Attack", "Flee", "Use Skill"]

        def __str__(self):
            return "TestTile"

    def _make_engine(self):
        from src.core.combat.battle_engine import BattleEngine
        from tests.test_framework import TestGameState

        player = TestGameState.create_player(
            name="Hero",
            class_name="Warrior",
            race_name="Human",
            level=5,
            health=(50, 50),
            mana=(10, 10),
        )
        enemy = TestGameState.create_player(
            name="Goblin",
            class_name="Warrior",
            race_name="Human",
            level=3,
            health=(20, 20),
            mana=(1, 0),
        )
        # BattleLogger expects enemy_typ and non-zero mana max for ratio logging.
        enemy.enemy_typ = "TestEnemy"
        tile = self.MockTile(enemy=enemy)
        engine = BattleEngine(player=player, enemy=enemy, tile=tile)
        return engine, player, enemy, tile

    def test_start_battle_sets_attacker_and_defender(self, monkeypatch):
        import src.core.combat.battle_engine as battle_engine

        engine, player, enemy, _tile = self._make_engine()

        monkeypatch.setattr(
            battle_engine,
            "determine_initiative",
            lambda _p, _e: (player, enemy),
        )

        attacker, defender = engine.start_battle()
        assert attacker == player
        assert defender == enemy
        assert engine.attacker == player
        assert engine.defender == enemy

    def test_execute_attack_uses_weapon_damage(self, monkeypatch):
        import src.core.combat.battle_engine as battle_engine

        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy

        monkeypatch.setattr(battle_engine.random, "randint", lambda _a, _b: 1)

        def weapon_damage(target, **_kwargs):
            damage = 7
            target.health.current -= damage
            return "Hit for 7 damage.\n", True, damage

        monkeypatch.setattr(player, "weapon_damage", weapon_damage)

        result = engine.execute_action("Attack")
        assert "Hit for 7 damage" in result.message
        assert enemy.health.current == 13

    def test_execute_flee_sets_flee_flag(self, monkeypatch):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy

        monkeypatch.setattr(player, "flee", lambda _t, smoke=False: (True, "Fled.\n"))

        result = engine.execute_action("Flee")
        assert engine.flee is True
        assert result.fled is True
        assert "Fled" in result.message

    def test_pre_turn_parses_shield_explosion_damage(self, monkeypatch):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy

        enemy.health.current = 10
        monkeypatch.setattr(
            player, "effects", lambda: "Exploding shield deals 5 damage.\n"
        )
        pre = engine.pre_turn()
        assert pre.shield_explosion_damage == 5
        assert enemy.health.current == 5

    def test_charging_skill_can_continue_after_paying_mana_cost(self, monkeypatch):
        """
        Regression: charging skills pay mana up-front. The engine must allow the
        follow-up turns even if mana is now 0, otherwise the charge can never
        resolve.
        """
        from src.core import abilities

        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy

        # Add Charge to the player's skillbook. Give exactly enough mana to start.
        player.spellbook["Skills"]["Charge"] = abilities.Charge()
        player.mana.max = 10
        player.mana.current = 10

        def weapon_damage(target, **_kwargs):
            damage = 5
            target.health.current -= damage
            return "Hit for 5 damage.\n", True, 1

        monkeypatch.setattr(player, "weapon_damage", weapon_damage)

        # Turn 1: start charging (mana becomes 0).
        res1 = engine.execute_action("Use Skill", choice="Charge")
        assert player.mana.current == 0
        assert "is lowering their head" in res1.message or "begins to charge" in res1.message

        # Turn 2: resolve charge with mana == 0 (should be allowed).
        res2 = engine.execute_action("Use Skill", choice="Charge")
        assert "Hit for 5 damage" in res2.message

    def test_execute_skill_calls_skill_use(self):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy

        class DummySkill:
            def __init__(self):
                self.name = "Test Skill"
                self.cost = 0

            def use(self, _user, target=None, **_kwargs):
                return "Skill used.\n"

        player.spellbook["Skills"]["Test Skill"] = DummySkill()

        result = engine.execute_action("Use Skill", choice="Test Skill")
        assert "uses Test Skill" in result.message
        assert "Skill used" in result.message

    def test_end_battle_flee_clears_tile_enemy(self):
        engine, _player, _enemy, tile = self._make_engine()
        engine.flee = True

        outcome = engine.end_battle()
        assert outcome.result == "flee"
        assert tile.enemy is None

    def test_silence_prevents_summoning(self):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy

        player.status_effects["Silence"].active = True
        player.status_effects["Silence"].duration = 2
        player.summons["TestSummon"] = enemy

        result = engine.execute_action("Summon", choice="TestSummon")
        assert "silenced" in result.message.lower()
        assert result.summon_started is False


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
