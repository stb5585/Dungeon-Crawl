#!/usr/bin/env python3
"""
Advanced coverage for the combat simulator analytics module.

This file is intentionally self-contained and only targets
src.core.analytics.combat_simulator.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

from tests.test_framework import TestGameState


def _make_stats(
    *,
    winner="Hero",
    loser="Goblin",
    winner_class="Warrior",
    loser_class="Mage",
    turns=3,
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


def _make_player(
    *,
    name="Hero",
    class_name="Warrior",
    race_name="Human",
    level=10,
    health=(100, 100),
    mana=(50, 50),
):
    return TestGameState.create_player(
        name=name,
        class_name=class_name,
        race_name=race_name,
        level=level,
        health=health,
        mana=mana,
    )


def _make_damage_effect(name="DamagePulse"):
    return type(name, (), {})()


def _make_spell(name, *, cost=0, subtyp="Attack", effects=None, weapon=False):
    return SimpleNamespace(
        name=name,
        cost=cost,
        subtyp=subtyp,
        weapon=weapon,
        passive=False,
        combat=True,
        typ="Spell",
        _effects=list(effects or []),
    )


def _make_skill(name, *, cost=0, subtyp="Attack", effects=None, weapon=False):
    return SimpleNamespace(
        name=name,
        cost=cost,
        subtyp=subtyp,
        weapon=weapon,
        passive=False,
        combat=True,
        typ="Skill",
        _effects=list(effects or []),
    )


def _make_tile(actions=None):
    class Tile:
        def __init__(self):
            self.enemy = None
            self.defeated = False
            self.actions = list(actions or ["Attack", "Cast Spell", "Use Skill", "Defend", "Use Item"])

        def available_actions(self, _player):
            return list(self.actions)

        def __str__(self):
            return "SimTile"

    return Tile()


def _make_fake_engine(*, player_turn=True, start_events=()):
    class FakeBattleEngine:
        last_instance = None

        def __init__(self, player, enemy, tile, logger=None):
            self.player = player
            self.enemy = enemy
            self.tile = tile
            self.logger = logger
            self.attacker = player if player_turn else enemy
            self.defender = enemy if player_turn else player
            self.available_actions = tile.available_actions(player)
            self._event_bus = None
            self._running = True
            self.actions = []
            self.boss = False
            self.summon_active = False
            self.summon = None
            FakeBattleEngine.last_instance = self

        def start_battle(self):
            from src.core.events.event_bus import get_event_bus

            self._event_bus = get_event_bus()
            for event in start_events:
                self._event_bus.emit(event)
            return self.attacker, self.defender

        def battle_continues(self):
            return self._running

        def pre_turn(self):
            return SimpleNamespace(can_act=True)

        def get_forced_action(self):
            return None

        def is_player_turn(self):
            return self.attacker == self.player

        def get_enemy_action(self):
            return "Attack", None

        def execute_action(self, action, choice):
            self.actions.append((action, choice))
            self._running = False
            return SimpleNamespace(message=f"{action}:{choice}")

        def companion_turn(self):
            return ""

        def post_turn(self):
            return SimpleNamespace()

        def swap_turns(self):
            self.attacker, self.defender = self.defender, self.attacker

    return FakeBattleEngine


def test_combat_level_handles_property_errors_and_plain_values():
    from src.core.analytics.combat_simulator import _combat_level

    class BrokenLevel:
        @property
        def level(self):
            raise RuntimeError("boom")

    assert _combat_level(SimpleNamespace(level=BrokenLevel())) == 1
    assert _combat_level(SimpleNamespace(level="9")) == 9
    assert _combat_level(SimpleNamespace(level=SimpleNamespace(level=12))) == 12


def test_balance_report_handles_equal_win_rates_and_quick_balance_placeholder():
    from src.core.analytics.combat_simulator import BalanceReport, quick_balance_test

    report = BalanceReport(
        total_battles=2,
        results=[
            _make_stats(winner_class="Warrior", loser_class="Mage", abilities={"Attack": 2}),
            _make_stats(winner_class="Mage", loser_class="Warrior", abilities={"Attack": 1}),
        ],
    )

    assert report.identify_outliers() == {"overpowered": [], "underpowered": []}
    summary = report.generate_summary()
    assert "COMBAT BALANCE REPORT" in summary
    assert "Win Rates by Class" in summary
    assert quick_balance_test("Warrior", level=10) is None


def test_simulate_battle_records_all_event_accounting_branches(monkeypatch):
    from src.core.analytics import combat_simulator as sim_mod
    from src.core.events.event_bus import EventType, create_combat_event

    start_events = [
        create_combat_event(EventType.SPELL_CAST, actor=None, spell_name="Zap"),
        create_combat_event(EventType.SKILL_USE, actor=None, skill_name="Crush"),
        create_combat_event(EventType.ATTACK, actor=None),
        create_combat_event(EventType.STATUS_APPLIED, actor=None, status_name="Poison"),
        create_combat_event(EventType.CRITICAL_HIT, actor=None),
        create_combat_event(EventType.MISS, actor=None),
        SimpleNamespace(type=EventType.DAMAGE_DEALT, data={"actor": "Hero", "damage": 11}),
        SimpleNamespace(type=EventType.SKILL_USE, data=None),
    ]

    monkeypatch.setattr("src.core.combat.battle_engine.BattleEngine", _make_fake_engine(start_events=start_events))

    player = _make_player()
    enemy = _make_player(name="Goblin")

    sim = sim_mod.CombatSimulator()
    stats = sim.simulate_battle(player, enemy, max_turns=0, seed=123)

    assert stats.turns == 0
    assert stats.winner == "draw"
    assert stats.abilities_used == {"Zap": 1, "Crush": 1, "Attack": 1}
    assert stats.status_effects_applied == {"Poison": 1}
    assert stats.critical_hits == 1
    assert stats.misses == 1
    assert stats.total_damage_dealt == 11


@pytest.mark.parametrize(
    ("case_name", "configure", "expected_action", "expected_choice"),
    [
        (
            "summon",
            lambda player, tile: (
                player.summons.update({"Wolf": SimpleNamespace(name="Wolf")}),
                tile.actions.append("Summon"),
            ),
            "Summon",
            "Wolf",
        ),
        (
            "totem",
            lambda player, tile: (
                player.spellbook["Skills"].update({"Totem": _make_skill("Totem")}),
                tile.actions.append("Totem"),
            ),
            "Totem",
            None,
        ),
        (
            "item",
            lambda player, tile: (
                setattr(player.health, "current", 15),
                player.inventory.update({"Health Potion": [SimpleNamespace(subtyp="Health", percent=75)]}),
                tile.actions.append("Use Item"),
            ),
            "Use Item",
            "Health Potion",
        ),
        (
            "heal spell",
            lambda player, tile: (
                setattr(player.health, "current", 15),
                player.spellbook["Spells"].update({"Heal": _make_spell("Heal", subtyp="Heal")}),
                tile.actions.append("Cast Spell"),
            ),
            "Cast Spell",
            "Heal",
        ),
        (
            "offensive spell",
            lambda player, tile: (
                player.spellbook["Spells"].update(
                    {"Fireball": _make_spell("Fireball", effects=[_make_damage_effect("DamageSpark")])}
                ),
                tile.actions.append("Cast Spell"),
            ),
            "Cast Spell",
            "Fireball",
        ),
        (
            "offensive skill",
            lambda player, tile: (
                player.spellbook["Skills"].update(
                    {"Crush": _make_skill("Crush", effects=[_make_damage_effect("DamageChunk")])}
                ),
                tile.actions.append("Use Skill"),
            ),
            "Use Skill",
            "Crush",
        ),
        (
            "attack fallback",
            lambda player, tile: (
                player.inventory.clear(),
                player.spellbook["Spells"].clear(),
                player.spellbook["Skills"].clear(),
            ),
            "Attack",
            None,
        ),
    ],
)
def test_simulate_battle_default_policy_prefers_high_value_actions(monkeypatch, case_name, configure, expected_action, expected_choice):
    from src.core.analytics import combat_simulator as sim_mod

    player = _make_player()
    enemy = _make_player(name="Goblin")
    tile = _make_tile()
    configure(player, tile)

    # Keep the player eligible to act and the policy eligible to run.
    player.status_effects["Silence"].active = False

    engine_cls = _make_fake_engine(player_turn=True)
    monkeypatch.setattr("src.core.combat.battle_engine.BattleEngine", engine_cls)

    sim = sim_mod.CombatSimulator()
    stats = sim.simulate_battle(player, enemy, max_turns=1, seed=7)

    instance = engine_cls.last_instance
    assert instance is not None
    assert instance.actions == [(expected_action, expected_choice)]
    assert stats.winner == "draw"


def test_simulate_battle_policy_exceptions_fall_back_to_attack(monkeypatch):
    from src.core.analytics import combat_simulator as sim_mod

    player = _make_player()
    enemy = _make_player(name="Goblin")

    player_engine = _make_fake_engine(player_turn=True)
    enemy_engine = _make_fake_engine(player_turn=False)

    monkeypatch.setattr("src.core.combat.battle_engine.BattleEngine", player_engine)
    sim = sim_mod.CombatSimulator()
    stats = sim.simulate_battle(player, enemy, max_turns=1, seed=11, char1_policy=lambda _engine: (_ for _ in ()).throw(RuntimeError("boom")))

    assert player_engine.last_instance.actions == [("Attack", None)]
    assert stats.winner == "draw"

    monkeypatch.setattr("src.core.combat.battle_engine.BattleEngine", enemy_engine)
    stats = sim.simulate_battle(
        player,
        enemy,
        max_turns=1,
        seed=12,
        char2_policy=lambda _engine: (_ for _ in ()).throw(RuntimeError("boom")),
    )

    assert enemy_engine.last_instance.actions == [("Attack", None)]
    assert stats.winner == "draw"


def test_run_simulations_copies_inputs_and_handles_uncopyable_fallback(monkeypatch):
    from src.core.analytics.combat_simulator import CombatSimulator

    class Uncopyable:
        def __init__(self, name):
            self.name = name

        def __deepcopy__(self, memo):
            raise RuntimeError("no deepcopy")

    factory_calls = {"players": 0, "enemies": 0}

    def make_player():
        factory_calls["players"] += 1
        return SimpleNamespace(name=f"FactoryHero-{factory_calls['players']}")

    enemy = Uncopyable("Boss")
    sim = CombatSimulator()
    seen = []

    def fake_simulate_battle(c1, c2, seed=None):
        seen.append((c1.name, c2.name, seed, c2 is enemy))
        return _make_stats(winner=c1.name, loser=c2.name)

    monkeypatch.setattr(sim, "simulate_battle", fake_simulate_battle)

    report = sim.run_simulations(make_player, enemy, iterations=2, seed=None)

    assert factory_calls["players"] == 2
    assert seen == [
        ("FactoryHero-1", "Boss", None, True),
        ("FactoryHero-2", "Boss", None, True),
    ]
    assert report.total_battles == 2
    assert len(report.results) == 2


def test_run_simulations_seeds_and_deepcopies_when_possible(monkeypatch):
    from src.core.analytics.combat_simulator import CombatSimulator

    seed_calls = []
    monkeypatch.setattr("random.seed", lambda value: seed_calls.append(value))

    player = SimpleNamespace(name="Hero")
    enemy = SimpleNamespace(name="Goblin")
    sim = CombatSimulator()
    seen = []

    def fake_simulate_battle(c1, c2, seed=None):
        seen.append((c1 is player, c2 is enemy, seed))
        return _make_stats(winner="Hero", loser="Goblin")

    monkeypatch.setattr(sim, "simulate_battle", fake_simulate_battle)

    report = sim.run_simulations(player, enemy, iterations=2, seed=50)

    assert seed_calls == [50, 51]
    assert seen == [(False, False, 50), (False, False, 51)]
    assert report.total_battles == 2
