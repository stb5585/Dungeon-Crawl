#!/usr/bin/env python3
"""Focused coverage for reusable pygame popup menu helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pygame

from src.ui_pygame.gui import popup_menus


class RenderedText:
    def __init__(self, text):
        self.text = text
        self.width = max(8, len(text) * 8)
        self.height = 18

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_rect(self, **kwargs):
        rect = pygame.Rect(0, 0, self.width, self.height)
        for key, value in kwargs.items():
            setattr(rect, key, value)
        return rect


class RecordingFont:
    def __init__(self):
        self.render_calls = []

    def render(self, text, _antialias, _color):
        self.render_calls.append(text)
        return RenderedText(text)

    def size(self, text):
        return (max(8, len(text) * 8), 18)

    def get_height(self):
        return 18


class RecordingScreen:
    def __init__(self):
        self.blit_calls = []
        self.fill_calls = []
        self.size = (640, 480)

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))

    def fill(self, color):
        self.fill_calls.append(color)

    def copy(self):
        return "screen-copy"

    def get_size(self):
        return self.size


class DummyItem:
    def __init__(
        self,
        name,
        *,
        typ="Weapon",
        subtyp="Sword",
        description="Useful description text for testing.",
        value=25,
        weight=2,
        qty=None,
        unequip=False,
        passive=False,
        cost=None,
    ):
        self.name = name
        self.typ = typ
        self.subtyp = subtyp
        self.description = description
        self.value = value
        self.weight = weight
        self.qty = qty
        self.unequip = unequip
        self.passive = passive
        if cost is not None:
            self.cost = cost

    def use(self, _player_char):
        return f"Used {self.name}"


class DemoPopup(popup_menus.BasePopupMenu):
    def build_items(self, _player_char):
        self.items = [{"is_header": True, "text": "Header"}, "Alpha", "Beta", "Gamma"]

    def draw_details_extra(self, player_char, item, x, y):
        self.screen.blit(self.normal_font.render(f"Extra:{item}", True, self.WHITE), (x, y))

    def on_select(self, player_char, item):
        return ("selected", item)


def _make_presenter():
    return SimpleNamespace(
        screen=RecordingScreen(),
        width=640,
        height=480,
        title_font=RecordingFont(),
        large_font=RecordingFont(),
        normal_font=RecordingFont(),
        small_font=RecordingFont(),
        clock=SimpleNamespace(tick=lambda _fps: None),
        set_background_provider=lambda provider: None,
        show_message=lambda message, **kwargs: None,
    )


def _make_parent():
    calls = []
    return SimpleNamespace(draw_all=lambda player_char, do_flip=False: calls.append((player_char, do_flip)), calls=calls)


def _make_player():
    inventory = {
        "Weapons": [DummyItem("Bronze Sword"), DummyItem("Bronze Sword"), DummyItem("Apple", typ="Misc", subtyp="Health")],
        "Accessories": [DummyItem("Silver Ring", typ="Accessory", subtyp="Ring"), DummyItem("Sun Pendant", typ="Accessory", subtyp="Pendant")],
    }
    equipment = {
        "Weapon": DummyItem("Starter Blade"),
        "Armor": DummyItem("Traveler Coat", typ="Armor", subtyp="Light"),
        "OffHand": DummyItem("None", typ="OffHand", subtyp="Shield", unequip=True),
        "Ring": DummyItem("None", typ="Accessory", subtyp="Ring", unequip=True),
        "Pendant": DummyItem("None", typ="Accessory", subtyp="Pendant", unequip=True),
    }
    player = SimpleNamespace(
        inventory=inventory,
        equipment=equipment,
        quest_dict={},
        cls=SimpleNamespace(equip_check=lambda item, slot: True),
        level=SimpleNamespace(level=12),
        special_inventory={"Triangulus": [DummyItem("Triangulus", typ="Misc")]},
        spellbook={"Skills": {"Jump": None, "Totem": None}},
        equip_diff=lambda item, slot, buy=False: "Attack  +2\nDefense  -1",
    )
    return player


def _patch_visuals(monkeypatch):
    monkeypatch.setattr("src.ui_pygame.gui.popup_menus.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.popup_menus.pygame.draw.rect", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.popup_menus.pygame.Surface", lambda size, *_args: SimpleNamespace(fill=lambda *_a, **_k: None))


def test_base_popup_helpers_and_show_navigation(monkeypatch):
    _patch_visuals(monkeypatch)
    presenter = _make_presenter()
    parent = _make_parent()
    popup = DemoPopup(presenter, parent, title="Test")
    player = _make_player()

    assert popup._truncate_text("very long title", 20).endswith("...")
    popup.items = ["A", "B", "C", "D"]
    popup.selected_index = 3
    popup.scroll_offset = 0
    popup._ensure_visible()
    assert popup.scroll_offset >= 0

    popup.items = []
    popup._ensure_visible()
    assert popup.selected_index == 0

    popup.build_items(player)
    popup.draw_background("bg")
    popup.draw_popup(player)
    popup.draw_list()
    popup.draw_details(player)
    popup._capture_menu_surface(player)
    assert parent.calls

    events = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_DOWN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_PAGEDOWN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.popup_menus.pygame.event.get", lambda: next(events, []))
    result = popup.show(player)
    assert result[0] == "selected"


def test_inventory_popup_build_sort_cycle_and_item_actions(monkeypatch):
    _patch_visuals(monkeypatch)
    presenter = _make_presenter()
    parent = _make_parent()
    player = _make_player()
    popup = popup_menus.InventoryPopupMenu(presenter, parent)

    popup.build_items(player)
    assert popup.title.startswith("Inventory [Name]")
    assert popup.item_display_text(("Weapons", DummyItem("Potion", qty=3), 1)) == "Potion x3"
    assert popup._is_combat_usable(DummyItem("Potion", typ="Misc", subtyp="Health")) is True
    assert popup._is_combat_usable(DummyItem("Sanctuary Scroll", typ="Misc", subtyp="Scroll")) is False

    popup.handle_key_down(player, SimpleNamespace(key=pygame.K_s))
    assert popup.title.startswith("Inventory [Type]")

    shown = []
    presenter.show_message = lambda message: shown.append(message)
    no_equip_player = _make_player()
    no_equip_player.cls = SimpleNamespace(equip_check=lambda item, slot: False)
    popup._equip_item(no_equip_player, DummyItem("Forbidden"), "Weapons")
    assert shown == ["You cannot equip Forbidden."]

    player.equipment["Weapon"] = DummyItem("No Weapon", unequip=True)
    popup._equip_item(player, player.inventory["Weapons"][0], "Weapons")
    assert player.equipment["Weapon"].name == "Bronze Sword"

    class FakeConfirm:
        def __init__(self, *_args, **_kwargs):
            pass

        def show(self, **_kwargs):
            return True

    monkeypatch.setattr(popup_menus, "ConfirmationPopup", FakeConfirm)
    popup._use_item(player, player.inventory["Weapons"][0], "Weapons", background_surface="bg")
    assert "Weapons" in player.inventory
    popup._drop_item(player, player.inventory["Weapons"][0], "Weapons", background_surface="bg")


def test_inventory_popup_on_select_uses_nested_selection_popup(monkeypatch):
    _patch_visuals(monkeypatch)
    presenter = _make_presenter()
    parent = _make_parent()
    player = _make_player()
    popup = popup_menus.InventoryPopupMenu(presenter, parent)
    popup.build_items(player)

    actions = iter([("selection", "Equip"), ("selection", "Use"), ("selection", "Drop"), ("selection", "Cancel")])

    class FakeSelectionPopup:
        def __init__(self, *_args, **_kwargs):
            self.draw_background = lambda surf: None

        def show(self, _player_char):
            return next(actions)

    monkeypatch.setattr(popup_menus, "SelectionPopup", FakeSelectionPopup)
    monkeypatch.setattr(popup, "_equip_item", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(popup, "_use_item", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(popup, "_drop_item", lambda *_args, **_kwargs: None)
    popup.on_select(player, popup.items[0])


def test_equipment_popup_build_details_and_selection_flows(monkeypatch):
    _patch_visuals(monkeypatch)
    presenter = _make_presenter()
    parent = _make_parent()
    player = _make_player()
    popup = popup_menus.EquipmentPopupMenu(presenter, parent)

    popup.build_items(player)
    assert popup.item_display_text(("Weapon", DummyItem("Very Long Equipment Name That Truncates"))) .startswith("Weapon:")
    popup.draw_details(player)

    equippable = popup._get_equippable_items_for_slot(player, "Ring")
    assert any(item.name == "Silver Ring" for item in equippable)

    new_ring = DummyItem("Ruby Ring", typ="Accessory", subtyp="Ring")
    player.inventory.setdefault("Ruby Ring", []).append(new_ring)
    popup._equip_from_inventory(player, "Ring", new_ring)
    assert player.equipment["Ring"].name == "Ruby Ring"

    popup._unequip_item(player, "Ring", player.equipment["Ring"])
    assert player.equipment["Ring"].name == "No Ring"

    class FakeEquipPopup:
        def __init__(self, *_args, **_kwargs):
            self.draw_background = lambda surf: None

        def show(self, _player_char):
            return ("selection", "Cancel")

    monkeypatch.setattr(popup_menus, "EquipmentSelectionPopup", FakeEquipPopup)
    assert popup.on_select(player, popup.items[0]) is None


def test_quest_popup_build_and_details_cover_main_side_and_bounty(monkeypatch):
    _patch_visuals(monkeypatch)
    presenter = _make_presenter()
    parent = _make_parent()
    player = _make_player()
    player.quest_dict = {
        "Main": {
            "Main Quest": {"Type": "Defeat", "What": "Dragon", "Completed": False, "Turned In": False, "Experience": 100},
            "Turned Quest": {"Type": "Locate", "What": "Tower", "Completed": True, "Turned In": True},
        },
        "Side": {
            "Relic Hunt": {"Type": "Collect", "What": "Relics", "Total": 6, "Completed": True, "Turned In": False, "Reward": ["Gold"], "Reward Number": 50},
        },
        "Bounty": {
            "Goblin Hunt": [{"enemy": SimpleNamespace(name="Goblin"), "num": 3, "gold": 40, "exp": 20}, 1, False],
        },
    }
    popup = popup_menus.QuestPopupMenu(presenter, parent)
    popup.build_items(player)
    assert any(isinstance(item, dict) and item.get("is_header") for item in popup.items)
    popup.draw_details(player)
    assert popup.on_select(player, popup.items[0]) is None


def test_simple_list_jumpmods_totems_and_selection_popups(monkeypatch):
    _patch_visuals(monkeypatch)
    presenter = _make_presenter()
    parent = _make_parent()
    player = _make_player()

    simple = popup_menus.SimpleListPopupMenu(presenter, parent, "Simple", lambda _player: ["--- Header ---", DummyItem("Lore Entry", description="Story text"), "Plain"])
    simple.build_items(player)
    simple.draw_details(player)

    messages = []
    presenter.show_message = lambda message, **kwargs: messages.append(message)
    monkeypatch.setattr(popup_menus.map_tiles, "reveal_chalice_map_on_inspect", lambda _player, _value: None)
    monkeypatch.setattr(popup_menus.map_tiles, "get_chalice_progress", lambda _player: {"Revealed": True, "Adventurer": False})
    chalice_item = {"is_header": False, "text": "Chalice Map", "value": SimpleNamespace(name="Chalice Map")}
    assert simple.on_select(player, chalice_item) is None

    jump_skill = SimpleNamespace(
        modifications={"Crit": True, "Quake": False},
        unlock_requirements={"Crit": {"type": "lancer_level", "requirement": 5}},
        get_active_count=lambda: 1,
        get_max_active_modifications=lambda _player: 2,
        get_unlocked_modifications=lambda: ["Crit", "Quake"],
        set_modification=lambda name, value, _player: (True, ""),
    )
    player.spellbook["Skills"]["Jump"] = jump_skill
    jump_popup = popup_menus.JumpModsPopupMenu(presenter, parent)
    jump_popup.build_items(player)
    jump_popup.draw_details(player)
    assert jump_popup.on_select(player, jump_popup.items[1]) is None

    totem_skill = SimpleNamespace(
        active_aspect="Bear",
        aspects={"Bear": {"cost": 4, "description": "Tank stance"}},
        get_unlocked_aspects=lambda _player: ["Bear"],
        set_active_aspect=lambda aspect: (True, ""),
    )
    player.spellbook["Skills"]["Totem"] = totem_skill
    totem_popup = popup_menus.TotemAspectsPopupMenu(presenter, parent)
    totem_popup.build_items(player)
    totem_popup.draw_details(player)
    assert totem_popup.on_select(player, totem_popup.items[1]) is None

    selection = popup_menus.SelectionPopup(presenter, parent, title="Pick", header_message="Choose wisely", options=["A", "B"])
    selection.build_items(player)
    selection.draw_details(player)
    assert selection.on_select(player, "A") == ("selection", "A")

    equip_sel = popup_menus.EquipmentSelectionPopup(
        presenter,
        parent,
        title="Equip",
        header_message="Pick gear",
        options=["Unequip", "Cancel"],
        slot="Weapon",
        current_item=DummyItem("Sword"),
        player_char=player,
    )
    equip_sel.build_items(player)
    equip_sel.draw_details(player)


def test_second_popup_menus_pass_covers_remaining_helper_branches(monkeypatch):
    _patch_visuals(monkeypatch)
    presenter = _make_presenter()
    parent = _make_parent()
    player = _make_player()

    # Base popup hook defaults
    base = popup_menus.BasePopupMenu(presenter, parent, title="Base")
    assert base.help_footer().startswith("Arrows:")
    assert base.handle_key_down(player, SimpleNamespace(key=pygame.K_a)) is False
    assert base.on_select(player, "item") == ("selected", "item")

    # Inventory sorting and non-success tuple handling
    inv = popup_menus.InventoryPopupMenu(presenter, parent)
    inv.sort_mode_idx = inv.sort_modes.index("Quantity")
    inv.build_items(player)
    assert inv.items[0][2] >= inv.items[-1][2]
    inv.sort_mode_idx = inv.sort_modes.index("Combat")
    inv.build_items(player)
    assert inv.items[0][1].name == "Apple"

    class FalseConfirm:
        def __init__(self, *_args, **_kwargs):
            pass

        def show(self, **_kwargs):
            return False

    monkeypatch.setattr(popup_menus, "ConfirmationPopup", FalseConfirm)
    before = list(player.inventory["Weapons"])
    inv._drop_item(player, player.inventory["Weapons"][0], "Weapons", background_surface="bg")
    assert player.inventory["Weapons"] == before

    # Equipment popup empty and select-unequip path
    eq = popup_menus.EquipmentPopupMenu(presenter, parent)
    empty_player = _make_player()
    empty_player.equipment["Weapon"] = None
    eq.build_items(empty_player)
    eq.draw_details(empty_player)

    actions = iter([("selection", "Unequip")])

    class UnequipPopup:
        def __init__(self, *_args, **_kwargs):
            self.draw_background = lambda surf: None

        def show(self, _player_char):
            return next(actions)

    real_equipment_selection_popup = popup_menus.EquipmentSelectionPopup
    monkeypatch.setattr(popup_menus, "EquipmentSelectionPopup", UnequipPopup)
    monkeypatch.setattr(eq, "_unequip_item", lambda *_args, **_kwargs: setattr(eq, "_unequipped", True))
    eq.build_items(player)
    eq.on_select(player, eq.items[0])
    assert getattr(eq, "_unequipped", False) is True

    # Quest details with callable rewards and no-quest fallback
    quest_popup = popup_menus.QuestPopupMenu(presenter, parent)
    player.quest_dict = {}
    quest_popup.build_items(player)
    quest_popup.draw_details(player)

    player.quest_dict = {
        "Side": {
            "Collector": {
                "Type": "Collect",
                "What": lambda: DummyItem("Moon Pearl", typ="Misc"),
                "Total": 2,
                "Completed": False,
                "Turned In": False,
                "Reward": [lambda: DummyItem("Shard", typ="Misc")],
            }
        }
    }
    player.special_inventory["Moon Pearl"] = [DummyItem("Moon Pearl", typ="Misc")]
    quest_popup.build_items(player)
    quest_popup.draw_details(player)

    # Simple list fallback/alternate chalice messages
    simple = popup_menus.SimpleListPopupMenu(presenter, parent, "Simple", lambda _player: [DummyItem("Passive Aura", description="", passive=True, cost=4)])
    simple.build_items(player)
    simple.draw_details(player)

    messages = []
    presenter.show_message = lambda message, **kwargs: messages.append(message)
    monkeypatch.setattr(popup_menus.map_tiles, "reveal_chalice_map_on_inspect", lambda _player, _value: None)
    monkeypatch.setattr(popup_menus.map_tiles, "get_chalice_progress", lambda _player: {"Revealed": False, "Adventurer": True})
    simple.on_select(player, {"is_header": False, "text": "Chalice Map", "value": SimpleNamespace(name="Chalice Map")})
    monkeypatch.setattr(popup_menus.map_tiles, "get_chalice_progress", lambda _player: {"Revealed": False, "Adventurer": False})
    simple.on_select(player, {"is_header": False, "text": "Chalice Map", "value": SimpleNamespace(name="Chalice Map")})
    assert len(messages) == 2

    # Jump/Totem not learned or unsuccessful selection
    player.spellbook["Skills"] = {}
    jump_popup = popup_menus.JumpModsPopupMenu(presenter, parent)
    jump_popup.build_items(player)
    jump_popup.draw_details(player)
    assert jump_popup.on_select(player, jump_popup.items[0]) is None

    totem_popup = popup_menus.TotemAspectsPopupMenu(presenter, parent)
    totem_popup.build_items(player)
    totem_popup.draw_details(player)
    assert totem_popup.on_select(player, totem_popup.items[0]) is None

    fail_jump = SimpleNamespace(
        modifications={"Crit": False},
        get_unlocked_modifications=lambda: ["Crit"],
        set_modification=lambda name, value, _player: (False, "blocked"),
    )
    player.spellbook["Skills"]["Jump"] = fail_jump
    jump_popup.build_items(player)
    assert jump_popup.on_select(player, jump_popup.items[1]) is None

    fail_totem = SimpleNamespace(
        active_aspect="",
        aspects={"Wolf": {"description": "Speed up"}},
        get_unlocked_aspects=lambda _player: ["Wolf"],
        set_active_aspect=lambda aspect: (False, "blocked"),
    )
    player.spellbook["Skills"]["Totem"] = fail_totem
    totem_popup.build_items(player)
    assert totem_popup.on_select(player, totem_popup.items[1]) is None

    # Selection popup header wrapping and equipment selection diff branches
    selection = popup_menus.SelectionPopup(presenter, parent, title="Pick", header_message="A very long header message that should wrap across multiple lines in the details panel.", options=["A"])
    selection.build_items(player)
    selection.draw_details(player)

    player.inventory["Weapons"] = [DummyItem("Steel Sword")]
    monkeypatch.setattr(popup_menus, "EquipmentSelectionPopup", real_equipment_selection_popup)
    equip_sel = popup_menus.EquipmentSelectionPopup(
        presenter,
        parent,
        title="Equip",
        header_message="Choose replacement",
        options=["Steel Sword", "Unequip", "Cancel"],
        slot="Weapon",
        current_item=DummyItem("Starter Blade"),
        player_char=player,
    )
    equip_sel.build_items(player)
    equip_sel.draw_details(player)
    equip_sel.selected_index = 1
    equip_sel.draw_details(player)
    equip_sel.selected_index = 2
    equip_sel.draw_details(player)
