#!/usr/bin/env python3
"""Focused coverage for shared pygame popup helpers."""

from __future__ import annotations

from types import SimpleNamespace

import pygame

from src.ui_pygame.gui import confirmation_popup


class RenderedText:
    def __init__(self, text):
        self.text = text

    def get_width(self):
        return max(8, len(self.text) * 8)

    def get_height(self):
        return 18

    def get_rect(self, **kwargs):
        rect = SimpleNamespace(x=0, y=0, width=self.get_width(), height=self.get_height())
        for key, value in kwargs.items():
            setattr(rect, key, value)
        return rect


class RecordingFont:
    def __init__(self):
        self.render_calls = []

    def render(self, text, _antialias, _color):
        self.render_calls.append(text)
        return RenderedText(text)

    def get_height(self):
        return 18

    def size(self, text):
        return (max(8, len(text) * 8), 18)


class RecordingScreen:
    def __init__(self):
        self.blit_calls = []
        self.fill_calls = []

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))

    def fill(self, color):
        self.fill_calls.append(color)

    def copy(self):
        return "copied-surface"


def _make_presenter(*, debug_mode=False):
    return SimpleNamespace(
        screen=RecordingScreen(),
        width=640,
        height=480,
        title_font=RecordingFont(),
        large_font=RecordingFont(),
        normal_font=RecordingFont(),
        small_font=RecordingFont(),
        debug_mode=debug_mode,
        clock=SimpleNamespace(tick=lambda _fps: None),
    )


def _event(event_type, key=None):
    evt = SimpleNamespace(type=event_type)
    if key is not None:
        evt.key = key
    return evt


def _patch_visuals(monkeypatch):
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.pygame.draw.rect", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.pygame.display.flip", lambda: None)


def test_confirmation_popup_wrap_visible_lines_and_background_helpers(monkeypatch):
    _patch_visuals(monkeypatch)
    presenter = _make_presenter()
    popup = confirmation_popup.ConfirmationPopup(
        presenter,
        "Alpha beta gamma delta epsilon zeta eta theta\n\nSecond paragraph",
        show_buttons=False,
        slow_print=True,
    )

    assert popup.popup_height >= 180
    assert "" in popup._wrapped_lines

    tick_values = iter([popup._start_ms + 100, popup._start_ms + 10000])
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.pygame.time.get_ticks", lambda: next(tick_values))
    visible = popup._get_visible_lines()
    assert visible[0].startswith("Al")
    assert popup._reveal_complete() is True

    presenter.get_background_surface = lambda: "bg-surface"
    assert popup._get_background_surface() == "bg-surface"
    presenter.get_background_surface = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
    assert popup._get_background_surface() == "copied-surface"


def test_confirmation_popup_show_handles_navigation_and_message_only(monkeypatch):
    _patch_visuals(monkeypatch)
    presenter = _make_presenter()
    popup = confirmation_popup.ConfirmationPopup(presenter, "Proceed?")
    clear_calls = []
    draw_calls = []
    popup.draw_popup = lambda: draw_calls.append("drawn")

    event_batches = iter([
        [_event(pygame.KEYDOWN, pygame.K_RIGHT)],
        [_event(pygame.KEYDOWN, pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.pygame.event.get", lambda: next(event_batches, []))
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.pygame.event.clear", lambda: clear_calls.append(True))
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.pygame.time.get_ticks", lambda: 1000)

    bg_calls = []
    assert popup.show(background_draw_func=lambda: bg_calls.append("bg"), flush_events=True) is False
    assert clear_calls == [True]
    assert draw_calls
    assert bg_calls[-1] == "bg"

    message_popup = confirmation_popup.ConfirmationPopup(presenter, "Notice", show_buttons=False)
    message_popup.draw_popup = lambda: None
    monkeypatch.setattr(
        "src.ui_pygame.gui.confirmation_popup.pygame.event.get",
        lambda: [_event(pygame.KEYDOWN, pygame.K_SPACE)],
    )
    assert message_popup.show() is True


def test_confirmation_popup_show_respects_require_release_slow_print_and_min_display(monkeypatch):
    _patch_visuals(monkeypatch)
    presenter = _make_presenter()
    popup = confirmation_popup.ConfirmationPopup(presenter, "Slow reveal test", slow_print=True)
    popup.draw_popup = lambda: None

    tick_values = iter([1000, 1005, 1010, 4000, 4000, 4000, 4000])
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.pygame.time.get_ticks", lambda: next(tick_values))

    pressed_states = iter([[1], [], []])
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.pygame.key.get_pressed", lambda: next(pressed_states))

    event_batches = iter([
        [_event(pygame.KEYDOWN, pygame.K_RETURN)],
        [_event(pygame.KEYDOWN, pygame.K_RETURN)],
        [_event(pygame.KEYDOWN, pygame.K_RETURN)],
        [_event(pygame.KEYDOWN, pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.pygame.event.get", lambda: next(event_batches, []))

    assert popup.show(require_key_release=True, min_display_ms=2000) is True


def test_choice_popup_draw_and_show_cover_wrap_navigation_and_escape(monkeypatch):
    _patch_visuals(monkeypatch)
    presenter = _make_presenter()
    popup = confirmation_popup.ChoicePopup(
        presenter,
        "Pick One",
        ["Alpha", "Beta", "Gamma"],
        header_message="This is a long header that should wrap across multiple lines.",
    )

    popup.draw_popup("background", do_flip=False)
    assert len(popup._header_lines) >= 1
    assert "UP/DOWN: Navigate  ENTER: Select  ESC: Cancel" in presenter.small_font.render_calls

    event_batches = iter([
        [_event(pygame.KEYDOWN, pygame.K_DOWN)],
        [_event(pygame.KEYDOWN, pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.pygame.event.get", lambda: next(event_batches, []))
    assert popup.show() == 1

    popup.current_selection = 0
    monkeypatch.setattr(
        "src.ui_pygame.gui.confirmation_popup.pygame.event.get",
        lambda: [_event(pygame.KEYDOWN, pygame.K_ESCAPE)],
    )
    assert popup.show() is None


def test_reward_selection_popup_draw_and_show_confirm_branch(monkeypatch):
    _patch_visuals(monkeypatch)
    presenter = _make_presenter()
    long_name = "Very Long Reward Name That Needs Truncation"
    items = [SimpleNamespace(name=long_name), SimpleNamespace(name="Potion")]
    popup = confirmation_popup.RewardSelectionPopup(
        presenter,
        "Rewards",
        items,
        detail_provider=lambda item: f"Details for {item.name}\nSecond line",
    )

    popup.draw_popup("background", do_flip=False)
    assert any(text.endswith("...") for text in presenter.normal_font.render_calls)

    class FakeConfirm:
        def __init__(self, _presenter, message, show_buttons=True):
            self.message = message
            self.show_buttons = show_buttons

        def show(self, **_kwargs):
            return True

    monkeypatch.setattr(confirmation_popup, "ConfirmationPopup", FakeConfirm)
    event_batches = iter([
        [_event(pygame.KEYDOWN, pygame.K_DOWN)],
        [_event(pygame.KEYDOWN, pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.pygame.event.get", lambda: next(event_batches, []))
    assert popup.show() == 1

    empty_popup = confirmation_popup.RewardSelectionPopup(presenter, "Rewards", [], lambda _item: "")
    assert empty_popup.show() is None


def test_quantity_popup_draw_and_show_cover_adjustment_confirmation_and_cancel(monkeypatch):
    _patch_visuals(monkeypatch)
    presenter = _make_presenter()
    popup = confirmation_popup.QuantityPopup(
        presenter,
        "Potion",
        unit_cost=5,
        max_quantity=12,
        action="sell",
        default_quantity=27,
    )

    popup.draw_popup(background_draw_func=lambda: presenter.screen.fill((1, 2, 3)))
    assert popup.quantity == 12
    assert "Sell Potion" in presenter.title_font.render_calls
    assert "Total Value: 60g" in presenter.normal_font.render_calls

    event_batches = iter([
        [_event(pygame.KEYDOWN, pygame.K_UP)],
        [_event(pygame.KEYDOWN, pygame.K_LEFT)],
        [_event(pygame.KEYDOWN, pygame.K_DOWN)],
        [_event(pygame.KEYDOWN, pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.pygame.event.get", lambda: next(event_batches, []))
    assert popup.show() == 2

    cancel_popup = confirmation_popup.QuantityPopup(presenter, "Potion", max_quantity=9)
    monkeypatch.setattr(
        "src.ui_pygame.gui.confirmation_popup.pygame.event.get",
        lambda: [_event(pygame.KEYDOWN, pygame.K_ESCAPE)],
    )
    assert cancel_popup.show() is None


def test_code_entry_popup_draw_and_show_cover_digit_navigation(monkeypatch):
    _patch_visuals(monkeypatch)
    presenter = _make_presenter()
    popup = confirmation_popup.CodeEntryPopup(presenter, "Vault", "Enter code")

    popup.draw_popup(background_draw_func=lambda: presenter.screen.fill((0, 0, 0)))
    assert "Enter code" in presenter.normal_font.render_calls

    event_batches = iter([
        [_event(pygame.KEYDOWN, pygame.K_UP)],
        [_event(pygame.KEYDOWN, pygame.K_RIGHT)],
        [_event(pygame.KEYDOWN, pygame.K_UP)],
        [_event(pygame.KEYDOWN, pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.gui.confirmation_popup.pygame.event.get", lambda: next(event_batches, []))
    assert popup.show() == "1100"

    cancel_popup = confirmation_popup.CodeEntryPopup(presenter, "Vault", "Enter code")
    monkeypatch.setattr(
        "src.ui_pygame.gui.confirmation_popup.pygame.event.get",
        lambda: [_event(pygame.KEYDOWN, pygame.K_ESCAPE)],
    )
    assert cancel_popup.show() is None


def test_confirm_yes_no_helper_delegates_to_popup(monkeypatch):
    presenter = _make_presenter()

    class FakeConfirm:
        def __init__(self, received_presenter, message):
            self.received_presenter = received_presenter
            self.message = message

        def show(self):
            return True

    monkeypatch.setattr(confirmation_popup, "ConfirmationPopup", FakeConfirm)
    assert confirmation_popup.confirm_yes_no(presenter, "Continue?") is True
