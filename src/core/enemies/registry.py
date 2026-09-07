"""Resolved enemy implementation registry.

The static catalog stores stable display and class names. This module resolves
those names after implementation modules load, keeping construction and
Bestiary queries independent from the package compatibility facade.
"""

from __future__ import annotations

import src.core.enemies.base as base
import src.core.enemies.early as early
import src.core.enemies.endgame as endgame
import src.core.enemies.midgame as midgame

from .base import Enemy
from .catalog import (
    FUNHOUSE_ENEMY_SPECS,
    resolve_enemy_specs,
    resolve_random_enemy_catalog,
)

ENEMY_NAMESPACE = {
    name: value
    for module in (base, early, midgame, endgame)
    for name, value in vars(module).items()
    if isinstance(value, type) and issubclass(value, Enemy)
}

RANDOM_ENEMY_CATALOG = resolve_random_enemy_catalog(ENEMY_NAMESPACE)
FUNHOUSE_ENEMY_CATALOG = resolve_enemy_specs(FUNHOUSE_ENEMY_SPECS, ENEMY_NAMESPACE)
