"""Versioned, non-destructive migrations for persisted player saves."""

from __future__ import annotations

import copy
from dataclasses import dataclass
import re
from typing import Any

from ..progression import (
    CLASS_DETAILS,
    MAX_PLAYER_LEVEL,
    attribute_points_through_level,
    cumulative_experience_for_level,
    progression_points_through_level,
)


CURRENT_SAVE_VERSION = 5
SUPPORTED_LEGACY_SAVE_VERSIONS = frozenset({3})
_LEGACY_LEVEL_OFFSETS = {1: 0, 2: 30, 3: 60}


class InvalidSaveDataError(ValueError):
    """Raised when a known save version contains unsafe or incomplete data."""


@dataclass(frozen=True)
class SaveMigration:
    """A validated save payload and its migration metadata."""

    data: dict[str, Any]
    source_version: int
    migrated: bool = False


def _integer(value: object, field_name: str) -> int:
    if isinstance(value, bool):
        raise InvalidSaveDataError(f"{field_name} must be an integer.")
    try:
        return int(value)
    except (TypeError, ValueError) as error:
        raise InvalidSaveDataError(f"{field_name} must be an integer.") from error


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _class_lineage(class_name: str) -> list[str]:
    if class_name not in CLASS_DETAILS:
        raise InvalidSaveDataError(f"Unknown legacy class: {class_name!r}.")
    lineage = [class_name]
    parent = CLASS_DETAILS[class_name][2]
    while parent is not None:
        lineage.append(parent)
        parent = CLASS_DETAILS[parent][2]
    return list(reversed(lineage))


def _migrate_version_3(data: dict[str, Any]) -> dict[str, Any]:
    migrated = copy.deepcopy(data)
    level_data = migrated.get("level")
    if not isinstance(level_data, dict):
        raise InvalidSaveDataError("Version 3 save is missing level data.")

    class_name = migrated.get("class_name")
    if not isinstance(class_name, str) or not class_name:
        raise InvalidSaveDataError("Version 3 save is missing its class name.")
    lineage = _class_lineage(class_name)
    class_stage = CLASS_DETAILS[class_name][1]
    legacy_stage = _integer(level_data.get("pro_level"), "level.pro_level")
    if legacy_stage != class_stage:
        raise InvalidSaveDataError(
            f"Legacy class {class_name!r} is stage {class_stage}, but the save records "
            f"promotion stage {legacy_stage}."
        )

    local_level = _integer(level_data.get("level"), "level.level")
    if local_level < 1:
        raise InvalidSaveDataError("level.level must be positive.")
    global_level = min(
        MAX_PLAYER_LEVEL,
        _LEGACY_LEVEL_OFFSETS[legacy_stage] + local_level,
    )

    completed_trees = lineage[:-1]
    chosen_promotions = dict(zip(lineage, lineage[1:]))
    promotion_nodes = [
        f"{_slug(source)}.promotion.{_slug(target)}"
        for source, target in zip(lineage, lineage[1:])
    ]
    migrated["version"] = CURRENT_SAVE_VERSION
    migrated["progression"] = {
        "level": global_level,
        "total_xp": cumulative_experience_for_level(global_level),
        "unspent_points": progression_points_through_level(global_level),
        # Version 3 already applied its every-four-level attribute choices to
        # the serialized stats. Re-granting those choices would duplicate them.
        "unspent_attribute_points": 0,
        "purchased_node_ids": promotion_nodes,
        "trained_attributes": {},
        "ability_ranks": {},
        "completed_trees": completed_trees,
        "chosen_promotions": chosen_promotions,
    }
    return migrated


def migrate_save_data(data: object) -> SaveMigration:
    """Validate and migrate a supported save payload to the current version."""
    if not isinstance(data, dict):
        raise InvalidSaveDataError("Save payload must be a JSON object.")
    version = _integer(data.get("version"), "version")
    if version == CURRENT_SAVE_VERSION:
        if not isinstance(data.get("progression"), dict):
            raise InvalidSaveDataError("Version 5 save is missing progression data.")
        return SaveMigration(copy.deepcopy(data), version)
    if version == 3:
        return SaveMigration(_migrate_version_3(data), version, migrated=True)

    supported = ", ".join(str(item) for item in sorted(SUPPORTED_LEGACY_SAVE_VERSIONS))
    detail = (
        "Version 4 was never produced by a committed save serializer and cannot be "
        "migrated safely."
        if version == 4
        else f"Supported legacy versions: {supported}."
    )
    raise UnsupportedSaveVersionError(version, detail)


class UnsupportedSaveVersionError(ValueError):
    """Raised when repository history provides no safe migration contract."""

    def __init__(self, actual_version: object, detail: str = ""):
        message = (
            f"Unsupported save version {actual_version!r}; current version is "
            f"{CURRENT_SAVE_VERSION}."
        )
        if detail:
            message = f"{message} {detail}"
        super().__init__(message)
        self.actual_version = actual_version
        self.required_version = CURRENT_SAVE_VERSION
