"""Flat level and point-based player progression.

This module is the only authority for player XP, progression purchases, and
promotion-node application.  Frontends should render the result objects rather
than duplicate progression rules.
"""

from __future__ import annotations

import copy
import math
import random
import re
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from dataclasses import replace
from enum import Enum
from typing import Any

from . import abilities
from .classes import classes_dict
from .constants import (
    LEVELUP_ATK_LUCK_FACTOR,
    LEVELUP_DEF_LUCK_FACTOR,
    LEVELUP_LUCK_DIVISOR_BASE,
    LEVELUP_LUCK_FACTOR_HP_MP,
    LEVELUP_MAG_LUCK_FACTOR,
    LEVELUP_MDEF_LUCK_FACTOR,
    LEVELUP_STAT_DIVISOR,
)
from .progression_manifest import (
    ABILITY_BRANCH_OVERRIDES,
    ABILITY_ICON_KEYS,
    ABILITY_ICON_OVERRIDES,
    ABILITY_NODE_NAME_OVERRIDES,
    AUTHORED_TREE_CLASSES,
    BASE_TREE_BRANCHES,
    BASE_TREE_RATING_NODES,
    BERSERKER_TREE_NODE_SPECS,
    CLASS_KIT_TALENTS,
    CLASS_STAT_GROUPS,
    CONJURER_CARRIED_NODE_IDS,
    CONJURER_CARRIED_NODE_POSITIONS,
    CONJURER_TREE_NODE_SPECS,
    EXTERNAL_ACQUISITION_ABILITIES,
    FIRST_PROMOTION_STAT_REQUIREMENT_OVERRIDES,
    DRAGOON_TREE_NODE_SPECS,
    CRUSADER_TREE_NODE_SPECS,
    DEMONOLOGIST_TREE_NODE_SPECS,
    GRANDMASTER_TREE_NODE_SPECS,
    LANCER_TREE_NODE_SPECS,
    KNIGHT_ENCHANTER_TREE_NODE_SPECS,
    MAGE_CARRIED_NODE_IDS,
    MAGE_CARRIED_NODE_POSITIONS,
    MAGE_PROMOTION_SPECS,
    MAGE_TREE_NODE_SPECS,
    PALADIN_TREE_NODE_SPECS,
    PROMOTED_TREE_PATHS,
    PROMOTED_TREE_PROMOTION_PATHS,
    SECOND_PROMOTION_STAT_REQUIREMENT_OVERRIDES,
    SHADOWCASTER_TREE_NODE_SPECS,
    SENTINEL_TREE_NODE_SPECS,
    SORCERER_TREE_NODE_SPECS,
    SPELLBLADE_TREE_NODE_SPECS,
    STAGE_SIZE_RANGES,
    STALWART_DEFENDER_TREE_NODE_SPECS,
    TALENT_KIT_EFFECTS,
    TREE_SIZE_OVERRIDES,
    TREE_LANES,
    WARRIOR_CONNECTOR_CHANNEL_OVERRIDES,
    WARRIOR_FLOATING_NODES,
    WARRIOR_NODE_LEVEL_REQUIREMENTS,
    WARRIOR_NODE_CROSS_REQUIREMENTS,
    WARRIOR_NODE_POSITION_OVERRIDES,
    WARRIOR_NODE_PREREQUISITE_OVERRIDES,
    WARRIOR_PATH_ROW_OFFSETS,
    WARRIOR_PROMOTION_CROSS_REQUIREMENTS,
    WARRIOR_TREE_PATHS,
    WARLOCK_TREE_NODE_SPECS,
    WEAPON_MASTER_TREE_NODE_SPECS,
    WIZARD_TREE_NODE_SPECS,
)


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


def progression_class_name(player: Any) -> str:
    """Return the permanent class whose progression tree should be displayed."""
    if getattr(player, "_transformed", False):
        permanent_name = getattr(player, "_normal_class_name", None)
        if permanent_name in ABILITY_TREES:
            return permanent_name
    return player.cls.name
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
        if "unspent_attribute_points" in data:
            unspent_attribute_points = max(
                0,
                int(data.get("unspent_attribute_points", 0)),
            )
            unspent_points = max(0, int(data.get("unspent_points", 0)))
        else:
            legacy_training_cost = sum(trained_attributes.values())
            unspent_attribute_points = max(
                0,
                attribute_points_through_level(level)
                - legacy_training_cost,
            )
            unspent_points = (
                max(0, int(data.get("unspent_points", 0)))
                + legacy_training_cost
            )
        purchased_node_ids = set(data.get("purchased_node_ids", ()))
        legacy_reflection_id = "sentinel.ability.spell-reflection"
        if legacy_reflection_id in purchased_node_ids:
            purchased_node_ids.discard(legacy_reflection_id)
            purchased_node_ids.add("sentinel.ability.deflect-spell")
        return cls(
            level=level,
            total_xp=max(0, int(data.get("total_xp", 0))),
            unspent_points=unspent_points,
            unspent_attribute_points=unspent_attribute_points,
            purchased_node_ids=purchased_node_ids,
            trained_attributes=trained_attributes,
            ability_ranks={
                str(name): max(1, int(rank))
                for name, rank in data.get("ability_ranks", {}).items()
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
    return max(
        1,
        min(3, int(getattr(getattr(player, "cls", None), "pro_level", 1))),
    )


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _flatten_classes() -> tuple[
    dict[str, tuple[type, int, str | None]],
    dict[str, tuple[str, ...]],
]:
    details: dict[str, tuple[type, int, str | None]] = {}
    children: dict[str, tuple[str, ...]] = {}

    def visit(entry: dict[str, Any], stage: int, parent: str | None) -> None:
        class_ctor = entry["class"]
        class_name = class_ctor().name
        details[class_name] = (class_ctor, stage, parent)
        child_names = tuple(child["class"]().name for child in entry.get("pro", {}).values())
        children[class_name] = child_names
        for child in entry.get("pro", {}).values():
            visit(child, stage + 1, class_name)

    for base_entry in classes_dict.values():
        visit(base_entry, 1, None)
    return details, children


CLASS_DETAILS, CLASS_CHILDREN = _flatten_classes()


def effective_node_level_requirement(
    node: AbilityTreeNode,
    class_name: str,
) -> int:
    """Return a node's nonredundant level gate in the displayed class tree.

    Promotion already proves the player reached level 30 for a first-promotion
    class and level 60 for a terminal class. An ability authored below that
    floor therefore needs neither another runtime check nor requirement text
    when it is carried into the promoted tree.
    """
    required_level = int(node.payload.get("level_requirement", 0) or 0)
    if node.kind != NodeKind.ABILITY or required_level <= 0:
        return required_level
    class_details = CLASS_DETAILS.get(class_name)
    if class_details is None:
        return required_level
    stage = int(class_details[1])
    promotion_floor = {1: 1, 2: 30, 3: 60}.get(stage, 1)
    if required_level < promotion_floor:
        return 0
    return required_level


def _ability_entries(class_name: str) -> list[tuple[int, int, str, type, Any]]:
    entries: list[tuple[int, int, str, type, Any]] = []
    for source_order, (book, source) in enumerate(
        (("Spells", abilities.spell_dict), ("Skills", abilities.skill_dict))
    ):
        for raw_level, raw_abilities in source.get(class_name, {}).items():
            for ability_order, ability_ctor in enumerate(abilities.ability_classes_for(raw_abilities)):
                ability = ability_ctor()
                if ability.name in EXTERNAL_ACQUISITION_ABILITIES:
                    continue
                entries.append((
                    int(raw_level),
                    source_order * 100 + ability_order,
                    book,
                    ability_ctor,
                    ability,
                ))
    entries.sort(key=lambda row: (row[0], row[1], row[4].name))
    return entries


def _ability_icon_key(book: str, ability: Any) -> str:
    """Return the semantic icon shared by abilities of the same type."""
    override = ABILITY_ICON_OVERRIDES.get(ability.name)
    if override:
        return override
    normalized_name = ability.name.lower()
    if "transform" in normalized_name or "shapeshift" in normalized_name:
        return "spell_transform"
    if any(
        token in normalized_name
        for token in ("summon", "familiar", "invoke", "tame")
    ):
        return "spell_summon"
    subtype = str(getattr(ability, "subtyp", "") or "").strip().lower()
    if book == "Spells":
        spell_icons = {
            "death": "spell_shadow",
            "earth": "spell_earth",
            "electric": "spell_lightning",
            "fire": "spell_fire",
            "heal": "spell_heal",
            "holy": "spell_holy",
            "ice": "spell_ice",
            "illusion": "spell_illusion",
            "movement": "spell_movement",
            "non-elemental": "spell_arcane",
            "offensive": "spell_arcane",
            "poison": "spell_poison",
            "shadow": "spell_shadow",
            "soul": "spell_shadow",
            "status": "spell_status",
            "support": "spell_support",
            "time": "spell_time",
            "water": "spell_water",
            "wind": "spell_wind",
        }
        return spell_icons.get(subtype, "spell_arcane")
    skill_icons = {
        "chi strike": "skill_martial_arts",
        "class": "skill_passive" if getattr(ability, "passive", False) else "skill_support",
        "defensive": "skill_defense",
        "drain": "skill_drain",
        "enhance": "skill_support",
        "luck": "skill_luck",
        "martial arts": "skill_martial_arts",
        "offensive": "skill_offense",
        "power up": "skill_passive",
        "stealth": "skill_stealth",
        "truth": "skill_truth",
    }
    return skill_icons.get(
        subtype,
        "skill_passive" if getattr(ability, "passive", False) else "skill_offense",
    )


def _ability_lane(book: str, ability: Any) -> str:
    override = ABILITY_BRANCH_OVERRIDES.get(ability.name)
    if override:
        return override
    if book == "Spells":
        support_names = {
            "Bless",
            "Calming Breeze",
            "Cleanse",
            "Divine Protection",
            "Heal",
            "Heal 2",
            "Heal 3",
            "Natural Attunement",
            "Regen",
            "Regen 2",
            "Regen 3",
            "Regrowth",
            "Resurrection",
            "Sanctuary",
            "Shell",
        }
        if (
            ability.name in support_names
            or getattr(ability, "subtyp", "") == "Support"
            or getattr(ability, "typ", "") == "Support"
        ):
            return "Support"
        return "Arcane"
    defensive_names = {
        "Brace Wall",
        "Bulwark",
        "Centered Guard",
        "Covering Guard",
        "Evasion",
        "Evasive Guard",
        "Goad",
        "Guard Partner",
        "Hold the Line",
        "Last Stand",
        "Mana Shield",
        "Parry",
        "Posturing",
        "Quickstep",
        "Retaliate",
        "Shield Block",
        "Shield Riposte",
        "Spell Reflection",
    }
    if ability.name in defensive_names or getattr(ability, "passive", False):
        return "Defense"
    return "Martial"


def _promotion_requirements(target_class: str, stage: int) -> dict[str, int]:
    if stage == 3 and target_class in SECOND_PROMOTION_STAT_REQUIREMENT_OVERRIDES:
        return dict(SECOND_PROMOTION_STAT_REQUIREMENT_OVERRIDES[target_class])
    primary, secondary = CLASS_STAT_GROUPS[target_class]
    if stage == 2:
        primary_value = 17 if len(primary) == 1 else 14 if len(primary) == 2 else 13
        secondary_value = 13 if len(secondary) == 1 else 10
    else:
        primary_value = 24 if len(primary) == 1 else 20 if len(primary) == 2 else 18
        secondary_value = 19 if len(secondary) == 1 else 15
    requirements = {stat: primary_value for stat in primary}
    requirements.update({stat: secondary_value for stat in secondary})
    if stage == 2:
        requirements.update(
            FIRST_PROMOTION_STAT_REQUIREMENT_OVERRIDES.get(
                target_class,
                {},
            )
        )
    return requirements


def _tree_branch_specs(
    class_name: str,
    entries: list[tuple[int, int, str, type, Any]],
) -> tuple[tuple[str, ...], dict[str, str], dict[str, str]]:
    """Return branch order, ability assignments, and promotion assignments."""
    authored = BASE_TREE_BRANCHES.get(class_name)
    if authored:
        branches = tuple(branch_name for branch_name, _target, _abilities, _rating in authored)
        ability_branches = {
            ability_name: branch_name
            for branch_name, _target, ability_names, _rating in authored
            for ability_name in ability_names
        }
        promotion_branches = {
            target_name: branch_name
            for branch_name, target_name, _abilities, _rating in authored
        }
        return branches, ability_branches, promotion_branches

    promoted_paths = PROMOTED_TREE_PATHS.get(class_name)
    if promoted_paths is not None:
        branches = tuple(branch_name for branch_name, _abilities in promoted_paths)
        ability_branches = {
            ability_name: branch_name
            for branch_name, ability_names in promoted_paths
            for ability_name in ability_names
        }
        expected = {
            ability_ctor.__name__
            for _level, _tie, _book, ability_ctor, _ability in entries
        }
        missing = expected - set(ability_branches)
        extra = set(ability_branches) - expected
        if missing or extra:
            raise ValueError(
                f"{class_name} authored paths mismatch catalog; "
                f"missing={sorted(missing)}, extra={sorted(extra)}"
            )
        declared_promotions = PROMOTED_TREE_PROMOTION_PATHS.get(class_name, {})
        missing_promotions = set(CLASS_CHILDREN[class_name]) - set(declared_promotions)
        extra_promotions = set(declared_promotions) - set(CLASS_CHILDREN[class_name])
        if missing_promotions or extra_promotions:
            raise ValueError(
                f"{class_name} authored promotion paths mismatch registry; "
                f"missing={sorted(missing_promotions)}, "
                f"extra={sorted(extra_promotions)}"
            )
        return branches, ability_branches, dict(declared_promotions)

    raise ValueError(f"{class_name} has no explicit authored paths")


def _branch_rating_focus(class_name: str, branch: str) -> str:
    authored = BASE_TREE_BRANCHES.get(class_name, ())
    for branch_name, _target, _abilities, rating in authored:
        if branch_name == branch:
            return rating
    promoted = PROMOTED_TREE_PATHS.get(class_name, ())
    for branch_name, ability_names in promoted:
        if branch_name != branch:
            continue
        entries = {
            ability_ctor.__name__: (book, ability)
            for _level, _tie, book, ability_ctor, ability
            in _ability_entries(class_name)
        }
        lane_counts = {lane: 0 for lane in TREE_LANES}
        for ability_name in ability_names:
            book, ability = entries[ability_name]
            lane_counts[_ability_lane(book, ability)] += 1
        if any(lane_counts.values()):
            lane = max(
                TREE_LANES,
                key=lambda name: (
                    lane_counts[name],
                    -TREE_LANES.index(name),
                ),
            )
            return {
                "Martial": "Attack",
                "Arcane": "Magic",
                "Defense": "Defense",
                "Support": "Magic Defense",
            }[lane]
        normalized = branch.lower()
        if any(word in normalized for word in ("guard", "defense", "control", "body")):
            return "Defense"
        if any(word in normalized for word in ("grace", "ward", "shelter", "prayer")):
            return "Magic Defense"
        if any(
            word in normalized
            for word in ("magic", "arcane", "corruption", "rune", "constellation")
        ):
            return "Magic"
        return "Attack"
    return {
        "Martial": "Attack",
        "Arcane": "Magic",
        "Defense": "Defense",
        "Support": "Magic Defense",
    }.get(branch, "Defense")


def _rating_icon_key(rating_name: str) -> str:
    return f"rating_{_slug(rating_name).replace('-', '_')}"


def _development_level_requirement(stage: int, row: int) -> int | None:
    """Return the authored global-level milestone for a development row."""
    milestones = {
        1: (None, 10, 15, 20, 25),
        2: (35, 40, 45, 50, 55),
        3: (65, 70, 75, 80, 85, 90, 95),
    }[stage]
    return milestones[min(max(0, row), len(milestones) - 1)]


def _tree_size_range(class_name: str, stage: int) -> tuple[int, int]:
    """Return class-specific development bounds when a tree needs extra space."""
    return TREE_SIZE_OVERRIDES.get(class_name, STAGE_SIZE_RANGES[stage])


def _build_warrior_tree() -> AbilityTree:
    """Build the explicit Warrior prototype graph."""
    class_name = "Warrior"
    entries = {
        ability_ctor.__name__: (book, ability_ctor, ability)
        for _level, _tie, book, ability_ctor, ability in _ability_entries(class_name)
    }
    branches = (
        *(path[0] for path in WARRIOR_TREE_PATHS),
        "Independent",
    )
    all_nodes: list[AbilityTreeNode] = []
    rating_counts: dict[str, int] = {}
    ability_node_ids: dict[str, str] = {}
    path_node_ids: dict[tuple[str, str], str] = {}
    promotion_terminals: dict[str, str] = {}

    for column, (lane, target_name, specs) in enumerate(WARRIOR_TREE_PATHS):
        prerequisite: tuple[str, ...] = ()
        row_offset = WARRIOR_PATH_ROW_OFFSETS.get(target_name, 0)
        for row, (kind_name, identifier, icon_key) in enumerate(
            specs,
            start=row_offset + 1,
        ):
            if kind_name == "ability":
                try:
                    book, ability_ctor, ability = entries[identifier]
                except KeyError as exc:
                    raise ValueError(
                        f"Warrior tree references unknown ability {identifier}"
                    ) from exc
                node_id = f"warrior.ability.{_slug(identifier)}"
                kind = NodeKind.ABILITY
                payload = {
                    "name": ability.name,
                    "book": book,
                    "ability_class": ability_ctor,
                    "description": getattr(ability, "description", ""),
                }
                ability_node_ids[identifier] = node_id
            elif kind_name == "rating":
                rating_counts[identifier] = rating_counts.get(identifier, 0) + 1
                node_id = (
                    f"warrior.rating.{_slug(identifier)}."
                    f"{rating_counts[identifier]}"
                )
                kind = NodeKind.RATING
                payload = {
                    "name": f"+10 {identifier}",
                    "rating": identifier,
                    "amount": 10,
                    "description": (
                        f"Permanently increase {identifier} by 10."
                    ),
                }
            elif kind_name == "health":
                node_id = "warrior.health.25"
                kind = NodeKind.HEALTH
                payload = {
                    "name": "+25 HP",
                    "amount": 25,
                    "description": "Permanently increase maximum HP by 25.",
                }
            else:
                raise ValueError(f"Unknown Warrior node kind: {kind_name}")
            level_requirement = WARRIOR_NODE_LEVEL_REQUIREMENTS.get(identifier)
            if level_requirement:
                payload["level_requirement"] = level_requirement
            node = AbilityTreeNode(
                id=node_id,
                tree_id=class_name,
                kind=kind,
                lane=lane,
                position=WARRIOR_NODE_POSITION_OVERRIDES.get(
                    (target_name, identifier),
                    (column, row),
                ),
                icon_key=icon_key,
                prerequisites=prerequisite,
                payload=payload,
            )
            all_nodes.append(node)
            path_node_ids[(target_name, identifier)] = node.id
            prerequisite = (node.id,)
        promotion_terminals[target_name] = prerequisite[0]

    node_indexes = {
        node.id: index
        for index, node in enumerate(all_nodes)
    }
    for target_identifier, required_nodes in (
        WARRIOR_NODE_PREREQUISITE_OVERRIDES.items()
    ):
        target_id = ability_node_ids[target_identifier]
        target_index = node_indexes[target_id]
        all_nodes[target_index] = replace(
            all_nodes[target_index],
            prerequisites=tuple(
                path_node_ids[(path_target, identifier)]
                for path_target, identifier in required_nodes
            ),
        )
    for target_identifier, required_nodes in (
        WARRIOR_NODE_CROSS_REQUIREMENTS.items()
    ):
        target_id = ability_node_ids[target_identifier]
        target_index = node_indexes[target_id]
        target_node = all_nodes[target_index]
        cross_requirements = tuple(
            path_node_ids[(path_target, identifier)]
            for path_target, identifier in required_nodes
        )
        connector_channels = {
            path_node_ids[(path_target, identifier)]:
                WARRIOR_CONNECTOR_CHANNEL_OVERRIDES[
                    (target_identifier, identifier)
                ]
            for path_target, identifier in required_nodes
            if (
                target_identifier,
                identifier,
            ) in WARRIOR_CONNECTOR_CHANNEL_OVERRIDES
        }
        all_nodes[target_index] = replace(
            target_node,
            prerequisites=(
                *target_node.prerequisites,
                *cross_requirements,
            ),
            payload={
                **target_node.payload,
                **(
                    {"connector_channel_columns": connector_channels}
                    if connector_channels
                    else {}
                ),
            },
        )

    for kind_name, identifier, icon_key, position in WARRIOR_FLOATING_NODES:
        if kind_name != "ability":
            raise ValueError(f"Unknown floating Warrior node kind: {kind_name}")
        try:
            book, ability_ctor, ability = entries[identifier]
        except KeyError as exc:
            raise ValueError(
                f"Warrior tree references unknown ability {identifier}"
            ) from exc
        node_id = f"warrior.ability.{_slug(identifier)}"
        ability_node_ids[identifier] = node_id
        all_nodes.append(AbilityTreeNode(
            id=node_id,
            tree_id=class_name,
            kind=NodeKind.ABILITY,
            lane="Independent",
            position=position,
            icon_key=icon_key,
            payload={
                "name": ability.name,
                "book": book,
                "ability_class": ability_ctor,
                "description": getattr(ability, "description", ""),
                **(
                    {
                        "level_requirement":
                            WARRIOR_NODE_LEVEL_REQUIREMENTS[identifier]
                    }
                    if identifier in WARRIOR_NODE_LEVEL_REQUIREMENTS
                    else {}
                ),
            },
        ))

    promotion_row = max(node.position[1] for node in all_nodes) + 1
    for column, (lane, target_name, _specs) in enumerate(WARRIOR_TREE_PATHS):
        cross_requirements = tuple(
            ability_node_ids[identifier]
            for identifier in WARRIOR_PROMOTION_CROSS_REQUIREMENTS.get(
                target_name,
                (),
            )
        )
        all_nodes.append(AbilityTreeNode(
            id=f"warrior.promotion.{_slug(target_name)}",
            tree_id=class_name,
            kind=NodeKind.PROMOTION,
            lane=lane,
            position=(column, promotion_row),
            icon_key="promotion",
            prerequisites=(promotion_terminals[target_name], *cross_requirements),
            payload={
                "name": f"Promote: {target_name}",
                "target_class": target_name,
                "target_class_ctor": CLASS_DETAILS[target_name][0],
                "requirements": _promotion_requirements(target_name, 2),
                "level_requirement": 30,
            },
            cost=2,
        ))

    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=1,
        branches=branches,
        nodes=tuple(all_nodes),
    )


def _build_mage_tree() -> AbilityTree:
    """Build the explicit Mage specialization graph."""
    class_name = "Mage"
    entries = {
        ability_ctor.__name__: (book, ability_ctor, ability)
        for _level, _tie, book, ability_ctor, ability
        in _ability_entries(class_name)
    }
    branches = ("Elementalism", "Arcana", "Occultism", "Conjuration", "Universal")
    nodes: list[AbilityTreeNode] = []

    for spec in MAGE_TREE_NODE_SPECS:
        kind = NodeKind(str(spec["kind"]))
        identifier = str(spec["identifier"])
        if kind == NodeKind.ABILITY:
            book, ability_ctor, ability = entries[identifier]
            payload = {
                "name": ability.name,
                "book": book,
                "ability_class": ability_ctor,
                "description": getattr(ability, "description", ""),
            }
            icon_key = str(spec.get("icon_key", _ability_icon_key(book, ability)))
        elif kind == NodeKind.TALENT:
            payload = {
                "name": str(spec["name"]),
                "talent_key": identifier,
                "description": str(spec["description"]),
                "bonuses": spec["bonuses"],
            }
            icon_key = "skill_passive"
        elif kind == NodeKind.RATING:
            payload = {
                "name": f"+10 {identifier}",
                "rating": identifier,
                "amount": 10,
                "description": f"Permanently increase {identifier} by 10.",
            }
            icon_key = _rating_icon_key(identifier)
        elif kind in {NodeKind.HEALTH, NodeKind.MANA}:
            resource_name = "HP" if kind == NodeKind.HEALTH else "MP"
            payload = {
                "name": f"+25 {resource_name}",
                "amount": 25,
                "description": (
                    f"Permanently increase maximum {resource_name} by 25."
                ),
            }
            icon_key = (
                "skill_defense"
                if kind == NodeKind.HEALTH
                else "spell_arcane"
            )
        else:
            raise ValueError(f"Unsupported Mage node kind: {kind.value}")

        if spec.get("level") is not None:
            payload["level_requirement"] = int(spec["level"])
        if spec.get("prerequisite_mode"):
            payload["prerequisite_mode"] = str(spec["prerequisite_mode"])
        if spec.get("exclusive_group"):
            payload["exclusive_group"] = str(spec["exclusive_group"])
        if spec.get("connector_enter_from_top"):
            payload["connector_enter_from_top"] = True
        if spec.get("connector_channel_columns"):
            payload["connector_channel_columns"] = dict(
                spec["connector_channel_columns"]
            )
        nodes.append(AbilityTreeNode(
            id=str(spec["id"]),
            tree_id=class_name,
            kind=kind,
            lane=str(spec["lane"]),
            position=tuple(spec["position"]),
            icon_key=icon_key,
            prerequisites=tuple(spec.get("prerequisites", ())),
            payload=payload,
        ))

    for target_name, lane, prerequisites, position, prerequisite_mode in MAGE_PROMOTION_SPECS:
        nodes.append(AbilityTreeNode(
            id=f"mage.promotion.{_slug(target_name)}",
            tree_id=class_name,
            kind=NodeKind.PROMOTION,
            lane=lane,
            position=position,
            icon_key="promotion",
            prerequisites=tuple(prerequisites),
            payload={
                "name": f"Promote: {target_name}",
                "target_class": target_name,
                "target_class_ctor": CLASS_DETAILS[target_name][0],
                "requirements": _promotion_requirements(target_name, 2),
                "level_requirement": 30,
                "prerequisite_mode": prerequisite_mode,
            },
            cost=2,
        ))

    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=1,
        branches=branches,
        nodes=tuple(nodes),
    )


def _build_weapon_master_tree() -> AbilityTree:
    """Build Weapon Master's asymmetric routes and independent weapon arts."""
    class_name = "Weapon Master"
    branches = tuple(path[0] for path in PROMOTED_TREE_PATHS[class_name])
    entries = {
        ability_ctor.__name__: (book, ability_ctor, ability)
        for _level, _tie, book, ability_ctor, ability in _ability_entries(class_name)
    }
    nodes: list[AbilityTreeNode] = []
    local_ids: dict[str, str] = {}

    for spec in WEAPON_MASTER_TREE_NODE_SPECS:
        kind = NodeKind(spec["kind"])
        suffix = str(spec["id"])
        node_id = f"weapon-master.{kind.value}.{suffix}"
        local_ids[suffix] = node_id
        identifier = str(spec["identifier"])
        if kind == NodeKind.ABILITY:
            book, ability_ctor, ability = entries[identifier]
            payload = {
                "name": str(spec.get("name", ability.name)),
                "book": book,
                "ability_class": ability_ctor,
                "description": getattr(ability, "description", ""),
            }
        elif kind == NodeKind.RATING:
            amount = 20
            payload = {
                "name": f"+{amount} {identifier}",
                "rating": identifier,
                "amount": amount,
                "description": (
                    f"Permanently increase {identifier} by {amount}."
                ),
            }
        else:
            raise ValueError(f"Unsupported Weapon Master node kind: {kind.value}")
        if spec.get("level") is not None:
            payload["level_requirement"] = int(spec["level"])
        for key in (
            "exclusive_group",
            "owned_if_known",
            "prerequisite_mode",
            "stack_if_known",
            "weapon_specialization",
        ):
            if key in spec:
                payload[key] = spec[key]
        nodes.append(AbilityTreeNode(
            id=node_id,
            tree_id=class_name,
            kind=kind,
            lane=str(spec["lane"]),
            position=tuple(spec["position"]),
            icon_key=(
                _ability_icon_key(book, ability)
                if kind == NodeKind.ABILITY
                else _rating_icon_key(identifier)
            ),
            prerequisites=tuple(
                local_ids[prerequisite]
                for prerequisite in spec.get("prerequisites", ())
            ),
            payload=payload,
            cost=int(spec.get("cost", 1)),
        ))

    promotions = (
        ("Berserker", "Berserker", "brutish-strength", (0, 7)),
        (
            "Grandmaster of Arms",
            "Grandmaster",
            "true-piercing-strike",
            (1.5, 7),
        ),
    )
    for target_name, lane, prerequisite, position in promotions:
        nodes.append(AbilityTreeNode(
            id=f"weapon-master.promotion.{_slug(target_name)}",
            tree_id=class_name,
            kind=NodeKind.PROMOTION,
            lane=lane,
            position=position,
            icon_key="promotion",
            prerequisites=(local_ids[prerequisite],),
            payload={
                "name": f"Promote: {target_name}",
                "target_class": target_name,
                "target_class_ctor": CLASS_DETAILS[target_name][0],
                "requirements": _promotion_requirements(target_name, 3),
                "level_requirement": 60,
            },
            cost=3,
        ))
    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=2,
        branches=branches,
        nodes=tuple(nodes),
    )


def _build_terminal_weapon_tree(
    class_name: str,
    specs: tuple[dict[str, Any], ...],
) -> AbilityTree:
    """Build an authored terminal Weapon Discipline tree."""
    entries = {
        ability_ctor.__name__: (book, ability_ctor, ability)
        for _level, _tie, book, ability_ctor, ability in _ability_entries(class_name)
    }
    branches = tuple(dict.fromkeys(str(spec["lane"]) for spec in specs))
    nodes: list[AbilityTreeNode] = []
    local_ids: dict[str, str] = {}

    for spec in specs:
        kind = NodeKind(spec["kind"])
        suffix = str(spec["id"])
        node_id = f"{_slug(class_name)}.{kind.value}.{suffix}"
        local_ids[suffix] = node_id
        identifier = str(spec["identifier"])
        if kind == NodeKind.ABILITY:
            book, ability_ctor, ability = entries[identifier]
            payload = {
                "name": str(spec.get("name", ability.name)),
                "book": book,
                "ability_class": ability_ctor,
                "description": getattr(ability, "description", ""),
            }
            icon_key = str(
                spec.get("icon_key", _ability_icon_key(book, ability))
            )
        elif kind == NodeKind.TALENT:
            payload = {
                "name": str(spec["name"]),
                "talent_key": identifier,
                "description": str(spec["description"]),
            }
            icon_key = "skill_passive"
        elif kind == NodeKind.RATING:
            amount = 30
            payload = {
                "name": f"+{amount} {identifier}",
                "rating": identifier,
                "amount": amount,
                "description": (
                    f"Permanently increase {identifier} by {amount}."
                ),
            }
            icon_key = _rating_icon_key(identifier)
        elif kind == NodeKind.HEALTH:
            amount = RESOURCE_NODE_AMOUNTS[3]
            payload = {
                "name": f"+{amount} HP",
                "amount": amount,
                "description": (
                    f"Permanently increase maximum HP by {amount}."
                ),
            }
            icon_key = "skill_defense"
        else:
            raise ValueError(
                f"Unsupported {class_name} node kind: {kind.value}"
            )
        if spec.get("level") is not None:
            payload["level_requirement"] = int(spec["level"])
        for key in (
            "available_on_promotion",
            "level_band_gate",
            "owned_if_known",
            "weapon_specialization",
        ):
            if key in spec:
                payload[key] = spec[key]
        nodes.append(AbilityTreeNode(
            id=node_id,
            tree_id=class_name,
            kind=kind,
            lane=str(spec["lane"]),
            position=tuple(spec["position"]),
            icon_key=icon_key,
            prerequisites=tuple(
                local_ids.get(prerequisite, prerequisite)
                for prerequisite in spec.get("prerequisites", ())
            ),
            payload=payload,
            cost=int(spec.get("cost", 1)),
        ))

    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=3,
        branches=branches,
        nodes=tuple(nodes),
    )


def _build_lancer_dragoon_tree(
    class_name: str,
    specs: tuple[dict[str, Any], ...],
) -> AbilityTree:
    """Build an authored Jump progression tree."""
    entries = {
        ability_ctor.__name__: (book, ability_ctor, ability)
        for _level, _tie, book, ability_ctor, ability
        in _ability_entries(class_name)
    }
    branches = tuple(dict.fromkeys(str(spec["lane"]) for spec in specs))
    nodes: list[AbilityTreeNode] = []
    local_ids: dict[str, str] = {}
    for spec in specs:
        raw_kind = str(spec["kind"])
        kind = NodeKind.TALENT if raw_kind == "jump_mod" else NodeKind(raw_kind)
        suffix = str(spec["id"])
        local_ids[suffix] = (
            f"{_slug(class_name)}.jump-mod.{suffix}"
            if raw_kind == "jump_mod"
            else f"{_slug(class_name)}.{kind.value}.{suffix}"
        )

    for spec in specs:
        raw_kind = str(spec["kind"])
        kind = NodeKind.TALENT if raw_kind == "jump_mod" else NodeKind(raw_kind)
        suffix = str(spec["id"])
        node_id = local_ids[suffix]
        identifier = str(spec["identifier"])

        if kind == NodeKind.ABILITY:
            book, ability_ctor, ability = entries[identifier]
            payload = {
                "name": str(spec.get("name", ability.name)),
                "book": book,
                "ability_class": ability_ctor,
                "description": getattr(ability, "description", ""),
            }
            icon_key = _ability_icon_key(book, ability)
        elif kind == NodeKind.TALENT:
            description = spec.get("description")
            if description is None:
                description = (
                    f"Unlock the {spec['jump_modification']} Jump modification."
                )
            payload = {
                "name": str(spec["name"]),
                "talent_key": identifier,
                "description": str(description),
            }
            if spec.get("bonuses"):
                payload["bonuses"] = spec["bonuses"]
            if spec.get("kit_effect"):
                payload["kit_effect"] = spec["kit_effect"]
            if spec.get("jump_modification"):
                payload["jump_modification"] = str(spec["jump_modification"])
            icon_key = "skill_mobility"
        elif kind == NodeKind.RATING:
            amount = 20 if class_name == "Lancer" else 30
            payload = {
                "name": f"+{amount} {identifier}",
                "rating": identifier,
                "amount": amount,
                "description": (
                    f"Permanently increase {identifier} by {amount}."
                ),
            }
            icon_key = _rating_icon_key(identifier)
        elif kind == NodeKind.HEALTH:
            stage = CLASS_DETAILS[class_name][1]
            amount = RESOURCE_NODE_AMOUNTS[stage]
            payload = {
                "name": f"+{amount} HP",
                "amount": amount,
                "description": (
                    f"Permanently increase maximum HP by {amount}."
                ),
            }
            icon_key = "skill_defense"
        else:
            raise ValueError(
                f"Unsupported {class_name} node kind: {kind.value}"
            )

        if spec.get("level") is not None:
            payload["level_requirement"] = int(spec["level"])
        for key in (
            "available_on_promotion",
            "level_band_gate",
            "owned_if_known",
            "requires_known_ability",
        ):
            if key in spec:
                payload[key] = spec[key]
        nodes.append(AbilityTreeNode(
            id=node_id,
            tree_id=class_name,
            kind=kind,
            lane=str(spec["lane"]),
            position=tuple(spec["position"]),
            icon_key=icon_key,
            prerequisites=tuple(
                local_ids.get(prerequisite, prerequisite)
                for prerequisite in spec.get("prerequisites", ())
            ),
            payload=payload,
            cost=int(spec.get("cost", 1)),
        ))

    stage = 2 if class_name == "Lancer" else 3
    if class_name == "Lancer":
        nodes.append(AbilityTreeNode(
            id="lancer.promotion.dragoon",
            tree_id=class_name,
            kind=NodeKind.PROMOTION,
            lane="Jump Core",
            position=(3, 7),
            icon_key="promotion",
            prerequisites=(
                "lancer.ability.vigilant-landing",
                "lancer.ability.polearm-excellence",
            ),
            payload={
                "name": "Promote: Dragoon",
                "target_class": "Dragoon",
                "target_class_ctor": CLASS_DETAILS["Dragoon"][0],
                "requirements": _promotion_requirements("Dragoon", 3),
                "level_requirement": 60,
                "connector_enter_from_top": True,
                "connector_channel_columns": {
                    "lancer.ability.vigilant-landing": 1,
                    "lancer.ability.polearm-excellence": 4,
                },
            },
            cost=3,
        ))
    else:
        lancer_tree = _build_lancer_dragoon_tree(
            "Lancer",
            LANCER_TREE_NODE_SPECS,
        )
        inherited_nodes = [
            node
            for node in lancer_tree.nodes
            if node.kind != NodeKind.PROMOTION
        ]
        nodes = [*inherited_nodes, *nodes]
        branches = tuple(dict.fromkeys(node.lane for node in nodes))

    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=stage,
        branches=branches,
        nodes=tuple(nodes),
    )


def _build_authored_kit_tree(
    class_name: str,
    specs: tuple[dict[str, Any], ...],
    *,
    promotion_target: str | None = None,
    promotion_position: tuple[float, int] | None = None,
    promotion_prerequisites: tuple[str, ...] = (),
    promotion_prerequisite_mode: str = "all",
    promotion_connector_join_at_target_row: bool = False,
) -> AbilityTree:
    """Build a compact authored first- or terminal-promotion class tree."""
    entries = {
        ability_ctor.__name__: (book, ability_ctor, ability)
        for _level, _tie, book, ability_ctor, ability
        in _ability_entries(class_name)
    }
    stage = CLASS_DETAILS[class_name][1]
    branches = tuple(dict.fromkeys(str(spec["lane"]) for spec in specs))
    nodes: list[AbilityTreeNode] = []
    local_ids: dict[str, str] = {}
    for spec in specs:
        kind = NodeKind(str(spec["kind"]))
        suffix = str(spec["id"])
        local_ids[suffix] = f"{_slug(class_name)}.{kind.value}.{suffix}"

    for spec in specs:
        kind = NodeKind(str(spec["kind"]))
        suffix = str(spec["id"])
        identifier = str(spec["identifier"])
        node_id = local_ids[suffix]
        if kind == NodeKind.ABILITY:
            book, ability_ctor, ability = entries[identifier]
            payload = {
                "name": str(spec.get("name", ability.name)),
                "book": book,
                "ability_class": ability_ctor,
                "description": getattr(ability, "description", ""),
            }
            icon_key = str(
                spec.get("icon_key", _ability_icon_key(book, ability))
            )
        elif kind == NodeKind.TALENT:
            payload = {
                "name": str(spec["name"]),
                "talent_key": identifier,
                "description": str(spec["description"]),
            }
            if spec.get("bonuses"):
                payload["bonuses"] = spec["bonuses"]
            if spec.get("kit_effect"):
                payload["kit_effect"] = spec["kit_effect"]
            icon_key = "skill_passive"
        elif kind == NodeKind.RATING:
            amount = 20 if stage == 2 else 30
            payload = {
                "name": f"+{amount} {identifier}",
                "rating": identifier,
                "amount": amount,
                "description": (
                    f"Permanently increase {identifier} by {amount}."
                ),
            }
            icon_key = _rating_icon_key(identifier)
        elif kind == NodeKind.HEALTH:
            amount = RESOURCE_NODE_AMOUNTS[stage]
            payload = {
                "name": f"+{amount} HP",
                "amount": amount,
                "description": (
                    f"Permanently increase maximum HP by {amount}."
                ),
            }
            icon_key = "skill_defense"
        elif kind == NodeKind.MANA:
            amount = RESOURCE_NODE_AMOUNTS[stage]
            payload = {
                "name": f"+{amount} MP",
                "amount": amount,
                "description": (
                    f"Permanently increase maximum MP by {amount}."
                ),
            }
            icon_key = "spell_arcane"
        else:
            raise ValueError(
                f"Unsupported {class_name} node kind: {kind.value}"
            )

        if spec.get("level") is not None:
            payload["level_requirement"] = int(spec["level"])
        for key in (
            "available_on_promotion",
            "exclusive_group",
            "level_band_gate",
            "owned_if_known",
            "prerequisite_mode",
            "requires_known_ability",
            "school_affinity",
            "upgrade_without_source",
            "hidden_until_known",
            "quest_unlock",
            "revealed_name",
        ):
            if key in spec:
                payload[key] = spec[key]
        if spec.get("connector_enter_from_top"):
            payload["connector_enter_from_top"] = True
        if spec.get("connector_channel_columns"):
            payload["connector_channel_columns"] = {
                local_ids.get(prerequisite, prerequisite): column
                for prerequisite, column
                in spec["connector_channel_columns"].items()
            }
        nodes.append(AbilityTreeNode(
            id=node_id,
            tree_id=class_name,
            kind=kind,
            lane=str(spec["lane"]),
            position=tuple(spec["position"]),
            icon_key=icon_key,
            prerequisites=tuple(
                local_ids.get(prerequisite, prerequisite)
                for prerequisite in spec.get("prerequisites", ())
            ),
            payload=payload,
            cost=int(spec.get("cost", 1)),
        ))

    if promotion_target:
        if promotion_position is None:
            raise ValueError(f"{class_name} promotion position is required")
        nodes.append(AbilityTreeNode(
            id=f"{_slug(class_name)}.promotion.{_slug(promotion_target)}",
            tree_id=class_name,
            kind=NodeKind.PROMOTION,
            lane=branches[0],
            position=promotion_position,
            icon_key="promotion",
            prerequisites=tuple(
                local_ids.get(prerequisite, prerequisite)
                for prerequisite in promotion_prerequisites
            ),
            payload={
                "name": f"Promote: {promotion_target}",
                "target_class": promotion_target,
                "target_class_ctor": CLASS_DETAILS[promotion_target][0],
                "floating_promotion": not promotion_prerequisites,
                "requirements": _promotion_requirements(
                    promotion_target,
                    3,
                ),
                "level_requirement": 60,
                "prerequisite_mode": promotion_prerequisite_mode,
                "connector_join_at_target_row": (
                    promotion_connector_join_at_target_row
                ),
            },
            cost=3,
        ))

    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=stage,
        branches=branches,
        nodes=tuple(nodes),
    )


def _build_warlock_tree() -> AbilityTree:
    """Build the Warlock development paths and its two terminal promotions."""
    base_tree = _build_authored_kit_tree("Warlock", WARLOCK_TREE_NODE_SPECS)
    promotions = (
        AbilityTreeNode(
            id="warlock.promotion.shadowcaster",
            tree_id="Warlock",
            kind=NodeKind.PROMOTION,
            lane="Umbral Offense",
            position=(0.5, 7),
            icon_key="promotion",
            prerequisites=(
                "warlock.ability.doom",
                "warlock.ability.mana-drain",
            ),
            payload={
                "name": "Promote: Shadowcaster",
                "target_class": "Shadowcaster",
                "target_class_ctor": CLASS_DETAILS["Shadowcaster"][0],
                "floating_promotion": False,
                "requirements": _promotion_requirements("Shadowcaster", 3),
                "level_requirement": 60,
                "prerequisite_mode": "any",
                "connector_join_at_target_row": True,
            },
            cost=3,
        ),
        AbilityTreeNode(
            id="warlock.promotion.demonologist",
            tree_id="Warlock",
            kind=NodeKind.PROMOTION,
            lane="Curses",
            position=(3.5, 7),
            icon_key="promotion",
            prerequisites=(
                "warlock.ability.curse-swarms",
                "warlock.ability.life-tap",
            ),
            payload={
                "name": "Promote: Demonologist",
                "target_class": "Demonologist",
                "target_class_ctor": CLASS_DETAILS["Demonologist"][0],
                "floating_promotion": False,
                "requirements": _promotion_requirements("Demonologist", 3),
                "level_requirement": 60,
                "prerequisite_mode": "any",
                "connector_join_at_target_row": True,
            },
            cost=3,
        ),
    )
    return replace(base_tree, nodes=(*base_tree.nodes, *promotions))


THAUMATURGIST_XENID_GROUPS = (
    ("Animal", "Hodag", "Caladrius"),
    ("Humanoid", "Patagon", "Kobalos"),
    ("Monster", "Dilong", "Cacus"),
    ("Spirit", "Agloolik", "Izulu"),
    ("Fiend", "Hala", "Lamashtu"),
    ("Celestial", "Seraphim", "Bardi"),
    ("Dragon", "Tiamat", "Zahhak"),
)


def _build_thaumaturgist_tree() -> AbilityTree:
    """Build Callings, Xenid choices, conduit utility, and Miracles explicitly."""
    class_name = "Thaumaturgist"
    branches = (
        "Calling",
        "Xenid Choice",
        "Xenid Ultimate",
        "Conduit",
        "Miracles",
    )
    nodes: list[AbilityTreeNode] = []

    mage_animal = next(
        node
        for node in _build_mage_tree().nodes
        if node.id == "mage.ability.conjure-animal"
    )
    conjurer_tree = _build_authored_kit_tree(
        "Conjurer",
        CONJURER_TREE_NODE_SPECS,
    )
    calling_nodes = [replace(
        mage_animal,
        lane="Calling",
        position=(0, 1),
        payload={
            **mage_animal.payload,
            "available_on_promotion": True,
            "owned_if_known": True,
        },
        prerequisites=(),
    )]
    calling_nodes.extend(
        replace(node, position=(0, row))
        for row, node in enumerate(
            (
                node
                for node_id in (
                    "conjurer.ability.conjure-humanoid",
                    "conjurer.ability.conjure-monster",
                    "conjurer.ability.conjure-spirit",
                    "conjurer.ability.conjure-fiend",
                    "conjurer.ability.conjure-celestial",
                    "conjurer.ability.conjure-dragon",
                )
                for node in conjurer_tree.nodes
                if node.id == node_id
            ),
            start=2,
        )
    )
    nodes.extend(calling_nodes)

    for row, ((category, first, second), calling) in enumerate(
        zip(THAUMATURGIST_XENID_GROUPS, calling_nodes)
    ):
        choice_id = f"thaumaturgist.talent.bind-{_slug(category)}"
        nodes.append(AbilityTreeNode(
            id=choice_id,
            tree_id=class_name,
            kind=NodeKind.TALENT,
            lane="Xenid Choice",
            position=(1, row+1),
            icon_key="skill_passive",
            prerequisites=(calling.id,),
            payload={
                "name": f"Bind Xenid - {category}",
                "talent_key": f"thaumaturgist.bind-{_slug(category)}",
                "xenid_category": category,
                "xenid_options": (first, second),
                "available_on_promotion": True,
                "description": (
                    f"Permanently choose either {first} or {second} as the "
                    f"{category} Xenid for this Calling."
                ),
            },
        ))
        nodes.append(AbilityTreeNode(
            id=f"thaumaturgist.talent.{_slug(category)}-ultimate",
            tree_id=class_name,
            kind=NodeKind.TALENT,
            lane="Xenid Ultimate",
            position=(2, row+1),
            icon_key="skill_passive",
            prerequisites=(choice_id,),
            payload={
                "name": f"{category} Ultimate",
                "talent_key": f"thaumaturgist.{_slug(category)}-ultimate",
                "xenid_ultimate_category": category,
                "available_on_promotion": True,
                "description": (
                    f"Unlock the ultimate ability of the chosen {category} Xenid."
                ),
            },
        ))

    ability_entries = {
        ability_ctor.__name__: (book, ability_ctor, ability)
        for _level, _tie, book, ability_ctor, ability
        in _ability_entries(class_name)
    }
    previous_id: str | None = None
    for row, (identifier, level) in enumerate((
        ("HealSummon", 65),
        ("ConduitCommand", 70),
        ("RaiseSummon", 75),
    ), start=2):
        book, ability_ctor, ability = ability_entries[identifier]
        node_id = f"thaumaturgist.ability.{_slug(identifier)}"
        nodes.append(AbilityTreeNode(
            id=node_id,
            tree_id=class_name,
            kind=NodeKind.ABILITY,
            lane="Conduit",
            position=(3, row),
            icon_key=_ability_icon_key(book, ability),
            prerequisites=(previous_id,) if previous_id else (),
            payload={
                "name": ability.name,
                "book": book,
                "ability_class": ability_ctor,
                "description": getattr(ability, "description", ""),
                "level_requirement": level,
            },
        ))
        previous_id = node_id
    nodes.append(AbilityTreeNode(
        id="thaumaturgist.talent.conduit-mastery",
        tree_id=class_name,
        kind=NodeKind.TALENT,
        lane="Conduit",
        position=(3, 5),
        icon_key="skill_passive",
        prerequisites=(previous_id,),
        payload={
            "name": "Conduit Mastery",
            "talent_key": "thaumaturgist.conduit-mastery",
            "level_requirement": 80,
            "description": (
                "Amplifies the effects the Thaumaturgist's chosen Xenids have "
                "on the caster."
            ),
        },
        cost=2,
    ))
    previous_id = None
    for row, (identifier, level) in enumerate((
        ("MiracleBlade", 65),
        ("MiracleShackles", 70),
        ("MiraclePotion", 75),
        ("MiracleCrystal", 80),
    ), start=2):
        book, ability_ctor, ability = ability_entries[identifier]
        node_id = f"thaumaturgist.ability.{_slug(identifier)}"
        nodes.append(AbilityTreeNode(
            id=node_id,
            tree_id=class_name,
            kind=NodeKind.ABILITY,
            lane="Miracles",
            position=(4, row),
            icon_key=_ability_icon_key(book, ability),
            prerequisites=(previous_id,) if previous_id else (),
            payload={
                "name": ability.name,
                "book": book,
                "ability_class": ability_ctor,
                "description": getattr(ability, "description", ""),
                "level_requirement": level,
            },
            cost=2,
        ))
        previous_id = node_id
    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=3,
        branches=branches,
        nodes=tuple(nodes),
    )


def _build_authored_tree(class_name: str) -> AbilityTree:
    """Build one declared class tree from its catalog and authored identity."""
    if class_name not in AUTHORED_TREE_CLASSES:
        raise ValueError(f"{class_name} has no authored ability-tree identity")
    if class_name == "Warrior":
        return _build_warrior_tree()
    if class_name == "Mage":
        return _build_mage_tree()
    if class_name == "Weapon Master":
        return _build_weapon_master_tree()
    if class_name == "Berserker":
        return _build_terminal_weapon_tree(
            class_name,
            BERSERKER_TREE_NODE_SPECS,
        )
    if class_name == "Grandmaster of Arms":
        return _build_terminal_weapon_tree(
            class_name,
            GRANDMASTER_TREE_NODE_SPECS,
        )
    if class_name == "Lancer":
        return _build_lancer_dragoon_tree(
            class_name,
            LANCER_TREE_NODE_SPECS,
        )
    if class_name == "Dragoon":
        return _build_lancer_dragoon_tree(
            class_name,
            DRAGOON_TREE_NODE_SPECS,
        )
    if class_name == "Sentinel":
        return _build_authored_kit_tree(
            class_name,
            SENTINEL_TREE_NODE_SPECS,
            promotion_target="Stalwart Defender",
            promotion_position=(2, 8),
            promotion_prerequisites=(
                "watchful-reprisal",
                "resolute-guard",
                "shielding-ward",
                "braggadocious",
            ),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Stalwart Defender":
        return _build_authored_kit_tree(
            class_name,
            STALWART_DEFENDER_TREE_NODE_SPECS,
        )
    if class_name == "Paladin":
        return _build_authored_kit_tree(
            class_name,
            PALADIN_TREE_NODE_SPECS,
            promotion_target="Crusader",
            promotion_position=(2.5, 7),
            promotion_prerequisites=(
                "oath-judgment",
                "oath-shelter",
            ),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Crusader":
        return _build_authored_kit_tree(
            class_name,
            CRUSADER_TREE_NODE_SPECS,
        )
    if class_name == "Spellblade":
        return _build_authored_kit_tree(
            class_name,
            SPELLBLADE_TREE_NODE_SPECS,
            promotion_target="Knight Enchanter",
            promotion_position=(1.5, 7),
            promotion_prerequisites=(
                "enhance-blade",
                "enhance-armor",
                "storage-capacity",
            ),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Sorcerer":
        return _build_authored_kit_tree(
            class_name,
            SORCERER_TREE_NODE_SPECS,
            promotion_target="Wizard",
            promotion_position=(1, 7),
            promotion_prerequisites=(
                "classical-enrichment",
                "arcane-ritual",
            ),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Wizard":
        return _build_authored_kit_tree(
            class_name,
            WIZARD_TREE_NODE_SPECS,
        )
    if class_name == "Warlock":
        return _build_warlock_tree()
    if class_name == "Shadowcaster":
        return _build_authored_kit_tree(
            class_name,
            SHADOWCASTER_TREE_NODE_SPECS,
        )
    if class_name == "Demonologist":
        return _build_authored_kit_tree(
            class_name,
            DEMONOLOGIST_TREE_NODE_SPECS,
        )
    if class_name == "Knight Enchanter":
        return _build_authored_kit_tree(
            class_name,
            KNIGHT_ENCHANTER_TREE_NODE_SPECS,
        )
    if class_name == "Conjurer":
        return _build_authored_kit_tree(
            class_name,
            CONJURER_TREE_NODE_SPECS,
            promotion_target="Thaumaturgist",
            promotion_position=(1.5, 7),
            promotion_prerequisites=(
                "barrier-wall",
                "mana-barbs",
                "explosive-decoy",
                "conjure-dragon",
            ),
            promotion_prerequisite_mode="any",
            promotion_connector_join_at_target_row=True,
        )
    if class_name == "Thaumaturgist":
        return _build_thaumaturgist_tree()
    _ctor, stage, _parent = CLASS_DETAILS[class_name]
    entries = _ability_entries(class_name)
    branches, ability_branches, promotion_branches = _tree_branch_specs(
        class_name,
        entries,
    )
    lane_nodes: dict[str, list[AbilityTreeNode]] = {lane: [] for lane in branches}
    all_nodes: list[AbilityTreeNode] = []

    for _old_level, _tie, book, ability_ctor, ability in entries:
        lane = ability_branches.get(ability_ctor.__name__, _ability_lane(book, ability))
        node_id = f"{_slug(class_name)}.ability.{_slug(ability_ctor.__name__)}"
        if lane_nodes[lane]:
            prerequisites = (lane_nodes[lane][-1].id,)
        else:
            prerequisites = ()
        row = len(lane_nodes[lane])
        level_requirement = _development_level_requirement(stage, row)
        payload = {
            "name": ABILITY_NODE_NAME_OVERRIDES.get(
                ability_ctor.__name__,
                ability.name,
            ),
            "book": book,
            "ability_class": ability_ctor,
            "description": getattr(ability, "description", ""),
            **(
                {"level_requirement": level_requirement}
                if level_requirement
                else {}
            ),
        }
        if (
            class_name == "Knight Enchanter"
            and ability.name in {"Mana Tap", "Enhance Armor"}
        ):
            payload["owned_if_known"] = True
        node = AbilityTreeNode(
            id=node_id,
            tree_id=class_name,
            kind=NodeKind.ABILITY,
            lane=lane,
            position=(branches.index(lane), row),
            icon_key=_ability_icon_key(book, ability),
            prerequisites=prerequisites,
            payload=payload,
        )
        lane_nodes[lane].append(node)
        all_nodes.append(node)

    minimum, maximum = _tree_size_range(class_name, stage)
    authored_talents = (
        CLASS_KIT_TALENTS.get(class_name, ())
        if stage > 1
        else ()
    )
    talent_bonus = stage * 10

    def talent_mechanic_text(talent_key: str) -> str:
        if talent_key == "summoner.conduit-mastery":
            return " It also increases permanent-summon damage by 5%."
        if talent_key == "summoner.true-name-ward":
            return " It also increases permanent-summon maximum HP by 5%."
        return ""

    for talent_name, talent_key, rating_name in authored_talents[
        :max(0, maximum - len(all_nodes))
    ]:
        preferred = next(
            (
                branch
                for branch in branches
                if _branch_rating_focus(class_name, branch) == rating_name
            ),
            min(branches, key=lambda branch: len(lane_nodes[branch])),
        )
        row = len(lane_nodes[preferred])
        level_requirement = _development_level_requirement(stage, row)
        node = AbilityTreeNode(
            id=f"{_slug(class_name)}.talent.{_slug(talent_key)}",
            tree_id=class_name,
            kind=NodeKind.TALENT,
            lane=preferred,
            position=(branches.index(preferred), row),
            icon_key="skill_passive",
            prerequisites=(
                (lane_nodes[preferred][-1].id,)
                if lane_nodes[preferred]
                else ()
            ),
            payload={
                "name": talent_name,
                "talent_key": talent_key,
                "description": (
                    f"{talent_name} permanently increases {rating_name} by "
                    f"{talent_bonus}%."
                    + talent_mechanic_text(talent_key)
                    + (
                        " It also increases the associated class-kit meter "
                        f"cap by {TALENT_KIT_EFFECTS[talent_key][2]}."
                        if talent_key in TALENT_KIT_EFFECTS
                        else ""
                    )
                ),
                "bonuses": {
                    "rating_percentages": {
                        rating_name: talent_bonus / 100,
                    },
                },
                **(
                    {"kit_effect": TALENT_KIT_EFFECTS[talent_key]}
                    if talent_key in TALENT_KIT_EFFECTS
                    else {}
                ),
                **(
                    {"level_requirement": level_requirement}
                    if level_requirement
                    else {}
                ),
            },
        )
        lane_nodes[preferred].append(node)
        all_nodes.append(node)

    rating_plan = list(BASE_TREE_RATING_NODES.get(class_name, ()))

    for lane, rating_name in rating_plan:
        amount = stage * 10
        node_id = (
            f"{_slug(class_name)}.rating.{_slug(rating_name)}."
            f"{1 + sum(n.kind == NodeKind.RATING and n.payload['rating'] == rating_name for n in all_nodes)}"
        )
        prerequisites = (
            (lane_nodes[lane][-1].id,)
            if lane_nodes[lane]
            else ()
        )
        node = AbilityTreeNode(
            id=node_id,
            tree_id=class_name,
            kind=NodeKind.RATING,
            lane=lane,
            position=(branches.index(lane), len(lane_nodes[lane])),
            icon_key=_rating_icon_key(rating_name),
            prerequisites=prerequisites,
            payload={
                "name": f"+{amount} {rating_name}",
                "rating": rating_name,
                "amount": amount,
                "description": (
                    f"Permanently increase {rating_name} by {amount}."
                ),
            },
        )
        lane_nodes[lane].append(node)
        all_nodes.append(node)

    talent_ranks: dict[str, int] = {
        talent_key: 1
        for _name, talent_key, _rating in authored_talents
    }
    talent_index = 0
    while stage > 1 and len(all_nodes) < minimum:
        base_name, talent_key, rating_name = authored_talents[
            talent_index % len(authored_talents)
        ]
        talent_index += 1
        talent_ranks[talent_key] += 1
        rank = talent_ranks[talent_key]
        lane = next(
            (
                branch
                for branch in branches
                if _branch_rating_focus(class_name, branch) == rating_name
            ),
            min(branches, key=lambda branch: len(lane_nodes[branch])),
        )
        row = len(lane_nodes[lane])
        level_requirement = _development_level_requirement(stage, row)
        node = AbilityTreeNode(
            id=(
                f"{_slug(class_name)}.talent.{_slug(talent_key)}."
                f"rank-{rank}"
            ),
            tree_id=class_name,
            kind=NodeKind.TALENT,
            lane=lane,
            position=(branches.index(lane), row),
            icon_key="skill_passive",
            prerequisites=(
                (lane_nodes[lane][-1].id,)
                if lane_nodes[lane]
                else ()
            ),
            payload={
                "name": f"{base_name} {rank}",
                "talent_key": f"{talent_key}.rank-{rank}",
                "description": (
                    f"Deepen {base_name}; permanently increase "
                    f"{rating_name} by {talent_bonus}%."
                    + talent_mechanic_text(talent_key)
                ),
                "bonuses": {
                    "rating_percentages": {
                        rating_name: talent_bonus / 100,
                    },
                },
                **(
                    {"level_requirement": level_requirement}
                    if level_requirement
                    else {}
                ),
            },
        )
        lane_nodes[lane].append(node)
        all_nodes.append(node)

    terminal_by_lane = {
        lane: (nodes[-1].id if nodes else None)
        for lane, nodes in lane_nodes.items()
    }
    promotion_row = max((len(nodes) for nodes in lane_nodes.values()), default=0)
    promotions_in_lane: dict[str, int] = {lane: 0 for lane in branches}
    for target_name in CLASS_CHILDREN[class_name]:
        lane = promotion_branches[target_name]
        terminal = terminal_by_lane[lane]
        row = promotion_row + promotions_in_lane[lane]
        promotions_in_lane[lane] += 1
        node = AbilityTreeNode(
            id=f"{_slug(class_name)}.promotion.{_slug(target_name)}",
            tree_id=class_name,
            kind=NodeKind.PROMOTION,
            lane=lane,
            position=(branches.index(lane), row),
            icon_key="promotion",
            prerequisites=(terminal,) if terminal else (),
            payload={
                "name": f"Promote: {target_name}",
                "target_class": target_name,
                "target_class_ctor": CLASS_DETAILS[target_name][0],
                "requirements": _promotion_requirements(target_name, stage + 1),
                "level_requirement": 30 if stage == 1 else 60,
                **(
                    {"floating_promotion": True}
                    if class_name == "Conjurer" and terminal is None
                    else {}
                ),
            },
            cost=2 if stage == 1 else 3,
        )
        lane_nodes[lane].append(node)
        all_nodes.append(node)

    if class_name in {"Sorcerer", "Wizard"}:
        mage_tree = _build_mage_tree()
        carried_nodes = [
            replace(
                node,
                position=MAGE_CARRIED_NODE_POSITIONS[node.id],
            )
            for node in mage_tree.nodes
            if node.id in MAGE_CARRIED_NODE_POSITIONS
        ]
        all_nodes.extend(carried_nodes)
        branches = (*branches, "Elementalism", "Arcana")
    development_node_count = sum(
        node.kind != NodeKind.PROMOTION for node in all_nodes
    )
    if not minimum <= development_node_count <= maximum:
        raise ValueError(
            f"{class_name} tree has {development_node_count} development nodes; "
            f"expected {minimum}-{maximum}"
        )
    return AbilityTree(
        id=class_name,
        class_name=class_name,
        stage=stage,
        branches=branches,
        nodes=tuple(all_nodes),
    )


def _remove_numeric_node_level_gates(tree: AbilityTree) -> AbilityTree:
    """Apply the global rule that plain rating/resource nodes are path-gated only."""
    normalized = []
    for node in tree.nodes:
        if (
            node.kind in {NodeKind.RATING, NodeKind.HEALTH, NodeKind.MANA}
            and "level_requirement" in node.payload
            and not node.payload.get("level_band_gate")
        ):
            payload = dict(node.payload)
            payload.pop("level_requirement", None)
            node = replace(node, payload=payload)
        normalized.append(node)
    return replace(tree, nodes=tuple(normalized))


ABILITY_TREES = {
    name: _remove_numeric_node_level_gates(_build_authored_tree(name))
    for name in CLASS_DETAILS
}
TREE_NODES = {
    node.id: node
    for tree in ABILITY_TREES.values()
    for node in tree.nodes
}
CARRIED_NODE_IDS_BY_CLASS = {
    "Dragoon": frozenset(
        node.id
        for node in ABILITY_TREES["Dragoon"].nodes
        if node.tree_id == "Lancer"
    ),
    "Sorcerer": frozenset(),
    "Wizard": frozenset(),
    "Thaumaturgist": frozenset({
        *CONJURER_CARRIED_NODE_IDS,
        "mage.ability.conjure-animal",
    }),
}
TALENT_NODES = {
    str(node.payload["talent_key"]): node
    for node in TREE_NODES.values()
    if node.kind == NodeKind.TALENT
}


def _is_carried_node(
    node: AbilityTreeNode,
    current_class: str,
    completed_tree_ids: set[str],
) -> bool:
    """Return whether a promoted class may edit a completed-tree node."""
    return (
        node.tree_id in completed_tree_ids
        and node.id in CARRIED_NODE_IDS_BY_CLASS.get(current_class, ())
    )


def has_talent(player: Any, talent_key: str) -> bool:
    """Return whether a player permanently owns a named progression talent."""
    node = TALENT_NODES.get(str(talent_key))
    state = getattr(player, "progression", None)
    return bool(
        node is not None
        and isinstance(state, ProgressionState)
        and node.id in state.purchased_node_ids
    )


def validate_trees() -> tuple[str, ...]:
    """Validate all manifests and return errors without mutating state."""
    errors: list[str] = []
    seen: set[str] = set()
    known_classes = set(CLASS_DETAILS)
    known_ability_classes = {
        entry[3].__name__
        for class_name in known_classes
        for entry in _ability_entries(class_name)
    }
    catalog_ability_classes = {
        ability_ctor.__name__
        for source in (abilities.spell_dict, abilities.skill_dict)
        for levels in source.values()
        for raw in levels.values()
        for ability_ctor in abilities.ability_classes_for(raw)
        if ability_ctor().name not in EXTERNAL_ACQUISITION_ABILITIES
    }
    manifested: set[str] = set()

    for tree in ABILITY_TREES.values():
        minimum, maximum = _tree_size_range(tree.class_name, tree.stage)
        development_node_count = sum(
            node.kind != NodeKind.PROMOTION for node in tree.nodes
        )
        if not minimum <= development_node_count <= maximum:
            errors.append(f"{tree.id}: invalid stage size")
        node_map = {node.id: node for node in tree.nodes}
        expected_tree_abilities = {
            entry[3].__name__
            for entry in _ability_entries(tree.class_name)
        }
        manifested_tree_abilities = {
            node.payload["ability_class"].__name__
            for node in tree.nodes
            if (
                node.kind == NodeKind.ABILITY
                and node.tree_id == tree.class_name
            )
        }
        missing_tree_abilities = expected_tree_abilities - manifested_tree_abilities
        if missing_tree_abilities:
            errors.append(
                f"{tree.id}: catalog abilities missing from tree: "
                f"{sorted(missing_tree_abilities)}"
            )
        extra_tree_abilities = manifested_tree_abilities - expected_tree_abilities
        if extra_tree_abilities:
            errors.append(
                f"{tree.id}: undeclared catalog abilities in tree: "
                f"{sorted(extra_tree_abilities)}"
            )
        positions: set[tuple[float, int]] = set()
        for node in tree.nodes:
            if node.id in seen and node.tree_id == tree.class_name:
                errors.append(f"{tree.id}: duplicate node ID {node.id}")
            seen.add(node.id)
            node_stage = CLASS_DETAILS[node.tree_id][1]
            node_allowed_levels = {
                1: {0, 5, 10, 15, 20, 25},
                2: {35, 40, 45, 50, 55},
                3: {60, 65, 70, 75, 80, 85, 90, 95},
            }[node_stage]
            if node.lane not in tree.branches:
                errors.append(f"{node.id}: unknown branch")
            if node.position in positions:
                errors.append(f"{tree.id}: duplicate position {node.position}")
            positions.add(node.position)
            if node.icon_key not in ABILITY_ICON_KEYS:
                errors.append(f"{node.id}: unknown icon key {node.icon_key}")
            if node.cost < 1:
                errors.append(f"{node.id}: invalid point cost {node.cost}")
            for prerequisite in node.prerequisites:
                if prerequisite not in node_map:
                    errors.append(f"{node.id}: unknown prerequisite {prerequisite}")
            if node.kind == NodeKind.ABILITY:
                ability_class_name = node.payload["ability_class"].__name__
                manifested.add(ability_class_name)
                if ability_class_name not in known_ability_classes:
                    errors.append(f"{node.id}: unknown ability {node.name}")
                specialization = node.payload.get("weapon_specialization")
                if specialization is not None:
                    from .classes import grandmaster

                    if (
                        not isinstance(specialization, tuple)
                        or len(specialization) != 2
                        or specialization[0] not in grandmaster.WEAPON_TYPES
                        or int(specialization[1]) < 1
                    ):
                        errors.append(
                            f"{node.id}: invalid weapon specialization gate"
                        )
            prerequisite_mode = node.payload.get("prerequisite_mode", "all")
            if prerequisite_mode not in {"all", "any"}:
                errors.append(
                    f"{node.id}: invalid prerequisite mode {prerequisite_mode}"
                )
            if prerequisite_mode == "any" and len(node.prerequisites) < 2:
                errors.append(
                    f"{node.id}: any-prerequisite node needs multiple choices"
                )
            if node.kind == NodeKind.TALENT:
                talent_key = str(node.payload.get("talent_key", "")).strip()
                if not talent_key:
                    errors.append(f"{node.id}: talent has no stable key")
                elif (
                    TALENT_NODES.get(talent_key) is None
                    or TALENT_NODES[talent_key].id != node.id
                ):
                    errors.append(f"{node.id}: duplicate talent key {talent_key}")
                if not str(node.payload.get("description", "")).strip():
                    errors.append(f"{node.id}: talent has no description")
                kit_effect = node.payload.get("kit_effect")
                if kit_effect is not None and (
                    not isinstance(kit_effect, tuple)
                    or len(kit_effect) != 3
                    or kit_effect[0] != "meter_cap"
                    or int(kit_effect[2]) <= 0
                ):
                    errors.append(f"{node.id}: invalid kit effect {kit_effect!r}")
            if node.kind == NodeKind.PROMOTION:
                expected_cost = 2 if tree.stage == 1 else 3
                if node.cost != expected_cost:
                    errors.append(
                        f"{node.id}: promotion must cost {expected_cost} points"
                    )
                target = node.payload["target_class"]
                if target not in known_classes:
                    errors.append(f"{node.id}: unknown target class {target}")
                if (
                    not node.prerequisites
                    and not node.payload.get("floating_promotion")
                ):
                    errors.append(f"{node.id}: promotion has no completed path")
            if (
                node.kind == NodeKind.RATING
                and int(node.payload.get("amount", 0)) != node_stage * 10
            ):
                errors.append(
                    f"{node.id}: rating node must grant {node_stage * 10}"
                )
            if (
                node.kind == NodeKind.HEALTH
                and int(node.payload.get("amount", 0))
                != RESOURCE_NODE_AMOUNTS[node_stage]
            ):
                errors.append(
                    f"{node.id}: health node must grant "
                    f"{RESOURCE_NODE_AMOUNTS[node_stage]}"
                )
            if (
                node.kind == NodeKind.MANA
                and int(node.payload.get("amount", 0))
                != RESOURCE_NODE_AMOUNTS[node_stage]
            ):
                errors.append(
                    f"{node.id}: mana node must grant "
                    f"{RESOURCE_NODE_AMOUNTS[node_stage]}"
                )
            if node.kind != NodeKind.PROMOTION:
                required_level = int(
                    node.payload.get("level_requirement", 0) or 0
                )
                level_optional = (
                    node.kind == NodeKind.RATING
                    or node.kind == NodeKind.HEALTH
                    or node.kind == NodeKind.MANA
                    or bool(node.payload.get("available_on_promotion"))
                    or bool(node.payload.get("owned_if_known"))
                    or bool(node.payload.get("weapon_specialization"))
                )
                if (
                    node.kind == NodeKind.RATING
                    and required_level
                    and not node.payload.get("level_band_gate")
                ):
                    errors.append(
                        f"{node.id}: rating node must not have a level gate"
                    )
                elif (
                    not level_optional
                    and required_level not in node_allowed_levels
                ):
                    errors.append(
                        f"{node.id}: invalid stage-{node_stage} level gate "
                        f"{required_level}"
                    )
                if (
                    node_stage > 1
                    and not level_optional
                    and required_level == 0
                ):
                    errors.append(
                        f"{node.id}: promoted-tree node has no level gate"
                    )

        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(node_id: str) -> None:
            if node_id in visiting:
                errors.append(f"{tree.id}: prerequisite cycle at {node_id}")
                return
            if node_id in visited or node_id not in node_map:
                return
            visiting.add(node_id)
            for prerequisite in node_map[node_id].prerequisites:
                visit(prerequisite)
            visiting.remove(node_id)
            visited.add(node_id)

        for node_id in node_map:
            visit(node_id)

        exclusive_groups: dict[str, list[AbilityTreeNode]] = {}
        for node in tree.nodes:
            group = node.payload.get("exclusive_group")
            if group:
                exclusive_groups.setdefault(str(group), []).append(node)
        for group, choices in exclusive_groups.items():
            if len(choices) < 2:
                errors.append(
                    f"{tree.id}: exclusive group {group} has fewer than two choices"
                )

        if tree.stage == 3:
            roots = [
                node
                for node in tree.nodes
                if not node.prerequisites
            ]
            if len(roots) < 2:
                errors.append(f"{tree.id}: terminal tree has fewer than two roots")
            if not any(
                node.kind in {NodeKind.ABILITY, NodeKind.TALENT}
                for node in tree.nodes
            ):
                errors.append(f"{tree.id}: terminal tree has no class-specific choice")

    missing = catalog_ability_classes - manifested
    if missing:
        errors.append(f"ordinary catalog abilities missing from trees: {sorted(missing)}")

    from .races import races_dict

    races = [race_ctor() for race_ctor in races_dict.values()]
    for class_name, (_ctor, stage, _parent) in CLASS_DETAILS.items():
        if stage != 2:
            continue
        if not any(
            class_name in getattr(race, "cls_res", {}).get("First", ())
            for race in races
        ):
            errors.append(f"{class_name}: no race can reach this promotion")
    return tuple(errors)


def ensure_progression(player: Any) -> ProgressionState:
    """Return the player's state, creating an unallocated state if needed."""
    _migrate_spell_reflection_ability(player)
    current = getattr(player, "progression", None)
    if isinstance(current, ProgressionState):
        _adopt_known_ability_nodes(player, current)
        return current
    level = max(1, min(MAX_PLAYER_LEVEL, int(getattr(player.level, "level", 1))))
    total_xp = max(0, int(getattr(player.level, "exp", 0)))
    state = ProgressionState(
        level=level,
        total_xp=total_xp,
        unspent_points=progression_points_through_level(level),
        unspent_attribute_points=attribute_points_through_level(level),
    )
    player.progression = state
    _adopt_known_ability_nodes(player, state)
    _sync_level(player)
    return state


def _migrate_spell_reflection_ability(player: Any) -> None:
    """Replace the retired Deflect Spell skill with merged Spell Reflection."""
    skills = getattr(player, "spellbook", {}).setdefault("Skills", {})
    if "Deflect Spell" not in skills:
        return
    skills.pop("Deflect Spell", None)
    skills.setdefault("Spell Reflection", abilities.SpellReflection())


def _adopt_known_ability_nodes(player: Any, state: ProgressionState) -> None:
    """Mark explicitly inheritable abilities and Jump mods as pre-owned."""
    class_name = getattr(getattr(player, "cls", None), "name", None)
    if class_name == "Stalwart Defender":
        for ability_ctor in (
            abilities.CitadelAegis,
            abilities.IronwallReprisal,
            abilities.LastBastionSurge,
            abilities.Stronghold,
        ):
            ability = ability_ctor()
            player.spellbook.setdefault("Skills", {}).setdefault(
                ability.name,
                ability,
            )
    tree = ABILITY_TREES.get(class_name)
    if tree is None:
        return
    learned = {
        ability_name
        for book in getattr(player, "spellbook", {}).values()
        for ability_name in getattr(book, "keys", lambda: ())()
    }
    if (
        class_name == "Paladin"
        and "paladin.ability.oath-judgment" in state.purchased_node_ids
        and "Oath's Judgment" not in learned
    ):
        # Earlier authored-tree adoption recursively marked the prerequisites
        # of inherited Double/True Strike as purchased without granting their
        # payloads. Repair that impossible state while retaining abilities the
        # character genuinely learned before becoming a Paladin.
        state.purchased_node_ids.difference_update({
            "paladin.ability.oath-judgment",
            "paladin.rating.attack-1",
            "paladin.talent.tempered-conviction",
        })
        if "Double Strike" not in learned:
            state.purchased_node_ids.discard(
                "paladin.ability.double-strike"
            )
    jump_skill = player.spellbook.get("Skills", {}).get("Jump")
    unlocked_jump_mods = set()
    if jump_skill is not None:
        unlocked_jump_mods = {
            name
            for name, unlocked
            in getattr(jump_skill, "unlocked_modifications", {}).items()
            if unlocked
        }
    def adopt_with_prerequisites(
        node: AbilityTreeNode,
        available_nodes: dict[str, AbilityTreeNode],
    ) -> None:
        state.purchased_node_ids.add(node.id)
        for prerequisite_id in node.prerequisites:
            prerequisite = available_nodes.get(prerequisite_id)
            if prerequisite is not None:
                adopt_with_prerequisites(prerequisite, available_nodes)

    for node in tree.nodes:
        if (
            node.kind == NodeKind.ABILITY
            and node.payload.get("owned_if_known")
            and node.name in learned
        ):
            state.purchased_node_ids.add(node.id)

    modifier_tree_names = (
        ("Lancer", "Dragoon")
        if class_name == "Dragoon"
        else (class_name,)
    )
    for modifier_tree_name in modifier_tree_names:
        modifier_tree = ABILITY_TREES.get(modifier_tree_name)
        if modifier_tree is None:
            continue
        modifier_node_map = {
            node.id: node
            for node in modifier_tree.nodes
        }
        for node in modifier_tree.nodes:
            jump_modification = node.payload.get("jump_modification")
            if jump_modification and jump_modification in unlocked_jump_mods:
                adopt_with_prerequisites(node, modifier_node_map)
    sync_jump_modification_nodes(player, state)


def sync_jump_modification_nodes(
    player: Any,
    state: ProgressionState | None = None,
) -> None:
    """Synchronize purchased Jump-mod nodes into the stateful Jump skill."""
    progression_state = state or getattr(player, "progression", None)
    if not isinstance(progression_state, ProgressionState):
        return
    jump_skill = player.spellbook.get("Skills", {}).get("Jump")
    if jump_skill is None or not hasattr(jump_skill, "unlock_modification"):
        return
    for node_id in progression_state.purchased_node_ids:
        node = TREE_NODES.get(node_id)
        if node is None:
            continue
        modification = node.payload.get("jump_modification")
        if modification:
            jump_skill.unlock_modification(str(modification))


def initialize_progression(player: Any) -> PurchaseResult:
    """Initialize a new player with one freely allocatable point."""
    player.progression = ProgressionState(
        level=1,
        total_xp=0,
        unspent_points=1,
        unspent_attribute_points=0,
    )
    _sync_level(player)
    return PurchaseResult(
        True,
        "Progression initialized with 1 unspent point.",
        points_remaining=1,
    )


def _sync_level(player: Any) -> None:
    state = player.progression
    player.level.level = state.level
    player.level.pro_level = class_tier(player)
    player.level.exp = state.total_xp
    player.level.exp_to_gain = (
        "MAX"
        if state.level >= MAX_PLAYER_LEVEL
        else cumulative_experience_for_level(state.level + 1) - state.total_xp
    )


def _roll_growth(player: Any, rng: random.Random) -> GrowthResult:
    luck = player.check_mod
    divisor = max(
        1,
        LEVELUP_LUCK_DIVISOR_BASE
        - luck("luck", luck_factor=LEVELUP_LUCK_FACTOR_HP_MP),
    )
    health = rng.randint(player.stats.con // divisor, player.stats.con)
    mana = rng.randint(player.stats.intel // divisor, player.stats.intel)
    attack = rng.randint(
        0,
        luck("luck", luck_factor=LEVELUP_ATK_LUCK_FACTOR)
        + (player.stats.strength // LEVELUP_STAT_DIVISOR)
        + max(1, player.cls.att_plus // 2),
    )
    defense = rng.randint(
        0,
        luck("luck", luck_factor=LEVELUP_DEF_LUCK_FACTOR)
        + (player.stats.con // LEVELUP_STAT_DIVISOR)
        + max(1, player.cls.def_plus // 2),
    )
    magic = rng.randint(
        0,
        luck("luck", luck_factor=LEVELUP_MAG_LUCK_FACTOR)
        + (player.stats.intel // LEVELUP_STAT_DIVISOR)
        + max(1, player.cls.int_plus // 2),
    )
    magic_defense = rng.randint(
        0,
        luck("luck", luck_factor=LEVELUP_MDEF_LUCK_FACTOR)
        + (player.stats.wisdom // LEVELUP_STAT_DIVISOR)
        + max(1, player.cls.wis_plus // 2),
    )
    player.health.max += health
    player.mana.max += mana
    player.combat.attack += attack
    player.combat.defense += defense
    player.combat.magic += magic
    player.combat.magic_def += magic_defense
    if player.in_town():
        player.health.current = player.health.max
        player.mana.current = player.mana.max
    return GrowthResult(health, mana, attack, defense, magic, magic_defense)


def award_experience(
    player: Any,
    amount: int,
    rng: random.Random | None = None,
) -> LevelUpResult:
    """Award total XP, carry across levels, and stop at global level 100."""
    state = ensure_progression(player)
    requested = max(0, int(amount))
    old_level = state.level
    maximum_xp = cumulative_experience_for_level(MAX_PLAYER_LEVEL)
    awarded = min(requested, max(0, maximum_xp - state.total_xp))
    state.total_xp += awarded
    growth: list[GrowthResult] = []
    points_awarded = 0
    attribute_points_awarded = 0
    generator = rng or random

    while (
        state.level < MAX_PLAYER_LEVEL
        and state.total_xp >= cumulative_experience_for_level(state.level + 1)
    ):
        state.level += 1
        if state.level % 2 == 0:
            state.unspent_points += 1
            points_awarded += 1
        if state.level % 4 == 0:
            state.unspent_attribute_points += 1
            attribute_points_awarded += 1
        growth.append(_roll_growth(player, generator))
    _sync_level(player)
    if hasattr(player, "refresh_highest_level"):
        player.refresh_highest_level()
    return LevelUpResult(
        experience_awarded=awarded,
        old_level=old_level,
        new_level=state.level,
        points_awarded=points_awarded,
        growth=tuple(growth),
        reached_max_level=state.level == MAX_PLAYER_LEVEL,
        attribute_points_awarded=attribute_points_awarded,
    )


def _outside_combat(player: Any) -> bool:
    return not bool(
        getattr(player, "in_combat", False)
        or getattr(player, "combat_active", False)
        or getattr(player, "_active_combat", False)
    )


def increase_attribute(player: Any, stat_name: str) -> PurchaseResult:
    """Permanently increase one primary attribute for one point."""
    state = ensure_progression(player)
    normalized = stat_name.strip().lower().replace("intelligence", "intel")
    normalized = normalized.replace("constitution", "con").replace("dexterity", "dex")
    if not _outside_combat(player):
        return PurchaseResult(False, "Progression purchases are unavailable in combat.")
    if normalized not in PRIMARY_ATTRIBUTES:
        return PurchaseResult(False, f"Unknown primary attribute: {stat_name}.")
    if state.unspent_attribute_points < 1:
        return PurchaseResult(False, "No attribute points are available.")
    setattr(player.stats, normalized, getattr(player.stats, normalized) + 1)
    state.trained_attributes[normalized] = state.trained_attributes.get(normalized, 0) + 1
    state.unspent_attribute_points -= 1
    return PurchaseResult(
        True,
        f"{normalized.replace('intel', 'intelligence').title()} increased by 1.",
        points_remaining=state.unspent_points,
    )


def _race_allows(player: Any, target_class: str) -> bool:
    if class_tier(player) != 1:
        return True
    allowed = getattr(getattr(player, "race", None), "cls_res", {}).get("First", ())
    return not allowed or target_class in allowed


def _node_blockers(
    player: Any,
    node: AbilityTreeNode,
    *,
    purchased_node_ids: set[str] | None = None,
    remaining_points: int | None = None,
    planned_attributes: dict[str, int] | None = None,
) -> tuple[str, ...]:
    state = ensure_progression(player)
    purchased = (
        state.purchased_node_ids
        if purchased_node_ids is None
        else purchased_node_ids
    )
    points = state.unspent_points if remaining_points is None else remaining_points
    attribute_plan = planned_attributes or {}
    blockers: list[str] = []
    if points < node.cost:
        noun = "point" if node.cost == 1 else "points"
        blockers.append(f"Requires {node.cost} {noun}.")
    prerequisite_mode = node.payload.get("prerequisite_mode", "all")

    def prerequisite_path_satisfied(node_id: str, visiting: set[str]) -> bool:
        """Require an unbroken purchased path through inherited nodes."""
        if node_id not in purchased or node_id in visiting:
            return False
        prerequisite_node = TREE_NODES[node_id]
        if not prerequisite_node.prerequisites:
            return True
        next_visiting = {*visiting, node_id}
        satisfied = [
            prerequisite_path_satisfied(prerequisite, next_visiting)
            for prerequisite in prerequisite_node.prerequisites
        ]
        if prerequisite_node.payload.get("prerequisite_mode", "all") == "any":
            return any(satisfied)
        return all(satisfied)

    if prerequisite_mode == "any" and node.prerequisites:
        if not any(
            prerequisite_path_satisfied(prerequisite, set())
            for prerequisite in node.prerequisites
        ):
            names = " or ".join(
                TREE_NODES[prerequisite].name
                for prerequisite in node.prerequisites
            )
            blockers.append(f"Requires {names}.")
    else:
        for prerequisite in node.prerequisites:
            if not prerequisite_path_satisfied(prerequisite, set()):
                blockers.append(f"Requires {TREE_NODES[prerequisite].name}.")
    required_level = effective_node_level_requirement(
        node,
        progression_class_name(player),
    )
    if required_level and state.level < required_level:
        blockers.append(
            f"Requires level {required_level} (current {state.level})."
        )
    required_ability = str(
        node.payload.get("requires_known_ability", "") or ""
    )
    if required_ability and not any(
        required_ability in player.spellbook.get(book, {})
        for book in ("Spells", "Skills")
    ):
        blockers.append(f"Requires learned ability {required_ability}.")
    quest_unlock = str(node.payload.get("quest_unlock", "") or "")
    if quest_unlock:
        quest = getattr(player, "quest_dict", {}).get("Side", {}).get(
            quest_unlock,
            {},
        )
        if not bool(quest.get("Turned In")):
            blockers.append(f"Requires completing {quest_unlock}.")
    school_affinity = node.payload.get("school_affinity")
    if school_affinity:
        from .classes import wizard

        school_name, required_affinity = school_affinity
        current_affinity = wizard.ensure_affinity(player).get(str(school_name), 0)
        if current_affinity < float(required_affinity):
            blockers.append(
                f"Requires {required_affinity:g} {school_name} affinity "
                f"(current {current_affinity:g})."
            )
    if node.kind == NodeKind.ABILITY:
        exclusive_group = node.payload.get("exclusive_group")
        if exclusive_group:
            selected = next(
                (
                    candidate
                    for candidate in TREE_NODES.values()
                    if candidate.id in purchased
                    and candidate.id != node.id
                    and candidate.payload.get("exclusive_group") == exclusive_group
                ),
                None,
            )
            if selected is not None:
                blockers.append(
                    f"{selected.name} permanently closed this style path."
                )
        specialization = node.payload.get("weapon_specialization")
        if specialization:
            from .classes import grandmaster

            weapon_type, required_rank = specialization
            current_rank = grandmaster.discipline_rank(player, weapon_type)
            if current_rank < int(required_rank):
                blockers.append(
                    f"Requires {weapon_type} specialization level "
                    f"{required_rank} (current {current_rank})."
                )
        ability_ctor = node.payload["ability_class"]
        from .player.stats import _upgrade_source_name

        source_name = _upgrade_source_name(ability_ctor)
        planned_names = {
            TREE_NODES[node_id].name
            for node_id in purchased - state.purchased_node_ids
            if TREE_NODES[node_id].kind == NodeKind.ABILITY
        }
        if (
            source_name
            and not node.payload.get("upgrade_without_source")
            and source_name not in planned_names
            and not any(
                source_name in player.spellbook.get(book, {})
                for book in ("Spells", "Skills")
            )
        ):
            blockers.append(f"Requires learned ability {source_name}.")
    if node.kind == NodeKind.PROMOTION:
        target_class = node.payload["target_class"]
        permanent_class = getattr(player, "transform_type", None)
        if (
            (
                permanent_class is not None
                and getattr(permanent_class, "name", None) != player.cls.name
            )
            or getattr(player, "state", "normal") != "normal"
        ):
            blockers.append("Return to your permanent form before promotion.")
        if not _race_allows(player, target_class):
            blockers.append(f"{player.race.name} cannot promote to {target_class}.")
        for stat_name, requirement in node.payload["requirements"].items():
            current = int(getattr(player.stats, stat_name))
            current += int(attribute_plan.get(stat_name, 0))
            if current < requirement:
                blockers.append(
                    f"Requires {stat_name.replace('intel', 'intelligence').title()} "
                    f"{requirement} (current {current})."
                )
    return tuple(blockers)


def available_nodes(
    player: Any,
    tree_id: str | None = None,
    *,
    planned_node_ids: tuple[str, ...] | list[str] | set[str] = (),
    planned_attributes: dict[str, int] | None = None,
) -> list[NodeStatus]:
    """Return owned, available, blocked, and closed nodes for one tree."""
    state = ensure_progression(player)
    selected_tree = tree_id or progression_class_name(player)
    tree = ABILITY_TREES[selected_tree]
    is_closed = selected_tree in state.completed_trees
    planned = {
        node_id
        for node_id in planned_node_ids
        if node_id in TREE_NODES
    }
    effective_purchased = state.purchased_node_ids | planned
    planned_cost = sum(TREE_NODES[node_id].cost for node_id in planned)
    remaining_points = state.unspent_points - planned_cost
    planned_promotions = {
        node_id
        for node_id in planned
        if TREE_NODES[node_id].kind == NodeKind.PROMOTION
    }
    selected_exclusive_nodes = {
        str(node.payload["exclusive_group"]): node.id
        for node in tree.nodes
        if node.id in effective_purchased
        and node.payload.get("exclusive_group")
    }
    choice_closed: dict[str, bool] = {}

    def is_choice_closed(node: AbilityTreeNode) -> bool:
        """Return whether a permanent exclusive choice made this node unreachable."""
        if node.id in choice_closed:
            return choice_closed[node.id]
        exclusive_group = node.payload.get("exclusive_group")
        selected = selected_exclusive_nodes.get(str(exclusive_group))
        if selected is not None and selected != node.id:
            choice_closed[node.id] = True
            return True
        closed_prerequisites = [
            is_choice_closed(TREE_NODES[prerequisite])
            for prerequisite in node.prerequisites
        ]
        if not closed_prerequisites:
            closed = False
        elif node.payload.get("prerequisite_mode", "all") == "any":
            closed = all(closed_prerequisites)
        else:
            closed = any(closed_prerequisites)
        choice_closed[node.id] = closed
        return closed

    statuses: list[NodeStatus] = []
    learned_names = {
        name
        for book in getattr(player, "spellbook", {}).values()
        for name in getattr(book, "keys", lambda: ())()
    }
    for node in tree.nodes:
        hidden_until_known = str(
            node.payload.get("hidden_until_known", "") or ""
        )
        if hidden_until_known and hidden_until_known not in learned_names:
            continue
        display_node = node
        revealed_name = str(node.payload.get("revealed_name", "") or "")
        if revealed_name and revealed_name in learned_names:
            display_node = replace(
                node,
                payload={**node.payload, "name": revealed_name},
            )
        if node.id in effective_purchased:
            statuses.append(NodeStatus(display_node, NodeState.OWNED))
        elif is_closed:
            statuses.append(NodeStatus(
                display_node,
                NodeState.CLOSED,
                ("This completed branch is permanently closed.",),
            ))
        elif is_choice_closed(node):
            statuses.append(NodeStatus(
                display_node,
                NodeState.CLOSED,
                ("The competing style path was chosen permanently.",),
            ))
        else:
            blockers = _node_blockers(
                player,
                node,
                purchased_node_ids=effective_purchased,
                remaining_points=remaining_points,
                planned_attributes=planned_attributes,
            )
            if (
                node.kind == NodeKind.PROMOTION
                and planned_promotions
                and node.id not in planned_promotions
            ):
                blockers = (
                    *blockers,
                    "Another promotion is already distributed.",
                )
            permanently_unavailable_promotion = (
                node.kind == NodeKind.PROMOTION
                and (
                    not _race_allows(
                        player,
                        node.payload["target_class"],
                    )
                    or (
                        bool(planned_promotions)
                        and node.id not in planned_promotions
                    )
                )
            )
            statuses.append(NodeStatus(
                display_node,
                (
                    NodeState.CLOSED
                    if permanently_unavailable_promotion
                    else NodeState.BLOCKED
                    if blockers
                    else NodeState.AVAILABLE
                ),
                blockers,
            ))
    return statuses


def permanent_closures_for_plan(
    player: Any,
    tree_id: str,
    planned_node_ids: tuple[str, ...] | list[str] | set[str],
) -> tuple[str, ...]:
    """List currently open development nodes a staged choice will close forever."""
    planned = {
        node_id
        for node_id in planned_node_ids
        if node_id in TREE_NODES
        and TREE_NODES[node_id].kind != NodeKind.PROMOTION
    }
    if not planned:
        return ()
    before = {
        status.node.id: status
        for status in available_nodes(player, tree_id)
    }
    after = available_nodes(player, tree_id, planned_node_ids=planned)
    closures = {
        status.node.name
        for status in after
        if status.node.id not in planned
        and status.state == NodeState.CLOSED
        and before[status.node.id].state != NodeState.CLOSED
        and status.node.kind != NodeKind.PROMOTION
    }
    return tuple(sorted(closures))


def _grant_ability(player: Any, node: AbilityTreeNode) -> str:
    ability_ctor = node.payload["ability_class"]
    ability = ability_ctor()
    book_name = node.payload["book"]
    book = player.spellbook[book_name]
    if node.payload.get("stack_if_known") and ability.name in book:
        existing = book[ability.name]
        state = ensure_progression(player)
        existing.ranks = max(
            1,
            int(state.ability_ranks.get(ability.name, 1) or 1),
        ) + 1
        state.ability_ranks[ability.name] = existing.ranks
        return f"{ability.name} {existing.ranks}"
    from .player.stats import _upgrade_source_name

    old_name = _upgrade_source_name(ability_ctor)
    if old_name:
        for candidate_book in player.spellbook.values():
            candidate_book.pop(old_name, None)
    if ability.name == "Health/Mana Drain":
        for old_name in ("Health Drain", "Mana Drain"):
            player.spellbook["Skills"].pop(old_name, None)
    elif ability.name == "True Piercing Strike":
        for old_name in ("Piercing Strike", "True Strike"):
            player.spellbook["Skills"].pop(old_name, None)
    elif ability.name == "Triple Strike":
        player.spellbook["Skills"].pop("Double Strike", None)
    elif ability.name == "Flurry of Blades":
        player.spellbook["Skills"].pop("Triple Strike", None)
    book[ability.name] = ability
    if node.payload.get("stack_if_known"):
        ensure_progression(player).ability_ranks.setdefault(ability.name, 1)
    if ability.name in ("Transform", "Purity of Body", "Reveal"):
        ability.use(player)
    return ability.name


def _grant_talent(player: Any, node: AbilityTreeNode) -> None:
    """Apply the immediate permanent bonuses attached to a talent."""
    bonuses = node.payload.get("bonuses", {})
    for rating_name, amount in bonuses.get("ratings", {}).items():
        rating_attr = RATING_PAYLOADS[rating_name]
        setattr(
            player.combat,
            rating_attr,
            getattr(player.combat, rating_attr) + int(amount),
        )
    for rating_name, percentage in bonuses.get(
        "rating_percentages",
        {},
    ).items():
        rating_attr = RATING_PAYLOADS[rating_name]
        current = int(getattr(player.combat, rating_attr))
        amount = max(1, math.ceil(current * float(percentage)))
        setattr(player.combat, rating_attr, current + amount)
    for resource_name in ("health", "mana"):
        amount = int(bonuses.get(resource_name, 0) or 0)
        if not amount:
            continue
        resource = getattr(player, resource_name)
        resource.max += amount
        resource.current += amount
    for resource_name in ("health", "mana"):
        percentage = float(
            bonuses.get(f"{resource_name}_percentage", 0) or 0
        )
        if not percentage:
            continue
        resource = getattr(player, resource_name)
        amount = max(1, math.ceil(resource.max * percentage))
        resource.max += amount
        resource.current += amount
    jump_modification = node.payload.get("jump_modification")
    if jump_modification:
        jump_skill = player.spellbook.get("Skills", {}).get("Jump")
        if (
            jump_skill is None
            or not hasattr(jump_skill, "unlock_modification")
            or not jump_skill.unlock_modification(str(jump_modification))
        ):
            raise ValueError(
                f"Jump cannot unlock the {jump_modification} modification."
            )


def _equipment_conflicts(player: Any, target_class: Any) -> tuple[str, ...]:
    from .classes import ability_mechanics

    conflicts: list[str] = []
    for slot in ("Weapon", "OffHand", "Armor", "Helmet"):
        item = getattr(player, "equipment", {}).get(slot)
        if item is None or getattr(item, "subtyp", None) == "None":
            continue
        try:
            legal = target_class.equip_check(item, slot)
            legal = legal or ability_mechanics.can_dual_wield_item(
                player,
                item,
                slot,
            )
        except (KeyError, TypeError, ValueError):
            legal = False
        if not legal:
            conflicts.append(f"{slot}: {getattr(item, 'name', item)}")
    return tuple(conflicts)


def promotion_combat_bonuses(target_class: Any) -> dict[str, int]:
    """Return one-time combat bonuses scaled by promotion depth."""
    scale = max(1, int(getattr(target_class, "pro_level", 1)))
    return {
        "attack": int(getattr(target_class, "att_plus", 0)) * scale,
        "defense": int(getattr(target_class, "def_plus", 0)) * scale,
        "magic": int(getattr(target_class, "magic_plus", 0)) * scale,
        "magic defense": (
            int(getattr(target_class, "magic_def_plus", 0)) * scale
        ),
    }


def _promotion_closure_warning(source_class: str, target_class: str) -> str:
    """Describe which prior-tree development remains after promotion."""
    if (source_class, target_class) == ("Lancer", "Dragoon"):
        return (
            "All Lancer development nodes remain purchasable in the Dragoon "
            "tree after promotion."
        )
    if (source_class, target_class) == ("Mage", "Sorcerer"):
        return (
            "Unpurchased Mage nodes and competing promotions close permanently. "
            "Sorcerer tier-two spells unlock through matching School Affinity."
        )
    if (source_class, target_class) == ("Sorcerer", "Wizard"):
        return (
            "Unpurchased Sorcerer nodes close permanently. Learned spells and "
            "passives are retained in the Wizard spellbook."
        )
    if (source_class, target_class) == ("Conjurer", "Thaumaturgist"):
        return (
            "Conjure Animal and all six Conjurer Calling nodes appear in the "
            "Thaumaturgist tree. Other unpurchased Conjurer nodes close "
            "permanently; each Calling gains a permanent paired-Xenid choice."
        )
    return (
        f"Promoting permanently closes all unpurchased {source_class} nodes "
        "and competing promotions. Learned abilities are retained."
    )


def promotion_preview(player: Any, node_id: str) -> PromotionPreview:
    """Build the mandatory confirmation details for a promotion node."""
    node = TREE_NODES[node_id]
    if node.kind != NodeKind.PROMOTION:
        raise ValueError(f"{node_id} is not a promotion node")
    target = node.payload["target_class_ctor"]()
    combat_bonuses = promotion_combat_bonuses(target)
    bonuses = {
        "strength": target.str_plus,
        "intelligence": target.int_plus,
        "wisdom": target.wis_plus,
        "constitution": target.con_plus,
        "charisma": target.cha_plus,
        "dexterity": target.dex_plus,
        "health": target.con_plus * 2,
        "mana": target.int_plus * 2,
        **combat_bonuses,
    }
    return PromotionPreview(
        node_id=node.id,
        source_class=node.tree_id,
        target_class=target.name,
        level_requirement=int(node.payload["level_requirement"]),
        requirements=dict(node.payload["requirements"]),
        bonuses=bonuses,
        equipment_conflicts=_equipment_conflicts(player, target),
        warning=_promotion_closure_warning(node.tree_id, target.name),
    )


def _remove_illegal_gear(player: Any) -> tuple[str, ...]:
    from .classes import ability_mechanics
    from .items import remove_equipment

    removed: list[str] = []
    for slot in ("Weapon", "OffHand", "Armor", "Helmet"):
        item = player.equipment.get(slot)
        if item is None or getattr(item, "subtyp", None) == "None":
            continue
        try:
            legal = player.cls.equip_check(item, slot)
            legal = legal or ability_mechanics.can_dual_wield_item(
                player,
                item,
                slot,
            )
        except (KeyError, TypeError, ValueError):
            legal = False
        if legal:
            continue
        if hasattr(player, "modify_inventory"):
            player.modify_inventory(item, 1)
        player.equipment[slot] = remove_equipment(slot)
        removed.append(f"{slot}: {getattr(item, 'name', item)}")
    return tuple(removed)


def _apply_promotion(
    player: Any,
    node: AbilityTreeNode,
    choices: dict[str, Any] | None,
) -> tuple[str, ...]:
    choices = choices or {}
    new_class = node.payload["target_class_ctor"]()
    target_name = new_class.name
    if target_name == "Paladin" and not choices.get("vow"):
        raise ValueError("A Paladin vow must be selected before promotion.")
    if target_name == "Warlock" and not choices.get("familiar"):
        raise ValueError("A familiar must be selected before promotion.")

    old_class_name = player.cls.name
    permanent_class = getattr(player, "transform_type", None)
    player.cls = new_class
    if (
        permanent_class is None
        or getattr(permanent_class, "name", None) == old_class_name
    ):
        player.transform_type = new_class
    for stat_name, bonus_name in (
        ("strength", "str_plus"),
        ("intel", "int_plus"),
        ("wisdom", "wis_plus"),
        ("con", "con_plus"),
        ("charisma", "cha_plus"),
        ("dex", "dex_plus"),
    ):
        setattr(player.stats, stat_name, getattr(player.stats, stat_name) + getattr(new_class, bonus_name))
    health_bonus = new_class.con_plus * 2
    mana_bonus = new_class.int_plus * 2
    player.health.max += health_bonus
    player.health.current = min(player.health.max, player.health.current + health_bonus)
    player.mana.max += mana_bonus
    player.mana.current = min(player.mana.max, player.mana.current + mana_bonus)
    combat_bonuses = promotion_combat_bonuses(new_class)
    player.combat.attack += combat_bonuses["attack"]
    player.combat.defense += combat_bonuses["defense"]
    player.combat.magic += combat_bonuses["magic"]
    player.combat.magic_def += combat_bonuses["magic defense"]
    removed = _remove_illegal_gear(player)

    if target_name == "Paladin":
        success, message = player.choose_paladin_vow(choices["vow"])
        if not success:
            raise ValueError(message)
    elif target_name == "Warlock":
        player.familiar = choices["familiar"]
        player.spellbook["Skills"]["Familiar"] = abilities.Familiar()
    elif target_name == "Demonologist":
        player.spellbook["Skills"]["Call Contract"] = abilities.CallContract()
        player.ensure_demonologist_contracts()
    elif target_name == "Ranger":
        player.spellbook["Skills"]["Tame"] = abilities.Tame()
        player.ensure_tamed_companion()
    elif target_name == "Stalwart Defender":
        for ability_ctor in (
            abilities.CitadelAegis,
            abilities.IronwallReprisal,
            abilities.LastBastionSurge,
            abilities.Stronghold,
        ):
            ability = ability_ctor()
            player.spellbook["Skills"][ability.name] = ability
    if target_name in ("Seeker", "Wizard"):
        player.teleport = (player.location_x, player.location_y, player.location_z)
    from .classes import class_rings, promotion_kits

    promotion_kits.clear_combat_state(player)
    class_rings.reset_combat_flags(player)
    _adopt_known_ability_nodes(player, ensure_progression(player))
    return removed


def _purchase_snapshot(player: Any) -> dict[str, Any]:
    """Capture all state mutated by progression purchases."""
    return {
        "progression": copy.deepcopy(ensure_progression(player)),
        "cls": player.cls,
        "transform_type": getattr(player, "transform_type", None),
        "stats": copy.deepcopy(player.stats),
        "health": copy.deepcopy(player.health),
        "mana": copy.deepcopy(player.mana),
        "combat": copy.deepcopy(player.combat),
        "equipment": copy.deepcopy(getattr(player, "equipment", {})),
        "inventory": copy.deepcopy(getattr(player, "inventory", {})),
        "spellbook": copy.deepcopy(player.spellbook),
        "familiar": getattr(player, "familiar", None),
        "summons": copy.deepcopy(getattr(player, "summons", {})),
        "special_fields": {
            field_name: copy.deepcopy(getattr(player, field_name, None))
            for field_name in (
                "paladin_vow",
                "demonologist_contracts",
                "promotion_kit_state",
                "teleport",
                "xenid_choices",
            )
        },
    }


def _restore_purchase_snapshot(player: Any, snapshot: dict[str, Any]) -> None:
    """Restore a progression purchase snapshot after an atomic failure."""
    player.progression = snapshot["progression"]
    player.cls = snapshot["cls"]
    player.transform_type = snapshot["transform_type"]
    player.stats = snapshot["stats"]
    player.health = snapshot["health"]
    player.mana = snapshot["mana"]
    player.combat = snapshot["combat"]
    player.equipment = snapshot["equipment"]
    player.inventory = snapshot["inventory"]
    player.spellbook = snapshot["spellbook"]
    player.familiar = snapshot["familiar"]
    player.summons = snapshot["summons"]
    for field_name, value in snapshot["special_fields"].items():
        setattr(player, field_name, value)
    _sync_level(player)


def purchase_node(
    player: Any,
    node_id: str,
    *,
    confirm_promotion: bool = False,
    promotion_choices: dict[str, Any] | None = None,
    node_choices: dict[str, Any] | None = None,
    allow_in_combat: bool = False,
) -> PurchaseResult:
    """Permanently purchase one node and atomically apply its payload."""
    state = ensure_progression(player)
    node = TREE_NODES.get(node_id)
    if node is None:
        return PurchaseResult(False, f"Unknown progression node: {node_id}.")
    if node.id in state.purchased_node_ids:
        return PurchaseResult(False, f"{node.name} is already owned.", node.id, state.unspent_points)
    if not allow_in_combat and not _outside_combat(player):
        return PurchaseResult(False, "Progression purchases are unavailable in combat.")
    current_class = player.cls.name
    carried_node = _is_carried_node(
        node,
        current_class,
        state.completed_trees,
    )
    if node.tree_id != current_class and not carried_node:
        return PurchaseResult(False, "Only the current class tree can be edited.")
    if node.tree_id in state.completed_trees and not carried_node:
        return PurchaseResult(False, "That completed tree is permanently closed.")
    blockers = _node_blockers(player, node)
    if blockers:
        return PurchaseResult(False, " ".join(blockers), node.id, state.unspent_points)
    if node.kind == NodeKind.PROMOTION and not confirm_promotion:
        return PurchaseResult(
            False,
            "Promotion requires confirmation after reviewing its permanent effects.",
            node.id,
            state.unspent_points,
        )

    snapshot = _purchase_snapshot(player)
    try:
        promoted_to = None
        removed: tuple[str, ...] = ()
        if node.kind == NodeKind.ABILITY:
            learned = _grant_ability(player, node)
            message = f"Learned {learned}."
        elif node.kind == NodeKind.TALENT:
            category = node.payload.get("xenid_category")
            if category:
                from . import companions

                selected = str((node_choices or {}).get("xenid", "") or "")
                success, choice_message = companions.choose_xenid(
                    player,
                    str(category),
                    selected,
                )
                if not success:
                    raise ValueError(choice_message)
            ultimate_category = node.payload.get("xenid_ultimate_category")
            if ultimate_category:
                from . import companions

                success, choice_message = companions.unlock_xenid_ultimate(
                    player,
                    str(ultimate_category),
                )
                if not success:
                    raise ValueError(choice_message)
            _grant_talent(player, node)
            message = (
                choice_message
                if category or ultimate_category
                else f"Learned talent {node.name}."
            )
        elif node.kind == NodeKind.RATING:
            rating_attr = RATING_PAYLOADS[node.payload["rating"]]
            amount = int(node.payload["amount"])
            setattr(player.combat, rating_attr, getattr(player.combat, rating_attr) + amount)
            message = f"{node.payload['rating']} increased by {amount}."
        elif node.kind == NodeKind.HEALTH:
            amount = int(node.payload["amount"])
            player.health.max += amount
            player.health.current = min(
                player.health.max,
                player.health.current + amount,
            )
            message = f"Maximum HP increased by {amount}."
        elif node.kind == NodeKind.MANA:
            amount = int(node.payload["amount"])
            player.mana.max += amount
            player.mana.current = min(
                player.mana.max,
                player.mana.current + amount,
            )
            message = f"Maximum MP increased by {amount}."
        else:
            removed = _apply_promotion(player, node, promotion_choices)
            promoted_to = node.payload["target_class"]
            state.completed_trees.add(node.tree_id)
            state.chosen_promotions[node.tree_id] = promoted_to
            if (node.tree_id, promoted_to) == ("Lancer", "Dragoon"):
                message = (
                    "Promoted to Dragoon; remaining Lancer training is retained "
                    "in the Dragoon tree."
                )
            elif (node.tree_id, promoted_to) == ("Mage", "Sorcerer"):
                message = (
                    "Promoted to Sorcerer; remaining Mage elemental-school "
                    "training is retained through Wizard."
                )
            elif (node.tree_id, promoted_to) == ("Sorcerer", "Wizard"):
                message = (
                    "Promoted to Wizard; remaining Mage elemental-school "
                    "training is retained."
                )
            else:
                message = (
                    f"Promoted to {promoted_to}; unpurchased {node.tree_id} "
                    "nodes are now closed."
                )
        state.purchased_node_ids.add(node.id)
        state.unspent_points -= node.cost
        _sync_level(player)
        return PurchaseResult(
            True,
            message,
            node.id,
            state.unspent_points,
            promoted_to,
            removed,
        )
    except Exception as exc:
        _restore_purchase_snapshot(player, snapshot)
        return PurchaseResult(False, f"Purchase failed: {exc}", node.id, state.unspent_points)


def apply_progression_plan(
    player: Any,
    node_ids: tuple[str, ...] | list[str],
    attribute_increases: dict[str, int],
    *,
    promotion_choices: dict[str, dict[str, Any]] | None = None,
    node_choices: dict[str, dict[str, Any]] | None = None,
) -> PurchaseResult:
    """Atomically commit a staged set of node and attribute purchases."""
    state = ensure_progression(player)
    nodes = list(dict.fromkeys(node_ids))
    attributes = {
        name: int(amount)
        for name, amount in attribute_increases.items()
        if int(amount) > 0
    }
    unknown_nodes = [node_id for node_id in nodes if node_id not in TREE_NODES]
    if unknown_nodes:
        return PurchaseResult(
            False,
            f"Unknown progression node: {unknown_nodes[0]}.",
            points_remaining=state.unspent_points,
        )
    unknown_attributes = [
        name
        for name in attributes
        if name not in PRIMARY_ATTRIBUTES
    ]
    if unknown_attributes:
        return PurchaseResult(
            False,
            f"Unknown primary attribute: {unknown_attributes[0]}.",
            points_remaining=state.unspent_points,
        )
    node_cost = sum(
        TREE_NODES[node_id].cost
        for node_id in nodes
    )
    attribute_cost = sum(attributes.values())
    if node_cost + attribute_cost <= 0:
        return PurchaseResult(
            False,
            "No points have been distributed.",
            points_remaining=state.unspent_points,
        )
    if node_cost > state.unspent_points:
        return PurchaseResult(
            False,
            "The staged nodes exceed the available progression points.",
            points_remaining=state.unspent_points,
        )
    if attribute_cost > state.unspent_attribute_points:
        return PurchaseResult(
            False,
            "The staged attributes exceed the available attribute points.",
            points_remaining=state.unspent_points,
        )
    if not _outside_combat(player):
        return PurchaseResult(
            False,
            "Progression purchases are unavailable in combat.",
            points_remaining=state.unspent_points,
        )

    snapshot = _purchase_snapshot(player)
    try:
        for stat_name in PRIMARY_ATTRIBUTES:
            for _index in range(attributes.get(stat_name, 0)):
                result = increase_attribute(player, stat_name)
                if not result.success:
                    raise ValueError(result.message)

        ordinary_nodes = [
            node_id
            for node_id in nodes
            if TREE_NODES.get(node_id, None)
            and TREE_NODES[node_id].kind != NodeKind.PROMOTION
        ]
        promotion_nodes = [
            node_id
            for node_id in nodes
            if TREE_NODES.get(node_id, None)
            and TREE_NODES[node_id].kind == NodeKind.PROMOTION
        ]
        if len(promotion_nodes) > 1:
            raise ValueError("Only one promotion can be purchased at a time.")

        pending = ordinary_nodes[:]
        while pending:
            progressed = False
            for node_id in pending[:]:
                result = purchase_node(
                    player,
                    node_id,
                    node_choices=(node_choices or {}).get(node_id),
                )
                if not result.success:
                    continue
                pending.remove(node_id)
                progressed = True
            if not progressed:
                first = pending[0]
                failure = purchase_node(
                    player,
                    first,
                    node_choices=(node_choices or {}).get(first),
                )
                raise ValueError(failure.message)

        promoted_to = None
        promotion_message = ""
        removed_equipment: tuple[str, ...] = ()
        for node_id in promotion_nodes:
            result = purchase_node(
                player,
                node_id,
                confirm_promotion=True,
                promotion_choices=(promotion_choices or {}).get(node_id),
            )
            if not result.success:
                raise ValueError(result.message)
            promoted_to = result.promoted_to
            promotion_message = result.message
            removed_equipment = result.removed_equipment
        spent_parts = []
        if node_cost:
            spent_parts.append(
                f"{node_cost} progression point"
                f"{'s' if node_cost != 1 else ''}"
            )
        if attribute_cost:
            spent_parts.append(
                f"{attribute_cost} attribute point"
                f"{'s' if attribute_cost != 1 else ''}"
            )
        message = f"Spent {' and '.join(spent_parts)}."
        if promotion_message:
            message = f"{message} {promotion_message}"
        return PurchaseResult(
            True,
            message,
            points_remaining=player.progression.unspent_points,
            promoted_to=promoted_to,
            removed_equipment=removed_equipment,
        )
    except Exception as exc:
        _restore_purchase_snapshot(player, snapshot)
        return PurchaseResult(
            False,
            f"Purchase failed: {exc}",
            points_remaining=player.progression.unspent_points,
        )


def level_up_message(result: LevelUpResult) -> str:
    """Build a frontend-neutral level-up summary."""
    if result.new_level == result.old_level:
        return f"Gained {result.experience_awarded} experience."
    lines = [f"Reached global level {result.new_level}."]
    if result.points_awarded:
        lines.append(
            f"+{result.points_awarded} progression point"
            f"{'s' if result.points_awarded != 1 else ''}."
        )
    else:
        lines.append("No progression point awarded at this level.")
    if result.attribute_points_awarded:
        lines.append(
            f"+{result.attribute_points_awarded} attribute point"
            f"{'s' if result.attribute_points_awarded != 1 else ''}."
        )
    for index, growth in enumerate(result.growth, start=result.old_level + 1):
        values = asdict(growth)
        details = ", ".join(f"+{amount} {name.replace('_', ' ')}" for name, amount in values.items())
        lines.append(f"Level {index}: {details}.")
    return "\n".join(lines)
