#!/usr/bin/env python3
"""Focused coverage for church manager helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pygame

from src.ui_pygame.gui import church


class FakePopup:
    messages = []
    show_kwargs = []

    def __init__(self, _presenter, message, show_buttons=False, **_kwargs):
        self.message = message
        FakePopup.messages.append(message)

    def show(self, **kwargs):
        FakePopup.show_kwargs.append(kwargs)
        return True


def _make_player():
    return SimpleNamespace(
        name="Ada Hero",
        quest_dict={"Main": {}, "Bounty": {}},
        gold=0,
        familiar=None,
        summons={},
        cls=SimpleNamespace(name="Warrior", equipment={}),
        race=SimpleNamespace(cls_res={"First": []}),
        level=SimpleNamespace(level=10, pro_level=1, exp_to_gain=10),
        spellbook={"Spells": {}, "Skills": {}},
        equipment={},
        level_exp=lambda: 42,
        save=lambda filepath=None: None,
        unequip=lambda promo=False: None,
        equip=lambda slot, item, check=True: None,
    )


def _make_presenter():
    pygame.font.init()
    return SimpleNamespace(
        screen=object(),
        width=900,
        height=700,
        title_font=pygame.font.Font(None, 30),
        large_font=pygame.font.Font(None, 26),
        normal_font=pygame.font.Font(None, 22),
        small_font=pygame.font.Font(None, 18),
        clock=SimpleNamespace(tick=lambda _fps: None),
        render_menu=lambda *_args, **_kwargs: None,
        show_message=lambda *_args, **_kwargs: None,
        get_text_input=lambda *_args, **_kwargs: "Buddy",
        debug_mode=False,
    )


def test_visit_church_routes_actions(monkeypatch):
    FakePopup.messages = []
    FakePopup.show_kwargs = []
    player = _make_player()
    presenter = _make_presenter()
    monkeypatch.setattr(church.ChurchManager, "_load_background", lambda self: setattr(self, "background", None))
    monkeypatch.setattr("src.ui_pygame.gui.church.ConfirmationPopup", FakePopup)
    manager = church.ChurchManager(presenter, player)

    calls = []
    manager.handle_promotion = lambda: calls.append("promotion")
    manager.save_game = lambda: calls.append("save")

    selections = iter([0, 1, 2, 3])
    rendered = []

    class FakeLocationMenuScreen:
        def __init__(self, _presenter, _title):
            pass

        def navigate(self, _options, reset_cursor=False):
            return next(selections)

        def display_quest_text(self, text):
            rendered.append(text)

    class FakeQuestManager:
        def __init__(self, _presenter, _player, quest_text_renderer):
            self.quest_text_renderer = quest_text_renderer

        def check_and_offer(self, patron):
            self.quest_text_renderer(f"{patron} quest")

    monkeypatch.setattr("src.ui_pygame.gui.church.LocationMenuScreen", FakeLocationMenuScreen)
    monkeypatch.setattr("src.ui_pygame.gui.church.QuestManager", FakeQuestManager)

    manager.visit_church()

    assert calls == ["promotion", "save"]
    assert rendered == ["Priest quest"]
    assert "Let the light of Elysia guide you." in FakePopup.messages
    assert FakePopup.show_kwargs[-1]["flush_events"] is True
    assert FakePopup.show_kwargs[-1]["require_key_release"] is True
    assert callable(FakePopup.show_kwargs[-1]["background_draw_func"])


def test_handle_promotion_guards_and_save_game(monkeypatch):
    FakePopup.messages = []
    FakePopup.show_kwargs = []
    player = _make_player()
    presenter = _make_presenter()
    monkeypatch.setattr(church.ChurchManager, "_load_background", lambda self: setattr(self, "background", None))
    monkeypatch.setattr("src.ui_pygame.gui.church.ConfirmationPopup", FakePopup)
    manager = church.ChurchManager(presenter, player)

    player.level.level = 20
    manager.handle_promotion()
    assert "You need to be level 30 before you can promote your character." in FakePopup.messages
    assert FakePopup.show_kwargs[-1]["flush_events"] is True
    assert FakePopup.show_kwargs[-1]["require_key_release"] is True

    player.level.level = 30
    player.level.pro_level = 3
    manager.handle_promotion()
    assert "You are at max promotion level" in FakePopup.messages[-1]

    player.level.pro_level = 1
    monkeypatch.setattr("src.ui_pygame.gui.church.classes_dict", {})
    manager.handle_promotion()
    assert "No promotion options are currently available." in FakePopup.messages[-1]

    save_paths = []
    monkeypatch.setattr("src.ui_pygame.gui.church.os.path.exists", lambda _path: True)
    player.save = lambda filepath=None: save_paths.append(filepath)
    manager.save_game()
    assert save_paths == ["save_files/ada_hero.save"]
    assert "Game saved successfully!" in FakePopup.messages[-1]

    player.save = lambda filepath=None: (_ for _ in ()).throw(RuntimeError("disk full"))
    manager.save_game()
    assert "Error saving game:" in FakePopup.messages[-1]


def test_handle_promotion_success_and_cancel(monkeypatch):
    FakePopup.messages = []
    FakePopup.show_kwargs = []
    player = _make_player()
    player.level.level = 30
    presenter = _make_presenter()
    monkeypatch.setattr(church.ChurchManager, "_load_background", lambda self: setattr(self, "background", None))
    monkeypatch.setattr("src.ui_pygame.gui.church.ConfirmationPopup", FakePopup)
    monkeypatch.setattr("src.ui_pygame.gui.church.remove_equipment", lambda slot: f"default-{slot}")
    monkeypatch.setattr("src.ui_pygame.gui.church.apply_promotion_ability_rules", lambda _player, chosen: "Promotion rules updated.")
    monkeypatch.setattr("src.ui_pygame.gui.church.spell_dict", {})
    monkeypatch.setattr("src.ui_pygame.gui.church.skill_dict", {})

    class BaseClass:
        def __init__(self):
            self.name = "Warrior"

    class PromotedClass:
        def __init__(self):
            self.name = "Knight"
            self.equipment = {"Weapon": "blade", "Armor": "plate", "Accessory": "ring"}

    monkeypatch.setattr(
        "src.ui_pygame.gui.church.classes_dict",
        {"Base": {"class": BaseClass, "pro": {"Knight": {"class": PromotedClass}}}},
    )

    class FakePromotionScreen:
        def __init__(self, *_args, **_kwargs):
            pass

        def navigate(self):
            return selection.pop(0)

    selection = ["Knight", None]
    monkeypatch.setattr("src.ui_pygame.gui.church.PromotionScreen", FakePromotionScreen)

    manager = church.ChurchManager(presenter, player)
    manager.handle_promotion()

    assert player.cls.name == "Knight"
    assert player.level.pro_level == 2
    assert player.level.level == 1
    assert player.level.exp_to_gain == 42
    assert "Promotion rules updated." in FakePopup.messages
    assert "Congratulations! You are now a Knight." in FakePopup.messages

    player.cls = BaseClass()
    player.level.level = 30
    player.level.pro_level = 1
    manager.handle_promotion()
    assert "Promotion cancelled." in FakePopup.messages[-1]


def test_handle_promotion_advanced_branches(monkeypatch):
    FakePopup.messages = []
    FakePopup.show_kwargs = []
    player = _make_player()
    player.level.level = 30
    player.race = SimpleNamespace(cls_res={"First": ["Warlock", "Summoner"]})
    presenter = _make_presenter()
    menu_choices = iter([1, 0, 0, 0, None])
    shown_messages = []
    presenter.render_menu = lambda *_args, **_kwargs: next(menu_choices)
    presenter.show_message = lambda message, title="": shown_messages.append((title, message))
    presenter.get_text_input = lambda *_args, **_kwargs: ""

    monkeypatch.setattr(church.ChurchManager, "_load_background", lambda self: setattr(self, "background", None))
    monkeypatch.setattr("src.ui_pygame.gui.church.ConfirmationPopup", FakePopup)
    monkeypatch.setattr("src.ui_pygame.gui.church.remove_equipment", lambda slot: f"default-{slot}")

    class BaseClass:
        def __init__(self):
            self.name = "Warrior"

    class WarlockClass:
        def __init__(self):
            self.name = "Warlock"
            self.equipment = {"Weapon": "wand", "OffHand": "orb", "Armor": "robe"}

    class SummonerClass:
        def __init__(self):
            self.name = "Summoner"
            self.equipment = {"Weapon": "staff", "Armor": "cloak"}

    class NestedClass:
        def __init__(self):
            self.name = "Archmage"
            self.equipment = {}

    class FakeSpell:
        def __init__(self):
            self.name = "Arc Bolt"

    class FakeSkill:
        def __init__(self):
            self.name = "Transform"
            self.used_on = None

        def use(self, target):
            self.used_on = target

    class FakeFairy:
        def __init__(self):
            self.race = "Fairy"
            self.name = "Fairy"

        def inspect(self):
            return "A bright familiar."

    class FakePatagon:
        def __init__(self):
            self.name = "Patagon"
            self.initialized = None

        def initialize_stats(self, target):
            self.initialized = target

    monkeypatch.setattr(
        "src.ui_pygame.gui.church.classes_dict",
        {
            "Base": {
                "class": BaseClass,
                "pro": {
                    "Warlock": {"class": WarlockClass},
                    "Summoner": {"class": SummonerClass},
                },
            },
            "Mage": {
                "class": BaseClass,
                "pro": {
                    "Warlock": {
                        "class": WarlockClass,
                        "pro": {"Archmage": {"class": NestedClass}},
                    }
                },
            },
        },
    )
    monkeypatch.setattr("src.ui_pygame.gui.church.apply_promotion_ability_rules", lambda _player, chosen: f"{chosen} adjusted.")
    monkeypatch.setattr("src.ui_pygame.gui.church.spell_dict", {"Warlock": {"1": FakeSpell}})
    monkeypatch.setattr("src.ui_pygame.gui.church.skill_dict", {"Warlock": {"1": FakeSkill}})
    monkeypatch.setattr("src.ui_pygame.gui.church.companions.Fairy", FakeFairy)
    monkeypatch.setattr("src.ui_pygame.gui.church.companions.Patagon", FakePatagon)

    class FakePromotionScreen:
        def __init__(self, _presenter, _player, options, option_map, current_class, pro_level):
            self.options = options
            self.option_map = option_map

        def navigate(self):
            return selections.pop(0)

    selections = ["Missing", "Warlock", "Summoner", "Archmage"]
    monkeypatch.setattr("src.ui_pygame.gui.church.PromotionScreen", FakePromotionScreen)

    manager = church.ChurchManager(presenter, player)
    manager.handle_promotion()
    assert "Promotion option unavailable." in FakePopup.messages[-1]

    player.cls = BaseClass()
    player.level.level = 30
    player.level.pro_level = 1
    player.level.exp_to_gain = 10
    player.spellbook = {"Spells": {}, "Skills": {}}
    player.familiar = None
    manager.handle_promotion()
    assert player.cls.name == "Warlock"
    assert player.spellbook["Spells"]["Arc Bolt"].name == "Arc Bolt"
    assert player.spellbook["Skills"]["Transform"].name == "Transform"
    assert player.familiar is not None
    assert player.familiar.name == "Buddy"
    assert any("joins you as 'Buddy'" in message for message in FakePopup.messages)
    assert shown_messages[-1][0] == "Fairy"

    player.cls = BaseClass()
    player.level.level = 30
    player.level.pro_level = 1
    player.summons = {}
    manager.handle_promotion()
    assert "Patagon" in player.summons
    assert any("learned to summon Patagon" in message for message in FakePopup.messages)

    player.cls = WarlockClass()
    player.level.level = 30
    player.level.pro_level = 2
    manager.handle_promotion()
    assert player.cls.name == "Archmage"

    monkeypatch.setattr(
        "src.ui_pygame.gui.church.classes_dict",
        {"Base": {"class": BaseClass, "pro": {"Warlock": {"class": WarlockClass}}}},
    )

    class BrokenSelectionScreen:
        def __init__(self, *_args, **_kwargs):
            pass

        def navigate(self):
            return "Warlock"

    monkeypatch.setattr("src.ui_pygame.gui.church.PromotionScreen", BrokenSelectionScreen)
    monkeypatch.setattr("src.ui_pygame.gui.church.apply_promotion_ability_rules", lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("broken promo")))
    player.cls = BaseClass()
    player.level.level = 30
    player.level.pro_level = 1
    manager.handle_promotion()
    assert "Promotion failed:" in FakePopup.messages[-1]
