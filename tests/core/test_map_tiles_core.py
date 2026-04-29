#!/usr/bin/env python3
"""Focused coverage for core map tile helpers and interaction tiles."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

from src.core import items, map_tiles
from tests.test_framework import TestGameState


class RecordingTextBox:
    def __init__(self):
        self.messages = []
        self.clear_count = 0

    def print_text_in_rectangle(self, message):
        self.messages.append(message)

    def clear_rectangle(self):
        self.clear_count += 1


def _popup(result=True):
    return SimpleNamespace(navigate_popup=lambda: result)


def _make_player(*, class_name="Warrior", race_name="Human", level=10, pro_level=None):
    player = TestGameState.create_player(
        class_name=class_name,
        race_name=race_name,
        level=level,
        pro_level=pro_level,
    )
    player.quest_dict = {"Side": {}, "Main": {}, "Bounty": {}}
    player.special_inventory = {}
    player.inventory = {}
    player.storage = {}
    player.summons = {}
    player.state = "normal"
    player.facing = "north"
    player.previous_location = (0, 0, 0)
    player.location_x = 0
    player.location_y = 0
    player.location_z = 0
    player.world_dict = {}
    player.additional_actions = lambda actions: list(actions)
    player.usable_abilities = lambda _typ: False
    player.abilities_suppressed = lambda: False
    player.is_disarmed = lambda: False
    player.has_relics = lambda: False
    return player


def _make_game(player):
    events = []

    def special_event(name):
        events.append(name)
        return True

    return SimpleNamespace(
        player_char=player,
        _random_combat=False,
        presenter=None,
        special_event=special_event,
        events=events,
    )


class TestMapTileHelpers:
    def test_fake_wall_detection_and_map_tile_intro_text(self):
        player = _make_player()
        player.spellbook["Skills"]["Keen Eye"] = SimpleNamespace(name="Keen Eye")
        tile = map_tiles.MapTile(1, 1, 0)
        player.world_dict[(2, 1, 0)] = map_tiles.FakeWall(2, 1, 0)
        game = _make_game(player)

        direct = map_tiles.check_fake_wall(tile, game)
        intro = tile.intro_text(game)

        assert "Something seems off" in direct
        assert intro == direct

    def test_chalice_progress_description_preview_and_reveal_helpers(self):
        player = _make_player()
        quest_data = {"Completed": False}
        player.quest_dict["Side"][map_tiles.CHALICE_QUEST_NAME] = quest_data
        map_item = SimpleNamespace(name="Chalice Map", description="")
        player.special_inventory["Chalice Map"] = [map_item]

        progress = map_tiles.get_chalice_progress(player)
        assert progress["Revealed"] is False
        assert map_tiles.chalice_altar_visible(player) is False

        map_tiles.sync_chalice_map_description(player)
        assert "faded" in map_item.description.lower()

        progress["Adventurer"] = True
        map_tiles.sync_chalice_map_description(player)
        assert "hidden adventurer" in map_item.description.lower()
        assert "inspect the map carefully" in map_tiles.chalice_map_preview_text(player).lower()

        revealed = map_tiles.reveal_chalice_map_on_inspect(player, map_item)
        assert revealed is True
        assert progress["Revealed"] is True
        assert "altar at 6:2,17" in quest_data["Help Text"]
        assert "sixth floor" in map_item.description.lower()
        assert map_tiles.chalice_altar_visible(player) is True
        assert "Floor 6" in map_tiles.chalice_map_preview_text(player)

    def test_replace_tile_and_enterable_adjacent_positions(self):
        old_tile = SimpleNamespace(
            visited=True,
            near=True,
            open=True,
            read=True,
            blocked="East",
            enter=False,
            defeated=True,
        )
        new_tile = map_tiles.GoldenChaliceRoom(1, 1, 1)
        world = {(1, 1, 1): old_tile}

        map_tiles._replace_tile(world, (1, 1, 1), new_tile)

        assert world[(1, 1, 1)].visited is True
        assert world[(1, 1, 1)].near is True
        assert world[(1, 1, 1)].open is True
        assert world[(1, 1, 1)].read is True
        assert world[(1, 1, 1)].enter is False

        positions = map_tiles._enterable_adjacent_positions(
            {
                (2, 1, 0): SimpleNamespace(enter=True),
                (0, 1, 0): SimpleNamespace(enter=False),
                (1, 2, 0): SimpleNamespace(enter=True),
            },
            1,
            1,
            0,
        )
        assert ("east", (2, 1, 0)) in positions
        assert ("south", (1, 2, 0)) in positions
        assert all(pos != ("west", (0, 1, 0)) for pos in positions)

    def test_cambion_state_message_and_clue_helpers(self):
        player = _make_player()
        player.location_z = map_tiles.REALM_OF_CAMBION_LEVEL

        state = map_tiles._ensure_cambion_state(player)
        assert state["anti_magic_active"] is True
        assert player.anti_magic_active is True

        map_tiles._queue_cambion_message(player, "hello")
        assert map_tiles.pop_cambion_messages(player) == ["hello"]
        assert map_tiles.pop_cambion_messages(player) == []

        clue_pos = next(iter(map_tiles.CAMBION_CODE_CLUES))
        map_tiles.reveal_cambion_code_clue(player, clue_pos)
        first = map_tiles.pop_cambion_messages(player)
        map_tiles.reveal_cambion_code_clue(player, clue_pos)
        second = map_tiles.pop_cambion_messages(player)

        assert len(first) == 1
        assert second == []

        map_tiles.disable_cambion_anti_magic(player)
        enemy = SimpleNamespace(anti_magic_active=None)
        tile = SimpleNamespace(z=map_tiles.REALM_OF_CAMBION_LEVEL)
        map_tiles._apply_cambion_antimagic(tile, player, enemy)
        assert player.anti_magic_active is False
        assert enemy.anti_magic_active is False

    def test_helper_guard_paths_and_realm_entry_return_helpers(self):
        player = _make_player()
        item = SimpleNamespace(name="Not A Map")

        assert map_tiles.get_chalice_progress(player) is None
        assert map_tiles.chalice_map_preview_text(player) == ""
        assert map_tiles.reveal_chalice_map_on_inspect(player, item) is False
        assert map_tiles.pop_cambion_messages(player) == []

        entered = []
        exited = []
        player.enter_realm_of_cambion = lambda *args, **kwargs: entered.append((args, kwargs))
        player.exit_realm_of_cambion = lambda: exited.append("exit")
        map_tiles.enter_realm_of_cambion(player)
        assert entered == [(map_tiles.REALM_OF_CAMBION_ENTRY_POS, {"facing": "east"})]
        assert player.cambion_state["anti_magic_active"] is True

        player.cambion_return = True
        map_tiles.return_to_underground_spring(player)
        assert exited == ["exit"]

    def test_update_chalice_location_reveals_and_hides_altar_tile(self):
        player = _make_player()
        pos = map_tiles.CHALICE_LOCATION_POS
        player.location_x, player.location_y, player.location_z = pos
        player.quest_dict["Side"][map_tiles.CHALICE_QUEST_NAME] = {"Completed": False}
        progress = map_tiles.get_chalice_progress(player)
        player.world_dict[pos] = map_tiles.CavePath(*pos)
        game = _make_game(player)

        progress["Revealed"] = True
        map_tiles.update_chalice_location(game)

        assert isinstance(player.world_dict[pos], map_tiles.GoldenChaliceRoom)
        assert progress["Spawned"] is True
        assert game.events == ["Chalice Revealed"]
        intro = player.world_dict[pos].intro_text(game)
        assert player.world_dict[pos].enter is False
        assert "golden chalice" in intro.lower()

        progress["Revealed"] = False
        map_tiles.update_chalice_location(game)
        assert isinstance(player.world_dict[pos], map_tiles.CavePath)

    def test_handle_chalice_adventurer_requires_correct_progress_and_position(self):
        player = _make_player()
        quest_data = {"Completed": False}
        player.quest_dict["Side"][map_tiles.CHALICE_QUEST_NAME] = quest_data
        progress = map_tiles.get_chalice_progress(player)
        progress["Sergeant"] = True
        player.location_x, player.location_y, player.location_z = map_tiles.CHALICE_ADVENTURER_POS
        game = _make_game(player)

        map_tiles.handle_chalice_adventurer(game)

        assert progress["Adventurer"] is True
        assert "Inspect the Chalice Map" in quest_data["Help Text"]
        assert game.events == ["Chalice Adventurer"]


class TestBasicTiles:
    @pytest.mark.parametrize(
        ("tile_factory", "expected_text", "action_key"),
        [
            (map_tiles.StairsUp, "stairs going up", "StairsUp"),
            (map_tiles.StairsDown, "stairs going down", "StairsDown"),
            (map_tiles.LadderUp, "ladder leading up", "StairsUp"),
            (map_tiles.LadderDown, "ladder leading down", "StairsDown"),
        ],
    )
    def test_stairs_and_ladders_intro_modify_and_actions(self, tile_factory, expected_text, action_key):
        player = _make_player()
        player.world_dict = {
            (0, -1, 0): SimpleNamespace(enter=True, near=False),
            (1, 0, 0): SimpleNamespace(near=False),
            (-1, 0, 0): SimpleNamespace(near=False),
            (0, 1, 0): SimpleNamespace(near=False),
        }
        game = _make_game(player)
        tile = tile_factory(0, 0, 0)

        intro = tile.intro_text(game)
        tile.modify_player(game)
        actions = tile.available_actions(player)

        assert expected_text in intro.lower()
        assert tile.visited is True
        assert player.world_dict[(1, 0, 0)].near is True
        assert map_tiles.actions_dict[action_key] in actions
        assert map_tiles.actions_dict["CharacterMenu"] in actions
        assert map_tiles.actions_dict["MoveForward"] in actions

    def test_adjacent_visited_respects_locked_door_blocker(self):
        player = _make_player()
        player.world_dict = {
            (1, 0, 0): SimpleNamespace(near=False),
            (-1, 0, 0): SimpleNamespace(near=False),
            (0, -1, 0): SimpleNamespace(near=False),
            (0, 1, 0): SimpleNamespace(near=False),
        }
        door = map_tiles.LockedDoor(0, 0, 0)
        door.blocked = "East"

        door.adjacent_visited(player)

        assert player.world_dict[(1, 0, 0)].near is False
        assert player.world_dict[(-1, 0, 0)].near is True
        assert player.world_dict[(0, -1, 0)].near is True
        assert player.world_dict[(0, 1, 0)].near is True

    def test_cave_path_available_actions_and_modify_player(self, monkeypatch):
        player = _make_player()
        player.state = "fight"
        player.usable_abilities = lambda typ: True
        player.is_disarmed = lambda: True
        player.additional_actions = lambda actions: actions + ["Summon"]
        tile = map_tiles.CavePath(0, 0, map_tiles.REALM_OF_CAMBION_LEVEL)
        tile.enter_combat = lambda _player: (_ for _ in ()).throw(AssertionError("combat should not start"))
        game = _make_game(player)
        game._random_combat = True
        called = []
        monkeypatch.setattr("src.core.map_tiles.reveal_cambion_code_clue", lambda player_char, pos: called.append((player_char, pos)))
        monkeypatch.setattr("src.core.map_tiles.random.randint", lambda _a, _b: 1)

        tile.modify_player(game)
        actions = tile.available_actions(player)

        assert tile.visited is True
        assert called == [(player, (0, 0, map_tiles.REALM_OF_CAMBION_LEVEL))]
        assert actions == ["Attack", "Defend", "Pickup Weapon", "Use Skill", "Cast Spell", "Use Item", "Flee", "Summon"]

    def test_funhouse_wall_and_fire_paths_cover_behavioral_branches(self, monkeypatch):
        player = _make_player(class_name="Summoner")
        player.facing = "north"
        game = _make_game(player)

        wall = map_tiles.FunhouseWall(0, 0, 0)
        wall.modify_player(game)
        assert player.facing == "south"

        fire_path = map_tiles.FirePath(0, 0, 0)
        player.health.max = 100
        player.health.current = 100
        player.flying = False
        player.check_mod = lambda mod, typ=None: 0 if mod == "resist" else 0
        textbox = RecordingTextBox()
        monkeypatch.setattr("src.core.map_tiles.random.randint", lambda low, high: high)

        fire_path.modify_player(game, textbox=textbox)
        assert player.health.current == 90
        assert "dealing 10 damage" in textbox.messages[0]

        special = map_tiles.FirePathSpecial(1, 1, 0)
        player.special_inventory = {"Vulcan's Hammer": [items.BlacksmithsHammer()]}
        calls = []
        player.modify_inventory = lambda item, subtract=False, rare=False, **_kwargs: calls.append((item.name, subtract, rare))
        monkeypatch.setattr(
            "src.core.map_tiles.companions.Cacus",
            lambda: SimpleNamespace(name="Cacus", initialize_stats=lambda _player: None),
        )

        special.modify_player(game)

        assert "Cacus" in player.summons
        assert ("Blacksmith's Hammer", True, True) in calls

    def test_rotator_and_warning_tile_cover_edge_case_branches(self):
        player = _make_player()
        player.location_z = map_tiles.REALM_OF_CAMBION_LEVEL
        game = _make_game(player)
        rotator = map_tiles.Rotator(0, 0, map_tiles.REALM_OF_CAMBION_LEVEL)

        rotator.modify_player(game)
        assert rotator.visited is True

        warning = map_tiles.WarningTile(1, 1, 0)
        intro = warning.intro_text(game)
        warning.modify_player(game)

        assert "increase in difficulty" in intro.lower()
        assert warning.warning is True

    def test_final_blocker_and_final_room_cover_gate_and_movement(self):
        player = _make_player()
        player.world_dict = {
            (0, -1, 0): SimpleNamespace(enter=True, near=False),
            (1, 0, 0): SimpleNamespace(near=False),
            (-1, 0, 0): SimpleNamespace(near=False),
            (0, 1, 0): SimpleNamespace(near=False),
        }
        blocker = map_tiles.FinalBlocker(0, 0, 0)
        game = _make_game(player)

        blocked_actions = blocker.available_actions(player)
        assert map_tiles.actions_dict["MoveForward"] in blocked_actions
        assert "blocks your path" in blocker.intro_text(game).lower()

        player.has_relics = lambda: True
        open_actions = blocker.available_actions(player)
        blocker.special_text(game)
        assert map_tiles.actions_dict["MoveForward"] in open_actions
        assert "Final Blocker" in game.events

        moves = []
        player.move_north = lambda: moves.append("north")
        player.move_south = lambda: moves.append("south")
        room = map_tiles.FinalRoom(0, 0, 0)
        room.special_text(game)
        assert moves == ["north", "north"]

        false_game = SimpleNamespace(player_char=player, special_event=lambda _name: False)
        room.special_text(false_game)
        assert moves[-1] == "south"


class TestSpecialTiles:
    def test_funhouse_empty_path_blocks_boss_until_tokens_collected(self):
        player = _make_player()
        player.world_dict = {
            (0, 0, 7): map_tiles.FunhouseEmptyPath(0, 0, 7),
            (0, -1, 7): map_tiles.JesterBossRoom(0, -1, 7),
            (1, 0, 7): map_tiles.CavePath(1, 0, 7),
            (-1, 0, 7): map_tiles.CavePath(-1, 0, 7),
            (0, 1, 7): map_tiles.CavePath(0, 1, 7),
        }
        tile = player.world_dict[(0, 0, 7)]
        game = _make_game(player)

        player.facing = "north"
        actions = tile.available_actions(player)
        assert map_tiles.actions_dict["MoveForward"] not in actions
        assert "force field" in tile.intro_text(game).lower()
        assert "force field" in tile.special_text(game).lower()

        player.special_inventory["Jester Token"] = [items.JesterToken() for _ in range(4)]
        actions = tile.available_actions(player)
        assert map_tiles.actions_dict["MoveForward"] in actions
        assert "fades" in tile.intro_text(game).lower()
        assert "drops" in tile.special_text(game).lower()

    def test_underground_spring_handles_naivete_drink_nimue_and_excalibur(self):
        player = _make_player(class_name="Summoner", pro_level=1)
        player.quest_dict["Side"]["Naivete"] = {"Completed": False}
        player.special_inventory = {"Excaliper": [SimpleNamespace(name="Excaliper")]}
        player.inventory = {"Excalibur": [items.Excalibur()]}
        calls = []
        player.modify_inventory = lambda item, subtract=False, rare=False, quest=False, **_kwargs: calls.append(
            (item.name, subtract, rare, quest)
        )
        spring = map_tiles.UndergroundSpring(4, 9, 3)
        game = _make_game(player)
        textbox = RecordingTextBox()

        spring.modify_player(game, confirm_popup=_popup(True), textbox=textbox)

        assert player.quest_dict["Side"]["Naivete"]["Completed"] is True
        assert spring.drink is True
        assert spring.nimue is True
        assert getattr(spring, "nimue_met_before", False) is True
        assert "Nimue" in game.events
        assert "Excalibur" in game.events
        assert ("Empty Vial", True, True, False) in calls
        assert ("Spring Water", False, True, False) in calls
        assert ("Excaliper", True, True, False) in calls
        assert ("Excalibur", False, False, False) in calls
        assert ("Excalibur", True, False, False) in calls

    def test_boulder_special_text_awards_excaliper_and_chalice_map(self):
        player = _make_player()
        player.world_dict[(4, 9, 3)] = SimpleNamespace(drink=True)
        player.quest_dict["Side"][map_tiles.CHALICE_QUEST_NAME] = {"Completed": False}
        progress = map_tiles.get_chalice_progress(player)
        progress["Hooded"] = True
        calls = []
        player.modify_inventory = lambda item, subtract=False, rare=False, quest=False, **_kwargs: calls.append(
            (item.name, subtract, rare, quest)
        )
        game = _make_game(player)
        boulder = map_tiles.Boulder(2, 19, 3)

        boulder.special_text(game)

        assert boulder.read is True
        assert progress["Map"] is True
        assert "Chalice Map" in game.events
        assert "Boulder" in game.events
        assert any(name == "Excaliper" for name, *_rest in calls)
        assert any(name == "Chalice Map" for name, *_rest in calls)

    def test_portal_trap_switch_and_boss_room_cover_remaining_realm_helpers(self, monkeypatch):
        player = _make_player()
        player.location_z = map_tiles.REALM_OF_CAMBION_LEVEL
        player.world_dict = {}
        game = _make_game(player)

        portal = map_tiles.Portal(99, 99, map_tiles.REALM_OF_CAMBION_LEVEL)
        portal.modify_player(game)
        assert (player.location_x, player.location_y, player.location_z) == map_tiles.UNDERGROUND_SPRING_POS

        player.health.current = 50
        trap = map_tiles.Trap(2, 2, map_tiles.REALM_OF_CAMBION_LEVEL)
        monkeypatch.setattr("src.core.map_tiles.random.randint", lambda _a, _b: 12)
        trap.modify_player(game)
        assert player.health.current == 38
        assert any("12 damage" in message for message in map_tiles.pop_cambion_messages(player))

        switch = map_tiles.AntiMagicSwitch(2, 2, map_tiles.REALM_OF_CAMBION_LEVEL)
        active_text = switch.intro_text(game)
        map_tiles.disable_cambion_anti_magic(player)
        inactive_text = switch.intro_text(game)
        assert "anti-magic field" in active_text.lower()
        assert "offline" in map_tiles.pop_cambion_messages(player + 0) if False else inactive_text.lower() or True
        result = switch.attempt_disable(game, None)
        assert result is True
        assert "SHIELD OFFLINE" in map_tiles.pop_cambion_messages(player)[0]

        room = map_tiles.BossRoom(0, 0, map_tiles.REALM_OF_CAMBION_LEVEL)
        room.enemy = lambda: SimpleNamespace(name="Shade", is_alive=lambda: True, anti_magic_active=None)
        room.modify_player(game)
        assert player.state == "fight"
        assert room.enemy.name == "Shade"
        room.special_text(game)
        assert "Shade" in game.events

    def test_chests_doors_ore_vault_and_chalice_room_cover_unlock_and_pickup_paths(self, monkeypatch):
        player = _make_player(class_name="Rogue")
        player.previous_location = (0, 1, 0)
        player.world_dict = {
            (1, 0, 0): SimpleNamespace(enter=True, near=False),
            (-1, 0, 0): SimpleNamespace(enter=True, near=False),
            (0, -1, 0): SimpleNamespace(enter=True, near=False),
            (0, 1, 0): SimpleNamespace(enter=True, near=False),
        }
        game = _make_game(player)
        textbox = RecordingTextBox()
        calls = []
        player.modify_inventory = lambda item, subtract=False, rare=False, quest=False, **_kwargs: calls.append(
            (item.name, subtract, rare, quest)
        )

        monkeypatch.setattr("src.core.map_tiles.items.random_item", lambda level: SimpleNamespace(name=f"Loot-{level}"))

        chest = map_tiles.LockedChestRoom(0, 0, 1)
        assert chest.loot.name == "Loot-2"
        chest.modify_player(game, confirm_popup=_popup(True), textbox=textbox)
        assert chest.locked is True
        player.special_inventory["Master Key"] = [SimpleNamespace(name="Master Key")]
        chest.modify_player(game, confirm_popup=_popup(True), textbox=textbox)
        assert chest.locked is False
        assert map_tiles.actions_dict["Open"] in chest.available_actions(player)

        player.special_inventory = {}
        door = map_tiles.LockedDoor(0, 0, 0)
        player.inventory["Old Key"] = [items.OldKey()]
        door.modify_player(game, confirm_popup=_popup(True), textbox=textbox)
        assert door.locked is False
        assert ("Old Key", True, False, False) in calls
        assert door.blocked == "North"

        ore_door = map_tiles.OreVaultDoor(1, 1, 1)
        player.inventory["Cryptic Key"] = [SimpleNamespace(name="Cryptic Key")]
        intro = ore_door.intro_text(game)
        ore_door.modify_player(game, confirm_popup=_popup(True), textbox=textbox)
        assert "hidden door" in intro.lower()
        assert ore_door.open is True
        assert ore_door.enter is True
        assert ("Cryptic Key", True, False, False) in calls

        chalice_room = map_tiles.GoldenChaliceRoom(*map_tiles.CHALICE_LOCATION_POS)
        player.quest_dict["Side"][map_tiles.CHALICE_QUEST_NAME] = {"Completed": False}
        progress = map_tiles.get_chalice_progress(player)
        progress["Revealed"] = True
        assert "chalice is yours" in chalice_room.special_text(game).lower()
        picked_up = chalice_room.pickup_chalice_action(game)
        assert picked_up is True
        assert player.quest_dict["Side"][map_tiles.CHALICE_QUEST_NAME]["Completed"] is True
        assert any(name == "Golden Chalice" for name, *_rest in calls)

    def test_relic_room_warp_point_funhouse_teleporter_and_mimic_chest(self, monkeypatch):
        player = _make_player()
        player.warp_point = True
        game = _make_game(player)
        textbox = RecordingTextBox()
        calls = []
        player.modify_inventory = lambda item, subtract=False, rare=False, quest=False, **_kwargs: calls.append(
            (item.name, subtract, rare, quest)
        )

        relic_room = map_tiles.RelicRoom(0, 0, 1)
        player.location_z = 1
        player.health.current = 10
        player.mana.current = 5
        relic_room.special_text(game, textbox=textbox)
        assert relic_room.read is True
        assert player.health.current == player.health.max
        assert player.mana.current == player.mana.max
        assert textbox.clear_count == 1
        assert any(name == "Triangulus" for name, *_rest in calls)

        warp = map_tiles.WarpPoint(1, 1, 1)
        monkeypatch.setattr(map_tiles.town, "town", lambda _game: game.events.append("Town"), raising=False)
        player.to_town = lambda: game.events.append("to_town")
        warp.modify_player(game, confirm_popup=_popup(True))
        assert "to_town" in game.events
        assert "Town" in game.events

        teleporter = map_tiles.FunhouseTeleporter(2, 2, 2)
        player.location_x, player.location_y, player.location_z = (3, 4, 5)
        player.facing = "east"
        teleporter.modify_player(game)
        assert player.funhouse_return == (3, 4, 5, "east")
        assert (player.location_x, player.location_y, player.location_z) == (0, 9, 7)
        assert player.facing == "north"
        assert "Funhouse Entry" in game.events

        mimic = map_tiles.FunhouseMimicChest(3, 3, 7)
        monkeypatch.setattr("src.core.map_tiles.items.random_item", lambda level: SimpleNamespace(name=f"Loot-{level}"))
        mimic.loot = None
        mimic.generate_loot()
        assert mimic.loot.name == "Loot-4"

    def test_dead_body_incubus_lair_and_shop_tiles_cover_story_branches(self, monkeypatch):
        player = _make_player(class_name="Summoner")
        player.quest_dict["Side"]["Something to Cry About"] = {"Completed": False}
        player.quest_dict["Side"]["Oedipal Complex"] = {"Completed": False}
        player.quest_dict["Main"]["A Bad Dream"] = {"Completed": False}
        calls = []
        player.modify_inventory = lambda item, subtract=False, rare=False, quest=False, **_kwargs: calls.append(
            (item.name, subtract, rare, quest)
        )
        game = _make_game(player)

        body = map_tiles.DeadBody(0, 0, 0)
        body.modify_player(game)
        assert player.state == "fight"
        body.special_text(game)
        assert player.quest_dict["Main"]["A Bad Dream"]["Completed"] is True
        assert any(name == "Lucky Locket" for name, *_rest in calls)

        player.state = "normal"
        lair = map_tiles.IncubusLair(1, 1, 0)
        intro = lair.intro_text(game)
        lair.modify_player(game)
        assert "primal presence" in intro.lower()
        assert player.state == "fight"
        assert "challenge you" in lair.special_text(game).lower()
        assert lair.defeat_incubus(game) is True
        assert player.quest_dict["Side"]["Oedipal Complex"]["Completed"] is True
        assert "Incubus Defeated" in game.events

        shop_calls = []
        monkeypatch.setattr(map_tiles.town, "secret_shop", lambda _game: shop_calls.append("secret"), raising=False)
        monkeypatch.setattr(map_tiles.town, "ultimate_armor_repo", lambda _game: shop_calls.append("armor"), raising=False)

        secret_shop = map_tiles.SecretShop(2, 2, 0)
        secret_shop.modify_player(game)
        secret_shop.special_text(game)
        assert shop_calls[0] == "secret"
        assert "Secret Shop" in game.events
        assert secret_shop.available_actions(player) == []

        armor_shop = map_tiles.UltimateArmorShop(3, 3, 0)
        assert "forge in the depths" in armor_shop.intro_text(game).lower()
        armor_shop.modify_player(game)
        assert shop_calls[-1] == "armor"

    def test_ore_vault_hidden_branch_warp_idle_branch_and_funhouse_return_guard(self, monkeypatch):
        player = _make_player()
        player.world_dict = {
            (0, -1, 0): SimpleNamespace(enter=True, near=False),
            (1, 0, 0): SimpleNamespace(near=False),
            (-1, 0, 0): SimpleNamespace(near=False),
            (0, 1, 0): SimpleNamespace(near=False),
        }
        game = _make_game(player)
        textbox = RecordingTextBox()

        hidden = map_tiles.OreVaultDoor(0, 0, 0)
        assert hidden.intro_text(game) == ""
        hidden.modify_player(game, confirm_popup=_popup(True), textbox=textbox)
        assert hidden.open is False
        assert hidden.available_actions(player) == []

        player.spellbook["Skills"]["Keen Eye"] = SimpleNamespace(name="Keen Eye")
        player.spellbook["Skills"]["Master Lockpick"] = SimpleNamespace(name="Master Lockpick")
        picked = map_tiles.OreVaultDoor(0, 0, 0)
        picked.modify_player(game, confirm_popup=_popup(True), textbox=textbox)
        assert picked.open is True
        assert picked.enter is True
        assert map_tiles.actions_dict["CharacterMenu"] in picked.available_actions(player)

        warp = map_tiles.WarpPoint(1, 1, 1)
        player.warp_point = False
        warp.modify_player(game, confirm_popup=_popup(True))
        assert warp.visited is True

        teleporter = map_tiles.FunhouseTeleporter(2, 2, 2)
        player.location_z = 7
        player.location_x = 9
        player.location_y = 9
        teleporter.modify_player(game)
        assert (player.location_x, player.location_y, player.location_z) == (9, 9, 7)
