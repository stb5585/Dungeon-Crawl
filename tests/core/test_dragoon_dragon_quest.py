"""Regression coverage for the Dragoon Red Dragon quest route."""

from types import SimpleNamespace

from src.core import abilities, enemies, items, map_tiles
from src.core.classes import dragoon
from src.core.combat.battle_engine import BattleEngine
from src.core.save_system import PlayerDataSerializer
from tests.test_framework import TestGameState


def _lancer_with_recover():
    player = TestGameState.create_player(
        class_name="Lancer",
        race_name="Human",
        level=40,
        health=(500, 350),
        mana=(200, 100),
        stats={
            "strength": 40,
            "intel": 20,
            "wisdom": 20,
            "con": 30,
            "charisma": 20,
            "dex": 30,
        },
        skills=["Jump"],
    )
    jump = abilities.Jump()
    jump.unlock_modification("Recover")
    jump.modifications["Recover"] = True
    jump.modifications["Quick Dive"] = True
    jump.modifications["Crit"] = False
    player.spellbook["Skills"]["Jump"] = jump
    return player, jump


def test_dragoon_dragon_quest_defaults_and_save_load_round_trip():
    player, _jump = _lancer_with_recover()

    assert player.ensure_dragoon_dragon_quest() == dragoon.default_state()

    player.dragoon_dragon_quest["kaelenon_restored"] = True
    player.dragoon_dragon_quest["portal_key_obtained"] = True
    data = PlayerDataSerializer.serialize(player)
    restored = PlayerDataSerializer.deserialize(data, skip_tiles=True)

    assert restored.dragoon_dragon_quest["kaelenon_restored"] is True
    assert restored.dragoon_dragon_quest["portal_key_obtained"] is True
    assert restored.dragoon_dragon_quest["kaelenon_returned_home"] is False


def test_recover_jump_restores_kaelenon_without_low_health_requirement():
    player, jump = _lancer_with_recover()
    red_dragon = enemies.RedDragon()
    red_dragon.health.current = red_dragon.health.max

    result = jump.use(player, red_dragon)

    assert "restores the lost thread" in result
    assert red_dragon.health.current == 0
    assert red_dragon.kaelenon_restored is True
    assert player.dragoon_dragon_quest["kaelenon_restored"] is True


def test_kaelenon_restoration_requires_lancer_lineage_recover_and_red_dragon():
    player, jump = _lancer_with_recover()
    goblin = enemies.Goblin()
    jump.use(player, goblin)
    assert player.dragoon_dragon_quest["kaelenon_restored"] is False

    red_dragon = enemies.RedDragon()
    jump.modifications["Recover"] = False
    jump.use(player, red_dragon)
    assert player.dragoon_dragon_quest["kaelenon_restored"] is False
    assert not hasattr(red_dragon, "kaelenon_restored")

    warrior = TestGameState.create_player(class_name="Warrior", skills=["Jump"])
    warrior_jump = abilities.Jump()
    warrior_jump.unlock_modification("Recover")
    warrior_jump.modifications["Recover"] = True
    warrior_jump.modifications["Quick Dive"] = True
    warrior.spellbook["Skills"]["Jump"] = warrior_jump
    warrior_jump.use(warrior, enemies.RedDragon())
    assert warrior.dragoon_dragon_quest["kaelenon_restored"] is False


def test_red_dragon_alternate_victory_preserves_progression_and_jump_unlock():
    player, _jump = _lancer_with_recover()
    player.quest_dict["Main"]["Dracarys"] = {
        "Type": "Defeat",
        "What": "Red Dragon",
        "Completed": False,
    }
    red_dragon = enemies.RedDragon()
    red_dragon.health.current = 0
    red_dragon.kaelenon_restored = True
    class BossTile(SimpleNamespace):
        def __str__(self):
            return "RedDragonBossRoom"

    tile = BossTile(
        defeated=False,
        enemy=red_dragon,
        available_actions=lambda _player: ["Attack"],
    )

    engine = BattleEngine(player, red_dragon, tile)
    outcome = engine.end_battle()

    assert outcome.result == "victory"
    assert "Kaelenon is restored" in outcome.message
    assert tile.defeated is True
    assert player.quest_dict["Main"]["Dracarys"]["Completed"] is True
    assert player.spellbook["Skills"]["Jump"].unlocked_modifications["Dragon's Fury"] is True


def test_cambion_terminal_grants_key_then_returns_kaelenon_home_once():
    player, _jump = _lancer_with_recover()
    player.dragoon_dragon_quest["kaelenon_restored"] = True
    switch = map_tiles.AntiMagicSwitch(12, 28, map_tiles.REALM_OF_CAMBION_LEVEL)
    game = SimpleNamespace(player_char=player)

    assert switch.has_kaelenon_branch(game) is True
    assert switch.attempt_disable(game, None) is True
    first_messages = map_tiles.pop_cambion_messages(player)
    assert "Portal Key" in first_messages[0]
    assert "Kaelenon's Portal Key" in player.special_inventory
    assert player.dragoon_dragon_quest["portal_key_obtained"] is True

    assert switch.attempt_disable(game, None) is True
    second_messages = map_tiles.pop_cambion_messages(player)
    assert "returns home" in second_messages[0]
    assert "Draconite" in player.special_inventory
    assert player.dragoon_dragon_quest["kaelenon_returned_home"] is True

    assert switch.has_kaelenon_branch(game) is False


def test_draconite_pendant_crafting_consumes_draconite_and_boosts_recover():
    player, _jump = _lancer_with_recover()
    player.dragoon_dragon_quest["draconite_claimed"] = True
    player.modify_inventory(items.Draconite(), rare=True)

    ok, message = dragoon.craft_draconite_pendant(player)

    assert ok is True
    assert "Draconite Pendant" in message
    assert "Draconite" not in player.special_inventory
    assert "Draconite Pendant" in player.special_inventory
    assert player.dragoon_dragon_quest["pendant_crafted"] is True

    player.equipment["Pendant"] = items.DraconitePendant()
    hp_recover, mp_recover = dragoon.recover_amounts(player)
    assert hp_recover == int(player.health.max * 0.10)
    assert mp_recover == int(player.mana.max * 0.10)
