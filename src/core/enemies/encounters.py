"""Enemy encounter catalogs, random selection, and debug overrides."""

from __future__ import annotations

from collections.abc import Callable, Iterable
import os
import random
from typing import NamedTuple

from . import base, early, endgame, midgame
from .base import Enemy
from .catalog import FUNHOUSE_ENEMY_SPECS, resolve_enemy_specs, resolve_random_enemy_catalog


AbilityFactory = Callable[[], object]
EnemyFactory = Callable[[], Enemy]
RandomEnemyOverride = str | type[Enemy] | EnemyFactory
_random_enemy_override: RandomEnemyOverride | None = None
_RANDOM_ENEMY_OVERRIDE_ENV = "DUNGEON_FORCE_ENEMY"

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
) -> Enemy:
    """Return a random enemy appropriate for the current dungeon level."""
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
