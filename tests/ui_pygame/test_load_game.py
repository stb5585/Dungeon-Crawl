#!/usr/bin/env python3
"""Focused coverage for the load-game screen helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pygame

from src.ui_pygame.gui import load_game


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


class RecordingScreen:
    def __init__(self, size=(800, 600)):
        self._size = size
        self.blit_calls = []
        self.fill_calls = []

    def fill(self, color):
        self.fill_calls.append(color)

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))


def _make_presenter():
    return SimpleNamespace(
        screen=RecordingScreen(),
        width=800,
        height=600,
        title_font=RecordingFont(),
        normal_font=RecordingFont(),
        small_font=RecordingFont(),
        clock=SimpleNamespace(tick=lambda _fps: None),
    )


def test_load_game_draw_helpers_and_data_loading(monkeypatch):
    presenter = _make_presenter()
    screen = load_game.LoadGameScreen(presenter)

    draw_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.load_game.pygame.draw.rect", lambda *_args, **_kwargs: draw_calls.append((_args, _kwargs)))
    flip_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.load_game.pygame.display.flip", lambda: flip_calls.append(True))

    player_a = SimpleNamespace(
        name="hero",
        race=SimpleNamespace(name="Human"),
        cls=SimpleNamespace(name="Warrior"),
        level=SimpleNamespace(level=5, exp=123),
        gold=77,
        stats=SimpleNamespace(strength=10, intel=9, wisdom=8, con=11, charisma=7, dex=6),
    )
    player_b = None

    def fake_load_player(path):
        if path == "a.save":
            return player_a
        if path == "b.save":
            return player_b
        raise RuntimeError("broken")

    monkeypatch.setattr(load_game.SaveManager, "load_player", staticmethod(fake_load_player))
    screen.load_save_files(["a.save", "b.save", "c.save"])

    assert screen.save_data[0]["name"] == "Hero"
    assert screen.save_data[0]["stats"]["STR"] == 10
    assert screen.save_data[1]["name"] == "Corrupted save"
    assert screen.save_data[2]["name"] == "Error loading"

    screen.draw_header()
    assert "Choose the character to load" in presenter.normal_font.render_calls

    screen.current_selection = 0
    screen.draw_char_info()
    assert "Level: 5" in presenter.small_font.render_calls
    assert "Race: Human" in presenter.small_font.render_calls
    assert "Class: Warrior" in presenter.small_font.render_calls
    assert "Experience: 123" in presenter.small_font.render_calls
    assert "Gold: 77" in presenter.small_font.render_calls
    assert "Stats:" in presenter.small_font.render_calls
    assert "STR: 10" in presenter.small_font.render_calls

    screen.draw_file_list()
    assert "Save Files" in presenter.small_font.render_calls
    assert "Hero (Lvl 5)" in presenter.small_font.render_calls

    screen.save_data = []
    screen.draw_file_list()
    assert "No save files found" in presenter.normal_font.render_calls

    screen.save_data = [{"name": "Hero", "level": 5, "race": "Human", "class": "Warrior", "file": "a.save"}]
    screen.current_selection = 0
    screen.draw_all()
    assert presenter.screen.fill_calls
    assert flip_calls
    assert draw_calls


def test_load_game_navigation_selects_and_cancels(monkeypatch):
    presenter = _make_presenter()
    screen = load_game.LoadGameScreen(presenter)
    screen.save_data = [
        {"name": "Hero", "level": 5, "file": "a.save"},
        {"name": "Mage", "level": 3, "file": "b.save"},
    ]
    screen.save_files = ["a.save", "b.save"]
    monkeypatch.setattr(screen, "draw_all", lambda: None)

    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_DOWN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.load_game.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate(["a.save", "b.save"]) == "b.save"

    screen.current_selection = 0
    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.load_game.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate(["a.save", "b.save"]) is None
