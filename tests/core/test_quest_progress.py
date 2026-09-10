#!/usr/bin/env python3
"""Coverage for shared staged quest progress helpers."""

from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace

from src.core import items, quest_progress
from src.core.data.data_loader import get_quests
from tests.test_framework import TestGameState


def _player():
    return SimpleNamespace(
        quest_dict={"Main": {}, "Side": {}, "Bounty": {}},
        special_inventory={},
    )


def _content_quest(name: str) -> dict:
    for quests_at_level in get_quests()["Sergeant"]["Main"].values():
        if name in quests_at_level:
            return deepcopy(quests_at_level[name])
    raise AssertionError(f"Missing Sergeant quest {name}")


def test_first_relic_completes_uncertain_reports_without_creating_holy_relics():
    player = _player()
    player.quest_dict["Main"][quest_progress.UNCERTAIN_REPORTS] = _content_quest(
        quest_progress.UNCERTAIN_REPORTS
    )
    player.special_inventory["Triangulus"] = [items.Relic1()]

    message = quest_progress.sync_relic_story_progress(player)

    uncertain = player.quest_dict["Main"][quest_progress.UNCERTAIN_REPORTS]
    assert quest_progress.HOLY_RELICS not in player.quest_dict["Main"]
    assert uncertain["Stage"] == "report_first_relic"
    assert uncertain["Completed"] is True
    assert "Bring the strange relic back" in uncertain["Help Text"]
    assert quest_progress.UNCERTAIN_REPORTS in message


def test_uncertain_reports_turn_in_creates_active_holy_relics_quest():
    player = _player()
    player.special_inventory["Triangulus"] = [items.Relic1()]

    quest_progress.handle_quest_turn_in(player, quest_progress.UNCERTAIN_REPORTS)

    holy = player.quest_dict["Main"][quest_progress.HOLY_RELICS]
    assert holy["Stage"] == "collecting"
    assert holy["Type"] == "Collect"
    assert holy["What"] == "Relics"
    assert holy["Completed"] is False
    assert "Recovered 1/6 relics" in holy["Help Text"]


def test_all_relics_complete_holy_relics_without_removing_staged_metadata():
    player = _player()
    quest_progress.ensure_holy_relics_quest(player)
    player.special_inventory.update(
        {
            "Triangulus": [items.Relic1()],
            "Quadrata": [items.Relic2()],
            "Hexagonum": [items.Relic3()],
            "Luna": [items.Relic4()],
            "Polaris": [items.Relic5()],
            "Infinitas": [items.Relic6()],
        }
    )

    message = quest_progress.sync_relic_story_progress(player)

    holy = player.quest_dict["Main"][quest_progress.HOLY_RELICS]
    assert holy["Completed"] is True
    assert holy["Stage"] == "collecting"
    assert "All six relics" in holy["Help Text"]
    assert quest_progress.HOLY_RELICS in message


def test_location_and_conversation_objectives_complete_only_matching_active_quests():
    player = _player()
    player.quest_dict["Side"] = {
        "Find the Spring": {
            "Type": "Locate", "Target Position": [4, 9, 3], "Completed": False,
            "Turned In": False,
        },
        "Speak to Griswold": {
            "Type": "Talk", "What": "Griswold", "Completed": False, "Turned In": False,
        },
        "Already Done": {
            "Type": "Talk", "What": "Griswold", "Completed": True, "Turned In": False,
        },
    }

    assert quest_progress.record_location(player, (1, 1, 1)) == ""
    assert quest_progress.record_location(player, (4, 9, 3)) == "You have completed the quest Find the Spring.\n"
    assert quest_progress.record_conversation(player, "Barkeep") == ""
    assert quest_progress.record_conversation(player, "Griswold") == "You have completed the quest Speak to Griswold.\n"
    assert player.quest_dict["Side"]["Already Done"]["Completed"] is True


def test_staged_talk_objective_advances_to_its_combat_objective():
    player = _player()
    player.quest_dict["Side"]["Mara's Contract"] = {
        "Type": "Talk",
        "What": "Griswold",
        "Stage": "ask_griswold",
        "Completed": False,
        "Turned In": False,
        "Stages": {
            "ask_griswold": {
                "Type": "Talk",
                "What": "Griswold",
                "Next Stage": "defeat_bandits",
                "Progress Text": "Griswold identifies the Bandits behind the theft.",
            },
            "defeat_bandits": {
                "Type": "Defeat",
                "What": "Bandit",
                "Total": 2,
                "Completion Text": "The route is clear. Return to Mara.",
            },
        },
    }

    message = quest_progress.record_conversation(player, "Griswold")
    quest = player.quest_dict["Side"]["Mara's Contract"]

    assert "identifies the Bandits" in message
    assert quest["Stage"] == "defeat_bandits"
    assert quest["Type"] == "Defeat"
    assert quest_progress.record_defeat(player, "Bandit") == ""
    assert quest_progress.record_defeat(player, "Bandit") == "The route is clear. Return to Mara.\n"
    assert quest["Completed"] is True


def test_bounty_kills_also_advance_matching_side_defeat_objectives():
    player = TestGameState.create_player(class_name="Warrior", level=10)
    player.quest_dict = {
        "Main": {},
        "Side": {
            "Mara's Contract": {
                "Type": "Defeat", "What": "Bandit", "Total": 2,
                "Completed": False, "Turned In": False,
            }
        },
        "Bounty": {"Bandit": [{"num": 3}, 0, False]},
    }

    player.quests(enemy=SimpleNamespace(name="Bandit"))
    player.quests(enemy=SimpleNamespace(name="Bandit"))

    assert player.quest_dict["Bounty"]["Bandit"][1] == 2
    assert player.quest_dict["Side"]["Mara's Contract"]["Killed"] == 2
    assert player.quest_dict["Side"]["Mara's Contract"]["Completed"] is True


def test_collection_progress_completes_at_inventory_target_and_caps_legacy_overflow():
    player = _player()
    player.inventory = {"Mystery Meat": [items.MysteryMeat() for _ in range(16)]}
    player.quest_dict["Side"]["Where's the Beef?"] = {
        "Type": "Collect",
        "What": "MysteryMeat",
        "Total": 12,
        "Collected": 16,
        "Completed": False,
        "Turned In": False,
    }

    quest_progress.sync_collection_progress(player)

    quest = player.quest_dict["Side"]["Where's the Beef?"]
    assert quest["Collected"] == 12
    assert quest["Completed"] is True
