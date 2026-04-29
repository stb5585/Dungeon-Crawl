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
    assert "Gold Toss" in jester.spellbook["Skills"]
    assert "Mirror Image" in jester.spellbook["Spells"]


def test_jester_switches_forms_based_on_player_profile():
    jester = enemies.Jester()
    target = _make_target()

    target.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 80 if mod == "magic" else 20
    text = jester.special_effects(target)
    assert "Yellow Heckler" in text
    assert jester._jester_form == "amber"
    assert jester.picture == "jester1.png"

    target.magic_effects["Reflect"].active = True
    text = jester.special_effects(target)
    assert "Blue Mirrorlord" in text
    assert jester._jester_form == "azure"
    assert jester.picture == "jester4.png"

    target.magic_effects["Reflect"].active = False
    target.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 90 if mod == "weapon" else 20
    text = jester.special_effects(target)
    assert "Green Cutpurse" in text
    assert jester._jester_form == "verdant"
    assert jester.picture == "jester3.png"

    target.health.current = max(1, int(target.health.max * 0.20))
    text = jester.special_effects(target)
    assert "Purple Hexer" in text
    assert jester._jester_form == "violet"
    assert jester.picture == "jester2.png"
