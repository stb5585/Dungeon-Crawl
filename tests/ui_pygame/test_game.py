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


def test_cleanup_clears_background_provider_and_quits(monkeypatch):
    game = pygame_game.PygameGame.__new__(pygame_game.PygameGame)
    cleanup_calls = []
    provider_values = []
    quit_calls = []
    game.presenter = SimpleNamespace(
        cleanup=lambda: cleanup_calls.append(True),
        set_background_provider=lambda provider: provider_values.append(provider),
    )
    monkeypatch.setattr(pygame_game.pygame, "quit", lambda: quit_calls.append(True))

    game.cleanup()

    assert cleanup_calls == [True]
    assert provider_values == [None]
    assert quit_calls == [True]


def test_cleanup_clears_background_provider_when_presenter_cleanup_fails(monkeypatch):
    game = pygame_game.PygameGame.__new__(pygame_game.PygameGame)
    cleanup_calls = []
    provider_values = []
    quit_calls = []

    def fail_cleanup():
        cleanup_calls.append(True)
        raise RuntimeError("cleanup failed")

    game.presenter = SimpleNamespace(
        cleanup=fail_cleanup,
        set_background_provider=lambda provider: provider_values.append(provider),
    )
    monkeypatch.setattr(pygame_game.pygame, "quit", lambda: quit_calls.append(True))

    with pytest.raises(RuntimeError, match="cleanup failed"):
        game.cleanup()

    assert cleanup_calls == [True]
    assert provider_values == [None]
    assert quit_calls == [True]


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


def test_location_music_wrapper_is_defensive_and_routes_to_sound_manager():
    game = pygame_game.PygameGame.__new__(pygame_game.PygameGame)
    calls = []
    stop_calls = []
    game.presenter = SimpleNamespace(
        sound_manager=SimpleNamespace(
            play_location_music=lambda location, **kwargs: calls.append((location, kwargs)) or "theme",
            stop_music=lambda **kwargs: stop_calls.append(kwargs),
        )
    )

    assert game._play_location_music("dungeon", boss=True) == "theme"
    assert calls == [("dungeon", {"boss": True, "final": False})]
    game._stop_music(fade_ms=125)
    assert stop_calls == [{"fade_ms": 125}]

    game.presenter.sound_manager.play_location_music = lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("audio"))
    assert game._play_location_music("town") is None
    game.presenter.sound_manager.stop_music = lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("audio"))
    game._stop_music()

    game.presenter.sound_manager = None
    assert game._play_location_music("town") is None
    game._stop_music()


def test_top_level_flows_request_location_music(monkeypatch):
    game = pygame_game.PygameGame.__new__(pygame_game.PygameGame)
    music_calls = []
    game._play_location_music = lambda location, **kwargs: music_calls.append((location, kwargs)) or location
    game.presenter = SimpleNamespace(set_background_provider=lambda _provider: None)
    game.shop_manager = SimpleNamespace(
        visit_blacksmith=lambda: None,
        visit_alchemist=lambda: None,
        visit_jeweler=lambda: None,
    )
    game.church_manager = SimpleNamespace(visit_church=lambda: None)
    game.barracks_manager = SimpleNamespace(visit_barracks=lambda: None)
    game.inn_manager = SimpleNamespace(visit_inn=lambda: None)
    game.dungeon_manager = SimpleNamespace(explore_dungeon=lambda: None)
    game.player_char = SimpleNamespace(quit=False, in_town=lambda: True)

    class FakeShopSelection:
        def __init__(self, _presenter):
            pass

        def navigate(self, _options, **_kwargs):
            return 3

    monkeypatch.setattr(pygame_game, "ShopSelectionScreen", FakeShopSelection)

    game.visit_shop()
    game.visit_church()
    game.visit_barracks()
    game.visit_inn()
    game.enter_dungeon()

    assert music_calls == [
        ("shop", {}),
        ("church", {}),
        ("town", {}),
        ("inn", {}),
        ("dungeon", {}),
        ("town", {}),
    ]


def test_new_game_uses_guarded_race_and_class_selection(monkeypatch):
    game = pygame_game.PygameGame.__new__(pygame_game.PygameGame)
    route_kwargs = []
    game.presenter = SimpleNamespace(
        show_message=lambda _message: None,
        get_text_input=lambda _prompt: "Ada",
    )

    class FakeRace:
        name = "Human"

    class FakeClass:
        name = "Warrior"

    class FakeSexScreen:
        def __init__(self, _presenter):
            pass

        def navigate(self, **kwargs):
            route_kwargs.append(("sex", kwargs))
            return "Female"

    class FakeRaceScreen:
        def __init__(self, _presenter):
            pass

        def navigate(self, races_dict, **kwargs):
            route_kwargs.append(("race", kwargs))
            return "Human"

    class FakeClassScreen:
        def __init__(self, _presenter):
            pass

        def navigate(self, race_name, race, classes_dict, **kwargs):
            route_kwargs.append(("class", kwargs))
            return "Warrior"

    class FakeNamingScreen:
        def __init__(self, _presenter, sex, race_name, class_name):
            route_kwargs.append(("naming_init", {"sex": sex, "race": race_name, "class": class_name}))

        def navigate(self, **kwargs):
            route_kwargs.append(("naming", kwargs))
            return "Ada"

    class FakePopup:
        def __init__(self, *_args, **_kwargs):
            pass

        def show(self, **_kwargs):
            return True

    game.races_dict = {"Human": FakeRace}
    game.classes_dict = {"Warrior": {"class": FakeClass}}
    game._build_player_character = lambda race_name, class_name, name, sex: SimpleNamespace(
        race_name=race_name,
        class_name=class_name,
        name=name,
        sex=sex,
        health=SimpleNamespace(max=20),
        mana=SimpleNamespace(max=10),
    )
    game.initialize_managers = lambda: None
    monkeypatch.setattr(pygame_game, "RaceSelectionScreen", FakeRaceScreen)
    monkeypatch.setattr(pygame_game, "SexSelectionScreen", FakeSexScreen)
    monkeypatch.setattr(pygame_game, "ClassSelectionScreen", FakeClassScreen)
    monkeypatch.setattr(pygame_game, "CharacterNamingScreen", FakeNamingScreen)
    monkeypatch.setattr(pygame_game, "ConfirmationPopup", FakePopup)

    player = game.new_game()

    assert player.name == "Ada"
    assert player.sex == "Female"
    assert route_kwargs == [
        ("sex", {"flush_events": True, "require_key_release": True}),
        ("race", {"flush_events": True, "require_key_release": True}),
        ("class", {"flush_events": True, "require_key_release": True}),
        ("naming_init", {"sex": "Female", "race": "Human", "class": "Warrior"}),
        ("naming", {"default": "Hero", "flush_events": True, "require_key_release": True}),
    ]


def test_main_menu_load_game_show_intro_warp_point_save_and_character_info(monkeypatch):
    game = pygame_game.PygameGame.__new__(pygame_game.PygameGame)
    popup_messages = []
    popup_kwargs = []
    popup_show_calls = []
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
    save_list = ["save1"]
    monkeypatch.setattr(pygame_game.SaveManager, "list_saves", staticmethod(lambda: list(save_list)))
    stop_calls = []
    music_calls = []
    game._stop_music = lambda **kwargs: stop_calls.append(kwargs)
    game._play_location_music = lambda location, **kwargs: music_calls.append((location, kwargs)) or location
    init_calls = []

    class FakePopup:
        def __init__(self, presenter_obj, message, show_buttons=False, **_kwargs):
            popup_messages.append(message)
            self.message = message

        def show(self, **kwargs):
            popup_kwargs.append(kwargs)
            popup_show_calls.append((self.message, kwargs))
            return True

    class FakeMenu:
        def __init__(self, presenter_obj):
            self.presenter_obj = presenter_obj

        def navigate(self, options, **kwargs):
            menu_calls.append(tuple(options))
            popup_kwargs.append(kwargs)
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
    assert popup_kwargs[-1]["flush_events"] is True
    assert popup_kwargs[-1]["require_key_release"] is True
    assert any("Settings" in opts for opts in menu_calls)
    settings_calls = [
        kwargs for message, kwargs in popup_show_calls
        if "settings menu coming soon" in message.lower()
    ]
    assert settings_calls
    assert settings_calls[-1]["flush_events"] is True
    assert settings_calls[-1]["require_key_release"] is True
    assert game.running is False
    assert stop_calls == [{"fade_ms": 250}]
    assert music_calls == [("menu", {})]

    presenter_messages.clear()
    game.load_files = []
    save_list.clear()
    assert pygame_game.PygameGame.load_game(game) is None
    assert presenter_messages[-1][1] == "No saved games found!"
    assert game.load_files == []

    class FakeLoadScreen:
        def __init__(self, presenter_obj):
            self.presenter_obj = presenter_obj

        def navigate(self, save_files, **kwargs):
            popup_kwargs.append(kwargs)
            return navigate_results.pop(0)

    navigate_results = ["save1", "save2"]
    monkeypatch.setattr(pygame_game, "LoadGameScreen", FakeLoadScreen)
    monkeypatch.setattr(pygame_game.SaveManager, "load_player", staticmethod(lambda filename: load_results.pop(0)))
    load_results = [
        SimpleNamespace(in_town=lambda: True, quit=True),
        None,
    ]
    save_list[:] = ["save1"]
    game.load_files = []
    loaded = pygame_game.PygameGame.load_game(game)
    assert loaded.quit is False
    assert loaded._suppress_heal_message is True
    assert game.load_files == ["save1"]
    assert popup_kwargs[-1]["flush_events"] is True
    assert popup_kwargs[-1]["require_key_release"] is True
    assert progress_calls
    assert init_calls
    assert pygame_game.PygameGame.load_game(game) is None
    assert presenter_messages[-1][1] == "Failed to load character!"

    presenter_messages.clear()
    game.show_intro()
    assert len(presenter_messages) == 5

    confirm_results = iter([True, False])
    popup_kwargs.clear()

    class FakePopup2:
        def __init__(self, presenter_obj, message, show_buttons=False, **_kwargs):
            popup_messages.append(message)
            self.message = message
            self._show_buttons = show_buttons

        def show(self, **kwargs):
            popup_kwargs.append(kwargs)
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
    assert any("Two field scientists" in message for message in popup_messages)
    assert any("throw their levers" in message for message in popup_messages)
    assert popup_kwargs[0]["flush_events"] is True
    assert popup_kwargs[0]["require_key_release"] is True
    assert callable(popup_kwargs[0]["background_draw_func"])
    assert game.player_char.location_x == 3 and game.player_char.location_z == 5
    assert game.player_char.world_dict[(3, 0, 5)].visited is True
    assert game.player_char.world_dict[(3, 0, 5)].warped is True
    assert game.player_char.world_dict[(2, 0, 5)].near is True
    assert game.use_warp_point(background_draw_func=lambda: None) is None

    render_menu_calls = []
    game.presenter = SimpleNamespace(
        render_menu=lambda prompt, options, **kwargs: render_menu_calls.append((prompt, tuple(options), kwargs)) or 0,
        show_message=lambda message, title="": presenter_messages.append((title, message)),
        cleanup=lambda: cleanup_calls.append(True),
        set_background_provider=lambda provider: background_provider_calls.append(provider),
    )
    game.player_char = SimpleNamespace(
        name="Hero",
        world_dict={(3, 0, 5): SimpleNamespace(visited=False, warped=False)},
        location_x=0,
        location_y=0,
        location_z=0,
        facing="north",
        quit=False,
    )
    assert game.use_warp_point(background_draw_func=lambda: None) == "dungeon"
    assert render_menu_calls
    assert "Two field scientists" in render_menu_calls[0][0]
    assert render_menu_calls[0][1] == ("Yes", "No")
    assert render_menu_calls[0][2]["split_layout"] is True

    monkeypatch.setattr(pygame_game.SaveManager, "save_player", staticmethod(lambda player, filename: save_results.pop(0)))
    monkeypatch.setattr(pygame_game.SaveManager, "list_saves", staticmethod(lambda: ["hero.save", "mage.save"]))
    save_results = [True, False]
    game.player_char = SimpleNamespace(name="Hero")
    game.save_game()
    assert game.load_files == ["hero.save", "mage.save"]
    assert "Game saved successfully!" in presenter_messages[-1][1]
    game.save_game()
    assert presenter_messages[-1][1] == "Save failed. Please try again."

    class FakeStandardCharacterScreen:
        def __init__(self, presenter_obj):
            self.presenter_obj = presenter_obj

        def navigate(self, player):
            return nav_results.pop(0)

    nav_results = ["Exit Menu"]
    monkeypatch.setattr(pygame_game, "ModernCharacterScreen", FakeStandardCharacterScreen)
    game.player_char = SimpleNamespace(quit=False)
    game.show_character_info()
    assert game.player_char.quit is False

    game.cleanup()
    assert cleanup_calls == [True]


def test_main_menu_stops_music_after_returning_from_gameplay(monkeypatch):
    game = pygame_game.PygameGame.__new__(pygame_game.PygameGame)
    game.presenter = SimpleNamespace()
    game.running = True
    game.debug_mode = False
    game.load_files = []
    game.player_char = None
    stop_calls = []
    music_calls = []
    run_calls = []
    game._stop_music = lambda **kwargs: stop_calls.append(kwargs)
    game._play_location_music = lambda location, **kwargs: music_calls.append((location, kwargs)) or location
    game.new_game = lambda: SimpleNamespace(name="Hero")
    game.run = lambda: run_calls.append(True)
    monkeypatch.setattr(pygame_game.SaveManager, "list_saves", staticmethod(lambda: []))

    class FakeMenu:
        def __init__(self, _presenter):
            pass

        def navigate(self, _options, **_kwargs):
            return menu_choices.pop(0)

    menu_choices = [0, 2]
    monkeypatch.setattr(pygame_game, "MainMenuScreen", FakeMenu)

    game.main_menu()

    assert run_calls == [True]
    assert stop_calls == [{"fade_ms": 250}, {"fade_ms": 250}]
    assert music_calls == [("menu", {})]


def test_main_menu_refreshes_save_files_before_rendering_options(monkeypatch):
    game = pygame_game.PygameGame.__new__(pygame_game.PygameGame)
    game.presenter = SimpleNamespace()
    game.running = True
    game.debug_mode = False
    game.load_files = []
    game.player_char = None
    game._stop_music = lambda **_kwargs: None
    game._play_location_music = lambda *_args, **_kwargs: None
    game.new_game = lambda: None
    game.load_game = lambda: load_calls.append(True)
    game.run = lambda: None
    load_calls = []
    menu_calls = []
    monkeypatch.setattr(pygame_game.SaveManager, "list_saves", staticmethod(lambda: ["fresh.save"]))

    class FakeMenu:
        def __init__(self, _presenter):
            pass

        def navigate(self, options, **_kwargs):
            menu_calls.append(tuple(options))
            return menu_choices.pop(0)

    menu_choices = [1, 3]
    monkeypatch.setattr(pygame_game, "MainMenuScreen", FakeMenu)

    game.main_menu()

    assert menu_calls[0] == ("New Game", "Load Game", "Settings", "Exit")
    assert load_calls == [True]
    assert game.load_files == ["fresh.save"]


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
    assert "Exploration" in formatted
    assert "Combat" in formatted
    assert "Records" in formatted
    assert "Steps Taken: 12" in formatted
    assert "Encounters Survived: 5" in formatted
    assert "Combat Outcomes: 7" in formatted
    assert "Combat Survival Rate: 71%" in formatted
    assert "Exploration Actions: 15" in formatted
    assert "Total Activity: 22" in formatted
    assert "Highest Level Reached: 6" in formatted

    broken_stats_player = SimpleNamespace(
        level=SimpleNamespace(level="bad"),
        gameplay_stats={
            "steps_taken": object(),
            "enemies_defeated": 1,
            "flees": 0,
            "deaths": 5,
            "highest_damage_taken": None,
        },
    )
    broken_formatted = pygame_game.PygameGame.format_gameplay_statistics(broken_stats_player)
    assert "Steps Taken: 0" in broken_formatted
    assert "Encounters Survived: 0" in broken_formatted
    assert "Combat Outcomes: 6" in broken_formatted
    assert "Combat Survival Rate: 0%" in broken_formatted
    assert "Exploration Actions: 0" in broken_formatted
    assert "Total Activity: 6" in broken_formatted
    assert "Highest Level Reached: 1" in broken_formatted

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

        def navigate(self, options, **kwargs):
            options_seen.append(tuple(options))
            popup_kwargs.append(kwargs)
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
    assert popup_kwargs[-1]["flush_events"] is True
    assert popup_kwargs[-1]["require_key_release"] is True
