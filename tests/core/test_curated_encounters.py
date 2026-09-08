"""Development-only curated multi-enemy encounter contracts."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from src.core import enemies


class _RolloutRng:
    """Deterministic source that selects the Pilot 3 branch."""

    def random(self):
        return 0.0

    def choice(self, candidates):
        return candidates[0]


def test_curated_pair_catalog_is_stable_and_builds_fresh_rosters():
    specs = enemies.curated_encounter_specs()

    assert [(spec.key, spec.display_name, spec.floor) for spec in specs] == [
        ("carrion_crawl", "Giant Hornet & Battle Toad", 1),
        ("wing_and_mattock", "Electric Bat & Battle Toad", 1),
        ("fang_and_spear", "Twisted Dwarf & Vampire Bat", 2),
        ("grave_web", "Zombie & Quasit", 1),
        ("lesser_conspiracy", "Battle Toad & Satyr", 1),
        ("hoof_and_howl", "Twisted Dwarf & Xorn", 2),
        ("rot_and_raptor", "Ghoul & Golden Eagle", 3),
        ("venomous_dream", "Night Hag & Pit Viper", 3),
        ("burrow_and_bone", "Antlion & Troll", 4),
    ]

    first = enemies.build_curated_encounter("carrion_crawl")
    second = enemies.build_curated_encounter("carrion_crawl")

    assert [member.enemy.name for member in first.members] == [
        "Giant Hornet",
        "Battle Toad",
    ]
    assert first.encounter_id != second.encounter_id
    assert first.primary_enemy is not second.primary_enemy
    by_key = {spec.key: spec for spec in specs}
    assert (
        by_key["grave_web"].health_multiplier,
        by_key["grave_web"].offense_multiplier,
    ) == (0.85, 1.2)
    assert (
        by_key["lesser_conspiracy"].health_multiplier,
        by_key["lesser_conspiracy"].offense_multiplier,
    ) == (0.8, 1.1)
    assert (
        by_key["hoof_and_howl"].health_multiplier,
        by_key["hoof_and_howl"].offense_multiplier,
    ) == (0.9, 1.1)
    assert (
        by_key["venomous_dream"].health_multiplier,
        by_key["venomous_dream"].offense_multiplier,
    ) == (0.8, 1.2)
    assert (
        by_key["burrow_and_bone"].health_multiplier,
        by_key["burrow_and_bone"].offense_multiplier,
    ) == (0.9, 0.95)


def test_curated_override_applies_only_through_random_enemy(monkeypatch):
    monkeypatch.setenv("DUNGEON_FORCE_ENCOUNTER", "fang_and_spear")
    selected = enemies.random_enemy("2", allow_curated_encounter=True)

    encounter = selected._runtime_combat_encounter
    assert encounter.primary_enemy is selected
    assert [member.enemy.name for member in encounter.members] == [
        "Twisted Dwarf",
        "Vampire Bat",
    ]


@pytest.mark.parametrize(
    ("key", "floor", "member_names"),
    (
        ("grave_web", "1", ("Zombie", "Quasit")),
        ("lesser_conspiracy", "1", ("Battle Toad", "Satyr")),
        ("hoof_and_howl", "2", ("Twisted Dwarf", "Xorn")),
    ),
)
def test_pilot_two_overrides_build_authored_fresh_rosters(
    monkeypatch,
    key,
    floor,
    member_names,
):
    monkeypatch.setenv("DUNGEON_FORCE_ENCOUNTER", key)

    first = enemies.random_enemy(floor, allow_curated_encounter=True)
    first_encounter = first._runtime_combat_encounter
    second = enemies.build_curated_encounter(key)

    assert tuple(member.enemy.name for member in first_encounter.members) == member_names
    assert first_encounter.encounter_id != second.encounter_id
    assert all(
        first_member.enemy is not second_member.enemy
        for first_member, second_member in zip(
            first_encounter.members,
            second.members,
        )
    )


@pytest.mark.parametrize(
    ("key", "floor", "member_names"),
    (
        ("rot_and_raptor", "3", ("Ghoul", "Golden Eagle")),
        ("venomous_dream", "3", ("Night Hag", "Pit Viper")),
        ("burrow_and_bone", "4", ("Antlion", "Troll")),
    ),
)
def test_deeper_floor_pilot_overrides_build_authored_fresh_rosters(
    monkeypatch,
    key,
    floor,
    member_names,
):
    monkeypatch.setenv("DUNGEON_FORCE_ENCOUNTER", key)

    selected = enemies.random_enemy(floor, allow_curated_encounter=True)
    encounter = selected._runtime_combat_encounter

    assert tuple(member.enemy.name for member in encounter.members) == member_names
    assert all(member.enemy.health.current > 0 for member in encounter.members)


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

    assert [member.enemy.name for member in selected._runtime_combat_encounter.members] == [
        "Giant Hornet",
        "Battle Toad",
    ]


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


def test_ordinary_rollout_requires_evidence_qualification(monkeypatch):
    monkeypatch.setattr(enemies.encounters, "QUALIFIED_PILOT3_PAIR_KEYS", ())

    selected = enemies.random_enemy(
        "3",
        rng=_RolloutRng(),
        allow_pilot3_rollout=True,
    )

    assert not hasattr(selected, "_runtime_combat_encounter")


def test_qualified_ordinary_rollout_builds_a_pair_at_fixed_rate(monkeypatch):
    monkeypatch.setattr(
        enemies.encounters,
        "QUALIFIED_PILOT3_PAIR_KEYS",
        ("rot_and_raptor",),
    )

    selected = enemies.random_enemy(
        "3",
        rng=_RolloutRng(),
        allow_pilot3_rollout=True,
    )

    encounter = selected._runtime_combat_encounter
    assert enemies.encounters.PILOT3_PAIR_CHANCE == 0.15
    assert selected._curated_encounter_key == "rot_and_raptor"
    assert encounter.encounter_key == "rot_and_raptor"
    assert encounter.encounter_source == "curated"
    assert tuple(member.enemy.name for member in encounter.members) == ("Ghoul", "Golden Eagle")


def test_rollout_kill_switch_and_quest_targets_keep_generation_singleton(monkeypatch):
    monkeypatch.setattr(
        enemies.encounters,
        "QUALIFIED_PILOT3_PAIR_KEYS",
        ("rot_and_raptor",),
    )
    monkeypatch.setenv("DUNGEON_PILOT3_ROLLOUT", "off")

    disabled = enemies.random_enemy("3", rng=_RolloutRng(), allow_pilot3_rollout=True)
    assert not hasattr(disabled, "_runtime_combat_encounter")

    monkeypatch.setenv("DUNGEON_PILOT3_ROLLOUT", "on")
    quest_targeted = enemies.random_enemy(
        "3",
        preferred_names=("Ghoul",),
        rng=_RolloutRng(),
        allow_pilot3_rollout=True,
    )
    assert not hasattr(quest_targeted, "_runtime_combat_encounter")


def test_curated_multipliers_apply_only_to_fresh_pair_members():
    from src.core.enemies.encounters import CuratedEncounterSpec

    baseline = enemies.GiantCentipede()
    spec = CuratedEncounterSpec(
        key="scaled",
        display_name="Scaled",
        floor=1,
        member_factories=(enemies.GiantCentipede, enemies.Zombie),
        health_multiplier=0.8,
        offense_multiplier=1.2,
    )

    encounter = spec.build()

    assert encounter.primary_enemy.health.max == int(
        encounter.primary_enemy._curated_base_health_max * 0.8
    )
    assert encounter.primary_enemy.health.current == encounter.primary_enemy.health.max
    assert encounter.primary_enemy._encounter_offense_multiplier == 1.2
    assert not hasattr(baseline, "_encounter_offense_multiplier")
