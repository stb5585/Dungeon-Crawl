#!/usr/bin/env python3
"""
Companion and summon coverage for familiar progression and summon behavior.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

from tests.test_framework import TestGameState


@pytest.mark.parametrize(
    ("factory", "first_gain", "second_gain"),
    [
        ("Homunculus", "Cover", "Resurrection"),
        ("Fairy", "Reflect", "Cleanse"),
        ("Mephit", "Fireball", "Firestorm"),
        ("Jinkin", "Enfeeble", "Slot Machine"),
    ],
)
def test_familiar_level_up_progression(factory, first_gain, second_gain):
    from src.core import companions

    familiar = getattr(companions, factory)()
    familiar.name = factory
    familiar.level.pro_level = 1

    first_message = familiar.level_up()
    second_message = familiar.level_up()

    assert familiar.level.pro_level == 3
    assert first_gain in first_message
    assert second_gain in second_message


@pytest.mark.parametrize(
    ("factory", "expected_race"),
    [
        ("Homunculus", "Homunculus"),
        ("Fairy", "Fairy"),
        ("Mephit", "Mephit"),
        ("Jinkin", "Jinkin"),
    ],
)
def test_familiar_inspect_mentions_identity(factory, expected_race):
    from src.core import companions

    familiar = getattr(companions, factory)()

    assert expected_race in familiar.inspect()
    assert familiar.cls == "Familiar"


@pytest.mark.parametrize(
    "factory",
    [
        "Patagon",
        "Dilong",
        "Agloolik",
        "Cacus",
        "Fuath",
        "Izulu",
        "Hala",
        "Grigori",
        "Bardi",
        "Kobalos",
        "Zahhak",
    ],
)
def test_summon_constructors_define_core_identity(factory):
    from src.core import companions

    summon = getattr(companions, factory)()

    assert summon.name == factory
    assert set(summon.equipment.keys()) == {"Weapon", "Armor", "OffHand", "Ring", "Pendant"}
    assert summon.level.pro_level >= 1
    assert isinstance(summon.description, str)


def test_summon_options_hide_spell_actions_when_silenced():
    from src.core.companions import Patagon

    summon = Patagon()

    assert summon.options() == ["Attack", "Use Skill", "Recall"]

    summon.status_effects["Silence"].active = True
    assert summon.options() == ["Attack", "Recall"]


def test_summon_inspect_formats_stat_block():
    from src.core.companions import Patagon

    summon = Patagon()
    text = summon.inspect()

    assert "Patagon - Level" in text
    assert "Hit Points:" in text
    assert "Mana Points:" in text
    assert "Attack:" in text


def test_summon_level_up_adds_even_level_stats_and_odd_level_ability(monkeypatch):
    from src.core.companions import Patagon

    player = TestGameState.create_player(
        class_name="Knight Enchanter",
        race_name="Human",
        pro_level=3,
    )
    summon = Patagon()
    summon.stats.strength = 5

    monkeypatch.setattr("src.core.companions.random.randint", lambda _a, _b: 0)
    monkeypatch.setattr("src.core.companions.random.choices", lambda _choices, _weights: [0])

    even_message = summon.level_up(player)
    odd_message = summon.level_up(player)

    assert summon.level.level == 3
    assert "power increases" in even_message
    assert summon.stats.strength == 7
    assert "Piercing Strike" in summon.spellbook["Skills"]
    assert "Piercing Strike" in odd_message


def test_zahhak_special_attack_delegates_to_breathe_fire(monkeypatch):
    from src.core.companions import Zahhak

    target = TestGameState.create_player(name="Target", class_name="Warrior", race_name="Human")
    summon = Zahhak()

    class FakeBreath:
        def use(self, user, target=None):
            assert user is summon
            assert target is not None
            return "Flames!"

    monkeypatch.setattr("src.core.companions.abilities.BreatheFire", lambda: FakeBreath())

    assert summon.special_attack(target) == "Flames!"
