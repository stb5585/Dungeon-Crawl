#!/usr/bin/env python3
"""Focused coverage for character-screen helper and rendering behavior."""

from __future__ import annotations

from types import SimpleNamespace

import pygame

from src.ui_pygame.gui import character_screen


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
    def __init__(self, size=(900, 700)):
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
        width=900,
        height=700,
        title_font=RecordingFont(34),
        large_font=RecordingFont(28),
        normal_font=RecordingFont(22),
        small_font=RecordingFont(18),
        clock=SimpleNamespace(tick=lambda _fps: None),
        debug_mode=True,
    )


def _make_player():
    jump_skill = SimpleNamespace(name="Jump", modifications=["High Jump"])
    totem_skill = SimpleNamespace(name="Totem", get_unlocked_aspects=lambda _player=None: ["Flame"])
    virtue = SimpleNamespace(name="Mercy")
    sin = SimpleNamespace(name="Wrath")
    player = SimpleNamespace(
        name="Hero",
        race=SimpleNamespace(name="Human", virtue=virtue, sin=sin),
        cls=SimpleNamespace(name="Warrior"),
        level=SimpleNamespace(level=7, exp=250, exp_to_gain=50),
        health=SimpleNamespace(current=45, max=60),
        mana=SimpleNamespace(current=12, max=20),
        stats=SimpleNamespace(strength=14, intel=11, wisdom=10, con=13, charisma=9, dex=8),
        combat=SimpleNamespace(attack=10, defense=8),
        resistance={name: 0.1 for name in ["Fire", "Electric", "Earth", "Shadow", "Poison", "Ice", "Water", "Wind", "Holy", "Physical"]},
        gold=321,
        encumbered=True,
        location_z=2,
        spellbook={
            "Spells": {"Spark": SimpleNamespace(name="Spark")},
            "Skills": {"Jump": jump_skill, "Totem": totem_skill, "Slash": SimpleNamespace(name="Slash")},
        },
        quest_dict={"Main": {"Slay Beast": {}}, "Side": {"Find Ring": {}}},
        special_inventory={"Orb": [SimpleNamespace(name="Orb", description="A relic"), SimpleNamespace(name="Orb", description="A relic")]},
        equipment={
            "Weapon": SimpleNamespace(name="Sword"),
            "Armor": SimpleNamespace(name="Mail"),
            "OffHand": None,
            "Ring": SimpleNamespace(name="Ruby Ring"),
            "Pendant": SimpleNamespace(name="Pendant of Sight", mod="Vision"),
        },
        buffs=[SimpleNamespace(name="Might"), SimpleNamespace(name="Might"), SimpleNamespace(name="Shield")],
        specials=[],
    )
    player.current_weight = lambda: 55
    player.max_weight = lambda: 40
    player.critical_chance = lambda _slot: 0.125
    player.check_mod = lambda mod: {"shield": 15, "magic def": 7, "magic": 9, "heal": 4}.get(mod, 0)
    player.in_town = lambda: False
    return player


def test_character_screen_helper_lists_and_feature_checks():
    screen = character_screen.CharacterScreen(_make_presenter())
    player = _make_player()

    assert screen._get_jump_skill(player).name == "Jump"
    assert screen._has_jump_mods(player) is True
    assert screen._get_totem_skill(player).name == "Totem"
    assert screen._has_totem_aspects(player) is True

    quests = screen._get_quests_list(player)
    assert "[Main] Slay Beast" in quests
    assert "[Side] Find Ring" in quests

    key_items = screen._get_key_items_list(player)
    assert key_items[0]["text"] == "Orb (2)"
    assert key_items[0]["value"].name == "Orb"

    specials = screen._get_specials_list(player)
    assert specials[0] == "--- RACIAL TRAITS ---"
    assert any(getattr(entry, "name", "") == "Spark" for entry in specials)
    assert any(getattr(entry, "name", "") == "Slash" for entry in specials)

    empty_player = SimpleNamespace(quest_dict={}, quests=[], special_inventory={}, spellbook={"Spells": {}, "Skills": {}}, race=None, specials=[])
    assert screen._get_quests_list(empty_player) == ["No quests available"]
    assert screen._get_key_items_list(empty_player) == ["No key items"]
    assert screen._get_specials_list(empty_player) == ["No special abilities"]


def test_character_screen_draw_helpers_and_composition(monkeypatch):
    presenter = _make_presenter()
    screen = character_screen.CharacterScreen(presenter)
    player = _make_player()

    panel_calls = []
    monkeypatch.setattr(screen, "draw_semi_transparent_panel", lambda rect, alpha=180: panel_calls.append((rect, alpha)))
    draw_rect_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.character_screen.pygame.draw.rect", lambda *_args, **_kwargs: draw_rect_calls.append((_args, _kwargs)))
    flip_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.character_screen.pygame.display.flip", lambda: flip_calls.append(True))

    screen.draw_info(player)
    assert "Hero" in presenter.title_font.render_calls
    assert "Dungeon Level 2" in presenter.large_font.render_calls
    assert "ENCUMBERED" in presenter.small_font.render_calls
    assert "Human Warrior" in presenter.large_font.render_calls
    assert "Virtue: Mercy" in presenter.small_font.render_calls
    assert "Sin: Wrath" in presenter.small_font.render_calls
    assert "321G" in presenter.large_font.render_calls

    screen.draw_exp(player)
    assert "Level: 7" in presenter.large_font.render_calls
    assert "Experience: 250" in presenter.normal_font.render_calls
    assert "To Next Level: 50" in presenter.normal_font.render_calls

    screen.menu_options = ["Inventory", "Equipment", "Exit Menu", "Quit Game", "Key Items", "Specials"]
    screen.current_selection = 1
    screen.draw_menu()
    assert "Equipment" in presenter.large_font.render_calls

    screen.draw_stats(player)
    assert "Hit Points:" in presenter.large_font.render_calls
    assert "Critical Chance:" in presenter.large_font.render_calls
    assert "Equipped Gear" in presenter.large_font.render_calls
    assert "Weight/Max:" in presenter.large_font.render_calls
    assert "Resistances" in presenter.large_font.render_calls
    assert "Vision" in presenter.large_font.render_calls
    assert "Might" in presenter.large_font.render_calls
    assert "Shield" in presenter.large_font.render_calls

    draw_background_calls = []
    monkeypatch.setattr(screen, "draw_background", lambda: draw_background_calls.append(True))
    monkeypatch.setattr(screen, "draw_info", lambda player_char: panel_calls.append(("info", player_char.name)))
    monkeypatch.setattr(screen, "draw_menu", lambda: panel_calls.append(("menu", None)))
    monkeypatch.setattr(screen, "draw_stats", lambda player_char: panel_calls.append(("stats", player_char.name)))
    monkeypatch.setattr(screen, "draw_exp", lambda player_char: panel_calls.append(("exp", player_char.name)))
    screen.draw_all(player, do_flip=True)
    assert draw_background_calls
    assert ("info", "Hero") in panel_calls
    assert flip_calls


def test_empty_key_items_notice_uses_stale_input_guard(monkeypatch):
    presenter = _make_presenter()
    screen = character_screen.CharacterScreen(presenter)
    player = _make_player()
    player.special_inventory = {}
    player.spellbook = {"Spells": {}, "Skills": {}}
    player.in_town = lambda: False
    screen.current_selection = 4

    popup_kwargs = []

    class FakePopup:
        def __init__(self, _presenter, message, show_buttons=False):
            assert message == "You do not have any key items."
            assert show_buttons is False

        def show(self, **kwargs):
            popup_kwargs.append(kwargs)
            return True

    event_batches = iter([
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)],
        [pygame.event.Event(pygame.KEYUP, key=pygame.K_RETURN)],
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)],
        [pygame.event.Event(pygame.KEYUP, key=pygame.K_ESCAPE)],
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
    ])
    monkeypatch.setattr(screen, "draw_all", lambda *_args, **_kwargs: None)
    clear_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.character_screen.pygame.event.clear", lambda: clear_calls.append(True))
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.ConfirmationPopup", FakePopup)
    monkeypatch.setattr("src.ui_pygame.gui.character_screen.pygame.event.get", lambda: next(event_batches, []))

    assert screen.navigate(player) == "Exit Menu"
    assert popup_kwargs == [{"flush_events": True, "require_key_release": True}]
    assert clear_calls == [True]


def test_character_submenus_use_stale_input_guard(monkeypatch):
    guarded_kwargs_by_title = {}
    popup_classes = {}

    class FakePopup:
        def __init__(self, _presenter, _owner, title=None, **_kwargs):
            self.title = title or self.__class__.__name__

        def show(self, _player_char, **kwargs):
            guarded_kwargs_by_title[self.title] = kwargs
            return None

    def fake_popup_class(title):
        cls = type(title, (FakePopup,), {})
        popup_classes[title] = cls
        return cls

    monkeypatch.setattr(character_screen, "InventoryPopupMenu", fake_popup_class("Inventory"))
    monkeypatch.setattr(character_screen, "EquipmentPopupMenu", fake_popup_class("Equipment"))
    monkeypatch.setattr(character_screen, "SimpleListPopupMenu", FakePopup)
    monkeypatch.setattr(character_screen, "JumpModsPopupMenu", FakePopup)
    monkeypatch.setattr(character_screen, "TotemAspectsPopupMenu", FakePopup)

    import src.ui_pygame.gui.popup_menus as popup_menus

    monkeypatch.setattr(popup_menus, "QuestPopupMenu", fake_popup_class("Quests"))

    expected_guard = {"flush_events": True, "require_key_release": True}
    selections = {
        "Inventory": 0,
        "Equipment": 1,
        "Quests": 2,
        "Key Items": 4,
        "Special Abilities": 5,
        "Jump Modifications": 6,
        "Totem Aspects": 7,
    }

    for title, selection in selections.items():
        presenter = _make_presenter()
        screen = character_screen.CharacterScreen(presenter)
        player = _make_player()
        screen.current_selection = selection
        event_batches = iter([
            [pygame.event.Event(pygame.KEYUP, key=pygame.K_RETURN)],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)],
            [pygame.event.Event(pygame.KEYUP, key=pygame.K_ESCAPE)],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
        ])
        monkeypatch.setattr(screen, "draw_all", lambda *_args, **_kwargs: None)
        monkeypatch.setattr("src.ui_pygame.gui.character_screen.pygame.event.get", lambda: next(event_batches, []))

        assert screen.navigate(player) == "Exit Menu"
        assert guarded_kwargs_by_title[title] == expected_guard


def test_character_screen_navigation_can_opt_out_of_stale_input_guard(monkeypatch):
    presenter = _make_presenter()
    screen = character_screen.CharacterScreen(presenter)
    player = _make_player()

    clear_calls = []
    monkeypatch.setattr(screen, "draw_all", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.character_screen.pygame.event.clear", lambda: clear_calls.append(True))
    event_batches = iter([[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]])
    monkeypatch.setattr("src.ui_pygame.gui.character_screen.pygame.event.get", lambda: next(event_batches, []))

    assert screen.navigate(player, flush_events=False, require_key_release=False) == "Exit Menu"
    assert clear_calls == []
