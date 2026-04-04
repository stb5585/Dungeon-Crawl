#!/usr/bin/env python3
"""Catalog and legacy behavior coverage for enemy definitions."""

import inspect
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from src.core import abilities, enemies, items
from tests.test_framework import TestGameState


def _no_arg_enemy_classes():
    enemy_classes = []
    for name in dir(enemies):
        obj = getattr(enemies, name)
        if not inspect.isclass(obj):
            continue
        if not issubclass(obj, enemies.Enemy) or obj is enemies.Enemy:
            continue
        signature = inspect.signature(obj)
        required = [
            param
            for param in signature.parameters.values()
            if param.default is param.empty
            and param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD)
        ]
        if not required:
            enemy_classes.append(obj)
    return sorted(enemy_classes, key=lambda cls: cls.__name__)


def _make_enemy(name="Scout"):
    return enemies.Enemy(name, 10, 10, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 10)


def test_no_arg_enemy_catalog_instantiates_and_renders_cleanly():
    discovered = _no_arg_enemy_classes()

    assert len(discovered) >= 100

    instantiated_names = []
    for enemy_cls in discovered:
        enemy = enemy_cls()
        instantiated_names.append(enemy.name)
        assert enemy.cls is enemy
        assert isinstance(enemy.experience, int)
        assert isinstance(enemy.enemy_typ, str)
        assert enemy.spellbook.keys() >= {"Spells", "Skills"}
        assert "Health:" in str(enemy)
        details = enemy.inspect()
        assert f"Name: {enemy.name}" in details
        assert "Type:" in details

    assert "Goblin" in instantiated_names
    assert "Hydra" in instantiated_names
    assert "Copycat" in instantiated_names


def test_random_enemy_and_funhouse_enemy_follow_expected_catalog_edges(monkeypatch):
    monkeypatch.setattr("src.core.enemies.random.choice", lambda seq: seq[0])
    assert isinstance(enemies.random_enemy("0"), enemies.GreenSlime)

    monkeypatch.setattr("src.core.enemies.random.choice", lambda seq: seq[-1])
    assert isinstance(enemies.random_enemy("999"), enemies.BrainGorger)
    assert isinstance(enemies.funhouse_enemy(), enemies.Copycat)


def test_enemy_options_short_circuit_for_berserk_turtle_and_ice_block():
    target = TestGameState.create_player(class_name="Warrior", race_name="Human", level=1)

    berserk_enemy = _make_enemy()
    berserk_enemy.status_effects["Berserk"].active = True
    assert berserk_enemy.options(target, [], None) == ("Attack", None)

    turtle_enemy = _make_enemy()
    turtle_enemy.turtle = True
    assert turtle_enemy.options(target, [], None) == ("Nothing", None)

    ice_block_enemy = _make_enemy()
    ice_block_enemy.magic_effects["Ice Block"].active = True
    assert ice_block_enemy.options(target, [], None) == ("Nothing", None)


def test_enemy_options_cover_pickup_surface_and_flee_legacy_paths(monkeypatch):
    low_level_target = TestGameState.create_player(class_name="Warrior", race_name="Human", level=1)
    weapon = items.Weapon("Test Sword", "", 0, 0.0, 1, 1, "1-Handed", "Sword", False, True)

    pickup_enemy = _make_enemy(name="Test")
    pickup_enemy.tunnel = True
    pickup_enemy.equipment["Weapon"] = weapon
    pickup_enemy.physical_effects["Disarm"].active = True
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])
    assert pickup_enemy.options(low_level_target, [], None) == ("Pickup Weapon", None)

    surface_enemy = _make_enemy(name="Test")
    surface_enemy.tunnel = True
    surface_enemy.equipment["Weapon"] = weapon
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])
    assert surface_enemy.options(low_level_target, [], None) == ("Surface", None)

    flee_enemy = _make_enemy(name="Scout")
    flee_target = TestGameState.create_player(class_name="Sorcerer", race_name="Human", level=10)
    monkeypatch.setattr("src.core.enemies.random.randint", lambda low, high: 1)
    monkeypatch.setattr(random, "choice", lambda seq: seq[-1])
    assert flee_enemy.options(flee_target, [], None) == ("Flee", None)


def test_required_argument_enemy_constructors_render_expected_state():
    mimic = enemies.Mimic(z=1, player_level=25)
    assert mimic.name == "Mimic"
    assert mimic.level.pro_level == 3
    assert mimic.sight is True
    assert "Name: Mimic" in mimic.inspect()

    minion = enemies.FunhouseMinion(
        name="Practice Dummy",
        health_range=(10, 10),
        mana_range=(5, 5),
        stat_range=(3, 3),
        combat_range=(4, 4),
        exp_range=(7, 7),
    )
    assert minion.name == "Practice Dummy"
    assert minion.level.pro_level == 4
    assert any(entry["ability"] == "Attack" for entry in minion.action_stack)


def test_enemy_legacy_options_can_select_spell_and_skill(monkeypatch):
    target = TestGameState.create_player(class_name="Warrior", race_name="Human", level=1)

    spell_enemy = _make_enemy(name="Test")
    spell_enemy.spellbook["Spells"]["Regen"] = abilities.Regen()
    monkeypatch.setattr(random, "choice", lambda seq: seq[-1])
    assert spell_enemy.options(target, [], None) == ("Cast Spell", "Regen")

    skill_enemy = _make_enemy(name="Test")
    skill_enemy.spellbook["Skills"]["Disarm"] = abilities.Disarm()
    monkeypatch.setattr(random, "choice", lambda seq: seq[-1])
    assert skill_enemy.options(target, [], None) == ("Use Skill", "Disarm")
