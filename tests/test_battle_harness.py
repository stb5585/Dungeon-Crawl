#!/usr/bin/env python3
"""
BattleEngineHarness tests.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_harness_runs_single_turn(monkeypatch):
    from tests.test_framework import TestGameState
    from tests.combat_harness import BattleEngineHarness
    import src.core.combat.battle_engine as battle_engine

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

    harness = BattleEngineHarness(
        player,
        enemy,
        player_actions=[("Attack", None)],
    )
    harness.start()

    monkeypatch.setattr(battle_engine.random, "randint", lambda _a, _b: 1)

    def weapon_damage(target, **_kwargs):
        target.health.current -= 5
        return "Hit for 5 damage.\n", True, 5

    monkeypatch.setattr(player, "weapon_damage", weapon_damage)

    outcome = harness.run_turn()
    assert outcome.action == "Attack"
    assert "Hit for 5 damage" in outcome.result.message
