#!/usr/bin/env python3
"""Focused coverage for the main menu screen helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pygame
import pytest

from src.ui_pygame.gui import main_menu


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
    def __init__(self):
        self.render_calls = []

    def render(self, text, _antialias, _color):
        self.render_calls.append(text)
        return DummySurface((max(8, len(text) * 8), 20), text=text)

    def size(self, text):
        return (max(8, len(text) * 8), 20)


class RecordingScreen:
    def __init__(self):
        self.blit_calls = []
        self.fill_calls = []

    def fill(self, color):
        self.fill_calls.append(color)

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))


def _make_presenter():
    return SimpleNamespace(
        screen=RecordingScreen(),
        width=900,
        height=700,
        title_font=RecordingFont(),
        normal_font=RecordingFont(),
        small_font=RecordingFont(),
        clock=SimpleNamespace(tick=lambda _fps: None),
    )


def test_main_menu_draw_and_navigation(monkeypatch):
    presenter = _make_presenter()
    ascii_font = RecordingFont()
    monkeypatch.setattr("src.ui_pygame.gui.main_menu.pygame.font.match_font", lambda *_args, **_kwargs: "courier")
    monkeypatch.setattr("src.ui_pygame.gui.main_menu.pygame.font.Font", lambda *_args, **_kwargs: ascii_font)
    screen = main_menu.MainMenuScreen(presenter)

    draw_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.main_menu.pygame.draw.rect", lambda *_args, **_kwargs: draw_calls.append((_args, _kwargs)))
    flip_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.main_menu.pygame.display.flip", lambda: flip_calls.append(True))

    screen.options = ["New Game", "Load Game", "Quit"]
    screen.current_option = 1
    screen.draw_title()
    assert ascii_font.render_calls

    screen.draw_menu()
    assert "New Game" in presenter.normal_font.render_calls
    assert "Load Game" in presenter.normal_font.render_calls
    assert draw_calls

    screen.draw()
    assert presenter.screen.fill_calls
    assert flip_calls

    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_DOWN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.main_menu.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate(["New Game", "Load Game", "Quit"]) == 2

    screen.current_option = 0
    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.main_menu.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate(["New Game", "Load Game", "Quit"]) is None


def test_main_menu_quit_event_raises_system_exit(monkeypatch):
    presenter = _make_presenter()
    monkeypatch.setattr("src.ui_pygame.gui.main_menu.pygame.font.match_font", lambda *_args, **_kwargs: "courier")
    monkeypatch.setattr("src.ui_pygame.gui.main_menu.pygame.font.Font", lambda *_args, **_kwargs: RecordingFont())
    screen = main_menu.MainMenuScreen(presenter)
    monkeypatch.setattr(screen, "draw", lambda: None)

    quit_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.main_menu.pygame.quit", lambda: quit_calls.append(True))
    monkeypatch.setattr("sys.exit", lambda: (_ for _ in ()).throw(SystemExit()))
    monkeypatch.setattr(
        "src.ui_pygame.gui.main_menu.pygame.event.get",
        lambda: [SimpleNamespace(type=pygame.QUIT)],
    )

    with pytest.raises(SystemExit):
        screen.navigate(["Play"])
    assert quit_calls
