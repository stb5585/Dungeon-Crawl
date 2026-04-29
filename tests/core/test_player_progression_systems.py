#!/usr/bin/env python3
"""Focused coverage for player progression, save wrappers, and map-loading helpers."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

from src.core import items, map_tiles, player as player_module
from src.core.player import (
    REALM_OF_CAMBION_LEVEL,
    _extract_tile_type,
    _load_tiled_map,
    _load_tiled_tileset,
    _parse_tiled_properties,
    load_char,
    normalize_gameplay_stats,
)
from tests.test_framework import TestGameState


class RecordingTextBox:
    def __init__(self):
        self.messages = []
        self.clear_count = 0

    def print_text_in_rectangle(self, message):
        self.messages.append(message)

    def clear_rectangle(self):
        self.clear_count += 1


class SequencePopup:
    def __init__(self, selections):
        self.selections = list(selections)
        self.calls = 0

    def navigate_popup(self):
        self.calls += 1
        return self.selections.pop(0)


def _menu_choice(index):
    return SimpleNamespace(navigate_popup=lambda: index)


def _confirm(result):
    return SimpleNamespace(navigate_popup=lambda: result)


def _tile_factory(kind):
    class Tile:
        def __init__(self, x, y, z):
            self.kind = kind
            self.position = (x, y, z)

    return Tile


class TestPlayerTopLevelHelpers:
    def test_normalize_gameplay_stats_and_load_char_tmp_cleanup(self, monkeypatch):
        normalized = normalize_gameplay_stats(
            {"steps_taken": "7", "deaths": "bad", "highest_level_reached": "2"},
            current_level=5,
        )

        assert normalized["steps_taken"] == 7
        assert normalized["deaths"] == 0
        assert normalized["highest_level_reached"] == 5

        loaded = SimpleNamespace(name="Loaded Hero")
        load_calls = []
        removed = []
        monkeypatch.setattr(
            player_module.SaveManager,
            "load_player",
            lambda filename, is_tmp=False, skip_tiles=False: load_calls.append((filename, is_tmp, skip_tiles)) or loaded,
        )
        monkeypatch.setattr(player_module.os, "remove", lambda path: removed.append(path))

        assert load_char() is None

        restored = load_char(char=SimpleNamespace(name="Hero"))

        assert restored is loaded
        assert load_calls == [("hero.save", True, True)]
        assert removed == ["tmp_files/hero.save"]

    def test_tiled_parsing_helpers_cover_json_xml_inline_and_chunk_maps(self, tmp_path):
        assert _parse_tiled_properties(None) == {}
        assert _parse_tiled_properties([{"name": "default_tile", "value": "Wall"}]) == {
            "default_tile": "Wall"
        }
        assert _extract_tile_type({"type": "Floor"}) == "Floor"
        assert _extract_tile_type({"class": "Portal"}) == "Portal"
        assert _extract_tile_type({"properties": [{"name": "tile", "value": "Trap"}]}) == "Trap"

        json_tileset = tmp_path / "tileset.json"
        json_tileset.write_text(json.dumps({"tiles": [{"id": 0, "type": "Floor"}]}), encoding="utf-8")
        xml_tileset = tmp_path / "tileset.tsx"
        xml_tileset.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<tileset>
  <tile id="0" type="Wall"/>
</tileset>
""",
            encoding="utf-8",
        )

        json_data, json_gid = _load_tiled_tileset({"source": "tileset.json", "firstgid": 4}, str(tmp_path))
        xml_data, xml_gid = _load_tiled_tileset({"source": "tileset.tsx", "firstgid": 8}, str(tmp_path))
        inline_data, inline_gid = _load_tiled_tileset({"firstgid": 3, "tiles": []}, str(tmp_path))

        assert json_data["tiles"][0]["type"] == "Floor"
        assert json_gid == 4
        assert xml_data["tiles"][0]["type"] == "Wall"
        assert xml_gid == 8
        assert inline_data["firstgid"] == 3
        assert inline_gid == 3

        fake_tiles = SimpleNamespace(
            Wall=_tile_factory("Wall"),
            Floor=_tile_factory("Floor"),
        )

        map_path = tmp_path / "map.json"
        map_path.write_text(
            json.dumps(
                {
                    "width": 2,
                    "height": 2,
                    "properties": [{"name": "default_tile", "value": "Wall"}],
                    "tilesets": [{"firstgid": 1, "tiles": [{"id": 0, "type": "Floor"}]}],
                    "layers": [{"type": "tilelayer", "data": [1, 0, 0, 1]}],
                }
            ),
            encoding="utf-8",
        )
        world = _load_tiled_map(str(map_path), 3, fake_tiles)
        assert world[(0, 0, 3)].kind == "Floor"
        assert world[(1, 0, 3)].kind == "Wall"
        assert world[(1, 1, 3)].kind == "Floor"

        chunk_path = tmp_path / "chunked.json"
        chunk_path.write_text(
            json.dumps(
                {
                    "width": 2,
                    "height": 2,
                    "tilesets": [{"firstgid": 1, "tiles": [{"id": 0, "type": "Floor"}]}],
                    "layers": [
                        {
                            "type": "tilelayer",
                            "chunks": [{"x": 0, "y": 0, "width": 2, "height": 2, "data": [1, 0, 0, 1]}],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        chunked_world = _load_tiled_map(str(chunk_path), 4, fake_tiles)
        assert chunked_world[(0, 0, 4)].kind == "Floor"
        assert chunked_world[(1, 1, 4)].kind == "Floor"

        missing_layer = tmp_path / "missing_layer.json"
        missing_layer.write_text(json.dumps({"width": 1, "height": 1, "layers": []}), encoding="utf-8")
        with pytest.raises(ValueError):
            _load_tiled_map(str(missing_layer), 1, fake_tiles)

    def test_load_tiles_prefers_json_per_level_and_loads_optional_side_areas(self, tmp_path, monkeypatch):
        map_dir = tmp_path / "map_files"
        map_dir.mkdir()
        (map_dir / "map_level_0.txt").write_text("Wall\tCavePath\n", encoding="utf-8")
        (map_dir / "map_level_1.txt").write_text("Wall\n", encoding="utf-8")
        for name in ["map_level_1.json", "map_funhouse.json", "map_realm_cambion.json"]:
            (map_dir / name).write_text("{}", encoding="utf-8")

        def fake_load_tiled_map(path, z, _map_tiles):
            return {(99, z, z): SimpleNamespace(source=Path(path).name, z=z)}

        monkeypatch.setattr(player_module, "_load_tiled_map", fake_load_tiled_map)
        monkeypatch.setattr(player_module, "MAP_FILES_DIR", map_dir)
        monkeypatch.chdir(tmp_path)

        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        player.load_tiles()

        assert type(player.world_dict[(0, 0, 0)]).__name__ == "Wall"
        assert type(player.world_dict[(1, 0, 0)]).__name__ == "CavePath"
        assert player.world_dict[(99, 1, 1)].source == "map_level_1.json"
        assert player.world_dict[(99, 7, 7)].source == "map_funhouse.json"
        assert player.world_dict[(99, REALM_OF_CAMBION_LEVEL, REALM_OF_CAMBION_LEVEL)].source == "map_realm_cambion.json"

    def test_load_tiles_finds_repo_maps_when_cwd_changes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        player.load_tiles()

        assert player.world_dict
        assert any(pos[2] == 1 for pos in player.world_dict)
        assert (5, 10, 1) in player.world_dict


class TestPlayerProgressionAndMenus:
    def test_level_up_adds_spell_skill_jump_totem_and_stat_choice(self, monkeypatch):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human", level=3)
        player.to_town()
        player.health.current = 1
        player.mana.current = 1
        player.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 0

        class BaseSpell:
            def __init__(self):
                self.name = "Old Flare"
                self.passive = False
                self.cost = 0

        class DummySpell(BaseSpell):
            def __init__(self):
                super().__init__()
                self.name = "Flare"

        class BaseSkill:
            def __init__(self):
                self.name = "Old Totem"
                self.passive = False
                self.cost = 0

        class DummyTotem(BaseSkill):
            def __init__(self):
                super().__init__()
                self.name = "Totem"

            def check_and_unlock_aspects(self, _level):
                return ["Soul", "Storm"]

        jump_unlocks = []
        player.spellbook["Skills"]["Jump"] = SimpleNamespace(
            name="Jump",
            check_and_unlock_level_modifications=lambda level, cls_name: jump_unlocks.append((level, cls_name)) or ["Dive"],
        )

        monkeypatch.setattr(player_module.abilities, "spell_dict", {"Warrior": {"4": DummySpell}})
        monkeypatch.setattr(player_module.abilities, "skill_dict", {"Warrior": {"4": DummyTotem}})
        rolls = iter([5, 4, 2, 1, 3, 1])
        monkeypatch.setattr(player_module.random, "randint", lambda _a, _b: next(rolls))

        textbox = RecordingTextBox()
        getch_calls = []
        game = SimpleNamespace(stdscr=SimpleNamespace(getch=lambda: getch_calls.append(True)))

        old_exp_to_gain = player.level.exp_to_gain
        old_strength = player.stats.strength
        player.level_up(game=game, textbox=textbox, menu=_menu_choice(0))

        joined_messages = "\n".join(textbox.messages)
        assert player.level.level == 4
        assert player.health.current == player.health.max
        assert player.mana.current == player.mana.max
        assert player.stats.strength == old_strength + 1
        assert player.level.exp_to_gain > old_exp_to_gain
        assert "Flare" in player.spellbook["Spells"]
        assert "Totem" in player.spellbook["Skills"]
        assert "gained the ability to cast Flare" in joined_messages
        assert "gained the ability to use Totem" in joined_messages
        assert "New Jump modifications unlocked: Dive." in joined_messages
        assert "Totem aspects unlocked: Soul, Storm." in joined_messages
        assert "New Totem aspects unlocked: Soul, Storm." in joined_messages
        assert "strength" in textbox.messages[-1].lower()
        assert jump_unlocks == [(4, "Warrior")]
        assert textbox.clear_count == 2
        assert len(getch_calls) == 2

    def test_level_up_handles_upgrades_and_skill_side_effect_branches(self, monkeypatch):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human", level=1)
        player.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 0

        class BaseSpell:
            def __init__(self):
                self.name = "Spark"
                self.passive = False
                self.cost = 0

        class UpgradedSpell(BaseSpell):
            def __init__(self):
                super().__init__()
                self.name = "Spark II"

        class BaseSkill:
            def __init__(self):
                self.name = "True Strike"
                self.passive = False
                self.cost = 0

        class UpgradedSkill(BaseSkill):
            def __init__(self):
                super().__init__()
                self.name = "True Piercing Strike"

        player.spellbook["Spells"]["Spark"] = BaseSpell()
        player.spellbook["Skills"]["True Strike"] = BaseSkill()
        player.spellbook["Skills"]["Piercing Strike"] = SimpleNamespace(name="Piercing Strike")

        monkeypatch.setattr(player_module.abilities, "spell_dict", {"Warrior": {"2": UpgradedSpell}})
        monkeypatch.setattr(player_module.abilities, "skill_dict", {"Warrior": {"2": UpgradedSkill}})
        rolls = iter([1, 1, 0, 0, 0, 0])
        monkeypatch.setattr(player_module.random, "randint", lambda _a, _b: next(rolls))

        textbox = RecordingTextBox()
        game = SimpleNamespace(stdscr=SimpleNamespace(getch=lambda: None))
        player.level_up(game=game, textbox=textbox)

        joined_messages = "\n".join(textbox.messages)
        assert "Spark" not in player.spellbook["Spells"]
        assert "Spark II" in player.spellbook["Spells"]
        assert "True Strike" not in player.spellbook["Skills"]
        assert "Piercing Strike" not in player.spellbook["Skills"]
        assert "True Piercing Strike" in player.spellbook["Skills"]
        assert "Spark is upgraded to Spark II." in joined_messages
        assert "True Strike is upgraded to True Piercing Strike." in joined_messages

    def test_level_up_transform_and_drain_skill_paths(self, monkeypatch):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human", level=1)
        player.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 0

        class BaseSkill:
            def __init__(self):
                self.name = "Old Skill"
                self.passive = False
                self.cost = 0

        class TransformSkill(BaseSkill):
            def __init__(self):
                super().__init__()
                self.name = "Transform"

            def use(self, _player):
                return "Wild shape awakened.\n"

        monkeypatch.setattr(player_module.abilities, "spell_dict", {"Warrior": {}})
        monkeypatch.setattr(player_module.abilities, "skill_dict", {"Warrior": {"2": TransformSkill}})
        monkeypatch.setattr(player_module.random, "randint", lambda _a, _b: 0)

        textbox = RecordingTextBox()
        game = SimpleNamespace(stdscr=SimpleNamespace(getch=lambda: None))
        player.level_up(game=game, textbox=textbox)
        assert "Wild shape awakened." in textbox.messages[0]

        drain_player = TestGameState.create_player(class_name="Warrior", race_name="Human", level=1)
        drain_player.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 0

        class DrainBase:
            def __init__(self):
                self.name = "Old Drain"
                self.passive = False
                self.cost = 0

        class DrainFusion(DrainBase):
            def __init__(self):
                super().__init__()
                self.name = "Health/Mana Drain"

        drain_player.spellbook["Skills"]["Health Drain"] = SimpleNamespace(name="Health Drain")
        drain_player.spellbook["Skills"]["Mana Drain"] = SimpleNamespace(name="Mana Drain")
        monkeypatch.setattr(player_module.abilities, "skill_dict", {"Warrior": {"2": DrainFusion}})
        drain_player.level_up()

        assert "Health Drain" not in drain_player.spellbook["Skills"]
        assert "Mana Drain" not in drain_player.spellbook["Skills"]
        assert "Health/Mana Drain" in drain_player.spellbook["Skills"]

    def test_level_up_handles_non_named_parent_ability(self, monkeypatch):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human", level=1)
        player.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 0

        class ObjectParentSpell(object):
            def __init__(self):
                self.name = "Sunburst"

        monkeypatch.setattr(player_module.abilities, "spell_dict", {"Warrior": {"2": ObjectParentSpell}})
        monkeypatch.setattr(player_module.abilities, "skill_dict", {"Warrior": {}})
        rolls = iter([1, 1, 0, 0, 0, 0])
        monkeypatch.setattr(player_module.random, "randint", lambda _a, _b: next(rolls))

        textbox = RecordingTextBox()
        game = SimpleNamespace(stdscr=SimpleNamespace(getch=lambda: None))
        player.level_up(game=game, textbox=textbox)

        joined_messages = "\n".join(textbox.messages)
        assert "You have gained the ability to cast Sunburst." in joined_messages
        assert "Sunburst" in player.spellbook["Spells"]

    def test_inventory_and_screen_helpers_cover_errors_and_navigation(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        game = SimpleNamespace()
        player.change_location(1, 1, 1)

        with pytest.raises(ValueError):
            player.inventory_screen(game)

        potion = SimpleNamespace(name="Health Potion", subtyp="Health", use=lambda _user: "Used.\n")
        with pytest.raises(ValueError):
            player.inventory_screen(game, inv_popup=SequencePopup([potion]))

        with pytest.raises(ValueError):
            player.inventory_screen(
                game,
                inv_popup=SequencePopup([potion]),
                confirm_popup=lambda *_args, **_kwargs: _confirm(True),
            )

        sanctuary = SimpleNamespace(name="Sanctuary Draft", subtyp="Health", use=lambda _user: "Safe.\n")
        use_box = RecordingTextBox()
        player.inventory_screen(
            game,
            inv_popup=SequencePopup([sanctuary]),
            confirm_popup=lambda *_args, **_kwargs: _confirm(True),
            useitembox=use_box,
        )
        assert use_box.messages == ["Safe.\n"]
        assert use_box.clear_count == 1

        with pytest.raises(ValueError):
            player.key_item_screen(game)

        key_popup = SequencePopup(["Go Back"])
        player.key_item_screen(game, inv_popup=key_popup)
        assert key_popup.calls == 1

        nav_calls = []
        popup = SimpleNamespace(navigate_popup=lambda: nav_calls.append("popup"))
        player.equipment_screen(game, popup)
        player.abilities_screen(game, popup)
        assert nav_calls == ["popup", "popup"]

        with pytest.raises(ValueError):
            player.jump_mods_menu(game)
        with pytest.raises(ValueError):
            player.totem_aspects_menu(game)

        jump_popup = SequencePopup([None])
        totem_popup = SequencePopup([None])
        player.jump_mods_menu(game, jump_popup=jump_popup)
        player.totem_aspects_menu(game, totem_popup=totem_popup)
        assert jump_popup.calls == 1
        assert totem_popup.calls == 1

    def test_save_wrapper_covers_direct_tmp_and_confirmed_interactive_paths(self, monkeypatch):
        player = TestGameState.create_player(name="Saver", class_name="Warrior", race_name="Human")
        save_calls = []
        mkdir_calls = []
        popup_calls = []

        monkeypatch.setattr(
            player_module.SaveManager,
            "save_player",
            lambda player_obj, filename, is_tmp=False: save_calls.append((player_obj.name, filename, is_tmp)),
        )

        player.save(filepath="/tmp/custom_name.save")
        player.save(tmp=True)

        monkeypatch.setattr(player_module.os.path, "isdir", lambda _path: False)
        monkeypatch.setattr(player_module.os, "mkdir", lambda path: mkdir_calls.append(path))
        monkeypatch.setattr(player_module.os.path, "exists", lambda _path: True)

        player.save(game=SimpleNamespace(), confirm_popup=_confirm(False))
        player.save(
            game=SimpleNamespace(),
            confirm_popup=_confirm(True),
            save_popup=lambda _game: popup_calls.append("popup"),
        )

        assert ("Saver", "custom_name.save", False) in save_calls
        assert ("Saver", "saver.save", True) in save_calls
        assert save_calls.count(("Saver", "saver.save", False)) == 1
        assert mkdir_calls == ["save_files", "save_files"]
        assert popup_calls == ["popup"]

    def test_equip_branches_handle_validation_two_handed_conflicts_and_jump_limits(self, monkeypatch):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        calls = []
        player.modify_inventory = lambda item, num=1, subtract=False, **_kwargs: calls.append((item.name, subtract))

        with pytest.raises(ValueError):
            player.equip("Helmet", SimpleNamespace(subtyp="Armor"))

        player.cls.equip_check = lambda item, slot: False
        assert player.equip("Weapon", SimpleNamespace(subtyp="Sword")) is False

        player.cls.equip_check = lambda item, slot: True
        two_hander = SimpleNamespace(name="Great Pike", subtyp="Polearm", handed=2)
        assert player.equip("Weapon", two_hander) is True
        assert player.equipment["Weapon"] is two_hander
        assert player.equipment["OffHand"].subtyp == "None"
        assert any(name == "No OffHand" or "No OffHand" == name for name, _subtract in calls) is False
        assert any(subtract is True and name == "Great Pike" for name, subtract in calls)

        enforced = []
        player.spellbook["Skills"]["Jump"] = SimpleNamespace(
            name="Jump",
            enforce_modification_limit=lambda _player: enforced.append(True) or ["Long"],
        )
        ring = items.PowerRing()
        assert player.equip("Ring", ring) is True
        assert enforced == [True]

    def test_equip_updates_visibility_sight_and_flight_flags(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        player.cls.equip_check = lambda item, slot: True
        player.modify_inventory = lambda *_args, **_kwargs: None

        player.sight = True
        player.equipment["Pendant"] = items.VisionPendant()
        player.equip("Pendant", items.NoPendant())
        assert player.sight is False

        player.equip("Pendant", items.VisionPendant())
        assert player.sight is True

        player.invisible = True
        player.equipment["Armor"] = items.Tarnkappe()
        player.equip("Armor", items.PlateMail())
        assert player.invisible is False

        player.equip("Pendant", SimpleNamespace(name="Levitation Necklace", subtyp="Pendant", handed=0))
        assert player.flying is True

    def test_open_up_handles_funhouse_mimic_chest_and_door(self, monkeypatch):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human", level=12)
        player.location_x, player.location_y, player.location_z = (1, 2, 7)
        player.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 0
        calls = []
        player.modify_inventory = lambda item, num=1, subtract=False, **kwargs: calls.append((item.name, subtract, kwargs.get("rare", False)))
        battle_calls = []

        class FunhouseMimicChestTile:
            def __init__(self):
                self.open = False
                self.enemy = None
                self.loot = lambda: SimpleNamespace(name="Treasure")

            def __str__(self):
                return "FunhouseMimicChest"

        class DoorTile:
            def __init__(self):
                self.open = False
                self.locked = True
                self.enter = False

            def __str__(self):
                return "LockedDoor"

        chest_tile = FunhouseMimicChestTile()
        player.world_dict[(1, 2, 7)] = chest_tile
        monkeypatch.setattr(player_module.random, "randint", lambda _a, _b: 10)
        monkeypatch.setattr(
            player_module.enemies,
            "Mimic",
            lambda level, player_level=None: SimpleNamespace(name=f"Mimic-{level}", anti_magic_active=None),
        )

        textbox = RecordingTextBox()
        player.open_up(
            game=SimpleNamespace(),
            textbox=textbox,
            battle_manager=lambda _game, enemy: battle_calls.append(enemy.name),
        )

        assert player.state == "fight"
        assert chest_tile.open is True
        assert any(name == "Treasure" and rare is False for name, _subtract, rare in calls)
        assert any(name == "Jester Token" and rare is True for name, _subtract, rare in calls)
        assert battle_calls == ["Mimic-4"]
        assert player.gold > 0

        door_tile = DoorTile()
        player.world_dict[(1, 2, 7)] = door_tile
        player.open_up(game=SimpleNamespace(), textbox=textbox)
        assert door_tile.open is True
        assert door_tile.locked is False
        assert door_tile.enter is True
        assert textbox.messages[-1].endswith("opens the door.")

    def test_action_and_movement_helpers_cover_transform_move_forward_and_stairs(self):
        player = TestGameState.create_player(class_name="Lycan", race_name="Human", level=12)
        player.world_dict[(5, 9, 0)] = SimpleNamespace(enter=True)
        player.facing = "north"
        player.transform_type = player.cls
        player.class_effects["Power Up"].duration = 3
        player.physical_effects["Disarm"].active = False

        actions = player.additional_actions(["Attack", "Use Item", "Flee"])
        assert "Transform" in actions
        assert "Untransform" in actions
        assert "Use Item" not in actions
        assert "Flee" not in actions

        player.dwarf_hangover_steps = 2
        player.move_forward(game=None)
        assert (player.location_x, player.location_y) == (5, 9)
        assert player.gameplay_stats["steps_taken"] == 1
        assert player.dwarf_hangover_steps == 1

        player.location_x, player.location_y, player.location_z = (0, 0, 7)
        player.facing = "north"
        player.world_dict[(0, 0, 7)] = map_tiles.FunhouseEmptyPath(0, 0, 7)
        player.world_dict[(0, -1, 7)] = map_tiles.JesterBossRoom(0, -1, 7)
        events = []
        player.move_forward(game=SimpleNamespace(special_event=lambda name: events.append(name)))
        assert (player.location_x, player.location_y) == (0, 0)
        assert events == [map_tiles.JESTER_FORCE_FIELD_EVENT]

        player.special_inventory["Jester Token"] = [items.JesterToken() for _ in range(4)]
        player.move_forward(game=None)
        assert (player.location_x, player.location_y) == (0, -1)

        player.location_z = 0
        player.stairs_up()
        assert player.location_z == -1
        assert player.gameplay_stats["stairs_used"] == 1

        player.special_inventory = {
            "Triangulus": [items.Relic1()],
            "Quadrata": [items.Relic2()],
            "Hexagonum": [items.Relic3()],
            "Luna": [items.Relic4()],
            "Polaris": [items.Relic5()],
            "Infinitas": [items.Relic6()],
        }
        assert player.has_relics() is True
        assert player.level_exp() == (player.exp_scale ** player.level.pro_level) * player.level.level
