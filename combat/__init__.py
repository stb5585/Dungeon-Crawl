"""
Combat module for Dungeon Crawl.

This module contains the core combat mechanics, including:
- Action queue system for turn-based combat
- Battle management and flow control
- Combat logging and analytics
"""

from combat.action_queue import (
    ActionQueue,
    ActionPriority,
    ActionType,
    ScheduledAction,
    TurnManager,
    create_attack_action,
    create_spell_action,
)

# Note: EnhancedBattleManager imports are deferred to avoid circular dependencies
# Import it directly: from combat.enhanced_manager import EnhancedBattleManager

__all__ = [
    'ActionQueue',
    'ActionPriority',
    'ActionType',
    'ScheduledAction',
    'TurnManager',
    'create_attack_action',
    'create_spell_action',
]
