from types import SimpleNamespace

from src.core import abilities, items
from src.core.classes import grandmaster
from src.core.combat.battle_engine import BattleEngine
from src.core.enemies import Enemy, Goblin
from src.core.map_tiles import actions_dict
from src.core.progression import (
    NodeState,
    available_nodes,
    ensure_progression,
    purchase_node,
)
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


def _unlock_weapon_art(player, weapon_type, node_id, xp):
    grandmaster.add_discipline_xp(player, weapon_type, xp)
    if player.cls.name == "Weapon Master":
        state = ensure_progression(player)
        state.level = max(35, state.level)
        state.unspent_points = max(1, state.unspent_points)
        result = purchase_node(player, node_id)
        assert result.success
    else:
        art_name = grandmaster.WEAPON_ARTS[weapon_type]
        art_class = {
            "Iron Palm": abilities.IronPalm,
            "Hemorrhage": abilities.Hemorrhage,
            "Riposte Line": abilities.RiposteLine,
            "Low Sweep": abilities.LowSweep,
            "Guard Cleaver": abilities.GuardCleaver,
            "Reaver's Mark": abilities.ReaversMark,
            "Brace": abilities.Brace,
            "Anvil Strike": abilities.AnvilStrike,
        }[art_name]
        player.spellbook["Skills"][art_name] = art_class()


def test_grandmaster_discipline_state_defaults_and_ranks():
    player = _grandmaster()

    assert player.ensure_grandmaster_discipline()["activated"] is False
    assert grandmaster.discipline_rank(player, "Sword") == 0

    before, after = grandmaster.add_discipline_xp(player, "Sword", grandmaster.XP_THRESHOLDS[-1])

    assert before == 0
    assert after == 10
    assert grandmaster.accuracy_bonus(player, "Sword") == 0.05
    assert grandmaster.proc_chance(player, "Sword") == 0.10


def test_weapon_master_rank_one_makes_tree_art_available_without_auto_learning():
    player = _weapon_master()
    player.equipment["Weapon"] = items.BrassKnuckles()

    player.grandmaster_discipline["disciplines"]["Fist"]["xp"] = grandmaster.XP_THRESHOLDS[0]
    player.ensure_grandmaster_discipline()
    ensure_progression(player).level = 35

    assert grandmaster.discipline_rank(player, "Fist") == 1
    assert "Iron Palm" not in player.spellbook["Skills"]
    status = next(
        status
        for status in available_nodes(player, "Weapon Master")
        if status.node.name == "Iron Palm"
    )
    assert status.state == NodeState.AVAILABLE


def test_weapon_art_descriptions_do_not_duplicate_tree_weapon_requirement():
    art = abilities.ReaversMark()

    assert art.required_weapon_type == "Battle Axe"
    assert not art.description.startswith("Requires:")


def test_weapon_art_requires_matching_weapon_and_applies_effect(monkeypatch):
    player = _weapon_master()
    player.equipment["Weapon"] = items.BrassKnuckles()
    enemy = Goblin()
    _unlock_weapon_art(
        player,
        "Fist",
        "weapon-master.ability.iron-palm",
        grandmaster.XP_THRESHOLDS[4],
    )
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
    _unlock_weapon_art(
        player,
        "Fist",
        "weapon-master.ability.iron-palm",
        grandmaster.XP_THRESHOLDS[-1],
    )
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


def test_weapon_hits_and_victory_award_discipline_xp(monkeypatch):
    player = _grandmaster()
    enemy = Goblin()
    enemy.level.pro_level = 2
    monkeypatch.setattr(grandmaster.random, "random", lambda: 0.0)

    player.record_grandmaster_weapon_hit("Sword", enemy)
    assert player.grandmaster_discipline["disciplines"]["Sword"]["xp"] == 1

    player.award_grandmaster_victory_xp(enemy)
    assert player.grandmaster_discipline["disciplines"]["Sword"]["xp"] == 4


def test_weapon_discipline_xp_chance_scales_by_enemy_pro_level_and_intellect(monkeypatch):
    player = _weapon_master()
    player.stats.intel = 10
    zero_enemy = Goblin()
    zero_enemy.level.pro_level = 0

    before, after, amount = player.record_grandmaster_weapon_hit("Sword", zero_enemy)

    assert (before, after, amount) == (0, 0, 0)
    assert player.grandmaster_discipline["disciplines"]["Sword"]["xp"] == 0
    assert player.award_grandmaster_victory_xp(zero_enemy) == {}

    weak_enemy = Goblin()
    weak_enemy.level.pro_level = 1
    baseline_enemy = Goblin()
    baseline_enemy.level.pro_level = 2
    assert grandmaster.discipline_xp_chance(player, weak_enemy, reason="hit") == (
        grandmaster.discipline_xp_chance(player, baseline_enemy, reason="hit") / 2
    )

    low_int = _weapon_master()
    low_int.stats.intel = 5
    high_int = _weapon_master()
    high_int.stats.intel = 18
    assert grandmaster.discipline_xp_chance(high_int, baseline_enemy, reason="hit") > grandmaster.discipline_xp_chance(
        low_int,
        baseline_enemy,
        reason="hit",
    )

    monkeypatch.setattr(grandmaster.random, "random", lambda: 1.0)
    player.record_grandmaster_weapon_hit("Sword", weak_enemy)
    assert player.grandmaster_discipline["disciplines"]["Sword"]["xp"] == 0

    monkeypatch.setattr(grandmaster.random, "random", lambda: 0.0)
    player.record_grandmaster_weapon_hit("Sword", weak_enemy)
    assert player.grandmaster_discipline["disciplines"]["Sword"]["xp"] == 1
    player.award_grandmaster_victory_xp(weak_enemy)
    assert player.grandmaster_discipline["disciplines"]["Sword"]["xp"] == 4


def test_weapon_master_battle_axe_hits_show_rank_progression_text(monkeypatch):
    player = _weapon_master()
    player.equipment["Weapon"] = items.Broadaxe()
    player.equipment["OffHand"] = items.NoOffHand()
    target = Goblin()
    target.level.pro_level = 2
    target.health.current = target.health.max = 999
    player.grandmaster_discipline["disciplines"]["Battle Axe"]["xp"] = grandmaster.XP_THRESHOLDS[0] - 1
    player.ensure_grandmaster_discipline()
    monkeypatch.setattr(grandmaster.random, "random", lambda: 0.0)

    message, hit, _crit = player.weapon_damage(target, hit=True, use_offhand=False)

    assert hit is True
    battle_axe = player.grandmaster_discipline["disciplines"]["Battle Axe"]
    assert battle_axe["xp"] == grandmaster.XP_THRESHOLDS[0]
    assert battle_axe["rank"] == 1
    assert "Battle Axe Discipline +1 XP" in message
    assert f"{grandmaster.XP_THRESHOLDS[0]}/{grandmaster.XP_THRESHOLDS[1]} XP" not in message
    assert "Battle Axe Discipline reached rank 1" in message
    assert "Reaver's Mark is now available in the Weapon Master ability tree" in message


def test_weapon_art_can_grant_discipline_insight(monkeypatch):
    player = _weapon_master()
    player.equipment["Weapon"] = items.BrassKnuckles()
    enemy = Goblin()
    enemy.level.pro_level = 2
    _unlock_weapon_art(
        player,
        "Fist",
        "weapon-master.ability.iron-palm",
        grandmaster.XP_THRESHOLDS[0],
    )
    before_xp = player.grandmaster_discipline["disciplines"]["Fist"]["xp"]
    monkeypatch.setattr(player, "weapon_damage", lambda *_args, **_kwargs: ("Iron Palm lands.\n", True, 1))
    monkeypatch.setattr(grandmaster.random, "random", lambda: 0.0)

    message = player.spellbook["Skills"]["Iron Palm"].use(player, enemy)

    assert player.grandmaster_discipline["disciplines"]["Fist"]["xp"] == before_xp + grandmaster.ART_XP
    assert f"Fist Discipline +{grandmaster.ART_XP} XP" in message


def test_normal_victory_reports_weapon_discipline_bonus_xp(monkeypatch):
    player = _weapon_master()
    enemy = Goblin()
    enemy.level.pro_level = 2
    monkeypatch.setattr(grandmaster.random, "random", lambda: 0.0)
    player.record_grandmaster_weapon_hit("Sword", enemy)
    enemy.health.current = 0
    tile = DummyTrialTile()
    engine = BattleEngine(player, enemy, tile)

    outcome = engine.end_battle()

    assert outcome.result == "victory"
    assert "Sword Discipline +3 XP" in outcome.message
    assert f"4/{grandmaster.XP_THRESHOLDS[0]} XP" not in outcome.message


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


def test_trial_victory_skips_normal_rewards_but_keeps_discipline_xp(monkeypatch):
    player = _grandmaster()
    enemy = Enemy("Trial Adept", 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, exp=999)
    enemy.level.pro_level = 2
    monkeypatch.setattr(grandmaster.random, "random", lambda: 0.0)
    player.record_grandmaster_weapon_hit("Sword", enemy)
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


def test_grandmaster_class_ring_description_names_activation_binding_and_equipped_effect():
    player = _grandmaster()

    dormant_description = player.equipment["Ring"].get_description(player)
    assert "dormant Class Ring for a Grandmaster of Arms" in dormant_description
    assert "Ring location: equipped" in dormant_description
    assert "Activation: Secret Master trial" in dormant_description
    assert "Active effect: inactive until awakened" in dormant_description

    grandmaster.add_discipline_xp(player, "Hammer", grandmaster.XP_THRESHOLDS[-1])
    grandmaster.bind_weapon(player, "Hammer")
    player.equipment["Ring"] = items.NoRing()
    player.storage = {"Class Ring": [items.ClassRing()]}

    stored_description = player.storage["Class Ring"][0].get_description(player)
    assert "awakened Class Ring for a Grandmaster of Arms" in stored_description
    assert "Ring location: stored" in stored_description
    assert "Bound weapon: Hammer" in stored_description
    assert "Active effect: equip the ring to use it" in stored_description

    player.equipment["Ring"] = items.ClassRing()
    player.storage = {}
    equipped_description = player.equipment["Ring"].get_description(player)
    assert "Ring location: equipped" in equipped_description
    assert "Bound weapon: Hammer" in equipped_description
    assert "+10% accuracy" in equipped_description
    assert "20% technique chance" in equipped_description
    assert "Active effect: active while equipped" in equipped_description


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
