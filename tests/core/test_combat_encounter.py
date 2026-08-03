"""Regression coverage for the Slice 1 runtime encounter roster."""

from __future__ import annotations

from copy import deepcopy

import pytest

from src.core.combat import (
    CombatEncounter,
    EncounterEnemy,
    EnemyResolution,
)
from src.core.combat.battle_engine import BattleEngine
from src.core.enemies import Goblin, GreenSlime
from src.core.events.event_bus import EventType, get_event_bus, reset_event_bus
from tests.test_framework import TestGameState


class DummyCombatTile:
    """Minimal singleton combat tile."""

    def available_actions(self, _player):
        return ["Attack", "Flee"]


def _player():
    return TestGameState.create_player(
        name="EncounterTester",
        class_name="Warrior",
        race_name="Human",
    )


def test_encounter_rejects_empty_roster_and_mismatched_ids():
    with pytest.raises(ValueError, match="at least one"):
        CombatEncounter.from_enemies([])

    with pytest.raises(ValueError, match="every encounter enemy"):
        CombatEncounter.from_enemies([Goblin()], combatant_ids=["one", "two"])


def test_encounter_builds_stable_authored_identity_and_duplicate_labels():
    first = Goblin()
    second = Goblin()
    encounter = CombatEncounter.from_enemies(
        [first, second],
        encounter_id="enc-test",
        combatant_ids=["goblin-1", "goblin-2"],
    )

    assert encounter.encounter_id == "enc-test"
    assert [member.enemy for member in encounter.members] == [first, second]
    assert [member.slot for member in encounter.members] == [0, 1]
    assert [member.combatant_id for member in encounter.members] == [
        "goblin-1",
        "goblin-2",
    ]
    assert [member.display_label for member in encounter.members] == [
        "Goblin A",
        "Goblin B",
    ]
    assert encounter.primary_enemy is first
    assert encounter.member_by_id("goblin-2").enemy is second


def test_encounter_identity_survives_enemy_transformation():
    enemy = Goblin()
    encounter = CombatEncounter.singleton(
        enemy,
        encounter_id="transform-test",
        combatant_id="original-goblin",
    )

    enemy.name = "Direwolf"
    enemy.enemy_typ = "Animal"

    member = encounter.primary_member
    assert member.combatant_id == "original-goblin"
    assert member.canonical_name == "Goblin"
    assert member.display_label == "Goblin"


def test_encounter_rejects_duplicate_ids_and_unordered_slots():
    first = Goblin()
    second = GreenSlime()
    with pytest.raises(ValueError, match="unique"):
        CombatEncounter.from_enemies(
            [first, second],
            combatant_ids=["duplicate", "duplicate"],
        )

    member = EncounterEnemy(first, "first", 1, "Goblin", "Goblin")
    with pytest.raises(ValueError, match="authored order"):
        CombatEncounter([member])


def test_resolution_ledger_is_ordered_and_members_resolve_once():
    encounter = CombatEncounter.from_enemies(
        [Goblin(), GreenSlime()],
        combatant_ids=["goblin", "slime"],
    )

    first = encounter.resolve_enemy(
        "slime",
        EnemyResolution.EJECTED,
        cause="windswept",
    )
    second = encounter.resolve_enemy("goblin", EnemyResolution.MERCY)

    assert encounter.resolution_ledger == (first, second)
    assert encounter.member_by_id("slime").resolution is EnemyResolution.EJECTED
    assert encounter.member_by_id("slime").resolution_cause == "windswept"
    assert encounter.victory_ready is True
    with pytest.raises(ValueError, match="already been resolved"):
        encounter.resolve_enemy("slime", EnemyResolution.DEFEATED)
    with pytest.raises(KeyError):
        encounter.member_by_id("missing")


def test_dead_unresolved_enemy_is_not_a_living_hostile():
    encounter = CombatEncounter.singleton(Goblin())
    encounter.primary_enemy.health.current = 0

    assert encounter.living_members == []
    assert encounter.victory_ready is True


def test_engine_wraps_legacy_enemy_in_singleton_encounter():
    enemy = Goblin()
    engine = BattleEngine(_player(), enemy, DummyCombatTile())

    assert engine.encounter.primary_enemy is enemy
    assert not hasattr(engine, "enemy")
    assert len(engine.encounter.members) == 1
    assert engine.available_actions == ["Attack", "Flee"]


def test_engine_accepts_explicit_singleton_encounter():
    enemy = Goblin()
    encounter = CombatEncounter.singleton(
        enemy,
        encounter_id="explicit",
        combatant_id="enemy-slot",
    )
    engine = BattleEngine(
        _player(),
        tile=DummyCombatTile(),
        encounter=encounter,
    )

    assert engine.encounter is encounter
    assert engine.encounter.primary_enemy is enemy


def test_explicit_singleton_matches_legacy_start_behavior(monkeypatch):
    import src.core.combat.battle_engine.core as battle_core

    monkeypatch.setattr(
        battle_core,
        "determine_initiative",
        lambda player, enemy: (player, enemy),
    )
    legacy_player = _player()
    explicit_player = _player()
    legacy_enemy = Goblin()
    explicit_enemy = deepcopy(legacy_enemy)
    legacy = BattleEngine(legacy_player, legacy_enemy, DummyCombatTile())
    explicit = BattleEngine(
        explicit_player,
        tile=DummyCombatTile(),
        encounter=CombatEncounter.singleton(
            explicit_enemy,
            encounter_id="parity",
            combatant_id="parity-enemy",
        ),
    )

    legacy_order = legacy.start_battle()
    explicit_order = explicit.start_battle()

    assert [actor.name for actor in legacy_order] == [
        actor.name for actor in explicit_order
    ]
    assert legacy.available_actions == explicit.available_actions
    assert legacy_player.bestiary["Goblin"] == explicit_player.bestiary["Goblin"]
    assert legacy.logger.metadata["player"] == explicit.logger.metadata["player"]
    assert legacy.logger.metadata["enemy"] == explicit.logger.metadata["enemy"]
    assert legacy.logger.metadata["enemies"][0]["name"] == "Goblin"
    assert explicit.logger.metadata["enemies"][0]["name"] == "Goblin"


def test_engine_rejects_invalid_enemy_and_encounter_combinations():
    player = _player()
    enemy = Goblin()
    encounter = CombatEncounter.singleton(enemy)

    with pytest.raises(ValueError, match="exactly one"):
        BattleEngine(player, tile=DummyCombatTile())
    with pytest.raises(ValueError, match="exactly one"):
        BattleEngine(
            player,
            enemy,
            DummyCombatTile(),
            encounter=encounter,
        )
    with pytest.raises(ValueError, match="combat tile"):
        BattleEngine(player, enemy)


def test_engine_allows_pairs_but_rejects_larger_rosters():
    pair = CombatEncounter.from_enemies([Goblin(), GreenSlime()])
    engine = BattleEngine(
        _player(),
        tile=DummyCombatTile(),
        encounter=pair,
    )

    engine.start_battle()

    trio = CombatEncounter.from_enemies([Goblin(), GreenSlime(), Goblin()])
    engine = BattleEngine(_player(), tile=DummyCombatTile(), encounter=trio)
    with pytest.raises(NotImplementedError, match="at most two"):
        engine.start_battle()


def test_lifecycle_events_and_logger_keep_legacy_target_and_add_roster():
    reset_event_bus()
    player = _player()
    enemy = Goblin()
    encounter = CombatEncounter.singleton(
        enemy,
        encounter_id="lifecycle",
        combatant_id="lifecycle-enemy",
    )
    engine = BattleEngine(
        player,
        tile=DummyCombatTile(),
        encounter=encounter,
    )

    engine.start_battle()
    start_event = get_event_bus().get_history(EventType.COMBAT_START)[-1]

    assert start_event.target is enemy
    assert start_event.data["encounter_id"] == "lifecycle"
    assert start_event.data["enemies"][0]["combatant_id"] == "lifecycle-enemy"
    assert engine.logger.metadata["enemy"]["name"] == "Goblin"
    assert engine.logger.metadata["encounter_id"] == "lifecycle"
    assert engine.logger.metadata["enemies"][0]["display_label"] == "Goblin"

    enemy.health.current = 0
    outcome = engine.end_battle()
    end_event = get_event_bus().get_history(EventType.COMBAT_END)[-1]

    assert outcome.result == "victory"
    assert end_event.target is enemy
    assert end_event.data["enemies"][0]["resolution"] == "defeated"
    assert end_event.data["enemies"][0]["cause"] is None
    assert engine.logger.metadata["enemy"]["name"] == "Goblin"
    assert engine.logger.metadata["enemies"][0]["resolution"] == "defeated"


@pytest.mark.parametrize(
    ("attribute", "expected", "cause"),
    [
        ("paladin_mercy_victory", EnemyResolution.MERCY, "paladin_mercy"),
        ("tamed_by_player", EnemyResolution.TAMED, "tame"),
        ("windswept_ejected", EnemyResolution.EJECTED, "windswept"),
        ("paladin_repelled", EnemyResolution.ESCAPED, "paladin_repel"),
    ],
)
def test_singleton_outcome_records_existing_nonstandard_resolution(
    attribute,
    expected,
    cause,
):
    player = _player()
    enemy = Goblin()
    setattr(enemy, attribute, True)
    engine = BattleEngine(player, enemy, DummyCombatTile())

    engine.end_battle()

    record = engine.encounter.resolution_ledger[0]
    assert record.resolution is expected
    assert record.cause == cause
