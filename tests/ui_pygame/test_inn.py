#!/usr/bin/env python3
"""Focused coverage for inn/tavern manager helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pygame

from src.ui_pygame.gui import inn


class FakePopup:
    messages = []
    show_kwargs = []

    def __init__(self, _presenter, message, show_buttons=False, **_kwargs):
        self.message = message
        self.show_buttons = show_buttons
        FakePopup.messages.append(message)

    def show(self, **kwargs):
        FakePopup.show_kwargs.append(kwargs)
        return True


def _make_player(*, level=10):
    return SimpleNamespace(
        quest_dict={"Main": {}, "Bounty": {}},
        gold=10,
        familiar=None,
        summons={},
        player_level=lambda: level,
        level=SimpleNamespace(exp=0, exp_to_gain=10),
        max_level=lambda: False,
        modify_inventory=lambda _item: None,
    )


def _make_presenter():
    pygame.font.init()
    return SimpleNamespace(
        screen=object(),
        width=900,
        height=700,
        title_font=pygame.font.Font(None, 30),
        large_font=pygame.font.Font(None, 26),
        normal_font=pygame.font.Font(None, 22),
        small_font=pygame.font.Font(None, 18),
        clock=SimpleNamespace(tick=lambda _fps: None),
        debug_mode=False,
    )


def test_visit_inn_and_patron_helpers(monkeypatch):
    FakePopup.messages = []
    FakePopup.show_kwargs = []
    player = _make_player(level=30)
    presenter = _make_presenter()
    monkeypatch.setattr(inn.InnManager, "_load_background", lambda self: setattr(self, "background", None))
    monkeypatch.setattr("src.ui_pygame.gui.inn.ConfirmationPopup", FakePopup)
    monkeypatch.setattr("src.ui_pygame.gui.inn.LevelUpScreen", lambda *_args, **_kwargs: SimpleNamespace(show_level_up=lambda *_a, **_k: None))
    manager = inn.InnManager(presenter, player)

    calls = []
    manager.talk_to_patrons = lambda: calls.append("talk")
    manager.show_bounty_board = lambda: calls.append("bounty")

    selections = iter([0, 1, 2])

    class FakeLocationMenuScreen:
        def __init__(self, _presenter, _title):
            pass

        def navigate(self, _options, reset_cursor=False):
            return next(selections)

    monkeypatch.setattr("src.ui_pygame.gui.inn.LocationMenuScreen", FakeLocationMenuScreen)

    manager.visit_inn()

    assert calls == ["talk", "bounty"]
    assert "Come back whenever you'd like." in FakePopup.messages
    assert FakePopup.show_kwargs[-1]["flush_events"] is True
    assert FakePopup.show_kwargs[-1]["require_key_release"] is True
    assert callable(FakePopup.show_kwargs[-1]["background_draw_func"])

    player.quest_dict["Main"] = {"A Bad Dream": {"Turned In": False}}
    assert manager._build_patron_list() == ["Barkeep", "Waitress", "Drunkard", "Soldier", "Hooded Figure", "Back"]

    player.quest_dict["Main"] = {"A Bad Dream": {"Turned In": True}}
    assert "Busboy" in manager._build_patron_list()

    monkeypatch.setattr("src.ui_pygame.gui.inn.random.choice", lambda seq: seq[0])
    comment = manager._random_patron_comment("Drunkard")
    assert comment is not None


def test_talk_to_patrons_accepts_quest_or_shows_hint(monkeypatch):
    FakePopup.messages = []
    FakePopup.show_kwargs = []
    player = _make_player(level=12)
    presenter = _make_presenter()
    monkeypatch.setattr(inn.InnManager, "_load_background", lambda self: setattr(self, "background", None))
    monkeypatch.setattr("src.ui_pygame.gui.inn.LevelUpScreen", lambda *_args, **_kwargs: SimpleNamespace(show_level_up=lambda *_a, **_k: None))
    manager = inn.InnManager(presenter, player)
    monkeypatch.setattr(manager, "_build_patron_list", lambda: ["Barkeep", "Back"])
    monkeypatch.setattr(manager, "_random_patron_comment", lambda patron: f"{patron} comment")

    rendered = []

    class FakeLocationMenuScreen:
        def __init__(self, _presenter, _title):
            pass

        def navigate(self, _options, reset_cursor=False):
            if not rendered:
                return 0
            return 1

        def display_quest_text(self, text):
            rendered.append(text)

    class FakeQuestManager:
        def __init__(self, _presenter, _player, quest_text_renderer):
            self.quest_text_renderer = quest_text_renderer

        def check_and_offer(self, patron, show_help=False, suppress_no_quests_message=True):
            return False, False

        def get_random_help_hint(self, patron):
            return f"{patron} hint"

    monkeypatch.setattr("src.ui_pygame.gui.inn.LocationMenuScreen", FakeLocationMenuScreen)
    monkeypatch.setattr("src.ui_pygame.gui.quest_manager.QuestManager", FakeQuestManager)
    monkeypatch.setattr("src.ui_pygame.gui.inn.random.choice", lambda seq: seq[0])

    manager.talk_to_patrons()

    assert rendered == ["Barkeep hint"]


def test_bounty_accept_turn_in_and_view(monkeypatch):
    FakePopup.messages = []
    FakePopup.show_kwargs = []
    player = _make_player(level=20)
    presenter = _make_presenter()
    presenter.game = SimpleNamespace(
        bounties={
            "Goblin Hunt": {
                "enemy": SimpleNamespace(name="Goblin"),
                "num": 2,
                "gold": 50,
                "exp": 5,
                "reward": lambda: SimpleNamespace(name="Goblin Ear"),
            }
        }
    )
    added_items = []
    player.modify_inventory = lambda item: added_items.append(item.name)
    monkeypatch.setattr(inn.InnManager, "_load_background", lambda self: setattr(self, "background", None))
    monkeypatch.setattr("src.ui_pygame.gui.inn.ConfirmationPopup", FakePopup)
    monkeypatch.setattr("src.ui_pygame.gui.inn.LevelUpScreen", lambda *_args, **_kwargs: SimpleNamespace(show_level_up=lambda *_a, **_k: None))
    manager = inn.InnManager(presenter, player)

    class FakeLocationMenuScreen:
        def __init__(self, _presenter, title):
            self.title = title

        def navigate(self, options, reset_cursor=False):
            if self.title == "Turn In Bounty":
                return 0
            return None

        def navigate_with_content(self, items):
            if self.title == "Accept Bounty":
                return 0
            if self.title == "Active Bounties":
                return 0
            return None

    monkeypatch.setattr("src.ui_pygame.gui.inn.LocationMenuScreen", FakeLocationMenuScreen)

    manager.accept_bounty()
    assert "Goblin Hunt" in player.quest_dict["Bounty"]
    assert any("Bounty Accepted: Goblin Hunt" in message for message in FakePopup.messages)
    assert all(kwargs["flush_events"] is True for kwargs in FakePopup.show_kwargs)
    assert all(kwargs["require_key_release"] is True for kwargs in FakePopup.show_kwargs)

    manager.accept_bounty()
    assert "No new bounties available at this time." in FakePopup.messages

    player.quest_dict["Bounty"]["Goblin Hunt"][2] = True
    player.level.exp_to_gain = 0
    level_up_calls = []
    manager.level_up = lambda: level_up_calls.append(True) or setattr(player.level, "exp_to_gain", "MAX")
    manager.turn_in_bounty(["Goblin Hunt"])
    assert player.gold == 60
    assert player.level.exp == 5
    assert added_items == ["Goblin Ear"]
    assert level_up_calls == [True]
    assert "Goblin Hunt" not in player.quest_dict["Bounty"]

    player.quest_dict["Bounty"] = {}
    manager.view_active_bounties()
    assert any("No active bounties." in message for message in FakePopup.messages)
