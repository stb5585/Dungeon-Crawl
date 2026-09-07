"""Regression coverage for the authored Beast Master terminal tree."""

from types import SimpleNamespace

import pytest

from src.core import abilities, enemies
from src.core.classes import ability_mechanics, pathfinder, promotion_kits
from src.core.progression import ABILITY_TREES, NodeKind, ProgressionState
from tests.test_framework import TestGameState


def _beast_master(*, bond: int = 100):
    player = TestGameState.create_player(class_name="Beast Master", level=90)
    player.progression = ProgressionState(level=90)
    player.spellbook["Skills"]["Favored Enemy"] = abilities.FavoredEnemy()
    player.tamed_companion = {
        "active": True,
        "enemy_class": "GiantRat",
        "name": "Giant Rat",
        "bond": bond,
        "special_ability": "Pounce",
    }
    player.ensure_tamed_companion()
    return player


def _grant(player, *talent_keys: str) -> None:
    talents = {
        node.payload["talent_key"]: node
        for tree_name in ("Ranger", "Beast Master")
        for node in ABILITY_TREES[tree_name].nodes
        if node.kind == NodeKind.TALENT
    }
    for key in talent_keys:
        player.progression.purchased_node_ids.add(talents[key].id)


def test_beast_master_tree_has_twenty_two_authored_nodes_and_stable_legacy_ids():
    tree = ABILITY_TREES["Beast Master"]
    ids = {node.id for node in tree.nodes}

    assert len(tree.nodes) == 22
    assert tree.branches == ("Pack Tactics", "Commands")
    assert {
        "beast-master.ability.packstrike",
        "beast-master.ability.guardpartner",
        "beast-master.ability.harryprey",
        "beast-master.ability.mendwounds",
        "beast-master.ability.cover",
        "beast-master.ability.zephyrstrike",
        "beast-master.talent.beast-master-bonded-bulwark",
    } <= ids
    assert {"Heavy Hunter", "Trail Guard"} <= {node.name for node in tree.nodes}


def test_heavy_hunter_coordinated_assault_and_trail_guard_reuse_ranger_rules():
    beast = _beast_master()
    target = enemies.Goblin()
    beast.equipment["Weapon"] = SimpleNamespace(typ="Weapon", handed=2)
    abilities.FavoredEnemy().use(beast, target)
    _grant(
        beast,
        "beast-master.heavy-hunter",
        "beast-master.coordinated-assault",
        "beast-master.trail-guard",
    )

    assert pathfinder.ranger_weapon_damage_multiplier(beast, target) == pytest.approx(1.15 * 1.10)
    reduced, message = pathfinder.ranger_damage_reduction(
        beast,
        target,
        100,
        physical=True,
    )
    assert reduced == 90
    assert "Trail Guard" in message


def test_unleash_instinct_and_rally_partner_each_use_one_command_action():
    beast = _beast_master(bond=50)
    target = enemies.Goblin()
    for command in (abilities.UnleashInstinct(), abilities.RallyPartner()):
        beast.spellbook["Skills"][command.name] = command

    before = target.health.current
    ability_mechanics.set_pending_companion_command(beast, "Unleash Instinct")
    instinct_message = ability_mechanics.resolve_tamed_companion_command(beast, target)

    beast.health.current -= 20
    beast.status_effects["Poison"].active = True
    ability_mechanics.set_pending_companion_command(beast, "Rally Partner")
    rally_message = ability_mechanics.resolve_tamed_companion_command(beast, target)

    assert target.health.current < before
    assert "unleashes Pounce" in instinct_message
    assert beast.health.current > beast.health.max - 20
    assert beast.status_effects["Poison"].active is False
    assert "clears Poison" in rally_message
    assert ability_mechanics.pending_companion_command(beast) is None


def test_apex_pack_and_cornered_prey_scale_without_extra_companion_turns():
    beast = _beast_master(bond=100)
    target = enemies.Goblin()
    abilities.FavoredEnemy().use(beast, target)
    target.health.current = target.health.max * 3 // 10
    _grant(beast, "beast-master.apex-pack", "beast-master.cornered-prey")

    assert ability_mechanics.tamed_auto_action_chance(beast) == pytest.approx(0.50)
    assert ability_mechanics.tamed_companion_damage_multiplier(
        beast,
        target,
    ) == pytest.approx(1.10 * 1.25)


def test_guardian_and_command_capstones_strengthen_existing_commands():
    beast = _beast_master(bond=100)
    target = enemies.Goblin()
    abilities.FavoredEnemy().use(beast, target)
    _grant(
        beast,
        "beast-master.commanders-voice",
        "beast-master.adaptive-orders",
        "beast-master.crippling-harrier",
        "beast-master.field-dressing",
        "beast-master.guardian-pack",
        "ranger.companion-bond",
        "beast-master.bonded-bulwark",
        "beast-master.true-bond",
    )

    ability_mechanics.set_pending_companion_command(beast, "Harry Prey")
    ability_mechanics.resolve_tamed_companion_command(beast, target)
    assert target.stat_effects["Attack"].active is True
    assert target.stat_effects["Attack"].duration == 3

    beast.health.current -= 30
    beast.familiar.health.current -= 3
    beast.status_effects["Poison"].active = True
    ability_mechanics.set_pending_companion_command(beast, "Mend Wounds")
    message = ability_mechanics.resolve_tamed_companion_command(beast, target)

    assert beast.health.current > beast.health.max - 30
    assert beast.familiar.health.current > beast.familiar.health.max - 3
    assert beast.status_effects["Poison"].active is False
    assert "shared treatment" in message
    assert promotion_kits.companion_bond_multiplier(beast) == pytest.approx(1.40)
