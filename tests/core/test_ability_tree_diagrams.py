"""Regression coverage for generated ability-tree reference diagrams."""

from html import escape
from pathlib import Path

from src.core.ability_tree_diagrams import (
    MANUALLY_AUTHORED_DIAGRAM_CLASSES,
    OUTPUT_DIRECTORY,
    base_class_name,
    diagram_relative_path,
    render_index,
    render_tree_svg,
    write_all,
)
from src.core.progression import ABILITY_TREES


def test_generated_ability_tree_diagrams_match_runtime_trees():
    assert (OUTPUT_DIRECTORY / "README.md").read_text(
        encoding="utf-8",
    ) == render_index()
    expected = {
        diagram_relative_path(class_name)
        for class_name in ABILITY_TREES
    }
    actual = {
        path.relative_to(OUTPUT_DIRECTORY)
        for path in OUTPUT_DIRECTORY.rglob("*.svg")
    }
    assert actual == expected
    for class_name in ABILITY_TREES:
        if class_name in MANUALLY_AUTHORED_DIAGRAM_CLASSES:
            continue
        path = OUTPUT_DIRECTORY / diagram_relative_path(class_name)
        assert path.read_text(encoding="utf-8") == render_tree_svg(class_name)


def test_mage_diagram_is_authoritative_and_tracks_runtime_nodes():
    mage_svg = (
        OUTPUT_DIRECTORY / diagram_relative_path("Mage")
    ).read_text(encoding="utf-8")

    for node in ABILITY_TREES["Mage"].nodes:
        label = node.name if len(node.name) <= 25 else f"{node.name[:22]}..."
        assert f">{escape(label)}</text>" in mage_svg


def test_regeneration_preserves_manually_authored_mage_svg(tmp_path):
    mage_path = tmp_path / "mage.svg"
    mage_path.write_text("authoritative mage connectors\n", encoding="utf-8")

    write_all(tmp_path)

    organized_path = tmp_path / diagram_relative_path("Mage")
    assert organized_path.read_text(encoding="utf-8") == "authoritative mage connectors\n"
    assert not mage_path.exists()


def test_promoted_tree_diagrams_hide_redundant_carried_ability_levels():
    thaumaturgist = render_tree_svg("Thaumaturgist")

    assert "Conjure Dragon" in thaumaturgist
    assert "Level 55" not in thaumaturgist
    assert "Miracle Blade" in thaumaturgist
    assert "Level 65" in thaumaturgist


def test_spellblade_diagram_matches_authored_runtime_tree():
    path = OUTPUT_DIRECTORY / diagram_relative_path("Spellblade")

    assert path.read_text(encoding="utf-8") == render_tree_svg("Spellblade")


def test_diagram_paths_group_by_base_lineage_and_promotion_level():
    assert base_class_name("Dragoon") == "Warrior"
    assert diagram_relative_path("Warrior") == Path("warrior/base/warrior.svg")
    assert diagram_relative_path("Lancer") == Path(
        "warrior/first-promotion/lancer.svg"
    )
    assert diagram_relative_path("Dragoon") == Path(
        "warrior/second-promotion/dragoon.svg"
    )


def test_authored_promotion_connectors_join_at_the_target_row():
    spellblade = render_tree_svg("Spellblade")

    assert 'M 136.0 623.0 V 823.0 H 469.0 V 823.0' in spellblade
    assert 'M 358.0 723.0 V 823.0 H 469.0 V 823.0' in spellblade
    assert 'M 580.0 723.0 V 823.0 H 469.0 V 823.0' in spellblade


def test_sorcerer_arcane_ritual_connector_enters_from_above():
    sorcerer = render_tree_svg("Sorcerer")

    assert 'M 486.0 623.0 H 469.0 V 692.0 H 469.0' in sorcerer


def test_passive_nodes_use_distinct_svg_colors():
    sorcerer = render_tree_svg("Sorcerer")

    assert 'fill="#263b2b" stroke="#72c987"' in sorcerer


def test_all_stat_and_resource_nodes_share_a_non_promotion_color():
    mage = render_tree_svg("Mage")
    warrior = render_tree_svg("Warrior")

    stat_color = 'fill="#17383a" stroke="#63d3ca"'
    promotion_color = 'fill="#3b2d12" stroke="#f4bf2a"'
    assert mage.count(stat_color) + warrior.count(stat_color) >= 4
    assert promotion_color in mage
    assert stat_color != promotion_color
    for legacy_color in (
        'fill="#3b3218" stroke="#e3bc48"',
        'fill="#401d25" stroke="#e46b78"',
        'fill="#182f45" stroke="#6aa8e8"',
    ):
        assert legacy_color not in mage + warrior


def test_non_mana_resource_nodes_use_distinct_svg_colors_and_labels():
    sentinel = render_tree_svg("Sentinel")
    paladin = render_tree_svg("Paladin")

    assert 'fill="#3d2418" stroke="#ed8a3d"' in sentinel
    assert "Resolve</text>" in sentinel
    assert 'fill="#42360f" stroke="#f0d45a"' in paladin
    assert "Oath Conviction</text>" in paladin


def test_developer_diagrams_reveal_ultimate_names():
    wizard = render_tree_svg("Wizard")

    assert ">Photon Sphere</text>" in wizard
    assert ">Prismatic Cataclysm</text>" in wizard


def test_warlock_familiar_bond_connector_uses_side_midpoints():
    warlock = render_tree_svg("Warlock")

    assert 'M 1340.0 223.0 H 1357.0 V 723.0 H 1340.0' in warlock
