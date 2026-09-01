"""Focused coverage for the bespoke Mage tree and its new lineage."""

from __future__ import annotations

import pytest

from src.core import abilities, companions, enemies, items, races
from src.core.classes import Mage, promotion_kits
from src.core.combat.battle_engine import BattleEngine
from src.core.combat.encounter import CombatEncounter
from src.core.progression import (
    ABILITY_TREES,
    NodeKind,
    NodeState,
    ProgressionState,
    apply_progression_plan,
    attribute_points_through_level,
    available_nodes,
    effective_node_level_requirement,
    permanent_closures_for_plan,
    promotion_preview,
    purchase_node,
)
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


PROMOTION_ROUTES = {
    "Sorcerer": (
        "mage.ability.magicmissile",
        "mage.talent.arcane-fundamentals",
        "mage.ability.mana-rupture",
        "mage.ability.arcane-tradition",
        "mage.promotion.sorcerer",
    ),
    "Spellblade": (
        "mage.ability.magicmissile",
        "mage.talent.arcane-fundamentals",
        "mage.ability.mana-rupture",
        "mage.ability.polymorph",
        "mage.ability.manashield",
        "mage.ability.imbue-weapon",
        "mage.promotion.spellblade",
    ),
    "Warlock": (
        "mage.ability.enfeeble",
        "mage.ability.blinding-fog",
        "mage.ability.shadow-bolt",
        "mage.ability.inflate-health",
        "mage.ability.enliven-dead",
        "mage.talent.forbidden-studies",
        "mage.promotion.warlock",
    ),
    "Conjurer": (
        "mage.ability.conjure-blade",
        "mage.mana.conjuration-reserve",
        "mage.ability.conjure-animal",
        "mage.talent.binding-circle",
        "mage.ability.conjure-shackles",
        "mage.ability.conjure-potion",
        "mage.promotion.conjurer",
    ),
}

PROMOTION_REQUIREMENTS = {
    "Sorcerer": {"intel": 15, "wisdom": 13},
    "Warlock": {"intel": 13, "charisma": 14},
    "Spellblade": {"con": 11, "intel": 13, "charisma": 12},
    "Conjurer": {
        "charisma": 12,
        "intel": 13,
        "wisdom": 12,
    },
}

ELEMENTAL_IDS = (
    "mage.ability.firebolt",
    "mage.ability.icelance",
    "mage.ability.shock",
    "mage.ability.gust",
    "mage.ability.waterjet",
    "mage.ability.tremor",
)
ENHANCEMENT_IDS = (
    "mage.ability.fire-inside",
    "mage.ability.frozen-armor",
    "mage.ability.electrified",
    "mage.ability.wind-currents",
    "mage.ability.refreshment",
    "mage.ability.terra-firma",
)


def _player(class_name: str = "Mage", *, level: int = 100):
    player = TestGameState.create_player(
        class_name=class_name,
        race_name="Human",
        level=level,
        health=(500, 500),
        mana=(500, 500),
        stats={
            "strength": 30,
            "intel": 30,
            "wisdom": 30,
            "con": 30,
            "charisma": 30,
            "dex": 30,
        },
    )
    player.progression = ProgressionState(
        level=level,
        unspent_points=100,
        unspent_attribute_points=100,
    )
    return player


def _nodes(class_name: str = "Mage"):
    return {node.id: node for node in ABILITY_TREES[class_name].nodes}


def _promote(target: str):
    player = _player()
    choices = (
        {"mage.promotion.warlock": {"familiar": companions.Jinkin()}}
        if target == "Warlock"
        else None
    )
    result = apply_progression_plan(
        player,
        PROMOTION_ROUTES[target],
        {},
        promotion_choices=choices,
    )
    assert result.success, result.message
    return player


def test_mage_tree_has_exact_ids_coordinates_gates_and_prerequisites():
    tree = ABILITY_TREES["Mage"]
    nodes = _nodes()
    expected_positions = {
        **{node_id: (0, row) for row, node_id in enumerate(ELEMENTAL_IDS)},
        **{node_id: (1, row) for row, node_id in enumerate(ENHANCEMENT_IDS)},
        "mage.ability.magicmissile": (2, 0),
        "mage.talent.arcane-fundamentals": (2, 1),
        "mage.ability.mana-rupture": (2, 2),
        "mage.ability.polymorph": (2, 3),
        "mage.ability.manashield": (2, 4),
        "mage.ability.imbue-weapon": (2, 5),
        "mage.ability.enfeeble": (3, 0),
        "mage.ability.blinding-fog": (3, 1),
        "mage.ability.shadow-bolt": (3, 2),
        "mage.ability.inflate-health": (3, 3),
        "mage.ability.enliven-dead": (3, 4),
        "mage.talent.forbidden-studies": (3, 5),
        "mage.ability.conjure-blade": (4, 0),
        "mage.mana.conjuration-reserve": (4, 1),
        "mage.ability.conjure-animal": (4, 2),
        "mage.talent.binding-circle": (4, 3),
        "mage.ability.conjure-shackles": (4, 4),
        "mage.ability.conjure-potion": (4, 5),
        "mage.ability.reflect": (5, 1),
        "mage.ability.sleep": (5, 2),
        "mage.ability.boost": (5, 3),
        "mage.ability.mirror-image": (5, 4),
        "mage.ability.classical-force": (0.5, 6),
        "mage.ability.arcane-tradition": (1.5, 6),
    }
    development = {
        node.id: node for node in tree.nodes if node.kind != NodeKind.PROMOTION
    }

    assert tree.branches == (
        "Elementalism",
        "Arcana",
        "Occultism",
        "Conjuration",
        "Universal",
    )
    assert set(development) == set(expected_positions)
    assert {node_id: node.position for node_id, node in development.items()} == expected_positions
    assert all(development[node_id].prerequisites == () for node_id in ELEMENTAL_IDS)
    assert all(
        development[node_id].payload.get("level_requirement") is None
        for node_id in ELEMENTAL_IDS
    )
    for spell_id, passive_id in zip(ELEMENTAL_IDS, ENHANCEMENT_IDS):
        assert development[passive_id].prerequisites == (spell_id,)
        assert development[passive_id].payload["level_requirement"] == 20
        assert development[passive_id].icon_key == "skill_passive"

    expected_levels = {
        **{node_id: 20 for node_id in ENHANCEMENT_IDS},
        "mage.talent.arcane-fundamentals": 5,
        "mage.ability.polymorph": 15,
        "mage.ability.manashield": 20,
        "mage.ability.imbue-weapon": 25,
        "mage.ability.blinding-fog": 5,
        "mage.ability.shadow-bolt": 10,
        "mage.ability.inflate-health": 15,
        "mage.ability.enliven-dead": 20,
        "mage.talent.forbidden-studies": 25,
        "mage.ability.conjure-animal": 10,
        "mage.talent.binding-circle": 15,
        "mage.ability.conjure-shackles": 20,
        "mage.ability.conjure-potion": 25,
        "mage.ability.reflect": 10,
        "mage.ability.sleep": 15,
        "mage.ability.boost": 20,
        "mage.ability.mirror-image": 25,
        "mage.ability.classical-force": 25,
        "mage.ability.arcane-tradition": 25,
    }
    assert {
        node_id: node.payload.get("level_requirement")
        for node_id, node in development.items()
        if node.payload.get("level_requirement")
    } == expected_levels
    assert "level_requirement" not in development["mage.ability.mana-rupture"].payload
    assert "level_requirement" not in development["mage.mana.conjuration-reserve"].payload
    assert "mage.talent.warded-casting" not in nodes
    assert {
        node_id: node.icon_key for node_id, node in development.items()
    } == {
        "mage.ability.firebolt": "spell_fire",
        "mage.ability.icelance": "spell_ice",
        "mage.ability.shock": "spell_lightning",
        "mage.ability.gust": "spell_wind",
        "mage.ability.waterjet": "spell_water",
        "mage.ability.tremor": "spell_earth",
        **{node_id: "skill_passive" for node_id in ENHANCEMENT_IDS},
        "mage.ability.magicmissile": "spell_arcane",
        "mage.talent.arcane-fundamentals": "skill_passive",
        "mage.ability.mana-rupture": "spell_arcane",
        "mage.ability.polymorph": "spell_arcane",
        "mage.ability.manashield": "skill_support",
        "mage.ability.imbue-weapon": "skill_support",
        "mage.ability.enfeeble": "spell_status",
        "mage.ability.blinding-fog": "spell_status",
        "mage.ability.shadow-bolt": "spell_shadow",
        "mage.ability.inflate-health": "spell_shadow",
        "mage.ability.enliven-dead": "spell_shadow",
        "mage.talent.forbidden-studies": "skill_passive",
        "mage.ability.conjure-blade": "spell_arcane",
        "mage.mana.conjuration-reserve": "spell_arcane",
        "mage.ability.conjure-animal": "spell_arcane",
        "mage.talent.binding-circle": "skill_passive",
        "mage.ability.conjure-shackles": "spell_arcane",
        "mage.ability.conjure-potion": "spell_arcane",
        "mage.ability.reflect": "spell_support",
        "mage.ability.sleep": "spell_status",
        "mage.ability.boost": "spell_support",
        "mage.ability.mirror-image": "spell_illusion",
        "mage.ability.classical-force": "skill_passive",
        "mage.ability.arcane-tradition": "skill_passive",
    }


def test_promotions_have_exact_terminals_costs_and_stat_gates():
    promotions = {
        node.payload["target_class"]: node
        for node in ABILITY_TREES["Mage"].nodes
        if node.kind == NodeKind.PROMOTION
    }
    assert set(promotions) == {"Sorcerer", "Spellblade", "Warlock", "Conjurer"}
    assert promotions["Sorcerer"].prerequisites == (
        "mage.ability.classical-force",
        "mage.ability.arcane-tradition",
    )
    assert promotions["Sorcerer"].payload["prerequisite_mode"] == "any"
    assert promotions["Spellblade"].prerequisites == ("mage.ability.imbue-weapon",)
    assert promotions["Warlock"].prerequisites == ("mage.talent.forbidden-studies",)
    assert promotions["Conjurer"].prerequisites == ("mage.ability.conjure-potion",)
    assert all(node.cost == 2 for node in promotions.values())
    assert all(node.payload["level_requirement"] == 30 for node in promotions.values())
    assert {
        target: node.payload["requirements"] for target, node in promotions.items()
    } == PROMOTION_REQUIREMENTS
    assert {
        target: sum(_nodes()[node_id].cost for node_id in route)
        for target, route in PROMOTION_ROUTES.items()
    } == {"Sorcerer": 6, "Spellblade": 8, "Warlock": 8, "Conjurer": 8}


def test_sorcerer_specializations_are_exclusive_and_warn_before_closure():
    player = _player(level=25)
    assert apply_progression_plan(
        player,
        (
            "mage.ability.magicmissile",
            "mage.talent.arcane-fundamentals",
            "mage.ability.mana-rupture",
        ),
        {},
    ).success
    assert permanent_closures_for_plan(
        player, "Mage", ("mage.ability.arcane-tradition",)
    ) == ("Classical Force",)
    assert purchase_node(player, "mage.ability.arcane-tradition").success
    classical = next(
        status for status in available_nodes(player)
        if status.node.id == "mage.ability.classical-force"
    )
    assert classical.state == NodeState.CLOSED


def test_classical_force_accepts_any_enhanced_element():
    for spell_id, passive_id in zip(ELEMENTAL_IDS, ENHANCEMENT_IDS):
        player = _player(level=25)
        assert apply_progression_plan(player, (spell_id, passive_id), {}).success
        status = next(
            entry for entry in available_nodes(player)
            if entry.node.id == "mage.ability.classical-force"
        )
        assert status.state == NodeState.AVAILABLE


def test_every_registry_legal_mage_race_can_reach_level_30_gate():
    mage = Mage()
    bonuses = {
        "strength": mage.str_plus,
        "intel": mage.int_plus,
        "wisdom": mage.wis_plus,
        "con": mage.con_plus,
        "charisma": mage.cha_plus,
        "dex": mage.dex_plus,
    }
    available_points = attribute_points_through_level(30)
    for race_ctor in races.races_dict.values():
        race = race_ctor()
        if "Mage" not in race.cls_res["Base"]:
            continue
        for target, requirements in PROMOTION_REQUIREMENTS.items():
            if target not in race.cls_res["First"]:
                continue
            deficit = sum(
                max(0, required - int(getattr(race, stat)) - bonuses[stat])
                for stat, required in requirements.items()
            )
            assert deficit <= available_points, (race.name, target, deficit)


@pytest.mark.parametrize("target", tuple(PROMOTION_ROUTES))
def test_promotions_retain_learned_spells_and_close_mage_development(target: str):
    player = _promote(target)
    assert player.cls.name == target
    assert "Mage" in player.progression.completed_trees
    assert all(
        status.state in {NodeState.OWNED, NodeState.CLOSED}
        for status in available_nodes(player, "Mage")
    )
    result = purchase_node(player, "mage.ability.enfeeble")
    if "mage.ability.enfeeble" not in player.progression.purchased_node_ids:
        assert not result.success


def test_sorcerer_no_longer_carries_unpurchased_level_one_mage_spells():
    player = _promote("Sorcerer")
    result = purchase_node(player, "mage.ability.firebolt")

    assert not result.success
    assert "current class tree" in result.message
    assert "Firebolt" not in player.spellbook["Spells"]


def test_new_mage_state_round_trips_with_version_five_saves():
    player = _promote("Conjurer")
    player.last_defeated_enemy = {
        "name": "Goblin",
        "enemy_type": "Humanoid",
        "level": 4,
    }
    player.transient_companion = {
        "name": "Wolf",
        "kind": "animal",
        "source": "Conjure Animal",
        "steps_remaining": 41,
        "damage": 12,
    }
    player.conjure_potion_cooldown = 17
    player.torchlight_steps = 23
    assert companions.choose_xenid(player, "Spirit", "Izulu")[0]
    restored = PlayerDataSerializer.deserialize(
        PlayerDataSerializer.serialize(player),
        skip_tiles=True,
    )
    assert restored.cls.name == "Conjurer"
    assert restored.last_defeated_enemy["name"] == "Goblin"
    assert restored.transient_companion["steps_remaining"] == 41
    assert restored.conjure_potion_cooldown == 17
    assert restored.torchlight_steps == 23
    assert restored.xenid_choices == {"Spirit": "Izulu"}
    assert set(restored.summons) == {"Izulu"}


def test_conjurer_tree_has_exact_authored_disciplines_and_gates():
    nodes = _nodes("Conjurer")
    expected = {
        "conjurer.ability.floating-crystal": ((3, 1), None, ()),
        "conjurer.ability.torchlight": (
            (3, 2),
            35,
            ("conjurer.ability.floating-crystal",),
        ),
        "conjurer.rating.magic-1": (
            (3, 3),
            None,
            ("conjurer.ability.torchlight",),
        ),
        "conjurer.ability.conjure-elixir": (
            (3, 4),
            45,
            ("conjurer.rating.magic-1",),
        ),
        "conjurer.ability.barrier-wall": (
            (3, 6),
            55,
            ("conjurer.ability.conjure-elixir",),
        ),
        "conjurer.ability.sleep": ((1, 1), None, ()),
        "conjurer.ability.silence": (
            (1, 2),
            35,
            ("conjurer.ability.sleep",),
        ),
        "conjurer.ability.banish": (
            (1, 3),
            40,
            ("conjurer.ability.silence",),
        ),
        "conjurer.ability.weaken-mind": (
            (1, 4),
            45,
            ("conjurer.ability.banish",),
        ),
        "conjurer.ability.mana-barbs": (
            (1, 6),
            55,
            ("conjurer.ability.weaken-mind",),
        ),
        "conjurer.ability.mirror-image": ((2, 1), None, ()),
        "conjurer.ability.nightmare-fuel": (
            (2, 2),
            35,
            ("conjurer.ability.mirror-image",),
        ),
        "conjurer.ability.volitation": (
            (2, 4),
            45,
            ("conjurer.ability.nightmare-fuel",),
        ),
        "conjurer.ability.teleport": (
            (2, 5),
            50,
            ("conjurer.ability.volitation",),
        ),
        "conjurer.ability.explosive-decoy": (
            (2, 6),
            55,
            ("conjurer.ability.teleport",),
        ),
        "conjurer.ability.conjure-humanoid": ((0, 1), None, ()),
        "conjurer.ability.conjure-monster": (
            (0, 2),
            35,
            ("conjurer.ability.conjure-humanoid",),
        ),
        "conjurer.ability.conjure-spirit": (
            (0, 3),
            40,
            ("conjurer.ability.conjure-monster",),
        ),
        "conjurer.ability.conjure-fiend": (
            (0, 4),
            45,
            ("conjurer.ability.conjure-spirit",),
        ),
        "conjurer.ability.conjure-celestial": (
            (0, 5),
            50,
            ("conjurer.ability.conjure-fiend",),
        ),
        "conjurer.ability.conjure-dragon": (
            (0, 6),
            55,
            ("conjurer.ability.conjure-celestial",),
        ),
    }
    development = {
        node_id: node
        for node_id, node in nodes.items()
        if node.kind != NodeKind.PROMOTION
    }
    assert set(development) == set(expected)
    assert {
        node_id: (
            node.position,
            node.payload.get("level_requirement"),
            node.prerequisites,
        )
        for node_id, node in development.items()
    } == expected
    promotion = nodes["conjurer.promotion.thaumaturgist"]
    assert promotion.position == (1.5, 7)
    assert promotion.cost == 3
    assert promotion.payload["level_requirement"] == 60
    assert promotion.payload["prerequisite_mode"] == "any"


def test_conjurer_adopts_sleep_and_mirror_image_when_already_known():
    conjurer = _player("Conjurer")
    conjurer.spellbook["Spells"]["Sleep"] = abilities.Sleep()
    conjurer.spellbook["Spells"]["Mirror Image"] = abilities.MirrorImage()

    statuses = {status.node.id: status for status in available_nodes(conjurer)}

    assert statuses["conjurer.ability.sleep"].state == NodeState.OWNED
    assert statuses["conjurer.ability.mirror-image"].state == NodeState.OWNED


def test_thaumaturgist_tree_carries_animal_and_six_conjurer_callings():
    calling_ids = {
        "conjurer.ability.conjure-humanoid",
        "conjurer.ability.conjure-monster",
        "conjurer.ability.conjure-spirit",
        "conjurer.ability.conjure-fiend",
        "conjurer.ability.conjure-celestial",
        "conjurer.ability.conjure-dragon",
    }
    carried = {
        node.id
        for node in ABILITY_TREES["Thaumaturgist"].nodes
        if node.tree_id == "Conjurer"
    }
    assert carried == calling_ids
    assert "mage.ability.conjure-animal" in {
        node.id
        for node in ABILITY_TREES["Thaumaturgist"].nodes
        if node.tree_id == "Mage"
    }

    thaumaturgist = _player("Thaumaturgist")
    thaumaturgist.progression.completed_trees.add("Conjurer")
    statuses = {
        status.node.id: status
        for status in available_nodes(thaumaturgist)
    }
    assert statuses["conjurer.ability.conjure-humanoid"].state == NodeState.AVAILABLE
    assert "conjurer.ability.floating-crystal" not in statuses

    unrelated = _player("Warlock")
    unrelated.progression.completed_trees.add("Conjurer")
    result = purchase_node(unrelated, "conjurer.ability.conjure-humanoid")
    assert not result.success


def test_thaumaturgist_tree_has_paired_choices_ultimates_and_conduit_lane():
    tree = ABILITY_TREES["Thaumaturgist"]
    assert len(tree.nodes) == 29
    assert tree.branches == (
        "Calling",
        "Xenid Choice",
        "Xenid Ultimate",
        "Conduit",
        "Miracles",
    )
    for row, category in enumerate(
        ("animal", "humanoid", "monster", "spirit", "fiend", "celestial", "dragon")
    ):
        choice = _nodes("Thaumaturgist")[f"thaumaturgist.talent.bind-{category}"]
        ultimate = _nodes("Thaumaturgist")[
            f"thaumaturgist.talent.{category}-ultimate"
        ]
        assert choice.position == (1, row + 1)
        assert ultimate.position == (2, row + 1)
        assert ultimate.prerequisites == (choice.id,)
    conduit = [
        ("thaumaturgist.ability.healsummon", (3, 2), 65),
        ("thaumaturgist.ability.conduitcommand", (3, 3), 70),
        ("thaumaturgist.ability.raisesummon", (3, 4), 75),
        ("thaumaturgist.talent.conduit-mastery", (3, 5), 80),
    ]
    nodes = _nodes("Thaumaturgist")
    for node_id, position, level in conduit:
        assert nodes[node_id].position == position
        assert nodes[node_id].payload["level_requirement"] == level
    assert "thaumaturgist.true-name-ward" not in {
        node.payload.get("talent_key") for node in tree.nodes
    }

    miracle_ids = (
        "thaumaturgist.ability.miracleblade",
        "thaumaturgist.ability.miracleshackles",
        "thaumaturgist.ability.miraclepotion",
        "thaumaturgist.ability.miraclecrystal",
    )
    for row, (node_id, level) in enumerate(
        zip(miracle_ids, (65, 70, 75, 80)),
        start=2,
    ):
        node = nodes[node_id]
        assert node.position == (4, row)
        assert node.payload["level_requirement"] == level
        expected = (miracle_ids[row - 3],) if row > 2 else ()
        assert node.prerequisites == expected


def test_promoted_trees_drop_ability_gates_below_their_promotion_floor():
    thaumaturgist_nodes = _nodes("Thaumaturgist")
    carried_ids = (
        "mage.ability.conjure-animal",
        "conjurer.ability.conjure-monster",
        "conjurer.ability.conjure-spirit",
        "conjurer.ability.conjure-fiend",
        "conjurer.ability.conjure-celestial",
        "conjurer.ability.conjure-dragon",
    )

    assert all(
        effective_node_level_requirement(
            thaumaturgist_nodes[node_id],
            "Thaumaturgist",
        ) == 0
        for node_id in carried_ids
    )
    assert effective_node_level_requirement(
        thaumaturgist_nodes["thaumaturgist.ability.miracleblade"],
        "Thaumaturgist",
    ) == 65
    conjure_dragon = thaumaturgist_nodes["conjurer.ability.conjure-dragon"]
    assert effective_node_level_requirement(conjure_dragon, "Conjurer") == 55


def test_thaumaturgist_tree_choice_binds_xenid_and_unlocks_ultimate():
    thaumaturgist = _player("Thaumaturgist")
    thaumaturgist.progression.completed_trees.update({"Mage", "Conjurer"})
    thaumaturgist.progression.purchased_node_ids.update({
        "mage.mana.conjuration-reserve",
        "mage.ability.conjure-animal",
    })

    choice = purchase_node(
        thaumaturgist,
        "thaumaturgist.talent.bind-animal",
        node_choices={"xenid": "Caladrius"},
    )
    ultimate = purchase_node(
        thaumaturgist,
        "thaumaturgist.talent.animal-ultimate",
    )

    assert choice.success
    assert ultimate.success
    assert thaumaturgist.xenid_choices["Animal"] == "Caladrius"
    assert set(thaumaturgist.summons) == {"Caladrius"}
    assert "Resurrection" in thaumaturgist.summons["Caladrius"].spellbook["Spells"]


def test_xenid_conduit_replaces_experience_growth_and_shapes_the_caster():
    thaumaturgist = _player("Thaumaturgist")
    assert companions.choose_xenid(
        thaumaturgist,
        "Monster",
        "Cacus",
    )[0]
    cacus = thaumaturgist.summons["Cacus"]
    starting_attack = cacus.combat.attack

    promotion_kits.gain_summon_bond(
        thaumaturgist,
        "Cacus",
        100,
        "test",
    )

    assert cacus.level.exp == 0
    assert cacus.level.exp_to_gain == 0
    assert cacus.level.level == 10
    assert cacus.combat.attack > starting_attack
    assert promotion_kits.xenid_caster_attribute_bonus(
        thaumaturgist,
        "strength",
    ) == 5
    assert promotion_kits.xenid_caster_multiplier(
        thaumaturgist,
        "melee",
    ) == pytest.approx(1.15)
    thaumaturgist.progression.purchased_node_ids.add(
        "thaumaturgist.talent.conduit-mastery"
    )
    assert promotion_kits.xenid_caster_attribute_bonus(
        thaumaturgist,
        "strength",
    ) == 7
    assert promotion_kits.xenid_caster_multiplier(
        thaumaturgist,
        "melee",
    ) == pytest.approx(1.225)


def test_xenid_roster_is_exactly_the_seven_declared_pairs():
    assert companions.XENID_PAIRS == {
        "Animal": ("Hodag", "Caladrius"),
        "Humanoid": ("Patagon", "Kobalos"),
        "Monster": ("Dilong", "Cacus"),
        "Spirit": ("Agloolik", "Izulu"),
        "Fiend": ("Hala", "Lamashtu"),
        "Celestial": ("Seraphim", "Bardi"),
        "Dragon": ("Tiamat", "Zahhak"),
    }
    assert len(companions.XENID_NAMES) == 14


def test_thaumaturgist_preview_explains_calling_carry_forward():
    conjurer = _player("Conjurer")

    preview = promotion_preview(
        conjurer,
        "conjurer.promotion.thaumaturgist",
    )

    assert "Conjure Animal and all six Conjurer Calling nodes" in preview.warning
    assert "permanent paired-Xenid choice" in preview.warning


def test_floating_crystal_siphons_percent_mana_and_scales_with_spell_power():
    class Tile:
        enemy = None

        def available_actions(self, _player):
            return ["Attack", "Cast Spell", "Defend"]

        def __str__(self):
            return "Floating Crystal Test"

    player = _player("Conjurer", level=30)
    player.mana.max = 200
    player.mana.current = 200
    enemy = enemies.Goblin()
    enemy.health.max = 10_000
    enemy.health.current = 10_000
    spell_power = int(player.check_mod("magic", enemy=enemy))
    engine = BattleEngine(player, enemy, Tile())
    engine.start_battle()

    abilities.FloatingCrystal().cast(player)
    assert player.floating_crystal["threshold"] == 60
    for _turn in range(3):
        engine.attacker = player
        engine.defender = enemy
        engine._turn_action_committed = True
        result = engine.post_turn()

    expected_damage = int(60 * (1 + spell_power / 100))
    assert player.mana.current == 140
    assert player.floating_crystal is None
    assert enemy.health.current == 10_000 - expected_damage
    assert any(
        f"with {spell_power} spell power" in message
        for message in result.messages
    )


def test_miracles_consume_reality_fragments_and_break_normal_rules():
    thaumaturgist = _player("Thaumaturgist", level=80)
    thaumaturgist.mana.max = 500
    thaumaturgist.mana.current = 500
    target = enemies.Goblin()
    target.health.max = 1_000
    target.health.current = 1_000

    blade = abilities.MiracleBlade()
    mana_before = thaumaturgist.mana.current
    assert "needs a Reality Fragment" in blade.cast(thaumaturgist, target)
    assert thaumaturgist.mana.current == mana_before

    thaumaturgist.modify_inventory(items.RealityFragment(), num=3)
    blade_message = blade.cast(thaumaturgist, target)
    assert "every protection" in blade_message
    assert target.health.current <= 750
    assert len(thaumaturgist.inventory["Reality Fragment"]) == 2

    shackles = abilities.MiracleShackles()
    shackles.cast(thaumaturgist, target)
    assert target.conjured_shackles == {
        "turns": 3,
        "difficulty": 0,
        "unbreakable": True,
    }

    potion = abilities.MiraclePotion()
    potion.cast(thaumaturgist)
    assert "Reality Fragment" not in thaumaturgist.inventory
    assert "Master Health Potion" in thaumaturgist.inventory
    assert "Master Mana Potion" in thaumaturgist.inventory


def test_miracle_crystal_creates_mana_and_damages_every_enemy():
    class Tile:
        enemy = None

        def available_actions(self, _player):
            return ["Attack", "Cast Spell", "Defend"]

        def __str__(self):
            return "Miracle Crystal Test"

    thaumaturgist = _player("Thaumaturgist", level=80)
    thaumaturgist.mana.max = 400
    thaumaturgist.mana.current = 400
    thaumaturgist.modify_inventory(items.RealityFragment())
    first = enemies.Goblin()
    second = enemies.GreenSlime()
    for target in (first, second):
        target.health.max = 10_000
        target.health.current = 10_000
    engine = BattleEngine(
        thaumaturgist,
        tile=Tile(),
        encounter=CombatEncounter.from_enemies([first, second]),
    )
    engine.start_battle()

    spell = abilities.MiracleCrystal()
    spell.cast(thaumaturgist)
    mana_after_cast = thaumaturgist.mana.current
    for _turn in range(4):
        engine.attacker = thaumaturgist
        engine.defender = first
        engine._turn_action_committed = True
        result = engine.post_turn()

    assert mana_after_cast == 400 - spell.cost
    assert thaumaturgist.mana.current == mana_after_cast
    assert first.health.current < 10_000
    assert second.health.current == first.health.current
    assert thaumaturgist.floating_crystal is None
    assert any("every enemy" in message for message in result.messages)


def test_explosive_decoy_requires_and_consumes_one_mirror_image():
    conjurer = _player("Conjurer")
    target = enemies.Goblin()
    decoy = abilities.ExplosiveDecoy()
    mana_before = conjurer.mana.current

    assert "requires a remaining Mirror Image" in decoy.cast(conjurer, target)

    duplicates = conjurer.magic_effects["Duplicates"]
    duplicates.active = True
    duplicates.duration = 2
    health_before = target.health.current
    message = decoy.cast(conjurer, target)

    assert "explodes" in message
    assert duplicates.active
    assert duplicates.duration == 1
    assert conjurer.mana.current == mana_before - decoy.cost
    assert target.health.current < health_before


def test_necromancer_raise_dead_adds_rewardless_undead_to_turn_order():
    class Tile:
        enemy = None

        def available_actions(self, _player):
            return ["Attack", "Cast Spell", "Defend"]

        def __str__(self):
            return "Necromancer Test"

    player = _player("Warrior")
    necromancer = enemies.Necromancer()
    engine = BattleEngine(player, necromancer, Tile())
    engine.start_battle()

    message = necromancer.spellbook["Spells"]["Raise Dead"].cast(
        necromancer,
        player,
        battle_engine=engine,
    )

    assert "Raised Ghoul" in message
    assert len(engine.encounter.members) == 2
    raised = engine.encounter.members[1].enemy
    assert raised.name == "Raised Ghoul"
    assert raised.gold == 0
    assert raised.level.exp == 0
    assert engine.encounter.members[1].combatant_id in engine.fixed_turn_order


def test_conjurer_promotes_to_thaumaturgist_without_an_automatic_xenid():
    conjurer = _promote("Conjurer")
    assert "Summon" not in conjurer.spellbook["Skills"]
    assert not getattr(conjurer, "summons", {})

    conjurer.level.level = 100
    conjurer.progression.level = 100
    result = apply_progression_plan(
        conjurer,
        (
            "conjurer.ability.conjure-humanoid",
            "conjurer.ability.conjure-monster",
            "conjurer.ability.conjure-spirit",
            "conjurer.ability.conjure-fiend",
            "conjurer.ability.conjure-celestial",
            "conjurer.ability.conjure-dragon",
            "conjurer.promotion.thaumaturgist",
        ),
        {},
    )

    assert result.success
    assert conjurer.cls.name == "Thaumaturgist"
    assert conjurer.cls.pro_level == 3
    assert "Summon" not in conjurer.spellbook["Skills"]
    assert not conjurer.summons

    success, _message = companions.choose_xenid(
        conjurer,
        "Humanoid",
        "Patagon",
    )
    competing_success, _message = companions.choose_xenid(
        conjurer,
        "Humanoid",
        "Kobalos",
    )
    assert success
    assert not competing_success
    assert set(conjurer.summons) == {"Patagon"}


def test_new_abilities_are_owned_by_the_mage_catalog():
    names = {
        ability().name
        for levels in (
            abilities.spell_dict["Mage"],
            abilities.skill_dict["Mage"],
        )
        for raw in levels.values()
        for ability in abilities.ability_classes_for(raw)
    }
    assert {
        "Polymorph",
        "Inflate Health",
        "Enliven Dead",
        "Conjure Blade",
        "Conjure Animal",
        "Conjure Shackles",
        "Conjure Potion",
        "Classical Force",
        "Arcane Tradition",
    }.issubset(names)
    assert hasattr(abilities, "ArcaneTradition")


def test_obsolete_summon_training_abilities_are_removed():
    assert not hasattr(abilities, "Summon")
    assert not hasattr(abilities, "Summon2")
