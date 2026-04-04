#!/usr/bin/env python3
"""Focused coverage for queue-oriented curses battle helpers."""

from __future__ import annotations

from types import SimpleNamespace

from src.core.combat.action_queue import ActionPriority, ActionType, ScheduledAction
from src.ui_curses import enhanced_manager


class FakeQueue:
    def __init__(self):
        self.scheduled = []

    def schedule(self, **kwargs):
        self.scheduled.append(kwargs)


class Actor:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def _make_manager():
    manager = enhanced_manager.EnhancedBattleManager.__new__(enhanced_manager.EnhancedBattleManager)
    manager.use_queue = True
    manager.action_queue = FakeQueue()
    manager.pending_actions = {}
    manager.charging_actions = {}
    manager.printed = []
    manager.print_text = lambda text: manager.printed.append(text)
    manager.execute_action = lambda action, choice=None: manager.printed.append((action, choice))
    player = Actor(
        name="Hero",
        spellbook={"Spells": {}, "Skills": {}},
        status_effects={"Berserk": SimpleNamespace(active=False)},
        class_effects={"Jump": SimpleNamespace(active=False)},
        effects=lambda: "",
        is_alive=lambda: True,
        check_active=lambda: (True, ""),
        incapacitated=lambda: False,
        summons={},
    )
    enemy = Actor(
        name="Goblin",
        spellbook={"Skills": {}},
        effects=lambda: "",
        is_alive=lambda: True,
        check_active=lambda: (True, ""),
        options=lambda player, actions, tile: ("Attack", None),
        incapacitated=lambda: False,
        status_effects={"Sleep": SimpleNamespace(active=False), "Stun": SimpleNamespace(active=False)},
        physical_effects={"Prone": SimpleNamespace(active=False)},
    )
    manager.engine = SimpleNamespace(player=player, enemy=enemy, tile="tile", logger=SimpleNamespace(next_turn=lambda: None), player_has_sight=lambda: True, flee=False)
    manager.summon = Actor(name="Wolf", is_alive=lambda: True, incapacitated=lambda: False)
    manager.summon_active = True
    manager.available_actions = ["Attack", "Use Skill"]
    manager.attacker = player
    manager.defender = enemy
    manager.charging_ability = None
    manager.battle_ui = SimpleNamespace(navigate_menu=lambda: "Attack")
    manager.battle_popup = SimpleNamespace(update_options=lambda *args, **kwargs: None, navigate_popup=lambda: "Go Back")
    return manager


def test_enhanced_manager_helper_methods(monkeypatch):
    manager = _make_manager()
    manager.engine.player_has_sight = lambda: True

    assert manager._get_telegraph_message("Meteor") == "Goblin is preparing Meteor!"
    manager.engine.player_has_sight = lambda: False
    assert manager._get_telegraph_message("Meteor") == "Goblin is preparing something..."

    skill = SimpleNamespace(charging=True)
    manager.charging_ability = (manager.player_char, "Charge", skill)
    manager.player_char.spellbook["Skills"]["Charge"] = skill
    assert manager._get_active_charging_skill(manager.player_char) == ("Charge", skill)

    assert manager._get_action_properties("Attack", None) == (ActionPriority.NORMAL, 0, ActionType.ATTACK)
    assert manager._get_action_properties("Use Skill", "Quick Jab") == (ActionPriority.HIGH, 0, ActionType.SKILL)
    assert manager._get_action_properties("Flee", None) == (ActionPriority.HIGH, 0, ActionType.FLEE)
    manager.player_char.spellbook["Spells"]["Meteor"] = SimpleNamespace(cost=25)
    assert manager._get_action_properties("Cast Spell", "Meteor") == (ActionPriority.NORMAL, 1, ActionType.SPELL)

    callback = manager._create_action_callback("Attack", "Slash")
    callback(actor=manager.player_char, target=manager.enemy)
    assert manager.attacker == manager.player_char
    assert manager.defender == manager.enemy
    assert manager.printed[-1] == ("Attack", "Slash")


def test_enhanced_manager_updates_and_scheduling(monkeypatch):
    manager = _make_manager()
    manager.engine.player_has_sight = lambda: True
    manager.render_screen = lambda: None

    manager.charging_actions = {
        manager.enemy: ("Meteor", 2),
        manager.player_char: ("Charge", 1),
    }
    manager._update_charging_actions()
    assert manager.charging_actions[manager.enemy] == ("Meteor", 1)
    assert manager.player_char not in manager.charging_actions
    assert "preparing Meteor" in manager.printed[-1]

    manager.player_char.spellbook["Skills"]["Charge"] = SimpleNamespace(charging=True)
    manager.charging_ability = (manager.player_char, "Charge", manager.player_char.spellbook["Skills"]["Charge"])
    manager._schedule_player_action()
    assert manager.action_queue.scheduled[-1]["choice"] == "Charge"

    manager.action_queue.scheduled.clear()
    manager.charging_ability = None
    manager.player_char.effects = lambda: "Poison"
    manager.player_char.check_active = lambda: (False, "Sleep")
    manager._schedule_player_action()
    assert "Poison" in manager.printed
    assert "Sleep" in manager.printed
    assert manager.action_queue.scheduled[-1]["action_type"] == ActionType.SPECIAL

    manager.action_queue.scheduled.clear()
    manager.player_char.effects = lambda: ""
    manager.player_char.check_active = lambda: (True, "")
    manager.player_char.status_effects["Berserk"].active = True
    manager._schedule_player_action()
    assert manager.action_queue.scheduled[-1]["action"] == "Attack"

    manager.action_queue.scheduled.clear()
    manager.player_char.status_effects["Berserk"].active = False
    manager.player_char.class_effects["Jump"].active = True
    manager.player_char.spellbook["Skills"] = {"Big Jump": object()}
    manager._schedule_player_action()
    assert manager.action_queue.scheduled[-1]["choice"] == "Big Jump"

    manager.action_queue.scheduled.clear()
    manager.player_char.class_effects["Jump"].active = False
    manager.battle_ui.navigate_menu = lambda: "Attack"
    manager._schedule_player_action()
    assert manager.action_queue.scheduled[-1]["action"] == "Attack"

    manager.action_queue.scheduled.clear()
    manager.charging_actions.clear()
    manager.charging_ability = None
    manager.enemy.effects = lambda: "Burn"
    manager.enemy.check_active = lambda: (False, "Stun")
    manager._schedule_enemy_action()
    assert "Burn" in manager.printed
    assert "Stun" in manager.printed
    assert manager.action_queue.scheduled[-1]["action_type"] == ActionType.SPECIAL

    manager.action_queue.scheduled.clear()
    manager.enemy.check_active = lambda: (True, "")
    manager.enemy.spellbook["Skills"]["Charge"] = SimpleNamespace(charging=True)
    manager.charging_ability = (manager.enemy, "Charge", manager.enemy.spellbook["Skills"]["Charge"])
    manager._schedule_enemy_action()
    assert manager.action_queue.scheduled[-1]["choice"] == "Charge"

    manager.action_queue.scheduled.clear()
    manager.charging_ability = None
    manager.enemy.options = lambda *_args: ("Use Skill", "Quick Stab")
    manager._schedule_enemy_action()
    assert manager.action_queue.scheduled[-1]["priority"] == ActionPriority.HIGH

    manager.action_queue.scheduled.clear()
    manager._schedule_summon_action()
    assert manager.action_queue.scheduled[-1]["target"] == manager.enemy


def test_enhanced_manager_executes_scheduled_actions_and_after_turn(monkeypatch):
    manager = _make_manager()
    logger_calls = []
    manager.engine.tile = SimpleNamespace(available_actions=lambda _player: ["Attack", "Flee"])
    manager.engine.logger = SimpleNamespace(next_turn=lambda: logger_calls.append(True))
    manager.summon = SimpleNamespace(name="Wolf", is_alive=lambda: False)
    manager.summon_active = True
    manager.enemy.is_alive = lambda: False
    manager.enemy.special_effects = lambda _player: "Meteor falls"
    manager.after_turn()
    assert "Wolf has been slain.\n" in manager.printed
    assert "Meteor falls" in manager.printed
    assert manager.summon_active is False
    assert manager.summon is None
    assert logger_calls == [True]

    actor = Actor(
        name="Hero",
        incapacitated=lambda: True,
        status_effects={"Sleep": SimpleNamespace(active=True), "Stun": SimpleNamespace(active=False)},
        physical_effects={"Prone": SimpleNamespace(active=True)},
        stats=SimpleNamespace(dex=5),
    )
    scheduled = ScheduledAction(actor=actor, action_type=ActionType.ATTACK, target=None, priority=ActionPriority.NORMAL, callback=lambda **kwargs: None)
    manager._execute_scheduled_action(scheduled)
    assert "asleep and prone" in manager.printed[-1]

    actor = Actor(
        name="Hero",
        incapacitated=lambda: False,
        status_effects={"Sleep": SimpleNamespace(active=False), "Stun": SimpleNamespace(active=False)},
        physical_effects={"Prone": SimpleNamespace(active=False)},
        stats=SimpleNamespace(dex=5),
    )
    callback_calls = []
    scheduled = ScheduledAction(
        actor=actor,
        action_type=ActionType.ATTACK,
        target=None,
        priority=ActionPriority.NORMAL,
        callback=lambda **kwargs: callback_calls.append(kwargs),
    )
    manager.engine.player = actor
    manager.summon = SimpleNamespace(name="Wolf", is_alive=lambda: True)
    manager._execute_scheduled_action(scheduled)
    assert callback_calls[-1]["target"] == manager.enemy


def test_enhanced_manager_process_turn_and_additional_after_turn_paths(monkeypatch):
    manager = _make_manager()
    manager.engine.turn_count = 4
    emitted = []
    monkeypatch.setattr(
        enhanced_manager,
        "get_event_bus",
        lambda: SimpleNamespace(emit=lambda event: emitted.append(event)),
    )
    monkeypatch.setattr(
        enhanced_manager,
        "create_combat_event",
        lambda event_type, **kwargs: (event_type, kwargs),
    )
    monkeypatch.setattr(
        enhanced_manager,
        "EventType",
        SimpleNamespace(TURN_START="turn_start", TURN_END="turn_end"),
    )

    ready_actions = iter([False, True, False])
    queue_actions = iter([SimpleNamespace(actor=manager.player_char, target=manager.enemy, callback=lambda **kwargs: None, params={})])
    manager.action_queue = SimpleNamespace(
        has_ready_actions=lambda: next(ready_actions),
        get_next_action=lambda: next(queue_actions, None),
        next_round=lambda: emitted.append("next_round"),
    )
    calls = []
    manager.before_turn = lambda: calls.append("before")
    manager._update_charging_actions = lambda: calls.append("update")
    manager._schedule_player_action = lambda: calls.append("player")
    manager._schedule_enemy_action = lambda: calls.append("enemy")
    manager._schedule_summon_action = lambda: calls.append("summon")
    manager._execute_scheduled_action = lambda action: calls.append(("exec", action.actor.name))
    manager.after_turn = lambda: calls.append("after")
    manager.player_char.is_alive = lambda: True
    manager.enemy.is_alive = lambda: True
    manager.engine.flee = False

    manager.process_turn()
    assert emitted[0][0] == "turn_start"
    assert emitted[1] == "next_round"
    assert emitted[2][0] == "turn_end"
    assert calls == ["before", "update", "player", "enemy", "summon", ("exec", "Hero"), "after"]

    base_calls = []
    monkeypatch.setattr("src.ui_curses.battle.BattleManager.process_turn", lambda self: base_calls.append("base"))
    manager.use_queue = False
    manager.process_turn()
    assert base_calls == ["base"]

    manager = _make_manager()
    logger_calls = []
    manager.engine.logger = SimpleNamespace(next_turn=lambda: logger_calls.append(True), flee=True)
    manager.engine.flee = True
    manager.engine.tile = SimpleNamespace(available_actions=lambda _player: ["Attack"])
    manager.summon = Actor(name="Wolf", is_alive=lambda: True, incapacitated=lambda: False)
    manager.summon_active = True
    manager.after_turn()
    assert logger_calls == [True]
    assert manager.available_actions == ["Attack", "Use Skill"]

    manager = _make_manager()
    manager.engine.tile = SimpleNamespace(available_actions=lambda _player: ["Attack"])
    manager.engine.logger = SimpleNamespace(next_turn=lambda: logger_calls.append("alive"))
    manager.enemy.is_alive = lambda: True
    manager.summon = Actor(name="Wolf", is_alive=lambda: True, incapacitated=lambda: False)
    manager.summon_active = True
    manager.after_turn()
    assert "Recall" in manager.available_actions
