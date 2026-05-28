#!/usr/bin/env python3
"""Focused combat-result contract coverage."""

from __future__ import annotations

from src.core.combat.combat_result import CombatResult, CombatResultGroup
from tests.test_framework import TestGameState


def test_combat_result_to_dict_uses_character_names():
    actor = TestGameState.create_player(name="Hero", class_name="Warrior", race_name="Human")
    target = TestGameState.create_player(name="Target", class_name="Warrior", race_name="Human")
    result = CombatResult(action="Attack", actor=actor, target=target, damage=7, message="Hit.")

    payload = result.to_dict()

    assert payload["actor"] == "Hero"
    assert payload["target"] == "Target"
    assert payload["damage"] == 7
    assert payload["message"] == "Hit."


def test_combat_result_to_dict_snapshots_mutable_fields():
    result = CombatResult(action="Cast Spell")
    result.effects_applied["Status"].append("Poison")
    result.extra["rolls"] = [4]

    payload = result.to_dict()
    payload["effects_applied"]["Status"].append("Sleep")
    payload["extra"]["rolls"].append(8)

    assert result.effects_applied["Status"] == ["Poison"]
    assert result.extra["rolls"] == [4]


def test_combat_result_defaults_are_independent():
    first = CombatResult(action="Attack")
    second = CombatResult(action="Attack")

    first.effects_applied["Physical"].append("Prone")
    first.extra["note"] = "first"

    assert second.effects_applied["Physical"] == []
    assert "note" not in second.extra


def test_combat_result_group_to_dict_preserves_order():
    group = CombatResultGroup()
    group.add(CombatResult(action="Attack", damage=3))
    group.add(CombatResult(action="Heal", healing=5))

    payload = group.to_dict()

    assert [entry["action"] for entry in payload] == ["Attack", "Heal"]
    assert payload[0]["damage"] == 3
    assert payload[1]["healing"] == 5
