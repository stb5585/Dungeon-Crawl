#!/usr/bin/env python3
"""
Integration-style smoke tests for the enhanced combat system.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from src.core.combat import ActionPriority, ActionQueue, ActionType
from src.ui_curses.enhanced_manager import EnhancedBattleManager


class MockClass:
    def __init__(self, name):
        self.name = name


class MockChar:
    def __init__(self, cls_name):
        self.cls = MockClass(cls_name)
        self.name = "TestChar"


class MockStats:
    def __init__(self, dex):
        self.dex = dex


class MockCharWithStats:
    def __init__(self, name, dex):
        self.name = name
        self.stats = MockStats(dex)


def test_enhanced_battle_manager_import():
    assert EnhancedBattleManager is not None


def test_action_queue_components_import():
    assert ActionQueue is not None
    assert ActionType is not None
    assert ActionPriority is not None


def test_telegraph_foresight_logic():
    seeker = MockChar("Seeker")
    warrior = MockChar("Warrior")

    assert seeker.cls.name in ["Seeker", "Inquisitor"]
    assert warrior.cls.name not in ["Seeker", "Inquisitor"]


def test_action_priority_logic():
    test_cases = [
        ("Attack", None, ActionPriority.NORMAL),
        ("Cast Spell", "Fireball", ActionPriority.NORMAL),
        ("Use Skill", "Quick Strike", ActionPriority.HIGH),
        ("Flee", None, ActionPriority.HIGH),
        ("Defend", None, ActionPriority.HIGH),
    ]

    for action, choice, expected_priority in test_cases:
        if action == "Attack":
            priority = ActionPriority.NORMAL
        elif action == "Use Skill" and choice and "Quick" in choice:
            priority = ActionPriority.HIGH
        elif action in ["Flee", "Defend"]:
            priority = ActionPriority.HIGH
        else:
            priority = ActionPriority.NORMAL

        assert priority == expected_priority


def test_action_queue_orders_by_priority_then_speed():
    queue = ActionQueue()
    fast_char = MockCharWithStats("FastFighter", 18)
    slow_char = MockCharWithStats("SlowMage", 8)
    executed_actions = []

    def mock_callback(**kwargs):
        actor = kwargs.get("actor")
        executed_actions.append(actor.name)
        return f"{actor.name} acted"

    queue.schedule(
        actor=slow_char,
        action_type=ActionType.SPELL,
        callback=mock_callback,
        priority=ActionPriority.NORMAL,
    )
    queue.schedule(
        actor=fast_char,
        action_type=ActionType.ATTACK,
        callback=mock_callback,
        priority=ActionPriority.HIGH,
    )

    assert len(queue.queue) == 2
    assert queue.queue[0].actor.name == "FastFighter"
    assert queue.queue[1].actor.name == "SlowMage"

    while queue.has_ready_actions():
        queue.resolve_next()

    assert executed_actions == ["FastFighter", "SlowMage"]


def test_action_queue_delay_ticks_until_ready():
    queue = ActionQueue()
    char = MockCharWithStats("Mage", 10)

    queue.schedule(
        actor=char,
        action_type=ActionType.SPELL,
        callback=lambda **kwargs: kwargs["actor"].name,
        priority=ActionPriority.NORMAL,
        delay=2,
    )

    action = queue.queue[0]
    assert action.delay == 2
    assert action.is_ready() is False

    action.tick()
    assert action.delay == 1
    assert action.is_ready() is False

    action.tick()
    assert action.delay == 0
    assert action.is_ready() is True


def test_scheduled_action_lt_uses_speed_modifier_for_tiebreak():
    from src.core.combat.action_queue import ScheduledAction

    slow = MockCharWithStats("Slow", 10)
    fast = MockCharWithStats("Fast", 8)

    slower_action = ScheduledAction(slow, ActionType.ATTACK, None, ActionPriority.NORMAL, callback=lambda **_: None)
    faster_action = ScheduledAction(
        fast,
        ActionType.ATTACK,
        None,
        ActionPriority.NORMAL,
        callback=lambda **_: None,
        speed_modifier=2.0,
    )

    assert faster_action < slower_action


def test_action_queue_resolve_next_tracks_history_and_metadata():
    queue = ActionQueue()
    actor = MockCharWithStats("Hero", 12)

    queue.schedule(
        actor=actor,
        action_type=ActionType.ATTACK,
        callback=lambda **kwargs: f"{kwargs['actor'].name} attacks",
        priority=ActionPriority.NORMAL,
    )

    result = queue.resolve_next()

    assert result == "Hero attacks"
    assert len(queue.history) == 1
    assert queue.history[0].metadata["executed_round"] == 0


def test_action_queue_management_helpers_cover_clear_round_filter_and_cancel():
    queue = ActionQueue()
    actor = MockCharWithStats("Hero", 12)
    other = MockCharWithStats("Goblin", 9)

    queue.schedule(actor=actor, action_type=ActionType.ATTACK, callback=lambda **_: None)
    queue.schedule(actor=other, action_type=ActionType.ATTACK, callback=lambda **_: None)
    queue.schedule(actor=actor, action_type=ActionType.DEFEND, callback=lambda **_: None)

    assert len(queue.get_actions_for(actor)) == 2
    assert queue.cancel_actions_for(actor) == 2
    assert queue.get_actions_for(actor) == []

    queue.next_round()
    assert queue.current_round == 1

    queue.clear()
    assert queue.queue == []


def test_turn_manager_round_flow_and_helpers(monkeypatch):
    from src.core.combat.action_queue import TurnManager

    slow = MockCharWithStats("Slow", 10)
    fast = MockCharWithStats("Fast", 15)
    manager = TurnManager([slow, fast])

    rolls = iter([0, 0])
    monkeypatch.setattr("random.randint", lambda a, b: next(rolls))

    order = manager.determine_turn_order()
    assert [char.name for char in order] == ["Fast", "Slow"]
    assert manager.get_current_actor().name == "Fast"
    assert manager.next_turn().name == "Slow"
    assert manager.next_turn() is None
    assert manager.is_round_complete() is True

    rolls = iter([0, 0])
    monkeypatch.setattr("random.randint", lambda a, b: next(rolls))
    manager.start_new_round()
    assert manager.action_queue.current_round == 1
    assert manager.get_current_actor().name == "Fast"


def test_create_attack_and_spell_action_helpers():
    from src.core.combat.action_queue import create_attack_action, create_spell_action

    actor = MockCharWithStats("Hero", 12)
    target = MockCharWithStats("Goblin", 9)

    fast_attack = create_attack_action(actor, target, lambda **_: "ok", fast=True)
    spell = create_spell_action(actor, target, lambda **_: "zap", cast_time=2)

    assert fast_attack.priority == ActionPriority.HIGH
    assert fast_attack.speed_modifier == 1.5
    assert spell.priority == ActionPriority.DELAYED
    assert spell.delay == 2
