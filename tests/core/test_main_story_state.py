"""Regression coverage for main-story progression state."""

from __future__ import annotations

from src.core import main_story
from src.core.player import LIMINAL_GAP_ENTRY_FACING, LIMINAL_GAP_ENTRY_POS, LIMINAL_GAP_LEVEL
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


def test_new_players_initialize_main_story_defaults():
    player = TestGameState.create_player()

    assert player.ensure_main_story_state() == main_story.default_state()
    assert player.can_enter_true_final() is False


def test_legacy_player_save_deserializes_main_story_defaults():
    player = TestGameState.create_player()
    data = PlayerDataSerializer.serialize(player)
    data.pop("main_story")

    loaded = PlayerDataSerializer.deserialize(data, skip_tiles=True)

    assert loaded.ensure_main_story_state() == main_story.default_state()


def test_main_story_round_trips_through_player_serializer():
    player = TestGameState.create_player()
    player.main_story["vesperion_false_final_triggered"] = True
    player.main_story["liminal_gap_entered"] = True
    player.main_story["voluntas_revealed"] = True
    player.main_story["seventh_seat_revealed"] = True
    player.main_story["acolyte_liminal_seen"] = True
    player.main_story["reflection_defeated"] = True
    player.main_story["returned_from_liminal_gap"] = True
    player.main_story["hooded_figure_witness_revealed"] = True
    player.main_story["liminal_gap_guide_revealed"] = True
    player.main_story["liminal_gap_clues_reviewed"] = True
    player.main_story["reflection_attempts"] = 2
    player.main_story["reflection_failures"] = 1
    player.main_story["vesperion_true_final_defeated"] = True
    player.main_story["main_story_complete"] = True
    player.main_story["guardian_trials_completed"]["Triangulus"] = True
    player.main_story["guardian_trials_started"]["Triangulus"] = True
    player.main_story["guardian_trial_choices"]["Triangulus"] = "Memory"
    player.main_story["voluntas_clues_found"]["Triangulus"] = True
    player.main_story["guardian_trials_completed"]["Quadrata"] = True
    player.main_story["guardian_trials_started"]["Quadrata"] = True
    player.main_story["guardian_trial_choices"]["Quadrata"] = "Rewrite"
    player.main_story["voluntas_clues_found"]["Quadrata"] = True
    player.main_story["guardian_trial_choices"]["Hexagonum"] = "not-a-valid-choice"
    player.liminal_gap_return = (7, 8, 6, "south")

    loaded = PlayerDataSerializer.deserialize(PlayerDataSerializer.serialize(player), skip_tiles=True)

    assert loaded.main_story["vesperion_false_final_triggered"] is True
    assert loaded.main_story["liminal_gap_entered"] is True
    assert loaded.main_story["voluntas_revealed"] is True
    assert loaded.main_story["seventh_seat_revealed"] is True
    assert loaded.main_story["acolyte_liminal_seen"] is True
    assert loaded.main_story["reflection_defeated"] is True
    assert loaded.main_story["returned_from_liminal_gap"] is True
    assert loaded.main_story["hooded_figure_witness_revealed"] is True
    assert loaded.main_story["liminal_gap_guide_revealed"] is True
    assert loaded.main_story["liminal_gap_clues_reviewed"] is True
    assert loaded.main_story["reflection_attempts"] == 2
    assert loaded.main_story["reflection_failures"] == 1
    assert loaded.main_story["vesperion_true_final_defeated"] is True
    assert loaded.main_story["main_story_complete"] is True
    assert loaded.main_story["guardian_trials_completed"]["Triangulus"] is True
    assert loaded.main_story["guardian_trials_completed"]["Quadrata"] is True
    assert loaded.main_story["guardian_trials_started"]["Triangulus"] is True
    assert loaded.main_story["guardian_trials_started"]["Quadrata"] is True
    assert loaded.main_story["guardian_trial_choices"]["Triangulus"] == "Memory"
    assert loaded.main_story["guardian_trial_choices"]["Quadrata"] == "Rewrite"
    assert loaded.main_story["guardian_trial_choices"]["Hexagonum"] is None
    assert loaded.main_story["voluntas_clues_found"]["Triangulus"] is True
    assert loaded.main_story["voluntas_clues_found"]["Quadrata"] is True
    assert loaded.main_story["true_final_unlocked"] is False
    assert loaded.liminal_gap_return == (7, 8, 6, "south")


def test_main_story_helpers_gate_voluntas_and_true_final():
    state = main_story.default_state()

    assert main_story.all_guardian_trials_completed(state) is False
    assert main_story.all_voluntas_clues_found(state) is False
    assert main_story.can_reveal_voluntas(state) is False
    assert main_story.can_unlock_true_final(state) is False

    for guardian in main_story.GUARDIAN_TRIALS:
        state["guardian_trials_completed"][guardian] = True
        state["voluntas_clues_found"][guardian] = True

    assert main_story.all_guardian_trials_completed(state) is True
    assert main_story.all_voluntas_clues_found(state) is True
    assert main_story.can_reveal_voluntas(state) is True
    assert main_story.can_unlock_true_final(state) is False

    state["voluntas_revealed"] = True
    state["reflection_defeated"] = True

    assert main_story.can_unlock_true_final(state) is True


def test_main_story_guardian_progress_summaries_include_choices():
    state = main_story.default_state()
    state["guardian_trials_completed"]["Triangulus"] = True
    state["voluntas_clues_found"]["Triangulus"] = True
    state["guardian_trial_choices"]["Triangulus"] = "Memory"
    state["guardian_trials_completed"]["Luna"] = True
    state["voluntas_clues_found"]["Luna"] = True
    state["guardian_trial_choices"]["Luna"] = "Release"

    summaries = main_story.guardian_clue_summary(state)

    assert main_story.completed_guardian_count(state) == 2
    assert summaries == [
        "Triangulus (Memory): selfhood is chosen, not assigned.",
        "Luna (Release): love without freedom becomes possession or obligation.",
    ]


def test_liminal_gap_stub_enters_real_hub_restores_resources_and_clears_effects():
    player = TestGameState.create_player(health=(101, 0), mana=(51, 0))
    player.location_x, player.location_y, player.location_z, player.facing = (10, 2, 4, "north")
    player.state = "fight"
    player.main_story["pending_liminal_gap_entry"] = True
    effect_calls = []
    player.effects = lambda end=False: effect_calls.append(end)

    player.enter_liminal_gap_stub((7, 8, 9, "south"))

    assert (player.location_x, player.location_y, player.location_z) == LIMINAL_GAP_ENTRY_POS
    assert player.facing == LIMINAL_GAP_ENTRY_FACING
    assert player.in_liminal_gap() is True
    assert player.liminal_gap_return == (7, 8, 9, "south")
    assert player.health.current == 50
    assert player.mana.current == 25
    assert player.state == "normal"
    assert effect_calls == [True]
    assert player.main_story["vesperion_false_final_triggered"] is True
    assert player.main_story["pending_liminal_gap_entry"] is False
    assert player.main_story["liminal_gap_entered"] is True


def test_liminal_gap_map_loads_with_hub_tiles():
    player = TestGameState.create_player()
    player.load_tiles()

    tile_names = {
        type(tile).__name__
        for (x, y, z), tile in player.world_dict.items()
        if z == LIMINAL_GAP_LEVEL
    }

    assert "LiminalGuide" in tile_names
    assert "LiminalExitBlocker" in tile_names
    assert "LiminalSeventhSeat" in tile_names
    assert "LiminalAcolyte" in tile_names
    assert "LiminalReflection" in tile_names
    assert {
        "TriangulusGate",
        "QuadrataGate",
        "HexagonumGate",
        "LunaGate",
        "PolarisGate",
        "InfinitasGate",
    }.issubset(tile_names)
