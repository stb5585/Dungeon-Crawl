"""Battle-engine phase and outcome value objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..combat_result import CombatResultGroup
from ..targeting import ActionIntent, ActionValidationCode

if TYPE_CHECKING:
    from ...character import Character


@dataclass
class PreTurnResult:
    """Result of pre-turn processing (status effects, activity check)."""
    effects_text: str = ""
    can_act: bool = True
    inactive_reason: str = ""
    # Exploding shield damage dealt to the defender during effects processing
    shield_explosion_damage: int = 0
    # True when the attacker died from their own effects (poison, DOT, bleed)
    died_from_effects: bool = False


@dataclass
class ForcedAction:
    """Represents an automatically-determined action (berserk, charging, jump)."""
    action: str = ""
    choice: str | None = None
    cancel_message: str = ""  # non-empty when a charging ability was cancelled


@dataclass
class ActionResult:
    """Result of executing a combat action."""
    message: str = ""
    fled: bool = False
    summon_started: bool = False
    summon_recalled: bool = False
    summon: Character | None = None
    committed: bool = True
    validation_code: ActionValidationCode | None = None
    combat_results: CombatResultGroup | None = None


@dataclass
class PostTurnResult:
    """Result of post-turn processing."""
    messages: list[str] = field(default_factory=list)
    defender_died: bool = False
    resurrected: bool = False
    summon_died: bool = False


@dataclass
class BattleOutcome:
    """Final result of a completed battle."""
    result: str = ""          # "victory", "defeat", "flee"
    winner: str | None = None
    message: str = ""         # Summary text (exp, loot, quests, etc.)
    level_up: bool = False
    boss: bool = False
    rewards_settled: bool = True
