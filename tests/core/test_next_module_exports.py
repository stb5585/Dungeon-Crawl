"""Compatibility coverage for the second core refactor wave."""

import inspect

from src.core import save_system
from src.core.classes import ability_mechanics
from src.core.combat import battle_engine
from src.core.data import ability_loader


SAVE_MODULES = (
    save_system.models,
    save_system.item_serialization,
    save_system.summons,
    save_system.tiles,
    save_system.enemy,
    save_system.quests,
    save_system.player,
    save_system.manager,
)
EFFECT_FACTORY_MODULES = (
    ability_loader.effect_base,
    ability_loader.effect_dynamic,
    ability_loader.effect_enemy,
    ability_loader.effect_special,
)
ABILITY_MECHANIC_MODULES = (
    ability_mechanics.equipment,
    ability_mechanics.passives,
    ability_mechanics.companions,
    ability_mechanics.exploration,
    ability_mechanics.rewind,
    ability_mechanics.summons,
)
BATTLE_BEHAVIOR_MODULES = (
    battle_engine.turns,
    battle_engine.actions,
    battle_engine.outcomes,
)


def _owned_classes(module):
    return {
        name: value
        for name, value in vars(module).items()
        if inspect.isclass(value) and value.__module__ == module.__name__
    }


def _owned_functions(module):
    return {
        name: value
        for name, value in vars(module).items()
        if inspect.isfunction(value) and value.__module__ == module.__name__
    }


def _defined_methods(class_type):
    methods = {}
    for name, value in vars(class_type).items():
        if isinstance(value, staticmethod):
            methods[name] = value.__func__
        elif inspect.isfunction(value):
            methods[name] = value
    return methods


def test_save_system_facade_preserves_all_serializer_classes():
    exports = {
        name: implementation
        for module in SAVE_MODULES
        for name, implementation in _owned_classes(module).items()
    }

    assert len(exports) == 15
    for name, implementation in exports.items():
        assert getattr(save_system, name) is implementation


def test_effect_factory_composes_every_constructor_group():
    methods = {
        name: implementation
        for module in EFFECT_FACTORY_MODULES
        for mixin in _owned_classes(module).values()
        for name, implementation in _defined_methods(mixin).items()
    }

    assert len(methods) == 95
    for name, implementation in methods.items():
        assert getattr(ability_loader.EffectFactory, name) is implementation


def test_ability_mechanics_facade_preserves_all_split_functions():
    exports = {
        name: implementation
        for module in ABILITY_MECHANIC_MODULES
        for name, implementation in _owned_functions(module).items()
    }

    assert len(exports) == 105
    for name, implementation in exports.items():
        assert getattr(ability_mechanics, name) is implementation


def test_battle_engine_composes_every_split_behavior_method():
    methods = {
        name: implementation
        for module in BATTLE_BEHAVIOR_MODULES
        for mixin in _owned_classes(module).values()
        for name, implementation in _defined_methods(mixin).items()
    }

    assert len(methods) == 62
    assert len(_defined_methods(battle_engine.BattleEngine)) == 22
    for name, implementation in methods.items():
        assert getattr(battle_engine.BattleEngine, name) is implementation
