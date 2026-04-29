#!/usr/bin/env python3
"""Focused coverage for pygame game launcher helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.ui_pygame import game as pygame_game


def test_signal_handler_quits_and_exits(monkeypatch):
    quit_calls = []
    exit_codes = []
    monkeypatch.setattr("src.ui_pygame.game.pygame.quit", lambda: quit_calls.append(True))
    monkeypatch.setattr("src.ui_pygame.game.sys.exit", lambda code=0: exit_codes.append(code) or (_ for _ in ()).throw(SystemExit(code)))

    with pytest.raises(SystemExit):
        pygame_game.signal_handler(None, None)

    assert quit_calls == [True]
    assert exit_codes == [0]


def test_init_build_character_and_default_character(monkeypatch):
    class FakePresenter:
        def __init__(self):
            self.screen = SimpleNamespace()
            self.event_bus = "bus"
            self.height = 480
            self.width = 640
            self.debug_mode = False
            self.cleanup_called = False

        def cleanup(self):
            self.cleanup_called = True

    monkeypatch.setattr("src.ui_pygame.game.pygame.init", lambda: None)
    monkeypatch.setattr(pygame_game, "PygamePresenter", FakePresenter)
    monkeypatch.setattr(pygame_game.SaveManager, "list_saves", staticmethod(lambda: ["hero.save"]))
    game = pygame_game.PygameGame(debug_mode=True)

    assert game.load_files == ["hero.save"]
    assert game.event_bus == "bus"
    assert game.presenter.debug_mode is True
    assert game.stdscr.getmaxyx() == (480, 640)

    event_batches = iter([[SimpleNamespace(type=pygame_game.pygame.KEYDOWN)] if False else []])
    monkeypatch.setattr("src.ui_pygame.game.pygame.event.get", lambda: [SimpleNamespace(type=pygame_game.pygame.KEYDOWN)])
    assert game.stdscr.getch() == 13

    class FakeRace:
        def __init__(self):
            self.name = "Human"
            self.strength = 1
            self.intel = 2
            self.wisdom = 3
            self.con = 4
            self.charisma = 5
            self.dex = 6
            self.base_attack = 7
            self.base_defense = 8
            self.base_magic = 9
            self.base_magic_def = 10
            self.resistance = {"Fire": 0.1}
            self.cls_res = {"Base": ["Warrior"]}

    class FakeClass:
        def __init__(self):
            self.name = "Warrior"
            self.str_plus = 10
            self.int_plus = 11
            self.wis_plus = 12
            self.con_plus = 13
            self.cha_plus = 14
            self.dex_plus = 15
            self.att_plus = 2
            self.def_plus = 3
            self.magic_plus = 4
            self.magic_def_plus = 5
            self.equipment = {"Weapon": "starter"}

    created = {}

    class FakePlayer:
        def __init__(self, location_x, location_y, location_z, level, health, mana, stats, combat, gold, resistance):
            created.update(
                location=(location_x, location_y, location_z),
                level=level,
                health=health,
                mana=mana,
                stats=stats,
                combat=combat,
                gold=gold,
                resistance=resistance,
            )
            self.location_x = location_x
            self.location_y = location_y
            self.location_z = location_z
            self.level = level
            self.health = health
            self.mana = mana
            self.stats = stats
            self.combat = combat
            self.gold = gold
            self.resistance = resistance
            self.spellbook = {"Spells": {}, "Skills": {}}
            self.storage = {}
            self.equipment = {}
            self.loaded_tiles = False

        def load_tiles(self):
            self.loaded_tiles = True

    class FakeSpell:
        def __init__(self):
            self.name = "Spark"

    monkeypatch.setattr("src.core.player.Player", FakePlayer)
    monkeypatch.setattr("src.core.abilities.spell_dict", {"Warrior": {"1": FakeSpell}})
    monkeypatch.setattr(pygame_game.items, "HealthPotion", lambda: "potion")

    game.races_dict = {"Human": FakeRace}
    game.classes_dict = {"Warrior": {"class": FakeClass}}
    player = game._build_player_character("Human", "Warrior", name="Ada")

    assert created["location"] == (5, 10, 0)
    assert player.name == "Ada"
    assert player.race.name == "Human"
    assert player.cls.name == "Warrior"
    assert player.spellbook["Spells"]["Spark"].name == "Spark"
    assert player.storage["Health Potion"] == ["potion"] * 5
    assert player.loaded_tiles is True
    assert game.create_default_character(name="Bob").name == "Bob"


def test_debug_level_up_initialize_managers_and_update_bounties(monkeypatch):
    game = pygame_game.PygameGame.__new__(pygame_game.PygameGame)
    game.debug_mode = True
    game.presenter = SimpleNamespace(
        screen="screen",
        show_message=lambda message: messages.append(message),
    )
    messages = []
    game.player_char = SimpleNamespace(
        level=SimpleNamespace(level=5, exp=10, exp_to_gain=20),
        max_level=lambda: False,
    )

    class FakeLevelUpScreen:
        def __init__(self, screen, presenter):
            self.screen = screen
            self.presenter = presenter

        def show_level_up(self, player_char, game_obj):
            calls.append((player_char, game_obj))

    calls = []
    monkeypatch.setattr("src.ui_pygame.gui.level_up.LevelUpScreen", FakeLevelUpScreen)
    game.debug_level_up()
    assert game.player_char.level.exp == 30
    assert game.player_char.level.exp_to_gain == 0
    assert calls == [(game.player_char, game)]

    game.player_char.max_level = lambda: True
    game.debug_level_up()
    assert messages == ["Already at max level."]

    manager_calls = []
    monkeypatch.setattr(pygame_game, "ShopManager", lambda presenter, player: manager_calls.append(("shop", player)) or "shop")
    monkeypatch.setattr(pygame_game, "ChurchManager", lambda presenter, player: manager_calls.append(("church", player)) or "church")
    monkeypatch.setattr(pygame_game, "InnManager", lambda presenter, player: manager_calls.append(("inn", player)) or "inn")
    monkeypatch.setattr(pygame_game, "BarracksManager", lambda presenter, player: manager_calls.append(("barracks", player)) or "barracks")
    monkeypatch.setattr(pygame_game, "DungeonManager", lambda presenter, player, game_obj: manager_calls.append(("dungeon", player, game_obj)) or "dungeon")
    game.initialize_managers()
    assert game.shop_manager == "shop"
    assert game.dungeon_manager == "dungeon"

    class FakeBountyBoard:
        def __init__(self):
            self.bounties = [{"enemy": SimpleNamespace(name="Goblin"), "reward": 50}]

        def generate_bounties(self, game_obj):
            manager_calls.append(("bounties", game_obj))

    monkeypatch.setattr("src.core.town.BountyBoard", FakeBountyBoard)
    game.update_bounties()
    assert game.bounties["Goblin"]["reward"] == 50


def test_main_menu_load_game_show_intro_warp_point_save_and_character_info(monkeypatch):
    game = pygame_game.PygameGame.__new__(pygame_game.PygameGame)
    popup_messages = []
    presenter_messages = []
    progress_calls = []
    presenter = SimpleNamespace(
        show_message=lambda message, title="": presenter_messages.append((title, message)),
        show_progress_popup=lambda **kwargs: progress_calls.append(kwargs),
        cleanup=lambda: cleanup_calls.append(True),
        set_background_provider=lambda provider: background_provider_calls.append(provider),
    )
    cleanup_calls = []
    background_provider_calls = []
    game.presenter = presenter
    game.running = True
    game.debug_mode = True
    game._random_combat = True
    game.load_files = ["save1"]
    game.player_char = None
    game.initialize_managers = lambda: init_calls.append(True)
    init_calls = []

    class FakePopup:
        def __init__(self, presenter_obj, message, show_buttons=False, **_kwargs):
            popup_messages.append(message)
            self.message = message

        def show(self, **_kwargs):
            return True

    class FakeMenu:
        def __init__(self, presenter_obj):
            self.presenter_obj = presenter_obj

        def navigate(self, options):
            menu_calls.append(tuple(options))
            return menu_choices.pop(0)

    menu_calls = []
    menu_choices = [2, 3]
    monkeypatch.setattr(pygame_game, "confirm_yes_no", lambda presenter_obj, message: False)
    monkeypatch.setattr(pygame_game, "ConfirmationPopup", FakePopup)
    monkeypatch.setattr(pygame_game, "MainMenuScreen", FakeMenu)
    game.new_game = lambda: None
    game.load_game = lambda: None
    game.run = lambda: run_calls.append(True)
    run_calls = []
    game.main_menu()
    assert game._random_combat is True
    assert any("Random encounters enabled" in msg for msg in popup_messages)
    assert any("Settings" in opts for opts in menu_calls)
    assert any("coming soon" in message.lower() for _title, message in presenter_messages)
    assert game.running is False

    presenter_messages.clear()
    game.load_files = []
    assert pygame_game.PygameGame.load_game(game) is None
    assert presenter_messages[-1][1] == "No saved games found!"

    class FakeLoadScreen:
        def __init__(self, presenter_obj):
            self.presenter_obj = presenter_obj

        def navigate(self, save_files):
            return navigate_results.pop(0)

    navigate_results = ["save1", "save2"]
    monkeypatch.setattr(pygame_game, "LoadGameScreen", FakeLoadScreen)
    monkeypatch.setattr(pygame_game.SaveManager, "load_player", staticmethod(lambda filename: load_results.pop(0)))
    load_results = [
        SimpleNamespace(in_town=lambda: True, quit=True),
        None,
    ]
    game.load_files = ["save1"]
    loaded = pygame_game.PygameGame.load_game(game)
    assert loaded.quit is False
    assert loaded._suppress_heal_message is True
    assert progress_calls
    assert init_calls
    assert pygame_game.PygameGame.load_game(game) is None
    assert presenter_messages[-1][1] == "Failed to load character!"

    presenter_messages.clear()
    game.show_intro()
    assert len(presenter_messages) == 5

    confirm_results = iter([True, False])

    class FakePopup2:
        def __init__(self, presenter_obj, message, show_buttons=False, **_kwargs):
            popup_messages.append(message)
            self.message = message
            self._show_buttons = show_buttons

        def show(self, **_kwargs):
            if "Do you want to warp down to level 5?" in self.message:
                return next(confirm_results)
            return True

    monkeypatch.setattr(pygame_game, "ConfirmationPopup", FakePopup2)
    game.player_char = SimpleNamespace(
        name="Hero",
        world_dict={(3, 0, 5): SimpleNamespace(visited=False, warped=False), (2, 0, 5): SimpleNamespace(near=False), (4, 0, 5): SimpleNamespace(near=False), (3, -1, 5): SimpleNamespace(near=False), (3, 1, 5): SimpleNamespace(near=False)},
        location_x=0,
        location_y=0,
        location_z=0,
        facing="north",
        quit=False,
    )
    assert game.use_warp_point(background_draw_func=lambda: None) == "dungeon"
    assert game.player_char.location_x == 3 and game.player_char.location_z == 5
    assert game.player_char.world_dict[(3, 0, 5)].visited is True
    assert game.player_char.world_dict[(3, 0, 5)].warped is True
    assert game.player_char.world_dict[(2, 0, 5)].near is True
    assert game.use_warp_point(background_draw_func=lambda: None) is None

    monkeypatch.setattr(pygame_game.SaveManager, "save_player", staticmethod(lambda player, filename: save_results.pop(0)))
    monkeypatch.setattr(pygame_game.SaveManager, "list_saves", staticmethod(lambda: ["hero.save", "mage.save"]))
    save_results = [True, False]
    game.player_char = SimpleNamespace(name="Hero")
    game.save_game()
    assert game.load_files == ["hero.save", "mage.save"]
    assert "Game saved successfully!" in presenter_messages[-1][1]
    game.save_game()
    assert presenter_messages[-1][1] == "Save failed. Please try again."

    class FakeCharacterScreen:
        def __init__(self, presenter_obj):
            self.presenter_obj = presenter_obj

        def navigate(self, player):
            return nav_results.pop(0)

    nav_results = ["Quit Game"]
    monkeypatch.setattr(pygame_game, "CharacterScreen", FakeCharacterScreen)
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.confirm_yes_no", lambda presenter_obj, message: True)
    game.player_char = SimpleNamespace(quit=False)
    game.show_character_info()
    assert game.player_char.quit is True

    game.cleanup()
    assert cleanup_calls == [True]


def test_gameplay_statistics_popup_and_town_menu_entry(monkeypatch):
    game = pygame_game.PygameGame.__new__(pygame_game.PygameGame)
    game.presenter = SimpleNamespace()
    game.player_char = SimpleNamespace(
        name="Hero",
        level=SimpleNamespace(level=6),
        gameplay_stats={
            "steps_taken": "12",
            "stairs_used": 3,
            "enemies_defeated": 4,
            "deaths": 1,
            "flees": 2,
            "highest_level_reached": 5,
            "highest_damage_dealt": 99,
            "highest_damage_taken": 42,
        },
        town_heal=lambda: None,
        _suppress_heal_message=True,
        special_inventory={},
        quest_dict={"Side": {}},
        warp_point=False,
        quit=False,
    )

    popup_messages = []
    popup_kwargs = []

    class FakePopup:
        def __init__(self, _presenter, message, show_buttons=False, **_kwargs):
            popup_messages.append((message, show_buttons))

        def show(self, **kwargs):
            popup_kwargs.append(kwargs)
            return True

    monkeypatch.setattr(pygame_game, "ConfirmationPopup", FakePopup)

    formatted = pygame_game.PygameGame.format_gameplay_statistics(game.player_char)
    assert "Steps Taken: 12" in formatted
    assert "Highest Level Reached: 6" in formatted

    game.show_gameplay_statistics(background_draw_func=lambda: None)
    assert "Adventure Statistics" in popup_messages[-1][0]
    assert popup_messages[-1][1] is False
    assert popup_kwargs[-1]["flush_events"] is True
    assert popup_kwargs[-1]["require_key_release"] is True

    options_seen = []

    class FakeTownMenu:
        def __init__(self, _presenter):
            self.calls = 0

        def draw_background(self):
            return None

        def draw_menu_panel(self, _options):
            return None

        def navigate(self, options):
            options_seen.append(tuple(options))
            self.calls += 1
            if self.calls == 1:
                return options.index("Statistics")
            return len(options) - 1

    stats_calls = []
    monkeypatch.setattr(pygame_game, "TownMenuScreen", FakeTownMenu)
    game.show_gameplay_statistics = lambda background_draw_func=None: stats_calls.append(background_draw_func)

    assert game.town_menu() == "quit"
    assert stats_calls
    assert any("Statistics" in options for options in options_seen)
