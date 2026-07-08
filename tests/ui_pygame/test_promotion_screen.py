#!/usr/bin/env python3
"""Focused coverage for the pygame promotion screen."""

from __future__ import annotations

from types import SimpleNamespace

import pygame
import pytest

from src.ui_pygame.gui import promotion_screen


class DummySurface:
    def __init__(self, size=(64, 24), text=None):
        self._size = size
        self.text = text

    def get_width(self):
        return self._size[0]

    def get_height(self):
        return self._size[1]

    def get_rect(self, **kwargs):
        rect = pygame.Rect(0, 0, *self._size)
        for key, value in kwargs.items():
            setattr(rect, key, value)
        return rect


class RecordingFont:
    def __init__(self, height=24):
        self.render_calls = []
        self._height = height

    def render(self, text, _aa, _color):
        self.render_calls.append(text)
        return DummySurface((max(8, len(text) * 8), self._height), text=text)

    def get_height(self):
        return self._height


class RecordingScreen:
    def __init__(self):
        self.blit_calls = []
        self.fill_calls = []

    def blit(self, surface, pos):
        self.blit_calls.append((surface, pos))

    def fill(self, color):
        self.fill_calls.append(color)


def _make_presenter():
    return SimpleNamespace(
        screen=RecordingScreen(),
        width=900,
        height=700,
        title_font=RecordingFont(30),
        large_font=RecordingFont(26),
        normal_font=RecordingFont(22),
        small_font=RecordingFont(18),
        clock=SimpleNamespace(tick=lambda _fps: None),
    )


def _make_player():
    return SimpleNamespace(
        stats=SimpleNamespace(strength=10, intel=9, wisdom=8, con=7, charisma=6, dex=5),
        health=SimpleNamespace(max=40),
        mana=SimpleNamespace(max=20),
        combat=SimpleNamespace(attack=3, defense=4, magic=5, magic_def=6),
    )


class KnightClass:
    def __init__(self):
        self.name = "Knight"
        self.description = "A stalwart defender.\nKnows how to lead from the front."
        self.str_plus = 2
        self.int_plus = 1
        self.wis_plus = 0
        self.con_plus = 3
        self.cha_plus = 1
        self.dex_plus = 2
        self.att_plus = 4
        self.def_plus = 5
        self.magic_plus = 1
        self.magic_def_plus = 2
        self.restrictions = {"Weapon": ["Sword", "Mace"], "Armor": ["Heavy"]}


class WeaponMasterClass(KnightClass):
    def __init__(self):
        super().__init__()
        self.name = "Weapon Master"
        self.description = "Mastery grows through worthy weapon practice."
        self.restrictions = {"Weapon": ["Fist", "Dagger", "Sword"], "Armor": ["Light", "Medium"]}


def test_promotion_screen_draw_helpers(monkeypatch):
    presenter = _make_presenter()
    player = _make_player()
    monkeypatch.setattr(promotion_screen.PromotionScreen, "_load_background", lambda self: setattr(self, "background", None))
    screen = promotion_screen.PromotionScreen(
        presenter,
        player,
        options=["Knight"],
        option_map={"Knight": KnightClass},
        current_class="Warrior",
        pro_level=1,
    )

    panel_calls = []
    draw_rect_calls = []
    flip_calls = []
    monkeypatch.setattr(screen, "draw_background", lambda: panel_calls.append("bg"))
    monkeypatch.setattr(screen, "draw_semi_transparent_panel", lambda rect, alpha=180: panel_calls.append((rect, alpha)))
    monkeypatch.setattr("src.ui_pygame.gui.promotion_screen.pygame.draw.rect", lambda *_a, **_k: draw_rect_calls.append(True))
    monkeypatch.setattr("src.ui_pygame.gui.promotion_screen.pygame.display.flip", lambda: flip_calls.append(True))

    assert screen._wrap_lines("alpha beta\ngamma", 5)

    stat_pairs = screen._stat_pairs(KnightClass())
    assert stat_pairs[0][0][0] == "Strength"

    screen._draw_header()
    screen._draw_options_panel()
    screen._draw_detail_panel(KnightClass)
    screen._draw_instructions()
    screen.draw_all()

    assert "Church of Elysia - Promotion" in presenter.normal_font.render_calls
    assert "Choose your path" in presenter.normal_font.render_calls
    assert "Warrior -> Knight" in presenter.large_font.render_calls
    assert "Promotion Impact" in presenter.normal_font.render_calls
    assert "Character Menu Preview" in presenter.normal_font.render_calls
    assert "Character" in presenter.small_font.render_calls
    assert "Equipment" in presenter.small_font.render_calls
    assert "Class Gear Profile" not in presenter.normal_font.render_calls
    assert any("Existing legal gear is kept" in call for call in presenter.small_font.render_calls)
    assert "Equipment Restrictions" in presenter.normal_font.render_calls
    note_blits = [
        pos
        for surface, pos in presenter.screen.blit_calls
        if getattr(surface, "text", "").startswith("Existing legal gear is kept")
    ]
    restriction_blits = [
        pos
        for surface, pos in presenter.screen.blit_calls
        if getattr(surface, "text", "") == "Equipment Restrictions"
    ]
    assert note_blits[-1][1] > restriction_blits[-1][1]
    assert "UP/DOWN: Select   ENTER: Promote   ESC: Cancel" in presenter.small_font.render_calls
    assert draw_rect_calls
    assert flip_calls


def test_promotion_screen_previews_new_mechanic_tab(monkeypatch):
    presenter = _make_presenter()
    player = _make_player()
    monkeypatch.setattr(promotion_screen.PromotionScreen, "_load_background", lambda self: setattr(self, "background", None))
    screen = promotion_screen.PromotionScreen(
        presenter,
        player,
        options=["Weapon Master"],
        option_map={"Weapon Master": WeaponMasterClass},
        current_class="Warrior",
        pro_level=1,
    )

    panel_calls = []
    draw_rect_calls = []
    monkeypatch.setattr(screen, "draw_background", lambda: panel_calls.append("bg"))
    monkeypatch.setattr(screen, "draw_semi_transparent_panel", lambda rect, alpha=180: panel_calls.append((rect, alpha)))
    monkeypatch.setattr("src.ui_pygame.gui.promotion_screen.pygame.draw.rect", lambda *_a, **_k: draw_rect_calls.append(True))
    monkeypatch.setattr("src.ui_pygame.gui.promotion_screen.pygame.display.flip", lambda: None)

    screen.draw_all()

    assert "Warrior -> Weapon Master" in presenter.large_font.render_calls
    assert "Weapon Discipline" in presenter.small_font.render_calls
    assert any("New tab: Weapon Discipline" in call for call in presenter.small_font.render_calls)
    assert any("Intelligence helps" in call for call in presenter.small_font.render_calls)
    assert draw_rect_calls


def test_promotion_screen_navigation(monkeypatch):
    presenter = _make_presenter()
    player = _make_player()
    monkeypatch.setattr(promotion_screen.PromotionScreen, "_load_background", lambda self: setattr(self, "background", None))
    screen = promotion_screen.PromotionScreen(
        presenter,
        player,
        options=["Knight"],
        option_map={"Knight": KnightClass},
        current_class="Warrior",
        pro_level=2,
    )
    monkeypatch.setattr(screen, "draw_all", lambda: None)

    class FakePopup:
        responses = [True]
        show_kwargs = []

        def __init__(self, _presenter, _message):
            pass

        def show(self, **kwargs):
            FakePopup.show_kwargs.append(kwargs)
            return FakePopup.responses.pop(0)

    monkeypatch.setattr("src.ui_pygame.gui.promotion_screen.ConfirmationPopup", FakePopup)

    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.promotion_screen.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate() == "Knight"
    assert FakePopup.show_kwargs[-1]["flush_events"] is True
    assert FakePopup.show_kwargs[-1]["require_key_release"] is True
    assert callable(FakePopup.show_kwargs[-1]["background_draw_func"])

    screen.current_selection = 1
    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.promotion_screen.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate() is None

    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.promotion_screen.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate() is None

    screen.options = []
    assert screen.navigate() is None


def test_promotion_screen_mouse_selects_option(monkeypatch):
    presenter = _make_presenter()
    player = _make_player()
    monkeypatch.setattr(promotion_screen.PromotionScreen, "_load_background", lambda self: setattr(self, "background", None))
    screen = promotion_screen.PromotionScreen(
        presenter,
        player,
        options=["Knight"],
        option_map={"Knight": KnightClass},
        current_class="Warrior",
        pro_level=1,
    )
    monkeypatch.setattr(screen, "draw_all", lambda: None)

    class FakePopup:
        messages = []

        def __init__(self, _presenter, message):
            self.messages.append(message)

        def show(self, **_kwargs):
            return True

    monkeypatch.setattr("src.ui_pygame.gui.promotion_screen.ConfirmationPopup", FakePopup)

    click_pos = screen.option_rects()[0].center
    event_batches = iter([
        [SimpleNamespace(type=pygame.MOUSEMOTION, pos=click_pos)],
        [SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=click_pos)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.promotion_screen.pygame.event.get", lambda: next(event_batches, []))

    assert screen.navigate() == "Knight"
    assert FakePopup.messages == ["Promote to Knight?"]

    screen.current_selection = 0
    back_pos = screen.option_rects()[1].center
    event_batches = iter([
        [SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=back_pos)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.promotion_screen.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate() is None


def test_promotion_screen_quit_event_raises(monkeypatch):
    presenter = _make_presenter()
    player = _make_player()
    monkeypatch.setattr(promotion_screen.PromotionScreen, "_load_background", lambda self: setattr(self, "background", None))
    screen = promotion_screen.PromotionScreen(
        presenter,
        player,
        options=["Knight"],
        option_map={"Knight": KnightClass},
        current_class="Warrior",
        pro_level=1,
    )
    monkeypatch.setattr(screen, "draw_all", lambda: None)
    quit_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.promotion_screen.pygame.quit", lambda: quit_calls.append(True))
    monkeypatch.setattr("sys.exit", lambda: (_ for _ in ()).throw(SystemExit()))
    monkeypatch.setattr(
        "src.ui_pygame.gui.promotion_screen.pygame.event.get",
        lambda: [SimpleNamespace(type=pygame.QUIT)],
    )

    with pytest.raises(SystemExit):
        screen.navigate()
    assert quit_calls
