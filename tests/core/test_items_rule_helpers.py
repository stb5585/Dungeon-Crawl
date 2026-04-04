#!/usr/bin/env python3
"""Additional coverage for rule-heavy item helpers and metadata."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

from src.core import items
from src.core.constants import DWARF_HANGOVER_MAX_STEPS
from tests.test_framework import TestGameState


def _player_with_ring(class_name):
    player = TestGameState.create_player(class_name=class_name, race_name="Human")
    ring = items.ClassRing()
    player.equipment["Ring"] = ring
    return player, ring


@pytest.mark.parametrize(
    ("class_name", "expected_mod", "description_fragment"),
    [
        ("Crusader", "+10% Holy Damage", "Holy damage"),
        ("Dragoon", "+1 Jump Mod", "Jump modification slot"),
        ("Stalwart Defender", "Damage Reduction", "reduces damage taken"),
        ("Wizard", "Spell Effect", "spell special effects"),
        ("Shadowcaster", "Shadow Bolt Heal", "Shadow Bolt"),
        ("Knight Enchanter", "Mana Tap+", "Mana Tap"),
        ("Grand Summoner", "+30% Summons", "summoned creatures"),
        ("Seeker", "Rare Find", "find rare items"),
        ("Ninja", "First Strike", "double damage"),
        ("Arcane Trickster", "Spell Steal Buff", "spell is stolen"),
        ("Templar", "Random Blessing", "random blessings"),
        ("Master Monk", "Martial Master", "unarmed"),
        ("Archbishop", "Divine Intervention", "heal 25%"),
        ("Troubadour", "Amplified Song", "songs"),
        ("Lycan", "Transform Boost", "after transforming"),
        ("Geomancer", "Terrain Master", "terrain effect"),
        ("Soulcatcher", "Soul Aspect Unlock", "Soul Aspect"),
        ("Beast Master", "Pack Bond", "companion"),
    ],
)
def test_class_ring_covers_remaining_description_and_modifier_branches(
    class_name,
    expected_mod,
    description_fragment,
):
    player, ring = _player_with_ring(class_name)
    player.spellbook.pop("Totem", None)

    ring.class_mod(player)

    assert player.equipment["Ring"].mod == expected_mod
    assert description_fragment in ring.get_description(player)


@pytest.mark.parametrize(
    ("factory", "resource", "maximum", "current", "expected_after", "expected_text"),
    [
        (items.HealthPotion, "health", 100, 40, 67, "healed you for 27 life"),
        (items.ManaPotion, "mana", 80, 10, 32, "restored 22 mana points"),
        (items.Elixir, "both", (100, 60), (20, 0), (75, 33), "restored 55 health points and 33 mana points"),
    ],
)
def test_dwarf_out_of_combat_consumables_clamp_hangover_steps(
    factory,
    resource,
    maximum,
    current,
    expected_after,
    expected_text,
    monkeypatch,
):
    kwargs = {"class_name": "Warrior", "race_name": "Dwarf"}
    if resource == "health":
        kwargs["health"] = (maximum, current)
    elif resource == "mana":
        kwargs["mana"] = (maximum, current)
    else:
        kwargs["health"] = (maximum[0], current[0])
        kwargs["mana"] = (maximum[1], current[1])
    player = TestGameState.create_player(**kwargs)
    player.state = "normal"
    player.dwarf_hangover_steps = DWARF_HANGOVER_MAX_STEPS - 1
    player.modify_inventory = lambda *_args, **_kwargs: None
    monkeypatch.setattr("src.core.items.random.uniform", lambda _a, _b: 1.0)

    result = factory().use(player)

    assert player.dwarf_hangover_steps == DWARF_HANGOVER_MAX_STEPS
    if resource == "health":
        assert player.health.current == expected_after
    elif resource == "mana":
        assert player.mana.current == expected_after
    else:
        assert (player.health.current, player.mana.current) == expected_after
    assert expected_text in result


def test_status_items_cover_out_of_combat_dwarf_steps_and_early_returns(monkeypatch):
    dwarf = TestGameState.create_player(class_name="Warrior", race_name="Dwarf", health=(100, 70))
    dwarf.state = "normal"
    dwarf.dwarf_hangover_steps = DWARF_HANGOVER_MAX_STEPS - 1
    dwarf.status_effects["Blind"].active = True
    dwarf.status_effects["Blind"].duration = 2
    dwarf.status_effects["Blind"].extra = 4
    dwarf.modify_inventory = lambda *_args, **_kwargs: None
    monkeypatch.setattr("src.core.items.random.randint", lambda low, high: high)

    eye_drop_result = items.EyeDrop().use(dwarf)

    assert dwarf.status_effects["Blind"].active is False
    assert dwarf.status_effects["Blind"].duration == 0
    assert dwarf.status_effects["Blind"].extra == 0
    assert dwarf.health.current == 80
    assert dwarf.dwarf_hangover_steps == DWARF_HANGOVER_MAX_STEPS
    assert "cured of blind" in eye_drop_result
    assert "healed for 10 health" in eye_drop_result

    human = TestGameState.create_player(class_name="Warrior", race_name="Human")
    assert items.Bandage().use(human) == "You are not affected by bleed.\n"
    assert items.Remedy().use(human) == "You are not affected by any negative status effects.\n"


def test_scroll_use_keeps_scroll_until_last_charge():
    player = TestGameState.create_player(class_name="Warrior", race_name="Human")
    calls = []
    player.modify_inventory = lambda item, subtract=False, **_kwargs: calls.append((item.name, subtract))

    scroll = items.FireScroll()
    scroll.spell = SimpleNamespace(cast=lambda user, target=None, special=True: "Flames erupt!\n")
    scroll.charges = 2

    result = scroll.use(player)

    assert "uses Fire Scroll" in result
    assert "Flames erupt!" in result
    assert "crumbles to dust" not in result
    assert scroll.charges == 1
    assert calls == []


@pytest.mark.parametrize(
    ("factory", "name", "subtyp", "mod"),
    [
        (items.Key, "Key", "Key", None),
        (items.OldKey, "Old Key", "Key", None),
        (items.MasterKey, "Master Key", "Key", None),
        (items.CrypticKey, "Cryptic Key", "Key", None),
        (items.JesterToken, "Jester Token", "Quest", None),
        (items.RibbonPendant, "Ribbon Pendant", "Pendant", "Status-All"),
        (items.MagicPendant, "Magic Pendant", "Pendant", "Magic Dodge"),
    ],
)
def test_misc_item_metadata_smoke(factory, name, subtyp, mod):
    item = factory()

    assert item.name == name
    assert item.subtyp == subtyp
    if mod is not None:
        assert item.mod == mod
