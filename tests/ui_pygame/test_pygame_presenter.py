#!/usr/bin/env python3
"""Focused coverage for pygame presenter helpers and event-driven UI flow."""

from __future__ import annotations

from types import SimpleNamespace

import pygame

from src.core.events import EventType
from src.ui_pygame.presentation import pygame_presenter


class DummyRenderedText:
    def __init__(self, text):
        self.text = text
        self.alpha = None

    def set_alpha(self, value):
        self.alpha = value

    def get_width(self):
        return max(8, len(self.text) * 8)

    def get_height(self):
        return 18

    def get_rect(self, **kwargs):
        rect = pygame.Rect(0, 0, self.get_width(), self.get_height())
        for key, value in kwargs.items():
            setattr(rect, key, value)
        return rect


class RecordingFont:
    def __init__(self):
        self.render_calls = []

    def render(self, text, _antialias, _color):
        self.render_calls.append(text)
        return DummyRenderedText(text)

    def size(self, text):
        return (max(8, len(text) * 8), 18)


class DummyScreen:
    def __init__(self, size=(640, 480)):
        self._size = size
        self.blit_calls = []
        self.fill_calls = []

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))

    def fill(self, color):
        self.fill_calls.append(color)

    def copy(self):
        return DummyScreen(self._size)

    def get_size(self):
        return self._size


class DummySurface:
    def __init__(self, size=(64, 64)):
        self._size = size
        self.blit_calls = []
        self.fill_calls = []

    def fill(self, color):
        self.fill_calls.append(color)

    def blit(self, surface, position):
        self.blit_calls.append((surface, position))

    def copy(self):
        return DummySurface(self._size)

    def get_size(self):
        return self._size

    def get_rect(self, **kwargs):
        rect = pygame.Rect(0, 0, *self._size)
        for key, value in kwargs.items():
            setattr(rect, key, value)
        return rect

    def convert_alpha(self):
        return self

    def convert(self):
        return self


class DummyClock:
    def __init__(self):
        self.ticks = []

    def tick(self, fps):
        self.ticks.append(fps)


class DummyEventBus:
    def __init__(self):
        self.subscriptions = []

    def subscribe(self, event_type, callback):
        self.subscriptions.append((event_type, callback))


class DummySoundManager:
    def __init__(self):
        self.sfx = []
        self.cleaned = False

    def play_sfx(self, name):
        self.sfx.append(name)

    def cleanup(self):
        self.cleaned = True


def _make_character(name="Hero", *, hp=(80, 100), mp=(10, 20), statuses=None):
    status_effects = statuses or {}
    return SimpleNamespace(
        name=name,
        health=SimpleNamespace(current=hp[0], max=hp[1]),
        mana=SimpleNamespace(current=mp[0], max=mp[1]),
        status_effects=status_effects,
        level=SimpleNamespace(level=7),
        stats=SimpleNamespace(strength=12, intel=11, wisdom=10, con=13, dex=14, charisma=9),
    )


def _event(event_type, key=None, unicode=""):
    evt = SimpleNamespace(type=event_type)
    evt.key = key
    evt.unicode = unicode
    return evt


def _install_presenter_fakes(monkeypatch):
    event_bus = DummyEventBus()
    sound_manager = DummySoundManager()
    display_screen = DummyScreen((640, 480))
    title_font = RecordingFont()
    large_font = RecordingFont()
    normal_font = RecordingFont()
    small_font = RecordingFont()
    fonts = iter([title_font, large_font, normal_font, small_font])
    flip_calls = []
    captions = []
    quit_calls = []

    monkeypatch.setattr(pygame_presenter, "SOUND_AVAILABLE", True)
    monkeypatch.setattr(pygame_presenter, "get_event_bus", lambda: event_bus)
    monkeypatch.setattr(pygame_presenter, "get_sound_manager", lambda event_bus=None: sound_manager)
    monkeypatch.setattr("src.ui_pygame.presentation.pygame_presenter.pygame.init", lambda: None)
    monkeypatch.setattr("src.ui_pygame.presentation.pygame_presenter.pygame.font.init", lambda: None)
    monkeypatch.setattr(
        "src.ui_pygame.presentation.pygame_presenter.pygame.display.set_mode",
        lambda size: display_screen,
    )
    monkeypatch.setattr(
        "src.ui_pygame.presentation.pygame_presenter.pygame.display.set_caption",
        lambda caption: captions.append(caption),
    )
    monkeypatch.setattr(
        "src.ui_pygame.presentation.pygame_presenter.pygame.font.Font",
        lambda *_args, **_kwargs: next(fonts),
    )
    monkeypatch.setattr(
        "src.ui_pygame.presentation.pygame_presenter.pygame.time.Clock",
        lambda: DummyClock(),
    )
    monkeypatch.setattr(
        "src.ui_pygame.presentation.pygame_presenter.pygame.display.flip",
        lambda: flip_calls.append(True),
    )
    monkeypatch.setattr(
        "src.ui_pygame.presentation.pygame_presenter.pygame.draw.rect",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "src.ui_pygame.presentation.pygame_presenter.pygame.Surface",
        lambda size, *_args, **_kwargs: DummySurface(size),
    )
    monkeypatch.setattr(
        "src.ui_pygame.presentation.pygame_presenter.pygame.transform.smoothscale",
        lambda surface, size: DummySurface(size),
    )
    monkeypatch.setattr(
        "src.ui_pygame.presentation.pygame_presenter.pygame.transform.scale",
        lambda surface, size: DummySurface(size),
    )
    monkeypatch.setattr(
        "src.ui_pygame.presentation.pygame_presenter.pygame.quit",
        lambda: quit_calls.append(True),
    )

    presenter = pygame_presenter.PygamePresenter(width=640, height=480)
    return SimpleNamespace(
        presenter=presenter,
        event_bus=event_bus,
        sound_manager=sound_manager,
        screen=display_screen,
        flip_calls=flip_calls,
        captions=captions,
        quit_calls=quit_calls,
        title_font=title_font,
        large_font=large_font,
        normal_font=normal_font,
        small_font=small_font,
    )


def test_floating_text_updates_and_draws():
    font = RecordingFont()
    surface = DummyScreen()
    floating = pygame_presenter.FloatingText("12", 100, 200, pygame_presenter.WHITE, font)

    assert floating.update() is True
    assert floating.y == 198
    assert floating.alpha == 251

    floating.draw(surface)
    drawn_surface, position = surface.blit_calls[-1]
    assert isinstance(drawn_surface, DummyRenderedText)
    assert drawn_surface.alpha == 251
    assert position == (100, 198)


def test_presenter_initializes_subscriptions_and_basic_event_handlers(monkeypatch):
    bundle = _install_presenter_fakes(monkeypatch)
    presenter = bundle.presenter

    subscribed = {event_type for event_type, _callback in bundle.event_bus.subscriptions}
    assert bundle.captions == ["Dungeon Crawl - Combat"]
    assert {
        EventType.COMBAT_START,
        EventType.COMBAT_END,
        EventType.TURN_START,
        EventType.DAMAGE_DEALT,
        EventType.HEALING_DONE,
        EventType.CRITICAL_HIT,
        EventType.STATUS_APPLIED,
    } <= subscribed
    assert presenter.sound_manager is bundle.sound_manager

    hero = _make_character("Hero")
    goblin = _make_character("Goblin", hp=(12, 30), mp=(0, 0))
    presenter.enemy = goblin

    presenter._on_combat_start(SimpleNamespace(actor=hero, target=goblin, data={}))
    presenter._on_turn_start(SimpleNamespace(data={"turn_number": 4}))
    presenter._on_damage_dealt(
        SimpleNamespace(
            data={"damage": 35, "damage_type": "Fire", "is_critical": True, "target": goblin}
        )
    )
    presenter._on_healing_done(SimpleNamespace(data={"amount": 18, "actor": hero}))
    presenter._on_critical_hit(SimpleNamespace(data={}))
    presenter._on_status_applied(
        SimpleNamespace(target=goblin, data={"status_name": "Poisoned"})
    )
    presenter._on_status_applied(
        SimpleNamespace(target=None, data={"status_name": "Burning", "target": "Torch"})
    )
    presenter._on_combat_end(SimpleNamespace(actor=hero, data={"player_alive": True}))
    presenter._on_combat_end(SimpleNamespace(actor=hero, data={"fled": True}))
    presenter._on_combat_end(SimpleNamespace(actor=hero, data={}))

    assert presenter.turn_number == 4
    assert len(presenter.floating_texts) == 2
    assert presenter.floating_texts[0].text == "CRIT! -35"
    assert presenter.floating_texts[1].text == "+18 HP"
    assert presenter.shake_intensity == 15
    assert presenter.shake_duration == 20
    assert "Combat begins: Hero vs Goblin!" in presenter.combat_log
    assert "Goblin is Poisoned!" in presenter.combat_log
    assert "Torch is Burning!" in presenter.combat_log
    assert "Hero is victorious!" in presenter.combat_log
    assert "Hero fled from combat!" in presenter.combat_log
    assert "Hero was defeated..." in presenter.combat_log


def test_presenter_background_helpers_and_cleanup(monkeypatch):
    bundle = _install_presenter_fakes(monkeypatch)
    presenter = bundle.presenter

    copied = presenter.get_background_surface()
    assert copied is not presenter.screen

    background = DummySurface((320, 240))
    presenter.set_background_provider(lambda: background)
    assert presenter.get_background_surface() is background

    presenter.set_background_provider(lambda: None)
    assert presenter.get_background_surface() is not None

    presenter.set_background_provider(lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    assert presenter.get_background_surface() is not None

    presenter.clear()
    presenter.update()
    presenter.cleanup()

    assert bundle.screen.fill_calls[-1] == pygame_presenter.BLACK
    assert bundle.flip_calls
    assert bundle.sound_manager.cleaned is True
    assert bundle.quit_calls


def test_render_combat_processes_input_updates_and_draws(monkeypatch):
    bundle = _install_presenter_fakes(monkeypatch)
    presenter = bundle.presenter

    player = _make_character("Hero", statuses={"Poison": SimpleNamespace(active=True)})
    enemy = _make_character("Goblin", hp=(10, 20), mp=(0, 0))

    presenter.combat_log = [f"Line {index}" for index in range(10)]
    presenter.log_scroll_offset = 1
    presenter.turn_number = 3
    presenter.telegraph_message = "Enemy is charging!"
    presenter.floating_texts = [pygame_presenter.FloatingText("hit", 1, 2, pygame_presenter.WHITE, presenter.large_font)]
    presenter.shake_intensity = 2
    presenter.shake_duration = 1

    randint_values = iter([1, -1])
    monkeypatch.setattr(
        "src.ui_pygame.presentation.pygame_presenter.pygame.event.get",
        lambda: [],
    )
    monkeypatch.setattr("random.randint", lambda _a, _b: next(randint_values))

    presenter.render_combat(player, enemy)

    assert presenter.log_scroll_offset == 1
    assert presenter.shake_duration == 0
    assert presenter.small_font.render_calls.count("▲") == 1
    assert presenter.small_font.render_calls.count("▼") == 1
    assert any("Enemy is charging!" in text for text in presenter.normal_font.render_calls)
    assert any("Combat Log" == text for text in presenter.normal_font.render_calls)
    assert bundle.flip_calls
    assert presenter.clock.ticks[-1] == presenter.fps


def test_render_menu_list_grid_and_split_layout_paths(monkeypatch):
    bundle = _install_presenter_fakes(monkeypatch)
    presenter = bundle.presenter

    event_batches = iter([
        [_event(pygame.KEYDOWN, pygame.K_DOWN)],
        [_event(pygame.KEYDOWN, pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.presentation.pygame_presenter.pygame.event.get", lambda: next(event_batches, []))
    assert presenter.render_menu("Title", ["One", "Two", "Three"], selected_index=0, max_visible=2) == 1

    event_batches = iter([
        [_event(pygame.KEYDOWN, pygame.K_RIGHT)],
        [_event(pygame.KEYDOWN, pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.presentation.pygame_presenter.pygame.event.get", lambda: next(event_batches, []))
    assert presenter.render_menu("Grid", ["A", "B", "C"], use_grid=True) == 1

    fake_image = DummySurface((200, 100))
    bg_calls = []
    event_batches = iter([
        [_event(pygame.KEYDOWN, pygame.K_DOWN)],
        [_event(pygame.KEYDOWN, pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.presentation.pygame_presenter.pygame.event.get", lambda: next(event_batches, []))
    monkeypatch.setattr("os.path.exists", lambda _path: True)
    monkeypatch.setattr(
        "src.ui_pygame.presentation.pygame_presenter.pygame.image.load",
        lambda _path: fake_image,
    )
    assert presenter.render_menu(
        "Wrapped title for split layout rendering.",
        ["Left", "Right", "Down"],
        split_layout=True,
        max_visible=2,
        image_path="portrait.png",
        background_draw_func=lambda: bg_calls.append(True),
    ) == 1
    assert bg_calls
    assert "UP/DOWN: Navigate  ENTER: Select  ESC: Cancel" in presenter.small_font.render_calls
    assert "menu_select" in bundle.sound_manager.sfx
    assert "menu_confirm" in bundle.sound_manager.sfx


def test_show_message_progress_popup_and_dialogue_paths(monkeypatch):
    bundle = _install_presenter_fakes(monkeypatch)
    presenter = bundle.presenter
    presenter.debug_mode = True

    tick_values = iter([0, 0, 1000, 1000])
    event_batches = iter([
        [],
        [_event(pygame.KEYDOWN, pygame.K_SPACE)],
    ])
    monkeypatch.setattr("src.ui_pygame.presentation.pygame_presenter.pygame.time.get_ticks", lambda: next(tick_values))
    monkeypatch.setattr("src.ui_pygame.presentation.pygame_presenter.pygame.event.get", lambda: next(event_batches, []))
    presenter.show_message(
        "A very long message that should wrap in the split layout pane.",
        title="Header",
        split_layout=True,
        min_display_seconds=0.5,
        background_draw_func=lambda: bundle.screen.fill((1, 2, 3)),
    )

    fake_image = DummySurface((90, 45))
    tick_values = iter([1000, 1000])
    event_batches = iter([
        [_event(pygame.KEYDOWN, pygame.K_SPACE)],
    ])
    monkeypatch.setattr("src.ui_pygame.presentation.pygame_presenter.pygame.time.get_ticks", lambda: next(tick_values))
    monkeypatch.setattr("src.ui_pygame.presentation.pygame_presenter.pygame.event.get", lambda: next(event_batches, []))
    monkeypatch.setattr("os.path.exists", lambda _path: True)
    monkeypatch.setattr(
        "src.ui_pygame.presentation.pygame_presenter.pygame.image.load",
        lambda _path: fake_image,
    )
    presenter.show_message("Short message", title="Notice", image_path="img.png")

    event_batches = iter([
        [],
        [],
    ])
    monkeypatch.setattr("src.ui_pygame.presentation.pygame_presenter.pygame.event.get", lambda: next(event_batches, []))
    presenter.show_progress_popup("Loading", "Please wait", steps=1, total_time=0.0)

    calls = []
    monkeypatch.setattr(presenter, "show_message", lambda text, title="": calls.append((title, text)))
    event_batches = iter([
        [_event(pygame.KEYDOWN, pygame.K_SPACE)],
    ])
    monkeypatch.setattr("src.ui_pygame.presentation.pygame_presenter.pygame.event.get", lambda: next(event_batches, []))
    presenter.show_dialogue("Guide", "Welcome")

    assert calls == [("Guide", "Welcome")]
    assert "Please wait..." in presenter.small_font.render_calls
    assert "Press any key to continue..." in presenter.small_font.render_calls


def test_input_confirmation_and_basic_render_helpers(monkeypatch):
    bundle = _install_presenter_fakes(monkeypatch)
    presenter = bundle.presenter

    event_batches = iter([
        [_event(pygame.KEYDOWN, pygame.K_DOWN)],
        [_event(pygame.KEYDOWN, pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.presentation.pygame_presenter.pygame.event.get", lambda: next(event_batches, []))
    menu_calls = []
    monkeypatch.setattr(
        presenter,
        "render_menu",
        lambda prompt, options, selected=0: menu_calls.append((prompt, tuple(options), selected)),
    )
    assert presenter.get_player_action("Choose", ["Attack", "Defend"]) == "Defend"

    event_batches = iter([
        [_event(pygame.KEYDOWN, unicode="A")],
        [_event(pygame.KEYDOWN, unicode="B")],
        [_event(pygame.KEYDOWN, pygame.K_BACKSPACE)],
        [_event(pygame.KEYDOWN, pygame.K_RETURN)],
    ])
    monkeypatch.setattr("src.ui_pygame.presentation.pygame_presenter.pygame.event.get", lambda: next(event_batches, []))
    assert presenter.get_text_input("Name?", default="Hero") == "HeroA"

    event_batches = iter([
        [_event(pygame.KEYDOWN, pygame.K_ESCAPE)],
    ])
    monkeypatch.setattr("src.ui_pygame.presentation.pygame_presenter.pygame.event.get", lambda: next(event_batches, []))
    assert presenter.get_text_input("Name?", default="Hero") == "Hero"

    monkeypatch.setattr(presenter, "get_player_action", lambda prompt, options: "Yes")
    assert presenter.confirm("Continue?") is True

    hero = _make_character("Hero")
    presenter.render_map([["."]], (0, 0))
    presenter.render_character_sheet(hero)

    assert menu_calls
    assert "Map View (Not Implemented)" in presenter.large_font.render_calls
    assert "Hero" in presenter.title_font.render_calls
    assert any(text.startswith("Level:") for text in presenter.normal_font.render_calls)
