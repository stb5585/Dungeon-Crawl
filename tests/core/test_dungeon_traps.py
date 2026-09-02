"""Regression coverage for sparse ordinary-path dungeon traps."""

import random
from types import SimpleNamespace

from src.core import abilities, enemies, map_tiles
from src.core.combat.battle_engine import BattleEngine
from src.core.save_system import TileStateSerializer
from tests.test_framework import TestGameState


class _PlacementRng:
    def random(self):
        return 0.0

    def choices(self, population, **_kwargs):
        return [population[0]]


class _TripwireRng:
    def randint(self, low, _high):
        return low

    def random(self):
        return 1.0


def _player(class_name="Warrior"):
    player = TestGameState.create_player(class_name=class_name, level=30)
    player.quest_dict = {"Main": {}, "Side": {}, "Bounty": {}}
    player.state = "normal"
    return player


def test_traps_are_only_assigned_to_exact_ordinary_path_types():
    ordinary = [
        map_tiles.EmptyCavePath(0, 0, 0),
        map_tiles.CavePath0(1, 0, 0),
        map_tiles.CavePath1(2, 0, 1),
        map_tiles.CavePath2(3, 0, 2),
    ]
    excluded = [
        map_tiles.BossPath(4, 0, 2),
        map_tiles.FirePath(5, 0, 2),
        map_tiles.RubbleTile(6, 0, 2),
        map_tiles.StairsDown(7, 0, 2),
    ]
    world = {(tile.x, tile.y, tile.z): tile for tile in (*ordinary, *excluded)}

    count = map_tiles.assign_dungeon_traps(world, rng=_PlacementRng())

    assert count == 4
    assert all(tile.trap_type == "Tripwire" for tile in ordinary)
    assert all(not hasattr(tile, "trap_type") or tile.trap_type is None for tile in excluded)


def test_tripwire_scales_with_depth_uses_defense_and_only_triggers_once():
    player = _player()
    tile = map_tiles.EmptyCavePath(1, 1, 3)
    tile.trap_type = "Tripwire"
    initial_health = player.health.current

    message = map_tiles.trigger_tile_trap(tile, player, rng=_TripwireRng())
    health_after_first = player.health.current
    second_message = map_tiles.trigger_tile_trap(tile, player, rng=_TripwireRng())

    assert "arrow" in message
    assert health_after_first < initial_health
    assert second_message == ""
    assert player.health.current == health_after_first


def test_avoid_traps_halves_a_failed_tripwire_avoidance():
    baseline = _player("Footpad")
    protected = _player("Footpad")
    protected.spellbook["Skills"]["Avoid Traps"] = abilities.AvoidTraps()
    baseline_tile = map_tiles.EmptyCavePath(1, 1, 2)
    protected_tile = map_tiles.EmptyCavePath(2, 1, 2)
    baseline_tile.trap_type = protected_tile.trap_type = "Tripwire"

    map_tiles.trigger_tile_trap(baseline_tile, baseline, rng=_TripwireRng())
    message = map_tiles.trigger_tile_trap(protected_tile, protected, rng=_TripwireRng())

    baseline_damage = baseline.health.max - baseline.health.current
    protected_damage = protected.health.max - protected.health.current
    assert protected_damage <= baseline_damage // 2
    assert "halves" in message


def test_magic_ward_uses_an_offensive_spell_and_magic_defense(monkeypatch):
    player = _player()
    tile = map_tiles.EmptyCavePath(1, 1, 3)
    tile.trap_type = "Magic Ward"
    monkeypatch.setattr(player, "damage_reduction", lambda damage, _source, typ: (True, "warded", damage // 2))
    rng = SimpleNamespace(
        random=lambda: 1.0,
        choice=lambda entries: entries[-1],
        randint=lambda low, _high: low,
    )

    message = map_tiles.trigger_tile_trap(tile, player, rng=rng)

    assert "Magic Ward casts Shadow Bolt" in message
    assert "Shadow damage" in message
    assert "warded" in message


def test_alert_forces_enemy_initiative(monkeypatch):
    player = _player()
    tile = map_tiles.EmptyCavePath(1, 1, 1)
    tile.trap_type = "Alert"
    enemy = enemies.Goblin()
    monkeypatch.setattr(
        "src.core.map_tiles.traps.quest_biased_random_enemy",
        lambda *_args, **_kwargs: enemy,
    )

    message = map_tiles.trigger_tile_trap(tile, player, rng=random.Random(1))
    engine = BattleEngine(player, enemy=enemy, tile=tile, rng=random.Random(2))
    first, _second = engine.start_battle()

    assert "has the initiative" in message
    assert first is enemy
    assert tile.trap_forced_initiative is False


def test_red_alert_uses_the_next_depth_enemy_pool(monkeypatch):
    player = _player()
    tile = map_tiles.EmptyCavePath(1, 1, 2)
    tile.trap_type = "Red Alert"
    requested = []
    enemy = enemies.Goblin()

    def fake_random_enemy(level, **_kwargs):
        requested.append(level)
        return enemy

    monkeypatch.setattr("src.core.map_tiles.traps.enemies.random_enemy", fake_random_enemy)
    message = map_tiles.trigger_tile_trap(tile, player, rng=random.Random(1))

    assert requested == ["3"]
    assert tile.enemy is enemy
    assert "stronger enemy" in message


def test_trap_type_and_triggered_state_round_trip_through_saves():
    tile = map_tiles.EmptyCavePath(1, 2, 3)
    tile.trap_type = "Magic Ward"
    tile.trap_triggered = True
    tile.deathcap_available = True
    tile.deathcap_gathered = True
    payload = TileStateSerializer.serialize_tile_state({(1, 2, 3): tile})
    restored = map_tiles.EmptyCavePath(1, 2, 3)

    TileStateSerializer.restore_tile_state({(1, 2, 3): restored}, payload)

    assert restored.trap_type == "Magic Ward"
    assert restored.trap_triggered is True
    assert restored.deathcap_available is True
    assert restored.deathcap_gathered is True
