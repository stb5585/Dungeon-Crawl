"""Regression coverage for the authored Monk and Priest promotion paths."""

from types import MethodType
from types import SimpleNamespace

import pytest

from src.core import abilities, enemies, items
from src.core.classes import class_rings, healer, promotion_kits
from src.core.progression import ABILITY_TREES, NodeKind, ProgressionState, ensure_progression
from src.core.progression_manifest import EXTERNAL_ACQUISITION_ABILITIES
from tests.test_framework import TestGameState


TREE_NAMES = ("Monk", "Master Monk", "Priest", "Archbishop")


def _player(class_name: str, level: int = 90, health=(200, 100)):
    player = TestGameState.create_player(
        class_name=class_name,
        level=level,
        health=health,
        mana=(300, 300),
    )
    player.progression = ProgressionState(level=level)
    return player


def _grant(player, *talent_keys: str) -> None:
    talents = {
        node.payload["talent_key"]: node
        for tree_name in TREE_NAMES
        for node in ABILITY_TREES[tree_name].nodes
        if node.kind == NodeKind.TALENT
    }
    for talent_key in talent_keys:
        player.progression.purchased_node_ids.add(talents[talent_key].id)


def test_four_trees_use_authored_budgets_and_standard_rows():
    monk = ABILITY_TREES["Monk"]
    monk_development = [node for node in monk.nodes if node.kind != NodeKind.PROMOTION]
    monk_promotion = next(node for node in monk.nodes if node.kind == NodeKind.PROMOTION)
    master = ABILITY_TREES["Master Monk"]
    priest = ABILITY_TREES["Priest"]
    priest_development = [node for node in priest.nodes if node.kind != NodeKind.PROMOTION]
    priest_promotion = next(node for node in priest.nodes if node.kind == NodeKind.PROMOTION)
    archbishop = ABILITY_TREES["Archbishop"]

    assert (len(monk_development), sum(node.cost for node in monk_development)) == (23, 23)
    assert (len(priest_development), sum(node.cost for node in priest_development)) == (22, 22)
    assert len(master.nodes) == 27
    assert sum(node.cost for node in master.nodes) == 28
    assert len(archbishop.nodes) == 29
    assert sum(node.cost for node in archbishop.nodes) == 31
    assert 0.60 <= 20 / 28 <= 0.75
    assert 0.60 <= 20 / 31 <= 0.70
    assert monk_promotion.payload["prerequisite_mode"] == "any"
    assert priest_promotion.payload["prerequisite_mode"] == "any"
    assert max(node.position[1] for tree in (monk, master, priest, archbishop) for node in tree.nodes) <= 7


def test_dim_mak_is_external_and_its_tree_modifiers_are_terminal():
    master = ABILITY_TREES["Master Monk"]
    nodes = {node.name: node for node in master.nodes}
    modifier_names = {
        "Decisive Pressure",
        "Death-Point Focus",
        "Flexible Form",
        "Essence Mastery",
        "Inner Reserve",
        "Perfect Recovery",
    }

    assert "Dim Mak" not in nodes
    assert "Dim Mak" in EXTERNAL_ACQUISITION_ABILITIES
    assert nodes["Suplex"].prerequisites == (nodes["Hadouken"].id,)
    for name in modifier_names:
        node = nodes[name]
        assert node.lane == "Dim Mak Mastery"
        assert not any(node.id in candidate.prerequisites for candidate in master.nodes)


def test_legacy_tree_dim_mak_is_removed_and_refunded_without_quest_unlock():
    monk = _player("Master Monk")
    monk.progression.unspent_points = 0
    monk.progression.purchased_node_ids.add("master-monk.ability.dim-mak")
    monk.spellbook["Skills"]["Dim Mak"] = abilities.DimMak()

    ensure_progression(monk)

    assert "master-monk.ability.dim-mak" not in monk.progression.purchased_node_ids
    assert "Dim Mak" not in monk.spellbook["Skills"]
    assert monk.progression.unspent_points == 2


def test_legacy_tree_marker_preserves_quest_unlocked_dim_mak():
    monk = _player("Master Monk")
    monk.progression.unspent_points = 0
    monk.progression.purchased_node_ids.add("master-monk.ability.dim-mak")
    monk.spellbook["Skills"]["Dim Mak"] = abilities.DimMak()
    monk.quest_dict["Side"]["This Thing's Nuclear"] = {"Turned In": True}

    ensure_progression(monk)

    assert "master-monk.ability.dim-mak" not in monk.progression.purchased_node_ids
    assert "Dim Mak" in monk.spellbook["Skills"]
    assert monk.progression.unspent_points == 0


def test_unarmed_proficiency_and_monk_ki_talents_are_live():
    monk = _player("Monk", 60)
    monk.spellbook["Skills"]["Unarmed Proficiency"] = abilities.UnarmedProficiency()
    monk.equipment["Weapon"] = items.NoWeapon()
    _grant(monk, "monk.rhythmic-breathing", "monk.deep-restoration")

    assert healer.accuracy_bonus(monk, "None") == pytest.approx(0.10)
    assert healer.staff_damage_multiplier(monk, "None") == pytest.approx(1.10)
    promotion_kits.begin_action(monk, action="Attack")
    promotion_kits.record_ki_martial_hit(monk, {"weapon_type": "None"})
    assert promotion_kits.combat_state(monk)["ki"] == 2

    promotion_kits.begin_ki_spender(monk, "Chi Heal")
    monk.health.current = 120
    promotion_kits.finish_ki_spender(monk, monk, "Chi Heal", healing=20)
    assert monk.health.current == 126


def test_purging_kata_cleanses_only_actionable_martial_conditions():
    monk = _player("Monk", 60)
    for name in ("Poison", "Blind", "Silence", "Berserk"):
        monk.status_effects[name].active = True
        monk.status_effects[name].duration = 3

    message = abilities.PurgingKata().use(monk)

    assert "Blind" in message and "Berserk" in message
    assert monk.status_effects["Blind"].active is False
    assert monk.status_effects["Berserk"].active is False
    assert monk.status_effects["Poison"].active is True
    assert monk.status_effects["Silence"].active is True
    assert "defensive stance for two turns" in abilities.CenteredGuard().description


def test_rope_a_dope_escalates_and_releases_four_hit_combo():
    monk = _player("Master Monk")
    target = enemies.Goblin()
    target.health.max = target.health.current = 500
    _grant(
        monk,
        "master-monk.slip-the-rope",
        "master-monk.rolling-shoulders",
        "master-monk.championship-round",
        "master-monk.second-wind",
    )
    modifiers = []

    def weapon_damage(self, defender, **kwargs):
        modifiers.append(kwargs["dmg_mod"])
        return "combo hit\n", True, 1

    monk.weapon_damage = MethodType(weapon_damage, monk)
    abilities.RopeADope().use(monk, target, rng=SimpleNamespace(random=lambda: 1.0))

    assert promotion_kits.rope_a_dope_dodge_bonus(monk) == pytest.approx(0.15)
    promotion_kits.record_rope_a_dope_dodge(monk, target)
    assert promotion_kits.rope_a_dope_dodge_bonus(monk) == pytest.approx(0.22)
    promotion_kits.record_rope_a_dope_dodge(monk, target)
    message = promotion_kits.record_rope_a_dope_dodge(monk, target)

    assert modifiers == [0.50, 0.60, 0.70, 0.80]
    assert "combination" in message
    assert promotion_kits.rope_a_dope_dodge_bonus(monk) == 0.0
    assert monk.health.current == 120


def test_priest_passives_deepen_prayer_and_regeneration():
    priest = _player("Priest", 60)
    priest.spellbook["Skills"]["Magical Invigoration"] = abilities.MagicalInvigoration()
    _grant(
        priest,
        "priest.deliberate-prayer",
        "priest.long-regeneration",
        "priest.arcane-renewal",
    )
    promotion_kits.begin_action(priest, action="Cast Spell", choice="Bless", round_number=1)
    promotion_kits.record_prayer_source(priest, "Bless", divine_support=True)
    assert promotion_kits.combat_state(priest)["prayer"] == 2

    promotion_kits.record_magical_invigoration_tick(priest)
    promotion_kits.record_magical_invigoration_tick(priest)
    assert promotion_kits.magical_invigoration_bonus(priest) == 12
    assert promotion_kits.combat_state(priest)["magical_invigoration"] == [4, 4]
    promotion_kits.tick_magical_invigoration(priest)
    assert promotion_kits.combat_state(priest)["magical_invigoration"] == [3, 3]


def test_archbishop_talents_modify_benediction_and_intervention():
    archbishop = _player("Archbishop")
    _grant(
        archbishop,
        "archbishop.ready-benediction",
        "archbishop.lasting-benediction",
        "archbishop.assured-intervention",
        "archbishop.miraculous-recovery",
    )
    promotion_kits.gain_meter(archbishop, "prayer", 2, "test")

    message = abilities.GreatBenediction().use(archbishop)
    assert "spends 2 Prayer" in message
    assert promotion_kits.combat_state(archbishop)["great_benediction"]["turns"] == 5

    archbishop.equipment["Ring"] = items.ClassRing()
    ring_state = class_rings.ensure_state(archbishop)
    ring_state["awakened"]["Archbishop"] = True
    archbishop.equipment["Ring"].class_mod(archbishop)
    archbishop.health.current = 40
    healed = class_rings.divine_intervention(
        archbishop,
        rng=SimpleNamespace(random=lambda: 0.49),
    )
    assert healed == 70
    assert archbishop.health.current == 110
