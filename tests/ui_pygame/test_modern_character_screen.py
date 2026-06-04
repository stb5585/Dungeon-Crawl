#!/usr/bin/env python3
"""Focused coverage for the parallel modern character menu."""

from __future__ import annotations

from types import SimpleNamespace

import pygame

from src.ui_pygame import game as pygame_game
from src.ui_pygame.gui.dungeon_manager import DungeonManager
from src.ui_pygame.gui.modern_character_screen import ModernCharacterScreen, RESISTANCE_ORDER


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

    def size(self, text):
        return (max(8, len(text) * 8), self._height)


class RecordingScreen:
    def __init__(self, size=(1000, 720)):
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

    def copy(self):
        return "screen-copy"


def _make_presenter():
    return SimpleNamespace(
        screen=RecordingScreen(),
        width=1000,
        height=720,
        title_font=RecordingFont(34),
        large_font=RecordingFont(28),
        normal_font=RecordingFont(22),
        small_font=RecordingFont(18),
        clock=SimpleNamespace(tick=lambda _fps: None),
        debug_mode=True,
    )


def _effect(active=True, duration=2, extra=0):
    return SimpleNamespace(active=active, duration=duration, extra=extra)


def _make_player():
    player = SimpleNamespace(
        name="Longnamed Hero of the Northern Gate",
        race=SimpleNamespace(name="Human"),
        sex="Female",
        cls=SimpleNamespace(name="Warrior"),
        level=SimpleNamespace(level=7, exp=250, exp_to_gain=50),
        health=SimpleNamespace(current=45, max=60),
        mana=SimpleNamespace(current=12, max=20),
        stats=SimpleNamespace(strength=14, intel=11, wisdom=10, con=13, charisma=9, dex=8),
        combat=SimpleNamespace(attack=10, defense=8, magic=3, magic_def=4),
        resistance={
            "Fire": -0.15,
            "Ice": -0.15,
            "Water": -0.15,
            "Poison": 0.2,
            "Physical": 0.1,
        },
        equipment={
            "Weapon": SimpleNamespace(name="Sword", damage=12, weight=4, description="Reliable steel."),
            "Armor": SimpleNamespace(name="Mail", armor=8, weight=12),
            "OffHand": None,
            "Ring": SimpleNamespace(name="Ruby Ring", mod="Block"),
            "Pendant": SimpleNamespace(name="Pendant of Sight", mod="Vision"),
        },
        buffs=[SimpleNamespace(name="Might"), SimpleNamespace(name="Might")],
        stat_effects={"Attack": _effect(True, 3, 4), "Speed": _effect(False)},
        magic_effects={"Regen": _effect(True, 2, 5)},
        class_effects={"Power Up": _effect(False)},
        status_effects={"Poison": _effect(True, 4, 2)},
        physical_effects={"Bleed": _effect(False)},
        spellbook={"Spells": {}, "Skills": {}},
        special_inventory={},
        sight=True,
    )
    player.current_weight = lambda: 19
    player.max_weight = lambda: 140
    player.critical_chance = lambda _slot: 0.125
    player.check_mod = lambda mod: {
        "weapon": 18,
        "offhand": 8,
        "armor": 22,
        "shield": 15,
        "magic def": 7,
        "magic": 9,
        "speed": 8,
    }.get(mod, 0)
    player.in_town = lambda: True
    return player


def test_modern_character_tabs_are_generic_and_switchable():
    screen = ModernCharacterScreen(_make_presenter())

    assert [tab.label for tab in screen.tabs] == ["Character", "Equipment"]
    assert screen.active_tab.key == "character"
    assert abs(screen.character_panel_rect.width - screen.combat_panel_rect.width) <= 1

    screen.move_tab(1)
    assert screen.active_tab.key == "equipment"

    screen.move_tab(1)
    assert screen.active_tab.key == "character"


def test_modern_character_summary_helpers_cover_xp_equipment_resistances_and_effects():
    screen = ModernCharacterScreen(_make_presenter())
    player = _make_player()

    assert screen.xp_progress(player) == 250 / 300
    assert screen.xp_label(player) == "250 XP / 50 next"

    player.level.exp_to_gain = "MAX"
    assert screen.xp_progress(player) == 1.0
    assert screen.xp_label(player) == "250 XP / MAX level"
    player.level.exp_to_gain = 50

    summary = dict(screen.build_character_summary(player))
    assert summary["Race"] == "Human"
    assert summary["Class"] == "Warrior"
    assert screen.portrait_filename(player) == "human_female.png"

    player.race = SimpleNamespace(name="Half Elf")
    player.sex = "Male"
    assert screen.portrait_filename(player) == "halfelf_male.png"
    player.race = SimpleNamespace(name="Human")
    player.sex = "Female"

    combat = dict(screen.build_combat_stats(player))
    assert combat["HP"] == "45/60"
    assert combat["Attack"] == "18"
    assert combat["Magic Defense"] == "7"
    assert combat["Critical"] == "12.5%"
    assert combat["Weight"] == "19/140"

    player.equipment["OffHand"] = SimpleNamespace(name="Dagger", typ="Weapon", subtyp="Dagger")
    combat = dict(screen.build_combat_stats(player))
    assert combat["Attack"] == "18/8"
    player.equipment["OffHand"] = None

    slots = screen.build_equipment_slots(player)
    assert [slot.slot for slot in slots] == ["Weapon", "Armor", "Helmet", "OffHand", "Ring", "Pendant"]
    helmet = next(slot for slot in slots if slot.slot == "Helmet")
    assert helmet.implemented is False
    assert helmet.item_name == "(future slot)"

    grouped_resistances = screen.group_resistances(player)
    assert [entry.name for entry in grouped_resistances["weaknesses"]] == ["Fire", "Ice", "Water"]
    assert [entry.name for entry in grouped_resistances["resistances"]] == ["Poison", "Physical"]

    equipment_buffs = screen.collect_equipment_buffs(player)
    assert [(buff.name, buff.source) for buff in equipment_buffs] == [
        ("Block", "Ring: Ruby Ring"),
        ("Vision", "Pendant: Pendant of Sight"),
    ]


def test_modern_character_draw_all_renders_active_tabs(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()

    monkeypatch.setattr(screen, "draw_semi_transparent_panel", lambda rect, alpha=180: DummySurface((rect.width, rect.height)))
    draw_rect_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.draw.rect", lambda *_args, **_kwargs: draw_rect_calls.append((_args, _kwargs)))
    draw_line_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.draw.line", lambda *_args, **_kwargs: draw_line_calls.append((_args, _kwargs)))
    flip_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.display.flip", lambda: flip_calls.append(True))

    screen.draw_all(player)
    rendered_text = set(presenter.large_font.render_calls + presenter.normal_font.render_calls + presenter.small_font.render_calls)
    assert "Character" in presenter.large_font.render_calls
    assert "Combat Stats" in presenter.large_font.render_calls
    assert "Core Attributes" in presenter.large_font.render_calls
    assert "Strength" in presenter.large_font.render_calls
    assert "RACE" in presenter.normal_font.render_calls
    assert "CLASS" in presenter.normal_font.render_calls
    assert "Human" in presenter.large_font.render_calls
    assert "Warrior" in presenter.large_font.render_calls
    assert "HP" in rendered_text
    assert "Weaknesses" in presenter.large_font.render_calls
    assert "Resistances" in presenter.large_font.render_calls
    assert "Fire (-15%)" in rendered_text
    assert "Equipment" not in presenter.large_font.render_calls
    assert "XP EARNED" not in presenter.small_font.render_calls
    assert "XP TO NEXT" not in presenter.small_font.render_calls
    assert "250 XP / 50 next" in presenter.small_font.render_calls
    assert len(draw_line_calls) >= 2
    assert flip_calls

    screen.select_tab("equipment")
    screen.draw_all(player, do_flip=False)
    assert "Equipment" in presenter.large_font.render_calls
    assert "Equipment Layout" not in presenter.large_font.render_calls
    assert "Item Details" not in presenter.normal_font.render_calls
    assert "Equipment Buffs" in presenter.normal_font.render_calls
    assert {"Helmet", "Weapon", "Armor", "OffHand", "Ring", "Pendant"}.issubset(set(presenter.normal_font.render_calls))
    assert "Sword" in presenter.normal_font.render_calls
    assert "Block: Ring: Ruby Ring  |  Vision: Pendant: Pendant of Sight" in presenter.small_font.render_calls


def test_modern_character_resistance_columns_render_all_possible_entries(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()
    player.resistance = {name: -0.1 for name in RESISTANCE_ORDER}

    monkeypatch.setattr(screen, "draw_semi_transparent_panel", lambda rect, alpha=180: DummySurface((rect.width, rect.height)))
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.draw.rect", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.draw.line", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.display.flip", lambda: None)

    screen.draw_all(player)
    rendered_text = set(presenter.normal_font.render_calls + presenter.small_font.render_calls)
    for name in RESISTANCE_ORDER:
        assert f"{name} (-10%)" in rendered_text


def test_modern_character_navigation_switches_tabs_and_exits(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()

    event_batches = iter([
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2)],
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
    ])
    monkeypatch.setattr(screen, "draw_all", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: [])
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.event.get", lambda: next(event_batches, []))

    assert screen.navigate(player) == "Exit Menu"
    assert screen.active_tab.key == "equipment"


def test_modern_character_menu_actions_remove_quit_and_put_exit_last(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()

    event_batches = iter([[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]])
    monkeypatch.setattr(screen, "draw_all", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: [])
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.event.get", lambda: next(event_batches, []))

    assert screen.navigate(player) == "Exit Menu"
    assert screen.menu_options == ["Inventory", "Change Equipment", "Quests", "Key Items", "Specials", "Exit Menu"]
    assert "Quit Game" not in screen.menu_options


def test_town_character_info_uses_modern_screen_by_default(monkeypatch):
    used = []

    class FakeModern:
        def __init__(self, _presenter):
            used.append("modern")

        def navigate(self, _player):
            return "Exit Menu"

    game = pygame_game.PygameGame.__new__(pygame_game.PygameGame)
    game.presenter = SimpleNamespace()
    game.player_char = SimpleNamespace(quit=False)
    monkeypatch.setattr(pygame_game, "ModernCharacterScreen", FakeModern)

    game.show_character_info()

    assert used == ["modern"]


def test_dungeon_character_screen_router_lazy_loads_modern_default(monkeypatch):
    created = []

    class FakeModern:
        def __init__(self, presenter):
            self.presenter = presenter
            self.background = None
            created.append(self)

    import src.ui_pygame.gui.modern_character_screen as modern_module

    monkeypatch.setattr(modern_module, "ModernCharacterScreen", FakeModern)

    manager = DungeonManager.__new__(DungeonManager)
    manager.presenter = SimpleNamespace()
    manager.game = SimpleNamespace()
    manager.modern_character_screen = None
    manager._dungeon_background = "dungeon-bg"

    first = manager._get_character_screen()
    second = manager._get_character_screen()

    assert first is second
    assert first.background == "dungeon-bg"
    assert created == [first]
