"""Regression coverage for Berserker and Grandmaster authored trees."""

from __future__ import annotations

import pytest

from src.core import abilities
from src.core import items
from src.core.classes import ability_mechanics
from src.core.classes import grandmaster
from src.core.combat.battle_engine import BattleEngine
from src.core.progression import (
    ABILITY_TREES,
    NodeKind,
    ensure_progression,
    purchase_node,
)
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


class _CombatTile:
    def available_actions(self, _player):
        return ["Attack"]


def _player(class_name: str):
    player = TestGameState.create_player(
        class_name=class_name,
        race_name="Human",
        level=100,
        pro_level=3,
        stats={
            "strength": 30,
            "intel": 20,
            "wisdom": 15,
            "con": 25,
            "charisma": 12,
            "dex": 28,
        },
    )
    state = ensure_progression(player)
    state.level = 100
    state.unspent_points = 60
    return player


def test_berserker_tree_has_centered_development_and_heavy_weapon_arts():
    tree = ABILITY_TREES["Berserker"]
    by_name = {node.name: node for node in tree.nodes}
    expected_positions = {
        "Final Assault": (0, 1),
        "Frenzy": (1, 1),
        "Monkey Grip 1": (0, 2),
        "+30 Attack": (0, 3),
        "+100 HP": (1, 2),
        "Mortal Strike 2": (1, 3),
        "Reckless Onslaught": (0, 4),
        "Boomerang Toss": (1, 4),
        "Monkey Grip 2": (0, 5),
        "Triple Strike": (1, 5),
        "Parry": (2, 2),
        "Pain Tolerance": (2, 3),
        "Hemorrhage Thirst": (2, 4),
    }
    expected_levels = {
        "Monkey Grip 1": 65,
        "Mortal Strike 2": 65,
        "Pain Tolerance": 65,
        "Hemorrhage Thirst": 70,
        "Reckless Onslaught": 70,
        "Boomerang Toss": 70,
        "Monkey Grip 2": 75,
        "Triple Strike": 75,
    }

    assert "Bloodied Ferocity" not in by_name
    assert "Scarred Endurance" not in by_name
    for name, position in expected_positions.items():
        assert by_name[name].position == position
    assert "level_requirement" not in by_name["Final Assault"].payload
    assert "level_requirement" not in by_name["Frenzy"].payload
    assert "level_requirement" not in by_name["Parry"].payload
    assert by_name["Hemorrhage Thirst"].payload["ability_class"]().passive is True
    assert by_name["+30 Attack"].payload["amount"] == 30
    assert by_name["+100 HP"].payload["amount"] == 100
    assert by_name["Reckless Onslaught"].prerequisites == (
        by_name["+30 Attack"].id,
    )
    assert by_name["Monkey Grip 2"].prerequisites == (
        by_name["Reckless Onslaught"].id,
    )
    assert (
        by_name["Reckless Onslaught"].payload["ability_class"].replaces
        == "Final Assault"
    )
    for name, level in expected_levels.items():
        assert by_name[name].payload["level_requirement"] == level

    art_nodes = [
        node
        for node in tree.nodes
        if node.payload.get("weapon_specialization")
    ]
    assert len(art_nodes) == 8
    assert {
        node.payload["weapon_specialization"][0]
        for node in art_nodes
    } == grandmaster.TWO_HANDED_WEAPONS
    assert all("level_requirement" not in node.payload for node in art_nodes)
    assert {node.position[1] for node in art_nodes} == {2, 3, 4, 5}


def test_grandmaster_tree_has_three_rank_gated_art_levels_and_floating_talents():
    tree = ABILITY_TREES["Grandmaster of Arms"]
    by_name = {node.name: node for node in tree.nodes}
    art_nodes = [
        node
        for node in tree.nodes
        if node.payload.get("weapon_specialization")
    ]

    assert len(art_nodes) == 24
    assert {node.payload["weapon_specialization"][1] for node in art_nodes} == {
        1,
        5,
        10,
    }
    assert all("level_requirement" not in node.payload for node in art_nodes)
    for base_name in grandmaster.WEAPON_ARTS.values():
        assert by_name[f"{base_name} 2"].prerequisites == (
            by_name[base_name].id,
        )
        assert by_name[f"{base_name} 3"].prerequisites == (
            by_name[f"{base_name} 2"].id,
        )
        assert (
            by_name[f"{base_name} 3"].payload["ability_class"].replaces
            == f"{base_name} 2"
        )

    perfect_form = by_name["Perfect Form"]
    adaptive_arsenal = by_name["Adaptive Arsenal"]
    double_strike = by_name["Double Strike"]
    assert perfect_form.kind == NodeKind.TALENT
    assert adaptive_arsenal.kind == NodeKind.TALENT
    assert perfect_form.prerequisites == ()
    assert adaptive_arsenal.prerequisites == ()
    assert "level_requirement" not in perfect_form.payload
    assert "level_requirement" not in adaptive_arsenal.payload
    assert "level_requirement" not in double_strike.payload
    assert double_strike.payload["owned_if_known"] is True
    assert (
        perfect_form.position[0]
        == adaptive_arsenal.position[0]
        == double_strike.position[0]
        == 3
    )
    assert (
        perfect_form.position[1]
        < double_strike.position[1]
        < adaptive_arsenal.position[1]
    )


def test_frenzy_forces_three_turn_berserk_and_adds_critical_chance():
    player = _player("Berserker")
    player.equipment["Weapon"] = items.Bastard()
    before = player.critical_chance("Weapon")

    result = abilities.Frenzy().use(player)

    berserk = player.status_effects["Berserk"]
    assert result.message
    assert berserk.active is True
    assert berserk.duration == 3
    assert berserk.source == "Frenzy"
    assert player.critical_chance("Weapon") == pytest.approx(before + 0.15)


def test_reckless_onslaught_stacks_tradeoff_and_prones_user_when_parried(
    monkeypatch,
):
    player = _player("Berserker")
    target = _player("Grandmaster of Arms")
    player.equipment["Weapon"] = items.Bastard()
    player.mana.current = 100
    damage_modifiers = []

    def attack(defender, **kwargs):
        damage_modifiers.append(kwargs["dmg_mod"])
        player._last_attack_parried = len(damage_modifiers) == 1
        defender.health.current -= 20
        return "Onslaught attack.\n", True, 1

    monkeypatch.setattr(player, "weapon_damage", attack)
    ability = abilities.RecklessOnslaught()

    first = ability.use(player, target)
    first_message = first.message
    first_damage = first.damage
    second = ability.use(player, target)

    assert damage_modifiers == [2.0, 2.0]
    assert first_damage == 20
    assert second.damage == 20
    assert player.stat_effects["Attack"].extra == 10
    assert player.stat_effects["Defense"].extra == -10
    assert player.stat_effects["Attack"].duration == 3
    assert player.stat_effects["Defense"].duration == 3
    assert player.physical_effects["Prone"].active is True
    assert player.physical_effects["Prone"].duration == 2
    assert "knocked prone" in first_message


def test_reckless_onslaught_purchase_replaces_final_assault():
    player = _player("Berserker")

    assert purchase_node(
        player,
        "berserker.ability.final-assault",
    ).success
    assert "Final Assault" in player.spellbook["Skills"]

    for node_id in (
        "berserker.ability.monkey-grip",
        "berserker.rating.attack-1",
        "berserker.ability.reckless-onslaught",
    ):
        assert purchase_node(player, node_id).success
    assert "Final Assault" not in player.spellbook["Skills"]
    assert "Reckless Onslaught" in player.spellbook["Skills"]

    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(player),
        skip_tiles=True,
    )
    assert "Final Assault" not in restored.spellbook["Skills"]
    assert "Reckless Onslaught" in restored.spellbook["Skills"]


def test_parry_outcome_is_exposed_to_reckless_onslaught(monkeypatch):
    attacker = _player("Berserker")
    defender = _player("Grandmaster of Arms")
    defender.spellbook["Skills"]["Parry"] = abilities.Parry()
    attacker._last_attack_parried = False
    monkeypatch.setattr(
        "src.core.character.offense.random.random",
        lambda: 0.0,
    )
    monkeypatch.setattr(
        defender,
        "weapon_damage",
        lambda *_args, **_kwargs: ("Counterattack.\n", True, 1),
    )

    message, aborted = attacker._handle_dodge(
        defender,
        damage=10,
        typ="attacks",
    )

    assert aborted is False
    assert attacker._last_attack_parried is True
    assert "parries" in message


def test_pain_tolerance_reduces_bleed_effects_and_doubles_bandage_healing(
    monkeypatch,
):
    player = _player("Berserker")
    assert ability_mechanics.pain_tolerance_bleed_multiplier(player) == 1.0
    assert ability_mechanics.bandage_healing_multiplier(player) == 1.0
    player.spellbook["Skills"]["Pain Tolerance"] = abilities.PainTolerance()
    assert ability_mechanics.pain_tolerance_bleed_multiplier(player) == 0.50
    assert ability_mechanics.bandage_healing_multiplier(player) == 2.0

    bandage = items.Bandage()
    player.inventory["Bandage"] = [bandage]
    player.health.max = 200
    player.health.current = 100
    bleed = player.physical_effects["Bleed"]
    bleed.active = True
    bleed.duration = 2
    bleed.extra = 10
    monkeypatch.setattr(
        "src.core.items.consumables.random.randint",
        lambda _low, high: high,
    )

    bandage.use(player)

    assert player.health.current == 140
    assert bleed.active is False


def test_hemorrhage_thirst_heals_bleed_and_crashes_after_three_turns():
    player = _player("Berserker")
    enemy = _player("Grandmaster of Arms")
    player.health.current = 100
    player.spellbook["Skills"]["Hemorrhage Thirst"] = (
        abilities.HemorrhageThirst()
    )
    bleed = enemy.physical_effects["Bleed"]
    bleed.active = True
    bleed.duration = 4
    bleed.extra = 20
    enemy.stats.con = 0
    engine = BattleEngine(player, enemy, _CombatTile())
    engine.attacker = enemy
    engine.defender = player

    results = [engine.pre_turn() for _turn in range(3)]

    assert player.health.current == 145
    assert all("restores 15 health" in result.effects_text for result in results)
    assert player.status_effects["Sleep"].active is True
    assert player.status_effects["Sleep"].duration == 2
    assert player.status_effects["Sleep"].source == "Hemorrhage Thirst"
    assert player._hemorrhage_thirst_streak == 0
    assert "unconscious for two turns" in results[-1].effects_text


def test_hemorrhage_thirst_has_no_effect_before_purchase_and_survives_save():
    player = _player("Berserker")
    player.health.current = 100

    assert ability_mechanics.trigger_hemorrhage_thirst(player, 20) == ""
    assert player.health.current == 100
    assert purchase_node(
        player,
        "berserker.ability.hemorrhage-thirst",
    ).success

    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(player),
        skip_tiles=True,
    )
    assert "Hemorrhage Thirst" in restored.spellbook["Skills"]
    ability_mechanics.trigger_hemorrhage_thirst(restored, 20)
    assert restored.health.current == 120
    ability_mechanics.trigger_hemorrhage_thirst(restored, 0)
    assert restored._hemorrhage_thirst_streak == 0
    ability_mechanics.trigger_hemorrhage_thirst(restored, 10)
    ability_mechanics.trigger_hemorrhage_thirst(restored, 10)
    assert restored._hemorrhage_thirst_streak == 2
    assert restored.status_effects["Sleep"].active is False


def test_boomerang_toss_turns_devastating_throw_into_returning_multi_hit(
    monkeypatch,
):
    player = _player("Berserker")
    target = _player("Grandmaster of Arms")
    player.equipment["Weapon"] = items.Bastard()
    player.spellbook["Skills"]["Boomerang Toss"] = abilities.BoomerangToss()
    calls = []

    def attack(defender, **kwargs):
        calls.append(kwargs)
        defender.health.current -= 10
        return "Boomerang hit.\n", True, 1

    monkeypatch.setattr(player, "weapon_damage", attack)
    result = abilities.DevastatingThrow().use(player, target)

    assert len(calls) == 3
    assert result.damage == 30
    assert player.physical_effects["Disarm"].active is False
    assert "returns to hand" in result.message


def test_grandmaster_mastery_talents_scale_with_equipped_discipline():
    player = _player("Grandmaster of Arms")
    player.equipment["Weapon"] = items.Bastard()
    grandmaster.add_discipline_xp(
        player,
        "Longsword",
        grandmaster.XP_THRESHOLDS[-1],
    )

    assert grandmaster.perfect_form_accuracy_bonus(player, "Longsword") == 0.0
    assert grandmaster.perfect_form_damage_multiplier(player, "Longsword") == 1.0
    assert grandmaster.adaptive_arsenal_parry_bonus(player) == 0.0
    assert grandmaster.adaptive_arsenal_counter_crit_chance(player) == 0.0

    assert purchase_node(
        player,
        "grandmaster-of-arms.talent.perfect-form",
    ).success
    assert purchase_node(
        player,
        "grandmaster-of-arms.talent.adaptive-arsenal",
    ).success

    assert grandmaster.perfect_form_accuracy_bonus(
        player,
        "Longsword",
    ) == pytest.approx(0.05)
    assert grandmaster.perfect_form_damage_multiplier(
        player,
        "Longsword",
    ) == pytest.approx(1.10)
    assert grandmaster.adaptive_arsenal_parry_bonus(player) == pytest.approx(
        0.05,
    )
    assert grandmaster.adaptive_arsenal_counter_crit_chance(
        player,
    ) == pytest.approx(0.10)

    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(player),
        skip_tiles=True,
    )
    assert grandmaster.perfect_form_damage_multiplier(
        restored,
        "Longsword",
    ) == pytest.approx(1.10)
    assert grandmaster.adaptive_arsenal_parry_bonus(restored) == pytest.approx(
        0.05,
    )


def test_grandmaster_rank_ten_art_replaces_level_two_and_survives_sync():
    player = _player("Grandmaster of Arms")
    grandmaster.add_discipline_xp(
        player,
        "Fist",
        grandmaster.XP_THRESHOLDS[-1],
    )
    for node_id in (
        "grandmaster-of-arms.ability.iron-palm",
        "grandmaster-of-arms.ability.iron-palm-2",
        "grandmaster-of-arms.ability.iron-palm-3",
    ):
        assert purchase_node(player, node_id).success

    assert "Iron Palm" not in player.spellbook["Skills"]
    assert "Iron Palm 2" not in player.spellbook["Skills"]
    assert "Iron Palm 3" in player.spellbook["Skills"]
    grandmaster.sync_weapon_art_skills(player)
    assert "Iron Palm 3" in player.spellbook["Skills"]
