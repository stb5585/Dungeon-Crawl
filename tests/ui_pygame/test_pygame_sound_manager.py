#!/usr/bin/env python3
"""Coverage for pygame sound-manager behavior using mixer fakes."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.events import EventBus, EventType, GameEvent
from src.ui_pygame.assets import sound_manager as sound_module


class FakeSound:
    def __init__(self, path: str):
        self.path = path
        self.volumes: list[float] = []
        self.play_loops: list[int] = []

    def set_volume(self, value: float):
        self.volumes.append(value)

    def play(self, loops: int = 0):
        self.play_loops.append(loops)


class FakeMusic:
    def __init__(self):
        self.busy = False
        self.raise_on_load = False
        self.fadeouts: list[int] = []
        self.loaded: list[str] = []
        self.volumes: list[float] = []
        self.plays: list[tuple[int, int]] = []
        self.paused = 0
        self.unpaused = 0

    def get_busy(self):
        return self.busy

    def fadeout(self, value: int):
        self.fadeouts.append(value)
        self.busy = False

    def load(self, path: str):
        if self.raise_on_load:
            raise sound_module.pygame.error("music boom")
        self.loaded.append(path)

    def set_volume(self, value: float):
        self.volumes.append(value)

    def play(self, loops: int = -1, fade_ms: int = 0):
        self.plays.append((loops, fade_ms))
        self.busy = True

    def pause(self):
        self.paused += 1

    def unpause(self):
        self.unpaused += 1


@pytest.fixture
def fake_mixer(monkeypatch):
    state = {
        "initialized": True,
        "init_calls": [],
        "channels": [],
        "loaded_sounds": [],
        "stop_calls": 0,
        "quit_calls": 0,
        "init_exception": None,
        "sound_exception": None,
    }
    music = FakeMusic()

    def fake_get_init():
        return state["initialized"]

    def fake_init(**kwargs):
        state["init_calls"].append(kwargs)
        if state["init_exception"] is not None:
            raise state["init_exception"]
        state["initialized"] = True

    def fake_set_num_channels(count):
        state["channels"].append(count)

    def fake_sound(path):
        if state["sound_exception"] is not None:
            raise state["sound_exception"]
        sound = FakeSound(path)
        state["loaded_sounds"].append(sound)
        return sound

    def fake_stop():
        state["stop_calls"] += 1

    def fake_quit():
        state["quit_calls"] += 1
        state["initialized"] = False

    monkeypatch.setattr(sound_module.pygame.mixer, "get_init", fake_get_init)
    monkeypatch.setattr(sound_module.pygame.mixer, "init", fake_init)
    monkeypatch.setattr(sound_module.pygame.mixer, "set_num_channels", fake_set_num_channels)
    monkeypatch.setattr(sound_module.pygame.mixer, "Sound", fake_sound)
    monkeypatch.setattr(sound_module.pygame.mixer, "music", music, raising=False)
    monkeypatch.setattr(sound_module.pygame.mixer, "stop", fake_stop)
    monkeypatch.setattr(sound_module.pygame.mixer, "quit", fake_quit)
    return state, music


def _make_assets_dir(tmp_path: Path) -> Path:
    assets_dir = tmp_path / "assets"
    (assets_dir / "sounds").mkdir(parents=True)
    (assets_dir / "music").mkdir(parents=True)
    return assets_dir


def test_sound_manager_initializes_mixer_and_subscribes_to_bus(tmp_path, fake_mixer):
    state, _music = fake_mixer
    state["initialized"] = False
    bus = EventBus()
    manager = sound_module.SoundManager(assets_dir=str(_make_assets_dir(tmp_path)), event_bus=bus)

    assert manager.enabled is True
    assert state["init_calls"] == [
        {"frequency": 44100, "size": -16, "channels": 2, "buffer": 512}
    ]
    assert state["channels"] == [16]
    assert EventType.COMBAT_START in bus._subscribers
    assert EventType.LEVEL_UP in bus._subscribers


def test_sound_manager_disables_when_mixer_init_fails(tmp_path, fake_mixer):
    state, _music = fake_mixer
    state["initialized"] = False
    state["init_exception"] = sound_module.pygame.error("no audio")

    manager = sound_module.SoundManager(assets_dir=str(_make_assets_dir(tmp_path)))

    assert manager.enabled is False
    assert state["channels"] == []


def test_load_sfx_uses_cache_and_fallback_extensions(tmp_path, fake_mixer):
    state, _music = fake_mixer
    assets_dir = _make_assets_dir(tmp_path)
    (assets_dir / "sounds" / "hit.ogg").write_bytes(b"ogg")
    manager = sound_module.SoundManager(assets_dir=str(assets_dir))

    first = manager.load_sfx("hit")
    second = manager.load_sfx("hit")

    assert first is second
    assert len(state["loaded_sounds"]) == 1
    assert state["loaded_sounds"][0].path.endswith("hit.ogg")


def test_load_sfx_returns_none_for_missing_files_or_loader_errors(tmp_path, fake_mixer):
    state, _music = fake_mixer
    assets_dir = _make_assets_dir(tmp_path)
    manager = sound_module.SoundManager(assets_dir=str(assets_dir))

    assert manager.load_sfx("missing") is None

    (assets_dir / "sounds" / "bad.wav").write_bytes(b"wav")
    state["sound_exception"] = sound_module.pygame.error("bad sound")
    assert manager.load_sfx("bad") is None


def test_play_sfx_applies_volume_and_loops(tmp_path, fake_mixer, monkeypatch):
    _state, _music = fake_mixer
    manager = sound_module.SoundManager(assets_dir=str(_make_assets_dir(tmp_path)))
    sound = FakeSound("manual")
    monkeypatch.setattr(manager, "load_sfx", lambda sound_name: sound)

    manager.master_volume = 0.5
    manager.play_sfx("hit")
    manager.play_sfx("critical", volume=1.0, loops=2)

    assert sound.volumes == [0.35, 0.5]
    assert sound.play_loops == [0, 2]


def test_play_music_handles_busy_track_and_fallback_files(tmp_path, fake_mixer):
    _state, music = fake_mixer
    assets_dir = _make_assets_dir(tmp_path)
    (assets_dir / "music" / "battle.mp3").write_bytes(b"mp3")
    manager = sound_module.SoundManager(assets_dir=str(assets_dir))
    music.busy = True

    manager.play_music("battle", loops=3, fade_ms=600)

    assert music.fadeouts == [300]
    assert music.loaded and music.loaded[0].endswith("battle.mp3")
    assert music.volumes == [0.5]
    assert music.plays == [(3, 600)]
    assert manager.current_music == "battle"


def test_play_music_missing_or_erroring_files_are_safe(tmp_path, fake_mixer):
    _state, music = fake_mixer
    assets_dir = _make_assets_dir(tmp_path)
    manager = sound_module.SoundManager(assets_dir=str(assets_dir))

    manager.play_music("missing")
    assert manager.current_music is None

    (assets_dir / "music" / "broken.ogg").write_bytes(b"ogg")
    music.raise_on_load = True
    manager.play_music("broken")
    assert manager.current_music is None


def test_stop_pause_resume_and_volume_controls(tmp_path, fake_mixer):
    _state, music = fake_mixer
    assets_dir = _make_assets_dir(tmp_path)
    (assets_dir / "music" / "battle.ogg").write_bytes(b"ogg")
    manager = sound_module.SoundManager(assets_dir=str(assets_dir))
    music.busy = True
    manager.current_music = "battle"

    manager.stop_music(fade_ms=700)
    manager.pause_music()
    manager.resume_music()
    music.busy = True
    manager.set_master_volume(1.5)
    manager.set_sfx_volume(-0.2)
    manager.set_music_volume(2.0)

    assert music.fadeouts == [700]
    assert music.paused == 1
    assert music.unpaused == 1
    assert manager.current_music is None
    assert manager.master_volume == 1.0
    assert manager.sfx_volume == 0.0
    assert manager.music_volume == 1.0
    assert music.volumes[-2:] == [0.5, 1.0]


def test_enable_disable_cleanup_and_singleton_access(tmp_path, fake_mixer, monkeypatch):
    state, music = fake_mixer
    assets_dir = _make_assets_dir(tmp_path)
    manager = sound_module.SoundManager(assets_dir=str(assets_dir))
    manager.sfx_cache["hit"] = FakeSound("cached")
    music.busy = True

    manager.disable()
    assert manager.enabled is False
    assert music.fadeouts == [0]
    assert state["stop_calls"] == 1

    manager.enable()
    assert manager.enabled is True

    music.busy = True
    manager.cleanup()
    assert manager.sfx_cache == {}
    assert state["quit_calls"] == 1
    assert music.fadeouts[-1] == 0

    created = []

    class FakeSingleton:
        def __init__(self, assets_dir="src/ui_pygame/assets", event_bus=None):
            self.assets_dir = assets_dir
            self.event_bus = event_bus
            created.append((assets_dir, event_bus))

    monkeypatch.setattr(sound_module, "_sound_manager", None)
    monkeypatch.setattr(sound_module, "SoundManager", FakeSingleton)

    first = sound_module.get_sound_manager("alpha", event_bus="bus")
    second = sound_module.get_sound_manager("beta", event_bus=None)

    assert first is second
    assert created == [("alpha", "bus")]


def test_event_handlers_route_to_expected_sound_effects(tmp_path, fake_mixer, monkeypatch):
    _state, _music = fake_mixer
    manager = sound_module.SoundManager(assets_dir=str(_make_assets_dir(tmp_path)))
    calls = []
    monkeypatch.setattr(manager, "play_sfx", lambda name, volume=None, loops=0: calls.append((name, volume, loops)))

    manager._on_combat_start(GameEvent(type=EventType.COMBAT_START, timestamp=0, data={}))
    manager._on_combat_end(GameEvent(type=EventType.COMBAT_END, timestamp=0, data={"player_alive": True}))
    manager._on_combat_end(GameEvent(type=EventType.COMBAT_END, timestamp=0, data={"fled": True}))
    manager._on_combat_end(GameEvent(type=EventType.COMBAT_END, timestamp=0, data={}))
    manager._on_damage_dealt(GameEvent(type=EventType.DAMAGE_DEALT, timestamp=0, data={"crit": True, "damage": 1}))
    manager._on_damage_dealt(GameEvent(type=EventType.DAMAGE_DEALT, timestamp=0, data={"damage": 80}))
    manager._on_damage_dealt(GameEvent(type=EventType.DAMAGE_DEALT, timestamp=0, data={"damage": 10}))
    manager._on_healing(GameEvent(type=EventType.HEALING_DONE, timestamp=0, data={}))
    manager._on_spell_cast(GameEvent(type=EventType.SPELL_CAST, timestamp=0, data={"spell_name": "Fireball"}))
    manager._on_spell_cast(GameEvent(type=EventType.SPELL_CAST, timestamp=0, data={"spell_name": "Frost Lance"}))
    manager._on_spell_cast(GameEvent(type=EventType.SPELL_CAST, timestamp=0, data={"ability_name": "Lightning Arc"}))
    manager._on_spell_cast(GameEvent(type=EventType.SPELL_CAST, timestamp=0, data={"spell_name": "Heal"}))
    manager._on_spell_cast(GameEvent(type=EventType.SPELL_CAST, timestamp=0, data={"spell_name": "Mystery"}))
    manager._on_skill_use(GameEvent(type=EventType.SKILL_USE, timestamp=0, data={"skill_name": "Fire Slash"}))
    manager._on_skill_use(GameEvent(type=EventType.SKILL_USE, timestamp=0, data={"skill_name": "Ice Kick"}))
    manager._on_skill_use(GameEvent(type=EventType.SKILL_USE, timestamp=0, data={"ability_name": "Shock Palm"}))
    manager._on_skill_use(GameEvent(type=EventType.SKILL_USE, timestamp=0, data={"skill_name": "Healing Waltz"}))
    manager._on_skill_use(GameEvent(type=EventType.SKILL_USE, timestamp=0, data={"skill_name": "Backflip"}))
    manager._on_status_applied(GameEvent(type=EventType.STATUS_APPLIED, timestamp=0, data={"status_name": "Poison"}))
    manager._on_status_applied(GameEvent(type=EventType.STATUS_APPLIED, timestamp=0, data={"status_name": "Freeze"}))
    manager._on_status_applied(GameEvent(type=EventType.STATUS_APPLIED, timestamp=0, data={"status_name": "Burn"}))
    manager._on_status_applied(GameEvent(type=EventType.STATUS_APPLIED, timestamp=0, data={"status_name": "Sleep"}))
    manager._on_death(GameEvent(type=EventType.CHARACTER_DEATH, timestamp=0, data={"is_player": True}))
    manager._on_death(GameEvent(type=EventType.CHARACTER_DEATH, timestamp=0, data={"is_player": False}))
    manager._on_level_up(GameEvent(type=EventType.LEVEL_UP, timestamp=0, data={}))

    assert calls == [
        ("combat_start", None, 0),
        ("victory", None, 0),
        ("flee", None, 0),
        ("defeat", None, 0),
        ("critical_hit", 1.0, 0),
        ("heavy_hit", None, 0),
        ("hit", None, 0),
        ("heal", None, 0),
        ("spell_fire", None, 0),
        ("spell_ice", None, 0),
        ("spell_lightning", None, 0),
        ("spell_heal", None, 0),
        ("spell_cast", None, 0),
        ("spell_fire", None, 0),
        ("spell_ice", None, 0),
        ("spell_lightning", None, 0),
        ("spell_heal", None, 0),
        ("spell_cast", None, 0),
        ("poison", None, 0),
        ("stun", None, 0),
        ("burn", None, 0),
        ("player_death", None, 0),
        ("enemy_death", None, 0),
        ("level_up", None, 0),
    ]
