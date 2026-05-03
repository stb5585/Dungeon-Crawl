#!/usr/bin/env python3
"""Focused coverage for pygame combat-view helpers and overlays."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import sys

import pygame
import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

from src.ui_pygame.gui import combat_view
from src.ui_pygame.gui.status_icons import prioritize_status_icons


@pytest.fixture(autouse=True)
def _init_pygame():
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    yield


class DummyScreen:
    def __init__(self, size=(900, 600)):
        self._size = size
        self.blit_calls = []
        self.fill_calls = []

    def get_width(self):
        return self._size[0]

    def get_height(self):
        return self._size[1]

    def blit(self, surface, position, *args, **kwargs):
        self.blit_calls.append((surface, position, args, kwargs))

    def fill(self, color, rect=None):
        self.fill_calls.append((color, rect))

    def copy(self):
        return DummySurface(self._size)


class DummySurface:
    def __init__(self, size=(64, 64), text=None):
        self._size = size
        self.text = text
        self.alpha = None
        self.fill_calls = []
        self.blit_calls = []

    def get_size(self):
        return self._size

    def copy(self):
        return DummySurface(self._size, self.text)

    def get_width(self):
        return self._size[0]

    def get_height(self):
        return self._size[1]

    def set_alpha(self, value):
        self.alpha = value

    def fill(self, color):
        self.fill_calls.append(color)

    def blit(self, surface, position, *args, **kwargs):
        self.blit_calls.append((surface, position, args, kwargs))

    def get_rect(self, **kwargs):
        rect = pygame.Rect(0, 0, *self._size)
        for key, value in kwargs.items():
            setattr(rect, key, value)
        return rect

    def convert_alpha(self):
        return self


class RecordingFont:
    def __init__(self):
        self.render_calls = []
        self.color_calls = []

    def size(self, text):
        return (max(8, len(text) * 8), 20)

    def render(self, text, _antialias, _color):
        self.render_calls.append(text)
        self.color_calls.append((text, _color))
        return DummySurface((max(8, len(text) * 8), 20), text=text)


class DummyClock:
    def __init__(self, frame_ms=80):
        self.frame_ms = frame_ms
        self.ticks = []

    def tick(self, fps):
        self.ticks.append(fps)

    def get_time(self):
        return self.frame_ms


def _make_view():
    screen = DummyScreen()
    presenter = SimpleNamespace()
    return combat_view.CombatView(screen, presenter)


def _effect(active=True, extra=0):
    return SimpleNamespace(active=active, extra=extra)


def _make_character():
    return SimpleNamespace(
        name="Hero",
        cls=SimpleNamespace(name="Warrior"),
        equipment={"Pendant": SimpleNamespace(mod="None")},
        sight=False,
        health=SimpleNamespace(current=40, max=50),
        mana=SimpleNamespace(current=10, max=15),
        encumbered=False,
        status_effects={"Berserk": _effect(), "Steal Success": _effect()},
        physical_effects={"Prone": _effect()},
        stat_effects={"Attack": _effect(extra=2), "Defense": _effect(extra=-1)},
        magic_effects={"Totem": _effect(), "Regen": _effect(), "Jump": _effect()},
        class_effects={"Power Chant": _effect()},
    )


def test_sprite_animator_lifecycle_and_tint():
    animator = combat_view.SpriteAnimator()
    still_alive = animator.update(30)
    assert still_alive is None
    assert animator.frame in (0, 1)
    assert animator.bob_offset != 0 or animator.sway_offset != 0

    animator.trigger_damage()
    assert animator.damage_flash == 1.0

    animator.trigger_death()
    assert animator.animation_type == "death"
    animator.update(60)
    assert animator.is_dead is True
    assert animator.death_progress == 1.0

    surface = DummySurface((20, 20))
    tinted = animator.apply_tint(surface, (255, 0, 0), 0.5)
    assert tinted is not surface
    assert tinted.blit_calls
    assert animator.apply_tint(surface, (255, 0, 0), 0) is surface


def test_combat_log_filters_scrolls_and_status_helpers():
    view = _make_view()

    view.add_combat_message("Hero attacks!\nHero is affected by poison\nAlready stunned\nEnemy resists the spell\nNext line")
    assert view.combat_log == ["Hero attacks!", "Next line"]

    view.combat_log = [f"Line {i}" for i in range(8)]
    view.log_scroll_offset = 3
    view.scroll_log(-10)
    assert view.log_scroll_offset == 0
    view.scroll_log(99)
    assert view.log_scroll_offset == view._max_log_scroll()
    view.reset_combat_log()
    assert view.combat_log == []
    assert view.log_scroll_offset == 0

    assert view._effect_label("Resist Fire") == "RF"
    assert view._effect_label("Mystery") == "MYS"

    icons = view._collect_status_icons(_make_character())
    assert ("ATK", True) in icons
    assert ("DEF", True) in icons
    assert ("BRK", False) in icons
    assert ("PRN", False) in icons
    assert ("REG", True) in icons
    assert icons.index(("PRN", False)) < icons.index(("REG", True))


def test_combat_log_wraps_long_charge_messages(monkeypatch):
    view = _make_view()
    font = RecordingFont()

    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.font.Font", lambda *_args, **_kwargs: font)
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.draw.rect", lambda *_args, **_kwargs: None)

    message = "Goblin is lowering their head and building momentum for a devastating charge that needs wrapping."
    view.add_combat_message(message)

    assert len(view.combat_log) > 1

    view._render_combat_log()

    assert len(font.render_calls) > 1
    assert all(font.size(text)[0] <= view.combat_width - 30 for text in font.render_calls)

    font.render_calls.clear()
    view.combat_log = [
        "Goblin is lowering their head and building momentum for a devastating overlay charge that must fit the narrower dungeon combat pane."
    ]
    view._render_combat_log_overlay()
    overlay_width = int(view.screen_width * 0.65) - 30
    assert len(font.render_calls) > 1
    assert all(font.size(text)[0] <= overlay_width for text in font.render_calls)


def test_turn_indicator_renders_player_and_enemy_states(monkeypatch):
    view = _make_view()
    player = SimpleNamespace(name="Hero")
    enemy = SimpleNamespace(name="Goblin")
    fonts = iter([RecordingFont(), RecordingFont(), RecordingFont(), RecordingFont(), RecordingFont(), RecordingFont(), RecordingFont(), RecordingFont()])
    rect_calls = []
    circle_calls = []

    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.font.Font", lambda *_args, **_kwargs: next(fonts))
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.draw.rect", lambda *_args, **_kwargs: rect_calls.append((_args, _kwargs)))
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.draw.circle", lambda *_args, **_kwargs: circle_calls.append((_args, _kwargs)))
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.Surface", lambda size, *_args, **_kwargs: DummySurface(size))

    view._render_turn_indicator(player, enemy, current_turn="player")
    view._render_turn_indicator(player, enemy, current_turn="enemy", overlay=True)
    view._render_turn_indicator(player, enemy, current_turn=None)

    rendered_text = [
        getattr(surface, "text", "")
        for surface, _pos, _args, _kwargs in view.screen.blit_calls
        if getattr(surface, "text", "")
    ]
    colors = [args[1] for args, _kwargs in rect_calls if len(args) > 1]

    assert "Your Turn" in rendered_text
    assert "Enemy Turn" in rendered_text
    assert "Goblin" in rendered_text
    assert view.colors["turn_player"] in colors
    assert view.colors["turn_enemy"] in colors
    assert circle_calls


def test_render_combat_does_not_default_to_player_turn(monkeypatch):
    view = _make_view()
    player = _make_character()
    enemy = SimpleNamespace(name="Goblin")
    recorded_turns = []

    monkeypatch.setattr(view, "update_animations", lambda: None)
    monkeypatch.setattr(view.screen, "fill", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(view, "_render_enemy", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(view, "_render_turn_indicator", lambda *_args, **kwargs: recorded_turns.append(kwargs.get("current_turn")))
    monkeypatch.setattr(view, "_render_telegraph_banner", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(view, "_render_player_status", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(view, "_render_action_menu", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(view, "_render_combat_log", lambda *_args, **_kwargs: None)

    view.render_combat(player, enemy, actions=[])

    assert recorded_turns == [None]


def test_telegraph_banner_uses_latest_matching_log_line(monkeypatch):
    view = _make_view()
    fonts = iter([RecordingFont(), RecordingFont(), RecordingFont(), RecordingFont(), RecordingFont(), RecordingFont()])
    rect_calls = []

    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.font.Font", lambda *_args, **_kwargs: next(fonts))
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.draw.rect", lambda *_args, **_kwargs: rect_calls.append((_args, _kwargs)))
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.draw.circle", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.Surface", lambda size, *_args, **_kwargs: DummySurface(size))

    view.combat_log = [
        "Goblin attacks.",
        "Goblin is lowering their head and building momentum!",
        "Hero blocks.",
    ]

    view._render_telegraph_banner(overlay=False)
    view._render_telegraph_banner(overlay=True)

    rendered_text = [
        getattr(surface, "text", "")
        for surface, _pos, _args, _kwargs in view.screen.blit_calls
        if getattr(surface, "text", "")
    ]

    assert "Telegraph" in rendered_text
    assert any("lowering their head" in text for text in rendered_text)
    assert any(args[1] == view.colors["telegraph"] for args, _kwargs in rect_calls if len(args) > 1)


def test_sprite_loading_reload_and_sight_rules(monkeypatch):
    view = _make_view()
    enemy = SimpleNamespace(name="Invisible Stalker", picture="invisible_stalker.txt")
    loaded = []

    monkeypatch.setattr("src.ui_pygame.gui.combat_view.os.path.exists", lambda path: str(path).endswith("_hidden.png"))
    monkeypatch.setattr(
        "src.ui_pygame.gui.combat_view.pygame.image.load",
        lambda path: loaded.append(path) or DummySurface((32, 32)),
    )

    sprite = view._get_enemy_sprite(enemy, has_sight=False)
    assert isinstance(sprite, DummySurface)
    assert loaded and loaded[0].endswith("invisible_stalker_hidden.png")

    loaded.clear()
    assert view._get_enemy_sprite(enemy, has_sight=False) is sprite
    assert loaded == []

    view.reload_enemy_sprite(enemy)
    assert "invisible_stalker_hidden" not in view.sprite_cache

    loaded.clear()
    palette_enemy = SimpleNamespace(name="Jester", picture="jester3.png")
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.os.path.exists", lambda path: str(path).endswith("jester3.png"))
    sprite = view._get_enemy_sprite(palette_enemy, has_sight=True)
    assert isinstance(sprite, DummySurface)
    assert loaded and loaded[0].endswith("jester3.png")

    loaded.clear()
    legacy_picture_enemy = SimpleNamespace(name="Giant Rat", picture="giantrat.txt")
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.os.path.exists", lambda path: str(path).endswith("giant_rat.png"))
    sprite = view._get_enemy_sprite(legacy_picture_enemy, has_sight=True)
    assert isinstance(sprite, DummySurface)
    assert loaded and loaded[0].endswith("giant_rat.png")

    player = _make_character()
    assert view._has_sight(player) is False
    player.cls.name = "Seeker"
    assert view._has_sight(player) is True
    player.cls.name = "Warrior"
    player.equipment["Pendant"].mod = "Vision"
    assert view._has_sight(player) is True
    player.equipment["Pendant"].mod = "None"
    player.sight = True
    assert view._has_sight(player) is True


def test_render_helpers_cover_icons_player_status_and_logs(monkeypatch):
    view = _make_view()
    font_small = RecordingFont()
    font_medium = RecordingFont()
    font_large = RecordingFont()
    fonts = [
        font_small,
        font_medium,
        font_large,
        RecordingFont(),
        RecordingFont(),
        RecordingFont(),
        RecordingFont(),
        RecordingFont(),
        RecordingFont(),
        RecordingFont(),
    ]

    monkeypatch.setattr(
        "src.ui_pygame.gui.combat_view.pygame.font.Font",
        lambda *_args, **_kwargs: fonts.pop(0) if fonts else RecordingFont(),
    )
    rect_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.draw.rect", lambda *_args, **_kwargs: rect_calls.append((_args, _kwargs)))

    view._render_status_icons([("ATK", True), ("PSN", False), ("REG", True)], 10, 20, max_width=90)
    assert "ATK" in font_small.render_calls
    assert "PSN" in font_small.render_calls

    player = _make_character()
    player.encumbered = True
    view._render_player_status(player)
    combined = font_medium.render_calls + font_large.render_calls
    assert any(text.startswith("HP:") for text in combined)
    assert any("ENCUMBERED" in text for text in combined)

    view.combat_log = ["Line one", "Line two\nLine three"]
    view._render_combat_log()
    assert any("Line one" in call[0].text for call in view.screen.blit_calls if hasattr(call[0], "text"))

    view.combat_log = [f"Msg {i}" for i in range(9)]
    view.log_scroll_offset = 2
    fonts = [RecordingFont(), RecordingFont(), RecordingFont()]
    monkeypatch.setattr(
        "src.ui_pygame.gui.combat_view.pygame.font.Font",
        lambda *_args, **_kwargs: fonts.pop(0) if fonts else RecordingFont(),
    )
    view._render_combat_log_overlay()

    fonts = [RecordingFont(), RecordingFont()]
    monkeypatch.setattr(
        "src.ui_pygame.gui.combat_view.pygame.font.Font",
        lambda *_args, **_kwargs: fonts.pop(0) if fonts else RecordingFont(),
    )
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.Surface", lambda size, *_args, **_kwargs: DummySurface(size))
    view._render_action_menu_overlay(["Attack", "Skills", "Items"], 1)
    assert rect_calls


def test_status_icons_compact_overflow_and_telegraph_log_color(monkeypatch):
    view = _make_view()
    font = RecordingFont()
    rect_calls = []

    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.font.Font", lambda *_args, **_kwargs: font)
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.draw.rect", lambda *_args, **_kwargs: rect_calls.append((_args, _kwargs)))
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.Surface", lambda size, *_args, **_kwargs: DummySurface(size))

    icons = [(f"E{i}", i % 2 == 0) for i in range(6)]
    view._render_status_icons(icons, 10, 20, max_width=90, max_rows=2)

    assert font.render_calls == ["E0", "E1", "E2", "+3"]
    assert view.status_colors["overflow"] in [args[1] for args, _kwargs in rect_calls if len(args) > 1]

    normal_line = "Hero attacks."
    telegraph_line = "Goblin is lowering their head and building momentum!"
    font.render_calls.clear()
    font.color_calls.clear()
    view.combat_log = [telegraph_line, normal_line]
    view.log_scroll_offset = 0

    view._render_combat_log()
    assert (telegraph_line, view.colors["telegraph"]) in font.color_calls
    assert (normal_line, view.colors["text"]) in font.color_calls

    font.color_calls.clear()
    view._render_combat_log_overlay()
    assert (telegraph_line, view.colors["telegraph"]) in font.color_calls
    assert (normal_line, (240, 240, 240)) in font.color_calls


def test_status_icon_priority_keeps_urgent_effects_visible_before_overflow(monkeypatch):
    view = _make_view()
    font = RecordingFont()
    rect_calls = []

    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.font.Font", lambda *_args, **_kwargs: font)
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.draw.rect", lambda *_args, **_kwargs: rect_calls.append((_args, _kwargs)))

    icons = prioritize_status_icons(
        [
            ("ATK", True),
            ("REG", True),
            ("PSN", False),
            ("STN", False),
            ("MSH", True),
            ("PRN", False),
        ]
    )

    assert icons[:3] == [("STN", False), ("PRN", False), ("PSN", False)]

    view._render_status_icons(icons, 10, 20, max_width=90, max_rows=2)
    assert font.render_calls == ["STN", "PRN", "PSN", "+3"]
    colors = [args[1] for args, _kwargs in rect_calls if len(args) > 1]
    assert view.status_colors["urgent_negative"] in colors


def test_damage_flash_enemy_render_and_combat_render_paths(monkeypatch):
    view = _make_view()
    player = _make_character()
    enemy = SimpleNamespace(name="Goblin", health=SimpleNamespace(current=10, max=20), flying=False, tunnel=False)
    enemy.status_effects = {}
    enemy.physical_effects = {}
    enemy.stat_effects = {}
    enemy.magic_effects = {}
    enemy.class_effects = {}

    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.Surface", lambda size, *_args, **_kwargs: DummySurface(size))
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.event.get", lambda: [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PAGEUP), pygame.event.Event(pygame.QUIT)])
    quit_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.quit", lambda: quit_calls.append(True))
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.sys.exit", lambda _code=0: (_ for _ in ()).throw(SystemExit()))
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.time.Clock", lambda: DummyClock(frame_ms=80))

    with pytest.raises(SystemExit):
        view.show_damage_flash(True, event_handler=lambda event: view.scroll_log(-1) if event.type == pygame.KEYDOWN else None)
    assert quit_calls

    fonts = iter([RecordingFont(), RecordingFont(), RecordingFont(), RecordingFont(), RecordingFont()])
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.font.Font", lambda *_args, **_kwargs: next(fonts))
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.draw.circle", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.draw.rect", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.transform.scale", lambda surface, size: DummySurface(size))
    view._get_enemy_sprite = lambda _enemy, has_sight=False: None
    view._render_enemy(enemy, has_sight=True)

    enemy.tunnel = True
    view._render_enemy(enemy, has_sight=True)

    enemy.tunnel = False
    view._has_sight = lambda _player: True
    view._render_enemy = lambda _enemy, _has_sight=True: view.screen.blit(DummySurface((10, 10), text="enemy"), (0, 0))
    view._render_player_status = lambda _player: view.screen.blit(DummySurface((10, 10), text="player"), (0, 0))
    view._render_action_menu = lambda actions, selected: view.screen.blit(DummySurface((10, 10), text=f"menu:{selected}"), (0, 0))
    view._render_combat_log = lambda: view.screen.blit(DummySurface((10, 10), text="log"), (0, 0))
    view.render_combat(player, enemy, ["Attack", "Defend"], selected_action=1)
    assert any(getattr(surface, "text", "") == "menu:1" for surface, _pos, _args, _kwargs in view.screen.blit_calls)


def test_render_enemy_in_dungeon_draws_name_based_sprite_for_legacy_picture(monkeypatch):
    view = _make_view()
    player = _make_character()
    enemy = SimpleNamespace(
        name="Giant Rat",
        picture="giantrat.txt",
        health=SimpleNamespace(current=8, max=12),
        flying=False,
        tunnel=False,
        status_effects={},
        physical_effects={},
        stat_effects={},
        magic_effects={},
        class_effects={},
    )
    loaded = []
    scaled = []

    monkeypatch.setattr("src.ui_pygame.gui.combat_view.os.path.exists", lambda path: str(path).endswith("giant_rat.png"))
    monkeypatch.setattr(
        "src.ui_pygame.gui.combat_view.pygame.image.load",
        lambda path: loaded.append(path) or DummySurface((32, 32), text="source-enemy"),
    )
    monkeypatch.setattr(
        "src.ui_pygame.gui.combat_view.pygame.transform.scale",
        lambda surface, size: scaled.append((surface, size)) or DummySurface(size, text="scaled-enemy"),
    )
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.font.Font", lambda *_args, **_kwargs: RecordingFont())
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.draw.rect", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.combat_view.pygame.draw.circle", lambda *_args, **_kwargs: None)

    view.render_enemy_in_dungeon(player, enemy)

    assert loaded and loaded[0].endswith("giant_rat.png")
    assert scaled and scaled[0][1] == (320, 320)
    assert any(
        getattr(surface, "text", "") == "scaled-enemy"
        for surface, _pos, _args, _kwargs in view.screen.blit_calls
    )
