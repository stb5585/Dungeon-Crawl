"""Development-only curated multi-enemy encounter contracts."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.core import enemies


def test_curated_pair_catalog_is_stable_and_builds_fresh_rosters():
    specs = enemies.curated_encounter_specs()

    assert [
        (spec.key, spec.display_name, spec.floor)
        for spec in specs
    ] == [
        ("carrion_crawl", "Carrion Crawl", 1),
        ("wing_and_mattock", "Wing and Mattock", 1),
        ("fang_and_spear", "Fang and Spear", 2),
    ]

    first = enemies.build_curated_encounter("carrion_crawl")
    second = enemies.build_curated_encounter("carrion_crawl")

    assert [member.enemy.name for member in first.members] == [
        "Giant Centipede",
        "Zombie",
    ]
    assert first.encounter_id != second.encounter_id
    assert first.primary_enemy is not second.primary_enemy


def test_curated_override_applies_only_through_random_enemy(monkeypatch):
    monkeypatch.setenv("DUNGEON_FORCE_ENCOUNTER", "fang_and_spear")
    selected = enemies.random_enemy("2", allow_curated_encounter=True)

    encounter = selected._runtime_combat_encounter
    assert encounter.primary_enemy is selected
    assert [member.enemy.name for member in encounter.members] == [
        "Gnoll",
        "Giant Snake",
    ]


def test_curated_override_validates_floor_and_override_conflicts(monkeypatch):
    monkeypatch.setenv("DUNGEON_FORCE_ENCOUNTER", "carrion_crawl")

    with pytest.raises(ValueError, match="belongs to floor 1"):
        enemies.random_enemy("2", allow_curated_encounter=True)

    monkeypatch.setenv("DUNGEON_FORCE_ENEMY", "Goblin")
    with pytest.raises(ValueError, match="cannot be used together"):
        enemies.random_enemy("1")


def test_curated_override_is_ignored_by_noncombat_random_consumers(monkeypatch):
    monkeypatch.setenv("DUNGEON_FORCE_ENCOUNTER", "carrion_crawl")

    selected = enemies.random_enemy("3")

    assert not hasattr(selected, "_runtime_combat_encounter")


def test_curated_override_remains_enabled_for_ordinary_dungeon_tiles(monkeypatch):
    from src.core.map_tiles.rules import quest_biased_random_enemy

    monkeypatch.setenv("DUNGEON_FORCE_ENCOUNTER", "carrion_crawl")
    player = SimpleNamespace(
        quest_dict={"Main": {}, "Side": {}, "Bounty": {}},
        stats=SimpleNamespace(charisma=10),
        check_mod=lambda *_args, **_kwargs: 0,
    )

    selected = quest_biased_random_enemy(player, "1")

    assert [
        member.enemy.name
        for member in selected._runtime_combat_encounter.members
    ] == ["Giant Centipede", "Zombie"]


def test_unknown_curated_pair_is_explicit_error():
    with pytest.raises(ValueError, match="Unknown curated encounter"):
        enemies.build_curated_encounter("not-a-pair")


def test_curated_runtime_metadata_is_not_written_to_enemy_state():
    from src.core.save_system.enemy import EnemyStateSerializer

    encounter = enemies.build_curated_encounter("carrion_crawl")
    encounter.primary_enemy._runtime_combat_encounter = encounter

    state = EnemyStateSerializer.serialize(encounter.primary_enemy)

    assert "encounter_state" not in state
    assert "_runtime_combat_encounter" not in state
