"""Regression coverage for generated ability-tree reference diagrams."""

from src.core.ability_tree_diagrams import (
    OUTPUT_DIRECTORY,
    class_slug,
    render_index,
    render_tree_svg,
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
        path = OUTPUT_DIRECTORY / f"{class_slug(class_name)}.svg"
        assert path.read_text(encoding="utf-8") == render_tree_svg(class_name)


def test_promoted_tree_diagrams_hide_redundant_carried_ability_levels():
    thaumaturgist = render_tree_svg("Thaumaturgist")

    assert "Conjure Dragon" in thaumaturgist
    assert "Level 55" not in thaumaturgist
    assert "Miracle Blade" in thaumaturgist
    assert "Level 65" in thaumaturgist
