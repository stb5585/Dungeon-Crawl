"""Regression coverage for split ability modules and the public façade."""

import inspect

from src.core import abilities
from src.core.abilities import (
    base,
    enemy,
    mage,
    powerups,
    promotions,
    skills,
    spell_types,
    spells,
    utility,
)


ABILITY_MODULES = (
    base,
    skills,
    promotions,
    utility,
    powerups,
    mage,
    enemy,
    spell_types,
    spells,
)


def _module_ability_classes(module):
    return {
        name: value
        for name, value in vars(module).items()
        if inspect.isclass(value) and value.__module__ == module.__name__
    }


def _progression_abilities():
    for progression in (abilities.skill_dict, abilities.spell_dict):
        for levels in progression.values():
            for entry in levels.values():
                yield from abilities.ability_classes_for(entry)


def test_abilities_facade_preserves_all_split_class_exports():
    direct_exports = {
        name: implementation
        for module in ABILITY_MODULES
        for name, implementation in _module_ability_classes(module).items()
    }

    assert len(direct_exports) == 519
    for name, implementation in direct_exports.items():
        if name in {"ShieldRiposte", "SpellReflection"}:
            # The defender passives intentionally supersede older promotion
            # actives with the same public names.
            continue
        assert getattr(abilities, name) is implementation


def test_progression_catalogs_reference_split_implementations():
    progression_abilities = list(_progression_abilities())

    assert progression_abilities
    for ability_class in progression_abilities:
        assert getattr(abilities, ability_class.__name__) is ability_class
        assert ability_class.__module__.startswith("src.core.abilities.")


def test_legacy_alias_and_yaml_directory_remain_available():
    assert abilities.SongInspiration is abilities.MelodyInspiration
    assert abilities._YAML_DIR.is_dir()
