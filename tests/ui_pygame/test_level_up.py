"""Focused coverage for the shared pygame level-up presentation."""

from __future__ import annotations

from types import SimpleNamespace

import pygame

from src.core.progression import GrowthResult, LevelUpResult
from src.ui_pygame.gui import level_up


class RenderedText:
    def __init__(self, text):
        self.text = text

    def get_rect(self, **kwargs):
        rect = pygame.Rect(0, 0, max(8, len(self.text) * 8), 20)
        for key, value in kwargs.items():
            setattr(rect, key, value)
        return rect


class RecordingFont:
    def __init__(self):
        self.render_calls = []

    def render(self, text, _antialias, _color):
        self.render_calls.append(text)
        return RenderedText(text)


class RecordingScreen:
    def __init__(self, size=(640, 480)):
        self._size = size
        self.blit_calls = []
        self.fill_calls = []

    def get_width(self):
        return self._size[0]

    def get_height(self):
        return self._size[1]

    def fill(self, color):
        self.fill_calls.append(color)

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))

    def copy(self):
        return "screen-copy"


def _make_presenter():
    return SimpleNamespace(
        screen=RecordingScreen(),
        width=640,
        height=480,
        title_font=RecordingFont(),
        header_font=RecordingFont(),
        normal_font=RecordingFont(),
        small_font=RecordingFont(),
        clock=SimpleNamespace(tick=lambda _fps: None),
    )


def _make_player(level=4):
    return SimpleNamespace(
        level=SimpleNamespace(level=level),
        _pending_level_up_result=None,
    )


def _make_ui(monkeypatch):
    fonts = iter([RecordingFont(), RecordingFont(), RecordingFont(), RecordingFont()])
    monkeypatch.setattr(
        "src.ui_pygame.gui.level_up.pygame.font.Font",
        lambda *_args, **_kwargs: next(fonts),
    )
    screen = RecordingScreen()
    presenter = _make_presenter()
    presenter.screen = screen
    return level_up.LevelUpScreen(screen, presenter), screen, presenter


def test_show_level_up_uses_shared_result_without_forced_stat_pick(monkeypatch):
    ui, _screen, presenter = _make_ui(monkeypatch)
    popup_calls = []

    class FakeLevelUpPopup:
        def __init__(self, presenter_arg, level_info):
            popup_calls.append((presenter_arg, level_info))

        def show(self, **kwargs):
            popup_calls.append(kwargs)

    monkeypatch.setattr(level_up, "LevelUpPopup", FakeLevelUpPopup)
    monkeypatch.setattr(ui, "_calculate_level_up", lambda _player: {"new_level": 4})
    monkeypatch.setattr(ui, "_get_background_surface", lambda: "background")

    info = ui.show_level_up(_make_player(), SimpleNamespace())

    assert info == {"new_level": 4}
    assert ui._popup_background == "background"
    assert popup_calls[0] == (presenter, {"new_level": 4})
    assert popup_calls[1]["background_draw_func"] is not None
    assert popup_calls[1]["flush_events"] is True
    assert popup_calls[1]["require_key_release"] is True


def test_calculate_level_up_consumes_pending_service_result(monkeypatch):
    ui, _screen, _presenter = _make_ui(monkeypatch)
    player = _make_player(level=4)
    player._pending_level_up_result = LevelUpResult(
        experience_awarded=100,
        old_level=3,
        new_level=4,
        points_awarded=1,
        growth=(
            GrowthResult(
                health=8,
                mana=6,
                attack=2,
                defense=1,
                magic=3,
                magic_defense=2,
            ),
        ),
        reached_max_level=False,
        attribute_points_awarded=1,
    )

    info = ui._calculate_level_up(player)

    assert info == {
        "new_level": 4,
        "health_gain": 8,
        "mana_gain": 6,
        "attack_gain": 2,
        "defense_gain": 1,
        "magic_gain": 3,
        "magic_def_gain": 2,
        "new_abilities": [
            "+1 progression point",
            "+1 attribute point",
        ],
        "spell_upgrades": [],
        "skill_upgrades": [],
    }
    assert player._pending_level_up_result is None


def test_calculate_level_up_reports_multiple_points(monkeypatch):
    ui, _screen, _presenter = _make_ui(monkeypatch)
    player = _make_player(level=6)
    player._pending_level_up_result = LevelUpResult(
        experience_awarded=200,
        old_level=4,
        new_level=6,
        points_awarded=2,
        growth=(
            GrowthResult(health=0, mana=0, attack=0, defense=0, magic=0, magic_defense=0),
            GrowthResult(health=0, mana=0, attack=0, defense=0, magic=0, magic_defense=0),
        ),
        reached_max_level=False,
    )

    info = ui._calculate_level_up(player)

    assert info["new_abilities"] == ["+2 progression points"]
    assert info["spell_upgrades"] == []
    assert info["skill_upgrades"] == []


def test_background_helpers_prefer_presenter_surface(monkeypatch):
    ui, screen, presenter = _make_ui(monkeypatch)
    presenter.get_background_surface = lambda: SimpleNamespace(copy=lambda: "presenter-bg")
    assert ui._get_background_surface() == "presenter-bg"

    presenter.get_background_surface = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    assert ui._get_background_surface() == "screen-copy"

    ui._popup_background = None
    ui._draw_popup_background()
    assert screen.blit_calls[-1] == ("screen-copy", (0, 0))


def test_wait_for_continue_accepts_key_or_quit(monkeypatch):
    ui, _screen, _presenter = _make_ui(monkeypatch)
    event_batches = iter([[SimpleNamespace(type=pygame.KEYDOWN)]])
    monkeypatch.setattr(
        "src.ui_pygame.gui.level_up.pygame.event.get",
        lambda: next(event_batches),
    )

    ui._wait_for_continue()
