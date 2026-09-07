"""Progression value objects, level curves, and shared constants."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

MAX_PLAYER_LEVEL = 100
XP_CURVE_COEFFICIENT = 9.186159389176172
PRIMARY_ATTRIBUTES = (
    "strength",
    "intel",
    "wisdom",
    "con",
    "charisma",
    "dex",
)

RATING_PAYLOADS = {
    "Attack": "attack",
    "Magic": "magic",
    "Defense": "defense",
    "Magic Defense": "magic_def",
}

RESOURCE_NODE_AMOUNTS = {
    1: 25,
    2: 50,
    3: 100,
}


class NodeKind(str, Enum):
    """Kinds of purchases supported by an ability tree."""

    ABILITY = "ability"
    TALENT = "talent"
    RATING = "rating"
    HEALTH = "health"
    MANA = "mana"
    PROMOTION = "promotion"


class NodeState(str, Enum):
    """Availability state rendered by Pygame and inspected by headless tools."""

    OWNED = "owned"
    AVAILABLE = "available"
    BLOCKED = "blocked"
    CLOSED = "closed"


@dataclass
class ProgressionState:
    """Persistent flat-progression state for a player."""

    level: int = 1
    total_xp: int = 0
    unspent_points: int = 0
    unspent_attribute_points: int = 0
    purchased_node_ids: set[str] = field(default_factory=set)
    trained_attributes: dict[str, int] = field(default_factory=dict)
    ability_ranks: dict[str, int] = field(default_factory=dict)
    completed_trees: set[str] = field(default_factory=set)
    chosen_promotions: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe representation."""
        return {
            "level": self.level,
            "total_xp": self.total_xp,
            "unspent_points": self.unspent_points,
            "unspent_attribute_points": self.unspent_attribute_points,
            "purchased_node_ids": sorted(self.purchased_node_ids),
            "trained_attributes": dict(self.trained_attributes),
            "ability_ranks": dict(self.ability_ranks),
            "completed_trees": sorted(self.completed_trees),
            "chosen_promotions": dict(self.chosen_promotions),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProgressionState":
        """Restore a progression state from save data."""
        level = max(1, min(MAX_PLAYER_LEVEL, int(data.get("level", 1))))
        trained_attributes = {
            str(name): max(0, int(amount))
            for name, amount in data.get("trained_attributes", {}).items()
        }
        unspent_attribute_points = max(
            0,
            int(data.get("unspent_attribute_points", 0)),
        )
        unspent_points = max(0, int(data.get("unspent_points", 0)))
        return cls(
            level=level,
            total_xp=max(0, int(data.get("total_xp", 0))),
            unspent_points=unspent_points,
            unspent_attribute_points=unspent_attribute_points,
            purchased_node_ids=set(data.get("purchased_node_ids", ())),
            trained_attributes=trained_attributes,
            ability_ranks={
                str(name): max(1, int(rank)) for name, rank in data.get("ability_ranks", {}).items()
            },
            completed_trees=set(data.get("completed_trees", ())),
            chosen_promotions={
                str(source): str(target)
                for source, target in data.get("chosen_promotions", {}).items()
            },
        )


@dataclass(frozen=True)
class AbilityTreeNode:
    """One immutable purchase in a class tree."""

    id: str
    tree_id: str
    kind: NodeKind
    lane: str
    position: tuple[float, int]
    icon_key: str
    prerequisites: tuple[str, ...] = ()
    payload: dict[str, Any] = field(default_factory=dict)
    cost: int = 1

    @property
    def name(self) -> str:
        """Return the player-facing node label."""
        return str(self.payload.get("name", self.id))


def prerequisite_groups(node: AbilityTreeNode) -> tuple[tuple[str, ...], ...]:
    """Return conjunctive groups whose members are alternative prerequisites."""
    authored_groups = node.payload.get("prerequisite_groups")
    if authored_groups:
        return tuple(tuple(str(node_id) for node_id in group) for group in authored_groups)
    if node.payload.get("prerequisite_mode", "all") == "any":
        return (tuple(node.prerequisites),) if node.prerequisites else ()
    return tuple((node_id,) for node_id in node.prerequisites)


@dataclass(frozen=True)
class AbilityTree:
    """Validated class-owned progression tree."""

    id: str
    class_name: str
    stage: int
    branches: tuple[str, ...]
    nodes: tuple[AbilityTreeNode, ...]


@dataclass(frozen=True)
class NodeStatus:
    """A tree node paired with its current availability."""

    node: AbilityTreeNode
    state: NodeState
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class GrowthResult:
    """Permanent random growth from one global level."""

    health: int
    mana: int
    attack: int
    defense: int
    magic: int
    magic_defense: int


@dataclass(frozen=True)
class LevelUpResult:
    """Result of a potentially multi-level XP award."""

    experience_awarded: int
    old_level: int
    new_level: int
    points_awarded: int
    growth: tuple[GrowthResult, ...]
    reached_max_level: bool
    attribute_points_awarded: int = 0


@dataclass(frozen=True)
class PurchaseResult:
    """Result of a point purchase."""

    success: bool
    message: str
    node_id: str | None = None
    points_remaining: int = 0
    promoted_to: str | None = None
    removed_equipment: tuple[str, ...] = ()


@dataclass(frozen=True)
class PromotionPreview:
    """Information required for a permanent promotion confirmation."""

    node_id: str
    source_class: str
    target_class: str
    level_requirement: int
    requirements: dict[str, int]
    bonuses: dict[str, int]
    equipment_conflicts: tuple[str, ...]
    warning: str


def experience_for_level(level: int) -> int:
    """Return XP needed to advance from ``level`` to the next global level."""
    if level >= MAX_PLAYER_LEVEL:
        return 0
    normalized = max(1, int(level))
    return round(25 + XP_CURVE_COEFFICIENT * ((normalized - 1) ** 2))


def cumulative_experience_for_level(level: int) -> int:
    """Return total XP required to have reached ``level``."""
    normalized = max(1, min(MAX_PLAYER_LEVEL, int(level)))
    return sum(experience_for_level(current) for current in range(1, normalized))


def progression_points_through_level(level: int) -> int:
    """Return total points earned at creation and on even-numbered levels."""
    normalized = max(1, min(MAX_PLAYER_LEVEL, int(level)))
    return 1 + (normalized // 2)


def attribute_points_through_level(level: int) -> int:
    """Return total primary-attribute points earned every four levels."""
    normalized = max(1, min(MAX_PLAYER_LEVEL, int(level)))
    return normalized // 4


def class_tier(player: Any) -> int:
    """Return promotion depth independently from global player level."""
    form_snapshot = getattr(player, "_normal_form_snapshot", None)
    current_class = (
        form_snapshot.get("cls")
        if isinstance(form_snapshot, dict)
        else getattr(player, "cls", None)
    )
    return max(
        1,
        min(3, int(getattr(current_class, "pro_level", 1))),
    )


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
