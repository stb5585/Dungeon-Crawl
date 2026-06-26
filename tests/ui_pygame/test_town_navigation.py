#!/usr/bin/env python3
"""Focused coverage for the optional town navigation prototype."""

from __future__ import annotations

from types import SimpleNamespace

import pygame
import pytest

from src.ui_pygame.gui import town_navigation


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

    def get_height(self):
        return self._height

    def size(self, text):
        return (max(8, len(text) * 8), self._height)


class RecordingScreen:
    def __init__(self):
        self.blit_calls = []
        self.fill_calls = []

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))

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


def test_town_navigation_draws_current_node_and_options(monkeypatch):
    presenter = _make_presenter()
    screen = town_navigation.TownNavigationScreen(presenter)
    monkeypatch.setattr(screen, "_load_background", lambda: None)
    monkeypatch.setattr(screen, "draw_semi_transparent_panel", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.town_navigation.pygame.draw.rect", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.town_navigation.pygame.draw.polygon", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.town_navigation.pygame.draw.line", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.town_navigation.pygame.draw.circle", lambda *_args, **_kwargs: None)

    options = screen.build_options()
    screen.draw()

    assert options[-1] == ("Return to Town Menu", "Exit Town Navigation")
    assert "Explore Town" in presenter.title_font.render_calls
    assert "Town Square" in presenter.large_font.render_calls
    assert "North: Barracks" in presenter.small_font.render_calls
    assert "East: Shops" in presenter.small_font.render_calls


def test_town_navigation_moves_with_arrow_keys_and_returns_action(monkeypatch):
    presenter = _make_presenter()
    screen = town_navigation.TownNavigationScreen(presenter)
    monkeypatch.setattr(screen, "draw", lambda: screen.build_options())
    monkeypatch.setattr("src.ui_pygame.gui.town_navigation.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: [])

    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_UP)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.town_navigation.pygame.event.get", lambda: next(event_batches, []))

    assert screen.navigate() == "Barracks"
    assert screen.current_node_key == "Barracks"


def test_town_navigation_mouse_click_moves_and_escape(monkeypatch):
    presenter = _make_presenter()
    screen = town_navigation.TownNavigationScreen(presenter)
    screen._direction_rects = screen._town_direction_rects(screen.view_rect())
    click_pos = screen._direction_rects["east"].center
    monkeypatch.setattr(screen, "draw", lambda: screen.build_options())
    monkeypatch.setattr("src.ui_pygame.gui.town_navigation.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: [])

    event_batches = iter([
        [SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=click_pos)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.town_navigation.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate() is None
    assert screen.current_node_key == "Shops"

    event_batches = iter([[SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)]])
    monkeypatch.setattr("src.ui_pygame.gui.town_navigation.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate() is None


def test_town_navigation_ignores_blocked_direction():
    presenter = _make_presenter()
    screen = town_navigation.TownNavigationScreen(presenter)

    assert screen.move("north") is True
    assert screen.current_node_key == "Barracks"
    assert screen.move("north") is False
    assert screen.current_node_key == "Barracks"


def test_town_navigation_quit_exits(monkeypatch):
    presenter = _make_presenter()
    screen = town_navigation.TownNavigationScreen(presenter)
    quit_calls = []
    monkeypatch.setattr(screen, "draw", lambda: screen.build_options())
    monkeypatch.setattr("src.ui_pygame.gui.town_navigation.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.town_navigation.pygame.quit", lambda: quit_calls.append(True))
    monkeypatch.setattr("sys.exit", lambda: (_ for _ in ()).throw(SystemExit()))
    monkeypatch.setattr("src.ui_pygame.gui.town_navigation.pygame.event.get", lambda: [SimpleNamespace(type=pygame.QUIT)])

    with pytest.raises(SystemExit):
        screen.navigate()
    assert quit_calls
