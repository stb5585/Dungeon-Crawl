#!/usr/bin/env python3
"""Focused event-bus infrastructure coverage."""

from __future__ import annotations

from src.core.events.event_bus import EventBus, EventType, GameEvent


def test_unsubscribing_during_emit_does_not_skip_other_subscribers():
    bus = EventBus()
    received: list[str] = []

    def first(event: GameEvent) -> None:
        received.append(f"first:{event.data['value']}")
        bus.unsubscribe(EventType.ATTACK, first)

    def second(event: GameEvent) -> None:
        received.append(f"second:{event.data['value']}")

    bus.subscribe(EventType.ATTACK, first)
    bus.subscribe(EventType.ATTACK, second)

    bus.emit_simple(EventType.ATTACK, {"value": 1})
    bus.emit_simple(EventType.ATTACK, {"value": 2})

    assert received == ["first:1", "second:1", "second:2"]


def test_event_bus_diagnostics_report_history_and_subscribers():
    bus = EventBus(max_history=2)
    bus.subscribe(EventType.ATTACK, lambda _event: None)

    bus.emit_simple(EventType.ATTACK, {"turn": 1})
    bus.emit_simple(EventType.DEFEND, {"turn": 2})
    bus.emit_simple(EventType.ATTACK, {"turn": 3})

    diagnostics = bus.get_diagnostics()

    assert diagnostics["history_size"] == 2
    assert diagnostics["max_history"] == 2
    assert diagnostics["history_full"] is True
    assert diagnostics["history_counts"] == {"DEFEND": 1, "ATTACK": 1}
    assert diagnostics["subscriber_counts"] == {"ATTACK": 1}
