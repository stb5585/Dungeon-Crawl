"""Regression coverage for the authored Ranger tree and class mechanics."""

from types import SimpleNamespace

import pytest

from src.core import abilities, enemies, items
from src.core.classes import ability_mechanics, pathfinder, promotion_kits
from src.core.progression import ABILITY_TREES, NodeKind, ProgressionState
from tests.test_framework import TestGameState


def _ranger() -> object:
    player = TestGameState.create_player(class_name="Ranger", level=60)
    player.progression = ProgressionState(level=60)
    player.spellbook["Skills"]["Favored Enemy"] = abilities.FavoredEnemy()
    return player


def _grant_talent(player, key: str) -> None:
    node = next(
        node
        for node in ABILITY_TREES["Ranger"].nodes
        if node.kind == NodeKind.TALENT and node.payload["talent_key"] == key
    )
    player.progression.purchased_node_ids.add(node.id)


def test_ranger_tree_has_five_paths_and_companion_bond_promotion_gate():
    tree = ABILITY_TREES["Ranger"]
    development = [node for node in tree.nodes if node.kind != NodeKind.PROMOTION]
    promotion = next(node for node in tree.nodes if node.kind == NodeKind.PROMOTION)
    favored_enemy = next(node for node in tree.nodes if node.name == "Favored Enemy")
    pack_tactics = next(node for node in tree.nodes if node.name == "Pack Tactics")
    companion_bond = next(node for node in tree.nodes if node.name == "Companion Bond")

    assert len(development) == 24
    assert tree.branches == (
        "Hunt",
        "Companion Bond",
        "Duelist / Ranged",
        "Two-Handed Fighting",
        "Defense",
    )
    assert favored_enemy.prerequisites == ()
    assert pack_tactics.payload["prerequisite_mode"] == "any"
    assert len(pack_tactics.prerequisites) == 2
    assert companion_bond.position[1] == 5
    assert companion_bond.prerequisites == (pack_tactics.id,)
    assert promotion.prerequisites == (companion_bond.id,)


def test_wild_sense_reveals_more_detail_at_mastered_trail():
    ranger = _ranger()
    target = enemies.Goblin()
    abilities.FavoredEnemy().use(ranger, target)

    fresh = abilities.WildSense().use(ranger, target).message
    promotion_kits.ensure_state(ranger)["favored_enemy"]["practice"] = 30
    mastered = abilities.WildSense().use(ranger, target).message

    assert "Vitality" in fresh
    assert "Combat profile" not in fresh
    assert "Combat profile" in mastered
    assert "Resistances" in mastered
    assert "Known techniques" in mastered


def test_uncanny_volley_uses_one_bolt_and_unnatural_damage_bonus(monkeypatch):
    ranger = _ranger()
    ranger.equipment["OffHand"] = SimpleNamespace(subtyp="Crossbow")
    ranger.inventory["Wooden Bolts"] = [SimpleNamespace(charges=3)]
    targets = [("natural", enemies.Goblin()), ("unnatural", enemies.Skeleton())]
    multipliers = []

    monkeypatch.setattr(
        "src.core.classes.crossbow.selected_bolts",
        lambda _character: SimpleNamespace(charges=3),
    )

    def fake_fire(_user, target, **kwargs):
        multipliers.append((target.enemy_typ, kwargs))
        return f"hit {target.name}\n", True, [10]

    monkeypatch.setattr("src.core.classes.crossbow.fire_crossbow", fake_fire)
    engine = SimpleNamespace(current_actor_id="ranger")
    result = abilities.UncannyVolley().use_group(
        ranger,
        targets,
        battle_engine=engine,
    )

    assert len(result.results) == 2
    assert all(kwargs["shot_limit"] == 1 for _typ, kwargs in multipliers)
    assert multipliers[0][1]["damage_multiplier"] == pytest.approx(1.0)
    assert multipliers[1][1]["damage_multiplier"] == pytest.approx(1.25)


def test_combo_breaker_scales_only_within_one_enemy_action():
    ranger = _ranger()
    _grant_talent(ranger, "ranger.combo-breaker")
    attacker = enemies.Goblin()
    pathfinder.record_incoming_action_start(ranger)

    first, _message = pathfinder.ranger_damage_reduction(
        ranger, attacker, 100, physical=True
    )
    second, message = pathfinder.ranger_damage_reduction(
        ranger, attacker, 100, physical=True
    )
    pathfinder.record_incoming_action_end(ranger, ranger.health.current)
    reset, _message = pathfinder.ranger_damage_reduction(
        ranger, attacker, 100, physical=True
    )

    assert first == 100
    assert second == 92
    assert "Combo Breaker 8%" in message
    assert reset == 100


def test_ranger_duelist_allows_crossbow_but_two_handed_style_does_not():
    ranger = _ranger()
    ranger.spellbook["Skills"]["Duelist"] = abilities.Duelist()
    ranger.equipment["OffHand"] = items.HandCrossbow()

    assert ability_mechanics.duelist_style_active(ranger)
    ranger.equipment["Weapon"] = SimpleNamespace(typ="Weapon", handed=2)
    assert not ability_mechanics.duelist_style_active(ranger)


def test_companion_bond_talent_increases_existing_bond_scaling():
    ranger = _ranger()
    ranger.tamed_companion = {"bond": 100}

    assert promotion_kits.companion_bond_multiplier(ranger) == pytest.approx(1.15)
    _grant_talent(ranger, "ranger.companion-bond")
    assert promotion_kits.companion_bond_multiplier(ranger) == pytest.approx(1.20)


def test_quarry_cleave_is_an_active_two_handed_quarry_attack(monkeypatch):
    ranger = _ranger()
    target = enemies.Goblin()
    ranger.equipment["Weapon"] = SimpleNamespace(typ="Weapon", handed=2)
    modifiers = []

    def fake_weapon_damage(_target, **kwargs):
        modifiers.append(kwargs["dmg_mod"])
        return "cleave\n", True, 1

    monkeypatch.setattr(ranger, "weapon_damage", fake_weapon_damage)
    abilities.QuarryCleave().use(ranger, target)
    abilities.FavoredEnemy().use(ranger, target)
    result = abilities.QuarryCleave().use(ranger, target)

    assert modifiers == [1.25, 1.50]
    assert "marked trail" in result.message


def test_hunters_snare_scales_with_tracking_mastery():
    ranger = _ranger()
    target = enemies.Goblin()
    abilities.FavoredEnemy().use(ranger, target)
    promotion_kits.ensure_state(ranger)["favored_enemy"]["practice"] = 20

    result = abilities.HuntersSnare().use(ranger, target)

    speed = target.stat_effects["Speed"]
    assert result.hit is True
    assert speed.active is True
    assert speed.duration == 4
    assert speed.extra == -7
