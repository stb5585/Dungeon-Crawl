#!/usr/bin/env python3
"""Focused coverage for shared curses menu helpers."""

from __future__ import annotations

import io
from types import SimpleNamespace

from src.ui_curses import menus as curses_menus


class FakeWindow:
    def __init__(self, height=24, width=80, y=0, x=0):
        self.height = height
        self.width = width
        self.y = y
        self.x = x
        self.calls = []

    def erase(self):
        self.calls.append(("erase",))

    def refresh(self):
        self.calls.append(("refresh",))

    def box(self):
        self.calls.append(("box",))

    def attron(self, attr):
        self.calls.append(("attron", attr))

    def attroff(self, attr):
        self.calls.append(("attroff", attr))

    def addstr(self, *args):
        self.calls.append(("addstr", args))

    def addch(self, *args):
        self.calls.append(("addch", args))

    def delch(self, *args):
        self.calls.append(("delch", args))

    def getmaxyx(self):
        return (self.height, self.width)


class FakeStdScr(FakeWindow):
    def __init__(self, keys=None, height=24, width=80):
        super().__init__(height=height, width=width)
        self.keys = list(keys or [])

    def getch(self):
        if self.keys:
            return self.keys.pop(0)
        return 10


def _fake_newwin_factory(created):
    def fake_newwin(height, width, y, x):
        win = FakeWindow(height, width, y, x)
        created.append(win)
        return win

    return fake_newwin


def _make_game(keys=None, debug_mode=False, height=24, width=80):
    return SimpleNamespace(
        stdscr=FakeStdScr(keys=keys, height=height, width=width),
        debug_mode=debug_mode,
        player_char=SimpleNamespace(
            spellbook={"Spells": {}, "Skills": {}},
            inventory={},
            special_inventory={},
            quest_dict={"Bounty": {}, "Main": {}, "Side": {}},
            world_dict={},
            stats=SimpleNamespace(strength=1, intel=2, wisdom=3, con=4, charisma=5, dex=6),
            health=SimpleNamespace(current=10, max=12),
            mana=SimpleNamespace(current=5, max=8),
            combat=SimpleNamespace(attack=7, defense=8, magic=9, magic_def=10),
            location_x=0,
            location_y=0,
            location_z=1,
            name="Ada",
        ),
        races_dict={},
        classes_dict={},
    )


def test_player_input_ascii_art_and_save_popup(monkeypatch):
    created = []
    game = _make_game(keys=[ord("A"), ord("d"), ord("a"), 127, ord("a"), 10], debug_mode=True)
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory(created))
    cursor_calls = []
    monkeypatch.setattr(curses_menus.curses, "curs_set", lambda value: cursor_calls.append(value))

    assert curses_menus.player_input(game, "Name?") == "Ada"
    assert cursor_calls == [1, 0]

    monkeypatch.setattr("builtins.open", lambda path, mode="r": io.StringIO("one\n\n two\n"))
    assert curses_menus.ascii_art("hero.txt") == ["one\n", " two\n"]

    sleep_calls = []
    curses_menus.save_file_popup(game, load=False)
    assert created[-1].calls
    monkeypatch.setattr(curses_menus.time, "sleep", lambda secs: sleep_calls.append(secs))
    game.debug_mode = False
    curses_menus.save_file_popup(game, load=True)
    assert sleep_calls


def test_main_menu_navigates_and_triggers_debug_level_up(monkeypatch):
    created = []
    game = _make_game(keys=[ord("l"), curses_menus.curses.KEY_DOWN, 10], debug_mode=True)
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory(created))
    debug_calls = []
    game.debug_level_up = lambda: debug_calls.append("level")

    menu = curses_menus.MainMenu(game)
    menu.update_options(["New Game", "Exit"])

    assert menu.navigate_menu() == 1
    assert debug_calls == ["level"]


def test_new_game_menu_update_and_navigation(monkeypatch):
    created = []
    game = _make_game(keys=[10, 10])
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory(created))

    race = SimpleNamespace(
        name="Elf",
        description="Wise and swift",
        strength=1,
        intel=2,
        wisdom=3,
        con=4,
        charisma=5,
        dex=6,
        base_attack=7,
        base_defense=8,
        base_magic=9,
        base_magic_def=10,
        resistance={key: 0 for key in ["Fire", "Ice", "Electric", "Water", "Earth", "Wind", "Shadow", "Holy", "Poison", "Physical"]},
        cls_res={"Base": ["Mage"], "First": ["Wizard"]},
        virtue=SimpleNamespace(name="Mercy", description="Kind"),
        sin=SimpleNamespace(name="Pride", description="Bold"),
    )
    cls = SimpleNamespace(
        name="Mage",
        description="Arcane student",
        str_plus=1,
        int_plus=2,
        wis_plus=3,
        con_plus=4,
        cha_plus=5,
        dex_plus=6,
        att_plus=1,
        def_plus=2,
        magic_plus=3,
        magic_def_plus=4,
        restrictions={"Armor": ["Heavy"]},
    )
    game.races_dict = {"Elf": lambda: race}
    game.classes_dict = {"Mage": {"class": lambda: cls, "pro": {"Wizard": {}}}}

    menu = curses_menus.NewGameMenu(game)
    menu.update_options()
    assert menu.options_list == ["Elf", "Go Back"]
    chosen_race = menu.navigate_menu()
    assert chosen_race.name == "Elf"

    menu.page = 2
    menu.race = race
    menu.current_option = 0
    menu.update_options()
    assert menu.options_list == ["Mage", "Go Back"]
    chosen_cls = menu.navigate_menu()
    assert chosen_cls.name == "Mage"


def test_load_game_menu_config_and_navigation(monkeypatch):
    created = []
    game = _make_game(keys=[curses_menus.curses.KEY_DOWN, 10])
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory(created))
    player_obj = SimpleNamespace(
        name="Ada",
        level=SimpleNamespace(level=7),
        race=SimpleNamespace(name="Elf"),
        cls=SimpleNamespace(name="Mage"),
        health=SimpleNamespace(current=8, max=12),
        mana=SimpleNamespace(current=5, max=9),
        stats=SimpleNamespace(strength=1, intel=2, wisdom=3, con=4, charisma=5, dex=6),
    )
    monkeypatch.setattr(curses_menus.SaveManager, "load_player", staticmethod(lambda _name: player_obj))

    menu = curses_menus.LoadGameMenu(game, ["Ada", "Go Back"])
    assert "Level 7 Elf Mage" in menu.config_desc_str(player_obj)
    assert menu.config_desc_str(None) == "Corrupted save"
    assert menu.navigate_menu() == 1


def test_town_and_location_menu_navigation(monkeypatch):
    created = []
    game = _make_game(keys=[curses_menus.curses.KEY_RIGHT, 10])
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory(created))
    town_menu = curses_menus.TownMenu(game, ["Barracks", "Tavern", "Church"])
    assert town_menu.navigate_menu() == 1

    game2 = _make_game(keys=[curses_menus.curses.KEY_DOWN, curses_menus.curses.KEY_DOWN, 10], height=18, width=80)
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory([]))
    loc_menu = curses_menus.LocationMenu(game2, "Where?", [f"Option {i}" for i in range(8)], options_message="Choose")
    assert loc_menu.navigate_menu() == 2
    loc_menu.update_options(["A", "B"], reset_current=False)
    assert loc_menu.current_option == 1


def test_popup_selection_shop_and_confirm_popups(monkeypatch):
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory([]))

    game = _make_game(keys=[curses_menus.curses.KEY_DOWN, 10])
    popup = curses_menus.PopupMenu(game, "Header", box_height=6, box_width=20)
    popup.options_list = ["Yes", "No"]
    assert popup.navigate_popup() == 1

    game = _make_game(keys=[ord("i"), 10])
    inspected = []
    monkeypatch.setattr(curses_menus, "TextBox", lambda game: SimpleNamespace(print_text_in_rectangle=lambda text: inspected.append(text), clear_rectangle=lambda: inspected.append("cleared")))
    select = curses_menus.SelectionPopupMenu(game, "Pick", ["Sword"], rewards=[lambda: "Blade"], confirm=False)
    assert select.navigate_popup() == 0
    assert inspected[0] == "Blade"

    game = _make_game(keys=[curses_menus.curses.KEY_LEFT, curses_menus.curses.KEY_UP, 10])
    shop = curses_menus.ShopPopup(game, "How many?", max="09", box_height=7)
    assert shop.navigate_popup() == 19

    game = _make_game(keys=[curses_menus.curses.KEY_DOWN, ord("\n")])
    confirm = curses_menus.ConfirmPopupMenu(game, "Proceed?")
    assert confirm.navigate_popup() is False


def test_combat_popup_and_helpers(monkeypatch):
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory([]))
    game = _make_game(keys=[10])
    game.player_char.mana.current = 5
    game.player_char.physical_effects = {"Disarm": SimpleNamespace(active=False)}
    game.player_char.magic_effects = {"Mana Shield": SimpleNamespace(active=False)}
    game.player_char.equipment = {
        "OffHand": SimpleNamespace(subtyp="Shield"),
        "Weapon": SimpleNamespace(handed=2),
    }
    game.player_char.spellbook = {
        "Spells": {
            "Fire": SimpleNamespace(subtyp="Attack", cost=3),
            "Jump": SimpleNamespace(subtyp="Movement", cost=1),
        },
        "Skills": {
            "Slash": SimpleNamespace(cost=2, passive=False, name="Slash", weapon=False),
            "Smoke Screen": SimpleNamespace(cost=1, passive=False, name="Smoke Screen", weapon=False),
            "Lockpick": SimpleNamespace(cost=0, passive=False, name="Lockpick", weapon=False),
        },
    }
    tile = SimpleNamespace(enemy=SimpleNamespace(incapacitated=lambda: True))

    combat_popup = curses_menus.CombatPopupMenu(game, "Combat")
    combat_popup.update_options("Cast Spell")
    assert combat_popup.options_list == ["Fire  3", "Go Back"]
    combat_popup.update_options("Use Skill", tile=tile)
    assert "Slash  2" in combat_popup.options_list

    game.player_char.world_dict = {(0, 0, 1): SimpleNamespace(enemy=None, intro_text=lambda game: "Room")}
    game.player_char.minimap = lambda: "Map"
    game.player_char.state = "town"
    combat_menu = curses_menus.CombatMenu(game)
    assert combat_menu._effect_label("Mana Shield") == "MSH"

    character = SimpleNamespace(
        status_effects={"Defend": SimpleNamespace(active=True)},
        physical_effects={"Stun": SimpleNamespace(active=True)},
        stat_effects={"Attack": SimpleNamespace(active=True, extra=2)},
        magic_effects={"Reflect": SimpleNamespace(active=True)},
        class_effects={"Jump": SimpleNamespace(active=True)},
    )
    icons = combat_menu._collect_status_icons(character)
    assert ("DEF", True) in icons
    assert ("STN", False) in icons
    assert ("ATK", True) in icons
    assert ("RFL", True) in icons
    assert all(label != "JMP" for label, _positive in icons)


def test_quest_list_and_text_box_helpers(monkeypatch):
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory([]))
    shown = []
    monkeypatch.setattr(curses_menus, "TextBox", lambda game: SimpleNamespace(print_text_in_rectangle=lambda text: shown.append(text), clear_rectangle=lambda: shown.append("cleared")))
    game = _make_game(keys=[ord("\n"), curses_menus.curses.KEY_DOWN, ord("\n"), curses_menus.curses.KEY_DOWN, ord("\n")])
    game.player_char.quest_dict = {
        "Bounty": {"Rat": [{"num": 3}, 1, False]},
        "Main": {"Heroic": {"Completed": False, "Turned In": False, "Type": "Collect", "What": "Relics", "Who": "Sergeant", "Total": 6}},
        "Side": {"Done": {"Completed": True, "Turned In": False, "Type": "Defeat", "What": "Ogre", "Who": "Barkeep"}},
    }
    game.player_char.special_inventory = {"Triangulus": object(), "Quadrata": object()}

    popup = curses_menus.QuestListPopupMenu(game, "Quests")
    popup.update_options()
    assert "Completed Quests" in popup.options_list
    popup.current_option = 0
    quest_text = popup.quest_str_config(game.player_char.quest_dict["Main"]["Heroic"])
    assert "Collected: 2/6" in quest_text
    popup.inspect_quests()
    popup.show_turned_in()
    assert shown

    real_textbox = curses_menus.TextBox(_make_game(keys=[10]))
    real_textbox.print_text_in_rectangle("Hello there")
    real_textbox.clear_rectangle()


def test_inventory_popup_sorting_paging_and_inspection(monkeypatch):
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory([]))
    messages = []
    monkeypatch.setattr(
        curses_menus,
        "TextBox",
        lambda game: SimpleNamespace(
            print_text_in_rectangle=lambda text: messages.append(text),
            clear_rectangle=lambda: messages.append("cleared"),
        ),
    )
    reveal_calls = []
    monkeypatch.setattr(curses_menus.map_tiles, "reveal_chalice_map_on_inspect", lambda player, item: reveal_calls.append(item.name))
    monkeypatch.setattr(curses_menus.map_tiles, "chalice_map_preview_text", lambda player: "Revealed map path")

    game = _make_game(keys=[10])
    potion = SimpleNamespace(name="Potion", subtyp="Health")
    scroll = SimpleNamespace(name="Warp Scroll", subtyp="Scroll")
    sanctuary = SimpleNamespace(name="Sanctuary Scroll", subtyp="Scroll")
    chalice = SimpleNamespace(name="Chalice Map")
    game.player_char.inventory = {
        "Potion": [potion, potion],
        "Warp Scroll": [scroll],
        "Sanctuary Scroll": [sanctuary],
        "Bomb": [SimpleNamespace(name="Bomb", subtyp="Throwable")],
    }
    game.player_char.special_inventory = {"Chalice Map": [chalice]}

    popup = curses_menus.InventoryPopupMenu(game, "Inventory")
    assert popup._is_combat_usable(potion) is True
    assert popup._is_combat_usable(scroll) is True
    assert popup._is_combat_usable(sanctuary) is False
    popup.update_itemlist()
    popup.cycle_sort_mode()
    popup.cycle_sort_mode()
    assert popup.sort_modes[popup.sort_mode_idx] == "Quantity"
    keys = popup._sorted_inventory_keys(game.player_char.inventory)
    assert keys[0] == "Potion"
    chosen = popup.navigate_popup()
    assert chosen.name in game.player_char.inventory

    popup.header_message = ["Key Items"]
    popup.page = 0
    popup.current_option = 0
    popup.inspect_item(chalice)
    assert reveal_calls[-1] == "Chalice Map"
    assert "Revealed map path" in messages


def test_inventory_popup_empty_and_next_page(monkeypatch):
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory([]))
    messages = []
    monkeypatch.setattr(
        curses_menus,
        "TextBox",
        lambda game: SimpleNamespace(
            print_text_in_rectangle=lambda text: messages.append(text),
            clear_rectangle=lambda: messages.append("cleared"),
        ),
    )
    game = _make_game(keys=[10])
    popup = curses_menus.InventoryPopupMenu(game, "Inventory")
    popup.update_itemlist = lambda: setattr(popup, "options_list", [])
    popup.navigate_popup()
    assert messages[0] == "You do not have any items in your inventory."

    game = _make_game(keys=[curses_menus.curses.KEY_DOWN] * 14 + [10, 10])
    game.player_char.inventory = {
        f"Item {i:02d}": [SimpleNamespace(name=f"Item {i:02d}", subtyp="Misc")]
        for i in range(15)
    }
    popup = curses_menus.InventoryPopupMenu(game, "Inventory")
    popup.update_itemlist()
    assert popup.options_list[-2][0] == "Next Page"
    assert popup.navigate_popup().name == "Item 14"


def test_equip_popup_update_and_diffbox(monkeypatch):
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory([]))
    messages = []
    monkeypatch.setattr(
        curses_menus,
        "TextBox",
        lambda game: SimpleNamespace(
            print_text_in_rectangle=lambda text: messages.append(text),
            clear_rectangle=lambda: messages.append("cleared"),
        ),
    )
    game = _make_game()
    sword = SimpleNamespace(name="Iron Sword")
    shield = SimpleNamespace(name="Buckler")
    equipped_shield = SimpleNamespace(name="Old Shield")
    game.player_char.inventory = {"Iron Sword": [sword], "Buckler": [shield]}
    game.player_char.equipment = {
        "Weapon": SimpleNamespace(name="Club"),
        "OffHand": equipped_shield,
        "Armor": SimpleNamespace(name="Rags"),
        "Ring": SimpleNamespace(name="Band"),
        "Pendant": SimpleNamespace(name="Charm"),
    }
    game.player_char.cls = SimpleNamespace(equip_check=lambda item, typ: item.name != "Buckler" or typ == "OffHand")
    game.player_char.unequip = lambda typ=None: SimpleNamespace(name="Unequipped")
    equipped = []
    game.player_char.equip_diff = lambda item, equip_type: "Attack  +3\nDefense  +1"
    game.player_char.equip = lambda equip_type, item: equipped.append((equip_type, item.name))

    popup = curses_menus.EquipPopupMenu(game, "Equip", box_height=10)
    popup.update_options()
    assert popup.options_list[0] == "Weapon"
    popup.current_option = 0
    popup.page = 2
    popup.update_options()
    assert "Iron Sword" in popup.options_list
    assert "Unequip" in popup.options_list

    monkeypatch.setattr(curses_menus, "ConfirmPopupMenu", lambda game, text, box_height=7: SimpleNamespace(navigate_popup=lambda: True))
    popup.options_list = ["Iron Sword", "Go Back"]
    popup.current_option = 0
    popup.equip_type = "Weapon"
    assert popup.diffbox() is True
    assert equipped == [("Weapon", "Iron Sword")]
    assert "Attack" in messages[0]


def test_abilities_popup_update_and_inspect_use(monkeypatch):
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory([]))
    messages = []
    monkeypatch.setattr(
        curses_menus,
        "TextBox",
        lambda game: SimpleNamespace(
            print_text_in_rectangle=lambda text: messages.append(text),
            clear_rectangle=lambda: messages.append("cleared"),
        ),
    )
    monkeypatch.setattr(curses_menus, "ConfirmPopupMenu", lambda game, text, box_height=6: SimpleNamespace(navigate_popup=lambda: True))

    spell = SimpleNamespace(name="Blink", cost=2, cast_out=lambda game: "Blink cast!", __str__=lambda self: "Spell details")
    skill = SimpleNamespace(name="Meditate", cost=1, use_out=lambda game: "Skill used!", __str__=lambda self: "Skill details")
    game = _make_game(keys=[10, 10])
    game.player_char.mana.current = 5
    game.player_char.spellbook = {"Spells": {"Blink": spell}, "Skills": {"Meditate": skill}}
    game.player_char.usable_abilities = lambda ability_type: ["Blink"] if ability_type == "Spells" else ["Meditate"]
    game.player_char.in_town = lambda: False

    popup = curses_menus.AbilitiesPopupMenu(game, "Abilities")
    popup.page = 2
    popup.options_list = ["Spells", "Skills", "Go Back"]
    popup.current_option = 0
    popup.update_options()
    assert popup.options_list == ["Blink", "Go Back"]
    popup.inspect_ability()
    assert "Blink cast!" in messages

    game2 = _make_game()
    game2.player_char.spellbook = {"Spells": {}, "Skills": {}}
    game2.player_char.usable_abilities = lambda ability_type: []
    popup2 = curses_menus.AbilitiesPopupMenu(game2, "Abilities")
    popup2.page = 2
    popup2.options_list = ["Spells", "Skills", "Go Back"]
    popup2.current_option = 0
    popup2.update_options()
    assert "You do not have any abilities." in messages


def test_jump_and_totem_popup_menus(monkeypatch):
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory([]))
    messages = []
    monkeypatch.setattr(
        curses_menus,
        "TextBox",
        lambda game: SimpleNamespace(
            print_text_in_rectangle=lambda text: messages.append(text),
            clear_rectangle=lambda: messages.append("cleared"),
        ),
    )

    jump_skill = SimpleNamespace(
        name="Jump",
        modifications={"Crit": False, "Recover": False},
        get_unlocked_modifications=lambda: ["Crit", "Recover"],
        get_active_count=lambda: 0,
        get_max_active_modifications=lambda player: 2,
        set_modification=lambda name, value, player: (True, None),
    )
    game = _make_game(
        keys=[
            curses_menus.curses.KEY_DOWN,
            curses_menus.curses.KEY_DOWN,
            10,
            curses_menus.curses.KEY_DOWN,
            curses_menus.curses.KEY_DOWN,
            10,
        ]
    )
    game.player_char.spellbook = {"Skills": {"Jump": jump_skill}}
    popup = curses_menus.JumpModsPopupMenu(game, "Jump Mods")
    popup.navigate_popup()
    assert any("Increases critical factor" in str(message) or "Regain a small amount" in str(message) for message in messages)

    messages.clear()
    totem_skill = SimpleNamespace(
        name="Totem",
        active_aspect="Bear",
        get_unlocked_aspects=lambda player: ["Bear", "Eagle"],
        set_active_aspect=lambda aspect: (True, None),
        aspects={"Eagle": {"description": "Swift strikes."}, "Bear": {"description": "Sturdy guard."}},
    )
    game = _make_game(keys=[curses_menus.curses.KEY_DOWN, curses_menus.curses.KEY_DOWN, curses_menus.curses.KEY_DOWN, 10])
    game.player_char.spellbook = {"Skills": {"Totem": totem_skill}}
    popup = curses_menus.TotemAspectsPopupMenu(game, "Totem")
    assert popup.navigate_popup() == "Eagle"
    assert any("Swift strikes." in str(message) for message in messages)


def test_dungeon_menu_draws_map_room_and_controls(monkeypatch):
    created = []
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory(created))
    room = SimpleNamespace(
        enemy=SimpleNamespace(name="Goblin"),
        intro_text=lambda game: "A damp room.\nWith bones.",
    )
    game = _make_game()
    game.player_char.world_dict = {(0, 0, 1): room}
    game.player_char.minimap = lambda: "###\n#@#"
    game.player_char.state = "fight"
    game.player_char.__str__ = lambda self=game.player_char: "Ada the Brave"

    menu = curses_menus.DungeonMenu(game)
    menu.draw_all()
    menu.refresh_all()

    assert any("Dungeon Level 1" in str(call[1][2]) for call in created[0].calls if call[0] == "addstr" and len(call[1]) >= 3)
    assert any("Ada is attacked by a Goblin." in str(call[1][2]) for call in created[0].calls if call[0] == "addstr" and len(call[1]) >= 3)
    assert any("A damp room." in str(call[1][2]) for call in created[1].calls if call[0] == "addstr" and len(call[1]) >= 3)
    assert any("Move Forward (w)" in str(call[1][2]) for call in created[2].calls if call[0] == "addstr" and len(call[1]) >= 3)


def test_shop_menu_configures_items_mods_and_navigation(monkeypatch):
    created = []
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory(created))
    game = _make_game(keys=[10])
    game.player_char.gold = 123
    game.player_char.in_town = lambda: True
    game.player_char.player_level = lambda: 10
    game.player_char.shop_price_scale = lambda: 1.5
    game.player_char.inventory = {"Bronze Sword": [SimpleNamespace(name="Bronze Sword", typ="Weapon", description="A blade", rarity=0.9, value=20, element=None)]}
    game.player_char.equip_diff = lambda item, typ, buy=True: "Attack  +2\nDefense  +0"

    class WeaponFactory:
        def __call__(self):
            return SimpleNamespace(name="Bronze Sword", typ="Weapon", description="A blade", rarity=0.9, value=20, element=None)

    itemdict = {"Weapon": [WeaponFactory()]}
    menu = curses_menus.ShopMenu(game, "Shop here")
    menu.update_itemdict(itemdict)
    assert menu.item_str_list[0].startswith("Weapon")
    menu.buy_or_sell = "Buy"
    menu.current_item = 0
    mod_dict = menu.config_mod_str()
    assert mod_dict == {"Attack": "+2", "Defense": "+0"}
    menu.draw_all()
    assert menu.navigate_options() == "Buy"
    game.stdscr.keys = [10]
    menu.current_item = 0
    assert "Bronze Sword" in menu.navigate_items()

    game2 = _make_game()
    game2.player_char.gold = 50
    game2.player_char.in_town = lambda: False
    game2.player_char.player_level = lambda: 1
    game2.player_char.shop_price_scale = lambda: 1.0
    game2.player_char.inventory = {}
    game2.player_char.equip_diff = lambda item, typ, buy=True: ""
    menu2 = curses_menus.ShopMenu(game2, "Shop here")
    menu2.buy_or_sell = "Buy"
    menu2.itemdict = {"Misc": [lambda: SimpleNamespace(name="Old Key", typ="Misc", description="Key", rarity=1.0, value=5, element=None)]}
    menu2.config_item_str()
    assert any("Old Key" in item for item in menu2.item_str_list)


def test_character_menu_draws_panels_and_navigates(monkeypatch):
    created = []
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory(created))
    game = _make_game(keys=[curses_menus.curses.KEY_RIGHT, 10])
    player = game.player_char
    player.gold = 250
    player.level = SimpleNamespace(level=9, exp=99, exp_to_gain=11)
    player.race = SimpleNamespace(name="Elf")
    player.cls = SimpleNamespace(name="Mage")
    player.encumbered = True
    player.current_weight = lambda: 12
    player.max_weight = lambda: 10
    player.in_town = lambda: False
    player.status_str = lambda: "Healthy\nBlessed"
    player.combat_str = lambda: "Attack  10\nDefense  8"
    player.equipment_str = lambda: "Weapon: Staff\nArmor: Robe"
    player.resist_str = lambda: "Fire: 0\nIce: 0\nWind: 1\nEarth: 2"

    menu = curses_menus.CharacterMenu(game, ["Inventory", "Spells", "Quests", "Back"])
    menu.draw_all()
    menu.refresh_all()
    assert menu.navigate_menu() == 1

    assert any("Level 9 Elf Mage" in str(call[1][2]) for call in created[1].calls if call[0] == "addstr" and len(call[1]) >= 3)
    assert any("ENCUMBERED" in str(call[1][2]) for call in created[1].calls if call[0] == "addstr" and len(call[1]) >= 3)
    assert any("Experience:" in str(call[1][2]) for call in created[2].calls if call[0] == "addstr" and len(call[1]) >= 3)
    assert any("Equipped Gear" in str(call[1][2]) for call in created[3].calls if call[0] == "addstr" and len(call[1]) >= 3)


def test_promotion_popup_draws_class_and_familiar_views(monkeypatch):
    created = []
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory(created))
    game = _make_game()
    game.player_char.stats = SimpleNamespace(strength=10, intel=11, wisdom=12, con=13, charisma=14, dex=15)
    game.player_char.health = SimpleNamespace(max=30)
    game.player_char.mana = SimpleNamespace(max=20)
    game.player_char.combat = SimpleNamespace(attack=5, defense=6, magic=7, magic_def=8)

    offhand = SimpleNamespace(name="Kite Shield", subtyp="Shield", mod=0.25)
    cls = SimpleNamespace(
        name="Knight",
        description="A sturdy fighter",
        str_plus=1,
        int_plus=2,
        wis_plus=3,
        con_plus=4,
        cha_plus=5,
        dex_plus=6,
        att_plus=1,
        def_plus=2,
        magic_plus=3,
        magic_def_plus=4,
        equipment={"Weapon": SimpleNamespace(name="Sword"), "OffHand": offhand, "Armor": SimpleNamespace(name="Plate")},
        restrictions={"Armor": ["Cloth"]},
    )
    popup = curses_menus.PromotionPopupMenu(game, "Choose", "Warrior")
    popup.update_options(["Knight", "Go Back"], {"Warrior": [cls]})
    popup.draw_popup()
    assert any("Promotion" in call[1][2] for call in created[-1].calls if call[0] == "addstr" and len(call[1]) >= 3)

    fam_cls = lambda: SimpleNamespace(
        race="Fairy",
        inspect=lambda: "Helpful familiar",
        spellbook={"Spells": {"Spark": object()}, "Skills": {"Heal": object()}},
    )
    fam_popup = curses_menus.PromotionPopupMenu(game, "Choose Familiar", "Mage", familiar=True)
    fam_popup.update_options(["Fairy", "Go Back"], {"Fairy": fam_cls})
    fam_popup.draw_popup()
    assert any("Fairy" in str(call[1][2]) for call in created[-1].calls if call[0] == "addstr" and len(call[1]) >= 3)


def test_combat_popup_navigation_item_branch_and_remove_shield(monkeypatch):
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory([]))
    game = _make_game(keys=[10])
    game.player_char.mana.current = 5
    game.player_char.inventory = {
        "Potion": [SimpleNamespace(name="Potion", subtyp="Health")],
        "Bomb": [SimpleNamespace(name="Bomb", subtyp="Throwable")],
    }
    game.player_char.equipment = {
        "OffHand": SimpleNamespace(subtyp="Shield"),
        "Weapon": SimpleNamespace(handed=2),
    }
    game.player_char.physical_effects = {"Disarm": SimpleNamespace(active=False)}
    game.player_char.magic_effects = {"Mana Shield": SimpleNamespace(active=True)}
    game.player_char.spellbook = {
        "Spells": {},
        "Skills": {
            "Mana Shield": SimpleNamespace(cost=2, passive=False, name="Mana Shield", weapon=False),
            "Backstab": SimpleNamespace(cost=2, passive=False, name="Backstab", weapon=False),
            "Shield Slam": SimpleNamespace(cost=1, passive=False, name="Shield Slam", weapon=False),
        },
    }
    tile = SimpleNamespace(enemy=SimpleNamespace(incapacitated=lambda: False))

    popup = curses_menus.CombatPopupMenu(game, "Combat")
    popup.update_options("Use Skill", tile=tile)
    assert "Remove Shield  2" in popup.options_list
    assert "Backstab  2" not in popup.options_list
    popup.update_options("Use Item")
    assert popup.options_list == ["Potion  1", "Go Back"]
    assert popup.navigate_popup() == "Potion  1"


def test_slot_machine_and_blackjack_popup_helpers(monkeypatch):
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory([]))
    game = _make_game(keys=[10, 10, 10, 10, 10])
    digits = iter(["1", "2", "3"] * 100)
    monkeypatch.setattr(curses_menus.random, "randint", lambda a, b: int(next(digits)))
    monkeypatch.setattr(curses_menus.time, "sleep", lambda secs: None)

    slot = curses_menus.SlotMachinePopupMenu(game, "Slots")
    result = slot.results()
    assert len(result) == 3
    assert set(result) <= set("123")

    game = _make_game(keys=[10, 10, 10, 10, 10, 10])
    blackjack = curses_menus.BlackjackPopupMenu(game, "Ada  Goblin")
    blackjack.deck = ["♠️ 10", "♠️ 9", "♠️ 8", "♠️ 7", "♠️ 6"]
    monkeypatch.setattr(curses_menus.random, "choice", lambda seq: seq[0])
    result = blackjack.navigate_popup()
    assert result in {"Target Win", "User Win", "Push", "Target Break", "User Break"}


def test_selection_confirm_quest_popup_and_quest_list_navigation(monkeypatch):
    monkeypatch.setattr(curses_menus.curses, "newwin", _fake_newwin_factory([]))
    messages = []
    monkeypatch.setattr(
        curses_menus,
        "TextBox",
        lambda game: SimpleNamespace(
            print_text_in_rectangle=lambda text: messages.append(text),
            clear_rectangle=lambda: messages.append("cleared"),
        ),
    )
    monkeypatch.setattr(curses_menus, "ConfirmPopupMenu", lambda game, text, box_height=7: SimpleNamespace(navigate_popup=lambda: True))

    game = _make_game(keys=[10])
    popup = curses_menus.SelectionPopupMenu(game, "Choose", ["Reward"], rewards=[lambda: "Shown"], confirm=True)
    assert popup.navigate_popup() == 0

    game = _make_game(keys=[10], debug_mode=False)
    monkeypatch.setattr(curses_menus.time, "sleep", lambda secs: None)
    quest_popup = curses_menus.QuestPopupMenu(game, box_height=6, box_width=20)
    quest_popup.draw_popup(["Hi"])

    game = _make_game(
        keys=[
            curses_menus.curses.KEY_DOWN,
            10,
            curses_menus.curses.KEY_DOWN,
            10,
            curses_menus.curses.KEY_DOWN,
            10,
            curses_menus.curses.KEY_DOWN,
            10,
        ]
    )
    game.player_char.quest_dict = {
        "Bounty": {"Rat": [{"num": 2}, 2, True]},
        "Main": {"Main Quest": {"Completed": False, "Turned In": False, "Type": "Defeat", "What": "Rat", "Who": "Sergeant"}},
        "Side": {
            "Complete Me": {"Completed": True, "Turned In": False, "Type": "Defeat", "What": "Bat", "Who": "Barkeep"},
            "Done Deal": {"Completed": True, "Turned In": True, "Type": "Defeat", "What": "Slime", "Who": "Barkeep"},
        },
    }
    qlist = curses_menus.QuestListPopupMenu(game, "Quests")
    qlist.navigate_popup()
    assert any("Turned In" in option or "Complete Me" in option for option in qlist.options_list)
