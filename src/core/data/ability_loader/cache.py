"""Cached YAML ability-definition loading."""

from functools import lru_cache

import yaml


@lru_cache(maxsize=512)
def _load_yaml_definition(file_path: str, modified_ns: int) -> dict:
    """Parse one YAML definition, keyed by path and modification timestamp."""
    del modified_ns  # The timestamp is part of the cache key.
    with open(file_path, "r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Ability definition must be a mapping: {file_path}")
    return data


def clear_ability_definition_cache() -> None:
    """Clear parsed YAML data, primarily for live modding and development."""
    _load_yaml_definition.cache_clear()
