"""Central registry for validated secondary ability traits."""

from __future__ import annotations

_REGISTERED_TRAITS: set[str] = set()


def register_ability_trait(trait: str) -> None:
    """Register one namespaced trait for ability-schema validation."""
    if "." not in trait or trait.startswith(".") or trait.endswith("."):
        raise ValueError(f"ability trait must be namespaced: {trait!r}")
    _REGISTERED_TRAITS.add(trait)


def registered_ability_traits() -> frozenset[str]:
    """Return an immutable view of every registered trait."""
    return frozenset(_REGISTERED_TRAITS)


def is_registered_ability_trait(trait: str) -> bool:
    """Return whether a trait is present in the central registry."""
    return trait in _REGISTERED_TRAITS
