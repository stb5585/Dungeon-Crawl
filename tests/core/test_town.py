#!/usr/bin/env python3
"""
Town-system coverage for bounty generation and quest hint helpers.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).parents[2]))


def _make_game(*, bounty_quests=None, pro_level=2, player_level=20, luck=3):
    player = SimpleNamespace(
        quest_dict={"Bounty": bounty_quests or {}, "Side": {}},
        level=SimpleNamespace(pro_level=pro_level),
        player_level=lambda: player_level,
        check_mod=lambda stat, luck_factor=None: luck if stat == "luck" else 0,
        special_inventory={},
    )
    return SimpleNamespace(player_char=player)


def test_create_bounty_skips_existing_targets_and_can_grant_reward(monkeypatch):
    from src.core import town

    board = town.BountyBoard()
    board.bounties = [{"name": "Second Target"}]
    game = _make_game(bounty_quests={"First Target": {"Completed": False}})

    enemy_cycle = iter(
        [
            SimpleNamespace(name="First Target", experience=10),
            SimpleNamespace(name="Second Target", experience=10),
            SimpleNamespace(name="Fresh Target", experience=10),
        ]
    )
    randint_values = iter([4, 30, 160, 1, 1])

    monkeypatch.setattr("src.core.town.enemies.random_enemy", lambda level: next(enemy_cycle))
    monkeypatch.setattr("src.core.town.items.random_item", lambda level: f"Reward-{level}")
    monkeypatch.setattr("src.core.town.random.randint", lambda a, b: next(randint_values))

    bounty = board.create_bounty(game)

    assert bounty["enemy"].name == "Fresh Target"
    assert bounty["num"] == 4
    assert bounty["exp"] == 30 * game.player_char.level.pro_level
    assert bounty["gold"] == 160 * game.player_char.player_level()
    assert bounty["reward"] == "Reward-3"


def test_generate_bounties_appends_requested_count(monkeypatch):
    from src.core import town

    board = town.BountyBoard()
    game = _make_game()

    monkeypatch.setattr("src.core.town.random.randint", lambda _a, _b: 3)
    monkeypatch.setattr(board, "create_bounty", lambda _game: {"name": f"Bounty-{len(board.bounties)}"})

    board.generate_bounties(game)

    assert len(board.bounties) == 3


def test_bounty_options_and_accept_quest_handle_missing_names():
    from src.core.town import BountyBoard

    board = BountyBoard()
    board.bounties = [{"name": "Goblin Hunt"}, {"name": "Rat Hunt"}]
    assert board.bounty_options() == ["Goblin Hunt", "Rat Hunt"]

    board.accept_quest({"name": "Goblin Hunt"})
    assert board.bounties == [{"name": "Rat Hunt"}]

    board.bounties = [{"enemy": "Nameless"}]
    assert board.bounty_options() == []


def test_get_quest_dict_uses_cache(monkeypatch):
    from src.core import town

    calls = {"count": 0}

    def fake_get_quests():
        calls["count"] += 1
        return {"Side": {"Quest": {}}}

    monkeypatch.setattr(town, "get_quests", fake_get_quests)
    town._quest_dict_cache = None

    first = town.get_quest_dict()
    second = town.get_quest_dict()

    assert first == second == {"Side": {"Quest": {}}}
    assert calls["count"] == 1


def test_holy_grail_rotation_hints_cover_hooded_and_sergeant_states():
    from src.core.town import get_holy_grail_rotation_hints

    player = SimpleNamespace(
        quest_dict={
            "Side": {
                "The Holy Grail of Quests": {
                    "Completed": False,
                    "Turned In": False,
                    "Chalice Progress": {
                        "Hooded": True,
                        "Map": False,
                        "Sergeant": False,
                        "Adventurer": False,
                        "Revealed": False,
                        "Spawned": False,
                    },
                }
            }
        },
        special_inventory={},
    )

    hooded_hints = get_holy_grail_rotation_hints(player, "Hooded Figure")
    assert len(hooded_hints) == 2
    assert "Golden Chalice" in hooded_hints[0]

    player.quest_dict["Side"]["The Holy Grail of Quests"]["Chalice Progress"]["Map"] = True
    sergeant_hints = get_holy_grail_rotation_hints(player, "Sergeant")
    assert len(sergeant_hints) == 2
    assert "third floor" in sergeant_hints[0]

    player.quest_dict["Side"]["The Holy Grail of Quests"]["Chalice Progress"]["Adventurer"] = True
    revealed_hints = get_holy_grail_rotation_hints(player, "Sergeant")
    assert "Inspect the Chalice Map" in revealed_hints[1]

    player.quest_dict["Side"]["The Holy Grail of Quests"]["Chalice Progress"]["Revealed"] = True
    final_hints = get_holy_grail_rotation_hints(player, "Sergeant")
    assert len(final_hints) == 1
    assert "sixth floor" in final_hints[0]


def test_holy_grail_rotation_hints_return_empty_for_completed_or_missing_quest():
    from src.core.town import get_holy_grail_rotation_hints

    missing = SimpleNamespace(quest_dict={"Side": {}}, special_inventory={})
    assert get_holy_grail_rotation_hints(missing, "Sergeant") == []

    completed = SimpleNamespace(
        quest_dict={"Side": {"The Holy Grail of Quests": {"Completed": True, "Turned In": False}}},
        special_inventory={},
    )
    assert get_holy_grail_rotation_hints(completed, "Sergeant") == []
