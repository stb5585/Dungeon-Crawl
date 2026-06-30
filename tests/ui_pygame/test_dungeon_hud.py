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
    draw_ellipse_calls = []
    draw_polygon_calls = []

    def font_factory(*_args, **_kwargs):
        if seeded_fonts:
            return seeded_fonts.pop(0)
        return RecordingFont()

    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.font.Font", font_factory)
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.draw.rect", lambda *_args, **_kwargs: draw_rect_calls.append((_args, _kwargs)))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.draw.line", lambda *_args, **_kwargs: draw_line_calls.append((_args, _kwargs)))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.draw.circle", lambda *_args, **_kwargs: draw_circle_calls.append((_args, _kwargs)))
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.draw.ellipse", lambda *_args, **_kwargs: draw_ellipse_calls.append((_args, _kwargs)))
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
        draw_ellipse_calls=draw_ellipse_calls,
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
        evasive_guard_stacks=2,
        spellbook={"Skills": {"Maelstrom Weapon": object(), "Evasive Guard": object()}},
        status_effects={"Poison": _effect(), "Steal Success": _effect()},
        physical_effects={"Prone": _effect()},
        stat_effects={"Attack": _effect(extra=1), "Defense": _effect(extra=-1)},
        magic_effects={
            "Regen": _effect(),
            "Jump": _effect(),
            "Duplicates": _effect(),
            "Totem": _effect(),
            "Astral Shift": _effect(),
        },
        class_effects={"Blessing": _effect()},
        world_dict={},
        familiar=None,
        summons={},
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
    assert ("ATK2", True) in icons
    assert ("DEF", False) in icons
    assert ("DEF", True) in icons
    assert ("REG", True) in icons
    assert ("TOT", True) not in icons
    assert ("AST", True) in icons
    assert ("BLE", True) in icons
    assert ("MW2", True) in icons
    assert ("EG2", True) in icons
    assert icons.index(("PRN", False)) < icons.index(("REG", True))

    player.status_effects["Blind Rage"] = SimpleNamespace(active=True)
    assert ("BRG", False) in hud._collect_status_icons(player)

    player.class_effects["Attack"] = _effect()
    icons = hud._collect_status_icons(player)
    assert ("ATK3", True) in icons

    player.stat_effects["Magic"] = _effect(extra=0)
    assert ("MAG", True) not in hud._collect_status_icons(player)
    assert ("MAG", False) not in hud._collect_status_icons(player)

    player.magic_effects["DOT"] = _effect()
    player.magic_effects["DOT"].source = "Slot Machine"
    assert ("DOT", False) in hud._collect_status_icons(player)

    player.magic_effects["DOT"].source = "Burn"
    assert ("BRN", False) in hud._collect_status_icons(player)

    player.spellbook = {"Skills": {}}
    assert ("MW2", True) not in hud._collect_status_icons(player)
    assert ("EG2", True) not in hud._collect_status_icons(player)

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

    assert y == 132
    assert any(text.startswith("+") for text in font.render_calls)
    colors = [args[1] for args, _kwargs in bundle.draw_rect_calls if len(args) > 1]
    assert hud.status_colors["overflow"] in colors
    assert hud.status_colors["urgent_negative"] in colors


def test_status_art_icons_render_without_badge_background_in_hud(monkeypatch):
    bundle = _make_hud(monkeypatch)
    hud = bundle.hud
    font = RecordingFont()
    icon_surface = DummySurface((14, 14), text="stun-icon")
    icon_sizes = []
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.font.Font", lambda *_args, **_kwargs: font)
    monkeypatch.setattr(
        "src.ui_pygame.gui.dungeon_hud.load_status_icon_surface",
        lambda _label, size, _is_positive=None: icon_sizes.append(size) or icon_surface,
    )
    player = _make_player()
    player.status_effects = {"Stun": _effect()}
    player.physical_effects = {}
    player.stat_effects = {}
    player.magic_effects = {}
    player.class_effects = {}
    player.maelstrom_hits = 0
    player.evasive_guard_stacks = 0

    hud._render_status_icons(player, 100)

    assert font.render_calls == []
    assert bundle.draw_rect_calls == []
    assert icon_sizes == [(24, 24)]
    assert any(surface is icon_surface for surface, _position in bundle.screen.blit_calls)


def test_counted_art_status_icons_render_badge_over_icon_in_hud(monkeypatch):
    bundle = _make_hud(monkeypatch)
    hud = bundle.hud
    font = RecordingFont()
    icon_surface = DummySurface((14, 14), text="maelstrom-icon")
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.font.Font", lambda *_args, **_kwargs: font)
    monkeypatch.setattr(
        "src.ui_pygame.gui.dungeon_hud.load_status_icon_surface",
        lambda _label, _size, _is_positive=None: icon_surface,
    )
    player = _make_player()
    player.status_effects = {}
    player.physical_effects = {}
    player.stat_effects = {}
    player.magic_effects = {}
    player.class_effects = {}
    player.maelstrom_hits = 5
    player.spellbook = {"Skills": {"Maelstrom Weapon": object()}}

    hud._render_status_icons(player, 100)

    blitted_text = [getattr(surface, "text", "") for surface, _position in bundle.screen.blit_calls]
    assert "maelstrom-icon" in blitted_text
    assert "5" in blitted_text
    assert bundle.draw_circle_calls


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

    assert y == 132
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

    player.location_z = 2
    assert hud.location_label(player) == "Dungeon Level 2"
    player.location_z = dungeon_hud.REALM_OF_CAMBION_LEVEL
    assert hud.location_label(player) == "Realm of Cambion"
    player.location_z = dungeon_hud.LIMINAL_GAP_LEVEL
    assert hud.location_label(player) == "Liminal Gap"
    y5 = hud._render_location_label(player, y4)
    assert y5 > y4
    assert "Liminal Gap" in bundle.small_font.render_calls


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
        (28, 30, 2): ChestTile(),
    }

    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.map_tiles.chalice_altar_visible", lambda _player: True)
    monkeypatch.setattr("src.ui_pygame.gui.dungeon_hud.pygame.time.get_ticks", lambda: 0)

    assert hud._is_direction_visible_from_tile(SimpleNamespace(blocked="north"), "north") is False
    assert hud._is_direction_visible_from_tile(SimpleNamespace(blocked="north", open=True), "north") is True
    assert hud._is_direction_visible_from_tile(DoorTile(open_state=False), "north") is False

    visible = hud._get_visible_adjacent_positions(player)
    assert (5, 6) in visible
    assert (6, 7) not in visible
    full_level_positions = hud._revealed_level_minimap_positions(player, visible)
    assert (28, 30) in full_level_positions

    y = hud._render_minimap(player, 120)
    assert y > 120
    assert bundle.draw_rect_calls
    assert bundle.draw_polygon_calls
    assert bundle.draw_circle_calls
    minimap_colors = [args[1] for args, _kwargs in bundle.draw_rect_calls if len(args) > 1]
    assert (255, 215, 0) in minimap_colors
    assert (255, 255, 110) in minimap_colors
    assert (255, 255, 255) in minimap_colors
    assert (220, 180, 80) in minimap_colors
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

    modal_rect = hud.render_enlarged_minimap_modal(player)
    assert modal_rect.width > hud.hud_width
    assert hud.last_minimap_rect is not None
    assert "Dungeon Level 2 Map" in bundle.stat_font.render_calls


def test_visible_adjacent_positions_require_enterable_and_hide_undiscovered_fake_walls(monkeypatch):
    bundle = _make_hud(monkeypatch)
    hud = bundle.hud

    class Floor:
        enter = True
        visited = True
        blocked = None

    class Wall:
        enter = False
        visited = False
        near = True
        blocked = None

    class FakeWall:
        enter = True
        visited = False
        blocked = None

    player = SimpleNamespace(location_x=2, location_y=2, location_z=1)
    player.world_dict = {
        (2, 2, 1): Floor(),
        (2, 1, 1): Floor(),
        (2, 3, 1): FakeWall(),
        (3, 2, 1): Wall(),
    }

    visible = hud._get_visible_adjacent_positions(player)

    assert (2, 1) in visible
    assert (2, 3) not in visible
    assert (3, 2) not in visible
    assert hud._minimap_tile_is_revealed(player, 3, 2, player.world_dict[(3, 2, 1)], visible) is True
    assert hud._minimap_tile_is_revealed(player, 2, 3, player.world_dict[(2, 3, 1)], visible) is False


def test_enlarged_minimap_modal_requests_full_level_map(monkeypatch):
    bundle = _make_hud(monkeypatch)
    hud = bundle.hud
    player = _make_player()
    full_level_flags = []

    monkeypatch.setattr(
        hud,
        "_render_minimap",
        lambda _player_char, _y, **kwargs: full_level_flags.append(kwargs.get("full_level")) or _y,
    )

    hud.render_enlarged_minimap_modal(player)

    assert full_level_flags == [True]


def test_combat_hud_replaces_minimap_with_class_focus_panel(monkeypatch):
    bundle = _make_hud(monkeypatch)
    hud = bundle.hud
    player = _make_player()
    feature_calls = []
    minimap_calls = []

    monkeypatch.setattr(hud, "_render_combat_indicator", lambda enemy, y: y + 10)
    monkeypatch.setattr(hud, "_render_character_info", lambda player_char, y: y + 120)
    monkeypatch.setattr(hud, "_render_resource_bars", lambda player_char, y: y + 70)
    monkeypatch.setattr(hud, "_render_status_icons", lambda player_char, y: y + 80)
    monkeypatch.setattr(
        hud,
        "_render_combat_features",
        lambda player_char, enemy, y, feature_height=None: feature_calls.append((y, feature_height, enemy.name)) or (y + feature_height),
    )
    monkeypatch.setattr(
        hud,
        "_render_minimap",
        lambda player_char, y, minimap_size=None: minimap_calls.append((y, minimap_size)) or (y + minimap_size),
    )

    hud.render_hud(player, combat_mode=True, enemy=SimpleNamespace(name="Orc"))

    feature_height = hud._combat_feature_height()
    assert feature_calls == [(hud._combat_feature_title_y(feature_height), feature_height, "Orc")]
    assert minimap_calls == []


def test_combat_focus_panel_shows_familiar_summons_and_totem(monkeypatch):
    bundle = _make_hud(monkeypatch)
    hud = bundle.hud
    player = _make_player()
    player.cls = SimpleNamespace(name="Soulcatcher")
    player.familiar = SimpleNamespace(name="Izulu", spec="Mephit", level=SimpleNamespace(level=3))
    player.summons = {
        "Fuath": SimpleNamespace(name="Fuath", is_alive=lambda: True),
        "Spent": SimpleNamespace(name="Spent", is_alive=lambda: False),
    }
    player.magic_effects["Totem"] = _effect(
        extra={"aspect": "Fire", "attack_bonus": 0.25, "defense_bonus": 0, "secondary": "elemental"}
    )
    player.magic_effects["Totem"].duration = 6

    lines = hud._combat_feature_lines(player, enemy=SimpleNamespace(name="Jester"))
    assert ("Class", "Soulcatcher", hud.text_color) in lines
    assert ("Familiar", "Izulu", (170, 210, 255)) in lines
    assert any(label == "Summons" and value == "Fuath" for label, value, _color in lines)
    assert ("Totem", "Fire Totem", (230, 205, 120)) in lines
    assert any(label == "Benefit" and "+25% ATK" in value and "Elemental" in value for label, value, _color in lines)
    assert ("Evasive Guard", "2 stack(s)", (170, 210, 255)) in lines

    player.cls = SimpleNamespace(name="Rogue")
    player._promotion_kit_combat = {"fortune": 2, "misfortune": 1}
    lines = hud._combat_feature_lines(player, enemy=SimpleNamespace(name="Jester"))
    assert ("Fortune", "2/3", (230, 205, 120)) in lines
    assert ("Misfortune", "1/3", (220, 150, 150)) in lines

    y = hud._render_combat_features(player, SimpleNamespace(name="Jester"), 120, feature_height=190)
    assert y > 120
    assert "Combat Focus" in bundle.stat_font.render_calls
    assert "Totem:" in bundle.small_font.render_calls
    assert bundle.draw_circle_calls

    bundle.screen.blit_calls = []
    guard_player = _make_player()
    hud._render_combat_features(guard_player, SimpleNamespace(name="Warrior"), 120, feature_height=190)
    rendered = [
        (getattr(surface, "text", ""), position, surface)
        for surface, position in bundle.screen.blit_calls
    ]
    guard_label = next(entry for entry in rendered if entry[0] == "Evasive Guard:")
    guard_value = next(entry for entry in rendered if entry[0] == "2 stack(s)")
    assert guard_value[1][0] >= guard_label[1][0] + guard_label[2].get_width() + 8


def test_render_hud_full_flow(monkeypatch):
    bundle = _make_hud(monkeypatch)
    hud = bundle.hud
    player = _make_player()
    calls = []

    monkeypatch.setattr(hud, "_render_combat_indicator", lambda enemy, y: calls.append(("combat", enemy.name if enemy else None, y)) or (y + 10))
    monkeypatch.setattr(hud, "_render_character_info", lambda player_char, y: calls.append(("info", player_char.name, y)) or (y + 10))
    monkeypatch.setattr(hud, "_render_resource_bars", lambda player_char, y: calls.append(("bars", player_char.name, y)) or (y + 10))
    monkeypatch.setattr(hud, "_render_location_label", lambda player_char, y: calls.append(("location", player_char.name, y)) or (y + 10))
    monkeypatch.setattr(hud, "_render_status_icons", lambda player_char, y: calls.append(("status", player_char.name, y)) or (y + 10))
    monkeypatch.setattr(
        hud,
        "_render_minimap",
        lambda player_char, y, **_kwargs: calls.append(("map", player_char.name, y)) or (y + 10),
    )
    monkeypatch.setattr(
        hud,
        "_render_combat_features",
        lambda player_char, enemy, y, **_kwargs: calls.append(("focus", player_char.name, y)) or (y + 10),
    )
    monkeypatch.setattr(hud, "_render_compass", lambda player_char, y: calls.append(("compass", player_char.name, y)) or (y + 10))

    hud.render_hud(player, combat_mode=True, enemy=SimpleNamespace(name="Orc"))
    assert [entry[0] for entry in calls] == ["combat", "info", "bars", "status", "focus"]

    calls.clear()
    hud.render_hud(player, combat_mode=False, enemy=None)
    assert [entry[0] for entry in calls] == ["info", "location", "bars", "compass", "map"]
