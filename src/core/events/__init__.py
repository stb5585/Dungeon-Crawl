"""
Events module for The Forsaken Tenet.

Provides event-driven architecture for decoupling game logic from presentation.
"""

from .event_bus import (
    CombatEvent,
    CombatEventCollector,
    ConsoleEventLogger,
    EventBus,
    EventDispatchFailure,
    EventType,
    GameEvent,
    create_combat_event,
    create_ui_event,
    get_event_bus,
    reset_event_bus,
)

__all__ = [
    "EventType",
    "GameEvent",
    "CombatEvent",
    "EventDispatchFailure",
    "EventBus",
    "get_event_bus",
    "reset_event_bus",
    "create_combat_event",
    "create_ui_event",
    "ConsoleEventLogger",
    "CombatEventCollector",
]
