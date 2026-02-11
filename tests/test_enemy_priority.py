#!/usr/bin/env python3
"""Tests for priority-weighted enemy action selection."""

import random

from src.core import abilities, items
from src.core.character import Character, Combat, Resource, Stats
from src.core.combat.action_queue import ActionPriority
from src.core.enemies import Enemy


def _make_enemy():
    enemy = Enemy("TestEnemy", 10, 10, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 10)
    enemy.spellbook["Skills"]["Disarm"] = abilities.Disarm()
    enemy.mana.current = enemy.mana.max
    return enemy


def _make_target(has_weapon: bool) -> Character:
    target = Character("Target", Resource(10, 10), Resource(10, 10), Stats(), Combat())
    if has_weapon:
        weapon = items.Weapon("Test Sword", "", 0, 0.0, 1, 1, "1-Handed", "Sword", False, True)
    else:
        weapon = items.NoWeapon()
    target.equipment = {"Weapon": weapon}
    return target


def test_priority_to_weight_includes_skip():
    assert Enemy._priority_to_weight(ActionPriority.HIGH) == 3
    assert Enemy._priority_to_weight(ActionPriority.NORMAL) == 2
    assert Enemy._priority_to_weight(ActionPriority.LOW) == 1
    assert Enemy._priority_to_weight(ActionPriority.SKIP) == 0


def test_priority_if_skips_disarm_when_target_unarmed():
    enemy = _make_enemy()
    target = _make_target(False)
    enemy.action_stack = [
        {
            "ability": "Disarm",
            "priority": ActionPriority.NORMAL,
            "priority_if": {
                "target_has_weapon": True,
                "priority": ActionPriority.HIGH,
                "else": ActionPriority.SKIP,
            },
        },
        {"ability": "Attack", "priority": ActionPriority.NORMAL},
    ]

    action, ability = enemy.options(target, [], None)

    assert action == "Attack"
    assert ability == "Attack"


def test_priority_if_allows_disarm_when_target_armed(monkeypatch):
    enemy = _make_enemy()
    target = _make_target(True)
    enemy.action_stack = [
        {
            "ability": "Disarm",
            "priority": ActionPriority.NORMAL,
            "priority_if": {
                "target_has_weapon": True,
                "priority": ActionPriority.HIGH,
                "else": ActionPriority.SKIP,
            },
        },
        {"ability": "Attack", "priority": ActionPriority.NORMAL},
    ]

    monkeypatch.setattr(random, "choice", lambda seq: seq[0])

    action, ability = enemy.options(target, [], None)

    assert (action, ability) == ("Use Skill", "Disarm")
