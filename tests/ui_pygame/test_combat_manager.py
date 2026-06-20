#!/usr/bin/env python3
"""Focused coverage for pygame combat-manager helper logic."""

from __future__ import annotations

from types import SimpleNamespace

import pygame
import pytest

from src.ui_pygame.gui import combat_manager


@pytest.fixture(autouse=True)
def _init_pygame():
    if not pygame.get_init():
        pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    yield


class RecordingScreen:
    def __init__(self, size=(800, 600)):
        self._size = size
        self.blit_calls = []
        self.fill_calls = []

    def fill(self, color):
        self.fill_calls.append(color)

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))

    def copy(self):
        return f"screen-copy-{len(self.blit_calls)}"

    def get_size(self):
        return self._size

    def get_width(self):
        return self._size[0]

    def get_height(self):
        return self._size[1]


class RecordingFont:
    def __init__(self):
        self.render_calls = []

    def render(self, text, _antialias, _color):
        self.render_calls.append(text)
        return SimpleNamespace(
            text=text,
            get_rect=lambda **kwargs: pygame.Rect(0, 0, max(8, len(text) * 8), 24),
        )

    def size(self, text):
        return (max(8, len(text) * 8), 24)


class DummyCombatView:
    def __init__(self, screen, presenter):
        self.screen = screen
        self.presenter = presenter
        self.combat_width = screen.get_size()[0]
        self.combat_height = screen.get_size()[1]
        self.scrolled = []
        self.messages = []
        self.enemy_damage_calls = []
        self.flash_calls = []
        self.impact_calls = []
        self.reload_calls = []
        self.enemy_deaths = []
        self.reset_calls = 0
        self.render_calls = []
        self.hide_enemy_calls = 0
        self.colors = {"log_damage": (235, 120, 105), "log_heal": (120, 210, 135)}

    def scroll_log(self, amount):
        self.scrolled.append(amount)

    def add_combat_message(self, message):
        self.messages.append(message)

    def reset_combat_log(self):
        self.reset_calls += 1

    def hide_enemy_for_flee(self):
        self.hide_enemy_calls += 1

    def render_enemy_in_dungeon(self, *args, **kwargs):
        self.render_calls.append(("enemy", args, kwargs))
        return None

    def render_combat_overlay(self, *args, **kwargs):
        self.render_calls.append(("overlay", args, kwargs))
        return None

    def enemy_take_damage(self, enemy):
        self.enemy_damage_calls.append(enemy)

    def show_damage_flash(self, player_side, event_handler=None):
        self.flash_calls.append((player_side, event_handler))

    def trigger_impact_effect(self, target, kind="weapon", element=None, critical=False):
        self.impact_calls.append((target, kind, element, critical))

    def trigger_floating_text(self, target, text, color=None):
        self.impact_calls.append(("float", target, text, color))

    def reload_enemy_sprite(self, enemy):
        self.reload_calls.append(enemy)

    def enemy_dies(self, enemy):
        self.enemy_deaths.append(enemy)


class DummyLevelUpScreen:
    def __init__(self, screen, presenter):
        self.screen = screen
        self.presenter = presenter
        self.calls = []

    def show_level_up(self, player_char, game):
        self.calls.append((player_char, game))


class DummyHud:
    def __init__(self):
        self.calls = []

    def render_hud(self, *args, **kwargs):
        self.calls.append((args, kwargs))


class DummyPresenter:
    def __init__(self):
        self.screen = RecordingScreen()
        self.title_font = RecordingFont()
        self.normal_font = RecordingFont()
        self.small_font = RecordingFont()
        self._background = "presenter-background"

    def get_background_surface(self):
        return self._background


class DummyClock:
    def __init__(self, frame_ms=100):
        self.ticks = []
        self.frame_ms = frame_ms

    def tick(self, fps):
        self.ticks.append(fps)

    def get_time(self):
        return self.frame_ms


class DummySurface:
    def __init__(self, size=(800, 600)):
        self._size = size
        self.alpha = None
        self.fill_calls = []

    def set_alpha(self, value):
        self.alpha = value

    def fill(self, color):
        self.fill_calls.append(color)

    def get_size(self):
        return self._size


def _make_manager(monkeypatch):
    presenter = DummyPresenter()
    hud = DummyHud()
    game = SimpleNamespace()

    monkeypatch.setattr(combat_manager, "CombatView", DummyCombatView)
    monkeypatch.setattr(combat_manager, "LevelUpScreen", DummyLevelUpScreen)

    manager = combat_manager.GUICombatManager(presenter, hud, game)
    return manager


def _make_player(name="Hero"):
    player = SimpleNamespace(
        name=name,
        health=SimpleNamespace(current=50, max=50),
        mana=SimpleNamespace(current=10, max=10),
        spellbook={"Spells": {}, "Skills": {}},
        inventory={},
        encumbered=False,
        anti_magic_active=False,
    )
    player.in_town = lambda: False
    player.is_disarmed = lambda: False
    player.abilities_suppressed = lambda: False
    player.effects = lambda end=False: None
    return player


def _make_enemy(name="Goblin", hp=(20, 20)):
    enemy = SimpleNamespace(name=name, health=SimpleNamespace(current=hp[0], max=hp[1]))
    enemy.is_alive = lambda: enemy.health.current > 0
    return enemy


def test_render_combat_frame_preserves_enemy_draw_before_overlay(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy()
    dungeon_calls = []
    manager.dungeon_renderer = SimpleNamespace(
        render_dungeon_view=lambda *args, **kwargs: dungeon_calls.append((args, kwargs))
    )
    manager.player_world_dict = {"tile": object()}
    manager.engine = SimpleNamespace(is_player_turn=lambda: False, show_enemy_details=lambda: False)

    manager._render_combat_frame(player, enemy, ["Attack"], 0)

    assert dungeon_calls
    assert [call[0] for call in manager.combat_view.render_calls] == ["enemy", "overlay"]
    assert manager.combat_view.render_calls[0][1] == (player, enemy)
    assert manager.combat_view.render_calls[1][2]["current_turn"] is None
    assert manager.combat_view.render_calls[1][2]["show_enemy_details"] is False
    assert manager.hud.calls


def test_render_combat_frame_records_bestiary_details_when_visible(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy("Specter")
    enemy.enemy_typ = "Undead"
    calls = []
    player.record_bestiary_enemy = lambda observed, enemy_type=None: calls.append((observed, enemy_type))
    manager.engine = SimpleNamespace(is_player_turn=lambda: False, show_enemy_details=lambda: True)

    manager._render_combat_frame(player, enemy, ["Attack"], 0)

    assert calls == [(enemy, "Undead")]


def test_capture_background_scroll_handling_and_action_deduplication(monkeypatch):
    manager = _make_manager(monkeypatch)

    assert manager._capture_background() == "presenter-background"
    manager.presenter.get_background_surface = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    assert str(manager._capture_background()).startswith("screen-copy")

    up = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PAGEUP)
    down = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PAGEDOWN)
    wheel_up = pygame.event.Event(pygame.MOUSEWHEEL, y=1)
    wheel_down = pygame.event.Event(pygame.MOUSEWHEEL, y=-1)
    noop = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)

    assert manager._handle_combat_log_scroll_event(up) is True
    assert manager._handle_combat_log_scroll_event(down) is True
    assert manager._handle_combat_log_scroll_event(wheel_up) is True
    assert manager._handle_combat_log_scroll_event(wheel_down) is True
    assert manager._handle_combat_log_scroll_event(noop) is False
    assert manager.combat_view.scrolled == [-1, 1, -1, 1]

    player = _make_player()
    player.is_disarmed = lambda: True
    manager.engine = SimpleNamespace(
        available_actions=["Attack", "Cast Spell", "Cast Spell", {"name": "Use Skill"}, "Use Item", ""],
        player=player,
    )
    assert manager._build_display_actions() == ["Attack", "Defend", "Pickup Weapon", "Spells", "Skills", "Items"]

    manager.game.debug_mode = True
    assert manager._build_display_actions() == [
        "Attack",
        "Defend",
        "Pickup Weapon",
        "Spells",
        "Skills",
        "Items",
        "Auto Kill",
    ]


def test_combat_damage_effect_classifies_actions_and_elements(monkeypatch):
    manager = _make_manager(monkeypatch)

    assert manager._combat_effect_kind("Attack") == "weapon"
    assert manager._combat_effect_kind("Spells") == "spell"
    assert manager._combat_effect_kind("Use Skill") == "skill"
    assert manager._combat_effect_element("Lightning Bolt", "Goblin takes damage") == "Electric"
    assert manager._combat_effect_element(None, "The target burns in holy fire") == "Fire"

    manager._show_combat_damage_effect("enemy", "Spells", "Lightning Bolt", "Goblin takes 12 electric damage.", 12)
    manager._show_combat_damage_effect("player", "Attack", None, "Hero takes 4 damage.", 4)

    assert manager.combat_view.impact_calls == [
        ("enemy", "spell", "Electric", False),
        ("float", "enemy", "-12", (235, 120, 105)),
        ("player", "weapon", None, False),
        ("float", "player", "-4", (235, 120, 105)),
    ]
    assert [call[0] for call in manager.combat_view.flash_calls] == [False, True]


def test_post_turn_and_special_effect_helpers(monkeypatch):
    manager = _make_manager(monkeypatch)
    manager.engine = SimpleNamespace(post_turn=lambda: SimpleNamespace(messages=["Line one\nLine two", "", "Last line"]))
    flushes = []
    manager._flush_result_frame = lambda player, enemy: flushes.append((player, enemy, tuple(manager.combat_view.messages)))
    manager._post_turn_processing(_make_player(), _make_enemy())
    assert manager.combat_view.messages == ["Line one", "Line two", "Last line"]
    assert flushes[-1][2] == ("Line one", "Line two", "Last line")

    manager.combat_view.messages.clear()
    flushes.clear()
    enemy = _make_enemy()
    enemy.picture = "jester.png"

    def post_turn():
        enemy.picture = "jester2.png"
        return SimpleNamespace(messages=["Palette shift!"])

    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: [])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.time.Clock", lambda: DummyClock())
    manager.dungeon_renderer = SimpleNamespace(render_dungeon_view=lambda *_args, **_kwargs: None)
    manager.player_world_dict = {}
    manager.engine = SimpleNamespace(post_turn=post_turn, is_player_turn=lambda: True)
    manager.hud = DummyHud()

    manager._post_turn_processing(_make_player(), enemy)
    assert enemy.picture == "jester2.png"
    assert len(manager.combat_view.reload_calls) >= 6
    assert any(call[0] == "enemy" for call in manager.combat_view.render_calls)
    assert manager.combat_view.messages == ["Palette shift!"]
    assert flushes[-1][2] == ("Palette shift!",)


def test_show_slot_machine_reveal_returns_three_digits_and_renders(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy()

    frame_calls = []
    event_calls = []

    def slot_events():
        event_calls.append("poll")
        if len(event_calls) == 103:
            return [pygame.event.Event(pygame.KEYUP, key=pygame.K_SPACE)]
        if len(event_calls) == 104:
            return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)]
        return []

    monkeypatch.setattr(
        "src.ui_pygame.gui.combat_manager.random.sample",
        lambda _deck, _count: ["AS", "2S", "3S"],
    )
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", slot_events)
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.draw.rect", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.font.Font", lambda *_args, **_kwargs: RecordingFont())
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.Surface", lambda size, *_args, **_kwargs: RecordingScreen(size))
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.time.Clock", lambda: DummyClock())
    monkeypatch.setattr(manager, "_render_combat_frame", lambda *args, **kwargs: frame_calls.append((args, kwargs)))
    monkeypatch.setattr(manager, "_slot_symbol_surfaces", lambda: [])

    result = manager._show_slot_machine_reveal(player, enemy)

    assert result == "AS,2S,3S"
    assert frame_calls
    assert any(
        getattr(surface, "text", "") == "Press any key or click to continue"
        for surface, _position in manager.screen.blit_calls
    )
    assert any(
        getattr(surface, "text", "") == "Straight Flush"
        for surface, _position in manager.screen.blit_calls
    )
    assert len(event_calls) == 104


def test_slot_machine_result_labels_match_core_hands():
    assert combat_manager.GUICombatManager._slot_machine_result_label("AS,2S,3S") == "Straight Flush"
    assert combat_manager.GUICombatManager._slot_machine_result_label("AS,9S,KS") == "Flush"
    assert combat_manager.GUICombatManager._slot_machine_result_label("AH,2S,3D") == "Straight"
    assert combat_manager.GUICombatManager._slot_machine_result_label("AH,AD,AC") == "3 of a Kind"
    assert combat_manager.GUICombatManager._slot_machine_result_label("AH,AD,9C") == "Pair"
    assert combat_manager.GUICombatManager._slot_machine_result_label("AH,7D,9C") == "Chance"
    assert combat_manager.GUICombatManager._slot_machine_result_label("666") == "Death"
    assert combat_manager.GUICombatManager._slot_machine_result_label("777") == "3 of a Kind"
    assert combat_manager.GUICombatManager._slot_machine_result_label("345") == "Straight"
    assert combat_manager.GUICombatManager._slot_machine_result_label("121") == "Palindrome"
    assert combat_manager.GUICombatManager._slot_machine_result_label("112") == "Pairs"
    assert combat_manager.GUICombatManager._slot_machine_result_label("246") == "Evens"
    assert combat_manager.GUICombatManager._slot_machine_result_label("135") == "Odds"
    assert combat_manager.GUICombatManager._slot_machine_result_label("148") == "Chance"


def test_slot_machine_symbol_atlas_slices_ten_reel_images(monkeypatch):
    manager = _make_manager(monkeypatch)
    atlas = pygame.Surface((500, 200), pygame.SRCALPHA)
    atlas.fill((0, 0, 0, 0))
    pygame.draw.rect(atlas, (255, 0, 0, 255), pygame.Rect(12, 14, 30, 40))
    loads = []

    monkeypatch.setattr(
        "src.ui_pygame.gui.combat_manager.pygame.image.load",
        lambda path: loads.append(path) or atlas,
    )

    symbols = manager._slot_symbol_surfaces()

    assert len(symbols) == 10
    assert symbols[0].get_size() == (42, 52)
    assert all(symbol.get_size() == (100, 100) for symbol in symbols[1:])
    assert loads == [str(combat_manager.SLOT_SYMBOL_ATLAS)]
    assert manager._slot_symbol_surfaces() is symbols


def test_slot_machine_symbol_atlas_slices_full_deck(monkeypatch):
    manager = _make_manager(monkeypatch)
    atlas = pygame.Surface((1300, 400), pygame.SRCALPHA)
    atlas.fill((0, 0, 0, 0))
    pygame.draw.rect(atlas, (255, 0, 0, 255), pygame.Rect(12, 14, 30, 40))

    monkeypatch.setattr(
        "src.ui_pygame.gui.combat_manager.pygame.image.load",
        lambda _path: atlas,
    )

    symbols = manager._slot_symbol_surfaces()

    assert len(symbols) == 52
    assert symbols[0].get_size() == (42, 52)


def test_waitress_transition_and_preservation_helpers(monkeypatch):
    manager = _make_manager(monkeypatch)
    popup_calls = []

    class FakeNightHag2:
        pass

    class FakePopup:
        def __init__(self, presenter, message, show_buttons=False):
            self.message = message
            self.show_buttons = show_buttons

        def show(self, **kwargs):
            popup_calls.append((self.message, kwargs))
    monkeypatch.setattr(combat_manager.enemies, "NightHag2", FakeNightHag2)
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.ConfirmationPopup", FakePopup)

    enemy = FakeNightHag2()
    enemy.name = "Mad Waitress"
    enemy.health = SimpleNamespace(current=5, max=100)
    enemy.is_alive = lambda: enemy.health.current > 0

    manager._check_enemy_form_change(_make_player(), enemy)

    assert enemy._form_changed is True
    assert enemy.name == "Waitress"
    assert enemy.health.current == 0
    assert manager.combat_view.reload_calls == [enemy]
    assert manager.combat_view.enemy_deaths == [enemy]
    assert any("turns her weapon on herself" in message for message in manager.combat_view.messages)
    assert popup_calls
    assert popup_calls[0][1].get("flush_events") is True
    assert popup_calls[0][1].get("require_key_release") is True

    enemy2 = FakeNightHag2()
    enemy2._form_changed = False
    enemy2.health = SimpleNamespace(current=0, max=100)
    manager._preserve_waitress_for_transition(enemy2)
    assert enemy2.health.current == 1


def test_execute_action_handles_suppression_and_slot_machine_skill(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy()

    player.abilities_suppressed = lambda: True
    player.anti_magic_active = True
    assert manager._execute_action("Spells", player, enemy) is None
    assert "cannot cast spells because of the anti-magic field" in manager.combat_view.messages[-1]

    manager.combat_view.messages.clear()
    player.abilities_suppressed = lambda: False
    player.spellbook["Skills"]["Slot Machine"] = SimpleNamespace(name="Slot Machine")
    manager._select_skill = lambda _player, _enemy: "Slot Machine"
    manager._show_slot_machine_reveal = lambda _player, _enemy: "777"
    frame_calls = []
    manager._render_combat_frame = lambda *args, **kwargs: frame_calls.append((args, kwargs))
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.display.flip", lambda: None)

    def execute_action(action, choice=None, slot_machine_callback=None):
        assert frame_calls
        assert action == "Use Skill"
        assert choice == "Slot Machine"
        assert slot_machine_callback and slot_machine_callback(player, enemy) == "777"
        enemy.health.current = 11
        enemy.name = "Goblin King"
        return SimpleNamespace(message="Big hit!\nJackpot!", fled=False)

    manager.engine = SimpleNamespace(execute_action=execute_action)
    result = manager._execute_action("Skills", player, enemy)

    assert result == "action_taken"
    assert manager.combat_view.messages[-2:] == ["Big hit!", "Jackpot!"]
    assert manager.combat_view.enemy_damage_calls == [enemy]
    assert manager.combat_view.flash_calls[-1][0] is False
    assert manager.combat_view.reload_calls[-1] == enemy
    assert frame_calls[-1][0] == (player, enemy, [], -1)


def test_execute_spell_flushes_result_log_before_damage_effect(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy(hp=(20, 20))
    order = []

    manager._select_spell = lambda _player, _enemy: "Firebolt"
    manager._flush_result_frame = lambda _player, _enemy: order.append("flush")
    manager._show_combat_damage_effect = lambda *_args, **_kwargs: order.append("effect")
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.display.flip", lambda: None)

    def execute_action(action, choice=None, slot_machine_callback=None):
        assert action == "Cast Spell"
        assert choice == "Firebolt"
        enemy.health.current = 7
        return SimpleNamespace(message="Hero damages Goblin for 13 hit points.", fled=False)

    manager.engine = SimpleNamespace(execute_action=execute_action)

    assert manager._execute_action("Spells", player, enemy) == "action_taken"
    assert order == ["flush", "effect", "flush"]
    assert manager.combat_view.messages[-1] == "Hero damages Goblin for 13 hit points."


def test_debug_auto_kill_action_requires_debug_mode(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy()

    manager.game.debug_mode = False
    assert manager._execute_action("Auto Kill", player, enemy) is None
    assert enemy.health.current == 20
    assert manager.combat_view.messages[-1] == "Auto Kill is only available in debug mode."

    manager.game.debug_mode = True
    assert manager._execute_action("Auto Kill", player, enemy) == "action_taken"
    assert enemy.health.current == 0
    assert manager.combat_view.messages[-1] == "Debug: Goblin defeated."
    assert manager.combat_view.enemy_damage_calls == [enemy]
    assert manager.combat_view.flash_calls[-1][0] is False


def test_handle_combat_end_victory_defeat_and_flee_paths(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy()
    popup_messages = []
    popup_kwargs = []

    class FakePopup:
        def __init__(self, presenter, message, show_buttons=False):
            popup_messages.append(message)

        def show(self, **kwargs):
            popup_messages.append("shown")
            popup_kwargs.append(kwargs)

    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.ConfirmationPopup", FakePopup)
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: [])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.time.Clock", lambda: DummyClock())
    render_calls = []
    monkeypatch.setattr(manager, "_render_combat_frame", lambda *args, **kwargs: render_calls.append((args, kwargs)))
    monkeypatch.setattr(manager, "_pause_with_events", lambda _ms: None)

    manager.engine = SimpleNamespace(
        flee=False,
        end_battle=lambda: SimpleNamespace(result="victory", message="Gold +5\nQuest updated", level_up=True),
    )
    assert manager._handle_combat_end(player, enemy, fled=False) is True
    assert popup_messages[0].startswith("Victory! Goblin defeated!")
    assert manager.level_up_screen.calls == [(player, manager.game)]
    assert manager.combat_view.reset_calls == 1
    assert manager._combat_background is None
    assert popup_kwargs[0].get("flush_events") is True
    assert popup_kwargs[0].get("require_key_release") is True

    popup_messages.clear()
    manager.combat_view.reset_calls = 0
    render_calls.clear()
    manager.engine = SimpleNamespace(
        flee=False,
        end_battle=lambda: SimpleNamespace(result="defeat", message="You lost", level_up=False),
    )
    assert manager._handle_combat_end(player, enemy, fled=False) is False
    assert popup_messages[0] == "You have been defeated!"
    assert manager.combat_view.reset_calls == 1
    assert popup_kwargs[0].get("flush_events") is True
    assert popup_kwargs[0].get("require_key_release") is True
    assert render_calls == []

    popup_messages.clear()
    manager.combat_view.reset_calls = 0
    manager.engine = SimpleNamespace(
        flee=False,
        end_battle=lambda: SimpleNamespace(result="flee", message="Escaped", level_up=False),
    )
    assert manager._handle_combat_end(player, enemy, fled=True) is False
    assert manager.engine.flee is True
    assert popup_messages[0] == "You fled from combat!"


def test_jester_victory_runs_death_fade_before_dungeon_end_event(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy("Jester", hp=(0, 20))

    class JesterBossRoom:
        pass

    class FakePopup:
        def __init__(self, _presenter, message, show_buttons=False):
            popup_messages.append(message)

        def show(self, **_kwargs):
            popup_messages.append("shown")

    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.ConfirmationPopup", FakePopup)
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: [])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.time.Clock", lambda: DummyClock())
    render_calls = []
    monkeypatch.setattr(manager, "_render_combat_frame", lambda *args, **kwargs: render_calls.append((args, kwargs)))
    monkeypatch.setattr(manager, "_pause_with_events", lambda _ms: None)
    popup_messages = []

    manager.current_tile = JesterBossRoom()
    manager.engine = SimpleNamespace(
        flee=False,
        end_battle=lambda: SimpleNamespace(result="victory", message="Gold +5", level_up=False),
    )

    assert manager._handle_combat_end(player, enemy, fled=False) is True
    assert popup_messages[0].startswith("Victory! Jester defeated!")
    assert "Gold +5" in popup_messages[0]
    assert len(render_calls) == 71
    assert manager.combat_view.reset_calls == 1
    assert manager._combat_background is None


def test_debug_battle_log_persistence_is_opt_in_and_sanitized(monkeypatch):
    manager = _make_manager(monkeypatch)
    manager.game.debug_mode = False
    manager.presenter.debug_mode = False

    exported = []
    manager.logger = SimpleNamespace(
        metadata={
            "player": {"name": "Ada Hero"},
            "enemy": {"name": "Slime/Blob"},
        },
        export_json_file=lambda path: exported.append(path) or path,
    )

    assert manager._persist_debug_battle_log("victory") is None
    assert exported == []

    manager.game.debug_mode = True
    output_path = manager._persist_debug_battle_log("victory")

    assert output_path is exported[0]
    assert output_path.parent.parts[-2:] == ("debug_logs", "battles")
    assert output_path.name.endswith("-ada-hero-vs-slime-blob-victory.json")


def test_debug_battle_log_persistence_ignores_export_errors(monkeypatch):
    manager = _make_manager(monkeypatch)
    manager.game.debug_mode = True
    manager.logger = SimpleNamespace(
        metadata={},
        export_json_file=lambda _path: (_ for _ in ()).throw(OSError("disk full")),
    )

    assert manager._persist_debug_battle_log("defeat") is None


def test_select_item_spell_and_skill_cover_empty_cancel_and_selection_paths(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy()

    pauses = []
    manager._pause_with_events = lambda ms: pauses.append(ms)
    manager._render_combat_frame = lambda *args, **kwargs: None
    menu_calls = []
    manager._render_selection_menu = lambda title, options, selected, scroll_offset=0: menu_calls.append(
        (title, tuple(options), selected, scroll_offset)
    )
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.display.flip", lambda: None)

    assert manager._select_item(player, enemy) is None
    assert manager.combat_view.messages[-1] == "No usable items!"
    assert pauses[-1] == 500

    player.inventory = {
        "Potion": [SimpleNamespace(name="Potion", subtyp="Health") for _ in range(2)],
        "Bomb": [SimpleNamespace(name="Bomb", subtyp="Throwing")],
        "Scroll": [SimpleNamespace(name="Scroll of Ice", subtyp="Scroll")],
    }
    pressed_states = iter([[1], [], [], []])
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: next(pressed_states, []))
    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_DOWN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: next(event_batches, []))
    selected_item = manager._select_item(player, enemy)
    assert selected_item.name == "Scroll of Ice"
    assert menu_calls[-2][1] == ("Potion (2)", "Scroll (1)")
    assert menu_calls[-1][2] == 1

    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYUP, key=pygame.K_ESCAPE)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_ESCAPE)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: next(event_batches, []))
    assert manager._select_item(player, enemy) is None

    player.spellbook["Spells"] = {}
    assert manager._select_spell(player, enemy) is None
    assert manager.combat_view.messages[-1] == "No spells learned!"

    player.spellbook["Spells"] = {
        "Passive Aura": SimpleNamespace(cost=0, passive=True),
        "Fireball": SimpleNamespace(cost=4, passive=False),
        "Ice": SimpleNamespace(cost=2, passive=False),
    }
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: [])
    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_DOWN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: next(event_batches, []))
    assert manager._select_spell(player, enemy) == "Ice"
    assert any(call[0] == "Select Spell" for call in menu_calls)

    player.spellbook["Skills"] = {}
    assert manager._select_skill(player, enemy) is None
    assert manager.combat_view.messages[-1] == "No skills learned!"

    player.equipment = {"OffHand": SimpleNamespace(subtyp="None")}
    player.spellbook["Skills"] = {
        "Shield Slam": SimpleNamespace(name="Shield Slam", cost=2, passive=False),
    }
    assert manager._select_skill(player, enemy) is None
    assert manager.combat_view.messages[-1] == "No skills learned!"

    player.equipment = {"OffHand": SimpleNamespace(subtyp="Shield")}
    event_batches = iter([[SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)]])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: next(event_batches, []))
    assert manager._select_skill(player, enemy) == "Shield Slam"
    assert menu_calls[-1][1] == ("Shield Slam (MP: 2)",)

    player.is_disarmed = lambda: True
    player.spellbook["Skills"] = {
        "Piercing Strike": SimpleNamespace(name="Piercing Strike", cost=5, passive=False, weapon=True),
        "Smoke Screen": SimpleNamespace(name="Smoke Screen", cost=1, passive=False, weapon=False),
    }
    event_batches = iter([[SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)]])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: next(event_batches, []))
    assert manager._select_skill(player, enemy) == "Smoke Screen"
    assert menu_calls[-1][1] == ("Smoke Screen (MP: 1)",)
    player.is_disarmed = lambda: False

    player.spellbook["Skills"] = {
        "Passive Stance": SimpleNamespace(cost=0, passive=True),
        "Slash": SimpleNamespace(cost=1, passive=False),
        "Jump": SimpleNamespace(cost=3, passive=False),
    }
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: [])
    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_PAGEDOWN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: next(event_batches, []))
    assert manager._select_skill(player, enemy) == "Jump"


def test_select_totem_aspect_ignores_stale_confirm_until_key_release(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy()
    manager._render_combat_frame = lambda *args, **kwargs: None
    menu_calls = []
    manager._render_selection_menu = lambda title, options, selected, scroll_offset=0: menu_calls.append(
        (title, tuple(options), selected, scroll_offset)
    )
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.display.flip", lambda: None)
    clear_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.clear", lambda: clear_calls.append(True))
    pressed_states = iter([[1], [], [], []])
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: next(pressed_states, []))
    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_DOWN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: next(event_batches, []))
    totem = SimpleNamespace(
        active_aspect="Wolf",
        get_unlocked_aspects=lambda _player: ["Wolf", "Bear"],
    )

    assert manager._select_totem_aspect(player, enemy, totem) == "Bear"
    assert clear_calls == [True]
    assert menu_calls[0][1] == ("Wolf (Active)", "Bear")


def test_render_selection_menu_refresh_background_and_pause_helpers(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy()

    large_font = RecordingFont()
    medium_font = RecordingFont()
    small_font = RecordingFont()
    fonts = iter([large_font, medium_font, small_font])

    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.font.Font", lambda *_args, **_kwargs: next(fonts))
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.Surface", lambda size, *_args, **_kwargs: DummySurface(size))
    draw_calls = []
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.draw.rect", lambda *_args, **_kwargs: draw_calls.append((_args, _kwargs)))
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.display.flip", lambda: None)

    long_options = [f"Option {index} with very long descriptive text that should truncate" for index in range(15)]
    manager._render_selection_menu("Choose Action", long_options, selected=13, scroll_offset=99)

    assert "Choose Action" in large_font.render_calls
    fitted_option = next(text for text in medium_font.render_calls if text.startswith("13. Option 12"))
    assert fitted_option.endswith("...")
    assert medium_font.size(fitted_option)[0] <= 462
    assert "Up/Down or W/S: Navigate | PgUp/PgDn: Scroll | Enter: Select | Esc: Cancel" in small_font.render_calls
    assert draw_calls

    manager._combat_background = None
    manager._render_combat_frame = lambda *args, **kwargs: manager.screen.blit("combat-frame", (1, 2))
    manager._refresh_combat_background(player, enemy)
    assert str(manager._combat_background).startswith("screen-copy-")

    scroll_events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_PAGEUP), pygame.event.Event(pygame.QUIT)]
    event_batches = iter([[scroll_events[0]], []])
    clock = DummyClock(frame_ms=300)
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: next(event_batches, []))
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.time.Clock", lambda: clock)
    manager._pause_with_events(500)
    assert manager.combat_view.scrolled[-1] == -1
    assert clock.ticks == [60, 60]


def test_start_combat_handles_initiative_and_sanctuary_escape(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy()
    tile = SimpleNamespace()

    player.world_dict = {"z": {}}
    player.encumbered = True
    player.in_town = lambda: False

    end_calls = []
    fake_engine = SimpleNamespace(
        available_actions=["Attack"],
        start_battle=lambda: (enemy, player),
        battle_continues=lambda: True,
        is_player_turn=lambda: True,
        swap_turns=lambda: end_calls.append("swap"),
        player=player,
    )

    monkeypatch.setattr(combat_manager, "BattleEngine", lambda **kwargs: fake_engine)
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: [])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.time.Clock", lambda: DummyClock())
    monkeypatch.setattr(manager, "_render_combat_frame", lambda *args, **kwargs: None)
    monkeypatch.setattr(manager, "_player_turn", lambda _player, _enemy: "flee")
    monkeypatch.setattr(manager, "_handle_combat_end", lambda _player, _enemy, fled: end_calls.append(("end", fled)) or False)

    result = manager.start_combat(player, enemy, tile)

    assert result is False
    assert manager.current_tile is tile
    assert manager.player_world_dict == player.world_dict
    assert "Combat started with Goblin!" in manager.combat_view.messages
    assert "You are ENCUMBERED! Enemy strikes first!" in manager.combat_view.messages
    assert "Goblin has the initiative!" in manager.combat_view.messages
    assert end_calls == [("end", True)]

    sanctuary_manager = _make_manager(monkeypatch)
    sanctuary_player = _make_player()
    sanctuary_player.in_town = lambda: True
    sanctuary_player.effects = lambda end=False: end_calls.append(("effects", end))
    sanctuary_manager.logger = SimpleNamespace(end_battle=lambda **kwargs: end_calls.append(("logger", kwargs)))
    sanctuary_manager.engine = SimpleNamespace(flee=False)
    sanctuary_manager._combat_background = "cached"
    sanctuary_manager.combat_view.reset_calls = 0

    assert sanctuary_manager._handle_combat_end(sanctuary_player, enemy, fled=False) is False
    assert ("effects", True) in end_calls
    assert any(call[0] == "logger" and call[1]["result"] == "Escaped" for call in end_calls if isinstance(call, tuple))
    assert sanctuary_manager.combat_view.reset_calls == 1
    assert sanctuary_manager._combat_background is None


def test_render_combat_frame_waits_for_initiative_before_turn_label(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy()

    turn_calls = []
    manager.engine = SimpleNamespace(attacker=None, is_player_turn=lambda: True)
    manager.dungeon_renderer = None
    manager.player_world_dict = None
    manager.combat_view.render_enemy_in_dungeon = lambda *_args, **_kwargs: None
    manager.combat_view.render_combat_overlay = lambda *_args, **kwargs: turn_calls.append(kwargs.get("current_turn"))
    manager.hud.render_hud = lambda *_args, **_kwargs: None

    manager._render_combat_frame(player, enemy, [], -1)

    assert turn_calls == [None]


def test_player_turn_covers_preturn_forced_actions_and_grid_selection(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy()

    manager._render_combat_frame = lambda *args, **kwargs: None
    flushed_messages = []
    manager._flush_result_frame = lambda *_args: flushed_messages.append(tuple(manager.combat_view.messages))
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.display.flip", lambda: None)

    manager.engine = SimpleNamespace(
        pre_turn=lambda: SimpleNamespace(effects_text="Poison ticks", died_from_effects=True, can_act=True, inactive_reason=""),
    )
    assert manager._player_turn(player, enemy) is True
    assert manager.combat_view.messages[-1] == "Poison ticks"
    assert flushed_messages[-1] == ("Poison ticks",)

    manager.engine = SimpleNamespace(
        pre_turn=lambda: SimpleNamespace(effects_text="", died_from_effects=False, can_act=False, inactive_reason="Asleep"),
    )
    assert manager._player_turn(player, enemy) is True
    assert manager.combat_view.messages[-1] == "Asleep"
    assert flushed_messages[-1][-1] == "Asleep"

    forced = SimpleNamespace(action="Cancelled", cancel_message="Jump failed", choice=None)
    manager.engine = SimpleNamespace(
        pre_turn=lambda: SimpleNamespace(effects_text="", died_from_effects=False, can_act=True, inactive_reason=""),
        get_forced_action=lambda: forced,
    )
    assert manager._player_turn(player, enemy) is True
    assert manager.combat_view.messages[-1] == "Jump failed"

    enemy.health.current = 12
    forced = SimpleNamespace(action="Attack", cancel_message="", choice=None)
    manager.engine = SimpleNamespace(
        pre_turn=lambda: SimpleNamespace(effects_text="", died_from_effects=False, can_act=True, inactive_reason=""),
        get_forced_action=lambda: forced,
        execute_action=lambda action, choice=None: SimpleNamespace(message="Hit hard", fled=False),
        companion_turn=lambda: None,
    )
    assert manager._player_turn(player, enemy) is True
    assert any("BERSERKED" in message for message in manager.combat_view.messages)

    actions = []
    manager.available_actions = ["Attack", "Defend", "Items", "Spells"]
    manager.engine = SimpleNamespace(
        pre_turn=lambda: SimpleNamespace(effects_text="", died_from_effects=False, can_act=True, inactive_reason=""),
        get_forced_action=lambda: None,
        companion_turn=lambda: "Fairy assists",
    )
    manager._execute_action = lambda action, _player, _enemy: actions.append(action) or "action_taken"
    pressed_states = iter([[1], [], [], []])
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: next(pressed_states, []))
    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RIGHT)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: next(event_batches, []))
    assert manager._player_turn(player, enemy) is True
    assert actions == ["Defend"]
    assert manager.combat_view.messages[-1] == "Fairy assists"

    manager.available_actions = ["Attack", "Defend", "Items"]
    actions.clear()
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: [])
    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_3)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: next(event_batches, []))
    assert manager._player_turn(player, enemy) is True
    assert actions == ["Items"]


def test_player_turn_accepts_first_fresh_key_after_guard_pumps_state(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy()

    manager._render_combat_frame = lambda *args, **kwargs: None
    flushed_messages = []
    manager._flush_result_frame = lambda *_args: flushed_messages.append(tuple(manager.combat_view.messages))
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.display.flip", lambda: None)

    actions = []
    manager.available_actions = ["Attack", "Defend", "Items"]
    manager.engine = SimpleNamespace(
        pre_turn=lambda: SimpleNamespace(effects_text="", died_from_effects=False, can_act=True, inactive_reason=""),
        get_forced_action=lambda: None,
        companion_turn=lambda: None,
    )
    manager._execute_action = lambda action, _player, _enemy: actions.append(action) or "action_taken"

    key_held = {"value": True}

    def fake_pump():
        key_held["value"] = False

    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.event.pump", fake_pump)
    monkeypatch.setattr(
        "src.ui_pygame.gui.input_guards.pygame.key.get_pressed",
        lambda: [1] if key_held["value"] else [],
    )
    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RIGHT)],
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: next(event_batches, []))

    assert manager._player_turn(player, enemy) is True
    assert actions == ["Defend"]


def test_player_turn_refreshes_actions_after_silence_expires(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy()

    manager._render_combat_frame = lambda *args, **kwargs: None
    manager._flush_result_frame = lambda *_args: None
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.input_guards.pygame.key.get_pressed", lambda: [])

    actions = []
    manager.available_actions = ["Attack", "Defend", "Items"]
    manager.engine = SimpleNamespace(
        available_actions=["Attack", "Cast Spell", "Use Skill", "Use Item"],
        player=player,
        pre_turn=lambda: SimpleNamespace(
            effects_text=f"{player.name} can speak again.",
            died_from_effects=False,
            can_act=True,
            inactive_reason="",
        ),
        get_forced_action=lambda: None,
        companion_turn=lambda: None,
    )
    manager._execute_action = lambda action, _player, _enemy: actions.append(action) or "action_taken"
    event_batches = iter([
        [SimpleNamespace(type=pygame.KEYDOWN, key=pygame.K_3)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: next(event_batches, []))

    assert manager._player_turn(player, enemy) is True
    assert actions == ["Spells"]
    assert manager.available_actions == ["Attack", "Defend", "Spells", "Skills", "Items"]


def test_enemy_turn_covers_skip_forced_nothing_and_damage_paths(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy()

    manager._render_combat_frame = lambda *args, **kwargs: None
    flushed_messages = []
    manager._flush_result_frame = lambda *_args: flushed_messages.append(tuple(manager.combat_view.messages))
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: [])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.time.Clock", lambda: DummyClock())
    player.status_effects = {"Stun": SimpleNamespace(active=False)}

    manager.engine = SimpleNamespace(
        pre_turn=lambda: SimpleNamespace(effects_text="Bleeding", died_from_effects=True, can_act=True, inactive_reason=""),
    )
    assert manager._enemy_turn(player, enemy) is None
    assert manager.combat_view.messages[-1] == "Bleeding"
    assert flushed_messages[-1] == ("Bleeding",)

    manager.engine = SimpleNamespace(
        pre_turn=lambda: SimpleNamespace(effects_text="", died_from_effects=False, can_act=False, inactive_reason="Stunned"),
    )
    assert manager._enemy_turn(player, enemy) is None
    assert manager.combat_view.messages[-1] == "Stunned"
    assert flushed_messages[-1][-1] == "Stunned"

    manager.engine = SimpleNamespace(
        pre_turn=lambda: SimpleNamespace(effects_text="", died_from_effects=False, can_act=True, inactive_reason=""),
        get_forced_action=lambda: SimpleNamespace(action="Cancelled", cancel_message="Charge broken", choice=None),
    )
    assert manager._enemy_turn(player, enemy) is None
    assert manager.combat_view.messages[-1] == "Charge broken"

    enemy.name = "Shifter"
    enemy.spellbook = {"Skills": {}}
    player.health.current = 42
    manager.engine = SimpleNamespace(
        pre_turn=lambda: SimpleNamespace(effects_text="", died_from_effects=False, can_act=True, inactive_reason=""),
        get_forced_action=lambda: None,
        get_enemy_action=lambda: ("Nothing", None),
    )
    assert manager._enemy_turn(player, enemy) is None
    assert manager.combat_view.messages[-1] == "Shifter does nothing."

    enemy.name = "Mage"
    enemy.spellbook = {"Skills": {}}
    player.health.current = 30

    def execute_action(action, choice=None, slot_machine_callback=None):
        player.health.current = 18
        player.status_effects["Stun"].active = True
        enemy.name = "Mage Form"
        return SimpleNamespace(message="Dark blast", fled=False)

    manager.engine = SimpleNamespace(
        pre_turn=lambda: SimpleNamespace(effects_text="", died_from_effects=False, can_act=True, inactive_reason=""),
        get_forced_action=lambda: None,
        get_enemy_action=lambda: ("Use Skill", "Hex"),
        show_enemy_details=lambda: True,
        execute_action=execute_action,
    )
    ability_calls = []
    player.record_bestiary_ability = lambda observed, ability_name: ability_calls.append((observed, ability_name))
    assert manager._enemy_turn(player, enemy) is None
    assert ability_calls == [(enemy, "Hex")]
    assert "Dark blast" in manager.combat_view.messages
    assert manager.combat_view.messages[-1] == "Hero is stunned and cannot act."
    assert manager.combat_view.reload_calls[-1] == enemy
    assert manager.combat_view.flash_calls[-1][0] is True


def test_enemy_smoke_screen_flee_keeps_enemy_hidden_for_end_transition(monkeypatch):
    manager = _make_manager(monkeypatch)
    player = _make_player()
    enemy = _make_enemy("Bandit")
    enemy.spellbook = {"Skills": {"Smoke Screen": SimpleNamespace(name="Smoke Screen")}}
    player.status_effects = {"Stun": SimpleNamespace(active=False)}
    smoke_visuals = []

    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.display.flip", lambda: None)
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.event.get", lambda: [])
    monkeypatch.setattr("src.ui_pygame.gui.combat_manager.pygame.time.Clock", lambda: DummyClock())
    manager._render_combat_frame = lambda *args, **kwargs: None
    manager._flush_result_frame = lambda *_args: None

    def play_smoke_screen_visual(_player, _enemy, target):
        smoke_visuals.append((target, manager.combat_view.hide_enemy_calls))

    manager._play_smoke_screen_visual = play_smoke_screen_visual

    def execute_smoke_screen(action, choice=None, slot_machine_callback=None):
        manager.engine.flee = True
        return SimpleNamespace(
            message="Bandit vanishes in smoke.",
            fled=False,
        )

    manager.engine = SimpleNamespace(
        flee=False,
        pre_turn=lambda: SimpleNamespace(effects_text="", died_from_effects=False, can_act=True, inactive_reason=""),
        get_forced_action=lambda: None,
        get_enemy_action=lambda: ("Use Skill", "Smoke Screen"),
        execute_action=execute_smoke_screen,
    )

    assert manager._enemy_turn(player, enemy) == "flee"
    assert smoke_visuals == [("enemy", 1)]
    assert manager.combat_view.hide_enemy_calls == 1
