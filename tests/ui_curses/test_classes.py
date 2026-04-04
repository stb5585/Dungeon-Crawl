#!/usr/bin/env python3
"""Focused coverage for curses class-selection helpers."""

from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace

from src.core import abilities as real_abilities
from src.core import companions as real_companions
from src.core import classes as real_classes
from src.ui_curses import menus as real_menus
from src.ui_curses import classes as curses_classes


def test_choose_familiar(monkeypatch):
    fake_menus = ModuleType("src.ui_curses.menus")

    popup_calls = []

    class FakePromotionPopupMenu:
        def __init__(self, game, title, current_class, familiar=False):
            popup_calls.append((title, current_class, familiar))

        def update_options(self, choose_list, choose_dict):
            popup_calls.append((tuple(choose_list), tuple(choose_dict)))

        def navigate_popup(self):
            return 1

    class FakeConfirmPopupMenu:
        responses = [False, True]

        def __init__(self, game, text, box_height=8):
            popup_calls.append((text, box_height))

        def navigate_popup(self):
            return self.responses.pop(0)

    name_inputs = iter(["", "pixie"])
    fake_menus.PromotionPopupMenu = FakePromotionPopupMenu
    fake_menus.ConfirmPopupMenu = FakeConfirmPopupMenu
    fake_menus.player_input = lambda game, prompt: next(name_inputs)

    fake_companions = ModuleType("src.core.companions")
    for familiar_name in ("Homunculus", "Fairy", "Mephit", "Jinkin"):
        setattr(fake_companions, familiar_name, type(familiar_name, (), {"__init__": lambda self, n=familiar_name: setattr(self, "spec", n)}))

    monkeypatch.setattr(real_menus, "PromotionPopupMenu", FakePromotionPopupMenu)
    monkeypatch.setattr(real_menus, "ConfirmPopupMenu", FakeConfirmPopupMenu)
    monkeypatch.setattr(real_menus, "player_input", lambda game, prompt: next(name_inputs))
    monkeypatch.setattr(real_companions, "Homunculus", getattr(fake_companions, "Homunculus"))
    monkeypatch.setattr(real_companions, "Fairy", getattr(fake_companions, "Fairy"))
    monkeypatch.setattr(real_companions, "Mephit", getattr(fake_companions, "Mephit"))
    monkeypatch.setattr(real_companions, "Jinkin", getattr(fake_companions, "Jinkin"))

    familiar = curses_classes.choose_familiar(SimpleNamespace())

    assert familiar.name == "Pixie"
    assert familiar.spec == "Fairy"
    assert popup_calls[0] == ("Select Familiar", "Mage", True)


def test_promotion_go_back_and_success(monkeypatch):
    fake_menus = ModuleType("src.ui_curses.menus")
    output = []

    class FakePromotionPopupMenu:
        selections = [1, 0]

        def __init__(self, game, message, current_class):
            self.message = message
            self.current_class = current_class

        def update_options(self, class_options, _mapping):
            self.class_options = class_options

        def navigate_popup(self):
            return self.selections.pop(0)

    class FakeConfirmPopupMenu:
        responses = [True]

        def __init__(self, game, text, box_height=9):
            self.text = text

        def navigate_popup(self):
            return self.responses.pop(0)

    class FakeTextBox:
        def __init__(self, game):
            pass

        def print_text_in_rectangle(self, text):
            output.append(text)

        def clear_rectangle(self):
            output.append("cleared")

    fake_menus.PromotionPopupMenu = FakePromotionPopupMenu
    fake_menus.ConfirmPopupMenu = FakeConfirmPopupMenu
    fake_menus.TextBox = FakeTextBox
    monkeypatch.setattr(real_menus, "PromotionPopupMenu", FakePromotionPopupMenu)
    monkeypatch.setattr(real_menus, "ConfirmPopupMenu", FakeConfirmPopupMenu)
    monkeypatch.setattr(real_menus, "TextBox", FakeTextBox)

    fake_abilities = {"Knight": {"1": lambda: SimpleNamespace(name="Spark")}}

    class TransformSkill:
        def __init__(self):
            self.name = "Transform"

        def use(self, target):
            target.skill_used = True

    fake_skill_dict = {"Knight": {"1": TransformSkill}}
    monkeypatch.setattr(real_abilities, "spell_dict", fake_abilities)
    monkeypatch.setattr(real_abilities, "skill_dict", fake_skill_dict)

    monkeypatch.setattr(real_classes, "apply_promotion_ability_rules", lambda player, chosen: "Abilities updated.\n")

    class BaseClass:
        def __init__(self):
            self.name = "Warrior"

    class KnightClass:
        def __init__(self):
            self.name = "Knight"
            self.pro_level = 2
            self.str_plus = 1
            self.int_plus = 2
            self.wis_plus = 3
            self.con_plus = 4
            self.cha_plus = 5
            self.dex_plus = 6
            self.att_plus = 1
            self.def_plus = 2
            self.magic_plus = 3
            self.magic_def_plus = 4
            self.equipment = {"Weapon": "Sword", "Armor": "Plate", "OffHand": "Shield"}

    fake_classes_dict = {
        "Base": {"class": BaseClass, "pro": {"Knight": {"class": KnightClass}}},
    }
    monkeypatch.setattr(real_classes, "classes_dict", fake_classes_dict)

    monkeypatch.setattr(real_companions, "Patagon", lambda: SimpleNamespace(name="Patagon", initialize_stats=lambda _player: None))

    game = SimpleNamespace(
        player_char=SimpleNamespace(
            name="Ada",
            race=SimpleNamespace(cls_res={"First": ["Knight"]}),
            cls=BaseClass(),
            level=SimpleNamespace(pro_level=1, level=30),
            stats=SimpleNamespace(strength=10, intel=10, wisdom=10, con=10, charisma=10, dex=10),
            health=SimpleNamespace(max=20),
            mana=SimpleNamespace(max=10),
            combat=SimpleNamespace(attack=1, defense=1, magic=1, magic_def=1),
            equipment={},
            spellbook={"Spells": {}, "Skills": {}},
            summons={},
            unequip=lambda promo=False: output.append(("unequip", promo)),
            level_exp=lambda: 99,
        )
    )

    curses_classes.promotion(game)
    assert "If you change your mind" in output[0]

    FakePromotionPopupMenu.selections = [0]
    curses_classes.promotion(game)

    final_text = output[-2]
    assert "promoted from a Warrior to a Knight" in final_text
    assert "Abilities updated." in final_text
    assert "You have gained the spell Spark." in final_text
    assert "You have gained the skill Transform." in final_text
    assert game.player_char.cls.name == "Knight"
    assert game.player_char.level.level == 1
    assert game.player_char.skill_used is True


def test_promotion_second_tier_and_special_class_branches(monkeypatch):
    output = []

    class FakePromotionPopupMenu:
        selections = [0, 1, 2, 0, 0]

        def __init__(self, game, message, current_class):
            self.current_class = current_class

        def update_options(self, class_options, _mapping):
            self.class_options = class_options

        def navigate_popup(self):
            return self.selections.pop(0)

    class FakeConfirmPopupMenu:
        responses = [True, True, True, True, False]

        def __init__(self, game, text, box_height=9):
            self.text = text

        def navigate_popup(self):
            return self.responses.pop(0)

    class FakeTextBox:
        def __init__(self, game):
            pass

        def print_text_in_rectangle(self, text):
            output.append(text)

        def clear_rectangle(self):
            output.append("cleared")

    monkeypatch.setattr(real_menus, "PromotionPopupMenu", FakePromotionPopupMenu)
    monkeypatch.setattr(real_menus, "ConfirmPopupMenu", FakeConfirmPopupMenu)
    monkeypatch.setattr(real_menus, "TextBox", FakeTextBox)

    monkeypatch.setattr(curses_classes, "choose_familiar", lambda game: SimpleNamespace(name="Buddy", spec="Fairy"))

    class LevelOneSpell:
        def __init__(self):
            self.name = "Spark"

    class TotemSkill:
        def __init__(self):
            self.name = "Totem"

        def check_and_unlock_aspects(self, level):
            return ["Bear", "Eagle"] if level == 1 else []

    class RevealSkill:
        def __init__(self):
            self.name = "Reveal"

        def use(self, target):
            target.revealed = True

    monkeypatch.setattr(
        real_abilities,
        "spell_dict",
        {
            "Wizard": {"1": LevelOneSpell},
            "Warlock": {"1": LevelOneSpell},
            "Shaman": {},
            "Summoner": {},
        },
    )
    monkeypatch.setattr(
        real_abilities,
        "skill_dict",
        {
            "Warlock": {},
            "Wizard": {"1": RevealSkill},
            "Shaman": {"1": TotemSkill},
            "Summoner": {},
        },
    )
    monkeypatch.setattr(real_classes, "apply_promotion_ability_rules", lambda player, chosen: f"{chosen} rules\n")

    class Warrior:
        def __init__(self):
            self.name = "Warrior"

    class Mage:
        def __init__(self):
            self.name = "Mage"

    class Warlock:
        def __init__(self):
            self.name = "Warlock"
            self.pro_level = 2
            self.str_plus = self.int_plus = self.wis_plus = self.con_plus = self.cha_plus = self.dex_plus = 0
            self.att_plus = self.def_plus = self.magic_plus = self.magic_def_plus = 0
            self.equipment = {"Weapon": "Wand", "Armor": "Robe", "OffHand": "Orb"}

    class Shaman:
        def __init__(self):
            self.name = "Shaman"
            self.pro_level = 2
            self.str_plus = self.int_plus = self.wis_plus = self.con_plus = self.cha_plus = self.dex_plus = 0
            self.att_plus = self.def_plus = self.magic_plus = self.magic_def_plus = 0
            self.equipment = {"Weapon": "Staff", "Armor": "Hide", "OffHand": "Charm"}

    class Summoner:
        def __init__(self):
            self.name = "Summoner"
            self.pro_level = 2
            self.str_plus = self.int_plus = self.wis_plus = self.con_plus = self.cha_plus = self.dex_plus = 0
            self.att_plus = self.def_plus = self.magic_plus = self.magic_def_plus = 0
            self.equipment = {"Weapon": "Book", "Armor": "Cloth", "OffHand": "Bell"}

    class Wizard:
        def __init__(self):
            self.name = "Wizard"
            self.pro_level = 3
            self.str_plus = self.int_plus = self.wis_plus = self.con_plus = self.cha_plus = self.dex_plus = 1
            self.att_plus = self.def_plus = self.magic_plus = self.magic_def_plus = 1
            self.equipment = {"Weapon": "Rod", "Armor": "Cape", "OffHand": "Focus"}

    monkeypatch.setattr(
        real_classes,
        "classes_dict",
        {
            "Warrior": {
                "class": Warrior,
                "pro": {
                    "Warlock": {"class": Warlock},
                    "Shaman": {"class": Shaman},
                    "Summoner": {"class": Summoner},
                },
            },
            "Mage": {
                "class": Mage,
                "pro": {"Warlock": {"class": Warlock, "pro": {"Wizard": {"class": Wizard}}}},
            },
        },
    )

    patagons = []
    monkeypatch.setattr(
        real_companions,
        "Patagon",
        lambda: SimpleNamespace(name="Patagon", initialize_stats=lambda _player: patagons.append(True)),
    )

    game = SimpleNamespace(
        player_char=SimpleNamespace(
            name="Ada",
            race=SimpleNamespace(cls_res={"First": ["Warlock", "Shaman", "Summoner"]}),
            cls=Warrior(),
            level=SimpleNamespace(pro_level=1, level=30),
            stats=SimpleNamespace(strength=10, intel=10, wisdom=10, con=10, charisma=10, dex=10),
            health=SimpleNamespace(max=20),
            mana=SimpleNamespace(max=10),
            combat=SimpleNamespace(attack=1, defense=1, magic=1, magic_def=1),
            equipment={},
            spellbook={"Spells": {"Spark": LevelOneSpell()}, "Skills": {"Totem": TotemSkill()}},
            summons={},
            location_x=7,
            location_y=8,
            location_z=9,
            unequip=lambda promo=False: output.append(("unequip", promo)),
            level_exp=lambda: 33,
        )
    )

    curses_classes.promotion(game)
    assert "Spark goes up a level." in output[-2]
    assert "Buddy the Fairy familiar has joined your team!" in output[-2]

    game.player_char.cls = Warrior()
    game.player_char.level.pro_level = 1
    curses_classes.promotion(game)
    assert "Totem aspects unlocked: Bear, Eagle." in output[-2]

    game.player_char.cls = Warrior()
    game.player_char.level.pro_level = 1
    curses_classes.promotion(game)
    assert "You have gained the summon Patagon." in output[-2]
    assert "Patagon" in game.player_char.summons
    assert patagons == [True]

    game.player_char.cls = Warlock()
    game.player_char.level.pro_level = 2
    curses_classes.promotion(game)
    assert game.player_char.cls.name == "Wizard"
    assert game.player_char.teleport == (7, 8, 9)
    assert game.player_char.revealed is True

    game.player_char.cls = Warrior()
    game.player_char.level.pro_level = 1
    curses_classes.promotion(game)
    assert "If you change your mind" in output[-2]
