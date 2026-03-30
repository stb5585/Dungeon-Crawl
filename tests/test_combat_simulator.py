#!/usr/bin/env python3
"""
Combat simulator tests (Focus Area 6.3).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_combat_simulator_runs_single_battle():
    from src.core.analytics.combat_simulator import CombatSimulator
    from src.core.enemies import Goblin
    from tests.test_framework import TestGameState

    player = TestGameState.create_player(
        name="Hero",
        class_name="Warrior",
        race_name="Human",
        level=8,
        health=(120, 120),
        mana=(30, 30),
    )
    enemy = Goblin()

    sim = CombatSimulator()
    stats = sim.simulate_battle(player, enemy, max_turns=50, seed=123)

    assert stats.turns > 0
    assert stats.winner in [player.name, enemy.name, "draw"]
    assert isinstance(stats.abilities_used, dict)
    assert isinstance(stats.status_effects_applied, dict)


def test_combat_simulator_run_simulations_with_factories():
    from src.core.analytics.combat_simulator import CombatSimulator
    from src.core.enemies import Goblin
    from tests.test_framework import TestGameState

    def make_player():
        return TestGameState.create_player(
            name="Hero",
            class_name="Warrior",
            race_name="Human",
            level=8,
            health=(120, 120),
            mana=(30, 30),
        )

    def make_enemy():
        return Goblin()

    sim = CombatSimulator()
    report = sim.run_simulations(make_player, make_enemy, iterations=10, seed=999)

    assert report.total_battles == 10
    assert len(report.results) == 10
