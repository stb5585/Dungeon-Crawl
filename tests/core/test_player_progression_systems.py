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
    summarize_gameplay_stats,
    summarize_gameplay_stat_groups,
)
from tests.test_framework import TestGameState


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

        clamped = normalize_gameplay_stats(
            {
                "steps_taken": -10,
                "stairs_used": "-3",
                "highest_damage_taken": -99,
                "highest_level_reached": -2,
            },
            current_level=-4,
        )
        assert clamped["steps_taken"] == 0
        assert clamped["stairs_used"] == 0
        assert clamped["highest_damage_taken"] == 0
        assert clamped["highest_level_reached"] == 1

        summary = summarize_gameplay_stats(
            {
                "enemies_defeated": "4",
                "flees": 2,
                "deaths": "1",
                "highest_level_reached": "3",
            },
            current_level=6,
        )
        assert summary["encounters_survived"] == 5
        assert summary["combat_outcomes"] == 7
        assert summary["combat_survival_rate_percent"] == 71
        assert summary["exploration_actions"] == 0
        assert summary["total_activity"] == 7
        assert summary["highest_level_reached"] == 6

        groups = summarize_gameplay_stat_groups(
            {
                "steps_taken": 12,
                "stairs_used": 3,
                "enemies_defeated": 4,
                "flees": 2,
                "deaths": 1,
                "highest_damage_dealt": 99,
            },
            current_level=6,
        )
        assert groups["exploration"] == {
            "steps_taken": 12,
            "stairs_used": 3,
            "exploration_actions": 15,
        }
        assert groups["combat"]["encounters_survived"] == 5
        assert groups["combat"]["combat_survival_rate_percent"] == 71
        assert groups["records"]["highest_damage_dealt"] == 99
        assert groups["records"]["total_activity"] == 22

        loaded = SimpleNamespace(name="Loaded Hero")
        load_calls = []
        removed = []
        monkeypatch.setattr(
            player_module.persistence.SaveManager,
            "load_player",
            lambda filename, is_tmp=False, skip_tiles=False: load_calls.append(
                (filename, is_tmp, skip_tiles)
            )
            or loaded,
        )
        monkeypatch.setattr(
            player_module.persistence.SaveManager,
            "delete_save",
            lambda filename, is_tmp=False: removed.append((filename, is_tmp)) or True,
        )

        assert load_char() is None

        restored = load_char(char=SimpleNamespace(name="Hero"))

        assert restored is loaded
        assert load_calls == [("hero.save", True, True)]
        assert removed == [("hero.save", True)]

    def test_tiled_parsing_helpers_cover_json_xml_inline_and_chunk_maps(self, tmp_path):
        assert _parse_tiled_properties(None) == {}
        assert _parse_tiled_properties([{"name": "default_tile", "value": "Wall"}]) == {
            "default_tile": "Wall"
        }
        assert _extract_tile_type({"type": "Floor"}) == "Floor"
        assert _extract_tile_type({"class": "Portal"}) == "Portal"
        assert _extract_tile_type({"properties": [{"name": "tile", "value": "Trap"}]}) == "Trap"

        json_tileset = tmp_path / "tileset.json"
        json_tileset.write_text(
            json.dumps({"tiles": [{"id": 0, "type": "Floor"}]}), encoding="utf-8"
        )
        xml_tileset = tmp_path / "tileset.tsx"
        xml_tileset.write_text(
            """<?xml version="1.0" encoding="UTF-8"?>
<tileset>
  <tile id="0" type="Wall"/>
</tileset>
""",
            encoding="utf-8",
        )

        json_data, json_gid = _load_tiled_tileset(
            {"source": "tileset.json", "firstgid": 4}, str(tmp_path)
        )
        xml_data, xml_gid = _load_tiled_tileset(
            {"source": "tileset.tsx", "firstgid": 8}, str(tmp_path)
        )
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
                            "chunks": [
                                {"x": 0, "y": 0, "width": 2, "height": 2, "data": [1, 0, 0, 1]}
                            ],
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
        missing_layer.write_text(
            json.dumps({"width": 1, "height": 1, "layers": []}), encoding="utf-8"
        )
        with pytest.raises(ValueError):
            _load_tiled_map(str(missing_layer), 1, fake_tiles)

    def test_tiled_map_loader_uses_gameplay_layer_and_supports_flexible_chunks(self, tmp_path):
        fake_tiles = SimpleNamespace(
            Wall=_tile_factory("Wall"),
            Floor=_tile_factory("Floor"),
            CrystalClusterTile=_tile_factory("CrystalClusterTile"),
        )

        flexible_path = tmp_path / "flexible.json"
        flexible_path.write_text(
            json.dumps(
                {
                    "width": 0,
                    "height": 0,
                    "infinite": True,
                    "properties": [{"name": "default_tile", "value": "Wall"}],
                    "tilesets": [
                        {
                            "firstgid": 1,
                            "tiles": [
                                {"id": 0, "type": "Floor"},
                                {"id": 1, "type": "CrystalClusterTile"},
                            ],
                        }
                    ],
                    "layers": [
                        {
                            "name": "Decor",
                            "type": "tilelayer",
                            "visible": True,
                            "properties": [{"name": "decorative", "value": True}],
                            "chunks": [{"x": -1, "y": -1, "width": 1, "height": 1, "data": [2]}],
                        },
                        {
                            "name": "Tiles",
                            "type": "tilelayer",
                            "visible": True,
                            "chunks": [{"x": -2, "y": -1, "width": 2, "height": 1, "data": [1, 0]}],
                        },
                    ],
                }
            ),
            encoding="utf-8",
        )

        flexible_world = _load_tiled_map(str(flexible_path), 5, fake_tiles)

        assert flexible_world[(-2, -1, 5)].kind == "Floor"
        assert flexible_world[(-1, -1, 5)].kind == "Wall"
        assert all(tile.kind != "CrystalClusterTile" for tile in flexible_world.values())

        narrow_path = tmp_path / "narrow.json"
        narrow_path.write_text(
            json.dumps(
                {
                    "width": 3,
                    "height": 1,
                    "tilesets": [{"firstgid": 1, "tiles": [{"id": 0, "type": "Floor"}]}],
                    "layers": [{"name": "Tiles", "type": "tilelayer", "data": [1, 0, 1]}],
                }
            ),
            encoding="utf-8",
        )

        narrow_world = _load_tiled_map(str(narrow_path), 2, fake_tiles)

        assert [narrow_world[(x, 0, 2)].kind for x in range(3)] == ["Floor", "Wall", "Floor"]

    def test_load_tiles_prefers_json_per_level_and_loads_optional_side_areas(
        self, tmp_path, monkeypatch
    ):
        map_dir = tmp_path / "map_files"
        map_dir.mkdir()
        (map_dir / "map_level_0.txt").write_text("Wall\tCavePath\n", encoding="utf-8")
        (map_dir / "map_level_1.txt").write_text("Wall\n", encoding="utf-8")
        for name in ["map_level_1.json", "map_funhouse.json", "map_realm_cambion.json"]:
            (map_dir / name).write_text("{}", encoding="utf-8")

        def fake_load_tiled_map(path, z, _map_tiles):
            return {(99, z, z): SimpleNamespace(source=Path(path).name, z=z)}

        monkeypatch.setattr(player_module.exploration, "_load_tiled_map", fake_load_tiled_map)
        monkeypatch.setattr(player_module.exploration, "MAP_FILES_DIR", map_dir)
        monkeypatch.chdir(tmp_path)

        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        player.load_tiles()

        assert type(player.world_dict[(0, 0, 0)]).__name__ == "Wall"
        assert type(player.world_dict[(1, 0, 0)]).__name__ == "CavePath"
        assert player.world_dict[(99, 1, 1)].source == "map_level_1.json"
        assert player.world_dict[(99, 7, 7)].source == "map_funhouse.json"
        assert (
            player.world_dict[(99, REALM_OF_CAMBION_LEVEL, REALM_OF_CAMBION_LEVEL)].source
            == "map_realm_cambion.json"
        )

    def test_load_tiles_finds_repo_maps_when_cwd_changes(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        player.load_tiles()

        assert player.world_dict
        assert any(pos[2] == 1 for pos in player.world_dict)
        assert (5, 10, 1) in player.world_dict


class TestPlayerProgression:
    def test_level_up_awards_a_point_without_abilities_or_stat_choice(self, monkeypatch):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human", level=3)
        player.to_town()
        player.health.current = 1
        player.mana.current = 1
        player.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 0
        rolls = iter([5, 4, 2, 1, 3, 1])
        monkeypatch.setattr(player_module.random, "randint", lambda _a, _b: next(rolls))

        old_strength = player.stats.strength
        old_spells = dict(player.spellbook["Spells"])
        old_skills = dict(player.spellbook["Skills"])
        old_points = player.progression.unspent_points
        result = player.level_up()

        assert result.new_level == 4
        assert player.level.level == 4
        assert player.health.current == player.health.max
        assert player.mana.current == player.mana.max
        assert player.stats.strength == old_strength
        assert player.spellbook["Spells"] == old_spells
        assert player.spellbook["Skills"] == old_skills
        assert player.progression.unspent_points == old_points + 1

    def test_level_up_does_not_apply_catalog_upgrades_automatically(self, monkeypatch):
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

        monkeypatch.setattr(
            player_module.abilities, "spell_dict", {"Warrior": {"2": UpgradedSpell}}
        )
        monkeypatch.setattr(
            player_module.abilities, "skill_dict", {"Warrior": {"2": UpgradedSkill}}
        )
        rolls = iter([1, 1, 0, 0, 0, 0])
        monkeypatch.setattr(player_module.random, "randint", lambda _a, _b: next(rolls))

        old_points = player.progression.unspent_points
        player.level_up()

        assert "Spark" in player.spellbook["Spells"]
        assert "Spark II" not in player.spellbook["Spells"]
        assert "True Strike" in player.spellbook["Skills"]
        assert "Piercing Strike" in player.spellbook["Skills"]
        assert "True Piercing Strike" not in player.spellbook["Skills"]
        assert player.progression.unspent_points == old_points + 1

    def test_level_up_does_not_trigger_catalog_skill_side_effects(self, monkeypatch):
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
        monkeypatch.setattr(
            player_module.abilities, "skill_dict", {"Warrior": {"2": TransformSkill}}
        )
        monkeypatch.setattr(player_module.random, "randint", lambda _a, _b: 0)

        player.level_up()
        assert "Transform" not in player.spellbook["Skills"]

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

        assert "Health Drain" in drain_player.spellbook["Skills"]
        assert "Mana Drain" in drain_player.spellbook["Skills"]
        assert "Health/Mana Drain" not in drain_player.spellbook["Skills"]

    def test_level_up_ignores_catalog_entries_until_purchased(self, monkeypatch):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human", level=1)
        player.check_mod = lambda mod, enemy=None, typ=None, luck_factor=1, **_kwargs: 0

        class ObjectParentSpell(object):
            def __init__(self):
                self.name = "Sunburst"

        monkeypatch.setattr(
            player_module.abilities, "spell_dict", {"Warrior": {"2": ObjectParentSpell}}
        )
        monkeypatch.setattr(player_module.abilities, "skill_dict", {"Warrior": {}})
        rolls = iter([1, 1, 0, 0, 0, 0])
        monkeypatch.setattr(player_module.random, "randint", lambda _a, _b: next(rolls))

        player.level_up()

        assert "Sunburst" not in player.spellbook["Spells"]

    def test_save_wrapper_covers_direct_tmp_and_default_paths(self, monkeypatch):
        player = TestGameState.create_player(name="Saver", class_name="Warrior", race_name="Human")
        save_calls = []

        monkeypatch.setattr(
            player_module.inventory.SaveManager,
            "save_player",
            lambda player_obj, filename, is_tmp=False: save_calls.append(
                (player_obj.name, filename, is_tmp)
            ),
        )

        player.save(filepath="/tmp/custom_name.save")
        player.save(tmp=True)
        player.save()

        assert ("Saver", "custom_name.save", False) in save_calls
        assert ("Saver", "saver.save", True) in save_calls
        assert save_calls.count(("Saver", "saver.save", False)) == 1

    def test_equip_branches_handle_validation_two_handed_conflicts_and_jump_limits(
        self, monkeypatch
    ):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        calls = []
        player.modify_inventory = lambda item, num=1, subtract=False, **_kwargs: calls.append(
            (item.name, subtract)
        )

        assert player.equip("Helmet", items.IronHelm(), check=True) is True
        assert player.equipment["Helmet"].name == "Iron Helm"

        player.cls.equip_check = lambda item, slot: False
        assert player.equip("Weapon", SimpleNamespace(subtyp="Sword")) is False

        player.cls.equip_check = lambda item, slot: True
        two_hander = SimpleNamespace(name="Great Pike", subtyp="Polearm", handed=2)
        assert player.equip("Weapon", two_hander) is True
        assert player.equipment["Weapon"] is two_hander
        assert player.equipment["OffHand"].subtyp == "None"
        assert (
            any(name == "No OffHand" or "No OffHand" == name for name, _subtract in calls) is False
        )
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

        player.equip("Helmet", items.Tarnhelm())
        assert player.invisible is True
        player.equip("Helmet", items.NoHelmet())
        assert player.invisible is False
        player.equip("Helmet", items.HelmOfRostam())
        assert player.invisible is False

        player.equip(
            "Pendant", SimpleNamespace(name="Levitation Necklace", subtyp="Pendant", handed=0)
        )
        assert player.flying is True

    def test_action_and_movement_helpers_cover_transform_move_forward_and_stairs(self):
        player = TestGameState.create_player(class_name="Lycan", race_name="Human", level=12)
        player.world_dict[(5, 9, 0)] = SimpleNamespace(enter=True)
        player.facing = "north"
        player.transform_type = player.cls
        player._transformed = True
        player.class_effects["Power Up"].duration = 3
        player.physical_effects["Disarm"].active = False

        actions = player.additional_actions(["Attack", "Use Item", "Flee"])
        assert "Transform" not in actions
        assert "Dismiss Form" in actions
        assert "Use Item" in actions
        assert "Flee" in actions

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
        assert player.level_exp() == 1137

    def test_untransform_is_absent_until_a_transform_is_active(self):
        player = TestGameState.create_player(
            class_name="Warrior",
            race_name="Human",
        )

        actions = player.additional_actions(["Attack", "Use Item", "Flee"])

        assert "Untransform" not in actions
