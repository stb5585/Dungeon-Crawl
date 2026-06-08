#!/usr/bin/env python3
"""Focused coverage for the character naming screen."""

from __future__ import annotations

from types import SimpleNamespace

import pygame
import pytest

from src.ui_pygame.gui import character_naming


class DummySurface:
    def __init__(self, size=(64, 24), text=None):
        self._size = size
        self.text = text

    def get_width(self):
        return self._size[0]

    def get_height(self):
        return self._size[1]

    def get_size(self):
        return self._size

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
        width=1000,
        height=760,
        title_font=RecordingFont(32),
        large_font=RecordingFont(28),
        normal_font=RecordingFont(22),
        small_font=RecordingFont(18),
        clock=SimpleNamespace(tick=lambda _fps: None),
    )


def test_character_naming_draws_identity_and_default_preview(monkeypatch):
    presenter = _make_presenter()
    draw_calls = []
    manager_calls = []
    real_portrait_manager = character_naming.PortraitManager

    class FakePortraitManager:
        @staticmethod
        def normalize_key(value, default="unknown"):
            return real_portrait_manager.normalize_key(value, default)

        def get_portrait(self, race, gender):
            manager_calls.append((race, gender))
            return pygame.Surface((225, 400), pygame.SRCALPHA)

    monkeypatch.setattr(character_naming, "PortraitManager", FakePortraitManager)
    monkeypatch.setattr(
        "src.ui_pygame.gui.character_naming.pygame.draw.rect",
        lambda *_args, **_kwargs: draw_calls.append((_args, _kwargs)),
    )

    screen = character_naming.CharacterNamingScreen(presenter, "Female", "Half Elf", "Spellblade")
    screen.draw()

    assert manager_calls == [("Half Elf", "Female")]
    assert screen.portrait_path.name == "half_elf_female.png"
    assert "Name your character" in presenter.normal_font.render_calls
    assert {"Sex", "Race", "Class", "Female", "Half Elf", "Spellblade"}.issubset(
        set(presenter.normal_font.render_calls)
    )
    assert "Choose a Name" in presenter.title_font.render_calls
    assert "Created as Hero" in presenter.normal_font.render_calls
    assert draw_calls


def test_character_naming_portrait_preview_preserves_aspect_ratio():
    presenter = _make_presenter()
    screen = character_naming.CharacterNamingScreen(presenter, "Male", "Human", "Warrior")
    screen.portrait = DummySurface((225, 400))

    portrait_rect = screen.portrait_preview_rect()

    assert portrait_rect.width == 225
    assert portrait_rect.height == 400


def test_character_naming_navigation_confirm_and_cancel(monkeypatch):
    presenter = _make_presenter()
    screen = character_naming.CharacterNamingScreen(presenter, "Male", "Human", "Warrior")
    monkeypatch.setattr(screen, "draw", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.character_naming.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: [])

    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_a, unicode="A")],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_d, unicode="d")],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_BACKSPACE)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_a, unicode="a")],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.character_naming.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate() == "Aa"

    screen.text = ""
    event_batches = iter([[SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)]])
    monkeypatch.setattr("src.ui_pygame.gui.character_naming.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate(default="Hero") == "Hero"

    event_batches = iter([[SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)]])
    monkeypatch.setattr("src.ui_pygame.gui.character_naming.pygame.event.get", lambda: next(event_batches, []))
    assert screen.navigate() is None


def test_character_naming_quit_exits(monkeypatch):
    presenter = _make_presenter()
    screen = character_naming.CharacterNamingScreen(presenter, "Male", "Human", "Warrior")
    quit_calls = []
    monkeypatch.setattr(screen, "draw", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.character_naming.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.character_naming.pygame.quit", lambda: quit_calls.append(True))
    monkeypatch.setattr("src.ui_pygame.gui.character_naming.sys.exit", lambda: (_ for _ in ()).throw(SystemExit()))
    monkeypatch.setattr(
        "src.ui_pygame.gui.character_naming.pygame.event.get",
        lambda: [SimpleNamespace(type=pygame.QUIT)],
    )

    with pytest.raises(SystemExit):
        screen.navigate()
    assert quit_calls
