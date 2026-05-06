#!/usr/bin/env python3
"""Focused coverage for the pygame town-menu screen."""

from __future__ import annotations

from types import SimpleNamespace

import pygame
import pytest

from src.ui_pygame.gui import town_menu


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

    def render(self, text, _antialias, _color):
        self.render_calls.append(text)
        return DummySurface((max(8, len(text) * 8), self._height), text=text)


class RecordingScreen:
    def __init__(self):
        self.blit_calls = []
        self.fill_calls = []

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))

    def fill(self, color):
        self.fill_calls.append(color)


def _make_presenter(*, debug_mode=False):
    return SimpleNamespace(
        screen=RecordingScreen(),
        width=900,
        height=700,
        title_font=RecordingFont(30),
        large_font=RecordingFont(26),
        normal_font=RecordingFont(22),
        small_font=RecordingFont(18),
        clock=SimpleNamespace(tick=lambda _fps: None),
        debug_mode=debug_mode,
        game=SimpleNamespace(debug_level_up=lambda: None),
    )


def test_town_menu_draw_panel(monkeypatch):
    presenter = _make_presenter(debug_mode=True)
    monkeypatch.setattr(town_menu.TownMenuScreen, "_load_background", lambda self: setattr(self, "background", None))
    screen = town_menu.TownMenuScreen(presenter)
    screen.current_selection = 1

    panel_calls = []
    draw_rect_calls = []
    monkeypatch.setattr(screen, "draw_semi_transparent_panel", lambda rect, alpha=180: panel_calls.append((rect, alpha)))
    monkeypatch.setattr(
        "src.ui_pygame.gui.town_menu.pygame.draw.rect",
        lambda *_args, **_kwargs: draw_rect_calls.append((_args, _kwargs)),
    )

    screen.draw_menu_panel(["Shop", "Inn", "Quit"])

    assert panel_calls
    assert draw_rect_calls
    assert "Town of Silvana" in presenter.title_font.render_calls
    assert "Shop" in presenter.normal_font.render_calls
    assert "Inn" in presenter.normal_font.render_calls
    assert "ESC: Quit" in presenter.small_font.render_calls
    assert "L: Debug Level Up" in presenter.small_font.render_calls


def test_town_menu_navigation_and_debug_level(monkeypatch):
    debug_calls = []
    presenter = _make_presenter(debug_mode=True)
    presenter.game = SimpleNamespace(debug_level_up=lambda: debug_calls.append(True))
    monkeypatch.setattr(town_menu.TownMenuScreen, "_load_background", lambda self: setattr(self, "background", None))
    screen = town_menu.TownMenuScreen(presenter)
    monkeypatch.setattr(screen, "draw_background", lambda: None)
    monkeypatch.setattr(screen, "draw_menu_panel", lambda _options: None)
    monkeypatch.setattr("src.ui_pygame.gui.town_menu.pygame.display.flip", lambda: None)

    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_l)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_DOWN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_SPACE)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.town_menu.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate(["Shop", "Inn", "Quit"]) == 1
    assert debug_calls == [True]

    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.town_menu.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate(["Shop", "Inn", "Quit"]) == 2

    screen.current_selection = 0
    clear_calls = []
    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_SPACE)],
        [SimpleNamespace(type=pygame.KEYUP, key=pygame.K_SPACE)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_DOWN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_SPACE)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.town_menu.pygame.event.get", lambda: next(event_batches, []))
    monkeypatch.setattr("src.ui_pygame.gui.town_menu.pygame.event.clear", lambda: clear_calls.append(True))
    assert screen.navigate(["Shop", "Inn", "Quit"], flush_events=True, require_key_release=True) == 1
    assert clear_calls == [True]


def test_town_menu_quit_event_raises(monkeypatch):
    presenter = _make_presenter()
    monkeypatch.setattr(town_menu.TownMenuScreen, "_load_background", lambda self: setattr(self, "background", None))
    screen = town_menu.TownMenuScreen(presenter)
    monkeypatch.setattr(screen, "draw_background", lambda: None)
    monkeypatch.setattr(screen, "draw_menu_panel", lambda _options: None)
    monkeypatch.setattr("src.ui_pygame.gui.town_menu.pygame.display.flip", lambda: None)

    quit_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.town_menu.pygame.quit", lambda: quit_calls.append(True))
    monkeypatch.setattr("sys.exit", lambda: (_ for _ in ()).throw(SystemExit()))
    monkeypatch.setattr(
        "src.ui_pygame.gui.town_menu.pygame.event.get",
        lambda: [SimpleNamespace(type=pygame.QUIT)],
    )

    with pytest.raises(SystemExit):
        screen.navigate(["Quit"])
    assert quit_calls
