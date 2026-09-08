"""Actor-relative targeting value objects."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TargetScope(str, Enum):
    """Canonical target shapes expressed relative to the acting combatant."""

    NONE = "none"
    SELF = "self"
    SINGLE_OPPONENT = "single_opponent"
    ALL_OPPONENTS = "all_opponents"


class TargetLossPolicy(str, Enum):
    """How a committed action behaves when its original target is lost."""

    LOCKED = "locked"
    RETARGET_FOCUS = "retarget_focus"
    SNAPSHOT_ROSTER = "snapshot_roster"


@dataclass(frozen=True)
class TargetingPolicy:
    """Target scope and retention behavior for one action."""

    scope: TargetScope
    loss_policy: TargetLossPolicy
    hostile: bool = False

    def __post_init__(self) -> None:
        if self.scope is TargetScope.ALL_OPPONENTS:
            if self.loss_policy is not TargetLossPolicy.SNAPSHOT_ROSTER:
                raise ValueError("all-opponents actions must snapshot their roster")
        elif self.loss_policy is TargetLossPolicy.SNAPSHOT_ROSTER:
            raise ValueError("snapshot-roster is valid only for all-opponents actions")
