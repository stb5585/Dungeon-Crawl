#!/usr/bin/env python3
"""Focused coverage for generic location-menu helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pygame
import pytest

from src.ui_pygame.gui import location_menu


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


class RecordingScreen:
    def __init__(self, size=(900, 700)):
        self._size = size
        self.blit_calls = []
        self.fill_calls = []

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))

    def fill(self, color):
        self.fill_calls.append(color)

    def copy(self):
        return "screen-copy"


def _make_presenter():
    return SimpleNamespace(
        screen=RecordingScreen(),
        width=900,
        height=700,
        title_font=RecordingFont(32),
        large_font=RecordingFont(28),
        normal_font=RecordingFont(22),
        small_font=RecordingFont(18),
        clock=SimpleNamespace(tick=lambda _fps: None),
        debug_mode=True,
    )


def test_location_menu_draw_helpers(monkeypatch):
    presenter = _make_presenter()
    screen = location_menu.LocationMenuScreen(presenter, "Church")
    screen.options_list = ["Heal", "Bless", "Leave"]
    screen.current_option = 1

    panel_calls = []
    monkeypatch.setattr(screen, "draw_semi_transparent_panel", lambda rect, alpha=180: panel_calls.append((rect, alpha)))
    draw_rect_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.location_menu.pygame.draw.rect", lambda *_args, **_kwargs: draw_rect_calls.append((_args, _kwargs)))
    flip_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.location_menu.pygame.display.flip", lambda: flip_calls.append(True))

    screen.draw_top()
    assert "Church" in presenter.large_font.render_calls

    screen.draw_options()
    assert "Heal" in presenter.normal_font.render_calls
    assert "Bless" in presenter.normal_font.render_calls

    screen.draw_content("Welcome to town\nThis is a wrapped paragraph.")
    assert "Welcome to town" in presenter.large_font.render_calls

    items_data = [(0, "Potion", 2, False), (1, "Elixir", 1, True)]
    screen.draw_content(items_data=items_data)
    assert any(surface.text == ">" for surface, _pos in presenter.screen.blit_calls if hasattr(surface, "text"))

    screen.draw_options_instructions()
    assert "[Use arrows to select]" in presenter.normal_font.render_calls

    monkeypatch.setattr(screen, "draw_background", lambda: panel_calls.append(("background", None)))
    monkeypatch.setattr(screen, "draw_top", lambda: panel_calls.append(("top", None)))
    monkeypatch.setattr(screen, "draw_options", lambda: panel_calls.append(("options", None)))
    monkeypatch.setattr(screen, "draw_content", lambda *args, **kwargs: panel_calls.append(("content", kwargs.get("items_data", args[0] if args else None))))
    screen.draw_all()
    assert ("background", None) in panel_calls
    assert flip_calls
    assert draw_rect_calls


def test_location_menu_navigation_and_item_navigation(monkeypatch):
    presenter = _make_presenter()
    screen = location_menu.LocationMenuScreen(presenter, "Inn")
    monkeypatch.setattr(screen, "draw_all", lambda: None)
    monkeypatch.setattr(screen, "draw_background", lambda: None)
    monkeypatch.setattr(screen, "draw_top", lambda: None)
    monkeypatch.setattr(screen, "draw_options", lambda: None)
    monkeypatch.setattr(screen, "draw_options_instructions", lambda: None)
    monkeypatch.setattr(screen, "draw_content", lambda *args, **kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.location_menu.pygame.display.flip", lambda: None)

    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_DOWN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.location_menu.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate(["Rest", "Leave"]) == 1

    screen.current_option = 1
    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.location_menu.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate(["Rest", "Leave"], reset_cursor=False) is None
    assert screen.current_option == 1

    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_SPACE)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.location_menu.pygame.event.get", lambda: next(event_batches, []))
    screen.display_items_list([("Potion", 2)])

    items = [(f"Item {idx}", idx + 1) for idx in range(25)]
    screen.current_option = 0
    screen.scroll_offset = 0
    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_DOWN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.location_menu.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate_with_content(items) == 1

    screen.current_option = 0
    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_UP)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.location_menu.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate_with_content(items) == len(items) - 1
    assert screen.scroll_offset > 0


def test_location_menu_quit_event_raises(monkeypatch):
    presenter = _make_presenter()
    screen = location_menu.LocationMenuScreen(presenter, "Shop")
    monkeypatch.setattr(screen, "draw_all", lambda: None)
    quit_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.location_menu.pygame.quit", lambda: quit_calls.append(True))
    monkeypatch.setattr("sys.exit", lambda: (_ for _ in ()).throw(SystemExit()))
    monkeypatch.setattr(
        "src.ui_pygame.gui.location_menu.pygame.event.get",
        lambda: [SimpleNamespace(type=pygame.QUIT)],
    )

    with pytest.raises(SystemExit):
        screen.navigate(["A", "B"])
    assert quit_calls
