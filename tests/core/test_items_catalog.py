#!/usr/bin/env python3
"""Broad catalog coverage for item definitions and helper utilities."""

import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from src.core import items


_BASE_ITEM_CLASSES = {
    items.Item,
    items.Weapon,
    items.Armor,
    items.Helmet,
    items.OffHand,
    items.Accessory,
    items.Potion,
    items.Misc,
}


def _no_arg_item_classes():
    discovered = []
    for name in dir(items):
        obj = getattr(items, name)
        if not inspect.isclass(obj):
            continue
        if not issubclass(obj, items.Item) or obj in _BASE_ITEM_CLASSES:
            continue
        signature = inspect.signature(obj)
        required = [
            param
            for param in signature.parameters.values()
            if param.default is param.empty
            and param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD)
        ]
        if not required:
            discovered.append(obj)
    return sorted(discovered, key=lambda cls: cls.__name__)


def test_no_arg_item_catalog_instantiates_and_renders_cleanly():
    discovered = _no_arg_item_classes()

    assert len(discovered) >= 300

    seen_types = set()
    saw_summon_misc = False
    for item_cls in discovered:
        item = item_cls()
        seen_types.add(item.typ)
        assert item.name
        assert isinstance(item.description, str)
        assert item.subtyp is not None

        rendered = str(item)
        assert item.name in rendered

        if isinstance(item, items.Weapon):
            assert "Damage:" in rendered
            assert "Critical Chance:" in rendered
            if item.subtyp == "Fist":
                assert item.disarm is False
        elif isinstance(item, items.Armor):
            assert "Armor:" in rendered
        elif isinstance(item, items.OffHand):
            if item.subtyp == "Shield":
                assert "Block:" in rendered
            else:
                assert "Spell Damage Mod:" in rendered
        elif isinstance(item, items.Accessory):
            assert "Mod:" in rendered
        elif isinstance(item, items.Potion):
            assert "Weight:" in rendered
            assert item.weight == 0.1
        else:
            assert "Sub-type:" in rendered
            if "Summon" in item.subtyp:
                assert "Sub-type: Special" in rendered
                saw_summon_misc = True

    assert {"Weapon", "Armor", "Helmet", "OffHand", "Accessory", "Potion", "Misc"} <= seen_types
    assert saw_summon_misc is True


def test_helmet_catalog_matches_equipment_table():
    helmet_names = {
        subtyp: [helmet_cls().name for helmet_cls in helmet_classes]
        for subtyp, helmet_classes in items.items_dict["Helmet"].items()
    }

    assert helmet_names["Cloth"] == [
        "Cloth Cap",
        "Jaapi",
        "Turban",
        "Witch Hat",
        "Enchanted Hood",
        "Mitre Hat",
        "Circlet",
        "Cohuleen Druith",
        "Ariadne's Diadem",
    ]
    assert helmet_names["Light"] == [
        "Leather Cap",
        "Pith Helmet",
        "War Mask",
        "Arming Cap",
        "Katapu",
        "Sōmen",
        "Demon Cowl",
    ]
    assert helmet_names["Medium"] == [
        "Scale Helm",
        "Chain Coif",
        "Kulah Khud",
        "Cervelliere",
        "Visored Sallet",
        "Tolga",
        "Tarnhelm",
    ]
    assert helmet_names["Heavy"] == [
        "Iron Helm",
        "Kettle Helm",
        "Barbute",
        "Great Helm",
        "Full Plate Helm",
        "Close Helm",
        "Kabuto",
    ]

    mitre = items.MitreHat()
    circlet = items.Circlet()
    assert mitre.restriction == ['Priest', 'Archbishop', 'Diviner', 'Geomancer']
    assert circlet.restricted_against == ['Priest', 'Archbishop', 'Diviner', 'Geomancer']
    assert items.CohuleenDruith().resist_mod == 0.5
    assert items.DemonCowl().element == "Death"


def test_item_metadata_lines_include_elements_and_resistance_mods():
    assert "Element: Electric" in items.item_metadata_lines(items.IndrasFist())
    assert "Resistance: Fire +25%" in items.item_metadata_lines(items.Svalinn())
    assert "Resistance: Fire +50%" in items.item_metadata_lines(items.FireChain())
    assert "Immunity: Electric" in items.item_metadata_lines(items.ElectricAmulet())


def test_resistance_item_descriptions_leave_numeric_effects_to_metadata_lines():
    resistance_items = [
        items.CohuleenDruith(),
        items.DemonCowl(),
        items.Svalinn(),
        items.FireChain(),
        items.IceChain(),
        items.ElectricChain(),
        items.WaterChain(),
        items.EarthChain(),
        items.WindChain(),
        items.ElementalChain(),
        items.FireAmulet(),
        items.IceAmulet(),
        items.ElectricAmulet(),
        items.WaterAmulet(),
        items.EarthAmulet(),
        items.WindAmulet(),
        items.ElementalAmulet(),
    ]

    for item in resistance_items:
        description = item.description.lower()
        assert "resistance" not in description
        assert "immunity" not in description
        assert "immune" not in description
        assert " by 50%" not in description
        assert " by 100%" not in description
        assert " by 25%" not in description


def test_base_item_classes_and_helper_utilities(monkeypatch):
    base_item = items.Item("Summon Sigil", "A helper token.", 5, 0.25, "Summon - Test")
    assert base_item.use(None) == ""
    assert base_item.special_effect(None) is None
    assert "Sub-type: Special" in str(base_item)

    fist_weapon = items.Weapon("Fist Wrap", "Simple wraps.", 10, 0.5, 2, 0.1, 1, "Fist", False, True)
    sword_weapon = items.Weapon("Training Sword", "A blunt sword.", 10, 0.5, 3, 0.2, 1, "Sword", False, True)
    armor = items.Armor("Padded Coat", "Simple protection.", 10, 0.5, 2, "Cloth", False)
    helmet = items.Helmet("Padded Cap", "Simple head protection.", 10, 0.5, 1, "Cloth", False)
    shield = items.OffHand("Practice Shield", "A round shield.", 10, 0.5, 0.25, "Shield", False)
    tome = items.OffHand("Study Tome", "A magical primer.", 10, 0.5, 3, "Book", False)
    accessory = items.Accessory("Charm Ring", "A simple charm.", 10, 0.5, "+1 Luck", "Ring", False)
    potion = items.Potion("Test Potion", "A minor tonic.", 10, 0.5, "Potion")
    misc = items.Misc("Quest Scrap", "A tiny scrap.", 0, 1.0, "Quest")
    sheet_music = items.SheetMusic("Song Sheet", "Sheet music.", 0, 0.5, "Special")
    blank_scroll = items.BlankScroll("Blank Scroll", "A writable scroll.", 0, 0.5, "Special")

    assert fist_weapon.disarm is False
    assert sword_weapon.disarm is True
    assert fist_weapon.special_effect(None) is None
    assert armor.special_effect(None) is None
    assert helmet.typ == "Helmet"
    assert "Damage:" in str(fist_weapon)
    assert "Armor:" in str(armor)
    assert "Armor:" in str(helmet)
    assert "Block:" in str(shield)
    assert "Spell Damage Mod:" in str(tome)
    assert "Mod:" in str(accessory)
    assert "Weight:" in str(potion)
    assert "Sub-type: Quest" in str(misc)
    assert sheet_music.typ == "Misc"
    assert blank_scroll.typ == "Misc"

    monkeypatch.setattr(items, "_rarity_table_cache", None)
    monkeypatch.setattr("src.core.items.random.choice", lambda seq: seq[0])
    rarity_table = items._build_rarity_table()
    assert items._build_rarity_table() is rarity_table
    assert all(str(index) in rarity_table for index in range(1, 9))

    low_bucket_pick = items.random_item(0)
    high_bucket_pick = items.random_item(99)
    assert low_bucket_pick is rarity_table["1"][0]
    assert high_bucket_pick is rarity_table["8"][0]

    assert items.stat_theme_for_item(items.PowerRing()) == "strength"
    assert items.stat_theme_for_item(items.RubyLocket()) == "wisdom"
    assert items.stat_theme_for_item(items.Rapier()) == "strength"
    assert items.stat_theme_for_item(items.FireChain()) == "resistance"
    assert items.stat_theme_for_item(items.IronHelm()) == "constitution"
    assert items.stat_themed_item_name(items.PowerRing()) == "Mighty Power Ring"
    assert items.stat_themed_item_name(items.Item("Pebble", "A pebble.", 0, 1.0, "Misc")) == "Pebble"

    assert isinstance(items.remove_equipment("Weapon"), items.NoWeapon)
    assert isinstance(items.remove_equipment("OffHand"), items.NoOffHand)
    assert isinstance(items.remove_equipment("Armor"), items.NoArmor)
    assert isinstance(items.remove_equipment("Helmet"), items.NoHelmet)
    assert isinstance(items.remove_equipment("Ring"), items.NoRing)
    assert isinstance(items.remove_equipment("Pendant"), items.NoPendant)
