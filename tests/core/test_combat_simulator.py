#!/usr/bin/env python3
"""
Combat simulator tests (Focus Area 6.3).
"""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parents[2]))


def _make_stat(
    *,
    winner="Hero",
    loser="Goblin",
    winner_class="Warrior",
    loser_class="Rogue",
    turns=5,
    hp_remaining=40,
    hp_max=100,
    abilities=None,
    statuses=None,
):
    from src.core.analytics.combat_simulator import CombatStats

    return CombatStats(
        winner=winner,
        loser=loser,
        winner_class=winner_class,
        loser_class=loser_class,
        winner_level=10,
        loser_level=9,
        turns=turns,
        winner_hp_remaining=hp_remaining,
        winner_hp_max=hp_max,
        total_damage_dealt=25,
        total_damage_taken=10,
        abilities_used=abilities or {},
        status_effects_applied=statuses or {},
    )


def test_combat_level_handles_nested_plain_and_invalid_levels():
    from src.core.analytics.combat_simulator import _combat_level

    assert _combat_level(SimpleNamespace(level=SimpleNamespace(level=7))) == 7
    assert _combat_level(SimpleNamespace(level=5)) == 5
    assert _combat_level(SimpleNamespace(level="bad")) == 1
    assert _combat_level(object()) == 1


def test_combat_stats_properties_cover_zero_and_close_fights():
    zero_hp = _make_stat(hp_remaining=0, hp_max=0)
    close_fight = _make_stat(hp_remaining=20, hp_max=100)
    safe_win = _make_stat(hp_remaining=40, hp_max=100)

    assert zero_hp.hp_remaining_percent == 0.0
    assert zero_hp.was_close is True
    assert close_fight.was_close is True
    assert safe_win.was_close is False


def test_balance_report_empty_results_return_zero_metrics():
    from src.core.analytics.combat_simulator import BalanceReport

    report = BalanceReport(total_battles=0, results=[])

    assert report.win_rates == {}
    assert report.average_turns == 0.0
    assert report.median_turns == 0.0
    assert report.close_fight_rate == 0.0
    assert report.stomp_rate == 0.0
    assert report.get_ability_usage() == {}
    assert report.get_status_effect_frequency() == {}
    assert report.identify_outliers() == {"overpowered": [], "underpowered": []}


def test_balance_report_aggregates_metrics_and_usage():
    from src.core.analytics.combat_simulator import BalanceReport

    results = [
        _make_stat(
            winner_class="Warrior",
            loser_class="Mage",
            turns=3,
            hp_remaining=20,
            hp_max=100,
            abilities={"Attack": 2, "Slash": 1},
            statuses={"Bleed": 1},
        ),
        _make_stat(
            winner_class="Mage",
            loser_class="Warrior",
            turns=7,
            hp_remaining=95,
            hp_max=100,
            abilities={"Fireball": 3, "Attack": 1},
            statuses={"Burn": 2},
        ),
        _make_stat(
            winner_class="Warrior",
            loser_class="Mage",
            turns=5,
            hp_remaining=92,
            hp_max=100,
            abilities={"Attack": 1},
            statuses={"Bleed": 2},
        ),
    ]

    report = BalanceReport(total_battles=3, results=results)

    assert report.win_rates == {"Warrior": 66.66666666666666, "Mage": 33.33333333333333}
    assert report.average_turns == 5
    assert report.median_turns == 5
    assert report.close_fight_rate == (1 / 3) * 100
    assert report.stomp_rate == (2 / 3) * 100
    assert report.get_ability_usage() == {"Attack": 4, "Slash": 1, "Fireball": 3}
    assert report.get_most_used_abilities(2) == [("Attack", 4), ("Fireball", 3)]
    assert report.get_status_effect_frequency() == {"Bleed": 3, "Burn": 2}


def test_balance_report_identifies_manual_outliers_and_summary_mentions_sections(monkeypatch):
    from src.core.analytics.combat_simulator import BalanceReport

    report = BalanceReport(total_battles=4, results=[_make_stat()])
    report._win_rates = {
        "Champion": 90.0,
        "Balanced": 50.0,
        "Struggler": 10.0,
    }
    report.results = [
        _make_stat(winner_class="Champion", loser_class="Balanced", abilities={"Meteor": 4}),
        _make_stat(winner_class="Balanced", loser_class="Struggler", abilities={"Slash": 2}),
    ]

    outliers = report.identify_outliers(threshold=0.5)
    monkeypatch.setattr(
        report,
        "identify_outliers",
        lambda threshold=2.0: {
            "overpowered": [("Champion", 90.0, 1.0)],
            "underpowered": [("Struggler", 10.0, -1.0)],
        },
    )
    summary = report.generate_summary()

    assert outliers["overpowered"][0][0] == "Champion"
    assert outliers["underpowered"][0][0] == "Struggler"
    assert "COMBAT BALANCE REPORT" in summary
    assert "Overpowered Classes" in summary
    assert "Underpowered Classes" in summary
    assert "Most Used Abilities" in summary


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


def test_combat_simulator_can_return_draw_when_no_turns_are_run():
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
    stats = sim.simulate_battle(player, enemy, max_turns=0, seed=123)

    assert stats.winner == "draw"
    assert stats.loser == "draw"
    assert stats.turns == 0


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


def test_run_simulations_seeds_each_iteration_and_extends_results(monkeypatch):
    from src.core.analytics.combat_simulator import CombatSimulator

    sim = CombatSimulator()
    calls = []

    def fake_simulate_battle(char1, char2, seed=None):
        calls.append((char1["id"], char2["id"], seed))
        return _make_stat(winner=f"Hero-{seed}", loser="Enemy")

    monkeypatch.setattr(sim, "simulate_battle", fake_simulate_battle)

    counter = {"value": 0}

    def make_player():
        counter["value"] += 1
        return {"id": f"player-{counter['value']}"}

    def make_enemy():
        counter["value"] += 1
        return {"id": f"enemy-{counter['value']}"}

    report = sim.run_simulations(make_player, make_enemy, iterations=3, seed=50)

    assert [seed for _char1, _char2, seed in calls] == [50, 51, 52]
    assert report.total_battles == 3
    assert len(report.results) == 3
    assert len(sim.results) == 3
