#!/usr/bin/env python3
"""Focused coverage for the Jester's adaptive combat forms."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from src.core import enemies
from tests.test_framework import TestGameState


def _make_target():
    target = TestGameState.create_player(class_name="Warrior", race_name="Human", level=20)
    target.health.current = target.health.max
    target.mana.current = target.mana.max
    for bucket_name in ("stat_effects", "magic_effects", "class_effects"):
        bucket = getattr(target, bucket_name, {})
        for effect in bucket.values():
            effect.active = False
    return target


def test_jester_starts_in_crimson_form():
    jester = enemies.Jester()

    assert jester._jester_form == "crimson"
    assert jester.picture == "jester.png"
    assert "Slot Machine" in jester.spellbook["Skills"]
    assert "Fireball" in jester.spellbook["Spells"]
    assert "Dispel" in jester.spellbook["Spells"]


def test_jester_form_abilities_are_in_cast_and_use_buckets():
    jester = enemies.Jester()

    for form_name in jester.FORM_DEFS:
        jester._apply_jester_form(form_name, track_cooldown=False)

        for ability in jester.spellbook["Spells"].values():
            assert hasattr(ability, "cast"), f"{form_name} spell {ability.name} cannot cast"

        for ability in jester.spellbook["Skills"].values():
            assert hasattr(ability, "use"), f"{form_name} skill {ability.name} cannot use"

    jester._apply_jester_form("amber", track_cooldown=False)
    assert "Mana Shield" in jester.spellbook["Skills"]
    assert "Mana Shield" not in jester.spellbook["Spells"]


def test_jester_switches_forms_based_on_player_profile(monkeypatch):
    jester = enemies.Jester()
    target = _make_target()
    jester._jester_form_shift_delay = 0
    monkeypatch.setattr(enemies.random, "random", lambda: 0.0)
    monkeypatch.setattr(enemies.random, "randint", lambda _low, _high: 1)
    monkeypatch.setattr(
        enemies.random,
        "choices",
        lambda candidates, weights, k=1: [candidates[weights.index(max(weights))]],
    )

    target.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 80 if mod == "magic" else 20
    text = jester.special_effects(target)
    assert text == (
        "The Jester changes form: Yellow Heckler.\n"
        "A yellow grin spreads across his mask, mocking every spark of magic you raise."
    )
    assert jester._jester_form == "amber"
    assert jester.picture == "jester1.png"

    jester._jester_form_shift_delay = 0
    target.magic_effects["Reflect"].active = True
    text = jester.special_effects(target)
    assert text == (
        "The Jester changes form: Blue Mirrorlord.\n"
        "Blue glass ripples over his costume, turning the whole room into a laughing mirror."
    )
    assert jester._jester_form == "azure"
    assert jester.picture == "jester4.png"

    jester._jester_form_shift_delay = 0
    target.magic_effects["Reflect"].active = False
    target.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 90 if mod == "weapon" else 20
    text = jester.special_effects(target)
    assert text == (
        "The Jester changes form: Green Cutpurse.\n"
        "Green motes scatter from his boots as the Jester slips into a knife dancer's stance."
    )
    assert jester._jester_form == "verdant"
    assert jester.picture == "jester3.png"

    jester._jester_form_shift_delay = 0
    target.health.current = max(1, int(target.health.max * 0.20))
    text = jester.special_effects(target)
    assert text == (
        "The Jester changes form: Purple Hexer.\n"
        "Purple smoke coils from his sleeves as he prepares a killing punchline."
    )
    assert jester._jester_form == "violet"
    assert jester.picture == "jester2.png"


def test_jester_does_not_change_form_while_stunned(monkeypatch):
    jester = enemies.Jester()
    target = _make_target()
    jester._jester_form_shift_delay = 0
    jester.status_effects["Stun"].active = True
    monkeypatch.setattr(enemies.random, "random", lambda: 0.0)
    monkeypatch.setattr(enemies.random, "choices", lambda candidates, weights, k=1: ["amber"])

    assert jester.special_effects(target) == ""
    assert jester._jester_form == "crimson"
    assert jester.picture == "jester.png"


def test_jester_form_delay_and_roll_prevent_constant_shifts(monkeypatch):
    jester = enemies.Jester()
    target = _make_target()
    target.magic_effects["Reflect"].active = True
    target.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 80
    jester._jester_form_shift_delay = 0
    monkeypatch.setattr(enemies.random, "random", lambda: 0.0)
    monkeypatch.setattr(enemies.random, "randint", lambda _low, _high: 2)
    monkeypatch.setattr(enemies.random, "choices", lambda candidates, weights, k=1: ["azure"])

    first = jester.special_effects(target)
    assert "Blue Mirrorlord" in first
    assert jester._jester_form == "azure"

    assert jester.special_effects(target) == ""
    assert jester.special_effects(target) == ""
    assert jester._jester_form == "azure"

    monkeypatch.setattr(enemies.random, "random", lambda: 0.99)
    jester._jester_form_shift_delay = 0
    assert jester.special_effects(target) == ""
    assert jester._jester_form == "azure"


def test_jester_weighted_choice_keeps_all_forms_possible(monkeypatch):
    jester = enemies.Jester()
    target = _make_target()
    target.mana.current = 0
    target.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 20

    captured = {}
    monkeypatch.setattr(enemies.random, "random", lambda: 0.0)
    monkeypatch.setattr(enemies.random, "choices", lambda candidates, weights, k=1: captured.update({
        "candidates": tuple(candidates),
        "weights": tuple(weights),
    }) or ["violet"])

    jester._jester_form_shift_delay = 0
    assert "Purple Hexer" in jester.special_effects(target)
    assert set(captured["candidates"]) == {"amber", "violet", "verdant", "azure"}
