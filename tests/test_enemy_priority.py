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
    enemy.spellbook["Spells"]["Regen"] = abilities.Regen()
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


def test_priority_if_list_supports_magic_effect_conditions(monkeypatch):
    """
    action_stack configs in enemies.py sometimes use list-style priority_if rules and refer
    to magic effects (e.g. Regen) via "self_status". Ensure those are respected.
    """
    enemy = _make_enemy()
    target = _make_target(True)

    enemy.magic_effects["Regen"].active = True
    enemy.action_stack = [
        {
            "ability": "Regen",
            "priority": ActionPriority.NORMAL,
            "priority_if": [
                {"condition": "self_hp_pct_lt", "value": 0.5, "priority": ActionPriority.HIGH},
                {"condition": "self_status", "value": "Regen", "priority": ActionPriority.SKIP},
            ],
        },
        {"ability": "Attack", "priority": ActionPriority.NORMAL},
    ]

    # Deterministic: if Regen isn't skipped it will appear first in the weighted pool.
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])

    action, ability = enemy.options(target, [], None)

    assert action == "Attack"
    assert ability == "Attack"


def test_priority_if_list_threshold_percent_parsing():
    enemy = _make_enemy()
    target = _make_target(True)

    # 4/10 = 0.4, which is NOT below 10% (0.1). This should not match.
    enemy.health.current = 4
    enemy.health.max = 10

    resolved = enemy._resolve_priority_condition(  # noqa: SLF001 - intentional unit coverage
        [{"condition": "self_hp_pct_lt", "value": 10, "priority": ActionPriority.HIGH}],
        ActionPriority.NORMAL,
        target,
        None,
    )
    assert resolved == ActionPriority.NORMAL

    # 0.05 below 10% should match.
    enemy.health.current = 1
    enemy.health.max = 100
    resolved2 = enemy._resolve_priority_condition(  # noqa: SLF001 - intentional unit coverage
        [{"condition": "self_hp_pct_lt", "value": 10, "priority": ActionPriority.HIGH}],
        ActionPriority.NORMAL,
        target,
        None,
    )
    assert resolved2 == ActionPriority.HIGH


def test_single_use_ability_only_selected_once(monkeypatch):
    enemy = _make_enemy()
    target = _make_target(True)
    enemy.single_use_abilities = {"Regen"}
    enemy.action_stack = [
        {"ability": "Regen", "priority": ActionPriority.HIGH},
        {"ability": "Attack", "priority": ActionPriority.NORMAL},
    ]

    monkeypatch.setattr(random, "choice", lambda seq: seq[0])

    first_action, first_ability = enemy.options(target, [], None)
    second_action, second_ability = enemy.options(target, [], None)

    assert (first_action, first_ability) == ("Cast Spell", "Regen")
    assert (second_action, second_ability) == ("Attack", "Attack")
