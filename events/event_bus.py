"""
Event System for Dungeon Crawl

This module provides an event-driven architecture to decouple game logic from presentation.
Events are emitted by the game engine and can be consumed by different presenters
(terminal, GUI, web, etc.) without modifying core game code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from character import Character
    from combat_result import CombatResult


class EventType(Enum):
    """Types of events that can be emitted during gameplay."""
    
    # Combat Events
    COMBAT_START = auto()
    COMBAT_END = auto()
    TURN_START = auto()
    TURN_END = auto()
    ROUND_START = auto()
    ROUND_END = auto()
    
    # Action Events
    ATTACK = auto()
    SPELL_CAST = auto()
    SKILL_USE = auto()
    ITEM_USE = auto()
    DEFEND = auto()
    FLEE_ATTEMPT = auto()
    
    # Damage Events
    DAMAGE_DEALT = auto()
    DAMAGE_TAKEN = auto()
    HEALING_DONE = auto()
    CRITICAL_HIT = auto()
    MISS = auto()
    DODGE = auto()
    BLOCK = auto()
    
    # Status Events
    STATUS_APPLIED = auto()
    STATUS_REMOVED = auto()
    STATUS_TICK = auto()
    BUFF_APPLIED = auto()
    DEBUFF_APPLIED = auto()
    
    # Character Events
    CHARACTER_DEATH = auto()
    LEVEL_UP = auto()
    STAT_CHANGE = auto()
    HP_CHANGE = auto()
    MP_CHANGE = auto()
    
    # UI Events
    MENU_OPEN = auto()
    MENU_CLOSE = auto()
    MESSAGE_DISPLAY = auto()
    CHOICE_REQUIRED = auto()
    
    # World Events
    MOVE = auto()
    INTERACT = auto()
    ITEM_PICKUP = auto()
    ITEM_DROP = auto()
    QUEST_UPDATE = auto()


@dataclass
class GameEvent:
    """
    Base class for all game events.
    
    Attributes:
        type: The type of event
        timestamp: When the event occurred (game time or real time)
        data: Event-specific data
        source: The source of the event (e.g., which character)
        metadata: Additional contextual information
    """
    type: EventType
    timestamp: float
    data: dict[str, Any] = field(default_factory=dict)
    source: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"{self.type.name}: {self.data}"


@dataclass
class CombatEvent(GameEvent):
    """
    Specialized event for combat actions.
    
    Additional attributes specific to combat.
    """
    actor: Character | None = None
    target: Character | None = None
    result: CombatResult | None = None
    
    def __post_init__(self):
        """Populate data dict from combat-specific fields."""
        if self.actor:
            self.data['actor'] = self.actor.name
        if self.target:
            self.data['target'] = self.target.name
        if self.result:
            self.data['result'] = self.result.to_dict()


class EventBus:
    """
    Central event dispatcher for the game.
    
    Implements the Observer pattern - components can subscribe to specific
    event types and receive callbacks when those events are emitted.
    """
    
    def __init__(self):
        self._subscribers: dict[EventType, list[Callable]] = {}
        self._history: list[GameEvent] = []
        self._enabled: bool = True
    
    def subscribe(self, event_type: EventType, callback: Callable[[GameEvent], None]) -> None:
        """
        Subscribe to a specific event type.
        
        Args:
            event_type: The type of event to listen for
            callback: Function to call when event is emitted
                     Should accept a GameEvent as its only parameter
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: The event type to unsubscribe from
            callback: The callback to remove
        """
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
    
    def emit(self, event: GameEvent) -> None:
        """
        Emit an event to all subscribers.
        
        Args:
            event: The event to emit
        """
        if not self._enabled:
            return
        
        # Store in history
        self._history.append(event)
        
        # Notify subscribers
        if event.type in self._subscribers:
            for callback in self._subscribers[event.type]:
                try:
                    callback(event)
                except Exception as e:
                    # Log error but don't crash the game
                    print(f"Error in event callback: {e}")
    
    def emit_simple(
        self,
        event_type: EventType,
        data: dict[str, Any] = None,
        source: Any = None
    ) -> None:
        """
        Convenience method to emit a simple event without creating an object first.
        
        Args:
            event_type: Type of event
            data: Event data
            source: Event source
        """
        import time
        event = GameEvent(
            type=event_type,
            timestamp=time.time(),
            data=data or {},
            source=source
        )
        self.emit(event)
    
    def clear_history(self) -> None:
        """Clear the event history."""
        self._history.clear()
    
    def get_history(self, event_type: EventType | None = None) -> list[GameEvent]:
        """
        Get event history, optionally filtered by type.
        
        Args:
            event_type: If provided, only return events of this type
            
        Returns:
            List of events
        """
        if event_type is None:
            return self._history.copy()
        return [e for e in self._history if e.type == event_type]
    
    def enable(self) -> None:
        """Enable event processing."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable event processing (events will not be emitted)."""
        self._enabled = False
    
    def clear_subscribers(self) -> None:
        """Remove all subscribers."""
        self._subscribers.clear()


# Global event bus instance
# This can be imported and used throughout the codebase
_global_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def reset_event_bus() -> None:
    """Reset the global event bus (useful for testing)."""
    global _global_event_bus
    _global_event_bus = EventBus()


# Event creation helpers
def create_combat_event(
    event_type: EventType,
    actor: Character,
    target: Character | None = None,
    result: CombatResult | None = None,
    **kwargs
) -> CombatEvent:
    """
    Helper to create combat events.
    
    Args:
        event_type: Type of combat event
        actor: The acting character
        target: The target character (optional)
        result: Combat result data (optional)
        **kwargs: Additional data
        
    Returns:
        CombatEvent instance
    """
    import time
    return CombatEvent(
        type=event_type,
        timestamp=time.time(),
        actor=actor,
        target=target,
        result=result,
        data=kwargs
    )


def create_ui_event(
    event_type: EventType,
    message: str = "",
    choices: list[str] = None,
    **kwargs
) -> GameEvent:
    """
    Helper to create UI events.
    
    Args:
        event_type: Type of UI event
        message: Message to display
        choices: Available choices (for CHOICE_REQUIRED)
        **kwargs: Additional data
        
    Returns:
        GameEvent instance
    """
    import time
    data = kwargs.copy()
    if message:
        data['message'] = message
    if choices:
        data['choices'] = choices
    
    return GameEvent(
        type=event_type,
        timestamp=time.time(),
        data=data
    )


# Example subscriber implementations
class ConsoleEventLogger:
    """
    Example event subscriber that logs events to console.
    Useful for debugging.
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._subscribe_all()
    
    def _subscribe_all(self) -> None:
        """Subscribe to all event types."""
        for event_type in EventType:
            self.event_bus.subscribe(event_type, self.log_event)
    
    def log_event(self, event: GameEvent) -> None:
        """Log an event to console."""
        print(f"[{event.timestamp:.2f}] {event.type.name}: {event.data}")


class CombatEventCollector:
    """
    Example subscriber that collects combat events for analysis.
    """
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.combat_events: list[CombatEvent] = []
        
        # Subscribe to combat events
        combat_event_types = [
            EventType.COMBAT_START,
            EventType.COMBAT_END,
            EventType.ATTACK,
            EventType.SPELL_CAST,
            EventType.DAMAGE_DEALT,
            EventType.CRITICAL_HIT,
        ]
        
        for event_type in combat_event_types:
            self.event_bus.subscribe(event_type, self.collect_event)
    
    def collect_event(self, event: GameEvent) -> None:
        """Collect a combat event."""
        if isinstance(event, CombatEvent):
            self.combat_events.append(event)
    
    def get_damage_total(self, character_name: str) -> int:
        """Get total damage dealt by a character."""
        total = 0
        for event in self.combat_events:
            if event.type == EventType.DAMAGE_DEALT:
                if event.actor and event.actor.name == character_name:
                    if 'damage' in event.data:
                        total += event.data['damage']
        return total
    
    def clear(self) -> None:
        """Clear collected events."""
        self.combat_events.clear()
