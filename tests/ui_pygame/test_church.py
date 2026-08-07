#!/usr/bin/env python3
"""Focused coverage for church manager helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pygame

from src.core import companions, items
from src.core.classes import class_rings, demonologist, paladin
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
        stats=SimpleNamespace(strength=10, intel=10, wisdom=10, con=10, charisma=10, dex=10),
        health=SimpleNamespace(max=100, current=100),
        mana=SimpleNamespace(max=50, current=50),
        combat=SimpleNamespace(attack=10, defense=10, magic=10, magic_def=10),
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


def _make_surface_presenter(width=900, height=700):
    presenter = _make_presenter()
    presenter.screen = pygame.Surface((width, height))
    presenter.width = width
    presenter.height = height
    return presenter


def test_paladin_vow_selection_popup_draws_details_and_selects_highlighted(monkeypatch):
    pygame.init()
    pygame.event.clear()
    presenter = _make_surface_presenter()
    flips = []
    monkeypatch.setattr("src.ui_pygame.gui.church.pygame.display.flip", lambda: flips.append(True))

    popup = church.PaladinVowSelectionPopup(presenter)
    popup.draw(lambda: presenter.screen.fill((0, 0, 0)))

    assert popup.options == list(paladin.PATHS)
    assert len(popup.option_rects) == len(paladin.PATHS)
    assert popup.detail_rect is not None
    assert popup.instruction_rect is not None
    assert popup.instruction_rect.top > popup.detail_rect.bottom
    popup_copy = " ".join(
        list(paladin.DESCRIPTIONS.values())
        + list(paladin.SIGNATURE_DESCRIPTIONS.values())
        + list(paladin.AURA_DESCRIPTIONS.values())
        + list(paladin.MARK_DESCRIPTIONS.values())
    )
    for documented_mechanic in (
        "three encounters",
        "two-turn",
        "+5%",
        "percentage points",
    ):
        assert documented_mechanic in popup_copy

    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

    selected = popup.show(
        flush_events=False,
        require_key_release=False,
        background_draw_func=lambda: presenter.screen.fill((0, 0, 0)),
    )

    assert selected == "Conquest"
    assert flips


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

    selections = iter([0, 1, 2])
    rendered = []
    draw_frame_calls = []

    class FakeLocationMenuScreen:
        def __init__(self, _presenter, _title):
            pass

        def set_location_portrait(self, _npc_name):
            return None

        def draw_frame(self, *, do_flip=False):
            draw_frame_calls.append(do_flip)

        def navigate(self, _options, reset_cursor=False, **_kwargs):
            return next(selections)

        def display_quest_text(self, text, **kwargs):
            rendered.append((text, kwargs.get("npc_name")))

    class FakeQuestManager:
        def __init__(self, _presenter, _player, quest_text_renderer, **_kwargs):
            self.quest_text_renderer = quest_text_renderer

        def check_and_offer(self, patron):
            self.quest_text_renderer(f"{patron} quest")

    monkeypatch.setattr("src.ui_pygame.gui.church.LocationMenuScreen", FakeLocationMenuScreen)
    monkeypatch.setattr("src.ui_pygame.gui.church.QuestManager", FakeQuestManager)

    manager.visit_church()

    assert calls == ["save"]
    assert rendered == [("Priest quest", "Priest")]
    assert "Let the light of Elysia guide you." in FakePopup.messages
    assert FakePopup.show_kwargs[-1]["flush_events"] is True
    assert FakePopup.show_kwargs[-1]["require_key_release"] is True
    assert callable(FakePopup.show_kwargs[-1]["background_draw_func"])
    FakePopup.show_kwargs[-1]["background_draw_func"]()
    assert draw_frame_calls == [False]


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
            self.name = "Weapon Master"
            self.equipment = {"Weapon": "blade", "Armor": "plate", "Accessory": "ring"}
            self.str_plus = 2
            self.int_plus = 1
            self.wis_plus = 0
            self.con_plus = 1
            self.cha_plus = 0
            self.dex_plus = 2
            self.att_plus = 4
            self.def_plus = 2
            self.magic_plus = 0
            self.magic_def_plus = 2

    monkeypatch.setattr(
        "src.ui_pygame.gui.church.classes_dict",
        {"Base": {"class": BaseClass, "pro": {"Weapon Master": {"class": PromotedClass}}}},
    )

    class FakePromotionScreen:
        def __init__(self, *_args, **_kwargs):
            pass

        def navigate(self):
            return selection.pop(0)

    selection = ["Weapon Master", None]
    monkeypatch.setattr("src.ui_pygame.gui.church.PromotionScreen", FakePromotionScreen)

    manager = church.ChurchManager(presenter, player)
    manager.handle_promotion()

    assert player.cls.name == "Weapon Master"
    assert player.level.pro_level == 2
    assert player.level.level == 1
    assert player.level.exp_to_gain == 42
    assert player.stats.strength == 12
    assert player.stats.intel == 11
    assert player.stats.con == 11
    assert player.stats.dex == 12
    assert player.health.max == 102
    assert player.health.current == 102
    assert player.mana.max == 52
    assert player.mana.current == 52
    assert player.combat.attack == 14
    assert player.combat.defense == 12
    assert player.combat.magic_def == 12
    assert "Promotion rules updated." not in FakePopup.messages
    assert not any("Character Menu tab available" in message for message in FakePopup.messages)
    assert any("Congratulations! You are now a Weapon Master." in message for message in FakePopup.messages)
    assert any("New Character Menu tab: Weapon Discipline" in message for message in FakePopup.messages)
    first_promotion_messages = list(FakePopup.messages)
    assert len(first_promotion_messages) == 1
    assert "New Character Menu tab: Weapon Discipline" in first_promotion_messages[0]

    player.cls = BaseClass()
    player.level.level = 30
    player.level.pro_level = 1
    manager.handle_promotion()
    assert "Promotion cancelled." in FakePopup.messages[-1]


def test_handle_promotion_grants_cleric_sanctuary_ward_immediately(monkeypatch):
    FakePopup.messages = []
    FakePopup.show_kwargs = []
    player = _make_player()
    player.cls = SimpleNamespace(name="Healer", equipment={})
    player.level.level = 30
    presenter = _make_presenter()

    monkeypatch.setattr(church.ChurchManager, "_load_background", lambda self: setattr(self, "background", None))
    monkeypatch.setattr("src.ui_pygame.gui.church.ConfirmationPopup", FakePopup)
    monkeypatch.setattr("src.ui_pygame.gui.church.remove_equipment", lambda slot: f"default-{slot}")

    class FakePromotionScreen:
        def __init__(self, *_args, **_kwargs):
            pass

        def navigate(self):
            return "Cleric"

    monkeypatch.setattr("src.ui_pygame.gui.church.PromotionScreen", FakePromotionScreen)

    manager = church.ChurchManager(presenter, player)
    manager.handle_promotion()

    assert player.cls.name == "Cleric"
    assert player.level.pro_level == 2
    assert player.level.level == 1
    assert "Sanctuary Ward" in player.spellbook["Skills"]
    assert "Smite" in player.spellbook["Spells"]
    assert len(FakePopup.messages) == 1
    assert "Congratulations! You are now a Cleric." in FakePopup.messages[0]
    assert "Learned abilities:" in FakePopup.messages[0]
    assert "Skill: Sanctuary Ward" in FakePopup.messages[0]
    assert "Sanctuary Ward" in FakePopup.messages[0]


def test_handle_promotion_grants_priest_supplication_and_explains_prayer(monkeypatch):
    FakePopup.messages = []
    FakePopup.show_kwargs = []
    player = _make_player()
    player.cls = SimpleNamespace(name="Healer", equipment={})
    player.level.level = 30
    presenter = _make_presenter()

    monkeypatch.setattr(
        church.ChurchManager,
        "_load_background",
        lambda self: setattr(self, "background", None),
    )
    monkeypatch.setattr("src.ui_pygame.gui.church.ConfirmationPopup", FakePopup)
    monkeypatch.setattr(
        "src.ui_pygame.gui.church.remove_equipment",
        lambda slot: f"default-{slot}",
    )

    class FakePromotionScreen:
        def __init__(self, *_args, **_kwargs):
            pass

        def navigate(self):
            return "Priest"

    monkeypatch.setattr("src.ui_pygame.gui.church.PromotionScreen", FakePromotionScreen)

    manager = church.ChurchManager(presenter, player)
    manager.handle_promotion()

    assert player.cls.name == "Priest"
    assert player.level.pro_level == 2
    assert player.level.level == 1
    assert "Supplication" in player.spellbook["Skills"]
    assert len(FakePopup.messages) == 1
    assert "Skill: Supplication" in FakePopup.messages[0]
    assert "Prayer" in FakePopup.messages[0]


def test_handle_promotion_grants_ranger_tame_and_favored_enemy_immediately(monkeypatch):
    FakePopup.messages = []
    FakePopup.show_kwargs = []
    player = _make_player()
    player.cls = SimpleNamespace(name="Pathfinder", equipment={})
    player.level.level = 30
    presenter = _make_presenter()

    monkeypatch.setattr(church.ChurchManager, "_load_background", lambda self: setattr(self, "background", None))
    monkeypatch.setattr("src.ui_pygame.gui.church.ConfirmationPopup", FakePopup)
    monkeypatch.setattr("src.ui_pygame.gui.church.remove_equipment", lambda slot: f"default-{slot}")

    class FakePromotionScreen:
        def __init__(self, *_args, **_kwargs):
            pass

        def navigate(self):
            return "Ranger"

    monkeypatch.setattr("src.ui_pygame.gui.church.PromotionScreen", FakePromotionScreen)

    manager = church.ChurchManager(presenter, player)
    manager.handle_promotion()

    assert player.cls.name == "Ranger"
    assert player.level.pro_level == 2
    assert player.level.level == 1
    assert "Tame" in player.spellbook["Skills"]
    assert "Favored Enemy" in player.spellbook["Skills"]
    assert "Skill: Tame" in FakePopup.messages[0]
    assert "Skill: Favored Enemy" in FakePopup.messages[0]


def test_promotion_mechanic_help_shows_tab_and_combat_guidance(monkeypatch):
    FakePopup.messages = []
    FakePopup.show_kwargs = []
    player = _make_player()
    presenter = _make_presenter()
    monkeypatch.setattr(church.ChurchManager, "_load_background", lambda self: setattr(self, "background", None))
    monkeypatch.setattr("src.ui_pygame.gui.church.ConfirmationPopup", FakePopup)
    manager = church.ChurchManager(presenter, player)

    manager._show_promotion_mechanic_help("Weapon Master")
    assert "New Character Menu tab: Weapon Discipline" in FakePopup.messages[-1]
    assert "Intelligence helps" in FakePopup.messages[-1]

    manager._show_promotion_mechanic_help("Spell Stealer")
    assert "Stolen spell scrolls" in FakePopup.messages[-1]

    manager._show_promotion_mechanic_help("Priest")
    assert "Prayer" in FakePopup.messages[-1]
    assert "Supplication" in FakePopup.messages[-1]

    manager._show_promotion_mechanic_help("Ranger")
    assert FakePopup.messages[-1].count("Companion & Hunt") == 1

    message_count = len(FakePopup.messages)
    manager._show_promotion_mechanic_help("Knight")
    assert len(FakePopup.messages) == message_count


def test_handle_promotion_keeps_legal_gear_removes_illegal_and_grants_no_defaults(monkeypatch):
    FakePopup.messages = []
    player = _make_player()
    player.level.level = 30
    presenter = _make_presenter()
    inventory_calls = []
    keep_weapon = SimpleNamespace(name="Keep Blade", subtyp="Sword")
    illegal_armor = SimpleNamespace(name="Old Plate", subtyp="Heavy")
    player.equipment = {
        "Weapon": keep_weapon,
        "Armor": illegal_armor,
        "OffHand": items.NoOffHand(),
        "Helmet": items.NoHelmet(),
    }
    player.modify_inventory = lambda item, *_args, **_kwargs: inventory_calls.append(item.name)
    player.can_equip_item = lambda item, slot=None: item.name == "Keep Blade"

    monkeypatch.setattr(church.ChurchManager, "_load_background", lambda self: setattr(self, "background", None))
    monkeypatch.setattr("src.ui_pygame.gui.church.ConfirmationPopup", FakePopup)
    monkeypatch.setattr("src.ui_pygame.gui.church.apply_promotion_ability_rules", lambda _player, _chosen: "")
    monkeypatch.setattr("src.ui_pygame.gui.church.spell_dict", {})
    monkeypatch.setattr("src.ui_pygame.gui.church.skill_dict", {})

    class BaseClass:
        def __init__(self):
            self.name = "Warrior"

    class PromotedClass:
        def __init__(self):
            self.name = "Knight"
            self.equipment = {
                "Weapon": SimpleNamespace(name="Default Sword", subtyp="Sword"),
                "Armor": SimpleNamespace(name="Default Armor", subtyp="Light"),
            }

    monkeypatch.setattr(
        "src.ui_pygame.gui.church.classes_dict",
        {"Base": {"class": BaseClass, "pro": {"Knight": {"class": PromotedClass}}}},
    )

    class FakePromotionScreen:
        def __init__(self, *_args, **_kwargs):
            pass

        def navigate(self):
            return "Knight"

    monkeypatch.setattr("src.ui_pygame.gui.church.PromotionScreen", FakePromotionScreen)

    manager = church.ChurchManager(presenter, player)
    manager.handle_promotion()

    assert player.equipment["Weapon"] is keep_weapon
    assert player.equipment["Armor"].name == "No Armor"
    assert inventory_calls == ["Old Plate"]
    assert "Default Sword" not in [getattr(item, "name", item) for item in player.equipment.values()]
    warning = "\n".join(FakePopup.messages)
    assert "Some equipped gear no longer fits" in warning
    assert "Armor: Old Plate" in warning


def test_handle_promotion_advanced_branches(monkeypatch):
    FakePopup.messages = []
    FakePopup.show_kwargs = []
    player = _make_player()
    player.level.level = 30
    player.race = SimpleNamespace(cls_res={"First": ["Warlock", "Thaumaturgist"]})
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
            self.str_plus = self.int_plus = self.wis_plus = self.con_plus = self.cha_plus = self.dex_plus = 0
            self.att_plus = self.def_plus = self.magic_plus = self.magic_def_plus = 0

    class ThaumaturgistClass:
        def __init__(self):
            self.name = "Thaumaturgist"
            self.equipment = {"Weapon": "staff", "Armor": "cloak"}
            self.str_plus = self.int_plus = self.wis_plus = self.con_plus = self.cha_plus = self.dex_plus = 0
            self.att_plus = self.def_plus = self.magic_plus = self.magic_def_plus = 0

    class NestedClass:
        def __init__(self):
            self.name = "Archmage"
            self.equipment = {}
            self.str_plus = self.int_plus = self.wis_plus = self.con_plus = self.cha_plus = self.dex_plus = 0
            self.att_plus = self.def_plus = self.magic_plus = self.magic_def_plus = 0

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
                    "Thaumaturgist": {"class": ThaumaturgistClass},
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
    monkeypatch.setattr(companions, "Patagon", FakePatagon)

    class FakePromotionScreen:
        def __init__(self, _presenter, _player, options, option_map, current_class, pro_level):
            self.options = options
            self.option_map = option_map

        def navigate(self):
            return selections.pop(0)

    selections = ["Missing", "Warlock", "Thaumaturgist", "Archmage"]
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
    assert not any("joins you as 'Buddy'" in message for message in FakePopup.messages)
    assert not any("Character Menu tab available: Companion" in message for message in FakePopup.messages)
    assert shown_messages[-1][0] == "Fairy"

    player.cls = BaseClass()
    player.level.level = 30
    player.level.pro_level = 1
    player.summons = {}
    manager.handle_promotion()
    assert player.cls.name == "Thaumaturgist"
    assert player.summons == {}
    assert not any("learned to summon Patagon" in message for message in FakePopup.messages)

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


def test_hidden_crypt_binds_contract_and_awakens_ring(monkeypatch):
    FakePopup.messages = []
    FakePopup.show_kwargs = []
    player = _make_player()
    player.cls = SimpleNamespace(name="Demonologist")
    player.kill_dict = {"Fiend": {"Imp": 1, "Balor": 1}}
    player.demonologist_contracts = demonologist.default_state()
    player.ensure_demonologist_contracts = lambda: demonologist.ensure_state(player)
    player.refresh_demonologist_contracts = lambda: demonologist.refresh_unlocked_contracts(player)
    player.equipment = {"Ring": items.ClassRing()}
    familiar = companions.Mephit()
    familiar.name = "Spark"
    player.familiar = familiar

    presenter = _make_presenter()
    selections = iter([1, 1, 2, 2])
    presenter.render_menu = lambda *_args, **_kwargs: next(selections)

    monkeypatch.setattr(church.ChurchManager, "_load_background", lambda self: setattr(self, "background", None))
    monkeypatch.setattr("src.ui_pygame.gui.church.ConfirmationPopup", FakePopup)

    manager = church.ChurchManager(presenter, player)
    assert manager.visit_hidden_crypt() is True

    assert player.demonologist_contracts["active_patron"] == "Balor"
    assert player.demonologist_contracts["ring_awakened"] is True
    assert player.familiar is None
    assert any("Balor is now your active contract." in message for message in FakePopup.messages)
    assert any("Class Ring awakens" in message for message in FakePopup.messages)


def test_arcane_class_ring_rite_requires_visible_dormant_ring(monkeypatch):
    player = _make_player()
    player.cls = SimpleNamespace(name="Wizard")
    player.class_ring_awakening = class_rings.default_state()
    player.inventory = {"Class Ring": [items.ClassRing()]}
    presenter = _make_presenter()
    monkeypatch.setattr(church.ChurchManager, "_load_background", lambda self: setattr(self, "background", None))

    manager = church.ChurchManager(presenter, player)
    assert manager._arcane_class_ring_rite_label() == "Four Formulae"
    assert manager._arcane_class_ring_rite_available() is False

    player.storage = {"Class Ring": [items.ClassRing()]}
    assert manager._arcane_class_ring_rite_available() is True

    player.storage = {}
    player.equipment["Ring"] = items.ClassRing()
    assert manager._arcane_class_ring_rite_available() is True

    player.class_ring_awakening["awakened"]["Wizard"] = True
    assert manager._arcane_class_ring_rite_available() is False


def test_arcane_class_ring_rites_awaken_ring_and_apply_mods(monkeypatch):
    FakePopup.messages = []
    presenter = _make_presenter()
    monkeypatch.setattr(church.ChurchManager, "_load_background", lambda self: setattr(self, "background", None))
    monkeypatch.setattr("src.ui_pygame.gui.church.ConfirmationPopup", FakePopup)

    for class_name, expected_mod, expected_label in (
        ("Wizard", "School Streak", "Four Formulae"),
        ("Shadowcaster", "Umbral Debt", "Debt Cap Trial"),
        ("Knight Enchanter", "Arcane Tempo", "Arcane Duel"),
        ("Thaumaturgist", "+30% Xenids", "Conduit Ritual"),
        ("Templar", "Ordered Blessings", "Relic Defense"),
        ("Hierophant", "Sacred Conduit", "Consecration Rite"),
        ("Master Monk", "Martial Master", "Purity Rite"),
        ("Archbishop", "Divine Intervention", "Miracle Vigil"),
        ("Troubadour", "Encore", "Lost Ballad"),
        ("Lycan", "Controlled Frenzy", "Control Rite"),
        ("Astromancer", "Constellation Cycle", "Star Chart"),
        ("Soulcatcher", "Aspect Evolution", "Ancestral Totem Rite"),
        ("Beast Master", "Shared Recovery", "Pack Trial"),
    ):
        player = _make_player()
        player.cls = SimpleNamespace(name=class_name)
        player.class_ring_awakening = class_rings.default_state()
        player.equipment["Ring"] = items.ClassRing()
        player.health = SimpleNamespace(current=200, max=200)
        player.awaken_class_ring = lambda class_name=None, _player=player, **kwargs: class_rings.activate(
            _player,
            class_name,
            **kwargs,
        )

        manager = church.ChurchManager(presenter, player)
        assert manager.visit_arcane_class_ring_rite() is True
        assert player.class_ring_awakening["awakened"][class_name] is True
        assert player.equipment["Ring"].mod == expected_mod
        assert any(expected_label in message for message in FakePopup.messages)
        if class_name == "Thaumaturgist":
            assert player.health.max == 190
            assert player.health.current == 190


def test_paladin_legacy_vow_choice_and_crusader_vow_trial(monkeypatch):
    FakePopup.messages = []
    FakePopup.show_kwargs = []
    presenter = _make_presenter()
    monkeypatch.setattr(church.ChurchManager, "_load_background", lambda self: setattr(self, "background", None))
    monkeypatch.setattr("src.ui_pygame.gui.church.ConfirmationPopup", FakePopup)

    class FakeVowSelectionPopup:
        show_kwargs = []

        def __init__(self, _presenter):
            pass

        def show(self, **kwargs):
            FakeVowSelectionPopup.show_kwargs.append(kwargs)
            return "Redemption"

    monkeypatch.setattr("src.ui_pygame.gui.church.PaladinVowSelectionPopup", FakeVowSelectionPopup)

    player = _make_player()
    player.cls = SimpleNamespace(name="Paladin")
    player.paladin_vow = paladin.default_state()
    player.choose_paladin_vow = lambda vow: paladin.choose_vow(player, vow)
    manager = church.ChurchManager(presenter, player)

    assert manager._legacy_paladin_vow_available() is True
    assert manager.visit_legacy_paladin_vow_choice() is True
    assert FakeVowSelectionPopup.show_kwargs[-1]["flush_events"] is True
    assert FakeVowSelectionPopup.show_kwargs[-1]["require_key_release"] is True
    assert FakePopup.show_kwargs[-1]["flush_events"] is True
    assert FakePopup.show_kwargs[-1]["require_key_release"] is True
    assert FakePopup.messages[0] == "Swear the Vow of Redemption?"
    assert "Redeem offers" not in FakePopup.messages[0]
    assert player.paladin_vow["path"] == "Redemption"
    assert "Redeem" in player.spellbook["Skills"]

    player.cls = SimpleNamespace(name="Crusader")
    player.class_ring_awakening = class_rings.default_state()
    player.equipment = {"Ring": items.ClassRing()}
    player.awaken_class_ring = lambda class_name=None, **kwargs: class_rings.activate(player, class_name, **kwargs)

    assert manager._crusader_vow_trial_available() is True
    assert manager.visit_crusader_vow_trial() is True
    assert player.equipment["Ring"].mod == "Vow Affirmation"
    assert player.class_ring_awakening["data"]["Crusader"]["vow"] == "Redemption"
