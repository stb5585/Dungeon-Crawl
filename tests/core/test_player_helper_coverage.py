#!/usr/bin/env python3
"""Focused coverage for player helper, quest, and menu behavior."""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parents[2]))

import pytest

from src.core import items
from src.core.constants import BASE_CRIT_PER_POINT
from src.core.player import Player
from tests.test_framework import TestGameState


class RecordingTextBox:
    def __init__(self):
        self.messages = []

    def print_text_in_rectangle(self, message):
        self.messages.append(message)


class LabelMenu:
    def __init__(self, selections):
        self.selections = list(selections)
        self.options = []
        self.draw_calls = 0
        self.refresh_calls = 0

    def set_options(self, options):
        self.options = list(options)

    def draw_all(self):
        self.draw_calls += 1

    def refresh_all(self):
        self.refresh_calls += 1

    def navigate_menu(self):
        label = self.selections.pop(0)
        return self.options.index(label)


def _popup(result):
    return SimpleNamespace(navigate_popup=lambda: result)


class TestPlayerHelperCoverage:
    def test_game_quit_declined_instance_popup_keeps_running(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        textbox = RecordingTextBox()

        result = player.game_quit(confirm_popup=_popup(False), textbox=textbox)

        assert result is None
        assert player.quit is False
        assert textbox.messages == []

    def test_character_menu_dispatches_ui_actions_and_quit_flow(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        player.spellbook["Skills"]["Jump"] = SimpleNamespace(name="Jump", modifications=["Long"])
        player.spellbook["Skills"]["Totem"] = SimpleNamespace(
            name="Totem",
            get_unlocked_aspects=lambda: ["Soul"],
        )

        action_calls = []
        menu_textbox = RecordingTextBox()
        quit_textboxes = []

        def record_inventory(self, game, inv_popup=None, confirm_popup=None, useitembox=None):
            action_calls.append(("inventory", getattr(inv_popup, "name", None), useitembox is not None))

        def record_quests(self, game, popup=None):
            action_calls.append(("quests", getattr(popup, "name", None)))

        def record_jump(self, game, jump_popup=None):
            action_calls.append(("jump", getattr(jump_popup, "name", None)))

        def record_totem(self, game, totem_popup=None):
            action_calls.append(("totem", getattr(totem_popup, "name", None)))

        ui_factory = {
            "InventoryPopup": lambda game, name: SimpleNamespace(name=name),
            "QuestsPopup": lambda game, name: SimpleNamespace(name=name),
            "JumpModsPopup": lambda game, name: SimpleNamespace(name=name),
            "TotemAspectsPopup": lambda game, name: SimpleNamespace(name=name),
            "ConfirmPopup": lambda game, header_message=None: _popup(True),
            "TextBox": lambda game: quit_textboxes.append(RecordingTextBox()) or quit_textboxes[-1],
        }
        actions_dict = {
            "ViewInventory": {"name": "Inventory", "method": record_inventory},
            "ViewKeyItems": {"name": "Key Items", "method": lambda *_args, **_kwargs: None},
            "Equipment": {"name": "Equipment", "method": lambda *_args, **_kwargs: None},
            "Specials": None,
            "ViewQuests": {"name": "Quests", "method": record_quests},
            "JumpMods": {"name": "Jump Mods", "method": record_jump},
            "TotemAspects": {"name": "Totem Aspects", "method": record_totem},
            "Quit": {"name": "Quit", "method": Player.game_quit},
        }
        menu = LabelMenu(["Specials", "Inventory", "Quests", "Jump Mods", "Totem Aspects", "Quit Game"])

        result = player.character_menu(
            game=SimpleNamespace(),
            menu=menu,
            textbox=menu_textbox,
            actions_dict=actions_dict,
            ui_factory=ui_factory,
        )

        assert result is True
        assert "Jump Mods" in menu.options
        assert "Totem Aspects" in menu.options
        assert any("does not have a special menu" in message for message in menu_textbox.messages)
        assert action_calls == [
            ("inventory", "Inventory", True),
            ("quests", "Quests"),
            ("jump", "Jump Mods"),
            ("totem", "Totem Aspects"),
        ]
        assert any(textbox.messages == [f"Goodbye, {player.name}!"] for textbox in quit_textboxes)

    def test_quests_screen_and_summon_menu_delegate_to_ui_components(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        popup_calls = []
        player.quests_screen(game=None, popup=SimpleNamespace(navigate_popup=lambda: popup_calls.append("quests")))

        player.summons = {
            "Patagon": SimpleNamespace(inspect=lambda: "A towering summon.")
        }
        summon_messages = []
        summon_box = SimpleNamespace(
            print_text_in_rectangle=lambda message: summon_messages.append(message),
            clear_rectangle=lambda: summon_messages.append("<cleared>"),
        )
        summon_popup = SimpleNamespace(navigate_popup=lambda: 0)
        player.summon_menu(game=None, summonpopup=summon_popup, summonbox=summon_box)

        assert popup_calls == ["quests"]
        assert summon_messages == ["A towering summon.", "<cleared>"]

    def test_summon_menu_requires_ui_components(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")

        with pytest.raises(ValueError):
            player.summon_menu(game=None)

    def test_quests_tracks_bounty_and_named_enemy_completion(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        player.quest_dict = {
            "Bounty": {"Goblin": [{"num": 2}, 1, False]},
            "Main": {"Clear the Cave": {"What": "Orc", "Completed": False}},
            "Side": {
                "Ogre Trouble": {"Type": "Defeat", "What": "Orc", "Completed": False},
                "Something to Cry About": {"Completed": False},
            },
        }

        bounty_message = player.quests(enemy=SimpleNamespace(name="Goblin"))
        named_enemy_message = player.quests(enemy=SimpleNamespace(name="Orc"))
        waitress_message = player.quests(enemy=SimpleNamespace(name="Waitress"))

        assert "completed a bounty" in bounty_message
        assert player.quest_dict["Bounty"]["Goblin"][1] == 2
        assert player.quest_dict["Bounty"]["Goblin"][2] is True
        assert "Clear the Cave" in named_enemy_message
        assert "Ogre Trouble" in named_enemy_message
        assert player.quest_dict["Main"]["Clear the Cave"]["Completed"] is True
        assert player.quest_dict["Side"]["Ogre Trouble"]["Completed"] is True
        assert "Something to Cry About" in waitress_message
        assert player.quest_dict["Side"]["Something to Cry About"]["Completed"] is True

    def test_quests_tracks_item_collection_and_holy_relics(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        rat_tail = items.RatTail()
        player.special_inventory = {
            rat_tail.name: [items.RatTail(), items.RatTail()],
        }
        player.quest_dict = {
            "Bounty": {},
            "Main": {"The Holy Relics": {"Completed": False}},
            "Side": {
                "Rat Trap": {"What": "RatTail", "Total": 2, "Completed": False},
            },
        }
        player.has_relics = lambda: True

        item_message = player.quests(item=rat_tail)
        relic_message = player.quests()

        assert "Rat Trap" in item_message
        assert player.quest_dict["Side"]["Rat Trap"]["Completed"] is True
        assert "The Holy Relics" in relic_message
        assert player.quest_dict["Main"]["The Holy Relics"]["Completed"] is True

    def test_check_mod_support_branches_cover_shield_magic_heal_and_magic_defense(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human", pro_level=3)
        player.equipment["OffHand"] = items.Buckler()
        player.equipment["Ring"] = items.BarrierRing()
        assert player.check_mod("shield") == 30

        player.equipment["OffHand"] = SimpleNamespace(subtyp="Tome", mod=6, damage=0, name="Prayer Tome", weight=0)
        player.stat_effects["Magic"].active = True
        player.stat_effects["Magic"].extra = 3
        assert player.check_mod("heal") == 84

        player.equipment["Pendant"] = items.RubyLocket()
        player.stat_effects["Magic Defense"].active = True
        player.stat_effects["Magic Defense"].extra = 4
        assert player.check_mod("magic def") == 105

        shadowcaster = TestGameState.create_player(class_name="Shadowcaster", race_name="Human")
        shadowcaster.power_up = True
        shadowcaster.class_effects["Power Up"].active = True
        shadowcaster.equipment["Weapon"] = SimpleNamespace(
            name="Void Staff",
            subtyp="Staff",
            damage=20,
            crit=0.1,
            typ="Weapon",
            weight=0,
        )
        shadowcaster.equipment["OffHand"] = SimpleNamespace(
            name="Hex Tome",
            subtyp="Tome",
            mod=7,
            damage=0,
            typ="OffHand",
            weight=0,
        )
        shadowcaster.equipment["Pendant"] = items.PlatinumNecklace()
        shadowcaster.stat_effects["Magic"].active = True
        shadowcaster.stat_effects["Magic"].extra = 3

        assert shadowcaster.check_mod("magic") == 201

    def test_check_mod_support_branches_cover_luck_speed_and_armor_variants(self, monkeypatch):
        rogue = TestGameState.create_player(class_name="Rogue", race_name="Human")
        rogue.power_up = True
        assert rogue.check_mod("luck", luck_factor=6) == 23

        rogue.stat_effects["Speed"].active = True
        rogue.stat_effects["Speed"].extra = 5
        assert rogue.check_mod("speed") == 23

        dragoon = TestGameState.create_player(class_name="Dragoon", race_name="Human")
        dragoon.power_up = True
        dragoon.class_effects["Power Up"].active = True
        dragoon.class_effects["Power Up"].duration = 2
        dragoon.equipment["Armor"] = SimpleNamespace(armor=10, name="Dragon Plate", weight=0)
        dragoon.equipment["Ring"] = items.SteelRing()
        dragoon.stat_effects["Defense"].active = True
        dragoon.stat_effects["Defense"].extra = 3

        assert dragoon.check_mod("armor") == 53
        assert dragoon.check_mod("armor", ignore=True) == 30

        warlock = TestGameState.create_player(class_name="Warlock", race_name="Human")
        warlock.equipment["Armor"] = SimpleNamespace(armor=5, name="Night Robe", weight=0)
        warlock.equipment["Ring"] = items.NoRing()
        warlock.familiar = SimpleNamespace(spec="Homunculus", level=SimpleNamespace(pro_level=2))
        familiar_rolls = iter([1, 2])
        monkeypatch.setattr("src.core.player.random.randint", lambda _a, _b: next(familiar_rolls))

        assert warlock.check_mod("armor") == 19

    def test_check_mod_resist_applies_flying_equipment_familiar_and_class_bonuses(self, monkeypatch):
        geomancer = TestGameState.create_player(class_name="Geomancer", race_name="Human")
        geomancer.power_up = True
        geomancer.class_effects["Power Up"].active = True
        geomancer.resistance["Fire"] = 0.1
        geomancer.equipment["Pendant"] = items.FireChain()
        geomancer.equipment["OffHand"] = items.Svalinn()

        assert geomancer.check_mod("resist", typ="Fire") == pytest.approx(1.35)

        geomancer.flying = True
        assert geomancer.check_mod("resist", typ="Earth") == pytest.approx(1.5)

        shadowcaster = TestGameState.create_player(class_name="Shadowcaster", race_name="Human")
        shadowcaster.stats.charisma = 20
        shadowcaster.familiar = SimpleNamespace(spec="Mephit", level=SimpleNamespace(pro_level=2))
        shadowcaster.equipment["Pendant"] = items.ElementalChain()
        familiar_rolls = iter([1, 2])
        monkeypatch.setattr("src.core.player.random.randint", lambda _a, _b: next(familiar_rolls))

        assert shadowcaster.check_mod("resist", typ="Fire") == pytest.approx(1.0)

        archbishop = TestGameState.create_player(class_name="Archbishop", race_name="Human")
        archbishop.class_effects["Power Up"].active = True

        assert archbishop.check_mod("resist", typ="Holy") == pytest.approx(0.25)

    def test_special_power_grants_shadowcaster_skill_and_invisibility(self):
        player = TestGameState.create_player(class_name="Shadowcaster", race_name="Human")
        events = []
        game = SimpleNamespace(special_event=lambda name: events.append(name))

        result = player.special_power(game)

        assert result == "You gain the skill Veil of Shadows.\n"
        assert events == ["Power Up"]
        assert player.power_up is True
        assert player.invisible is True
        assert "Veil of Shadows" in player.spellbook["Skills"]

    def test_status_string_includes_racial_traits(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")

        status_message = player.status_str()

        assert "Hit Points:" in status_message
        assert "Virtue:" in status_message
        assert "Diligence" in status_message
        assert "Sin:" in status_message
        assert "Lust" in status_message

    def test_combat_equipment_and_resist_strings_render_expected_sections(self):
        player = TestGameState.create_player(class_name="Warrior", race_name="Human")
        player.equipment["Weapon"] = SimpleNamespace(
            name="Falchion",
            crit=0.1,
            damage=12,
            subtyp="Sword",
            typ="Weapon",
            weight=0,
        )
        player.equipment["OffHand"] = SimpleNamespace(
            name="Parrying Dagger",
            crit=0.05,
            damage=5,
            mod=0,
            subtyp="Dagger",
            typ="Weapon",
            weight=0,
        )
        player.equipment["Armor"] = items.PlateMail()
        player.equipment["Ring"] = items.PowerRing()
        player.equipment["Pendant"] = items.FireChain()
        player.buff_str = lambda: "Blessed"

        resist_values = {
            "Fire": 1.5,
            "Electric": 0.5,
            "Earth": 0.0,
            "Shadow": -0.25,
            "Poison": 0.0,
            "Ice": 0.5,
            "Water": 0.0,
            "Wind": -0.1,
            "Holy": 0.25,
            "Physical": 0.1,
        }
        stat_values = {
            "weapon": 11,
            "speed": 4,
            "offhand": 7,
            "armor": 9,
            "shield": 12,
            "magic def": 13,
            "magic": 14,
            "heal": 15,
        }

        def fake_check_mod(mod, enemy=None, typ=None, **_kwargs):
            if mod == "resist":
                return resist_values[typ]
            return stat_values[mod]

        player.check_mod = fake_check_mod

        combat_message = player.combat_str()
        equipment_message = player.equipment_str()
        resist_message = player.resist_str()

        main_crit = int((player.equipment["Weapon"].crit + (BASE_CRIT_PER_POINT * stat_values["speed"])) * 100)
        off_crit = int((player.equipment["OffHand"].crit + (BASE_CRIT_PER_POINT * stat_values["speed"])) * 100)

        assert "Attack:" in combat_message
        assert "11/  7" in combat_message
        assert f"{main_crit}%/{off_crit:>2}%" in combat_message
        assert "Falchion" in equipment_message
        assert "Parrying Dagger" in equipment_message
        assert "Blessed" in equipment_message
        assert "Fire:" in resist_message
        assert "Physical:" in resist_message
