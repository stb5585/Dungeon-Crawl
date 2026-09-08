"""
Combat module for The Forsaken Tenet.

This module contains the core combat mechanics, including:
- Action queue system for turn-based combat
- Battle management and flow control
- Combat logging and analytics
"""

from .action_interface import (
    SHORTCUT_SLOT_COUNT,
    SYSTEM_COMMANDS,
    CombatActionPresentation,
    CombatInterfaceSnapshot,
    ShortcutSlotPresentation,
    assign_shortcut,
    combat_interface_snapshot,
)
from .action_queue import (
    ActionPriority,
    ActionQueue,
    ActionType,
    ScheduledAction,
    TurnManager,
    create_attack_action,
    create_spell_action,
)
from .encounter import (
    CombatEncounter,
    EncounterEnemy,
    EnemyResolution,
    EnemyResolutionRecord,
)
from .targeting import (
    ActionIntent,
    ActionValidationCode,
    TargetLossPolicy,
    TargetScope,
)

# Note: EnhancedBattleManager imports are deferred to avoid circular dependencies
# Import it directly: from combat.enhanced_manager import EnhancedBattleManager

__all__ = [
    "ActionQueue",
    "ActionIntent",
    "CombatActionPresentation",
    "CombatInterfaceSnapshot",
    "ActionPriority",
    "ActionType",
    "ActionValidationCode",
    "ScheduledAction",
    "SHORTCUT_SLOT_COUNT",
    "SYSTEM_COMMANDS",
    "ShortcutSlotPresentation",
    "TurnManager",
    "create_attack_action",
    "create_spell_action",
    "CombatEncounter",
    "EncounterEnemy",
    "EnemyResolution",
    "EnemyResolutionRecord",
    "TargetLossPolicy",
    "TargetScope",
    "assign_shortcut",
    "combat_interface_snapshot",
]
