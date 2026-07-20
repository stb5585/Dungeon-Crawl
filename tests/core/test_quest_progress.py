#!/usr/bin/env python3
"""Coverage for shared staged quest progress helpers."""

from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace

from src.core import items, quest_progress
from src.core.data.data_loader import get_quests


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
