"""Characterization coverage for the staged weapon-damage pipeline."""

import random

from src.core import items
from tests.test_framework import TestGameState


def _deterministic_weapon_attack(monkeypatch, attacker, defender) -> None:
    """Remove hit, dodge, crit, and damage-variance randomness from a test attack."""
    monkeypatch.setattr(attacker, "critical_chance", lambda _slot: 0.0)
    monkeypatch.setattr(attacker, "hit_chance", lambda *_args, **_kwargs: 1.0)
    monkeypatch.setattr(defender, "dodge_chance", lambda *_args, **_kwargs: 0.0)
    monkeypatch.setattr(random, "random", lambda: 0.9999)
    monkeypatch.setattr(random, "uniform", lambda _minimum, _maximum: 1.0)


def test_weapon_damage_returns_no_effect_before_slot_resolution(monkeypatch):
    attacker = TestGameState.create_player(class_name="Warrior", level=30)
    defender = TestGameState.create_player(class_name="Warrior", level=30)
    _deterministic_weapon_attack(monkeypatch, attacker, defender)

    attacker._surprise_ready = True
    defender.magic_effects["Ice Block"].active = True
    starting_health = defender.health.current

    result = attacker.weapon_damage(defender, crit=3, use_offhand=False)

    assert result == (f"{attacker.name}'s attack has no effect.\n", False, 3)
    assert defender.health.current == starting_health
    assert attacker._surprise_attack is False


def test_weapon_damage_uses_an_explicit_offhand_slot(monkeypatch):
    attacker = TestGameState.create_player(class_name="Warrior", level=30)
    defender = TestGameState.create_player(class_name="Warrior", level=30)
    attacker.equipment["Weapon"] = items.NoWeapon()
    attacker.equipment["OffHand"] = items.Dirk()
    _deterministic_weapon_attack(monkeypatch, attacker, defender)
    starting_health = defender.health.current

    message, hit, crit = attacker.weapon_damage(
        defender,
        hit=True,
        attack_slots=("OffHand",),
    )

    assert hit is True
    assert crit == 1
    assert defender.health.current < starting_health
    assert attacker.name in message


def test_weapon_damage_empty_slot_selection_keeps_the_existing_failure_contract():
    attacker = TestGameState.create_player(class_name="Warrior", level=30)
    defender = TestGameState.create_player(class_name="Warrior", level=30)

    assert attacker.weapon_damage(defender, attack_slots=()) == (
        f"{attacker.name} cannot use their main-hand weapon.\n",
        False,
        1,
    )
