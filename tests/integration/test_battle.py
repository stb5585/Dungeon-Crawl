#!/usr/bin/env python3
"""
Battle System Tests

Tests the battle manager and combat flow.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

import pytest
import json
from dataclasses import dataclass
from types import SimpleNamespace


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
        """Test basic BattleManager instantiation with minimal game context."""
        from src.ui_curses.battle import BattleManager
        from tests.test_framework import TestGameState

        class MockGame:
            def __init__(self, player):
                self.screen = None
                self.level = 1
                self.player_char = player

        class MockTile:
            def __init__(self, enemy):
                self.enemy = enemy
                self.defeated = False

            def available_actions(self, _player):
                return ["Attack", "Flee"]

        player = TestGameState.create_player(
            name="Hero",
            class_name="Warrior",
            race_name="Human",
            level=5,
        )
        enemy = TestGameState.create_player(
            name="Goblin",
            class_name="Warrior",
            race_name="Human",
            level=3,
        )
        enemy.enemy_typ = "TestEnemy"

        tile = MockTile(enemy)
        player.world_dict[(player.location_x, player.location_y, player.location_z)] = tile
        game = MockGame(player)

        manager = BattleManager(game, enemy)

        assert manager.player_char == player
        assert manager.enemy == enemy
        assert manager.tile == tile


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
        enemy.experience = 10
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
        assert player.gameplay_stats["flees"] == 1

    def test_process_victory_updates_enemies_defeated_stat(self, monkeypatch):
        engine, player, enemy, _tile = self._make_engine()

        monkeypatch.setattr(player, "loot", lambda *_args, **_kwargs: "")
        monkeypatch.setattr(player, "quests", lambda *_args, **_kwargs: "")

        engine._process_victory()

        assert player.gameplay_stats["enemies_defeated"] == 1

    def test_process_defeat_updates_deaths_stat(self, monkeypatch):
        engine, player, enemy, _tile = self._make_engine()

        monkeypatch.setattr(player, "to_town", lambda: None)
        monkeypatch.setattr(player, "effects", lambda end=False: "")
        monkeypatch.setattr(enemy, "effects", lambda end=False: "")

        engine._process_defeat()

        assert player.gameplay_stats["deaths"] == 1

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

    def test_pre_turn_marks_attacker_dead_from_effects(self, monkeypatch):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy

        def lethal_effects():
            player.health.current = 0
            return "Poison deals 999 damage.\n"

        monkeypatch.setattr(player, "effects", lethal_effects)

        pre = engine.pre_turn()

        assert pre.can_act is False
        assert pre.died_from_effects is True

    def test_pre_turn_handles_inactive_attacker(self, monkeypatch):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy

        monkeypatch.setattr(player, "effects", lambda: "")
        monkeypatch.setattr(player, "check_active", lambda: (False, "Stunned.\n"))

        pre = engine.pre_turn()

        assert pre.can_act is False
        assert pre.inactive_reason == "Stunned.\n"

    def test_battle_continues_stops_when_enemy_dead(self):
        engine, _player, enemy, _tile = self._make_engine()
        enemy.health.current = 0

        assert engine.battle_continues() is False

    def test_get_enemy_action_falls_back_to_attack_on_ai_error(self):
        engine, player, enemy, _tile = self._make_engine()

        enemy.options = lambda *_args: (_ for _ in ()).throw(RuntimeError("ai blew up"))

        assert engine.get_enemy_action() == ("Attack", None)

    def test_is_player_turn_counts_active_summon_as_player_turn(self):
        engine, player, enemy, _tile = self._make_engine()
        engine.summon_active = True
        engine.summon = enemy
        engine.attacker = enemy

        assert engine.is_player_turn() is True

    def test_get_forced_action_returns_berserk_attack(self):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        player.status_effects["Berserk"].active = True

        forced = engine.get_forced_action()

        assert forced.action == "Attack"

    def test_get_forced_action_cancels_jump_when_incapacitated(self):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        player.class_effects["Jump"].active = True
        player.spellbook["Skills"]["Jump"] = SimpleNamespace(
            name="Jump",
            cancel_charge=lambda _user: "Jump cancelled.\n"
        )
        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(player, "incapacitated", lambda: True)
        try:
            forced = engine.get_forced_action()
        finally:
            monkeypatch.undo()

        assert forced.action == "Cancelled"
        assert forced.cancel_message == "Jump cancelled.\n"
        assert player.class_effects["Jump"].active is False

    def test_get_forced_action_allows_unstoppable_jump_when_incapacitated(self):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        player.class_effects["Jump"].active = True
        player.spellbook["Skills"]["Jump"] = SimpleNamespace(
            name="Jump",
            modifications={"Unstoppable": True},
            cancel_charge=lambda _user: "Jump cancelled.\n",
        )
        player.incapacitated = lambda: True

        forced = engine.get_forced_action()

        assert forced.action == "Use Skill"
        assert forced.choice == "Jump"
        assert player.class_effects["Jump"].active is False

    def test_get_forced_action_returns_jump_skill_when_ready(self):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        player.class_effects["Jump"].active = True
        player.spellbook["Skills"]["Sky Jump"] = SimpleNamespace()
        player.incapacitated = lambda: False

        forced = engine.get_forced_action()

        assert forced.action == "Use Skill"
        assert forced.choice == "Sky Jump"

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

    def test_execute_cancelled_action_does_nothing(self):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy

        result = engine.execute_action("Cancelled")

        assert result.message == "Hero does nothing.\n"

    def test_execute_pickup_weapon_clears_disarm(self):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        player.physical_effects["Disarm"].active = True

        result = engine.execute_action("Pickup Weapon")

        assert player.physical_effects["Disarm"].active is False
        assert "picks up their weapon" in result.message

    def test_execute_defend_uses_defensive_stance(self, monkeypatch):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy

        monkeypatch.setattr(player, "enter_defensive_stance", lambda duration, source: f"{source}:{duration}")

        result = engine.execute_action("Defend")

        assert result.message == "Defend:2"

    def test_execute_spell_handles_suppressed_invalid_and_successful_casts(self):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy

        player.abilities_suppressed = lambda: True
        assert "cannot cast spells because of silence" in engine.execute_action("Cast Spell", "Missing").message

        player.abilities_suppressed = lambda: False
        assert "fumbles the spell" in engine.execute_action("Cast Spell", "Missing").message

        class DummySpell:
            cost = 3

            def cast(self, _user, target=None):
                return f"Hit {target.name}.\n"

        player.spellbook["Spells"]["Test Spell"] = DummySpell()
        player.mana.current = 2
        assert "does not have enough mana" in engine.execute_action("Cast Spell", "Test Spell").message

        player.mana.current = 10
        cast_result = engine.execute_action("Cast Spell", "Test Spell")
        assert "Hero casts Test Spell" in cast_result.message
        assert "Hit Goblin" in cast_result.message

    def test_execute_skill_handles_alias_totem_and_recall(self, monkeypatch):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy

        class DummySkill:
            def __init__(self, name, cost=0):
                self.name = name
                self.cost = cost

            def use(self, _user, target=None, **_kwargs):
                return f"{self.name} on {target.name if target else 'nobody'}.\n"

        player.spellbook["Skills"]["Mana Shield"] = DummySkill("Mana Shield")
        assert "uses Mana Shield" in engine.execute_action("Use Skill", "Remove Shield").message

        player.spellbook["Skills"]["Totem"] = DummySkill("Totem")
        assert "Totem on Goblin" in engine.execute_action("Totem").message

        summon = TestBattleEngineBasics._make_engine(self)[2]
        summon.name = "Helper"
        player.summons["Helper"] = summon
        summon_result = engine.execute_action("Summon", "Helper")
        assert summon_result.summon_started is True
        assert summon_result.summon == summon
        assert engine.attacker == summon

        recall_result = engine.execute_action("Recall")
        assert recall_result.summon_recalled is True
        assert "recalls Helper" in recall_result.message

    def test_execute_item_handles_missing_item_and_enemy_scroll_target(self):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy

        assert "fumbles with their items" in engine.execute_action("Use Item").message
        assert "can't find Potion" in engine.execute_action("Use Item", "Potion").message

        target_names = []

        class DummyScroll:
            name = "Fire Scroll"
            subtyp = "Scroll"
            spell = SimpleNamespace(subtyp="Attack")

            def use(self, user, target=None):
                target_names.append(target.name)
                return f"{user.name} uses scroll on {target.name}.\n"

        player.inventory["Fire Scroll"] = [DummyScroll()]

        result = engine.execute_action("Use Item", "Fire Scroll")
        assert "uses scroll on Goblin" in result.message
        assert target_names == ["Goblin"]

    def test_execute_transform_and_unknown_action_fallback(self, monkeypatch):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        monkeypatch.setattr(player, "transform", lambda back=False: "back\n" if back else "forward\n")

        assert engine.execute_action("Transform").message == "forward\n"
        assert engine.execute_action("Untransform").message == "back\n"
        assert engine.execute_action("Mystery").message == "Hero does nothing.\n"

    def test_enemy_charge_does_not_force_player_charge_action(self):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = enemy
        engine.defender = player

        class DummyChargeSkill:
            def __init__(self):
                self.name = "Charge"
                self.cost = 0
                self.charging = False

            def get_charge_time(self):
                return 1

            def use(self, _user, target=None, **_kwargs):
                if not self.charging:
                    self.charging = True
                    return "begins to charge!\n"
                self.charging = False
                return "crashes into the target!\n"

        enemy.spellbook["Skills"]["Charge"] = DummyChargeSkill()

        result = engine.execute_action("Use Skill", choice="Charge")
        assert "begins to charge" in result.message

        engine.swap_turns()
        assert engine.attacker == player
        assert engine.get_forced_action() is None

        engine.swap_turns()
        forced = engine.get_forced_action()
        assert forced is not None
        assert forced.action == "Use Skill"
        assert forced.choice == "Charge"

    def test_end_battle_flee_clears_tile_enemy(self):
        engine, _player, _enemy, tile = self._make_engine()
        engine.flee = True

        outcome = engine.end_battle()
        assert outcome.result == "flee"
        assert tile.enemy is None

    def test_post_turn_handles_special_effects_and_summon_death(self):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy

        enemy.special_effects = lambda _attacker: "Thorns!\n"
        summon = TestBattleEngineBasics._make_engine(self)[2]
        summon.name = "Fallen Ally"
        summon.health.current = 0
        engine.summon_active = True
        engine.summon = summon

        result = engine.post_turn()

        assert "Thorns!\n" in result.messages
        assert result.summon_died is True
        assert engine.summon_active is False

    def test_post_turn_handles_defender_resurrection(self):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy
        enemy.health.current = -1
        enemy.mana.current = 10
        enemy.spellbook["Spells"]["Resurrection"] = SimpleNamespace(
            cast=lambda target: f"{target.name} rises again!\n"
        )

        result = engine.post_turn()

        assert result.defender_died is True
        assert result.resurrected is True
        assert any("rises again" in msg for msg in result.messages)

    def test_post_turn_triggers_behemoth_death_effect(self):
        engine, player, enemy, _tile = self._make_engine()
        engine.attacker = player
        engine.defender = enemy
        enemy.name = "Behemoth"
        enemy.health.current = 0
        enemy.special_effects = lambda _attacker: "Meteor!\n"

        result = engine.post_turn()

        assert "Meteor!\n" in result.messages

    def test_end_battle_victory_marks_boss_tile_and_level_up(self, monkeypatch):
        engine, player, enemy, tile = self._make_engine()
        engine.boss = True
        player.level.exp_to_gain = 0

        monkeypatch.setattr(engine, "_process_victory", lambda: "Victory!\n")

        outcome = engine.end_battle()

        assert outcome.result == "victory"
        assert outcome.winner == player.name
        assert outcome.level_up is True
        assert tile.defeated is True
        assert tile.enemy is None

    def test_end_battle_defeat_reports_enemy_win(self, monkeypatch):
        engine, player, enemy, _tile = self._make_engine()
        player.health.current = 0
        defeat_called = []
        monkeypatch.setattr(engine, "_process_defeat", lambda: defeat_called.append(True))

        outcome = engine.end_battle()

        assert outcome.result == "defeat"
        assert outcome.winner == enemy.name
        assert defeat_called == [True]

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


class TestBattleLogger:
    def test_export_payload_includes_metadata_events_and_summary(self):
        from src.core.combat.battle_logger import BattleLogger
        from tests.test_framework import TestGameState

        player = TestGameState.create_player(name="Hero", class_name="Warrior", race_name="Human", level=7)
        enemy = TestGameState.create_player(name="Goblin", class_name="Warrior", race_name="Human", level=3)
        enemy.enemy_typ = "TestEnemy"

        logger = BattleLogger()
        logger.start_battle(player, enemy, initiative=True, boss=False)
        logger.log_event(
            event_type="Action",
            actor=player,
            target=enemy,
            action="Attack",
            outcome="Hit",
            damage=12,
            flags=["critical"],
        )
        logger.end_battle(result="victory", winner=player.name, boss=False)

        payload = logger.export_payload()

        assert payload["metadata"]["player"]["name"] == "Hero"
        assert payload["events"][0]["damage"] == 12
        assert payload["summary"]["event_count"] == 1
        assert payload["summary"]["total_damage_logged"] == 12
        assert payload["summary"]["result"] == "victory"

    def test_export_json_returns_serialized_payload(self):
        from src.core.combat.battle_logger import BattleLogger
        from tests.test_framework import TestGameState

        player = TestGameState.create_player(name="Hero", class_name="Warrior", race_name="Human", level=5)
        enemy = TestGameState.create_player(name="Slime", class_name="Warrior", race_name="Human", level=2)
        enemy.enemy_typ = "TestEnemy"

        logger = BattleLogger()
        logger.start_battle(player, enemy, initiative=False, boss=True)
        logger.end_battle(result="defeat", winner=enemy.name, boss=True)

        payload = json.loads(logger.export_json())

        assert payload["metadata"]["boss"] is True
        assert payload["summary"]["winner"] == "Slime"

    def test_build_summary_counts_event_types_and_ignores_negative_damage(self):
        from src.core.combat.battle_logger import BattleLogger
        from tests.test_framework import TestGameState

        player = TestGameState.create_player(name="Hero", class_name="Warrior", race_name="Human", level=5)
        enemy = TestGameState.create_player(name="Slime", class_name="Warrior", race_name="Human", level=2)
        enemy.enemy_typ = "TestEnemy"

        logger = BattleLogger()
        logger.start_battle(player, enemy, initiative=True, boss=False)
        logger.log_event("Attack", actor=player, target=enemy, damage=10)
        logger.log_event("Attack", actor=enemy, target=player, damage=-3)
        logger.log_event("Spell", actor=player, target=enemy, damage=None)
        logger.next_turn()
        logger.end_battle(result="victory", winner=player.name, boss=False)

        summary = logger.build_summary()

        assert summary["turns"] == 1
        assert summary["event_count"] == 3
        assert summary["event_types"] == {"Attack": 2, "Spell": 1}
        assert summary["total_damage_logged"] == 10
        assert summary["max_damage_logged"] == 10

    def test_serialize_value_handles_dataclasses_collections_and_objects(self):
        from src.core.combat.battle_logger import BattleLogger

        @dataclass
        class ExampleData:
            value: int
            tags: list[str]

        sample = {
            "data": ExampleData(3, ["alpha"]),
            "items": {1, 2},
            "obj": SimpleNamespace(name="Widget", hidden="ignored"),
        }

        serialized = BattleLogger._serialize_value(sample)

        assert serialized["data"] == {"value": 3, "tags": ["alpha"]}
        assert sorted(serialized["items"]) == [1, 2]
        assert serialized["obj"]["name"] == "Widget"
        assert serialized["obj"]["hidden"] == "ignored"


class TestInitiative:
    def test_encumbered_player_loses_initiative(self):
        from src.core.combat.initiative import determine_initiative
        from tests.test_framework import TestGameState

        player = TestGameState.create_player(name="Hero", class_name="Warrior", race_name="Human")
        enemy = TestGameState.create_player(name="Goblin", class_name="Warrior", race_name="Human")

        player.encumbered = True

        first, second = determine_initiative(player, enemy)

        assert first == enemy
        assert second == player

    def test_shadowcaster_surprise_activates_power_up(self):
        from src.core.combat.initiative import determine_initiative
        from tests.test_framework import TestGameState

        player = TestGameState.create_player(name="Shade", class_name="Shadowcaster", race_name="Human")
        enemy = TestGameState.create_player(name="Guard", class_name="Warrior", race_name="Human")

        player.invisible = True
        enemy.sight = False
        player.power_up = True
        player.class_effects["Power Up"].active = False
        player.class_effects["Power Up"].duration = 0

        first, second = determine_initiative(player, enemy)

        assert first == player
        assert second == enemy
        assert player.class_effects["Power Up"].active is True
        assert player.class_effects["Power Up"].duration == 1

    def test_invisible_enemy_beats_player_without_sight(self):
        from src.core.combat.initiative import determine_initiative
        from tests.test_framework import TestGameState

        player = TestGameState.create_player(name="Hero", class_name="Warrior", race_name="Human")
        enemy = TestGameState.create_player(name="Stalker", class_name="Warrior", race_name="Human")

        player.sight = False
        enemy.invisible = True

        first, second = determine_initiative(player, enemy)

        assert first == enemy
        assert second == player

    def test_weighted_random_branch_uses_speed_and_luck_weights(self, monkeypatch):
        from src.core.combat.initiative import determine_initiative
        from tests.test_framework import TestGameState

        player = TestGameState.create_player(name="Hero", class_name="Warrior", race_name="Human")
        enemy = TestGameState.create_player(name="Goblin", class_name="Warrior", race_name="Human")

        def check_mod(stat, enemy=None, luck_factor=None):
            if stat == "speed":
                return 40 if enemy is not None else 0
            if stat == "luck":
                return 10 if luck_factor == 10 else 0
            raise AssertionError(f"Unexpected stat {stat}")

        player.check_mod = check_mod
        enemy.check_mod = lambda stat, enemy=None, luck_factor=None: 25 if stat == "speed" else 5

        def fake_choices(options, weights):
            assert options == [player, enemy]
            assert weights == [0.625, 0.375]
            return [player]

        monkeypatch.setattr("src.core.combat.initiative.random.choices", fake_choices)

        first, second = determine_initiative(player, enemy)

        assert first == player
        assert second == enemy

    def test_zero_total_weight_falls_back_to_dexterity(self):
        from src.core.combat.initiative import determine_initiative
        from tests.test_framework import TestGameState

        player = TestGameState.create_player(
            name="Hero",
            class_name="Warrior",
            race_name="Human",
            stats={"strength": 20, "intel": 20, "wisdom": 20, "con": 20, "charisma": 20, "dex": 15},
        )
        enemy = TestGameState.create_player(
            name="Goblin",
            class_name="Warrior",
            race_name="Human",
            stats={"strength": 20, "intel": 20, "wisdom": 20, "con": 20, "charisma": 20, "dex": 10},
        )

        player.check_mod = lambda *_args, **_kwargs: 0
        enemy.check_mod = lambda *_args, **_kwargs: 0

        first, second = determine_initiative(player, enemy)

        assert first == player
        assert second == enemy


class TestEventBus:
    def test_subscribe_emit_and_unsubscribe(self):
        from src.core.events.event_bus import EventBus, EventType

        bus = EventBus()
        received = []

        def handler(event):
            received.append(event.data["value"])

        bus.subscribe(EventType.ATTACK, handler)
        bus.subscribe(EventType.ATTACK, handler)
        bus.emit_simple(EventType.ATTACK, {"value": 7})
        bus.unsubscribe(EventType.ATTACK, handler)
        bus.emit_simple(EventType.ATTACK, {"value": 8})

        assert received == [7]

    def test_history_is_bounded_and_filterable(self):
        from src.core.events.event_bus import EventBus, EventType

        bus = EventBus(max_history=2)
        bus.emit_simple(EventType.ATTACK, {"turn": 1})
        bus.emit_simple(EventType.DEFEND, {"turn": 2})
        bus.emit_simple(EventType.ATTACK, {"turn": 3})

        history = bus.get_history()

        assert len(history) == 2
        assert [event.type for event in history] == [EventType.DEFEND, EventType.ATTACK]
        assert [event.data["turn"] for event in bus.get_history(EventType.ATTACK)] == [3]

    def test_disable_prevents_callbacks_and_history_growth(self):
        from src.core.events.event_bus import EventBus, EventType

        bus = EventBus()
        received = []
        bus.subscribe(EventType.ATTACK, lambda event: received.append(event))

        bus.disable()
        bus.emit_simple(EventType.ATTACK, {"value": 1})
        bus.enable()
        bus.emit_simple(EventType.ATTACK, {"value": 2})

        assert len(received) == 1
        assert received[0].data["value"] == 2
        assert len(bus.get_history()) == 1

    def test_emit_continues_after_callback_error(self, capsys):
        from src.core.events.event_bus import EventBus, EventType

        bus = EventBus()
        received = []

        def broken(_event):
            raise RuntimeError("boom")

        def healthy(event):
            received.append(event.type)

        bus.subscribe(EventType.ATTACK, broken)
        bus.subscribe(EventType.ATTACK, healthy)

        bus.emit_simple(EventType.ATTACK, {"value": 1})

        captured = capsys.readouterr()
        assert "Error in event callback: boom" in captured.out
        assert received == [EventType.ATTACK]

    def test_global_bus_helpers_reset_and_event_factories_populate_data(self):
        from src.core.combat.combat_result import CombatResult
        from src.core.events.event_bus import (
            EventType,
            create_combat_event,
            create_ui_event,
            get_event_bus,
            reset_event_bus,
        )
        from tests.test_framework import TestGameState

        player = TestGameState.create_player(name="Hero", class_name="Warrior", race_name="Human")
        enemy = TestGameState.create_player(name="Goblin", class_name="Warrior", race_name="Human")
        result = CombatResult(action="Attack", damage=9)

        combat_event = create_combat_event(EventType.ATTACK, actor=player, target=enemy, result=result, round=1)
        ui_event = create_ui_event(EventType.MESSAGE_DISPLAY, message="Hello", choices=["Yes", "No"], page=2)

        assert combat_event.data["actor"] == "Hero"
        assert combat_event.data["target"] == "Goblin"
        assert combat_event.data["result"]["damage"] == 9
        assert combat_event.data["round"] == 1
        assert ui_event.data == {"page": 2, "message": "Hello", "choices": ["Yes", "No"]}

        first_bus = get_event_bus()
        reset_event_bus()
        second_bus = get_event_bus()

        assert second_bus is not first_bus


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
