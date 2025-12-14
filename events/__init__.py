"""
Events Module for Dungeon Crawl

Provides event-driven architecture for decoupling game logic from presentation.
"""

from events.event_bus import (
    EventType,
    GameEvent,
    CombatEvent,
    EventBus,
    get_event_bus,
    reset_event_bus,
    create_combat_event,
    create_ui_event,
    ConsoleEventLogger,
    CombatEventCollector,
)

__all__ = [
    'EventType',
    'GameEvent',
    'CombatEvent',
    'EventBus',
    'get_event_bus',
    'reset_event_bus',
    'create_combat_event',
    'create_ui_event',
    'ConsoleEventLogger',
    'CombatEventCollector',
]
