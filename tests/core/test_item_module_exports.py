"""Regression coverage for split item modules and the public items façade."""

import inspect

from src.core import items
from src.core.items import accessories, armor, consumables, misc, offhands, weapons


ITEM_MODULES = (
    weapons,
    armor,
    offhands,
    accessories,
    consumables,
    misc,
)


def _module_item_classes(module):
    return {
        name: value
        for name, value in vars(module).items()
        if inspect.isclass(value)
        and issubclass(value, items.Item)
        and value is not items.Item
        and value.__module__ == module.__name__
    }


def _catalog_classes():
    for category, entries in items.items_dict.items():
        if category == "Weapon":
            for handed in entries.values():
                for classes in handed.values():
                    yield from classes
        else:
            for classes in entries.values():
                yield from classes


def test_items_facade_preserves_all_split_class_exports():
    direct_exports = {
        name: implementation
        for module in ITEM_MODULES
        for name, implementation in _module_item_classes(module).items()
    }

    assert len(direct_exports) == 385
    for name, implementation in direct_exports.items():
        assert getattr(items, name) is implementation


def test_shop_catalog_references_the_split_implementations():
    catalog_classes = list(_catalog_classes())

    assert catalog_classes
    for item_class in catalog_classes:
        assert getattr(items, item_class.__name__) is item_class
        assert item_class.__module__.startswith("src.core.items.")


def test_misc_item_helpers_remain_available_from_items_facade():
    for name in (
        "has_lockpick_kit",
        "has_smoke_bomb",
        "has_oculus",
        "can_detect_fake_walls",
        "lockpick_break_chance",
        "use_lockpick_kit",
        "consume_smoke_bomb",
    ):
        assert getattr(items, name) is getattr(misc, name)
