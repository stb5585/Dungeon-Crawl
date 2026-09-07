#!/usr/bin/env python3
"""Focused coverage for presentation/asset gate pygame screens."""

from __future__ import annotations

from types import SimpleNamespace

import pygame
import pytest

from src.ui_pygame.gui import presentation_asset_screens


@pytest.fixture(autouse=True)
def _init_pygame():
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    yield


class DummySurface:
    def __init__(self, size=(64, 24), text=None):
        self._size = size
        self.text = text

    def get_size(self):
        return self._size

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
    def __init__(self, height=22):
        self.render_calls = []
        self._height = height

    def render(self, text, _antialias, _color):
        self.render_calls.append(text)
        return DummySurface((max(8, len(str(text)) * 8), self._height), text=text)

    def size(self, text):
        return (max(8, len(str(text)) * 8), self._height)

    def get_height(self):
        return self._height


class RecordingScreen:
    def __init__(self, size=(900, 700)):
        self._size = size
        self.fill_calls = []
        self.blit_calls = []

    def fill(self, color):
        self.fill_calls.append(color)

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))


def _make_presenter():
    return SimpleNamespace(
        screen=RecordingScreen(),
        width=900,
        height=700,
        title_font=RecordingFont(34),
        large_font=RecordingFont(28),
        normal_font=RecordingFont(22),
        small_font=RecordingFont(18),
        clock=SimpleNamespace(tick=lambda _fps: None),
    )


def _patch_drawing(monkeypatch):
    monkeypatch.setattr(
        "src.ui_pygame.gui.presentation_asset_screens.pygame.draw.rect", lambda *_a, **_k: None
    )
    monkeypatch.setattr(
        "src.ui_pygame.gui.presentation_asset_screens.pygame.draw.line", lambda *_a, **_k: None
    )
    monkeypatch.setattr(
        "src.ui_pygame.gui.presentation_asset_screens.pygame.display.flip", lambda: None
    )


def test_character_created_screen_draws_summary_and_accepts_keyboard(monkeypatch):
    _patch_drawing(monkeypatch)
    presenter = _make_presenter()
    portrait = pygame.Surface((225, 400), pygame.SRCALPHA)
    player = SimpleNamespace(
        name="Ada",
        race=SimpleNamespace(name="Elf"),
        sex="Female",
        cls=SimpleNamespace(name="Mage"),
        portrait_variant=2,
        health=SimpleNamespace(max=42),
        mana=SimpleNamespace(max=31),
    )
    manager = SimpleNamespace(get_portrait=lambda *args, **kwargs: portrait)
    screen = presentation_asset_screens.CharacterCreatedScreen(
        presenter, player, portrait_manager=manager
    )

    screen.draw()

    rendered = (
        presenter.title_font.render_calls
        + presenter.large_font.render_calls
        + presenter.normal_font.render_calls
        + presenter.small_font.render_calls
    )
    assert "Character Created" in rendered
    assert "Ready for Silvana" in rendered
    assert "Ada" in rendered
    assert "Elf" in rendered
    assert "Female" in rendered
    assert "Mage" in rendered
    assert "42" in rendered
    assert "31" in rendered
    assert any("1 Progression Point" in text for text in rendered)

    event_batches = iter([[SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)]])
    monkeypatch.setattr(
        "src.ui_pygame.gui.presentation_asset_screens.pygame.event.get",
        lambda: next(event_batches, []),
    )

    assert screen.show() is True


def test_character_created_screen_survives_portrait_fallback(monkeypatch):
    _patch_drawing(monkeypatch)
    presenter = _make_presenter()
    player = SimpleNamespace(
        name="Hero",
        race="Human",
        sex="Male",
        cls="Warrior",
        health=SimpleNamespace(max=20),
        mana=SimpleNamespace(max=10),
    )
    manager = SimpleNamespace(
        get_portrait=lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("missing"))
    )
    screen = presentation_asset_screens.CharacterCreatedScreen(
        presenter, player, portrait_manager=manager
    )

    screen.draw()

    assert screen.portrait is None
    assert presenter.screen.blit_calls


def test_story_card_sequence_advances_with_keyboard_mouse_and_can_skip(monkeypatch):
    _patch_drawing(monkeypatch)
    presenter = _make_presenter()
    sequence = presentation_asset_screens.StoryCardSequence(
        presenter,
        ["First page of the story.", "Second page of the story."],
        title="The Story Begins",
    )

    event_batches = iter(
        [
            [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_SPACE)],
            [SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=(450, 620))],
        ]
    )
    monkeypatch.setattr(
        "src.ui_pygame.gui.presentation_asset_screens.pygame.event.get",
        lambda: next(event_batches, []),
    )

    assert sequence.show() is True
    assert sequence.page_index == 1
    assert "The Story Begins" in presenter.title_font.render_calls
    assert "1/2" in presenter.small_font.render_calls
    assert "2/2" in presenter.small_font.render_calls

    skip_sequence = presentation_asset_screens.StoryCardSequence(
        presenter, ["Only page"], title="Skip Me"
    )
    event_batches = iter([[SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)]])
    monkeypatch.setattr(
        "src.ui_pygame.gui.presentation_asset_screens.pygame.event.get",
        lambda: next(event_batches, []),
    )

    assert skip_sequence.show() is False
