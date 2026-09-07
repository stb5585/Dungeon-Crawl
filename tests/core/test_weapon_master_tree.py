"""Regression coverage for the authored Warrior and Weapon Master trees."""

from __future__ import annotations

import pytest

from src.core import abilities
from src.core import items
from src.core.character import defense as defense_module
from src.core.character import offense as offense_module
from src.core.classes import ability_mechanics
from src.core.classes import grandmaster
from src.core.progression import (
    ABILITY_TREES,
    NodeState,
    available_nodes,
    ensure_progression,
    purchase_node,
)
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


def _player(class_name: str = "Weapon Master", level: int = 60):
    player = TestGameState.create_player(
        class_name=class_name,
        race_name="Human",
        level=level,
        pro_level=2 if class_name == "Weapon Master" else 1,
        stats={
            "strength": 30,
            "intel": 18,
            "wisdom": 12,
            "con": 22,
            "charisma": 10,
            "dex": 26,
        },
    )
    state = ensure_progression(player)
    state.level = level
    state.unspent_points = 40
    return player


def test_warrior_replaces_dual_wield_with_level_twenty_cripple():
    tree = ABILITY_TREES["Warrior"]
    by_name = {node.name: node for node in tree.nodes}
    warrior = _player("Warrior", 20)

    assert "Dual Wield" not in by_name
    assert by_name["Cripple"].position == (0, 4)
    assert by_name["Cripple"].payload["level_requirement"] == 20
    assert by_name["True Strike"].prerequisites[0] == by_name["Cripple"].id
    assert warrior.cls.restrictions["OffHand"] == ["Shield"]
    warrior.spellbook["Skills"]["Dual Wield"] = abilities.DualWield()
    assert (
        ability_mechanics.can_dual_wield_item(
            warrior,
            items.Rondel(),
            "OffHand",
        )
        is False
    )


def test_weapon_master_layout_uses_distinct_routes_and_independent_weapon_arts():
    tree = ABILITY_TREES["Weapon Master"]
    by_name = {node.name: node for node in tree.nodes}
    arts = {
        "Iron Palm": ("Fist", 1),
        "Hemorrhage": ("Dagger", 1),
        "Riposte Line": ("Sword", 1),
        "Low Sweep": ("Club", 1),
        "Guard Cleaver": ("Longsword", 1),
        "Reaver's Mark": ("Battle Axe", 1),
        "Brace": ("Polearm", 1),
        "Anvil Strike": ("Hammer", 1),
    }
    upgrades = {f"{name} 2": (weapon_type, 5) for name, (weapon_type, _rank) in arts.items()}

    assert by_name["Double Strike"].lane == "Berserker"
    assert by_name["Mortal Strike"].lane == "Berserker"
    assert by_name["Devastating Throw"].lane == "Berserker"
    assert by_name["Two-Handed Weapon Proficiency"].lane == "Berserker"
    assert by_name["Two-Handed Weapon Proficiency"].position == (0, 2)
    assert by_name["Two-Handed Weapon Proficiency"].payload["level_requirement"] == 35
    assert (
        by_name["Two-Handed Weapon Proficiency"].payload["exclusive_group"] == "weapon-master.style"
    )
    assert by_name["Mortal Strike"].position == (0, 4)
    assert by_name["Brutish Strength"].lane == "Berserker"
    assert by_name["Brutish Strength"].prerequisites == (by_name["Devastating Throw"].id,)
    assert by_name["Parry"].lane == "Grandmaster"
    assert by_name["True Piercing Strike"].lane == "Grandmaster"
    assert by_name["True Piercing Strike"].payload["prerequisite_mode"] == "any"
    assert set(by_name["True Piercing Strike"].prerequisites) == {
        by_name["Cross Block"].id,
        by_name["Maim"].id,
    }
    assert "Disciplined Grip" not in by_name
    assert "Measured Guard" not in by_name
    assert "level_requirement" not in by_name["Double Strike"].payload
    assert "level_requirement" not in by_name["Parry"].payload
    assert by_name["+20 Attack"].payload["amount"] == 20
    assert by_name["+20 Defense"].payload["amount"] == 20
    assert "level_requirement" not in by_name["+20 Attack"].payload
    assert "level_requirement" not in by_name["+20 Defense"].payload
    assert by_name["Dual Wield"].payload["level_requirement"] == 35
    assert by_name["Honed Attack"].payload["level_requirement"] == 40
    assert by_name["Momentum"].payload["level_requirement"] == 45
    assert by_name["Cross Block"].payload["level_requirement"] == 50
    assert by_name["Duelist"].payload["level_requirement"] == 35
    assert by_name["Blind Fighting"].payload["level_requirement"] == 40
    assert by_name["Retort"].payload["level_requirement"] == 45
    assert by_name["Maim"].payload["level_requirement"] == 50
    assert by_name["True Piercing Strike"].payload["level_requirement"] == 55
    promotions = [node for node in tree.nodes if node.kind.value == "promotion"]
    assert {node.position[1] for node in promotions} == {7}
    for name, requirement in arts.items():
        assert by_name[name].position[0] == 3
        assert by_name[name].prerequisites == ()
        assert by_name[name].payload["weapon_specialization"] == requirement
        assert "level_requirement" not in by_name[name].payload
    for name, requirement in upgrades.items():
        base_name = name.removesuffix(" 2")
        assert by_name[name].position[0] == 4
        assert by_name[name].prerequisites == (by_name[base_name].id,)
        assert by_name[name].payload["weapon_specialization"] == requirement
        assert "level_requirement" not in by_name[name].payload
        assert by_name[name].payload["ability_class"].replaces == base_name


def test_inherited_warrior_entries_are_preowned_without_spending_points():
    player = _player()
    player.spellbook["Skills"]["Double Strike"] = abilities.DoubleStrike()
    player.spellbook["Skills"]["Parry"] = abilities.Parry()
    before = player.progression.unspent_points

    statuses = {status.node.name: status for status in available_nodes(player, "Weapon Master")}

    assert statuses["Double Strike"].state == NodeState.OWNED
    assert statuses["Parry"].state == NodeState.OWNED
    assert player.progression.unspent_points == before


def test_duelist_choice_closes_dual_wield_and_rejoins_at_true_piercing_strike():
    player = _player()
    player.spellbook["Skills"]["Parry"] = abilities.Parry()
    player.spellbook["Skills"]["Cripple"] = abilities.Cripple()
    available_nodes(player)

    for node_id in (
        "weapon-master.rating.defense-1",
        "weapon-master.ability.duelist",
        "weapon-master.ability.blind-fighting",
        "weapon-master.ability.retort",
        "weapon-master.ability.maim",
    ):
        assert purchase_node(player, node_id).success

    statuses = {status.node.name: status for status in available_nodes(player, "Weapon Master")}
    for name in ("Dual Wield", "Honed Attack", "Momentum", "Cross Block"):
        assert statuses[name].state == NodeState.CLOSED
    assert statuses["True Piercing Strike"].state == NodeState.AVAILABLE
    assert not purchase_node(player, "weapon-master.ability.dual-wield").success
    assert purchase_node(
        player,
        "weapon-master.ability.true-piercing-strike",
    ).success
    assert "Cripple" not in player.spellbook["Skills"]
    assert "Maim" in player.spellbook["Skills"]


def test_two_handed_choice_closes_both_other_weapon_master_styles():
    player = _player()
    player.spellbook["Skills"]["Double Strike"] = abilities.DoubleStrike()
    available_nodes(player)

    assert purchase_node(player, "weapon-master.rating.attack-1").success
    assert purchase_node(
        player,
        "weapon-master.ability.two-handed-weapon-proficiency",
    ).success

    statuses = {status.node.name: status for status in available_nodes(player, "Weapon Master")}
    for name in (
        "Dual Wield",
        "Honed Attack",
        "Momentum",
        "Cross Block",
        "Duelist",
        "Blind Fighting",
        "Retort",
        "Maim",
    ):
        assert statuses[name].state == NodeState.CLOSED


def test_weapon_art_requires_discipline_rank_and_is_not_auto_learned():
    player = _player(level=35)
    iron_palm_id = "weapon-master.ability.iron-palm"

    blocked = purchase_node(player, iron_palm_id)
    assert not blocked.success
    assert "Fist specialization level 1" in blocked.message

    grandmaster.add_discipline_xp(
        player,
        "Fist",
        grandmaster.XP_THRESHOLDS[0],
    )
    assert "Iron Palm" not in player.spellbook["Skills"]
    assert purchase_node(player, iron_palm_id).success
    assert "Iron Palm" in player.spellbook["Skills"]


def test_rank_five_weapon_art_upgrade_replaces_the_lower_ability():
    player = _player(level=35)
    base_id = "weapon-master.ability.iron-palm"
    upgrade_id = "weapon-master.ability.iron-palm-2"
    grandmaster.add_discipline_xp(
        player,
        "Fist",
        grandmaster.XP_THRESHOLDS[0],
    )
    assert purchase_node(player, base_id).success

    blocked = purchase_node(player, upgrade_id)
    assert not blocked.success
    assert "Fist specialization level 5" in blocked.message

    grandmaster.add_discipline_xp(
        player,
        "Fist",
        grandmaster.XP_THRESHOLDS[4] - grandmaster.XP_THRESHOLDS[0],
    )
    assert purchase_node(player, upgrade_id).success
    assert "Iron Palm" not in player.spellbook["Skills"]
    assert "Iron Palm 2" in player.spellbook["Skills"]


def test_berserker_passives_modify_two_handed_attacks_and_survive_save_load():
    player = _player()
    player.equipment["Weapon"] = items.Bastard()
    grandmaster.add_discipline_xp(
        player,
        "Longsword",
        grandmaster.XP_THRESHOLDS[4],
    )

    assert grandmaster.two_handed_accuracy_bonus(player, "Weapon") == 0.0
    assert grandmaster.two_handed_damage_multiplier(player, "Weapon") == 1.0
    assert grandmaster.brutish_critical_multiplier(player, "Longsword", 2.0) == 2.0

    for node_id in (
        "weapon-master.ability.double-strike",
        "weapon-master.rating.attack-1",
        "weapon-master.ability.two-handed-weapon-proficiency",
        "weapon-master.ability.mortal-strike",
        "weapon-master.ability.devastating-throw",
        "weapon-master.ability.brutish-strength",
    ):
        assert purchase_node(player, node_id).success

    assert grandmaster.two_handed_accuracy_bonus(player, "Weapon") == 0.10
    assert grandmaster.two_handed_damage_multiplier(player, "Weapon") == 1.10
    assert grandmaster.brutish_critical_multiplier(
        player,
        "Longsword",
        2.0,
    ) == pytest.approx(2.25)

    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(player),
        skip_tiles=True,
    )
    assert grandmaster.two_handed_accuracy_bonus(restored, "Weapon") == 0.10
    assert grandmaster.two_handed_damage_multiplier(restored, "Weapon") == 1.10
    assert grandmaster.brutish_critical_multiplier(
        restored,
        "Longsword",
        2.0,
    ) == pytest.approx(2.25)


def test_weapon_master_honed_attack_purchase_stacks_warrior_rank():
    player = _player()
    player.spellbook["Skills"]["Parry"] = abilities.Parry()
    player.spellbook["Skills"]["Honed Attack"] = abilities.HonedAttack()
    available_nodes(player)
    for node_id in (
        "weapon-master.rating.defense-1",
        "weapon-master.ability.dual-wield",
        "weapon-master.ability.honed-attack",
    ):
        assert purchase_node(player, node_id).success

    honed = player.spellbook["Skills"]["Honed Attack"]
    assert honed.ranks == 2
    assert player._honed_attack_critical_multiplier(1.5) == pytest.approx(1.75)

    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(player),
        skip_tiles=True,
    )
    assert restored.progression.ability_ranks["Honed Attack"] == 2
    assert restored.spellbook["Skills"]["Honed Attack"].ranks == 2
    assert restored._honed_attack_critical_multiplier(1.5) == pytest.approx(1.75)


def test_cripple_scales_melee_penalty_from_damage_dealt(monkeypatch):
    user = _player("Warrior", 20)
    target = _player("Warrior", 20)
    target.equipment["Weapon"] = items.Rapier()
    target.health.current = target.health.max = 100

    def attack(defender, **_kwargs):
        defender.health.current -= 30
        return "Crippling hit.\n", True, 1

    monkeypatch.setattr(user, "weapon_damage", attack)
    result = abilities.Cripple().use(user, target)

    assert result.hit is True
    assert result.damage == 30
    assert target.physical_effects["Cripple"].active is True
    assert target.physical_effects["Cripple"].extra == pytest.approx(0.30)


def test_cripple_effect_reduces_subsequent_melee_damage(monkeypatch):
    attacker = _player()
    defender = _player()
    attacker.equipment["Weapon"] = items.Rapier()
    defender.health.current = defender.health.max = 999
    monkeypatch.setattr(offense_module.random, "random", lambda: 1.0)
    monkeypatch.setattr(offense_module.random, "uniform", lambda _low, _high: 1.0)

    before = defender.health.current
    attacker.weapon_damage(defender, hit=True, use_offhand=False)
    normal_damage = before - defender.health.current
    defender.health.current = before
    cripple = attacker.physical_effects["Cripple"]
    cripple.active = True
    cripple.duration = 3
    cripple.extra = 0.30

    attacker.weapon_damage(defender, hit=True, use_offhand=False)
    crippled_damage = before - defender.health.current

    assert crippled_damage < normal_damage


def test_maim_uses_triple_critical_and_disables_main_hand(monkeypatch):
    user = _player()
    target = _player()
    target.equipment["Weapon"] = items.Rapier()
    captured = {}

    def attack(defender, **kwargs):
        captured.update(kwargs)
        defender.health.current -= 45
        return "Maiming hit.\n", True, 3

    monkeypatch.setattr(user, "weapon_damage", attack)
    result = abilities.Maim().use(user, target)

    assert captured["critical_multiplier"] == 3
    assert result.crit == 3
    assert target.physical_effects["Maim"].active is True
    message, hit, _crit = target.weapon_damage(user, hit=True, use_offhand=False)
    assert hit is False
    assert "cannot use their main-hand weapon" in message


def test_devastating_throw_disarms_user_after_massive_attack(monkeypatch):
    user = _player()
    target = _player()
    user.equipment["Weapon"] = items.Rapier()
    captured = {}

    def attack(defender, **kwargs):
        captured.update(kwargs)
        defender.health.current -= 50
        return "Thrown weapon hits.\n", True, 2

    monkeypatch.setattr(user, "weapon_damage", attack)
    result = abilities.DevastatingThrow().use(user, target)

    assert captured["dmg_mod"] == 2.50
    assert captured["use_offhand"] is False
    assert result.damage == 50
    assert user.physical_effects["Disarm"].active is True


def test_duelist_and_retort_bonuses_require_their_passives():
    player = _player()
    player.equipment["Weapon"] = items.Rapier()
    player.equipment["OffHand"] = items.NoOffHand()

    assert ability_mechanics.duelist_style_active(player) is False
    player.spellbook["Skills"]["Duelist"] = abilities.Duelist()
    assert ability_mechanics.duelist_accuracy_bonus(player) == 0.10
    assert ability_mechanics.duelist_critical_bonus(player) == 0.10
    assert ability_mechanics.duelist_damage_multiplier(player) == 1.10

    assert ability_mechanics.retort_parry_bonus(player) == 0.0
    player.spellbook["Skills"]["Retort"] = abilities.Retort()
    assert ability_mechanics.retort_parry_bonus(player) == 0.08
    assert ability_mechanics.retort_counter_multiplier(player) == 1.0

    player.equipment["OffHand"] = items.Buckler()
    assert ability_mechanics.duelist_style_active(player) is False


def test_blind_fighting_halves_blind_accuracy_penalty(monkeypatch):
    attacker = _player()
    defender = _player()
    attacker.status_effects["Blind"].active = True
    monkeypatch.setattr(
        offense_module.random,
        "randint",
        lambda _low, high: high,
    )

    ordinary_blind_chance = attacker.hit_chance(defender)
    attacker.spellbook["Skills"]["Blind Fighting"] = abilities.BlindFighting()
    trained_blind_chance = attacker.hit_chance(defender)

    assert trained_blind_chance > ordinary_blind_chance


def test_cross_block_profile_uses_both_weapons_and_strength():
    player = _player()
    player.spellbook["Skills"]["Cross Block"] = abilities.CrossBlock()
    player.equipment["Weapon"] = items.Rapier()
    player.equipment["OffHand"] = items.Rondel()

    chance, mitigation = ability_mechanics.cross_block_profile(player)

    assert chance > 0.10
    assert mitigation > 0.25


def test_complete_cross_block_disarms_attacker(monkeypatch):
    attacker = _player()
    defender = _player()
    attacker.equipment["Weapon"] = items.Rapier()
    defender.equipment["Weapon"] = items.Rapier()
    defender.equipment["OffHand"] = items.Rondel()
    defender.spellbook["Skills"]["Cross Block"] = abilities.CrossBlock()
    defender.stats.strength = 100
    monkeypatch.setattr(defense_module.random, "random", lambda: 0.0)
    health_before = defender.health.current

    message, hit, _crit = attacker.weapon_damage(
        defender,
        hit=True,
        use_offhand=False,
    )

    assert hit is False
    assert defender.health.current == health_before
    assert "Cross Block completely stops" in message
    assert attacker.physical_effects["Disarm"].active is True


def test_momentum_requires_two_weapons_and_adds_finisher(monkeypatch):
    user = _player()
    target = _player()
    user.equipment["Weapon"] = items.Rapier()
    user.equipment["OffHand"] = items.Rondel()
    calls = []

    def attack(defender, **kwargs):
        calls.append(kwargs)
        defender.health.current -= 10
        return "Hit.\n", True, 1

    monkeypatch.setattr(user, "weapon_damage", attack)
    result = abilities.Momentum().use(user, target)

    assert result.hit is True
    assert result.damage == 30
    assert [call["attack_slots"] for call in calls] == [
        ("Weapon",),
        ("OffHand",),
        ("Weapon",),
    ]
    assert "two-handed finisher" in result.message
