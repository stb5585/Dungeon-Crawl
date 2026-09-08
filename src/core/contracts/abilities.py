"""Ability identity, taxonomy, and declarative-definition contracts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from re import fullmatch
from typing import Mapping

from .targeting import TargetingPolicy


class AbilityOrigin(str, Enum):
    """Source from which an ability derives its power."""

    MARTIAL = "martial"
    ARCANE = "arcane"
    DIVINE = "divine"
    NATURAL = "natural"
    SPIRITUAL = "spiritual"
    EXTRAPLANAR = "extraplanar"
    INNATE = "innate"
    ALCHEMICAL = "alchemical"


class AbilityMethod(str, Enum):
    """Primary means by which an ability produces its outcome."""

    STRIKE = "strike"
    PROJECTION = "projection"
    MANIFESTATION = "manifestation"
    BINDING = "binding"
    TRANSFORMATION = "transformation"
    CHANNELING = "channeling"
    MOVEMENT = "movement"
    COMMAND = "command"
    CONSUMPTION = "consumption"


class PrimaryIntent(str, Enum):
    """Primary player-facing purpose of an ability."""

    DAMAGE = "damage"
    PROTECTION = "protection"
    RESTORATION = "restoration"
    CONTROL = "control"
    MOBILITY = "mobility"
    INFORMATION = "information"
    SUMMONING = "summoning"
    UTILITY = "utility"


class AbilityActivation(str, Enum):
    """How an ability enters resolution."""

    ACTIVE = "active"
    PASSIVE = "passive"
    REACTION = "reaction"


class AbilityForm(str, Enum):
    """Resolution shape of an ability."""

    DIRECT = "direct"
    FIELD = "field"
    SUMMON = "summon"
    ITEM_ACTION = "item_action"


@dataclass(frozen=True)
class AbilityTaxonomy:
    """Closed primary axes plus registered secondary traits."""

    origin: AbilityOrigin
    method: AbilityMethod
    primary_intent: PrimaryIntent
    activation: AbilityActivation
    form: AbilityForm
    traits: frozenset[str] = frozenset()


@dataclass(frozen=True)
class AbilityDefinition:
    """Stable ability identity and validated declarative metadata."""

    ability_id: str
    name: str
    description: str
    taxonomy: AbilityTaxonomy
    targeting: TargetingPolicy
    aliases: tuple[str, ...] = ()
    effects: tuple[Mapping[str, object], ...] = ()

    def __post_init__(self) -> None:
        if fullmatch(r"[a-z0-9]+(?:_[a-z0-9]+)*", self.ability_id) is None:
            raise ValueError("ability_id must be a lowercase underscore-separated slug")
        if not self.name:
            raise ValueError("ability name must not be empty")
        if self.ability_id in self.aliases:
            raise ValueError("canonical ability_id must not also be an alias")

    @property
    def player_facing_traits(self) -> tuple[str, ...]:
        """Return sorted traits that are safe to include in descriptions."""
        return tuple(
            sorted(trait for trait in self.taxonomy.traits if not trait.startswith("internal."))
        )
