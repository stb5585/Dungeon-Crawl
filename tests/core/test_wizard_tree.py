"""Focused coverage for the authored Wizard tree and Photon Sphere quest."""

from src.core import abilities, enemies
from src.core.classes import wizard
from src.core.combat.contact import ContactResult
from src.core.progression import ABILITY_TREES, NodeState, available_nodes
from tests.test_framework import TestGameState


def _player(level: int = 95):
    player = TestGameState.create_player(
        class_name="Wizard",
        race_name="Human",
        level=level,
        stats={
            "strength": 20,
            "intel": 35,
            "wisdom": 30,
            "con": 20,
            "charisma": 20,
            "dex": 20,
        },
    )
    player.wizard_affinity = wizard.default_affinity()
    player.wizard_affinity_version = 2
    return player


def test_wizard_tree_uses_master_spells_modifiers_and_quest_placeholder():
    tree = ABILITY_TREES["Wizard"]
    nodes = {node.payload.get("revealed_name", node.name): node for node in tree.nodes}

    assert len(tree.nodes) == 28
    assert [
        nodes[name].position
        for name in (
            "Firestorm",
            "Blizzard",
            "Electrocution",
            "Tornado",
            "Tsunami",
            "Earthquake",
        )
    ] == [(0, row) for row in range(6)]
    assert nodes["Magic Missile III"].payload["school_affinity"] == (
        "Arcane",
        80,
    )
    assert nodes["Fragmentation"].prerequisites == (nodes["Magic Missile III"].id,)
    assert {"Kinetic Explosion", "Arcane Empowerment"}.isdisjoint(nodes)
    assert nodes["Photon Sphere"].icon_key == "unknown"
    assert nodes["Prismatic Cataclysm"].icon_key == "unknown"
    assert nodes["Mana Splinters"].position == (2, 2)
    assert nodes["Mana Splinters"].prerequisites == (nodes["Fragmentation"].id,)
    assert nodes["Detonation Cascade"].position == (2, 3)
    assert nodes["Detonation Cascade"].payload["level_requirement"] == 75
    assert nodes["Detonation Cascade"].prerequisites == (nodes["Mana Splinters"].id,)
    assert nodes["Photon Sphere"].position == (2, 6)
    assert nodes["Spaghettification"].prerequisites == (nodes["Photon Sphere"].id,)
    assert nodes["Spaghettification"].position == (2, 7)
    assert nodes["Prismatic Cataclysm"].position == (0.5, 6)
    assert nodes["Elemental Convergence"].position == (0.5, 7)
    assert nodes["Elemental Convergence"].prerequisites == (nodes["Prismatic Cataclysm"].id,)
    assert nodes["Counterspell"].position == (3, 0)
    assert nodes["Counterspell"].payload.get("level_requirement") is None
    assert nodes["Gravitational Pull"].position == (3, 1)
    assert nodes["Gravitational Pull"].payload["level_requirement"] == 65
    assert nodes["Petrify"].position == (3, 4)
    assert nodes["Petrify"].payload["level_requirement"] == 80
    assert nodes["Volitation"].position == (4, 0)
    assert nodes["Mirror Image II"].position == (4, 1)
    assert nodes["Multiplicity"].position == (4, 2)
    assert nodes["Teleport"].position == (4, 3)
    assert nodes["Triplecast"].position == (4, 6)
    assert nodes["Triplecast"].payload["level_requirement"] == 90
    assert nodes["Mirror Image II"].payload["level_requirement"] == 65
    assert nodes["Multiplicity"].payload["level_requirement"] == 70
    assert nodes["Teleport"].payload["level_requirement"] == 75

    removed = {
        "Firebolt",
        "Ice Lance",
        "Shock",
        "Gust",
        "Water Jet",
        "Tremor",
        "Magic Missile",
        "Arcane Fundamentals",
        "Guidance Upgrade",
        "Perfected Formula",
        "Layered Countermagic",
        "Mana Rupture",
    }
    assert removed.isdisjoint(nodes)


def test_wizard_master_spells_are_affinity_gated_and_spaghettification_hidden():
    player = _player()
    status_list = available_nodes(player)
    statuses = {status.node.name: status for status in status_list}

    assert statuses["Firestorm"].state == NodeState.BLOCKED
    assert "Requires 80 Fire affinity" in statuses["Firestorm"].reasons[0]
    assert "Spaghettification" not in statuses
    assert "Elemental Convergence" not in statuses
    assert [status.node.name for status in status_list].count("Unknown") == 2
    assert "Photon Sphere" not in statuses
    assert "Prismatic Cataclysm" not in statuses

    player.wizard_affinity["Fire"] = 80
    statuses = {status.node.name: status for status in available_nodes(player)}
    assert statuses["Firestorm"].state == NodeState.AVAILABLE


def test_observing_domingo_starts_difficult_research_and_unlocks_spell():
    player = _player()
    message = wizard.observe_photon_sphere(player, enemies.Domingo())

    assert "Quest started" in message
    quest = player.quest_dict["Side"][wizard.PHOTON_SPHERE_QUEST]
    assert quest["Stage"] == "consult_scientists"

    message = wizard.consult_photon_sphere_scientists(player)
    assert "six distinct proofs" in message
    player.quests(enemy=enemies.FlameWisp())
    assert quest["Killed"] == 0
    for enemy_name in wizard.ARCANE_EVIDENCE_ENEMIES:
        wizard.record_ultimate_quest_defeat(player, enemy_name)
    assert quest["Completed"] is True

    mana_before = player.mana.max
    points_before = player.progression.unspent_points
    message = wizard.consult_photon_sphere_scientists(player)
    assert "learn Photon Sphere" in message
    assert "Photon Sphere" in player.spellbook["Spells"]
    assert quest["Turned In"] is True
    assert "wizard.ability.photon-sphere" in player.progression.purchased_node_ids
    assert player.mana.max == mana_before + 50
    assert player.progression.unspent_points == points_before + 3

    statuses = {status.node.name: status for status in available_nodes(player)}
    assert "Photon Sphere" in statuses


def test_elemental_ultimate_requires_six_myrmidons_and_mastery():
    player = _player()
    message = wizard.observe_elemental_ultimate(player, enemies.Circe())
    assert "Sixfold Calamity" in message
    wizard.consult_elemental_ultimate_scientists(player)
    for enemy_name in wizard.ELEMENTAL_EVIDENCE_ENEMIES:
        wizard.record_ultimate_quest_defeat(player, enemy_name)

    assert wizard.consult_elemental_ultimate_scientists(player) == ""
    for school in wizard.OPPOSITES:
        player.wizard_affinity[school] = wizard.WIZARD_MASTERY_THRESHOLD
    message = wizard.consult_elemental_ultimate_scientists(player)

    assert "learn Prismatic Cataclysm" in message
    assert "Prismatic Cataclysm" in player.spellbook["Spells"]


def test_photon_sphere_is_a_multi_target_four_hit_spell_costing_150_mp():
    spell = abilities.PhotonSphere()

    assert spell.name == "Photon Sphere"
    assert spell.cost == 150
    assert spell.missiles == 4
    assert spell.target_scope.value == "all_enemies"

    elemental = abilities.PrismaticCataclysm()
    assert elemental.cost == 180
    assert elemental.target_scope.value == "all_enemies"


def test_gravitational_pull_slows_grounded_and_pins_flying_targets(monkeypatch):
    player = _player()
    grounded = enemies.Goblin()
    grounded.flying = False
    flying = enemies.Goblin()
    flying.flying = True
    spell = abilities.GravitationalPull()
    monkeypatch.setattr(
        player,
        "resolve_contact",
        lambda *_args, **_kwargs: ContactResult(hit=True, chance=1.0, roll=None, always_hit=True),
    )

    grounded_result = spell.cast(player, grounded)
    flying_result = spell.cast(player, flying)

    assert grounded_result.damage > 0
    assert grounded.stat_effects["Speed"].duration == 2
    assert grounded.stat_effects["Speed"].extra < 0
    assert flying_result.damage > 0
    assert flying.flying is False
    assert flying.status_effects["Stun"].active
    assert flying.status_effects["Stun"].duration == 2
