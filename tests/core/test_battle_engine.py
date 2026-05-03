#!/usr/bin/env python3
"""Focused regression coverage for the UI-agnostic battle engine."""

from __future__ import annotations

from src.core.combat.battle_engine import BattleEngine
from src.core.enemies import Goblin
from tests.test_framework import TestGameState


class DummyCombatTile:
    def available_actions(self, _player):
        return ["Attack"]


def _make_engine_with_player_attacking():
    player = TestGameState.create_player(name="TestHero", class_name="Warrior", race_name="Human")
    enemy = Goblin()
    engine = BattleEngine(player, enemy, DummyCombatTile())
    engine.attacker = player
    engine.defender = enemy
    return engine, player


class FakeJumpSkill:
    name = "Jump"
    cost = 0

    def __init__(self, *, unstoppable: bool = False):
        self.charging = True
        self.modifications = {"Unstoppable": unstoppable}
        self.use_calls = 0

    def get_charge_time(self):
        return 1

    def use(self, _user, target=None):
        self.use_calls += 1
        self.charging = False
        return f"Jump hits {target.name}.\n"


def test_pre_turn_duration_one_stun_still_skips_current_turn():
    engine, player = _make_engine_with_player_attacking()
    player.status_effects["Stun"].active = True
    player.status_effects["Stun"].duration = 1

    result = engine.pre_turn()

    assert result.can_act is False
    assert "incapacitated" in result.inactive_reason
    assert "no longer stunned" in result.effects_text
    assert player.status_effects["Stun"].active is False


def test_pre_turn_duration_one_sleep_still_skips_current_turn():
    engine, player = _make_engine_with_player_attacking()
    player.status_effects["Sleep"].active = True
    player.status_effects["Sleep"].duration = 1

    result = engine.pre_turn()

    assert result.can_act is False
    assert "incapacitated" in result.inactive_reason
    assert "no longer asleep" in result.effects_text
    assert player.status_effects["Sleep"].active is False


def test_pre_turn_prone_recovery_still_skips_current_turn(monkeypatch):
    engine, player = _make_engine_with_player_attacking()
    player.physical_effects["Prone"].active = True
    player.physical_effects["Prone"].duration = 1
    monkeypatch.setattr("src.core.character.random.randint", lambda *_args: 0)

    result = engine.pre_turn()

    assert result.can_act is False
    assert "incapacitated" in result.inactive_reason
    assert "no longer prone" in result.effects_text
    assert player.physical_effects["Prone"].active is False


def test_resolved_jump_clears_forced_action_and_returns_control():
    engine, player = _make_engine_with_player_attacking()
    jump = FakeJumpSkill()
    player.spellbook["Skills"] = {"Jump": jump}
    player.class_effects["Jump"].active = True

    forced = engine.get_forced_action()
    assert forced is not None
    assert forced.action == "Use Skill"
    assert forced.choice == "Jump"

    result = engine.execute_action(forced.action, forced.choice)

    assert "Jump hits" in result.message
    assert jump.use_calls == 1
    assert jump.charging is False
    assert player.class_effects["Jump"].active is False
    assert engine.get_forced_action() is None


def test_unstoppable_jump_resolves_before_berserk_forced_attack():
    engine, player = _make_engine_with_player_attacking()
    jump = FakeJumpSkill(unstoppable=True)
    player.spellbook["Skills"] = {"Jump": jump}
    player.class_effects["Jump"].active = True
    player.status_effects["Berserk"].active = True
    player.status_effects["Berserk"].duration = 2

    forced = engine.get_forced_action()

    assert forced is not None
    assert forced.action == "Use Skill"
    assert forced.choice == "Jump"
