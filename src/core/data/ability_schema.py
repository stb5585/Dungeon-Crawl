"""Validation and parsing for the canonical YAML ability contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

import yaml

from ..contracts import (
    AbilityActivation,
    AbilityDefinition,
    AbilityForm,
    AbilityMethod,
    AbilityOrigin,
    AbilityTaxonomy,
    PrimaryIntent,
    TargetingPolicy,
    TargetLossPolicy,
    TargetScope,
)
from .ability_traits import is_registered_ability_trait

ABILITY_DIRECTORY = Path(__file__).resolve().parent / "abilities"
LEGACY_ALLOWLIST_PATH = ABILITY_DIRECTORY / "legacy_taxonomy_allowlist.txt"
_CANONICAL_KEYS = frozenset({"id", "aliases", "taxonomy", "targeting"})
_TAXONOMY_KEYS = frozenset({"origin", "method", "primary_intent", "activation", "form", "traits"})
_TARGETING_KEYS = frozenset({"scope", "loss_policy", "hostile"})


@dataclass(frozen=True)
class AbilitySchemaIssue:
    """One machine-readable validation failure."""

    ability_id: str
    code: str
    message: str


@dataclass(frozen=True)
class AbilityValidationReport:
    """Directory validation result and migration progress."""

    definitions: tuple[AbilityDefinition, ...]
    legacy_ability_ids: tuple[str, ...]
    issues: tuple[AbilitySchemaIssue, ...]

    @property
    def valid(self) -> bool:
        """Return whether the directory satisfies the selected migration gate."""
        return not self.issues


def load_legacy_allowlist(path: Path = LEGACY_ALLOWLIST_PATH) -> frozenset[str]:
    """Load the exact set of abilities temporarily allowed to omit taxonomy."""
    lines = path.read_text(encoding="utf-8").splitlines()
    entries = [line.strip() for line in lines if line.strip() and not line.startswith("#")]
    if len(entries) != len(set(entries)):
        raise ValueError("legacy taxonomy allowlist contains duplicate IDs")
    return frozenset(entries)


def _mapping(payload: object, *, field: str) -> Mapping[str, object]:
    if not isinstance(payload, Mapping):
        raise ValueError(f"{field} must be a mapping")
    return payload


def _strings(payload: object, *, field: str) -> tuple[str, ...]:
    if not isinstance(payload, Sequence) or isinstance(payload, (str, bytes)):
        raise ValueError(f"{field} must be a list of strings")
    if any(not isinstance(value, str) for value in payload):
        raise ValueError(f"{field} must contain only strings")
    values = tuple(payload)
    if any(not value for value in values):
        raise ValueError(f"{field} cannot contain an empty value")
    if len(values) != len(set(values)):
        raise ValueError(f"{field} cannot contain duplicates")
    return values


def parse_ability_definition(path: Path, payload: Mapping[str, object]) -> AbilityDefinition:
    """Parse one fully migrated YAML mapping into its typed definition."""
    ability_id = str(payload.get("id", ""))
    if ability_id != path.stem:
        raise ValueError(f"id must equal filename stem {path.stem!r}")
    name = str(payload.get("name", ""))
    aliases = _strings(payload.get("aliases", ()), field="aliases")
    if name not in aliases:
        raise ValueError("aliases must preserve the display name")

    taxonomy_data = _mapping(payload.get("taxonomy"), field="taxonomy")
    unknown_taxonomy = set(taxonomy_data) - _TAXONOMY_KEYS
    missing_taxonomy = _TAXONOMY_KEYS - set(taxonomy_data)
    if unknown_taxonomy or missing_taxonomy:
        raise ValueError(
            f"taxonomy keys differ: missing={sorted(missing_taxonomy)}, "
            f"unknown={sorted(unknown_taxonomy)}"
        )
    traits = frozenset(_strings(taxonomy_data["traits"], field="taxonomy.traits"))
    unknown_traits = sorted(trait for trait in traits if not is_registered_ability_trait(trait))
    if unknown_traits:
        raise ValueError(f"unregistered traits: {unknown_traits}")

    targeting_data = _mapping(payload.get("targeting"), field="targeting")
    unknown_targeting = set(targeting_data) - _TARGETING_KEYS
    missing_targeting = _TARGETING_KEYS - set(targeting_data)
    if unknown_targeting or missing_targeting:
        raise ValueError(
            f"targeting keys differ: missing={sorted(missing_targeting)}, "
            f"unknown={sorted(unknown_targeting)}"
        )
    if not isinstance(targeting_data["hostile"], bool):
        raise ValueError("targeting.hostile must be a boolean")

    effects_value = payload.get("effects", ())
    if not isinstance(effects_value, Sequence) or isinstance(effects_value, (str, bytes)):
        raise ValueError("effects must be a list")
    effects = tuple(_mapping(effect, field="effects entry") for effect in effects_value)
    taxonomy = AbilityTaxonomy(
        origin=AbilityOrigin(str(taxonomy_data["origin"])),
        method=AbilityMethod(str(taxonomy_data["method"])),
        primary_intent=PrimaryIntent(str(taxonomy_data["primary_intent"])),
        activation=AbilityActivation(str(taxonomy_data["activation"])),
        form=AbilityForm(str(taxonomy_data["form"])),
        traits=traits,
    )
    targeting = TargetingPolicy(
        scope=TargetScope(str(targeting_data["scope"])),
        loss_policy=TargetLossPolicy(str(targeting_data["loss_policy"])),
        hostile=bool(targeting_data["hostile"]),
    )
    return AbilityDefinition(
        ability_id=ability_id,
        name=name,
        description=str(payload.get("description", "")),
        taxonomy=taxonomy,
        targeting=targeting,
        aliases=aliases,
        effects=effects,
    )


def validate_ability_directory(
    directory: Path = ABILITY_DIRECTORY,
    *,
    allowlist_path: Path = LEGACY_ALLOWLIST_PATH,
    require_complete: bool = False,
) -> AbilityValidationReport:
    """Validate typed definitions and the exact shrinking migration allowlist."""
    allowed_legacy = load_legacy_allowlist(allowlist_path)
    definitions: list[AbilityDefinition] = []
    legacy_ids: list[str] = []
    issues: list[AbilitySchemaIssue] = []
    alias_owners: dict[str, list[AbilityDefinition]] = {}

    for path in sorted(directory.glob("*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            issues.append(AbilitySchemaIssue(path.stem, "invalid_yaml", "root must be a mapping"))
            continue
        present_canonical = _CANONICAL_KEYS.intersection(payload)
        if not present_canonical:
            legacy_ids.append(path.stem)
            continue
        if present_canonical != _CANONICAL_KEYS:
            missing = sorted(_CANONICAL_KEYS - present_canonical)
            issues.append(
                AbilitySchemaIssue(
                    path.stem,
                    "partial_metadata",
                    f"canonical metadata is incomplete; missing {missing}",
                )
            )
            continue
        try:
            definition = parse_ability_definition(path, payload)
        except (KeyError, TypeError, ValueError) as error:
            issues.append(AbilitySchemaIssue(path.stem, "invalid_metadata", str(error)))
            continue
        definitions.append(definition)
        for alias in definition.aliases:
            alias_owners.setdefault(alias, []).append(definition)

    actual_legacy = frozenset(legacy_ids)
    for unexpected in sorted(actual_legacy - allowed_legacy):
        issues.append(
            AbilitySchemaIssue(unexpected, "missing_metadata", "ability is not in legacy allowlist")
        )
    for stale in sorted(allowed_legacy - actual_legacy):
        issues.append(
            AbilitySchemaIssue(
                stale, "stale_allowlist", "migrated or missing ability remains allowed"
            )
        )
    canonical_ids = {definition.ability_id for definition in definitions}
    for alias, owners in sorted(alias_owners.items()):
        owner_ids = [owner.ability_id for owner in owners]
        if len(owners) > 1 and any(owner.name != alias for owner in owners):
            issues.append(
                AbilitySchemaIssue(
                    owners[-1].ability_id,
                    "duplicate_alias",
                    f"non-display alias {alias!r} is shared by {owner_ids}",
                )
            )
        if alias in canonical_ids and any(alias != owner.ability_id for owner in owners):
            issues.append(
                AbilitySchemaIssue(
                    owners[-1].ability_id,
                    "alias_conflicts_with_id",
                    f"alias {alias!r} conflicts with a canonical ability ID",
                )
            )
    if require_complete:
        for ability_id in sorted(actual_legacy):
            issues.append(
                AbilitySchemaIssue(
                    ability_id,
                    "incomplete_migration",
                    "complete taxonomy is required",
                )
            )
    return AbilityValidationReport(tuple(definitions), tuple(sorted(legacy_ids)), tuple(issues))
