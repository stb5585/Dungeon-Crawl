"""Enemy encounter catalogs, random selection, and debug overrides."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
import os
import random
from typing import NamedTuple

from . import base, early, endgame, midgame
from .base import Enemy
from ..combat.encounter import CombatEncounter
from .catalog import (
    CURATED_PAIR_SPECS,
    FUNHOUSE_ENEMY_SPECS,
    resolve_enemy_specs,
    resolve_random_enemy_catalog,
)


AbilityFactory = Callable[[], object]
EnemyFactory = Callable[[], Enemy]
RandomEnemyOverride = str | type[Enemy] | EnemyFactory
_random_enemy_override: RandomEnemyOverride | None = None
_RANDOM_ENEMY_OVERRIDE_ENV = "DUNGEON_FORCE_ENEMY"
_CURATED_ENCOUNTER_OVERRIDE_ENV = "DUNGEON_FORCE_ENCOUNTER"

_ENEMY_NAMESPACE = {
    name: value
    for module in (base, early, midgame, endgame)
    for name, value in vars(module).items()
    if isinstance(value, type) and issubclass(value, Enemy)
}


class EnemyCandidate(NamedTuple):
    """Lightweight encounter choice preserving the historical ``.name`` API."""

    name: str
    factory: EnemyFactory


@dataclass(frozen=True)
class CuratedEncounterSpec:
    """Immutable development-pilot encounter definition."""

    key: str
    display_name: str
    floor: int
    member_factories: tuple[EnemyFactory, EnemyFactory]

    def build(self) -> CombatEncounter:
        """Build a fresh runtime encounter in authored member order."""
        return CombatEncounter.from_enemies(
            [factory() for factory in self.member_factories]
        )


def set_random_enemy_override(enemy: RandomEnemyOverride | None) -> None:
    """Force random encounters to use a specific enemy for debug playtesting.

    Accepts an enemy class, a zero-argument factory, an enemy class name, or
    ``None`` to clear the override.
    """
    global _random_enemy_override
    _random_enemy_override = enemy


def clear_random_enemy_override() -> None:
    """Return random encounters to normal catalog selection."""
    set_random_enemy_override(None)


def curated_encounter_specs() -> tuple[CuratedEncounterSpec, ...]:
    """Return the development-only pair catalog in authored order."""
    specs = []
    for key, (display_name, floor, class_names) in CURATED_PAIR_SPECS.items():
        factories = tuple(_ENEMY_NAMESPACE[name] for name in class_names)
        specs.append(
            CuratedEncounterSpec(
                key=key,
                display_name=display_name,
                floor=floor,
                member_factories=factories,
            )
        )
    return tuple(specs)


def curated_encounter_spec(key: str) -> CuratedEncounterSpec:
    """Return one curated encounter definition by stable key."""
    for spec in curated_encounter_specs():
        if spec.key == key:
            return spec
    raise ValueError(f"Unknown curated encounter override: {key}")


def build_curated_encounter(key: str) -> CombatEncounter:
    """Build a fresh curated development encounter."""
    return curated_encounter_spec(key).build()


def _forced_curated_encounter(
    level: str,
    *,
    enabled: bool,
) -> CombatEncounter | None:
    """Build an environment-forced pair for an authorized random encounter."""
    key = os.getenv(_CURATED_ENCOUNTER_OVERRIDE_ENV, "").strip()
    forced_enemy = (
        _random_enemy_override is not None
        or bool(os.getenv(_RANDOM_ENEMY_OVERRIDE_ENV, "").strip())
    )
    if key and forced_enemy:
        raise ValueError(
            "DUNGEON_FORCE_ENEMY and DUNGEON_FORCE_ENCOUNTER "
            "cannot be used together."
        )
    if not key or not enabled:
        return None
    spec = curated_encounter_spec(key)
    if int(level) != spec.floor:
        raise ValueError(
            f"Curated encounter {key!r} belongs to floor {spec.floor}, "
            f"not floor {level}."
        )
    return spec.build()


def _build_random_enemy_override() -> Enemy | None:
    override = _random_enemy_override
    if override is None:
        env_override = os.getenv(_RANDOM_ENEMY_OVERRIDE_ENV, "").strip()
        override = env_override or None
    if override is None:
        return None
    if isinstance(override, str):
        enemy_cls = _ENEMY_NAMESPACE.get(override)
        if not isinstance(enemy_cls, type) or not issubclass(enemy_cls, Enemy):
            raise ValueError(f"Unknown random enemy override: {override}")
        return enemy_cls()
    if isinstance(override, type):
        if not issubclass(override, Enemy):
            raise TypeError("Random enemy override class must inherit Enemy.")
        return override()
    enemy = override()
    if not isinstance(enemy, Enemy):
        raise TypeError("Random enemy override factory must return an Enemy.")
    return enemy


def random_enemy_catalog() -> dict[str, list[Enemy]]:
    """Return freshly instantiated random-encounter enemies keyed by floor.

    This compatibility view intentionally creates every entry. Runtime selection
    should use :func:`random_enemy`, which instantiates only the chosen enemy.
    """
    return {
        level: [factory() for _name, factory in entries]
        for level, entries in _RANDOM_ENEMY_CATALOG.items()
    }


def random_enemy_candidates(level: str) -> tuple[tuple[str, EnemyFactory], ...]:
    """Return immutable ``(display_name, factory)`` entries for one floor."""
    if level not in _RANDOM_ENEMY_CATALOG:
        level = max(_RANDOM_ENEMY_CATALOG, key=int)
    return _RANDOM_ENEMY_CATALOG[level]


def random_enemy(
    level: str,
    preferred_names: Iterable[str] | None = None,
    preferred_chance: float = 0.0,
    rng=random,
    *,
    allow_curated_encounter: bool = False,
) -> Enemy:
    """Return an enemy appropriate for one random-selection consumer.

    Curated pair overrides are disabled by default so utility consumers such
    as bounty generation cannot accidentally receive runtime encounters.
    Ordinary dungeon entry points must opt in explicitly.
    """
    if forced_encounter := _forced_curated_encounter(
        level,
        enabled=allow_curated_encounter,
    ):
        primary = forced_encounter.primary_enemy
        primary._runtime_combat_encounter = forced_encounter
        primary._curated_encounter_key = os.getenv(
            _CURATED_ENCOUNTER_OVERRIDE_ENV,
            "",
        ).strip()
        return primary
    if forced_enemy := _build_random_enemy_override():
        return forced_enemy

    candidates = tuple(EnemyCandidate(*entry) for entry in random_enemy_candidates(level))
    preferred = {str(name) for name in (preferred_names or []) if str(name)}
    preferred_candidates = [entry for entry in candidates if entry.name in preferred]
    if preferred_candidates and rng.random() < max(0.0, min(1.0, preferred_chance)):
        candidates = tuple(preferred_candidates)

    selected = rng.choice(candidates)
    return selected.factory()


def funhouse_enemy_catalog() -> list[Enemy]:
    """Return the Funhouse challenge enemy catalog."""
    return [factory() for _name, factory in _FUNHOUSE_ENEMY_CATALOG]


def funhouse_enemy() -> Enemy:
    """Return a random Funhouse challenge enemy."""
    _name, enemy_factory = random.choice(_FUNHOUSE_ENEMY_CATALOG)
    return enemy_factory()


_RANDOM_ENEMY_CATALOG: dict[str, tuple[tuple[str, EnemyFactory], ...]] = (
    resolve_random_enemy_catalog(_ENEMY_NAMESPACE)
)
_FUNHOUSE_ENEMY_CATALOG: tuple[tuple[str, EnemyFactory], ...] = resolve_enemy_specs(
    FUNHOUSE_ENEMY_SPECS,
    _ENEMY_NAMESPACE,
)
