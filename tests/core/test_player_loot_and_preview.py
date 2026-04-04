#!/usr/bin/env python3
"""Focused coverage for player loot logic and equipment preview helpers."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

from src.core import items, player as player_module
from tests.test_framework import TestGameState


def _fake_item(
    name,
    *,
    typ="Weapon",
    subtyp="Sword",
    handed=1,
    crit=0.1,
    mod="No Mod",
    restriction=None,
):
    return SimpleNamespace(
        name=name,
        typ=typ,
        subtyp=subtyp,
        handed=handed,
        crit=crit,
        mod=mod,
        restriction=[] if restriction is None else restriction,
        damage=0,
        armor=0,
        weight=0,
    )


def _preview_player():
    player = TestGameState.create_player(class_name="Warrior", race_name="Human")
    player.cls.equip_check = lambda item, equip_slot: item.name != "Forbidden Blade"
    player.cls.restrictions["OffHand"] = ["Sword", "Shield", "Dagger"]
    player.equipment["Weapon"] = _fake_item("Blade", crit=0.10)
    player.equipment["OffHand"] = _fake_item("Dagger", typ="Weapon", subtyp="Dagger", crit=0.05)
    player.equipment["Armor"] = _fake_item("Mail", typ="Armor", subtyp="Armor", handed=0)
    player.equipment["Ring"] = _fake_item("Old Ring", typ="Accessory", subtyp="Ring", handed=0)
    player.equipment["Pendant"] = _fake_item("Charm", typ="Accessory", subtyp="Pendant", handed=0)

    def fake_check_mod(mod, enemy=None, typ=None, luck_factor=1, ultimate=False, ignore=False):
        if mod == "speed":
            return 0
        if mod == "weapon":
            return {
                "Blade": 10,
                "Greatsword": 20,
                "Twinblade": 15,
            }.get(player.equipment["Weapon"].name, 0)
        if mod == "offhand":
            return {
                "Dagger": 5,
                "Twinblade": 15,
            }.get(player.equipment["OffHand"].name, 0)
        if mod == "armor":
            return 30
        if mod == "shield":
            return 25 if player.equipment["OffHand"].subtyp == "Shield" else 0
        if mod == "magic def":
            return 40
        if mod == "magic":
            return 50
        if mod == "heal":
            return 60
        return 0

    player.check_mod = fake_check_mod
    player.buff_str = lambda: f"Buff-{player.equipment['Ring'].name}"
    return player


class BossTile:
    def __str__(self):
        return "RedDragonBossRoom"


class CaveTile:
    def __str__(self):
        return "CavePath"


class UnknownTile:
    def __str__(self):
        return "UnknownTile"


class TestPlayerLootCoverage:
    def test_loot_handles_gnome_gold_quest_ability_and_non_summoner_summon_skip(self, monkeypatch):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        player.cls.name = "Lancer"
        player.race.name = "Gnome"
        player.stats.charisma = 20
        player.gold = 0
        player.quest_dict = {
            "Main": {},
            "Side": {"Grease the Gears": {"What": items.BirdFat, "Completed": False}},
            "Bounty": {},
        }
        captured = []
        player.modify_inventory = lambda item, rare=False, **_kwargs: captured.append((item.name, rare))
        player.quests = lambda enemy=None, item=None: f"Quest:{item.name}\n" if item is not None else ""
        player.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 2 if mod == "luck" else 0
        player.spellbook["Skills"]["Jump"] = SimpleNamespace(
            unlock_item_modification=lambda name: "Recover" if name == "Dragon's Tear" else None
        )
        summon_item = SimpleNamespace(name="Spirit Sigil", subtyp="Summon - Spirit", rarity=1.0)
        enemy = SimpleNamespace(
            name="Wyvern",
            gold=100,
            inventory={"drops": [items.BirdFat, items.DragonTear, summon_item]},
        )
        rolls = iter([0.0, 0.0, 0.0])
        monkeypatch.setattr(player_module.random, "random", lambda: next(rolls))

        message = player.loot(enemy, CaveTile())

        assert "Wyvern dropped 125 gold." in message
        assert ("Bird Fat", True) in captured
        assert ("Dragon's Tear", True) in captured
        assert all(name != "Spirit Sigil" for name, _rare in captured)
        assert "Quest:Bird Fat" in message
        assert "New Jump modification unlocked: Recover." in message
        assert player.gold == 125

    def test_loot_boss_branch_drops_special_and_regular_items_but_not_unneeded_quest_items(self, monkeypatch):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        captured = []
        player.modify_inventory = lambda item, rare=False, **_kwargs: captured.append((item.name, rare))
        player.quests = lambda enemy=None, item=None: ""
        player.spellbook["Skills"]["Jump"] = SimpleNamespace(
            unlock_boss_modification=lambda name: "Skyfall" if name == "Red Dragon" else None
        )
        boss_special = SimpleNamespace(name="Boss Relic", subtyp="Special", rarity=1.0)
        enemy = SimpleNamespace(
            name="Red Dragon",
            gold=0,
            inventory={"drops": [boss_special, items.HealthPotion(), items.ElementalMote]},
        )
        monkeypatch.setattr(player_module.random, "random", lambda: 0.0)

        message = player.loot(enemy, BossTile())

        assert ("Boss Relic", True) in captured
        assert ("Health Potion", False) in captured
        assert all(name != "Elemental Mote" for name, _rare in captured)
        assert "New Jump modification unlocked: Skyfall." in message

    def test_loot_skips_duplicate_summon_items_and_restricted_ability_items(self, monkeypatch):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        player.cls.name = "Summoner"
        player.special_inventory = {"Spirit Sigil": [SimpleNamespace(name="Spirit Sigil")]}
        player.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 4 if mod == "luck" else 0
        captured = []
        player.modify_inventory = lambda item, rare=False, **_kwargs: captured.append((item.name, rare))
        player.quests = lambda enemy=None, item=None: ""
        enemy = SimpleNamespace(
            name="Imp",
            gold=0,
            inventory={"drops": [SimpleNamespace(name="Spirit Sigil", subtyp="Summon - Spirit", rarity=1.0), items.DragonTear]},
        )
        rolls = iter([0.0, 0.0])
        monkeypatch.setattr(player_module.random, "random", lambda: next(rolls))

        message = player.loot(enemy, CaveTile())

        assert message == ""
        assert captured == []


class TestPlayerPreviewCoverage:
    def test_equip_diff_returns_empty_for_forbidden_item(self):
        player = _preview_player()
        forbidden = _fake_item("Forbidden Blade")

        diff = player.equip_diff(forbidden, "Weapon")

        assert diff == ""
        assert player.equipment["Weapon"].name == "Blade"
        assert player.equipment["OffHand"].name == "Dagger"

    def test_equip_diff_covers_two_handed_weapon_offhand_weapon_and_accessory_preview(self):
        player = _preview_player()

        greatsword = _fake_item("Greatsword", handed=2, crit=0.2)
        weapon_diff = player.equip_diff(greatsword, "Weapon")
        assert "10/5 -> 20" in weapon_diff
        assert "10%/5% -> 20%" in weapon_diff
        assert player.equipment["Weapon"].name == "Blade"
        assert player.equipment["OffHand"].name == "Dagger"

        offhand_diff = player.equip_diff(_fake_item("Twinblade", typ="Weapon", subtyp="Dagger", crit=0.15), "OffHand")
        assert "10 -> 10/15" in offhand_diff
        assert "10% -> 10%/15%" in offhand_diff

        ring_diff = player.equip_diff(
            _fake_item("Power Ring", typ="Accessory", subtyp="Ring", handed=0),
            "Accessory",
        )
        assert "Buff-Power Ring" in ring_diff
        assert player.equipment["Ring"].name == "Old Ring"

    def test_equip_diff_buy_weapon_can_preview_dual_wield_path(self):
        player = _preview_player()
        player.equipment["OffHand"] = items.NoOffHand()

        diff = player.equip_diff(_fake_item("Twinblade", crit=0.15), "Weapon", buy=True)

        assert "10 -> 15/15" in diff
        assert "10% -> 15%/15%" in diff
        assert player.equipment["Weapon"].name == "Blade"
        assert player.equipment["OffHand"].subtyp == "None"

    def test_equip_offhand_with_two_handed_weapon_unequips_weapon_and_jump_lookup_via_values(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        player.cls.equip_check = lambda item, equip_slot: True
        player.equipment["Weapon"] = _fake_item("Great Pike", subtyp="Polearm", handed=2, crit=0.2)
        player.equipment["OffHand"] = items.NoOffHand()
        player.spellbook["Skills"] = {"Leap Alias": SimpleNamespace(name="Jump", enforce_modification_limit=lambda _player: ["Long"])}
        captured = []
        player.modify_inventory = lambda item, num=1, subtract=False, **_kwargs: captured.append((item.name, subtract))

        result = player.equip("OffHand", _fake_item("Buckler", typ="OffHand", subtyp="Shield", handed=0))

        assert result is True
        assert player.equipment["Weapon"].subtyp == "None"
        assert player.equipment["OffHand"].name == "Buckler"
        assert ("Great Pike", False) in captured

    def test_unequip_promo_and_open_up_unknown_tile_branch(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        captured = []
        player.modify_inventory = lambda item, num=1, subtract=False, **_kwargs: captured.append((item.name, subtract))

        empty_weapon = player.unequip("Weapon")
        player.unequip(promo=True)

        assert empty_weapon.subtyp == "None"
        assert any(name == player.cls.equipment["Weapon"].name for name, _subtract in captured)
        with pytest.raises(NotImplementedError):
            player.unequip()

        player.world_dict[(player.location_x, player.location_y, player.location_z)] = UnknownTile()
        with pytest.raises(AssertionError):
            player.open_up(game=SimpleNamespace())
