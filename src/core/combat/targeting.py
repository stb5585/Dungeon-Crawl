"""Targeting contracts shared by abilities and the battle engine."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from ..contracts.targeting import (
    TargetingPolicy,
)
from ..contracts.targeting import TargetLossPolicy as CanonicalTargetLossPolicy
from ..contracts.targeting import TargetScope as CanonicalTargetScope


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
    CONCEALED_TARGET = "concealed_target"
    CHARGE_NOT_READY = "charge_not_ready"
    CHARGE_PENDING = "charge_pending"
    NO_CHARGE_TO_CANCEL = "no_charge_to_cancel"
    FORCED_ACTION_REQUIRED = "forced_action_required"


@dataclass(frozen=True, init=False)
class ActionIntent:
    """Immutable ID-based action request; the engine owns the actor.

    The ``action`` keyword and :meth:`from_legacy` remain the public
    compatibility boundary for legacy command strings. Internal callers use
    ``action_id`` exclusively.
    """

    action_id: str
    choice: str | None
    target_ids: tuple[str, ...]

    def __init__(
        self,
        action_id: str | None = None,
        choice: str | None = None,
        target_ids: Iterable[str] = (),
        *,
        action: str | None = None,
    ) -> None:
        resolved_action_id = action_id if action_id is not None else action
        if resolved_action_id is None or not resolved_action_id:
            raise ValueError("action_id must not be empty")
        if action_id is not None and action is not None and action_id != action:
            raise ValueError("action and action_id cannot disagree")
        object.__setattr__(self, "action_id", resolved_action_id)
        object.__setattr__(self, "choice", choice)
        object.__setattr__(self, "target_ids", tuple(target_ids))

    @classmethod
    def from_legacy(
        cls,
        action: str,
        choice: str | None = None,
        target_ids: Iterable[str] = (),
    ) -> ActionIntent:
        """Adapt the former command/choice request shape at a public boundary."""
        return cls(action_id=action, choice=choice, target_ids=target_ids)


def canonical_targeting_policy(
    scope: TargetScope,
    loss_policy: TargetLossPolicy,
    *,
    hostile: bool = False,
) -> TargetingPolicy:
    """Adapt enemy-named runtime targeting values to canonical actor-relative values."""
    canonical_scope = {
        TargetScope.NONE: CanonicalTargetScope.NONE,
        TargetScope.SELF: CanonicalTargetScope.SELF,
        TargetScope.SINGLE_ENEMY: CanonicalTargetScope.SINGLE_OPPONENT,
        TargetScope.ALL_ENEMIES: CanonicalTargetScope.ALL_OPPONENTS,
    }[scope]
    canonical_loss_policy = CanonicalTargetLossPolicy(loss_policy.value)
    return TargetingPolicy(canonical_scope, canonical_loss_policy, hostile=hostile)


def legacy_target_scope(scope: CanonicalTargetScope) -> TargetScope:
    """Adapt a canonical actor-relative scope for unmigrated runtime callers."""
    return {
        CanonicalTargetScope.NONE: TargetScope.NONE,
        CanonicalTargetScope.SELF: TargetScope.SELF,
        CanonicalTargetScope.SINGLE_OPPONENT: TargetScope.SINGLE_ENEMY,
        CanonicalTargetScope.ALL_OPPONENTS: TargetScope.ALL_ENEMIES,
    }[scope]
