#!/usr/bin/env python3
"""Focused coverage for curses battle-manager helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.ui_curses import battle


class FakeBattleUI:
    def __init__(self, actions=None):
        self.actions = list(actions or [])
        self.calls = []

    def draw_enemy(self, enemy, vision=False):
        self.calls.append(("enemy", enemy.name, vision))

    def draw_options(self, options):
        self.calls.append(("options", tuple(options)))

    def draw_char(self, char=None):
        self.calls.append(("char", getattr(char, "name", None)))

    def refresh_all(self):
        self.calls.append(("refresh",))

    def navigate_menu(self):
        return self.actions.pop(0)


class FakeBattlePopup:
    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.calls = []

    def update_options(self, action, tile=None, options=None):
        self.calls.append((action, tile, tuple(options) if options else None))

    def navigate_popup(self):
        return self.responses.pop(0)


class FakeTextBox:
    def __init__(self):
        self.print_calls = []
        self.clear_calls = 0

    def print_text_in_rectangle(self, text):
        self.print_calls.append(text)

    def clear_rectangle(self):
        self.clear_calls += 1


def _make_manager(monkeypatch):
    player = SimpleNamespace(
        name="Hero",
        location_x=1,
        location_y=2,
        location_z=0,
        world_dict={(1, 2, 0): "tile"},
        end_combat=lambda *args, **kwargs: end_calls.append((args, kwargs)),
        is_alive=lambda: True,
    )
    enemy = SimpleNamespace(name="Goblin", is_alive=lambda: False)
    game = SimpleNamespace(player_char=player, stdscr=SimpleNamespace(getch=lambda: getch_calls.append(True)))
    ui = FakeBattleUI()
    popup = FakeBattlePopup()
    textbox = FakeTextBox()
    end_calls = []
    getch_calls = []

    fake_engine = SimpleNamespace(
        player=player,
        enemy=enemy,
        tile="tile",
        logger=SimpleNamespace(end_battle=lambda **kwargs: logger_calls.append(kwargs)),
        flee=False,
        boss=False,
        available_actions=["Attack", "Cast Spell"],
        summon_active=False,
        summon=None,
        attacker=player,
        defender=enemy,
        charging_ability=None,
        show_enemy_details=lambda: True,
        start_battle=lambda: (player, enemy),
        battle_continues=lambda: continue_flags.pop(0),
        swap_turns=lambda: swaps.append(True),
        post_turn=lambda: SimpleNamespace(messages=["Buff fades", ""]),
        pre_turn=lambda: SimpleNamespace(effects_text="", died_from_effects=False, can_act=True, inactive_reason=""),
        get_forced_action=lambda: None,
        is_player_turn=lambda: True,
        get_enemy_action=lambda: ("Attack", None),
        execute_action=lambda action, choice=None: SimpleNamespace(message=f"{action}:{choice}", summon_started=False, summon_recalled=False),
        companion_turn=lambda: "Pet helps",
    )
    logger_calls = []
    continue_flags = [True, False]
    swaps = []

    monkeypatch.setattr(battle, "BattleEngine", lambda **kwargs: fake_engine)

    manager = battle.BattleManager(
        game,
        enemy,
        logger=None,
        battle_ui=ui,
        battle_popup=popup,
        textbox=textbox,
    )
    return manager, fake_engine, ui, popup, textbox, end_calls, getch_calls, logger_calls, swaps


def test_battle_manager_render_print_and_execute_flow(monkeypatch):
    manager, engine, ui, popup, textbox, _end_calls, _getch_calls, _logger_calls, swaps = _make_manager(monkeypatch)

    manager.render_screen()
    assert ("enemy", "Goblin", True) in ui.calls
    assert ("options", ("Attack", "Cast Spell")) in ui.calls
    assert ("char", None) in ui.calls

    assert manager._filter_status_lines("Hero is affected by poison\nRegular line\n") == "Regular line"
    manager.print_text("Hero is affected by poison\nShown line")
    assert textbox.print_calls == ["Shown line"]
    assert textbox.clear_calls == 1

    engine.post_turn = lambda: SimpleNamespace(messages=["First line\nSecond line"])
    manager.after_turn()
    assert textbox.print_calls[-2:] == ["Shown line", "First line\nSecond line"]

    engine.execute_action = lambda action, choice=None: SimpleNamespace(
        message=f"{action}:{choice}",
        summon_started=action == "Summon",
        summon_recalled=action == "Recall",
    )
    manager.execute_action("Summon", choice="Patagon")
    assert manager.summon_active is True
    manager.execute_action("Recall")
    assert manager.summon_active is False

    manager.companion_turn()
    assert textbox.print_calls[-1] == "Pet helps"

    engine.battle_continues = lambda: True
    assert manager.battle_continues() is True
    engine.battle_continues = lambda: False
    assert manager.battle_continues() is False

    called = []
    manager.before_turn = lambda: called.append("before")
    manager.take_turn = lambda: called.append("take")
    manager.after_turn = lambda: called.append("after")
    manager.process_turn()
    assert called == ["before", "take", "after"]
    assert swaps == [True]


def test_battle_manager_take_turn_and_player_input(monkeypatch):
    manager, engine, ui, popup, textbox, *_rest = _make_manager(monkeypatch)

    engine.pre_turn = lambda: SimpleNamespace(effects_text="Bleed", died_from_effects=True, can_act=True, inactive_reason="")
    manager.take_turn()
    assert textbox.print_calls[-1] == "Bleed"

    engine.pre_turn = lambda: SimpleNamespace(effects_text="", died_from_effects=False, can_act=False, inactive_reason="Stunned")
    manager.take_turn()
    assert textbox.print_calls[-2:] == ["Stunned", "Pet helps"]

    engine.pre_turn = lambda: SimpleNamespace(effects_text="", died_from_effects=False, can_act=True, inactive_reason="")
    engine.get_forced_action = lambda: SimpleNamespace(action="Cancelled", cancel_message="Jump cancelled", choice=None)
    manager.take_turn()
    assert textbox.print_calls[-2:] == ["Jump cancelled", "Pet helps"]

    forced_actions = []
    manager.execute_action = lambda action, choice=None, result=None: forced_actions.append((action, choice))
    engine.get_forced_action = lambda: SimpleNamespace(action="Attack", cancel_message="", choice="Target")
    manager.take_turn()
    assert forced_actions[-1] == ("Attack", "Target")

    engine.get_forced_action = lambda: None
    engine.is_player_turn = lambda: True
    manager.execute_action = lambda action, choice=None, result=None: forced_actions.append((action, choice))
    ui.actions = ["Cast Spell"]
    popup.responses = ["Fireball  3"]
    assert manager._get_player_input() == ("Cast Spell", "Fireball")

    ui.actions = ["Summon"]
    popup.responses = ["Wolf"]
    engine.attacker.summons = {"Wolf": object()}
    assert manager._get_player_input() == ("Summon", "Wolf")

    transformed = []
    engine.attacker.transform = lambda back=False: transformed.append(back) or ("back" if back else "forward")
    ui.actions = ["Untransform", "Transform", "Attack"]
    assert manager._get_player_input() == ("Attack", None)
    assert transformed == [True, False]

    engine.is_player_turn = lambda: False
    engine.get_enemy_action = lambda: ("Use Skill", "Hex")
    manager.take_turn()
    assert forced_actions[-1] == ("Use Skill", "Hex")
    assert textbox.print_calls[-1] == "Pet helps"


def test_battle_manager_execute_battle_and_end_battle(monkeypatch):
    manager, engine, _ui, _popup, _textbox, end_calls, getch_calls, logger_calls, _swaps = _make_manager(monkeypatch)

    engine.start_battle = lambda: ("first", "second")
    flags = iter([True, False])
    manager.battle_continues = lambda: next(flags)
    processed = []
    manager.process_turn = lambda: processed.append(True)
    ended = []
    manager.end_battle = lambda: ended.append(True)
    manager.flee = True
    assert manager.execute_battle() is True
    assert processed == [True]
    assert ended == [True]

    events = []
    monkeypatch.setattr("src.core.events.event_bus.get_event_bus", lambda: SimpleNamespace(emit=lambda event: events.append(event)))
    monkeypatch.setattr("src.core.events.event_bus.create_combat_event", lambda event_type, **kwargs: (event_type, kwargs))
    monkeypatch.setattr("src.core.events.event_bus.EventType", SimpleNamespace(COMBAT_END="combat_end"))

    manager = battle.BattleManager.__new__(battle.BattleManager)
    player = SimpleNamespace(
        name="Hero",
        is_alive=lambda: True,
        end_combat=lambda *args, **kwargs: end_calls.append((args, kwargs)),
    )
    enemy = SimpleNamespace(name="Dragon", is_alive=lambda: False)
    tile = SimpleNamespace(enemy="present", defeated=False)
    manager.engine = SimpleNamespace(
        player=player,
        enemy=enemy,
        tile=tile,
        logger=SimpleNamespace(end_battle=lambda **kwargs: logger_calls.append(kwargs)),
        flee=False,
        boss=True,
        summon="summon",
    )
    manager.game = SimpleNamespace(stdscr=SimpleNamespace(getch=lambda: getch_calls.append(True)))
    manager.textbox = object()
    manager.end_battle()

    assert tile.defeated is True
    assert tile.enemy is None
    assert logger_calls[-1]["result"] == "victory"
    assert getch_calls
    assert events[-1][0] == "combat_end"

    manager.engine.flee = True
    player.is_alive = lambda: False
    manager.end_battle()
    assert logger_calls[-1]["result"] == "flee"
