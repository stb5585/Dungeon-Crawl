"""Regression coverage for owner-relative combat-status durations."""

from __future__ import annotations

from src.core.classes import paladin
from src.core.combat.battle_engine import BattleEngine
from src.core.enemies import Goblin
from tests.test_framework import TestGameState


class _CombatTile:
    def available_actions(self, _player):
        return ["Attack"]


def _engine() -> tuple[BattleEngine, object, Goblin]:
    player = TestGameState.create_player(name="TestHero", class_name="Paladin", race_name="Human")
    enemy = Goblin()
    engine = BattleEngine(player, enemy, _CombatTile())
    return engine, player, enemy


def test_paladin_turn_timers_tick_only_at_the_owner_pre_turn():
    engine, player, enemy = _engine()
    state = paladin.ensure_state(player)
    state["riposte"] = {"turns": 2, "spent": False}

    engine.attacker = enemy
    engine.defender = player
    engine.pre_turn()

    assert paladin.ensure_state(player)["riposte"]["turns"] == 2

    engine.attacker = player
    engine.defender = enemy
    engine.pre_turn()

    assert paladin.ensure_state(player)["riposte"]["turns"] == 1


def test_post_turn_does_not_consume_the_players_paladin_timer():
    engine, player, enemy = _engine()
    state = paladin.ensure_state(player)
    state["challenge"] = {"turns": 2, "spent": False}
    engine.attacker = enemy
    engine.defender = player
    engine._turn_action_committed = True

    engine.post_turn()

    assert paladin.ensure_state(player)["challenge"]["turns"] == 2
