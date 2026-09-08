"""Contracts for virtual-readiness combat scheduling."""

from __future__ import annotations

from random import Random
from types import SimpleNamespace

from src.core.combat.actor_cycle import ActorCycle, build_readiness_cycle


class _Actor:
    """Minimal timing actor with deterministic Speed and Luck modifiers."""

    def __init__(self, speed: int, luck: int = 0):
        self.speed = speed
        self.luck = luck
        self.invisible = False
        self.sight = False
        self.cls = SimpleNamespace(name="Warrior")
        self.power_up = False
        self.class_effects = {"Power Up": SimpleNamespace(active=False, duration=0)}

    def check_mod(self, category, **_kwargs):
        if category == "speed":
            return self.speed
        if category == "luck":
            return self.luck
        raise AssertionError(f"Unexpected timing modifier: {category}")


def test_readiness_initialization_is_seeded_and_uses_median_speed():
    player = _Actor(speed=12, luck=3)
    enemy = _Actor(speed=24, luck=7)
    encounter = SimpleNamespace(
        living_members=[SimpleNamespace(combatant_id="enemy-a", enemy=enemy)]
    )

    first = build_readiness_cycle(player, encounter, rng=Random(1337))
    second = build_readiness_cycle(player, encounter, rng=Random(1337))

    assert first.readiness == second.readiness
    assert first.median_speed == 18.0
    assert min(first.readiness.values()) == 0.0
    assert all(value >= 0.0 for value in first.readiness.values())


def test_surprise_is_scheduled_at_time_zero():
    player = _Actor(speed=10)
    player.invisible = True
    enemy = _Actor(speed=10)
    encounter = SimpleNamespace(
        living_members=[SimpleNamespace(combatant_id="enemy-a", enemy=enemy)]
    )

    cycle = build_readiness_cycle(player, encounter, rng=Random(7))

    assert cycle.current_actor_id == "player"
    assert cycle.current_ready_at == 0.0


def test_third_consecutive_turn_waits_for_another_living_actor():
    cycle = ActorCycle(("fast", "slow"), readiness={"fast": 0.0, "slow": 1000.0})

    cycle.start_current_turn()
    _wrapped, actor_id = cycle.advance({"fast", "slow"}, readiness_cost=100.0)
    assert actor_id == "fast"
    cycle.start_current_turn()
    _wrapped, actor_id = cycle.advance({"fast", "slow"}, readiness_cost=100.0)

    assert actor_id == "slow"
    assert cycle.current_ready_at == 1000.0
    cycle.start_current_turn()
    _wrapped, actor_id = cycle.advance({"fast", "slow"}, readiness_cost=100.0)
    assert actor_id == "fast"
    assert cycle.current_ready_at == 1000.0


def test_round_completes_after_each_initial_actor_gets_an_opportunity():
    cycle = ActorCycle(("first", "second"), readiness={"first": 0.0, "second": 20.0})

    cycle.start_current_turn()
    wrapped, actor_id = cycle.advance({"first", "second"}, readiness_cost=100.0)
    assert wrapped is False
    assert actor_id == "second"
    cycle.start_current_turn()
    wrapped, actor_id = cycle.advance({"first", "second"}, readiness_cost=100.0)

    assert wrapped is True
    assert cycle.round_number == 2
    assert actor_id == "first"


def test_reinforcement_is_immediate_but_does_not_extend_the_current_round():
    cycle = ActorCycle(("first", "second"), readiness={"first": 0.0, "second": 20.0})
    cycle.start_current_turn()
    cycle.add_actor("reinforcement")

    assert "reinforcement" not in cycle.round_pending_actor_ids
    _wrapped, actor_id = cycle.advance({"first", "second", "reinforcement"}, readiness_cost=100.0)
    assert actor_id == "reinforcement"


def test_preview_projects_future_opportunities_without_mutating_the_cycle():
    cycle = ActorCycle(("first", "second"), readiness={"first": 0.0, "second": 20.0})
    cycle.start_current_turn()

    preview = cycle.preview({"first", "second"}, lambda _actor_id: 100.0, limit=3)

    assert preview == (("first", 0.0), ("second", 20.0), ("first", 100.0))
    assert cycle.current_actor_id == "first"
    assert cycle.current_ready_at == 0.0
    assert cycle.round_number == 1
