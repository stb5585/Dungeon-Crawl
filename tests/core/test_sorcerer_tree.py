"""Focused coverage for the authored Sorcerer ability tree."""

from src.core import abilities
from src.core.classes import wizard
from src.core.progression import (
    ABILITY_TREES,
    NodeKind,
    NodeState,
    available_nodes,
    purchase_node,
)
from tests.test_framework import TestGameState


ELEMENTAL_SPELLS = {
    "Fireball": (0, 0),
    "Icicle": (0, 1),
    "Lightning": (0, 2),
    "Hurricane": (0, 3),
    "Aqualung": (0, 4),
    "Mudslide": (0, 5),
}


def _player(level: int = 60):
    player = TestGameState.create_player(
        class_name="Sorcerer",
        race_name="Human",
        level=level,
        stats={
            "strength": 20,
            "intel": 30,
            "wisdom": 30,
            "con": 20,
            "charisma": 20,
            "dex": 20,
        },
    )
    player.wizard_affinity = wizard.default_affinity()
    player.wizard_affinity_version = 2
    return player


def test_tree_matches_authored_schools_specializations_and_utility_columns():
    tree = ABILITY_TREES["Sorcerer"]
    nodes = {node.name: node for node in tree.nodes}

    assert len(tree.nodes) == 30
    assert tree.branches == (
        "Elemental Spells",
        "Spell Modifiers",
        "Arcana",
        "Spell Enhancements",
        "Illusion",
    )
    assert {
        name: nodes[name].position for name in ELEMENTAL_SPELLS
    } == ELEMENTAL_SPELLS
    assert {
        name: nodes[name].position
        for name in (
            "Combustion",
            "Snowpiercer",
            "Paralyzer",
            "Ejection Gale",
            "Aspirate",
            "Unsteady Ground",
        )
    } == {
        "Combustion": (1, 0),
        "Snowpiercer": (1, 1),
        "Paralyzer": (1, 2),
        "Ejection Gale": (1, 3),
        "Aspirate": (1, 4),
        "Unsteady Ground": (1, 5),
    }
    assert nodes["Classical Enrichment"].position == (0.5, 6)
    assert nodes["Classical Enrichment"].payload["prerequisite_mode"] == "any"
    assert nodes["Arcane Ritual"].position == (1.5, 6)
    assert nodes["Arcane Ritual"].payload["connector_enter_from_top"] is True
    assert nodes["Promote: Wizard"].position == (1, 7)
    assert nodes["Promote: Wizard"].payload["prerequisite_mode"] == "any"
    assert nodes["Promote: Wizard"].prerequisites == (
        nodes["Classical Enrichment"].id,
        nodes["Arcane Ritual"].id,
    )

    assert nodes["Magic Missile II"].position == (2, 0)
    assert nodes["Force Multiplier"].prerequisites == (nodes["Magic Missile II"].id,)
    assert nodes["Mana Rupture"].position == (2, 2)
    assert nodes["Mana Rupture"].prerequisites == (
        nodes["Force Multiplier"].id,
    )
    assert nodes["Mana Leak"].prerequisites == (nodes["Mana Rupture"].id,)
    assert nodes["Kinetic Explosion"].position == (2, 4)
    assert nodes["Kinetic Explosion"].payload["level_requirement"] == 50
    assert nodes["Kinetic Explosion"].prerequisites == (
        nodes["Mana Leak"].id,
    )
    assert nodes["Arcane Empowerment"].prerequisites == (
        nodes["Kinetic Explosion"].id,
    )
    assert nodes["Arcane Ritual"].prerequisites == (
        nodes["Arcane Empowerment"].id,
    )
    assert nodes["Boost"].payload.get("level_requirement") is None
    assert nodes["Mirror Image"].payload.get("level_requirement") is None
    assert nodes["+20 Magic"].kind == NodeKind.RATING


def test_tier_two_spells_require_thirty_matching_affinity():
    player = _player()
    statuses = {
        status.node.name: status
        for status in available_nodes(player, "Sorcerer")
    }

    assert statuses["Fireball"].state == NodeState.BLOCKED
    assert "Requires 30 Fire affinity" in statuses["Fireball"].reasons[0]

    player.wizard_affinity["Fire"] = 30
    statuses = {
        status.node.name: status
        for status in available_nodes(player, "Sorcerer")
    }

    assert statuses["Fireball"].state == NodeState.AVAILABLE
    assert statuses["Icicle"].state == NodeState.BLOCKED


def test_removed_mage_roots_and_retired_placeholder_talents_are_absent():
    names = {node.name for node in ABILITY_TREES["Sorcerer"].nodes}

    assert {
        "Elemental Affinity",
        "Reactive Ward",
        "Firebolt",
        "Ice Lance",
        "Shock",
        "Gust",
        "Water Jet",
        "Tremor",
        "Magic Missile",
        "Arcane Fundamentals",
        "Guidance Upgrade",
    }.isdisjoint(names)


def test_one_elemental_spell_modifier_pair_unlocks_classical_enrichment():
    player = _player()
    player.wizard_affinity["Fire"] = 30
    player.spellbook["Spells"]["Firebolt"] = abilities.Firebolt()
    nodes = {node.name: node for node in ABILITY_TREES["Sorcerer"].nodes}

    assert purchase_node(player, nodes["Fireball"].id).success
    assert "Firebolt" not in player.spellbook["Spells"]
    assert "Fireball" in player.spellbook["Spells"]
    assert purchase_node(player, nodes["Combustion"].id).success

    statuses = {
        status.node.name: status
        for status in available_nodes(player, "Sorcerer")
    }
    assert statuses["Classical Enrichment"].state == NodeState.AVAILABLE
    assert statuses["Arcane Ritual"].state == NodeState.BLOCKED
