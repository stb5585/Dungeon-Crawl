#!/usr/bin/env python3
"""Focused coverage for the curses game controller."""

from __future__ import annotations

from types import ModuleType, SimpleNamespace

import pytest

from src.ui_curses import game as curses_game


class FakeStdScr:
    def __init__(self, inputs=None):
        self.inputs = list(inputs or [])
        self.clear_calls = 0
        self.refresh_calls = 0
        self.getch_calls = 0

    def getch(self):
        self.getch_calls += 1
        if self.inputs:
            return self.inputs.pop(0)
        return 10

    def clear(self):
        self.clear_calls += 1

    def refresh(self):
        self.refresh_calls += 1


def test_game_init_sets_state_and_calls_main_menu(monkeypatch):
    stdscr = FakeStdScr()
    main_menu_calls = []
    monkeypatch.setattr("src.ui_curses.game.SaveManager.list_saves", staticmethod(lambda: ["hero.save"]))
    monkeypatch.setattr("src.ui_curses.game.curses.curs_set", lambda value: main_menu_calls.append(("cursor", value)))
    monkeypatch.setattr(curses_game.Game, "main_menu", lambda self: main_menu_calls.append("main_menu"))
    monkeypatch.setattr("src.ui_curses.game.time.time", lambda: 123.0)

    game = curses_game.Game(stdscr, debug_mode=True)

    assert game.stdscr is stdscr
    assert game.debug_mode is True
    assert game.load_files == ["hero.save"]
    assert game._time == 123.0
    assert main_menu_calls == [("cursor", 0), "main_menu"]


def test_main_menu_routes_new_load_run_and_exit(monkeypatch):
    menu_updates = []
    navigate_results = iter([0, 1, 3])

    class FakeMainMenu:
        def __init__(self, game):
            pass

        def erase(self):
            menu_updates.append("erase")

        def update_options(self, options):
            menu_updates.append(tuple(options))

        def navigate_menu(self):
            return next(navigate_results)

    class FakeConfirmPopup:
        def __init__(self, game, text, box_height=8):
            self.text = text

        def navigate_popup(self):
            return True

    monkeypatch.setattr(curses_game, "menus", SimpleNamespace(MainMenu=FakeMainMenu, ConfirmPopupMenu=FakeConfirmPopup))

    game = curses_game.Game.__new__(curses_game.Game)
    game.debug_mode = True
    game._random_combat = True
    game.load_files = ["hero.save"]
    game.player_char = None
    game.new_game = lambda: "new-player"
    game.load_game = lambda menu: "loaded-player"
    run_calls = []
    game.run = lambda: run_calls.append(game.player_char)
    game.update_loadfiles = lambda: None

    monkeypatch.setattr("src.ui_curses.game.sys.exit", lambda code=0: (_ for _ in ()).throw(SystemExit(code)))

    with pytest.raises(SystemExit):
        game.main_menu()

    assert game._random_combat is False
    assert ("New Game", "Load Game", "Settings", "Exit") in menu_updates
    assert run_calls == ["new-player", "loaded-player"]


def test_debug_level_up_and_bounty_helpers(monkeypatch):
    outputs = []

    class FakeTextBox:
        def __init__(self, game):
            pass

        def print_text_in_rectangle(self, text):
            outputs.append(text)

        def clear_rectangle(self):
            outputs.append("cleared")

    class FakeSelectionPopupMenu:
        def __init__(self, game, message, options, box_height=12, confirm=False):
            self.options = options

    monkeypatch.setattr(curses_game, "menus", SimpleNamespace(TextBox=FakeTextBox, SelectionPopupMenu=FakeSelectionPopupMenu))

    game = curses_game.Game.__new__(curses_game.Game)
    game.debug_mode = True
    game.stdscr = FakeStdScr()
    game.player_char = SimpleNamespace(
        max_level=lambda: False,
        level=SimpleNamespace(exp=10, exp_to_gain=5, pro_level=2),
        stats=SimpleNamespace(strength=1, intel=2, wisdom=3, con=4, charisma=5, dex=6),
        level_up=lambda game_obj, textbox=None, menu=None: outputs.append(("level_up", textbox is not None, menu is not None)),
    )
    game.debug_level_up()
    assert game.player_char.level.exp == 15
    assert game.player_char.level.exp_to_gain == 0
    assert outputs[-1] == ("level_up", True, True)

    outputs.clear()
    game.player_char.max_level = lambda: True
    game.debug_level_up()
    assert outputs[:2] == ["Already at max level.", "cleared"]

    class FakeBountyBoard:
        def __init__(self):
            self.bounties = [{"enemy": SimpleNamespace(name="Goblin"), "gold": 10}]

        def generate_bounties(self, game_obj):
            outputs.append("generated")

    monkeypatch.setattr("src.ui_curses.game.BountyBoard", FakeBountyBoard)
    game.update_bounties()
    assert game.bounties["Goblin"]["gold"] == 10
    game.delete_bounty({"enemy": SimpleNamespace(name="Goblin")})
    assert game.bounties == {}


def test_new_game_builds_player_and_load_game_restores_clean_state(monkeypatch):
    stdscr = FakeStdScr(inputs=[10])
    sleep_calls = []
    monkeypatch.setattr("src.ui_curses.game.time.sleep", lambda secs: sleep_calls.append(secs))

    fake_menus = ModuleType("menus")

    class FakeQuestPopupMenu:
        def __init__(self, game, box_height=0, box_width=0):
            self.drawn = []

        def draw_popup(self, texts):
            sleep_calls.append(tuple(texts))

    class FakeConfirmPopupMenu:
        responses = [True, True, True]

        def __init__(self, game, text, box_height=7, header_message=None):
            self.text = text
            self.header_message = header_message

        def navigate_popup(self):
            return self.responses.pop(0)

    class FakeNewGameMenu:
        def __init__(self, game):
            self.page = 0
            self.options_list = []
            self.current_option = 0
            self.calls = 0

        def update_options(self):
            return None

        def navigate_menu(self):
            self.calls += 1
            if self.calls == 1:
                return race
            return cls

        def erase(self):
            sleep_calls.append("erased")

    class FakeLoadGameMenu:
        def __init__(self, game, options):
            self.options = options

        def navigate_menu(self):
            return 0

    class FakeTextBox:
        def __init__(self, game):
            pass

        def print_text_in_rectangle(self, text):
            sleep_calls.append(text)

        def clear_rectangle(self):
            sleep_calls.append("cleared")

    fake_menus.QuestPopupMenu = FakeQuestPopupMenu
    fake_menus.ConfirmPopupMenu = FakeConfirmPopupMenu
    fake_menus.NewGameMenu = FakeNewGameMenu
    fake_menus.LoadGameMenu = FakeLoadGameMenu
    fake_menus.TextBox = FakeTextBox
    fake_menus.player_input = lambda game, prompt: "ada"
    fake_menus.save_file_popup = lambda game, load=False: sleep_calls.append(("save_popup", load))
    monkeypatch.setattr(curses_game, "menus", fake_menus)

    race = SimpleNamespace(
        name="Elf",
        strength=8,
        intel=12,
        wisdom=11,
        con=9,
        charisma=10,
        dex=13,
        base_attack=2,
        base_defense=3,
        base_magic=4,
        base_magic_def=5,
        resistance={"Fire": 0.1},
    )
    cls = SimpleNamespace(
        name="Mage",
        str_plus=1,
        int_plus=2,
        wis_plus=3,
        con_plus=4,
        cha_plus=5,
        dex_plus=6,
        att_plus=1,
        def_plus=2,
        magic_plus=3,
        magic_def_plus=4,
        equipment={"Weapon": "Staff"},
    )

    created = {}

    class FakePlayer:
        def __init__(self, x, y, z, level, health, mana, stats, combat, gold, resistance):
            created.update(location=(x, y, z), health=health.max, mana=mana.max, gold=gold, resistance=resistance)
            self.location_x = x
            self.location_y = y
            self.location_z = z
            self.level = level
            self.health = health
            self.mana = mana
            self.stats = stats
            self.combat = combat
            self.gold = gold
            self.resistance = resistance
            self.spellbook = {"Spells": {}}
            self.storage = {}
            self.world_dict = {}
            self.quit = False

        def load_tiles(self):
            created["loaded_tiles"] = True

    monkeypatch.setattr("src.ui_curses.game.player.Player", FakePlayer)
    monkeypatch.setattr(curses_game.abilities, "spell_dict", {"Mage": {"1": lambda: SimpleNamespace(name="Spark")}})
    monkeypatch.setattr(curses_game.items, "HealthPotion", lambda: "potion")

    game = curses_game.Game.__new__(curses_game.Game)
    game.stdscr = stdscr
    game.debug_mode = False
    player_char = game.new_game()

    assert created["location"] == (5, 10, 0)
    assert player_char.name == "Ada"
    assert player_char.race.name == "Elf"
    assert player_char.cls.name == "Mage"
    assert player_char.spellbook["Spells"]["Spark"].name == "Spark"
    assert player_char.storage["Health Potion"] == ["potion"] * 5
    assert created["loaded_tiles"] is True

    room = SimpleNamespace(enemy="enemy")
    loaded_player = SimpleNamespace(
        state="battle",
        location_x=1,
        location_y=2,
        location_z=3,
        world_dict={(1, 2, 3): room},
    )
    monkeypatch.setattr("src.ui_curses.game.SaveManager.load_player", staticmethod(lambda filename: loaded_player))
    game.load_files = ["ada.save"]
    loaded = game.load_game(fake_menus.NewGameMenu(game))
    assert loaded is loaded_player
    assert loaded_player.state == "normal"
    assert room.enemy is None
    assert stdscr.clear_calls == 1
    assert stdscr.refresh_calls == 1


def test_run_navigate_and_special_event(monkeypatch):
    calls = []

    game = curses_game.Game.__new__(curses_game.Game)
    game._time = 0
    game.player_char = SimpleNamespace(
        quit=False,
        level=SimpleNamespace(pro_level=1),
        current_weight=lambda: 10,
        max_weight=lambda: 5,
        in_town=lambda: True,
        town_heal=lambda: calls.append("heal"),
    )
    game.update_bounties = lambda: calls.append("bounties")
    monkeypatch.setattr("src.ui_curses.game.time.time", lambda: 1000)
    monkeypatch.setattr(curses_game.town, "town", lambda game_obj: calls.append("town") or setattr(game_obj.player_char, "quit", True))
    game.run()
    assert calls == ["bounties", "bounties", "heal", "town"]
    assert game.player_char.encumbered is True

    fake_menus = ModuleType("menus")

    class FakeQuestPopupMenu:
        def __init__(self, game, box_height=0, box_width=0):
            self.args = (box_height, box_width)

        def draw_popup(self, text):
            calls.append(tuple(text))

        def clear_popup(self):
            calls.append("clear_popup")

    fake_menus.QuestPopupMenu = FakeQuestPopupMenu
    monkeypatch.setattr(curses_game, "menus", fake_menus)
    monkeypatch.setattr("src.ui_curses.game.get_special_events", lambda: {"Intro": {"Text": ["One", "Two"]}})
    game.special_event("Intro")
    assert ("One", "Two") in calls
    assert "clear_popup" in calls
