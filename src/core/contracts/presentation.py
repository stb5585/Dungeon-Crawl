"""UI-agnostic timeline, visibility, and combat-resource presentation models."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class TimelineEntry:
    """One predicted normal actor opportunity."""

    actor_id: str
    display_label: str
    ready_at: float
    forced_action_id: str | None = None

    def __post_init__(self) -> None:
        if not self.actor_id:
            raise ValueError("actor_id must not be empty")
        if not isfinite(self.ready_at) or self.ready_at < 0:
            raise ValueError("ready_at must be finite and non-negative")


@dataclass(frozen=True)
class VisibilityState:
    """Runtime concealment and reveal observations for one combatant."""

    actor_id: str
    concealed: bool = False
    revealed_by: frozenset[str] = frozenset()
    concealment_bonus: float = 0.0

    def __post_init__(self) -> None:
        if not self.actor_id:
            raise ValueError("actor_id must not be empty")
        if self.concealment_bonus < 0:
            raise ValueError("concealment_bonus must not be negative")

    @property
    def revealed(self) -> bool:
        """Return whether any active source currently reveals the actor."""
        return bool(self.revealed_by)

    @property
    def hostile_single_target_legal(self) -> bool:
        """Return whether a hostile single-target action may select the actor."""
        return not self.concealed or self.revealed


@dataclass(frozen=True)
class CombatResourcePresentation:
    """One prioritized, text-complete combat resource row."""

    stable_key: str
    label: str
    priority: int
    icon_key: str
    value: int | None = None
    capacity: int | None = None
    state_text: str = ""
    ready: bool = False

    def __post_init__(self) -> None:
        if not self.stable_key or not self.label or not self.icon_key:
            raise ValueError("resource key, label, and icon key must not be empty")
        if self.value is not None and self.value < 0:
            raise ValueError("resource value must not be negative")
        if self.capacity is not None and self.capacity < 0:
            raise ValueError("resource capacity must not be negative")


@dataclass(frozen=True)
class EnvironmentalEffectPresentation:
    """One active world effect that must remain visible during play."""

    stable_key: str
    label: str
    detail: str
    icon_label: str

    def __post_init__(self) -> None:
        if not all((self.stable_key, self.label, self.detail, self.icon_label)):
            raise ValueError("environmental effect fields must not be empty")
