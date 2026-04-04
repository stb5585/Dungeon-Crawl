#!/usr/bin/env python3
"""Focused coverage for pygame quest-manager helpers and flows."""

from __future__ import annotations

from types import SimpleNamespace

from src.ui_pygame.gui import quest_manager


class DummyItem:
    def __init__(
        self,
        name="Reward Blade",
        *,
        typ="Weapon",
        subtyp="Sword",
        value=100,
        description="Reward item description.",
        damage=3,
        armor=0,
        magic=0,
        magic_defense=0,
    ):
        self.name = name
        self.typ = typ
        self.subtyp = subtyp
        self.value = value
        self.description = description
        self.damage = damage
        self.armor = armor
        self.magic = magic
        self.magic_defense = magic_defense


class EmptyVial:
    def __init__(self):
        self.name = "Empty Vial"


class ShieldReward(DummyItem):
    def __init__(self):
        super().__init__("Shield Reward", typ="OffHand", subtyp="Shield")


class FakePopup:
    messages = []
    responses = []

    def __init__(self, _presenter, message, show_buttons=True):
        self.message = message
        self.show_buttons = show_buttons
        FakePopup.messages.append((message, show_buttons))

    def show(self, **_kwargs):
        if FakePopup.responses:
            return FakePopup.responses.pop(0)
        return None


class FakeRewardSelectionPopup:
    responses = []

    def __init__(self, _presenter, _title, items, detail_provider):
        self.items = items
        self.detail_provider = detail_provider

    def show(self):
        return FakeRewardSelectionPopup.responses.pop(0)


class FakeLevelUpScreen:
    calls = []

    def __init__(self, _screen, _presenter):
        pass

    def show_level_up(self, player_char, _arg):
        FakeLevelUpScreen.calls.append(player_char.level.exp)
        player_char.level.exp_to_gain = 1


def _make_presenter():
    return SimpleNamespace(screen=object())


def _make_player(level=12):
    inventory_calls = []

    def modify_inventory(item, num=1, subtract=False, rare=False):
        inventory_calls.append((item.name, num, subtract, rare))

    player = SimpleNamespace(
        gold=0,
        level=SimpleNamespace(level=level, pro_level=2, exp=0, exp_to_gain=0),
        quest_dict={"Main": {}, "Side": {}},
        inventory={},
        special_inventory={},
        spellbook={"Spells": {}},
        kill_dict={},
        warp_point=False,
        modify_inventory=modify_inventory,
        player_level=lambda: level,
        max_level=lambda: False,
        has_relics=lambda: False,
    )
    player.inventory_calls = inventory_calls
    return player


def _manager(player=None, **kwargs):
    return quest_manager.QuestManager(_make_presenter(), player or _make_player(), **kwargs)


def test_formatting_and_chalice_hint_helpers(monkeypatch):
    player = _make_player()
    player.quest_dict["Side"]["The Holy Grail of Quests"] = {
        "Completed": False,
        "Turned In": False,
        "Help Text": "",
    }
    rendered = []
    manager = _manager(player, quest_text_renderer=lambda text: rendered.append(text), wrap_width=12)

    assert manager._format_for_renderer("alpha beta gamma") == "alpha beta\ngamma"
    preserved = _manager(player, renderer_preserve_formatting=True)
    assert preserved._format_for_renderer("a\nb") == "a\nb"

    progress = manager._ensure_chalice_progress(player.quest_dict["Side"]["The Holy Grail of Quests"])
    assert progress["Hooded"] is False
    assert progress["Spawned"] is False

    assert manager._handle_chalice_giver_hint("Hooded Figure") is True
    assert progress["Hooded"] is True
    assert "ugly sword" in rendered[-1]

    player.special_inventory["Chalice Map"] = [DummyItem("Chalice Map", typ="Misc", subtyp="Key")]
    assert manager._handle_chalice_giver_hint("Sergeant") is True
    assert progress["Sergeant"] is True
    assert "third" in rendered[-1]
    assert "floor" in rendered[-1]


def test_show_hint_eligible_quests_and_random_help(monkeypatch):
    player = _make_player(level=10)
    player.quest_dict = {
        "Main": {"Quest A": {"Help Text": "Find the key.", "Turned In": False}},
        "Side": {"Quest B": {"Help Text": "Visit the ruins.", "Turned In": False}},
    }
    rendered = []
    manager = _manager(player, quest_text_renderer=lambda text: rendered.append(text), wrap_width=15)

    monkeypatch.setattr(
        quest_manager,
        "quest_dict",
        {
            "Guide": {
                "Main": {"5": [{"Quest A": {"Type": "Talk"}}][0]},
                "Side": {"10": [{"Quest B": {"Type": "Collect"}}][0]},
            }
        },
    )
    monkeypatch.setattr(quest_manager, "get_holy_grail_rotation_hints", lambda _player, _giver: ["Secret grail hint"])
    monkeypatch.setattr(quest_manager.random, "choice", lambda seq: seq[0])

    mains, sides = manager._eligible_quests("Guide")
    assert list(mains[0].keys()) == ["Quest A"]
    assert list(sides[0].keys()) == ["Quest B"]
    assert manager.get_random_help_hint("Guide") == "Find the key."

    monkeypatch.setattr(quest_manager, "ConfirmationPopup", FakePopup)
    manager_no_renderer = _manager(player, wrap_width=10)
    manager_no_renderer._show_hint("This is a popup hint")
    assert "This is a" in FakePopup.messages[-1][0]


def test_can_offer_and_already_killed_helpers():
    player = _make_player()
    player.quest_dict["Main"]["Earlier"] = {"Turned In": True}
    player.quest_dict["Side"]["Blocked"] = {"Turned In": False}
    player.kill_dict = {"Boss": {"Dragon": 1}}
    manager = _manager(player)

    assert manager._can_offer_quest("Any", {}, "Main") is True
    assert manager._can_offer_quest("Later", {"Requires": "Earlier"}, "Main") is True
    assert manager._can_offer_quest("Later", {"Requires": "Blocked"}, "Main") is False
    assert manager._can_offer_quest("Later", {"Requires": "Missing"}, "Main") is False
    assert manager._already_killed("Dragon") is True
    assert manager._already_killed("Slime") is False


def test_offer_accept_covers_kill_check_relics_naivete_and_decline(monkeypatch):
    player = _make_player()
    player.kill_dict = {"Boss": {"Goblin King": 1}}
    player.has_relics = lambda: True
    rendered = []
    choices = iter([0, 0, 0, 1])
    manager = _manager(
        player,
        quest_text_renderer=lambda text: rendered.append(text),
        quest_choice_renderer=lambda _prompt, _options: next(choices),
    )

    monkeypatch.setattr(quest_manager, "RESPONSE_MAP", {"Guide": ["Accepted!", "Declined!"]})
    monkeypatch.setattr(quest_manager.items, "EmptyVial", EmptyVial, raising=False)

    assert manager._offer("Guide", "Defeat Quest", {"Type": "Defeat", "What": "Goblin King"}, "Main") is True
    assert player.quest_dict["Main"]["Defeat Quest"]["Completed"] is True

    assert manager._offer("Guide", "The Holy Relics", {"Type": "Collect", "What": "Relics"}, "Main") is True
    assert player.quest_dict["Main"]["The Holy Relics"]["Completed"] is True

    assert manager._offer("Guide", "Naivete", {"Type": "Collect", "What": "Vial"}, "Side") is True
    assert ("Empty Vial", 1, False, True) in player.inventory_calls
    assert manager._offer("Guide", "Declined Quest", {"Type": "Talk"}, "Side") is False
    assert any("Accepted!" in text for text in rendered)
    assert any("Declined!" in text for text in rendered)


def test_turn_in_handles_gold_collect_cleanup_and_levelup(monkeypatch):
    player = _make_player()
    player.level.exp_to_gain = -5
    player.quest_dict["Main"]["Collect Quest"] = {
        "End Text": "You did it.",
        "Experience": 5,
        "Reward": ["Gold"],
        "Reward Number": 30,
        "Type": "Collect",
        "What": "QuestGem",
        "Total": 2,
        "Completed": True,
        "Turned In": False,
    }
    player.inventory["QuestGem"] = [DummyItem("QuestGem", typ="Misc", subtyp="Gem"), DummyItem("QuestGem", typ="Misc", subtyp="Gem")]
    rendered = []
    manager = _manager(player, quest_text_renderer=lambda text: rendered.append(text))

    FakeLevelUpScreen.calls = []
    monkeypatch.setattr(quest_manager, "LevelUpScreen", FakeLevelUpScreen)

    events = []
    monkeypatch.setattr(manager, "_handle_quest_events", lambda quest_name: events.append(quest_name))

    manager._turn_in("Collect Quest", "Main")

    assert player.gold == 30
    assert player.level.exp == 10
    assert FakeLevelUpScreen.calls == [10]
    assert "QuestGem" not in player.inventory
    assert player.quest_dict["Main"]["Collect Quest"]["Turned In"] is True
    assert events == ["Collect Quest"]
    assert any("Quest turned in: Collect Quest" in text for text in rendered)


def test_turn_in_handles_reward_selection_and_bad_dream_event(monkeypatch):
    player = _make_player()
    player.quest_dict["Side"]["A Bad Dream"] = {
        "End Text": "Nightmare solved.",
        "Experience": 0,
        "Reward": [DummyItem, ShieldReward],
        "Reward Number": 1,
        "Type": "Talk",
        "Completed": True,
        "Turned In": False,
    }
    player.quest_dict["Side"]["Where's the Beef?"] = {"Turned In": False}

    FakeRewardSelectionPopup.responses = [None, 1]
    monkeypatch.setattr(quest_manager, "RewardSelectionPopup", FakeRewardSelectionPopup)
    monkeypatch.setattr(quest_manager, "LevelUpScreen", FakeLevelUpScreen)
    monkeypatch.setattr(
        "src.core.data.data_loader.get_special_events",
        lambda: {"Busboy": {"Text": ["Busboy event line 1", "Busboy event line 2"]}},
    )
    rendered = []
    manager = _manager(player, quest_text_renderer=lambda text: rendered.append(text))

    manager._turn_in("A Bad Dream", "Side")

    assert any(call[0] == "Shield Reward" for call in player.inventory_calls)
    beef = player.quest_dict["Side"]["Where's the Beef?"]
    assert beef["Who"] == "Busboy"
    assert "help feed a lot of people" in beef["End Text"]
    assert any("Busboy event line 1" in text for text in rendered)


def test_check_and_offer_covers_turnin_offer_help_and_noquest(monkeypatch):
    player = _make_player(level=12)
    player.quest_dict["Main"]["Done Quest"] = {"Completed": True, "Turned In": False}
    player.quest_dict["Main"]["Help Quest"] = {"Help Text": "Need help here.", "Turned In": False}
    manager = _manager(player)

    monkeypatch.setattr(
        manager,
        "_eligible_quests",
        lambda giver: ([{"Done Quest": {"Type": "Talk"}}, {"New Quest": {"Type": "Talk"}}], []),
    )

    turnins = []
    offers = []
    monkeypatch.setattr(manager, "_turn_in", lambda name, typ: turnins.append((name, typ)))
    monkeypatch.setattr(manager, "_offer", lambda giver, name, q, typ: offers.append((giver, name, typ)) or False)
    monkeypatch.setattr(manager, "_handle_chalice_giver_hint", lambda giver: False)
    monkeypatch.setattr(quest_manager, "get_holy_grail_rotation_hints", lambda _player, _giver: [])
    monkeypatch.setattr(quest_manager.random, "choice", lambda seq: seq[0])
    monkeypatch.setattr(quest_manager, "ConfirmationPopup", FakePopup)
    FakePopup.messages = []

    acted, showed = manager.check_and_offer("Guide")
    assert (acted, showed) == (True, True)
    assert turnins == [("Done Quest", "Main")]

    player.quest_dict["Main"]["Done Quest"]["Turned In"] = True
    monkeypatch.setattr(
        manager,
        "_eligible_quests",
        lambda giver: ([{"Done Quest": {"Type": "Talk"}}, {"Help Quest": {"Type": "Talk"}}, {"New Quest": {"Type": "Talk"}}], []),
    )
    acted, showed = manager.check_and_offer("Guide")
    assert (acted, showed) == (False, True)
    assert offers == [("Guide", "New Quest", "Main")]
    assert "Need help here." in FakePopup.messages[-1][0]

    player.quest_dict["Main"]["Help Quest"]["Turned In"] = True
    monkeypatch.setattr(manager, "_eligible_quests", lambda giver: ([], []))
    FakePopup.messages = []
    acted, showed = manager.check_and_offer("Guide", show_help=False)
    assert (acted, showed) == (False, True)
    assert "no new quests" in FakePopup.messages[-1][0].lower()


def test_turn_in_popup_reward_variants_and_collect_cleanup(monkeypatch):
    player = _make_player()
    player.max_level = lambda: True
    player.quest_dict["Side"]["Warp Trial"] = {
        "End Text": "Warp unlocked.",
        "Experience": 2,
        "Reward": ["Warp Point"],
        "Reward Number": 1,
        "Type": "Collect",
        "What": DummyItem,
        "Total": 1,
        "Completed": True,
        "Turned In": False,
    }
    player.inventory["Reward Blade"] = [DummyItem()]
    player.special_inventory["Reward Blade"] = [DummyItem()]
    FakePopup.messages = []
    monkeypatch.setattr(quest_manager, "ConfirmationPopup", FakePopup)
    monkeypatch.setattr(quest_manager, "LevelUpScreen", FakeLevelUpScreen)

    manager = _manager(player)
    manager._handle_quest_events = lambda _name: None
    manager._turn_in("Warp Trial", "Side")

    assert player.warp_point is True
    assert "Reward Blade" not in player.special_inventory
    assert "Reward Blade" in player.inventory
    assert any("Warp Point access" in message for message, _buttons in FakePopup.messages)

    player.quest_dict["Side"]["Gold Trial"] = {
        "End Text": "",
        "Experience": 0,
        "Reward": ["Gold"],
        "Reward Number": 25,
        "Type": "Talk",
        "Completed": True,
        "Turned In": False,
    }
    manager._turn_in("Gold Trial", "Side")
    assert player.gold == 25


def test_offer_without_renderer_and_check_and_offer_side_branches(monkeypatch):
    player = _make_player(level=20)
    FakePopup.messages = []
    FakePopup.responses = [None, True, None, False]
    monkeypatch.setattr(quest_manager, "ConfirmationPopup", FakePopup)
    monkeypatch.setattr(quest_manager, "RESPONSE_MAP", {"Priest": ["Blessings.", "Come back later."]})

    manager = _manager(player)
    accepted = manager._offer("Priest", "Popup Quest", {"Start Text": "A popup intro.", "Type": "Talk"}, "Main")
    declined = manager._offer("Priest", "Declined Popup Quest", {"Start Text": "Second intro.", "Type": "Talk"}, "Main")

    assert accepted is True
    assert declined is False
    assert "Popup Quest" in player.quest_dict["Main"]
    assert any("Blessings." in message for message, _buttons in FakePopup.messages)
    assert any("Come back later." in message for message, _buttons in FakePopup.messages)

    player.quest_dict["Main"] = {"Relic Quest": {"Completed": False, "Turned In": False}}
    player.has_relics = lambda: True
    monkeypatch.setattr(
        manager,
        "_eligible_quests",
        lambda giver: ([{"Relic Quest": {"Type": "Collect", "What": "Relics"}}], [{"Pandora's Box": {"Type": "Talk"}}]),
    )
    turnins = []
    monkeypatch.setattr(manager, "_turn_in", lambda name, typ: turnins.append((name, typ)))
    monkeypatch.setattr(manager, "_offer", lambda giver, name, q, typ: (_ for _ in ()).throw(AssertionError("should not offer")))
    monkeypatch.setattr(manager, "_handle_chalice_giver_hint", lambda giver: True)
    acted, showed = manager.check_and_offer("Priest", show_help=False)
    assert (acted, showed) == (True, True)
    assert player.quest_dict["Main"]["Relic Quest"]["Completed"] is True
    assert turnins == [("Relic Quest", "Main")]

    monkeypatch.setattr(manager, "_eligible_quests", lambda giver: ([], []))
    monkeypatch.setattr(manager, "_handle_chalice_giver_hint", lambda giver: False)
    FakePopup.messages = []
    acted, showed = manager.check_and_offer("Priest", suppress_no_quests_message=True)
    assert (acted, showed) == (False, False)


def test_handle_quest_events_popup_fallback(monkeypatch):
    player = _make_player()
    player.quest_dict["Side"]["Where's the Beef?"] = {"Turned In": False}
    FakePopup.messages = []
    monkeypatch.setattr(quest_manager, "ConfirmationPopup", FakePopup)
    monkeypatch.setattr(
        "src.core.data.data_loader.get_special_events",
        lambda: {"Busboy": {"Text": ["Busboy popup line"]}},
    )

    manager = _manager(player)
    manager._handle_quest_events("A Bad Dream")

    assert any("Busboy popup line" in message for message, _buttons in FakePopup.messages)
    assert player.quest_dict["Side"]["Where's the Beef?"]["Who"] == "Busboy"
