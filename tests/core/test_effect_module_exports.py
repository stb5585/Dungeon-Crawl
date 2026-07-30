"""Regression coverage for the split effect modules and compatibility façade."""

from src.core import effects
from src.core.effects import common, composite, enemy, skills, special, summon


EFFECT_MODULES = (common, enemy, skills, special, summon)


def test_composite_facade_preserves_all_split_effect_exports():
    direct_exports = {
        name: getattr(module, name)
        for module in EFFECT_MODULES
        for name in vars(module)
        if name.endswith("Effect") and name != "Effect"
    }

    assert set(composite.__all__) == {"Effect", *direct_exports}
    for name, implementation in direct_exports.items():
        assert getattr(composite, name) is implementation


def test_package_exports_resolve_to_the_split_implementations():
    for module in EFFECT_MODULES:
        for name, implementation in vars(module).items():
            if name.endswith("Effect") and name != "Effect":
                assert getattr(effects, name) is implementation
