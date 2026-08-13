"""Regression coverage for generated ability-tree reference diagrams."""

from html import escape

from src.core.ability_tree_diagrams import (
    MANUALLY_AUTHORED_DIAGRAM_CLASSES,
    OUTPUT_DIRECTORY,
    class_slug,
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
        f"{class_slug(class_name)}.svg"
        for class_name in ABILITY_TREES
    }
    actual = {path.name for path in OUTPUT_DIRECTORY.glob("*.svg")}
    assert actual == expected
    for class_name in ABILITY_TREES:
        if class_name in MANUALLY_AUTHORED_DIAGRAM_CLASSES:
            continue
        path = OUTPUT_DIRECTORY / f"{class_slug(class_name)}.svg"
        assert path.read_text(encoding="utf-8") == render_tree_svg(class_name)


def test_mage_diagram_is_authoritative_and_tracks_runtime_nodes():
    mage_svg = (OUTPUT_DIRECTORY / "mage.svg").read_text(encoding="utf-8")

    for node in ABILITY_TREES["Mage"].nodes:
        label = node.name if len(node.name) <= 25 else f"{node.name[:22]}..."
        assert f">{escape(label)}</text>" in mage_svg


def test_regeneration_preserves_manually_authored_mage_svg(tmp_path):
    mage_path = tmp_path / "mage.svg"
    mage_path.write_text("authoritative mage connectors\n", encoding="utf-8")

    write_all(tmp_path)

    assert mage_path.read_text(encoding="utf-8") == "authoritative mage connectors\n"


def test_promoted_tree_diagrams_hide_redundant_carried_ability_levels():
    thaumaturgist = render_tree_svg("Thaumaturgist")

    assert "Conjure Dragon" in thaumaturgist
    assert "Level 55" not in thaumaturgist
    assert "Miracle Blade" in thaumaturgist
    assert "Level 65" in thaumaturgist


def test_spellblade_diagram_matches_authored_runtime_tree():
    path = OUTPUT_DIRECTORY / "spellblade.svg"

    assert path.read_text(encoding="utf-8") == render_tree_svg("Spellblade")


def test_authored_promotion_connectors_join_at_the_target_row():
    spellblade = render_tree_svg("Spellblade")

    assert 'M 136.0 623.0 V 823.0 H 469.0 V 823.0' in spellblade
    assert 'M 358.0 723.0 V 823.0 H 469.0 V 823.0' in spellblade
    assert 'M 580.0 723.0 V 823.0 H 469.0 V 823.0' in spellblade
