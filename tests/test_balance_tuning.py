#!/usr/bin/env python3
"""Targeted regression tests for Focus Area 4.3 balance tuning tweaks."""

import random


def test_crit_chance_is_capped():
    from tests.test_framework import TestGameState
    from src.core.constants import MAX_CRIT_CHANCE

    player = TestGameState.create_player(
        class_name="Warrior",
        level=50,
        mana=(200, 200),
        health=(500, 500),
        stats={"dex": 80, "charisma": 80, "strength": 30, "intel": 30, "wisdom": 30, "con": 30},
    )

    # Force an extreme weapon crit contribution.
    player.equipment["Weapon"].crit = 1.0

    assert player.critical_chance("Weapon") <= MAX_CRIT_CHANCE


def test_laser2_applies_temporary_combat_stat_debuff(monkeypatch):
    from src.core.combat.combat_result import CombatResult, CombatResultGroup
    from src.core import items
    from tests.test_framework import TestGameState

    actor = TestGameState.create_player(class_name="Warrior", level=30)
    target = TestGameState.create_player(class_name="Warrior", level=30)
    target.stats.charisma = 0  # ensure t_chance doesn't push threshold > 1.0

    res = CombatResult(action="Weapon", actor=actor, target=target, hit=True, crit=2, damage=10)
    grp = CombatResultGroup()
    grp.add(res)

    # Force proc and deterministic debuff choice.
    monkeypatch.setattr(random, "random", lambda: 0.9999)
    monkeypatch.setattr(random, "choice", lambda seq: "Attack")

    items.Laser2().special_effect(grp)

    eff = target.stat_effects["Attack"]
    assert eff.active is True
    assert eff.extra < 0
    assert eff.duration > 0


def test_mimic_scales_with_player_level():
    from src.core.enemies import Mimic

    m = Mimic(z=1, player_level=50)
    # Player-level scaling is tiered; at level 50 we expect tier 5 (1 @ 1-10, ... 5 @ 41-50).
    assert m.level.pro_level >= 5
    assert m.action_stack[0]["ability"] == "Attack"


def test_clannfear_has_more_threatening_action_stack():
    from src.core.enemies import Clannfear
    from src.core.combat.action_queue import ActionPriority

    c = Clannfear()
    names = [e["ability"] for e in c.action_stack]
    assert "Double Strike" in names
    assert "Charge" in names
    charge = [e for e in c.action_stack if e["ability"] == "Charge"][0]
    assert charge["priority"] == ActionPriority.HIGH
