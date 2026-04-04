#!/usr/bin/env python3
"""Focused coverage for curses town flows and helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.ui_curses import town as curses_town


class FakeTextBox:
    messages: list[str] = []

    def __init__(self, game):
        self.game = game

    def print_text_in_rectangle(self, text):
        self.messages.append(text)

    def clear_rectangle(self):
        self.messages.append("cleared")


class FakeQuestPopupMenu:
    drawn: list[tuple[str, ...]] = []

    def __init__(self, game, box_height=0, box_width=0):
        self.game = game

    def draw_popup(self, texts):
        self.drawn.append(tuple(texts))

    def clear_popup(self):
        self.drawn.append(("cleared",))


class FakeSelectionPopupMenu:
    responses: list[int] = []

    def __init__(self, game, header_message, stat_options, box_height=0, rewards=None, confirm=False):
        self.game = game
        self.header_message = header_message
        self.stat_options = stat_options
        self.rewards = rewards or []

    def navigate_popup(self):
        if self.responses:
            return self.responses.pop(0)
        return 0


class FakeConfirmPopupMenu:
    responses: list[bool] = []

    def __init__(self, game, text, box_height=8):
        self.game = game
        self.text = text

    def navigate_popup(self):
        if self.responses:
            return self.responses.pop(0)
        return True

    def clear_popup(self):
        return None


class FakeLocationMenu:
    responses: list[int] = []

    def __init__(self, game, title, options, options_message=None):
        self.game = game
        self.title = title
        self.options_list = list(options)
        self.options_message = options_message
        self.update_history = []

    def navigate_menu(self):
        if self.responses:
            return self.responses.pop(0)
        return len(self.options_list) - 1

    def update_options(self, options, options_message=None, reset_current=True):
        self.options_list = list(options)
        self.update_history.append((tuple(options), options_message, reset_current))

    def draw_all(self):
        return None

    def refresh_all(self):
        return None


class FakeShopPopup:
    responses: list[int] = []

    def __init__(self, game, message, max=None, box_height=8):
        self.game = game
        self.message = message
        self.max = max

    def navigate_popup(self):
        if self.responses:
            return self.responses.pop(0)
        return 1


class FakeTownMenu:
    responses: list[int] = []

    def __init__(self, game, options):
        self.game = game
        self.options_list = list(options)

    def navigate_menu(self):
        if self.responses:
            return self.responses.pop(0)
        return len(self.options_list) - 1


class FakeShopMenu:
    option_responses: list[str] = []
    item_responses: list[str] = []

    def __init__(self, game, message):
        self.game = game
        self.message = message
        self.options = []
        self.itemdict = None

    def update_itemdict(self, itemdict, reset_current=True):
        self.itemdict = itemdict

    def navigate_options(self):
        if self.option_responses:
            return self.option_responses.pop(0)
        return "Leave"

    def update_options(self, options):
        self.options = list(options)

    def reset_options(self, quests=False):
        return None

    def navigate_items(self):
        if self.item_responses:
            return self.item_responses.pop(0)
        return "Go Back"


def _build_player(level=10):
    player = SimpleNamespace()
    player.name = "Ada"
    player.cls = SimpleNamespace(
        name="Warrior",
        equip_check=lambda weapon, slot: weapon.__name__ != "BlockedWeapon",
    )
    player.level = SimpleNamespace(level=level, pro_level=1, exp=0, exp_to_gain=10)
    player.stats = SimpleNamespace(strength=5, intel=4, wisdom=3, con=6, charisma=7, dex=8)
    player.health = SimpleNamespace(current=10, max=10)
    player.mana = SimpleNamespace(current=6, max=6)
    player.gold = 50
    player.storage = {}
    player.inventory = {}
    player.special_inventory = {}
    player.spellbook = {"Spells": {}, "Skills": {}}
    player.summons = {}
    player.warp_point = False
    player.quit = False
    player.encumbered = False
    player.location_x = 1
    player.location_y = 2
    player.location_z = 3
    player.quest_dict = {"Main": {}, "Side": {}, "Bounty": {}}
    player.kill_dict = {"Regular": {}}
    player.world_dict = {
        (3, 0, 5): SimpleNamespace(visited=False, near=False, warped=False),
        (2, 0, 5): SimpleNamespace(near=False),
        (4, 0, 5): SimpleNamespace(near=False),
        (3, 1, 5): SimpleNamespace(near=False),
    }
    player.modified = []
    player.saved = []
    player.changed_location = None
    player.current_weight = lambda: 0
    player.max_weight = lambda: 10
    player.player_level = lambda: level
    player.max_level = lambda: True
    player.has_relics = lambda: False
    player.change_location = lambda x, y, z: setattr(player, "changed_location", (x, y, z))
    player.move_south = lambda game: setattr(player, "moved_south", True)
    def modify_inventory(item, num=1, subtract=False, rare=False, storage=False):
        player.modified.append((item, num, subtract, rare, storage))
        name = getattr(item, "name", str(item))
        if rare:
            if subtract:
                player.special_inventory.pop(name, None)
            else:
                player.special_inventory[name] = item
            return
        bucket = player.storage if storage and not subtract else player.inventory
        if subtract and storage:
            source = player.inventory
            target = player.storage
        elif subtract:
            source = player.inventory
            target = None
        elif storage:
            source = player.storage
            target = player.inventory
        else:
            source = None
            target = player.inventory
        if source is not None and name in source:
            remaining = source[name][num:]
            if remaining:
                source[name] = remaining
            else:
                del source[name]
        if target is not None and not subtract:
            target.setdefault(name, [])
            target[name].extend([item] * num)
        if target is not None and subtract and storage:
            target.setdefault(name, [])
            target[name].extend([item] * num)

    player.modify_inventory = modify_inventory
    player.special_power = lambda game: "Power unlocked.\n"
    player.level_up = lambda game, textbox=None, menu=None: setattr(player.level, "exp_to_gain", "MAX")
    player.character_menu = lambda *args, **kwargs: setattr(player, "opened_character_menu", True)
    player.save = lambda **kwargs: player.saved.append(kwargs)
    return player


def _install_fake_menus(monkeypatch):
    fake_menus = SimpleNamespace(
        TextBox=FakeTextBox,
        QuestPopupMenu=FakeQuestPopupMenu,
        SelectionPopupMenu=FakeSelectionPopupMenu,
        ConfirmPopupMenu=FakeConfirmPopupMenu,
        LocationMenu=FakeLocationMenu,
        ShopPopup=FakeShopPopup,
        ShopMenu=FakeShopMenu,
        TownMenu=FakeTownMenu,
        CharacterMenu=lambda game: SimpleNamespace(game=game),
        InventoryPopupMenu=object(),
        PopupMenu=object(),
        EquipPopupMenu=object(),
        AbilitiesPopupMenu=object(),
        QuestListPopupMenu=object(),
        save_file_popup=lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(curses_town, "menus", fake_menus)
    return fake_menus


def test_ultimate_crafts_selected_weapon(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeSelectionPopupMenu.responses = [0]
    FakeTextBox.messages = []
    player = _build_player()
    player.special_inventory["Unobtainium"] = object()

    class WeaponA:
        def __init__(self):
            self.name = "Astra Blade"

    class WeaponB:
        def __init__(self):
            self.name = "Moon Staff"

    monkeypatch.setattr(curses_town.items, "ultimate_weapons", {"Sword": WeaponA, "Staff": (WeaponB, WeaponA)})
    monkeypatch.setattr(curses_town.time, "sleep", lambda _secs: None)

    game = SimpleNamespace(player_char=player)

    curses_town.ultimate(game)

    assert "Unobtainium" not in player.special_inventory
    assert any(getattr(call[0], "name", "") == "Astra Blade" for call in player.modified)
    assert any("mighty Astra Blade" in str(message) for message in FakeTextBox.messages)


def test_turn_in_quest_handles_gold_rewards_and_collect_cleanup(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeTextBox.messages = []
    player = _build_player()
    player.special_inventory["Rat Tail"] = object()
    player.quest_dict["Side"]["Rat Problem"] = {
        "End Text": "Thanks for the help.",
        "Reward": ["Gold"],
        "Reward Number": 99,
        "Experience": 5,
        "Type": "Collect",
        "What": lambda: SimpleNamespace(name="Rat Tail"),
        "Turned In": False,
    }
    game = SimpleNamespace(player_char=player)

    curses_town.turn_in_quest(game, "Rat Problem", "Side")

    assert player.quest_dict["Side"]["Rat Problem"]["Turned In"] is True
    assert player.gold == 149
    assert player.level.exp == 5
    assert "Rat Tail" not in player.special_inventory
    assert any("99 gold and 5 experience" in str(message) for message in FakeTextBox.messages)


def test_accept_quest_adds_copy_marks_defeat_complete_and_handles_naivete(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeConfirmPopupMenu.responses = [True, True]
    FakeTextBox.messages = []
    player = _build_player()
    player.kill_dict = {"Boss": {"Slime": True}}
    game = SimpleNamespace(player_char=player)

    empty_vial = SimpleNamespace(name="Empty Vial")
    monkeypatch.setattr(curses_town.items, "EmptyVial", lambda: empty_vial)
    monkeypatch.setitem(curses_town.RESPONSE_MAP, "Barkeep", ["Thanks.", "Maybe later."])

    first = {
        "Slime Hunt": {
            "Who": "Barkeep",
            "Start Text": "Please defeat a slime.",
            "Type": "Defeat",
            "What": "Slime",
        }
    }
    second = {
        "Naivete": {
            "Who": "Barkeep",
            "Start Text": "Bring this vial with you.",
            "Type": "Collect",
            "What": "Anything",
        }
    }

    assert curses_town.accept_quest(game, first, "Side") is True
    assert player.quest_dict["Side"]["Slime Hunt"]["Completed"] is True

    assert curses_town.accept_quest(game, second, "Side") is True
    assert any(call[0] is empty_vial and call[3] is True for call in player.modified)


def test_check_quests_respects_prerequisites_and_turns_in_completed_quest(monkeypatch):
    player = _build_player(level=20)
    player.quest_dict["Main"]["Starter"] = {"Turned In": False}
    player.quest_dict["Main"]["Current"] = {"Completed": True, "Turned In": False, "Help Text": "done"}
    game = SimpleNamespace(player_char=player)

    quest_map = {
        "Sergeant": {
            "Main": {
                1: {"Current": {"Help Text": "done", "Completed": False, "Turned In": False}},
                5: {"Locked": {"Requires": "Starter", "Help Text": "locked"}},
                10: {"Open": {"Requires": "Missing", "Help Text": "open"}},
            },
            "Side": {},
        }
    }
    monkeypatch.setattr(curses_town, "quest_dict", quest_map)

    turned_in = []
    accepted = []
    monkeypatch.setattr(curses_town, "turn_in_quest", lambda game, quest, typ: turned_in.append((quest, typ)))
    monkeypatch.setattr(curses_town, "accept_quest", lambda game, quest, typ: accepted.append((list(quest)[0], typ)) or False)

    quest, responses = curses_town.check_quests(game, "Sergeant")

    assert quest is True
    assert turned_in == [("Current", "Main")]
    assert accepted == []
    assert responses[0] == ["I have no new quests for you at this time."]


def test_tavern_patrons_handles_holy_grail_hint_branch(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeLocationMenu.responses = [4, 5]
    FakeTextBox.messages = []
    player = _build_player(level=30)
    player.quest_dict["Side"]["The Holy Grail of Quests"] = {"Completed": False, "Turned In": False}
    game = SimpleNamespace(player_char=player)

    monkeypatch.setattr(curses_town, "check_quests", lambda game, who: (False, [["no quest"]]))
    monkeypatch.setitem(curses_town.PATRON_DIALOGUES, "Hooded Figure", {25: [["fallback"]]})

    curses_town.tavern_patrons(game)

    progress = player.quest_dict["Side"]["The Holy Grail of Quests"]["Chalice Progress"]
    assert progress["Hooded"] is True
    assert any("Golden Chalice" in str(message) for message in FakeTextBox.messages)


def test_barracks_handles_brass_key_and_storage_store_flow(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeLocationMenu.responses = [1, 0, 0, 1, 2, 2]
    FakeShopPopup.responses = [1]
    FakeTextBox.messages = []
    player = _build_player()
    player.special_inventory["Brass Key"] = object()
    potion = SimpleNamespace(name="Potion")
    player.inventory = {"Potion": [potion, potion]}
    game = SimpleNamespace(player_char=player, special_event=lambda name: setattr(game, "event_name", name))

    brass_key = SimpleNamespace(name="Brass Key")
    letter = SimpleNamespace(name="Joffrey's Letter")
    big_potion = SimpleNamespace(name="Great Health Potion")
    monkeypatch.setattr(curses_town.items, "BrassKey", lambda: brass_key)
    monkeypatch.setattr(curses_town.items, "JoffreysLetter", lambda: letter)
    monkeypatch.setattr(curses_town.items, "GreatHealthPotion", lambda: big_potion)

    curses_town.barracks(game)

    assert game.event_name == "Joffrey's Key"
    assert any(call[0] is brass_key and call[2] is True for call in player.modified)
    assert any(call[0] is letter for call in player.modified)
    assert any(call[0] is big_potion and call[1] == 5 for call in player.modified)
    assert any(call[0] is potion and call[2] is True and call[4] is True for call in player.modified)


def test_church_handles_promotion_save_quest_quit_and_leave(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeLocationMenu.responses = [0, 1, 2, 3]
    FakeConfirmPopupMenu.responses = [True]
    FakeTextBox.messages = []
    player = _build_player(level=30)
    player.level.pro_level = 1
    game = SimpleNamespace(player_char=player)

    promoted = []
    monkeypatch.setattr(curses_town.classes, "promotion", lambda game: promoted.append("promoted"), raising=False)
    monkeypatch.setattr(curses_town, "check_quests", lambda game, who: (False, [["quest help"]]))
    monkeypatch.setattr(curses_town.random, "choice", lambda seq: seq[0])

    curses_town.church(game)

    assert promoted == ["promoted"]
    assert len(player.saved) == 1
    assert player.quit is True
    assert any("quest help" in str(message) for message in FakeTextBox.messages)


def test_warp_point_accepts_and_updates_tiles(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeConfirmPopupMenu.responses = [True]
    FakeTextBox.messages = []
    player = _build_player()
    game = SimpleNamespace(player_char=player)

    assert curses_town.warp_point(game) is True
    assert player.world_dict[(3, 0, 5)].visited is True
    assert player.world_dict[(3, 0, 5)].warped is True
    assert player.world_dict[(2, 0, 5)].near is True
    assert player.changed_location == (3, 0, 5)


def test_town_options_and_town_cover_old_warehouse_and_character_menu(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeTownMenu.responses = [7, 8, 6]
    FakeTextBox.messages = []
    player = _build_player(level=12)
    game = SimpleNamespace(player_char=player)

    monkeypatch.setattr("src.core.player.actions_dict", {"Inventory": object()})
    curses_town.town(game)

    assert player.health.current == player.health.max
    assert player.mana.current == player.mana.max
    assert player.opened_character_menu is True
    assert player.changed_location == (5, 10, 1)
    assert any("Authorized personnel only" in str(message) for message in FakeTextBox.messages)


def test_town_options_replaces_old_warehouse_with_warp_point():
    player = _build_player(level=12)
    player.warp_point = True
    game = SimpleNamespace(player_char=player)

    options = curses_town.town_options(game)

    assert "Old Warehouse" not in options
    assert options[-1] == "Warp Point"


def test_buy_and_sell_cover_purchase_and_sale_paths(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeShopMenu.item_responses = ["Potion  Healing Potion  10  0", "Go Back", "Potion  Healing Potion x2", "Go Back"]
    FakeShopPopup.responses = [2, 1]
    FakeConfirmPopupMenu.responses = [True, True]
    FakeTextBox.messages = []
    player = _build_player()
    player.gold = 100
    player.stats.charisma = 10
    potion = lambda: SimpleNamespace(name="Healing Potion", value=20, ultimate=False)
    player.inventory = {"Healing Potion": [potion(), potion()]}
    game = SimpleNamespace(player_char=player)
    menu = FakeShopMenu(game, "shop")

    monkeypatch.setattr(
        curses_town.items,
        "items_dict",
        {"Potion": {"Potion": [potion]}, "Misc": {}, "Accessory": {"Ring": [], "Pendant": []}},
    )

    assert curses_town.buy(game, menu, "Alchemist") is True
    assert any(getattr(call[0], "name", "") == "Healing Potion" and call[1] == 2 for call in player.modified)
    assert player.gold == 80

    player.modified.clear()
    assert curses_town.sell(game, menu) is True
    assert player.gold == 80 + int(0.025 * player.stats.charisma * 20)
    assert any(call[2] is True for call in player.modified)


def test_blacksmith_and_secret_shop_cover_leave_and_special_branches(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeShopMenu.option_responses = ["Leave", "Leave"]
    FakeTextBox.messages = []
    player = _build_player(level=65)
    player.cls.name = "Summoner"
    player.special_inventory.update({"Triangulus": object(), "Quadrata": object(), "Unobtainium": object()})
    player.world_dict[(9, 1, 6)] = SimpleNamespace(visited=True)
    game = SimpleNamespace(player_char=player)

    monkeypatch.setattr(curses_town, "ultimate", lambda game: setattr(game, "ultimate_called", True))
    monkeypatch.setattr(curses_town.items, "VulcansHammer", lambda: SimpleNamespace(name="Vulcan's Hammer"))
    monkeypatch.setattr(
        curses_town,
        "quest_dict",
        {"Griswold": {"Side": {60: {"He Ain't Heavy": {"Completed": False}}}}},
    )

    curses_town.blacksmith(game)
    curses_town.secret_shop(game)

    assert game.ultimate_called is True
    assert "He Ain't Heavy" in player.quest_dict["Side"]
    assert player.quest_dict["Side"]["He Ain't Heavy"]["Completed"] is True
    assert any(getattr(call[0], "name", "") == "Vulcan's Hammer" for call in player.modified)
    assert player.moved_south is True


def test_tavern_covers_bounty_accept_turn_in_and_leave(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeLocationMenu.responses = [1, 0, 2]
    FakeTextBox.messages = []
    player = _build_player(level=20)
    reward_item = lambda: SimpleNamespace(name="Ruby")
    bounty = {"enemy": SimpleNamespace(name="Rat"), "num": 3, "gold": 12, "exp": 5, "reward": reward_item}
    player.quest_dict["Bounty"] = {"Rat": [bounty, 3, True]}
    game = SimpleNamespace(player_char=player, bounties={"Wolf": {"enemy": SimpleNamespace(name="Wolf"), "num": 2, "gold": 9, "exp": 4, "reward": None}})
    game.delete_bounty = lambda selection: None

    curses_town.tavern(game)

    assert player.gold == 62
    assert player.level.exp == 5
    assert "Rat" not in player.quest_dict["Bounty"]
    assert any(getattr(call[0], "name", "") == "Ruby" for call in player.modified)
    assert any("Come back whenever you'd like." in str(message) for message in FakeTextBox.messages)


def test_tavern_job_board_accepts_and_abandons_bounties(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeLocationMenu.responses = [1, 0, 0, 0, 0, 2]
    FakeConfirmPopupMenu.responses = [True, True]
    FakeTextBox.messages = []
    player = _build_player(level=20)
    game = SimpleNamespace(
        player_char=player,
        bounties={"Wolf": {"enemy": SimpleNamespace(name="Wolf"), "num": 2, "gold": 9, "exp": 4, "reward": None}},
    )
    deleted = []
    game.delete_bounty = lambda selection: deleted.append(selection["enemy"].name)

    curses_town.tavern(game)

    assert deleted == ["Wolf"]
    assert "Wolf" not in player.quest_dict["Bounty"]
    assert any("Return here when the job is done" in str(message) for message in FakeTextBox.messages)


def test_barracks_quest_branch_handles_sergeant_chalice_hint(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeLocationMenu.responses = [0, 2]
    FakeTextBox.messages = []
    player = _build_player()
    player.special_inventory["Chalice Map"] = object()
    player.quest_dict["Side"]["The Holy Grail of Quests"] = {"Completed": False, "Turned In": False}
    game = SimpleNamespace(player_char=player, special_event=lambda name: None)

    monkeypatch.setattr(curses_town, "check_quests", lambda game, who: (False, [["fallback"]]))

    curses_town.barracks(game)

    progress = player.quest_dict["Side"]["The Holy Grail of Quests"]["Chalice Progress"]
    assert progress["Map"] is True
    assert progress["Sergeant"] is True
    assert any("hidden route somewhere on the third floor" in str(message) for message in FakeTextBox.messages)


def test_barracks_storage_retrieves_items(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeLocationMenu.responses = [1, 1, 0, 1, 2, 2]
    FakeShopPopup.responses = [1]
    player = _build_player()
    potion = SimpleNamespace(name="Potion")
    player.storage = {"Potion": [potion, potion]}
    game = SimpleNamespace(player_char=player, special_event=lambda name: None)

    curses_town.barracks(game)

    assert "Potion" in player.inventory
    assert len(player.inventory["Potion"]) == 1
    assert len(player.storage["Potion"]) == 1


def test_alchemist_and_jeweler_quest_wrappers_show_response(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeShopMenu.option_responses = ["Quests", "Leave", "Quests", "Leave"]
    FakeTextBox.messages = []
    player = _build_player(level=30)
    game = SimpleNamespace(player_char=player)

    monkeypatch.setattr(curses_town, "check_quests", lambda game, who: (False, [[f"{who} help"]]))
    monkeypatch.setattr(curses_town.random, "choice", lambda seq: seq[0])

    curses_town.alchemist(game)
    curses_town.jeweler(game)

    assert any("Alchemist help" in str(message) for message in FakeTextBox.messages)
    assert any("Jeweler help" in str(message) for message in FakeTextBox.messages)


def test_church_handles_unavailable_promotion_and_leave(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeLocationMenu.responses = [0, 4]
    FakeTextBox.messages = []
    player = _build_player(level=15)
    player.level.pro_level = 1
    game = SimpleNamespace(player_char=player)

    curses_town.church(game)

    assert any("need to be level 30" in str(message) for message in FakeTextBox.messages)
    assert any("Let the light of Elysia guide you." in str(message) for message in FakeTextBox.messages)


def test_ultimate_armor_repo_crafts_selected_armor(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeSelectionPopupMenu.responses = [0]
    FakeConfirmPopupMenu.responses = [True]
    FakeTextBox.messages = []
    player = _build_player()
    player.quest_dict["Side"]["He Ain't Heavy"] = {"Completed": False}
    tile = SimpleNamespace(looted=False)
    player.world_dict[(player.location_x, player.location_y, player.location_z)] = tile
    game = SimpleNamespace(player_char=player)

    robe = SimpleNamespace(name="Merlin Robe", description="A robe of legends.")
    monkeypatch.setattr(curses_town.items, "MerlinRobe", lambda: robe)
    monkeypatch.setattr(curses_town.items, "DragonHide", lambda: SimpleNamespace(name="Dragon Hide", description="Hide"))
    monkeypatch.setattr(curses_town.items, "Aegis", lambda: SimpleNamespace(name="Aegis", description="Shield"))
    monkeypatch.setattr(curses_town.items, "Genji", lambda: SimpleNamespace(name="Genji", description="Armor"))
    monkeypatch.setattr(curses_town.time, "sleep", lambda _secs: None)

    curses_town.ultimate_armor_repo(game)

    assert player.quest_dict["Side"]["He Ain't Heavy"]["Completed"] is True
    assert tile.looted is True
    assert any(call[0] is robe for call in player.modified)
    assert player.moved_south is True


def test_warp_point_decline_branch(monkeypatch):
    _install_fake_menus(monkeypatch)
    FakeConfirmPopupMenu.responses = [False]
    FakeTextBox.messages = []
    player = _build_player()
    game = SimpleNamespace(player_char=player)

    assert curses_town.warp_point(game) is None
    assert any("Not a problem" in str(message) for message in FakeTextBox.messages)
