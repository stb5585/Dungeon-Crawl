#!/usr/bin/env python3
"""Coverage for shared town-screen pygame helpers."""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

import pygame

from src.ui_pygame.gui import town_base


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


class RecordingScreen:
    def __init__(self):
        self.fill_calls = []
        self.blit_calls = []

    def fill(self, color):
        self.fill_calls.append(color)

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))


class RecordingTownScreen(town_base.TownScreenBase):
    def __init__(self, presenter):
        self.top_calls = 0
        self.options_calls = 0
        self.background_calls = 0
        super().__init__(presenter)

    def draw_background(self):
        self.background_calls += 1
        return super().draw_background()

    def draw_top(self):
        self.top_calls += 1

    def draw_options(self):
        self.options_calls += 1


def _make_presenter(*, debug_mode=False, screen=None):
    pygame.font.init()
    return SimpleNamespace(
        screen=screen or RecordingScreen(),
        width=640,
        height=480,
        title_font=pygame.font.Font(None, 32),
        large_font=pygame.font.Font(None, 24),
        normal_font=pygame.font.Font(None, 22),
        small_font=pygame.font.Font(None, 18),
        debug_mode=debug_mode,
        clock=SimpleNamespace(tick=lambda _fps: None),
    )


def test_load_background_scales_image_to_cover_screen(monkeypatch):
    presenter = _make_presenter()
    source = pygame.Surface((200, 100))
    scaled_sizes = []

    monkeypatch.setattr("src.ui_pygame.gui.town_base.os.path.exists", lambda _path: True)
    monkeypatch.setattr("src.ui_pygame.gui.town_base.pygame.image.load", lambda _path: source)

    def fake_scale(image, size):
        scaled_sizes.append((image.get_size(), size))
        return pygame.Surface(size)

    monkeypatch.setattr("src.ui_pygame.gui.town_base.pygame.transform.scale", fake_scale)

    base = town_base.TownScreenBase(presenter)

    assert scaled_sizes == [((200, 100), (960, 480))]
    assert base.background.get_size() == (960, 480)


def test_load_background_handles_missing_and_load_failures(monkeypatch, capsys):
    presenter = _make_presenter()

    monkeypatch.setattr("src.ui_pygame.gui.town_base.os.path.exists", lambda _path: False)
    missing = town_base.TownScreenBase(presenter)
    assert missing.background is None
    assert "Town background not found" in capsys.readouterr().out

    monkeypatch.setattr("src.ui_pygame.gui.town_base.os.path.exists", lambda _path: True)
    monkeypatch.setattr(
        "src.ui_pygame.gui.town_base.pygame.image.load",
        lambda _path: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    failed = town_base.TownScreenBase(presenter)
    assert failed.background is None
    assert "Could not load town background" in capsys.readouterr().out


def test_draw_background_and_panel_helpers(monkeypatch):
    screen = RecordingScreen()
    presenter = _make_presenter(screen=screen)
    monkeypatch.setattr("src.ui_pygame.gui.town_base.os.path.exists", lambda _path: False)
    base = town_base.TownScreenBase(presenter)

    base.draw_background()
    assert screen.fill_calls == [town_base.TownColors.BLACK]

    base.background = pygame.Surface((100, 80))
    base.draw_background()
    _surface, rect = screen.blit_calls[-1]
    assert rect.center == (presenter.width // 2, presenter.height // 2)

    panel = base.draw_semi_transparent_panel(pygame.Rect(10, 20, 30, 40), alpha=123)
    assert panel.get_size() == (30, 40)
    assert screen.blit_calls[-1][1] == (10, 20)


def test_display_quest_text_debug_mode_renders_full_text_and_exits(monkeypatch):
    pygame.init()
    pygame.display.set_mode((1, 1))
    presenter = _make_presenter(debug_mode=True, screen=pygame.Surface((640, 480), pygame.SRCALPHA))
    monkeypatch.setattr("src.ui_pygame.gui.town_base.os.path.exists", lambda _path: False)
    base = RecordingTownScreen(presenter)

    events = [SimpleNamespace(type=pygame.KEYDOWN)]
    monkeypatch.setattr("src.ui_pygame.gui.town_base.pygame.event.get", lambda: list(events))
    monkeypatch.setattr("src.ui_pygame.gui.town_base.pygame.display.flip", lambda: None)

    base.display_quest_text("====== Quest ======\nLine one\n\nLine two")

    assert base.background_calls == 1
    assert base.top_calls == 1
    assert base.options_calls == 1
    pygame.quit()


def test_display_quest_text_non_debug_supports_skip_and_advance(monkeypatch):
    pygame.init()
    pygame.display.set_mode((1, 1))
    presenter = _make_presenter(debug_mode=False, screen=pygame.Surface((640, 480), pygame.SRCALPHA))
    monkeypatch.setattr("src.ui_pygame.gui.town_base.os.path.exists", lambda _path: False)
    base = RecordingTownScreen(presenter)

    key_events = iter(
        [
            [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_SPACE)],
            [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
        ]
    )

    def fake_get():
        try:
            return next(key_events)
        except StopIteration:
            return []

    clear_calls = []
    tick_calls = []
    presenter.clock = SimpleNamespace(tick=lambda fps: tick_calls.append(fps))
    monkeypatch.setattr("src.ui_pygame.gui.town_base.pygame.event.get", fake_get)
    monkeypatch.setattr("src.ui_pygame.gui.town_base.pygame.event.clear", lambda event_type=None: clear_calls.append(event_type))
    monkeypatch.setattr("src.ui_pygame.gui.town_base.pygame.display.flip", lambda: None)
    monkeypatch.setattr("time.sleep", lambda _value: None)

    base.display_quest_text("====== Quest ======\nSkip me quickly")

    assert clear_calls == [pygame.KEYDOWN]
    assert base.background_calls >= 2
    assert base.top_calls >= 2
    assert base.options_calls >= 2
    assert tick_calls == []
    pygame.quit()
