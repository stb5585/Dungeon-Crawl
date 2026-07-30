"""Helpers behavior for the dungeon manager package."""

from src.core import map_tiles


def relic_discovery_text(relic) -> str:
    return map_tiles.relic_discovery_text(relic)
