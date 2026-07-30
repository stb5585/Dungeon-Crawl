#!/usr/bin/env python3
"""Tests for priority-weighted enemy action selection."""

import random

from src.core import abilities, items
from src.core.character import Character, Combat, Resource, Stats
from src.core.combat.action_queue import ActionPriority
from src.core.enemies import Bandit, Enemy, Jester


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
    assert ability is None


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


def test_bandit_steal_success_makes_smoke_screen_most_likely(monkeypatch):
    bandit = Bandit()
    target = _make_target(True)
    bandit.status_effects["Steal Success"].active = True
    bandit.status_effects["Steal Success"].duration = 2
    captured = []

    def choose(seq):
        captured.extend(seq)
        return next(entry for entry in seq if entry[:2] == ("Use Skill", "Smoke Screen"))

    monkeypatch.setattr(random, "choice", choose)

    action, ability = bandit.options(target, [], None)

    assert (action, ability) == ("Use Skill", "Smoke Screen")
    smoke_entries = [entry for entry in captured if entry[:2] == ("Use Skill", "Smoke Screen")]
    competing_entries = [entry for entry in captured if entry[:2] != ("Use Skill", "Smoke Screen")]
    assert len(smoke_entries) == 3
    assert len(competing_entries) == 1
    assert not any(entry[:2] == ("Use Skill", "Steal") for entry in captured)
    assert not any(entry[:2] == ("Use Skill", "Disarm") for entry in captured)


def test_priority_ai_skips_weapon_skills_while_disarmed(monkeypatch):
    enemy = _make_enemy()
    target = _make_target(True)
    enemy.spellbook["Skills"]["Mortal Strike"] = abilities.MortalStrike()
    enemy.equipment["Weapon"] = items.Weapon("Axe", "", 0, 0.0, 1, 1, "1-Handed", "Axe", False, True)
    enemy.physical_effects["Disarm"].active = True
    enemy.action_stack = [
        {"ability": "Mortal Strike", "priority": ActionPriority.HIGH},
        {"ability": "Attack", "priority": ActionPriority.NORMAL},
    ]
    captured = []

    def choose(seq):
        captured.extend(seq)
        return next(entry for entry in seq if entry[0] == "Attack")

    monkeypatch.setattr(random, "choice", choose)

    action, ability = enemy.options(target, [], None)

    assert (action, ability) == ("Attack", None)
    assert not any(entry[:2] == ("Use Skill", "Mortal Strike") for entry in captured)


def test_priority_ai_prioritizes_pickup_for_weapon_dependent_enemy(monkeypatch):
    enemy = _make_enemy()
    target = _make_target(True)
    enemy.spellbook["Spells"] = {}
    enemy.spellbook["Skills"] = {"Mortal Strike": abilities.MortalStrike()}
    enemy.equipment["Weapon"] = items.Weapon("Axe", "", 0, 0.0, 1, 1, "1-Handed", "Axe", False, True)
    enemy.physical_effects["Disarm"].active = True
    enemy.action_stack = [
        {"ability": "Mortal Strike", "priority": ActionPriority.HIGH},
        {"ability": "Attack", "priority": ActionPriority.NORMAL},
    ]
    captured = []

    def choose(seq):
        captured.extend(seq)
        return seq[0]

    monkeypatch.setattr(random, "choice", choose)

    action, ability = enemy.options(target, [], None)

    pickup_entries = [entry for entry in captured if entry[0] == "Pickup Weapon"]
    assert (action, ability) == ("Pickup Weapon", None)
    assert len(pickup_entries) == 3


def test_priority_ai_keeps_pickup_low_for_spell_focused_enemy(monkeypatch):
    enemy = _make_enemy()
    target = _make_target(True)
    enemy.spellbook["Skills"] = {}
    enemy.spellbook["Spells"] = {
        "Firebolt": abilities.Firebolt(),
        "Enfeeble": abilities.Enfeeble(),
    }
    enemy.equipment["Weapon"] = items.Weapon("Staff", "", 0, 0.0, 1, 1, "1-Handed", "Staff", False, True)
    enemy.physical_effects["Disarm"].active = True
    enemy.action_stack = [
        {"ability": "Firebolt", "priority": ActionPriority.NORMAL},
        {"ability": "Enfeeble", "priority": ActionPriority.NORMAL},
    ]
    captured = []

    def choose(seq):
        captured.extend(seq)
        return next(entry for entry in seq if entry[0] == "Cast Spell")

    monkeypatch.setattr(random, "choice", choose)

    action, ability = enemy.options(target, [], None)

    pickup_entries = [entry for entry in captured if entry[0] == "Pickup Weapon"]
    spell_entries = [entry for entry in captured if entry[0] == "Cast Spell"]
    assert action == "Cast Spell"
    assert ability in {"Firebolt", "Enfeeble"}
    assert len(pickup_entries) == 1
    assert len(spell_entries) == 4


def test_failed_debuff_cooldown_skips_repeated_enfeeble(monkeypatch):
    enemy = _make_enemy()
    target = _make_target(True)
    enemy.spellbook["Spells"] = {"Enfeeble": abilities.Enfeeble()}
    enemy.spellbook["Skills"] = {}
    enemy.action_stack = [
        {"ability": "Attack", "priority": ActionPriority.NORMAL},
        {"ability": "Enfeeble", "priority": ActionPriority.HIGH},
    ]
    enemy.record_debuff_failure("Enfeeble", turns=2)
    captured = []

    def choose(seq):
        captured.append(list(seq))
        assert all(entry[1] != "Enfeeble" for entry in seq)
        return seq[0]

    monkeypatch.setattr(random, "choice", choose)

    assert enemy.options(target, [], None) == ("Attack", None)
    assert enemy.options(target, [], None) == ("Attack", None)
    assert len(captured) == 2
    assert enemy._debuff_failure_cooldowns == {}


def test_priority_action_stack_can_explicitly_request_pickup_weapon(monkeypatch):
    enemy = _make_enemy()
    target = _make_target(True)
    enemy._pickup_weapon_priority = lambda: ActionPriority.SKIP
    enemy.equipment["Weapon"] = items.Weapon("Sword", "", 0, 0.0, 1, 1, "1-Handed", "Sword", False, True)
    enemy.physical_effects["Disarm"].active = True
    enemy.action_stack = [
        {"ability": "Pickup Weapon", "priority": ActionPriority.HIGH},
        {"ability": "Attack", "priority": ActionPriority.NORMAL},
    ]
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])

    action, ability = enemy.options(target, [], None)

    assert (action, ability) == ("Pickup Weapon", None)


def test_priority_if_list_supports_magic_effect_conditions(monkeypatch):
    """
    Enemy action stacks sometimes use list-style priority_if rules and refer to
    magic effects (e.g. Regen) via "self_status". Ensure those are respected.
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
    assert ability is None


def test_priority_if_skips_redundant_target_status_spell(monkeypatch):
    enemy = _make_enemy()
    target = _make_target(True)
    enemy.spellbook["Spells"]["Sleep"] = abilities.Sleep()
    target.status_effects["Sleep"].active = True
    target.status_effects["Sleep"].duration = 2
    enemy.action_stack = [
        {
            "ability": "Sleep",
            "priority": ActionPriority.HIGH,
            "priority_if": {
                "target_status": "Sleep",
                "priority": ActionPriority.SKIP,
                "else": ActionPriority.HIGH,
            },
        },
        {"ability": "Attack", "priority": ActionPriority.NORMAL},
    ]

    monkeypatch.setattr(random, "choice", lambda seq: seq[0])

    action, ability = enemy.options(target, [], None)

    assert (action, ability) == ("Attack", None)


def test_priority_if_targets_positive_effects_for_dispel(monkeypatch):
    enemy = _make_enemy()
    target = _make_target(True)
    enemy.spellbook["Spells"]["Dispel"] = abilities.Dispel()
    enemy.mana.current = 999
    enemy.mana.max = 999
    enemy.action_stack = [
        {
            "ability": "Dispel",
            "priority": ActionPriority.HIGH,
            "priority_if": {
                "target_has_positive_effects": True,
                "priority": ActionPriority.HIGH,
                "else": ActionPriority.SKIP,
            },
        },
        {"ability": "Attack", "priority": ActionPriority.NORMAL},
    ]

    monkeypatch.setattr(random, "choice", lambda seq: seq[0])

    action, ability = enemy.options(target, [], None)
    assert (action, ability) == ("Attack", None)

    target.stat_effects["Attack"].active = True
    action, ability = enemy.options(target, [], None)
    assert (action, ability) == ("Cast Spell", "Dispel")


def test_priority_if_targets_only_positive_stat_effects_for_dispel(monkeypatch):
    enemy = _make_enemy()
    target = _make_target(True)
    enemy.spellbook["Spells"]["Dispel"] = abilities.Dispel()
    enemy.mana.current = 999
    enemy.mana.max = 999
    enemy.action_stack = [
        {
            "ability": "Dispel",
            "priority": ActionPriority.HIGH,
            "priority_if": {
                "target_has_positive_stat_effects": True,
                "priority": ActionPriority.HIGH,
                "else": ActionPriority.SKIP,
            },
        },
        {"ability": "Attack", "priority": ActionPriority.NORMAL},
    ]

    monkeypatch.setattr(random, "choice", lambda seq: seq[0])

    target.magic_effects["Regen"].active = True
    assert enemy.options(target, [], None) == ("Attack", None)

    target.stat_effects["Defense"].active = True
    target.stat_effects["Defense"].extra = -2
    assert enemy.options(target, [], None) == ("Attack", None)

    target.stat_effects["Attack"].active = True
    target.stat_effects["Attack"].extra = 0
    assert enemy.options(target, [], None) == ("Attack", None)

    target.stat_effects["Attack"].extra = 3
    assert enemy.options(target, [], None) == ("Cast Spell", "Dispel")


def test_jester_dispel_only_targets_positive_player_stat_effects(monkeypatch):
    jester = Jester()
    target = _make_target(True)
    jester.mana.current = jester.mana.max

    def choose_dispel_if_available(seq):
        return next((entry for entry in seq if entry[:2] == ("Cast Spell", "Dispel")), seq[0])

    monkeypatch.setattr(random, "choice", choose_dispel_if_available)

    target.magic_effects["Regen"].active = True
    assert jester.options(target, [], None) != ("Cast Spell", "Dispel")

    target.stat_effects["Defense"].active = True
    target.stat_effects["Defense"].extra = -2
    assert jester.options(target, [], None) != ("Cast Spell", "Dispel")

    target.stat_effects["Attack"].active = True
    target.stat_effects["Attack"].extra = 2
    assert jester.options(target, [], None) == ("Cast Spell", "Dispel")


def test_jester_mana_shield_skips_when_mana_is_low(monkeypatch):
    jester = Jester()
    jester._apply_jester_form("amber", track_cooldown=False)  # noqa: SLF001 - explicit form setup for AI coverage
    target = _make_target(True)

    def choose_mana_shield_if_available(seq):
        return next((entry for entry in seq if entry[:2] == ("Use Skill", "Mana Shield")), seq[0])

    monkeypatch.setattr(random, "choice", choose_mana_shield_if_available)

    jester.mana.max = 100
    jester.mana.current = 19
    assert jester.options(target, [], None) != ("Use Skill", "Mana Shield")

    jester.mana.current = 20
    assert jester.options(target, [], None) == ("Use Skill", "Mana Shield")


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
    assert (second_action, second_ability) == ("Attack", None)


def test_action_stack_selection_records_delay_and_telegraph_metadata(monkeypatch):
    enemy = _make_enemy()
    target = _make_target(True)
    enemy.action_stack = [
        {
            "ability": "Disarm",
            "priority": ActionPriority.HIGH,
            "delay": 2,
            "telegraph": "raising a hook to catch the weapon",
        },
        {"ability": "Attack", "priority": ActionPriority.NORMAL},
    ]

    monkeypatch.setattr(random, "choice", lambda seq: seq[0])

    action, ability = enemy.options(target, [], None)
    metadata = enemy.get_last_action_metadata()

    assert (action, ability) == ("Use Skill", "Disarm")
    assert metadata == {
        "ability": "Disarm",
        "priority": ActionPriority.HIGH,
        "delay": 2,
        "telegraph": "raising a hook to catch the weapon",
        "from_action_stack": True,
    }


def test_action_stack_metadata_clears_on_fallback_selection(monkeypatch):
    enemy = _make_enemy()
    target = _make_target(True)
    enemy.last_action_stack_entry = {"ability": "Disarm", "delay": "bad"}
    enemy.action_stack = []

    monkeypatch.setattr(random, "choice", lambda seq: seq[0])

    action, ability = enemy.options(target, [], None)

    assert (action, ability) == ("Attack", None)
    assert enemy.get_last_action_metadata() == {
        "ability": None,
        "priority": None,
        "delay": 0,
        "telegraph": None,
        "from_action_stack": False,
    }
