"""Tests for the foundational characterization tool."""

from tools.characterize_foundational_contract import (
    ability_inventory,
    approved_contact_matrix,
    contact_matrix,
)


def test_ability_inventory_captures_pre_migration_shape():
    inventory = ability_inventory()

    assert inventory["ability_count"] == 197
    assert inventory["filename_slugs_unique"] is True
    assert inventory["legacy_value_counts"]["type"]["Skill"] == 81
    assert inventory["legacy_value_counts"]["type"]["Spell"] == 47
    assert inventory["missing_legacy_fields"]["subtype"] == 11
    assert inventory["missing_legacy_fields"]["school"] == 158


def test_contact_matrix_is_seeded_and_records_both_legacy_rolls():
    first = contact_matrix(samples=5, seed=1337)
    second = contact_matrix(samples=5, seed=1337)

    assert first == second
    assert first["ordinary_stats"] == [6, 10, 14, 18, 22]
    assert set(first["matrices"]) == {"weapon", "spell"}
    assert len(first["matrices"]["weapon"]) == 25
    assert len(first["matrices"]["spell"]) == 25
    assert all(0 <= cell["land_rate"] <= 1 for cell in first["matrices"]["weapon"])


def test_approved_contact_matrix_is_seeded_and_covers_decided_axes():
    first = approved_contact_matrix(samples=2, seed=1337)
    second = approved_contact_matrix(samples=2, seed=1337)

    assert first == second
    assert len(first["weapon"]["cells"]) == 100
    assert len(first["spell"]["cells"]) == 75
    assert first["weapon"]["armor_groups"] == ["none", "light", "medium", "heavy"]
    assert first["spell"]["charisma_terms"] == [-5, 0, 5]
