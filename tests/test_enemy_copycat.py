#!/usr/bin/env python3
"""Tests for the Funhouse Copycat enemy (mirrors a subset of player abilities)."""

import random

import pytest


def _make_player():
    from tests.test_framework import TestGameState
    from src.core import abilities

    player = TestGameState.create_player(
        name="Hero",
        class_name="Warrior",
        race_name="Human",
        level=10,
        health=(200, 200),
        mana=(200, 200),
    )

    # Known-good combat abilities
    player.spellbook["Spells"]["Fireball"] = abilities.Fireball()
    player.spellbook["Skills"]["Charge"] = abilities.Charge()

    # Blacklisted / special-context abilities (should not be copied)
    player.spellbook["Spells"]["Teleport"] = abilities.Teleport()
    player.spellbook["Skills"]["Slot Machine"] = abilities.SlotMachine()

    # Over-cost ability (force skip by inflating cost on the source instance)
    expensive = abilities.Fireball()
    expensive.cost = 9999
    player.spellbook["Spells"]["Too Expensive"] = expensive

    return player


def test_copycat_clones_abilities_not_same_instances():
    from src.core.enemies import Copycat

    player = _make_player()
    enemy = Copycat()

    # Trigger mirroring via options()
    enemy.options(player, [], None)

    copied_fireball = next(
        (ab for ab in enemy.spellbook.get("Spells", {}).values() if getattr(ab, "name", "") == "Fireball"),
        None,
    )
    copied_charge = next(
        (ab for ab in enemy.spellbook.get("Skills", {}).values() if getattr(ab, "name", "") == "Charge"),
        None,
    )

    assert copied_fireball is not None
    assert copied_charge is not None

    assert copied_fireball is not player.spellbook["Spells"]["Fireball"]
    assert copied_charge is not player.spellbook["Skills"]["Charge"]


def test_copycat_only_copies_affordable_non_blacklisted():
    from src.core.enemies import Copycat

    player = _make_player()
    enemy = Copycat()

    enemy.options(player, [], None)

    # Ensure blacklisted items not present (by class name / behavior)
    assert all(getattr(ab, "_class_name", ab.__class__.__name__) != "Teleport"
               for ab in enemy.spellbook.get("Spells", {}).values())
    assert all(getattr(ab, "_class_name", ab.__class__.__name__) != "SlotMachine"
               for ab in enemy.spellbook.get("Skills", {}).values())

    # Ensure over-cost source did not get copied
    assert all(getattr(ab, "cost", 0) < 9999 for ab in enemy.spellbook.get("Spells", {}).values())


def test_copycat_can_select_copied_action_deterministically(monkeypatch):
    from src.core.enemies import Copycat

    player = _make_player()
    enemy = Copycat()

    # Mirror first (so action_stack includes copied abilities)
    enemy.options(player, [], None)

    # Deterministic pick: choose the last weighted option, which should not be Attack
    monkeypatch.setattr(random, "choice", lambda seq: seq[-1])

    action, ability = enemy.options(player, [], None)

    assert action in {"Cast Spell", "Use Skill"}
    assert ability is not None

