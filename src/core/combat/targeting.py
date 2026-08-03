"""Targeting contracts shared by abilities and the battle engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TargetScope(str, Enum):
    """Canonical set of combat action target shapes."""

    NONE = "none"
    SELF = "self"
    SINGLE_ENEMY = "single_enemy"
    ALL_ENEMIES = "all_enemies"


class TargetLossPolicy(str, Enum):
    """How a committed action behaves when its original target is lost."""

    LOCKED = "locked"
    RETARGET_FOCUS = "retarget_focus"
    SNAPSHOT_ROSTER = "snapshot_roster"


class ActionValidationCode(str, Enum):
    """Machine-readable reason an action intent was rejected."""

    MISSING_TARGET = "missing_target"
    UNKNOWN_TARGET = "unknown_target"
    UNAVAILABLE_TARGET = "dead_or_resolved_target"
    WRONG_TARGET_COUNT = "wrong_target_count"
    WRONG_TARGET_SCOPE = "wrong_target_scope"
    ENEMY_AREA_UNSUPPORTED = "enemy_area_unsupported"


@dataclass(frozen=True)
class ActionIntent:
    """Immutable player or AI action request; the engine owns the actor."""

    action: str
    choice: str | None = None
    target_ids: tuple[str, ...] = ()
