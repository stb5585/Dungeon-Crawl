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


def test_create_bounty_force_enemy_collision_falls_back_to_catalog(monkeypatch):
    from src.core import town

    board = town.BountyBoard()
    game = _make_game(bounty_quests={"Goblin": {"Completed": False}}, player_level=1, luck=0)

    monkeypatch.setattr("src.core.town.enemies.random_enemy", lambda level: SimpleNamespace(name="Goblin", experience=10))
    monkeypatch.setattr("src.core.town.random.choice", lambda candidates: candidates[0])
    monkeypatch.setattr("src.core.town.random.randint", lambda a, b: 0 if a == 0 else a)

    bounty = board.create_bounty(game)

    assert bounty["enemy"].name != "Goblin"


def test_generate_bounties_force_enemy_can_fill_multiple_slots(monkeypatch):
    from src.core import town

    board = town.BountyBoard()
    game = _make_game(player_level=1, luck=0)

    monkeypatch.setattr("src.core.town.enemies.random_enemy", lambda level: SimpleNamespace(name="Goblin", experience=10))
    monkeypatch.setattr("src.core.town.random.choice", lambda candidates: candidates[0])

    def fake_randint(a, b):
        if (a, b) == (1, 4):
            return 2
        if a == 0:
            return 0
        return a

    monkeypatch.setattr("src.core.town.random.randint", fake_randint)

    board.generate_bounties(game)

    names = [bounty["enemy"].name for bounty in board.bounties]
    assert len(names) == 2
    assert names[0] == "Goblin"
    assert names[1] != "Goblin"


def test_generate_bounties_appends_requested_count(monkeypatch):
    from src.core import town

    board = town.BountyBoard()
    game = _make_game()

    monkeypatch.setattr("src.core.town.random.randint", lambda _a, _b: 3)
    monkeypatch.setattr(board, "create_bounty", lambda _game: {"name": f"Bounty-{len(board.bounties)}"})

    board.generate_bounties(game)

    assert len(board.bounties) == 3


def test_bounty_board_records_initial_restock_baseline(monkeypatch):
    from src.core import town

    board = town.BountyBoard()
    game = _make_game()
    game.player_char.gameplay_stats = {"steps_taken": 12, "enemies_defeated": 2}

    monkeypatch.setattr("src.core.town.random.randint", lambda _a, _b: 1)
    monkeypatch.setattr(board, "create_bounty", lambda _game: {"name": "Goblin Hunt"})

    assert board.generate_bounties(game) is True

    assert board.bounties == [{"name": "Goblin Hunt"}]
    assert game.player_char.bounty_board_state == {
        "initialized": True,
        "last_restock_level": 20,
        "last_restock_steps": 12,
        "last_restock_enemies_defeated": 2,
    }


def test_bounty_board_does_not_restock_when_visible_or_active(monkeypatch):
    from src.core import town

    game = _make_game()
    game.bounties = {"Goblin": {"name": "Goblin Hunt"}}
    game.player_char.bounty_board_state = town.default_bounty_board_state()
    game.player_char.gameplay_stats = {"steps_taken": 999, "enemies_defeated": 99}
    board = town.BountyBoard()
    monkeypatch.setattr(board, "create_bounty", lambda _game: {"name": "New Hunt"})

    assert board.generate_bounties(game) is False
    assert board.bounties == []
    assert game.player_char.bounty_board_state["initialized"] is True

    game = _make_game(bounty_quests={"Goblin": [{"enemy": "Goblin"}, 0, False]})
    game.player_char.gameplay_stats = {"steps_taken": 999, "enemies_defeated": 99}
    board = town.BountyBoard()
    monkeypatch.setattr(board, "create_bounty", lambda _game: {"name": "New Hunt"})

    assert board.generate_bounties(game) is False
    assert board.bounties == []
    assert game.player_char.bounty_board_state["initialized"] is True


def test_bounty_board_waits_for_progress_before_restock(monkeypatch):
    from src.core import town

    board = town.BountyBoard()
    game = _make_game()
    game.player_char.gameplay_stats = {"steps_taken": 199, "enemies_defeated": 7}
    game.player_char.bounty_board_state = {
        "initialized": True,
        "last_restock_level": 20,
        "last_restock_steps": 0,
        "last_restock_enemies_defeated": 0,
    }
    monkeypatch.setattr("src.core.town.random.randint", lambda _a, _b: 1)
    monkeypatch.setattr(board, "create_bounty", lambda _game: {"name": "New Hunt"})

    assert board.generate_bounties(game) is False
    assert board.bounties == []

    game.player_char.gameplay_stats["steps_taken"] = town.BOUNTY_RESTOCK_STEP_THRESHOLD
    assert board.generate_bounties(game) is True
    assert board.bounties == [{"name": "New Hunt"}]


def test_bounty_board_restock_can_be_triggered_by_defeats_or_level(monkeypatch):
    from src.core import town

    monkeypatch.setattr("src.core.town.random.randint", lambda _a, _b: 1)

    defeat_board = town.BountyBoard()
    defeat_game = _make_game()
    defeat_game.player_char.gameplay_stats = {
        "steps_taken": 0,
        "enemies_defeated": town.BOUNTY_RESTOCK_ENEMY_THRESHOLD,
    }
    defeat_game.player_char.bounty_board_state = {
        "initialized": True,
        "last_restock_level": 20,
        "last_restock_steps": 0,
        "last_restock_enemies_defeated": 0,
    }
    monkeypatch.setattr(defeat_board, "create_bounty", lambda _game: {"name": "Defeat Hunt"})

    assert defeat_board.generate_bounties(defeat_game) is True
    assert defeat_board.bounties == [{"name": "Defeat Hunt"}]

    level_board = town.BountyBoard()
    level_game = _make_game(player_level=21)
    level_game.player_char.gameplay_stats = {"steps_taken": 0, "enemies_defeated": 0}
    level_game.player_char.bounty_board_state = {
        "initialized": True,
        "last_restock_level": 20,
        "last_restock_steps": 0,
        "last_restock_enemies_defeated": 0,
    }
    monkeypatch.setattr(level_board, "create_bounty", lambda _game: {"name": "Level Hunt"})

    assert level_board.generate_bounties(level_game) is True
    assert level_board.bounties == [{"name": "Level Hunt"}]


def test_bounty_options_and_accept_quest_handle_missing_names():
    from src.core.town import BountyBoard

    board = BountyBoard()
    board.bounties = [{"name": "Goblin Hunt"}, {"name": "Rat Hunt"}]
    assert board.bounty_options() == ["Goblin Hunt", "Rat Hunt"]

    board.accept_quest({"name": "Goblin Hunt"})
    assert board.bounties == [{"name": "Rat Hunt"}]

    board.bounties = [{"enemy": SimpleNamespace(name="Wolf")}, {"enemy": "Nameless"}]
    assert board.bounty_options() == ["Wolf"]


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


def test_old_key_quest_rewards_are_intentionally_generous():
    from src.core import items
    from src.core.data import data_loader

    data_loader.clear_cache()
    quests = data_loader.get_quests()

    butcher = quests["Barkeep"]["Main"]["10"]["The Butcher"]
    bad_dream = quests["Waitress"]["Main"]["35"]["A Bad Dream"]

    assert butcher["Reward"] == [items.OldKey]
    assert butcher["Reward Number"] == 2
    assert bad_dream["Reward"] == [items.OldKey]
    assert bad_dream["Reward Number"] == 3


def test_p4a_content_hooks_load_tavern_sergeant_and_warp_flavor():
    from src.core.data import data_loader

    data_loader.clear_cache()
    patrons = data_loader.get_patron_dialogues()
    tavern_flavor = data_loader.get_tavern_flavor_dialogues()
    quests = data_loader.get_quests()

    assert any("boss fight" in line for line in patrons["Barkeep"][25])
    assert any("stable descent field" in line for line in tavern_flavor)
    assert "tracking the guardians" in quests["Sergeant"]["Main"]["1"]["The Holy Relics"]["Help Text"]
    warp_quest = quests["Sergeant"]["Main"]["60"]["In the Day of Our Lord"]
    assert "staffed warp point" in warp_quest["End Text"]
    assert "scientists" in warp_quest["Help Text"]


def test_p4b_content_hooks_load_post_fight_and_storage_flavor():
    from src.core.data import data_loader

    data_loader.clear_cache()
    patrons = data_loader.get_patron_dialogues()
    tavern_flavor = data_loader.get_tavern_flavor_dialogues()

    assert any("Jester fell" in line for line in patrons["Barkeep"][65])
    assert any("Merzhin's realm collapsed" in line for line in patrons["Barkeep"][65])
    assert any("Cambion" in line for line in patrons["Soldier"][65])
    assert any("learned how to lie" in line for line in patrons["Soldier"][65])
    assert any("portal room" in line for line in patrons["Busboy"][65])
    assert any("After Merzhin fell" in line for line in patrons["Busboy"][65])
    assert any("storage lockers" in line for line in tavern_flavor)


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
