#!/usr/bin/env python3
"""Focused coverage for dungeon HUD helpers and rendering."""

from __future__ import annotations

from types import SimpleNamespace

import pygame

from src.ui_pygame.gui import dungeon_hud
from src.ui_pygame.gui.status_icons import prioritize_status_icons


class DummySurface:
    def __init__(self, size=(64, 24), text=None):
        self._size = size
        self.text = text
        self.alpha = None
        self.fill_calls = []

    def get_width(self):
        return self._size[0]

    def get_height(self):
        return self._size[1]

    def get_rect(self, **kwargs):
        rect = pygame.Rect(0, 0, *self._size)
        for key, value in kwargs.items():
            setattr(rect, key, value)
        return rect

    def set_alpha(self, value):
        self.alpha = value

    def fill(self, color):
        self.fill_calls.append(color)


class RecordingFont:
    def __init__(self):
        self.render_calls = []

    def render(self, text, _antialias, _color):
        self.render_calls.append(text)
        return DummySurface((max(8, len(text) * 8), 20), text=text)


class RecordingScreen:
    def __init__(self, size=(900, 600)):
        self._size = size
        self.blit_calls = []
        self.fill_calls = []

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))

    def fill(self, color):
        self.fill_calls.append(color)

    def get_width(self):
        return self._size[0]

    def get_height(self):
        return self._size[1]


def _make_hud(monkeypatch):
    title_font = RecordingFont()
    stat_font = RecordingFont()
    small_font = RecordingFont()
    seeded_fonts = [title_font, stat_font, small_font]
    draw_rect_calls = []
    draw_line_calls = []
    draw_circle_calls = []
    draw_polygon_calls = []

    def font_factory(*_args, **_kwargs):
        if seeded_fonts:
            return seeded_fonts.pop(0)
        return RecordingFont()

    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.font.Font", font_factory)
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.draw.rect", lambda *_args, **_kwargs: draw_rect_calls.append((_args, _kwargs)))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.draw.line", lambda *_args, **_kwargs: draw_line_calls.append((_args, _kwargs)))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.draw.circle", lambda *_args, **_kwargs: draw_circle_calls.append((_args, _kwargs)))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.draw.polygon", lambda *_args, **_kwargs: draw_polygon_calls.append((_args, _kwargs)))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.Surface", lambda size, *_args, **_kwargs: DummySurface(size))

    presenter = SimpleNamespace(screen=RecordingScreen(), width=900, height=600)
    hud = dungeon_hud.DungeonHUD(presenter)
    return SimpleNamespace(
        hud=hud,
        screen=presenter.screen,
        title_font=title_font,
        stat_font=stat_font,
        small_font=small_font,
        draw_rect_calls=draw_rect_calls,
        draw_line_calls=draw_line_calls,
        draw_circle_calls=draw_circle_calls,
        draw_polygon_calls=draw_polygon_calls,
    )


def _effect(active=True, extra=0):
    return SimpleNamespace(active=active, extra=extra)


def _make_player():
    player = SimpleNamespace(
        name="Hero",
        race=SimpleNamespace(name="Human"),
        cls=SimpleNamespace(name="Warrior"),
        level=SimpleNamespace(level=5, exp_to_gain=20),
        health=SimpleNamespace(current=40, max=50),
        mana=SimpleNamespace(current=10, max=20),
        stats=SimpleNamespace(strength=12, intel=11, wisdom=10, con=13, dex=9, charisma=8),
        gold=123,
        location_x=5,
        location_y=7,
        location_z=2,
        facing="north",
        equipment={"Pendant": SimpleNamespace(mod="None")},
        sight=False,
        maelstrom_hits=2,
        spellbook={"Skills": {"Maelstrom Weapon": object()}},
        status_effects={"Poison": _effect(), "Steal Success": _effect()},
        physical_effects={"Prone": _effect()},
        stat_effects={"Attack": _effect(extra=1), "Defense": _effect(extra=-1)},
        magic_effects={"Regen": _effect(), "Jump": _effect(), "Duplicates": _effect()},
        class_effects={"Blessing": _effect()},
        world_dict={},
    )
    player.level_exp = lambda: 100
    return player


def test_effect_and_status_icon_helpers(monkeypatch):
    bundle = _make_hud(monkeypatch)
    hud = bundle.hud
    player = _make_player()

    assert hud._effect_label("Resist Fire") == "RF"
    assert hud._effect_label("Mystery") == "MYS"

    icons = hud._collect_status_icons(player)
    assert ("PSN", False) in icons
    assert ("PRN", False) in icons
    assert ("ATK", True) in icons
    assert ("DEF", False) in icons
    assert ("REG", True) in icons
    assert ("BLE", True) in icons
    assert ("MW2", True) in icons
    assert icons.index(("PRN", False)) < icons.index(("REG", True))

    player.class_effects["Attack"] = _effect()
    icons = hud._collect_status_icons(player)
    assert ("ATK2", True) in icons

    player.spellbook = {"Skills": {}}
    assert ("MW2", True) not in hud._collect_status_icons(player)

    y = hud._render_status_icons(_make_player(), 100)
    assert y > 100
    assert bundle.screen.blit_calls


def test_status_icons_compact_overflow_in_combat_hud(monkeypatch):
    bundle = _make_hud(monkeypatch)
    hud = bundle.hud
    font = RecordingFont()
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.font.Font", lambda *_args, **_kwargs: font)

    icons = prioritize_status_icons(
        [
            ("ATK", True),
            ("REG", True),
            ("PSN", False),
            ("STN", False),
            ("MSH", True),
            ("PRN", False),
            ("BLE", True),
            ("MW2", True),
        ]
    )

    assert icons[:3] == [("STN", False), ("PRN", False), ("PSN", False)]

    y = hud._render_status_icons(_make_player(), 100, max_rows=1)

    assert y == 124
    assert any(text.startswith("+") for text in font.render_calls)
    colors = [args[1] for args, _kwargs in bundle.draw_rect_calls if len(args) > 1]
    assert hud.status_colors["overflow"] in colors
    assert hud.status_colors["urgent_negative"] in colors


def test_dense_combat_hud_status_icons_keep_urgent_counts_and_overflow(monkeypatch):
    bundle = _make_hud(monkeypatch)
    hud = bundle.hud
    font = RecordingFont()
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.font.Font", lambda *_args, **_kwargs: font)
    player = _make_player()
    player.status_effects.update({
        "Stun": _effect(),
        "Poison": _effect(),
        "Sleep": _effect(),
        "Silence": _effect(),
        "Prone": _effect(),
    })
    player.physical_effects.update({
        "Stun": _effect(),
        "Prone": _effect(),
        "Disarm": _effect(),
    })
    player.stat_effects.update({
        "Magic": _effect(extra=2),
        "Speed": _effect(extra=1),
    })
    player.magic_effects.update({
        "Mana Shield": _effect(),
        "Reflect": _effect(),
        "Resist Fire": _effect(),
    })

    icons = hud._collect_status_icons(player)
    assert icons[:4] == [("STN2", False), ("SLP", False), ("SIL", False), ("PRN2", False)]

    y = hud._render_status_icons(player, 100, max_rows=1)

    assert y == 124
    assert font.render_calls[:4] == ["STN2", "SLP", "SIL", "PRN2"]
    assert any(text.startswith("+") for text in font.render_calls)
    colors = [args[1] for args, _kwargs in bundle.draw_rect_calls if len(args) > 1]
    assert hud.status_colors["urgent_negative"] in colors
    assert hud.status_colors["overflow"] in colors


def test_character_info_resource_bars_stats_and_quick_info(monkeypatch):
    bundle = _make_hud(monkeypatch)
    hud = bundle.hud
    player = _make_player()

    y = hud._render_character_info(player, 20)
    assert y > 20
    assert "Hero" in bundle.title_font.render_calls
    assert "Human Warrior" in bundle.stat_font.render_calls
    assert "Level 5" in bundle.stat_font.render_calls
    assert "80/100 XP" in bundle.small_font.render_calls

    player.level.exp_to_gain = "MAX"
    hud._render_character_info(player, 20)
    assert "MAX LEVEL" in bundle.small_font.render_calls

    y2 = hud._render_resource_bars(player, y)
    assert y2 > y
    assert "HP: 40/50" in bundle.stat_font.render_calls
    assert "MP: 10/20" in bundle.stat_font.render_calls

    y3 = hud._render_stats(player, y2)
    assert y3 > y2
    assert "Stats" in bundle.stat_font.render_calls
    assert "STR: 12" in bundle.small_font.render_calls

    y4 = hud._render_quick_info(player, y3)
    assert y4 > y3
    assert "Gold: 123" in bundle.small_font.render_calls
    assert "Depth: Level 2" in bundle.small_font.render_calls

    player.location_z = 0
    hud._render_quick_info(player, y3)
    assert "Depth: Town" in bundle.small_font.render_calls


def test_visibility_helpers_minimap_compass_and_combat_indicator(monkeypatch):
    bundle = _make_hud(monkeypatch)
    hud = bundle.hud
    player = _make_player()

    class DoorTile:
        def __init__(self, open_state):
            self.open = open_state
            self.enter = True
            self.visited = True
            self.near = True

    class ChestTile:
        def __init__(self, open_state=False):
            self.enter = True
            self.visited = True
            self.near = True
            self.open = open_state

    class StairsDownTile:
        enter = True
        visited = True
        near = True

    class RelicRoom:
        enter = True
        visited = True
        near = True
        read = True

    class GoldenChaliceRoom:
        enter = True
        visited = False
        near = True
        read = False

    class SecretShopTile:
        enter = True
        visited = True
        near = True

    class WarpPointTile:
        enter = True
        visited = True
        near = True

    class UndergroundSpringTile:
        enter = True
        visited = True
        near = True

    class WallTile:
        enter = False
        visited = True
        near = False
        blocked = None

    player.world_dict = {
        (5, 7, 2): DoorTile(open_state=True),
        (5, 6, 2): ChestTile(),
        (6, 7, 2): DoorTile(open_state=False),
        (7, 7, 2): ChestTile(open_state=True),
        (4, 7, 2): SecretShopTile(),
        (5, 8, 2): WarpPointTile(),
        (5, 9, 2): DoorTile(open_state=True),
        (4, 6, 2): UndergroundSpringTile(),
        (6, 6, 2): StairsDownTile(),
        (4, 8, 2): RelicRoom(),
        (6, 8, 2): GoldenChaliceRoom(),
        (3, 7, 2): WallTile(),
    }

    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.map_tiles.chalice_altar_visible", lambda _player: True)

    assert hud._is_direction_visible_from_tile(SimpleNamespace(blocked="north"), "north") is False
    assert hud._is_direction_visible_from_tile(SimpleNamespace(blocked="north", open=True), "north") is True
    assert hud._is_direction_visible_from_tile(DoorTile(open_state=False), "north") is False

    visible = hud._get_visible_adjacent_positions(player)
    assert (5, 6) in visible
    assert (6, 7) not in visible

    y = hud._render_minimap(player, 120)
    assert y > 120
    assert bundle.draw_rect_calls
    assert bundle.draw_polygon_calls
    assert bundle.draw_circle_calls
    minimap_colors = [args[1] for args, _kwargs in bundle.draw_rect_calls if len(args) > 1]
    assert (255, 215, 0) in minimap_colors
    assert (130, 130, 120) in minimap_colors
    assert (95, 170, 120) in minimap_colors
    assert (139, 69, 19) in minimap_colors

    y2 = hud._render_compass(player, y)
    assert y2 > y
    assert "N" in bundle.small_font.render_calls
    assert bundle.draw_line_calls

    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.time.get_ticks", lambda: 250)
    y3 = hud._render_combat_indicator(SimpleNamespace(name="Goblin"), y2)
    assert y3 > y2


def test_render_hud_full_flow(monkeypatch):
    bundle = _make_hud(monkeypatch)
    hud = bundle.hud
    player = _make_player()
    calls = []

    monkeypatch.setattr(hud, "_render_combat_indicator", lambda enemy, y: calls.append(("combat", enemy.name if enemy else None, y)) or (y + 10))
    monkeypatch.setattr(hud, "_render_character_info", lambda player_char, y: calls.append(("info", player_char.name, y)) or (y + 10))
    monkeypatch.setattr(hud, "_render_resource_bars", lambda player_char, y: calls.append(("bars", player_char.name, y)) or (y + 10))
    monkeypatch.setattr(hud, "_render_status_icons", lambda player_char, y: calls.append(("status", player_char.name, y)) or (y + 10))
    monkeypatch.setattr(hud, "_render_minimap", lambda player_char, y: calls.append(("map", player_char.name, y)) or (y + 10))
    monkeypatch.setattr(hud, "_render_compass", lambda player_char, y: calls.append(("compass", player_char.name, y)) or (y + 10))

    hud.render_hud(player, combat_mode=True, enemy=SimpleNamespace(name="Orc"))
    assert [entry[0] for entry in calls] == ["combat", "info", "bars", "status", "map"]

    calls.clear()
    hud.render_hud(player, combat_mode=False, enemy=None)
    assert [entry[0] for entry in calls] == ["info", "bars", "map", "compass"]
