#!/usr/bin/env python3
"""Focused coverage for pygame shop-manager helper logic."""

from __future__ import annotations

from types import SimpleNamespace

from src.ui_pygame.gui import shops


class DummyFont:
    def render(self, text, _antialias, _color):
        return SimpleNamespace(get_width=lambda: len(text) * 8)

    def get_height(self):
        return 16


class DummyScreen:
    def blit(self, *_args, **_kwargs):
        return None

    def fill(self, *_args, **_kwargs):
        return None


def _make_presenter():
    return SimpleNamespace(
        screen=DummyScreen(),
        width=640,
        height=480,
        title_font=DummyFont(),
        large_font=DummyFont(),
        normal_font=DummyFont(),
        small_font=DummyFont(),
        show_message=lambda message: None,
    )


def _make_player(*, level=12, in_town=True, gold=500):
    inventory = {}
    calls = []

    def modify_inventory(item, num=1, subtract=False):
        calls.append((item.name, num, subtract))

    player = SimpleNamespace(
        gold=gold,
        inventory=inventory,
        special_inventory={},
        equipment={},
        stats=SimpleNamespace(strength=10),
        level=SimpleNamespace(level=level),
        in_town=lambda: in_town,
        player_level=lambda: level,
        modify_inventory=modify_inventory,
        equip_diff=lambda item, slot, buy=False: "",
    )
    player.inventory_calls = calls
    return player


class FakePopup:
    responses = []
    messages = []
    calls = []

    def __init__(self, _presenter, message, show_buttons=True):
        self.message = message
        self.show_buttons = show_buttons
        FakePopup.messages.append((message, show_buttons))

    def show(self, background_draw_func=None, **kwargs):
        FakePopup.calls.append(kwargs)
        if background_draw_func:
            background_draw_func()
        if FakePopup.responses:
            return FakePopup.responses.pop(0)
        return None


class FakeQuantityPopup:
    responses = []
    created = []

    def __init__(self, _presenter, item_name, price, max_qty, action="buy", default_quantity=1):
        self.item_name = item_name
        self.price = price
        self.max_qty = max_qty
        self.action = action
        self.default_quantity = default_quantity
        FakeQuantityPopup.created.append((item_name, price, max_qty, action, default_quantity))

    def show(self, background_draw_func=None, **_kwargs):
        if background_draw_func:
            background_draw_func()
        return FakeQuantityPopup.responses.pop(0)


class FakeShopScreen:
    option_sequences = []
    item_sequences = []
    instances = []

    def __init__(self, _presenter, _player_char, shop_message, background_image="town.png", options_list=None):
        self.shop_message = shop_message
        self.background_image = background_image
        self.options = list(options_list or [])
        self.set_calls = []
        self.update_calls = []
        self.draw_calls = []
        self._navigate_options = list(FakeShopScreen.option_sequences.pop(0) if FakeShopScreen.option_sequences else [])
        self._navigate_items = list(FakeShopScreen.item_sequences.pop(0) if FakeShopScreen.item_sequences else [])
        FakeShopScreen.instances.append(self)

    def set_options(self, options):
        self.options = list(options)
        self.set_calls.append(list(options))

    def navigate_options(self):
        return self._navigate_options.pop(0) if self._navigate_options else None

    def update_item_list(self, itemdict, action):
        self.update_calls.append((itemdict, action))

    def navigate_items(self):
        return self._navigate_items.pop(0) if self._navigate_items else None

    def draw_all(self, do_flip=True):
        self.draw_calls.append(do_flip)

    def display_quest_text(self, text):
        self.last_quest_text = text


class FakeQuestManager:
    instances = []

    def __init__(self, _presenter, _player_char, quest_text_renderer):
        self.quest_text_renderer = quest_text_renderer
        self.calls = []
        FakeQuestManager.instances.append(self)

    def check_and_offer(self, who):
        self.calls.append(who)


class DummyItem:
    def __init__(
        self,
        name="Bronze Sword",
        *,
        typ="Weapon",
        subtyp="Sword",
        description="A simple sword for testing description wrapping.",
        value=40,
        rarity=0.8,
        damage=0,
        armor=0,
        magic=0,
        magic_defense=0,
        restriction=None,
        ultimate=False,
    ):
        self.name = name
        self.typ = typ
        self.subtyp = subtyp
        self.description = description
        self.value = value
        self.rarity = rarity
        self.damage = damage
        self.armor = armor
        self.magic = magic
        self.magic_defense = magic_defense
        self.restriction = [] if restriction is None else restriction
        self.ultimate = ultimate


def _manager(monkeypatch, *, level=12, in_town=True, gold=500):
    FakePopup.responses = []
    FakePopup.messages = []
    FakePopup.calls = []
    FakeQuantityPopup.responses = []
    FakeQuantityPopup.created = []
    FakeShopScreen.option_sequences = []
    FakeShopScreen.item_sequences = []
    FakeShopScreen.instances = []
    FakeQuestManager.instances = []
    monkeypatch.setattr("src.ui_pygame.gui.town_base.TownScreenBase._load_background", lambda self: setattr(self, "background", None))
    return shops.ShopManager(_make_presenter(), _make_player(level=level, in_town=in_town, gold=gold))


def test_visit_blacksmith_and_jeweler_closed_show_popup(monkeypatch):
    manager = _manager(monkeypatch, level=3)
    monkeypatch.setattr(shops, "ConfirmationPopup", FakePopup)

    manager.visit_blacksmith()
    manager.visit_jeweler()

    assert any("blacksmith is currently closed" in message for message, _buttons in FakePopup.messages)
    assert any("jeweler is currently closed" in message for message, _buttons in FakePopup.messages)
    assert all(call.get("flush_events") for call in FakePopup.calls)


def test_visit_blacksmith_handles_unobtainium_buy_branch_and_leave(monkeypatch):
    manager = _manager(monkeypatch, level=12)
    manager.player_char.special_inventory["Unobtainium"] = [object()]
    shown_messages = []
    manager.presenter.show_message = lambda message: shown_messages.append(message)
    buy_calls = []

    FakeShopScreen.option_sequences = [["Buy", "Weapons", "Leave"]]
    monkeypatch.setattr(shops, "ShopScreen", FakeShopScreen)
    monkeypatch.setattr(shops, "ConfirmationPopup", FakePopup)
    monkeypatch.setattr("src.ui_pygame.gui.quest_manager.QuestManager", FakeQuestManager)
    monkeypatch.setattr(manager, "buy_weapons", lambda: buy_calls.append("weapons"))

    manager.visit_blacksmith()

    assert any("Unobtainium" in message for message in shown_messages)
    assert buy_calls == ["weapons"]
    assert FakeShopScreen.instances[0].set_calls[:2] == [
        ["Buy", "Sell", "Quests", "Leave"],
        ["Weapons", "Shields", "Armor", "Back"],
    ]
    assert FakeShopScreen.instances[0].shop_message == "Griswold's Blacksmith"
    assert any("Come back whenever you'd like." in message for message, _buttons in FakePopup.messages)


def test_visit_alchemist_and_jeweler_cover_quest_and_sell_paths(monkeypatch):
    manager = _manager(monkeypatch, level=15)
    sell_calls = []

    FakeShopScreen.option_sequences = [["Quests", "Sell", "Leave"], ["Quests", "Leave"]]
    monkeypatch.setattr(shops, "ShopScreen", FakeShopScreen)
    monkeypatch.setattr(shops, "ConfirmationPopup", FakePopup)
    monkeypatch.setattr("src.ui_pygame.gui.quest_manager.QuestManager", FakeQuestManager)
    monkeypatch.setattr(manager, "sell_items", lambda: sell_calls.append("sold"))

    manager.visit_alchemist()
    manager.visit_jeweler()

    assert FakeQuestManager.instances[0].calls == ["Alchemist"]
    assert FakeQuestManager.instances[1].calls == ["Jeweler"]
    assert sell_calls == ["sold"]
    assert any("Good luck on your adventures!" in message for message, _buttons in FakePopup.messages)
    assert any("May fortune favor you!" in message for message, _buttons in FakePopup.messages)


def test_buy_helpers_route_to_expected_equipment_methods(monkeypatch):
    manager = _manager(monkeypatch, level=20)
    item_calls = []

    monkeypatch.setattr(manager, "buy_equipment", lambda item_list, category_name, background_image="town.png": item_calls.append((item_list, category_name, background_image)))
    monkeypatch.setattr(manager, "_buy_with_shop_screen", lambda itemdict, category_name, background_image="town.png": item_calls.append((itemdict, category_name, background_image)))

    FakeShopScreen.option_sequences = [["1-Handed", "Sword"], ["Light"]]
    monkeypatch.setattr(shops, "ShopScreen", FakeShopScreen)
    monkeypatch.setattr(manager, "_has_available_items", lambda _item_list: True)

    manager.buy_weapons()
    manager.buy_armor()
    manager.buy_shields()
    manager.buy_rings()
    manager.buy_pendants()
    manager.buy_scrolls(background_image="dungeon.png")
    manager.buy_misc()
    manager.buy_potions(background_image="dungeon.png")

    assert item_calls[0][1] == "Sword"
    assert item_calls[1][1] == "Light"
    assert item_calls[2][1] == "Shield"
    assert item_calls[3][1] == "Ring"
    assert item_calls[4][1] == "Pendant"
    assert item_calls[5][1] == "Scroll"
    assert item_calls[5][2] == "dungeon.png"
    assert item_calls[6][1] == "Misc"
    assert item_calls[7][1] == "Potions"
    assert item_calls[7][2] == "dungeon.png"


def test_buy_helpers_return_early_for_back_and_unavailable_items(monkeypatch):
    manager = _manager(monkeypatch, level=20)
    monkeypatch.setattr(shops, "ShopScreen", FakeShopScreen)
    monkeypatch.setattr(manager, "buy_equipment", lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("should not buy")))

    FakeShopScreen.option_sequences = [[None], ["Back"], []]
    manager.buy_weapons()

    FakeShopScreen.option_sequences = [[]]
    monkeypatch.setattr(manager, "_has_available_items", lambda _item_list: False)
    manager.buy_armor()

    assert FakeShopScreen.instances[-1].set_calls == []


def test_buy_with_shop_screen_covers_cancel_insufficient_gold_decline_and_purchase(monkeypatch):
    manager = _manager(monkeypatch, gold=120)
    item = DummyItem(name="Potion", typ="Potion", subtyp="Potion", value=10)
    itemdict = {"Potions": [item]}
    messages = []
    manager.presenter.show_message = lambda message: messages.append(message)

    FakeShopScreen.item_sequences = [[
        ("Potion", item, 30, 0),
        ("Potion", item, 100, 0),
        ("Potion", item, 20, 0),
        ("Potion", item, 10, 0),
        None,
    ]]
    FakeQuantityPopup.responses = [0, 2, 1, 2]
    FakePopup.responses = [False, True, None]

    monkeypatch.setattr(shops, "ShopScreen", FakeShopScreen)
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.QuantityPopup", FakeQuantityPopup)
    monkeypatch.setattr(shops, "ConfirmationPopup", FakePopup)

    manager._buy_with_shop_screen(itemdict, "Potions")

    assert messages == ["Not enough gold! Need 200g"]
    assert manager.player_char.gold == 100
    assert manager.player_char.inventory_calls == [("Potion", 2, False)]
    assert FakeShopScreen.instances[0].update_calls == [(itemdict, "Buy"), (itemdict, "Buy")]
    assert any("Purchased 2x Potion!" in message for message, _buttons in FakePopup.messages)
    assert any(call.get("flush_events") for call in FakePopup.calls)


def test_format_item_info_and_item_availability_helpers(monkeypatch):
    manager = _manager(monkeypatch, level=12, in_town=True)
    current = DummyItem(name="Old Sword", typ="Weapon", subtyp="Sword")
    manager.player_char.equipment = {"Weapon": current, "Ring": DummyItem(name="None", typ="Accessory", subtyp="Ring")}
    manager.player_char.equip_diff = lambda _item, _slot, buy=False: "Attack  +5\nDefense  -2\nSpeed  0"

    info = manager._format_item_info(DummyItem(name="New Sword", typ="Weapon", subtyp="Sword", description="A very long description that should wrap neatly in the info panel for testing.", value=75, damage=12))
    assert "Type: Weapon" in info
    assert "Subtype: Sword" in info
    assert "Damage: 12" in info
    assert "Value: 75g" in info
    assert "=== Currently Equipped ===" in info
    assert "(Better)" in info
    assert "(Worse)" in info

    manager.player_char.equipment = {"Ring": DummyItem(name="None", typ="Accessory", subtyp="Ring")}
    ring_info = manager._format_item_info(DummyItem(name="Silver Band", typ="Accessory", subtyp="Ring", value=40))
    assert "(No Ring currently equipped)" in ring_info

    class AvailableItem:
        def __call__(self):
            return DummyItem(name="Available", rarity=0.9)

    class RestrictedByLevel:
        def __call__(self):
            return DummyItem(name="Late", rarity=0.9, restriction=[20])

    class RestrictedByClass:
        def __call__(self):
            return DummyItem(name="ClassLock", rarity=0.9, restriction=["Ninja"])

    class LowRarity:
        def __call__(self):
            return DummyItem(name="Rare", rarity=0.1)

    assert manager._has_available_items([AvailableItem()]) is True
    assert manager._has_available_items([RestrictedByLevel(), RestrictedByClass(), LowRarity()]) is False


def test_sell_items_covers_empty_inventory_unsellable_cancel_and_confirm(monkeypatch):
    manager = _manager(monkeypatch, gold=50)
    monkeypatch.setattr(shops, "ConfirmationPopup", FakePopup)
    monkeypatch.setattr(shops, "ShopScreen", FakeShopScreen)
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.QuantityPopup", FakeQuantityPopup)

    manager.sell_items()
    assert any("nothing to sell" in message.lower() for message, _buttons in FakePopup.messages)

    manager.player_char.inventory = {"Legendary": [DummyItem(name="Legendary", ultimate=True)]}
    manager.sell_items(background_image="dungeon.png")
    assert any("no items to sell" in message.lower() for message, _buttons in FakePopup.messages)

    sell_item = DummyItem(name="Herb", typ="Potion", subtyp="Potion", value=10)
    manager.player_char.inventory = {"Herb": [sell_item, sell_item]}
    FakeShopScreen.item_sequences = [[("Herb", sell_item, 5, 2), ("Herb", sell_item, 5, 2), None]]
    FakeQuantityPopup.responses = [0, 2]
    FakePopup.responses = [True, None]

    manager.sell_items(background_image="dungeon.png")

    assert manager.player_char.gold == 60
    assert manager.player_char.inventory_calls[-1] == ("Herb", 2, True)
    assert any("Sold 2x Herb for 10g!" in message for message, _buttons in FakePopup.messages)
    assert any(call.get("flush_events") for call in FakePopup.calls)


def test_secret_shop_branches_delegate_to_expected_helpers(monkeypatch):
    manager = _manager(monkeypatch, level=20)
    calls = []

    monkeypatch.setattr(shops, "ShopScreen", FakeShopScreen)
    monkeypatch.setattr(shops, "ConfirmationPopup", FakePopup)
    monkeypatch.setattr(manager, "_buy_secret_weapons", lambda screen: calls.append(("weapons", screen.shop_message)))
    monkeypatch.setattr(manager, "_buy_secret_offhand", lambda screen: calls.append(("offhand", screen.shop_message)))
    monkeypatch.setattr(manager, "_buy_secret_armor", lambda screen: calls.append(("armor", screen.shop_message)))
    monkeypatch.setattr(manager, "_buy_secret_accessories", lambda screen: calls.append(("accessories", screen.shop_message)))
    monkeypatch.setattr(manager, "_buy_secret_consumables", lambda screen: calls.append(("consumables", screen.shop_message)))
    monkeypatch.setattr(manager, "sell_items", lambda background_image="town.png": calls.append(("sell", background_image)))

    FakeShopScreen.option_sequences = [[
        "Buy",
        "Weapons",
        "Buy",
        "Shields & Tomes",
        "Buy",
        "Armor",
        "Buy",
        "Accessories",
        "Buy",
        "Potions & Scrolls",
        "Sell",
        "Leave",
    ]]

    manager.visit_secret_shop()

    assert calls == [
        ("weapons", "Secret Shop - Rare Goods for Sale"),
        ("offhand", "Secret Shop - Rare Goods for Sale"),
        ("armor", "Secret Shop - Rare Goods for Sale"),
        ("accessories", "Secret Shop - Rare Goods for Sale"),
        ("consumables", "Secret Shop - Rare Goods for Sale"),
        ("sell", "dungeon.png"),
    ]
    assert any("Come back anytime!" in message for message, _buttons in FakePopup.messages)
    assert any(call.get("flush_events") for call in FakePopup.calls)


def test_secret_shop_submenus_and_misc_helpers(monkeypatch):
    manager = _manager(monkeypatch, level=20)
    delegated = []
    monkeypatch.setattr(shops, "ShopScreen", FakeShopScreen)
    monkeypatch.setattr(manager, "buy_equipment", lambda item_list, category_name, background_image="town.png": delegated.append((category_name, background_image, item_list)))
    monkeypatch.setattr(manager, "buy_potions", lambda background_image="town.png": delegated.append(("Potions", background_image, None)))
    monkeypatch.setattr(manager, "buy_scrolls", lambda background_image="town.png": delegated.append(("Scrolls", background_image, None)))

    FakeShopScreen.option_sequences = [["2-Handed", "Battle Axe"], ["Tomes"], ["Heavy"], ["Pendants"], ["Stat Potions"]]
    manager._buy_secret_weapons(FakeShopScreen(_make_presenter(), manager.player_char, "msg"))
    manager._buy_secret_offhand(FakeShopScreen(_make_presenter(), manager.player_char, "msg"))
    manager._buy_secret_armor(FakeShopScreen(_make_presenter(), manager.player_char, "msg"))
    manager._buy_secret_accessories(FakeShopScreen(_make_presenter(), manager.player_char, "msg"))
    manager._buy_secret_consumables(FakeShopScreen(_make_presenter(), manager.player_char, "msg"))
    manager._buy_secret_stat_potions()
    manager._buy_secret_keys()

    assert ("2-Handed Battle Axe", "dungeon.png", shops.items_module.items_dict["Weapon"]["2-Handed"]["Battle Axe"]) in delegated
    assert ("Tome", "dungeon.png", shops.items_module.items_dict["OffHand"]["Tome"]) in delegated
    assert ("Heavy Armor", "dungeon.png", shops.items_module.items_dict["Armor"]["Heavy"]) in delegated
    assert ("Pendant", "dungeon.png", shops.items_module.items_dict["Accessory"]["Pendant"]) in delegated
    assert ("Stat Potions", "dungeon.png", shops.items_module.items_dict["Potion"]["Stat"]) in delegated
    assert ("Keys", "dungeon.png", shops.items_module.items_dict["Misc"]["Key"]) in delegated
