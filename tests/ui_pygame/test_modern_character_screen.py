#!/usr/bin/env python3
"""Focused coverage for the standard pygame character menu."""

from __future__ import annotations

from types import SimpleNamespace

import pygame

from src.ui_pygame import game as pygame_game
from src.ui_pygame.gui.dungeon_manager import DungeonManager
from src.ui_pygame.gui.modern_character_screen import ModernCharacterScreen, RESISTANCE_ORDER


class DummySurface:
    def __init__(self, size=(64, 24), text=None):
        self._size = size
        self.text = text

    def get_width(self):
        return self._size[0]

    def get_height(self):
        return self._size[1]

    def get_rect(self, **kwargs):
        rect = pygame.Rect(0, 0, *self._size)
        for key, value in kwargs.items():
            setattr(rect, key, value)
        return rect


class RecordingFont:
    def __init__(self, height=24):
        self.render_calls = []
        self._height = height

    def render(self, text, _antialias, _color):
        self.render_calls.append(text)
        return DummySurface((max(8, len(text) * 8), self._height), text=text)

    def get_height(self):
        return self._height

    def size(self, text):
        return (max(8, len(text) * 8), self._height)


class RecordingScreen:
    def __init__(self, size=(1000, 720)):
        self._size = size
        self.blit_calls = []
        self.fill_calls = []

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))

    def fill(self, color):
        self.fill_calls.append(color)

    def get_width(self):
        return self._size[0]

    def get_height(self):
        return self._size[1]

    def copy(self):
        return "screen-copy"


def _make_presenter():
    return SimpleNamespace(
        screen=RecordingScreen(),
        width=1000,
        height=720,
        title_font=RecordingFont(34),
        large_font=RecordingFont(28),
        normal_font=RecordingFont(22),
        small_font=RecordingFont(18),
        clock=SimpleNamespace(tick=lambda _fps: None),
        debug_mode=True,
    )


def _effect(active=True, duration=2, extra=0):
    return SimpleNamespace(active=active, duration=duration, extra=extra)


def _make_player():
    player = SimpleNamespace(
        name="Longnamed Hero of the Northern Gate",
        race=SimpleNamespace(name="Human"),
        sex="Female",
        cls=SimpleNamespace(name="Warrior"),
        level=SimpleNamespace(level=7, exp=1250, exp_to_gain=50),
        gold=321,
        location_z=0,
        health=SimpleNamespace(current=45, max=60),
        mana=SimpleNamespace(current=12, max=20),
        stats=SimpleNamespace(strength=14, intel=11, wisdom=10, con=13, charisma=9, dex=8),
        combat=SimpleNamespace(attack=10, defense=8, magic=3, magic_def=4),
        resistance={
            "Fire": -0.15,
            "Ice": -0.15,
            "Water": -0.15,
            "Poison": 0.2,
            "Physical": 0.1,
        },
        equipment={
            "Weapon": SimpleNamespace(name="Sword", typ="Weapon", subtyp="Sword", damage=12, crit_chance=0.15, weight=4, description="Reliable steel."),
            "Armor": SimpleNamespace(name="Mail", typ="Armor", subtyp="Medium", armor=8, weight=12),
            "Helmet": SimpleNamespace(name="Iron Helm", typ="Helmet", subtyp="Heavy", armor=4, weight=6),
            "OffHand": None,
            "Ring": SimpleNamespace(name="Ruby Ring", typ="Accessory", subtyp="Ring", mod="Block", weight=0.1),
            "Pendant": SimpleNamespace(name="Pendant of Sight", typ="Accessory", subtyp="Pendant", mod="Vision", weight=0.2),
        },
        buffs=[SimpleNamespace(name="Might"), SimpleNamespace(name="Might")],
        stat_effects={"Attack": _effect(True, 3, 4), "Speed": _effect(False)},
        magic_effects={"Regen": _effect(True, 2, 5)},
        class_effects={"Power Up": _effect(False)},
        status_effects={"Poison": _effect(True, 4, 2)},
        physical_effects={"Bleed": _effect(False)},
        spellbook={"Spells": {}, "Skills": {}},
        special_inventory={},
        kill_dict={"Regular": {"Goblin": 2}},
        sight=True,
    )
    player.current_weight = lambda: 19
    player.max_weight = lambda: 140
    player.level_exp = lambda: 300
    player.critical_chance = lambda _slot: 0.125
    def check_mod(mod, typ=None):
        if mod == "resist":
            value = player.resistance.get(typ, 0)
            pendant = player.equipment.get("Pendant")
            pendant_mod = str(getattr(pendant, "mod", "") or "")
            if pendant_mod.split("-")[-1] in {typ, "Elemental"} and typ in {"Fire", "Ice", "Electric", "Water", "Earth", "Wind"}:
                value += 1 if "Immune" in pendant_mod else 0.5
            return value
        return {
            "weapon": 18,
            "offhand": 8,
            "armor": 22,
            "shield": 15,
            "magic def": 7,
            "magic": 9,
            "speed": 8,
        }.get(mod, 0)

    player.check_mod = check_mod
    player.in_town = lambda: True
    return player


def test_modern_character_tabs_are_generic_and_switchable():
    screen = ModernCharacterScreen(_make_presenter())

    assert [tab.label for tab in screen.tabs] == ["Character", "Class", "Equipment"]
    assert screen.active_tab.key == "character"
    assert abs((screen.character_panel_rect.width * 2) - (screen.combat_panel_rect.width * 3)) <= 3

    screen.move_tab(1)
    assert screen.active_tab.key == "class"

    screen.move_tab(1)
    assert screen.active_tab.key == "equipment"

    screen.move_tab(1)
    assert screen.active_tab.key == "character"
    assert screen.equipment_selector_active is False


def test_modern_character_summary_helpers_cover_xp_equipment_resistances_and_effects():
    screen = ModernCharacterScreen(_make_presenter())
    player = _make_player()

    assert screen.xp_progress(player) == 250 / 300
    assert screen.xp_label(player) == "250/300 XP (50 next)"

    player.level.exp_to_gain = "MAX"
    assert screen.xp_progress(player) == 1.0
    assert screen.xp_label(player) == "1250 XP / MAX level"
    player.level.exp_to_gain = 50

    summary = dict(screen.build_character_summary(player))
    assert summary["Race"] == "Human"
    assert summary["Class"] == "Warrior"
    assert dict(screen.build_portrait_details(player)) == {"Gold": "321G", "Location": "Town"}
    player.location_z = 3
    assert screen.location_label(player) == "Dungeon Level 3"
    player.location_z = 0
    assert screen.portrait_filename(player) == "human_base_portraits.png"

    player.race = SimpleNamespace(name="Half Elf")
    player.sex = "Male"
    assert screen.portrait_filename(player) == "half_elf_base_portraits.png"
    player.race = SimpleNamespace(name="Human")
    player.sex = "Female"

    combat = dict(screen.build_combat_stats(player))
    assert combat["HP"] == "45/60"
    assert combat["Attack"] == "18"
    assert combat["Magic Defense"] == "7"

    assert combat["Critical"] == "12.5%"
    assert combat["Weight"] == "19/140"

    player.equipment["OffHand"] = SimpleNamespace(name="Dagger", typ="Weapon", subtyp="Dagger")
    combat = dict(screen.build_combat_stats(player))
    assert combat["Attack"] == "18/8"
    player.equipment["OffHand"] = None

    slots = screen.build_equipment_slots(player)
    assert [slot.slot for slot in slots] == ["Weapon", "Armor", "Helmet", "OffHand", "Ring", "Pendant"]
    helmet = next(slot for slot in slots if slot.slot == "Helmet")
    assert helmet.implemented is True
    assert helmet.item_name == "Iron Helm"
    assert helmet.details == ("Type: Heavy", "Base Armor: 4")
    weapon = next(slot for slot in slots if slot.slot == "Weapon")
    assert weapon.item_name == "Sword (1H)"
    assert weapon.details == ("Type: Sword", "Base Damage: 12", "Crit: 15%")
    armor = next(slot for slot in slots if slot.slot == "Armor")
    assert armor.details == ("Type: Medium", "Base Armor: 8")
    ring = next(slot for slot in slots if slot.slot == "Ring")
    assert ring.details == ()
    assert ring.buffs == ("Block",)
    pendant = next(slot for slot in slots if slot.slot == "Pendant")
    assert pendant.details == ()
    assert pendant.buffs == ("Vision",)
    assert pendant.icon_item is player.equipment["Pendant"]
    assert weapon.icon_item is player.equipment["Weapon"]

    player.equipment["Ring"] = SimpleNamespace(name="Weightless Ring", typ="Accessory", subtyp="Ring", mod="Dodge", weight=0)
    weightless_ring = next(slot for slot in screen.build_equipment_slots(player) if slot.slot == "Ring")
    assert weightless_ring.details == ()
    assert weightless_ring.buffs == ("Dodge",)
    player.equipment["Ring"] = SimpleNamespace(name="Ruby Ring", typ="Accessory", subtyp="Ring", mod="Block", weight=0.1)

    player.equipment["OffHand"] = SimpleNamespace(name="Aspis", typ="OffHand", subtyp="Shield", mod=0.1, weight=10)
    shield = next(slot for slot in screen.build_equipment_slots(player) if slot.slot == "OffHand")
    assert shield.details == ("Type: Shield", "Block: 10%")
    assert shield.buffs == ()

    player.equipment["OffHand"] = SimpleNamespace(name="Svalinn", typ="OffHand", subtyp="Shield", mod=0.35, weight=18)
    svalinn = next(slot for slot in screen.build_equipment_slots(player) if slot.slot == "OffHand")
    assert svalinn.details == ("Type: Shield", "Block: 35%")
    assert svalinn.buffs == ("+25% Fire Resistance",)
    player.equipment["OffHand"] = None

    player.equipment["Pendant"] = SimpleNamespace(
        name="Fire Chain",
        typ="Accessory",
        subtyp="Pendant",
        mod="Resist-Fire",
        weight=0.2,
    )
    fire_chain = next(slot for slot in screen.build_equipment_slots(player) if slot.slot == "Pendant")
    assert fire_chain.buffs == ("+50% Fire Resistance",)

    player.equipment["Armor"] = SimpleNamespace(
        name="Resist Armor",
        typ="Armor",
        subtyp="Plate",
        armor=12,
        resistances={"Fire": 0.25, "Water": 0.25},
        weight=18,
    )
    resist_armor = next(slot for slot in screen.build_equipment_slots(player) if slot.slot == "Armor")
    assert "+25% Fire Resistance" in resist_armor.buffs
    assert "+25% Water Resistance" in resist_armor.buffs

    player.equipment["Weapon"] = SimpleNamespace(
        name="Claymore",
        typ="Weapon",
        subtyp="Longsword",
        handed=2,
        damage=28,
        crit_chance=0.15,
        weight=12,
    )
    player.equipment["OffHand"] = SimpleNamespace(name="No OffHand", typ="OffHand", subtyp="None")
    player.cls = SimpleNamespace(name="Warrior", equip_check=lambda _item, slot: slot != "OffHand")
    two_handed_slots = screen.build_equipment_slots(player)
    occupied_offhand = next(slot for slot in two_handed_slots if slot.slot == "OffHand")
    assert occupied_offhand.item_name == "Claymore (2H)"
    assert occupied_offhand.icon_item is player.equipment["Weapon"]
    assert occupied_offhand.details == ("Type: Longsword", "Base Damage: 28", "Crit: 15%")

    player.cls = SimpleNamespace(name="Berserker", equip_check=lambda _item, slot: slot == "OffHand")
    berserker_offhand = next(slot for slot in screen.build_equipment_slots(player) if slot.slot == "OffHand")
    assert berserker_offhand.item_name == "(empty)"

    player.cls = SimpleNamespace(name="Lancer", equip_check=lambda _item, _slot: False)
    player.equipment["Weapon"].subtyp = "Polearm"
    lancer_offhand = next(slot for slot in screen.build_equipment_slots(player) if slot.slot == "OffHand")
    assert lancer_offhand.item_name == "(empty)"

    player.equipment["Weapon"] = SimpleNamespace(name="Sword", typ="Weapon", subtyp="Sword", damage=12, crit_chance=0.15, weight=4)
    player.equipment["OffHand"] = None
    player.equipment["Pendant"] = SimpleNamespace(name="Pendant of Sight", typ="Accessory", subtyp="Pendant", mod="Vision", weight=0.2)
    player.cls = SimpleNamespace(name="Warrior", equip_check=lambda _item, _slot: True)

    grouped_resistances = screen.group_resistances(player)
    assert [entry.name for entry in grouped_resistances["weaknesses"]] == ["Fire", "Ice", "Water"]
    assert [entry.name for entry in grouped_resistances["resistances"]] == ["Poison", "Physical"]

    player.equipment["Pendant"] = SimpleNamespace(name="Fire Chain", typ="Accessory", subtyp="Pendant", mod="Resist-Fire", weight=0.2)
    grouped_resistances = screen.group_resistances(player)
    assert "Fire" not in [entry.name for entry in grouped_resistances["weaknesses"]]
    assert "Fire" in [entry.name for entry in grouped_resistances["resistances"]]
    player.equipment["Pendant"] = SimpleNamespace(name="Pendant of Sight", typ="Accessory", subtyp="Pendant", mod="Vision", weight=0.2)

    equipment_buffs = screen.collect_equipment_buffs(player)
    assert [(buff.name, buff.source) for buff in equipment_buffs] == [
        ("Block", "Ring: Ruby Ring"),
        ("Vision", "Pendant: Pendant of Sight"),
    ]

    assert screen.selected_equipment_slot(player) == "Weapon"
    screen.move_equipment_selector(player, "right")
    assert screen.selected_equipment_slot(player) == "Armor"
    screen.move_equipment_selector(player, "right")
    assert screen.selected_equipment_slot(player) == "OffHand"


def test_portrait_details_draws_long_location_without_truncating(monkeypatch):
    screen = ModernCharacterScreen(_make_presenter())
    drawn = []
    monkeypatch.setattr(
        screen,
        "_draw_text",
        lambda text, font, _color, _x, y, _max_width=None: drawn.append((text, y, font.get_height())),
    )

    detail_rect = pygame.Rect(0, 0, 120, 80)
    screen._draw_portrait_details(
        [("Location", "Realm of Cambion")],
        detail_rect,
        0,
    )

    assert "Realm of Cambion" in [text for text, _y, _height in drawn]
    assert not any(str(text).endswith("...") for text, _y, _height in drawn)
    assert all(y + height <= detail_rect.bottom for _text, y, height in drawn)


def test_portrait_details_compact_rows_stay_inside_short_detail_box(monkeypatch):
    screen = ModernCharacterScreen(_make_presenter())
    drawn = []
    monkeypatch.setattr(
        screen,
        "_draw_text",
        lambda text, font, _color, _x, y, _max_width=None: drawn.append((text, y, font.get_height())),
    )

    detail_rect = pygame.Rect(0, 0, 210, 46)
    screen._draw_portrait_details(
        [("Gold", "71789G"), ("Location", "Dungeon Level 1")],
        detail_rect,
        0,
    )

    assert "Location" in [text for text, _y, _height in drawn]
    assert "Dungeon Level 1" in [text for text, _y, _height in drawn]
    assert all(y + height <= detail_rect.bottom for _text, y, height in drawn)


def test_modern_character_companion_display_prefers_familiar_then_living_summon():
    screen = ModernCharacterScreen(_make_presenter())
    player = _make_player()

    assert screen.active_companion_for_display(player) is None

    familiar = SimpleNamespace(name="Aster", race="Fairy", level=SimpleNamespace(level=4), is_alive=lambda: True)
    player.familiar = familiar
    player.summons = {"Fuath": SimpleNamespace(name="Fuath", is_alive=lambda: True)}
    assert screen.active_companion_for_display(player) == ("Familiar", familiar)
    assert ("Level", "4") in screen.companion_summary_rows("Familiar", familiar)

    player.familiar = None
    spent = SimpleNamespace(name="Spent", is_alive=lambda: False)
    living = SimpleNamespace(name="Fuath", race="Spirit", level=SimpleNamespace(pro_level=2), is_alive=lambda: True)
    player.summons = {"Spent": spent, "Fuath": living}
    assert screen.active_companion_for_display(player) == ("Summon", living)
    assert ("Type", "Spirit") in screen.companion_summary_rows("Summon", living)

    patagon = SimpleNamespace(name="Patagon", cls=None, level=SimpleNamespace(level=1), is_alive=lambda: True)
    assert ("Type", "Summon") in screen.companion_summary_rows("Summon", patagon)

    player.summons = {"Spent": spent}
    assert screen.active_companion_for_display(player) is None


def test_modern_character_class_tab_renders_companion_art(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()
    companion = SimpleNamespace(
        name="Patagon",
        cls=None,
        health=SimpleNamespace(current=40, max=50),
        mana=SimpleNamespace(current=5, max=10),
        combat=SimpleNamespace(attack=14, defense=8, magic=0, magic_def=3),
        level=SimpleNamespace(level=1),
        is_alive=lambda: True,
    )
    player.cls = SimpleNamespace(name="Summoner", description="Calls allies from distant realms.")
    player.summons = {"Patagon": companion}
    calls = []
    screen.companion_art_manager = SimpleNamespace(
        get_scaled_sprite=lambda entity, size: calls.append((entity, size)) or DummySurface(size)
    )

    monkeypatch.setattr(screen, "draw_semi_transparent_panel", lambda rect, alpha=180: DummySurface((rect.width, rect.height)))
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.draw.rect", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.draw.line", lambda *_args, **_kwargs: None)

    screen.draw_class_tab(player)

    assert calls and calls[0][0] is companion
    rendered_text = set(presenter.small_font.render_calls + presenter.normal_font.render_calls)
    assert {"Class", "Class Profile", "Companions & Summons", "Patagon", "Type", "Summon", "HP", "40/50"}.issubset(rendered_text)


def test_modern_character_class_tab_supports_multiple_summon_tiles_and_popup(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()

    def summon(name):
        return SimpleNamespace(
            name=name,
            cls=None,
            health=SimpleNamespace(current=40, max=50),
            mana=SimpleNamespace(current=5, max=10),
            combat=SimpleNamespace(attack=14, defense=8, magic=0, magic_def=3),
            level=SimpleNamespace(level=1, exp=25, exp_to_gain=75),
            spellbook={"Skills": {"Throw Rock": object()}, "Spells": {}},
            is_alive=lambda: True,
        )

    player.cls = SimpleNamespace(name="Summoner", description="Calls allies from distant realms. " * 12)
    player.promotion_kit_state = {"summon_bonds": {"Patagon": 15, "Dilong": 0, "Agloolik": 0}}
    player.summons = {"Patagon": summon("Patagon"), "Dilong": summon("Dilong"), "Agloolik": summon("Agloolik")}
    screen.companion_art_manager = SimpleNamespace(get_scaled_sprite=lambda _entity, size: DummySurface(size))
    popups = []

    class FakePopup:
        def __init__(self, _presenter, message, show_buttons=False):
            self.message = message
            self.show_buttons = show_buttons
            self.show_kwargs = None
            popups.append(self)

        def show(self, **kwargs):
            self.show_kwargs = kwargs
            return None

    import src.ui_pygame.gui.modern_character_screen as modern_module

    monkeypatch.setattr(modern_module, "ConfirmationPopup", FakePopup)
    monkeypatch.setattr(screen, "draw_semi_transparent_panel", lambda rect, alpha=180: DummySurface((rect.width, rect.height)))
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.draw.rect", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.draw.line", lambda *_args, **_kwargs: None)

    screen.draw_class_tab(player)

    assert len(screen.class_companion_tile_rects(screen.class_companion_entries(player))) == 3
    rendered_text = set(presenter.small_font.render_calls + presenter.normal_font.render_calls)
    assert {"Patagon", "Dilong", "Agloolik", "XP", "25/100 XP", "Bond", "15/100"}.issubset(rendered_text)

    screen.selected_class_companion_index = 1
    screen._open_class_companion_popup(player)

    assert popups
    assert "Dilong" in popups[-1].message
    assert "Abilities:" in popups[-1].message
    assert callable(popups[-1].show_kwargs["background_draw_func"])


def test_modern_character_draw_all_renders_active_tabs(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()

    monkeypatch.setattr(screen, "draw_semi_transparent_panel", lambda rect, alpha=180: DummySurface((rect.width, rect.height)))
    draw_rect_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.draw.rect", lambda *_args, **_kwargs: draw_rect_calls.append((_args, _kwargs)))
    draw_line_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.draw.line", lambda *_args, **_kwargs: draw_line_calls.append((_args, _kwargs)))
    flip_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.display.flip", lambda: flip_calls.append(True))
    loaded_renders = []
    screen.item_render_manager = SimpleNamespace(
        get_scaled_render=lambda item, size: loaded_renders.append((getattr(item, "name", ""), size))
        or pygame.Surface(size, pygame.SRCALPHA)
    )

    screen.draw_all(player)
    rendered_text = set(presenter.large_font.render_calls + presenter.normal_font.render_calls + presenter.small_font.render_calls)
    assert "Character" in presenter.large_font.render_calls
    assert "Combat Stats" in presenter.large_font.render_calls
    assert "Core Attributes" in presenter.large_font.render_calls
    assert "Strength" in rendered_text
    assert "RACE" in presenter.normal_font.render_calls
    assert "CLASS" in presenter.normal_font.render_calls
    assert "Human" in presenter.large_font.render_calls
    assert "Warrior" in presenter.large_font.render_calls
    assert "HP" in rendered_text
    assert "Weaknesses" in presenter.large_font.render_calls
    assert "Resistances" in presenter.large_font.render_calls
    assert "Fire (-15%)" in rendered_text
    assert "Equipment" not in presenter.large_font.render_calls
    assert "XP EARNED" not in presenter.small_font.render_calls
    assert "XP TO NEXT" not in presenter.small_font.render_calls
    assert "250/300 XP (50 next)" in presenter.small_font.render_calls
    assert len(draw_line_calls) >= 2
    assert flip_calls

    screen.select_tab("class")
    screen.draw_all(player, do_flip=False)
    assert "Class" in presenter.large_font.render_calls
    assert "Class Profile" in presenter.normal_font.render_calls
    assert "Companions & Summons" in presenter.normal_font.render_calls

    screen.select_tab("equipment")
    screen.draw_all(player, do_flip=False)
    assert "Equipment" in presenter.large_font.render_calls
    assert "E: Select gear" in presenter.small_font.render_calls
    screen.equipment_selector_active = True
    screen.draw_all(player, do_flip=False)
    assert "Arrows: Select gear  Enter: Change  E/Esc: Back" in presenter.small_font.render_calls
    assert "Equipment Layout" not in presenter.large_font.render_calls
    assert "Item Details" not in presenter.normal_font.render_calls
    assert "Equipment Buffs" not in presenter.normal_font.render_calls
    assert {"Helmet", "Weapon", "Armor", "OffHand", "Ring", "Pendant"}.issubset(set(presenter.normal_font.render_calls))
    assert "Sword (1H)" in presenter.normal_font.render_calls
    assert "Type:" in presenter.small_font.render_calls
    assert "Sword" in presenter.small_font.render_calls
    assert "Base Damage:" in presenter.small_font.render_calls
    assert "12" in presenter.small_font.render_calls
    assert "Crit:" in presenter.small_font.render_calls
    assert any(name == "Sword" for name, _size in loaded_renders)
    assert any(name == "Mail" for name, _size in loaded_renders)
    assert any(name == "Iron Helm" for name, _size in loaded_renders)
    assert "15%" in presenter.small_font.render_calls
    assert "Medium" in presenter.small_font.render_calls
    assert "Base Armor:" in presenter.small_font.render_calls
    assert "8" in presenter.small_font.render_calls
    assert "Weight:" not in presenter.small_font.render_calls
    assert "Mod Block" not in presenter.small_font.render_calls
    assert "Buff: Block" in presenter.small_font.render_calls
    assert "Buff: Vision" in presenter.small_font.render_calls
    assert any(name == "Ruby Ring" for name, _size in loaded_renders)
    assert any(name == "Pendant of Sight" for name, _size in loaded_renders)


def test_modern_character_menu_renders_with_and_without_portrait_assets(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()
    monkeypatch.setattr(screen, "draw_semi_transparent_panel", lambda rect, alpha=180: DummySurface((rect.width, rect.height)))
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.draw.rect", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.draw.line", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.display.flip", lambda: None)

    screen.load_portrait = lambda _player: pygame.Surface((225, 400), pygame.SRCALPHA)
    screen.draw_all(player)
    assert presenter.screen.blit_calls
    assert "Gold" in presenter.small_font.render_calls
    assert "321G" in presenter.small_font.render_calls
    assert "Location" in presenter.small_font.render_calls
    assert "Town" in presenter.small_font.render_calls
    gold_label_x = next(position[0] for surface, position in presenter.screen.blit_calls if getattr(surface, "text", None) == "Gold")
    gold_value_x = next(position[0] for surface, position in presenter.screen.blit_calls if getattr(surface, "text", None) == "321G")
    assert gold_value_x > gold_label_x

    atlas_surface = pygame.Surface((225, 400), pygame.SRCALPHA)
    frame = screen.portrait_frame_rect(screen.character_panel_rect.top + 52, atlas_surface)
    assert frame.size == (225, 400)

    presenter.small_font.render_calls.clear()
    screen.load_portrait = lambda _player: None
    screen.draw_all(player)
    assert "Portrait" in presenter.small_font.render_calls


def test_modern_character_resistance_columns_render_all_possible_entries(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()
    player.resistance = {name: -0.1 for name in RESISTANCE_ORDER}

    monkeypatch.setattr(screen, "draw_semi_transparent_panel", lambda rect, alpha=180: DummySurface((rect.width, rect.height)))
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.draw.rect", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.draw.line", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.display.flip", lambda: None)

    screen.draw_all(player)
    rendered_text = set(presenter.normal_font.render_calls + presenter.small_font.render_calls)
    for name in RESISTANCE_ORDER:
        assert f"{name} (-10%)" in rendered_text


def test_modern_character_navigation_switches_tabs_and_exits(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()

    event_batches = iter([
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2)],
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_3)],
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
    ])
    monkeypatch.setattr(screen, "draw_all", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: [])
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.event.get", lambda: next(event_batches, []))

    assert screen.navigate(player) == "Exit Menu"
    assert screen.active_tab.key == "equipment"


def test_modern_equipment_selector_requires_explicit_toggle(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()

    event_batches = iter([
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_3)],
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)],
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_3)],
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_e)],
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)],
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
    ])
    monkeypatch.setattr(screen, "draw_all", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: [])
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.event.get", lambda: next(event_batches, []))

    assert screen.navigate(player) == "Exit Menu"
    assert screen.active_tab.key == "equipment"
    assert screen.selected_equipment_slot(player) == "Armor"
    assert screen.equipment_selector_active is False


def test_modern_equipment_tab_enter_opens_selected_slot_change(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()
    screen.select_tab("equipment")
    screen.set_selected_equipment_slot(player, "Ring")

    opened = []

    class FakeEquipmentPopup:
        def __init__(self, _presenter, _parent):
            self.items = []
            self.selected_index = 0

        def build_items(self, _player):
            self.items = [("Weapon", object()), ("Ring", object())]

        def on_select(self, _player, item):
            opened.append(item[0])

    import src.ui_pygame.gui.modern_character_screen as modern_module

    monkeypatch.setattr(modern_module, "EquipmentPopupMenu", FakeEquipmentPopup)

    screen.open_selected_equipment_change(player)

    assert opened == ["Ring"]


def test_modern_character_menu_mouse_selects_equipment_slot(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()
    screen.select_tab("equipment")
    opened = []

    monkeypatch.setattr(screen, "draw_all", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(screen, "open_selected_equipment_change", lambda _player: opened.append(screen.selected_equipment_slot(_player)))
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: [])

    click_pos = screen.equipment_slot_rects()["Ring"].center
    event_batches = iter([
        [SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=click_pos)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.event.get", lambda: next(event_batches, []))

    assert screen.navigate(player) == "Exit Menu"
    assert screen.equipment_selector_active is False
    assert screen.selected_equipment_slot(player) == "Ring"
    assert opened == ["Ring"]


def test_modern_character_menu_mouse_tabs_and_actions(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()
    monkeypatch.setattr(screen, "draw_all", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: [])

    equipment_tab_pos = screen.tab_button_rects()[2].center
    exit_pos = screen.action_rects()[-1].center
    event_batches = iter([
        [SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=equipment_tab_pos)],
        [SimpleNamespace(type=pygame.MOUSEBUTTONDOWN, button=1, pos=exit_pos)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.event.get", lambda: next(event_batches, []))

    assert screen.navigate(player) == "Exit Menu"
    assert screen.active_tab.key == "equipment"


def test_modern_character_menu_actions_remove_quit_and_put_exit_last(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()

    event_batches = iter([[pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]])
    monkeypatch.setattr(screen, "draw_all", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: [])
    monkeypatch.setattr("src.ui_pygame.gui.modern_character_screen.pygame.event.get", lambda: next(event_batches, []))

    assert screen.navigate(player) == "Exit Menu"
    assert screen.menu_options == ["Inventory", "Quests", "Key Items", "Bestiary", "Specials", "Exit Menu"]
    assert "Change Equipment" not in screen.menu_options
    assert "Quit Game" not in screen.menu_options


def test_modern_character_menu_opens_bestiary(monkeypatch):
    presenter = _make_presenter()
    screen = ModernCharacterScreen(presenter)
    player = _make_player()
    opened = []

    class FakeBestiaryPopup:
        def __init__(self, _presenter, _parent):
            opened.append("created")

        def show(self, _player, **kwargs):
            opened.append((kwargs.get("flush_events"), kwargs.get("require_key_release")))

    import src.ui_pygame.gui.modern_character_screen as modern_module

    monkeypatch.setattr(modern_module, "BestiaryPopupMenu", FakeBestiaryPopup)

    assert screen._open_menu_choice("Bestiary", player) is None
    assert opened == ["created", (True, True)]


def test_town_character_info_uses_modern_screen_by_default(monkeypatch):
    used = []

    class FakeModern:
        def __init__(self, _presenter):
            used.append("modern")

        def navigate(self, _player):
            return "Exit Menu"

    game = pygame_game.PygameGame.__new__(pygame_game.PygameGame)
    game.presenter = SimpleNamespace()
    game.player_char = SimpleNamespace(quit=False)
    monkeypatch.setattr(pygame_game, "ModernCharacterScreen", FakeModern)

    game.show_character_info()

    assert used == ["modern"]


def test_dungeon_character_screen_router_lazy_loads_modern_default(monkeypatch):
    created = []

    class FakeModern:
        def __init__(self, presenter):
            self.presenter = presenter
            self.background = None
            created.append(self)

    import src.ui_pygame.gui.modern_character_screen as modern_module

    monkeypatch.setattr(modern_module, "ModernCharacterScreen", FakeModern)

    manager = DungeonManager.__new__(DungeonManager)
    manager.presenter = SimpleNamespace()
    manager.game = SimpleNamespace()
    manager.character_screen = None
    manager._dungeon_background = "dungeon-bg"

    first = manager._get_character_screen()
    second = manager._get_character_screen()

    assert first is second
    assert first.background == "dungeon-bg"
    assert created == [first]
