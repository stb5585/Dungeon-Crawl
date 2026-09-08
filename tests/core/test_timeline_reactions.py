"""Regression coverage for immediate, bounded timeline reactions."""

from __future__ import annotations

from src.core.combat.battle_engine import BattleEngine
from src.core.combat.reactions import execute_reaction, reaction_result
from src.core.enemies import Goblin
from tests.test_framework import TestGameState


class _CombatTile:
    def available_actions(self, _player):
        return ["Attack"]


def test_reaction_cannot_reenter_through_its_own_result():
    calls: list[str] = []

    @reaction_result
    def resolve_root_result() -> str:
        def resolve_counter() -> str:
            calls.append("counter")
            nested = execute_reaction("counterspell", owner, resolve_counter)
            return "counter" + (nested or "")

        return execute_reaction("counterspell", owner, resolve_counter) or ""

    owner = object()

    assert resolve_root_result() == "counter"
    assert calls == ["counter"]


def test_reaction_can_execute_again_for_a_new_result():
    calls: list[str] = []
    owner = object()

    @reaction_result
    def resolve_root_result() -> str:
        return (
            execute_reaction("counterspell", owner, lambda: calls.append("counter") or "ok") or ""
        )

    assert resolve_root_result() == "ok"
    assert resolve_root_result() == "ok"
    assert calls == ["counter", "counter"]


def test_engine_reaction_runs_once_without_advancing_readiness():
    player = TestGameState.create_player(name="TestHero", class_name="Warrior", race_name="Human")
    engine = BattleEngine(player, Goblin(), _CombatTile())
    engine.start_battle()
    readiness_before = engine.current_readiness
    calls: list[str] = []

    def resolve() -> str:
        calls.append("reaction")
        return "done"

    assert engine._resolve_reaction_once("test", resolve) == "done"
    assert engine._resolve_reaction_once("test", resolve) == ""
    assert calls == ["reaction"]
    assert engine.current_readiness == readiness_before
