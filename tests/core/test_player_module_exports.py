"""Regression coverage for the composed Player class and public façade."""

import inspect

from src.core import player
from src.core.player import (
    combat,
    exploration,
    inventory,
    presentation,
    progression,
    state,
)


PLAYER_BEHAVIOR_MODULES = (
    state,
    exploration,
    presentation,
    inventory,
    progression,
    combat,
)


def _defined_methods(class_type):
    return {
        name: getattr(class_type, name)
        for name, value in vars(class_type).items()
        if inspect.isfunction(value) or isinstance(value, staticmethod)
    }


def test_player_composes_every_split_behavior_method():
    mixin_methods = {
        name: implementation
        for module in PLAYER_BEHAVIOR_MODULES
        for class_type in vars(module).values()
        if inspect.isclass(class_type) and class_type.__module__ == module.__name__
        for name, implementation in _defined_methods(class_type).items()
    }
    player_methods = _defined_methods(player.Player)

    assert len(mixin_methods) == 106
    assert set(player_methods) == {"__init__", "__str__"}
    for name, implementation in mixin_methods.items():
        assert getattr(player.Player, name) is implementation


def test_player_facade_preserves_support_helpers():
    assert player.normalize_gameplay_stats is player.stats.normalize_gameplay_stats
    assert player.summarize_gameplay_stats is player.stats.summarize_gameplay_stats
    assert player.load_char is player.persistence.load_char
    assert player._load_tiled_map is player.maps._load_tiled_map


def test_action_catalog_references_composed_player_methods():
    assert player.actions_dict
    for action in player.actions_dict.values():
        method = action["method"]
        assert getattr(player.Player, method.__name__) is method
