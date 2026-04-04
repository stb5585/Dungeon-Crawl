#!/usr/bin/env python3
"""Focused coverage for pygame level-up flow helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pygame

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


class DummyPopup:
    def __init__(self, presenter, payload):
        self.presenter = presenter
        self.payload = payload
        self.show_calls = []

    def show(self, **kwargs):
        self.show_calls.append(kwargs)
        return None


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


def _make_player(*, level=3, in_town=False, max_level=False):
    familiar = SimpleNamespace(level_up=lambda: "Familiar grew stronger")
    jump_skill = SimpleNamespace(
        name="Jump",
        get_max_active_modifications=lambda character: 1 if character.level.level < 4 else 2,
        check_and_unlock_level_modifications=lambda new_level, cls_name: ["Dive Bomb"] if new_level == 4 else [],
    )
    totem_skill = SimpleNamespace(
        name="Totem",
        check_and_unlock_aspects=lambda new_level: ["Storm"] if new_level == 4 else [],
    )
    player = SimpleNamespace(
        stats=SimpleNamespace(con=12, intel=10, strength=14, wisdom=11, charisma=9, dex=8),
        cls=SimpleNamespace(name="Mage", att_plus=4, def_plus=2, int_plus=6, wis_plus=4),
        health=SimpleNamespace(current=20, max=50),
        mana=SimpleNamespace(current=5, max=25),
        combat=SimpleNamespace(attack=7, defense=5, magic=8, magic_def=6),
        level=SimpleNamespace(level=level, exp_to_gain=100, pro_level=2),
        spellbook={"Spells": {}, "Skills": {"Jump": jump_skill, "Totem": totem_skill}},
        familiar=familiar,
        exp_scale=2,
    )
    player.check_mod = lambda _name, luck_factor=0: 1 if luck_factor == 8 else 2
    player.in_town = lambda: in_town
    player.max_level = lambda: max_level
    return player


def test_show_level_up_captures_background_and_triggers_optional_stat_pick(monkeypatch):
    fonts = iter([RecordingFont(), RecordingFont(), RecordingFont(), RecordingFont()])
    monkeypatch.setattr("src.ui_pygame.gui.level_up.pygame.font.Font", lambda *_args, **_kwargs: next(fonts))
    screen = RecordingScreen()
    presenter = _make_presenter()
    presenter.screen = screen
    ui = level_up.LevelUpScreen(screen, presenter)

    popup_calls = []

    class FakeLevelUpPopup:
        def __init__(self, presenter_arg, level_info):
            popup_calls.append((presenter_arg, level_info))

        def show(self, **kwargs):
            popup_calls.append(kwargs)

    stat_calls = []
    monkeypatch.setattr(level_up, "LevelUpPopup", FakeLevelUpPopup)
    monkeypatch.setattr(ui, "_calculate_level_up", lambda _player: {"new_level": 4})
    monkeypatch.setattr(ui, "_get_background_surface", lambda: "background")
    monkeypatch.setattr(ui, "_select_stat_increase", lambda player: stat_calls.append(player))

    player = _make_player(level=4)
    level_info = ui.show_level_up(player, SimpleNamespace())
    assert level_info == {"new_level": 4}
    assert ui._popup_background == "background"
    assert popup_calls[0][1] == {"new_level": 4}
    assert "background_draw_func" in popup_calls[1]
    assert stat_calls == [player]

    stat_calls.clear()
    player = _make_player(level=3)
    ui.show_level_up(player, SimpleNamespace())
    assert stat_calls == []


def test_calculate_level_up_applies_gains_and_discovers_abilities(monkeypatch):
    fonts = iter([RecordingFont(), RecordingFont(), RecordingFont(), RecordingFont()])
    monkeypatch.setattr("src.ui_pygame.gui.level_up.pygame.font.Font", lambda *_args, **_kwargs: next(fonts))
    ui = level_up.LevelUpScreen(RecordingScreen(), _make_presenter())

    randint_values = iter([8, 6, 2, 1, 3, 2])
    monkeypatch.setattr("src.ui_pygame.gui.level_up.random.randint", lambda _a, _b: next(randint_values))

    from src.core import abilities

    class BaseSpell:
        def __init__(self):
            self.name = "Spark"

    class UpgradedSpell(BaseSpell):
        def __init__(self):
            self.name = "Spark II"

    class BaseSkill:
        def __init__(self):
            self.name = "Slash"

    class UpgradedSkill(BaseSkill):
        def __init__(self):
            self.name = "Slash II"

    class BaseFamiliarSkill:
        def __init__(self):
            self.name = "Scout"

    class FamiliarSkill(BaseFamiliarSkill):
        def __init__(self):
            self.name = "Familiar"

    old_spell_dict = abilities.spell_dict
    old_skill_dict = abilities.skill_dict
    monkeypatch.setattr(abilities, "spell_dict", {"Mage": {"4": UpgradedSpell}})
    monkeypatch.setattr(abilities, "skill_dict", {"Mage": {"4": FamiliarSkill, "5": UpgradedSkill}})

    try:
        player = _make_player(level=3, in_town=True, max_level=False)
        player.spellbook["Spells"]["Spark"] = BaseSpell()
        info = ui._calculate_level_up(player)

        assert player.health.max == 58
        assert player.mana.max == 31
        assert player.health.current == 58
        assert player.mana.current == 31
        assert player.combat.attack == 9
        assert player.combat.defense == 6
        assert player.combat.magic == 11
        assert player.combat.magic_def == 8
        assert player.level.level == 4
        assert "Spark upgraded to Spark II" in info["spell_upgrades"]
        assert "Skill: Familiar" in info["new_abilities"] or "Familiar: Familiar grew stronger" in info["new_abilities"]
        assert "Familiar: Familiar grew stronger" in info["new_abilities"]
        assert "Jump: Can now equip 2 modifications (was 1)" in info["new_abilities"]
        assert "Jump Modification: Dive Bomb" in info["new_abilities"]
        assert "Totem Aspect: Storm" in info["new_abilities"]
        assert "Familiar" in player.spellbook["Skills"]
        assert player.level.exp_to_gain == 116

        randint_values = iter([5, 4, 1, 1, 1, 1])
        monkeypatch.setattr("src.ui_pygame.gui.level_up.random.randint", lambda _a, _b: next(randint_values))
        player = _make_player(level=4, in_town=False, max_level=True)
        player.spellbook["Skills"]["Slash"] = BaseSkill()
        info = ui._calculate_level_up(player)
        assert "Slash upgraded to Slash II" in info["skill_upgrades"]
        assert "Slash" not in player.spellbook["Skills"]
        assert "Slash II" in player.spellbook["Skills"]
        assert player.level.exp_to_gain == "MAX"
    finally:
        monkeypatch.setattr(abilities, "spell_dict", old_spell_dict)
        monkeypatch.setattr(abilities, "skill_dict", old_skill_dict)


def test_calculate_level_up_handles_special_skill_effects_and_max_paths(monkeypatch):
    fonts = iter([RecordingFont(), RecordingFont(), RecordingFont(), RecordingFont()])
    monkeypatch.setattr("src.ui_pygame.gui.level_up.pygame.font.Font", lambda *_args, **_kwargs: next(fonts))
    ui = level_up.LevelUpScreen(RecordingScreen(), _make_presenter())

    from src.core import abilities

    class BaseDrainSkill:
        def __init__(self):
            self.name = "Drain"

    class DrainSkill(BaseDrainSkill):
        def __init__(self):
            self.name = "Health/Mana Drain"

    class BaseTransformSkill:
        def __init__(self):
            self.name = "Shift"

    class TransformSkill(BaseTransformSkill):
        def __init__(self):
            self.name = "Transform"

        def use(self, _player):
            return "Beast form unlocked"

    old_skill_dict = abilities.skill_dict
    monkeypatch.setattr(abilities, "skill_dict", {"Mage": {"4": DrainSkill, "5": TransformSkill}})

    try:
        randint_values = iter([5, 5, 1, 1, 1, 1])
        monkeypatch.setattr("src.ui_pygame.gui.level_up.random.randint", lambda _a, _b: next(randint_values))
        player = _make_player(level=3)
        player.spellbook["Skills"]["Health Drain"] = SimpleNamespace(name="Health Drain")
        player.spellbook["Skills"]["Mana Drain"] = SimpleNamespace(name="Mana Drain")
        info = ui._calculate_level_up(player)
        assert "Health Drain" not in player.spellbook["Skills"]
        assert "Mana Drain" not in player.spellbook["Skills"]
        assert "Health/Mana Drain" in player.spellbook["Skills"]

        randint_values = iter([4, 4, 0, 0, 0, 0])
        monkeypatch.setattr("src.ui_pygame.gui.level_up.random.randint", lambda _a, _b: next(randint_values))
        player = _make_player(level=4)
        info = ui._calculate_level_up(player)
        assert "Beast form unlocked" in info["new_abilities"]
    finally:
        monkeypatch.setattr(abilities, "skill_dict", old_skill_dict)


def test_display_stat_selection_background_and_confirmation_helpers(monkeypatch):
    title_font = RecordingFont()
    header_font = RecordingFont()
    stat_font = RecordingFont()
    small_font = RecordingFont()
    fonts = iter([title_font, header_font, stat_font, small_font])
    monkeypatch.setattr("src.ui_pygame.gui.level_up.pygame.font.Font", lambda *_args, **_kwargs: next(fonts))
    flip_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.level_up.pygame.display.flip", lambda: flip_calls.append(True))

    screen = RecordingScreen()
    presenter = _make_presenter()
    presenter.screen = screen
    ui = level_up.LevelUpScreen(screen, presenter)

    level_info = {
        "new_level": 8,
        "health_gain": 5,
        "mana_gain": 4,
        "attack_gain": 1,
        "defense_gain": 0,
        "magic_gain": 2,
        "magic_def_gain": 0,
        "new_abilities": ["Spell: Nova"],
        "spell_upgrades": ["Spark upgraded to Spark II"],
        "skill_upgrades": [],
    }
    ui._display_level_up_info(_make_player(), level_info)
    assert screen.fill_calls[-1] == ui.bg_color
    assert "LEVEL UP!" in title_font.render_calls
    assert "Stats Gained:" in header_font.render_calls
    assert "Health: +5" in stat_font.render_calls
    assert "New Abilities:" in header_font.render_calls
    assert "Upgrades:" in header_font.render_calls
    assert flip_calls

    class FakeStatSelectionPopup:
        def __init__(self, presenter_arg, stat_options):
            self.presenter_arg = presenter_arg
            self.stat_options = stat_options

        def show(self, **kwargs):
            assert "background_draw_func" in kwargs
            return "Dexterity"

    confirmations = []
    monkeypatch.setattr(level_up, "StatSelectionPopup", FakeStatSelectionPopup)
    monkeypatch.setattr(ui, "_show_stat_confirmation", lambda stat_name, stat_options: confirmations.append((stat_name, stat_options)))
    player = _make_player()
    before = player.stats.dex
    ui._select_stat_increase(player)
    assert player.stats.dex == before + 1
    assert confirmations and confirmations[0][0] == "Dexterity"

    monkeypatch.setattr(level_up, "StatSelectionPopup", lambda presenter_arg, stat_options: SimpleNamespace(show=lambda **_kwargs: None))
    unchanged = player.stats.strength
    ui._select_stat_increase(player)
    assert player.stats.strength == unchanged

    presenter.get_background_surface = lambda: SimpleNamespace(copy=lambda: "presenter-bg")
    assert ui._get_background_surface() == "presenter-bg"
    presenter.get_background_surface = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    assert ui._get_background_surface() == "screen-copy"

    ui._popup_background = None
    ui._draw_popup_background()
    assert screen.blit_calls[-1] == ("screen-copy", (0, 0))
    ui._draw_level_up_background(player)
    assert screen.blit_calls[-1] == ("screen-copy", (0, 0))

    confirmations.clear()
    show_calls = []

    class FakeConfirmationPopup:
        def __init__(self, presenter_arg, message, show_buttons=False):
            confirmations.append((presenter_arg, message, show_buttons))

        def show(self, **kwargs):
            show_calls.append(kwargs)

    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.ConfirmationPopup", FakeConfirmationPopup)
    level_up.LevelUpScreen._show_stat_confirmation(ui, "Strength", [("Strength", 11), ("Dexterity", 8)])
    assert confirmations[0][1] == "Strength increased to 12!"
    assert "background_draw_func" in show_calls[0]

    event_batches = iter([[SimpleNamespace(type=pygame.KEYDOWN)], []])
    monkeypatch.setattr("src.ui_pygame.gui.level_up.pygame.event.get", lambda: next(event_batches, []))
    ui._wait_for_continue()
