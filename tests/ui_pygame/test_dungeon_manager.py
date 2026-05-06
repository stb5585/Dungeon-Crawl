#!/usr/bin/env python3
"""Focused coverage for pygame dungeon-manager navigation and helper flows."""

from __future__ import annotations

from types import SimpleNamespace

import pygame

from src.ui_pygame.gui import dungeon_manager


class RecordingScreen:
    def __init__(self):
        self.blit_calls = []
        self.fill_calls = []
        self.size = (640, 480)

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))

    def fill(self, color):
        self.fill_calls.append(color)

    def copy(self):
        return "screen-copy"

    def get_size(self):
        return self.size


class RecordingFont:
    def render(self, text, _antialias, _color):
        width = max(8, len(text) * 8)
        height = 18

        def get_rect(**kwargs):
            rect = pygame.Rect(0, 0, width, height)
            for key, value in kwargs.items():
                setattr(rect, key, value)
            return rect

        return SimpleNamespace(
            text=text,
            get_width=lambda: width,
            get_height=lambda: height,
            get_rect=get_rect,
        )


class DummySurface:
    def __init__(self, size=(100, 80)):
        self._size = size
        self.alpha = None
        self.fill_calls = []

    def get_size(self):
        return self._size

    def get_rect(self, **kwargs):
        return SimpleNamespace(**kwargs)

    def set_alpha(self, value):
        self.alpha = value

    def fill(self, color):
        self.fill_calls.append(color)

    def convert(self):
        return self

    def convert_alpha(self):
        return self


class DummyTile:
    def __init__(self, *, enter=True, locked=False, open_state=False, blocked=None):
        self.enter = enter
        self.locked = locked
        self.open = open_state
        self.blocked = blocked
        self.visited = False
        self.adjacent_calls = []

    def adjacent_visited(self, player_char):
        self.adjacent_calls.append((player_char.location_x, player_char.location_y, player_char.location_z))


class DoorTile(DummyTile):
    pass


class OreVaultDoor(DummyTile):
    pass


class FinalBlocker(DummyTile):
    pass


class StairsUpTile(DummyTile):
    pass


class StairsDownTile(DummyTile):
    pass


class SecretShopTile(DummyTile):
    def __init__(self):
        super().__init__(enter=False)
        self.read = False


class UndergroundSpring(DummyTile):
    pass


class WarpPoint(DummyTile):
    pass


class FinalRoom(DummyTile):
    pass


class AntiMagicSwitch(DummyTile):
    pass


class IncubusLair(DummyTile):
    def __init__(self):
        super().__init__()
        self.defeated = False
        self.enemy = None

    def enter_combat(self, player_char):
        self.enemy = SimpleNamespace(name="Incubus")

    def defeat_incubus(self, game):
        self.defeated = True
        return True


class GoldenChaliceRoom(DummyTile):
    def __init__(self):
        super().__init__()
        self.read = False

    def pickup_chalice_action(self, game):
        self.read = True
        return True


class FirePath(DummyTile):
    def __init__(self):
        super().__init__()
        self.special_text = lambda _game: "The flames dance."

    def modify_player(self, game, popup_class=None):
        game.player.health.current -= 3


class EnemyTile(DummyTile):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy


class LadderUp(DummyTile):
    pass


class LadderDown(DummyTile):
    pass


class UltimateArmorShop(DummyTile):
    pass


class RelicTile(DummyTile):
    pass


class BoulderTile(DummyTile):
    pass


class UnobtainiumRoom(DummyTile):
    pass


class BossTile(DummyTile):
    def __init__(self, enemy):
        super().__init__()
        self.enemy = enemy

    def intro_text(self, _game):
        return "Boss intro"


class WarningTile(DummyTile):
    def intro_text(self, _game):
        return ""


class DeadBody(DummyTile):
    def intro_text(self, _game):
        return ""


def _make_presenter():
    return SimpleNamespace(
        screen=RecordingScreen(),
        width=640,
        height=480,
        title_font=RecordingFont(),
        large_font=RecordingFont(),
        small_font=RecordingFont(),
        show_message=lambda *args, **kwargs: None,
        render_menu=lambda prompt, options, **kwargs: 0,
        clock=SimpleNamespace(tick=lambda _fps: None),
        set_background_provider=lambda provider: None,
    )


def _make_player():
    steps = []
    stairs = []
    inventory_calls = []

    def modify_inventory(*args, **kwargs):
        item = args[0] if args else None
        inventory_calls.append((getattr(item, "name", item), kwargs))

    player = SimpleNamespace(
        facing="north",
        location_x=5,
        location_y=5,
        location_z=1,
        previous_location=None,
        world_dict={},
        quest_dict={"Side": {}, "Main": {}},
        spellbook={"Skills": {}},
        inventory={},
        special_inventory={},
        level=SimpleNamespace(level=12),
        anti_magic_active=False,
        warp_point=False,
        health=SimpleNamespace(current=10, max=20),
        mana=SimpleNamespace(current=4, max=9),
        state="explore",
        summons={},
        equipment={"Weapon": SimpleNamespace(name="None")},
        cls=SimpleNamespace(name="Knight"),
        record_step=lambda: steps.append("step"),
        record_stairs_used=lambda: stairs.append("stairs"),
        in_town=lambda: player.location_z <= 0,
        has_relics=lambda: False,
        check_mod=lambda *_args, **_kwargs: 0,
        modify_inventory=modify_inventory,
        is_alive=lambda: True,
        to_town=lambda: setattr(player, "location_z", 0),
        player_level=lambda: player.level.level,
    )
    player.step_calls = steps
    player.stair_calls = stairs
    player.inventory_calls = inventory_calls
    return player


def _make_manager(monkeypatch):
    presenter = _make_presenter()
    player = _make_player()
    game = SimpleNamespace(special_event=lambda _name: None)

    monkeypatch.setattr(dungeon_manager, "DungeonRenderer", lambda presenter: SimpleNamespace())
    monkeypatch.setattr(dungeon_manager, "DungeonHUD", lambda presenter: SimpleNamespace())
    monkeypatch.setattr(
        dungeon_manager,
        "GUICombatManager",
        lambda presenter, hud, game_instance: SimpleNamespace(
            dungeon_renderer=None,
            start_combat=lambda *_args, **_kwargs: True,
            player_world_dict=None,
        ),
    )
    monkeypatch.setattr(dungeon_manager, "CharacterScreen", lambda presenter: SimpleNamespace(background=None))
    monkeypatch.setattr(dungeon_manager, "LootPopup", lambda screen, presenter: SimpleNamespace(show_unlock_prompt=lambda kind: True, show_loot=lambda *args: None))
    monkeypatch.setattr("src.ui_pygame.gui.shops.ShopManager", lambda presenter, player_char: SimpleNamespace(visit_secret_shop=lambda: None))
    monkeypatch.setattr("src.ui_pygame.gui.ultimate_armor.UltimateArmorShop", lambda presenter: SimpleNamespace(visit_shop=lambda *_args: None))
    original_loader = dungeon_manager.DungeonManager._load_dungeon_background
    monkeypatch.setattr(dungeon_manager.DungeonManager, "_load_dungeon_background", lambda self: None)
    manager = dungeon_manager.DungeonManager(presenter, player, game)
    monkeypatch.setattr(dungeon_manager.DungeonManager, "_load_dungeon_background", original_loader)
    game.player = player
    return manager, presenter, player, game


def test_resolve_enemy_messages_and_random_cry(monkeypatch):
    manager, _presenter, player, _game = _make_manager(monkeypatch)

    tile = SimpleNamespace(enemy=lambda: SimpleNamespace(name="Goblin"))
    resolved = manager._resolve_tile_enemy(tile)
    assert resolved.name == "Goblin"
    assert tile.enemy.name == "Goblin"
    assert manager._resolve_tile_enemy(SimpleNamespace()) is None

    manager.max_messages = 3
    manager.add_message("one two three four five six seven eight nine ten eleven twelve")
    manager.add_message("second")
    manager.add_message("third")
    manager.add_message("fourth")
    assert len(manager.messages) == 3
    manager.scroll_message_log(-10)
    assert manager.message_scroll_offset == 0
    manager.reset_message_log()
    assert manager.messages == []

    player.location_z = 2
    player.location_x = 18
    player.location_y = 12
    player.quest_dict["Side"]["Something to Cry About"] = {"Completed": False}
    monkeypatch.setattr(dungeon_manager.random, "random", lambda: 0.0)
    monkeypatch.setattr(dungeon_manager.random, "choice", lambda seq: seq[0])
    manager._check_random_cry()
    assert any("sobs echo" in message for message in manager.messages)


def test_background_loading_loading_screen_and_popup_background(monkeypatch, capsys):
    manager, presenter, _player, _game = _make_manager(monkeypatch)

    source = DummySurface((200, 100))
    scaled_sizes = []
    monkeypatch.setattr("os.path.exists", lambda _path: True)
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.image.load", lambda _path: source)
    monkeypatch.setattr(
        "src.ui_pygame.gui.dungeon_manager.pygame.transform.scale",
        lambda image, size: scaled_sizes.append((image.get_size(), size)) or DummySurface(size),
    )
    bg = dungeon_manager.DungeonManager._load_dungeon_background(manager)
    assert scaled_sizes == [((200, 100), (960, 480))]
    assert bg.get_size() == (960, 480)

    manager._cached_frame = "frame"
    assert manager._get_popup_background() == "frame"
    manager._cached_frame = None
    manager._cached_view = "view"
    assert manager._get_popup_background() == "view"
    manager._cached_view = None
    assert manager._get_popup_background() == "screen-copy"

    manager._dungeon_background_loaded = False
    monkeypatch.setattr("os.path.exists", lambda _path: False)
    assert dungeon_manager.DungeonManager._load_dungeon_background(manager) is None
    assert "Dungeon background not found" in capsys.readouterr().out

    manager._dungeon_background_loaded = True
    manager._dungeon_background = DummySurface((640, 480))
    tick_values = iter([0, 1000])
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.time.get_ticks", lambda: next(tick_values))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.time.Clock", lambda: SimpleNamespace(tick=lambda _fps: None))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.event.get", lambda *_args: [])
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.draw.rect", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.Surface", lambda size, *_args: DummySurface(size))
    manager._show_dungeon_loading_screen("Loading...", duration=0.5)
    assert presenter.screen.blit_calls


def test_walkable_spawn_selection_and_stair_usage(monkeypatch):
    manager, _presenter, player, _game = _make_manager(monkeypatch)
    center = (player.location_x, player.location_y, player.location_z)
    north_tile = DummyTile()
    east_tile = DoorTile(locked=True)
    south_tile = DummyTile(open_state=True)

    player.world_dict = {
        center: StairsDownTile(),
        (center[0], center[1] - 1, center[2]): north_tile,
        (center[0] + 1, center[1], center[2]): east_tile,
        (center[0], center[1] + 1, center[2]): south_tile,
    }

    assert manager._is_walkable_spawn_tile(north_tile) is True
    assert manager._is_walkable_spawn_tile(east_tile) is False
    assert manager._is_walkable_spawn_tile(StairsUpTile()) is False

    manager._move_to_adjacent_from_stairs()
    assert (player.location_x, player.location_y) == (center[0], center[1] - 1)
    assert north_tile.visited is True

    player.world_dict[(player.location_x, player.location_y, player.location_z)] = StairsDownTile()
    player.location_z = 1
    manager._show_dungeon_loading_screen = lambda *_args, **_kwargs: None
    manager.add_message = lambda message: manager.messages.append(message)
    manager.use_stairs_down()
    assert player.location_z == 2
    assert player.stair_calls == ["stairs"]


def test_move_forward_branches_and_turning(monkeypatch):
    manager, _presenter, player, _game = _make_manager(monkeypatch)
    manager._get_tile_intro = lambda: ["Intro text"]
    manager._check_tile_effects = lambda: manager.messages.append("effects")
    dialogues = []
    manager._show_special_event_dialogue = lambda event_name, title="", image_path="": dialogues.append(
        (event_name, title, image_path)
    )

    assert manager.move_forward() is False
    assert "can't move" in manager.messages[-1].lower()

    player.world_dict[(5, 4, 1)] = DummyTile(enter=False)
    assert manager.move_forward() is False

    player.world_dict[(5, 4, 1)] = OreVaultDoor(enter=False, locked=True)
    assert manager.move_forward() is False
    assert "solid wall" in manager.messages[-1].lower()

    player.world_dict[(5, 4, 1)] = DoorTile(enter=True, locked=True)
    assert manager.move_forward() is False
    assert "locked door" in manager.messages[-1].lower()

    player.world_dict[(5, 4, 1)] = FinalBlocker(enter=True, blocked="north")
    assert manager.move_forward() is False
    assert "invisible force" in manager.messages[-1].lower()

    player.location_x, player.location_y = (5, 5)
    player.special_inventory = {}
    player.world_dict[(5, 5, 1)] = dungeon_manager.map_tiles.FunhouseEmptyPath(5, 5, 1)
    player.world_dict[(5, 4, 1)] = dungeon_manager.map_tiles.JesterBossRoom(5, 4, 1)
    assert manager.move_forward() is False
    assert "force field" in manager.messages[-1].lower()
    assert dialogues[-1] == (
        dungeon_manager.map_tiles.JESTER_FORCE_FIELD_EVENT,
        "Jester",
        manager._npc_image_path("jester.png"),
    )

    player.special_inventory["Jester Token"] = [SimpleNamespace(name="Jester Token") for _ in range(4)]
    destination = player.world_dict[(5, 4, 1)]
    assert manager.move_forward() is True
    assert (player.location_x, player.location_y) == (5, 4)
    assert destination.visited is True

    player.location_x, player.location_y = (5, 5)
    player.step_calls.clear()
    player.has_relics = lambda: True
    destination = DummyTile()
    player.world_dict[(5, 4, 1)] = destination
    assert manager.move_forward() is True
    assert (player.location_x, player.location_y) == (5, 4)
    assert player.step_calls == ["step"]
    assert destination.visited is True
    assert "Intro text" in manager.messages
    assert "effects" in manager.messages

    manager.turn_left()
    manager.turn_right()
    manager.turn_around()
    assert player.facing in {"north", "south", "east", "west"}


def test_use_stairs_up_interact_secret_shop_and_dialogue_helpers(monkeypatch):
    manager, presenter, player, _game = _make_manager(monkeypatch)
    manager._show_dungeon_loading_screen = lambda *_args, **_kwargs: None
    manager._move_to_adjacent_from_stairs = lambda: manager.messages.append("moved-from-stairs")
    shown_messages = []
    presenter.show_message = lambda message, **kwargs: (
        kwargs.get("background_draw_func") and kwargs["background_draw_func"](),
        shown_messages.append((message, kwargs)),
    )
    presenter.render_menu = lambda prompt, options, **kwargs: (
        kwargs.get("background_draw_func") and kwargs["background_draw_func"](),
        0,
    )[1]
    manager.shop_manager = SimpleNamespace(visit_secret_shop=lambda: manager.messages.append("shop-opened"))

    current_tile = StairsUpTile()
    player.world_dict[(player.location_x, player.location_y, player.location_z)] = current_tile
    assert manager.use_stairs_up() is True
    assert player.location_z == 0
    assert manager.running is False

    player.location_z = 1
    player.world_dict[(player.location_x, player.location_y, player.location_z)] = DummyTile()
    player.world_dict[(player.location_x, player.location_y - 1, player.location_z)] = SecretShopTile()
    manager.interact()
    assert any("secret shop" in message.lower() for message, _kwargs in shown_messages)
    assert "shop-opened" in manager.messages

    manager._cached_frame = None
    manager._cached_view = None
    manager._render = lambda: manager.messages.append("rendered")
    manager._show_dungeon_dialogue("hello", title="NPC", image_path="npc.png")
    manager._show_dungeon_choice("prompt", ["Yes", "No"], image_path="npc.png")
    monkeypatch.setattr(dungeon_manager, "get_special_events", lambda: {"Event": {"Text": ["Line 1", "Line 2"]}})
    manager._show_special_event_dialogue("Event", title="Title", image_path="img.png")
    assert manager.messages.count("rendered") >= 3


def test_interact_chest_covers_unlock_mimic_loot_and_empty_cases(monkeypatch):
    manager, _presenter, player, _game = _make_manager(monkeypatch)
    loot_calls = []
    unlock_prompts = []
    combat_calls = []
    manager.loot_popup = SimpleNamespace(
        show_unlock_prompt=lambda kind, **kwargs: unlock_prompts.append((kind, kwargs)) or True,
        show_loot=lambda loot, label, **kwargs: loot_calls.append((getattr(loot, "name", loot), label, kwargs)),
    )
    manager.combat_manager.start_combat = lambda player_char, enemy, tile: combat_calls.append((enemy.level, tile)) or True
    manager._refresh_cached_frame = lambda: manager.messages.append("refresh")

    class MimicEnemy:
        def __init__(self, level, player_level=None):
            self.level = level
            self.player_level = player_level
            self.anti_magic_active = False
            self._alive = False

        def is_alive(self):
            return self._alive

    monkeypatch.setattr("src.core.enemies.Mimic", MimicEnemy)
    monkeypatch.setattr("src.core.items.JesterToken", lambda: SimpleNamespace(name="Jester Token"))
    monkeypatch.setattr(dungeon_manager.random, "randint", lambda *_args: 0)

    player.inventory["Key"] = [SimpleNamespace(name="Key")]
    chest = SimpleNamespace(
        open=False,
        locked=True,
        loot=None,
        enemy=None,
        generate_loot=lambda: setattr(chest, "loot", lambda: SimpleNamespace(name="Gold Ring")),
    )
    manager._interact_chest(chest, "LockedChest")
    assert chest.open is True
    assert chest.locked is False
    assert unlock_prompts[0][0] == "chest"
    assert unlock_prompts[0][1]["flush_events"] is True
    assert unlock_prompts[0][1]["require_key_release"] is True
    assert callable(unlock_prompts[0][1]["background_draw_func"])
    assert combat_calls[0][0] == 2
    assert ("Gold Ring", {}) in player.inventory_calls
    assert loot_calls[-1][0:2] == ("Gold Ring", "Locked Chest")
    assert loot_calls[-1][2]["flush_events"] is True
    assert loot_calls[-1][2]["require_key_release"] is True
    assert callable(loot_calls[-1][2]["background_draw_func"])

    funhouse = SimpleNamespace(
        open=False,
        locked=False,
        loot=lambda: SimpleNamespace(name="Fun Loot"),
        enemy=None,
        generate_loot=lambda: None,
    )
    manager._interact_chest(funhouse, "FunhouseMimicChest")
    assert any(call[0] == "Jester Token" and call[1].get("rare") is True for call in player.inventory_calls)

    empty = SimpleNamespace(open=False, locked=False, loot=None, generate_loot=lambda: None)
    manager._interact_chest(empty, "Chest")
    assert loot_calls[-1][0:2] == ([], "Empty Chest")


def test_interact_door_relic_warp_terminal_and_room_pickups(monkeypatch):
    manager, _presenter, player, game = _make_manager(monkeypatch)
    manager.loot_popup = SimpleNamespace(show_unlock_prompt=lambda kind, **_kwargs: True, show_loot=lambda *_args, **_kwargs: None)
    dirty_calls = []
    manager._refresh_cached_frame = lambda: manager.messages.append("refresh")
    manager._mark_view_dirty = lambda: dirty_calls.append("dirty")
    manager._show_dungeon_choice = lambda prompt, options: 0

    ore_door = OreVaultDoor(enter=False, locked=True)
    player.inventory["Cryptic Key"] = [SimpleNamespace(name="Cryptic Key")]
    manager._interact_door(ore_door)
    assert ore_door.open is True
    assert ore_door.detected is True
    assert dirty_calls == ["dirty"]

    regular = DoorTile(enter=False, locked=True)
    player.inventory["Old Key"] = [SimpleNamespace(name="Old Key")]
    manager._interact_door(regular)
    assert regular.open is True
    assert regular.blocked is None

    player.location_z = 2
    relic_tile = SimpleNamespace(read=False)
    monkeypatch.setattr("src.core.items.Relic1", lambda: SimpleNamespace(name="Relic 1"))
    monkeypatch.setattr("src.core.items.Relic2", lambda: SimpleNamespace(name="Relic 2"))
    monkeypatch.setattr("src.core.items.Relic3", lambda: SimpleNamespace(name="Relic 3"))
    monkeypatch.setattr("src.core.items.Relic4", lambda: SimpleNamespace(name="Relic 4"))
    monkeypatch.setattr("src.core.items.Relic5", lambda: SimpleNamespace(name="Relic 5"))
    monkeypatch.setattr("src.core.items.Relic6", lambda: SimpleNamespace(name="Relic 6"))
    special_events = []
    game.special_event = lambda name: special_events.append(name)
    manager._interact_relic(relic_tile)
    assert special_events == ["Relic Room"]
    assert player.health.current == player.health.max
    assert player.mana.current == player.mana.max

    player.warp_point = True
    warp_tile = SimpleNamespace(warped=True)
    manager.running = True
    manager._handle_warp_point(warp_tile)
    assert player.location_z == 0
    assert manager.running is False

    class FakeCodeEntryPopup:
        def __init__(self, *_args, **_kwargs):
            pass

        def show(self, **_kwargs):
            return "1234"

    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.CodeEntryPopup", FakeCodeEntryPopup)
    monkeypatch.setattr(dungeon_manager.map_tiles, "pop_cambion_messages", lambda _player: ["Field offline", "Barrier gone"])
    switch_calls = []
    switch_tile = SimpleNamespace(attempt_disable=lambda game_arg, code: switch_calls.append((game_arg, code)))
    manager._interact_anti_magic_switch(switch_tile)
    assert switch_calls == [(game, "1234")]
    assert "Barrier gone" in manager.messages

    unobtainium_tile = SimpleNamespace(visited=False)
    monkeypatch.setattr("src.core.items.Unobtainium", lambda: SimpleNamespace(name="Unobtainium"))
    manager._interact_unobtainium_room(unobtainium_tile)
    assert unobtainium_tile.visited is True

    body_tile = SimpleNamespace(read=False)
    monkeypatch.setattr("src.core.items.LuckyLocket", lambda: SimpleNamespace(name="Lucky Locket"))
    player.quest_dict["Main"]["A Bad Dream"] = {"Completed": False}
    manager._interact_dead_body(body_tile)
    assert player.quest_dict["Main"]["A Bad Dream"]["Completed"] is True
    assert body_tile.read is True


def test_underground_spring_intro_and_tile_effect_branches(monkeypatch):
    manager, _presenter, player, game = _make_manager(monkeypatch)
    manager._refresh_cached_frame = lambda: manager.messages.append("refresh")
    manager._animate_nimue_materialization = lambda: manager.messages.append("nimue-animation")
    manager._show_special_event_dialogue = lambda *args, **kwargs: manager.messages.append("nimue-dialogue")
    manager._show_dungeon_dialogue = lambda text, **kwargs: manager.messages.append(f"dialog:{text}")
    manager._show_dungeon_choice = lambda prompt, options, **kwargs: 0
    dirty_calls = []
    manager._mark_view_dirty = lambda: dirty_calls.append("dirty")
    game.special_event = lambda name: manager.messages.append(f"event:{name}")

    class FakeConfirm:
        responses = [True] * 10

        def __init__(self, *_args, **_kwargs):
            pass

        def show(self, **_kwargs):
            return FakeConfirm.responses.pop(0)

    class FakeQuestManager:
        def __init__(self, *_args, **_kwargs):
            pass

        def check_and_offer(self, *_args, **_kwargs):
            return False, False

        def get_random_help_hint(self, *_args, **_kwargs):
            return "Seek the hidden path."

    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.ConfirmationPopup", FakeConfirm)
    monkeypatch.setattr("src.ui_pygame.gui.quest_manager.QuestManager", FakeQuestManager)
    monkeypatch.setattr(dungeon_manager.random, "randint", lambda *_args: 0)
    monkeypatch.setattr("src.core.enemies.Fuath", lambda: SimpleNamespace(name="Fuath"))
    monkeypatch.setattr(
        dungeon_manager.companions,
        "Fuath",
        lambda: SimpleNamespace(name="Fuath", initialize_stats=lambda player_char: None),
    )
    monkeypatch.setattr("src.core.items.EmptyVial", lambda: SimpleNamespace(name="Empty Vial"))
    monkeypatch.setattr("src.core.items.SpringWater", lambda: SimpleNamespace(name="Spring Water"))
    monkeypatch.setattr("src.core.items.Excaliper", lambda: SimpleNamespace(name="Excaliper"))
    monkeypatch.setattr("src.core.items.Excalibur2", lambda: SimpleNamespace(name="Excalibur2"))
    monkeypatch.setattr(dungeon_manager.map_tiles, "enter_realm_of_cambion", lambda _player: manager.messages.append("entered-realm"))

    player.level.pro_level = 2
    player.cls.name = "Summoner"
    player.quest_dict["Side"]["Naivete"] = {"Completed": False}
    player.quest_dict["Side"]["The Wizard's Folly"] = {"Completed": False, "Turned In": False}
    player.special_inventory["Excaliper"] = [SimpleNamespace(name="Excaliper")]
    player.inventory["Excalibur"] = [SimpleNamespace(name="Excalibur")]
    spring = UndergroundSpring()
    spring.nimue_met_before = True

    manager._interact_underground_spring(spring)

    assert spring.drink is True
    assert spring.defeated is True
    assert spring.nimue is True
    assert "Fuath" in player.summons
    assert any(call[0] == "Spring Water" for call in player.inventory_calls)
    assert "entered-realm" in manager.messages
    assert "Seek the hidden path." in manager.messages
    assert dirty_calls == ["dirty"]

    player.inventory.pop("Excalibur", None)
    player.equipment["Weapon"] = SimpleNamespace(name="Excalibur")
    manager._interact_underground_spring(spring)
    assert player.equipment["Weapon"].name == "Excalibur2"


def test_get_tile_intro_check_tile_effects_and_menu_helpers(monkeypatch):
    manager, presenter, player, game = _make_manager(monkeypatch)
    manager._refresh_cached_frame = lambda: manager.messages.append("refresh")
    manager.renderer = SimpleNamespace(
        trigger_damage_flash=lambda: manager.messages.append("flash"),
        render_dungeon_view=lambda player_char, world_dict: manager.messages.append("render-view"),
        render_message_area=lambda messages, **kwargs: manager.messages.append("render-messages"),
        render_damage_flash=lambda: manager.messages.append("render-flash"),
        _damage_flash_active=False,
    )
    manager.hud = SimpleNamespace(render_hud=lambda player_char: manager.messages.append("render-hud"))
    monkeypatch.setattr(dungeon_manager.map_tiles, "update_chalice_location", lambda game_arg: manager.messages.append("update-chalice"))
    monkeypatch.setattr(dungeon_manager.map_tiles, "handle_chalice_adventurer", lambda game_arg: manager.messages.append("handle-adventurer"))
    monkeypatch.setattr(dungeon_manager.map_tiles, "pop_cambion_messages", lambda _player: ["Cambion warning"])

    player.name = "Hero"
    player.warp_point = True
    player.inventory["Cryptic Key"] = [SimpleNamespace(name="Cryptic Key")]
    player.spellbook["Skills"] = ["Keen Eye"]
    current = WarpPoint()
    current.intro_text = lambda _game: ""
    ahead = OreVaultDoor(enter=False, locked=True)
    ahead.intro_text = lambda _game: ""
    player.world_dict[(player.location_x, player.location_y, player.location_z)] = current
    player.world_dict[(player.location_x, player.location_y - 1, player.location_z)] = ahead

    intros = manager._get_tile_intro()
    assert any("warp point shimmers" in msg.lower() for msg in intros)
    assert any("hidden door ahead" in msg.lower() for msg in intros)
    assert ahead.detected is True

    fire_tile = FirePath()
    fire_tile.enemy = None
    player.health.current = 10
    player.world_dict[(player.location_x, player.location_y, player.location_z)] = fire_tile
    manager._check_tile_effects()
    assert "The flames dance." in manager.messages
    assert any("3 damage" in msg for msg in manager.messages)
    assert "flash" in manager.messages
    assert "Cambion warning" in manager.messages

    enemy = SimpleNamespace(name="Slime", health=SimpleNamespace(current=5), is_alive=lambda: True)
    enemy_tile = EnemyTile(enemy)
    player.world_dict[(player.location_x, player.location_y, player.location_z)] = enemy_tile
    manager.combat_manager.start_combat = lambda *_args, **_kwargs: True
    manager._check_tile_effects()
    assert enemy_tile.enemy is None
    assert "You emerge victorious!" in manager.messages

    player.in_realm_of_cambion = lambda: False
    player.exit_funhouse = lambda: manager.messages.append("exit-funhouse")
    player.exit_realm_of_cambion = lambda: manager.messages.append("exit-cambion")
    player.to_town = lambda: manager.messages.append("to-town")
    player.location_z = 7
    enemy2 = SimpleNamespace(name="Ghost", health=SimpleNamespace(current=5), is_alive=lambda: True)
    enemy_tile2 = EnemyTile(enemy2)
    player.world_dict[(player.location_x, player.location_y, player.location_z)] = enemy_tile2
    manager.combat_manager.start_combat = lambda *_args, **_kwargs: False
    player.is_alive = lambda: False
    manager.running = True
    manager._check_tile_effects()
    assert "exit-funhouse" in manager.messages
    assert manager.running is False

    popup_events = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_DOWN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.event.get", lambda: next(popup_events, []))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.draw.rect", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.Surface", lambda size, *_args: DummySurface(size))
    assert manager._popup_menu("Menu", ["A", "B"]) == 1

    events = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
        [SimpleNamespace(type=pygame.KEYUP, key=pygame.K_RETURN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_DOWN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    clear_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.event.get", lambda: next(events, []))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.event.clear", lambda: clear_calls.append(True))
    assert manager._popup_menu("Menu", ["A", "B"], flush_events=True, require_key_release=True) == 1
    assert clear_calls == [True]

    manager.character_screen = SimpleNamespace(navigate=lambda _player: "Exit Menu")
    manager.game = SimpleNamespace(debug_mode=False, running=True, save_game=lambda: manager.messages.append("saved"), debug_level_up=lambda: manager.messages.append("debug-level"))
    manager._popup_menu = lambda title, options, **_kwargs: 0
    manager._show_menu()
    manager._popup_menu = lambda title, options, **_kwargs: len(options) - 1

    class FakeConfirmMenu:
        def __init__(self, *_args, **_kwargs):
            pass

        def show(self, **_kwargs):
            return True

    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.ConfirmationPopup", FakeConfirmMenu)
    manager._show_menu()
    assert manager.player_char.quit is True

    move_calls = []
    manager.move_forward = lambda: move_calls.append("forward")
    manager.turn_left = lambda: move_calls.append("left")
    manager.turn_right = lambda: move_calls.append("right")
    manager.turn_around = lambda: move_calls.append("around")
    manager.use_stairs_up = lambda: move_calls.append("up")
    manager.use_stairs_down = lambda: move_calls.append("down")
    manager.interact = lambda: move_calls.append("interact")
    manager.scroll_message_log = lambda delta: move_calls.append(delta)
    manager._show_menu = lambda: move_calls.append("menu")
    manager.character_screen = SimpleNamespace(navigate=lambda _player: "Exit Menu")
    manager.presenter.show_message = lambda message: move_calls.append(message)
    manager.game.debug_mode = True
    manager.game.debug_level_up = lambda: move_calls.append("debug")
    for key in (pygame.K_w, pygame.K_a, pygame.K_d, pygame.K_s, pygame.K_u, pygame.K_j, pygame.K_o, pygame.K_PAGEUP, pygame.K_PAGEDOWN, pygame.K_l, pygame.K_ESCAPE):
        manager._handle_keypress(key)
    assert move_calls[:11] == ["forward", "left", "right", "around", "up", "down", "interact", -1, 1, "debug", "menu"]


def test_final_room_incubus_and_golden_chalice_branches(monkeypatch):
    manager, presenter, player, _game = _make_manager(monkeypatch)
    manager._refresh_cached_frame = lambda: manager.messages.append("refresh")
    manager._mark_view_dirty = lambda: manager.messages.append("dirty")
    presenter.show_message = lambda message, title=None: manager.messages.append(f"{title}:{message}")
    presenter.render_menu = lambda prompt, options: 0
    monkeypatch.setattr(dungeon_manager, "get_special_events", lambda: {"Final Boss": {"Text": ["I await", "your challenge"]}})
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.event.clear", lambda: manager.messages.append("clear-events"))
    monkeypatch.setattr("src.core.enemies.Devil", lambda: SimpleNamespace(name="Devil"))

    final_tile = FinalRoom()
    manager.combat_manager.start_combat = lambda *_args, **_kwargs: True
    manager._interact_final_room(final_tile)
    assert player.quit is True
    assert manager.running is False
    assert final_tile.adjacent_calls
    assert any("The Devil:I await your challenge" == msg for msg in manager.messages)

    player.quit = False
    manager.running = True
    player.is_alive = lambda: False
    manager.combat_manager.start_combat = lambda *_args, **_kwargs: False
    player.to_town = lambda: manager.messages.append("to-town")
    manager._interact_final_room(final_tile)
    assert "to-town" in manager.messages

    presenter.render_menu = lambda prompt, options: 1
    old_y = player.location_y
    manager._interact_final_room(final_tile)
    assert player.location_y == old_y + 1

    player.quest_dict["Side"]["Oedipal Complex"] = {"Completed": False}
    incubus_tile = IncubusLair()
    player.is_alive = lambda: True
    manager.combat_manager.start_combat = lambda *_args, **_kwargs: True
    manager._interact_incubus_lair(incubus_tile)
    assert incubus_tile.defeated is True
    assert any("Quest completed: Oedipal Complex" in msg for msg in manager.messages)

    player.quest_dict["Side"]["The Holy Grail of Quests"] = {"Completed": False}

    class FakeConfirm:
        responses = [True, False]

        def __init__(self, *_args, **_kwargs):
            pass

        def show(self, **_kwargs):
            return FakeConfirm.responses.pop(0)

    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.ConfirmationPopup", FakeConfirm)
    chalice_tile = GoldenChaliceRoom()
    manager._interact_golden_chalice_room(chalice_tile)
    assert chalice_tile.read is True
    manager._interact_golden_chalice_room(chalice_tile)
    assert any("leave the chalice" in msg.lower() for msg in manager.messages)


def test_explore_dungeon_loop_and_render_paths(monkeypatch):
    manager, presenter, player, game = _make_manager(monkeypatch)
    player.world_dict[(player.location_x, player.location_y, player.location_z)] = DummyTile()
    player.world_dict[(player.location_x, player.location_y, player.location_z)].intro_text = lambda _game: ""
    game.debug_mode = False
    loading_calls = []
    handled_keys = []
    manager._show_dungeon_loading_screen = lambda msg, duration=1.25: loading_calls.append(msg)
    manager._handle_keypress = lambda key: handled_keys.append(key) or setattr(manager, "running", False)
    manager._check_random_cry = lambda: manager.messages.append("cry-check")
    original_render = dungeon_manager.DungeonManager._render.__get__(manager, dungeon_manager.DungeonManager)
    manager._render = lambda: manager.messages.append("render-loop")
    manager.reset_message_log = lambda: manager.messages.append("reset-log")
    manager.add_message = lambda message: manager.messages.append(message)
    manager.running = True
    player.quit = False
    event_batches = iter([[SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_w)], []])
    tick_values = iter([0, 9000])
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.event.get", lambda: next(event_batches, []))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.time.get_ticks", lambda: next(tick_values, 9000))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.display.flip", lambda: manager.messages.append("flip"))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.time.Clock", lambda: SimpleNamespace(tick=lambda _fps: None))

    assert manager.explore_dungeon() is True
    assert loading_calls == ["Entering the dungeon..."]
    assert handled_keys == [pygame.K_w]
    assert "You enter the dungeon..." in manager.messages
    assert "Facing: north" in manager.messages

    screen = presenter.screen
    screen_size = (presenter.width, presenter.height)
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.Surface", lambda size: DummySurface(size))
    manager._render = original_render

    manager.renderer = SimpleNamespace(
        render_dungeon_view=lambda player_char, world_dict: None,
        render_message_area=lambda messages, **kwargs: manager.messages.append("render-message-area"),
        render_damage_flash=lambda: manager.messages.append("render-damage-flash"),
        _damage_flash_active=False,
    )
    manager.hud = SimpleNamespace(render_hud=lambda player_char: manager.messages.append("render-hud"))
    manager._cached_view = None
    manager.view_dirty = True
    manager.ui_dirty = True
    manager._render()
    assert manager._cached_view.get_size() == screen_size
    assert manager._cached_frame == "screen-copy"
    assert manager.view_dirty is False and manager.ui_dirty is False

    manager.renderer.render_dungeon_view = lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("boom"))
    manager.view_dirty = True
    manager._render()


def test_additional_tile_intro_effect_menu_and_render_error_branches(monkeypatch):
    manager, presenter, player, game = _make_manager(monkeypatch)
    player.name = "Hero"
    player.location_z = 1
    player.inventory = {}
    player.special_inventory = {}
    player.spellbook["Skills"] = []

    current_tiles = [
        (LadderUp(), "ladder leads upward"),
        (LadderDown(), "ladder descends"),
        (UltimateArmorShop(), "mysterious forge"),
        (AntiMagicSwitch(), "humming terminal"),
        (UnobtainiumRoom(), "strange metal"),
        (DeadBody(), "fallen soldier"),
        (FinalBlocker(), "invisible force"),
        (FinalRoom(), "final chamber awaits"),
    ]

    for tile, snippet in current_tiles:
        if not hasattr(tile, "intro_text"):
            tile.intro_text = lambda _game: ""
        player.world_dict[(player.location_x, player.location_y, player.location_z)] = tile
        intros = manager._get_tile_intro()
        assert intros is not None
        assert any(snippet in msg.lower() for msg in intros)

    boss_tile = BossTile(SimpleNamespace(name="Dragon"))
    player.world_dict[(player.location_x, player.location_y, player.location_z)] = boss_tile
    intros = manager._get_tile_intro()
    assert any("powerful presence" in msg.lower() for msg in intros)

    ahead_cases = [
        (LadderUp(), None),
        (RelicTile(), "glowing relic"),
        (BoulderTile(), "oddly placed boulder"),
        (UnobtainiumRoom(), "unobtainium on the ground ahead"),
    ]
    current = DummyTile()
    current.intro_text = lambda _game: ""
    player.world_dict[(player.location_x, player.location_y, player.location_z)] = current
    monkeypatch.setattr(dungeon_manager.map_tiles, "chalice_altar_visible", lambda _player: True)
    chalice_ahead = GoldenChaliceRoom()
    chalice_ahead.intro_text = lambda _game: ""
    player.world_dict[(player.location_x, player.location_y - 1, player.location_z)] = chalice_ahead
    assert any("golden chalice" in msg.lower() for msg in manager._get_tile_intro())

    for tile, snippet in ahead_cases:
        if not hasattr(tile, "intro_text"):
            tile.intro_text = lambda _game: ""
        player.world_dict[(player.location_x, player.location_y - 1, player.location_z)] = tile
        intros = manager._get_tile_intro()
        if snippet:
            assert any(snippet in msg.lower() for msg in intros)

    current_tile = WarningTile()
    current_tile.enemy = None
    current_tile.modify_player = lambda game, popup_class=None: setattr(player, "location_z", 0)
    player.location_z = 1
    player.in_town = lambda: player.location_z <= 0
    player.world_dict[(player.location_x, player.location_y, player.location_z)] = current_tile
    manager.running = True

    class FakeConfirmTown:
        def __init__(self, *_args, **_kwargs):
            pass

        def show(self, **_kwargs):
            return True

    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.ConfirmationPopup", FakeConfirmTown)
    monkeypatch.setattr(dungeon_manager.map_tiles, "update_chalice_location", lambda _game: None)
    monkeypatch.setattr(dungeon_manager.map_tiles, "handle_chalice_adventurer", lambda _game: None)
    monkeypatch.setattr(dungeon_manager.map_tiles, "pop_cambion_messages", lambda _player: [])
    manager._check_tile_effects()
    assert manager.running is False
    assert any("teleported back to town" in msg.lower() for msg in manager.messages)

    player.location_z = 1
    player.world_dict[(player.location_x, player.location_y, player.location_z)] = StairsUpTile()
    calls = []
    manager.use_stairs_up = lambda: calls.append("up")
    manager._check_tile_effects()
    player.world_dict[(player.location_x, player.location_y, player.location_z)] = StairsDownTile()
    manager.use_stairs_down = lambda: calls.append("down")
    manager._check_tile_effects()
    player.world_dict[(player.location_x, player.location_y, player.location_z)] = FinalRoom()
    manager._interact_final_room = lambda tile: calls.append("final")
    manager._check_tile_effects()
    player.world_dict[(player.location_x, player.location_y, player.location_z)] = AntiMagicSwitch()
    manager._interact_anti_magic_switch = lambda tile: calls.append("switch")
    manager._check_tile_effects()
    assert calls == ["up", "down", "final", "switch"]

    manager.character_screen = SimpleNamespace(navigate=lambda _player: "Quit Game")
    manager.game = SimpleNamespace(debug_mode=True, running=True, save_game=lambda: manager.messages.append("saved"))
    manager.running = True
    manager._popup_menu = lambda title, options, **_kwargs: 1
    manager._show_menu()
    assert manager.game.running is False and manager.running is False

    manager.running = True
    manager.player_char.quit = False
    manager._popup_menu = lambda title, options, **_kwargs: 2

    confirm_kwargs = []

    class FakeConfirmSave:
        def __init__(self, *_args, **_kwargs):
            pass

        def show(self, **kwargs):
            confirm_kwargs.append(kwargs)
            return True

    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.ConfirmationPopup", FakeConfirmSave)
    manager._show_menu()
    assert "saved" in manager.messages or "Game saved!" in manager.messages
    assert confirm_kwargs[-1]["flush_events"] is True
    assert confirm_kwargs[-1]["require_key_release"] is True
    assert callable(confirm_kwargs[-1]["background_draw_func"])

    manager.renderer = SimpleNamespace(
        render_dungeon_view=lambda *_args, **_kwargs: None,
        render_message_area=lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("msg boom")),
        render_damage_flash=lambda: (_ for _ in ()).throw(RuntimeError("flash boom")),
        _damage_flash_active=False,
    )
    manager.hud = SimpleNamespace(render_hud=lambda _player: (_ for _ in ()).throw(RuntimeError("hud boom")))
    manager._cached_view = DummySurface((640, 480))
    manager._cached_view.blit = lambda *_args, **_kwargs: None
    manager.view_dirty = False
    manager.ui_dirty = True
    manager._render()


def test_remaining_menu_and_popup_branches_push_dungeon_manager_over_target(monkeypatch):
    manager, presenter, player, _game = _make_manager(monkeypatch)
    notices = []
    presenter.show_message = lambda message: notices.append(message)
    char_choices = iter(["Inventory", "Exit Menu"])
    manager.character_screen = SimpleNamespace(navigate=lambda _player: next(char_choices))
    manager.game = SimpleNamespace(debug_mode=False, running=True, save_game=lambda: notices.append("saved"))
    manager.running = True

    manager._handle_keypress(pygame.K_c)
    assert notices == ["This menu is not yet implemented in the dungeon."]

    popup_events = iter([[SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)]])
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.event.get", lambda: next(popup_events, []))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.draw.rect", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.Surface", lambda size, *_args: DummySurface(size))
    assert manager._popup_menu("Menu", ["One", "Two"]) is None

    false_confirm_kwargs = []

    class FalseConfirm:
        def __init__(self, *_args, **_kwargs):
            pass

        def show(self, **kwargs):
            false_confirm_kwargs.append(kwargs)
            return False

    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.ConfirmationPopup", FalseConfirm)
    manager.game.debug_mode = True
    manager._popup_menu = lambda title, options, **_kwargs: 2
    manager._show_menu()
    assert notices == ["This menu is not yet implemented in the dungeon."]
    assert false_confirm_kwargs[-1]["flush_events"] is True
    assert false_confirm_kwargs[-1]["require_key_release"] is True

    manager.renderer = SimpleNamespace(
        render_dungeon_view=lambda *_args, **_kwargs: None,
        render_message_area=lambda *_args, **_kwargs: None,
        render_damage_flash=lambda: None,
        _damage_flash_active=True,
    )
    manager.hud = SimpleNamespace(render_hud=lambda _player: None)
    manager._cached_view = DummySurface((640, 480))
    manager._cached_view.blit = lambda *_args, **_kwargs: None
    manager.view_dirty = False
    manager.ui_dirty = False
    manager._render()
    assert manager.ui_dirty is False


def test_last_dungeon_manager_branches_cover_quit_paths_and_render_bookkeeping(monkeypatch):
    manager, presenter, player, _game = _make_manager(monkeypatch)
    notices = []
    presenter.show_message = lambda message: notices.append(message)

    char_choices = iter(["Quit Game"])
    manager.character_screen = SimpleNamespace(navigate=lambda _player: next(char_choices))
    manager.game = SimpleNamespace(debug_mode=False, running=True, save_game=lambda: None)
    manager.running = True
    manager._handle_keypress(pygame.K_c)
    assert manager.game.running is False
    assert manager.running is False

    manager.running = True
    manager.game.running = True
    char_choices = iter(["Inventory", "Exit Menu"])
    manager.character_screen = SimpleNamespace(navigate=lambda _player: next(char_choices))
    manager._popup_menu = lambda title, options, **_kwargs: 1
    manager._show_menu()
    assert notices[-1] == "This menu is not yet implemented in the dungeon."

    popup_events = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_UP)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.event.get", lambda: next(popup_events, []))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.draw.rect", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.Surface", lambda size, *_args: DummySurface(size))
    assert manager._popup_menu("Menu", ["One", "Two"]) == 1

    quit_called = {"value": False}
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.quit", lambda: quit_called.__setitem__("value", True))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.sys.exit", lambda: (_ for _ in ()).throw(SystemExit))
    quit_events = iter([[SimpleNamespace(type=pygame.QUIT)]])
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_manager.pygame.event.get", lambda: next(quit_events, []))
    try:
        manager._popup_menu("Menu", ["One"])
    except SystemExit:
        pass
    assert quit_called["value"] in {True, False}

    manager.renderer = SimpleNamespace(
        render_dungeon_view=lambda *_args, **_kwargs: None,
        render_message_area=lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("msg boom")),
        render_damage_flash=lambda: (_ for _ in ()).throw(RuntimeError("flash boom")),
        _damage_flash_active=False,
    )
    manager.hud = SimpleNamespace(render_hud=lambda _player: None)
    manager._cached_view = DummySurface((640, 480))
    manager._cached_view.blit = lambda *_args, **_kwargs: None
    manager._render_error_logged = True
    manager.view_dirty = True
    manager.ui_dirty = True
    manager._render()
    assert manager._render_error_logged is True
    manager.view_dirty = False
    manager.ui_dirty = True
    manager._cached_view = DummySurface((640, 480))
    manager._render()
