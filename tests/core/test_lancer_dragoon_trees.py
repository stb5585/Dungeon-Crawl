"""Focused coverage for authored Lancer and Dragoon progression."""

from __future__ import annotations

import pytest

from src.core import abilities
from src.core import items
from src.core.classes import class_rings
from src.core.classes import promotion_kits
from src.core.combat.combat_result import CombatResult
from src.core.effects.special import JumpEffect
from src.core.progression import ABILITY_TREES
from src.core.progression import NodeKind
from src.core.progression import ProgressionState
from src.core.progression import apply_progression_plan
from src.core.progression import available_nodes
from src.core.progression import ensure_progression
from src.core.progression import progression_points_through_level
from src.core.progression import purchase_node
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


def _player(class_name: str, *, level: int = 100):
    player = TestGameState.create_player(
        class_name=class_name,
        race_name="Human",
        level=level,
        health=(500, 500),
        mana=(200, 200),
        stats={
            "strength": 30,
            "intel": 20,
            "wisdom": 20,
            "con": 30,
            "charisma": 20,
            "dex": 30,
        },
    )
    player.progression = ProgressionState(
        level=level,
        unspent_points=100,
        unspent_attribute_points=100,
    )
    return player


def _tree_by_name(class_name: str):
    return {
        node.name: node
        for node in ABILITY_TREES[class_name].nodes
    }


def _prerequisite_closure(class_name: str, node_name: str) -> set[str]:
    tree = ABILITY_TREES[class_name]
    node_map = {node.id: node for node in tree.nodes}
    selected: set[str] = set()

    def add(node_id: str) -> None:
        if node_id in selected:
            return
        node = node_map[node_id]
        for prerequisite_id in node.prerequisites:
            add(prerequisite_id)
        selected.add(node_id)

    add(_tree_by_name(class_name)[node_name].id)
    return selected


def test_authored_lancer_tree_has_locked_graph_and_stable_ids():
    tree = ABILITY_TREES["Lancer"]
    nodes = _tree_by_name("Lancer")
    development = [node for node in tree.nodes if node.kind != NodeKind.PROMOTION]

    assert len(development) == 16
    assert nodes["Jump"].id == "lancer.ability.jump"
    assert nodes["Aerial Footwork"].prerequisites == (nodes["Jump"].id,)
    assert nodes["Aerial Footwork"].payload["level_requirement"] == 35
    assert nodes["Grounded Landing"].prerequisites == (nodes["Acrobat"].id,)
    assert nodes["Grounded Landing"].payload["level_requirement"] == 45
    assert nodes["Polearm Proficiency"].prerequisites == ()
    assert nodes["Lance Sweep"].payload["level_requirement"] == 35
    assert nodes["+50 HP"].prerequisites == (nodes["Lance Sweep"].id,)
    assert nodes["+50 HP"].position == (4, 2)
    assert nodes["Zephyrstrike"].prerequisites == (nodes["+50 HP"].id,)
    assert nodes["Zephyrstrike"].payload["level_requirement"] == 40
    assert "level_requirement" not in nodes["+20 Defense"].payload
    assert nodes["+20 Defense"].prerequisites == (nodes["Jump"].id,)
    assert nodes["+20 Attack"].prerequisites == (nodes["+20 Defense"].id,)
    assert nodes["Thrust"].prerequisites == (nodes["Quick Dive"].id,)
    assert nodes["Defend"].id == "lancer.jump-mod.defend"
    assert nodes["Acrobat"].id == "lancer.jump-mod.acrobat"
    assert nodes["Acrobat"].payload["level_requirement"] == 40
    assert nodes["Quick Dive"].id == "lancer.jump-mod.quick-dive"
    assert nodes["Thrust"].id == "lancer.jump-mod.thrust"
    assert nodes["Thrust"].position == (2, 3)
    assert nodes["Thrust"].payload["level_requirement"] == 45
    assert nodes["Rend"].id == "lancer.jump-mod.rend"
    assert nodes["Rend"].position == (2, 4)
    assert nodes["Rend"].payload["level_requirement"] == 50
    assert nodes["Jump"].position == (1, 0)
    assert nodes["Polearm Proficiency"].position == (4, 0)
    assert nodes["+20 Defense"].position == (1, 2)
    assert nodes["+20 Attack"].position == (1, 3)
    assert nodes["Parry"].position == (5, 2)
    assert nodes["Parry"].prerequisites == ()
    assert nodes["True Strike"].position == (5, 3)
    assert nodes["True Strike"].prerequisites == ()
    assert nodes["Promote: Dragoon"].position == (1, 6)
    assert nodes["Promote: Dragoon"].prerequisites == (
        nodes["+20 Attack"].id,
    )
    assert nodes["Promote: Dragoon"].payload["level_requirement"] == 60
    assert nodes["Promote: Dragoon"].payload["requirements"] == {
        "strength": 17,
        "dex": 13,
    }
    assert nodes["Promote: Dragoon"].cost == 3
    assert max(node.position[1] for node in tree.nodes) == 6


def test_authored_dragoon_tree_has_locked_graph_and_stable_ids():
    tree = ABILITY_TREES["Dragoon"]
    nodes = _tree_by_name("Dragoon")
    lancer_development_ids = {
        node.id
        for node in ABILITY_TREES["Lancer"].nodes
        if node.kind != NodeKind.PROMOTION
    }

    assert len(tree.nodes) == 27
    assert lancer_development_ids <= {node.id for node in tree.nodes}
    assert "lancer.promotion.dragoon" not in {
        node.id
        for node in tree.nodes
    }
    assert nodes["Polearm Excellence"].position == (4, 5)
    assert nodes["Polearm Excellence"].prerequisites == ()
    assert nodes["Grounded Landing"].prerequisites == (nodes["Acrobat"].id,)
    assert nodes["+20 Defense"].prerequisites == (nodes["Jump"].id,)
    assert nodes["+20 Attack"].prerequisites == (nodes["+20 Defense"].id,)
    assert nodes["Thrust"].prerequisites == (nodes["Quick Dive"].id,)
    assert nodes["+30 Attack"].prerequisites == (
        nodes["Polearm Excellence"].id,
    )
    assert nodes["True Piercing Strike"].position == (4, 7)
    assert nodes["True Piercing Strike"].payload["level_requirement"] == 70
    assert nodes["True Piercing Strike"].prerequisites == (
        nodes["+30 Attack"].id,
    )
    assert nodes["+30 Attack"].position == (4, 6)
    assert nodes["Polearm Mastery"].payload["level_requirement"] == 75
    assert nodes["Polearm Mastery"].position == (5, 7)
    assert nodes["Quake"].id == "dragoon.jump-mod.quake"
    assert nodes["Quake"].position == (2, 6)
    assert nodes["Quake"].prerequisites == (nodes["Rend"].id,)
    assert nodes["Soaring Strike"].id == "dragoon.jump-mod.soaring-strike"
    assert nodes["Soaring Strike"].position == (2, 7)
    assert nodes["Soaring Strike"].prerequisites == (nodes["Quake"].id,)
    assert "level_requirement" not in nodes["Dragon's Ascent"].payload
    assert nodes["Dragon's Ascent"].payload["available_on_promotion"] is True
    assert nodes["Dragon's Ascent"].prerequisites == (
        nodes["+20 Attack"].id,
    )
    assert nodes["Dragon Dive"].payload["level_requirement"] == 80
    assert nodes["Dragon Dive"].prerequisites == (
        nodes["Dragon's Ascent"].id,
        nodes["Soaring Strike"].id,
        nodes["Unstoppable"].id,
    )
    assert nodes["Dragon's Ascent"].position == (1, 5)
    assert nodes["+30 Defense"].position == (1, 6)
    assert nodes["+30 Defense"].prerequisites == (
        nodes["Dragon's Ascent"].id,
    )
    assert nodes["Dragon Dive"].position == (1, 7)
    assert "dragoon.ability.shield-block" not in {
        node.id
        for node in tree.nodes
    }
    assert "level_requirement" not in nodes["+30 Defense"].payload
    assert nodes["Retribution"].position == (0, 6)
    assert nodes["Retribution"].payload["level_requirement"] == 65
    assert nodes["Retribution"].prerequisites == (
        nodes["Grounded Landing"].id,
    )
    assert nodes["Unstoppable"].position == (0, 7)
    assert nodes["Unstoppable"].payload["level_requirement"] == 70
    assert max(node.position[1] for node in tree.nodes) == 7


def test_dragoon_promotion_requires_middle_path_level_and_authored_stats():
    player = _player("Lancer", level=59)
    player.stats.strength = 16
    player.stats.dex = 12
    status = next(
        status
        for status in available_nodes(player)
        if status.node.id == "lancer.promotion.dragoon"
    )

    assert status.reasons == (
        "Requires +20 Attack.",
        "Requires level 60 (current 59).",
        "Requires Strength 17 (current 16).",
        "Requires Dex 13 (current 12).",
    )

    player.level.level = 60
    player.progression.level = 60
    player.stats.strength = 17
    player.stats.dex = 13
    assert purchase_node(player, "lancer.ability.jump").success
    assert purchase_node(player, "lancer.rating.defense-1").success
    assert purchase_node(player, "lancer.rating.attack-1").success
    status = next(
        status
        for status in available_nodes(player)
        if status.node.id == "lancer.promotion.dragoon"
    )
    assert status.reasons == ()


def test_human_can_promote_at_60_and_continue_lancer_training_as_dragoon():
    player = TestGameState.create_player(
        class_name="Warrior",
        race_name="Human",
        level=30,
        stats={
            "strength": 12,
            "intel": 10,
            "wisdom": 10,
            "con": 12,
            "charisma": 10,
            "dex": 11,
        },
    )
    player.progression = ProgressionState(
        level=30,
        unspent_points=progression_points_through_level(30),
        unspent_attribute_points=7,
    )
    first_route = _prerequisite_closure("Warrior", "Promote: Lancer")
    first = apply_progression_plan(
        player,
        tuple(first_route),
        {"strength": 1, "con": 2},
    )
    assert first.success
    assert player.cls.name == "Lancer"

    player.level.level = 60
    player.progression.level = 60
    player.progression.unspent_points += 15
    player.progression.unspent_attribute_points += 8
    combat_state = promotion_kits.combat_state(player)
    combat_state["aerial_tempo"] = 3
    combat_state["pending_aerial_follow_through"] = {"stacks": 3}
    ring_data = class_rings.ensure_state(player)["data"]["Dragoon"]
    ring_data["meteor_guard_shield"] = 9
    ring_data["meteor_guard_turns"] = 2
    second_route = _prerequisite_closure("Lancer", "Promote: Dragoon")
    second = apply_progression_plan(
        player,
        tuple(second_route),
        {"strength": 2, "dex": 1},
    )

    assert second.success
    assert player.cls.name == "Dragoon"
    assert player.progression.unspent_points == 15
    assert player.progression.unspent_attribute_points == 9
    assert "Lancer" in player.progression.completed_trees
    assert promotion_kits.current_aerial_tempo(player) == 0
    assert (
        promotion_kits.combat_state(player)["pending_aerial_follow_through"]
        is None
    )
    ring_data = class_rings.ensure_state(player)["data"]["Dragoon"]
    assert ring_data["meteor_guard_shield"] == 0
    optional = apply_progression_plan(
        player,
        (
            "lancer.talent.aerial-footwork",
            "lancer.jump-mod.quick-dive",
        ),
        {},
    )
    assert optional.success
    assert player.progression.unspent_points == 13
    assert (
        player.spellbook["Skills"]["Jump"]
        .unlocked_modifications["Quick Dive"]
        is True
    )


def test_jump_mod_purchase_can_share_transaction_with_jump_without_fake_skill():
    player = _player("Lancer", level=40)
    result = apply_progression_plan(
        player,
        ("lancer.jump-mod.defend", "lancer.ability.jump"),
        {},
    )

    assert result.success
    jump = player.spellbook["Skills"]["Jump"]
    assert jump.unlocked_modifications["Defend"] is True
    assert "Defend" not in player.spellbook["Skills"]


def test_unlocked_jump_mod_is_adopted_and_round_trips_with_external_rewards():
    player = _player("Lancer")
    jump = abilities.Jump()
    jump.unlock_modification("Defend")
    jump.unlock_modification("Recover")
    jump.unlock_modification("Dragon's Fury")
    player.spellbook["Skills"]["Jump"] = jump

    ensure_progression(player)
    promotion_kits.combat_state(player)["aerial_tempo"] = 2
    ring_data = class_rings.ensure_state(player)["data"]["Dragoon"]
    ring_data["meteor_guard_shield"] = 7
    ring_data["meteor_guard_turns"] = 2

    assert "lancer.jump-mod.defend" in player.progression.purchased_node_ids
    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(player),
        skip_tiles=True,
    )
    restored_jump = restored.spellbook["Skills"]["Jump"]
    assert "lancer.jump-mod.defend" in restored.progression.purchased_node_ids
    assert restored_jump.unlocked_modifications["Defend"] is True
    assert restored_jump.unlocked_modifications["Recover"] is True
    assert restored_jump.unlocked_modifications["Dragon's Fury"] is True
    assert "Defend" not in restored.spellbook["Skills"]
    assert promotion_kits.current_aerial_tempo(restored) == 0
    restored_ring = class_rings.ensure_state(restored)["data"]["Dragoon"]
    assert restored_ring["meteor_guard_shield"] == 0


def test_dragoon_keeps_required_shield_block_off_tree_and_adopts_lancer_mods():
    player = _player("Dragoon")
    player.spellbook["Skills"]["Shield Block"] = abilities.ShieldBlock()
    player.spellbook["Skills"]["Parry"] = abilities.Parry()
    player.spellbook["Skills"]["True Strike"] = abilities.TrueStrike()
    jump = abilities.Jump()
    jump.unlock_modification("Acrobat")
    player.spellbook["Skills"]["Jump"] = jump

    ensure_progression(player)

    assert "dragoon.ability.shield-block" not in {
        node.id
        for node in ABILITY_TREES["Dragoon"].nodes
    }
    assert "Shield Block" in player.spellbook["Skills"]
    assert "lancer.ability.parry" in player.progression.purchased_node_ids
    assert "lancer.ability.true-strike" in player.progression.purchased_node_ids
    assert "lancer.jump-mod.defend" in player.progression.purchased_node_ids
    assert "lancer.jump-mod.acrobat" in player.progression.purchased_node_ids


def test_polearm_abilities_replace_their_previous_forms():
    player = _player("Dragoon")
    player.spellbook["Skills"]["Polearm Proficiency"] = (
        abilities.PolearmProficiency()
    )
    player.progression.purchased_node_ids.add(
        "lancer.ability.polearm-proficiency"
    )

    assert purchase_node(player, "dragoon.ability.polearm-excellence").success
    assert purchase_node(player, "dragoon.rating.attack-1").success
    assert "Polearm Proficiency" not in player.spellbook["Skills"]
    assert "Polearm Excellence" in player.spellbook["Skills"]
    assert purchase_node(player, "dragoon.ability.true-piercing-strike").success
    assert purchase_node(player, "dragoon.ability.polearm-mastery").success
    assert "Polearm Excellence" not in player.spellbook["Skills"]
    assert "Polearm Mastery" in player.spellbook["Skills"]


def test_aerial_footwork_produces_effective_lancer_and_dragoon_caps():
    lancer = _player("Lancer")
    dragoon = _player("Dragoon")
    talent_id = "lancer.talent.aerial-footwork"
    lancer.progression.purchased_node_ids.add(talent_id)
    dragoon.progression.purchased_node_ids.add(talent_id)

    assert promotion_kits.cap_for(lancer, "aerial_tempo") == 3
    assert promotion_kits.cap_for(dragoon, "aerial_tempo") == 4


def test_completed_jump_gains_tempo_on_hit_or_miss_and_consecutive_jumps_stack():
    player = _player("Lancer")
    player.progression.purchased_node_ids.add("lancer.talent.aerial-footwork")
    target = _player("Warrior")
    effect = JumpEffect()

    player.weapon_damage = lambda *_args, **_kwargs: ("miss\n", False, 1)
    effect.apply(player, target, CombatResult(action="Jump"))
    assert promotion_kits.current_aerial_tempo(player) == 1

    player.weapon_damage = lambda *_args, **_kwargs: ("hit\n", True, 1)
    effect.apply(player, target, CombatResult(action="Jump"))
    assert promotion_kits.current_aerial_tempo(player) == 2


def test_aerial_follow_through_is_action_level_and_miss_consumes():
    player = _player("Dragoon")
    target = _player("Warrior")
    player.equipment["Weapon"] = items.Halberd()
    state = promotion_kits.combat_state(player)
    state["aerial_tempo"] = 2

    promotion_kits.begin_action(player, action="Attack")
    assert state["aerial_tempo"] == 0
    assert promotion_kits.aerial_accuracy_bonus(player) == 0.06
    metadata = {"attack_source": "weapon", "weapon_type": "Polearm"}
    promotion_kits.record_aerial_weapon_damage(player, target, 40, metadata)
    promotion_kits.record_aerial_weapon_damage(player, target, 60, metadata)
    before = target.health.current
    message = promotion_kits.finish_action(player, defender_survived=True)

    assert target.health.current == before - 12
    assert "deals 12 damage" in message
    assert target.stat_effects["Speed"].extra == -2
    assert target.stat_effects["Speed"].duration == 2

    state["aerial_tempo"] = 2
    promotion_kits.begin_action(player, action="Attack")
    miss_message = promotion_kits.finish_action(
        player,
        defender_survived=True,
    )
    assert state["aerial_tempo"] == 0
    assert "misses" in miss_message


def test_jump_and_dragon_dive_do_not_arm_automatic_follow_through():
    player = _player("Dragoon")
    player.equipment["Weapon"] = items.Halberd()
    state = promotion_kits.combat_state(player)

    for choice in ("Jump", "Dragon Dive"):
        state["aerial_tempo"] = 3
        promotion_kits.begin_action(
            player,
            action="Use Skill",
            choice=choice,
        )
        assert state["aerial_tempo"] == 3
        assert promotion_kits.aerial_accuracy_bonus(player) == 0


def test_soaring_strike_with_dragons_ascent_gains_two_tempo():
    player = _player("Dragoon")
    player.progression.purchased_node_ids.add("dragoon.talent.dragons-ascent")

    message = promotion_kits.record_clean_jump_landing(
        player,
        25,
        {"Soaring Strike": True},
    )

    assert promotion_kits.current_aerial_tempo(player) == 2
    assert "gains 2 Aerial Tempo" in message


def test_grounded_landing_reduces_final_damage_only_while_jump_charges():
    player = _player("Lancer")
    player.progression.purchased_node_ids.add("lancer.talent.grounded-landing")
    jump = abilities.Jump()
    player.spellbook["Skills"]["Jump"] = jump

    assert promotion_kits.grounded_landing_reduction(player, 100) == (100, "")
    jump.charging = True
    reduced, message = promotion_kits.grounded_landing_reduction(player, 100)
    assert reduced == 90
    assert "reduces damage by 10" in message


def test_lance_sweep_validates_polearm_and_applies_dex_speed_control():
    player = _player("Lancer")
    target = _player("Warrior")
    skill = abilities.LanceSweep()
    starting_mana = player.mana.current

    player.equipment["Weapon"] = items.Rapier()
    result = skill.use(player, target)
    assert "requires a main-hand polearm" in result.message
    assert player.mana.current == starting_mana

    player.equipment["Weapon"] = items.Halberd()

    def weapon_damage(defender, **_kwargs):
        defender.health.current -= 20
        return "sweeps\n", True, 1

    player.weapon_damage = weapon_damage
    result = skill.use(player, target)
    assert player.mana.current == starting_mana - 8
    assert result.damage == 20
    assert target.stat_effects["Speed"].extra == -3
    assert target.stat_effects["Speed"].duration == 2


def test_dragon_dive_scales_spends_on_miss_and_never_arms_auto_payoff():
    player = _player("Dragoon")
    target = _player("Warrior")
    player.equipment["Weapon"] = items.Halberd()
    state = promotion_kits.combat_state(player)
    state["aerial_tempo"] = 3
    captured = {}

    def weapon_damage(_defender, **kwargs):
        captured.update(kwargs)
        return "miss\n", False, 1

    player.weapon_damage = weapon_damage
    promotion_kits.begin_action(
        player,
        action="Use Skill",
        choice="Dragon Dive",
    )
    result = abilities.DragonDive().use(player, target)
    finish_message = promotion_kits.finish_action(
        player,
        defender_survived=True,
    )

    assert player.mana.current == 182
    assert state["aerial_tempo"] == 0
    assert captured["dmg_mod"] == 2.0
    assert captured["accuracy_modifier"] == pytest.approx(0.15)
    assert result.hit is False
    assert "Tempo is spent" in result.message
    assert finish_message == ""


def test_aerial_supremacy_tuning_shield_refresh_absorption_and_expiry():
    player = _player("Dragoon")
    player.equipment["Ring"] = items.ClassRing()
    assert player.awaken_class_ring()[0] is True

    message = promotion_kits.record_clean_jump_landing(player, 100)
    data = class_rings.ensure_state(player)["data"]["Dragoon"]
    assert data["meteor_guard_shield"] == 15
    assert "15-point Landing Shield" in message

    promotion_kits.record_clean_jump_landing(player, 50)
    data = class_rings.ensure_state(player)["data"]["Dragoon"]
    assert data["meteor_guard_shield"] == 15
    promotion_kits.record_clean_jump_landing(player, 200)
    data = class_rings.ensure_state(player)["data"]["Dragoon"]
    assert data["meteor_guard_shield"] == 30

    remaining, absorb_message = class_rings.absorb_aerial_supremacy_shield(
        player,
        12,
    )
    data = class_rings.ensure_state(player)["data"]["Dragoon"]
    assert remaining == 0
    assert data["meteor_guard_shield"] == 18
    assert "absorbs 12 damage" in absorb_message
    assert class_rings.tick_aerial_supremacy_shield(player) == ""
    assert "expires" in class_rings.tick_aerial_supremacy_shield(player)
    data = class_rings.ensure_state(player)["data"]["Dragoon"]
    assert data["meteor_guard_shield"] == 0


def test_dormant_unequipped_and_legacy_jump_mod_ring_do_not_change_capacity():
    player = _player("Dragoon", level=30)
    jump = abilities.Jump()
    baseline = jump.get_max_active_modifications(player)
    ring = items.ClassRing()
    ring.mod = "+1 Jump Mod"
    player.equipment["Ring"] = ring

    assert jump.get_max_active_modifications(player) == baseline
    assert class_rings.apply_aerial_supremacy_shield(player, 100) == 0


def test_dragoon_death_clears_tempo_pending_payoff_and_landing_shield():
    player = _player("Dragoon")
    player.equipment["Ring"] = items.ClassRing()
    assert player.awaken_class_ring()[0] is True
    state = promotion_kits.combat_state(player)
    state["aerial_tempo"] = 3
    state["pending_aerial_follow_through"] = {"stacks": 3}
    class_rings.apply_aerial_supremacy_shield(player, 100)
    player.health.current = 0

    promotion_kits.record_damage_taken(player, 20, "Physical")

    assert state["aerial_tempo"] == 0
    assert state["pending_aerial_follow_through"] is None
    ring_data = class_rings.ensure_state(player)["data"]["Dragoon"]
    assert ring_data["meteor_guard_shield"] == 0
