from types import SimpleNamespace

from src.core import items
from src.core.classes import grandmaster
from src.core.combat.battle_engine import BattleEngine
from src.core.enemies import Enemy, Goblin
from src.core.map_tiles import actions_dict
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


class DummyTrialTile:
    enemy = None

    def __str__(self):
        return "GrandmasterTrialTile"

    def available_actions(self, _player):
        return [actions_dict["CharacterMenu"]]


def _grandmaster():
    player = TestGameState.create_player(
        class_name="Grandmaster of Arms",
        race_name="Human",
        level=60,
        pro_level=3,
        stats={"strength": 25, "intel": 10, "wisdom": 10, "con": 20, "charisma": 10, "dex": 24},
    )
    player.equipment["Ring"] = items.ClassRing()
    return player


def _weapon_master():
    player = TestGameState.create_player(
        class_name="Weapon Master",
        race_name="Human",
        level=30,
        pro_level=2,
        stats={"strength": 25, "intel": 10, "wisdom": 10, "con": 20, "charisma": 10, "dex": 24},
    )
    player.equipment["Ring"] = items.ClassRing()
    return player


def test_grandmaster_discipline_state_defaults_and_ranks():
    player = _grandmaster()

    assert player.ensure_grandmaster_discipline()["activated"] is False
    assert grandmaster.discipline_rank(player, "Sword") == 0

    before, after = grandmaster.add_discipline_xp(player, "Sword", grandmaster.XP_THRESHOLDS[-1])

    assert before == 0
    assert after == 10
    assert grandmaster.accuracy_bonus(player, "Sword") == 0.05
    assert grandmaster.proc_chance(player, "Sword") == 0.10


def test_weapon_master_starts_discipline_and_unlocks_rank_one_art():
    player = _weapon_master()
    player.equipment["Weapon"] = items.BrassKnuckles()

    before, after = player.record_grandmaster_weapon_hit("Fist")

    assert (before, after) == (0, 0)
    player.grandmaster_discipline["disciplines"]["Fist"]["xp"] = grandmaster.XP_THRESHOLDS[0]
    player.ensure_grandmaster_discipline()

    assert grandmaster.discipline_rank(player, "Fist") == 1
    assert "Iron Palm" in player.spellbook["Skills"]
    assert player.spellbook["Skills"]["Iron Palm"].cost == grandmaster.ART_COSTS["Fist"]


def test_weapon_art_requires_matching_weapon_and_applies_effect(monkeypatch):
    player = _weapon_master()
    player.equipment["Weapon"] = items.BrassKnuckles()
    enemy = Goblin()
    grandmaster.add_discipline_xp(player, "Fist", grandmaster.XP_THRESHOLDS[4])
    monkeypatch.setattr(grandmaster.random, "random", lambda: 1.0)

    message = player.spellbook["Skills"]["Iron Palm"].use(player, enemy)

    assert "Iron Palm" in message
    assert player.mana.current == player.mana.max - grandmaster.ART_COSTS["Fist"]
    assert enemy.stat_effects["Attack"].active is True
    assert enemy.stat_effects["Attack"].extra < 0


def test_perfect_bound_art_adds_grandmaster_ring_bonus(monkeypatch):
    player = _grandmaster()
    player.equipment["Weapon"] = items.BrassKnuckles()
    enemy = Goblin()
    grandmaster.add_discipline_xp(player, "Fist", grandmaster.XP_THRESHOLDS[-1])
    grandmaster.bind_weapon(player, "Fist")
    monkeypatch.setattr(grandmaster.random, "random", lambda: 1.0)

    message = player.spellbook["Skills"]["Iron Palm"].use(player, enemy)

    assert "Iron Palm" in message
    assert player.stat_effects["Defense"].active is True
    assert player.stat_effects["Defense"].extra >= 6


def test_bound_class_ring_doubles_chosen_weapon_bonus():
    player = _grandmaster()
    grandmaster.add_discipline_xp(player, "Sword", grandmaster.XP_THRESHOLDS[-1])
    grandmaster.bind_weapon(player, "Sword")
    player.equipment["Ring"].class_mod(player)

    assert player.equipment["Ring"].mod == "Sword Discipline x2"
    assert grandmaster.accuracy_bonus(player, "Sword") == 0.10
    assert grandmaster.proc_chance(player, "Sword") == 0.20
    assert grandmaster.accuracy_bonus(player, "Dagger") == 0.0
    assert "bound to Sword Discipline" in player.equipment["Ring"].get_description(player)


def test_weapon_hits_and_victory_award_discipline_xp():
    player = _grandmaster()

    player.record_grandmaster_weapon_hit("Sword")
    assert player.grandmaster_discipline["disciplines"]["Sword"]["xp"] == 1

    player.award_grandmaster_victory_xp()
    assert player.grandmaster_discipline["disciplines"]["Sword"]["xp"] == 4


def test_one_handed_technique_stacks_cap_and_refresh(monkeypatch):
    player = _grandmaster()
    target = Goblin()
    grandmaster.add_discipline_xp(player, "Fist", grandmaster.XP_THRESHOLDS[-1])
    grandmaster.bind_weapon(player, "Fist")
    monkeypatch.setattr(grandmaster.random, "random", lambda: 0.0)

    for _ in range(5):
        grandmaster.apply_weapon_technique(player, target, "Fist")

    entry = target.grandmaster_technique_stacks["Fist Stagger"]
    assert entry == {"stacks": 3, "duration": 3}
    assert target.stat_effects["Attack"].extra == -6

    grandmaster.tick_technique_stacks(target)
    assert target.grandmaster_technique_stacks["Fist Stagger"]["duration"] == 2


def test_two_handed_technique_refreshes_without_stacking(monkeypatch):
    player = _grandmaster()
    target = Goblin()
    grandmaster.add_discipline_xp(player, "Hammer", grandmaster.XP_THRESHOLDS[-1])
    grandmaster.bind_weapon(player, "Hammer")
    monkeypatch.setattr(grandmaster.random, "random", lambda: 0.0)

    grandmaster.apply_weapon_technique(player, target, "Hammer")
    target.stat_effects["Defense"].duration = 1
    grandmaster.apply_weapon_technique(player, target, "Hammer")

    assert target.stat_effects["Defense"].duration == 3
    assert target.stat_effects["Defense"].extra == -8
    assert not hasattr(target, "grandmaster_technique_stacks")


def test_trial_victory_skips_normal_rewards_but_keeps_discipline_xp():
    player = _grandmaster()
    player.record_grandmaster_weapon_hit("Sword")
    enemy = Enemy("Trial Adept", 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, exp=999)
    enemy.gold = 500
    enemy.inventory = {"Class Ring": [items.ClassRing]}
    enemy.enemy_typ = "Trial"
    enemy.grandmaster_trial_enemy = True
    tile = DummyTrialTile()
    engine = BattleEngine(player, enemy, tile)

    outcome = engine.end_battle()

    assert outcome.result == "victory"
    assert "Secret Master bout" in outcome.message
    assert player.level.exp == 0
    assert player.gold == 10000
    assert player.kill_dict == {}
    assert player.inventory == {}
    assert player.grandmaster_discipline["disciplines"]["Sword"]["xp"] == 4


def test_sergeant_recognizes_equipped_or_stored_ring_only():
    player = _grandmaster()
    player.equipment["Ring"] = items.NoRing()
    player.inventory = {"Class Ring": [items.ClassRing()]}
    player.storage = {}

    assert grandmaster.ring_visible_for_sergeant(player) is False

    player.storage = {"Class Ring": [items.ClassRing()]}
    assert grandmaster.ring_visible_for_sergeant(player) is True

    player.storage = {}
    player.equipment["Ring"] = items.ClassRing()
    assert grandmaster.ring_visible_for_sergeant(player) is True


def test_grandmaster_discipline_save_round_trip():
    player = _grandmaster()
    grandmaster.add_discipline_xp(player, "Hammer", grandmaster.XP_THRESHOLDS[-1])
    grandmaster.bind_weapon(player, "Hammer")

    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(player),
        skip_tiles=True,
    )

    assert restored.grandmaster_discipline["activated"] is True
    assert restored.grandmaster_discipline["bound_weapon"] == "Hammer"
    assert restored.grandmaster_discipline["disciplines"]["Hammer"]["rank"] == 10
