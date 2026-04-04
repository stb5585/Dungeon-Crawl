#!/usr/bin/env python3
"""Coverage for lightweight presenter interface helpers."""

from __future__ import annotations

from dataclasses import dataclass
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))

from src.core.events import EventBus, EventType, GameEvent
from src.ui_pygame.presentation import interface
from tests.test_framework import TestGameState


@dataclass
class _DummyCharacter:
    name: str = "Dummy"


class _RecordingEventPresenter(interface.EventDrivenPresenter):
    def __init__(self, event_bus):
        self.messages: list[tuple[str, bool]] = []
        super().__init__(event_bus)

    def initialize(self) -> None:
        pass

    def cleanup(self) -> None:
        pass

    def render_combat(self, player, enemy, available_actions, message="") -> None:
        pass

    def render_menu(self, title, options, selected_index=0, max_visible=None) -> None:
        pass

    def render_character_sheet(self, character) -> None:
        pass

    def render_map(self, world_map, player_x, player_y) -> None:
        pass

    def show_message(self, message: str, wait_for_input: bool = True) -> None:
        self.messages.append((message, wait_for_input))

    def show_dialogue(self, speaker, text, choices=None):
        return 0 if choices else None

    def get_player_action(self, available_actions):
        return available_actions[0] if available_actions else "Nothing"

    def get_text_input(self, prompt, max_length=50):
        return prompt[:max_length]

    def confirm(self, question):
        return True

    def update(self) -> None:
        pass

    def clear(self) -> None:
        pass


def test_game_presenter_methods_are_abstract_and_null_presenter_defaults_work():
    assert pytest.raises(TypeError, interface.GamePresenter)

    dummy = _DummyCharacter()
    interface.GamePresenter.initialize(dummy)
    interface.GamePresenter.cleanup(dummy)
    interface.GamePresenter.render_combat(dummy, None, None, [], "")
    interface.GamePresenter.render_menu(dummy, "Menu", [])
    interface.GamePresenter.render_character_sheet(dummy, None)
    interface.GamePresenter.render_map(dummy, [[]], 0, 0)
    interface.GamePresenter.show_message(dummy, "Hello")
    interface.GamePresenter.show_dialogue(dummy, "NPC", "Hi")
    interface.GamePresenter.get_player_action(dummy, [])
    interface.GamePresenter.get_text_input(dummy, "Prompt")
    interface.GamePresenter.confirm(dummy, "Question")
    interface.GamePresenter.update(dummy)
    interface.GamePresenter.clear(dummy)

    presenter = interface.NullPresenter()
    assert presenter.show_dialogue("Guide", "Welcome") is None
    assert presenter.show_dialogue("Guide", "Choose", ["Yes", "No"]) == 0
    assert presenter.get_player_action(["Attack", "Defend"]) == "Attack"
    assert presenter.get_player_action([]) == "Nothing"
    assert presenter.get_text_input("Name?") == ""
    assert presenter.confirm("Continue?") is False
    presenter.initialize()
    presenter.cleanup()
    presenter.render_combat(dummy, dummy, ["Attack"], "Message")
    presenter.render_menu("Menu", ["A"])
    presenter.render_character_sheet(dummy)
    presenter.render_map([["."]], 0, 0)
    presenter.show_message("Hello")
    presenter.update()
    presenter.clear()


def test_event_driven_presenter_subscribes_and_forwards_message_events():
    event_bus = EventBus()
    presenter = _RecordingEventPresenter(event_bus)

    assert EventType.DAMAGE_DEALT in event_bus._subscribers
    assert EventType.STATUS_APPLIED in event_bus._subscribers
    assert EventType.MESSAGE_DISPLAY in event_bus._subscribers

    presenter.on_damage_dealt(GameEvent(type=EventType.DAMAGE_DEALT, timestamp=0, data={}))
    presenter.on_status_applied(GameEvent(type=EventType.STATUS_APPLIED, timestamp=0, data={}))
    presenter.on_message(GameEvent(type=EventType.MESSAGE_DISPLAY, timestamp=0, data={}))
    assert presenter.messages == []

    event_bus.emit(
        GameEvent(
            type=EventType.MESSAGE_DISPLAY,
            timestamp=1,
            data={"message": "A hidden door opens."},
        )
    )

    assert presenter.messages == [("A hidden door opens.", True)]


def test_console_presenter_renders_text_views(capsys):
    presenter = interface.ConsolePresenter()
    player = TestGameState.create_player(name="Hero", class_name="Warrior", race_name="Human", health=(100, 80), mana=(40, 25))
    enemy = TestGameState.create_player(name="Goblin", class_name="Warrior", race_name="Human", health=(30, 10), mana=(0, 0))

    presenter.initialize()
    presenter.render_combat(player, enemy, ["Attack", "Defend"], message="A wild foe appears!")
    presenter.render_menu("Main Menu", ["Attack", "Defend"], selected_index=1)
    presenter.render_character_sheet(player)
    presenter.render_map([[".", "."], ["#", "."]], 1, 0)
    presenter.cleanup()

    output = capsys.readouterr().out
    assert "Dungeon Crawl - Console Mode" in output
    assert "Hero (HP: 80/100)" in output
    assert "Goblin (HP: 10/30)" in output
    assert "A wild foe appears!" in output
    assert "> 2. Defend" in output
    assert "Level:" in output
    assert ".@" in output
    assert "Game Over" in output


def test_console_presenter_input_helpers_loop_until_valid(monkeypatch, capsys):
    presenter = interface.ConsolePresenter()
    responses = iter(["abc", "4", "2", "0", "2", "very long name", "YES", "n"])
    prompts = []

    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": prompts.append(prompt) or next(responses),
    )

    choice = presenter.show_dialogue("Guide", "Choose wisely.", ["One", "Two", "Three"])
    action = presenter.get_player_action(["Attack", "Defend", "Item"])
    text = presenter.get_text_input("Character Name", max_length=4)
    yes = presenter.confirm("Proceed")
    no = presenter.confirm("Abort")

    assert choice == 1
    assert action == "Defend"
    assert text == "very"
    assert yes is True
    assert no is False
    output = capsys.readouterr().out
    assert "Invalid choice. Try again." in output
    assert "Invalid action. Try again." in output
    assert any("Your choice:" in prompt for prompt in prompts)
    assert any("Your action:" in prompt for prompt in prompts)


def test_console_presenter_show_message_and_clear(monkeypatch, capsys):
    presenter = interface.ConsolePresenter()
    prompts = []
    commands = []

    monkeypatch.setattr("builtins.input", lambda prompt="": prompts.append(prompt) or "")
    monkeypatch.setattr("os.system", lambda command: commands.append(command) or 0)

    presenter.show_message("A treasure chest appears.", wait_for_input=False)
    presenter.show_message("Press on.", wait_for_input=True)
    assert presenter.show_dialogue("Narrator", "No choices here.") is None
    presenter.update()
    presenter.clear()

    output = capsys.readouterr().out
    assert "A treasure chest appears." in output
    assert "Press on." in output
    assert "Narrator: No choices here." in output
    assert prompts == ["\nPress Enter to continue..."]
    assert commands == ["clear"]
